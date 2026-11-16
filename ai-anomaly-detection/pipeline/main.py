import csv
import os
import threading
import time
import traceback

import config
from collector import MetricsCollector
from dashboard import create_app
from evaluator import Evaluator
from feature_engineer import FeatureEngineer
from mitigator import Mitigator
from model_manager import ModelManager
from research_logger import ResearchLogger
from state_manager import StateManager


def _ensure_detection_log() -> None:
    os.makedirs(os.path.dirname(config.DETECTION_LOG_PATH), exist_ok=True)
    if not os.path.exists(config.DETECTION_LOG_PATH):
        with open(config.DETECTION_LOG_PATH, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["timestamp", "pod", "cpu", "mem_mb", "energy", "e_cpu", "ea", "basic", "score", "consecutive"])


def _log_detection(pod, fdict, result) -> None:
    with open(config.DETECTION_LOG_PATH, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            time.time(), pod, fdict["avg_cpu"], fdict["avg_memory_mb"], fdict["avg_energy"], fdict["energy_cpu_ratio"],
            result.prediction_ea, result.prediction_basic, result.score_ea, result.consecutive_count,
        ])


def _should_monitor_pod(pod_name: str, namespace: str) -> bool:
    if namespace in config.SYSTEM_NAMESPACES:
        return False
    return not any(pod_name.startswith(prefix) for prefix in config.EXCLUDED_POD_PREFIXES)


def startup():
    collector = MetricsCollector()
    feature_engineer = FeatureEngineer()
    model_manager = ModelManager()
    mitigator = Mitigator()
    evaluator = Evaluator()
    state_manager = StateManager()
    research_logger = ResearchLogger()
    _ensure_detection_log()

    state_manager.set_kepler_active(collector.kepler_available)

    app = create_app(state_manager, model_manager, evaluator)
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=config.DASHBOARD_PORT, debug=False, use_reloader=False), daemon=True).start()

    print("╔══════════════════════════════════════════╗")
    print("║  AI-Based Energy-Aware Anomaly Detection ║")
    print("║  Sahyadri College of Engineering         ║")
    print("║  Team CSE-26                             ║")
    print("╚══════════════════════════════════════════╝")
    print("Dashboard: http://localhost:8080")
    print("Prometheus: http://localhost:9090")
    print("Grafana: http://localhost:3000")
    print("State: IDLE - Open dashboard to start")

    return collector, feature_engineer, model_manager, mitigator, state_manager, research_logger


def main_loop():
    collector, feature_engineer, model_manager, mitigator, state_manager, research_logger = startup()

    while True:
        try:
            samples = collector.collect_all_pods()
            state_manager.set_state(model_manager.state)
            state_manager.set_training_progress(model_manager.training_progress_windows(), config.MIN_TRAINING_WINDOWS)
            state_manager.set_model_trained(model_manager.state == config.STATE_DETECTING)

            for pod_name, sample in samples.items():
                if not _should_monitor_pod(pod_name, sample.namespace):
                    continue

                state_manager.update_pod_metrics(pod_name, sample)

                if not feature_engineer.add_sample(pod_name, sample):
                    continue

                features = feature_engineer.extract_features(pod_name)

                if model_manager.state == config.STATE_COLLECTING:
                    model_manager.add_training_window(
                        features["features_16"], features["features_6"], pod_name, sample.namespace
                    )
                    print(
                        f"[{time.strftime('%H:%M:%S')}] COLLECTING | Pod: {pod_name:35} | "
                        f"CPU: {features['feature_dict']['avg_cpu']:.4f} | Mem: {features['feature_dict']['avg_memory_mb']:.1f}MB | "
                        f"Energy: {features['feature_dict']['avg_energy']:.4f}J | "
                        f"Windows: {model_manager.training_progress_windows()}/{config.MIN_TRAINING_WINDOWS}"
                    )
                    continue

                if model_manager.state == config.STATE_DETECTING:
                    result = model_manager.predict(
                        features["features_16"], features["features_6"], pod_name, features["feature_dict"]
                    )
                    state_manager.add_detection(result)
                    _log_detection(pod_name, features["feature_dict"], result)
                    research_logger.log_detection_cycle(sample, features["feature_dict"], result)

                    print(
                        f"[{time.strftime('%H:%M:%S')}] Pod: {pod_name:35} | "
                        f"CPU: {features['feature_dict']['avg_cpu']:.4f} | Mem: {features['feature_dict']['avg_memory_mb']:.1f}MB | "
                        f"Energy: {features['feature_dict']['avg_energy']:.4f}J | "
                        f"E/CPU: {features['feature_dict']['energy_cpu_ratio']:.4f} | "
                        f"EA: {result.prediction_ea:8} | Basic: {result.prediction_basic:8} | "
                        f"Score: {result.score_ea:.4f} | Consec: {result.consecutive_count}"
                    )

                    # Progressive mitigation is reserved for attack workloads only.
                    if result.confirmed_attack and pod_name.startswith("attack-"):
                        print(f"⚠️  ATTACK CONFIRMED: {pod_name}")
                        print(f"   EA Score: {result.score_ea:.4f} | Basic Score: {result.score_basic:.4f}")
                        action = mitigator.mitigate(pod_name, sample.namespace, result.score_ea, result.consecutive_count)
                        research_logger.log_mitigation_event(pod_name, action)
                        state_manager.add_mitigation({
                            "timestamp": time.time(),
                            "pod_name": pod_name,
                            "action": action,
                            "status": "SUCCESS",
                            "score": result.score_ea,
                        })

            # Keep live dashboard pod list aligned with currently active pods.
            state_manager.prune_stale_pods(max_stale_seconds=config.COLLECTION_INTERVAL * 3)
            live_pods = set(state_manager.pods.keys())
            model_manager.prune_pods(live_pods)
            mitigator.prune_pods(live_pods)
        except Exception as exc:
            print(f"[ERROR] Main loop failure: {exc}")
            traceback.print_exc()

        time.sleep(config.COLLECTION_INTERVAL)


if __name__ == "__main__":
    main_loop()
