// Modern AI Disaster Response Simulation Dashboard
// Enhanced with professional UI/UX and advanced charting

const api = {
  async getState() { return fetch('/api/state').then(r=>r.json()); },
  async telemetry() { return fetch('/api/telemetry').then(r=>r.json()); },
  async reset() { return fetch('/api/reset', {method:'POST'}).then(r=>r.json()); },
  async step() { return fetch('/api/step', {method:'POST'}).then(r=>r.json()); },
  async move(i,j) { return fetch('/api/move',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({i,j})}).then(r=>r.json()); },
  async recommend() { return fetch('/api/recommend_path').then(r=>r.json()); },
  async risk(i,j) { return fetch(`/api/risk?i=${i}&j=${j}`).then(r=>r.json()); },
  async collect() { return fetch('/api/collect', {method:'POST'}).then(r=>r.json()); },
  async rescue() { return fetch('/api/rescue', {method:'POST'}).then(r=>r.json()); },
  async summary() { return fetch('/api/summary').then(r=>r.json()); },
  async legend() { return fetch('/api/legend').then(r=>r.json()); },
};

// DOM Elements
const gridCanvas = document.getElementById('grid');
const ctx = gridCanvas.getContext('2d');
const statusEl = document.getElementById('status');
const simulationTimeEl = document.getElementById('simulation-time');
const metricsGridEl = document.getElementById('metrics-grid');
const logEl = document.getElementById('log');
const statsEl = document.getElementById('stats');

// State Variables
let state = null;
let cellSize = 24;
let autoTimer = null;
let zoomLevel = 1;
let lastRecommendedPath = [];
let showSurvival = false;

// Image Assets
const rescuerImg = new Image(); rescuerImg.src = '/static/rescuer.svg';
const victimImg = new Image(); victimImg.src = '/static/victim.svg';

// Chart Instances
let riskChart, victimsChart, efficiencyChart;

// Initialize Dashboard
function initDashboard() {
  initCharts();
  setupEventListeners();
  setupTabNavigation();
  createMetricsCards();
  addTooltips();
}

// Initialize Enhanced Charts
function initCharts() {
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 750,
      easing: 'easeInOutQuart'
    },
    plugins: {
      legend: {
        labels: {
          color: '#f8fafc',
          font: { family: 'Inter', size: 12 }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(30, 41, 59, 0.95)',
        titleColor: '#f8fafc',
        bodyColor: '#cbd5e1',
        borderColor: '#475569',
        borderWidth: 1,
        cornerRadius: 8
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(148, 163, 184, 0.1)' },
        ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
      },
      y: {
        grid: { color: 'rgba(148, 163, 184, 0.1)' },
        ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
      }
    }
  };

  // Risk Trend Chart
  riskChart = new Chart(document.getElementById('riskChartCanvas'), {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'Total Risk Level',
        data: [],
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#ef4444',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4
      }]
    },
    options: {
      ...chartOptions,
      plugins: {
        ...chartOptions.plugins,
        title: {
          display: true,
          text: 'Risk Evolution Over Time',
          color: '#f8fafc',
          font: { family: 'Inter', size: 14, weight: '600' }
        }
      }
    }
  });

  // Victims & Resources Chart
  victimsChart = new Chart(document.getElementById('victimsChartCanvas'), {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Victims Saved',
          data: [],
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          borderWidth: 3,
          fill: false,
          tension: 0.4,
          pointBackgroundColor: '#10b981',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: 4
        },
        {
          label: 'Victims Remaining',
          data: [],
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          borderWidth: 3,
          fill: false,
          tension: 0.4,
          pointBackgroundColor: '#f59e0b',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: 4
        },
        {
          label: 'Resources Used',
          data: [],
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderWidth: 3,
          fill: false,
          tension: 0.4,
          pointBackgroundColor: '#3b82f6',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: 4
        }
      ]
    },
    options: {
      ...chartOptions,
      plugins: {
        ...chartOptions.plugins,
        title: {
          display: true,
          text: 'Rescue Progress & Resource Usage',
          color: '#f8fafc',
          font: { family: 'Inter', size: 14, weight: '600' }
        }
      }
    }
  });

  // Efficiency Chart
  efficiencyChart = new Chart(document.getElementById('efficiencyChartCanvas'), {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'Efficiency Score',
        data: [],
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#8b5cf6',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4
      }]
    },
    options: {
      ...chartOptions,
      plugins: {
        ...chartOptions.plugins,
        title: {
          display: true,
          text: 'Performance Efficiency Over Time',
          color: '#f8fafc',
          font: { family: 'Inter', size: 14, weight: '600' }
        }
      }
    }
  });
}

