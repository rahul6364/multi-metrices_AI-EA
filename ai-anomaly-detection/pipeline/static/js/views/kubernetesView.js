/**
 * kubernetesView.js - Visual Kubernetes K3s cluster overview & workload topology.
 */

import { renderMetricCard } from '../components/metricCard.js';
import { renderStatusBadge } from '../components/statusBadge.js';

export function renderKubernetes(state) {
  const { systemData, clusterData } = state;
  const pods = systemData.pods || {};
  const detections = systemData.detection_history || [];

  const detectionsByPod = {};
  detections.forEach(d => {
    if (!detectionsByPod[d.pod_name]) detectionsByPod[d.pod_name] = d;
  });

  const podList = Object.values(pods);
  const totalPods = podList.length;
  const anomalousPods = podList.filter(p => {
    const d = detectionsByPod[p.pod_name];
    return d && (d.prediction_ea === 'ANOMALY' || d.consecutive >= 1);
  }).length;
  const healthyPods = totalPods - anomalousPods;

  // Aggregate cluster resources
  let totalCpu = 0;
  let totalMem = 0;
  let totalEnergy = 0;
  podList.forEach(p => {
    totalCpu += (p.cpu || 0);
    totalMem += (p.memory_mb || 0);
    totalEnergy += (p.energy_joules || 0);
  });

  // Group pods by namespace
  const namespaces = {};
  podList.forEach(p => {
    const ns = p.namespace || 'default';
    if (!namespaces[ns]) namespaces[ns] = [];
    namespaces[ns].push(p);
  });

  const podsListHtml = podList.map(p => {
    const d = detectionsByPod[p.pod_name];
    const isAnomaly = d && (d.prediction_ea === 'ANOMALY' || d.consecutive >= 1);
    return `
      <div class="node-pod-item">
        <div style="display: flex; align-items: center; gap: 8px; overflow: hidden;">
          <span style="color: ${isAnomaly ? 'var(--color-danger)' : 'var(--color-healthy)'}; font-size: 10px;">●</span>
          <span class="cell-mono" style="color: #fff; font-size: 12px; text-overflow: ellipsis; overflow: hidden;" title="${p.pod_name}">
            ${p.pod_name}
          </span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px; flex-shrink: 0;">
          <span class="cell-mono" style="font-size: 11px; color: var(--text-muted);">${p.cpu.toFixed(3)}c</span>
          <span class="cell-mono" style="font-size: 11px; color: var(--color-energy);">${p.energy_joules.toFixed(3)}J</span>
          ${renderStatusBadge(isAnomaly ? 'ANOMALY' : 'NORMAL')}
        </div>
      </div>
    `;
  }).join('');

  return `
    <!-- Top Cluster Metrics -->
    <div class="kpi-grid">
      ${renderMetricCard({
        label: 'Cluster Environment',
        value: 'K3s Cluster',
        subtext: 'v1.28+ Lightweight Orchestration',
        accent: 'blue',
      })}

      ${renderMetricCard({
        label: 'Monitored Pods',
        value: String(totalPods),
        subtext: `${healthyPods} Healthy | ${anomalousPods} Flagged`,
        accent: anomalousPods > 0 ? 'red' : 'green',
      })}

      ${renderMetricCard({
        label: 'Cluster CPU Usage',
        value: `${totalCpu.toFixed(4)}`,
        subtext: 'Aggregated core allocation',
        accent: 'cyan',
      })}

      ${renderMetricCard({
        label: 'Cluster Memory',
        value: `${totalMem.toFixed(1)} MB`,
        subtext: 'Working set memory footprint',
        accent: 'purple',
      })}
    </div>

    <!-- Cluster Nodes Topology (Section 11) -->
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">K3s Kubernetes Infrastructure Topology</div>
          <div class="card-subtitle">Cluster node state and active container workload placement</div>
        </div>
        ${renderStatusBadge('ONLINE', 'CONTROL-PLANE READY')}
      </div>

      <div class="cluster-grid">
        <!-- Node 1: Control-Plane / Primary Node -->
        <div class="node-card">
          <div class="node-header">
            <div class="node-title-box">
              <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--color-cyan);">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
              </svg>
              <div>
                <div class="node-title">Primary Node (Control-Plane / Worker)</div>
                <div class="node-role">K3s Core • Linux Kernel eBPF Telemetry Active</div>
              </div>
            </div>
            ${renderStatusBadge('HEALTHY', 'ONLINE')}
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 8px;">
            <div>
              <div style="font-size: 11px; color: var(--text-muted);">Allocated CPU</div>
              <div style="font-size: 16px; font-weight: 700; color: #fff; font-family: var(--font-mono);">${totalCpu.toFixed(4)} cores</div>
            </div>
            <div>
              <div style="font-size: 11px; color: var(--text-muted);">Energy Draw</div>
              <div style="font-size: 16px; font-weight: 700; color: var(--color-energy); font-family: var(--font-mono);">${totalEnergy.toFixed(4)} J</div>
            </div>
          </div>

          <div>
            <div style="font-size: 12px; font-weight: 700; color: var(--text-secondary); margin-bottom: 8px; text-transform: uppercase;">
              Active Pods (${podList.length})
            </div>
            <div class="node-pod-list">
              ${podsListHtml.length > 0 ? podsListHtml : '<div style="color: var(--text-muted); font-size: 12px;">No pods deployed.</div>'}
            </div>
          </div>
        </div>

        <!-- Monitoring & Telemetry Infrastructure Card -->
        <div class="node-card">
          <div class="node-header">
            <div class="node-title-box">
              <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--color-energy);">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <div>
                <div class="node-title">Observability & Pipeline Stack</div>
                <div class="node-role">Prometheus • Kepler • AI Detector Runtime</div>
              </div>
            </div>
            ${renderStatusBadge('HEALTHY', 'OPERATIONAL')}
          </div>

          <div style="display: flex; flex-direction: column; gap: 10px;">
            <div class="node-pod-item">
              <div>
                <strong style="color: #fff;">Kepler Energy Exporter</strong>
                <div style="font-size: 11px; color: var(--text-muted);">DaemonSet • eBPF Kernel Energy Counters</div>
              </div>
              ${renderStatusBadge(systemData.kepler_active ? 'ONLINE' : 'ESTIMATED')}
            </div>

            <div class="node-pod-item">
              <div>
                <strong style="color: #fff;">Prometheus TSDB</strong>
                <div style="font-size: 11px; color: var(--text-muted);">Scrapes container CPU, memory & Kepler joules</div>
              </div>
              ${renderStatusBadge('ONLINE', 'CONNECTED')}
            </div>

            <div class="node-pod-item">
              <div>
                <strong style="color: #fff;">AI Detector Pipeline</strong>
                <div style="font-size: 11px; color: var(--text-muted);">Dual Isolation Forest (8-D & 6-D) + Auto Mitigator</div>
              </div>
              ${renderStatusBadge(systemData.model_trained ? 'ONLINE' : 'TRAINING')}
            </div>
          </div>

          <div style="background: rgba(6, 182, 212, 0.08); border: 1px solid var(--color-cyan-border); border-radius: 8px; padding: 12px; font-size: 12px; color: #bae6fd; line-height: 1.5;">
            <strong>Cluster Architecture:</strong> Workloads run in target namespace <code>default</code> while monitoring agents run in isolated namespace <code>monitoring</code> to prevent interference with baseline power measurements.
          </div>
        </div>
      </div>
    </div>
  `;
}
