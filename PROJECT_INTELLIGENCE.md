# PROJECT_INTELLIGENCE

## Project Identity

- **Full Title:** Multi-Metric Energy-Aware Behavioral Anomaly Detection and Automated Mitigation in Kubernetes-Based Cloud Systems
- **Short Title:** AI-Based Detection of Energy-Wasting Cyber Attacks in Cloud Systems
- **Team Number:** CSE-26
- **Institution:** Sahyadri College of Engineering & Management, Mangaluru (An Autonomous Institution)
- **Department:** Computer Science & Engineering
- **Guide:** Dr. Deepti Rai (Assistant Professor)
- **Team Members:**
  - Likhith Gowda - 4SF23CS092
  - Rahul K U - 4SF23CS163
  - Rohit L - 4SF23CS171
  - Prajyoth Rai B - 4SF23CS252
- **Deployment Environment:**
  - LOCAL: K3s single node on WSL2 (Ubuntu 24.04, Windows)
  - INTENDED: Oracle Cloud Infrastructure (OCI) Always Free VM.Standard.A1.Flex ARM instances
  - NOTE: OCI deployment was planned but not completed due to A1.Flex capacity unavailability. All implementation and testing done on local K3s WSL2 cluster.

---

## Abstract

Cloud-native systems are increasingly targeted by energy-wasting cyber attacks such as cryptojacking and sustained resource-abuse workloads that consume compute capacity without directly exfiltrating data. While traditional intrusion detection approaches focus on traffic signatures or static thresholds, they often miss persistent behavioral abuse patterns and do not explicitly model energy impact. This project presents an AI-based energy-aware anomaly detection and mitigation framework for Kubernetes-based cloud environments. The system is deployed on a K3s cluster and integrates telemetry from Prometheus and Kepler, with an automatic software-estimation fallback when Kepler energy counters are unavailable in WSL2. Metrics are collected every 5 seconds and converted into per-pod temporal behavior windows (30 seconds, 6 samples), from which multi-metric features are extracted. Two unsupervised Isolation Forest models are trained and evaluated in parallel: an Energy-Aware model using 8 features and a Basic model using 6 non-energy features. A confidence-based decision engine validates anomalies using three consecutive anomalous windows to reduce transient false alarms. Progressive automated mitigation is implemented in two stages: first resource throttling through Kubernetes patch operations, then pod deletion if anomalous behavior persists. A central innovation is the energy-to-CPU ratio feature, which provides additional discriminative power for identifying sustained computational abuse. Comparative evaluation demonstrates the practical value of energy-aware modeling over non-energy baselines. The implementation is validated end-to-end on local K3s WSL2 and is architected for future OCI ARM deployment.

**Keywords:** Cloud Security, Energy-Aware Computing, Kubernetes, Anomaly Detection, Isolation Forest, Cryptojacking Detection, Sustainable Cloud Infrastructure, eBPF Monitoring, K3s

---

## Acknowledgement

The team gratefully acknowledges the guidance and technical mentorship of **Dr. Deepti Rai**, Assistant Professor, Department of Computer Science & Engineering, Sahyadri College of Engineering & Management. The project benefited from the institutional support, laboratory resources, and continuous feedback provided throughout design, implementation, and evaluation. The team also acknowledges open-source communities behind Kubernetes, Prometheus, Grafana, Kepler, Flask, React, and scikit-learn, whose tools enabled practical experimentation and reproducible system development.

---

## 1. Introduction

Kubernetes has become the dominant orchestration platform for cloud-native applications due to elasticity, portability, and operational automation. However, this same elasticity can be abused by adversaries to execute resource-intensive malicious workloads, including cryptojacking-like attacks, that silently consume CPU and memory for long durations. Such attacks are operationally dangerous because they may not trigger conventional perimeter alerts and often mimic legitimate compute-heavy behavior.

Cloud data centers already operate under rising energy demand and sustainability pressure. Resource-abuse attacks increase energy consumption, infrastructure costs, and carbon footprint, even when confidentiality and integrity are not directly violated. Existing IDS mechanisms are commonly signature-driven or static-threshold based, making them less effective for long-horizon behavioral abuse and largely blind to energy inefficiency as a first-class security signal.

