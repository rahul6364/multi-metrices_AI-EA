"""
Original File: ai-anomaly-detection/pipeline/collector.py
Original Entity: MetricsCollector.collect_all_pods
Lines: 123–167
Status: Implemented
Module: D.1 – Kubernetes Monitoring and Metric Collection
"""

from typing import Dict
import time
import config
from collector import PodSample

def collect_all_pods(self) -> Dict[str, PodSample]:
    """Query Prometheus for multi-pod resource metrics and synchronize with live K8s pods."""
    ns = config.TARGET_NAMESPACE
    cpu = self._by_pod(f'sum by(pod)(rate(container_cpu_usage_seconds_total{{namespace="{ns}",pod!=""}}[30s]))')
    mem = self._by_pod(f'sum by(pod)(container_memory_working_set_bytes{{namespace="{ns}",pod!=""}})')
    rx = self._by_pod(f'sum by(pod)(rate(container_network_receive_bytes_total{{namespace="{ns}",pod!=""}}[30s]))')
    tx = self._by_pod(f'sum by(pod)(rate(container_network_transmit_bytes_total{{namespace="{ns}",pod!=""}}[30s]))')

    now = time.time()
    pods = set(cpu) | set(mem) | set(rx) | set(tx)
    live_pods = self._live_pods_from_k8s(ns)
    if live_pods:
        pods = {pod for pod in pods if pod in live_pods}

    samples: Dict[str, PodSample] = {}
    for pod in sorted(pods):
        cpu_cores = cpu.get(pod, 0.0)
        sample = PodSample(
            timestamp=now,
            pod_name=pod,
            namespace=ns,
            cpu_cores=cpu_cores,
            memory_bytes=mem.get(pod, 0.0),
            memory_mb=mem.get(pod, 0.0) / (1024 * 1024),
            network_rx_bytes_per_sec=rx.get(pod, 0.0),
            network_tx_bytes_per_sec=tx.get(pod, 0.0),
            energy_joules=cpu_cores * 0.4,
            energy_source="estimated",
            is_attack_pod=pod.startswith("attack-"),
        )
        if sample.namespace in config.SYSTEM_NAMESPACES:
            continue
        self._save(sample)
        samples[pod] = sample
    return samples
