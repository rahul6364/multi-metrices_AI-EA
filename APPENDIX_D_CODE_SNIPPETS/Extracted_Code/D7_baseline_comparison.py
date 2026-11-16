"""
Original File: ai-anomaly-detection/pipeline/evaluator.py
Original Entity: Evaluator._calc and calculate_metrics
Lines: 21–68
Status: Implemented
Module: D.7 – Baseline Detection and Comparative Analysis
"""

import pandas as pd
from evaluator import MetricsResult

class Evaluator:
    @staticmethod
    def _safe_div(num: float, den: float) -> float:
        return float(num / den) if den else 0.0

    def _calc(self, true_labels, pred_labels, latency, model_name: str) -> MetricsResult:
        """Compute confusion matrix and derived classification metrics."""
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
        """Evaluate and compare proposed Energy-Aware model against non-energy Basic IF baseline."""
        df = pd.read_csv(evaluation_log_path)
        true_labels = df["true_label"].astype(int).tolist()
        pred_ea = [1 if p == "ANOMALY" else 0 for p in df["prediction_ea"].tolist()]
        pred_basic = [1 if p == "ANOMALY" else 0 for p in df["prediction_basic"].tolist()]

        first_attack = df[df.true_label == 1].timestamp.min()
        ea_lat = float(df[(df.true_label == 1) & (df.prediction_ea == "ANOMALY")].timestamp.min() - first_attack)
        basic_lat = float(df[(df.true_label == 1) & (df.prediction_basic == "ANOMALY")].timestamp.min() - first_attack)

        ea = self._calc(true_labels, pred_ea, ea_lat, "Energy-Aware")
        basic = self._calc(true_labels, pred_basic, basic_lat, "Basic IF")
        return {"energy_aware": ea, "basic": basic}