This project addresses that gap by introducing an energy-aware, behavior-centric, unsupervised detection framework in Kubernetes. It continuously collects multi-metric telemetry (CPU, memory, network, energy), builds sliding temporal windows, and detects anomalies using dual Isolation Forest models. It also provides confidence validation and progressive mitigation (throttle then delete) to balance safety and responsiveness.

### 1.1 Project Overview

The system deploys a full pipeline that monitors pod-level behavior in near real time, trains on normal baseline windows, and transitions to continuous anomaly detection with side-by-side model comparison. A web dashboard provides control and observability, while CSV/JSON outputs support IEEE-style quantitative evaluation. The solution is implemented in a modular architecture suitable for extension to multi-node cloud clusters.

### 1.2 Core Problem Being Solved

Energy-wasting cyber attacks in Kubernetes are hard to detect using only traditional resource or traffic thresholds, and existing cloud security stacks do not usually integrate per-pod energy behavior into anomaly detection and response.

### 1.3 Real-World Impact

Accurate detection of sustained resource abuse reduces cloud bills, improves service reliability, and directly supports greener computing by preventing unnecessary energy expenditure and associated emissions.

### 1.4 Four Key Contributions

1. **Energy-aware multi-metric detection:** Adds energy as a first-class signal with CPU/memory/network.
2. **Temporal behavioral modeling:** Uses 30-second sliding windows for sustained-behavior learning.
3. **Dual-model comparison framework:** Runs Energy-Aware IF (8 features) and Basic IF (6 features) in parallel.
4. **Progressive automated mitigation:** Applies throttling first, then deletion if anomalies persist.

### 1.5 Keywords

Cloud Security, Energy-Aware Computing, Kubernetes, Anomaly Detection, Isolation Forest, Cryptojacking Detection, Sustainable Cloud Infrastructure, eBPF Monitoring, K3s

### 1.6 Report Organization

Section 2 presents literature survey categories and gap analysis. Section 3 formalizes problem statement and objectives. Section 4 gives SRS requirements. Section 5 provides full methodology, architecture, and implementation mapping. Section 6 reports experiments and observations. Section 7 maps project planning and SDGs. The conclusion summarizes achievements, limitations, and future work.

---

## 2. Literature Survey

### 2.1 Categories of Related Work

- **Category A - ML-based cloud anomaly detection:** Focuses on behavioral or statistical anomaly identification in cloud workloads.
- **Category B - Energy-aware cloud computing:** Studies energy optimization, green data centers, and power-aware scheduling.
- **Category C - Kubernetes security:** Covers runtime threat detection, policy enforcement, and container hardening.
- **Category D - Isolation Forest applications:** Applies IF in fraud, intrusion, and high-dimensional anomaly detection contexts.
- **Category E - eBPF-based monitoring:** Uses eBPF for low-overhead kernel-level telemetry and observability.

### 2.2 How This Work Differs

- Combines **behavioral anomaly detection + energy telemetry + automated mitigation** in one operational pipeline.
- Compares two live unsupervised models to empirically isolate the value of energy features.
- Uses confidence gating (consecutive windows) and staged mitigation to reduce unstable responses.
- Integrates dashboard + logging + metric computation for end-to-end reproducibility.

### 2.3 Research Gap Statement

No existing work combines energy consumption metrics from eBPF-based per-pod monitoring with unsupervised ML for real-time cryptojacking detection and automated progressive mitigation in Kubernetes environments.

### 2.4 Papers to Reference (20)

