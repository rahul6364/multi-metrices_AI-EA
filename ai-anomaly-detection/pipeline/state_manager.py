from collections import Counter, deque
from copy import deepcopy
import time

import config


class StateManager:
    def __init__(self) -> None:
        self.current_state = config.STATE_IDLE
        self.training_progress = {"current": 0, "total": config.MIN_TRAINING_WINDOWS}
        self.kepler_active = False
        self.model_trained = False
        self.pods = {}
        self.detection_history = deque(maxlen=100)
        self.mitigation_history = deque(maxlen=50)
        self.metrics_timeline = {}
        self.attack_types_detected = Counter()
        self.comparison_stats = {
            "ea_detections": 0,
            "basic_detections": 0,
            "ea_false_positives": 0,
            "basic_false_positives": 0,
            "ea_confirmed": 0,
            "ea_confirmed_anomalies": 0,
            "ea_confirmed_attacks": 0,
            "basic_confirmed": 0,
        }
        self._confirmed_anomaly_pods: set[str] = set()
        self._confirmed_attack_pods: set[str] = set()
        self.start_time = time.time()

    def set_state(self, value: str) -> None:
        self.current_state = value

    def set_training_progress(self, current: int, total: int) -> None:
        self.training_progress = {"current": current, "total": total}

    def set_kepler_active(self, active: bool) -> None:
        self.kepler_active = active

    def set_model_trained(self, trained: bool) -> None:
        self.model_trained = trained

    def update_pod_metrics(self, pod_name: str, sample) -> None:
        self.pods[pod_name] = {
            "pod_name": pod_name,
            "cpu": sample.cpu_cores,
            "memory_mb": sample.memory_mb,
            "energy_joules": sample.energy_joules,
            "network_kbps": (sample.network_rx_bytes_per_sec + sample.network_tx_bytes_per_sec) / 1024,
            "namespace": sample.namespace,
            "timestamp": sample.timestamp,
        }
        self.metrics_timeline.setdefault(pod_name, deque(maxlen=60)).append({
            "timestamp": sample.timestamp,
            "cpu": sample.cpu_cores,
            "energy": sample.energy_joules,
            "network": sample.network_rx_bytes_per_sec + sample.network_tx_bytes_per_sec,
        })

    def prune_stale_pods(self, max_stale_seconds: int = 20) -> None:
        now = time.time()
        stale = [
            pod_name
            for pod_name, info in self.pods.items()
            if now - float(info.get("timestamp", 0)) > max_stale_seconds
        ]
        for pod_name in stale:
            self.pods.pop(pod_name, None)
            self.metrics_timeline.pop(pod_name, None)

    def _latest_detection_by_pod(self) -> dict:
        """Return the most recent detection entry for each pod."""
        latest = {}
        for entry in self.detection_history:
            pod_name = entry.get("pod_name")
            if pod_name and pod_name not in latest:
                latest[pod_name] = entry
        return latest

    def get_active_incidents(self) -> list:
        """
        Return incidents that are currently active on live pods only.

        A stale historical anomaly for a deleted pod must not appear as active.
        """
        live_pods = set(self.pods.keys())
        active = []
        for pod_name, entry in self._latest_detection_by_pod().items():
            if pod_name not in live_pods:
                continue
            if entry.get("prediction_ea") == "ANOMALY" and entry.get("consecutive", 0) >= config.ANOMALY_CONFIRMATION_THRESHOLD:
                active.append(entry)
        return active

    def clear_incident_history(self) -> None:
        """Clear in-memory incident counters and history without retraining models."""
        self.detection_history.clear()
        self.mitigation_history.clear()
        self.attack_types_detected = Counter()
        self.comparison_stats = {
            "ea_detections": 0,
            "basic_detections": 0,
            "ea_false_positives": 0,
            "basic_false_positives": 0,
            "ea_confirmed": 0,
            "ea_confirmed_anomalies": 0,
            "ea_confirmed_attacks": 0,
            "basic_confirmed": 0,
        }
        self._confirmed_anomaly_pods = set()
        self._confirmed_attack_pods = set()

    def add_detection(self, result) -> None:
        entry = {
            "timestamp": time.time(),
            "pod_name": result.pod_name,
            "prediction_ea": result.prediction_ea,
            "prediction_basic": result.prediction_basic,
            "score_ea": result.score_ea,
            "score_basic": result.score_basic,
            "consecutive": result.consecutive_count,
            **result.feature_dict,
        }
        self.detection_history.appendleft(entry)
        if result.prediction_ea == "ANOMALY":
            self.comparison_stats["ea_detections"] += 1
            if result.true_label == 0:
                self.comparison_stats["ea_false_positives"] += 1
        if result.prediction_basic == "ANOMALY":
            self.comparison_stats["basic_detections"] += 1
            if result.true_label == 0:
                self.comparison_stats["basic_false_positives"] += 1
        if result.confirmed_attack and result.pod_name not in self._confirmed_anomaly_pods:
            self._confirmed_anomaly_pods.add(result.pod_name)
            self.comparison_stats["ea_confirmed_anomalies"] += 1
            self.comparison_stats["ea_confirmed"] = self.comparison_stats["ea_confirmed_anomalies"]
            if result.true_label == 1 and result.pod_name not in self._confirmed_attack_pods:
                self._confirmed_attack_pods.add(result.pod_name)
                self.comparison_stats["ea_confirmed_attacks"] += 1
            if result.prediction_basic == "ANOMALY":
                self.comparison_stats["basic_confirmed"] += 1

    def add_mitigation(self, mitigation: dict) -> None:
        self.mitigation_history.appendleft(mitigation)

    def reset_runtime_stats(self) -> None:
        self.training_progress = {"current": 0, "total": config.MIN_TRAINING_WINDOWS}
        self.model_trained = False
        self.detection_history.clear()
        self.mitigation_history.clear()
        self.attack_types_detected = Counter()
        self.comparison_stats = {
            "ea_detections": 0,
            "basic_detections": 0,
            "ea_false_positives": 0,
            "basic_false_positives": 0,
            "ea_confirmed": 0,
            "ea_confirmed_anomalies": 0,
            "ea_confirmed_attacks": 0,
            "basic_confirmed": 0,
        }
        self._confirmed_anomaly_pods = set()
        self._confirmed_attack_pods = set()

    def get_dashboard_json(self) -> dict:
        active_incidents = self.get_active_incidents()
        return {
            "current_state": self.current_state,
            "training_progress": self.training_progress,
            "kepler_active": self.kepler_active,
            "model_trained": self.model_trained,
            "pods": deepcopy(self.pods),
            "detection_history": list(self.detection_history),
            "mitigation_history": list(self.mitigation_history),
            "metrics_timeline": {k: list(v) for k, v in self.metrics_timeline.items()},
            "attack_types_detected": dict(self.attack_types_detected),
            "comparison_stats": deepcopy(self.comparison_stats),
            "active_incidents": active_incidents,
            "active_incident_count": len(active_incidents),
            "has_active_incident": len(active_incidents) > 0,
            "uptime": int(time.time() - self.start_time),
        }
