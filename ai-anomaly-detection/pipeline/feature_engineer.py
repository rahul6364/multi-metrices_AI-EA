from collections import deque

import numpy as np

import config


class FeatureEngineer:
    def __init__(self) -> None:
        self.windows = {}

    def add_sample(self, pod_name: str, sample) -> bool:
        self.windows.setdefault(pod_name, deque(maxlen=config.WINDOW_SIZE)).append(sample)
        return len(self.windows[pod_name]) == config.WINDOW_SIZE

    def extract_features(self, pod_name: str) -> dict:
        window = list(self.windows[pod_name])

        cpu_values = np.array([s.cpu_cores for s in window], dtype=float)
        mem_values = np.array([s.memory_mb for s in window], dtype=float)
        energy_values = np.array([s.energy_joules for s in window], dtype=float)
        net_values = np.array([s.network_rx_bytes_per_sec + s.network_tx_bytes_per_sec for s in window], dtype=float)

        avg_cpu = float(np.mean(cpu_values))
        avg_memory_mb = float(np.mean(mem_values))
        avg_energy = float(np.mean(energy_values))
        energy_cpu_ratio = float(avg_energy / (avg_cpu + 1e-6))
        cpu_variance = float(np.var(cpu_values))
        memory_variance = float(np.var(mem_values))
        energy_variance = float(np.var(energy_values))
        avg_network = float(np.mean(net_values))
        avg_network_variance = float(np.var(net_values))

        features_8 = np.array([[avg_cpu, avg_memory_mb, avg_energy, energy_cpu_ratio, cpu_variance, memory_variance, energy_variance, avg_network]], dtype=float)
        features_6 = np.array([[avg_cpu, avg_memory_mb, avg_network, cpu_variance, memory_variance, avg_network_variance]], dtype=float)

        return {
            "features_8": features_8,
            "features_6": features_6,
            "feature_dict": {
                "avg_cpu": avg_cpu,
                "avg_memory_mb": avg_memory_mb,
                "avg_energy": avg_energy,
                "energy_cpu_ratio": energy_cpu_ratio,
                "cpu_variance": cpu_variance,
                "memory_variance": memory_variance,
                "energy_variance": energy_variance,
                "avg_network": avg_network,
                "avg_network_variance": avg_network_variance,
            },
        }
