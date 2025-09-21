// AI Disaster Response Simulation - Compressed JavaScript
class SimulationDashboard {
    constructor(apiBase = 'http://localhost:8000/api') {
        this.apiBase = apiBase;
        this.simulationState = null;
        this.updateInterval = null;
        this.gridCanvas = document.getElementById('simulationGrid');
        this.gridCtx = this.gridCanvas ? this.gridCanvas.getContext('2d') : null;
        this.tooltip = null;
        this.init();
    }

    async init() {
        console.log('🚀 Initializing AI Disaster Response Dashboard...');
        this.setupEventListeners();
        this.setupGridHover();
        await this.loadSimulationState();
        this.updateLastUpdateTime();
    }

    setupEventListeners() {
        document.getElementById('btnStart').addEventListener('click', () => this.startSimulation());
        document.getElementById('btnStop').addEventListener('click', () => this.stopSimulation());
        document.getElementById('btnReset').addEventListener('click', () => this.resetSimulation());
        document.getElementById('btnPause').addEventListener('click', () => this.pauseSimulation());
        document.getElementById('btnRecommendPath').addEventListener('click', () => this.recommendPath());
        
        if (this.gridCanvas) {
            this.gridCanvas.addEventListener('click', (e) => this.handleGridClick(e));
        }
    }

    setupGridHover() {
        if (!this.gridCanvas) return;
        
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'grid-tooltip';
        this.tooltip.style.cssText = `
            position: absolute; background: rgba(0, 0, 0, 0.9); color: white;
            padding: 8px 12px; border-radius: 6px; font-size: 12px;
            pointer-events: none; z-index: 1000; display: none;
            max-width: 200px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        `;
        document.body.appendChild(this.tooltip);
        
        this.gridCanvas.addEventListener('mousemove', (e) => this.handleGridHover(e));
        this.gridCanvas.addEventListener('mouseleave', () => this.hideTooltip());
    }

    async loadSimulationState() {
        try {
            const response = await fetch(`${this.apiBase}/state`);
            if (!response.ok) throw new Error('Failed to load simulation state');
            
            const data = await response.json();
            this.simulationState = data.state;
            this.updateDashboard();
            this.updateLastUpdateTime();
        } catch (error) {
            console.error('Error loading simulation state:', error);
        }
    }

    async startSimulation() {
        try {
            this.updateStatus('running');
            this.updateInterval = setInterval(() => this.stepSimulation(), 1000);
            this.updateButtonStates('running');
        } catch (error) {
            console.error('Error starting simulation:', error);
        }
    }

    async stopSimulation() {
        this.updateStatus('stopped');
        this.stopAutoUpdate();
        this.updateButtonStates('stopped');
    }

    async pauseSimulation() {
        if (this.updateInterval) {
            this.updateStatus('paused');
            this.stopAutoUpdate();
            this.updateButtonStates('paused');
        } else {
            this.updateStatus('running');
            this.updateInterval = setInterval(() => this.stepSimulation(), 1000);
            this.updateButtonStates('running');
        }
    }

    updateButtonStates(state) {
        const startBtn = document.getElementById('btnStart');
        const stopBtn = document.getElementById('btnStop');
        const pauseBtn = document.getElementById('btnPause');
        
        if (state === 'running') {
            startBtn.disabled = true;
            stopBtn.disabled = false;
            pauseBtn.disabled = false;
            pauseBtn.textContent = 'Pause';
        } else if (state === 'paused') {
            startBtn.disabled = true;
            stopBtn.disabled = false;
            pauseBtn.disabled = false;
            pauseBtn.textContent = 'Resume';
        } else if (state === 'stopped') {
            startBtn.disabled = false;
            stopBtn.disabled = true;
            pauseBtn.disabled = true;
            pauseBtn.textContent = 'Pause';
        }
    }

    async resetSimulation() {
        try {
            const response = await fetch(`${this.apiBase}/reset`, { method: 'POST' });
            if (!response.ok) throw new Error('Failed to reset simulation');
            
            const data = await response.json();
            this.simulationState = data.state;
            this.updateDashboard();
            this.updateLastUpdateTime();
        } catch (error) {
            console.error('Error resetting simulation:', error);
        }
    }