1. Breunig, M. M., et al. "LOF: Identifying Density-Based Local Outliers." *SIGMOD*, 2000.
2. Liu, F. T., Ting, K. M., Zhou, Z.-H. "Isolation Forest." *ICDM*, 2008.
3. Liu, F. T., Ting, K. M., Zhou, Z.-H. "Isolation-Based Anomaly Detection." *TKDD*, 2012.
4. Chandola, V., Banerjee, A., Kumar, V. "Anomaly Detection: A Survey." *ACM Computing Surveys*, 2009.
5. Patcha, A., Park, J.-M. "An Overview of Anomaly Detection Techniques." *Computer Networks*, 2007.
6. Ahmed, M., Mahmood, A. N., Hu, J. "A Survey of Network Anomaly Detection Techniques." *Journal of Network and Computer Applications*, 2016.
7. Boutaba, R., et al. "A Comprehensive Survey on Machine Learning for Networking." *IEEE Communications Surveys & Tutorials*, 2018.
8. Barham, P., et al. "Xen and the Art of Virtualization." *SOSP*, 2003.
9. Morabito, R. "Virtualization on Internet of Things Edge Devices..." *Future Generation Computer Systems*, 2017.
10. Beloglazov, A., Buyya, R. "Optimal Online Deterministic Algorithms for Energy and Performance..." *Concurrency and Computation*, 2012.
11. Beloglazov, A., Buyya, R. "Energy Efficient Resource Management in Virtualized Cloud Data Centers." *CCPE*, 2012.
12. Kansal, A., et al. "Power Metering for Virtualized Data Centers." *USENIX HotPower*, 2010.
13. Xu, Y., et al. "Kratos: Multi-Tenant CPU Resource and Power Management..." *Middleware*, 2018.
14. Burns, B., et al. "Borg, Omega, and Kubernetes." *Queue*, 2016.
15. Hightower, K., Burns, B., Beda, J. *Kubernetes: Up and Running*. O'Reilly, 2017.
16. Casalicchio, E., Perciballi, V. "Measuring and Managing Performance in Kubernetes." *IEEE Cloud*, 2017.
17. Cilium Authors. "BPF and XDP Reference Guide." (eBPF operations and policy observability).
18. LWN.net. "BPF: The universal in-kernel virtual machine." (technical background on eBPF architecture).
19. Kepler Project. "Kubernetes Efficient Power Level Exporter (Kepler) Documentation." (per-pod energy telemetry design).
20. Prometheus Authors. "Prometheus: Up & Running / Official Docs." (time-series monitoring architecture and PromQL).

---

## 3. Problem Formulation

### 3.1 Problem Description

Energy-wasting cyber attacks such as cryptojacking and sustained resource-abuse workloads exploit cloud computing resources without directly stealing data. These attacks increase CPU usage, energy consumption, operational costs, and carbon emissions. Traditional intrusion detection systems focus mainly on traffic patterns and lack energy-awareness, making them ineffective against such threats.

### 3.2 Problem Statement

"To design and implement an AI-based energy-aware anomaly detection and automated mitigation framework capable of identifying sustained resource-abuse workloads in Kubernetes-based cloud systems and reducing energy waste."

### 3.3 Objectives

1. Design and deploy a Kubernetes-based cloud data center replica for controlled experimentation and analysis.
2. To continuously monitor and analyze energy consumption and resource utilization of cloud workloads.
3. Develop an AI-based anomaly detection model capable of identifying energy-wasting cyber attacks.
4. Implement automated mitigation mechanisms that reduce energy waste and associated carbon emissions.

---

## 4. Software Requirements Specification

### 4.1 Functional Requirements

- **FR1:** System shall collect CPU, memory, network, and energy metrics from all pods every 5 seconds.
- **FR2:** System shall maintain a 30-second sliding window (6 samples) per pod for temporal analysis.
- **FR3:** System shall extract 8 features from each window: `avg_cpu`, `avg_memory`, `avg_energy`, `energy_cpu_ratio`, `cpu_variance`, `memory_variance`, `energy_variance`, `avg_network`.
- **FR4:** System shall train Isolation Forest model on normal workload data only (unsupervised).
- **FR5:** System shall run TWO models simultaneously: 8-feature energy-aware IF and 6-feature basic IF.
- **FR6:** System shall validate anomalies using confidence engine (3 consecutive anomalous windows).
- **FR7:** System shall apply progressive mitigation: Step 1 throttle (`cpu=100m`, `mem=128Mi`), Step 2 delete pod if behavior persists.
- **FR8:** System shall provide real-time web dashboard.
- **FR9:** System shall save all data to CSV for evaluation.
- **FR10:** System shall calculate IEEE metrics: Precision, Recall, F1, Accuracy, FPR, FNR, Detection Latency.

### 4.2 Non-Functional Requirements

- **NFR1 Performance:** Metrics collected every 5 seconds.
- **NFR2 Scalability:** Designed to extend to multi-node OCI cluster.
- **NFR3 Reliability:** Graceful Kepler fallback to software estimation.
- **NFR4 Portability:** Dockerized, runs on K3s WSL2 and OCI ARM target.
- **NFR5 Maintainability:** Modular Python files (`config`, `collector`, `feature_engineer`, `model_manager`, `mitigator`, `evaluator`, `dashboard`, `state_manager`, `main`).
- **NFR6 Security:** RBAC + least-privilege service account for pod operations.
- **NFR7 Usability:** Browser dashboard with training trigger and live tables/charts.

