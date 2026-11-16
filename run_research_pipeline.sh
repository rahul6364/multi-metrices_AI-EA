#!/usr/bin/env bash
# Single-command IEEE research pipeline orchestrator.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPERIMENTS_DIR="${ROOT_DIR}/experiments"
VENV_DIR="${ROOT_DIR}/.venv-research"
REQUIREMENTS="${EXPERIMENTS_DIR}/requirements.txt"

echo "=== AI Energy-Aware Anomaly Detection: Research Pipeline ==="

if ! command -v kubectl >/dev/null 2>&1; then
  echo "[ERROR] kubectl is required but not installed."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] python3 is required but not installed."
  exit 1
fi

# Auto-detect detector API (port-forward 8006 or NodePort 30080).
DETECTOR_URL="${DETECTOR_URL:-}"
if [[ -z "${DETECTOR_URL}" ]]; then
  if curl -sf "http://localhost:8006/api/status" >/dev/null 2>&1; then
    DETECTOR_URL="http://localhost:8006"
  elif curl -sf "http://localhost:30080/api/status" >/dev/null 2>&1; then
    DETECTOR_URL="http://localhost:30080"
  else
    echo "[WARN] Detector API not reachable at http://localhost:8006 or http://localhost:30080"
    echo "       Start port-forward:"
    echo "       ./ai-anomaly-detection/port-forward.sh start"
    DETECTOR_URL="http://localhost:8006"
  fi
fi
export DETECTOR_URL
echo "[INFO] Using detector API: ${DETECTOR_URL}"

if ! curl -sf "http://localhost:9090/-/ready" >/dev/null 2>&1; then
  echo "[WARN] Prometheus not reachable at http://localhost:9090"
  echo "       Start port-forward in another terminal:"
  echo "       kubectl port-forward -n monitoring svc/prometheus-service 9090:9090"
fi

install_dependencies() {
  local python_bin="$1"
  echo "[INFO] Installing Python dependencies..."
  "${python_bin}" -m pip install --upgrade pip
  "${python_bin}" -m pip install -r "${REQUIREMENTS}"
}

setup_python_env() {
  # Remove broken venv left by a failed ensurepip run.
  if [[ -d "${VENV_DIR}" ]] && [[ ! -f "${VENV_DIR}/bin/activate" ]]; then
    echo "[WARN] Removing incomplete virtual environment at ${VENV_DIR}"
    rm -rf "${VENV_DIR}"
  fi

  if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "[ERROR] python3-venv is not available."
    echo "        Install it with: sudo apt install python3.12-venv python3-pip"
    exit 1
  fi

  if [[ ! -d "${VENV_DIR}" ]]; then
    python3 -m venv "${VENV_DIR}"
  fi

  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"
  install_dependencies "python3"
}

if ! python3 -m pip --version >/dev/null 2>&1; then
  if [[ -x "${VENV_DIR}/bin/python3" ]] && "${VENV_DIR}/bin/python3" -m pip --version >/dev/null 2>&1; then
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"
    install_dependencies "python3"
  else
    echo "[ERROR] pip is not installed for python3."
    echo "        Run: sudo apt install python3-pip python3.12-venv"
    exit 1
  fi
else
  setup_python_env
fi

cd "${EXPERIMENTS_DIR}"
python3 run_research_pipeline.py "$@"
