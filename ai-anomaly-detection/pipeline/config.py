PROMETHEUS_URL = "http://prometheus-service.monitoring.svc.cluster.local:9090"

COLLECTION_INTERVAL = 5
WINDOW_SIZE = 6
TARGET_NAMESPACE = "default"

MIN_TRAINING_WINDOWS = 30
TRAINING_PODS_WHITELIST = []

CONTAMINATION = 0.1
N_ESTIMATORS = 100
RANDOM_STATE = 42

ANOMALY_CONFIRMATION_THRESHOLD = 3

THROTTLE_CPU_LIMIT = "100m"
THROTTLE_MEMORY_LIMIT = "128Mi"
THROTTLE_DURATION_WINDOWS = 2

MODEL_PATH = "/app/model/isolation_forest.pkl"
SCALER_PATH = "/app/model/scaler.pkl"
RAW_DATA_PATH = "/app/data/raw_metrics.csv"
TRAINING_DATA_PATH = "/app/data/training_data.csv"
DETECTION_LOG_PATH = "/app/logs/detections.csv"
MITIGATION_LOG_PATH = "/app/logs/mitigations.csv"
EVALUATION_LOG_PATH = "/app/logs/evaluation.csv"

DASHBOARD_PORT = 8080

STATE_IDLE = "IDLE"
STATE_COLLECTING = "COLLECTING_BASELINE"
STATE_TRAINING = "TRAINING"
STATE_DETECTING = "DETECTING"

SYSTEM_NAMESPACES = ["kube-system", "monitoring", "kube-public"]
ATTACK_POD_PREFIXES = ["attack-"]
EXCLUDED_POD_PREFIXES = ["ai-detector-", "mysql-"]
