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
let lastRecommendedPath = [];
let showSurvival = false;

// Charts
let riskChart, vrChart;

function colorForTerrain(t) {
  switch(t){
    case 'U': return '#9aa2ad';
    case 'R': return '#28b0ec';
    case 'S': return '#cdd3dc';
    case 'G': return '#27c36a';
    case 'W': return '#1b6eea';
    default: return '#0b1220';
  }
}

function draw(){
  if (!state) return;
  const size = state.grid_size;
  cellSize = Math.floor(Math.min(720/size, 720/size));
  ctx.clearRect(0,0,720,720);

  // Terrain
  for (let i=0;i<size;i++){
    for (let j=0;j<size;j++){
      const x = j*cellSize, y = i*cellSize;
      ctx.fillStyle = colorForTerrain(state.grid[i][j]);
      ctx.fillRect(x,y,cellSize,cellSize);
    }
  }

  // Hazards soft gradient
  for (const [i,j,val] of state.hazards){
    const x = j*cellSize, y = i*cellSize;
    const r = Math.max(cellSize*0.6, 10);
    const grd = ctx.createRadialGradient(x+cellSize/2,y+cellSize/2, r*0.2, x+cellSize/2,y+cellSize/2,r);
    grd.addColorStop(0, `rgba(239,68,68,${Math.min(.85, Math.max(.25, val))})`);
    grd.addColorStop(1, 'rgba(239,68,68,0)');
    ctx.fillStyle = grd;
    ctx.fillRect(x,y,cellSize,cellSize);
  }

  // Resources
  ctx.fillStyle = '#10b981';
  for (const [i,j] of state.resources) {
    ctx.fillRect(j*cellSize+cellSize*0.25, i*cellSize+cellSize*0.25, cellSize*0.5, cellSize*0.5);
  }

  // Victims
  for (const [i,j] of state.victims){
    const vx = j*cellSize+cellSize*0.1, vy = i*cellSize+cellSize*0.05;
    try { ctx.drawImage(victimImg, vx, vy, cellSize*0.8, cellSize*0.9); } catch {}
    if (showSurvival && state.survival_probabilities){
      const rec = state.survival_probabilities.find(p=>p[0]===i && p[1]===j);
      if (rec){ const p = Math.round(rec[2]*100); ctx.fillStyle = '#ffffff'; ctx.font = `${Math.max(10, Math.floor(cellSize*0.25))}px Arial`; ctx.fillText(`${p}%`, j*cellSize+cellSize*0.35, i*cellSize+cellSize*0.8); }
    }
  }

  // Team
  const [ti,tj] = state.rescue_team.position;
  const cx = tj*cellSize+cellSize*0.1, cy = ti*cellSize+cellSize*0.1;
  try { ctx.drawImage(rescuerImg, cx, cy, cellSize*0.8, cellSize*0.8); } catch {}

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

function updateStats(stats){ statsEl.textContent = JSON.stringify(stats, null, 2); updateBadges(stats); }
function setStatus(text){ statusEl.textContent = text; }
async function safe(fn,label){ try{ return await fn(); } catch(e){ logEl.textContent += `${label} failed: ${e}\n`; } }

function initCharts(){
  const riskEl = document.getElementById('riskChart');
  const vrEl = document.getElementById('vrChart');
  riskChart = new Chart(riskEl, { type:'line', data:{ labels: [], datasets:[{ label:'Total Risk', data: [], borderColor:'#ef4444', tension:0.1 }] }, options:{ responsive:true, maintainAspectRatio:false, scales:{ x:{ title:{ display:true, text:'Time Steps'} }, y:{ title:{ display:true, text:'Risk Level'} } } } });
  vrChart = new Chart(vrEl, { type:'line', data:{ labels: [], datasets:[ { label:'Victims Saved', data: [], borderColor:'#22c55e', tension:0.1 }, { label:'Victims Remaining', data: [], borderColor:'#eab308', tension:0.1 }, { label:'Resources Used', data: [], borderColor:'#93c5fd', tension:0.1 } ] }, options:{ responsive:true, maintainAspectRatio:false, scales:{ x:{ title:{ display:true, text:'Time Steps'} }, y:{ title:{ display:true, text:'Count'} } } } });
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
(function(){ const survivalToggle = document.createElement('button'); survivalToggle.textContent = 'Toggle Survival%'; survivalToggle.title = 'Show/Hide survival probabilities over victims'; survivalToggle.onclick = ()=>{ showSurvival = !showSurvival; draw(); }; const controls = document.querySelector('.controls'); controls.insertBefore(survivalToggle, document.getElementById('btnRecommend')); })();

// Init
(function(){ initCharts(); })();
(async ()=>{ const l = await safe(()=>api.legend(),'legend'); if (l) logEl.textContent += `Legend: ${JSON.stringify(l)}\n`; await refresh(); })();
