"""
Original File: ai-anomaly-detection/pipeline/research_logger.py
Original Entity: ResearchLogger.log_detection_cycle and _update_latency_tracking
Lines: 101–160
Status: Implemented
Module: D.10 – Performance Evaluation and Research Logging
"""

import csv
from research_logger import RESEARCH_LOG_COLUMNS, _attack_type_from_pod, _confidence_from_score

def _update_latency_tracking(self, pod_name: str, sample, prediction: str, confirmed: bool) -> tuple[float, float]:
    """Compute sub-second detection latency and mitigation latency in milliseconds."""
    now = float(sample.timestamp)
    is_attack = bool(getattr(sample, "is_attack_pod", False) or pod_name.startswith("attack-"))
    if is_attack and pod_name not in self._first_attack_sample:
        self._first_attack_sample[pod_name] = now
    if prediction == "ANOMALY" and pod_name not in self._first_anomaly:
        self._first_anomaly[pod_name] = now

    det_latency_ms = (self._first_anomaly[pod_name] - self._first_attack_sample[pod_name]) * 1000.0 if (pod_name in self._first_attack_sample and pod_name in self._first_anomaly) else -1.0
    mit_latency_ms = (self._first_mitigation[pod_name] - self._first_anomaly[pod_name]) * 1000.0 if (confirmed and pod_name in self._first_mitigation and pod_name in self._first_anomaly) else -1.0
    return det_latency_ms, mit_latency_ms

def log_detection_cycle(self, sample, feature_dict: dict, result) -> None:
    """Record comprehensive detection-cycle telemetry and operational metrics to CSV."""
    det_lat_ms, mit_lat_ms = self._update_latency_tracking(result.pod_name, sample, result.prediction_ea, result.confirmed_attack)
    row = {
        "timestamp": sample.timestamp, "pod_name": result.pod_name, "namespace": sample.namespace,
        "cpu_utilization_percent": self._cpu_percent(feature_dict.get("avg_cpu", 0.0)),
        "memory_utilization_percent": self._memory_percent(sample.memory_bytes),
        "energy_consumption_joules": float(feature_dict.get("avg_energy", 0.0)),
        "energy_cpu_ratio": float(feature_dict.get("energy_cpu_ratio", 0.0)),
        "anomaly_score": float(result.score_ea), "prediction": result.prediction_ea,
        "confidence": _confidence_from_score(result.score_ea),
        "detected_attack_type": _attack_type_from_pod(result.pod_name),
        "mitigation_action": self._last_mitigation_action.get(result.pod_name, ""),
        "detection_latency_ms": det_lat_ms, "mitigation_latency_ms": mit_lat_ms, "pod_status": "Running"
    }
    with open(self.log_path, "a", newline="", encoding="utf-8") as handle:
        csv.DictWriter(handle, fieldnames=RESEARCH_LOG_COLUMNS).writerow(row)