// Create Metrics Cards
function createMetricsCards() {
  const metrics = [
    { id: 'victims-saved', label: 'Victims Saved', icon: '🆘', color: '#10b981' },
    { id: 'victims-remaining', label: 'Victims Remaining', icon: '⚠️', color: '#f59e0b' },
    { id: 'time-steps', label: 'Time Steps', icon: '⏱️', color: '#3b82f6' },
    { id: 'total-risk', label: 'Total Risk', icon: '🔥', color: '#ef4444' },
    { id: 'efficiency', label: 'Efficiency', icon: '📊', color: '#8b5cf6' },
    { id: 'resources-used', label: 'Resources Used', icon: '📦', color: '#06b6d4' }
  ];

  metricsGridEl.innerHTML = metrics.map(metric => `
    <div class="metric-card" id="${metric.id}-card">
      <div class="metric-icon" style="color: ${metric.color}">${metric.icon}</div>
      <div class="metric-value" id="${metric.id}-value">0</div>
      <div class="metric-label">${metric.label}</div>
      <div class="metric-progress">
        <div class="metric-progress-bar" id="${metric.id}-progress" style="width: 0%"></div>
      </div>
    </div>
  `).join('');
}

// Update Metrics Display
function updateMetrics(stats) {
  const metrics = [
    { id: 'victims-saved', value: stats.victims_saved || 0, max: stats.initial_victims || 1 },
    { id: 'victims-remaining', value: Math.max(0, (stats.initial_victims || 0) - (stats.victims_saved || 0)), max: stats.initial_victims || 1 },
    { id: 'time-steps', value: stats.time_steps || 0, max: 100 },
    { id: 'total-risk', value: Math.round((stats.total_risk || 0) * 10) / 10, max: 500 },
    { id: 'efficiency', value: Math.round((stats.efficiency_score || 0) * 1000) / 1000, max: 1 },
    { id: 'resources-used', value: stats.resources_used || 0, max: 20 }
  ];

  metrics.forEach(metric => {
    const valueEl = document.getElementById(`${metric.id}-value`);
    const progressEl = document.getElementById(`${metric.id}-progress`);
    
    if (valueEl) valueEl.textContent = metric.value;
    if (progressEl) {
      const percentage = Math.min((metric.value / metric.max) * 100, 100);
      progressEl.style.width = `${percentage}%`;
    }
  });

  // Update status chip
  if (stats.victims_saved === stats.initial_victims) {
    statusEl.textContent = 'Complete';
    statusEl.style.background = 'var(--success-gradient)';
  } else if (autoTimer) {
    statusEl.textContent = 'Running';
    statusEl.style.background = 'var(--warning-gradient)';
  } else {
    statusEl.textContent = 'Ready';
    statusEl.style.background = 'var(--accent-gradient)';
  }
}

// Update Charts with Enhanced Data
function updateCharts(telemetry) {
  if (!telemetry) return;

  const labels = telemetry.time_steps_history || [];
  
  // Update Risk Chart
  if (riskChart) {
    riskChart.data.labels = labels;
    riskChart.data.datasets[0].data = telemetry.risk_history || [];
    riskChart.update('none');
  }

  // Update Victims Chart
  if (victimsChart) {
    victimsChart.data.labels = labels;
    victimsChart.data.datasets[0].data = telemetry.victims_saved_history || [];
    victimsChart.data.datasets[1].data = telemetry.remaining_history || [];
    victimsChart.data.datasets[2].data = telemetry.resources_used_history || [];
    victimsChart.update('none');
  }

  // Update Efficiency Chart
  if (efficiencyChart && telemetry.efficiency_history) {
    efficiencyChart.data.labels = labels;
    efficiencyChart.data.datasets[0].data = telemetry.efficiency_history;
    efficiencyChart.update('none');
  }
}

