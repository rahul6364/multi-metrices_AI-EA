/**
 * app.js - Main Application Orchestrator, Router & Real-Time Poller.
 */

import { api } from './api.js';
import { store } from './state.js';
import { renderOverview, initOverviewEvents } from './views/overviewView.js';
import { renderMonitoring, updateMonitoringCharts, initMonitoringEvents } from './views/monitoringView.js';
import { renderDetection, updateDetectionCharts } from './views/detectionView.js';
import { renderIncidents, initIncidentsEvents } from './views/incidentsView.js';
import { renderMitigation } from './views/mitigationView.js';
import { renderKubernetes } from './views/kubernetesView.js';
import { renderResearch, updateResearchCharts, initResearchEvents } from './views/researchView.js';

class App {
  constructor() {
    this.pollIntervalMs = 5000;
    this.pollTimer = null;
    this.viewContainers = {};
    this.currentViewId = 'overview';
  }

  init() {
    this._cacheDom();
    this._bindNavigation();
    this._bindGlobalEvents();
    this._setupStateSubscription();

    // Initial view render
    this.switchView('overview');

    // Initial data fetch and start periodic polling
    this.refresh();
    this.startPolling();
  }

  _cacheDom() {
    this.navItems = document.querySelectorAll('.nav-item');
    this.contentWrapper = document.getElementById('content-wrapper');
    this.pageTitle = document.getElementById('header-page-title');
    this.breadcrumbs = document.getElementById('header-breadcrumbs');
    this.headerStatus = document.getElementById('header-status-badge');
    this.headerTimestamp = document.getElementById('header-timestamp-val');
    this.sidebarStatusDot = document.getElementById('sidebar-status-dot');
    this.sidebarStatusText = document.getElementById('sidebar-status-text');
    this.sidebarKeplerText = document.getElementById('sidebar-kepler-text');
    this.incidentBadge = document.getElementById('nav-incident-badge');
    this.sidebar = document.getElementById('sidebar');
    this.mobileMenuBtn = document.getElementById('mobile-menu-btn');
  }

