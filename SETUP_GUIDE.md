# 🚀 Complete Setup Guide — AI-Based Energy-Aware Anomaly Detection Framework

**Project:** Multi-Metric Energy-Aware Behavioral Anomaly Detection and Automated Mitigation in Kubernetes-Based Cloud Systems  
**Team:** CSE-26, Sahyadri College of Engineering, Mangaluru  
**Guide:** Dr. Deepti Rai

---

> [!IMPORTANT]
> This guide is written for a **fresh Windows laptop with WSL2** (Windows Subsystem for Linux).
> Follow every step in order. Total estimated time: **15–25 minutes**.

---

## 📋 What You Will Set Up

| Component | Purpose |
|---|---|
| WSL2 Ubuntu | Linux environment inside Windows |
| Docker Desktop | Build and run container images |
| K3s | Lightweight Kubernetes cluster |
| Todo-List App | Legitimate workload (frontend + backend + MySQL) |
| AI Anomaly Detector | EnergyGuard dashboard + Isolation Forest detection |
| Prometheus + Grafana | Metrics collection and visualization |
| Kepler | Energy estimation via eBPF |

---

## ✅ PHASE 1 — Windows Prerequisites

### Step 1.1 — Enable WSL2 (if not already done)

Open **PowerShell as Administrator** and run:

```powershell
wsl --install
```

After it finishes, **restart your laptop**.

