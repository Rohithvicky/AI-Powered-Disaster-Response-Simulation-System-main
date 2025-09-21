// AI Disaster Response Simulation - Compressed JavaScript

class SoundManager {
    constructor() {
        this.sounds = {};
        this.enabled = true;
        this.initSounds();
    }

    initSounds() {
        // Create audio contexts for different sounds
        this.sounds = {
            rescue: this.createTone(800, 0.3, 'sine'),
            ambulance: this.createTone(600, 0.4, 'sawtooth'),
            fireTruck: this.createTone(400, 0.5, 'square'),
            helicopter: this.createTone(300, 0.6, 'triangle'),
            boat: this.createTone(200, 0.4, 'sine'),
            medical: this.createTone(1000, 0.2, 'sine'),
            machinery: this.createTone(150, 0.7, 'sawtooth'),
            success: this.createSuccessTone()
        };
    }

    createTone(frequency, duration, type = 'sine') {
        return () => {
            if (!this.enabled) return;
            
            try {
                // Initialize audio context if not already done
                if (!this.audioContext) {
                    this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                }
                
                // Resume audio context if suspended (required for user interaction)
                if (this.audioContext.state === 'suspended') {
                    this.audioContext.resume();
                }
                
                const oscillator = this.audioContext.createOscillator();
                const gainNode = this.audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(this.audioContext.destination);
                
                oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
                oscillator.type = type;
                
                gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
                
                oscillator.start(this.audioContext.currentTime);
                oscillator.stop(this.audioContext.currentTime + duration);
            } catch (error) {
                console.log('Audio not available:', error);
            }
        };
    }

    createSuccessTone() {
        return () => {
            if (!this.enabled) return;
            
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            // Success chord: C-E-G
            oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime); // C5
            oscillator.frequency.setValueAtTime(659.25, audioContext.currentTime + 0.1); // E5
            oscillator.frequency.setValueAtTime(783.99, audioContext.currentTime + 0.2); // G5
            
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        };
    }

    playSound(soundName) {
        if (this.sounds[soundName]) {
            this.sounds[soundName]();
        }
    }

    playRescueSound(resourceType) {
        // Play appropriate sound based on resource type
        switch (resourceType) {
            case 'ambulance':
                this.playSound('ambulance');
                break;
            case 'fire_truck':
                this.playSound('fireTruck');
                break;
            case 'helicopter':
                this.playSound('helicopter');
                break;
            case 'boat':
                this.playSound('boat');
                break;
            case 'medical_supplies':
                this.playSound('medical');
                break;
            case 'heavy_machinery':
                this.playSound('machinery');
                break;
            default:
                this.playSound('rescue');
        }
        
        // Always play success sound after rescue
        setTimeout(() => this.playSound('success'), 200);
    }

    toggle() {
        this.enabled = !this.enabled;
        return this.enabled;
    }
}