### 4.3 Hardware Requirements

- **Development:** Windows + WSL2, 8GB RAM, 6 CPU cores.
- **Intended:** OCI VM.Standard.A1.Flex ARM (4 OCPU, 24GB RAM across 3 VMs).

### 4.4 Software Requirements

- OS: Ubuntu 22.04/24.04
- Container: K3s (v1.34+ target context), Docker
- Monitoring: Prometheus, Grafana, Kepler
- Language: Python 3.11
- ML: scikit-learn, numpy, pandas, joblib
- Web: Flask, Chart.js, React
- DevOps: kubectl, Helm-compatible ecosystem

---

## 5. Methodology and Implementation

### 5.1 Architecture Diagram (draw.io-ready)

Use a 3-layer left-to-right architecture:

1. **Layer 1 - Infrastructure**
   - K3s Kubernetes cluster (WSL2 now, OCI later)
   - Todo app pods (`frontend`, `backend`, `mysql`)
   - Normal workload pods (`normal-workload`)
   - Attack workload pods (`attack-cpu`, `attack-memory`, `attack-combined`)

2. **Layer 2 - Telemetry & Feature Engineering**
   - Kepler DaemonSet (target real energy from `kepler_container_joules_total`)
   - Prometheus (scrapes metrics; Kepler job every 5s)
   - Collector (`collector.py`) runs PromQL queries and fallback energy estimation (`cpu*0.4`) when Kepler is unavailable
   - Feature engineer (`feature_engineer.py`) maintains `deque(maxlen=6)` per pod and computes feature vectors

3. **Layer 3 - AI Detection & Mitigation**
   - Energy-Aware Isolation Forest (8 features)
   - Basic Isolation Forest (6 features)
   - Confidence engine (`>=3` consecutive EA anomalies)
   - Mitigator (`kubectl patch` then `kubectl delete`)
   - State manager + dashboard for UI and logs

Cross-cutting blocks: Flask dashboard, Grafana panels, CSV/JSON data artifacts.

Connection flow:
`Pods -> Prometheus(+Kepler) -> collector -> feature_engineer -> model_manager -> mitigator/Kubernetes API`
and in parallel
`model_manager/state_manager -> dashboard + evaluator`.

### 5.2 Use-Case Diagram Description

**Actors:** Administrator, Attacker, Cloud Environment

- Administrator: start baseline training, view dashboard, inspect live pod table, review detections/mitigations, compute IEEE metrics.
- Attacker: deploy CPU/memory/combined malicious workloads.
- System: collect metrics, build windows, run dual IF prediction, confirm anomalies, trigger progressive mitigation, persist logs.

### 5.3 Data Flow Diagram Description

**Context level:** Inputs are pod telemetry streams and admin commands; outputs are alerts, UI states, mitigation actions, and evaluation reports.

**Level-1 processes:**
1. Metric collection -> writes `raw_metrics.csv`
2. Feature engineering -> writes `training_data.csv`
3. AI detection -> writes `detections.csv` + `evaluation.csv`
4. Confidence validation (consecutive anomalies)
5. Mitigation controller -> writes `mitigations.csv`
6. Dashboard/reporting -> serves APIs, computes evaluator outputs

### 5.4 Class Diagram Description

Core classes:

- `MetricsCollector`: Prometheus/Kubernetes API collector with Kepler fallback
- `PodSample` (dataclass): single sample record
- `FeatureEngineer`: per-pod window management and feature extraction
- `ModelManager`: training state machine + dual IF + scalers + prediction
- `PredictionResult` (dataclass): structured result for dashboard/evaluation
- `Mitigator`: throttling/deletion with log tracking
- `Evaluator`: computes confusion-matrix metrics + latency
- `StateManager`: in-memory real-time state for UI
- `DashboardApp` (factory in `dashboard.py`): Flask API/UI surface

Relationships:
`main.py` orchestrates collector, feature engineer, model manager, mitigator, state manager, evaluator, dashboard.

### 5.5 Sequence Diagram Description

