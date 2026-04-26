import csv
import os
import time
from collections import defaultdict
from dataclasses import dataclass

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

import config


@dataclass
class PredictionResult:
    pod_name: str
    prediction_ea: str
    score_ea: float
    prediction_basic: str
    score_basic: float
    consecutive_count: int
    confirmed_attack: bool
    true_label: int
    feature_dict: dict


class ModelManager:
    def __init__(self) -> None:
        self.state = config.STATE_IDLE
        self.training_buffer_8 = []
        self.training_buffer_6 = []
        self.training_counts = defaultdict(int)
        self.training_pods = set()
        self.consecutive_count = defaultdict(int)

        self.model_energy_aware = None
        self.model_basic = None
        self.scaler_8 = None
        self.scaler_6 = None

        self._evaluation_headers = [
            "timestamp", "pod_name", "prediction_ea", "score_ea", "prediction_basic", "score_basic",
            "consecutive_count", "confirmed_attack", "true_label", "avg_cpu", "avg_memory_mb", "avg_energy",
            "energy_cpu_ratio", "cpu_variance", "memory_variance", "energy_variance", "avg_network", "avg_network_variance",
        ]
        self._ensure_csv(config.EVALUATION_LOG_PATH, self._evaluation_headers)
        self._ensure_csv(config.TRAINING_DATA_PATH, ["model", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8"])

    def _ensure_csv(self, path: str, headers: list[str]) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(headers)

    def training_progress_windows(self) -> int:
        return min(self.training_counts.values()) if self.training_counts else 0

    def start_baseline_collection(self) -> None:
        self.state = config.STATE_COLLECTING
        self.training_buffer_8 = []
        self.training_buffer_6 = []
        self.training_counts = defaultdict(int)
        self.training_pods = set()
        self.consecutive_count = defaultdict(int)
        print("Baseline collection started.")
        print("IMPORTANT: Only normal workloads should be running now!")
        print(f"Progress will show: X/{config.MIN_TRAINING_WINDOWS} windows")

    def add_training_window(self, features_8, features_6, pod_name: str, namespace: str) -> None:
        if self.state != config.STATE_COLLECTING:
            return
        if pod_name.startswith("attack-") or namespace != config.TARGET_NAMESPACE:
            return

        self.training_buffer_8.append(features_8.flatten().tolist())
        self.training_buffer_6.append(features_6.flatten().tolist())
        self.training_counts[pod_name] += 1
        self.training_pods.add(pod_name)

        min_windows = min(self.training_counts.values()) if self.training_counts else 0
        print(
            f"[TRAINING] {min_windows}/{config.MIN_TRAINING_WINDOWS} windows "
            f"(pods tracked: {len(self.training_pods)})"
        )

        # Train only after each observed normal pod has contributed enough windows.
        if self.training_pods and min_windows >= config.MIN_TRAINING_WINDOWS:
            self.train_both_models()

    def train_both_models(self) -> None:
        self.state = config.STATE_TRAINING

        X_8 = np.array(self.training_buffer_8)
        X_6 = np.array(self.training_buffer_6)

        self.scaler_8 = StandardScaler().fit(X_8)
        self.scaler_6 = StandardScaler().fit(X_6)

        X_8_scaled = self.scaler_8.transform(X_8)
        X_6_scaled = self.scaler_6.transform(X_6)

        self.model_energy_aware = IsolationForest(
            n_estimators=config.N_ESTIMATORS,
            contamination=config.CONTAMINATION,
            random_state=config.RANDOM_STATE,
            max_samples="auto",
        ).fit(X_8_scaled)

        self.model_basic = IsolationForest(
            n_estimators=config.N_ESTIMATORS,
            contamination=config.CONTAMINATION,
            random_state=config.RANDOM_STATE,
            max_samples="auto",
        ).fit(X_6_scaled)

        os.makedirs("/app/model", exist_ok=True)
        joblib.dump(self.model_energy_aware, "/app/model/isolation_forest_energy_aware.pkl")
        joblib.dump(self.model_basic, "/app/model/isolation_forest_basic.pkl")
        joblib.dump(self.scaler_8, "/app/model/scaler_8.pkl")
        joblib.dump(self.scaler_6, "/app/model/scaler_6.pkl")

        with open(config.TRAINING_DATA_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in X_8.tolist():
                writer.writerow(["energy_aware", *row])
            for row in X_6.tolist():
                writer.writerow(["basic", *row, "", ""])

        self.state = config.STATE_DETECTING
        print("✅ BOTH models trained!")
        print(f"  Energy-Aware IF: trained on {len(X_8)} windows (8 features)")
        print(f"  Basic IF: trained on {len(X_6)} windows (6 features)")
        print("Detection active. Deploy attack workload to test.")

    def save_to_evaluation_log(self, result: PredictionResult) -> None:
        row = {
            "timestamp": time.time(),
            "pod_name": result.pod_name,
            "prediction_ea": result.prediction_ea,
            "score_ea": result.score_ea,
            "prediction_basic": result.prediction_basic,
            "score_basic": result.score_basic,
            "consecutive_count": result.consecutive_count,
            "confirmed_attack": int(result.confirmed_attack),
            "true_label": result.true_label,
            **result.feature_dict,
        }
        with open(config.EVALUATION_LOG_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self._evaluation_headers)
            writer.writerow(row)

    def predict(self, features_8, features_6, pod_name: str, feature_dict: dict) -> PredictionResult:
        x8 = self.scaler_8.transform(features_8)
        pred_ea = self.model_energy_aware.predict(x8)[0]
        score_ea = float(self.model_energy_aware.decision_function(x8)[0])

        x6 = self.scaler_6.transform(features_6)
        pred_basic = self.model_basic.predict(x6)[0]
        score_basic = float(self.model_basic.decision_function(x6)[0])

        if pred_ea == -1:
            self.consecutive_count[pod_name] += 1
        else:
            self.consecutive_count[pod_name] = 0

        confirmed = self.consecutive_count[pod_name] >= config.ANOMALY_CONFIRMATION_THRESHOLD
        true_label = 1 if pod_name.startswith("attack-") else 0

        result = PredictionResult(
            pod_name=pod_name,
            prediction_ea="ANOMALY" if pred_ea == -1 else "NORMAL",
            score_ea=score_ea,
            prediction_basic="ANOMALY" if pred_basic == -1 else "NORMAL",
            score_basic=score_basic,
            consecutive_count=self.consecutive_count[pod_name],
            confirmed_attack=confirmed,
            true_label=true_label,
            feature_dict=feature_dict,
        )

        self.save_to_evaluation_log(result)
        return result
