/**
 * timeline.js - Attack Response Timeline visualization based on real detection/mitigation data.
 */

export function renderTimeline(detections = [], mitigations = []) {
  // Determine current progression state based on recent events
  const hasMitigation = mitigations.length > 0;
  const latestMitigation = mitigations[0];
  const hasAnomaly = detections.some(d => d.prediction_ea === 'ANOMALY' || d.consecutive >= 1);
  const isConfirmed = detections.some(d => d.consecutive >= 3);
  const isDeleted = latestMitigation && latestMitigation.action === 'DELETED';
  const isThrottled = latestMitigation && latestMitigation.action === 'THROTTLED';

  const steps = [
    {
      id: 'normal',
      title: 'Normal State',
      desc: 'Baseline Workload Active',
      completed: true,
      active: !hasAnomaly && !hasMitigation,
      icon: '✓',
    },
    {
      id: 'abnormality',
      title: 'Resource Spike',
      desc: 'CPU/Energy Deviation',
      completed: hasAnomaly || hasMitigation,
      active: hasAnomaly && !isConfirmed,
      icon: '⚡',
    },
    {
      id: 'detected',
      title: 'AI Anomaly',
      desc: 'Isolation Forest Flagged',
      completed: hasAnomaly || hasMitigation,
      active: hasAnomaly && !isConfirmed,
      icon: '⚠',
    },
    {
      id: 'confirmed',
      title: 'Confirmed Attack',
      desc: '>=3 Consecutive Windows',
      completed: isConfirmed || hasMitigation,
      active: isConfirmed && !hasMitigation,
      icon: '●',
    },
    {
      id: 'throttled',
      title: 'Throttling',
      desc: 'Resource Limits Patched',
      completed: hasMitigation,
      active: isThrottled && !isDeleted,
      icon: '⚙',
    },
    {
      id: 'terminated',
      title: 'Termination',
      desc: 'Abuse Pod Evicted',
      completed: isDeleted,
      active: isDeleted,
      icon: '✕',
    },
    {
      id: 'recovery',
      title: 'Recovery',
      desc: 'Normal Pod Replacement',
      completed: isDeleted,
      active: false,
      icon: '🛡',
    }
  ];

  const stepsHtml = steps.map(step => {
    let stateClass = '';
    if (step.active) stateClass = 'active';
    else if (step.completed) stateClass = 'completed';

    return `
      <div class="timeline-step ${stateClass}">
        <div class="timeline-dot">${step.icon}</div>
        <div class="timeline-step-title">${step.title}</div>
        <div class="timeline-step-desc">${step.desc}</div>
      </div>
    `;
  }).join('');

  return `
    <div class="card" style="overflow-x: auto;">
      <div class="card-header">
        <div>
          <div class="card-title">Attack Response Lifecycle Timeline</div>
          <div class="card-subtitle">Real-time state tracking from anomaly confirmation to automated mitigation</div>
        </div>
      </div>
      <div class="timeline-container">
        <div class="timeline-line"></div>
        ${stepsHtml}
      </div>
    </div>
  `;
}
