/**
 * api.js - Resilient client for AI-Anomaly-Detection backend endpoints.
 */

export class ApiService {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
    this.isOnline = true;
    this.lastSuccessfulFetch = null;
  }

  async _request(endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Accept': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      this.isOnline = true;
      this.lastSuccessfulFetch = new Date();
      return await response.json();
    } catch (error) {
      this.isOnline = false;
      console.warn(`[API] Endpoint failure (${endpoint}):`, error);
      throw error;
    }
  }

  async getStatus() {
    return this._request('/api/status');
  }

  async getPods() {
    return this._request('/api/pods');
  }

  async getDetections() {
    return this._request('/api/detections');
  }

  async getMitigations() {
    return this._request('/api/mitigations');
  }

  async getComparison() {
    return this._request('/api/comparison');
  }

  async getMetricsHistory() {
    return this._request('/api/metrics/history');
  }

  async startBaselineTraining() {
    return this._request('/api/training/start', {
      method: 'POST',
    });
  }

  async clearIncidents() {
    return this._request('/api/incidents/clear', {
      method: 'POST',
    });
  }

  async getEvaluation() {
    return this._request('/api/evaluation');
  }

  async getClusterInfo() {
    try {
      return await this._request('/api/cluster');
    } catch (err) {
      // Graceful fallback if /api/cluster is not available
      return null;
    }
  }
}

export const api = new ApiService();
