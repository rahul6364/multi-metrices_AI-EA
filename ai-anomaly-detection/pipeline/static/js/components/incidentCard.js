/**
 * incidentCard.js - Security Command Center primary incident display.
 */

import { renderStatusBadge } from './statusBadge.js';

export function renderIncidentCard(activeAnomaly, latestMitigation) {
  if (!activeAnomaly) {
    return `
      <div class="incident-card incident-normal">
        <div class="incident-top-bar">
          <div class="incident-badge-group">
            <span class="status-dot online pulsing"></span>
            <div class="incident-title">SYSTEM NORMAL & PROTECTED</div>
          </div>
          ${renderStatusBadge('NORMAL', 'CLUSTER SECURE')}
        </div>
        <p style="color: var(--text-secondary); font-size: 13.5px; margin: 0;">
          No active security incidents or energy-wasting workloads detected in the Kubernetes cluster.
          AI Isolation Forest models are continuously evaluating pod telemetry.
        </p>
      </div>
    `;
  }

  // Active anomaly detected
  const isConfirmed = activeAnomaly.consecutive >= 3;
  const severity = isConfirmed ? 'CRITICAL' : 'HIGH';
  const score = (activeAnomaly.score_ea !== undefined ? activeAnomaly.score_ea : -0.05).toFixed(4);
  const action = latestMitigation ? latestMitigation.action : (isConfirmed ? 'THROTTLED' : 'OBSERVING');

  return `
    <div class="incident-card incident-active">
      <div class="incident-top-bar">
        <div class="incident-badge-group">
          <span class="status-dot offline pulsing"></span>
          <div class="incident-title">
            ACTIVE SECURITY INCIDENT
          </div>
        </div>
        <div style="display: flex; gap: 8px;">
          ${renderStatusBadge(severity, `SEVERITY: ${severity}`)}
          ${renderStatusBadge(activeAnomaly.prediction_ea || 'ANOMALY')}
          ${renderStatusBadge(action, `ACTION: ${action}`)}
        </div>
      </div>

      <div style="font-size: 13.5px; color: var(--text-primary);">
        <strong style="color: var(--color-danger);">Affected Workload:</strong> 
        <span class="cell-mono" style="color: #fff; background: rgba(0,0,0,0.3); padding: 3px 8px; border-radius: 4px; margin-left: 6px;">
          ${activeAnomaly.pod_name}
        </span>
      </div>

      <div class="incident-metrics-grid">
        <div class="incident-metric-item">
          <span class="incident-metric-label">AI Score</span>
          <span class="incident-metric-value" style="color: var(--color-danger);">${score}</span>
        </div>
        <div class="incident-metric-item">
          <span class="incident-metric-label">Consecutive</span>
          <span class="incident-metric-value">${activeAnomaly.consecutive || 1} windows</span>
        </div>
        <div class="incident-metric-item">
          <span class="incident-metric-label">CPU Usage</span>
          <span class="incident-metric-value">${(activeAnomaly.avg_cpu || 0).toFixed(4)} cores</span>
        </div>
        <div class="incident-metric-item">
          <span class="incident-metric-label">Memory</span>
          <span class="incident-metric-value">${(activeAnomaly.avg_memory_mb || 0).toFixed(1)} MB</span>
        </div>
        <div class="incident-metric-item">
          <span class="incident-metric-label">Energy</span>
          <span class="incident-metric-value" style="color: var(--color-energy);">${(activeAnomaly.avg_energy || 0).toFixed(4)} J</span>
        </div>
        <div class="incident-metric-item">
          <span class="incident-metric-label">Energy/CPU Ratio</span>
          <span class="incident-metric-value" style="color: var(--color-cyan);">${(activeAnomaly.energy_cpu_ratio || 0).toFixed(4)}</span>
        </div>
      </div>
    </div>
  `;
}