    async stepSimulation() {
        try {
            const response = await fetch(`${this.apiBase}/step`, { method: 'POST' });
            if (!response.ok) throw new Error('Failed to step simulation');
            
            const data = await response.json();
            if (data.result && data.result.state) {
                this.simulationState = data.result.state;
            } else {
                await this.loadSimulationState();
            }
            this.updateDashboard();
            this.updateLastUpdateTime();
        } catch (error) {
            console.error('Error stepping simulation:', error);
        }
    }

    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    updateDashboard() {
        if (!this.simulationState) return;
        
        this.updateMetrics();
        this.updateDisastersList();
        this.updateTeamsList();
        this.updateAIDecisions();
        this.drawGrid();
    }

    updateMetrics() {
        const metrics = this.simulationState.metrics || {};
        
        const disasterType = this.simulationState.disaster_type || 'earthquake';
        document.getElementById('disasterType').textContent = disasterType.charAt(0).toUpperCase() + disasterType.slice(1);
        
        document.getElementById('casualtiesSaved').textContent = metrics.victims_saved || 0;
        document.getElementById('responseTime').textContent = `${metrics.time_steps || 0}s`;
        document.getElementById('efficiency').textContent = `${Math.round((metrics.efficiency_score || 0) * 100)}%`;
    }

    updateDisastersList() {
        const disastersList = document.getElementById('disastersList');
        const hazards = this.simulationState.hazards || [];
        
        disastersList.innerHTML = '';
        
        if (hazards.length === 0) {
            disastersList.innerHTML = '<div class="no-data">No active hazards</div>';
            return;
        }
        
        hazards.slice(0, 10).forEach((hazard, index) => {
            const [i, j, intensity] = hazard;
            const disasterElement = document.createElement('div');
            disasterElement.className = 'disaster-item';
            disasterElement.innerHTML = `
                <span>Hazard at (${i}, ${j})</span>
                <span class="value">${Math.round(intensity * 100)}%</span>
            `;
            disastersList.appendChild(disasterElement);
        });
    }

    updateTeamsList() {
        const teamsList = document.getElementById('teamsList');
        const rescueTeam = this.simulationState.rescue_team || {};
        
        teamsList.innerHTML = '';
        
        const teamElement = document.createElement('div');
        teamElement.className = 'team-item';
        teamElement.innerHTML = `
            <span>Rescue Team at (${rescueTeam.position?.[0] || 0}, ${rescueTeam.position?.[1] || 0})</span>
            <span class="value">Res: ${rescueTeam.resources || 0}</span>
        `;
        teamsList.appendChild(teamElement);
    }

    updateAIDecisions() {
        const decisionsLog = document.getElementById('decisionsLog');
        const decisions = this.generateAIDecisions();
        const resourceMovements = this.simulationState.metrics?.resource_movements || [];
        const rescueOperations = this.simulationState.metrics?.rescue_operations || [];
        
        decisionsLog.innerHTML = '';
        
        // Show recent resource movements
        if (resourceMovements.length > 0) {
            const recentMovements = resourceMovements.slice(-3);
            recentMovements.forEach(movement => {
                const movementElement = document.createElement('div');
                movementElement.className = 'decision-item';
                movementElement.innerHTML = `
                    <span class="decision-action">🚶 ${movement.resource} moved</span>
                    <span class="decision-detail">from (${movement.from[0]},${movement.from[1]}) to (${movement.to[0]},${movement.to[1]})</span>
                `;
                decisionsLog.appendChild(movementElement);
            });
        }
        
        // Show recent rescue operations
        if (rescueOperations.length > 0) {
            const recentRescues = rescueOperations.slice(-3);
            recentRescues.forEach(operation => {
                const rescueElement = document.createElement('div');
                rescueElement.className = 'decision-item rescue-operation';
                rescueElement.innerHTML = `
                    <span class="decision-action">🆘 Rescue successful</span>
                    <span class="decision-detail">Victim at (${operation.victim[0]},${operation.victim[1]}) using ${operation.resources_used.join(', ')}</span>
                `;
                decisionsLog.appendChild(rescueElement);
            });
        }
        
        if (decisions.length === 0 && resourceMovements.length === 0 && rescueOperations.length === 0) {
            decisionsLog.innerHTML = '<div class="no-data">No AI decisions yet</div>';
        }
    }