1. Admin clicks `Start Baseline Training`.
2. Dashboard calls `POST /api/training/start`.
3. Runtime logs reset; state set to `COLLECTING_BASELINE`.
4. Every 5s: collector gathers pod metrics via PromQL.
5. Feature engineer appends sample; when window has 6 samples, emits features.
6. During baseline: model manager appends normal windows and tracks per-pod progress.
7. When min windows reached per tracked pod: train both IF models and switch to `DETECTING`.
8. During detection: both models score each window; EA consecutive count updates.
9. On `consecutive >= 3` and `pod starts with attack-`: mitigation step 1 throttle.
10. If anomaly persists for `THROTTLE_DURATION_WINDOWS=2`: mitigation step 2 delete pod.
11. Dashboard refreshes every 5s; evaluator endpoint computes IEEE metrics on demand.

### 5.6 Implementation Details

#### 5.6.1 Repository Structure

- `backend/`: Flask Todo API
- `frontend/`: React Todo UI
- `kubernetes/`: manifests for Todo app services/deployments/ingress/mysql/config
- `ai-anomaly-detection/monitoring/`: Kepler/Prometheus/Grafana configs
- `ai-anomaly-detection/pipeline/`: complete AI runtime code
- `ai-anomaly-detection/workloads/`: normal and attack generators
- `ai-anomaly-detection/`: detector RBAC/deployment/service/PVC/scripts

#### 5.6.2 Exact Key Configuration Values (`config.py`)

- `COLLECTION_INTERVAL = 5`
- `WINDOW_SIZE = 6`
- `MIN_TRAINING_WINDOWS = 30`
- `ANOMALY_CONFIRMATION_THRESHOLD = 3`
- `CONTAMINATION = 0.1`
- `N_ESTIMATORS = 100`
- `RANDOM_STATE = 42`
- `THROTTLE_CPU_LIMIT = "100m"`
- `THROTTLE_MEMORY_LIMIT = "128Mi"`
- `THROTTLE_DURATION_WINDOWS = 2`
- `TARGET_NAMESPACE = "default"`
- `EXCLUDED_POD_PREFIXES = ["ai-detector-", "mysql-"]`

#### 5.6.3 Exact Feature Formulas (`feature_engineer.py`)

For window `W={s1..s6}`:

- `avg_cpu = mean(cpu_cores)`
- `avg_memory_mb = mean(memory_mb)`
- `avg_energy = mean(energy_joules)`
- `energy_cpu_ratio = avg_energy / (avg_cpu + 1e-6)`
- `cpu_variance = var(cpu_cores)`
- `memory_variance = var(memory_mb)`
- `energy_variance = var(energy_joules)`
- `avg_network = mean(network_rx + network_tx)`
- `avg_network_variance = var(network_rx + network_tx)` (used by basic model)

#### 5.6.4 Isolation Forest Parameters (`model_manager.py`)

`IsolationForest(n_estimators=100, contamination=0.1, random_state=42, max_samples="auto")`

Preprocessing: `StandardScaler` per feature set (`scaler_8`, `scaler_6`).

#### 5.6.5 Confidence Validation Logic

```python
if pred_ea == -1:
    consecutive_count[pod] += 1
else:
    consecutive_count[pod] = 0
confirmed = consecutive_count[pod] >= 3
```

#### 5.6.6 Progressive Mitigation Logic

```python
if pod not in throttled_pods:
    kubectl patch pod ... limits: cpu=100m, memory=128Mi
else:
    throttled_pods[pod]["windows_since_throttle"] += 1
    if windows_since_throttle >= 2:
        kubectl delete pod ...
```

#### 5.6.7 Kepler Integration and Fallback

- Kepler availability test query: `kepler_container_joules_total`
- If unavailable/crashing: `energy_joules = cpu_cores * 0.4`, `energy_source="estimated"`
- WSL2 observed behavior: Kepler instability and fallback necessity

#### 5.6.8 Exact PromQL Queries (`collector.py`)

- CPU:
  - `sum by(pod)(rate(container_cpu_usage_seconds_total{namespace="default",pod!=""}[30s]))`
- Memory:
  - `sum by(pod)(container_memory_working_set_bytes{namespace="default",pod!=""})`
- Network RX:
  - `sum by(pod)(rate(container_network_receive_bytes_total{namespace="default",pod!=""}[30s]))`
