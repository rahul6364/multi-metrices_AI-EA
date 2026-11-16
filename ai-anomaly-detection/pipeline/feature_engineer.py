from collections import deque

import numpy as np

import config


class FeatureEngineer:
    """
    IEEE Research-Grade Feature Engineering Pipeline for Kubernetes Anomaly Detection.
    
    This class handles per-pod sliding window metric storage and temporal feature extraction.
    It computes 26 multi-metric and cross-resource engineered features designed to detect
    energy-wasting workloads (e.g. cryptojacking, CPU/memory/network stress).
    """
    def __init__(self) -> None:
        self.windows = {}

    def add_sample(self, pod_name: str, sample) -> bool:
        """
        Add a telemetry sample to the pod's sliding window.
        
        Args:
            pod_name: Unique identifier of the pod.
            sample: Telemetry sample containing CPU, Memory, Energy, and Network metrics.
            
        Returns:
            bool: True if the sliding window is fully populated, False otherwise.
        """
        self.windows.setdefault(pod_name, deque(maxlen=config.WINDOW_SIZE)).append(sample)
        return len(self.windows[pod_name]) == config.WINDOW_SIZE

    def extract_features(self, pod_name: str) -> dict:
        """
        Extract publication-quality statistical and cross-resource features from the pod window.
        
        Args:
            pod_name: Unique identifier of the pod.
            
        Returns:
            dict: Dictionary containing the three scaled/unscaled feature vectors and the raw feature dictionary.
        """
        window = list(self.windows[pod_name])
        
        # Telemetry parsing using raw NumPy arrays
        cpu_values = np.array([s.cpu_cores for s in window], dtype=float)
        mem_values = np.array([s.memory_mb for s in window], dtype=float)
        energy_values = np.array([s.energy_joules for s in window], dtype=float)
        net_values = np.array([s.network_rx_bytes_per_sec + s.network_tx_bytes_per_sec for s in window], dtype=float)
        
        # Small epsilon constant to avoid divide-by-zero errors in ratio calculations
        EPSILON = 1e-6
        N = len(window)
        x = np.arange(N)

        # Helper function for least-squares trend estimation using polyfit
        def _get_slope(y_vals):
            if len(y_vals) < 2:
                return 0.0
            # Fits first-degree polynomial (linear regression line): y = mx + c
            # Returns the slope m (trend coefficient)
            return float(np.polyfit(x, y_vals, 1)[0])

        # ----------------------------------------------------
        # 1. CPU FEATURES
        # ----------------------------------------------------
        avg_cpu = float(np.mean(cpu_values))
        max_cpu = float(np.max(cpu_values))
        min_cpu = float(np.min(cpu_values))
        std_cpu = float(np.std(cpu_values))
        cpu_variance = float(np.var(cpu_values))
        cpu_slope = _get_slope(cpu_values)
        cpu_peak_ratio = float(max_cpu / (avg_cpu + EPSILON))
        cpu_range = float(max_cpu - min_cpu)

        # ----------------------------------------------------
        # 2. MEMORY FEATURES
        # ----------------------------------------------------
        avg_memory = float(np.mean(mem_values))
        max_memory = float(np.max(mem_values))
        std_memory = float(np.std(mem_values))
        memory_variance = float(np.var(mem_values))

        # ----------------------------------------------------
        # 3. ENERGY FEATURES
        # ----------------------------------------------------
        avg_energy = float(np.mean(energy_values))
        max_energy = float(np.max(energy_values))
        std_energy = float(np.std(energy_values))
        energy_variance = float(np.var(energy_values))
        energy_slope = _get_slope(energy_values)
        energy_peak_ratio = float(max_energy / (avg_energy + EPSILON))

        # ----------------------------------------------------
        # 4. NETWORK FEATURES
        # ----------------------------------------------------
        avg_network = float(np.mean(net_values))
        network_variance = float(np.var(net_values))
        max_network = float(np.max(net_values))

        # ----------------------------------------------------
        # 5. CROSS FEATURES
        # ----------------------------------------------------
        energy_cpu_ratio = float(avg_energy / (avg_cpu + EPSILON))
        cpu_memory_ratio = float(avg_cpu / (avg_memory + EPSILON))
        energy_density = float(avg_energy / (avg_memory + EPSILON))
        
        # Rolling short-term averages (using last 3 samples within window)
        k_roll = min(3, N)
        rolling_cpu_avg = float(np.mean(cpu_values[-k_roll:]))
        rolling_energy_avg = float(np.mean(energy_values[-k_roll:]))

        # ----------------------------------------------------
        # COMPATIBILITY & ALIASES
        # ----------------------------------------------------
        avg_memory_mb = avg_memory
        network_peak = max_network
        avg_network_variance = network_variance
        cpu_trend = cpu_slope

        # ----------------------------------------------------
        # FEATURE DICTIONARY ASSEMBLY (all 26 features + aliases)
        # ----------------------------------------------------
        feature_dict = {
            # CPU
            "avg_cpu": avg_cpu,
            "max_cpu": max_cpu,
            "min_cpu": min_cpu,
            "std_cpu": std_cpu,
            "cpu_variance": cpu_variance,
            "cpu_slope": cpu_slope,
            "cpu_trend": cpu_trend,
            "cpu_peak_ratio": cpu_peak_ratio,
            "cpu_range": cpu_range,
            # Memory
            "avg_memory": avg_memory,
            "avg_memory_mb": avg_memory_mb,
            "max_memory": max_memory,
            "std_memory": std_memory,
            "memory_variance": memory_variance,
            # Energy
            "avg_energy": avg_energy,
            "max_energy": max_energy,
            "std_energy": std_energy,
            "energy_variance": energy_variance,
            "energy_slope": energy_slope,
            "energy_peak_ratio": energy_peak_ratio,
            # Network
            "avg_network": avg_network,
            "network_variance": network_variance,
            "avg_network_variance": avg_network_variance,
            "max_network": max_network,
            "network_peak": network_peak,
            # Cross-Metric
            "energy_cpu_ratio": energy_cpu_ratio,
            "cpu_memory_ratio": cpu_memory_ratio,
            "energy_density": energy_density,
            "rolling_cpu_average": rolling_cpu_avg,
            "rolling_energy_average": rolling_energy_avg,
            "rolling_cpu_avg": rolling_cpu_avg,
            "rolling_energy_avg": rolling_energy_avg
        }

        # ----------------------------------------------------
        # VECTOR REPRESENTATIONS (2D NumPy arrays of shape (1, N))
        # ----------------------------------------------------
        # features_16: Selected 16 strongest features.
        # First 8 features MUST correspond exactly to the original features_8 for model/scaler compatibility.
        features_16 = np.array([[
            avg_cpu,              # 1
            avg_memory_mb,        # 2
            avg_energy,           # 3
            energy_cpu_ratio,     # 4
            cpu_variance,         # 5
            memory_variance,      # 6
            energy_variance,      # 7
            avg_network,          # 8
            max_cpu,              # 9
            cpu_slope,            # 10
            cpu_peak_ratio,       # 11
            max_energy,           # 12
            energy_slope,         # 13
            cpu_memory_ratio,     # 14
            energy_density,       # 15
            max_network           # 16
        ]], dtype=float)

        # features_8: slice of features_16 for backward compatibility.
        features_8 = features_16[:, :8]

        # features_6: exactly the baseline features as before.
        features_6 = np.array([[
            avg_cpu,
            avg_memory_mb,
            avg_network,
            cpu_variance,
            memory_variance,
            network_variance
        ]], dtype=float)

        # Store in class-level dictionary as model_manager.py queries this via getattr on FeatureEngineer
        if not hasattr(FeatureEngineer, "last_extracted_features"):
            FeatureEngineer.last_extracted_features = {}
        FeatureEngineer.last_extracted_features[pod_name] = features_16

        return {
            "features_16": features_16,
            "features_8": features_8,
            "features_6": features_6,
            "feature_dict": feature_dict
        }