    generateAIDecisions() {
        const decisions = [];
        const metrics = this.simulationState.metrics || {};
        const rescueTeam = this.simulationState.rescue_team || {};
        
        if (metrics.victims_saved > 0) {
            decisions.push({
                action: "Victim rescue successful",
                confidence: 0.95
            });
        }
        
        if (rescueTeam.fatigue > 50) {
            decisions.push({
                action: "Team fatigue management",
                confidence: 0.75
            });
        }
        
        if (metrics.efficiency_score > 0.5) {
            decisions.push({
                action: "High efficiency achieved",
                confidence: 0.90
            });
        }
        
        return decisions.slice(-5);
    }

    drawGrid() {
        if (!this.gridCtx || !this.simulationState) return;
        
        const canvas = this.gridCanvas;
        const ctx = this.gridCtx;
        const gridSize = this.simulationState.grid_size || 20;
        const cellSize = Math.min(600, 600) / gridSize;
        
        canvas.width = 600;
        canvas.height = 600;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw grid lines
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 1;
        
        for (let i = 0; i <= gridSize; i++) {
            const pos = i * cellSize;
            ctx.beginPath();
            ctx.moveTo(pos, 0);
            ctx.lineTo(pos, gridSize * cellSize);
            ctx.stroke();
            
            ctx.beginPath();
            ctx.moveTo(0, pos);
            ctx.lineTo(gridSize * cellSize, pos);
            ctx.stroke();
        }
        
        // Draw terrain
        if (this.simulationState.grid) {
            for (let i = 0; i < gridSize; i++) {
                for (let j = 0; j < gridSize; j++) {
                    const terrain = this.simulationState.grid[i][j];
                    const x = j * cellSize;
                    const y = i * cellSize;
                    
                    let color = '#1f2937';
                    if (terrain === 'G') color = '#10b981';
                    else if (terrain === 'W') color = '#06b6d4';
                    else if (terrain === 'R') color = '#ef4444';
                    else if (terrain === 'U') color = '#6b7280';
                    
                    ctx.fillStyle = color;
                    ctx.fillRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
                }
            }
        }
        
        // Draw hazards
        if (this.simulationState.hazards) {
            this.simulationState.hazards.forEach(hazard => {
                const [i, j, intensity] = hazard;
                if (intensity > 0.3) {
                    const x = j * cellSize;
                    const y = i * cellSize;
                    
                    ctx.fillStyle = `rgba(239, 68, 68, ${intensity})`;
                    ctx.fillRect(x + 2, y + 2, cellSize - 4, cellSize - 4);
                }
            });
        }
        
        // Draw victims with emoji icons
        if (this.simulationState.victims) {
            this.simulationState.victims.forEach(victim => {
                const [i, j] = victim;
                const x = j * cellSize;
                const y = i * cellSize;
                
                // Draw victim icon
                this.drawIcon(ctx, 'victim-icon', x, y, cellSize);
            });
        }
        
        // Draw resources with SVG icons
        if (this.simulationState.resources) {
            this.simulationState.resources.forEach(resource => {
                const [i, j, resourceType] = resource;
                const x = j * cellSize;
                const y = i * cellSize;
                
                // Map resource types to SVG icons
                const iconMap = {
                    'ambulance': 'ambulance-icon',
                    'fire_truck': 'fire-truck-icon',
                    'helicopter': 'helicopter-icon',
                    'rescue_team': 'rescuer-icon',
                    'medical_supplies': 'rescuer-icon',
                    'boat': 'ambulance-icon',
                    'heavy_machinery': 'fire-truck-icon',
                    'emergency_shelter': 'ambulance-icon'
                };
                
                const iconId = iconMap[resourceType] || 'rescuer-icon';
                this.drawSVGIcon(ctx, iconId, x + cellSize/2 - 12, y + cellSize/2 - 12, 24, 24);
            });
        }
        
        // Draw rescue team with SVG icon
        if (this.simulationState.rescue_team) {
            const [i, j] = this.simulationState.rescue_team.position;
            const x = j * cellSize;
            const y = i * cellSize;
            
            // Draw SVG rescuer icon
            this.drawSVGIcon(ctx, 'rescuer-icon', x + cellSize/2 - 12, y + cellSize/2 - 12, 24, 24);
            
            // Add energy indicator
            const energyPercent = (this.simulationState.rescue_team.efficiency || 100) / 100;
            ctx.fillStyle = energyPercent > 0.5 ? '#10b981' : energyPercent > 0.2 ? '#f59e0b' : '#ef4444';
            ctx.fillRect(x + 2, y + cellSize - 4, (cellSize - 4) * energyPercent, 2);
        }
    }