// Enhanced Grid Drawing
function draw() {
  if (!state) return;
  
  const size = state.grid_size;
  cellSize = Math.floor(Math.min(720/size, 720/size));
  
  ctx.clearRect(0, 0, 720, 720);
  ctx.save();
  ctx.scale(zoomLevel, zoomLevel);

  // Draw terrain
  for (let i = 0; i < size; i++) {
    for (let j = 0; j < size; j++) {
      const x = j * cellSize, y = i * cellSize;
      ctx.fillStyle = colorForTerrain(state.grid[i][j]);
      ctx.fillRect(x, y, cellSize, cellSize);
    }
  }

  // Draw hazards with enhanced effects
  for (const [i, j, val] of state.hazards) {
    const x = j * cellSize, y = i * cellSize;
    const radius = Math.max(cellSize * 0.8, 12);
    
    // Create animated hazard effect
    const time = Date.now() * 0.003;
    const pulse = 0.8 + 0.2 * Math.sin(time + i + j);
    
    const gradient = ctx.createRadialGradient(
      x + cellSize/2, y + cellSize/2, 0,
      x + cellSize/2, y + cellSize/2, radius
    );
    
    gradient.addColorStop(0, `rgba(239, 68, 68, ${Math.min(0.9, Math.max(0.3, val * pulse))})`);
    gradient.addColorStop(0.7, `rgba(239, 68, 68, ${Math.min(0.6, Math.max(0.2, val * pulse * 0.7))})`);
    gradient.addColorStop(1, 'rgba(239, 68, 68, 0)');
    
    ctx.fillStyle = gradient;
    ctx.fillRect(x, y, cellSize, cellSize);
  }

  // Draw resources
  ctx.fillStyle = '#10b981';
  for (const [i, j] of state.resources) {
    const x = j * cellSize + cellSize * 0.2, y = i * cellSize + cellSize * 0.2;
    const size = cellSize * 0.6;
    
    // Draw resource with shadow
    ctx.shadowColor = 'rgba(16, 185, 129, 0.5)';
    ctx.shadowBlur = 8;
    ctx.fillRect(x, y, size, size);
    ctx.shadowBlur = 0;
  }

  // Draw victims with enhanced styling
  for (const [i, j] of state.victims) {
    const vx = j * cellSize + cellSize * 0.1, vy = i * cellSize + cellSize * 0.05;
    try {
      ctx.drawImage(victimImg, vx, vy, cellSize * 0.8, cellSize * 0.9);
      
      // Add survival probability overlay
      if (showSurvival && state.survival_probabilities) {
        const prob = state.survival_probabilities.find(p => p[0] === i && p[1] === j);
        if (prob) {
          const percentage = Math.round(prob[2] * 100);
          ctx.fillStyle = '#ffffff';
          ctx.font = `${Math.max(10, Math.floor(cellSize * 0.2))}px Inter`;
          ctx.textAlign = 'center';
          ctx.fillText(`${percentage}%`, j * cellSize + cellSize/2, i * cellSize + cellSize * 0.8);
        }
      }
    } catch (e) {
      // Fallback to circle if image fails
      ctx.fillStyle = '#f59e0b';
      ctx.beginPath();
      ctx.arc(j * cellSize + cellSize/2, i * cellSize + cellSize/2, cellSize * 0.35, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // Draw rescue team with enhanced styling
  const [ti, tj] = state.rescue_team.position;
  const cx = tj * cellSize + cellSize * 0.1, cy = ti * cellSize + cellSize * 0.1;
  try {
    ctx.drawImage(rescuerImg, cx, cy, cellSize * 0.8, cellSize * 0.8);
    
    // Add team indicator glow
    ctx.shadowColor = '#3b82f6';
    ctx.shadowBlur = 15;
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.strokeRect(cx - 2, cy - 2, cellSize * 0.8 + 4, cellSize * 0.8 + 4);
    ctx.shadowBlur = 0;
  } catch (e) {
    // Fallback to rectangle if image fails
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(cx, cy, cellSize * 0.8, cellSize * 0.8);
  }

  // Draw recommended path with enhanced styling
  if (lastRecommendedPath && lastRecommendedPath.length > 1) {
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.shadowColor = '#10b981';
    ctx.shadowBlur = 10;
    
    ctx.beginPath();
    for (let k = 0; k < lastRecommendedPath.length; k++) {
      const [i, j] = lastRecommendedPath[k];
      const x = j * cellSize + cellSize/2, y = i * cellSize + cellSize/2;
      if (k === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.shadowBlur = 0;
  }

  ctx.restore();
}

// Terrain Color Mapping
function colorForTerrain(t) {
  const terrainColors = {
    'U': '#64748b', // Urban
    'R': '#0ea5e9', // Road
    'S': '#94a3b8', // Structure
    'G': '#22c55e', // Green
    'W': '#1d4ed8'  // Water
  };
  return terrainColors[t] || '#0f172a';
}

// Setup Event Listeners
function setupEventListeners() {
  // Control buttons
  document.getElementById('btnStep').onclick = () => { stopAuto(); autoStepOnce(); };
  document.getElementById('btnAuto').onclick = startAuto;
  document.getElementById('btnStop').onclick = stopAuto;
  document.getElementById('btnRecommend').onclick = recommendPath;
  document.getElementById('btnCollect').onclick = collectResource;
  document.getElementById('btnRescue').onclick = rescueVictim;
  document.getElementById('btnToggleSurvival').onclick = toggleSurvival;
  document.getElementById('btnReset').onclick = resetSimulation;
  
  // Grid controls
  document.getElementById('btnZoomIn').onclick = () => { zoomLevel = Math.min(zoomLevel * 1.2, 3); draw(); };
  document.getElementById('btnZoomOut').onclick = () => { zoomLevel = Math.max(zoomLevel / 1.2, 0.5); draw(); };
  
  // Grid click for movement
  gridCanvas.addEventListener('click', handleGridClick);
  
  // Add hover effects
  addHoverEffects();
}

// Setup Tab Navigation
function setupTabNavigation() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const chartContainers = document.querySelectorAll('.chart-container');
  
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetChart = btn.dataset.chart;
      
      // Update active tab
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      // Show target chart
      chartContainers.forEach(container => {
        container.classList.remove('active');
        if (container.id === `${targetChart}Chart`) {
          container.classList.add('active');
        }
      });
    });
  });
}