class SimulationDashboard {
    constructor(apiBase = 'http://localhost:8000/api') {
        this.apiBase = apiBase;
        this.simulationState = null;
        this.updateInterval = null;
        this.gridCanvas = document.getElementById('simulationGrid');
        this.gridCtx = this.gridCanvas ? this.gridCanvas.getContext('2d') : null;
        this.tooltip = null;
        this.soundManager = new SoundManager();
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
        document.getElementById('btnSoundToggle').addEventListener('click', () => this.toggleSound());
        
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
                
                // Play sound effects for each resource used
                operation.resources_used.forEach(resource => {
                    this.soundManager.playRescueSound(resource);
                });
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
        
        // Clear canvas with transparent/dark background
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw professional grid lines
        ctx.strokeStyle = '#e2e8f0';
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
        
        // Add accent lines every 5 cells
        ctx.strokeStyle = '#cbd5e1';
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
        
        // Draw terrain with proper disaster response colors
        if (this.simulationState.grid) {
            for (let i = 0; i < gridSize; i++) {
                for (let j = 0; j < gridSize; j++) {
                    const terrain = this.simulationState.grid[i][j];
                    const x = j * cellSize;
                    const y = i * cellSize;
                    
                    let color = '#dcfce7'; // Light green for safe cells
                    if (terrain === 'G') color = '#f0fdf4'; // Light green for grass
                    else if (terrain === 'W') color = '#dbeafe'; // Light blue for water
                    else if (terrain === 'R') color = '#f3f4f6'; // Light gray for rock
                    else if (terrain === 'U') color = '#9ca3af'; // Grey for urban
                    
                    ctx.fillStyle = color;
                    ctx.fillRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
                }
            }
        }
        
        // Draw hazards with proper colors based on disaster type
        if (this.simulationState.hazards) {
            this.simulationState.hazards.forEach(hazard => {
                const [i, j, intensity] = hazard;
                if (intensity > 0.2) {
                    const x = j * cellSize;
                    const y = i * cellSize;
                    
                    // Use proper colors based on disaster type
                    let baseColor, borderColor;
                    const disasterType = this.simulationState.disaster_type || 'fire';
                    
                    if (disasterType === 'fire') {
                        // Red colors for fire
                        if (intensity > 0.8) {
                            baseColor = '#dc2626';
                            borderColor = '#b91c1c';
                        } else if (intensity > 0.5) {
                            baseColor = '#ef4444';
                            borderColor = '#dc2626';
                        } else {
                            baseColor = '#f87171';
                            borderColor = '#ef4444';
                        }
                    } else if (disasterType === 'flood') {
                        // Blue colors for flood
                        if (intensity > 0.8) {
                            baseColor = '#2563eb';
                            borderColor = '#1d4ed8';
                        } else if (intensity > 0.5) {
                            baseColor = '#3b82f6';
                            borderColor = '#2563eb';
                        } else {
                            baseColor = '#60a5fa';
                            borderColor = '#3b82f6';
                        }
                    } else {
                        // Default red for other disasters
                        if (intensity > 0.8) {
                            baseColor = '#dc2626';
                            borderColor = '#b91c1c';
                        } else if (intensity > 0.5) {
                            baseColor = '#ef4444';
                            borderColor = '#dc2626';
                        } else {
                            baseColor = '#f87171';
                            borderColor = '#ef4444';
                        }
                    }
                    
                    ctx.fillStyle = baseColor;
                    ctx.fillRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
                    
                    // Add border
                    ctx.strokeStyle = borderColor;
                    ctx.lineWidth = 1;
                    ctx.strokeRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
                }
            });
        }
        
        // Draw victims with proper yellow color
        if (this.simulationState.victims) {
            this.simulationState.victims.forEach(victim => {
                const [i, j] = victim;
                const x = j * cellSize;
                const y = i * cellSize;
                
                // Yellow background for victims
                ctx.fillStyle = '#fbbf24';
                ctx.fillRect(x + 2, y + 2, cellSize - 4, cellSize - 4);
                
                // Draw victim icon
                this.drawIcon(ctx, 'victim-icon', x, y, cellSize);
                
                // Add yellow border
                ctx.strokeStyle = '#d97706';
                ctx.lineWidth = 2;
                ctx.strokeRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
            });
        }
        
        // Draw resources with proper disaster response colors
        if (this.simulationState.resources) {
            this.simulationState.resources.forEach(resource => {
                const [i, j, resourceType] = resource;
                const x = j * cellSize;
                const y = i * cellSize;
                
                // Use proper colors for different resource types
                let baseColor, borderColor;
                if (resourceType.startsWith('used_')) {
                    baseColor = '#6b7280'; // Gray for used resources
                    borderColor = '#4b5563';
                } else if (resourceType === 'rescue_team') {
                    baseColor = '#fed7aa'; // Light orange for rescue teams
                    borderColor = '#fb923c';
                } else if (resourceType === 'ambulance') {
                    baseColor = '#06b6d4'; // Cyan for ambulances
                    borderColor = '#0891b2';
                } else if (resourceType === 'fire_truck' || resourceType === 'boat') {
                    baseColor = '#d946ef'; // Magenta for fire trucks/boats
                    borderColor = '#c026d3';
                } else if (resourceType === 'emergency_shelter') {
                    baseColor = '#ffffff'; // White background
                    borderColor = '#22c55e'; // Green border
                } else {
                    baseColor = '#22c55e'; // Default green
                    borderColor = '#16a34a';
                }
                
                ctx.fillStyle = baseColor;
                ctx.fillRect(x + 2, y + 2, cellSize - 4, cellSize - 4);
                
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
                    'used_fire_truck': 'fire-truck-icon',
                    'used_boat': 'boat-icon',
                    'used_helicopter': 'helicopter-icon',
                    'used_heavy_machinery': 'machinery-icon'
                };
                
                const iconId = iconMap[resourceType] || 'rescuer-icon';
                this.drawIcon(ctx, iconId, x, y, cellSize);
                
                // Add border
                ctx.strokeStyle = borderColor;
                ctx.lineWidth = 2;
                ctx.strokeRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
            });
        }
        
