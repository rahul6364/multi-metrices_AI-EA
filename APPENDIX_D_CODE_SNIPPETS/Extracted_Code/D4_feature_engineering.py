"""
Original File: ai-anomaly-detection/pipeline/feature_engineer.py
Original Entity: FeatureEngineer.extract_features
Lines: 43–112, 169–186
Status: Implemented
Module: D.4 – Multi-Metric Feature Engineering
"""

import numpy as np

def extract_features(self, pod_name: str) -> dict:
    """Extract temporal statistical and cross-resource features from pod sliding window."""
    window = list(self.windows[pod_name])
    cpu_values = np.array([s.cpu_cores for s in window], dtype=float)
    mem_values = np.array([s.memory_mb for s in window], dtype=float)
    energy_values = np.array([s.energy_joules for s in window], dtype=float)
    net_values = np.array([s.network_rx_bytes_per_sec + s.network_tx_bytes_per_sec for s in window], dtype=float)

    EPSILON = 1e-6
    x = np.arange(len(window))
    cpu_slope = float(np.polyfit(x, cpu_values, 1)[0]) if len(cpu_values) >= 2 else 0.0
    energy_slope = float(np.polyfit(x, energy_values, 1)[0]) if len(energy_values) >= 2 else 0.0

    avg_cpu, max_cpu, cpu_var = float(np.mean(cpu_values)), float(np.max(cpu_values)), float(np.var(cpu_values))
    avg_mem, mem_var = float(np.mean(mem_values)), float(np.var(mem_values))
    avg_energy, max_energy, energy_var = float(np.mean(energy_values)), float(np.max(energy_values)), float(np.var(energy_values))
    avg_network = float(np.mean(net_values))

    # Cross-resource behavioural features
    energy_cpu_ratio = float(avg_energy / (avg_cpu + EPSILON))
    cpu_memory_ratio = float(avg_cpu / (avg_mem + EPSILON))
    energy_density = float(avg_energy / (avg_mem + EPSILON))

    features_16 = np.array([[
        avg_cpu, avg_mem, avg_energy, energy_cpu_ratio,
        cpu_var, mem_var, energy_var, avg_network,
        max_cpu, cpu_slope, max_cpu / (avg_cpu + EPSILON),
        max_energy, energy_slope, cpu_memory_ratio, energy_density, float(np.max(net_values))
    ]], dtype=float)
    features_6 = np.array([[avg_cpu, avg_mem, avg_network, cpu_var, mem_var, float(np.var(net_values))]], dtype=float)
    return {"features_16": features_16, "features_6": features_6}
