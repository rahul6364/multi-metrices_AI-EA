"""
Original File: ai-anomaly-detection/pipeline/collector.py
Original Entity: MetricsCollector._detect_kepler and collect_all_pods (energy branch)
Lines: 62–72, 130–141, 159–160
Status: Implemented
Module: D.2 – Energy Metric Collection Using Kepler
"""

def _detect_kepler(self) -> None:
    """Detect whether Kepler eBPF metrics are available via Prometheus."""
    try:
        results = self._prom_query("kepler_container_joules_total")
        self.kepler_available = len(results) > 0
    except Exception:
        self.kepler_available = False
    if self.kepler_available:
        print("[KEPLER] Real energy metrics active")
    else:
        print("[ENERGY] Software estimation mode (Kepler unavailable)")

def _collect_energy_telemetry(self, ns: str, cpu_cores: float, pod: str) -> tuple[float, str]:
    """Extract Kepler eBPF joules rate or apply calibrated software estimation fallback."""
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

    # Assign real energy if Kepler is active; fallback to 0.4 * CPU cores in WSL2/VMs
    energy_joules = energy.get(pod, cpu_cores * 0.4) if energy_source == "kepler_real" else cpu_cores * 0.4
    return energy_joules, energy_source