// Add Tooltips
function addTooltips() {
  const tooltipEl = document.getElementById('tooltip');
  
  document.querySelectorAll('[title]').forEach(element => {
    element.addEventListener('mouseenter', (e) => {
      const rect = element.getBoundingClientRect();
      tooltipEl.textContent = element.title;
      tooltipEl.style.left = rect.left + rect.width/2 + 'px';
      tooltipEl.style.top = rect.top - 40 + 'px';
      tooltipEl.classList.add('active');
    });
    
    element.addEventListener('mouseleave', () => {
      tooltipEl.classList.remove('active');
    });
  });
}

// Add Hover Effects
function addHoverEffects() {
  document.querySelectorAll('.btn, .control-btn').forEach(btn => {
    btn.addEventListener('mouseenter', () => {
      btn.style.transform = 'translateY(-2px)';
    });
    
    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'translateY(0)';
    });
  });
}

// Handle Grid Click
async function handleGridClick(e) {
  if (!state) return;
  
  const rect = gridCanvas.getBoundingClientRect();
  const x = (e.clientX - rect.left) / zoomLevel;
  const y = (e.clientY - rect.top) / zoomLevel;
  const j = Math.floor(x / cellSize);
  const i = Math.floor(y / cellSize);
  
  if (i < 0 || j < 0 || i >= state.grid_size || j >= state.grid_size) {
    logMessage(`Out of bounds (${i},${j})`, 'warning');
    return;
  }
  
  const res = await safe(() => api.move(i, j), 'move');
  if (res && res.ok) {
    logMessage(`Moved to (${i},${j})`, 'success');
    await refresh();
  } else {
    logMessage(`Invalid move (${i},${j})`, 'error');
  }
}

// Simulation Functions
async function autoStepOnce() {
  const data = await safe(() => api.step(), 'step');
  if (!data) return false;
  
  state = data.state;
  updateMetrics(data.stats);
  updateCharts(data.telemetry);
  simulationTimeEl.textContent = `Step ${state.time_step}${data.done ? ' (Complete)' : ''}`;
  draw();
  
  if (data.done) {
    showResultsModal(data);
  }
  
  return !data.done;
}

async function startAuto() {
  if (autoTimer) return;
  logMessage('Auto-simulation started', 'info');
  
  const tick = async () => {
    const cont = await autoStepOnce();
    if (cont) {
      autoTimer = setTimeout(tick, 200);
    } else {
      autoTimer = null;
      logMessage('Auto-simulation completed', 'success');
    }
  };
  tick();
}

function stopAuto() {
  if (autoTimer) {
    clearTimeout(autoTimer);
    autoTimer = null;
    logMessage('Auto-simulation stopped', 'warning');
  }
}

