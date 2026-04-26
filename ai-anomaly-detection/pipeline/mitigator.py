import csv
import json
import os
import subprocess
import time

import config


class Mitigator:
    def __init__(self) -> None:
        self.throttled_pods = {}
        os.makedirs(os.path.dirname(config.MITIGATION_LOG_PATH), exist_ok=True)
        if not os.path.exists(config.MITIGATION_LOG_PATH):
            with open(config.MITIGATION_LOG_PATH, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["timestamp", "pod_name", "action", "status", "score"])

    def log_mitigation(self, pod_name: str, action: str, status: str, score: float) -> None:
        with open(config.MITIGATION_LOG_PATH, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([time.time(), pod_name, action, status, score])

    def _run(self, cmd: list[str]) -> bool:
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as exc:
            print(f"[MITIGATION] Failed: {' '.join(cmd)} -> {exc.stderr}")
            return False

    def _pod_container_name(self, pod_name: str, namespace: str) -> str:
        try:
            cmd = [
                "kubectl", "get", "pod", pod_name, "-n", namespace,
                "-o", "jsonpath={.spec.containers[0].name}",
            ]
            res = subprocess.run(cmd, check=True, capture_output=True, text=True)
            name = res.stdout.strip()
            return name if name else pod_name
        except Exception:
            return pod_name

    def mitigate(self, pod_name: str, namespace: str, score: float, consecutive_count: int) -> str:
        if pod_name not in self.throttled_pods:
            print(f"⚠️  STEP 1: Throttling pod {pod_name}")
            container_name = self._pod_container_name(pod_name, namespace)
            patch = {
                "spec": {
                    "containers": [
                        {
                            "name": container_name,
                            "resources": {
                                "limits": {
                                    "cpu": config.THROTTLE_CPU_LIMIT,
                                    "memory": config.THROTTLE_MEMORY_LIMIT,
                                }
                            },
                        }
                    ]
                }
            }
            ok = self._run(["kubectl", "patch", "pod", pod_name, "-n", namespace, "--patch", json.dumps(patch)])
            self.throttled_pods[pod_name] = {"timestamp": time.time(), "windows_since_throttle": 0}
            self.log_mitigation(pod_name, "THROTTLED", "SUCCESS" if ok else "FAILED", score)
            return "THROTTLED"

        self.throttled_pods[pod_name]["windows_since_throttle"] += 1
        if self.throttled_pods[pod_name]["windows_since_throttle"] >= config.THROTTLE_DURATION_WINDOWS:
            print(f"🔴 STEP 2: Deleting pod {pod_name} (throttling ineffective)")
            ok = self._run(["kubectl", "delete", "pod", pod_name, "-n", namespace])
            del self.throttled_pods[pod_name]
            self.log_mitigation(pod_name, "DELETED", "SUCCESS" if ok else "FAILED", score)
            return "DELETED"

        return "THROTTLED"
