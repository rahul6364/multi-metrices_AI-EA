# AI-Based Detection of Energy-Wasting Cyber Attacks in Cloud Systems

This repository contains two connected parts:

- A Todo application deployed on Kubernetes (`kubernetes/`) used as the legitimate workload.
- An IEEE-style AI energy-aware anomaly detection system (`ai-anomaly-detection/`) that monitors pods, detects anomalies, and performs progressive mitigation.

Project context:

- **Title**: Multi-Metric Energy-Aware Behavioral Anomaly Detection and Automated Mitigation in Kubernetes-Based Cloud Systems
- **Team**: CSE-26, Sahyadri College of Engineering, Mangaluru
- **Guide**: Dr. Deepti Rai
- **Environment target**: K3s single-node on WSL2 Ubuntu

---

## 1) Architecture Overview

### Layer 1 - Infrastructure

- K3s single-node cluster
- Todo app pods as normal workloads
- Attack workloads (`attack-cpu`, `attack-memory`, `attack-combined`) as malicious workloads

### Layer 2 - Telemetry and Features

- Prometheus collects metrics at **5s interval**
- Kepler is attempted for real energy; on WSL2 it may fail and pipeline automatically uses software estimation
- Sliding window is **30 seconds** (`6 x 5s`)
- Features include CPU, memory, network, energy, ratio, and variance metrics

### Layer 3 - AI Detection and Mitigation

- Dual model setup:
  - Energy-aware Isolation Forest (8 features)
  - Basic Isolation Forest (6 features, comparison baseline)
- Confidence validation with consecutive anomaly threshold
- Progressive mitigation:
  - Step 1: throttle resources
  - Step 2: delete pod if behavior persists

---

## 2) Repository Structure

- `kubernetes/` - Todo app manifests (frontend, backend, mysql)
- `backend/` - Flask backend source (Todo app)
- `frontend/` - React frontend source (Todo app)
- `ai-anomaly-detection/monitoring/` - Prometheus/Grafana/Kepler manifests
- `ai-anomaly-detection/pipeline/` - AI detector pipeline + upgraded dashboard + Dockerfile
  - `templates/index.html` - Modern semantic HTML5 shell for EnergyGuard Dashboard
  - `static/css/` - Modular dark cybersecurity design system (variables, layout, components, views)
  - `static/js/` - Vanilla ES6 modules (router, reactive state store, API client, Chart.js factory, components, and 7 view modules)
  - `dashboard.py` - Flask web application serving upgraded UI and REST endpoints
  - `main.py` - Core telemetry collection, feature engineering, and model inference loop
  - `model_manager.py` - Dual Isolation Forest (8-D Energy-Aware & 6-D Basic IF)
  - `collector.py` - Prometheus & Kepler telemetry collector with WSL2 fallback
  - `mitigator.py` - Progressive Kubernetes deployment-level mitigation (throttle & evict)
  - `evaluator.py` - IEEE research metrics calculation engine
- `ai-anomaly-detection/workloads/` - Normal and attack workload manifests
- `ai-anomaly-detection/*.yaml` - Detector RBAC/deployment/service/PVC manifests
- `ai-anomaly-detection/deploy.sh` - End-to-end deploy helper script
- `ai-anomaly-detection/port-forward.sh` - Local browser access helper script

---

## 3) Prerequisites

- WSL2 Ubuntu
- K3s installed and running
- Docker installed
- `kubectl` configured for K3s
- At least ~3 GB free RAM for stable demo

Quick checks:

```bash
kubectl get nodes
kubectl get pods -A
docker --version
```

---

## 4) Deploy Todo App (Legitimate Workload)

Apply app manifests:

```bash
kubectl apply -f kubernetes/
kubectl get pods -n default
kubectl get svc -n default
```

Expected pods in `default`:

- `frontend-deployment-*`
- `backend-deployment-*`
- `mysql-0`

---

## 5) Deploy AI Detector Stack

Use the provided script:

```bash
chmod +x ai-anomaly-detection/deploy.sh
./ai-anomaly-detection/deploy.sh
```

What it does:

1. Deploys Kepler manifests
2. Updates Prometheus scrape config
3. Applies Grafana datasource/dashboard config
4. Builds detector image and imports into K3s containerd
5. Deploys detector RBAC + PVC + deployment + service
6. Deploys normal workload

---

## 6) Persistent Storage (Important)

Detector state now survives pod restarts via PVC:

- `ai-detector-model-pvc` mounted at `/app/model`
- `ai-detector-logs-pvc` mounted at `/app/logs`
- `ai-detector-data-pvc` mounted at `/app/data`

Manifest:

- `ai-anomaly-detection/ai-detector-pvc.yaml`

Deployment uses these PVCs in:

- `ai-anomaly-detection/ai-detector-deployment.yaml`

---

## 7) Access URLs

### NodePort (if accessible from your browser)

- Detector dashboard: `http://<node-ip>:30080`
- Todo frontend: `http://<node-ip>:30214`
- Todo backend: `http://<node-ip>:32458`
- Grafana: `http://<node-ip>:30000`

### Recommended on WSL2: port-forward

Use helper:

```bash
./ai-anomaly-detection/port-forward.sh start
./ai-anomaly-detection/port-forward.sh status
```

Then use:

- Detector dashboard: `http://localhost:8006`
- Todo frontend: `http://localhost:8004`
- Todo backend: `http://localhost:8005`

Stop/restart:

```bash
./ai-anomaly-detection/port-forward.sh stop
./ai-anomaly-detection/port-forward.sh restart
```

---

## 8) EnergyGuard AI Cloud Security & Monitoring Dashboard (Upgraded Frontend)

The frontend for the AI Anomaly Detection Framework has been completely upgraded from a basic developer debugging view to a modern, publication-grade **Energy-Aware Cloud Security & AI Monitoring Dashboard**.

### Key UI Features & Architecture:
- **Clean Dark Cybersecurity Theme**: Tailored color palette (charcoal `#0a0d14`, cards `#141b2a`, healthy green `#10b981`, threat red `#ef4444`, warning amber `#f59e0b`, telemetry cyan `#06b6d4`, electric blue `#38bdf8`), typography with *Inter* and *JetBrains Mono*, and subtle glassmorphic styling.
- **Strict Data Truthfulness**: 100% connected to existing backend APIs—zero fake telemetry, zero fake AI scores, zero hardcoded research metrics.
- **7 Dedicated Dashboard Views**:
  1. **Overview**: Live status indicator, 6 real-time KPI cards (System Status, Pods Monitored, Active Anomalies, Mitigations, Current Energy Rate, Training Status), **Security Command Center** (prominent active threat banner vs. clean protected state), and interactive Baseline Training widget with animated progress bar.
  2. **Live Monitoring**: 5 dedicated time-series charts (Energy Consumption, CPU Utilization, Memory Working Set, Network Throughput, and Energy-to-CPU Ratio) with pod focus dropdown, status filter, and live search.
  3. **Live Pod Table**: Color-coded status badges, compact monospace telemetry, row highlighting on anomalies, and shortened pod names with tooltip expansion.
  4. **AI Detection & Model Comparison**: Explains the 8-dimensional Energy-Aware feature vector, side-by-side comparison table (Energy-Aware IF vs. Basic IF), real-time Anomaly Score Trajectory chart, and a *"Why Was This Workload Flagged?"* root-cause inspector.
  5. **Security Incidents**: Summary metrics, paginated Recent Security Events log, and the visual **Attack Response Lifecycle Timeline** (`Normal` → `Resource Abnormality` → `AI Anomaly` → `Consecutive Confirmation` → `Throttling` → `Termination` → `Recovery`).
  6. **Mitigation Operations**: 6-stage progressive mitigation pipeline (Detection, Confirmation, Deployment Throttling, Observation, Pod Deletion, Recovery), true energy conservation impact analysis, and chronological mitigation log.
  7. **Kubernetes Infrastructure**: Visual K3s cluster node topology (Control-Plane / Primary Node, Observability Stack) with live container distribution and resource usage.
  8. **Research Analytics (IEEE Evaluation)**: Replaced raw JSON dump with formatted metric cards (Accuracy, Precision, Recall, F1 Score, False Positive Rate, Detection Latency), comparative bar chart, "Calculate IEEE Metrics" trigger, and optional "View Raw Response" JSON drawer.

---

## 9) How to Run the Updated Frontend

### Method A: In the Kubernetes Cluster (Recommended Production / Demo Flow)

Whenever you deploy to K3s or rebuild the detector:

```bash
# 1. Ensure Docker daemon is running in WSL2
sudo service docker start

# 2. Build the updated Docker image (tagged as v2 matching deployment spec)
cd ai-anomaly-detection/pipeline
docker build -t todo-ai-detector:v2 .

# 3. Save and import the image directly into K3s containerd
docker save todo-ai-detector:v2 -o ai-detector.tar
sudo k3s ctr images import ai-detector.tar
rm ai-detector.tar
cd ../..

# 4. Restart the detector deployment to run the updated container
kubectl rollout restart deployment/ai-detector -n default
kubectl rollout status deployment/ai-detector -n default
```

**Accessing the Dashboard in Your Browser:**

