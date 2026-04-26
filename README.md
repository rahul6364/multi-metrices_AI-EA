# AI-Based Detection of Energy-Wasting Cyber Attacks in Cloud Systems

This repository contains two connected parts:

- A Todo application deployed on Kubernetes (`kubernetes/`) used as the legitimate workload.
- An IEEE-style AI energy-aware anomaly detection system (`ai-anomaly-detection/`) that monitors pods, detects anomalies, and performs progressive mitigation.

Project context:

- **Title**: AI-Based Detection of Energy-Wasting Cyber Attacks in Cloud Systems
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
- `backend/` - Flask backend source
- `frontend/` - React frontend source
- `ai-anomaly-detection/monitoring/` - Prometheus/Grafana/Kepler manifests
- `ai-anomaly-detection/pipeline/` - AI detector Python pipeline + dashboard + Dockerfile
- `ai-anomaly-detection/workloads/` - normal and attack workload manifests
- `ai-anomaly-detection/*.yaml` - detector RBAC/deployment/service/PVC
- `ai-anomaly-detection/deploy.sh` - end-to-end deploy helper
- `ai-anomaly-detection/port-forward.sh` - reliable local browser access helper

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

## 8) Demo Procedure (IEEE Flow)

1. Open detector dashboard.
2. Click **Start Baseline Training**.
3. Wait until training reaches `30/30`.
4. Apply one attack at a time:

```bash
kubectl apply -f ai-anomaly-detection/workloads/attack-cpu.yaml
kubectl apply -f ai-anomaly-detection/workloads/attack-memory.yaml
kubectl apply -f ai-anomaly-detection/workloads/attack-combined.yaml
```

5. Observe:
   - EA vs Basic model outputs
   - Consecutive anomaly counts
   - Mitigation actions
6. Click **Calculate IEEE Metrics**.
7. Repeat with clean baseline for each scenario for stronger results.

Cleanup attack workloads:

```bash
kubectl delete -f ai-anomaly-detection/workloads/attack-cpu.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/workloads/attack-memory.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/workloads/attack-combined.yaml --ignore-not-found
```

---

## 9) Kepler on WSL2 Reality

Kepler may crash on WSL2 due to kernel/eBPF limitations. The detector is implemented to continue in fallback mode:

- `energy_source = "estimated"`
- `energy = cpu * 0.4`

This keeps the end-to-end demo running and evaluation pipeline functional.

---

## 10) Prometheus and Grafana Access

Grafana is exposed as NodePort (`30000`) and can be opened in browser.

Prometheus service is `ClusterIP` by default. Access with:

```bash
ckubectl delete -f ai-anomaly-detection/workloads/attack-cpu.yaml --ignore-not-found
kubectl delete -f ai-anfoundomaly-detection/workloads/attack-memory.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/workloads/attack-combined.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/workloads/normal-workload.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/ai-detector-service.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/ai-detector-deployment.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/ai-detector-pvc.yaml --ignore-not-found
kubectl delete -f ai-anomaly-detection/rbac.yaml --ignore-not-```

Then open `http://localhost:9090`.

---

## 11) Common Troubleshooting

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

## 12) Useful Commands

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

## 13) Full Cleanup

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

## 14) Notes for Final Year Demo/Report

- Keep screenshots of:
  - Baseline training completion
  - Attack detection table (EA vs Basic)
  - Mitigation logs
  - Evaluation metrics output
- Run each attack type in separate controlled trials for publishable metrics.
- Mention WSL2 Kepler limitation and fallback estimation mode clearly in report.
