/**
 * detectionView.js - AI Detection Page: Isolation Forest architecture, feature attribution & dual model comparison.
 */

import { renderFeatureAnalysis } from '../components/featureAnalysis.js';
import { renderStatusBadge } from '../components/statusBadge.js';
import { chartManager } from '../charts.js';

export function renderDetection(state) {
  const { systemData } = state;
  const comparison = systemData.comparison_stats || {};
  const detections = systemData.detection_history || [];

  // Pick the most recent anomaly or first detection for analysis
  const recentAnomaly = detections.find(d => d.prediction_ea === 'ANOMALY' || d.consecutive >= 1) || detections[0];

  return `
    <!-- Top Model Architecture Overview -->
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--color-cyan);">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            <span>ENERGY-AWARE ISOLATION FOREST ARCHITECTURE</span>
          </div>
          <div class="card-subtitle">
            Unsupervised machine learning model leveraging cross-resource behavioral vectors to detect cryptojacking and resource abuse.
          </div>
        </div>
        ${renderStatusBadge(systemData.model_trained ? 'MODEL ACTIVE' : 'AWAITING BASELINE')}
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-top: 10px;">
        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 14px;">
          <div style="font-weight: 700; color: var(--color-cyan); margin-bottom: 6px;">Multi-Metric Temporal Features (8-D Vector)</div>
          <p style="font-size: 12.5px; color: var(--text-secondary); line-height: 1.6;">
            1. Average CPU Utilization (cores)<br>
            2. Average Memory Working Set (MB)<br>
            3. Average Energy Consumption (Joules)<br>
            4. <strong>Energy-to-CPU Ratio</strong> (Primary discriminative feature)<br>
            5. CPU Variance (temporal instability)<br>
            6. Memory Variance (allocation volatility)<br>
            7. Energy Variance (power draw fluctuations)<br>
            8. Average Network Throughput (RX + TX)
          </p>
        </div>

        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 14px;">
          <div style="font-weight: 700; color: #fff; margin-bottom: 6px;">Confidence & Mitigation Gate</div>
          <p style="font-size: 12.5px; color: var(--text-secondary); line-height: 1.6;">
            • <strong>Sliding Window:</strong> 30 seconds (6 consecutive 5s telemetry intervals)<br>
            • <strong>Confirmation Threshold:</strong> 3 consecutive anomalous windows<br>
            • <strong>Transient Alarm Shield:</strong> Eliminates brief legitimate CPU bursts<br>
            • <strong>Decision Score:</strong> Isolation path length normalized via StandardScaler
          </p>
        </div>
      </div>
    </div>

    <!-- Dual Model Comparison (Section 6) -->
    <div class="detection-grid">
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Energy-Aware IF vs Basic IF - Live Comparison</div>
            <div class="card-subtitle">Real-time side-by-side detection performance across all monitored pods</div>
          </div>
        </div>

        <table class="model-comparison-table">
          <thead>
            <tr>
              <th>Evaluation Parameter</th>
              <th>Energy-Aware IF</th>
              <th>Basic IF Baseline</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Input Telemetry Features</td>
              <td>8 Features (with Energy)</td>
              <td>6 Features (no Energy)</td>
            </tr>
            <tr>
              <td>Cumulative Detections</td>
              <td>${comparison.ea_detections || 0}</td>
              <td>${comparison.basic_detections || 0}</td>
            </tr>
            <tr>
              <td>False Positive Detections</td>
              <td>${comparison.ea_false_positives || 0}</td>
              <td>${comparison.basic_false_positives || 0}</td>
            </tr>
            <tr>
              <td>Confirmed Attack Incidents</td>
              <td>${comparison.ea_confirmed || 0}</td>
              <td>${comparison.basic_confirmed || 0}</td>
            </tr>
          </tbody>
        </table>

        <div style="margin-top: 14px; font-size: 12px; color: var(--text-muted); line-height: 1.5; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 6px;">
          <strong>Scientific Methodology:</strong> The energy-aware model incorporates energy-related telemetry, including the energy-to-CPU relationship, as an additional behavioral signal to distinguish sustained resource abuse from legitimate transient compute spikes.
        </div>
      </div>

      <!-- "Why was this workload flagged?" (Section 5) -->
      <div>
        ${renderFeatureAnalysis(recentAnomaly)}
      </div>
    </div>

    <!-- Anomaly Score Timeline Chart -->
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Real-Time Anomaly Score Trajectory</div>
          <div class="card-subtitle">Lower values (negative scores below threshold) indicate anomalous deviation from learned baseline</div>
        </div>
        <span class="badge badge-danger">Threshold: -0.015</span>
      </div>
      <div class="chart-canvas-container" style="min-height: 240px;">
        <canvas id="chart-score-timeline"></canvas>
      </div>
    </div>
  `;
}

export function updateDetectionCharts(state) {
  const { systemData } = state;
  const detections = (systemData.detection_history || []).slice().reverse();
  if (detections.length === 0) return;

  const labels = detections.map(d => new Date(d.timestamp * 1000).toLocaleTimeString());
  const scores = detections.map(d => d.score_ea !== undefined ? d.score_ea : 0);

  chartManager.createTimeSeriesChart('chart-score-timeline', 'Isolation Forest Score', '#ef4444', '239, 68, 68', '');
  chartManager.updateTimeSeriesData('chart-score-timeline', labels, scores);
}
