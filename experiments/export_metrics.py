#!/usr/bin/env python3
"""
Export Prometheus and Kepler metrics to CSV for IEEE research analysis.

Collects pod-level and node-level CPU, memory, network, and energy metrics
from a live Kubernetes cluster via Prometheus queries.
"""

from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from experiment_config import PROMETHEUS_URL, RAW_METRICS_DIR, TARGET_NAMESPACE, ensure_result_dirs


def prom_query(query: str) -> list[dict]:
    """Execute an instant PromQL query and return result rows."""
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": query},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") != "success":
        return []
    return payload.get("data", {}).get("result", [])


def rows_from_query(query: str, value_name: str, label_keys: list[str]) -> list[dict]:
    """Convert Prometheus vector results into flat dictionaries."""
    rows = []
    for item in prom_query(query):
        metric = item.get("metric", {})
        value = item.get("value", [None, "0"])[1]
        row = {key: metric.get(key, "") for key in label_keys}
        row[value_name] = float(value)
        rows.append(row)
    return rows


def export_pod_metrics(namespace: str) -> pd.DataFrame:
    """Export pod-level CPU, memory, network, and energy metrics."""
    cpu_rows = rows_from_query(
        f'sum by (pod)(rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod!=""}}[1m]))',
        "cpu_cores",
        ["pod"],
    )
    mem_rows = rows_from_query(
        f'sum by (pod)(container_memory_working_set_bytes{{namespace="{namespace}",pod!=""}})',
        "memory_bytes",
        ["pod"],
    )
    rx_rows = rows_from_query(
        f'sum by (pod)(rate(container_network_receive_bytes_total{{namespace="{namespace}",pod!=""}}[1m]))',
        "network_receive_bytes_per_sec",
        ["pod"],
    )
    tx_rows = rows_from_query(
        f'sum by (pod)(rate(container_network_transmit_bytes_total{{namespace="{namespace}",pod!=""}}[1m]))',
        "network_transmit_bytes_per_sec",
        ["pod"],
    )

    energy_rows = []
    kepler_available = len(prom_query("kepler_container_joules_total")) > 0
    if kepler_available:
        energy_rows = rows_from_query(
            f'sum by (container_name)(rate(kepler_container_joules_total{{namespace="{namespace}"}}[1m]))',
            "energy_joules_per_sec",
            ["container_name"],
        )
        for row in energy_rows:
            row["pod"] = row.pop("container_name", "")
    else:
        print("[WARN] Kepler metrics unavailable. Energy will be estimated from CPU.")

    frames = []
    for rows, rename_map in [
        (cpu_rows, {"pod": "pod_name"}),
        (mem_rows, {"pod": "pod_name"}),
        (rx_rows, {"pod": "pod_name"}),
        (tx_rows, {"pod": "pod_name"}),
        (energy_rows, {"pod": "pod_name"}),
    ]:
        if rows:
            frame = pd.DataFrame(rows).rename(columns=rename_map)
            frames.append(frame)

    if not frames:
        return pd.DataFrame()

    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on="pod_name", how="outer")

    merged["namespace"] = namespace
    merged["timestamp"] = datetime.now(timezone.utc).isoformat()
    merged["energy_source"] = "kepler_real" if kepler_available else "estimated"

    if "energy_joules_per_sec" not in merged.columns:
        merged["energy_joules_per_sec"] = merged.get("cpu_cores", 0.0) * 0.4
    else:
        merged["energy_joules_per_sec"] = merged["energy_joules_per_sec"].fillna(
            merged.get("cpu_cores", 0.0) * 0.4
        )

    return merged.fillna(0.0)


def export_node_metrics() -> pd.DataFrame:
    """Export node-level CPU, memory, and network metrics."""
    cpu_rows = rows_from_query(
        '100 - (avg by (instance)(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)',
        "cpu_utilization_percent",
        ["instance"],
    )
    mem_rows = rows_from_query(
        "100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))",
        "memory_utilization_percent",
        ["instance"],
    )
    rx_rows = rows_from_query(
        "sum by (instance)(rate(node_network_receive_bytes_total[1m]))",
        "network_receive_bytes_per_sec",
        ["instance"],
    )
    tx_rows = rows_from_query(
        "sum by (instance)(rate(node_network_transmit_bytes_total[1m]))",
        "network_transmit_bytes_per_sec",
        ["instance"],
    )

    frames = [pd.DataFrame(rows) for rows in [cpu_rows, mem_rows, rx_rows, tx_rows] if rows]
    if not frames:
        return pd.DataFrame()

    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on="instance", how="outer")

    merged["timestamp"] = datetime.now(timezone.utc).isoformat()
    return merged.fillna(0.0)


def export_metrics(output_dir: Path, namespace: str = TARGET_NAMESPACE) -> dict[str, Path]:
    """Export pod and node metrics to timestamped CSV files."""
    ensure_result_dirs()
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    pod_df = export_pod_metrics(namespace)
    node_df = export_node_metrics()

    pod_path = output_dir / f"pod_metrics_{stamp}.csv"
    node_path = output_dir / f"node_metrics_{stamp}.csv"

    if pod_df.empty:
        print("[WARN] No pod metrics returned from Prometheus.")
    else:
        pod_df.to_csv(pod_path, index=False)
        print(f"[OK] Pod metrics saved to {pod_path}")

    if node_df.empty:
        print("[WARN] No node metrics returned from Prometheus.")
    else:
        node_df.to_csv(node_path, index=False)
        print(f"[OK] Node metrics saved to {node_path}")

    return {"pod_metrics": pod_path, "node_metrics": node_path}


def main() -> None:
    """CLI entry point for metric export."""
    parser = argparse.ArgumentParser(description="Export Prometheus/Kepler metrics to CSV")
    parser.add_argument("--output-dir", default=str(RAW_METRICS_DIR))
    parser.add_argument("--namespace", default=TARGET_NAMESPACE)
    parser.add_argument("--duration-seconds", type=int, default=0, help="Optional repeated sampling duration")
    parser.add_argument("--interval-seconds", type=int, default=15)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    if args.duration_seconds <= 0:
        export_metrics(output_dir, args.namespace)
        return

    end_time = time.time() + args.duration_seconds
    while time.time() < end_time:
        export_metrics(output_dir, args.namespace)
        time.sleep(max(args.interval_seconds, 1))


if __name__ == "__main__":
    main()
