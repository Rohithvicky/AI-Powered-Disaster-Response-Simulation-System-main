const api = {
  async getState() { return fetch('/api/state').then(r=>r.json()); },
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

let state = null;
let cellSize = 24;
let autoTimer = null;

function colorForTerrain(t) {
  switch(t){
    case 'U': return '#94a3b8';
    case 'R': return '#0ea5e9';
    case 'S': return '#cbd5e1';
    case 'G': return '#22c55e';
    case 'W': return '#1d4ed8';
    default: return '#0b1220';
  }
}

function draw() {
  if (!state) return;
  const size = state.grid_size;
  cellSize = Math.floor(Math.min(600/size, 600/size));
  ctx.clearRect(0,0,600,600);

  for (let i=0;i<size;i++){
    for (let j=0;j<size;j++){
      const x = j*cellSize, y = i*cellSize;
      ctx.fillStyle = colorForTerrain(state.grid[i][j]);
      ctx.fillRect(x,y,cellSize,cellSize);
    }
  }

  for (const [i,j,val] of state.hazards) {
    const x = j*cellSize, y = i*cellSize;
    const alpha = Math.min(0.85, Math.max(0.2, val));
    ctx.fillStyle = `rgba(220,38,38,${alpha})`;
    ctx.fillRect(x,y,cellSize,cellSize);
  }

  ctx.fillStyle = '#10b981';
  for (const [i,j] of state.resources) {
    ctx.fillRect(j*cellSize+cellSize*0.25, i*cellSize+cellSize*0.25, cellSize*0.5, cellSize*0.5);
  }

  ctx.fillStyle = '#f59e0b';
  for (const [i,j] of state.victims) {
    ctx.beginPath();
    ctx.arc(j*cellSize+cellSize/2, i*cellSize+cellSize/2, cellSize*0.35, 0, Math.PI*2);
    ctx.fill();
  }

  ctx.fillStyle = '#ffffff';
  const [ti,tj] = state.rescue_team.position;
  ctx.fillRect(tj*cellSize+cellSize*0.2, ti*cellSize+cellSize*0.2, cellSize*0.6, cellSize*0.6);
}

function updateStats(stats) {
  statsEl.textContent = JSON.stringify(stats, null, 2);
}

function setStatus(text) {
  statusEl.textContent = text;
}

async function safe(fn, label){
  try { return await fn(); }
  catch(e){ logEl.textContent += `${label} failed: ${e}\n`; }
}

async function refresh() {
  const data = await safe(()=>api.getState(), 'getState');
  if (!data) return;
  state = data.state;
  updateStats(data.stats);
  setStatus(`Step ${state.time_step}`);
  draw();
}

// Auto-run loop
async function autoStepOnce(){
  const data = await safe(()=>api.step(),'step');
  if (!data) return false;
  state = data.state;
  updateStats(data.stats);
  setStatus(`Step ${state.time_step}${data.done?' (done)':''}`);
  draw();
  return !data.done;
}

async function startAuto(){
  if (autoTimer) return;
  logEl.textContent += 'Auto-run started\n';
  const tick = async () => {
    const cont = await autoStepOnce();
    if (cont) autoTimer = setTimeout(tick, 250); else {
      autoTimer = null;
      logEl.textContent += 'Auto-run finished\n';
      const sum = await safe(()=>api.summary(),'summary');
      if (sum) logEl.textContent += `Summary: ${JSON.stringify(sum)}\n`;
    }
  };
  tick();
}

function stopAuto(){
  if (autoTimer){ clearTimeout(autoTimer); autoTimer = null; logEl.textContent += 'Auto-run stopped\n'; }
}

// Controls

document.getElementById('btnReset').onclick = async () => {
  stopAuto();
  await safe(()=>api.reset(),'reset');
  logEl.textContent += `Reset\n`;
  await refresh();
};

document.getElementById('btnStep').onclick = async () => {
  stopAuto();
  await autoStepOnce();
};

document.getElementById('btnRecommend').onclick = async () => {
  const data = await safe(()=>api.recommend(),'recommend');
  if (!data) return;
  const path = data.path || [];
  logEl.textContent += `Recommended path len=${path.length}\n`;
  ctx.strokeStyle = '#eab308';
  ctx.lineWidth = 2;
  ctx.beginPath();
  for (let k=0;k<path.length;k++){
    const [i,j] = path[k];
    const x = j*cellSize+cellSize/2, y = i*cellSize+cellSize/2;
    if (k===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  }
  ctx.stroke();
};

document.getElementById('btnCollect').onclick = async () => {
  const res = await safe(()=>api.collect(),'collect');
  if (!res) return;
  logEl.textContent += `Collect: ${res.message || (res.detail?JSON.stringify(res.detail):'')}\n`;
  await refresh();
};

document.getElementById('btnRescue').onclick = async () => {
  const res = await safe(()=>api.rescue(),'rescue');
  if (!res) return;
  const msg = res.ok ? 'Rescue success' : 'Rescue failed';
  logEl.textContent += `Rescue: ${msg} ${res.detail?JSON.stringify(res.detail):''}\n`;
  await refresh();
};

// Mouse click to move team with bounds check

gridCanvas.addEventListener('click', async (e) => {
  if (!state) return;
  const rect = gridCanvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  const j = Math.floor(x / cellSize);
  const i = Math.floor(y / cellSize);
  if (i < 0 || j < 0 || i >= state.grid_size || j >= state.grid_size){
    logEl.textContent += `Out of bounds (${i},${j})\n`;
    return;
  }
  const res = await safe(()=>api.move(i,j),'move');
  if (res && res.ok){
    logEl.textContent += `Moved to (${i},${j})\n`;
    await refresh();
  } else {
    logEl.textContent += `Invalid move (${i},${j})\n`;
  }
});

// Add auto buttons
const ctrlBar = document.querySelector('.controls');
const btnAuto = document.createElement('button');
btnAuto.textContent = 'Auto-Run';
btnAuto.onclick = startAuto;
const btnStop = document.createElement('button');
btnStop.textContent = 'Stop';
btnStop.onclick = stopAuto;
ctrlBar.insertBefore(btnAuto, ctrlBar.children[2]);
ctrlBar.insertBefore(btnStop, ctrlBar.children[3]);

// Show legend in log
(async () => {
  const l = await safe(()=>api.legend(),'legend');
  if (l) logEl.textContent += `Legend: ${JSON.stringify(l)}\n`;
  await refresh();
})();
