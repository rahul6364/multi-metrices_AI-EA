# APPENDIX – D: CODE SNIPPETS OF MAJOR MODULES

## Traceability & Implementation Index

**Project Title:** Multi-Metric Energy-Aware Behavioral Anomaly Detection and Automated Mitigation in Kubernetes-Based Cloud Systems  
**Institution:** Sahyadri College of Engineering & Management, Mangaluru (Autonomous)  
**Department:** Computer Science & Engineering | **Team:** CSE-26  
**Target Standard:** Visvesvaraya Technological University (VTU) B.E. Major Project Report Format  

---

### Module Implementation Summary Table

| Figure Number | Module Name | Original Source File | Original Function / Entity | Extracted Lines | Implementation Status |
|:---:|:---|:---|:---|:---:|:---:|
| **D.1** | Kubernetes Monitoring and Metric Collection | `ai-anomaly-detection/pipeline/collector.py` | `MetricsCollector.collect_all_pods` | 40 | <span style="color:green;font-weight:bold;">✓ Implemented</span> |
| **D.2** | Energy Metric Collection Using Kepler | `ai-anomaly-detection/pipeline/collector.py` | `MetricsCollector._detect_kepler and collect_all_pods (energy branch)` | 29 | <span style="color:green;font-weight:bold;">✓ Implemented</span> |
| **D.3** | Prometheus Metric Extraction and Data Preprocessing | `experiments/export_metrics.py` | `export_pod_metrics` | 28 | <span style="color:green;font-weight:bold;">✓ Implemented</span> |
| **D.4** | Multi-Metric Feature Engineering | `ai-anomaly-detection/pipeline/feature_engineer.py` | `FeatureEngineer.extract_features` | 33 | <span style="color:green;font-weight:bold;">✓ Implemented</span> |
| **D.5** | Isolation Forest Model Training | `ai-anomaly-detection/pipeline/model_manager.py` | `ModelManager.train_both_models` | 38 | <span style="color:green;font-weight:bold;">✓ Implemented</span> |
| **D.6** | Anomaly Detection and Anomaly Score Generation | `ai-anomaly-detection/pipeline/model_manager.py` | `ModelManager.predict` | 37 | <span style="color:green;font-weight:bold;">✓ Implemented</span> |
| **D.7** | Baseline Detection and Comparative Analysis | `ai-anomaly-detection/pipeline/evaluator.py` | `Evaluator._calc and calculate_metrics` | 37 | <span style="color:green;font-weight:bold;">✓ Implemented</span> |
| **D.8** | Controlled Attack and Workload Simulation | `experiments/run_experiment.py` | `run_experiment and _wait_for_attack_outcome` | 31 | <span style="color:green;font-weight:bold;">✓ Implemented</span> |
| **D.9** | Kubernetes-Based Anomaly Mitigation | `ai-anomaly-detection/pipeline/mitigator.py` | `Mitigator.mitigate and _throttle_deployment` | 35 | <span style="color:green;font-weight:bold;">✓ Implemented</span> |
| **D.10** | Performance Evaluation and Research Logging | `ai-anomaly-detection/pipeline/research_logger.py` | `ResearchLogger.log_detection_cycle and _update_latency_tracking` | 33 | <span style="color:green;font-weight:bold;">✓ Implemented</span> |

---

### Detailed Module Specifications

#### D.1 – Kubernetes Monitoring and Metric Collection

- **Primary Source File:** `ai-anomaly-detection/pipeline/collector.py`
- **Original Entity/Block:** `MetricsCollector.collect_all_pods`
- **Original Source Lines:** Lines 123–167
- **Extracted Clean Code File:** `Extracted_Code/D1_monitoring.py` (40 lines)
- **High-Resolution Figure Image:** `Code_Screenshots/Figure_D1_Kubernetes_Monitoring.png`
- **Figure Caption:** *Figure D.1: Prometheus telemetry collection and Kubernetes API live-pod synchronization in collector.py*
- **Technical Summary:** The collect_all_pods function queries Prometheus via PromQL to extract multi-pod compute metrics (CPU rate, memory working set, and network transmit/receive throughput). It interfaces with the in-cluster Kubernetes API service account (/var/run/secrets/kubernetes.io/serviceaccount/) to filter out succeeded, failed, or terminating pods, ensuring that only actively running workloads are tracked. This module forms the foundational telemetry ingestion layer of the monitoring pipeline, instantiating structured PodSample objects for downstream behavioral analysis.

#### D.2 – Energy Metric Collection Using Kepler

