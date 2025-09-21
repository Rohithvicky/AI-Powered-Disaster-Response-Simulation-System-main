// Enhanced AI Disaster Response Simulation - Professional Dashboard JavaScript

class DisasterSimulationDashboard {
    constructor() {
        this.apiBase = 'http://localhost:8000/api';
        this.simulationState = null;
        this.isRunning = false;
        this.isPaused = false;
        this.autoMode = true;
        this.realTimeMode = false;
        this.updateInterval = null;
        this.charts = {};
        this.gridCanvas = null;
        this.gridCtx = null;
        this.cellSize = 20;
        this.zoomLevel = 1;
        this.lastUpdate = null;
        
        // Initialize dashboard
        this.init();
    }
    
    async init() {
        console.log('🚀 Initializing AI Disaster Response Dashboard...');
        
        // Initialize canvas
        this.gridCanvas = document.getElementById('simulationGrid');
        this.gridCtx = this.gridCanvas.getContext('2d');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Set up grid hover
        this.setupGridHover();
        
        // Initialize charts
        this.initializeCharts();
        
        // Load initial data
        await this.loadSimulationState();
        
        // Start real-time updates if enabled
        if (this.realTimeMode) {
            this.startRealTimeUpdates();
        }
        
        console.log('✅ Dashboard initialized successfully');
    }
    
    setupEventListeners() {
        // Control buttons
        document.getElementById('btnStart').addEventListener('click', () => this.startSimulation());
        document.getElementById('btnStop').addEventListener('click', () => this.stopSimulation());
        document.getElementById('btnReset').addEventListener('click', () => this.resetSimulation());
        document.getElementById('btnPause').addEventListener('click', () => this.togglePause());
        
        // Settings
        document.getElementById('autoMode').addEventListener('change', (e) => {
            this.autoMode = e.target.checked;
            this.updateStatus();
        });
        
        document.getElementById('realTimeMode').addEventListener('change', (e) => {
            this.realTimeMode = e.target.checked;
            if (this.realTimeMode) {
                this.startRealTimeUpdates();
            } else {
                this.stopRealTimeUpdates();
            }
        });
        
        // Grid controls
        document.getElementById('btnZoomIn').addEventListener('click', () => this.zoomIn());
        document.getElementById('btnZoomOut').addEventListener('click', () => this.zoomOut());
        document.getElementById('btnFullscreen').addEventListener('click', () => this.toggleFullscreen());
        
        // Chart tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
        
        // Grid click events
        this.gridCanvas.addEventListener('click', (e) => this.handleGridClick(e));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }
    
    async loadSimulationState() {
        try {
            const response = await fetch(`${this.apiBase}/state`);
            if (!response.ok) throw new Error('Failed to load simulation state');
            
            const data = await response.json();
            this.simulationState = data.state; // Extract the state from the response
            this.updateDashboard();
            this.updateLastUpdateTime();
        } catch (error) {
            console.error('Error loading simulation state:', error);
            this.showError('Failed to load simulation state');
        }
    }
    
