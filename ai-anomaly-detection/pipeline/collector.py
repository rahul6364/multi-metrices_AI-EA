import csv
import os
import time
from dataclasses import dataclass, asdict
from typing import Dict

import requests

import config


@dataclass
class PodSample:
    timestamp: float
    pod_name: str
    namespace: str
    cpu_cores: float
    memory_bytes: float
    memory_mb: float
    network_rx_bytes_per_sec: float
    network_tx_bytes_per_sec: float
    energy_joules: float
    energy_source: str
    is_attack_pod: bool


class MetricsCollector:
    def __init__(self) -> None:
        self.prom_url = config.PROMETHEUS_URL.rstrip("/")
        self.kepler_available = False
        self._k8s_token_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"
        self._k8s_ca_path = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
        self._k8s_api = "https://kubernetes.default.svc"
        self._ensure_raw_csv()
        self._test_prometheus_connection()
        self._detect_kepler()

    def _ensure_raw_csv(self) -> None:
        os.makedirs(os.path.dirname(config.RAW_DATA_PATH), exist_ok=True)
        if not os.path.exists(config.RAW_DATA_PATH):
            with open(config.RAW_DATA_PATH, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(list(PodSample.__annotations__.keys()))

    def _prom_query(self, query: str) -> list[dict]:
        r = requests.get(f"{self.prom_url}/api/v1/query", params={"query": query}, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "success":
            return []
        return data.get("data", {}).get("result", [])

    def _test_prometheus_connection(self) -> None:
        for i in range(5):
            try:
                self._prom_query("up")
                return
            except Exception as exc:
                print(f"[PROMETHEUS] Retry {i + 1}/5 failed: {exc}")
                time.sleep(3)
        raise RuntimeError("Prometheus connection failed after retries")

    def _detect_kepler(self) -> None:
        try:
            results = self._prom_query("kepler_container_joules_total")
            self.kepler_available = len(results) > 0
        except Exception:
            self.kepler_available = False
        if self.kepler_available:
            print("[KEPLER] Real energy metrics active")
        else:
            print("[ENERGY] Software estimation mode (Kepler unavailable)")

    @staticmethod
    def _f(value: str) -> float:
        try:
            return float(value)
        except Exception:
            return 0.0

    def _by_pod(self, query: str, label: str = "pod") -> Dict[str, float]:
        out: Dict[str, float] = {}
        for row in self._prom_query(query):
            metric = row.get("metric", {})
            pod = metric.get(label) or metric.get("pod") or metric.get("container_name")
            if not pod:
                continue
            out[pod] = self._f(row.get("value", [0, 0])[1])
        return out

    def _save(self, sample: PodSample) -> None:
        with open(config.RAW_DATA_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(PodSample.__annotations__.keys()))
            writer.writerow(asdict(sample))

    def _live_pods_from_k8s(self, namespace: str) -> set[str]:
        try:
            with open(self._k8s_token_path, "r", encoding="utf-8") as f:
                token = f.read().strip()
            headers = {"Authorization": f"Bearer {token}"}
            resp = requests.get(
                f"{self._k8s_api}/api/v1/namespaces/{namespace}/pods",
                headers=headers,
                timeout=5,
                verify=self._k8s_ca_path,
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])
            # Only keep active pods; drop succeeded/failed/terminating ones.
            live = set()
            for item in items:
                name = item.get("metadata", {}).get("name")
                phase = item.get("status", {}).get("phase")
                deletion_ts = item.get("metadata", {}).get("deletionTimestamp")
                if not name or deletion_ts:
                    continue
                if phase in {"Running", "Pending"}:
                    live.add(name)
            return live
        except Exception as exc:
            print(f"[K8S] Live pod filter unavailable, using Prometheus-only list: {exc}")
            return set()

    def collect_all_pods(self) -> Dict[str, PodSample]:
        ns = config.TARGET_NAMESPACE
        cpu = self._by_pod(f'sum by(pod)(rate(container_cpu_usage_seconds_total{{namespace="{ns}",pod!=""}}[30s]))')
        mem = self._by_pod(f'sum by(pod)(container_memory_working_set_bytes{{namespace="{ns}",pod!=""}})')
        rx = self._by_pod(f'sum by(pod)(rate(container_network_receive_bytes_total{{namespace="{ns}",pod!=""}}[30s]))')
        tx = self._by_pod(f'sum by(pod)(rate(container_network_transmit_bytes_total{{namespace="{ns}",pod!=""}}[30s]))')

        energy = {}
        energy_source = "estimated"
        if self.kepler_available:
            try:
                energy = self._by_pod(
                    f'sum by(container_name)(rate(kepler_container_joules_total{{namespace="{ns}"}}[30s]))',
                    label="container_name",
                )
                energy_source = "kepler_real"
            except Exception:
                energy_source = "estimated"

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
                energy_joules=energy.get(pod, cpu_cores * 0.4) if energy_source == "kepler_real" else cpu_cores * 0.4,
                energy_source=energy_source,
                is_attack_pod=pod.startswith("attack-"),
            )
            if sample.namespace in config.SYSTEM_NAMESPACES:
                continue
            self._save(sample)
            samples[pod] = sample

        return samples
