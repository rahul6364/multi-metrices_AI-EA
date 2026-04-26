#!/bin/bash
set -e
echo "═══════════════════════════════════════════"
echo " AI-Based Energy-Aware Anomaly Detection   "
echo " Sahyadri College | Team CSE-26            "
echo "═══════════════════════════════════════════"

# Step 1: Deploy Kepler
echo "[1/6] Deploying Kepler energy monitoring..."
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
kubectl rollout restart deployment/grafana -n monitoring

# Step 4: Build AI detector image
echo "[4/6] Building AI detector image..."
cd ai-anomaly-detection/pipeline
docker build -t todo-ai-detector:latest .
docker save todo-ai-detector:latest -o ai-detector.tar
sudo k3s ctr images import ai-detector.tar
rm ai-detector.tar
cd ../..

# Step 5: Deploy AI detector
echo "[5/6] Deploying AI detector..."
kubectl apply -f ai-anomaly-detection/rbac.yaml
kubectl apply -f ai-anomaly-detection/ai-detector-pvc.yaml
kubectl apply -f ai-anomaly-detection/ai-detector-deployment.yaml
kubectl apply -f ai-anomaly-detection/ai-detector-service.yaml

# Step 6: Deploy normal workload
echo "[6/6] Deploying normal workload..."
kubectl apply -f ai-anomaly-detection/workloads/normal-workload.yaml

# Wait and verify
echo "Waiting for AI detector to start..."
kubectl wait --for=condition=ready pod -l app=ai-detector --timeout=120s

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
