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
            
            this.simulationState = await response.json();
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
            
            this.simulationState = await response.json();
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
        const globalResources = this.simulationState.global_resources || {};
        
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
        const labels = history.map((_, index) => `Step ${index + 1}`);
        const efficiencyData = history.map(h => h.response_efficiency || 0);
        const casualtiesData = history.map(h => h.casualties_saved || 0);
        
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
        const cellSize = Math.min(canvas.width, canvas.height) / gridSize;
        
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
        
        // Draw disasters
        const disasters = this.simulationState.disasters || [];
        disasters.forEach(disaster => {
            this.drawDisaster(disaster, cellSize);
        });
        
        // Draw rescue teams
        const teams = this.simulationState.rescue_teams || [];
        teams.forEach(team => {
            this.drawRescueTeam(team, cellSize);
        });
        
        // Draw resources
        const resources = this.simulationState.resources || [];
        resources.forEach(resource => {
            this.drawResource(resource, cellSize);
        });
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
