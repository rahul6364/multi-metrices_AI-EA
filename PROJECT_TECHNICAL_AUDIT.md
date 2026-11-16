# PROJECT TECHNICAL AUDIT REPORT

**Project Title:** Energy-Aware Multi-Metric Behavioral Anomaly Detection and Automated Mitigation Framework for Kubernetes-Based Cloud Systems  
**Institution:** Sahyadri College of Engineering & Management, Mangaluru  
**Department:** Computer Science & Engineering | **Team:** CSE-26  
**Guide:** Dr. Deepti Rai (Assistant Professor)  
**Execution Environment Verified in Source Code:** Single-node K3s cluster on WSL2 Linux/Ubuntu (`/var/run/secrets/kubernetes.io/serviceaccount/`, `k3s ctr images import`)  
**Audit Type:** 100% Codebase-Verified Technical Audit (Zero Inferred / Hallucinated Elements)

---

## PART 1 — COMPLETE PROJECT STRUCTURE

```
/home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/
├── .gitignore
├── LICENSE
├── PROJECT_INTELLIGENCE.md
├── README.md
├── README_EXPERIMENTS.md
├── detections.csv
├── evaluation.csv
├── project.zip
├── run_research_pipeline.sh
├── setup_research_env.sh
├── ai-anomaly-detection/
│   ├── ai-detector-deployment.yaml
│   ├── ai-detector-pvc.yaml
│   ├── ai-detector-service.yaml
│   ├── ai-detector.tar
│   ├── cleanup_attacks.sh
│   ├── deploy.sh
│   ├── port-forward.sh
│   ├── rbac.yaml
│   ├── redeploy_detector.sh
│   ├── monitoring/
│   │   ├── grafana-dashboard-configmap.yaml
│   │   ├── grafana-dashboard-provider-configmap.yaml
│   │   ├── grafana-datasource-configmap.yaml
│   │   ├── grafana-deployment.yaml
│   │   ├── kepler-daemonset.yaml
│   │   ├── kepler-rbac.yaml
│   │   ├── kepler-service.yaml
│   │   ├── node-exporter.yaml
│   │   └── update-prometheus-configmap.yaml
│   ├── pipeline/
│   │   ├── Dockerfile
│   │   ├── ai-detector.tar
│   │   ├── collector.py
│   │   ├── config.py
│   │   ├── dashboard.py
│   │   ├── evaluator.py
│   │   ├── feature_engineer.py
│   │   ├── main.py
│   │   ├── mitigator.py
│   │   ├── model_manager.py
│   │   ├── requirements.txt
│   │   ├── research_logger.py
│   │   ├── state_manager.py
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   ├── components.css
│   │   │   │   ├── layout.css
│   │   │   │   ├── variables.css
│   │   │   │   └── views.css
│   │   │   └── js/
│   │   │       ├── api.js
│   │   │       ├── app.js
│   │   │       ├── charts.js
│   │   │       ├── state.js
│   │   │       ├── components/
│   │   │       │   ├── featureAnalysis.js
│   │   │       │   ├── incidentCard.js
│   │   │       │   ├── metricCard.js
│   │   │       │   ├── podTable.js
│   │   │       │   ├── statusBadge.js
│   │   │       │   └── timeline.js
│   │   │       └── views/
│   │   │           ├── detectionView.js
│   │   │           ├── incidentsView.js
│   │   │           ├── kubernetesView.js
│   │   │           ├── mitigationView.js
│   │   │           ├── monitoringView.js
│   │   │           ├── overviewView.js
│   │   │           └── researchView.js
│   │   └── templates/
│   │       └── index.html
│   └── workloads/
│       ├── attack-combined.yaml
│       ├── attack-cpu.yaml
│       ├── attack-cryptojacking.yaml
│       ├── attack-memory.yaml
│       ├── attack-network.yaml
│       └── normal-workload.yaml
├── backend/
│   ├── Dockerfile
│   ├── README.md
│   ├── app.py
│   └── requirements.txt
├── experiments/
│   ├── calculate_metrics.py
│   ├── experiment_config.py
│   ├── export_metrics.py
│   ├── generate_graphs.py
│   ├── requirements.txt
│   ├── run_experiment.py
│   ├── run_research_pipeline.py
│   └── utils.py
├── frontend/
│   ├── Dockerfile
│   ├── README.md
│   ├── package.json
│   ├── package-lock.json
│   ├── public/
│   └── src/
│       ├── App.css
│       ├── App.js
│       ├── App.test.js
│       ├── index.css
│       ├── index.js
│       ├── logo.svg
│       ├── reportWebVitals.js
│       └── setupTests.js
├── kubernetes/
│   ├── backend-deployment.yaml
│   ├── backend-ingress.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-ingress.yaml
│   ├── frontend-service.yaml
│   ├── mysql-deployment.yaml
│   ├── mysql-service.yml
│   └── todo-configmap.yml
└── results/
    ├── evaluation_results.csv
    ├── evaluation_results.json
    ├── experiments/
    ├── figures/
    ├── logs/
    ├── metrics/
    └── raw_metrics/
```

### File-by-File Audit

