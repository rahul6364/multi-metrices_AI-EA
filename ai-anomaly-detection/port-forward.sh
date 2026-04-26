#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="${LOG_DIR:-./ai-anomaly-detection/.port-forward-logs}"
PID_DIR="${PID_DIR:-./ai-anomaly-detection/.port-forward-pids}"

mkdir -p "$LOG_DIR" "$PID_DIR"

start_forward() {
  local name="$1"
  local svc="$2"
  local local_port="$3"
  local target_port="$4"
  local log_file="$LOG_DIR/${name}.log"
  local pid_file="$PID_DIR/${name}.pid"

  if [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
    echo "[skip] $name already running (pid $(cat "$pid_file"))"
    return
  fi

  nohup kubectl port-forward -n default "service/${svc}" "${local_port}:${target_port}" >"$log_file" 2>&1 &
  local pid=$!
  echo "$pid" >"$pid_file"
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
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
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
  if [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
    echo "[up]   $name -> http://localhost:${local_port} (pid $(cat "$pid_file"))"
  else
    echo "[down] $name -> http://localhost:${local_port}"
  fi
}

case "${1:-start}" in
  start)
    start_forward "frontend" "frontend-service" "8004" "80"
    start_forward "backend" "backend" "8005" "5000"
    start_forward "detector" "ai-detector-service" "8006" "8080"
    echo ""
    echo "Logs: $LOG_DIR"
    ;;
  stop)
    stop_forward "frontend"
    stop_forward "backend"
    stop_forward "detector"
    ;;
  restart)
    "$0" stop
    "$0" start
    ;;
  status)
    status_forward "frontend" "8004"
    status_forward "backend" "8005"
    status_forward "detector" "8006"
    echo "Logs: $LOG_DIR"
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac
