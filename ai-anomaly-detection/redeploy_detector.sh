#!/usr/bin/env bash
# Rebuild and redeploy the ai-detector after code fixes.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_DIR="${ROOT_DIR}/pipeline"
IMAGE="todo-ai-detector:v2"

echo "=== Rebuilding ai-detector image ==="
docker build -t "${IMAGE}" "${PIPELINE_DIR}"

echo "=== Importing image into k3s ==="
docker save "${IMAGE}" -o /tmp/ai-detector.tar
sudo k3s ctr images import /tmp/ai-detector.tar
rm -f /tmp/ai-detector.tar

echo "=== Applying deployment updates ==="
kubectl apply -f "${ROOT_DIR}/ai-detector-deployment.yaml"

echo "=== Restarting deployment ==="
kubectl rollout restart deployment/ai-detector -n default
kubectl rollout status deployment/ai-detector -n default --timeout=180s

echo "=== Restarting port-forwards ==="
"${ROOT_DIR}/port-forward.sh" restart

echo
echo "[OK] Detector redeployed."
echo "Dashboard: http://localhost:8006  (or http://localhost:30080)"
echo "Check health: ${ROOT_DIR}/port-forward.sh status"
