from flask import Flask, jsonify, send_file
from flask_cors import CORS
import io
import os

import config


def _reset_experiment_files() -> None:
    targets = {
        config.RAW_DATA_PATH: [
            "timestamp", "pod_name", "namespace", "cpu_cores", "memory_bytes", "memory_mb",
            "network_rx_bytes_per_sec", "network_tx_bytes_per_sec", "energy_joules", "energy_source", "is_attack_pod",
        ],
        config.TRAINING_DATA_PATH: ["model", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8"],
        config.DETECTION_LOG_PATH: ["timestamp", "pod", "cpu", "mem_mb", "energy", "e_cpu", "ea", "basic", "score", "consecutive"],
        config.EVALUATION_LOG_PATH: [
            "timestamp", "pod_name", "prediction_ea", "score_ea", "prediction_basic", "score_basic",
            "consecutive_count", "confirmed_attack", "true_label", "avg_cpu", "avg_memory_mb", "avg_energy",
            "energy_cpu_ratio", "cpu_variance", "memory_variance", "energy_variance", "avg_network", "avg_network_variance",
        ],
        config.MITIGATION_LOG_PATH: ["timestamp", "pod_name", "action", "status", "score"],
    }
    for path, header in targets.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(",".join(header) + "\n")


def create_app(state_manager, model_manager, evaluator):
    app = Flask(__name__)
    CORS(app)

    @app.get("/")
    def root():
        return DASHBOARD_HTML

    @app.get("/api/status")
    def api_status():
        return jsonify(state_manager.get_dashboard_json())

    @app.get("/api/pods")
    def api_pods():
        return jsonify(state_manager.get_dashboard_json()["pods"])

    @app.get("/api/detections")
    def api_detections():
        return jsonify(state_manager.get_dashboard_json()["detection_history"])

    @app.get("/api/mitigations")
    def api_mitigations():
        return jsonify(state_manager.get_dashboard_json()["mitigation_history"])

    @app.get("/api/comparison")
    def api_comparison():
        return jsonify(state_manager.get_dashboard_json()["comparison_stats"])

    @app.get("/api/metrics/history")
    def api_metrics_history():
        return jsonify(state_manager.get_dashboard_json()["metrics_timeline"])

    @app.post("/api/training/start")
    def api_training_start():
        _reset_experiment_files()
        state_manager.reset_runtime_stats()
        model_manager.start_baseline_collection()
        state_manager.set_state(config.STATE_COLLECTING)
        return jsonify({"status": "ok"})

    @app.get("/api/evaluation")
    def api_evaluation():
        try:
            data = evaluator.calculate_metrics(config.EVALUATION_LOG_PATH)
            return jsonify(data)
        except Exception as exc:
            return jsonify({"status": "error", "message": str(exc)}), 400

    @app.get("/api/export/dataset")
    def api_export_dataset():
        if not os.path.exists(config.RAW_DATA_PATH):
            return jsonify({"status": "error", "message": "Raw dataset not available yet"}), 404
        with open(config.RAW_DATA_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        mem = io.BytesIO(content.encode("utf-8"))
        return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="raw_metrics.csv")

    return app


DASHBOARD_HTML = """<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <title>AI-Based Energy-Aware Anomaly Detection</title>
  <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
  <style>
    body { background:#111; color:#eee; font-family:Arial; margin:16px; }
    .row { background:#1d1d1d; padding:10px; border-radius:8px; margin-bottom:12px; }
    .cards { display:grid; grid-template-columns:repeat(5,1fr); gap:8px; }
    .card { background:#242424; padding:8px; border-radius:6px; }
    .twocol { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
    table { width:100%; border-collapse:collapse; }
    th,td { padding:6px; border-bottom:1px solid #333; font-size:12px; }
    .green { background:#143d14; }
    .yellow { background:#665500; }
    .red { background:#5f1111; }
    button { padding:8px 12px; background:#2ecc71; border:none; border-radius:6px; cursor:pointer; color:#000; font-weight:bold; }
  </style>
</head>
<body>
  <h2>AI-Based Energy-Aware Anomaly Detection</h2>
  <div id='meta'></div>

  <div class='row cards'>
    <div class='card'>State<div id='state'></div></div>
    <div class='card'>Pods Monitored<div id='podsMon'></div></div>
    <div class='card'>Anomalies Today<div id='anom'></div></div>
    <div class='card'>Mitigations<div id='mit'></div></div>
    <div class='card'>Training<div id='train'></div></div>
  </div>

  <div class='row'>
    <button onclick='startTraining()'>▶ Start Baseline Training</button>
    <div id='trainText'>Collecting normal behavior: X/30 windows</div>
    <div style='color:#ffcc66'>⚠️ WARNING: Do NOT deploy attack workloads yet!</div>
  </div>

  <div class='row'>
    <h3>Live Pod Table</h3>
    <table>
      <thead><tr><th>Pod Name</th><th>CPU</th><th>Memory</th><th>Energy(J)</th><th>Net(KB/s)</th><th>E/CPU Ratio</th><th>EA Status</th><th>Basic Status</th><th>Score</th><th>Action</th></tr></thead>
      <tbody id='pods'></tbody>
    </table>
  </div>

  <div class='row'>
    <h3>Energy-Aware IF vs Basic IF - Live Comparison</h3>
    <div class='twocol'>
      <div><h4>Energy-Aware (8 features with energy)</h4><div id='ea'></div></div>
      <div><h4>Basic IF (6 features, no energy)</h4><div id='basic'></div></div>
    </div>
    <small>Energy-aware model uses energy-to-CPU ratio as key discriminating feature</small>
  </div>

  <div class='row twocol'>
    <canvas id='cpu'></canvas>
    <canvas id='energy'></canvas>
    <canvas id='score'></canvas>
    <canvas id='network'></canvas>
  </div>

  <div class='row'>
    <h3>Detection Log</h3>
    <table>
      <thead><tr><th>Timestamp</th><th>Pod</th><th>CPU</th><th>Mem</th><th>Energy</th><th>E/CPU</th><th>EA Result</th><th>Basic Result</th><th>Score</th><th>Consecutive</th></tr></thead>
      <tbody id='det'></tbody>
    </table>
  </div>

  <div class='row'>
    <h3>Mitigation Log</h3>
    <table>
      <thead><tr><th>Timestamp</th><th>Pod</th><th>Action</th><th>Status</th></tr></thead>
      <tbody id='mitTable'></tbody>
    </table>
  </div>

  <div class='row'>
    <button onclick='calcMetrics()'>📊 Calculate IEEE Metrics</button>
    <pre id='metrics'></pre>
  </div>

<script>
const c1 = new Chart(document.getElementById('cpu'), {type:'line',data:{labels:[],datasets:[{label:'CPU Usage per pod',data:[],borderColor:'#2ad',fill:false}]},options:{animation:false}});
const c2 = new Chart(document.getElementById('energy'), {type:'line',data:{labels:[],datasets:[{label:'Energy Consumption per pod',data:[],borderColor:'#f9c74f',fill:false}]},options:{animation:false}});
const c3 = new Chart(document.getElementById('score'), {type:'line',data:{labels:[],datasets:[{label:'Anomaly Score',data:[],borderColor:'#f94144',fill:false}]},options:{animation:false}});
const c4 = new Chart(document.getElementById('network'), {type:'line',data:{labels:[],datasets:[{label:'Network Traffic',data:[],borderColor:'#90be6d',fill:false}]},options:{animation:false}});

function rowColor(d){
  if (d.consecutive >= 3) return 'red';
  if (d.consecutive >= 1) return 'yellow';
  return 'green';
}

async function refresh(){
  try {
    const resp = await fetch('/api/status');
    if (!resp.ok) throw new Error(`status API ${resp.status}`);
    const s = await resp.json();

    document.getElementById('state').textContent = s.current_state;
    document.getElementById('podsMon').textContent = Object.keys(s.pods).length;
    document.getElementById('anom').textContent = s.comparison_stats.ea_detections;
    document.getElementById('mit').textContent = s.mitigation_history.length;
    document.getElementById('train').textContent = `${s.training_progress.current}/${s.training_progress.total}`;
    document.getElementById('meta').textContent = `${s.kepler_active ? '⚡ Real Energy' : '📊 Estimated Energy'} | Uptime ${s.uptime}s`;

    const detByPod = {};
    s.detection_history.forEach(d => { if (!detByPod[d.pod_name]) detByPod[d.pod_name] = d; });

    const tbody = document.getElementById('pods');
    tbody.innerHTML = '';
    Object.entries(s.pods).forEach(([pod, p]) => {
      const d = detByPod[pod] || {prediction_ea:'NORMAL',prediction_basic:'NORMAL',score_ea:0,consecutive:0,energy_cpu_ratio:0};
      const tr = document.createElement('tr');
      tr.className = rowColor(d);
      tr.innerHTML = `<td>${pod}</td><td>${p.cpu.toFixed(4)}</td><td>${p.memory_mb.toFixed(1)}</td><td>${p.energy_joules.toFixed(4)}</td><td>${p.network_kbps.toFixed(2)}</td><td>${(d.energy_cpu_ratio||0).toFixed(4)}</td><td>${d.prediction_ea}</td><td>${d.prediction_basic}</td><td>${d.score_ea.toFixed(4)}</td><td>${d.consecutive>=3?'CONFIRMED':(d.consecutive>=1?'ANOMALY':'-')}</td>`;
      tbody.appendChild(tr);
    });

    document.getElementById('ea').innerHTML = `Detections: ${s.comparison_stats.ea_detections}<br>False Positives: ${s.comparison_stats.ea_false_positives}<br>Confirmed Attacks: ${s.comparison_stats.ea_confirmed}`;
    document.getElementById('basic').innerHTML = `Detections: ${s.comparison_stats.basic_detections}<br>False Positives: ${s.comparison_stats.basic_false_positives}<br>Confirmed Attacks: ${s.comparison_stats.basic_confirmed}`;

    const dtab = document.getElementById('det');
    dtab.innerHTML = '';
    s.detection_history.forEach(d => {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${new Date(d.timestamp*1000).toLocaleTimeString()}</td><td>${d.pod_name}</td><td>${(d.avg_cpu||0).toFixed(4)}</td><td>${(d.avg_memory_mb||0).toFixed(1)}</td><td>${(d.avg_energy||0).toFixed(4)}</td><td>${(d.energy_cpu_ratio||0).toFixed(4)}</td><td>${d.prediction_ea}</td><td>${d.prediction_basic}</td><td>${(d.score_ea||0).toFixed(4)}</td><td>${d.consecutive}</td>`;
      dtab.appendChild(tr);
    });

    const mtab = document.getElementById('mitTable');
    mtab.innerHTML = '';
    s.mitigation_history.forEach(m => {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${new Date(m.timestamp*1000).toLocaleTimeString()}</td><td>${m.pod_name}</td><td>${m.action}</td><td>${m.status}</td>`;
      mtab.appendChild(tr);
    });

    const pod = Object.keys(s.metrics_timeline)[0];
    if (pod){
      const arr = s.metrics_timeline[pod];
      const labels = arr.map(x => new Date(x.timestamp*1000).toLocaleTimeString());
      c1.data.labels = labels; c1.data.datasets[0].data = arr.map(x => x.cpu); c1.update();
      c2.data.labels = labels; c2.data.datasets[0].data = arr.map(x => x.energy); c2.update();
      c4.data.labels = labels; c4.data.datasets[0].data = arr.map(x => x.network); c4.update();
    }
    const rev = s.detection_history.slice().reverse();
    c3.data.labels = rev.map(x => new Date(x.timestamp*1000).toLocaleTimeString());
    c3.data.datasets[0].data = rev.map(x => x.score_ea || 0);
    c3.update();
  } catch (err) {
    document.getElementById('meta').textContent = `⚠️ Connection issue: ${err.message}`;
  }
}

async function startTraining(){
  try {
    const resp = await fetch('/api/training/start', {method:'POST'});
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.message || `training start failed (${resp.status})`);
    document.getElementById('trainText').textContent = 'Collecting normal behavior: active';
  } catch (err) {
    document.getElementById('trainText').textContent = `Training start failed: ${err.message}`;
  }
}

async function calcMetrics(){
  const out = document.getElementById('metrics');
  try {
    const resp = await fetch('/api/evaluation');
    const data = await resp.json();
    if (!resp.ok || data.status === 'error') {
      out.textContent = `Evaluation unavailable: ${data.message || `HTTP ${resp.status}`}`;
      return;
    }
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    out.textContent = `Evaluation request failed: ${err.message}`;
  }
}

setInterval(refresh, 5000);
refresh();
</script>
</body>
</html>
"""
