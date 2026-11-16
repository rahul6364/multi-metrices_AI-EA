"""
Original File: ai-anomaly-detection/pipeline/mitigator.py
Original Entity: Mitigator.mitigate and _throttle_deployment
Lines: 126–182, 233–289
Status: Implemented
Module: D.9 – Kubernetes-Based Anomaly Mitigation
"""

import json
import config
from mitigator import _kubectl, _find_deployment, _container_name_from_deployment

def _throttle_deployment(deployment: str, namespace: str) -> bool:
    """Apply strategic-merge patch to throttle Deployment container CPU/memory limits."""
    container = _container_name_from_deployment(deployment, namespace)
    patch = {"spec": {"template": {"spec": {"containers": [{
        "name": container,
        "resources": {"limits": {"cpu": config.THROTTLE_CPU_LIMIT, "memory": config.THROTTLE_MEMORY_LIMIT}}
    }]}}}}
    ok, err = _kubectl("patch", "deployment", deployment, "-n", namespace, "--patch", json.dumps(patch))
    if ok:
        _kubectl("rollout", "status", f"deployment/{deployment}", "-n", namespace, "--timeout=120s")
    return ok

def mitigate(self, pod_name: str, namespace: str, score: float, consecutive_count: int) -> str:
    """Execute progressive 2-stage mitigation: throttle Deployment first, delete pod after observation."""
    if pod_name not in self.throttled_pods:
        # STEP 1: First confirmed detection -> throttle owning Deployment template
        deployment = _find_deployment(pod_name, namespace)
        ok = _throttle_deployment(deployment, namespace) if deployment else False
        self.throttled_pods[pod_name] = {"windows_since_throttle": 0, "deployment": deployment}
        self.log_mitigation(pod_name, "THROTTLED", "SUCCESS" if ok else "FAILED", score)
        return "THROTTLED"

    # STEP 2: Subsequent windows -> wait observation duration, then terminate offending pod
    self.throttled_pods[pod_name]["windows_since_throttle"] += 1
    if self.throttled_pods[pod_name]["windows_since_throttle"] >= config.THROTTLE_DURATION_WINDOWS:
        ok, err = _kubectl("delete", "pod", pod_name, "-n", namespace)
        del self.throttled_pods[pod_name]
        self.log_mitigation(pod_name, "DELETED", "SUCCESS" if ok else "FAILED", score)
        return "DELETED"
    return "THROTTLED"