- **Primary Source File:** `ai-anomaly-detection/pipeline/collector.py`
- **Original Entity/Block:** `MetricsCollector._detect_kepler and collect_all_pods (energy branch)`
- **Original Source Lines:** Lines 62–72, 130–141, 159–160
- **Extracted Clean Code File:** `Extracted_Code/D2_kepler_energy.py` (29 lines)
- **High-Resolution Figure Image:** `Code_Screenshots/Figure_D2_Kepler_Energy.png`
- **Figure Caption:** *Figure D.2: Kepler eBPF energy detection and software estimation fallback in collector.py*
- **Technical Summary:** This module dynamically detects whether Kepler (Kubernetes-based Efficient Power Level Exporter) is actively exporting kernel-level eBPF energy telemetry via Prometheus. When kepler_container_joules_total is available, real per-pod joule consumption rates are gathered. In virtualized or emulation environments (such as WSL2 or cloud VMs without bare-metal hardware Performance Monitoring Unit access), the system seamlessly transitions to a calibrated software fallback formula (E = CPU cores * 0.4 J). This ensures uninterrupted energy-aware behavioral profiling across diverse cloud infrastructure deployments.

#### D.3 – Prometheus Metric Extraction and Data Preprocessing

- **Primary Source File:** `experiments/export_metrics.py`
- **Original Entity/Block:** `export_pod_metrics`
- **Original Source Lines:** Lines 48–114
- **Extracted Clean Code File:** `Extracted_Code/D3_prometheus_preprocessing.py` (28 lines)
- **High-Resolution Figure Image:** `Code_Screenshots/Figure_D3_Prometheus_Preprocessing.png`
- **Figure Caption:** *Figure D.3: Multi-metric Prometheus query execution and DataFrame alignment in export_metrics.py*
- **Technical Summary:** The export_pod_metrics function queries Prometheus instant vectors to extract time-series resource utilization data for all pods in the target namespace. It transforms disjoint query results into pandas DataFrames, performing an outer join across CPU, memory working set, network RX/TX, and energy metrics on the pod_name key. The preprocessor handles timestamping, namespace labeling, and fallback value imputation for missing fields. This module provides verified, clean datasets required for both offline model evaluation and online training.

#### D.4 – Multi-Metric Feature Engineering

- **Primary Source File:** `ai-anomaly-detection/pipeline/feature_engineer.py`
- **Original Entity/Block:** `FeatureEngineer.extract_features`
- **Original Source Lines:** Lines 43–112, 169–186
- **Extracted Clean Code File:** `Extracted_Code/D4_feature_engineering.py` (33 lines)
- **High-Resolution Figure Image:** `Code_Screenshots/Figure_D4_Feature_Engineering.png`
- **Figure Caption:** *Figure D.4: Sliding-window temporal feature extraction and energy-to-CPU ratio calculation in feature_engineer.py*
- **Technical Summary:** This method maintains a per-pod temporal sliding window (W = 6 samples, spanning 30 seconds with 5-sample overlap) and calculates 26 statistical, slope, and cross-resource features. First-degree polynomial fits (np.polyfit) capture usage velocity and slope trends for CPU and energy. The module computes cross-resource couplings, most notably the novel energy-to-CPU ratio (E/CPU = avg_energy / (avg_cpu + EPSILON)) and energy density, which provide strong discriminative power to differentiate sustained cryptojacking and resource abuse from transient legitimate microservice spikes.

#### D.5 – Isolation Forest Model Training

- **Primary Source File:** `ai-anomaly-detection/pipeline/model_manager.py`
- **Original Entity/Block:** `ModelManager.train_both_models`
- **Original Source Lines:** Lines 123–160, 169–174
- **Extracted Clean Code File:** `Extracted_Code/D5_isolation_forest_training.py` (38 lines)
- **High-Resolution Figure Image:** `Code_Screenshots/Figure_D5_Isolation_Forest_Training.png`
- **Figure Caption:** *Figure D.5: Dual unsupervised Isolation Forest training and artifact serialization in model_manager.py*
- **Technical Summary:** The train_both_models function implements unsupervised learning on baseline normal operational windows collected across all monitored Kubernetes pods. It standardizes multi-dimensional feature distributions via StandardScaler and trains two scikit-learn IsolationForest models in parallel: a 16-dimensional Energy-Aware model and a 6-dimensional Basic baseline model lacking energy features. After training completes, the estimators and scalers are persisted to disk via joblib, and the system transitions from STATE_TRAINING to STATE_DETECTING.

#### D.6 – Anomaly Detection and Anomaly Score Generation

- **Primary Source File:** `ai-anomaly-detection/pipeline/model_manager.py`
- **Original Entity/Block:** `ModelManager.predict`
- **Original Source Lines:** Lines 196–242
- **Extracted Clean Code File:** `Extracted_Code/D6_anomaly_detection.py` (37 lines)
- **High-Resolution Figure Image:** `Code_Screenshots/Figure_D6_Anomaly_Detection.png`
- **Figure Caption:** *Figure D.6: Real-time anomaly scoring and consecutive window hysteresis validation in model_manager.py*
- **Technical Summary:** The predict method performs real-time inference on incoming pod feature vectors by applying saved scalers and evaluating decision_function and predict across both Isolation Forest models. An anomaly score lower than zero indicates an outlier isolated in short partition tree depths. To prevent transient CPU bursts from causing false alarms, the decision engine implements temporal hysteresis requiring at least three consecutive anomalous windows before confirming an active attack. Ground truth labels and inference results are saved to evaluation.csv.

