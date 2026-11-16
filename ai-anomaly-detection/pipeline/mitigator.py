"""
mitigator.py
============
Progressive, Deployment-level mitigation for detected attack Pods.

Strategy
--------
Step 1 (THROTTLED)  – First confirmation of an attack Pod.
    * Walk the owner chain: Pod -> ReplicaSet -> Deployment.
    * Patch the Deployment's pod-template container resources so every
      new Pod spawned from it is CPU/memory constrained.
    * Wait for the rollout to complete before returning.

Step 2 (DELETED)    – After THROTTLE_DURATION_WINDOWS windows have elapsed.
    * Delete the specific attack Pod so it is replaced by the already-
      throttled pod-template, completing the mitigation lifecycle.

Why not patch the running Pod?
    Kubernetes treats resources.limits on a running Pod as immutable; any
    attempt to PATCH them will be rejected with a 422 Unprocessable Entity.
    Patching the *Deployment template* is the correct production approach.
"""

import csv
import json
import os
import subprocess
import time

import config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(cmd: list) -> tuple:
    """Run *cmd* and return (success, stdout_or_stderr).  Never raises."""
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as exc:
        return False, exc.stderr.strip()


def _kubectl(*args) -> tuple:
    """Convenience wrapper that always prepends 'kubectl'."""
    return _run(["kubectl"] + list(args))


def _get_jsonpath(resource: str, name: str, namespace: str, jsonpath: str):
    """Return the value at *jsonpath* for the given resource, or None on failure."""
    ok, out = _kubectl(
        "get", resource, name,
        "-n", namespace,
        "-o", "jsonpath={}".format(jsonpath),
    )
    return out if ok else None


# ---------------------------------------------------------------------------
# Owner-chain resolution
# ---------------------------------------------------------------------------

def _owning_replicaset(pod_name: str, namespace: str):
    """
    Return the name of the ReplicaSet that owns *pod_name*, or None.

    We inspect .metadata.ownerReferences[?(@.kind=='ReplicaSet')].name.
    """
    owners_json = _get_jsonpath("pod", pod_name, namespace, "{.metadata.ownerReferences}")
    if not owners_json:
        return None
    try:
        owners = json.loads(owners_json)
        for owner in owners:
            if owner.get("kind") == "ReplicaSet":
                return owner.get("name")
    except (json.JSONDecodeError, TypeError):
        pass
    return None


def _owning_deployment(rs_name: str, namespace: str):
    """
    Return the name of the Deployment that owns *rs_name*, or None.
    """
    owners_json = _get_jsonpath("replicaset", rs_name, namespace, "{.metadata.ownerReferences}")
    if not owners_json:
        return None
    try:
        owners = json.loads(owners_json)
        for owner in owners:
            if owner.get("kind") == "Deployment":
                return owner.get("name")
    except (json.JSONDecodeError, TypeError):
        pass
    return None


def _find_deployment(pod_name: str, namespace: str):
    """Resolve Pod -> ReplicaSet -> Deployment and return the Deployment name."""
    rs = _owning_replicaset(pod_name, namespace)
    if not rs:
        print("[MITIGATION]   Could not find owning ReplicaSet for Pod '{}'".format(pod_name))
        return None
    deployment = _owning_deployment(rs, namespace)
    if not deployment:
        print("[MITIGATION]   ReplicaSet '{}' has no owning Deployment".format(rs))
    return deployment


# ---------------------------------------------------------------------------
# Deployment patching
# ---------------------------------------------------------------------------

def _container_name_from_deployment(deployment: str, namespace: str) -> str:
    """Return the first container name in the Deployment's pod template."""
    name = _get_jsonpath(
        "deployment", deployment, namespace,
        "{.spec.template.spec.containers[0].name}",
    )
    return name if name else deployment  # safe fallback


def _throttle_deployment(deployment: str, namespace: str) -> bool:
    """
    Patch the Deployment's pod-template so every (re-)created Pod is resource-
    constrained.  Waits for the rollout to finish before returning.

    Returns True if both the patch and the rollout succeeded.
    """
    container = _container_name_from_deployment(deployment, namespace)

    # Strategic-merge patch on the pod template (immutable pod spec fields
    # belong to the *running Pod*, not the template -- this is legal).
    patch = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": container,
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
        }
    }

    print("[MITIGATION] Patching Deployment '{}' (container '{}') -> cpu<={}, mem<={}".format(
        deployment, container, config.THROTTLE_CPU_LIMIT, config.THROTTLE_MEMORY_LIMIT))

    ok, err = _kubectl(
        "patch", "deployment", deployment,
        "-n", namespace,
        "--patch", json.dumps(patch),
    )
    if not ok:
        print("[MITIGATION] patch deployment failed: {}".format(err))
        return False

    # Wait for the rolling update to complete (timeout: 120 s).
    print("[MITIGATION] Waiting for rollout of Deployment '{}' ...".format(deployment))
    ok, out = _kubectl(
        "rollout", "status",
        "deployment/{}".format(deployment),
        "-n", namespace,
        "--timeout=120s",
    )
    if ok:
        print("[MITIGATION] Rollout complete: {}".format(out))
    else:
        print("[MITIGATION] Rollout did not finish cleanly: {}".format(out))

    return ok


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

