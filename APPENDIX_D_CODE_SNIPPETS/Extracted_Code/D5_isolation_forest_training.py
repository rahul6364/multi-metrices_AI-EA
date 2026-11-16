"""
Original File: ai-anomaly-detection/pipeline/model_manager.py
Original Entity: ModelManager.train_both_models
Lines: 123–160, 169–174
Status: Implemented
Module: D.5 – Isolation Forest Model Training
"""

import os, joblib, numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import config

def train_both_models(self) -> None:
    """Train Energy-Aware and Basic Isolation Forest models in parallel on baseline windows."""
    self.state = config.STATE_TRAINING
    X_16 = np.array(self.training_buffer_16)
    X_6 = np.array(self.training_buffer_6)

    # Fit feature scalers
    self.scaler_16 = StandardScaler().fit(X_16)
    self.scaler_6 = StandardScaler().fit(X_6)
    X_16_scaled = self.scaler_16.transform(X_16)
    X_6_scaled = self.scaler_6.transform(X_6)

    # Initialize and fit dual unsupervised Isolation Forests
    self.model_energy_aware = IsolationForest(
        n_estimators=config.N_ESTIMATORS, contamination=config.CONTAMINATION,
        bootstrap=config.MODEL_BOOTSTRAP, max_samples=config.MAX_SAMPLES,
        random_state=config.RANDOM_STATE, n_jobs=config.MODEL_N_JOBS
    ).fit(X_16_scaled)

    self.model_basic = IsolationForest(
        n_estimators=config.N_ESTIMATORS, contamination=config.CONTAMINATION,
        bootstrap=config.MODEL_BOOTSTRAP, max_samples=config.MAX_SAMPLES,
        random_state=config.RANDOM_STATE, n_jobs=config.MODEL_N_JOBS
    ).fit(X_6_scaled)

    os.makedirs("/app/model", exist_ok=True)
    joblib.dump(self.model_energy_aware, "/app/model/isolation_forest_energy_aware.pkl")
    joblib.dump(self.model_basic, "/app/model/isolation_forest_basic.pkl")
    joblib.dump(self.scaler_16, "/app/model/scaler_16.pkl")
    joblib.dump(self.scaler_6, "/app/model/scaler_6.pkl")

    self.state = config.STATE_DETECTING
    print(f"BOTH models trained! Energy-Aware: {len(X_16)} windows, Basic: {len(X_6)} windows.")
