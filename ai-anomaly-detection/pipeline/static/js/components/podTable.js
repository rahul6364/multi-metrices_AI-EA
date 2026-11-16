/**
 * podTable.js - Responsive, searchable, filterable Live Pod Table.
 */

import { renderStatusBadge } from './statusBadge.js';

export function renderPodTable(pods, detectionsByPod = {}, options = {}) {
  const {
    searchQuery = '',
    statusFilter = 'all',
  } = options;

  const podEntries = Object.entries(pods || {});

  if (podEntries.length === 0) {
    return `
      <div class="empty-state">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <div class="empty-state-title">No Monitored Pods Available</div>
        <div class="empty-state-text">Waiting for telemetry collection from Kubernetes cluster...</div>
      </div>
    `;
  }

  // Filter entries
  const filtered = podEntries.filter(([podName, p]) => {
    const d = detectionsByPod[podName] || {};
    const matchesSearch = !searchQuery || podName.toLowerCase().includes(searchQuery);
    
    let matchesStatus = true;
    if (statusFilter === 'anomaly') {
      matchesStatus = d.prediction_ea === 'ANOMALY' || (d.consecutive >= 1);
    } else if (statusFilter === 'normal') {
      matchesStatus = (!d.prediction_ea || d.prediction_ea === 'NORMAL') && (!d.consecutive || d.consecutive === 0);
    }

    return matchesSearch && matchesStatus;
  });

  if (filtered.length === 0) {
    return `
      <div class="empty-state">
        <div class="empty-state-title">No matching pods found</div>
        <div class="empty-state-text">Try adjusting your search query or status filter.</div>
      </div>
    `;
  }

  const rowsHtml = filtered.map(([podName, p]) => {
    const d = detectionsByPod[podName] || {
      prediction_ea: 'NORMAL',
      prediction_basic: 'NORMAL',
      score_ea: 0,
      consecutive: 0,
      energy_cpu_ratio: 0,
    };

    const isConfirmed = d.consecutive >= 3;
    const isAnomaly = d.consecutive >= 1 || d.prediction_ea === 'ANOMALY';
    let rowClass = '';
    if (isConfirmed) rowClass = 'row-confirmed';
    else if (isAnomaly) rowClass = 'row-anomaly';

    let actionStatus = '-';
    if (isConfirmed) actionStatus = 'CONFIRMED';
    else if (isAnomaly) actionStatus = 'ANOMALY';

    const eCpuRatio = d.energy_cpu_ratio !== undefined ? d.energy_cpu_ratio : (p.cpu > 0 ? p.energy_joules / p.cpu : 0);

    return `
      <tr class="${rowClass}">
        <td>
          <span class="pod-name-cell" title="${podName}">
            ${podName}
          </span>
        </td>
        <td class="cell-mono">${p.cpu.toFixed(4)}</td>
        <td class="cell-mono">${p.memory_mb.toFixed(1)} MB</td>
        <td class="cell-mono" style="color: var(--color-energy);">${p.energy_joules.toFixed(4)} J</td>
        <td class="cell-mono">${p.network_kbps.toFixed(2)} KB/s</td>
        <td class="cell-mono" style="color: var(--color-cyan);">${Number(eCpuRatio).toFixed(4)}</td>
        <td>${renderStatusBadge(d.prediction_ea)}</td>
        <td>${renderStatusBadge(d.prediction_basic)}</td>
        <td class="cell-mono" style="color: ${d.score_ea < 0 ? 'var(--color-danger)' : 'var(--text-secondary)'};">
          ${(d.score_ea || 0).toFixed(4)}
        </td>
        <td>${renderStatusBadge(actionStatus)}</td>
      </tr>
    `;
  }).join('');

  return `
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Pod Name</th>
            <th>CPU (Cores)</th>
            <th>Memory</th>
            <th>Energy</th>
            <th>Network</th>
            <th>E/CPU Ratio</th>
            <th>EA Status</th>
            <th>Basic Status</th>
            <th>Score</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          ${rowsHtml}
        </tbody>
      </table>
    </div>
  `;
}
