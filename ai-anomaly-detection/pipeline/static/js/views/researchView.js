/**
 * researchView.js - IEEE Research Analytics: Model Performance Comparison, Charts & Research Narrative.
 */

import { api } from '../api.js';
import { chartManager } from '../charts.js';
import { store } from '../state.js';

let showRawJson = false;

export function renderResearch(state) {
  const { lastEvaluationData, isCalculatingMetrics } = state;

  const ea = lastEvaluationData?.energy_aware || null;
  const basic = lastEvaluationData?.basic || null;

  return `
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">IEEE Research Evaluation: Model Performance</div>
          <div class="card-subtitle">
            Quantitative evaluation comparing Energy-Aware Isolation Forest (8 features) against Basic Isolation Forest (6 features)
          </div>
        </div>

        <div class="research-header-actions">
          <button id="btn-calc-metrics" class="btn btn-primary" ${isCalculatingMetrics ? 'disabled' : ''}>
            ${isCalculatingMetrics ? `
              <div class="spinner"></div>
              <span>Computing IEEE Metrics...</span>
            ` : `
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
              <span>Calculate IEEE Metrics</span>
            `}
          </button>

          ${lastEvaluationData ? `
            <button id="btn-toggle-raw-json" class="btn btn-secondary btn-sm">
              ${showRawJson ? 'Hide Raw JSON' : 'View Raw Response'}
            </button>
          ` : ''}
        </div>
      </div>

      ${lastEvaluationData ? `
        <!-- Metrics Cards Grid -->
        <div class="research-metrics-grid" style="margin-top: 10px;">
          <div class="research-card">
            <span class="research-card-title">Model Accuracy</span>
            <div class="research-dual-value">
              <span class="research-val-ea">${((ea?.accuracy || 0) * 100).toFixed(1)}%</span>
              <span class="research-val-basic">${((basic?.accuracy || 0) * 100).toFixed(1)}%</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span class="research-label-ea">● Energy-Aware</span>
              <span class="research-label-basic">● Basic IF</span>
            </div>
          </div>

          <div class="research-card">
            <span class="research-card-title">Precision (PPV)</span>
            <div class="research-dual-value">
              <span class="research-val-ea">${((ea?.precision || 0) * 100).toFixed(1)}%</span>
              <span class="research-val-basic">${((basic?.precision || 0) * 100).toFixed(1)}%</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span class="research-label-ea">● Energy-Aware</span>
              <span class="research-label-basic">● Basic IF</span>
            </div>
          </div>

          <div class="research-card">
            <span class="research-card-title">Recall (Sensitivity)</span>
            <div class="research-dual-value">
              <span class="research-val-ea">${((ea?.recall || 0) * 100).toFixed(1)}%</span>
              <span class="research-val-basic">${((basic?.recall || 0) * 100).toFixed(1)}%</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span class="research-label-ea">● Energy-Aware</span>
              <span class="research-label-basic">● Basic IF</span>
            </div>
          </div>

          <div class="research-card">
            <span class="research-card-title">F1 Score</span>
            <div class="research-dual-value">
              <span class="research-val-ea">${((ea?.f1_score || 0) * 100).toFixed(1)}%</span>
              <span class="research-val-basic">${((basic?.f1_score || 0) * 100).toFixed(1)}%</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span class="research-label-ea">● Energy-Aware</span>
              <span class="research-label-basic">● Basic IF</span>
            </div>
          </div>

          <div class="research-card">
            <span class="research-card-title">False Positive Rate</span>
            <div class="research-dual-value">
              <span class="research-val-ea" style="color: ${(ea?.fpr || 0) > 0.1 ? 'var(--color-warning)' : 'var(--color-healthy)'};">
                ${((ea?.fpr || 0) * 100).toFixed(1)}%
              </span>
              <span class="research-val-basic">
                ${((basic?.fpr || 0) * 100).toFixed(1)}%
              </span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span class="research-label-ea">● Energy-Aware</span>
              <span class="research-label-basic">● Basic IF</span>
            </div>
          </div>

          <div class="research-card">
            <span class="research-card-title">Detection Latency</span>
            <div class="research-dual-value">
              <span class="research-val-ea">${ea?.detection_latency !== undefined && ea.detection_latency >= 0 ? `${ea.detection_latency.toFixed(2)}s` : 'N/A'}</span>
              <span class="research-val-basic">${basic?.detection_latency !== undefined && basic.detection_latency >= 0 ? `${basic.detection_latency.toFixed(2)}s` : 'N/A'}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span class="research-label-ea">● Energy-Aware</span>
              <span class="research-label-basic">● Basic IF</span>
            </div>
          </div>
        </div>

        <!-- Comparative Bar Chart -->
        <div class="chart-card" style="margin-top: 20px; min-height: 280px;">
          <div class="chart-header">
            <span style="font-weight: 700; color: #fff; font-size: 14px;">Comparative Research Metrics (Higher is Better)</span>
            <span class="badge badge-normal">IEEE Evaluation Standard</span>
          </div>
          <div class="chart-canvas-container" style="min-height: 220px;">
            <canvas id="chart-research-comparison"></canvas>
          </div>
        </div>

        <!-- Raw JSON Inspector Drawer -->
        ${showRawJson ? `
          <div style="margin-top: 16px;">
            <div style="font-size: 12px; font-weight: 700; color: var(--text-muted); margin-bottom: 6px; text-transform: uppercase;">
              Raw Backend Evaluation Payload
            </div>
            <pre class="raw-json-drawer">${JSON.stringify(lastEvaluationData, null, 2)}</pre>
          </div>
        ` : ''}
      ` : `
        <div class="empty-state" style="padding: 36px 20px;">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <div class="empty-state-title">No Evaluation Metrics Generated Yet</div>
          <div class="empty-state-text">
            Click <strong>Calculate IEEE Metrics</strong> to evaluate ground-truth attack telemetry from the experiment log.
          </div>
        </div>
      `}
    </div>

    <!-- Research Contribution Narrative (Section 12) -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--color-cyan);">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
          </svg>
          <span>WHY ENERGY-AWARE DETECTION? (RESEARCH CONTRIBUTION)</span>
        </div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 14px; font-size: 13.5px; color: var(--text-secondary); line-height: 1.7;">
        <p>
          Conventional intrusion detection systems rely almost exclusively on perimeter network signatures or static resource thresholds. In modern containerized Kubernetes clusters, sophisticated attackers execute <strong>cryptojacking and persistent resource-abuse attacks</strong> that mimic legitimate batch compute or microservice bursts to evade detection.
        </p>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; margin-top: 4px;">
          <div style="background: rgba(255, 255, 255, 0.02); padding: 14px; border-radius: 8px; border: 1px solid var(--border-subtle);">
            <strong style="color: #fff; display: block; margin-bottom: 4px;">Energy as a First-Class Signal</strong>
            Energy consumption exhibits physical thermodynamics that software-level virtualization cannot conceal. Malicious compute loops generate distinct energy-to-CPU ratios compared to normal application transactions.
          </div>

          <div style="background: rgba(255, 255, 255, 0.02); padding: 14px; border-radius: 8px; border: 1px solid var(--border-subtle);">
            <strong style="color: #fff; display: block; margin-bottom: 4px;">Temporal Sliding Windows</strong>
            Rather than flagging instantaneous spikes, our framework analyzes 30-second temporal behavior envelopes (6 sliding samples) to identify sustained behavioral deviation while discarding transient noise.
          </div>

          <div style="background: rgba(255, 255, 255, 0.02); padding: 14px; border-radius: 8px; border: 1px solid var(--border-subtle);">
            <strong style="color: #fff; display: block; margin-bottom: 4px;">Progressive Cloud Mitigation</strong>
            Mitigation balances service reliability with threat containment through progressive action: resource constraint via Deployment template patching, followed by eviction only if abusive behavior persists.
          </div>
        </div>
      </div>
    </div>
  `;
}

export function updateResearchCharts(state) {
  const { lastEvaluationData } = state;
  if (!lastEvaluationData) return;

  const ea = lastEvaluationData.energy_aware || {};
  const basic = lastEvaluationData.basic || {};

  chartManager.createResearchComparisonChart('chart-research-comparison', ea, basic);
}

export function initResearchEvents() {
  const btnCalc = document.getElementById('btn-calc-metrics');
  if (btnCalc) {
    btnCalc.addEventListener('click', async () => {
      try {
        store.setCalculatingMetrics(true);
        window.reRenderCurrentView?.();
        const data = await api.getEvaluation();
        store.setEvaluationData(data);
        window.showToast?.('IEEE research metrics calculated successfully.', 'success');
        window.reRenderCurrentView?.();
      } catch (err) {
        store.setCalculatingMetrics(false);
        window.showToast?.(`Evaluation unavailable: ${err.message}`, 'danger');
        window.reRenderCurrentView?.();
      }
    });
  }

  const btnToggleRaw = document.getElementById('btn-toggle-raw-json');
  if (btnToggleRaw) {
    btnToggleRaw.addEventListener('click', () => {
      showRawJson = !showRawJson;
      window.reRenderCurrentView?.();
    });
  }
}