        // Draw recommended path with proper light blue color
        if (this.recommendedPath && this.recommendedPath.length > 1) {
            // Light blue path
            ctx.strokeStyle = '#60a5fa';
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
            
            // Add path nodes
            this.recommendedPath.forEach((point, index) => {
                const x = point[1] * cellSize + cellSize/2;
                const y = point[0] * cellSize + cellSize/2;
                
                ctx.fillStyle = index === 0 ? '#22c55e' : '#60a5fa';
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, 2 * Math.PI);
                ctx.fill();
            });
        }

        // Draw rescue team with proper green color
        if (this.simulationState.rescue_team) {
            const [i, j] = this.simulationState.rescue_team.position;
            const x = j * cellSize;
            const y = i * cellSize;
            
            // Light orange background for rescue team
            ctx.fillStyle = '#fed7aa';
            ctx.fillRect(x + 2, y + 2, cellSize - 4, cellSize - 4);
            
            // Draw rescuer icon
            this.drawIcon(ctx, 'rescuer-icon', x, y, cellSize);
            
            // Add energy indicator
            const energyPercent = (this.simulationState.rescue_team.efficiency || 100) / 100;
            let energyColor;
            if (energyPercent > 0.5) {
                energyColor = '#10b981';
            } else if (energyPercent > 0.2) {
                energyColor = '#f59e0b';
            } else {
                energyColor = '#ef4444';
            }
            
            ctx.fillStyle = energyColor;
            ctx.fillRect(x + 3, y + cellSize - 5, (cellSize - 6) * energyPercent, 3);
            
            // Add light orange border
            ctx.strokeStyle = '#fb923c';
            ctx.lineWidth = 2;
            ctx.strokeRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
        }
    }

    _darkenColor(color, amount) {
        const hex = color.replace('#', '');
        const r = Math.max(0, parseInt(hex.substr(0, 2), 16) - Math.floor(255 * amount));
        const g = Math.max(0, parseInt(hex.substr(2, 2), 16) - Math.floor(255 * amount));
        const b = Math.max(0, parseInt(hex.substr(4, 2), 16) - Math.floor(255 * amount));
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    _lightenColor(color, amount) {
        const hex = color.replace('#', '');
        const r = Math.min(255, parseInt(hex.substr(0, 2), 16) + Math.floor(255 * amount));
        const g = Math.min(255, parseInt(hex.substr(2, 2), 16) + Math.floor(255 * amount));
        const b = Math.min(255, parseInt(hex.substr(4, 2), 16) + Math.floor(255 * amount));
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    drawIcon(ctx, icon, x, y, size) {
        // Use emoji icons for better compatibility and immediate display
        const emojiMap = {
            'rescuer-icon': '👨‍🚒',
            'victim-icon': '🚨',
            'ambulance-icon': '🚑',
            'fire-truck-icon': '🚒',
            'helicopter-icon': '🚁',
            'boat-icon': '🚤',
            'medical-icon': '🏥',
            'machinery-icon': '🚜'
        };
        
        const emoji = emojiMap[icon] || '❓';
        ctx.font = `${size * 0.8}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = '#000000';
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
                    'used_helicopter': '🚁 Used Helicopter (Air Rescue)',
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

    toggleSound() {
        const isEnabled = this.soundManager.toggle();
        const btn = document.getElementById('btnSoundToggle');
        const icon = btn.querySelector('i');
        const text = btn.querySelector('span') || btn.childNodes[btn.childNodes.length - 1];
        
        if (isEnabled) {
            icon.className = 'fas fa-volume-up';
            text.textContent = ' Sound On';
        } else {
            icon.className = 'fas fa-volume-mute';
            text.textContent = ' Sound Off';
        }
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new SimulationDashboard();
});