class Mitigator:
    """
    Progressive Deployment-level mitigator.

    State is tracked per *pod_name*.  The pod_name acts as the user-visible
    identity even though the actual Kubernetes operation targets the owning
    Deployment.
    """

    def __init__(self) -> None:
        self.throttled_pods = {}
        os.makedirs(os.path.dirname(config.MITIGATION_LOG_PATH), exist_ok=True)
        if not os.path.exists(config.MITIGATION_LOG_PATH):
            with open(config.MITIGATION_LOG_PATH, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["timestamp", "pod_name", "action", "status", "score"])

    # ------------------------------------------------------------------
    def log_mitigation(self, pod_name: str, action: str, status: str, score: float) -> None:
        """Append one row to the mitigation CSV log."""
        with open(config.MITIGATION_LOG_PATH, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([time.time(), pod_name, action, status, score])

    def prune_pods(self, live_pods: set[str]) -> None:
        """Remove mitigation tracking state for pods that no longer exist."""
        stale = [pod_name for pod_name in self.throttled_pods if pod_name not in live_pods]
        for pod_name in stale:
            del self.throttled_pods[pod_name]

    # ------------------------------------------------------------------
    def mitigate(self, pod_name: str, namespace: str, score: float, consecutive_count: int) -> str:
        """
        Progressive mitigation entry-point called by main.py.

        Parameters
        ----------
        pod_name         : Kubernetes Pod name of the detected attacker.
        namespace        : Kubernetes namespace the Pod lives in.
        score            : Anomaly score from the model (for logging).
        consecutive_count: Number of consecutive anomalous windows.

        Returns
        -------
        "THROTTLED" or "DELETED"
        """
        # -- STEP 1: First detection -- throttle the owning Deployment ------
        if pod_name not in self.throttled_pods:
            print("\n[MITIGATION] STEP 1: Throttling Deployment for attack Pod '{}'".format(pod_name))

            deployment = _find_deployment(pod_name, namespace)
            if deployment is None:
                # Cannot walk the owner chain -- log failure and bail.
                self.log_mitigation(pod_name, "THROTTLED", "FAILED", score)
                # Register anyway so we don't hammer the API on every window.
                self.throttled_pods[pod_name] = {
                    "timestamp": time.time(),
                    "windows_since_throttle": 0,
                    "deployment": None,
                }
                return "THROTTLED"

            ok = _throttle_deployment(deployment, namespace)
            self.throttled_pods[pod_name] = {
                "timestamp": time.time(),
                "windows_since_throttle": 0,
                "deployment": deployment,
            }

            status = "SUCCESS" if ok else "FAILED"
            self.log_mitigation(pod_name, "THROTTLED", status, score)

            if ok:
                print("  STEP 1 COMPLETE: Deployment '{}' throttled (cpu<={}, mem<={})".format(
                    deployment, config.THROTTLE_CPU_LIMIT, config.THROTTLE_MEMORY_LIMIT))
            else:
                print("  STEP 1 FAILED: Could not throttle Deployment '{}'".format(deployment))

            return "THROTTLED"

        # -- STEP 2: Subsequent windows -- wait, then delete the attack Pod --
        self.throttled_pods[pod_name]["windows_since_throttle"] += 1
        windows_elapsed = self.throttled_pods[pod_name]["windows_since_throttle"]

        if windows_elapsed >= config.THROTTLE_DURATION_WINDOWS:
            deployment = self.throttled_pods[pod_name].get("deployment", "<unknown>")
            print("\n[MITIGATION] STEP 2: Deleting attack Pod '{}' "
                  "(throttled via Deployment '{}' for {} windows)".format(
                      pod_name, deployment, windows_elapsed))

            ok, err = _kubectl("delete", "pod", pod_name, "-n", namespace)
            del self.throttled_pods[pod_name]

            status = "SUCCESS" if ok else "FAILED"
            self.log_mitigation(pod_name, "DELETED", status, score)

            if ok:
                print("  STEP 2 COMPLETE: Pod '{}' deleted -- replacement will use throttled Deployment template.".format(pod_name))
            else:
                print("  STEP 2 FAILED: {}".format(err))

            return "DELETED"

        # Still within the throttle observation window.
        remaining = config.THROTTLE_DURATION_WINDOWS - windows_elapsed
        print("[MITIGATION] Pod '{}' throttled ({}/{} windows) -- deletion in {} more window(s).".format(
            pod_name, windows_elapsed, config.THROTTLE_DURATION_WINDOWS, remaining))
        return "THROTTLED"
