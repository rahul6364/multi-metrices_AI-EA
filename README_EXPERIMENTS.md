# IEEE Research Experiment Pipeline

This document explains how to run reproducible experiments for the paper:

**AI-Based Energy-Aware Anomaly Detection Framework for Kubernetes-Based Cloud Systems**

The pipeline collects **only real metrics** from your running K3s cluster (Prometheus, Kepler, detector logs). It does not generate synthetic data.

---

## Architecture Overview

```text
Prometheus / Kepler
        |
        v
ai-detector pod (Isolation Forest + mitigation)
        |
        +-- /app/logs/research/detection_cycles_*.csv
        +-- /app/logs/evaluation.csv
        +-- /app/logs/mitigations.csv
        |
        v
experiments/ scripts (host)
        |
        +-- results/raw_metrics/
        +-- results/logs/
        +-- results/metrics/
        +-- results/figures/
        +-- results/experiments/
```

---

## Folder Structure

```text
project/
├── experiments/
│   ├── experiment_config.py
│   ├── export_metrics.py
│   ├── run_experiment.py
│   ├── calculate_metrics.py
│   ├── generate_graphs.py
│   ├── run_research_pipeline.py
│   ├── utils.py
│   └── requirements.txt
├── results/
│   ├── logs/
│   ├── metrics/
│   ├── figures/
│   ├── raw_metrics/
│   └── experiments/
├── run_research_pipeline.sh
└── ai-anomaly-detection/
    ├── pipeline/research_logger.py
    └── workloads/
        ├── attack-cpu.yaml
        ├── attack-memory.yaml
        ├── attack-network.yaml
        ├── attack-combined.yaml
        └── attack-cryptojacking.yaml
```

---

## Prerequisites

### 1. Cluster services running

```bash
kubectl get pods -n default -l app=ai-detector
kubectl get pods -n monitoring
```

### 2. Rebuild and redeploy detector (one-time after update)

```bash
cd ai-anomaly-detection/pipeline
docker build -t ai-detector:latest .
kubectl rollout restart deployment/ai-detector -n default
kubectl rollout status deployment/ai-detector -n default
```

### 3. Port-forwards (required on WSL2)

**Terminal 1 — Detector API**

```bash
./ai-anomaly-detection/port-forward.sh start
```

**Terminal 2 — Prometheus**

```bash
kubectl port-forward -n monitoring svc/prometheus-service 9090:9090
```

### 4. Python environment

**Required system packages (run once):**

```bash
sudo apt update
sudo apt install -y python3-pip python3.12-venv
```

**Then set up the research virtual environment:**

```bash
chmod +x setup_research_env.sh
./setup_research_env.sh
```

Or manually:

```bash
python3 -m venv .venv-research
source .venv-research/bin/activate
pip install -r experiments/requirements.txt
```

---

## Quick Start: Single Command

```bash
chmod +x run_research_pipeline.sh
./run_research_pipeline.sh --scenarios cpu
```

Run all scenarios:

```bash
./run_research_pipeline.sh --all-scenarios
```

Reuse existing logs (skip live experiments):

```bash
./run_research_pipeline.sh --scenarios cpu --skip-export --skip-experiments
```

---

## Step-by-Step Manual Execution

### Step 1: Export metrics

```bash
cd experiments
python3 export_metrics.py
```

### Step 2: Run one experiment

| Scenario | Attack |
|----------|--------|
| `normal` | None |
| `cpu` | CPU stress |
| `memory` | Memory stress |
| `network` | Network stress |
| `combined` | CPU + memory |
| `cryptojacking` | CPU matrix workload |

```bash
python3 run_experiment.py --scenario cpu
```

### Step 3: Calculate metrics

```bash
python3 calculate_metrics.py
```

Outputs: `results/metrics/metrics_summary.csv` and `results/metrics_summary.csv`

### Step 4: Generate figures

```bash
python3 generate_graphs.py
```

Outputs 10 figures in PNG, PDF, and SVG at 300 DPI under `results/figures/`.

---

## Research Logging Fields

Each detection cycle records: timestamp, pod_name, namespace, CPU/memory/network/energy metrics, anomaly score, prediction, confidence, attack type, mitigation action, detection/mitigation latency, and pod status.

Logs are append-only in `/app/logs/research/detection_cycles_<timestamp>.csv`.

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `PROMETHEUS_URL` | `http://localhost:9090` | Prometheus API |
| `DETECTOR_URL` | `http://localhost:8006` | Detector dashboard API |
| `TARGET_NAMESPACE` | `default` | Workload namespace |
| `RESEARCH_EXPERIMENT_ID` | auto timestamp | Log file suffix |

---

## Regenerating Paper Figures

```bash
cd experiments
python3 calculate_metrics.py
python3 generate_graphs.py
```

---

## Troubleshooting

**Detector API unreachable:** `./ai-anomaly-detection/port-forward.sh restart`

**Prometheus empty:** ensure port-forward on 9090 is active.

**Kepler unavailable (WSL2):** energy falls back to `cpu * 0.4` estimation.

**No research logs:** rebuild and redeploy the detector image.

**Training stuck:** delete all attack workloads before starting baseline.

---

## Recommended IEEE Protocol

```bash
for scenario in normal cpu memory network combined cryptojacking; do
  ./run_research_pipeline.sh --scenarios "$scenario"
  sleep 30
done

cd experiments
python3 calculate_metrics.py
python3 generate_graphs.py
```
