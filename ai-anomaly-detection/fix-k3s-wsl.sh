#!/bin/bash
# Recover k3s on WSL2 when Docker Desktop's /Docker/host mount crashes kubelet.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DROPIN_SRC="${ROOT_DIR}/k3s-wsl-docker-mount.conf"
DROPIN_DIR="/etc/systemd/system/k3s.service.d"
DROPIN_DST="${DROPIN_DIR}/wsl-docker-mount.conf"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Re-running with sudo..."
  exec sudo -E "$0" "$@"
fi

echo "Installing k3s systemd drop-in to hide /Docker/host from kubelet..."
mkdir -p "${DROPIN_DIR}"
cp "${DROPIN_SRC}" "${DROPIN_DST}"
systemctl daemon-reload
systemctl restart k3s

export KUBECONFIG="${KUBECONFIG:-/etc/rancher/k3s/k3s.yaml}"

echo "Waiting for Kubernetes API..."
for i in $(seq 1 60); do
  if kubectl get --raw=/readyz >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo "Force-deleting pods stuck Unknown/Terminating after the k3s crash loop..."
kubectl get pods -A --no-headers 2>/dev/null | awk '$4=="Unknown" || $4=="Terminating" {print $1, $2}' | while read -r ns name; do
  kubectl delete pod "${name}" -n "${ns}" --force --grace-period=0 --ignore-not-found >/dev/null 2>&1 || true
done

kubectl rollout restart deployment/ai-detector -n default >/dev/null 2>&1 || true
kubectl rollout restart deployment/grafana -n monitoring >/dev/null 2>&1 || true
kubectl rollout restart deployment/prometheus-deployment -n monitoring >/dev/null 2>&1 || true

echo
echo "k3s status: $(systemctl is-active k3s)"
kubectl get pods -A --field-selector=status.phase!=Succeeded
echo
echo "If ai-detector is still not Ready, wait ~30s then:"
echo "  kubectl wait --for=condition=ready pod -l app=ai-detector --timeout=180s"
