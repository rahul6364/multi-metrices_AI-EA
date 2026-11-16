#!/usr/bin/env bash
# Remove all attack/stress workloads and reset dashboard incident history.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKLOADS_DIR="${ROOT_DIR}/workloads"

echo "=== Cleaning up attack workloads ==="

for manifest in \
  attack-cpu.yaml \
  attack-memory.yaml \
  attack-network.yaml \
  attack-combined.yaml \
  attack-cryptojacking.yaml
do
  kubectl delete -f "${WORKLOADS_DIR}/${manifest}" --ignore-not-found
done

echo
echo "=== Remaining pods in default namespace ==="
kubectl get pods -n default

DETECTOR_URL="${DETECTOR_URL:-}"
if [[ -z "${DETECTOR_URL}" ]]; then
  if curl -sf "http://localhost:8006/api/status" >/dev/null 2>&1; then
    DETECTOR_URL="http://localhost:8006"
  elif curl -sf "http://localhost:30080/api/status" >/dev/null 2>&1; then
    DETECTOR_URL="http://localhost:30080"
  fi
fi

if [[ -n "${DETECTOR_URL}" ]]; then
  echo
  echo "=== Clearing dashboard incident history ==="
  curl -sf -X POST "${DETECTOR_URL}/api/incidents/clear" && echo "[OK] Incident history cleared"
else
  echo
  echo "[WARN] Detector API not reachable. Start port-forward and run:"
  echo "       curl -X POST http://localhost:8006/api/incidents/clear"
fi

echo
echo "[OK] Cleanup complete. Refresh the dashboard."
