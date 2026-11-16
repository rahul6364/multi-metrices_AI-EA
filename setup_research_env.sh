#!/usr/bin/env bash
# Install Python dependencies required for the IEEE research pipeline.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-research"
REQUIREMENTS="${ROOT_DIR}/experiments/requirements.txt"

echo "=== Research Pipeline Environment Setup ==="

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] python3 is not installed."
  exit 1
fi

if ! python3 -m venv --help >/dev/null 2>&1 || ! python3 -m pip --version >/dev/null 2>&1; then
  echo "[ACTION REQUIRED] Install system Python tooling first:"
  echo
  echo "  sudo apt update"
  echo "  sudo apt install -y python3-pip python3.12-venv"
  echo
  echo "Then rerun:"
  echo "  ./setup_research_env.sh"
  exit 1
fi

if [[ -d "${VENV_DIR}" ]] && [[ ! -f "${VENV_DIR}/bin/activate" ]]; then
  echo "[WARN] Removing broken virtual environment..."
  rm -rf "${VENV_DIR}"
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "[INFO] Creating virtual environment..."
  python3 -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "[INFO] Installing Python packages..."
python3 -m pip install --upgrade pip
python3 -m pip install -r "${REQUIREMENTS}"

echo
echo "[OK] Environment ready."
echo "Run experiments with:"
echo "  ./run_research_pipeline.sh --scenarios cpu"
