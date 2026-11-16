"""
Original File: ai-anomaly-detection/pipeline/model_manager.py
Original Entity: ModelManager.predict
Lines: 196–242
Status: Implemented
Module: D.6 – Anomaly Detection and Anomaly Score Generation
"""

import numpy as np
import config
from model_manager import PredictionResult

def predict(self, features_ea, features_6, pod_name: str, feature_dict: dict) -> PredictionResult:
    """Score pod telemetry against dual models and confirm anomalies via temporal hysteresis."""
    x16 = self.scaler_16.transform(features_ea)
    raw_pred_ea = self.model_energy_aware.predict(x16)[0]
    score_ea = float(self.model_energy_aware.decision_function(x16)[0])

    x6 = self.scaler_6.transform(features_6)
    pred_basic = self.model_basic.predict(x6)[0]
    score_basic = float(self.model_basic.decision_function(x6)[0])

    # Unsupervised anomaly decision: -1 indicates isolation outlier
    is_anomalous_ea = (raw_pred_ea == -1)
    if is_anomalous_ea:
        self.consecutive_count[pod_name] += 1
    else:
        self.consecutive_count[pod_name] = 0

    confirmed = self.consecutive_count[pod_name] >= config.ANOMALY_CONFIRMATION_THRESHOLD
    true_label = 1 if pod_name.startswith("attack-") else 0

    result = PredictionResult(
        pod_name=pod_name,
        prediction_ea="ANOMALY" if is_anomalous_ea else "NORMAL",
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