    drawIcon(ctx, icon, x, y, size) {
        // Use Unicode emojis for better compatibility
        const iconMap = {
            'rescuer-icon': '👨‍🚒',
            'victim-icon': '🚨',
            'ambulance-icon': '🚑',
            'fire-truck-icon': '🚒',
            'helicopter-icon': '🚁',
            'boat-icon': '🚤',
            'medical-icon': '🏥',
            'machinery-icon': '🚜'
        };
        
        const emoji = iconMap[icon] || '❓';
        
        // Set font and draw emoji
        ctx.font = `${size}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(emoji, x + size/2, y + size/2);
    }

    handleGridHover(event) {
        if (!this.simulationState) return;
        
        const rect = this.gridCanvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const gridSize = this.simulationState.grid_size || 20;
        const cellSize = Math.min(600, 600) / gridSize;
        
        const col = Math.floor(x / cellSize);
        const row = Math.floor(y / cellSize);
        
        if (row >= 0 && row < gridSize && col >= 0 && col < gridSize) {
            const terrain = this.simulationState.grid[row][col];
            const hazard = this.simulationState.hazards.find(h => h[0] === row && h[1] === col);
            const victim = this.simulationState.victims.find(v => v[0] === row && v[1] === col);
            const resource = this.simulationState.resources.find(r => r[0] === row && r[1] === col);
            const rescueTeam = this.simulationState.rescue_team && 
                              this.simulationState.rescue_team.position[0] === row && 
                              this.simulationState.rescue_team.position[1] === col;
            
            let tooltipText = `Position: (${row}, ${col})\n`;
            
            const terrainInfo = {
                'G': '🟢 Green Area - Safe zones and parks',
                'W': '🔵 Water - Rivers and lakes',
                'R': '🔴 Urban Red - High-risk urban areas',
                'U': '⚫ Urban - Urban infrastructure'
            };
            tooltipText += `Terrain: ${terrainInfo[terrain] || 'Unknown'}\n`;
            
            if (hazard) {
                tooltipText += `🌪️ Hazard Intensity: ${(hazard[2] * 100).toFixed(1)}%\n`;
            }
            
            if (victim) {
                tooltipText += `🟠 Victim - Needs rescue\n`;
            }
            
            if (resource) {
                const resourceType = resource[2] || 'unknown';
                const resourceNames = {
                    'ambulance': '🚑 Ambulance', 'fire_truck': '🚒 Fire Truck',
                    'rescue_team': '👥 Rescue Team', 'medical_supplies': '🏥 Medical Supplies',
                    'helicopter': '🚁 Helicopter', 'boat': '🚤 Boat',
                    'heavy_machinery': '🚜 Heavy Machinery', 'emergency_shelter': '🏠 Emergency Shelter'
                };
                tooltipText += `${resourceNames[resourceType] || '🟢 Resource'}\n`;
            }
            
            if (rescueTeam) {
                tooltipText += `🔵 Rescue Team - Emergency response\n`;
            }
            
            this.showTooltip(event, tooltipText);
        }
    }

    showTooltip(event, text) {
        if (!this.tooltip) return;
        
        this.tooltip.textContent = text;
        this.tooltip.style.display = 'block';
        this.tooltip.style.left = (event.pageX + 10) + 'px';
        this.tooltip.style.top = (event.pageY - 10) + 'px';
    }

    hideTooltip() {
        if (this.tooltip) {
            this.tooltip.style.display = 'none';
        }
    }

    handleGridClick(event) {
        if (!this.simulationState) return;
        
        const rect = this.gridCanvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const gridSize = this.simulationState.grid_size || 20;
        const cellSize = Math.min(600, 600) / gridSize;
        
        const col = Math.floor(x / cellSize);
        const row = Math.floor(y / cellSize);
        
        if (row >= 0 && row < gridSize && col >= 0 && col < gridSize) {
            console.log(`Clicked on cell (${row}, ${col})`);
        }
    }

    async recommendPath() {
        console.log('AI recommending path to nearest victim...');
    }

    updateStatus(status) {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.getElementById('statusText');
        
        statusDot.className = `status-dot ${status}`;
        statusText.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    }

    updateLastUpdateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        document.getElementById('lastUpdate').textContent = `Last Update: ${timeString}`;
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new SimulationDashboard();
});