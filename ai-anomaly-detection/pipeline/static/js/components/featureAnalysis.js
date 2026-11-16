/**
 * featureAnalysis.js - Anomaly root cause explanation ("Why was this workload flagged?")
 */

import { renderStatusBadge } from './statusBadge.js';

export function renderFeatureAnalysis(detection) {
  if (!detection) {
    return `
      <div class="card">
        <div class="card-header">
          <div class="card-title">AI Anomaly Root Cause Analysis</div>
          <div class="card-subtitle">Select an anomaly event to inspect telemetry attribution</div>
        </div>
        <div class="empty-state" style="padding: 24px;">
          <div class="empty-state-title">No Active Anomaly Selected</div>
          <div class="empty-state-text">Workload feature levels will populate automatically when an anomaly is detected.</div>
        </div>
      </div>
    `;
  }

  // Derive feature levels from real thresholds established in config.py / model_manager.py
  // MIN_ATTACK_CPU = 0.15, MIN_ATTACK_ENERGY = 0.05
  const avgCpu = detection.avg_cpu !== undefined ? detection.avg_cpu : (detection.cpu || 0);
  const avgMem = detection.avg_memory_mb !== undefined ? detection.avg_memory_mb : (detection.mem_mb || 0);
  const avgEnergy = detection.avg_energy !== undefined ? detection.avg_energy : (detection.energy || 0);
  const eCpuRatio = detection.energy_cpu_ratio !== undefined ? detection.energy_cpu_ratio : (avgCpu > 0 ? avgEnergy / avgCpu : 0);
  const consecutive = detection.consecutive || 0;

  const isCpuHigh = avgCpu > 0.15;
  const isEnergyHigh = avgEnergy > 0.05;
  const isMemHigh = avgMem > 150;
  const isRatioHigh = eCpuRatio > 0.38;
  const isDurationHigh = consecutive >= 3;

  return `
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Why Was This Workload Flagged?</div>
          <div class="card-subtitle">Workload: <strong style="color:#fff;">${detection.pod_name || detection.pod}</strong></div>
        </div>
        ${renderStatusBadge(detection.prediction_ea || 'ANOMALY')}
      </div>

      <div class="feature-flag-list">
        <div class="feature-flag-row">
          <div class="feature-flag-name">
            <span>CPU Utilization</span>
            <span class="cell-mono" style="color:var(--text-muted); font-size:12px;">(${avgCpu.toFixed(4)} cores)</span>
          </div>
          ${renderStatusBadge(isCpuHigh ? 'ANOMALY' : 'NORMAL', isCpuHigh ? 'HIGH' : 'NORMAL')}
        </div>

        <div class="feature-flag-row">
          <div class="feature-flag-name">
            <span>Energy Consumption</span>
            <span class="cell-mono" style="color:var(--text-muted); font-size:12px;">(${avgEnergy.toFixed(4)} J)</span>
          </div>
          ${renderStatusBadge(isEnergyHigh ? 'ANOMALY' : 'NORMAL', isEnergyHigh ? 'HIGH' : 'NORMAL')}
        </div>

        <div class="feature-flag-row">
          <div class="feature-flag-name">
            <span>Memory Consumption</span>
            <span class="cell-mono" style="color:var(--text-muted); font-size:12px;">(${avgMem.toFixed(1)} MB)</span>
          </div>
          ${renderStatusBadge(isMemHigh ? 'WARNING' : 'NORMAL', isMemHigh ? 'ELEVATED' : 'NORMAL')}
        </div>

        <div class="feature-flag-row">
          <div class="feature-flag-name">
            <span>Energy-to-CPU Ratio</span>
            <span class="cell-mono" style="color:var(--text-muted); font-size:12px;">(${Number(eCpuRatio).toFixed(4)})</span>
          </div>
          ${renderStatusBadge(isRatioHigh ? 'ANOMALY' : 'NORMAL', isRatioHigh ? 'HIGH DISPROPORTION' : 'BALANCED')}
        </div>

        <div class="feature-flag-row">
          <div class="feature-flag-name">
            <span>Consecutive Duration</span>
            <span class="cell-mono" style="color:var(--text-muted); font-size:12px;">(${consecutive} windows)</span>
          </div>
          ${renderStatusBadge(isDurationHigh ? 'ANOMALY' : 'NORMAL', isDurationHigh ? 'SUSTAINED ABUSE' : 'OBSERVING')}
        </div>
      </div>
    </div>
  `;
}