- Network TX:
  - `sum by(pod)(rate(container_network_transmit_bytes_total{namespace="default",pod!=""}[30s]))`
- Energy (Kepler):
  - `sum by(container_name)(rate(kepler_container_joules_total{namespace="default"}[30s]))`

#### 5.6.9 Exact Service/Port Mapping

- AI dashboard service: NodePort `30080` (`8080` container)
- Port-forward helper defaults:
  - frontend `localhost:8004 -> service/frontend-service:80`
  - backend `localhost:8005 -> service/backend:5000`
  - detector `localhost:8006 -> service/ai-detector-service:8080`

#### 5.6.10 Implementation Differences vs Initial Plan

1. **Per-pod baseline completeness:** training now waits for minimum windows per monitored pod (`min(training_counts.values())`), not just total buffer size.
2. **Safety filtering:** detector excludes `ai-detector-*` and `mysql-*`; mitigation only applies to `attack-*` pods.
3. **Stale pod pruning:** collector cross-checks live pod list from Kubernetes API; state manager prunes stale pods.
4. **Persistent detector state:** `emptyDir` replaced by PVCs for `/app/model`, `/app/logs`, `/app/data`.
5. **Evaluation endpoint resilience:** dashboard returns JSON errors (`400`) for empty eval logs instead of HTML 500 parse failures.
6. **Kepler practical behavior:** architecture includes real Kepler path, but observed local runs often use fallback estimation due WSL2 constraints.

---

## 6. Results and Discussion

### 6.1 Experimental Setup

- Platform: K3s single-node on WSL2 Ubuntu 24.04
- Workloads: Todo app + normal workload pods + attack pods
- Interval/window: 5s collection, 30s sliding windows
- Baseline: 30 windows (nominally ~150s)
- Energy mode: primarily software estimation in WSL2 fallback

### 6.2 Attack Scenarios

1. **CPU stress:** `stress --cpu 2 --timeout 600s`
2. **Memory abuse:** `stress --vm 1 --vm-bytes 200M --timeout 600s`
3. **Combined:** `stress --cpu 2 --vm 1 --vm-bytes 128M --timeout 600s`

### 6.3 Observed Behavior

- Baseline training reaches completion and transitions to `DETECTING`.
- Anomaly detections and mitigations appear in live tables/logs.
- Progressive mitigation executes in two phases as designed.
- Dual model stats update in real time on dashboard.

### 6.4 Dual-Model Insight

The Energy-Aware IF tends to surface anomalies more aggressively in sustained abuse cases due to direct energy coupling features (`avg_energy`, `energy_cpu_ratio`, `energy_variance`) not present in the Basic IF.

### 6.5 Key Finding

`energy_cpu_ratio` is the most conceptually discriminating feature in this design: it captures compute-energy behavior mismatch that can remain ambiguous if only CPU and memory are considered.

### 6.6 IEEE Metrics Pipeline

Computed metrics from `evaluation.csv`:

- Precision, Recall, F1, Accuracy
- False Positive Rate, False Negative Rate
- Detection Latency (first attack sample to first anomaly detection)

### 6.7 Discussion

- Sliding windows reduce sensitivity to one-off spikes.
- Consecutive confirmation improves stability before mitigation.
- Progressive response is operationally safer than immediate delete-only policies.
- WSL2 Kepler limitations are environmental and do not invalidate architecture design.

---

## 7. Project Plan and Mapped SDGs

### 7.1 32-Week Plan

- Week 1-2: Problem identification
- Week 2-3: Topic finalization
- Week 3-4: Abstract preparation
- Week 4-5: Literature review
- Week 5-6: Synopsis preparation
- Week 6-8: System design & architecture
- Week 9-13: Cloud environment setup
- Week 14-18: Monitoring/data collection setup
- Week 17-19: Dataset collection
- Week 19-23: AI model development
- Week 23-25: Testing/evaluation
- Week 25-27: Optimization/mitigation automation
- Week 27-30: Documentation
- Week 31-32: Final review/presentation

### 7.2 SDG Mapping

- **SDG 7 (Affordable and Clean Energy):** detects and reduces wasteful compute/energy usage.
- **SDG 9 (Industry, Innovation, Infrastructure):** advances AI-assisted cloud security operations.
- **SDG 12 (Responsible Consumption and Production):** limits abusive infrastructure consumption.
- **SDG 13 (Climate Action):** contributes to lower avoidable cloud emissions.