After restart, Ubuntu will open and ask you to set a **username** and **password** (remember these — you'll need them for `sudo` commands).

---

### Step 1.2 — Install Docker Desktop

1. Download from: **https://www.docker.com/products/docker-desktop/**
2. Run the installer. When prompted, make sure **"Use WSL2 instead of Hyper-V"** is checked.
3. After installation, open Docker Desktop.
4. Go to **Settings → Resources → WSL Integration**.
5. Enable your Ubuntu distro and click **Apply & Restart**.

---

### Step 1.3 — Verify Docker Works in WSL2

Open **Ubuntu (WSL2)** terminal and run:

```bash
docker --version
docker ps
```

You should see a Docker version number and an empty container list. If you see an error, make sure Docker Desktop is running in the Windows system tray.

---

## ✅ PHASE 2 — Install K3s (Kubernetes)

Open your **Ubuntu (WSL2)** terminal and run all these commands:

### Step 2.1 — Install K3s

```bash
curl -sfL https://get.k3s.io | sh -
```

> This downloads and installs K3s. It may take 1–2 minutes.

---

### Step 2.2 — Configure kubectl Access

```bash
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown -R $USER:$USER ~/.kube
chmod 600 ~/.kube/config
```

---

### Step 2.3 — Verify Cluster is Running

```bash
kubectl get nodes
```

You should see output like:
```
NAME     STATUS   ROLES                  AGE   VERSION
rahul    Ready    control-plane,master   30s   v1.28.x
```

If status shows `NotReady`, wait 30 seconds and try again.

---

### Step 2.4 — Apply the K3s WSL2 Fix (Prevents Crashes with Docker Desktop)

This is an important fix that prevents Docker Desktop from crashing your Kubernetes cluster.

```bash
sudo mkdir -p /etc/systemd/system/k3s.service.d
sudo tee /etc/systemd/system/k3s.service.d/wsl-docker-mount.conf << 'EOF'
[Service]
ExecStart=
ExecStart=/usr/bin/unshare --mount --propagation private /bin/sh -c "umount /Docker/host > /dev/null 2>&1 || true; exec /usr/local/bin/k3s server"
EOF
sudo systemctl daemon-reload
sudo systemctl restart k3s
```

Wait about 20 seconds, then verify k3s is running:
```bash
sudo systemctl is-active k3s
kubectl get nodes
```

---

## ✅ PHASE 3 — Get the Project

### Step 3.1 — Clone from GitHub

```bash
cd ~
git clone https://github.com/rahul6364/multi-metrices_AI-EA.git
cd multi-metrices_AI-EA
```

### Step 3.2 — Make all scripts executable

```bash
chmod +x ai-anomaly-detection/deploy.sh
chmod +x ai-anomaly-detection/port-forward.sh
chmod +x ai-anomaly-detection/fix-k3s-wsl.sh
chmod +x ai-anomaly-detection/cleanup_attacks.sh
chmod +x ai-anomaly-detection/redeploy_detector.sh
```

---

## ✅ PHASE 4 — Deploy the Todo-List Application (Legitimate Workload)

The Todo-List app acts as the normal, legitimate workload that the AI monitors.

### Step 4.1 — Create the MySQL secret

```bash
kubectl create secret generic db-secret \
  --from-literal=MYSQL_ROOT_PASSWORD=root123 \
  --from-literal=MYSQL_DATABASE=todo_db \
  --from-literal=MYSQL_USER=todo_user \
  --from-literal=MYSQL_PASSWORD=todo_pass
```

### Step 4.2 — Build the Docker images for the Todo App

```bash
# Build frontend image
cd frontend
docker build -t todo-frontend-react:latest .
sudo k3s ctr images import <(docker save todo-frontend-react:latest)
cd ..

# Build backend image
cd backend
docker build -t todo-backend:latest .
sudo k3s ctr images import <(docker save todo-backend:latest)
cd ..
```

> **Note:** This may take 3–5 minutes on first run as it downloads base images.

### Step 4.3 — Deploy all Todo App Kubernetes manifests

```bash
kubectl apply -f kubernetes/
```

### Step 4.4 — Verify all pods are running

```bash
kubectl get pods -n default
```

Expected output (wait 1–2 minutes for all to show `Running`):
```
NAME                                   READY   STATUS    RESTARTS
backend-deployment-xxx-xxx             1/1     Running   0
frontend-deployment-xxx-xxx            1/1     Running   0
mysql-0                                1/1     Running   0
```

---

## ✅ PHASE 5 — Deploy AI Anomaly Detection Stack

This is the main project. It deploys Prometheus, Grafana, Kepler, and the AI Detector.

### Step 5.1 — Run the full deploy script

```bash
./ai-anomaly-detection/deploy.sh
```

This script automatically:
1. Deploys Kepler (energy monitoring), node-exporter, kube-state-metrics
2. Updates Prometheus scrape configuration
3. Configures Grafana with dashboards
4. **Builds the AI detector Docker image** (`todo-ai-detector:v2`)
5. Imports the image into K3s containerd
6. Deploys the AI detector with RBAC, PVC, Deployment, and Service
7. Deploys the normal workload pods

> ⏳ This takes **5–10 minutes** total. You will see step-by-step output. This is normal.

---

### Step 5.2 — Verify all pods are running

```bash
kubectl get pods -A
```

Expected pods:

| Namespace | Pod | Status |
|---|---|---|
| default | ai-detector-xxx | Running |
| default | frontend-deployment-xxx | Running |
| default | backend-deployment-xxx | Running |
| default | mysql-0 | Running |
| default | normal-workload-xxx | Running |
| monitoring | prometheus-deployment-xxx | Running |
| monitoring | grafana-xxx | Running |
| monitoring | kepler-xxx | Running |
| kube-system | coredns-xxx | Running |

If any pod shows `Pending` or `Error`, wait 2 minutes and check again.

---

## ✅ PHASE 6 — Start Port-Forwarding & Open in Browser

### Step 6.1 — Start port-forwarding

```bash
./ai-anomaly-detection/port-forward.sh start
```

You should see:
```
[ok] frontend  -> http://localhost:8004
[ok] backend   -> http://localhost:8005
[ok] detector  -> http://localhost:8006
[ok] prometheus -> http://localhost:9090
[ok] grafana   -> http://localhost:3000
[ok] detector responds at http://localhost:8006/api/status
```

### Step 6.2 — Open in your browser

Open **Brave / Chrome / Edge** in Windows and visit:

| Service | URL | Description |
|---|---|---|
| 🤖 **AI Anomaly Detector** | **http://localhost:8006** | Main EnergyGuard Dashboard |
| 🌐 Todo-List App | http://localhost:8004 | Legitimate workload UI |
| 📊 Grafana | http://localhost:3000 | Metrics visualization |
| 📈 Prometheus | http://localhost:9090 | Raw telemetry |

---

## ✅ PHASE 7 — Run the Demo

### Step 7.1 — Start Baseline Training
1. Open **http://localhost:8006** in your browser.
2. Click the **"Start Baseline Training"** button.
3. Wait **~3 minutes** (30 windows of 5-second data are collected).
4. The status will change from `Training` to `Detecting`.

### Step 7.2 — Trigger an Attack (Anomaly Simulation)
Open a new WSL terminal and run:

```bash
cd ~/multi-metrices_AI-EA
kubectl apply -f ai-anomaly-detection/workloads/attack-cpu.yaml
```

Watch the **EnergyGuard Dashboard** — within 30–60 seconds you will see:
- 🔴 **Anomaly detected** alert in the Security Command Center
- CPU and Energy metrics spike in the Live Monitoring charts
- Security incident logged with mitigation details

### Step 7.3 — Stop the Attack
```bash
kubectl delete -f ai-anomaly-detection/workloads/attack-cpu.yaml
```

The dashboard will show recovery and the system will return to normal.

### Step 7.4 — Calculate IEEE Research Metrics
On the dashboard, scroll to the **Research Analytics** view and click **"Calculate IEEE Metrics"** to view:
- Precision, Recall, F1-Score
- False Positive Rate
- Detection Latency
- Energy Saved %

---

## 🔄 Everyday Usage (After First Setup)

Every time you restart your laptop, run these two commands in WSL:

```bash
cd ~/multi-metrices_AI-EA

# If k3s is not running
sudo systemctl start k3s

# Start port-forwarding
./ai-anomaly-detection/port-forward.sh start
```

Then open **http://localhost:8006** in your browser.

---

## 🛠 Troubleshooting

### Problem: `kubectl` command not found
```bash
export KUBECONFIG=~/.kube/config
echo 'export KUBECONFIG=~/.kube/config' >> ~/.bashrc
```

### Problem: K3s crashes after Docker Desktop restart
```bash
./ai-anomaly-detection/fix-k3s-wsl.sh
```

### Problem: Port-forwarding stopped working (browser refuses to connect)
```bash
./ai-anomaly-detection/port-forward.sh restart
```

### Problem: AI Detector pod is in `CrashLoopBackOff`
```bash
kubectl logs deployment/ai-detector
./ai-anomaly-detection/redeploy_detector.sh
```

### Problem: `localhost` works in WSL but not in Windows Brave browser
Run this in **PowerShell (Administrator)** on Windows:
```powershell
$wsl = (wsl hostname -I).Trim().Split()[0]
netsh interface portproxy reset
netsh interface portproxy add v4tov4 listenport=8006 listenaddress=0.0.0.0 connectport=8006 connectaddress=$wsl
netsh interface portproxy add v4tov4 listenport=8004 listenaddress=0.0.0.0 connectport=8004 connectaddress=$wsl
netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=$wsl
netsh interface portproxy add v4tov4 listenport=9090 listenaddress=0.0.0.0 connectport=9090 connectaddress=$wsl
```

### Problem: Deploy script fails at `kube-state-metrics` with `i/o timeout`
This means K3s cannot reach the internet for the manifest. Fix your kubeconfig first:
```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
./ai-anomaly-detection/deploy.sh
```

### Check Status of Everything at Once
```bash
kubectl get pods -A
./ai-anomaly-detection/port-forward.sh status
```

---

## 📁 Project Structure (Quick Reference)

```
multi-metrices_AI-EA/
├── kubernetes/                    # Todo-List App Kubernetes manifests
│   ├── frontend-deployment.yaml
│   ├── backend-deployment.yaml
│   ├── mysql-deployment.yaml
│   └── ...
├── frontend/                      # React frontend source code
├── backend/                       # Flask backend source code
├── ai-anomaly-detection/
│   ├── deploy.sh                  # ⭐ Main one-click deployment script
│   ├── port-forward.sh            # ⭐ Browser access helper
│   ├── fix-k3s-wsl.sh             # WSL2 crash recovery script
│   ├── pipeline/                  # AI detector source code
│   │   ├── main.py                # Core telemetry + inference loop
│   │   ├── model_manager.py       # Dual Isolation Forest model
│   │   ├── collector.py           # Prometheus + Kepler collector
│   │   ├── feature_engineer.py    # 8-dimensional feature engineering
│   │   ├── mitigator.py           # Kubernetes-based mitigation
│   │   ├── evaluator.py           # IEEE metrics evaluation
│   │   ├── dashboard.py           # Flask web server + REST APIs
│   │   └── Dockerfile
│   ├── monitoring/                # Prometheus, Grafana, Kepler configs
│   └── workloads/                 # Normal and attack workload manifests
├── APPENDIX_D_CODE_SNIPPETS/      # VTU project report Appendix D
│   ├── Appendix_D_Report.docx     # Word document with screenshots
│   ├── Extracted_Code/            # Clean Python code extracts D1–D10
│   └── Code_Screenshots/          # 300 DPI figure images
└── SETUP_GUIDE.md                 # ← This file
```

---

## 📞 Support

If anything breaks, check the logs:
```bash
# AI Detector logs
kubectl logs deployment/ai-detector --tail=50

# Port-forward logs
cat ai-anomaly-detection/.port-forward-logs/detector.log

# K3s system logs
sudo journalctl -u k3s -n 50 --no-pager
```

---

*Setup Guide written for Sahyadri College CSE-26 Major Project — November 2026*

