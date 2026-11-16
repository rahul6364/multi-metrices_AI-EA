/**
 * overviewView.js - Primary landing view with KPI cards, Command Center & Baseline training.
 */

import { renderMetricCard } from '../components/metricCard.js';
import { renderIncidentCard } from '../components/incidentCard.js';
import { renderStatusBadge } from '../components/statusBadge.js';
import { api } from '../api.js';

export function renderOverview(state) {
  const { systemData } = state;
  const pods = systemData.pods || {};
  const podCount = Object.keys(pods).length;
  const mitigations = systemData.mitigation_history || [];
  const detections = systemData.detection_history || [];
  const comparison = systemData.comparison_stats || {};
  const training = systemData.training_progress || { current: 0, total: 30 };

  // Calculate cluster total energy rate from real pod values
  let totalEnergy = 0;
  Object.values(pods).forEach(p => {
    totalEnergy += (p.energy_joules || 0);
  });

  // Only show incidents that are active on live pods (server-computed).
  const activeIncidents = systemData.active_incidents || [];
  const activeAnomaly = activeIncidents.length > 0 ? activeIncidents[0] : null;
  const latestMitigation = activeAnomaly
    ? (mitigations.find(m => m.pod_name === activeAnomaly.pod_name) || null)
    : null;
  const currentActiveCount = systemData.active_incident_count || 0;

  // Derive dynamic system status
  let systemStatusText = 'PROTECTED';
  let systemStatusAccent = 'green';
  if (systemData.current_state === 'COLLECTING_BASELINE' || systemData.current_state === 'COLLECTING') {
    systemStatusText = 'COLLECTING BASELINE';
    systemStatusAccent = 'amber';
  } else if (systemData.current_state === 'TRAINING') {
    systemStatusText = 'TRAINING MODELS';
    systemStatusAccent = 'cyan';
  } else if (activeAnomaly) {
    systemStatusText = activeAnomaly.consecutive >= 3 ? 'ACTIVE INCIDENT' : 'WARNING';
    systemStatusAccent = activeAnomaly.consecutive >= 3 ? 'red' : 'amber';
  }

  // Baseline Progress percentage
  const progressPercent = Math.min(100, Math.round((training.current / (training.total || 30)) * 100));

  return `
    <!-- Top Hero Section -->
    <div class="hero-header">
      <div class="hero-title">ENERGY-AWARE CLOUD SECURITY</div>
      <div class="hero-subtitle">AI-based anomaly detection and progressive energy-aware mitigation for Kubernetes workloads</div>
    </div>

    <!-- Real Data KPI Grid -->
    <div class="kpi-grid">
      ${renderMetricCard({
        label: 'System Status',
        value: systemStatusText,
        subtext: `● ${systemData.current_state || 'IDLE'}`,
        accent: systemStatusAccent,
        iconSvg: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>'
      })}

      ${renderMetricCard({
        label: 'Pods Monitored',
        value: String(podCount),
        subtext: `${systemData.kepler_active ? 'Kepler Hardware eBPF' : 'Software Estimated'}`,
        accent: 'blue',
        iconSvg: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>'
      })}

      ${renderMetricCard({
        label: 'Active Anomalies',
        value: String(currentActiveCount),
        subtext: `${comparison.ea_false_positives || 0} false positives | ${comparison.ea_confirmed_attacks || 0} attack workloads`,
        accent: currentActiveCount > 0 ? 'red' : 'green',
        iconSvg: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>'
      })}

      ${renderMetricCard({
        label: 'Mitigations Executed',
        value: String(mitigations.length),
        subtext: `${mitigations.filter(m => m.status === 'SUCCESS').length} Successful Actions`,
        accent: 'amber',
        iconSvg: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>'
      })}

      ${renderMetricCard({
        label: 'Current Energy Rate',
        value: `${totalEnergy.toFixed(4)} J`,
        subtext: systemData.kepler_active ? '⚡ Real eBPF joules' : '📊 Real-time telemetry',
        accent: 'cyan',
        iconSvg: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>'
      })}

      ${renderMetricCard({
        label: 'Baseline Training',
        value: `${training.current}/${training.total}`,
        subtext: systemData.model_trained ? 'Model Ready (Active)' : 'Collecting Windows',
        accent: systemData.model_trained ? 'green' : 'purple',
        iconSvg: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>'
      })}
    </div>

    <!-- Security Command Center -->
    ${renderIncidentCard(activeAnomaly, latestMitigation)}

    <!-- Baseline Training Panel (Section 13) -->
    <div class="training-panel">
      <div class="training-panel-header">
        <div>
          <div class="card-title">
            <span>Normal Baseline Collection & Training</span>
            ${renderStatusBadge(systemData.model_trained ? 'TRAINED' : systemData.current_state)}
          </div>
          <div class="card-subtitle">
            Trains unsupervised Isolation Forest models on legitimate workload behavior
          </div>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <button id="btn-start-training" class="btn btn-healthy" ${systemData.current_state === 'COLLECTING_BASELINE' ? 'disabled' : ''}>
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>${systemData.current_state === 'COLLECTING_BASELINE' ? 'Collecting Baseline...' : 'Start Baseline Training'}</span>
          </button>
          <button id="btn-clear-incidents" class="btn btn-secondary" type="button">
            Clear Incident History
          </button>
        </div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 8px;">
        <div style="display: flex; justify-content: space-between; font-size: 13px;">
          <span style="color: var(--text-secondary);">Collection Progress (${training.current} / ${training.total} windows)</span>
          <span style="font-weight: 700; color: #fff;">${progressPercent}%</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill cyan ${systemData.current_state === 'COLLECTING_BASELINE' ? 'striped' : ''}" style="width: ${progressPercent}%;"></div>
        </div>
      </div>

      <div class="warning-callout">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        <span>
          <strong>Operational Guideline:</strong> Do not deploy attack or stress workloads during baseline collection.
          The models learn legitimate resource envelopes to minimize false alarms.
        </span>
      </div>
    </div>
  `;
}

export function initOverviewEvents() {
  const btn = document.getElementById('btn-start-training');
  if (btn) {
    btn.addEventListener('click', async () => {
      try {
        btn.disabled = true;
        btn.textContent = 'Initiating Collection...';
        await api.startBaselineTraining();
        window.showToast?.('Baseline collection initiated successfully.', 'success');
      } catch (err) {
        window.showToast?.(`Failed to start baseline: ${err.message}`, 'danger');
        btn.disabled = false;
      }
    });
  }

  const clearBtn = document.getElementById('btn-clear-incidents');
  if (clearBtn) {
    clearBtn.addEventListener('click', async () => {
      try {
        clearBtn.disabled = true;
        await api.clearIncidents();
        window.showToast?.('Incident history cleared.', 'success');
        window.location.reload();
      } catch (err) {
        window.showToast?.(`Failed to clear incidents: ${err.message}`, 'danger');
        clearBtn.disabled = false;
      }
    });
  }
}