async function recommendPath() {
  const data = await safe(() => api.recommend(), 'recommend');
  if (!data) return;
  
  lastRecommendedPath = data.path || [];
  draw();
  
  logMessage(`AI Path: ${data.length} steps, Risk: ${data.risk?.toFixed(2) || 'N/A'}, Expected Survival: ${data.expected_survival ? Math.round(data.expected_survival * 100) + '%' : 'N/A'}`, 'info');
}

async function collectResource() {
  const res = await safe(() => api.collect(), 'collect');
  if (!res) return;
  
  const message = res.ok ? 'Resource collected successfully' : 'No resources at this location';
  logMessage(message, res.ok ? 'success' : 'warning');
  await refresh();
}

async function rescueVictim() {
  const res = await safe(() => api.rescue(), 'rescue');
  if (!res) return;
  
  const message = res.ok ? 'Victim rescued successfully!' : 'Rescue failed - no victim here';
  logMessage(message, res.ok ? 'success' : 'error');
  await refresh();
}

function toggleSurvival() {
  showSurvival = !showSurvival;
  const btn = document.getElementById('btnToggleSurvival');
  btn.classList.toggle('active');
  btn.textContent = showSurvival ? 'Hide Survival%' : 'Show Survival%';
  draw();
}

async function resetSimulation() {
  stopAuto();
  const res = await safe(() => api.reset(), 'reset');
  if (res) {
    logMessage('Simulation reset', 'info');
    lastRecommendedPath = [];
    await refresh();
  }
}

// Utility Functions
async function safe(fn, label) {
  try {
    return await fn();
  } catch(e) {
    logMessage(`${label} failed: ${e}`, 'error');
    return null;
  }
}

function logMessage(message, type = 'info') {
  const timestamp = new Date().toLocaleTimeString();
  const typeIcon = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' }[type] || 'ℹ️';
  logEl.textContent += `[${timestamp}] ${typeIcon} ${message}\n`;
  logEl.scrollTop = logEl.scrollHeight;
}

// Refresh Function
async function refresh() {
  const data = await safe(() => api.getState(), 'getState');
  if (!data) return;
  
  state = data.state;
  updateMetrics(data.stats);
  updateCharts(data.telemetry);
  simulationTimeEl.textContent = `Step ${state.time_step}`;
  draw();
  
  // Show top survival probabilities
  if (state.survival_probabilities && state.survival_probabilities.length) {
    const top = [...state.survival_probabilities]
      .sort((a, b) => b[2] - a[2])
      .slice(0, 3)
      .map(([i, j, p]) => `(${i},${j}): ${Math.round(p * 100)}%`)
      .join(', ');
    logMessage(`Top survival probabilities: ${top}`, 'info');
  }
}

// Modal Functions
function showResultsModal(data) {
  const modal = document.getElementById('resultsModal');
  const modalBody = document.getElementById('modalBody');
  
  const summary = data.summary || {};
  modalBody.innerHTML = `
    <div class="results-summary">
      <div class="result-item">
        <span class="result-label">Victims Saved:</span>
        <span class="result-value">${summary.victims_saved || 0}/${summary.initial_victims || 0}</span>
      </div>
      <div class="result-item">
        <span class="result-label">Efficiency Score:</span>
        <span class="result-value">${(summary.efficiency_score || 0).toFixed(3)}</span>
      </div>
      <div class="result-item">
        <span class="result-label">Time Steps:</span>
        <span class="result-value">${summary.time_steps || 0}</span>
      </div>
      <div class="result-item">
        <span class="result-label">Resources Used:</span>
        <span class="result-value">${summary.resources_used || 0}</span>
      </div>
    </div>
  `;
  
  modal.classList.add('active');
}

function closeResultsModal() {
  document.getElementById('resultsModal').classList.remove('active');
}

// Debug Panel Toggle
function toggleDebug() {
  const content = document.getElementById('debugContent');
  const icon = document.querySelector('.toggle-icon');
  
  content.classList.toggle('expanded');
  icon.style.transform = content.classList.contains('expanded') ? 'rotate(180deg)' : 'rotate(0deg)';
}

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
  initDashboard();
  
  // Load initial data
  (async () => {
    const legend = await safe(() => api.legend(), 'legend');
    if (legend) logMessage('System initialized successfully', 'success');
    await refresh();
  })();
});