    async startSimulation() {
        try {
            this.showLoading();
            
            const response = await fetch(`${this.apiBase}/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ auto_mode: this.autoMode })
            });
            
            if (!response.ok) throw new Error('Failed to start simulation');
            
            this.isRunning = true;
            this.isPaused = false;
            this.updateControlButtons();
            this.updateStatus();
            
            // Start real-time updates
            this.startRealTimeUpdates();
            
            this.hideLoading();
            this.showSuccess('Simulation started successfully');
            
        } catch (error) {
            console.error('Error starting simulation:', error);
            this.showError('Failed to start simulation');
            this.hideLoading();
        }
    }
    
    async stopSimulation() {
        try {
            const response = await fetch(`${this.apiBase}/stop`, { method: 'POST' });
            if (!response.ok) throw new Error('Failed to stop simulation');
            
            this.isRunning = false;
            this.isPaused = false;
            this.stopRealTimeUpdates();
            this.updateControlButtons();
            this.updateStatus();
            
            this.showSuccess('Simulation stopped');
            
        } catch (error) {
            console.error('Error stopping simulation:', error);
            this.showError('Failed to stop simulation');
        }
    }
    
    async resetSimulation() {
        try {
            this.showLoading();
            
            const response = await fetch(`${this.apiBase}/reset`, { method: 'POST' });
            if (!response.ok) throw new Error('Failed to reset simulation');
            
            this.isRunning = false;
            this.isPaused = false;
            this.stopRealTimeUpdates();
            this.updateControlButtons();
            
            await this.loadSimulationState();
            this.hideLoading();
            this.showSuccess('Simulation reset successfully');
            
        } catch (error) {
            console.error('Error resetting simulation:', error);
            this.showError('Failed to reset simulation');
            this.hideLoading();
        }
    }
    
    togglePause() {
        this.isPaused = !this.isPaused;
        this.updateControlButtons();
        this.updateStatus();
        
        if (this.isPaused) {
            this.stopRealTimeUpdates();
            this.showInfo('Simulation paused');
        } else {
            this.startRealTimeUpdates();
            this.showInfo('Simulation resumed');
        }
    }
    
    startRealTimeUpdates() {
        if (this.updateInterval) return;
        
        this.updateInterval = setInterval(async () => {
            if (this.isRunning && !this.isPaused) {
                await this.stepSimulation();
            }
        }, 1000); // Update every second
    }
    
    stopRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
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
                // Fallback to getting fresh state
                await this.loadSimulationState();
            }
            this.updateDashboard();
            this.updateLastUpdateTime();
            
        } catch (error) {
            console.error('Error stepping simulation:', error);
        }
    }
    
    updateDashboard() {
        if (!this.simulationState) return;
        
        this.updateMetrics();
        this.updateDisastersList();
        this.updateTeamsList();
        this.updateResourceStatus();
        this.updateAIDecisions();
        this.updateCharts();
        this.drawGrid();
    }
    
    updateMetrics() {
        const metrics = this.simulationState.metrics || {};
        
        document.getElementById('casualtiesSaved').textContent = metrics.casualties_saved || 0;
        document.getElementById('responseTime').textContent = `${metrics.average_response_time || 0}s`;
        document.getElementById('efficiency').textContent = `${Math.round((metrics.response_efficiency || 0) * 100)}%`;
        document.getElementById('activeDisasters').textContent = metrics.active_disasters || 0;
    }
    
    updateDisastersList() {
        const disastersList = document.getElementById('disastersList');
        const disasters = this.simulationState.disasters || [];
        
        disastersList.innerHTML = '';
        
        if (disasters.length === 0) {
            disastersList.innerHTML = '<div class="no-data">No active disasters</div>';
            return;
        }
        
        disasters.forEach((disaster, index) => {
            const disasterElement = document.createElement('div');
            disasterElement.className = 'disaster-item';
            disasterElement.innerHTML = `
                <div class="disaster-type">${this.formatDisasterType(disaster.type)}</div>
                <div class="disaster-severity severity-${disaster.severity}">${disaster.severity.toUpperCase()}</div>
                <div class="disaster-casualties">${disaster.casualties} casualties</div>
                <div class="disaster-location">Location: (${disaster.location[0]}, ${disaster.location[1]})</div>
            `;
            disastersList.appendChild(disasterElement);
        });
    }
    
    updateAIDecisions() {
        const decisionsLog = document.getElementById('decisionsLog');
        
        // Generate sample AI decisions based on simulation state
        const decisions = this.generateAIDecisions();
        
        decisionsLog.innerHTML = '';
        
        if (decisions.length === 0) {
            decisionsLog.innerHTML = '<div class="no-data">No AI decisions yet</div>';
            return;
        }
        
        decisions.forEach((decision, index) => {
            const decisionElement = document.createElement('div');
            decisionElement.className = 'decision-item';
            decisionElement.innerHTML = `
                <div class="decision-action">${decision.action}</div>
                <div class="decision-reasoning">${decision.reasoning}</div>
                <div class="decision-confidence">Confidence: ${Math.round(decision.confidence * 100)}%</div>
            `;
            decisionsLog.appendChild(decisionElement);
        });
    }
    
    generateAIDecisions() {
        const decisions = [];
        const metrics = this.simulationState.metrics || {};
        const disasters = this.simulationState.disasters || [];
        const rescueTeam = this.simulationState.rescue_team || {};
        
        // Generate decisions based on current state
        if (disasters.length > 0) {
            decisions.push({
                action: "Pathfinding to nearest victim",
                reasoning: `Rescue team moving to victim at high-risk location. Priority: ${disasters[0].priority_score.toFixed(2)}`,
                confidence: 0.85
            });
        }
        
        if (metrics.casualties_saved > 0) {
            decisions.push({
                action: "Victim rescue successful",
                reasoning: `Successfully rescued ${metrics.casualties_saved} victims using A* pathfinding`,
                confidence: 0.95
            });
        }
        
        if (rescueTeam.fatigue > 50) {
            decisions.push({
                action: "Team fatigue management",
                reasoning: `Rescue team fatigue at ${rescueTeam.fatigue}%. Considering rest period.`,
                confidence: 0.75
            });
        }
        
        if (metrics.response_efficiency > 0.5) {
            decisions.push({
                action: "High efficiency achieved",
                reasoning: `Response efficiency at ${(metrics.response_efficiency * 100).toFixed(1)}%. Optimal resource allocation.`,
                confidence: 0.90
            });
        }
        
        return decisions.slice(-5); // Show last 5 decisions
    }
    
    updateTeamsList() {
        const teamsList = document.getElementById('teamsList');
        const teams = this.simulationState.rescue_teams || [];
        
        teamsList.innerHTML = '';
        
        if (teams.length === 0) {
            teamsList.innerHTML = '<div class="no-data">No rescue teams</div>';
            return;
        }
        
        teams.forEach((team, index) => {
            const teamElement = document.createElement('div');
            teamElement.className = 'team-item';
            teamElement.innerHTML = `
                <div class="team-specialization">${this.formatSpecialization(team.specialization)}</div>
                <div class="team-status">Position: (${team.position[0]}, ${team.position[1]})</div>
                <div class="team-efficiency">Efficiency: ${Math.round(team.efficiency * 100)}%</div>
                <div class="team-fatigue">Fatigue: ${team.fatigue}/${team.max_fatigue || 100}</div>
            `;
            teamsList.appendChild(teamElement);
        });
    }
    
    updateResourceStatus() {
        const resourceList = document.getElementById('resourceList');
        const utilization = this.simulationState.resource_utilization || {};
        
        // Default resource data
        const globalResources = {
            'ambulances': 10,
            'fire_trucks': 5,
            'rescue_teams': 8,
            'medical_supplies': 500,
            'helicopters': 3,
            'boats': 4
        };
        
        resourceList.innerHTML = '';
        
        Object.entries(globalResources).forEach(([resourceType, total]) => {
            const utilized = utilization[resourceType] || 0;
            const percentage = (utilized / total) * 100;
            
            const resourceElement = document.createElement('div');
            resourceElement.className = 'resource-item';
            resourceElement.innerHTML = `
                <div>
                    <div class="resource-name">${this.formatResourceName(resourceType)}</div>
                    <div class="resource-value">${utilized}/${total}</div>
                    <div class="resource-bar">
                        <div class="resource-fill" style="width: ${percentage}%"></div>
                    </div>
                </div>
            `;
            resourceList.appendChild(resourceElement);
        });
    }
    
    updateCharts() {
        if (!this.simulationState) return;
        
        const metrics = this.simulationState.metrics || {};
        const performanceHistory = this.simulationState.performance_history || [];
        
        // Update performance chart
        if (this.charts.performance) {
            this.updatePerformanceChart(performanceHistory);
        }
        
        // Update resource chart
        if (this.charts.resource) {
            this.updateResourceChart(metrics);
        }
        
        // Update disaster chart
        if (this.charts.disaster) {
            this.updateDisasterChart(metrics);
        }
        
        // Update AI analytics chart
        if (this.charts.ai) {
            this.updateAIChart(metrics);
        }
    }
    
    initializeCharts() {
        // Performance Chart
        const performanceCtx = document.getElementById('performanceChart').getContext('2d');
        this.charts.performance = new Chart(performanceCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Response Efficiency',
                    data: [],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Casualties Saved',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#cbd5e1' }
                    }
                },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                }
            }
        });
        
        // Resource Chart
        const resourceCtx = document.getElementById('resourceChart').getContext('2d');
        this.charts.resource = new Chart(resourceCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#cbd5e1' }
                    }
                }
            }
        });
        
        // Disaster Chart
        const disasterCtx = document.getElementById('disasterChart').getContext('2d');
        this.charts.disaster = new Chart(disasterCtx, {
            type: 'bar',
            data: {
                labels: ['Active', 'Resolved', 'Total Impact'],
                datasets: [{
                    label: 'Disasters',
                    data: [],
                    backgroundColor: ['#ef4444', '#10b981', '#f59e0b']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#cbd5e1' }
                    }
                },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                }
            }
        });
        
        // AI Analytics Chart
        const aiCtx = document.getElementById('aiChart').getContext('2d');
        this.charts.ai = new Chart(aiCtx, {
            type: 'radar',
            data: {
                labels: ['Decision Accuracy', 'Response Time', 'Resource Efficiency', 'Casualty Reduction'],
                datasets: [{
                    label: 'AI Performance',
                    data: [],
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.2)',
                    pointBackgroundColor: '#8b5cf6'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#cbd5e1' }
                    }
                },
                scales: {
                    r: {
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#334155' },
                        pointLabels: { color: '#cbd5e1' }
                    }
                }
            }
        });
    }
    
    updatePerformanceChart(history) {
        // Generate sample data if no history
        const labels = [];
        const efficiencyData = [];
        const casualtiesData = [];
        
        if (history && history.length > 0) {
            for (let i = 0; i < history.length; i++) {
                labels.push(`Step ${i + 1}`);
                efficiencyData.push(history[i].response_efficiency || 0);
                casualtiesData.push(history[i].casualties_saved || 0);
            }
        } else {
            // Generate sample data
            const metrics = this.simulationState.metrics || {};
            for (let i = 0; i < 10; i++) {
                labels.push(`Step ${i + 1}`);
                efficiencyData.push((metrics.response_efficiency || 0) * (0.8 + Math.random() * 0.4));
                casualtiesData.push((metrics.casualties_saved || 0) * (0.5 + Math.random() * 0.5));
            }
        }
        
        this.charts.performance.data.labels = labels;
        this.charts.performance.data.datasets[0].data = efficiencyData;
        this.charts.performance.data.datasets[1].data = casualtiesData;
        this.charts.performance.update();
    }
    
    updateResourceChart(metrics) {
        const utilization = this.simulationState.resource_utilization || {};
        const labels = Object.keys(utilization);
        const data = Object.values(utilization);
        
        this.charts.resource.data.labels = labels;
        this.charts.resource.data.datasets[0].data = data;
        this.charts.resource.update();
    }
    
    updateDisasterChart(metrics) {
        const data = [
            metrics.active_disasters || 0,
            metrics.disasters_resolved || 0,
            metrics.total_casualties || 0
        ];
        
        this.charts.disaster.data.datasets[0].data = data;
        this.charts.disaster.update();
    }
    
    updateAIChart(metrics) {
        const data = [
            (metrics.decision_accuracy || 0) * 100,
            Math.max(0, 100 - (metrics.average_response_time || 0) * 10),
            (metrics.response_efficiency || 0) * 100,
            Math.min(100, (metrics.casualties_saved || 0) * 2)
        ];
        
        this.charts.ai.data.datasets[0].data = data;
        this.charts.ai.update();
    }
    
    drawGrid() {
        if (!this.gridCtx || !this.simulationState) return;
        
        const canvas = this.gridCanvas;
        const ctx = this.gridCtx;
        const gridSize = this.simulationState.grid_size || 20;
        const cellSize = Math.min(600, 600) / gridSize; // Fixed size for better display
        
        // Set canvas size
        canvas.width = 600;
        canvas.height = 600;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw grid
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
                    
                    // Terrain colors
                    let color = '#1f2937'; // Default
                    if (terrain === 'G') color = '#10b981'; // Green
                    else if (terrain === 'W') color = '#06b6d4'; // Water
                    else if (terrain === 'R') color = '#ef4444'; // Red/Urban
                    else if (terrain === 'U') color = '#6b7280'; // Urban
                    
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
                    
                    // Hazard overlay
                    ctx.fillStyle = `rgba(239, 68, 68, ${intensity})`;
                    ctx.fillRect(x + 2, y + 2, cellSize - 4, cellSize - 4);
                }
            });
        }
        
        // Draw victims
        if (this.simulationState.victims) {
            this.simulationState.victims.forEach(victim => {
                const [i, j] = victim;
                const x = j * cellSize;
                const y = i * cellSize;
                
                // Victim circle
                ctx.fillStyle = '#f59e0b';
                ctx.beginPath();
                ctx.arc(x + cellSize/2, y + cellSize/2, cellSize/4, 0, 2 * Math.PI);
                ctx.fill();
                
                // Victim border
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 2;
                ctx.stroke();
            });
        }
        
        // Draw resources with types
        if (this.simulationState.resources) {
            this.simulationState.resources.forEach(resource => {
                const [i, j, resourceType] = resource;
                const x = j * cellSize;
                const y = i * cellSize;
                
                // Resource color based on type
                const colors = {
                    'ambulance': '#ef4444',      // Red
                    'fire_truck': '#f59e0b',     // Orange
                    'rescue_team': '#3b82f6',    // Blue
                    'medical_supplies': '#10b981', // Green
                    'helicopter': '#8b5cf6',     // Purple
                    'boat': '#06b6d4',           // Cyan
                    'heavy_machinery': '#6b7280', // Gray
                    'emergency_shelter': '#f97316' // Orange-red
                };
                
                ctx.fillStyle = colors[resourceType] || '#10b981';
                ctx.fillRect(x + 3, y + 3, cellSize - 6, cellSize - 6);
                
                // Resource border
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 1;
                ctx.stroke();
                
                // Resource type label
                ctx.fillStyle = '#ffffff';
                ctx.font = '8px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(resourceType.charAt(0).toUpperCase(), x + cellSize/2, y + cellSize/2 + 3);
            });
        }
        
        // Draw rescue team
        if (this.simulationState.rescue_team) {
            const [i, j] = this.simulationState.rescue_team.position;
            const x = j * cellSize;
            const y = i * cellSize;
            
            // Rescue team circle
            ctx.fillStyle = '#3b82f6';
            ctx.beginPath();
            ctx.arc(x + cellSize/2, y + cellSize/2, cellSize/3, 0, 2 * Math.PI);
            ctx.fill();
            
            // Rescue team border
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.stroke();
        }
    }
    
    drawDisaster(disaster, cellSize) {
        const ctx = this.gridCtx;
        const x = disaster.location[1] * cellSize;
        const y = disaster.location[0] * cellSize;
        
        // Disaster color based on type
        const colors = {
            'earthquake': '#ef4444',
            'flood': '#06b6d4',
            'fire': '#f59e0b',
            'hurricane': '#8b5cf6',
            'tornado': '#64748b',
            'tsunami': '#0891b2'
        };
        
        ctx.fillStyle = colors[disaster.type] || '#ef4444';
        ctx.fillRect(x + 2, y + 2, cellSize - 4, cellSize - 4);
        
        // Severity indicator
        const severityColors = {
            'low': '#10b981',
            'medium': '#f59e0b',
            'high': '#ef4444',
            'critical': '#8b5cf6'
        };
        
        ctx.fillStyle = severityColors[disaster.severity] || '#ef4444';
        ctx.fillRect(x + 4, y + 4, cellSize - 8, 3);
        
        // Casualty count
        ctx.fillStyle = '#ffffff';
        ctx.font = '10px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(disaster.casualties.toString(), x + cellSize/2, y + cellSize/2 + 3);
    }
    
    drawRescueTeam(team, cellSize) {
        const ctx = this.gridCtx;
        const x = team.position[1] * cellSize;
        const y = team.position[0] * cellSize;
        
        // Team circle
        ctx.fillStyle = '#10b981';
        ctx.beginPath();
        ctx.arc(x + cellSize/2, y + cellSize/2, cellSize/3, 0, 2 * Math.PI);
        ctx.fill();
        
        // Team border
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Specialization indicator
        const specColors = {
            'search_rescue': '#ef4444',
            'medical': '#06b6d4',
            'fire_suppression': '#f59e0b',
            'water_rescue': '#0891b2',
            'logistics': '#64748b'
        };
        
        ctx.fillStyle = specColors[team.specialization] || '#10b981';
        ctx.fillRect(x + cellSize/2 - 2, y + cellSize/2 - 2, 4, 4);
    }
    
    drawResource(resource, cellSize) {
        const ctx = this.gridCtx;
        const x = resource.position[1] * cellSize;
        const y = resource.position[0] * cellSize;
        
        // Resource square
        ctx.fillStyle = '#f59e0b';
        ctx.fillRect(x + 3, y + 3, cellSize - 6, cellSize - 6);
        
        // Resource border
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.stroke();
    }
    
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }
    
    updateControlButtons() {
        const startBtn = document.getElementById('btnStart');
        const stopBtn = document.getElementById('btnStop');
        const pauseBtn = document.getElementById('btnPause');
        
        if (this.isRunning) {
            startBtn.disabled = true;
            stopBtn.disabled = false;
            pauseBtn.disabled = false;
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
            pauseBtn.disabled = true;
        }
        
        if (this.isPaused) {
            pauseBtn.innerHTML = '<i class="fas fa-play"></i> Resume';
        } else {
            pauseBtn.innerHTML = '<i class="fas fa-pause"></i> Pause';
        }
    }
    
    updateStatus() {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.getElementById('statusText');
        
        if (this.isRunning) {
            if (this.isPaused) {
                statusDot.className = 'status-dot warning';
                statusText.textContent = 'Paused';
            } else {
                statusDot.className = 'status-dot';
                statusText.textContent = 'Running';
            }
        } else {
            statusDot.className = 'status-dot';
            statusText.textContent = 'Ready';
        }
    }
    
    updateLastUpdateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        document.getElementById('lastUpdate').textContent = `Last Update: ${timeString}`;
    }
    
    handleGridClick(event) {
        if (!this.simulationState) return;
        
        const rect = this.gridCanvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const gridSize = this.simulationState.grid_size || 20;
        const cellSize = Math.min(this.gridCanvas.width, this.gridCanvas.height) / gridSize;
        
        const col = Math.floor(x / cellSize);
        const row = Math.floor(y / cellSize);
        
        if (row >= 0 && row < gridSize && col >= 0 && col < gridSize) {
            this.showInfo(`Clicked on cell (${row}, ${col})`);
            // Add custom logic for grid interactions here
        }
    }
    
    setupGridHover() {
        if (!this.gridCanvas) return;
        
        // Create tooltip element
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'grid-tooltip';
        this.tooltip.style.cssText = `
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            display: none;
            max-width: 200px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        `;
        document.body.appendChild(this.tooltip);
        
        // Add hover event listeners
        this.gridCanvas.addEventListener('mousemove', (e) => this.handleGridHover(e));
        this.gridCanvas.addEventListener('mouseleave', () => this.hideTooltip());
    }
    
    handleGridHover(event) {
        if (!this.simulationState) return;
        
        const rect = this.gridCanvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const gridSize = this.simulationState.grid_size || 20;
        const cellSize = Math.min(this.gridCanvas.width, this.gridCanvas.height) / gridSize;
        
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
            
            // Terrain information
            const terrainInfo = {
                'G': '🟢 Green Area - Safe zones and parks',
                'W': '🔵 Water - Rivers and lakes',
                'R': '🔴 Urban Red - High-risk urban areas',
                'U': '⚫ Urban - Urban infrastructure'
            };
            tooltipText += `Terrain: ${terrainInfo[terrain] || 'Unknown'}\n`;
            
            // Hazard information
            if (hazard) {
                tooltipText += `🌪️ Hazard Intensity: ${(hazard[2] * 100).toFixed(1)}%\n`;
            }
            
            // Victim information
            if (victim) {
                tooltipText += `🟠 Victim - Needs rescue\n`;
            }
            
            // Resource information
            if (resource) {
                const resourceType = resource[2] || 'unknown';
                const resourceNames = {
                    'ambulance': '🚑 Ambulance',
                    'fire_truck': '🚒 Fire Truck',
                    'rescue_team': '👥 Rescue Team',
                    'medical_supplies': '🏥 Medical Supplies',
                    'helicopter': '🚁 Helicopter',
                    'boat': '🚤 Boat',
                    'heavy_machinery': '🚜 Heavy Machinery',
                    'emergency_shelter': '🏠 Emergency Shelter'
                };
                tooltipText += `${resourceNames[resourceType] || '🟢 Resource'}\n`;
            }
            
            // Rescue team information
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
    
    handleKeyboard(event) {
        switch(event.key) {
            case ' ':
                event.preventDefault();
                if (this.isRunning) {
                    this.togglePause();
                } else {
                    this.startSimulation();
                }
                break;
            case 'r':
                if (event.ctrlKey) {
                    event.preventDefault();
                    this.resetSimulation();
                }
                break;
            case 'Escape':
                this.stopSimulation();
                break;
        }
    }
    
    zoomIn() {
        this.zoomLevel = Math.min(this.zoomLevel * 1.2, 3);
        this.updateGridSize();
    }
    
    zoomOut() {
        this.zoomLevel = Math.max(this.zoomLevel / 1.2, 0.5);
        this.updateGridSize();
    }
    
    updateGridSize() {
        const canvas = this.gridCanvas;
        const baseSize = 800;
        const newSize = baseSize * this.zoomLevel;
        
        canvas.width = newSize;
        canvas.height = newSize;
        this.drawGrid();
    }
    
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            this.gridCanvas.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }
    
    // Utility methods
    formatDisasterType(type) {
        return type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' ');
    }
    
    formatSpecialization(spec) {
        return spec.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    formatResourceName(name) {
        return name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    // Notification methods
    showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }
    
    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showInfo(message) {
        this.showNotification(message, 'info');
    }
    
    showNotification(message, type) {
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
            font-weight: 500;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        
        // Set background color based on type
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            info: '#06b6d4'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DisasterSimulationDashboard();
});

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .no-data {
        text-align: center;
        color: #94a3b8;
        font-style: italic;
        padding: 20px;
    }
`;
document.head.appendChild(style);