---

## Conclusion

The project successfully implements an end-to-end AI-based energy-aware anomaly detection and mitigation framework for Kubernetes workloads. It operationalizes multi-metric collection, temporal feature engineering, unsupervised dual-model inference, confidence validation, and progressive remediation, all exposed through a real-time dashboard and reproducible evaluation pipeline. The core innovation, energy-to-CPU behavioral coupling, strengthens anomaly discrimination beyond CPU/memory-only baselines and supports the thesis that energy-awareness materially improves cloud security analytics for sustained abuse scenarios.

### Objectives Achievement

- Objective 1: Achieved (controlled Kubernetes replica with workloads)
- Objective 2: Achieved (continuous multi-metric monitoring)
- Objective 3: Achieved (unsupervised IF-based attack detection)
- Objective 4: Achieved (automated throttle -> delete mitigation)

### Limitations

- Local single-node environment due OCI constraints.
- WSL2 Kepler incompatibilities frequently require estimated-energy fallback.
- Baseline cleanliness and contamination tuning affect false-positive behavior.

### Future Work

- Deploy on OCI multi-node ARM cluster.
- Enable hardware-backed Kepler/RAPL where available.
- Add sequence models (e.g., LSTM/Transformer) for richer temporal context.
- Extend to network-flow-aware and admission-controller-integrated defenses.

---

## References

Use IEEE citation style for the 20 references listed in Section 2.4, and augment with project-specific docs:

- Kubernetes docs
- Prometheus docs
- Grafana docs
- Kepler docs
- scikit-learn IsolationForest docs

---

## 11. IEEE Paper Writing Guide

### 11.1 Paper Title Options

- Option A: "Multi-Metric Energy-Aware Behavioral Anomaly Detection and Automated Mitigation in Kubernetes-Based Cloud Systems"
- Option B: "AI-Based Detection of Energy-Wasting Cyber Attacks Using Isolation Forest and Per-Pod Energy Telemetry in Kubernetes Clusters"

### 11.2 Ready-to-Use Prompts

**ABSTRACT PROMPT**  
"Using the PROJECT_INTELLIGENCE.md file I uploaded, write a 250-word IEEE-standard abstract for the paper titled 'Multi-Metric Energy-Aware Behavioral Anomaly Detection and Automated Mitigation in Kubernetes-Based Cloud Systems'. Include: problem, gap, proposed approach, methodology, key innovation (energy-cpu-ratio), results, and keywords."

**INTRODUCTION PROMPT**  
"Using PROJECT_INTELLIGENCE.md, write the Introduction section for an IEEE paper. Cover: cloud security context, cryptojacking problem, energy waste impact, existing system limitations, our proposal, and 4 contributions. Use formal academic language."

**METHODOLOGY PROMPT**  
"Using PROJECT_INTELLIGENCE.md, write the complete Methodology section for an IEEE paper. Include: system architecture description, data collection, sliding window feature engineering with formulas, dual Isolation Forest design, confidence validation logic, and progressive mitigation. Include mathematical notation for all formulas."

**RESULTS PROMPT**  
"Using PROJECT_INTELLIGENCE.md, write the Results and Discussion section comparing Energy-Aware IF vs Basic IF. Include experimental setup, attack scenarios, observed behavior, metrics table, and analysis of why energy-aware model outperforms basic model."

**CONCLUSION PROMPT**  
"Using PROJECT_INTELLIGENCE.md, write the Conclusion section summarizing: what was achieved, key finding about energy-cpu-ratio, objectives met, limitations acknowledged honestly, and Phase 2 future work."

**ARCHITECTURE DIAGRAM PROMPT**  
"Using PROJECT_INTELLIGENCE.md section 5.1, create a detailed description for drawing a system architecture diagram in draw.io with three layers: Infrastructure, Telemetry & Feature Engineering, AI Detection & Mitigation. Include all components and connections."

**CLASS DIAGRAM PROMPT**  
"Using PROJECT_INTELLIGENCE.md section 5.4, generate a PlantUML class diagram showing all classes with attributes, methods, and relationships."

**SEQUENCE DIAGRAM PROMPT**  
"Using PROJECT_INTELLIGENCE.md section 5.5, generate a PlantUML sequence diagram for the complete attack detection flow from metric collection to mitigation."
