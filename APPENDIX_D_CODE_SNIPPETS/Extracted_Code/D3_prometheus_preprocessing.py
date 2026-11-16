"""
Original File: experiments/export_metrics.py
Original Entity: export_pod_metrics
Lines: 48–114
Status: Implemented
Module: D.3 – Prometheus Metric Extraction and Data Preprocessing
"""

import pandas as pd
from datetime import datetime, timezone

def export_pod_metrics(namespace: str) -> pd.DataFrame:
    """Export and preprocess pod-level CPU, memory, network, and energy metrics from Prometheus."""
    cpu_rows = rows_from_query(f'sum by (pod)(rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod!=""}}[1m]))', "cpu_cores", ["pod"])
    mem_rows = rows_from_query(f'sum by (pod)(container_memory_working_set_bytes{{namespace="{namespace}",pod!=""}})', "memory_bytes", ["pod"])
    rx_rows = rows_from_query(f'sum by (pod)(rate(container_network_receive_bytes_total{{namespace="{namespace}",pod!=""}}[1m]))', "network_rx", ["pod"])
    tx_rows = rows_from_query(f'sum by (pod)(rate(container_network_transmit_bytes_total{{namespace="{namespace}",pod!=""}}[1m]))', "network_tx", ["pod"])

    kepler_available = len(prom_query("kepler_container_joules_total")) > 0
    energy_rows = rows_from_query(f'sum by (container_name)(rate(kepler_container_joules_total{{namespace="{namespace}"}}[1m]))', "energy_joules", ["container_name"]) if kepler_available else []
    for row in energy_rows:
        row["pod"] = row.pop("container_name", "")

    frames = [pd.DataFrame(r).rename(columns={"pod": "pod_name"}) for r in [cpu_rows, mem_rows, rx_rows, tx_rows, energy_rows] if r]
    if not frames:
        return pd.DataFrame()

    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on="pod_name", how="outer")

    merged["namespace"] = namespace
    merged["timestamp"] = datetime.now(timezone.utc).isoformat()
    merged["energy_source"] = "kepler_real" if kepler_available else "estimated"
    merged["energy_joules"] = merged.get("energy_joules", merged.get("cpu_cores", 0.0) * 0.4).fillna(merged.get("cpu_cores", 0.0) * 0.4)
    return merged.fillna(0.0)
