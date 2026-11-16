/**
 * statusBadge.js - Standardized badge generator.
 */

export function renderStatusBadge(status, label = null) {
  if (!status) return '<span class="badge badge-normal">NORMAL</span>';
  const s = String(status).toUpperCase();
  const text = label || s;

  switch (s) {
    case 'NORMAL':
    case 'HEALTHY':
    case 'SUCCESS':
    case 'PROTECTED':
    case 'ONLINE':
      return `<span class="badge badge-normal">${text}</span>`;

    case 'WARNING':
    case 'COLLECTING_BASELINE':
    case 'COLLECTING':
      return `<span class="badge badge-warning">${text}</span>`;

    case 'ANOMALY':
    case 'ATTACK':
    case 'ACTIVE INCIDENT':
    case 'FAILED':
      return `<span class="badge badge-danger">${text}</span>`;

    case 'CONFIRMED':
    case 'CONFIRMED_ATTACK':
      return `<span class="badge badge-danger" style="background-color: rgba(239, 68, 68, 0.25); border-color: #ef4444;">● ${text}</span>`;

    case 'THROTTLED':
      return `<span class="badge badge-throttled">⚡ ${text}</span>`;

    case 'DELETED':
    case 'TERMINATED':
      return `<span class="badge badge-deleted">✕ ${text}</span>`;

    case 'DETECTING':
    case 'TRAINED':
      return `<span class="badge badge-info">${text}</span>`;

    default:
      return `<span class="badge badge-info">${text}</span>`;
  }
}
