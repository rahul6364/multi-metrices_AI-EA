/**
 * state.js - Central reactive store for dashboard state.
 */

class Store {
  constructor() {
    this.state = {
      activeView: 'overview',
      selectedPod: 'all',
      searchQuery: '',
      statusFilter: 'all',
      incidentFilter: 'all',
      activeAnomalyPod: null,
      isTrainingStarting: false,
      isCalculatingMetrics: false,
      lastEvaluationData: null,
      
      // Live Data from /api/status
      systemData: {
        current_state: 'IDLE',
        training_progress: { current: 0, total: 30 },
        kepler_active: false,
        model_trained: false,
        pods: {},
        detection_history: [],
        mitigation_history: [],
        metrics_timeline: {},
        attack_types_detected: {},
        comparison_stats: {
          ea_detections: 0,
          basic_detections: 0,
          ea_false_positives: 0,
          basic_false_positives: 0,
          ea_confirmed: 0,
          basic_confirmed: 0,
        },
        uptime: 0,
      },
      clusterData: null,
      isOnline: true,
      lastUpdated: null,
    };

    this.listeners = new Set();
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notify() {
    for (const listener of this.listeners) {
      try {
        listener(this.state);
      } catch (err) {
        console.error('[Store] Error in listener:', err);
      }
    }
  }

  updateSystemData(data) {
    this.state.systemData = {
      ...this.state.systemData,
      ...data,
    };
    this.state.isOnline = true;
    this.state.lastUpdated = new Date();

    // Auto-detect active anomaly pod from recent detections
    const recentAnomalies = (data.detection_history || []).filter(
      d => d.prediction_ea === 'ANOMALY' || d.consecutive >= 1
    );
    if (recentAnomalies.length > 0) {
      this.state.activeAnomalyPod = recentAnomalies[0].pod_name;
    } else {
      this.state.activeAnomalyPod = null;
    }

    this.notify();
  }

  setOnline(status) {
    if (this.state.isOnline !== status) {
      this.state.isOnline = status;
      this.notify();
    }
  }

  setActiveView(view) {
    if (this.state.activeView !== view) {
      this.state.activeView = view;
      this.notify();
    }
  }

  setSelectedPod(podName) {
    this.state.selectedPod = podName;
    this.notify();
  }

  setSearchQuery(query) {
    this.state.searchQuery = query.toLowerCase();
    this.notify();
  }

  setStatusFilter(filter) {
    this.state.statusFilter = filter;
    this.notify();
  }

  setEvaluationData(data) {
    this.state.lastEvaluationData = data;
    this.state.isCalculatingMetrics = false;
    this.notify();
  }

  setCalculatingMetrics(val) {
    this.state.isCalculatingMetrics = val;
    this.notify();
  }
}

export const store = new Store();
