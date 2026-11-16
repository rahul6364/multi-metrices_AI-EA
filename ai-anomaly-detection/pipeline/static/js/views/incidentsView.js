/**
 * incidentsView.js - Security Incidents log with pagination, filtering & Attack Response Timeline.
 */

import { renderMetricCard } from '../components/metricCard.js';
import { renderStatusBadge } from '../components/statusBadge.js';
import { renderTimeline } from '../components/timeline.js';

let currentPage = 1;
const pageSize = 15;

export function renderIncidents(state) {
  const { systemData, incidentFilter = 'all' } = state;
  const detections = systemData.detection_history || [];
  const mitigations = systemData.mitigation_history || [];
  const comparison = systemData.comparison_stats || {};

  // Metrics summary
  const totalEvents = detections.length;
  const totalAnomalies = comparison.ea_detections || 0;
  const falsePositives = comparison.ea_false_positives || 0;
  const confirmedAnomalies = comparison.ea_confirmed_anomalies || comparison.ea_confirmed || 0;
  const confirmedAttacks = comparison.ea_confirmed_attacks || 0;
  const activeIncidents = systemData.active_incident_count || 0;

  // Filter detections
  let filtered = detections;
  if (incidentFilter === 'anomalies') {
    filtered = detections.filter(d => d.prediction_ea === 'ANOMALY' || d.consecutive >= 1);
  } else if (incidentFilter === 'confirmed') {
    filtered = detections.filter(d => d.consecutive >= 3);
  }

  // Pagination calculation
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  if (currentPage > totalPages) currentPage = totalPages;
  const startIndex = (currentPage - 1) * pageSize;
  const pageItems = filtered.slice(startIndex, startIndex + pageSize);

  const tableRowsHtml = pageItems.length === 0 ? `
    <tr>
      <td colspan="10" style="text-align: center; padding: 24px; color: var(--text-muted);">
        No security events recorded in this filter view.
      </td>
    </tr>
  ` : pageItems.map(d => {
    const isConfirmed = d.consecutive >= 3;
    const isAnomaly = d.consecutive >= 1 || d.prediction_ea === 'ANOMALY';
    const rowClass = isConfirmed ? 'row-confirmed' : (isAnomaly ? 'row-anomaly' : '');
    const dateStr = new Date(d.timestamp * 1000).toLocaleTimeString();

    return `
      <tr class="${rowClass}">
        <td class="cell-mono" style="color: var(--text-muted);">${dateStr}</td>
        <td>
          <span class="pod-name-cell" title="${d.pod_name || d.pod}">
            ${d.pod_name || d.pod}
          </span>
        </td>
        <td class="cell-mono">${(d.avg_cpu || d.cpu || 0).toFixed(4)}</td>
        <td class="cell-mono">${(d.avg_memory_mb || d.mem_mb || 0).toFixed(1)} MB</td>
        <td class="cell-mono" style="color: var(--color-energy);">${(d.avg_energy || d.energy || 0).toFixed(4)} J</td>
        <td class="cell-mono" style="color: var(--color-cyan);">${Number(d.energy_cpu_ratio || d.e_cpu || 0).toFixed(4)}</td>
        <td>${renderStatusBadge(d.prediction_ea || d.ea)}</td>
        <td>${renderStatusBadge(d.prediction_basic || d.basic)}</td>
        <td class="cell-mono" style="color: ${(d.score_ea || d.score || 0) < 0 ? 'var(--color-danger)' : 'var(--text-secondary)'};">
          ${(d.score_ea || d.score || 0).toFixed(4)}
        </td>
        <td class="cell-mono" style="font-weight: 700; color: ${isConfirmed ? 'var(--color-danger)' : 'var(--text-primary)'};">
          ${d.consecutive || 0}
        </td>
      </tr>
    `;
  }).join('');

  return `
    <!-- Top KPI Cards (Section 7) -->
    <div class="kpi-grid">
      ${renderMetricCard({
        label: 'Total Detection Events',
        value: String(totalEvents),
        subtext: 'Historical sliding windows evaluated',
        accent: 'blue',
      })}

      ${renderMetricCard({
        label: 'Anomalies Flagged',
        value: String(totalAnomalies),
        subtext: 'Energy-Aware Isolation Forest detections',
        accent: totalAnomalies > 0 ? 'red' : 'green',
      })}

      ${renderMetricCard({
        label: 'Confirmed Anomalies',
        value: String(confirmedAnomalies),
        subtext: `${confirmedAttacks} attack workloads | ${falsePositives} false positives`,
        accent: confirmedAttacks > 0 ? 'red' : (confirmedAnomalies > 0 ? 'amber' : 'green'),
      })}

      ${renderMetricCard({
        label: 'Active Incidents',
        value: String(activeIncidents),
        subtext: 'Currently unmitigated abnormal states',
        accent: activeIncidents > 0 ? 'amber' : 'green',
      })}
    </div>

    <!-- Visual Attack Response Timeline (Section 8) -->
    ${renderTimeline(detections, mitigations)}

    <!-- Recent Security Events Log -->
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Recent Security Events Log</div>
          <div class="card-subtitle">Chronological record of multi-metric anomaly predictions and model scores</div>
        </div>

        <div style="display: flex; align-items: center; gap: 10px;">
          <select id="select-incident-filter" class="select-clean">
            <option value="all" ${incidentFilter === 'all' ? 'selected' : ''}>All Events</option>
            <option value="anomalies" ${incidentFilter === 'anomalies' ? 'selected' : ''}>Anomalies Only</option>
            <option value="confirmed" ${incidentFilter === 'confirmed' ? 'selected' : ''}>Confirmed Attacks Only</option>
          </select>
        </div>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Workload</th>
              <th>CPU</th>
              <th>Memory</th>
              <th>Energy</th>
              <th>E/CPU</th>
              <th>EA Result</th>
              <th>Basic Result</th>
              <th>Score</th>
              <th>Consecutive</th>
            </tr>
          </thead>
          <tbody>
            ${tableRowsHtml}
          </tbody>
        </table>
      </div>

      <!-- Pagination Controls -->
      <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--border-subtle);">
        <div style="font-size: 12px; color: var(--text-muted);">
          Showing ${filtered.length > 0 ? startIndex + 1 : 0} to ${Math.min(filtered.length, startIndex + pageSize)} of ${filtered.length} events
        </div>
        <div style="display: flex; gap: 8px;">
          <button id="btn-prev-page" class="btn btn-secondary btn-sm" ${currentPage <= 1 ? 'disabled' : ''}>Previous</button>
          <span style="font-size: 12px; color: var(--text-secondary); align-self: center;">Page ${currentPage} of ${totalPages}</span>
          <button id="btn-next-page" class="btn btn-secondary btn-sm" ${currentPage >= totalPages ? 'disabled' : ''}>Next</button>
        </div>
      </div>
    </div>
  `;
}

export function initIncidentsEvents() {
  const prevBtn = document.getElementById('btn-prev-page');
  const nextBtn = document.getElementById('btn-next-page');
  const filterSelect = document.getElementById('select-incident-filter');

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (currentPage > 1) {
        currentPage--;
        window.reRenderCurrentView?.();
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      currentPage++;
      window.reRenderCurrentView?.();
    });
  }

  if (filterSelect) {
    filterSelect.addEventListener('change', (e) => {
      currentPage = 1;
      window.reRenderCurrentView?.({ incidentFilter: e.target.value });
    });
  }
}