- **Via WSL2 Port-Forwarding (Fastest & Most Reliable):**
  ```bash
  ./ai-anomaly-detection/port-forward.sh start
  ./ai-anomaly-detection/port-forward.sh status
  ```
  Open **`http://localhost:8006`** in your browser.

- **Via Kubernetes NodePort:**
  Open **`http://localhost:30080`** (or `http://<node-ip>:30080`).

---

### Method B: Standalone Local Preview / Development Mode

You can also run the upgraded dashboard directly on your host machine without rebuilding the Docker container:

```bash
# 1. Ensure Python dependencies are installed in your virtual environment
.venv-research/bin/pip install flask flask-cors pandas scikit-learn

# 2. Run the dashboard preview server (connects to real detections.csv and telemetry)
.venv-research/bin/python -c "
import sys, os
sys.path.insert(0, 'ai-anomaly-detection/pipeline')
from main import startup
"
```

Or run the preconfigured verification preview server (loaded with real experiment data from `detections.csv`):
```bash
.venv-research/bin/python .gemini/antigravity-ide/brain/9a1809e0-e7f3-4d00-af89-250c060f842d/scratch/test_server.py
```

Open **`http://localhost:8089`** in your browser to inspect all 7 views immediately.

---

## 10) Demo Procedure (IEEE Flow)

1. Open detector dashboard (`http://localhost:8006` or `http://localhost:30080`).
2. Click **Start Baseline Training**.
3. Wait until training reaches `30/30` windows.
4. Apply one attack at a time:

```bash
kubectl apply -f ai-anomaly-detection/workloads/attack-cpu.yaml
kubectl apply -f ai-anomaly-detection/workloads/attack-memory.yaml
kubectl apply -f ai-anomaly-detection/workloads/attack-combined.yaml
```

5. Observe:
   - Security Command Center active threat alerts
   - Live monitoring graphs and pod telemetry
   - EA vs Basic model outputs
   - Attack response timeline & mitigation progression
6. Navigate to **Research Analytics** and click **Calculate IEEE Metrics**.
7. Repeat with clean baseline for each scenario for stronger results.

Cleanup attack workloads:

```bash
kubectl delete -f ai-anomaly-detection/workloads/attack-cpu.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/workloads/attack-memory.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/workloads/attack-combined.yaml --ignore-not-found
```

---

## 11) Kepler on WSL2 Reality

Kepler may crash on WSL2 due to kernel/eBPF limitations. The detector is implemented to continue in fallback mode:

- `energy_source = "estimated"`
- `energy = cpu * 0.4`

This keeps the end-to-end demo running and evaluation pipeline functional.

---

## 12) Prometheus and Grafana Access

Grafana is exposed as NodePort (`30000`) and can be opened in browser.

Prometheus service is `ClusterIP` by default. Access with:

```bash
kubectl port-forward -n monitoring service/prometheus-service 9090:9090
```

Then open `http://localhost:9090`.

---

## 13) Common Troubleshooting

### A) Dashboard flips to IDLE unexpectedly

Cause: detector pod restarted/rolled.

Check:

```bash
kubectl get pods -n default -l app=ai-detector
kubectl logs deployment/ai-detector -n default --tail=100
```

### B) Browser shows `ERR_CONNECTION_REFUSED`

Use port-forward helper (`8004/8005/8006`) instead of NodePort on WSL.

### C) `/api/evaluation` gives error

If no detections yet, evaluation log is empty; run baseline + attack first.

### D) K3s instability after long sessions

```bash
sudo service k3s restart
kubectl get pods -A
```

---

## 14) Useful Commands

```bash
# Cluster status
kubectl get nodes
kubectl get pods -A

# Detector status
kubectl get deploy,pods,svc -n default | grep ai-detector
kubectl logs deployment/ai-detector -n default --tail=200

# Monitoring status
kubectl get pods,svc -n monitoring

# Restart detector
kubectl rollout restart deployment/ai-detector -n default
kubectl rollout status deployment/ai-detector -n default
```

---

## 15) Full Cleanup

```bash
kubectl delete -f ai-anomaly-detection/workloads/attack-cpu.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/workloads/attack-memory.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/workloads/attack-combined.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/workloads/normal-workload.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/ai-detector-service.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/ai-detector-deployment.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/ai-detector-pvc.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/rbac.yaml --ignore-not-found
kubectl delete -f kubernetes/ --ignore-not-found
```

---

## 16) Notes for Final Year Demo/Report

- Keep screenshots of:
  - Baseline training completion
  - Attack detection table (EA vs Basic)
  - Mitigation logs
  - Evaluation metrics output
- Run each attack type in separate controlled trials for publishable metrics.
- Mention WSL2 Kepler limitation and fallback estimation mode clearly in report.
