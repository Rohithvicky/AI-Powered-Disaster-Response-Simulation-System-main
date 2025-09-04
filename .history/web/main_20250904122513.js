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

const gridCanvas = document.getElementById('grid');
const ctx = gridCanvas.getContext('2d');
const statusEl = document.getElementById('status');
const statsEl = document.getElementById('stats');
const logEl = document.getElementById('log');
const badgesEl = document.getElementById('badges');

let state = null;
let cellSize = 24;
let autoTimer = null;
const rescuerImg = new Image(); rescuerImg.src = '/static/rescuer.svg';
const victimImg = new Image(); victimImg.src = '/static/victim.svg';
rescuerImg.decoding = 'async'; rescuerImg.loading = 'eager';
victimImg.decoding = 'async'; victimImg.loading = 'eager';

// Inline SVG icons for overlays (warning + terrain context)
function createIcon(svg){ const img = new Image(); img.src = 'data:image/svg+xml;utf8,'+encodeURIComponent(svg); img.decoding='async'; img.loading='eager'; return img; }
const iconWarning = createIcon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><path d="M32 8l26 48H6L32 8z" fill="#ef4444"/><path d="M32 22v18" stroke="#fff" stroke-width="6" stroke-linecap="round"/><circle cx="32" cy="48" r="3.5" fill="#fff"/></svg>');
const iconUrban = createIcon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect x="8" y="30" width="16" height="26" fill="#1f2937"/><rect x="28" y="22" width="16" height="34" fill="#334155"/><rect x="48" y="28" width="8" height="28" fill="#475569"/></svg>');
const iconRoad = createIcon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect x="28" y="6" width="8" height="52" rx="2" fill="#475569"/><rect x="31" y="10" width="2" height="6" fill="#e5e7eb"/><rect x="31" y="22" width="2" height="6" fill="#e5e7eb"/><rect x="31" y="34" width="2" height="6" fill="#e5e7eb"/><rect x="31" y="46" width="2" height="6" fill="#e5e7eb"/></svg>');
const iconSand = createIcon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><path d="M6 48l14-16 10 12 8-10 20 14H6z" fill="#eab308"/></svg>');
const iconGrass = createIcon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><path d="M10 50c10-8 12-8 22 0 10-8 12-8 22 0" stroke="#10b981" stroke-width="6" fill="none" stroke-linecap="round"/></svg>');
const iconWater = createIcon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><path d="M32 10c10 14 14 20 14 26a14 14 0 1 1-28 0c0-6 4-12 14-26z" fill="#38bdf8"/></svg>');
let lastRecommendedPath = [];
let showSurvival = false;

// Charts
let riskChart, vrChart;

function colorForTerrain(t) {
  // Muted, realistic palette
  switch(t){
    case 'U': return '#8b95a5'; // urban
    case 'R': return '#4aa3df'; // road/rubble
    case 'S': return '#d3d8df'; // sand/soil
    case 'G': return '#2aa06a'; // grass/green
    case 'W': return '#1f6fd1'; // water
    default: return '#0b1220';
  }
}

