/**
 * mitigationView.js - Progressive Mitigation Pipeline, Mitigation Log & Energy Impact Analysis.
 */

import { renderMetricCard } from '../components/metricCard.js';
import { renderStatusBadge } from '../components/statusBadge.js';

export function renderMitigation(state) {
  const { systemData } = state;
  const mitigations = systemData.mitigation_history || [];
  const detections = systemData.detection_history || [];
  const comparison = systemData.comparison_stats || {};

  const threatsDetected = comparison.ea_confirmed_attacks || 0;
  const threatsMitigated = mitigations.length;
  const successfulActions = mitigations.filter(m => m.status === 'SUCCESS').length;
  const activeIncidents = systemData.active_incident_count || 0;

  // Real energy savings analysis check (Section 10)
  // Check if we have both an attack mitigation event AND before/after telemetry
  let energyImpactContent = '';
  const completedMitigations = mitigations.filter(m => m.action === 'DELETED' || m.action === 'THROTTLED');

  if (completedMitigations.length > 0 && detections.length > 10) {
    // Find telemetry before mitigation and after mitigation
    const firstMitigationTime = completedMitigations[completedMitigations.length - 1].timestamp;
    const beforeSamples = detections.filter(d => d.timestamp < firstMitigationTime && d.true_label === 1);
    const afterSamples = detections.filter(d => d.timestamp > firstMitigationTime && (d.prediction_ea === 'NORMAL' || d.true_label === 0));

    if (beforeSamples.length > 0 && afterSamples.length > 0) {
      const avgBefore = beforeSamples.reduce((sum, d) => sum + (d.avg_energy || 0), 0) / beforeSamples.length;
      const avgAfter = afterSamples.reduce((sum, d) => sum + (d.avg_energy || 0), 0) / afterSamples.length;
      const diff = avgBefore - avgAfter;
      const pctSaved = avgBefore > 0 ? (diff / avgBefore) * 100 : 0;

      energyImpactContent = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-top: 14px;">
          <div style="background: rgba(255, 255, 255, 0.02); padding: 12px; border-radius: 8px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Energy Before Mitigation</div>
            <div style="font-size: 20px; font-weight: 800; color: #fff; font-family: var(--font-mono); margin-top: 4px;">
              ${avgBefore.toFixed(4)} J
            </div>
          </div>
          <div style="background: rgba(255, 255, 255, 0.02); padding: 12px; border-radius: 8px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Energy After Mitigation</div>
            <div style="font-size: 20px; font-weight: 800; color: var(--color-healthy); font-family: var(--font-mono); margin-top: 4px;">
              ${avgAfter.toFixed(4)} J
            </div>
          </div>
          <div style="background: rgba(255, 255, 255, 0.02); padding: 12px; border-radius: 8px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Energy Difference</div>
            <div style="font-size: 20px; font-weight: 800; color: var(--color-cyan); font-family: var(--font-mono); margin-top: 4px;">
              -${diff.toFixed(4)} J
            </div>
          </div>
          <div style="background: rgba(255, 255, 255, 0.02); padding: 12px; border-radius: 8px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Measured Reduction</div>
            <div style="font-size: 20px; font-weight: 800; color: var(--color-healthy); font-family: var(--font-mono); margin-top: 4px;">
              ${pctSaved.toFixed(1)}%
            </div>
          </div>
        </div>
      `;
    } else {
      energyImpactContent = `
        <div class="empty-state" style="padding: 20px;">
          <div class="empty-state-title" style="color: var(--color-warning);">Observation Window Active</div>
          <div class="empty-state-text">Energy savings calculation requires a completed attack/mitigation measurement window.</div>
        </div>
      `;
    }
  } else {
    energyImpactContent = `
      <div class="empty-state" style="padding: 20px;">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <div class="empty-state-title">No Completed Mitigation Cycle Recorded</div>
        <div class="empty-state-text">Energy savings calculation requires a completed attack/mitigation measurement window.</div>
      </div>
    `;
  }

  // Mitigation rows
  const mitRowsHtml = mitigations.length === 0 ? `
    <tr>
      <td colspan="5" style="text-align: center; padding: 24px; color: var(--text-muted);">
        No mitigation actions triggered yet. Mitigations activate automatically upon attack confirmation.
      </td>
    </tr>
  ` : mitigations.map(m => {
    const timeStr = new Date(m.timestamp * 1000).toLocaleTimeString();
    return `
      <tr>
        <td class="cell-mono" style="color: var(--text-muted);">${timeStr}</td>
        <td>
          <span class="pod-name-cell" title="${m.pod_name}">${m.pod_name}</span>
        </td>
        <td>${renderStatusBadge(m.action)}</td>
        <td>${renderStatusBadge(m.status)}</td>
        <td class="cell-mono">${(m.score !== undefined ? m.score : 0).toFixed(4)}</td>
      </tr>
    `;
  }).join('');

  return `
    <!-- Top Cards (Section 9) -->
    <div class="kpi-grid">
      ${renderMetricCard({
        label: 'Threats Detected',
        value: String(threatsDetected),
        subtext: 'Confirmed attack workloads',
        accent: threatsDetected > 0 ? 'red' : 'green',
      })}

      ${renderMetricCard({
        label: 'Threats Mitigated',
        value: String(threatsMitigated),
        subtext: 'Kubernetes progressive actions',
        accent: 'amber',
      })}

      ${renderMetricCard({
        label: 'Successful Actions',
        value: String(successfulActions),
        subtext: 'Deployment patches & evictions',
        accent: 'green',
      })}

      ${renderMetricCard({
        label: 'Active Threats',
        value: String(activeIncidents),
        subtext: 'Currently unmitigated',
        accent: activeIncidents > 0 ? 'red' : 'green',
      })}
    </div>

    <!-- Visual Progressive Mitigation Pipeline (Section 9) -->
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Automated Progressive Mitigation Pipeline</div>
          <div class="card-subtitle">Production-grade two-stage Kubernetes mitigation architecture</div>
        </div>
      </div>

      <div class="pipeline-grid">
        <div class="pipeline-card">
          <div class="pipeline-step-num">Step 1</div>
          <div class="pipeline-step-name">AI Anomaly Flag</div>
          <div class="pipeline-step-detail">Telemetry vector evaluated by Isolation Forest.</div>
        </div>

        <div class="pipeline-card">
          <div class="pipeline-step-num">Step 2</div>
          <div class="pipeline-step-name">Confirmation</div>
          <div class="pipeline-step-detail">Validates 3 consecutive anomalous windows (15s).</div>
        </div>

        <div class="pipeline-card">
          <div class="pipeline-step-num">Step 3</div>
          <div class="pipeline-step-name">Deployment Throttle</div>
          <div class="pipeline-step-detail">Patches Deployment pod-template to cpu=100m, mem=128Mi.</div>
        </div>

        <div class="pipeline-card">
          <div class="pipeline-step-num">Step 4</div>
          <div class="pipeline-step-name">Observation</div>
          <div class="pipeline-step-detail">Monitors workload during 2-window grace period.</div>
        </div>

        <div class="pipeline-card">
          <div class="pipeline-step-num">Step 5</div>
          <div class="pipeline-step-name">Pod Deletion</div>
          <div class="pipeline-step-detail">Evicts persistent attack pod; replacement uses throttled template.</div>
        </div>

        <div class="pipeline-card">
          <div class="pipeline-step-num">Step 6</div>
          <div class="pipeline-step-name">Recovery</div>
          <div class="pipeline-step-detail">Normal cluster power budget and compute envelope restored.</div>
        </div>
      </div>
    </div>

    <!-- Energy Impact Section (Section 10) -->
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Energy Impact & Conservation Telemetry</div>
          <div class="card-subtitle">Verified power consumption differentials before and after automated mitigation</div>
        </div>
        <span class="badge badge-info">True Telemetry Only</span>
      </div>

      ${energyImpactContent}
    </div>

    <!-- Mitigation Log Table -->
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Mitigation Operations Log</div>
          <div class="card-subtitle">Chronological record of Kubernetes API patch and delete operations</div>
        </div>
        <span class="badge badge-normal">${mitigations.length} Logged Actions</span>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Target Workload</th>
              <th>Mitigation Action</th>
              <th>Kubernetes Status</th>
              <th>Trigger Score</th>
            </tr>
          </thead>
          <tbody>
            ${mitRowsHtml}
          </tbody>
        </table>
      </div>
    </div>
  `;
}
