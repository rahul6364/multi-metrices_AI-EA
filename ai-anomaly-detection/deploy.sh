#!/bin/bash
set -e
echo "═══════════════════════════════════════════"
echo " AI-Based Energy-Aware Anomaly Detection   "
echo " Sahyadri College | Team CSE-26            "
echo "═══════════════════════════════════════════"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

# Docker Desktop on WSL can crash k3s kubelet by writing a 7-field /proc/mounts line.
if awk 'NF != 6 { found=1 } END { exit !found }' /proc/mounts; then
  echo "[0/6] Docker Desktop /Docker/host mount breaks kubelet; applying k3s WSL fix..."
  sudo mkdir -p /etc/systemd/system/k3s.service.d
  sudo cp "${SCRIPT_DIR}/k3s-wsl-docker-mount.conf" /etc/systemd/system/k3s.service.d/wsl-docker-mount.conf
  sudo systemctl daemon-reload
  sudo systemctl restart k3s
  echo "Waiting for Kubernetes API after k3s restart..."
  for i in $(seq 1 60); do
    if kubectl get --raw=/readyz >/dev/null 2>&1; then
      break
    fi
    sleep 2
  done
fi

# Step 1: Deploy monitoring exporters
echo "[1/6] Deploying monitoring exporters (Kepler, kube-state-metrics, node-exporter)..."
kubectl apply -k github.com/kubernetes/kube-state-metrics/examples/standard?ref=main
kubectl apply -f ai-anomaly-detection/monitoring/node-exporter.yaml
kubectl apply -f ai-anomaly-detection/monitoring/kepler-rbac.yaml
kubectl apply -f ai-anomaly-detection/monitoring/kepler-daemonset.yaml
kubectl apply -f ai-anomaly-detection/monitoring/kepler-service.yaml

# Step 2: Update Prometheus to scrape Kepler
echo "[2/6] Updating Prometheus scrape config..."
kubectl apply -f ai-anomaly-detection/monitoring/update-prometheus-configmap.yaml
kubectl rollout restart deployment/prometheus-deployment -n monitoring

# Step 3: Update Grafana with auto dashboards
echo "[3/6] Configuring Grafana dashboards..."
kubectl apply -f ai-anomaly-detection/monitoring/grafana-datasource-configmap.yaml
kubectl apply -f ai-anomaly-detection/monitoring/grafana-dashboard-configmap.yaml
kubectl apply -f ai-anomaly-detection/monitoring/grafana-dashboard-provider-configmap.yaml
kubectl apply -f ai-anomaly-detection/monitoring/grafana-deployment.yaml
kubectl rollout restart deployment/grafana -n monitoring

# Step 4: Build AI detector image
echo "[4/6] Building AI detector image..."
cd ai-anomaly-detection/pipeline
docker build -t todo-ai-detector:v2 .
docker save todo-ai-detector:v2 -o ai-detector.tar
sudo k3s ctr images import ai-detector.tar
rm ai-detector.tar
cd ../..

# Step 5: Deploy AI detector
echo "[5/6] Deploying AI detector..."
kubectl apply -f ai-anomaly-detection/rbac.yaml
kubectl apply -f ai-anomaly-detection/ai-detector-pvc.yaml
kubectl apply -f ai-anomaly-detection/ai-detector-deployment.yaml
kubectl apply -f ai-anomaly-detection/ai-detector-service.yaml
# Spec may be unchanged after a node reboot; recreate the stuck pod anyway.
kubectl delete pod -l app=ai-detector --force --grace-period=0 --ignore-not-found
kubectl rollout restart deployment/ai-detector

# Step 6: Deploy normal workload
echo "[6/6] Deploying normal workload..."
kubectl apply -f ai-anomaly-detection/workloads/normal-workload.yaml

# Wait and verify
echo "Waiting for AI detector to start..."
kubectl wait --for=condition=ready pod -l app=ai-detector --timeout=180s

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ACCESS POINTS:"
echo "  🖥  Dashboard  → http://localhost:30080"
echo "  📊 Prometheus  → http://localhost:9090"
echo "  📈 Grafana     → http://localhost:3000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo " DEMO STEPS:"
echo "  1. Open http://localhost:30080"
echo "  2. Click 'Start Baseline Training'"
echo "  3. Wait for 30 windows (~3 min)"
echo "  4. Run attack:"
echo "     kubectl apply -f workloads/attack-cpu.yaml"
echo "  5. Watch detection on dashboard"
echo "  6. Click 'Calculate IEEE Metrics' for results"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
