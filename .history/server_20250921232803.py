"""
AI Disaster Response Simulation System - Compressed Version
All-in-one server with integrated simulation logic
"""

import random
import math
import json
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class RescueTeam:
    position: Tuple[int, int]
    resources: int
    efficiency: float = 1.0
    fatigue: float = 0.0

@dataclass
class SimulationState:
    time_step: int
    grid_size: int
    grid: List[List[str]]
    hazards: Dict[Tuple[int, int], float]
    victims: List[Tuple[int, int]]
    resources: List[Tuple[int, int, str]]
    rescue_team: RescueTeam
    disaster_type: str = "earthquake"

# ============================================================================
# SIMULATION LOGIC
# ============================================================================

class DisasterSimulator:
    def __init__(self, grid_size: int = 20):
        self.grid_size = grid_size
        self.state: Optional[SimulationState] = None
        self.stats = {
            'victims_saved': 0, 'resources_used': 0, 'time_steps': 0,
            'total_risk': 0.0, 'efficiency_score': 0.0, 'initial_victims': 0,
            'initial_resources': 0, 'disaster_type': 'earthquake'
        }
        self.telemetry = {
            'risk_history': [], 'victims_saved_history': [], 'remaining_history': [],
            'resources_used_history': []
        }
        self.reset()

    def reset(self):
        """Generate new single disaster scenario"""
        disaster_types = ["earthquake", "fire", "flood", "hurricane", "tornado"]
        disaster_type = random.choice(disaster_types)
        
        # Generate grid
        grid = self._generate_grid()
        hazards = self._generate_hazards(disaster_type)
        victims = self._generate_victims()
        resources = self._generate_resources(disaster_type)
        
        self.state = SimulationState(
            time_step=0, grid_size=self.grid_size, grid=grid,
            hazards=hazards, victims=victims, resources=resources,
            rescue_team=RescueTeam((0, 0), 10), disaster_type=disaster_type
        )
        
        self.stats = {
            'victims_saved': 0, 'resources_used': 0, 'time_steps': 0,
            'total_risk': sum(hazards.values()), 'efficiency_score': 0.0,
            'initial_victims': len(victims), 'initial_resources': len(resources),
            'disaster_type': disaster_type
        }
        self.telemetry = {
            'risk_history': [self.stats['total_risk']], 'victims_saved_history': [0],
            'remaining_history': [len(victims)], 'resources_used_history': [0]
        }

    def _generate_grid(self) -> List[List[str]]:
        """Generate terrain grid"""
        grid = []
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                center_dist = math.sqrt((i - self.grid_size/2)**2 + (j - self.grid_size/2)**2)
                if center_dist < self.grid_size * 0.3:
                    terrain = random.choices(['U', 'R', 'S'], weights=[0.6, 0.3, 0.1])[0]
                elif center_dist < self.grid_size * 0.6:
                    terrain = random.choices(['R', 'U', 'G'], weights=[0.4, 0.4, 0.2])[0]
                else:
                    terrain = random.choices(['G', 'R', 'W'], weights=[0.6, 0.3, 0.1])[0]
                row.append(terrain)
            grid.append(row)
        return grid

    def _generate_hazards(self, disaster_type: str) -> Dict[Tuple[int, int], float]:
        """Generate hazards based on disaster type"""
        hazards = {}
        if disaster_type == "earthquake":
            epicenter = (random.randint(self.grid_size//4, 3*self.grid_size//4),
                        random.randint(self.grid_size//4, 3*self.grid_size//4))
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    dist = math.sqrt((i - epicenter[0])**2 + (j - epicenter[1])**2)
                    if dist < self.grid_size * 0.3 and random.random() < 0.8:
                        intensity = max(0.1, 1.0 - dist / (self.grid_size * 0.3))
                        hazards[(i, j)] = intensity
        elif disaster_type == "fire":
            sources = [(random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)) 
                      for _ in range(random.randint(2, 4))]
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    min_dist = min(math.sqrt((i - s[0])**2 + (j - s[1])**2) for s in sources)
                    if min_dist < self.grid_size * 0.4 and random.random() < 0.6:
                        intensity = max(0.1, 1.0 - min_dist / (self.grid_size * 0.4))
                        hazards[(i, j)] = intensity
        elif disaster_type == "flood":
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            flood_line = random.randint(self.grid_size//4, 3*self.grid_size//4)
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if ((edge in ['top', 'bottom'] and 
                         ((edge == 'top' and i <= flood_line) or (edge == 'bottom' and i >= flood_line))) or
                        (edge in ['left', 'right'] and 
                         ((edge == 'left' and j <= flood_line) or (edge == 'right' and j >= flood_line)))):
                        dist = abs(i - flood_line) if edge in ['top', 'bottom'] else abs(j - flood_line)
                        intensity = max(0.1, 1.0 - dist / (self.grid_size * 0.4))
                        if random.random() < 0.7:
                            hazards[(i, j)] = intensity
        return hazards

    def _generate_victims(self) -> List[Tuple[int, int]]:
        """Generate victim positions"""
        count = random.randint(5, 15)
        positions = [(i, j) for i in range(self.grid_size) for j in range(self.grid_size) 
                    if (i, j) != (0, 0)]
        return random.sample(positions, min(count, len(positions)))

    def _generate_resources(self, disaster_type: str) -> List[Tuple[int, int, str]]:
        """Generate disaster-specific resources"""
        resource_map = {
            "earthquake": {"ambulance": 3, "rescue_team": 2, "medical_supplies": 4, "heavy_machinery": 1},
            "fire": {"fire_truck": 4, "rescue_team": 2, "medical_supplies": 3, "helicopter": 1},
            "flood": {"boat": 3, "helicopter": 2, "rescue_team": 3, "medical_supplies": 4},
            "hurricane": {"helicopter": 3, "rescue_team": 4, "medical_supplies": 5, "emergency_shelter": 2},
            "tornado": {"rescue_team": 3, "medical_supplies": 4, "ambulance": 2, "heavy_machinery": 1}
        }
        
        resources = []
        resource_types = resource_map.get(disaster_type, {"rescue_team": 2, "medical_supplies": 3})
        
        for resource_type, count in resource_types.items():
            for _ in range(count):
                positions = [(i, j) for i in range(self.grid_size) for j in range(self.grid_size) 
                           if (i, j) != (0, 0)]
                if positions:
                    pos = random.choice(positions)
                    resources.append((pos[0], pos[1], resource_type))
        
        return resources

    def step(self) -> Dict[str, Any]:
        """Advance simulation one step"""
        if not self.state:
            self.reset()
        
        self.state.time_step += 1
        self.stats['time_steps'] += 1
        
        # Update hazards (spread)
        self._update_hazards()
        
        # AI moves rescue team toward nearest victim
        self._ai_move()
        
        # Check for rescues
        self._check_rescues()
        
        # Update metrics
        self._update_metrics()
        
        return {"message": f"Step {self.state.time_step} completed"}

    def _update_hazards(self):
        """Spread existing hazards"""
        new_hazards = self.state.hazards.copy()
        for (r, c), intensity in self.state.hazards.items():
            if intensity > 0.3:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                            new_intensity = intensity * random.uniform(0.7, 0.9)
                            new_hazards[(nr, nc)] = max(new_hazards.get((nr, nc), 0), new_intensity)
        self.state.hazards = {k: v for k, v in new_hazards.items() if v > 0.1}

    def _ai_move(self):
        """AI moves rescue team toward nearest victim with resource usage tracking"""
        if not self.state.victims:
            return
        
        team_pos = self.state.rescue_team.position
        nearest_victim = min(self.state.victims, 
                           key=lambda v: math.sqrt((team_pos[0] - v[0])**2 + (team_pos[1] - v[1])**2))
        
        # Simple pathfinding: move one step toward victim
        dr = 1 if nearest_victim[0] > team_pos[0] else -1 if nearest_victim[0] < team_pos[0] else 0
        dc = 1 if nearest_victim[1] > team_pos[1] else -1 if nearest_victim[1] < team_pos[1] else 0
        
        new_pos = (team_pos[0] + dr, team_pos[1] + dc)
        
        # Track resource movement
        self.stats['resource_movements'] = self.stats.get('resource_movements', [])
        self.stats['resource_movements'].append({
            'step': self.state.time_step,
            'resource': 'rescue_team',
            'from': team_pos,
            'to': new_pos,
            'action': 'moving_to_victim',
            'target': nearest_victim
        })
        if 0 <= new_pos[0] < self.grid_size and 0 <= new_pos[1] < self.grid_size:
            self.state.rescue_team.position = new_pos

    def _check_rescues(self):
        """Check if rescue team can rescue victims with resource usage tracking"""
        team_pos = self.state.rescue_team.position
        rescued = []
        for victim in self.state.victims:
            if victim == team_pos and self.state.rescue_team.resources > 0:
                self.state.rescue_team.resources -= 1
                self.stats['victims_saved'] += 1
                rescued.append(victim)
                
                # Track rescue operation with resource usage
                self.stats['rescue_operations'] = self.stats.get('rescue_operations', [])
                self.stats['rescue_operations'].append({
                    'step': self.state.time_step,
                    'victim': victim,
                    'rescuer': team_pos,
                    'resources_used': ['rescue_team', 'medical_supplies'],
                    'success': True
                })
                
                # Add used resources to the grid for visualization
                self._add_used_resources_to_grid(team_pos, ['medical_supplies'])
        
        for victim in rescued:
            self.state.victims.remove(victim)

    def _add_used_resources_to_grid(self, position, resource_types):
        """Add used resources to the grid for visualization"""
        for resource_type in resource_types:
            # Add the resource at the rescue location
            self.state.resources.append((position[0], position[1], f"used_{resource_type}"))

    def _update_metrics(self):
        """Update simulation statistics"""
        total_risk = sum(self.state.hazards.values())
        self.stats['total_risk'] += total_risk
        self.stats['efficiency_score'] = (self.stats['victims_saved'] / 
                                        max(1, self.stats['resources_used'] + self.stats['time_steps']))
        
        self.telemetry['risk_history'].append(total_risk)
        self.telemetry['victims_saved_history'].append(self.stats['victims_saved'])
        self.telemetry['remaining_history'].append(len(self.state.victims))
        self.telemetry['resources_used_history'].append(self.stats['resources_used'])

    def serialize_state(self) -> Dict[str, Any]:
        """Convert state to JSON-serializable format"""
        if not self.state:
            return {}
        
        return {
            "time_step": self.state.time_step,
            "grid_size": self.state.grid_size,
            "grid": self.state.grid,
            "hazards": [[r, c, intensity] for (r, c), intensity in self.state.hazards.items()],
            "victims": self.state.victims,
            "resources": self.state.resources,
            "rescue_team": {
                "position": self.state.rescue_team.position,
                "resources": self.state.rescue_team.resources,
                "efficiency": self.state.rescue_team.efficiency,
                "fatigue": self.state.rescue_team.fatigue
            },
            "disaster_type": self.state.disaster_type,
            "metrics": self.stats,
            "telemetry": self.telemetry
        }

# ============================================================================
# FASTAPI SERVER
# ============================================================================

app = FastAPI(title="AI Disaster Response Simulation")
simulator = DisasterSimulator()

@app.on_event("startup")
async def startup():
    print("🚀 AI Disaster Response Simulation System initialized")

@app.get("/")
async def serve_index():
    return FileResponse("web/index.html")

@app.get("/api/state")
async def get_state():
    return {"state": simulator.serialize_state()}

@app.post("/api/reset")
async def reset_simulation():
    simulator.reset()
    return {"message": "Simulation reset", "state": simulator.serialize_state()}

@app.post("/api/step")
async def step_simulation():
    result = simulator.step()
    return {"result": result, "state": simulator.serialize_state()}

@app.post("/api/move")
async def move_team(data: dict):
    r, c = data.get("r", 0), data.get("c", 0)
    if 0 <= r < simulator.grid_size and 0 <= c < simulator.grid_size:
        simulator.state.rescue_team.position = (r, c)
        simulator._check_rescues()
        return {"ok": True, "message": f"Moved to ({r},{c})"}
    return {"ok": False, "message": "Invalid coordinates"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "disaster_type": simulator.state.disaster_type if simulator.state else "none"}

# Mount static files
app.mount("/", StaticFiles(directory="web", html=True), name="static")

if __name__ == "__main__":
    print("🚀 Starting AI Disaster Response Simulation Server...")
    print("📊 Professional Dashboard: http://localhost:8000")
    print("🔧 API Documentation: http://localhost:8000/docs")
    print("⚡ Server running on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
