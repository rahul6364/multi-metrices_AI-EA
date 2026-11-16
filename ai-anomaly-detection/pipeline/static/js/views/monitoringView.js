/**
 * monitoringView.js - Live Monitoring View with 5 dedicated time-series charts and Live Pod Table.
 */

import { chartManager } from '../charts.js';
import { renderPodTable } from '../components/podTable.js';
import { store } from '../state.js';

export function renderMonitoring(state) {
  const { systemData, selectedPod, searchQuery, statusFilter } = state;
  const pods = systemData.pods || {};
  const podList = Object.keys(pods);

  // Group detections by pod
  const detectionsByPod = {};
  (systemData.detection_history || []).forEach(d => {
    if (!detectionsByPod[d.pod_name]) {
      detectionsByPod[d.pod_name] = d;
    }
  });

  const podOptionsHtml = [
    `<option value="all" ${selectedPod === 'all' ? 'selected' : ''}>All Workloads (Aggregate)</option>`,
    ...podList.map(pod => `<option value="${pod}" ${selectedPod === pod ? 'selected' : ''}>${pod}</option>`)
  ].join('');

  return `
    <div class="card" style="padding: 16px 20px;">
      <div class="monitoring-controls">
        <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <label style="font-weight: 600; font-size: 13px; color: var(--text-secondary);">Focus Workload:</label>
            <select id="select-pod-filter" class="select-clean" style="min-width: 240px;">
              ${podOptionsHtml}
            </select>
          </div>

          <div style="display: flex; align-items: center; gap: 8px;">
            <label style="font-weight: 600; font-size: 13px; color: var(--text-secondary);">Status Filter:</label>
            <select id="select-status-filter" class="select-clean">
              <option value="all" ${statusFilter === 'all' ? 'selected' : ''}>All Statuses</option>
              <option value="anomaly" ${statusFilter === 'anomaly' ? 'selected' : ''}>Anomalies Only</option>
              <option value="normal" ${statusFilter === 'normal' ? 'selected' : ''}>Normal Only</option>
            </select>
          </div>
        </div>

        <div class="input-group" style="min-width: 220px;">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input type="text" id="pod-search-input" class="input-clean" placeholder="Filter pod name..." value="${searchQuery || ''}" />
        </div>
      </div>
    </div>

    <!-- 5 Dedicated Telemetry Charts (Section 3) -->
    <div class="charts-grid">
      <!-- 1. Energy Consumption -->
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title-box">
            <span class="chart-indicator-dot" style="background: var(--color-energy);"></span>
            <span style="font-weight: 700; color: #fff; font-size: 14px;">Energy Consumption Over Time</span>
          </div>
          <span class="badge badge-info">${systemData.kepler_active ? 'eBPF Kepler' : 'Estimated'}</span>
        </div>
        <div class="chart-canvas-container">
          <canvas id="chart-energy"></canvas>
        </div>
      </div>

      <!-- 2. CPU Utilization -->
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title-box">
            <span class="chart-indicator-dot" style="background: var(--color-cpu);"></span>
            <span style="font-weight: 700; color: #fff; font-size: 14px;">CPU Utilization Over Time</span>
          </div>
          <span style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono);">Rate 30s</span>
        </div>
        <div class="chart-canvas-container">
          <canvas id="chart-cpu"></canvas>
        </div>
      </div>

      <!-- 3. Memory Utilization -->
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title-box">
            <span class="chart-indicator-dot" style="background: var(--color-memory);"></span>
            <span style="font-weight: 700; color: #fff; font-size: 14px;">Memory Working Set Over Time</span>
          </div>
          <span style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono);">Megabytes</span>
        </div>
        <div class="chart-canvas-container">
          <canvas id="chart-memory"></canvas>
        </div>
      </div>

      <!-- 4. Network Throughput -->
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title-box">
            <span class="chart-indicator-dot" style="background: var(--color-network);"></span>
            <span style="font-weight: 700; color: #fff; font-size: 14px;">Network Throughput Over Time</span>
          </div>
          <span style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono);">RX + TX (KB/s)</span>
        </div>
        <div class="chart-canvas-container">
          <canvas id="chart-network"></canvas>
        </div>
      </div>

      <!-- 5. Energy/CPU Ratio (Spans full width or 5th slot) -->
      <div class="chart-card" style="grid-column: 1 / -1;">
        <div class="chart-header">
          <div class="chart-title-box">
            <span class="chart-indicator-dot" style="background: var(--color-cyan);"></span>
            <span style="font-weight: 700; color: #fff; font-size: 14px;">Energy-to-CPU Ratio Over Time (Research Differentiator)</span>
          </div>
          <span class="badge badge-normal">Behavioral Inefficiency Signal</span>
        </div>
        <div class="chart-canvas-container" style="min-height: 220px;">
          <canvas id="chart-ratio"></canvas>
        </div>
      </div>
    </div>

    <!-- Live Pod Table (Section 4) -->
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Live Monitored Workloads</div>
          <div class="card-subtitle">Real-time telemetry and dual Isolation Forest evaluation for active Kubernetes pods</div>
        </div>
        <span class="badge badge-info">${podList.length} Active Pods</span>
      </div>

      <div id="pod-table-wrapper">
        ${renderPodTable(pods, detectionsByPod, { searchQuery, statusFilter })}
      </div>
    </div>
  `;
}