  _bindNavigation() {
    this.navItems.forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const targetView = item.getAttribute('data-view');
        if (targetView) {
          this.switchView(targetView);
          // Close mobile sidebar if open
          if (this.sidebar) this.sidebar.classList.remove('open');
        }
      });
    });

    if (this.mobileMenuBtn && this.sidebar) {
      this.mobileMenuBtn.addEventListener('click', () => {
        this.sidebar.classList.toggle('open');
      });
    }
  }

  _bindGlobalEvents() {
    // Global toast system
    window.showToast = (message, type = 'info') => {
      const container = document.getElementById('toast-container');
      if (!container) return;

      const toast = document.createElement('div');
      toast.className = 'toast';
      toast.innerHTML = `
        <span style="font-size: 14px;">${type === 'danger' ? '❌' : (type === 'success' ? '✅' : 'ℹ️')}</span>
        <span>${message}</span>
      `;

      container.appendChild(toast);
      setTimeout(() => {
        toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(50px)';
        setTimeout(() => toast.remove(), 300);
      }, 4000);
    };

    // Global re-render function for component-level updates
    window.reRenderCurrentView = (extraState = {}) => {
      if (Object.keys(extraState).length > 0) {
        Object.assign(store.state, extraState);
      }
      this.renderActiveView();
    };

    // Download Dataset Trigger
    const btnDownload = document.getElementById('btn-download-dataset');
    if (btnDownload) {
      btnDownload.addEventListener('click', () => {
        window.location.href = '/api/export/dataset';
      });
    }
  }

  _setupStateSubscription() {
    store.subscribe((state) => {
      this._updateHeaderAndSidebar(state);
      this.renderActiveView();
    });
  }

  switchView(viewId) {
    this.currentViewId = viewId;
    store.setActiveView(viewId);

    // Update nav active states
    this.navItems.forEach(item => {
      if (item.getAttribute('data-view') === viewId) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Update Header Titles
    const titleMap = {
      overview: 'System Overview & Command Center',
      monitoring: 'Live Workload Telemetry & Monitoring',
      detection: 'AI Anomaly Detection & Model Comparison',
      incidents: 'Security Incidents & Response Timeline',
      mitigation: 'Automated Mitigation Operations',
      kubernetes: 'K3s Cluster Infrastructure Topology',
      research: 'IEEE Research Analytics & Model Evaluation',
    };

    if (this.pageTitle) {
      this.pageTitle.textContent = titleMap[viewId] || 'Cloud Security Dashboard';
    }
    if (this.breadcrumbs) {
      this.breadcrumbs.innerHTML = `EnergyGuard <span>/</span> <strong style="color:#fff;">${viewId.toUpperCase()}</strong>`;
    }

    this.renderActiveView();
  }

  renderActiveView() {
    if (!this.contentWrapper) return;
    const state = store.state;

    let html = '';
    switch (this.currentViewId) {
      case 'overview':
        html = renderOverview(state);
        break;
      case 'monitoring':
        html = renderMonitoring(state);
        break;
      case 'detection':
        html = renderDetection(state);
        break;
      case 'incidents':
        html = renderIncidents(state);
        break;
      case 'mitigation':
        html = renderMitigation(state);
        break;
      case 'kubernetes':
        html = renderKubernetes(state);
        break;
      case 'research':
        html = renderResearch(state);
        break;
      default:
        html = renderOverview(state);
    }

    this.contentWrapper.innerHTML = `
      <div class="view-container active">
        ${html}
      </div>
    `;

    // Initialize event listeners for the view
    if (this.currentViewId === 'overview') initOverviewEvents();
    if (this.currentViewId === 'monitoring') {
      initMonitoringEvents();
      updateMonitoringCharts(state);
    }
    if (this.currentViewId === 'detection') {
      updateDetectionCharts(state);
    }
    if (this.currentViewId === 'incidents') initIncidentsEvents();
    if (this.currentViewId === 'research') {
      initResearchEvents();
      updateResearchCharts(state);
    }
  }

  _updateHeaderAndSidebar(state) {
    const { isOnline, lastUpdated, systemData } = state;

    // Header Live Badge
    if (this.headerStatus) {
      if (isOnline) {
        this.headerStatus.className = 'header-badge live';
        this.headerStatus.innerHTML = '<span class="status-dot online pulsing"></span><span>LIVE</span>';
      } else {
        this.headerStatus.className = 'header-badge offline';
        this.headerStatus.innerHTML = '<span class="status-dot offline"></span><span>DISCONNECTED</span>';
      }
    }

    // Header Timestamp
    if (this.headerTimestamp) {
      this.headerTimestamp.textContent = lastUpdated ? lastUpdated.toLocaleTimeString() : '--:--:--';
    }

    // Sidebar Status
    if (this.sidebarStatusDot) {
      this.sidebarStatusDot.className = `status-dot ${isOnline ? 'online pulsing' : 'offline'}`;
    }
    if (this.sidebarStatusText) {
      this.sidebarStatusText.textContent = isOnline ? 'Cluster Connected' : 'Reconnecting...';
    }
    if (this.sidebarKeplerText) {
      this.sidebarKeplerText.textContent = systemData.kepler_active ? '⚡ Kepler Hardware eBPF' : '📊 Estimated Energy Mode';
    }

    // Nav Incident Badge — only currently active incidents on live pods
    if (this.incidentBadge) {
      const activeCount = systemData.active_incident_count || 0;

      if (activeCount > 0) {
        this.incidentBadge.style.display = 'inline-block';
        this.incidentBadge.textContent = activeCount;
      } else {
        this.incidentBadge.style.display = 'none';
      }
    }
  }

  async refresh() {
    try {
      const data = await api.getStatus();
      store.updateSystemData(data);
    } catch (err) {
      store.setOnline(false);
    }
  }

  startPolling() {
    if (this.pollTimer) clearInterval(this.pollTimer);
    this.pollTimer = setInterval(() => {
      this.refresh();
    }, this.pollIntervalMs);
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
});