function draw(){
  if (!state) return;
  const size = state.grid_size;
  cellSize = Math.floor(Math.min(720/size, 720/size));
  ctx.clearRect(0,0,720,720);
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = 'high';

  // Terrain with subtle vertical gradient for depth
  for (let i=0;i<size;i++){
    for (let j=0;j<size;j++){
      const x = j*cellSize, y = i*cellSize;
      const base = colorForTerrain(state.grid[i][j]);
      const g = ctx.createLinearGradient(x, y, x, y+cellSize);
      g.addColorStop(0, base);
      g.addColorStop(1, 'rgba(0,0,0,0.06)');
      ctx.fillStyle = g;
      ctx.fillRect(x, y, cellSize, cellSize);

      // Terrain icon overlay (very subtle)
      const iconSize = Math.max(12, Math.floor(cellSize * 0.4));
      const ox = x + cellSize - iconSize - 2;
      const oy = y + 2;
      ctx.globalAlpha = 0.18;
      const t = state.grid[i][j];
      let icon = null;
      if (t==='U') icon = iconUrban; else if (t==='R') icon = iconRoad; else if (t==='S') icon = iconSand; else if (t==='G') icon = iconGrass; else if (t==='W') icon = iconWater;
      if (icon) { try { ctx.drawImage(icon, ox, oy, iconSize, iconSize); } catch {} }
      ctx.globalAlpha = 1;
    }
  }

  // Subtle gridlines for realism
  ctx.beginPath();
  ctx.lineWidth = 1;
  ctx.strokeStyle = 'rgba(148,163,184,0.08)';
  for (let i=0;i<=size;i++){
    const y = i*cellSize + 0.5; // crisp lines
    ctx.moveTo(0, y); ctx.lineTo(size*cellSize, y);
  }
  for (let j=0;j<=size;j++){
    const x = j*cellSize + 0.5;
    ctx.moveTo(x, 0); ctx.lineTo(x, size*cellSize);
  }
  ctx.stroke();

  // Hazards soft gradient with subtle pulse
  const t = (performance.now() % 2000) / 2000; // 0..1
  const pulse = 0.75 + 0.25 * Math.sin(t * Math.PI * 2);
  for (const [i,j,val] of state.hazards){
    const x = j*cellSize, y = i*cellSize;
    const r = Math.max(cellSize*0.9, 16);
    const centerX = x + cellSize/2, centerY = y + cellSize/2;
    const grd = ctx.createRadialGradient(centerX, centerY, r*0.15, centerX, centerY, r);
    const alpha = Math.min(.6, Math.max(.18, val * 0.9)) * pulse;
    grd.addColorStop(0, `rgba(239,68,68,${alpha})`);
    grd.addColorStop(1, 'rgba(239,68,68,0)');
    ctx.fillStyle = grd;
    ctx.fillRect(x, y, cellSize, cellSize);
  }

  // Resources
  ctx.fillStyle = '#10b981';
  for (const [i,j] of state.resources) {
    ctx.fillRect(j*cellSize+cellSize*0.22, i*cellSize+cellSize*0.22, cellSize*0.56, cellSize*0.56);
  }

  // Victims
  for (const [i,j] of state.victims){
    const vx = j*cellSize+cellSize*0.06, vy = i*cellSize+cellSize*0.02;
    try { ctx.drawImage(victimImg, vx, vy, cellSize*0.88, cellSize*0.96); } catch {}
    if (showSurvival && state.survival_probabilities){
      const rec = state.survival_probabilities.find(p=>p[0]===i && p[1]===j);
      if (rec){ const p = Math.round(rec[2]*100); ctx.fillStyle = '#ffffff'; ctx.font = `${Math.max(10, Math.floor(cellSize*0.25))}px Arial`; ctx.fillText(`${p}%`, j*cellSize+cellSize*0.35, i*cellSize+cellSize*0.8); }
    }
  }

  // Team
  const [ti,tj] = state.rescue_team.position;
  const cx = tj*cellSize+cellSize*0.06, cy = ti*cellSize+cellSize*0.06;
  try { ctx.drawImage(rescuerImg, cx, cy, cellSize*0.88, cellSize*0.88); } catch {}

  // Recommended path
  if (lastRecommendedPath && lastRecommendedPath.length>1){
    ctx.strokeStyle = '#22c55e'; ctx.lineWidth = 3; ctx.beginPath();
    for (let k=0;k<lastRecommendedPath.length;k++){
      const [i,j] = lastRecommendedPath[k]; const x = j*cellSize+cellSize/2, y = i*cellSize+cellSize/2;
      if (k===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
    ctx.stroke();
  }
}

function updateBadges(stats){
  badgesEl.innerHTML = '';
  const entries = [
    ['Saved', stats.victims_saved],
    ['Remaining', Math.max(0, (stats.initial_victims||0) - (stats.victims_saved||0))],
    ['Steps', stats.time_steps],
    ['Risk', (stats.total_risk||0).toFixed(1)],
    ['Eff.', (stats.efficiency_score||0).toFixed(3)]
  ];
  for (const [k,v] of entries){ const b = document.createElement('div'); b.className='badge'; b.textContent=`${k}: ${v}`; badgesEl.appendChild(b); }
}

function updateStats(stats){
  statsEl.textContent = JSON.stringify(stats, null, 2);
  updateBadges(stats);
  const eff = Math.max(0, Math.min(1, stats.efficiency_score || 0));
  const bar = document.getElementById('efficiencyBar');
  if (bar) bar.style.width = `${eff*100}%`;
}
function setStatus(text){ statusEl.textContent = text; }
async function safe(fn,label){ try{ return await fn(); } catch(e){ logEl.textContent += `${label} failed: ${e}\n`; } }

function initCharts(){
  const riskEl = document.getElementById('riskChart');
  const vrEl = document.getElementById('vrChart');
  const riskGradient = riskEl.getContext('2d').createLinearGradient(0,0,0,riskEl.height);
  riskGradient.addColorStop(0, 'rgba(239,68,68,0.35)');
  riskGradient.addColorStop(1, 'rgba(239,68,68,0.02)');
  riskChart = new Chart(riskEl, { type:'line', data:{ labels: [], datasets:[{ label:'Total Risk', data: [], borderColor:'#ef4444', backgroundColor:riskGradient, fill:true, tension:0.35, pointRadius:0 }] }, options:{ responsive:true, maintainAspectRatio:false, plugins:{ legend:{ labels:{ color:'#e5e7eb', font:{ size:12, family:'Inter, Roboto, Arial' } } } }, scales:{ x:{ ticks:{ color:'#cbd5e1', font:{ size:12 } }, grid:{ color:'rgba(148,163,184,.1)' }, title:{ display:true, text:'Time Steps', color:'#e5e7eb', font:{ size:13 } } }, y:{ ticks:{ color:'#cbd5e1', font:{ size:12 } }, grid:{ color:'rgba(148,163,184,.1)' }, title:{ display:true, text:'Risk Level', color:'#e5e7eb', font:{ size:13 } } } } } });
  vrChart = new Chart(vrEl, { type:'line', data:{ labels: [], datasets:[ { label:'Victims Saved', data: [], borderColor:'#22c55e', tension:0.35, pointRadius:0 }, { label:'Victims Remaining', data: [], borderColor:'#eab308', tension:0.35, pointRadius:0 }, { label:'Resources Used', data: [], borderColor:'#93c5fd', tension:0.35, pointRadius:0 } ] }, options:{ responsive:true, maintainAspectRatio:false, plugins:{ legend:{ labels:{ color:'#e5e7eb', font:{ size:12, family:'Inter, Roboto, Arial' } } } }, scales:{ x:{ ticks:{ color:'#cbd5e1', font:{ size:12 } }, grid:{ color:'rgba(148,163,184,.1)' }, title:{ display:true, text:'Time Steps', color:'#e5e7eb', font:{ size:13 } } }, y:{ ticks:{ color:'#cbd5e1', font:{ size:12 } }, grid:{ color:'rgba(148,163,184,.1)' }, title:{ display:true, text:'Count', color:'#e5e7eb', font:{ size:13 } } } } } });
}

function updateCharts(tele){ if (!tele) return; const labels = tele.time_steps_history || []; riskChart.data.labels = labels; riskChart.data.datasets[0].data = tele.risk_history || []; riskChart.update('none'); vrChart.data.labels = labels; vrChart.data.datasets[0].data = tele.victims_saved_history || []; vrChart.data.datasets[1].data = tele.remaining_history || []; vrChart.data.datasets[2].data = tele.resources_used_history || []; vrChart.update('none'); }

async function refresh(){ const data = await safe(()=>api.getState(),'getState'); if(!data) return; state = data.state; updateStats(data.stats); updateCharts(data.telemetry); setStatus(`Step ${state.time_step}`); draw(); }

async function autoStepOnce(){ const data = await safe(()=>api.step(),'step'); if(!data) return false; state = data.state; updateStats(data.stats); updateCharts(data.telemetry); setStatus(`Step ${state.time_step}${data.done?' (done)':''}`); draw(); if (data.done){ const sum = await safe(()=>api.summary(),'summary'); if (sum) logEl.textContent += `Summary: ${JSON.stringify(sum)}\n`; } return !data.done; }

async function startAuto(){ if (autoTimer) return; logEl.textContent += 'Auto-run started\n'; const tick = async ()=>{ const cont = await autoStepOnce(); if (cont) autoTimer = setTimeout(tick, 180); else { autoTimer = null; logEl.textContent += 'Auto-run finished\n'; } }; tick(); }
function stopAuto(){ if (autoTimer){ clearTimeout(autoTimer); autoTimer = null; logEl.textContent += 'Auto-run stopped\n'; } }

// Controls
 document.getElementById('btnReset').onclick = async ()=>{ stopAuto(); await safe(()=>api.reset(),'reset'); logEl.textContent += 'Reset\n'; lastRecommendedPath = []; await refresh(); };
 document.getElementById('btnStep').onclick = async ()=>{ stopAuto(); await autoStepOnce(); };
 document.getElementById('btnAuto').onclick = startAuto;
 document.getElementById('btnStop').onclick = stopAuto;
 document.getElementById('btnRecommend').onclick = async ()=>{ const data = await safe(()=>api.recommend(),'recommend'); if (!data) return; lastRecommendedPath = data.path || []; draw(); logEl.textContent += `AI Path → len:${data.length||0}, risk:${(data.risk||0).toFixed(2)}, expectedSurvival:${data.expected_survival?Math.round(data.expected_survival*100)+'%':'N/A'}\n`; };
 document.getElementById('btnCollect').onclick = async ()=>{ const res = await safe(()=>api.collect(),'collect'); if (!res) return; logEl.textContent += `Collect: ${res.message || (res.detail?JSON.stringify(res.detail):'')}\n`; await refresh(); };
 document.getElementById('btnRescue').onclick = async ()=>{ const res = await safe(()=>api.rescue(),'rescue'); if (!res) return; const msg = res.ok ? 'Rescue success' : 'Rescue failed'; logEl.textContent += `Rescue: ${msg} ${res.detail?JSON.stringify(res.detail):''}\n`; await refresh(); };

// Click-to-move
 gridCanvas.addEventListener('click', async (e)=>{ if(!state) return; const rect = gridCanvas.getBoundingClientRect(); const x = e.clientX - rect.left; const y = e.clientY - rect.top; const j = Math.floor(x / cellSize); const i = Math.floor(y / cellSize); if (i<0||j<0||i>=state.grid_size||j>=state.grid_size){ logEl.textContent += `Out of bounds (${i},${j})\n`; return; } const res = await safe(()=>api.move(i,j),'move'); if (res && res.ok){ logEl.textContent += `Moved to (${i},${j})\n`; await refresh(); } else { logEl.textContent += `Invalid move (${i},${j})\n`; } });

// Add Survival% toggle button next to Recommend
(function(){ const survivalToggle = document.createElement('button'); survivalToggle.className = 'btn btn-primary'; survivalToggle.innerHTML = '<span class="btn-icon">📊</span><span class="btn-text">Toggle Survival%</span>'; survivalToggle.title = 'Show/Hide survival probabilities over victims'; survivalToggle.onclick = ()=>{ showSurvival = !showSurvival; draw(); }; const controls = document.querySelector('.controls'); controls.insertBefore(survivalToggle, document.getElementById('btnRecommend')); })();

// Init
(function(){ initCharts(); })();

// Animate hazards by redrawing periodically for pulse
setInterval(()=>{ if(state) draw(); }, 300);
(async ()=>{ const l = await safe(()=>api.legend(),'legend'); if (l) logEl.textContent += `Legend: ${JSON.stringify(l)}\n`; await refresh(); })();
