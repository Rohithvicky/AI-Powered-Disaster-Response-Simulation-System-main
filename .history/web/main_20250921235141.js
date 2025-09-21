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
        
        // Show current path recommendation
        if (this.currentPathRecommendation) {
            const pathElement = document.createElement('div');
            pathElement.className = 'decision-item path-recommendation';
            pathElement.innerHTML = `
                <span class="decision-action">🎯 AI Path Recommendation</span>
                <span class="decision-detail">Target: (${this.currentPathRecommendation.target_victim[0]},${this.currentPathRecommendation.target_victim[1]}) | ${this.currentPathRecommendation.path_length} steps | Risk: ${Math.round(this.currentPathRecommendation.risk_level * 100)}%</span>
            `;
            decisionsLog.appendChild(pathElement);
        }
        
        // Show recent resource movements
        if (resourceMovements.length > 0) {
            const recentMovements = resourceMovements.slice(-2);
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
            const recentRescues = rescueOperations.slice(-2);
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
        
        if (decisions.length === 0 && resourceMovements.length === 0 && rescueOperations.length === 0 && !this.currentPathRecommendation) {
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
        
        // Clear canvas with professional background
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw professional grid lines
        ctx.strokeStyle = '#e5e7eb';
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
        
        // Add stronger border lines every 5 cells for better orientation
        ctx.strokeStyle = '#d1d5db';
        ctx.lineWidth = 2;
        for (let i = 0; i <= gridSize; i += 5) {
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
        
        // Draw terrain with professional colors
        if (this.simulationState.grid) {
            for (let i = 0; i < gridSize; i++) {
                for (let j = 0; j < gridSize; j++) {
                    const terrain = this.simulationState.grid[i][j];
                    const x = j * cellSize;
                    const y = i * cellSize;
                    
                    let color = '#f9fafb'; // Light gray for default
                    if (terrain === 'G') color = '#dcfce7'; // Light green for grass
                    else if (terrain === 'W') color = '#dbeafe'; // Light blue for water
                    else if (terrain === 'R') color = '#fef2f2'; // Light red for rock
                    else if (terrain === 'U') color = '#f3f4f6'; // Light gray for urban
                    
                    ctx.fillStyle = color;
                    ctx.fillRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
                }
            }
        }
        
        // Draw hazards with professional colors
        if (this.simulationState.hazards) {
            this.simulationState.hazards.forEach(hazard => {
                const [i, j, intensity] = hazard;
                if (intensity > 0.2) {
                    const x = j * cellSize;
                    const y = i * cellSize;
                    
                    // Use professional hazard colors
                    let hazardColor;
                    if (intensity > 0.8) {
                        hazardColor = `rgba(220, 38, 38, 0.8)`; // High intensity - professional red
                    } else if (intensity > 0.5) {
                        hazardColor = `rgba(239, 68, 68, 0.6)`; // Medium intensity - professional red
                    } else {
                        hazardColor = `rgba(248, 113, 113, 0.4)`; // Low intensity - light red
                    }
                    
                    ctx.fillStyle = hazardColor;
                    ctx.fillRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
                    
                    // Add subtle border for clarity
                    ctx.strokeStyle = `rgba(185, 28, 28, ${intensity})`;
                    ctx.lineWidth = 1;
                    ctx.strokeRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
                }
            });
        }
        
        // Draw victims with professional styling
        if (this.simulationState.victims) {
            this.simulationState.victims.forEach(victim => {
                const [i, j] = victim;
                const x = j * cellSize;
                const y = i * cellSize;
                
                // Draw professional background for victims
                ctx.fillStyle = '#ef4444';
                ctx.fillRect(x + 2, y + 2, cellSize - 4, cellSize - 4);
                
                // Draw victim icon
                this.drawIcon(ctx, 'victim-icon', x, y, cellSize);
                
                // Add professional border
                ctx.strokeStyle = '#dc2626';
                ctx.lineWidth = 1;
                ctx.strokeRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
            });
        }
        
        // Draw resources with emoji icons
        if (this.simulationState.resources) {
            this.simulationState.resources.forEach(resource => {
                const [i, j, resourceType] = resource;
                const x = j * cellSize;
                const y = i * cellSize;
                
                // Map resource types to emoji icons
                const iconMap = {
                    'ambulance': 'ambulance-icon',
                    'fire_truck': 'fire-truck-icon',
                    'helicopter': 'helicopter-icon',
                    'rescue_team': 'rescuer-icon',
                    'medical_supplies': 'medical-icon',
                    'boat': 'boat-icon',
                    'heavy_machinery': 'machinery-icon',
                    'emergency_shelter': 'medical-icon',
                    'used_medical_supplies': 'medical-icon',
                    'used_ambulance': 'ambulance-icon',
                    'used_fire_truck': 'fire-truck-icon'
                };
                
                const iconId = iconMap[resourceType] || 'rescuer-icon';
                this.drawIcon(ctx, iconId, x, y, cellSize);
            });
        }
        
        // Draw recommended path with professional styling
        if (this.recommendedPath && this.recommendedPath.length > 1) {
            ctx.strokeStyle = '#3b82f6';
            ctx.lineWidth = 3;
            ctx.setLineDash([6, 3]);
            ctx.beginPath();
            
            this.recommendedPath.forEach((point, index) => {
                const x = point[1] * cellSize + cellSize/2;
                const y = point[0] * cellSize + cellSize/2;
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // Draw rescue team with professional styling
        if (this.simulationState.rescue_team) {
            const [i, j] = this.simulationState.rescue_team.position;
            const x = j * cellSize;
            const y = i * cellSize;
            
            // Draw professional background for rescue team
            ctx.fillStyle = '#3b82f6';
            ctx.fillRect(x + 2, y + 2, cellSize - 4, cellSize - 4);
            
            // Draw rescuer icon
            this.drawIcon(ctx, 'rescuer-icon', x, y, cellSize);
            
            // Add professional energy indicator
            const energyPercent = (this.simulationState.rescue_team.efficiency || 100) / 100;
            ctx.fillStyle = energyPercent > 0.5 ? '#10b981' : energyPercent > 0.2 ? '#f59e0b' : '#ef4444';
            ctx.fillRect(x + 3, y + cellSize - 5, (cellSize - 6) * energyPercent, 3);
            
            // Add professional border
            ctx.strokeStyle = '#1e40af';
            ctx.lineWidth = 2;
            ctx.strokeRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
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
                    'heavy_machinery': '🚜 Heavy Machinery', 'emergency_shelter': '🏠 Emergency Shelter',
                    'used_medical_supplies': '🏥 Used Medical Supplies (Victim Rescued)',
                    'used_ambulance': '🚑 Used Ambulance (Victim Transported)',
                    'used_fire_truck': '🚒 Used Fire Truck (Fire Extinguished)',
                    'used_boat': '🚤 Used Boat (Flood Rescue)',
                    'used_heavy_machinery': '🚜 Used Heavy Machinery (Debris Cleared)'
                };
                tooltipText += `${resourceNames[resourceType] || '🟢 Resource'}\n`;
                
                // Add special message for used resources
                if (resourceType.startsWith('used_')) {
                    tooltipText += '✅ This resource was used to save a victim!\n';
                }
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
        try {
            console.log('AI recommending path to nearest victim...');
            
            const response = await fetch(`${this.apiBase}/recommend`, { method: 'POST' });
            if (!response.ok) {
                throw new Error('Failed to get path recommendation');
            }
            
            const data = await response.json();
            
            if (data.error) {
                this.showNotification(data.error, 'warning');
                return;
            }
            
            // Show the recommended path
            this.showRecommendedPath(data.path);
            
            // Show detailed information about the recommendation
            const message = `AI recommends path to victim at (${data.target_victim[0]}, ${data.target_victim[1]}) - ${data.path_length} steps, ${data.estimated_time}s, risk: ${Math.round(data.risk_level * 100)}%`;
            this.showNotification(message, 'success');
            
            // Update AI decisions with path information
            this.updateAIDecisionsWithPath(data);
            
        } catch (error) {
            console.error('❌ Failed to generate path recommendation:', error);
            this.showNotification('Failed to generate path recommendation', 'error');
        }
    }

    generatePath(start, end) {
        const path = [start];
        let current = [...start];
        
        while (current[0] !== end[0] || current[1] !== end[1]) {
            if (current[0] < end[0]) current[0]++;
            else if (current[0] > end[0]) current[0]--;
            else if (current[1] < end[1]) current[1]++;
            else if (current[1] > end[1]) current[1]--;
            
            path.push([...current]);
        }
        
        return path;
    }

    showRecommendedPath(path) {
        this.recommendedPath = path;
        this.drawGrid(); // Redraw to show the path
    }

    updateAIDecisionsWithPath(pathData) {
        // Store path data for display in AI decisions
        this.currentPathRecommendation = pathData;
        this.updateAIDecisions(); // Refresh the AI decisions display
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 10000;
            animation: slideIn 0.3s ease;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        `;
        
        // Set background color based on type
        const colors = {
            'success': '#10b981',
            'error': '#ef4444',
            'warning': '#f59e0b',
            'info': '#3b82f6'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
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