#### 1. `ai-anomaly-detection/pipeline/main.py`
* **File Type:** Python script
* **Purpose:** Core runtime entry point. Starts Flask dashboard thread, enters infinite 5-second polling loop, coordinates metric collection, sliding window feature extraction, dual-model inference, consecutive anomaly tracking, progressive mitigation execution, and CSV logging.
* **Imports:** `csv`, `os`, `threading`, `time`, `traceback`, `config`, `collector.MetricsCollector`, `dashboard.create_app`, `evaluator.Evaluator`, `feature_engineer.FeatureEngineer`, `mitigator.Mitigator`, `model_manager.ModelManager`, `research_logger.ResearchLogger`, `state_manager.StateManager`.
* **Imported by:** Top-level executable (`if __name__ == '__main__': main_loop()`).
* **Actually executed?** **YES.** Specified as container runtime command in `Dockerfile`.
* **Evidence:** [`ai-anomaly-detection/pipeline/Dockerfile:14`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/Dockerfile#L14): `CMD ["python", "main.py"]`.

#### 2. `ai-anomaly-detection/pipeline/config.py`
* **File Type:** Python configuration module
* **Purpose:** Global configuration constants for runtime intervals, sliding window size, model hyper-parameters, file paths, and namespaces.
* **Imports:** Standard Python primitives.
* **Imported by:** `collector.py`, `dashboard.py`, `feature_engineer.py`, `main.py`, `mitigator.py`, `model_manager.py`, `research_logger.py`, `state_manager.py`.
* **Actually executed?** **YES.** Imported and evaluated across all pipeline modules.
* **Evidence:** References to `config.COLLECTION_INTERVAL`, `config.WINDOW_SIZE`, `config.MODEL_PATH`, etc. throughout `pipeline/*.py`.

#### 3. `ai-anomaly-detection/pipeline/collector.py`
* **File Type:** Python module
* **Purpose:** Telemetry collection service. Queries Prometheus for cAdvisor metrics (CPU, memory, network) and Kepler metrics (Joules). Probes Kepler availability and defaults to $0.4 \times \text{CPU}$ when offline. Filters active pods via Kubernetes API. Appends rows to `raw_metrics.csv`.
* **Imports:** `csv`, `os`, `time`, `dataclasses.dataclass`, `dataclasses.asdict`, `typing.Dict`, `requests`, `config`.
* **Imported by:** `main.py`.
* **Actually executed?** **YES.** Instantiated in `startup()` in `main.py:40`.
* **Evidence:** `collector.collect_all_pods()` is called on every iteration of `main_loop()` in [`main.py:72`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L72).

#### 4. `ai-anomaly-detection/pipeline/feature_engineer.py`
* **File Type:** Python module
* **Purpose:** Per-pod sliding window manager and feature extractor. Buffers metric samples in `collections.deque(maxlen=6)`. Computes 26 statistical, slope, ratio, and variance features. Assembles vectors `features_16`, `features_8`, and `features_6`.
* **Imports:** `collections.deque`, `numpy as np`, `config`.
* **Imported by:** `main.py`, `model_manager.py`.
* **Actually executed?** **YES.** Instantiated in `startup()` in `main.py:41`.
* **Evidence:** `feature_engineer.add_sample()` and `feature_engineer.extract_features()` called on every pod in [`main.py:83, 86`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L83).

#### 5. `ai-anomaly-detection/pipeline/model_manager.py`
* **File Type:** Python module
* **Purpose:** ML management service. Collects normal baseline windows, fits dual `StandardScaler` instances, trains dual `IsolationForest` models (16-feature Energy-Aware and 6-feature Basic), evaluates decision functions, tracks consecutive anomaly counts, and writes to `evaluation.csv`.
* **Imports:** `csv`, `os`, `time`, `collections.defaultdict`, `dataclasses.dataclass`, `joblib`, `numpy as np`, `sklearn.ensemble.IsolationForest`, `sklearn.preprocessing.StandardScaler`, `config`.
* **Imported by:** `main.py`.
* **Actually executed?** **YES.** Instantiated in `startup()` in `main.py:42`.
* **Evidence:** `model_manager.predict()` called in [`main.py:101`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L101).

#### 6. `ai-anomaly-detection/pipeline/mitigator.py`
* **File Type:** Python module
* **Purpose:** Progressive automated remediation controller. Resolves owning Deployment from pod `ownerReferences`. Step 1 patches Deployment container limits (`cpu=100m`, `memory=128Mi`) via `kubectl patch` and waits for rollout. Step 2 deletes the offending pod via `kubectl delete pod` after 2 elapsed windows.
* **Imports:** `csv`, `json`, `os`, `subprocess`, `time`, `config`.
* **Imported by:** `main.py`.
* **Actually executed?** **YES.** Instantiated in `startup()` in `main.py:43`.
* **Evidence:** `mitigator.mitigate()` called in [`main.py:121`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L121) when an attack is confirmed.

#### 7. `ai-anomaly-detection/pipeline/state_manager.py`
* **File Type:** Python module
* **Purpose:** In-memory reactive state cache holding live pod metrics, detection history (`deque(maxlen=100)`), mitigation history (`deque(maxlen=50)`), metric timelines (`deque(maxlen=60)`), and model comparison counters.
* **Imports:** `collections.Counter`, `collections.deque`, `copy.deepcopy`, `time`, `config`.
* **Imported by:** `main.py`.
* **Actually executed?** **YES.** Instantiated in `startup()` in `main.py:45`.
* **Evidence:** Passed to `dashboard.create_app()` and queried on every `/api/status` call.

#### 8. `ai-anomaly-detection/pipeline/evaluator.py`
* **File Type:** Python module
* **Purpose:** Evaluates model classification metrics (Precision, Recall, F1, Accuracy, FPR, FNR, Detection Latency) from `evaluation.csv`.
* **Imports:** `json`, `os`, `dataclasses.asdict`, `dataclasses.dataclass`, `pandas as pd`.
* **Imported by:** `main.py`, `dashboard.py`.
* **Actually executed?** **YES.** Instantiated in `startup()` in `main.py:44`, invoked by `GET /api/evaluation`.
* **Evidence:** [`dashboard.py:158`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/dashboard.py#L158): `evaluator.calculate_metrics(eval_path)`.

#### 9. `ai-anomaly-detection/pipeline/research_logger.py`
* **File Type:** Python module
* **Purpose:** Append-only CSV logger for IEEE experimental telemetry. Appends 19-column records to `/app/logs/research/detection_cycles_<id>.csv` and mitigation events to `/app/logs/research/mitigation_events_<id>.csv`.
* **Imports:** `csv`, `os`, `time`, `collections.defaultdict`, `typing.Optional`, `config`.
* **Imported by:** `main.py`.
* **Actually executed?** **YES.** Instantiated in `startup()` in `main.py:46`.
* **Evidence:** Called on every detection in [`main.py:106, 122`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L106).

#### 10. `ai-anomaly-detection/pipeline/dashboard.py`
* **File Type:** Python / Flask application
* **Purpose:** Web backend serving REST API endpoints (`/api/status`, `/api/pods`, `/api/detections`, `/api/mitigations`, `/api/comparison`, `/api/metrics/history`, `/api/cluster`, `/api/training/start`, `/api/incidents/clear`, `/api/evaluation`, `/api/export/dataset`) and serving static UI assets.
* **Imports:** `flask.Flask`, `jsonify`, `render_template`, `send_file`, `flask_cors.CORS`, `io`, `json`, `os`, `requests`, `config`.
* **Imported by:** `main.py`.
* **Actually executed?** **YES.** Spawned in a daemon thread on port 8080 in [`main.py:52`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L52).

#### 11. `ai-anomaly-detection/pipeline/static/js/app.js` & `state.js` & `api.js` & `charts.js`
* **File Type:** ES6 JavaScript modules
* **Purpose:** Client-side Single Page Application (SPA). `app.js` handles routing and 5s polling; `state.js` implements reactive store (`Store`); `api.js` wraps fetch calls; `charts.js` manages Chart.js instances; `views/*.js` render DOM views.
* **Imported by:** Loaded via `<script type="module" src="/static/js/app.js">` in `index.html`.
* **Actually executed?** **YES.** Runs in the user's browser when accessing `http://localhost:8080` (or `http://localhost:30080`).

#### 12. `backend/app.py`
* **File Type:** Python / Flask application
* **Purpose:** Legitimate To-Do List REST API connected to MySQL. Defines `Task` ORM model and `TaskSchema` schema. Implements `/tasks` GET, POST, PUT, DELETE endpoints.
* **Imports:** `flask.Flask`, `request`, `jsonify`, `flask_cors.CORS`, `flask_sqlalchemy.SQLAlchemy`, `flask_marshmallow.Marshmallow`, `os`.
* **Actually executed?** **YES.** Runs inside `backend-deployment` pod on port 5000.

#### 13. `frontend/src/App.js`
* **File Type:** React JavaScript application
* **Purpose:** Legitimate To-Do List web UI. Renders task input form and task table; communicates with `backend` via axios.
* **Imports:** `react.Component`, `axios`, `./App.css`.
* **Actually executed?** **YES.** Runs inside `frontend-deployment` pod served via Nginx on port 80.

#### 14. `experiments/calculate_metrics.py`
* **File Type:** Python script
* **Purpose:** Offline evaluation script. Reads host-side `evaluation.csv` and `detection_cycles_*.csv`, computes confusion matrix metrics, and writes `results/metrics/metrics_summary.csv`.
* **Imports:** `argparse`, `pathlib.Path`, `pandas as pd`, `experiment_config`, `utils.validate_csv`.
* **Actually executed?** **YES.** Executed during experimental evaluation runs.

#### 15. `experiments/generate_graphs.py`
* **File Type:** Python script
* **Purpose:** Generates publication figures (Figures 1–10) in PNG, PDF, and SVG at 300 DPI from real experiment CSV logs.
* **Imports:** `argparse`, `warnings`, `pathlib.Path`, `matplotlib.pyplot as plt`, `numpy as np`, `pandas as pd`, `sklearn.metrics`, `experiment_config`, `utils.validate_csv`.
* **Actually executed?** **YES.** Executed during research figure generation.

#### 16. `experiments/export_metrics.py`
* **File Type:** Python script
* **Purpose:** Queries live Prometheus/Kepler instances and dumps raw pod and node metric snapshots into CSV files.
* **Imports:** `argparse`, `time`, `datetime`, `pathlib.Path`, `pandas as pd`, `requests`, `experiment_config`.
* **Actually executed?** **YES.** Executed by research pipeline.

#### 17. `experiments/run_experiment.py`
* **File Type:** Python script
* **Purpose:** Automated single-scenario test runner. Clears old attack workloads, triggers baseline collection via API, deploys attack YAML, monitors outcome, and copies pod logs to host via `kubectl cp`.
* **Imports:** `argparse`, `time`, `datetime`, `pathlib.Path`, `experiment_config`, `export_metrics`, `utils`.
* **Actually executed?** **YES.** Test automation harness.

#### 18. `experiments/run_research_pipeline.py`
* **File Type:** Python script
* **Purpose:** End-to-end multi-scenario experiment orchestrator. Sequences export metrics $\to$ run experiments $\to$ calculate metrics $\to$ generate graphs.
* **Imports:** `argparse`, `shutil`, `sys`, `datetime`, `pathlib.Path`, `experiment_config`, `export_metrics`, `calculate_metrics`, `generate_graphs`, `run_experiment`, `utils`.
* **Actually executed?** **YES.** Called by `run_research_pipeline.sh`.

#### 19. Manifests in `kubernetes/` and `ai-anomaly-detection/monitoring/` and `ai-anomaly-detection/workloads/`
* **File Type:** Kubernetes YAML specifications
* **Purpose:** Declare cluster state: services, deployments, daemonsets, PVCs, RBAC roles, ConfigMaps, and stress workloads.
* **Actually executed?** **YES.** Applied to cluster via `kubectl apply -f ...` in `deploy.sh`.

---

## PART 2 — ACTUAL SYSTEM ARCHITECTURE

### Reconstructed Component Inventory

1. **Kubernetes Cluster:** Single-node K3s cluster running on WSL2 Linux/Ubuntu ([`PROJECT_INTELLIGENCE.md:17`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/PROJECT_INTELLIGENCE.md#L17), [`deploy.sh:34`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/deploy.sh#L34)).
2. **Legitimate Application Pods (`default` namespace):**
   * `frontend-deployment-*`: React + Nginx on port 80 ([`frontend-deployment.yaml`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/kubernetes/frontend-deployment.yaml)).
   * `backend-deployment-*`: Flask API on port 5000 ([`backend-deployment.yaml`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/kubernetes/backend-deployment.yaml)).
   * `mysql-0`: StatefulSet running MySQL on port 3306 ([`mysql-deployment.yaml`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/kubernetes/mysql-deployment.yaml)).
3. **Normal Workload Pod (`default` namespace):**
   * `normal-workload-*`: 2 replicas of BusyBox executing an infinite sleep loop (`sleep 3`) to provide steady-state compute baseline ([`normal-workload.yaml`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/workloads/normal-workload.yaml)).
4. **Attack / Resource-Abuse Pods (`default` namespace):**
   * `attack-cpu-*`: `polinux/stress` running `stress --cpu 2 --timeout 600s` ([`attack-cpu.yaml`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/workloads/attack-cpu.yaml)).
   * `attack-memory-*`: `polinux/stress` running `stress --vm 1 --vm-bytes 200M --timeout 600s` ([`attack-memory.yaml`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/workloads/attack-memory.yaml)).
   * `attack-network-*`: `alexeiled/stress-ng` running `stress-ng --class network --timeout 600s` ([`attack-network.yaml`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/workloads/attack-network.yaml)).
   * `attack-combined-*`: `polinux/stress` running `stress --cpu 2 --vm 1 --vm-bytes 128M --timeout 600s` ([`attack-combined.yaml`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/workloads/attack-combined.yaml)).
   * `attack-cryptojacking-*`: `polinux/stress` running `stress --cpu 1 --cpu-method matrixprod --timeout 600s` ([`attack-cryptojacking.yaml`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/workloads/attack-cryptojacking.yaml)).
5. **Monitoring Infrastructure (`monitoring` namespace):**
   * `kepler`: DaemonSet on port 9102 extracting container energy counters via eBPF ([`kepler-daemonset.yaml`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/monitoring/kepler-daemonset.yaml)).
   * `node-exporter`: DaemonSet on host port 9100 exporting node CPU/memory metrics ([`node-exporter.yaml`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/monitoring/node-exporter.yaml)).
   * `prometheus-deployment`: Scrapes cAdvisor (15s), Kepler (5s), node-exporter (15s), and kube-state-metrics (15s) ([`update-prometheus-configmap.yaml`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/monitoring/update-prometheus-configmap.yaml)).
   * `grafana`: Web dashboard on port 3000 provisioned with Prometheus datasource and energy anomaly dashboard ([`grafana-deployment.yaml`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/monitoring/grafana-deployment.yaml)).
6. **AI Anomaly Detector Pod (`default` namespace):**
   * Container image: `todo-ai-detector:v2`
   * Service: `ai-detector-service` (NodePort 30080 / container 8080)
   * Internal subsystems: `MetricsCollector`, `FeatureEngineer`, `ModelManager`, `Mitigator`, `StateManager`, `Evaluator`, `ResearchLogger`, `Flask API Dashboard`.

### Component Details

```
+---------------------------------------------------------------------------------------------------------------------------------+
| 1. MetricsCollector (collector.py)                                                                                              |
|    - Location: ai-anomaly-detection/pipeline/collector.py                                                                       |
|    - Receives: HTTP JSON responses from Prometheus query API; K8s active pod list from https://kubernetes.default.svc          |
|    - Produces: PodSample dataclass instances; writes rows to /app/data/raw_metrics.csv                                          |
|    - Called by: main_loop() in main.py:72                                                                                       |
|    - Calls: requests.get() against Prometheus (:9090) and Kubernetes API (:443)                                                 |
|    - Active during execution: YES                                                                                               |
+---------------------------------------------------------------------------------------------------------------------------------+
                                               |
                                               v
+---------------------------------------------------------------------------------------------------------------------------------+
| 2. FeatureEngineer (feature_engineer.py)                                                                                        |
|    - Location: ai-anomaly-detection/pipeline/feature_engineer.py                                                                |
|    - Receives: Stream of PodSample objects                                                                                      |
|    - Produces: 26-feature dictionary and NumPy feature vectors (features_16, features_8, features_6)                             |
|    - Called by: main_loop() in main.py:83, 86                                                                                   |
|    - Calls: np.mean, np.var, np.std, np.max, np.min, np.polyfit                                                                  |
|    - Active during execution: YES                                                                                               |
+---------------------------------------------------------------------------------------------------------------------------------+
                                               |
                                               v
+---------------------------------------------------------------------------------------------------------------------------------+
| 3. ModelManager (model_manager.py)                                                                                              |
|    - Location: ai-anomaly-detection/pipeline/model_manager.py                                                                  |
|    - Receives: Scaled feature vectors; pod metadata                                                                             |
|    - Produces: PredictionResult dataclass; writes /app/logs/evaluation.csv and /app/model/*.pkl                                  |
|    - Called by: main_loop() in main.py:89, 101                                                                                  |
|    - Calls: StandardScaler.transform(), IsolationForest.predict(), IsolationForest.decision_function()                          |
|    - Active during execution: YES                                                                                               |
+---------------------------------------------------------------------------------------------------------------------------------+
                                               |
                                               v
+---------------------------------------------------------------------------------------------------------------------------------+
| 4. Mitigator (mitigator.py)                                                                                                     |
|    - Location: ai-anomaly-detection/pipeline/mitigator.py                                                                      |
|    - Receives: Confirmed attack pod name, namespace, anomaly score, consecutive count                                           |
|    - Produces: Remediation action strings ("THROTTLED", "DELETED"); writes /app/logs/mitigations.csv                            |
|    - Called by: main_loop() in main.py:121 (only when confirmed_attack and pod_name.startswith("attack-"))                      |
|    - Calls: kubectl patch deployment and kubectl delete pod via subprocess.run()                                                |
|    - Active during execution: YES                                                                                               |
+---------------------------------------------------------------------------------------------------------------------------------+
                                               |
                                               v
+---------------------------------------------------------------------------------------------------------------------------------+
| 5. Dashboard & StateManager (dashboard.py, state_manager.py)                                                                    |
|    - Location: ai-anomaly-detection/pipeline/dashboard.py, state_manager.py                                                     |
|    - Receives: Real-time telemetry, detection results, and mitigation actions from main_loop()                                  |
|    - Produces: JSON API responses on port 8080 / 30080; serves web UI                                                           |
|    - Called by: Web browser client (app.js) and test runner scripts                                                             |
|    - Calls: Evaluator.calculate_metrics()                                                                                       |
|    - Active during execution: YES                                                                                               |
+---------------------------------------------------------------------------------------------------------------------------------+
```

### End-to-End Architectural Hierarchy

```text
cAdvisor (kubelet) + Kepler DaemonSet (eBPF)
       │
       ▼ (Scrape: 5s / 15s)
Prometheus Server (:9090)
       │
       ▼ (HTTP GET PromQL Query every 5s)
MetricsCollector (collector.py)
       │
       ▼ (PodSample instance)
FeatureEngineer (feature_engineer.py) -> Sliding window deque(maxlen=6)
       │
       ▼ (features_16 & features_6 vectors)
ModelManager (model_manager.py) -> Dual Isolation Forest inference
       │
       ▼ (PredictionResult: consecutive anomalies >= 3 & starts with "attack-")
Mitigator (mitigator.py)
       │
       ▼ (Subprocess kubectl)
Kubernetes API Server (https://kubernetes.default.svc:443)
       │
       ▼ (Strategic-Merge Patch Deployment limits -> Wait Rollout -> Delete Pod)
Target Attack Workload Pods (Restricted / Terminated)
```

---

## PART 3 — COMPLETE DATA FLOW

### Detailed Per-Metric Data Flows

#### 1. CPU Metric Data Flow
* **Original Source:** Linux kernel cgroup CPU accounting accessed via cAdvisor embedded in Kubelet.
* **Prometheus Ingestion:** Scraped every 15 seconds from cAdvisor endpoint `/api/v1/nodes/$1/proxy/metrics/cadvisor` under metric name `container_cpu_usage_seconds_total`.
* **Collection:** `MetricsCollector._by_pod()` in [`collector.py:125`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/collector.py#L125) executes PromQL:
  `sum by(pod)(rate(container_cpu_usage_seconds_total{namespace="default",pod!=""}[30s]))`
* **Preprocessing:** Stored as float `cpu_cores` in `PodSample`. Written to `raw_metrics.csv`.
* **Windowing:** Appended to `FeatureEngineer.windows[pod_name]` (`deque(maxlen=6)`).
* **Feature Extraction:**
  * `avg_cpu = float(np.mean(cpu_values))`
  * `max_cpu = float(np.max(cpu_values))`
  * `min_cpu = float(np.min(cpu_values))`
  * `cpu_variance = float(np.var(cpu_values))`
  * `cpu_slope = float(np.polyfit(x, cpu_values, 1)[0])`
  * `cpu_peak_ratio = float(max_cpu / (avg_cpu + 1e-6))`
* **ML Model:** Vectorized into `features_16` (indices 0, 4, 8, 9, 10) and `features_6` (indices 0, 3). Scaled via `StandardScaler.transform()`. Fed to `IsolationForest.predict()` and `decision_function()`.
* **Score & Decision:** Produces `score_ea` and `score_basic`. Anomaly detected if score $< 0$ (`raw_pred_ea == -1`).
* **Validation:** Must repeat for 3 consecutive windows before triggering progressive mitigation.
* **Mitigation:** Deployment patched with `cpu: 100m` limit.
* **Dashboard / Logging:** Logged in `detections.csv`, `evaluation.csv`, and rendered on `/api/status`.

#### 2. Memory Metric Data Flow
* **Original Source:** Linux kernel cgroup memory accounting via cAdvisor.
* **Prometheus Ingestion:** Scraped from cAdvisor under metric `container_memory_working_set_bytes`.
* **Collection:** `MetricsCollector._by_pod()` in [`collector.py:126`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/collector.py#L126) executes PromQL:
  `sum by(pod)(container_memory_working_set_bytes{namespace="default",pod!=""})`
* **Preprocessing:** Stored in bytes `memory_bytes` and converted to megabytes `memory_mb = memory_bytes / (1024 * 1024)`. Written to `raw_metrics.csv`.
* **Windowing:** Appended to `FeatureEngineer.windows[pod_name]`.
* **Feature Extraction:**
  * `avg_memory_mb = float(np.mean(mem_values))`
  * `max_memory = float(np.max(mem_values))`
  * `memory_variance = float(np.var(mem_values))`
  * `cpu_memory_ratio = float(avg_cpu / (avg_memory + 1e-6))`
  * `energy_density = float(avg_energy / (avg_memory + 1e-6))`
* **ML Model:** Scaled and evaluated by both models.
* **Mitigation:** Deployment patched with `memory: 128Mi` limit.

#### 3. Network Metric Data Flow
* **Original Source:** Linux network namespace virtual interface packet counters via cAdvisor.
* **Prometheus Ingestion:** Metrics `container_network_receive_bytes_total` and `container_network_transmit_bytes_total`.
* **Collection:** [`collector.py:127-128`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/collector.py#L127-L128) executes PromQL:
  `sum by(pod)(rate(container_network_receive_bytes_total{namespace="default",pod!=""}[30s]))`
  `sum by(pod)(rate(container_network_transmit_bytes_total{namespace="default",pod!=""}[30s]))`
* **Preprocessing:** Stored as `network_rx_bytes_per_sec` and `network_tx_bytes_per_sec`.
* **Windowing:** Summed per sample: `net_values = rx + tx`.
* **Feature Extraction:**
  * `avg_network = float(np.mean(net_values))`
  * `max_network = float(np.max(net_values))`
  * `network_variance = float(np.var(net_values))`
* **ML Model:** Evaluated in `features_16` (indices 7, 15) and `features_6` (indices 2, 5).

#### 4. Energy Metric Data Flow
* **Original Source:** Kepler eBPF probe reading kernel hardware counters/RAPL; when running on WSL2 without kernel energy counters, source is the calibrated software fallback.
* **Prometheus Ingestion:** Kepler DaemonSet exposes `/metrics` on port 9102; scraped every 5 seconds under `kepler_container_joules_total`.
* **Collection:** [`collector.py:134-137`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/collector.py#L134-L137) executes PromQL:
  `sum by(container_name)(rate(kepler_container_joules_total{namespace="default"}[30s]))`
* **Fallback Calculation (Verified Active in Stored Logs):**
  If Kepler query returns empty results:
  $$\text{energy\_joules} = \text{cpu\_cores} \times 0.4$$
  Tagged with `energy_source = "estimated"`.
* **Windowing:** Appended to pod deque.
* **Feature Extraction:**
  * `avg_energy = float(np.mean(energy_values))`
  * `max_energy = float(np.max(energy_values))`
  * `energy_variance = float(np.var(energy_values))`
  * `energy_slope = float(np.polyfit(x, energy_values, 1)[0])`
* **ML Model:** Fed exclusively to the Energy-Aware Isolation Forest (`features_16`). **Completely excluded from the Basic Isolation Forest (`features_6`).**

#### 5. Energy-to-CPU Ratio Data Flow
* **Original Source:** Derived cross-metric calculation.
* **Calculation:** Computed in [`feature_engineer.py:104`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/feature_engineer.py#L104):
  $$\text{energy\_cpu\_ratio} = \frac{\text{avg\_energy}}{\text{avg\_cpu} + 10^{-6}}$$
* **Feature Vector:** Positioned at index 3 in `features_16` and `features_8`.
* **Role:** Primary discriminating signal for detecting cryptojacking and compute-energy divergence.

---

## PART 4 — MONITORING IMPLEMENTATION

### Audit Specification

* **FILE:** [`ai-anomaly-detection/pipeline/collector.py`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/collector.py)
* **FUNCTION:** `MetricsCollector.collect_all_pods()` ([`collector.py:123-169`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/collector.py#L123-L169))
* **COLLECTION INTERVAL:** Every 5 seconds (`config.COLLECTION_INTERVAL = 5` in [`config.py:3`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L3), timed by `time.sleep(config.COLLECTION_INTERVAL)` in [`main.py:140`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L140)).
* **POLLING MECHANISM:** Synchronous HTTP GET requests executed serially in `collect_all_pods()`.
* **PROMETHEUS QUERIES USED:**
  * CPU: `sum by(pod)(rate(container_cpu_usage_seconds_total{namespace="default",pod!=""}[30s]))`
  * Memory: `sum by(pod)(container_memory_working_set_bytes{namespace="default",pod!=""})`
  * Network RX: `sum by(pod)(rate(container_network_receive_bytes_total{namespace="default",pod!=""}[30s]))`
  * Network TX: `sum by(pod)(rate(container_network_transmit_bytes_total{namespace="default",pod!=""}[30s]))`
  * Kepler Energy: `sum by(container_name)(rate(kepler_container_joules_total{namespace="default"}[30s]))`
* **KEPLER DETECTION & FALLBACK:**
  * Probing function: `MetricsCollector._detect_kepler()` queries `kepler_container_joules_total` on startup.
  * Fallback: If `results` is empty or query fails, `self.kepler_available = False`. Energy defaults to `cpu_cores * 0.4` with tag `"estimated"`.
* **KUBERNETES LIVE POD FILTER:**
  * Function `_live_pods_from_k8s(namespace)` queries `GET https://kubernetes.default.svc/api/v1/namespaces/{namespace}/pods` using token at `/var/run/secrets/kubernetes.io/serviceaccount/token` and CA cert at `/var/run/secrets/kubernetes.io/serviceaccount/ca.crt`.
  * Drops pods marked with `.metadata.deletionTimestamp` or not in phase `Running`/`Pending`.
* **MISSING-VALUE HANDLING:**
  * Prometheus parsing helper `_f(value)` catches exceptions and returns `0.0`.
  * Pod metric lookups use dictionary `.get(pod, 0.0)`.
* **RETRY MECHANISMS:**
  * Function `_test_prometheus_connection()` loops 5 times with 3-second sleep intervals upon initial connection failure before raising `RuntimeError`.

---

## PART 5 — 30-SECOND WINDOW

### Window Implementation Verification

* **Is it actually 30 seconds?** **YES.** Exactly $6\text{ samples} \times 5\text{ seconds/sample} = 30\text{ seconds}$.
* **Where implemented?** [`ai-anomaly-detection/pipeline/feature_engineer.py:16-43`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/feature_engineer.py#L16-L43).
* **Controlling variables:**
  * `config.WINDOW_SIZE = 6` ([`config.py:4`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L4))
  * `config.COLLECTION_INTERVAL = 5` ([`config.py:3`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L3))
* **Sampling frequency:** Exactly once every 5 seconds.
* **Samples per window:** Exactly 6 samples.
* **Tumbling or Sliding?** **SLIDING WINDOW.**
* **Window overlap:** Overlaps by 5 samples ($83.33\%$) on every 5-second cycle after initial fill.
* **Buffer data structure:** `collections.deque(maxlen=6)` initialized per pod in `FeatureEngineer.windows`.
* **Completion condition:** `len(self.windows[pod_name]) == config.WINDOW_SIZE` (evaluates to `True` on and after sample 6).
* **Handling of old samples:** The `collections.deque(maxlen=6)` automatically drops the oldest sample from the left (`popleft()`) whenever a 7th sample is appended.
* **Statistical calculations:** NumPy computes `mean`, `max`, `min`, `std`, `var`, `polyfit` (slope), peak ratios, and cross-resource ratios over the 6 buffered samples.

### Step-by-Step Chronological Window Execution Trace

```text
t =  0s : Collector gathers Sample 1 -> Deque: [S1]                 (len=1 < 6 -> Window incomplete, skip detection)
t =  5s : Collector gathers Sample 2 -> Deque: [S1, S2]             (len=2 < 6 -> Window incomplete, skip detection)
t = 10s : Collector gathers Sample 3 -> Deque: [S1, S2, S3]         (len=3 < 6 -> Window incomplete, skip detection)
t = 15s : Collector gathers Sample 4 -> Deque: [S1, S2, S3, S4]     (len=4 < 6 -> Window incomplete, skip detection)
t = 20s : Collector gathers Sample 5 -> Deque: [S1..S5]             (len=5 < 6 -> Window incomplete, skip detection)
t = 25s : Collector gathers Sample 6 -> Deque: [S1, S2, S3, S4, S5, S6]
          - add_sample() returns True (Window complete: exactly 30s covered)
          - extract_features() extracts 26 metrics from [S1..S6]
          - Model inference executes.
t = 30s : Collector gathers Sample 7 -> Deque auto-drops S1: [S2, S3, S4, S5, S6, S7]
          - add_sample() returns True (Sliding window advances by 5s)
          - extract_features() extracts 26 metrics from [S2..S7]
          - Model inference executes.
```

---

## PART 6 — FEATURE ENGINEERING

### Complete Feature Inventory

Extracted in [`ai-anomaly-detection/pipeline/feature_engineer.py:46-211`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/feature_engineer.py#L46-L211) over window array $W$ of length $N = 6$ ($x = [0, 1, 2, 3, 4, 5]$, $\epsilon = 10^{-6}$):

| Feature Name | Source Telemetry | Exact Formula in Code | Unit | Operation / Transformation |
| :--- | :--- | :--- | :--- | :--- |
| `avg_cpu` | `s.cpu_cores` | `float(np.mean(cpu_values))` | Cores | Window arithmetic mean |
| `max_cpu` | `s.cpu_cores` | `float(np.max(cpu_values))` | Cores | Window maximum |
| `min_cpu` | `s.cpu_cores` | `float(np.min(cpu_values))` | Cores | Window minimum |
| `std_cpu` | `s.cpu_cores` | `float(np.std(cpu_values))` | Cores | Standard deviation |
| `cpu_variance` | `s.cpu_cores` | `float(np.var(cpu_values))` | $\text{Cores}^2$ | Variance |
| `cpu_slope` | `s.cpu_cores` | `float(np.polyfit(x, cpu_values, 1)[0])` | Cores/step | Linear regression slope |
| `cpu_peak_ratio` | `max_cpu`, `avg_cpu` | `float(max_cpu / (avg_cpu + 1e-6))` | Dimensionless | Peak-to-mean ratio |
| `cpu_range` | `max_cpu`, `min_cpu` | `float(max_cpu - min_cpu)` | Cores | Peak-to-peak amplitude |
| `avg_memory_mb` | `s.memory_mb` | `float(np.mean(mem_values))` | Megabytes | Window arithmetic mean |
| `max_memory` | `s.memory_mb` | `float(np.max(mem_values))` | Megabytes | Window maximum |
| `std_memory` | `s.memory_mb` | `float(np.std(mem_values))` | Megabytes | Standard deviation |
| `memory_variance`| `s.memory_mb` | `float(np.var(mem_values))` | $\text{MB}^2$ | Variance |
| `avg_energy` | `s.energy_joules` | `float(np.mean(energy_values))` | Joules | Window arithmetic mean |
| `max_energy` | `s.energy_joules` | `float(np.max(energy_values))` | Joules | Window maximum |
| `std_energy` | `s.energy_joules` | `float(np.std(energy_values))` | Joules | Standard deviation |
| `energy_variance`| `s.energy_joules` | `float(np.var(energy_values))` | $\text{J}^2$ | Variance |
| `energy_slope` | `s.energy_joules` | `float(np.polyfit(x, energy_values, 1)[0])`| J/step | Linear regression slope |
| `energy_peak_ratio`| `max_energy`, `avg_energy`| `float(max_energy / (avg_energy + 1e-6))`| Dimensionless | Peak-to-mean ratio |
| `avg_network` | `s.network_rx + tx`| `float(np.mean(net_values))` | Bytes/sec | Window arithmetic mean |
| `max_network` | `s.network_rx + tx`| `float(np.max(net_values))` | Bytes/sec | Window maximum |
| `network_variance`| `s.network_rx + tx`| `float(np.var(net_values))` | $(\text{B/s})^2$ | Variance |
| `energy_cpu_ratio`| `avg_energy`, `avg_cpu`| `float(avg_energy / (avg_cpu + 1e-6))`| J / Core | Cross-resource coupling |
| `cpu_memory_ratio`| `avg_cpu`, `avg_mem` | `float(avg_cpu / (avg_memory + 1e-6))`| Cores / MB | Cross-resource coupling |
| `energy_density` | `avg_energy`, `avg_mem`| `float(avg_energy / (avg_memory + 1e-6))`| J / MB | Cross-resource coupling |
| `rolling_cpu_avg` | `s.cpu_cores` | `float(np.mean(cpu_values[-3:]))` | Cores | Sub-window mean (last 3 samples) |
| `rolling_energy_avg`| `s.energy_joules` | `float(np.mean(energy_values[-3:]))` | Joules | Sub-window mean (last 3 samples) |

### Final ML Feature Vectors Passed to Models

#### 1. Energy-Aware Model Feature Vector (`features_16`)
Passed to `model_energy_aware` ([`feature_engineer.py:169-186`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/feature_engineer.py#L169-L186)):
```python
[
    avg_cpu,              # 0
    avg_memory_mb,        # 1
    avg_energy,           # 2
    energy_cpu_ratio,     # 3
    cpu_variance,         # 4
    memory_variance,      # 5
    energy_variance,      # 6
    avg_network,          # 7
    max_cpu,              # 8
    cpu_slope,            # 9
    cpu_peak_ratio,       # 10
    max_energy,           # 11
    energy_slope,         # 12
    cpu_memory_ratio,     # 13
    energy_density,       # 14
    max_network           # 15
]
```

#### 2. Basic Model Baseline Feature Vector (`features_6`)
Passed to `model_basic` ([`feature_engineer.py:192-199`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/feature_engineer.py#L192-L199)):
```python
[
    avg_cpu,              # 0
    avg_memory_mb,        # 1
    avg_network,          # 2
    cpu_variance,         # 3
    memory_variance,      # 4
    network_variance      # 5
]
```

---

## PART 7 — RULE-BASED FILTERING / PREPROCESSING

### Audit of All Rules in Codebase

| Rule / Condition | Threshold | Unit | File & Line | Purpose | Action When TRUE | Action When FALSE |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `namespace in config.SYSTEM_NAMESPACES` | `["kube-system", "monitoring", "kube-public"]` | Strings | [`main.py:34`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L34) | Ignore system pods | Pod skipped from monitoring | Pod evaluated |
| `pod_name.startswith(prefix)` | `["ai-detector-", "mysql-"]` | Strings | [`main.py:36`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L36) | Self-monitoring & DB protection | Pod skipped from monitoring | Pod evaluated |
| `is_attack_pod` during baseline | Starts with `"attack-"` | String | [`model_manager.py:85`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/model_manager.py#L85) | Contamination prevention | Window discarded from baseline | Window evaluated |
| Startup window suppression | `pod_seen_counts <= 2` | Windows | [`model_manager.py:91`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/model_manager.py#L91) | Filter container start transients | Window dropped | Window added to buffer |
| Baseline completion check | `min(training_counts.values()) >= 30` | Windows | [`model_manager.py:120`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/model_manager.py#L120) | Ensure sufficient baseline | Trains models; enters `DETECTING` | Continues baseline collection |
| Consecutive anomaly count | `consecutive_count >= 3` | Windows | [`model_manager.py:226`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/model_manager.py#L226) | False positive suppression | Sets `confirmed_attack = True` | Sets `confirmed_attack = False` |
| Consecutive reset rule | `raw_pred_ea != -1` | Enum | [`model_manager.py:224`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/model_manager.py#L224) | Reset counter on normal window | `consecutive_count[pod] = 0` | `consecutive_count[pod] += 1` |
| Automated mitigation gate | `result.confirmed_attack and pod.startswith("attack-")` | Boolean & String | [`main.py:118`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L118) | Safety check against terminating app | Calls `mitigator.mitigate()` | No mitigation action taken |
| Stale pod eviction | `now - timestamp > 15s` | Seconds | [`main.py:132`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L132), [`state_manager.py:62`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/state_manager.py#L62) | Evict dead pods from live state | Pod evicted from `state_manager.pods` | Pod retained in live view |

* **CRITICAL FINDING ON DISABLED RULES:**
  `config.MIN_ATTACK_CPU = 0.3` and `config.MIN_ATTACK_ENERGY = 0.1` are defined in `config.py:20-21`, but are **NOT ENFORCED** in `model_manager.py:217-218`. The source code explicitly states:
  *"Static behavioral thresholds caused excessive false positives on normal backend/todo pods, so they are retained only for logging/research context."*

---

## PART 8 — ISOLATION FOREST IMPLEMENTATION

### Model Details

* **Library:** `scikit-learn==1.3.2`
* **Class:** `sklearn.ensemble.IsolationForest`
* **Preprocessing:** `sklearn.preprocessing.StandardScaler`
* **Supervision Type:** **UNSUPERVISED.** Fits exclusively on unlabeled baseline data collected when only legitimate workloads run.

### Exact Hyperparameters ([`config.py:11-16`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L11-L16), [`model_manager.py:137-153`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/model_manager.py#L137-L153))
* `n_estimators`: `100` (`config.N_ESTIMATORS = 100`)
* `contamination`: `0.1` (`config.CONTAMINATION = 0.1`)
* `random_state`: `42` (`config.RANDOM_STATE = 42`)
* `bootstrap`: `False` (`config.MODEL_BOOTSTRAP = False`)
* `max_samples`: `"auto"` (scikit-learn default: $\min(256, n)$)
* `max_features`: `1.0` (all features evaluated)
* `n_jobs`: `-1` (all CPU cores utilized)

### Training Flow ([`model_manager.py:123-174`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/model_manager.py#L123-L174))
1. `X_16` and `X_6` assembled from in-memory buffers.
2. `StandardScaler` fitted on each matrix (`scaler_16.fit(X_16)`, `scaler_6.fit(X_6)`).
3. `X_16_scaled = scaler_16.transform(X_16)` and `X_6_scaled = scaler_6.transform(X_6)`.
4. `model_energy_aware.fit(X_16_scaled)` and `model_basic.fit(X_6_scaled)`.
5. Models and scalers dumped via `joblib.dump()` to `/app/model/*.pkl`.
6. Training data exported to `/app/data/training_data.csv`.
7. State transitions to `DETECTING`.

### Detection Flow ([`model_manager.py:196-242`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/model_manager.py#L196-L242))
1. Ingests raw `features_16` and `features_6`.
2. Scales via `scaler_16.transform()` and `scaler_6.transform()`.
3. Calls `.predict()`: $+1 \to \text{"NORMAL"}$, $-1 \to \text{"ANOMALY"}$.
4. Calls `.decision_function()`: extracts raw floating-point score (negative indicates outlier).
5. Primary anomaly flag: `is_anomalous_ea = (raw_pred_ea == -1)`.
6. Result packaged into `PredictionResult` and appended to `/app/logs/evaluation.csv`.

---

## PART 9 — TRAINING DATA

### Data Specifications

* **Data Type:** **Live normal data only.** Attacks are explicitly excluded. No synthetic data is generated.
* **Attack Exclusion:** [`model_manager.py:85`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/model_manager.py#L85):
  `is_attack = any(pod_name.startswith(prefix) for prefix in config.ATTACK_POD_PREFIXES)`
  `if is_attack: return`
* **Startup Suppression:** First 2 windows observed per pod discarded (`config.IGNORE_STARTUP_WINDOWS = 2`).
* **Training Trigger:** Initiated via UI click `Start Baseline Training` (`POST /api/training/start`).
* **Minimum Windows Required:** Controlled by `config.MIN_TRAINING_WINDOWS = 30` in [`config.py:7`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L7).
* **Per-Pod Completion Condition:** Baseline training does **NOT** trigger when the total buffer reaches 30. It triggers only when **each observed normal pod** has contributed at least 30 valid windows:
  `min(self.training_counts.values()) >= config.MIN_TRAINING_WINDOWS` ([`model_manager.py:120`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/model_manager.py#L120)).
  For 4 pods, this generates $\ge 120$ windows ($30 \times 4$).

---

## PART 10 — ANOMALY VALIDATION

### Consecutive Window Verification

* **Counter Variable:** `self.consecutive_count[pod_name]` in `ModelManager`.
* **Threshold Variable:** `config.ANOMALY_CONFIRMATION_THRESHOLD = 3` in [`config.py:18`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L18).
* **Exact Logic ([`model_manager.py:219-226`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/model_manager.py#L219-L226)):**
  ```python
  is_anomalous_ea = raw_pred_ea == -1

  if is_anomalous_ea:
      self.consecutive_count[pod_name] += 1
  else:
      self.consecutive_count[pod_name] = 0

  confirmed = self.consecutive_count[pod_name] >= config.ANOMALY_CONFIRMATION_THRESHOLD
  ```
* **Consecutive Progression:**
  * Window 1 flagged anomalous $\to$ `consecutive_count = 1`, `confirmed = False` (Yellow warning).
  * Window 2 flagged anomalous $\to$ `consecutive_count = 2`, `confirmed = False` (Yellow warning).
  * Window 3 flagged anomalous $\to$ `consecutive_count = 3`, `confirmed = True` (Red confirmed attack alert).
* **Cooldown / Reset Behavior:** Immediate reset to `0` upon any single normal window. No decay or hysteresis.

---

## PART 11 — MITIGATION

### Progressive 2-Stage Mitigation Implementation

* **Trigger:** `result.confirmed_attack == True` AND `pod_name.startswith("attack-")` in [`main.py:118`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L118).
* **Target:** Owning Deployment of the offending pod.
* **Why Deployment instead of Pod?** Documented in [`mitigator.py:18-21`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/mitigator.py#L18-L21): Kubernetes rejects direct patches to running pod resource limits with HTTP 422. Patching the Deployment template updates the spec legally.

### Exact Progression Sequence

```text
Step 1: First Confirmation (pod not in throttled_pods)
  1. Resolves Pod -> ReplicaSet -> Deployment via ownerReferences JSONPath.
  2. Resolves container name from Deployment pod template.
  3. Strategic-merge patch applied to Deployment:
     limits: {cpu: "100m", memory: "128Mi"}
  4. Waits for rollout: kubectl rollout status deployment/<name> --timeout=120s
  5. Registers pod in self.throttled_pods with windows_since_throttle = 0.
  6. Logs action="THROTTLED", status="SUCCESS" to mitigations.csv.

Step 2: Subsequent Windows (windows_since_throttle increments on each window)
  1. Window 1 after throttle: windows_since_throttle = 1 < 2 (Observation window).
  2. Window 2 after throttle: windows_since_throttle = 2 >= THROTTLE_DURATION_WINDOWS (2).
  3. Deletion executed: kubectl delete pod <pod_name> -n default.
  4. Offending pod evicted from self.throttled_pods.
  5. Logs action="DELETED", status="SUCCESS" to mitigations.csv.
  6. Kubernetes Deployment controller spawns replacement pod adhering to throttled limits (cpu<=100m, mem<=128Mi).
```

---

## PART 12 — KUBERNETES IMPLEMENTATION

### Cluster Configuration & Manifest Audit

* **Cluster Type:** K3s v1.34+ single-node cluster running locally in WSL2.
* **Namespaces:**
  * `default`: Application, detector, and attack workloads.
  * `monitoring`: Prometheus, Kepler, Node Exporter, Grafana.
* **Deployments:**
  * `ai-detector`: 1 replica, image `todo-ai-detector:v2`, serviceAccount `ai-detector`, mounts PVCs `model` (1Gi), `logs` (1Gi), `data` (2Gi). Limits: `cpu: 500m`, `memory: 512Mi`. Requests: `cpu: 200m`, `memory: 256Mi`.
  * `backend-deployment`: 1 replica, image `todo-backend:latest`, port 5000.
  * `frontend-deployment`: 1 replica, image `todo-frontend-react:latest`, port 80.
  * `normal-workload`: 2 replicas, image `busybox:1.35`, limits `cpu: 100m`, `memory: 64Mi`.
  * `attack-cpu`: 1 replica, image `polinux/stress`, limits `cpu: 2000m`, `memory: 128Mi`.
  * `attack-memory`: 1 replica, image `polinux/stress`, limits `cpu: 500m`, `memory: 300Mi`.
  * `attack-network`: 1 replica, image `alexeiled/stress-ng`, limits `cpu: 1000m`, `memory: 128Mi`.
  * `attack-combined`: 1 replica, image `polinux/stress`, limits `cpu: 2000m`, `memory: 300Mi`.
  * `attack-cryptojacking`: 1 replica, image `polinux/stress`, limits `cpu: 1500m`, `memory: 128Mi`.
  * `grafana`: 1 replica, image `grafana/grafana:9.5.2`, port 3000.
* **StatefulSets:**
  * `mysql`: 1 replica, image `mysql:latest`, port 3306, PVC template 1Gi.
* **DaemonSets:**
  * `kepler`: Privileged container, hostPID, mounts `/proc`, `/sys`, `/var/lib/kubelet/pod-resources`, port 9102.
  * `node-exporter`: Privileged container, hostNetwork, hostPID, mounts `/proc`, `/sys`, `/`, port 9100.
* **RBAC:**
  * `ai-detector-role`: ClusterRole granting `get`, `list`, `watch`, `delete`, `patch` on `pods`; `get`, `list`, `watch` on `nodes`; `get`, `list` on `namespaces`; `create` on `pods/exec`. Bound to `ai-detector` ServiceAccount in `default`.
  * `kepler-role`: ClusterRole granting `get`, `list`, `watch` on `nodes`, `pods`, `namespaces`. Bound to `kepler-sa` in `monitoring`.

---

## PART 13 — ATTACK / RESOURCE ABUSE SIMULATION

All attack workloads represent **controlled, deterministic stress tests** packaged as standard Kubernetes Deployment manifests:

1. **CPU Stress (`workloads/attack-cpu.yaml`):**
   * Container image: `polinux/stress`
   * Command: `["stress", "--cpu", "2", "--timeout", "600s"]`
   * Effect: Spawns 2 CPU worker threads driving core usage to 2.0 cores.
2. **Memory Abuse (`workloads/attack-memory.yaml`):**
   * Container image: `polinux/stress`
   * Command: `["stress", "--vm", "1", "--vm-bytes", "200M", "--timeout", "600s"]`
   * Effect: Allocates 200 MB virtual memory via malloc/free spinning.
3. **Network Stress (`workloads/attack-network.yaml`):**
   * Container image: `alexeiled/stress-ng`
   * Command: `["stress-ng", "--class", "network", "--timeout", "600s"]`
   * Effect: Floods loopback/socket interfaces with network traffic.
4. **Combined Attack (`workloads/attack-combined.yaml`):**
   * Container image: `polinux/stress`
   * Command: `["stress", "--cpu", "2", "--vm", "1", "--vm-bytes", "128M", "--timeout", "600s"]`
   * Effect: Simultaneous 2 CPU workers and 128 MB VM worker.
5. **Cryptojacking Simulation (`workloads/attack-cryptojacking.yaml`):**
   * Container image: `polinux/stress`
   * Command: `["stress", "--cpu", "1", "--cpu-method", "matrixprod", "--timeout", "600s"]`
   * Effect: Continuous square matrix multiplication simulating cryptographic proof-of-work hash calculations.
* **Automation:** Managed by `experiments/run_experiment.py:102` (`apply_workload()`) and cleanup scripts (`cleanup_attacks.sh`).

---

## PART 14 — DATABASE / LOGGING

### Storage Mechanism Inventory

| Mechanism / Technology | File / Path | Schema / Fields | Purpose |
| :--- | :--- | :--- | :--- |
| **MySQL 8.0** (StatefulSet) | Port 3306 on `mysql-service` | `tasks(id INT PK, title VARCHAR(100), done BOOL)` | Legitimate application storage for To-Do tasks. (Not used by AI detector). |
| **Raw Telemetry CSV** | `/app/data/raw_metrics.csv` | `timestamp, pod_name, namespace, cpu_cores, memory_bytes, memory_mb, network_rx_bytes_per_sec, network_tx_bytes_per_sec, energy_joules, energy_source, is_attack_pod` | Raw metric archive written on every 5s polling cycle. |
| **Training Data CSV** | `/app/data/training_data.csv` | `model, f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15, f16` | Persisted feature vectors used to fit the models. |
| **Detection Log CSV** | `/app/logs/detections.csv` | `timestamp, pod, cpu, mem_mb, energy, e_cpu, ea, basic, score, consecutive` | Summary prediction log appended on each window evaluation. |
| **Evaluation Log CSV** | `/app/logs/evaluation.csv` | `timestamp, pod_name, prediction_ea, score_ea, prediction_basic, score_basic, consecutive_count, confirmed_attack, true_label, avg_cpu, avg_memory_mb, avg_energy, energy_cpu_ratio, cpu_variance, memory_variance, energy_variance, avg_network, avg_network_variance` | Detailed feature and prediction log used for IEEE metrics calculation. |
| **Mitigation Log CSV** | `/app/logs/mitigations.csv` | `timestamp, pod_name, action, status, score` | Audit trail of throttling and deletion actions. |
| **Research Detection CSV** | `/app/logs/research/detection_cycles_<id>.csv` | 19 fields including latencies, confidence, resource percentages. | High-fidelity IEEE paper reproduction data. |
| **Research Mitigation CSV** | `/app/logs/research/mitigation_events_<id>.csv` | `timestamp, pod_name, mitigation_action` | High-fidelity mitigation timestamps. |
| **Model Binaries** | `/app/model/*.pkl` | Serialized scikit-learn models and scalers | Persistent model weights loaded across pod restarts. |
| **In-Memory Ring Buffers** | `StateManager` | `detection_history` (maxlen=100), `mitigation_history` (maxlen=50), `metrics_timeline` (maxlen=60) | Live UI state feeding web browser dashboard. |

---

## PART 15 — DASHBOARD / FRONTEND

### Implementation Audit

* **Framework:** Flask 3.0.0 backend with Jinja2 template (`templates/index.html`); Vanilla ES6 JavaScript frontend with Chart.js 4.
* **Entry Point:** `http://localhost:8080` (or `http://localhost:30080` via NodePort).
* **Refresh Mechanism:** Client-side `setInterval(this.refresh, 5000)` in [`static/js/app.js:219`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/static/js/app.js#L219) polling `GET /api/status`.
* **API Endpoints Implemented in [`dashboard.py`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/dashboard.py):**
  * `GET /api/status`: Returns state, training progress, active incidents, comparison statistics, and pod metrics.
  * `GET /api/pods`: Returns dictionary of live monitored pods.
  * `GET /api/detections`: Returns last 100 detections from deque.
  * `GET /api/mitigations`: Returns last 50 mitigations from deque.
  * `GET /api/comparison`: Returns side-by-side stats (Energy-Aware vs Basic detections and false positives).
  * `GET /api/metrics/history`: Returns time series metric arrays per pod.
  * `GET /api/cluster`: Queries Kubernetes API for node readiness and roles.
  * `POST /api/training/start`: Resets runtime logs and initiates baseline collection.
  * `POST /api/incidents/clear`: Clears in-memory incident list without retraining models.
  * `GET /api/evaluation`: Computes and returns IEEE classification metrics from `evaluation.csv`.
  * `GET /api/export/dataset`: Streams `raw_metrics.csv` to user as a download.
* **Views Rendered:**
  * Overview: System status cards, baseline progress, live pod summary table.
  * Monitoring: Live line charts for CPU, memory, energy, and network throughput.
  * Detection: Energy-Aware vs Basic comparison cards and anomaly score timeline scatter plot.
  * Incidents: Active confirmed incidents table with alert badges.
  * Mitigation: Mitigation event log table (`THROTTLED`, `DELETED`).
  * Kubernetes: Cluster node health and namespace status.
  * Research: IEEE metric card summary, confusion matrix display, and dataset export button.

---

## PART 16 — EXPERIMENTAL PIPELINE

### Experiment Harness Implementation

Managed by scripts in [`experiments/`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/experiments):
* **Orchestrator:** `experiments/run_research_pipeline.py` (wrapped by `run_research_pipeline.sh`).
* **Scenarios Supported ([`experiments/experiment_config.py:46-77`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/experiments/experiment_config.py#L46-L77)):**
  1. `normal`: Control scenario (no attacks deployed).
  2. `cpu`: Deploys `attack-cpu.yaml`.
  3. `memory`: Deploys `attack-memory.yaml`.
  4. `network`: Deploys `attack-network.yaml`.
  5. `combined`: Deploys `attack-combined.yaml`.
  6. `cryptojacking`: Deploys `attack-cryptojacking.yaml`.
* **Execution Flow (`run_experiment.py`):**
  1. Health check on detector API (`/api/status`).
  2. Deletes any pre-existing attack workloads.
  3. Triggers baseline training via `POST /api/training/start`.
  4. Waits until detector state transitions to `DETECTING`.
  5. Exports baseline Prometheus snapshot to CSV.
  6. Applies attack YAML workload; waits 20 seconds.
  7. Exports attack-phase Prometheus snapshot to CSV.
  8. Polls `/api/detections` and `/api/mitigations` until mitigation occurs or timeout expires.
  9. Copies container logs to host using `kubectl cp` (`evaluation.csv`, `detections.csv`, `mitigations.csv`, `raw_metrics.csv`, `research/*.csv`).
  10. Saves `experiment_summary.json` and `metadata.json`.

---

## PART 17 — BASELINE METHODS

### Implementation Audit Across Repository

1. **Basic Isolation Forest (Baseline 1):**
   * **Implementation File:** [`ai-anomaly-detection/pipeline/model_manager.py:146-153`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/model_manager.py#L146-L153).
   * **Algorithm:** `sklearn.ensemble.IsolationForest`.
   * **Features (6 non-energy features):** `[avg_cpu, avg_memory_mb, avg_network, cpu_variance, memory_variance, network_variance]`.
   * **Parameters:** `n_estimators=100`, `contamination=0.1`, `random_state=42`, `max_samples="auto"`.
   * **Status:** **FULLY IMPLEMENTED AND RUNS IN PARALLEL** with the Energy-Aware model on every window.
2. **CPU-Only Static Threshold:**
   * Variable `MIN_ATTACK_CPU = 0.3` exists in `config.py:20`.
   * **Status:** **NOT ACTIVE AS A DECISION GATE.** Explicitly disabled in `model_manager.py:217` to prevent false alarms on legitimate backend traffic.
3. **Energy-Only Static Threshold:**
   * Variable `MIN_ATTACK_ENERGY = 0.1` exists in `config.py:21`.
   * **Status:** **NOT ACTIVE AS A DECISION GATE.**
4. **One-Class SVM (OC-SVM):**
   * **Status:** **NOT FOUND IN SOURCE CODE.** Mentioned only in literature review in `PROJECT_INTELLIGENCE.md`.
5. **Local Outlier Factor (LOF):**
   * **Status:** **NOT FOUND IN SOURCE CODE.** Mentioned only in literature review in `PROJECT_INTELLIGENCE.md`.

---

## PART 18 — EVALUATION

### Mathematical Metric Definitions in Code ([`evaluator.py:25-38`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/evaluator.py#L25-L38), [`calculate_metrics.py:25-51`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/experiments/calculate_metrics.py#L25-L51))

* **True Positive ($TP$):** `true_label == 1` AND `pred == 1` (`"ANOMALY"`)
* **True Negative ($TN$):** `true_label == 0` AND `pred == 0` (`"NORMAL"`)
* **False Positive ($FP$):** `true_label == 0` AND `pred == 1` (`"ANOMALY"`)
* **False Negative ($FN$):** `true_label == 1` AND `pred == 0` (`"NORMAL"`)

$$\text{Precision} = \frac{TP}{TP + FP}$$

$$\text{Recall} = \frac{TP}{TP + FN}$$

$$\text{F1-Score} = \frac{2 \times \text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$

$$\text{False Positive Rate (FPR)} = \frac{FP}{FP + TN}$$

$$\text{False Negative Rate (FNR)} = \frac{FN}{FN + TP}$$

* **Detection Latency:**
  $$\text{Latency} = t_{\text{first\_anomaly\_detection}} - t_{\text{first\_attack\_sample}}$$
  (Returns `-1.0` if no attack was present in the evaluated log).

### Resource Reduction Calculation ([`calculate_metrics.py:54-89`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/experiments/calculate_metrics.py#L54-L89))
* Computes pre-mitigation mean CPU/energy vs. post-mitigation mean CPU/energy for mitigated pods in `detection_cycles_*.csv`.
* Computes `Energy Saved Percentage` as:
  $$\text{Energy Saved \%} = \frac{\text{Average Energy Reduction}}{\text{Pre-mitigation Total Mean Energy}} \times 100$$

---

## PART 19 — FIGURES AND RESULTS

### Artifact Audit Across Repository

1. **`results/evaluation_results.csv` & `results/evaluation_results.json`:**
   * **Source Data:** Generated by `evaluator.py` evaluating the historical run in `evaluation.csv`.
   * **Values:**
     * Energy-Aware: Accuracy $= 0.9054$, FPR $= 0.0946$, Precision $= 0.0$, Recall $= 0.0$, F1 $= 0.0$, Latency $= -1.0$.
     * Basic IF: Accuracy $= 0.9981$, FPR $= 0.0019$, Precision $= 0.0$, Recall $= 0.0$, F1 $= 0.0$, Latency $= -1.0$.
   * **Analysis:** These values are **genuine experimental measurements** from a run where no attack pods were injected (all 1037 samples had `true_label = 0`). The 9.46% FPR represents false alarms on normal backend bursts.
2. **`detections.csv` & `evaluation.csv`:**
   * Real 1049-row and 1037-row datasets capturing continuous 22.7-minute operation of legitimate pods (`backend`, `frontend`, `normal-workload`).
3. **Publication Figures (1 to 10 in `experiments/generate_graphs.py`):**
   * Code is 100% written to plot real CSV logs at 300 DPI.
   * Figure 5 (Anomaly Scores) and Figure 8 (Confusion Matrix) can be executed directly from existing `evaluation.csv`.
   * Figures 1, 2, 4, 6, 7, 9, 10 require output from a full run of `run_research_pipeline.sh` that populates `results/logs/detection_cycles_*.csv`.

---

## PART 20 — CONFIGURATION

### Complete Master Configuration Table

| Variable Name | Current Value in Source Code | Defining File & Line | Purpose | Nature | Used By |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `PROMETHEUS_URL` | `"http://prometheus-service.monitoring.svc.cluster.local:9090"` | [`config.py:1`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L1) | In-cluster Prometheus endpoint | Configurable string | `collector.py` |
| `COLLECTION_INTERVAL` | `5` | [`config.py:3`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L3) | Telemetry query sampling frequency | Integer (seconds) | `main.py` |
| `WINDOW_SIZE` | `6` | [`config.py:4`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L4) | Samples per sliding window | Integer (samples) | `feature_engineer.py` |
| `TARGET_NAMESPACE` | `"default"` | [`config.py:5`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L5) | Namespace monitored for workloads | Configurable string | `collector.py`, `model_manager.py` |
| `MIN_TRAINING_WINDOWS` | `30` | [`config.py:7`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L7) | Min baseline windows per pod | Integer (windows) | `model_manager.py`, `state_manager.py` |
| `IGNORE_STARTUP_WINDOWS`| `2` | [`config.py:8`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L8) | Initial windows to drop per pod | Integer (windows) | `model_manager.py` |
| `TRAINING_PODS_WHITELIST`| `[]` | [`config.py:9`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L9) | Optional pod whitelist | List | Unused (empty) |
| `CONTAMINATION` | `0.1` | [`config.py:11`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L11) | Isolation Forest outlier fraction | Float | `model_manager.py` |
| `N_ESTIMATORS` | `100` | [`config.py:12`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L12) | Number of iTrees in forest | Integer | `model_manager.py` |
| `RANDOM_STATE` | `42` | [`config.py:13`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L13) | Reproducibility seed | Integer | `model_manager.py` |
| `MODEL_BOOTSTRAP` | `False` | [`config.py:14`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L14) | Bootstrap sampling flag | Boolean | `model_manager.py` |
| `MAX_SAMPLES` | `"auto"` | [`config.py:15`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L15) | Max samples per tree | String / Int | `model_manager.py` |
| `MODEL_N_JOBS` | `-1` | [`config.py:16`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L16) | CPU cores for model training | Integer | `model_manager.py` |
| `ANOMALY_CONFIRMATION_THRESHOLD` | `3` | [`config.py:18`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L18) | Consecutive anomalous windows | Integer | `model_manager.py`, `state_manager.py` |
| `ANOMALY_SCORE_THRESHOLD`| `0.0` | [`config.py:19`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L19) | Decision boundary threshold | Float | Reference in plots |
| `MIN_ATTACK_CPU` | `0.3` | [`config.py:20`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L20) | Static CPU gate threshold | Float (cores) | Disabled in prediction |
| `MIN_ATTACK_ENERGY` | `0.1` | [`config.py:21`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L21) | Static energy gate threshold | Float (Joules) | Disabled in prediction |
| `THROTTLE_CPU_LIMIT` | `"100m"` | [`config.py:23`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L23) | Throttled CPU limit string | String | `mitigator.py` |
| `THROTTLE_MEMORY_LIMIT` | `"128Mi"` | [`config.py:24`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L24) | Throttled memory limit string | String | `mitigator.py` |
| `THROTTLE_DURATION_WINDOWS` | `2` | [`config.py:25`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L25) | Windows before pod deletion | Integer (windows) | `mitigator.py` |
| `DASHBOARD_PORT` | `8080` | [`config.py:36`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L36) | Flask server listening port | Integer | `main.py` |
| `SYSTEM_NAMESPACES` | `["kube-system", "monitoring", "kube-public"]` | [`config.py:43`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L43) | Unmonitored namespaces | List of strings | `main.py`, `collector.py` |
| `ATTACK_POD_PREFIXES` | `["attack-"]` | [`config.py:44`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L44) | Prefixes identifying attacks | List of strings | `model_manager.py` |
| `EXCLUDED_POD_PREFIXES`| `["ai-detector-", "mysql-"]` | [`config.py:45`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L45) | Excluded workload pods | List of strings | `main.py` |

---

## PART 21 — CLASS AND FUNCTION INVENTORY

### Classes (17 Total)

1. `PodSample` ([`collector.py:12`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/collector.py#L12)): `@dataclass` holding 11 raw telemetry attributes for one pod.
2. `MetricsCollector` ([`collector.py:27`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/collector.py#L27)): Handles Prometheus queries, Kepler checks, fallback calculation, K8s live pod querying, and CSV saves.
3. `FeatureEngineer` ([`feature_engineer.py:8`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/feature_engineer.py#L8)): Manages sliding window deques, extracts 26 features, formats 16-D, 8-D, 6-D vectors.
4. `PredictionResult` ([`model_manager.py:15`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/model_manager.py#L15)): `@dataclass` holding dual-model predictions, scores, consecutive count, confirmed flag, true label.
5. `ModelManager` ([`model_manager.py:28`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/model_manager.py#L28)): State machine managing baseline buffers, dual scaler/IF training, scoring, consecutive validation, and evaluation logging.
6. `Mitigator` ([`mitigator.py:189`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/mitigator.py#L189)): Navigates `ownerReferences`, patches Deployment container limits, monitors rollout, deletes pods after 2 windows.
7. `StateManager` ([`state_manager.py:8`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/state_manager.py#L8)): In-memory thread-safe state store for dashboard live tables, timelines, and metrics.
8. `MetricsResult` ([`evaluator.py:9`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/evaluator.py#L9)): `@dataclass` holding calculated classification metrics and latency.
9. `Evaluator` ([`evaluator.py:20`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/evaluator.py#L20)): Calculates Precision, Recall, F1, Accuracy, FPR, FNR, Latency from `evaluation.csv`.
10. `ResearchLogger` ([`research_logger.py:65`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/research_logger.py#L65)): Append-only research CSV logger writing 19-field detection records.
11. `Task` ([`backend/app.py:14`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/backend/app.py#L14)): SQLAlchemy model for To-Do tasks (`id`, `title`, `done`).
12. `TaskSchema` ([`backend/app.py:19`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/backend/app.py#L19)): Marshmallow schema for `Task`.
13. `App` (React) ([`frontend/src/App.js:6`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/frontend/src/App.js#L6)): React component managing To-Do frontend.
14. `ApiService` ([`static/js/api.js:5`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/static/js/api.js#L5)): ES6 fetch wrapper for dashboard endpoints.
15. `Store` ([`static/js/state.js:5`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/static/js/state.js#L5)): ES6 pub/sub reactive store.
16. `ChartManager` ([`static/js/charts.js:21`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/static/js/charts.js#L21)): Chart.js factory for dark theme time series and gauges.
17. `App` (Dashboard Controller) ([`static/js/app.js:15`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/static/js/app.js#L15)): Single-page application orchestrator and 5s polling timer coordinator.

### Functions

* `_f(value: str) -> float` ([`collector.py:74`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/collector.py#L74)): Safe string-to-float converter.
* `_get_slope(y_vals) -> float` ([`feature_engineer.py:57`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/feature_engineer.py#L57)): Polynomial regression trend estimation.
* `_run(cmd: list) -> tuple` ([`mitigator.py:37`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/mitigator.py#L37)): Safe subprocess runner.
* `_kubectl(*args) -> tuple` ([`mitigator.py:46`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/mitigator.py#L46)): Prepend-`kubectl` command runner.
* `_get_jsonpath(...) -> str | None` ([`mitigator.py:51`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/mitigator.py#L51)): Queries K8s resource JSONPath.
* `_owning_replicaset(...) -> str | None` ([`mitigator.py:65`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/mitigator.py#L65)): Traverses pod ownerReferences.
* `_owning_deployment(...) -> str | None` ([`mitigator.py:84`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/mitigator.py#L84)): Traverses ReplicaSet ownerReferences.
* `_find_deployment(...) -> str | None` ([`mitigator.py:101`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/mitigator.py#L101)): Resolves parent Deployment name.
* `_container_name_from_deployment(...) -> str` ([`mitigator.py:117`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/mitigator.py#L117)): Extracts container name from pod template.
* `_throttle_deployment(...) -> bool` ([`mitigator.py:126`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/mitigator.py#L126)): Executes strategic patch and waits for rollout.
* `_attack_type_from_pod(pod_name: str) -> str` ([`research_logger.py:45`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/research_logger.py#L45)): Maps pod prefix to attack name.
* `_confidence_from_score(score: float) -> float` ([`research_logger.py:60`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/research_logger.py#L60)): Converts anomaly score to $[0.0, 1.0]$ confidence.
* `_reset_experiment_files() -> None` ([`dashboard.py:11`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/dashboard.py#L11)): Resets CSV headers on baseline start.
* `create_app(...) -> Flask` ([`dashboard.py:32`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/dashboard.py#L32)): Flask application factory.
* `_ensure_detection_log() -> None` ([`main.py:18`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L18)): Ensures `detections.csv` header exists.
* `_log_detection(...) -> None` ([`main.py:25`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L25)): Appends prediction summary to `detections.csv`.
* `_should_monitor_pod(...) -> bool` ([`main.py:33`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L33)): Excludes system and infrastructure pods.
* `startup() -> tuple` ([`main.py:39`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L39)): Initializes singletons and Flask server.
* `main_loop() -> None` ([`main.py:67`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/main.py#L67)): 5-second sampling and detection control loop.
* `calculate_metrics(...) -> pd.DataFrame` ([`calculate_metrics.py:109`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/experiments/calculate_metrics.py#L109)): Computes evaluation metrics.
* `export_pod_metrics(...) -> pd.DataFrame` ([`export_metrics.py:48`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/experiments/export_metrics.py#L48)): Exports pod metrics snapshot.
* `export_node_metrics() -> pd.DataFrame` ([`export_metrics.py:117`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/experiments/export_metrics.py#L117)): Exports node metrics snapshot.
* `generate_graphs(...) -> None` ([`generate_graphs.py:328`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/experiments/generate_graphs.py#L328)): Generates Figures 1–10.

---

## PART 22 — EXECUTION ORDER

### Exact Chronological Startup & Runtime Trace

```text
1. Program Start
   - Container executes CMD ["python", "main.py"].
   - if __name__ == "__main__": invokes main_loop() [main.py:144].

2. Service Initialization (startup() in main.py:39)
   - MetricsCollector() initialized [collector.py:28]:
     * Creates /app/data/raw_metrics.csv with headers if missing.
     * Retries Prometheus connection ("up" query) up to 5 times.
     * Detects Kepler availability (queries "kepler_container_joules_total").
   - FeatureEngineer() initialized with empty windows dict [feature_engineer.py:16].
   - ModelManager() initialized [model_manager.py:29]:
     * Ensures /app/logs/evaluation.csv and /app/data/training_data.csv exist.
     * Sets state = "IDLE".
   - Mitigator() initialized [mitigator.py:198]:
     * Ensures /app/logs/mitigations.csv exists.
   - Evaluator(), StateManager(), ResearchLogger() initialized.
   - create_app() configures Flask app; spawns daemon thread on port 8080.
   - System state is IDLE.

3. User Starts Baseline Training
   - Operator clicks "Start Baseline Training" on Web UI (or run_experiment.py calls POST /api/training/start).
   - _reset_experiment_files() resets CSV files [dashboard.py:11].
   - model_manager.start_baseline_collection() sets state = "COLLECTING_BASELINE".

4. Periodic Execution Loop (while True in main.py:70, runs every 5 seconds)
   a. Telemetry Querying:
      - collector.collect_all_pods() queries Prometheus for CPU, memory, network, Kepler Joules.
      - Queries K8s API (/api/v1/namespaces/default/pods) to filter live running pods.
      - Computes fallback energy (cpu * 0.4) if Kepler is unavailable.
      - Appends each pod sample to raw_metrics.csv.
   b. Window Buffering & Feature Extraction:
      - For each pod: checks _should_monitor_pod() (skips kube-system, monitoring, ai-detector-, mysql-).
      - feature_engineer.add_sample(pod, sample) appends sample to deque(maxlen=6).
      - If len(deque) < 6: skips to next pod (window not yet full).
      - If len(deque) == 6: feature_engineer.extract_features(pod) computes 26 features.
   c. State-Dependent Execution:
      - IF state == "COLLECTING_BASELINE":
        * model_manager.add_training_window(): checks pod is not an attack pod; skips first 2 startup windows.
        * Appends to training buffers (16-D, 8-D, 6-D).
        * Checks if min(training_counts.values()) >= 30.
        * When 30 windows collected per pod: trains both scalers and both IsolationForest models,
          persists .pkl files to /app/model/, transitions state to "DETECTING".
      - IF state == "DETECTING":
        * model_manager.predict(): scales features, scores models via decision_function().
        * If raw_pred_ea == -1: consecutive_count[pod] += 1; else consecutive_count[pod] = 0.
        * confirmed = (consecutive_count[pod] >= 3).
        * Saves row to /app/logs/evaluation.csv.
        * Appends to detections.csv and research detection cycle CSV.
        * IF confirmed == True AND pod_name.startswith("attack-"):
          - Step 1 (first detection): mitigator.mitigate() walks ownerReferences to Deployment;
            applies strategic patch (cpu=100m, memory=128Mi); waits for rollout; logs "THROTTLED".
          - Step 2 (after 2 windows): mitigator.mitigate() deletes offending pod via kubectl delete pod;
            logs "DELETED"; Deployment controller spawns replacement pod with throttled limits.
   d. Housekeeping:
      - state_manager.prune_stale_pods() evicts pods silent for > 15s.
      - model_manager.prune_pods() and mitigator.prune_pods() clear counters for terminated pods.
      - time.sleep(5) pauses until next cycle.
```

---

## PART 23 — FAILURE / EDGE CASE HANDLING

* **Prometheus Unavailable:** `MetricsCollector._test_prometheus_connection()` retries 5 times with 3-second intervals on startup. If still unreachable, raises `RuntimeError("Prometheus connection failed after retries")` preventing startup with broken monitoring. During runtime, `requests.get()` errors are caught in `main_loop()` try/except block, logging `[ERROR] Main loop failure` and sleeping 5 seconds before retrying.
* **Kepler Unavailable:** `MetricsCollector._detect_kepler()` queries `kepler_container_joules_total`. If query returns empty or fails, sets `self.kepler_available = False`. Energy automatically falls back to $\text{cpu\_cores} \times 0.4$ with tag `energy_source = "estimated"`.
* **Kubernetes API Unavailable:** If service account token/CA cannot contact K8s API in `_live_pods_from_k8s()`, logs `[K8S] Live pod filter unavailable, using Prometheus-only list` and falls back gracefully to Prometheus pod discovery.
* **Missing Metric Data:** Handled by `MetricsCollector._f()` returning `0.0` on string parse failures, and dictionary `.get(pod, 0.0)` for missing pod entries.
* **Pod Disappears / Terminated:**
  * K8s API query filters out pods with `.metadata.deletionTimestamp`.
  * `state_manager.prune_stale_pods(max_stale_seconds=15)` evicts missing pods from the dashboard live list.
  * `model_manager.prune_pods(live_pods)` and `mitigator.prune_pods(live_pods)` delete stale consecutive counters and mitigation state dictionaries.
* **Zero CPU / Division by Zero:** In `feature_engineer.py`, every ratio denominator is protected with `EPSILON = 1e-6` (e.g. `avg_energy / (avg_cpu + EPSILON)`). In `evaluator.py`, `_safe_div()` returns `0.0` if denominator is zero.
* **NaN Values in Slope:** `_get_slope()` returns `0.0` if sample array length $< 2$.
* **Mitigation Failure:** `_run()` traps `subprocess.CalledProcessError` and returns `(False, stderr)`. If Deployment resolution fails, logs `"FAILED"` to `mitigations.csv` and sets `deployment: None` to avoid hammering the K8s API.

---

## PART 24 — SOURCE CODE VERIFICATION

### Strict Epistemic Classification

#### [CONFIRMED FROM SOURCE CODE]
* 5-second sampling interval (`COLLECTION_INTERVAL = 5`) and 6-sample sliding window (`WINDOW_SIZE = 6`, exactly 30s).
* True sliding window implementation via `collections.deque(maxlen=6)` per pod with 5-sample ($83.33\%$) overlap.
* 26 statistical, slope, and cross-resource features extracted via NumPy.
* Dual-model architecture: 16-D Energy-Aware Isolation Forest vs 6-D Basic Isolation Forest.
* Exact Isolation Forest parameters: `n_estimators=100`, `contamination=0.1`, `random_state=42`, `bootstrap=False`, `max_samples="auto"`.
* Automated Kepler fallback to software estimation ($\text{cpu\_cores} \times 0.4$) when eBPF counters are unavailable.
* Anomaly validation requiring $\ge 3$ consecutive anomalous windows before attack confirmation.
* Progressive 2-stage mitigation: Deployment template patch (`cpu=100m`, `mem=128Mi`) via `ownerReferences` followed by pod deletion after 2 elapsed windows.
* Safety filter restricting mitigation actions exclusively to pods starting with `"attack-"`.
* Safety exclusions: `ai-detector-*` and `mysql-*` pods excluded; `kube-system`, `monitoring`, `kube-public` namespaces excluded.
* Dashboard implemented in Flask, semantic HTML5, Vanilla CSS, and Vanilla ES6 JS with Chart.js on port 8080.
* Automated experiment harness (`run_experiment.py`, `run_research_pipeline.py`) with `kubectl cp` log collection.
* Publication figure generator `generate_graphs.py` implementing 10 distinct plots at 300 DPI.
* Real datasets `detections.csv` (1049 rows) and `evaluation.csv` (1037 rows) capturing 22.7 minutes of normal workload execution.

#### [SUPPORTED BY DOCUMENTATION BUT NOT VERIFIED IN CODE]
* **Oracle Cloud Infrastructure (OCI) ARM Deployment:** `PROJECT_INTELLIGENCE.md:18` states OCI VM.Standard.A1.Flex was intended but abandoned due to capacity constraints; codebase is configured exclusively for single-node K3s on WSL2.
* **Real Hardware Kepler Counters in Stored Logs:** Manifests and queries for Kepler exist, but all stored datasets in the repository show energy values generated via the $0.4 \times \text{CPU}$ software fallback due to WSL2 kernel counter limitations.
* **Reported Attack Detection Rates ($\ge 95\%$):** Documented in project presentation narratives, but the historical CSV logs currently stored in the repository contain only normal workload data.
* **Ingress Domain Routing (`to-do-app.local`):** Ingress manifests exist, but running environment relies on NodePort services and `port-forward.sh`.

#### [NOT FOUND / UNKNOWN]
* **Traditional Database for AI Pipeline:** No SQLite, PostgreSQL, or MongoDB exists; results are stored strictly in flat CSV/JSON files on PVC volumes.
* **Online / Incremental Model Retraining:** Models are trained once during baseline; no online stream retraining or dynamic weight updating exists in code.
* **One-Class SVM / Local Outlier Factor Code:** Mentioned in literature survey, but zero implementation code exists in the repository.
* **Gradual Anomaly Counter Decay:** Counter immediately resets to 0 on any normal window; no decaying hysteresis window exists.

---

## PART 25 — CONFLICTS AND INCONSISTENCIES

1. **⚠️ DOCUMENTATION–CODE CONFLICT: Feature Vector Dimensionality:**
   * **Documentation:** `README.md:35` and `PROJECT_INTELLIGENCE.md:59` describe the Energy-Aware model as using **8 features** (`avg_cpu`, `avg_memory_mb`, `avg_energy`, `energy_cpu_ratio`, `cpu_variance`, `memory_variance`, `energy_variance`, `avg_network`).
   * **Source Code:** `feature_engineer.py:169-186` and `model_manager.py:137-144` actually assemble and train the Energy-Aware model on **16 features** (`features_16`), which includes additional polynomial slopes (`cpu_slope`, `energy_slope`), peak ratios, cross-resource densities, and maximums. `features_8` is retained only as a backward-compatibility slice.
2. **⚠️ DOCUMENTATION–CODE CONFLICT: Static Threshold Filtering:**
   * **Documentation:** Project descriptions mention filtering anomalies using `MIN_ATTACK_CPU = 0.3` and `MIN_ATTACK_ENERGY = 0.1`.
   * **Source Code:** In `model_manager.py:217-220`, static thresholds are **explicitly commented out and disabled** for decision gating because they caused false alarms on legitimate backend traffic. Anomaly gating relies strictly on `raw_pred_ea == -1`.
3. **⚠️ DOCUMENTATION–CODE CONFLICT: Kepler Energy Data:**
   * **Documentation:** Emphasizes real eBPF hardware power profiling via Kepler.
   * **Source Code:** While Kepler manifests and queries are implemented, the execution environment (WSL2) does not expose hardware performance counters. All stored experimental CSVs (`detections.csv`, `evaluation.csv`) show energy values calculated via the software fallback formula $\text{cpu} \times 0.4$.
4. **⚠️ DOCUMENTATION–CODE CONFLICT: Baseline Completion Condition:**
   * **Documentation:** Suggests baseline collection completes after 30 total windows (~150 seconds).
   * **Source Code:** `model_manager.py:120` enforces `min(self.training_counts.values()) >= 30`. Baseline training only finishes when **every tracked pod** has individually accumulated 30 valid windows.
5. **⚠️ UNUSED VARIABLES IN CODE:**
   * `config.TRAINING_PODS_WHITELIST = []` ([`config.py:9`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L9)): Never referenced in collection or training logic.
   * `config.ANOMALY_SCORE_THRESHOLD = 0.0` ([`config.py:19`](file:///home/rahul__ubuntu/projects/Todo-List-App-Deployment-on-Kubernetes/ai-anomaly-detection/pipeline/config.py#L19)): Never used in `model_manager.py` decision logic (used only as a plotting reference line in `generate_graphs.py`).

---

## PART 26 — FINAL VERIFIED PROJECT BLUEPRINT

* **A. PROJECT PURPOSE:** Real-time behavioral anomaly detection and automated progressive mitigation for Kubernetes workloads, focusing on energy-wasting threats (e.g. cryptojacking, CPU/memory stress).
* **B. ACTUAL ARCHITECTURE:** Single-node K3s on WSL2 Linux; target To-Do app (Flask + React + MySQL); cAdvisor + Kepler + Node Exporter metrics scraped by Prometheus; AI Detector pod running Python 3.11 with dual Isolation Forest models and Flask dashboard; `kubectl` subprocess mitigation.
* **C. ACTUAL DATA FLOW:** Kubelet/Kepler $\to$ Prometheus $\to$ `collector.py` (5s HTTP query) $\to$ `feature_engineer.py` (deque maxlen=6) $\to$ `model_manager.py` (StandardScaler + IsolationForest) $\to$ `mitigator.py` (kubectl patch/delete) $\to$ CSV/JSON logs $\to$ `dashboard.py` (polled every 5s).
* **D. MONITORING:** 5-second interval PromQL queries for CPU cores rate (30s), memory working set bytes, network RX/TX rate (30s), and Kepler Joules rate (30s) with $0.4 \times \text{CPU}$ fallback.
* **E. WINDOWING:** 6 samples $\times$ 5 seconds $= 30$-second sliding window per pod via `collections.deque(maxlen=6)` with 5-sample ($83.33\%$) overlap.
* **F. FEATURES:** 26 statistical features extracted; 16-D vector for Energy-Aware model; 6-D vector for Basic baseline model; core signal is `energy_cpu_ratio = avg_energy / (avg_cpu + 1e-6)`.
* **G. TRAINING:** Unsupervised baseline collection on normal pods only; discards first 2 startup windows; requires $\ge 30$ windows per pod before training dual scalers and models.
* **H. ISOLATION FOREST:** Scikit-learn `IsolationForest(n_estimators=100, contamination=0.1, random_state=42, max_samples='auto')`; decision via `predict() == -1` and `decision_function()`.
* **I. ANOMALY VALIDATION:** Requires 3 consecutive anomalous windows (`consecutive_count >= 3`) before confirming attack; resets immediately to 0 on any normal window.
* **J. MITIGATION:** Progressive 2-stage: Step 1 patches Deployment template limits (`cpu=100m`, `memory=128Mi`) via ownerReferences walk; Step 2 deletes offending pod via `kubectl delete pod` after 2 elapsed windows. Failsafe restricts mitigation to `attack-*` pods.
* **K. KUBERNETES:** Namespaces `default` and `monitoring`; `ai-detector` deployment mounted to 3 PVCs (`model`, `logs`, `data`) with ClusterRole permissions.
* **L. ATTACK SIMULATION:** Deterministic stress workloads (`stress`, `stress-ng`) targeting CPU, memory, network, combined, and matrix multiplication cryptojacking.
* **M. STORAGE/LOGGING:** Flat CSV/JSON files on PVC volumes (`raw_metrics.csv`, `training_data.csv`, `detections.csv`, `evaluation.csv`, `mitigations.csv`, `research/*.csv`). No relational/NoSQL DB in AI pipeline.
* **N. DASHBOARD:** Flask backend serving 11 REST endpoints; semantic HTML5/CSS/Vanilla JS frontend with Chart.js polling `/api/status` every 5 seconds.
* **O. BASELINES:** Basic Isolation Forest (6 non-energy features) running in parallel. Static thresholds exist in config but are disabled in decision logic.
* **P. EVALUATION:** Formulas implemented for TP, TN, FP, FN, Precision, Recall, F1, Accuracy, FPR, FNR, Detection Latency, and Energy Reduction.
* **Q. FIGURES/RESULTS:** Figure generator `generate_graphs.py` produces 10 publication figures at 300 DPI. Stored dataset reflects a 22.7-minute normal baseline run with 9.46% FPR on backend bursts.
* **R. CONFIGURATION:** Centralized in `config.py` (24 variables controlling intervals, sizes, thresholds, limits, and paths).
* **S. IMPORTANT FILES:** `main.py`, `collector.py`, `feature_engineer.py`, `model_manager.py`, `mitigator.py`, `dashboard.py`, `evaluator.py`, `research_logger.py`, `state_manager.py`, `generate_graphs.py`.
* **T. IMPORTANT CLASSES/FUNCTIONS:** `MetricsCollector`, `FeatureEngineer`, `ModelManager`, `Mitigator`, `StateManager`, `Evaluator`, `ResearchLogger`, `PodSample`, `PredictionResult`, `MetricsResult`.
* **U. KNOWN LIMITATIONS:** Single-node WSL2 deployment; hardware Kepler counters unsupported on WSL2 requiring fallback software estimation; models trained once offline with no stream retraining.
* **V. CODE–DOCUMENTATION CONFLICTS:** Code uses 16 features for Energy-Aware IF (docs state 8); static thresholds disabled in prediction (docs state active); stored data reflects estimated energy due to WSL2 environment.

---

## PART 27 — INFORMATION NEEDED FOR DIAGRAMS

### 1. System Architecture Diagram
* **Entities / Components:**
  * Infrastructure Layer: Single-Node K3s Cluster, `frontend-deployment` (port 80), `backend-deployment` (port 5000), `mysql` StatefulSet (port 3306), `normal-workload` (2 replicas), `attack-*` Deployments.
  * Telemetry Layer: `node-exporter` DaemonSet (:9100), `kepler` DaemonSet (:9102), `prometheus-deployment` (:9090).
  * Detection & Control Layer: `ai-detector` Pod containing `MetricsCollector`, `FeatureEngineer`, `ModelManager`, `Mitigator`, `StateManager`, `Evaluator`, `Flask API Dashboard` (:8080).
  * Storage Layer: PVCs (`ai-detector-model-pvc`, `ai-detector-logs-pvc`, `ai-detector-data-pvc`).
  * Presentation Layer: Web Browser (EnergyGuard Dashboard :30080), Grafana (:3000).
* **Connections & Directions:**
  * Workload Pods $\to$ cAdvisor / Node Exporter / Kepler (Kernel/cgroup telemetry).
  * Node Exporter / Kepler / cAdvisor $\to$ Prometheus (HTTP scrape: 5s for Kepler, 15s for others).
  * Prometheus $\to$ `MetricsCollector` (HTTP PromQL queries every 5s).
  * `MetricsCollector` $\to$ `FeatureEngineer` (In-memory `PodSample` stream).
  * `FeatureEngineer` $\to$ `ModelManager` (16-D and 6-D NumPy feature vectors).
  * `ModelManager` $\to$ `Mitigator` (Confirmed attack signal with pod name).
  * `Mitigator` $\to$ Kubernetes API Server (Subprocess `kubectl patch deployment` and `kubectl delete pod`).
  * Kubernetes API Server $\to$ `attack-*` Deployments (Applies resource limits and terminates offending pod).
  * `MetricsCollector` / `ModelManager` / `Mitigator` $\to$ PVC CSV Files (File append operations).
  * `StateManager` $\to$ Web Browser (HTTP GET `/api/status` polling every 5s).

### 2. Data Flow Diagram (Level-1 DFD)
* **Processes:**
  * $P_1$: Ingest Telemetry (`collector.py`)
  * $P_2$: Buffer Windows & Extract Features (`feature_engineer.py`)
  * $P_3$: Train Dual Isolation Forests (`model_manager.py`)
  * $P_4$: Infer Anomalies & Validate Persistence (`model_manager.py`)
  * $P_5$: Execute Progressive Mitigation (`mitigator.py`)
  * $P_6$: Serve State & Compute Metrics (`state_manager.py`, `evaluator.py`, `dashboard.py`)
* **External Entities:**
  * Kubernetes Cluster Telemetry (cAdvisor, Kepler)
  * Kubernetes API Server (`https://kubernetes.default.svc:443`)
  * System Administrator / Evaluator
* **Data Stores:**
  * $D_1$: Raw Telemetry Store (`raw_metrics.csv`)
  * $D_2$: Model Persistence Store (`isolation_forest_*.pkl`, `scaler_*.pkl`)
  * $D_3$: Evaluation & Detection Logs (`detections.csv`, `evaluation.csv`)
  * $D_4$: Mitigation Event Store (`mitigations.csv`)
  * $D_5$: Research Logs Store (`detection_cycles_*.csv`)
* **Data Flows:**
  * Telemetry $\to P_1$: Raw time-series PromQL responses.
  * $P_1 \to D_1$: Append raw pod telemetry rows.
  * $P_1 \to P_2$: Continuous stream of `PodSample` objects.
  * $P_2 \to P_3$: Feature vectors during baseline collection.
  * $P_3 \to D_2$: Serialized model and scaler objects.
  * $D_2 \to P_4$: Load fitted models and scalers.
  * $P_2 \to P_4$: Extracted feature vectors during detection.
  * $P_4 \to D_3, D_5$: Prediction results, decision scores, and research metrics.
  * $P_4 \to P_5$: Confirmed attack notification (`pod_name`, `namespace`, `score`).
  * $P_5 \to$ Kubernetes API Server: Strategic-merge JSON patch & delete commands.
  * $P_5 \to D_4$: Mitigation records (`THROTTLED`, `DELETED`, `SUCCESS`).
  * $D_3, D_4 \to P_6$: In-memory history queries.
  * $P_6 \to$ Administrator: JSON API responses and rendered dashboard views.
  * Administrator $\to P_6$: Trigger baseline collection (`POST /api/training/start`).

### 3. Sequence Diagram (Monitoring to Mitigation Cycle)
* **Lifelines:**
  * `Operator`
  * `Dashboard` (`dashboard.py` / `app.js`)
  * `Engine` (`main.py`)
  * `Collector` (`collector.py`)
  * `Prometheus` (`:9090`)
  * `FeatureEng` (`feature_engineer.py`)
  * `ModelMgr` (`model_manager.py`)
  * `Mitigator` (`mitigator.py`)
  * `K8sAPI` (`https://kubernetes.default.svc:443`)
* **Interactions:**
  1. `Operator -> Dashboard`: Click "Start Baseline Training".
  2. `Dashboard -> Engine`: `POST /api/training/start`.
  3. `Engine -> ModelMgr`: `start_baseline_collection()`.
  4. Loop every 5s:
     * `Engine -> Collector`: `collect_all_pods()`.
     * `Collector -> Prometheus`: HTTP GET PromQL queries.
     * `Prometheus --> Collector`: Return CPU, memory, network, energy JSON.
     * `Collector -> Collector`: Fallback to $0.4 \times \text{CPU}$ if Kepler unavailable.
     * `Collector -> Collector`: Write to `raw_metrics.csv`.
     * `Collector --> Engine`: Return `dict[pod, PodSample]`.
     * `Engine -> FeatureEng`: `add_sample(pod, sample)`.
     * `FeatureEng -> FeatureEng`: Push to `deque(maxlen=6)`.
     * If window complete (len == 6):
       - `Engine -> FeatureEng`: `extract_features(pod)`.
       - `FeatureEng --> Engine`: Return `features_16`, `features_6`, `feature_dict`.
       - If state == `DETECTING`:
         * `Engine -> ModelMgr`: `predict(features_16, features_6, pod, feature_dict)`.
         * `ModelMgr -> ModelMgr`: `scaler_16.transform()`, `model_energy_aware.predict()`, `decision_function()`.
         * `ModelMgr -> ModelMgr`: If anomalous, `consecutive_count[pod] += 1`; else reset to 0.
         * `ModelMgr -> ModelMgr`: Write to `evaluation.csv`.
         * `ModelMgr --> Engine`: Return `PredictionResult` (`confirmed_attack = consecutive >= 3`).
         * If `confirmed_attack` AND `pod.startswith("attack-")`:
           - `Engine -> Mitigator`: `mitigate(pod, namespace, score, consecutive)`.
           - `Mitigator -> K8sAPI`: Subprocess `kubectl get pod <pod> -o jsonpath={.metadata.ownerReferences}`.
           - `Mitigator -> K8sAPI`: Subprocess `kubectl get rs <rs> -o jsonpath={.metadata.ownerReferences}`.
           - `Mitigator -> K8sAPI`: Subprocess `kubectl patch deployment <deploy> limits: cpu=100m, mem=128Mi`.
           - `Mitigator -> K8sAPI`: Subprocess `kubectl rollout status deployment/<deploy> --timeout=120s`.
           - Wait 2 windows (`THROTTLE_DURATION_WINDOWS = 2`):
             * `Mitigator -> K8sAPI`: Subprocess `kubectl delete pod <pod> -n default`.
           - `Mitigator -> Mitigator`: Write to `mitigations.csv`.
     * `Dashboard -> Engine`: Poll `GET /api/status` every 5s.
     * `Engine --> Dashboard`: Return state JSON.
     * `Dashboard --> Operator`: Update charts, pod tables, and alert badges.

### 4. UML Class Diagram
* **Classes:**
  * `PodSample`: Dataclass with 11 attributes.
  * `MetricsCollector`: Attributes (`prom_url`, `kepler_available`, `_k8s_api`); methods (`collect_all_pods()`, `_prom_query()`, `_detect_kepler()`, `_live_pods_from_k8s()`, `_save()`).
  * `FeatureEngineer`: Attributes (`windows`, `last_extracted_features`); methods (`add_sample()`, `extract_features()`).
  * `PredictionResult`: Dataclass with 9 attributes.
  * `ModelManager`: Attributes (`state`, buffers, counts, `model_energy_aware`, `model_basic`, scalers); methods (`start_baseline_collection()`, `add_training_window()`, `train_both_models()`, `predict()`, `save_to_evaluation_log()`, `prune_pods()`).
  * `Mitigator`: Attributes (`throttled_pods`); methods (`mitigate()`, `log_mitigation()`, `prune_pods()`).
  * `StateManager`: Attributes (`current_state`, `pods`, ring buffer deques, `comparison_stats`); methods (`update_pod_metrics()`, `add_detection()`, `add_mitigation()`, `get_dashboard_json()`, `prune_stale_pods()`).
  * `MetricsResult`: Dataclass with 8 evaluation attributes.
  * `Evaluator`: Methods (`calculate_metrics()`, `_calc()`, `_safe_div()`).
  * `ResearchLogger`: Attributes (`log_dir`, `experiment_id`, `log_path`); methods (`log_detection_cycle()`, `log_mitigation_event()`).
* **Relationships:**
  * `MetricsCollector` creates `PodSample` (Composition).
  * `FeatureEngineer` aggregates `PodSample` in `deque(maxlen=6)`.
  * `ModelManager` produces `PredictionResult` (Association).
  * `ModelManager` contains `IsolationForest` and `StandardScaler` (Composition).
  * `main.py` orchestrates `MetricsCollector`, `FeatureEngineer`, `ModelManager`, `Mitigator`, `StateManager`, `Evaluator`, and `ResearchLogger`.

### 5. Monitoring / Data Collection Flow Diagram
* Kubelet cAdvisor & Kepler eBPF $\to$ Prometheus Server (Scrape :9100, :9102, cAdvisor) $\to$ HTTP GET Query $\to$ `MetricsCollector._prom_query()` $\to$ `_by_pod()` dictionary assembly $\to$ Kepler check / fallback calculation $\to$ Kubernetes API active pod validation $\to$ Instantiation of `PodSample` $\to$ Append to `raw_metrics.csv` $\to$ Pass to `FeatureEngineer`.

### 6. Anomaly Detection Flow Diagram
* Incoming `PodSample` $\to$ `FeatureEngineer.add_sample()` $\to$ Check window length ($N = 6$) $\to$ If $N = 6$, compute 26 metrics $\to$ Assemble `features_16` and `features_6` $\to$ `ModelManager.predict()` $\to$ Normalize via `StandardScaler.transform()` $\to$ Inference via `IsolationForest.predict()` & `decision_function()` $\to$ Check `raw_pred_ea == -1` $\to$ Increment or reset `consecutive_count` $\to$ Check `consecutive_count >= 3` $\to$ Emit `PredictionResult(confirmed_attack=True)` $\to$ Append to `evaluation.csv` & `detections.csv`.

### 7. Mitigation Flow Diagram
* `PredictionResult` with `confirmed_attack=True` $\to$ Check `pod_name.startswith("attack-")` $\to$ Call `Mitigator.mitigate()` $\to$ Check `pod_name in throttled_pods` $\to$ If NO: Resolve Deployment via `ownerReferences` $\to$ Execute `kubectl patch deployment` (limits: CPU 100m, Mem 128Mi) $\to$ Execute `kubectl rollout status` $\to$ Register pod with `windows_since_throttle = 0` $\to$ Return `"THROTTLED"` $\to$ If YES: Increment `windows_since_throttle` $\to$ If count $\ge 2$: Execute `kubectl delete pod` $\to$ Remove pod from dictionary $\to$ Return `"DELETED"` $\to$ Deployment controller spawns replacement pod with throttled resource limits.
