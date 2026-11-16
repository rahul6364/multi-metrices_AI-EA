/**
 * metricCard.js - Formatted KPI metric card generator.
 */

export function renderMetricCard({
  id = '',
  label = '',
  value = '0',
  subtext = '',
  accent = 'cyan',
  iconSvg = '',
}) {
  return `
    <div class="metric-card accent-${accent}" ${id ? `id="${id}"` : ''}>
      <div class="metric-top">
        <span class="metric-label">${label}</span>
        ${iconSvg ? `<div class="metric-icon-box">${iconSvg}</div>` : ''}
      </div>
      <div class="metric-value">${value}</div>
      ${subtext ? `<div class="metric-subtext">${subtext}</div>` : ''}
    </div>
  `;
}
