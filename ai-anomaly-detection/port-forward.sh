#!/usr/bin/env bash
# Port-forward helper with stale-PID cleanup and health checks.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${LOG_DIR:-${ROOT_DIR}/.port-forward-logs}"
PID_DIR="${PID_DIR:-${ROOT_DIR}/.port-forward-pids}"

mkdir -p "$LOG_DIR" "$PID_DIR"

if command -v kubectl >/dev/null 2>&1; then
  KUBECTL_BIN="$(command -v kubectl)"
elif [[ -x /usr/local/bin/kubectl ]]; then
  KUBECTL_BIN="/usr/local/bin/kubectl"
else
  echo "[ERROR] kubectl not found. Install kubectl or configure KUBECONFIG." >&2
  exit 1
fi

kubectl_cmd() {
  "$KUBECTL_BIN" "$@"
}

is_pid_running() {
  local pid="$1"
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

clean_stale_pid() {
  local name="$1"
  local pid_file="$PID_DIR/${name}.pid"
  if [[ ! -f "$pid_file" ]]; then
    return
  fi
  local pid
  pid="$(cat "$pid_file")"
  if ! is_pid_running "$pid"; then
    echo "[warn] Removing stale pid for ${name} (${pid})"
    rm -f "$pid_file"
  fi
}

start_forward() {
  local name="$1"
  local svc="$2"
  local local_port="$3"
  local target_port="$4"
  local ns="${5:-default}"
  local log_file="$LOG_DIR/${name}.log"
  local pid_file="$PID_DIR/${name}.pid"

  clean_stale_pid "$name"

  if [[ -f "$pid_file" ]] && is_pid_running "$(cat "$pid_file")"; then
    echo "[skip] $name already running (pid $(cat "$pid_file"))"
    return
  fi

  : >"$log_file"
  nohup "$KUBECTL_BIN" port-forward --address 0.0.0.0 -n "$ns" "service/${svc}" "${local_port}:${target_port}" >>"$log_file" 2>&1 &
  local pid=$!
  echo "$pid" >"$pid_file"
  sleep 1

  if ! is_pid_running "$pid"; then
    echo "[fail] $name port-forward exited immediately. Last log lines:"
    tail -n 5 "$log_file" || true
    rm -f "$pid_file"
    return 1
  fi

  echo "[ok] $name -> http://localhost:${local_port} (pid $pid)"
}

stop_forward() {
  local name="$1"
  local pid_file="$PID_DIR/${name}.pid"
  if [[ ! -f "$pid_file" ]]; then
    echo "[skip] $name not running (no pid file)"
    return
  fi

  local pid
  pid="$(cat "$pid_file")"
  if is_pid_running "$pid"; then
    kill "$pid" 2>/dev/null || true
    echo "[ok] stopped $name (pid $pid)"
  else
    echo "[skip] $name pid $pid not active"
  fi
  rm -f "$pid_file"
}

status_forward() {
  local name="$1"
  local local_port="$2"
  local pid_file="$PID_DIR/${name}.pid"
  if [[ -f "$pid_file" ]] && is_pid_running "$(cat "$pid_file")"; then
    echo "[up]   $name -> http://localhost:${local_port} (pid $(cat "$pid_file"))"
  else
    echo "[down] $name -> http://localhost:${local_port}"
    if [[ -f "$pid_file" ]]; then
      echo "       stale pid file present; run: $0 restart"
    fi
  fi
}

health_check() {
  local name="$1"
  local url="$2"
  if curl -sf "$url" >/dev/null 2>&1; then
    echo "[ok]   $name responds at $url"
  else
    echo "[warn] $name not responding at $url"
  fi
}

case "${1:-start}" in
  start)
    start_forward "frontend" "frontend-service" "8004" "80"
    start_forward "backend" "backend" "8005" "5000"
    start_forward "detector" "ai-detector-service" "8006" "8080"
    start_forward "prometheus" "prometheus-service" "9090" "9090" "monitoring"
    start_forward "grafana" "grafana" "3000" "3000" "monitoring"
    echo ""
    echo "Quick health checks:"
    health_check "detector" "http://localhost:8006/api/status"
    health_check "detector-nodeport" "http://localhost:30080/api/status"
    echo ""
    echo "If localhost:8006 is down but 30080 works, the detector pod restarted."
    echo "Run: $0 restart"
    echo "Logs: $LOG_DIR"
    ;;
  stop)
    stop_forward "frontend"
    stop_forward "backend"
    stop_forward "detector"
    stop_forward "prometheus"
    stop_forward "grafana"
    ;;
  restart)
    "$0" stop
    sleep 1
    "$0" start
    ;;
  status)
    status_forward "frontend" "8004"
    status_forward "backend" "8005"
    status_forward "detector" "8006"
    status_forward "prometheus" "9090"
    status_forward "grafana" "3000"
    echo ""
    health_check "detector" "http://localhost:8006/api/status"
    health_check "detector-nodeport" "http://localhost:30080/api/status"
    echo "Logs: $LOG_DIR"
    ;;
  watch)
    echo "[info] Watching port-forwards (Ctrl+C to stop)..."
    while true; do
      for entry in "frontend:8004" "backend:8005" "detector:8006" "prometheus:9090" "grafana:3000"; do
        name="${entry%%:*}"
        port="${entry##*:}"
        pid_file="$PID_DIR/${name}.pid"
        if [[ ! -f "$pid_file" ]] || ! is_pid_running "$(cat "$pid_file")"; then
          echo "[watch] restarting ${name}"
          case "$name" in
            frontend) start_forward "frontend" "frontend-service" "8004" "80" ;;
            backend) start_forward "backend" "backend" "8005" "5000" ;;
            detector) start_forward "detector" "ai-detector-service" "8006" "8080" ;;
            prometheus) start_forward "prometheus" "prometheus-service" "9090" "9090" "monitoring" ;;
            grafana) start_forward "grafana" "grafana" "3000" "3000" "monitoring" ;;
          esac
        fi
      done
      sleep 15
    done
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status|watch}"
    exit 1
    ;;
esac
