/**
 * charts.js - Reusable Chart.js factory tailored for dark cybersecurity theme.
 */

// Global Chart.js dark defaults
if (window.Chart) {
  Chart.defaults.color = '#94a3b8';
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.font.size = 11;
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.legend.labels.boxWidth = 8;
  Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15, 20, 31, 0.95)';
  Chart.defaults.plugins.tooltip.titleColor = '#fff';
  Chart.defaults.plugins.tooltip.bodyColor = '#e2e8f0';
  Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.12)';
  Chart.defaults.plugins.tooltip.borderWidth = 1;
  Chart.defaults.plugins.tooltip.padding = 10;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
}

export class ChartManager {
  constructor() {
    this.charts = {};
  }

  _getOrCreateGradient(ctx, colorRgb, height = 240) {
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, `rgba(${colorRgb}, 0.25)`);
    gradient.addColorStop(1, `rgba(${colorRgb}, 0.0)`);
    return gradient;
  }

  createTimeSeriesChart(canvasId, label, colorHex, colorRgb, unit = '') {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    if (this.charts[canvasId]) {
      this.charts[canvasId].destroy();
    }

    const ctx = canvas.getContext('2d');
    const bgGradient = this._getOrCreateGradient(ctx, colorRgb);

    this.charts[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: label,
          data: [],
          borderColor: colorHex,
          borderWidth: 2,
          backgroundColor: bgGradient,
          fill: true,
          tension: 0.35,
          pointRadius: 2,
          pointHoverRadius: 5,
          pointBackgroundColor: colorHex,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        scales: {
          x: {
            grid: {
              color: 'rgba(255, 255, 255, 0.04)',
              drawBorder: false,
            },
            ticks: {
              maxTicksLimit: 6,
              color: '#64748b',
            }
          },
          y: {
            grid: {
              color: 'rgba(255, 255, 255, 0.04)',
              drawBorder: false,
            },
            ticks: {
              maxTicksLimit: 5,
              color: '#64748b',
              callback: (val) => `${val}${unit ? ' ' + unit : ''}`,
            },
            beginAtZero: true,
          }
        },
        plugins: {
          legend: {
            display: false,
          }
        }
      }
    });

    return this.charts[canvasId];
  }

  updateTimeSeriesData(canvasId, labels, dataPoints) {
    const chart = this.charts[canvasId];
    if (!chart) return;

    chart.data.labels = labels;
    chart.data.datasets[0].data = dataPoints;
    chart.update('none'); // Update without full redraw animation for silky performance
  }

  createResearchComparisonChart(canvasId, dataEa, dataBasic) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    if (this.charts[canvasId]) {
      this.charts[canvasId].destroy();
    }

    const labels = ['Precision', 'Recall', 'F1 Score', 'Accuracy', '1 - FPR'];
    const valuesEa = [
      (dataEa.precision || 0) * 100,
      (dataEa.recall || 0) * 100,
      (dataEa.f1_score || 0) * 100,
      (dataEa.accuracy || 0) * 100,
      (1 - (dataEa.fpr || 0)) * 100,
    ];
    const valuesBasic = [
      (dataBasic.precision || 0) * 100,
      (dataBasic.recall || 0) * 100,
      (dataBasic.f1_score || 0) * 100,
      (dataBasic.accuracy || 0) * 100,
      (1 - (dataBasic.fpr || 0)) * 100,
    ];

    const ctx = canvas.getContext('2d');
    this.charts[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Energy-Aware IF (8 features)',
            data: valuesEa,
            backgroundColor: 'rgba(6, 182, 212, 0.75)',
            borderColor: '#06b6d4',
            borderWidth: 1,
            borderRadius: 6,
          },
          {
            label: 'Basic IF (6 features)',
            data: valuesBasic,
            backgroundColor: 'rgba(148, 163, 184, 0.45)',
            borderColor: '#94a3b8',
            borderWidth: 1,
            borderRadius: 6,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.04)' },
          },
          y: {
            min: 0,
            max: 100,
            grid: { color: 'rgba(255, 255, 255, 0.04)' },
            ticks: {
              callback: (val) => `${val}%`,
            }
          }
        },
        plugins: {
          legend: {
            position: 'top',
            labels: { boxWidth: 10 }
          },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: ${ctx.raw.toFixed(1)}%`
            }
          }
        }
      }
    });

    return this.charts[canvasId];
  }

  destroy(canvasId) {
    if (this.charts[canvasId]) {
      this.charts[canvasId].destroy();
      delete this.charts[canvasId];
    }
  }

  destroyAll() {
    for (const key of Object.keys(this.charts)) {
      this.destroy(key);
    }
  }
}

export const chartManager = new ChartManager();
