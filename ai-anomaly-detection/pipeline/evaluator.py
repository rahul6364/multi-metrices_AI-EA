import json
import os
from dataclasses import asdict, dataclass

import pandas as pd


@dataclass
class MetricsResult:
    model: str
    precision: float
    recall: float
    f1_score: float
    accuracy: float
    fpr: float
    fnr: float
    detection_latency: float


class Evaluator:
    @staticmethod
    def _safe_div(num: float, den: float) -> float:
        return float(num / den) if den else 0.0

    def _calc(self, true_labels, pred_labels, latency, model_name: str) -> MetricsResult:
        tp = sum((t == 1 and p == 1) for t, p in zip(true_labels, pred_labels))
        tn = sum((t == 0 and p == 0) for t, p in zip(true_labels, pred_labels))
        fp = sum((t == 0 and p == 1) for t, p in zip(true_labels, pred_labels))
        fn = sum((t == 1 and p == 0) for t, p in zip(true_labels, pred_labels))

        precision = self._safe_div(tp, tp + fp)
        recall = self._safe_div(tp, tp + fn)
        f1_score = self._safe_div(2 * precision * recall, precision + recall)
        accuracy = self._safe_div(tp + tn, tp + tn + fp + fn)
        fpr = self._safe_div(fp, fp + tn)
        fnr = self._safe_div(fn, fn + tp)

        return MetricsResult(model_name, precision, recall, f1_score, accuracy, fpr, fnr, latency)

    def calculate_metrics(self, evaluation_log_path: str) -> dict:
        df = pd.read_csv(evaluation_log_path)
        if df.empty:
            raise ValueError("Evaluation log is empty")

        true_labels = df["true_label"].astype(int).tolist()
        pred_ea = [1 if p == "ANOMALY" else 0 for p in df["prediction_ea"].tolist()]
        pred_basic = [1 if p == "ANOMALY" else 0 for p in df["prediction_basic"].tolist()]

        first_attack_time = df[df.true_label == 1].timestamp.min()
        first_ea_detection = df[(df.true_label == 1) & (df.prediction_ea == "ANOMALY")].timestamp.min()
        first_basic_detection = df[(df.true_label == 1) & (df.prediction_basic == "ANOMALY")].timestamp.min()

        ea_latency = float(first_ea_detection - first_attack_time) if pd.notna(first_attack_time) and pd.notna(first_ea_detection) else -1.0
        basic_latency = float(first_basic_detection - first_attack_time) if pd.notna(first_attack_time) and pd.notna(first_basic_detection) else -1.0

        ea = self._calc(true_labels, pred_ea, ea_latency, "Energy-Aware")
        basic = self._calc(true_labels, pred_basic, basic_latency, "Basic IF")

        print("┌─────────────────┬───────────────┬───────────┐")
        print("│ Metric          │ Energy-Aware  │ Basic IF  │")
        print("├─────────────────┼───────────────┼───────────┤")
        print(f"│ Precision       │ {ea.precision:.2f}          │ {basic.precision:.2f}      │")
        print(f"│ Recall          │ {ea.recall:.2f}          │ {basic.recall:.2f}      │")
        print(f"│ F1 Score        │ {ea.f1_score:.2f}          │ {basic.f1_score:.2f}      │")
        print(f"│ Accuracy        │ {ea.accuracy:.2f}          │ {basic.accuracy:.2f}      │")
        print(f"│ False Pos Rate  │ {ea.fpr:.2f}          │ {basic.fpr:.2f}      │")
        print(f"│ Detection Lat.  │ {ea.detection_latency:.2f}s         │ {basic.detection_latency:.2f}s     │")
        print("└─────────────────┴───────────────┴───────────┘")

        payload = {"energy_aware": asdict(ea), "basic": asdict(basic)}
        try:
            os.makedirs("/app/logs", exist_ok=True)
            with open("/app/logs/evaluation_results.json", "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            pd.DataFrame([asdict(ea), asdict(basic)]).to_csv("/app/logs/evaluation_results.csv", index=False)
        except Exception:
            try:
                os.makedirs("results", exist_ok=True)
                with open("results/evaluation_results.json", "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2)
                pd.DataFrame([asdict(ea), asdict(basic)]).to_csv("results/evaluation_results.csv", index=False)
            except Exception:
                pass
        return payload