export function updateMonitoringCharts(state) {
  const { systemData, selectedPod } = state;
  const timeline = systemData.metrics_timeline || {};
  const pods = systemData.pods || {};

  // Find target telemetry samples
  let targetSamples = [];
  if (selectedPod !== 'all' && timeline[selectedPod]) {
    targetSamples = timeline[selectedPod];
  } else {
    // Pick the first active pod or merge timestamps
    const firstPod = Object.keys(timeline)[0];
    if (firstPod) {
      targetSamples = timeline[firstPod];
    }
  }

  if (!targetSamples || targetSamples.length === 0) return;

  const labels = targetSamples.map(x => new Date(x.timestamp * 1000).toLocaleTimeString());
  const cpuData = targetSamples.map(x => x.cpu);
  const energyData = targetSamples.map(x => x.energy);
  const networkData = targetSamples.map(x => (x.network || 0) / 1024); // to KB/s

  // Memory data derived from current pod stats or timeline
  const memData = targetSamples.map(x => {
    // If pod currently has memory_mb
    const p = pods[selectedPod] || Object.values(pods)[0];
    return p ? p.memory_mb : 0;
  });

  // Energy/CPU Ratio
  const ratioData = targetSamples.map(x => {
    return x.cpu > 0 ? (x.energy / x.cpu) : 0;
  });

  // Initialize or update charts
  chartManager.createTimeSeriesChart('chart-energy', 'Energy (Joules)', '#38bdf8', '56, 189, 248', 'J');
  chartManager.updateTimeSeriesData('chart-energy', labels, energyData);

  chartManager.createTimeSeriesChart('chart-cpu', 'CPU (Cores)', '#60a5fa', '96, 165, 250', 'cores');
  chartManager.updateTimeSeriesData('chart-cpu', labels, cpuData);

  chartManager.createTimeSeriesChart('chart-memory', 'Memory (MB)', '#a78bfa', '167, 139, 250', 'MB');
  chartManager.updateTimeSeriesData('chart-memory', labels, memData);

  chartManager.createTimeSeriesChart('chart-network', 'Network (KB/s)', '#34d399', '52, 211, 153', 'KB/s');
  chartManager.updateTimeSeriesData('chart-network', labels, networkData);

  chartManager.createTimeSeriesChart('chart-ratio', 'Energy / CPU Ratio', '#06b6d4', '6, 182, 212', '');
  chartManager.updateTimeSeriesData('chart-ratio', labels, ratioData);
}

export function initMonitoringEvents() {
  const selectPod = document.getElementById('select-pod-filter');
  if (selectPod) {
    selectPod.addEventListener('change', (e) => {
      store.setSelectedPod(e.target.value);
    });
  }

  const selectStatus = document.getElementById('select-status-filter');
  if (selectStatus) {
    selectStatus.addEventListener('change', (e) => {
      store.setStatusFilter(e.target.value);
    });
  }

  const searchInput = document.getElementById('pod-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      store.setSearchQuery(e.target.value);
    });
  }
}