#### D.7 – Baseline Detection and Comparative Analysis

- **Primary Source File:** `ai-anomaly-detection/pipeline/evaluator.py`
- **Original Entity/Block:** `Evaluator._calc and calculate_metrics`
- **Original Source Lines:** Lines 21–68
- **Extracted Clean Code File:** `Extracted_Code/D7_baseline_comparison.py` (37 lines)
- **High-Resolution Figure Image:** `Code_Screenshots/Figure_D7_Baseline_Comparison.png`
- **Figure Caption:** *Figure D.7: Empirical comparative evaluation between Energy-Aware and Basic IF models in evaluator.py*
- **Technical Summary:** This module computes IEEE-standard classification performance metrics—including Precision, Recall, F1-Score, Accuracy, False Positive Rate (FPR), and Detection Latency—comparing the proposed Multi-Metric Energy-Aware model against the non-energy Basic Isolation Forest baseline. In initial development, static CPU and energy threshold baselines (config.MIN_ATTACK_CPU, MIN_ATTACK_ENERGY) were evaluated; however, as documented in model_manager.py, static thresholds caused high false alarm rates on dynamic microservices and were replaced by the dual-model machine learning comparison shown here.

#### D.8 – Controlled Attack and Workload Simulation

- **Primary Source File:** `experiments/run_experiment.py`
- **Original Entity/Block:** `run_experiment and _wait_for_attack_outcome`
- **Original Source Lines:** Lines 35–64, 99–129
- **Extracted Clean Code File:** `Extracted_Code/D8_attack_simulation.py` (31 lines)
- **High-Resolution Figure Image:** `Code_Screenshots/Figure_D8_Attack_Simulation.png`
- **Figure Caption:** *Figure D.8: Automated attack workload injection and outcome monitoring in run_experiment.py*
- **Technical Summary:** This module orchestrates reproducible experimental evaluation by deploying controlled synthetic attack workloads (such as attack-cryptojacking using polinux/stress executing matrix multiplication routines up to 1500m CPU limits) into the Kubernetes cluster. The runner monitors detector REST APIs until anomaly confirmation and automated mitigation execution are observed, or until a safety timeout elapses. It automatically exports telemetry snapshots and synchronizes pod logs to the results directory for post-experiment analysis.

#### D.9 – Kubernetes-Based Anomaly Mitigation

- **Primary Source File:** `ai-anomaly-detection/pipeline/mitigator.py`
- **Original Entity/Block:** `Mitigator.mitigate and _throttle_deployment`
- **Original Source Lines:** Lines 126–182, 233–289
- **Extracted Clean Code File:** `Extracted_Code/D9_kubernetes_mitigation.py` (35 lines)
- **High-Resolution Figure Image:** `Code_Screenshots/Figure_D9_Kubernetes_Mitigation.png`
- **Figure Caption:** *Figure D.9: Progressive Deployment throttling and pod deletion mitigation in mitigator.py*
- **Technical Summary:** The mitigation module executes a progressive, production-grade two-stage remediation policy. Upon first attack confirmation (Stage 1), the controller resolves the owner chain (Pod -> ReplicaSet -> Deployment) and applies a strategic-merge patch to the Deployment template, restricting CPU to 100m and memory to 128Mi while waiting for rollout completion. If malicious behavior persists beyond THROTTLE_DURATION_WINDOWS (Stage 2), the specific attack pod is deleted via kubectl delete pod, forcing the ReplicaSet to spawn replacements under the throttled template.

#### D.10 – Performance Evaluation and Research Logging

- **Primary Source File:** `ai-anomaly-detection/pipeline/research_logger.py`
- **Original Entity/Block:** `ResearchLogger.log_detection_cycle and _update_latency_tracking`
- **Original Source Lines:** Lines 101–160
- **Extracted Clean Code File:** `Extracted_Code/D10_evaluation.py` (33 lines)
- **High-Resolution Figure Image:** `Code_Screenshots/Figure_D10_Evaluation_Logging.png`
- **Figure Caption:** *Figure D.10: Per-cycle research telemetry logging and sub-second latency tracking in research_logger.py*
- **Technical Summary:** The research logging module maintains an append-only CSV audit record of every detection cycle to guarantee IEEE-standard experimental reproducibility. It computes sub-second detection latency (time elapsed between attack workload emergence and first anomaly classification) and mitigation latency (time elapsed between anomaly confirmation and successful mitigation) in milliseconds. Each record captures the full 19-column telemetry vector, including per-pod CPU/memory utilization, energy consumption, energy-to-CPU ratio, decision scores, confidence bounds, and mitigation actions.

