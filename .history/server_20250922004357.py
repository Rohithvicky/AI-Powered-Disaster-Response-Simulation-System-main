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
from contextlib import asynccontextmanager
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
    energy: float = 100.0  # Energy level (0-100)
    max_capacity: int = 3  # Max victims they can carry
    current_load: int = 0  # Current victims being carried
    status: str = "idle"  # idle, moving, rescuing, transporting

@dataclass
class Victim:
    position: Tuple[int, int]
    survival_probability: float = 1.0
    time_discovered: int = 0
    injury_level: int = 1  # 1-5 (1=minor, 5=critical)

@dataclass
class SimulationState:
    time_step: int
    grid_size: int
    grid: List[List[str]]
    hazards: Dict[Tuple[int, int], float]
    victims: List[Victim]
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
        """Generate hazards based on disaster type with consistent, clear patterns"""
        hazards = {}
        
        if disaster_type == "earthquake":
            # Earthquake: 2-3 clear epicenters with defined boundaries
            num_epicenters = random.randint(2, 3)
            for _ in range(num_epicenters):
                epicenter = (random.randint(3, self.grid_size-4), random.randint(3, self.grid_size-4))
                radius = random.randint(4, 7)
                for i in range(self.grid_size):
                    for j in range(self.grid_size):
                        dist = math.sqrt((i - epicenter[0])**2 + (j - epicenter[1])**2)
                        if dist <= radius and random.random() < 0.9:
                            intensity = max(0.3, 1.0 - (dist / radius) * 0.6)
                            hazards[(i, j)] = intensity
                            
        elif disaster_type == "fire":
            # Fire: 1-2 clear fire zones with strong boundaries
            num_fires = random.randint(1, 2)
            for _ in range(num_fires):
                center = (random.randint(4, self.grid_size-5), random.randint(4, self.grid_size-5))
                radius = random.randint(5, 8)
                for i in range(self.grid_size):
                    for j in range(self.grid_size):
                        dist = math.sqrt((i - center[0])**2 + (j - center[1])**2)
                        if dist <= radius and random.random() < 0.8:
                            intensity = max(0.2, 1.0 - (dist / radius) * 0.7)
                            hazards[(i, j)] = intensity
                            
        elif disaster_type == "flood":
            # Flood: clear flood zones from one edge
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            flood_depth = random.randint(3, 6)
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if edge == 'top' and i <= flood_depth:
                        intensity = max(0.2, 1.0 - (i / flood_depth) * 0.6)
                        if random.random() < 0.9:
                            hazards[(i, j)] = intensity
                    elif edge == 'bottom' and i >= self.grid_size - flood_depth:
                        intensity = max(0.2, 1.0 - ((self.grid_size - 1 - i) / flood_depth) * 0.6)
                        if random.random() < 0.9:
                            hazards[(i, j)] = intensity
                    elif edge == 'left' and j <= flood_depth:
                        intensity = max(0.2, 1.0 - (j / flood_depth) * 0.6)
                        if random.random() < 0.9:
                            hazards[(i, j)] = intensity
                    elif edge == 'right' and j >= self.grid_size - flood_depth:
                        intensity = max(0.2, 1.0 - ((self.grid_size - 1 - j) / flood_depth) * 0.6)
                        if random.random() < 0.9:
                            hazards[(i, j)] = intensity
                            
        elif disaster_type == "hurricane":
            # Hurricane: clear circular pattern with eye
            center = (random.randint(self.grid_size//3, 2*self.grid_size//3), 
                     random.randint(self.grid_size//3, 2*self.grid_size//3))
            radius = random.randint(6, 9)
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    dist = math.sqrt((i - center[0])**2 + (j - center[1])**2)
                    if dist <= radius and random.random() < 0.7:
                        if dist < radius * 0.2:
                            intensity = 0.1  # Eye (calm)
                        elif dist < radius * 0.4:
                            intensity = 1.0  # Eye wall (strongest)
                        else:
                            intensity = max(0.3, 0.8 - ((dist - radius * 0.4) / (radius * 0.6)) * 0.5)
                        hazards[(i, j)] = intensity
                        
        elif disaster_type == "tornado":
            # Tornado: clear spiral pattern
            center = (random.randint(self.grid_size//3, 2*self.grid_size//3), 
                     random.randint(self.grid_size//3, 2*self.grid_size//3))
            radius = random.randint(5, 7)
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    dist = math.sqrt((i - center[0])**2 + (j - center[1])**2)
                    if dist <= radius and random.random() < 0.8:
                        angle = math.atan2(j - center[1], i - center[0])
                        spiral_factor = abs(math.sin(angle * 2 + dist * 0.4))
                        intensity = max(0.3, (1.0 - dist / radius) * spiral_factor * 0.9)
                        hazards[(i, j)] = intensity
        else:
            # Default: clear scattered hazards
            num_hazards = random.randint(2, 4)
            for _ in range(num_hazards):
                center = (random.randint(3, self.grid_size-4), random.randint(3, self.grid_size-4))
                radius = random.randint(3, 5)
                for i in range(self.grid_size):
                    for j in range(self.grid_size):
                        dist = abs(i - center[0]) + abs(j - center[1])
                        if dist <= radius and random.random() < 0.9:
                            intensity = max(0.4, 1.0 - (dist / radius) * 0.5)
                            hazards[(i, j)] = intensity
                            
        return hazards

    def _generate_victims(self) -> List[Victim]:
        """Generate victims with survival probabilities and injury levels"""
        count = random.randint(5, 15)
        positions = [(i, j) for i in range(self.grid_size) for j in range(self.grid_size) 
                    if (i, j) != (0, 0)]
        selected_positions = random.sample(positions, min(count, len(positions)))
        
        victims = []
        for pos in selected_positions:
            # Random injury level (1-5)
            injury_level = random.randint(1, 5)
            # Initial survival probability based on injury level
            survival_prob = max(0.3, 1.0 - (injury_level - 1) * 0.15)
            victims.append(Victim(
                position=pos,
                survival_probability=survival_prob,
                time_discovered=0,
                injury_level=injury_level
            ))
        
        return victims

    def _generate_resources(self, disaster_type: str) -> List[Tuple[int, int, str]]:
        """Generate disaster-specific resources"""
        resource_map = {
            "earthquake": {"ambulance": 3, "medical_supplies": 4, "heavy_machinery": 1},
            "fire": {"fire_truck": 4, "medical_supplies": 3, "helicopter": 1},
            "flood": {"boat": 3, "helicopter": 2, "medical_supplies": 4},
            "hurricane": {"helicopter": 3, "medical_supplies": 5, "emergency_shelter": 2},
            "tornado": {"medical_supplies": 4, "ambulance": 2, "heavy_machinery": 1}
        }
        
        resources = []
        resource_types = resource_map.get(disaster_type, {"medical_supplies": 3})
        
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
        
        # Update victim survival probabilities
        self._update_victim_survival()
        
        # Update rescue team energy and fatigue
        self._update_rescue_team_status()
        
        # AI moves rescue team toward nearest victim
        self._ai_move()
        
        # Check for rescues
        self._check_rescues()
        
        # Update metrics
        self._update_metrics()
        
        return {"message": f"Step {self.state.time_step} completed"}

    def _update_hazards(self):
        """Spread existing hazards with realistic disaster behavior"""
        new_hazards = self.state.hazards.copy()
        
        # Calculate current hazard coverage for slowdown
        hazard_coverage = len(self.state.hazards) / (self.grid_size * self.grid_size)
        spread_slowdown_factor = max(0.2, 1.0 - hazard_coverage * 0.8)  # Slow down as coverage increases
        
        # Spread existing hazards (much slower)
        for (r, c), intensity in self.state.hazards.items():
            if intensity > 0.4:  # Only spread if hazard is significant
                # Spread to adjacent cells
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                            # Calculate spread probability based on intensity and terrain (much slower)
                            terrain = self.state.grid[nr][nc]
                            base_spread_prob = 0.3 if intensity > 0.7 else 0.15  # Much slower base rate
                            spread_prob = base_spread_prob * spread_slowdown_factor
                            
                            # Some terrains are more susceptible to certain disasters (reduced modifiers)
                            if self.state.disaster_type == 'fire' and terrain in ['G', 'U']:
                                spread_prob *= 1.1
                            elif self.state.disaster_type == 'flood' and terrain in ['G', 'U']:
                                spread_prob *= 1.05
                            elif self.state.disaster_type == 'earthquake' and terrain in ['U', 'R']:
                                spread_prob *= 1.15
                            
                            if random.random() < spread_prob:
                                new_intensity = intensity * random.uniform(0.4, 0.7)  # Slower intensity transfer
                            new_hazards[(nr, nc)] = max(new_hazards.get((nr, nc), 0), new_intensity)
        
        # Intensify existing hazards over time (slower changes)
        for pos in list(new_hazards.keys()):
            if new_hazards[pos] > 0.3:
                # Hazards can intensify or weaken randomly (smaller changes)
                change = random.uniform(-0.02, 0.05)
                new_hazards[pos] = max(0.1, min(1.0, new_hazards[pos] + change))
        
        # Remove very weak hazards
        self.state.hazards = {k: v for k, v in new_hazards.items() if v > 0.1}
        
        # Add new random hazards occasionally (much slower escalation)
        # Only add new hazards if coverage is still relatively low
        if hazard_coverage < 0.7:  # Only if less than 70% covered
            escalation_chance = max(0.005, 0.03 - hazard_coverage * 0.04)  # Much slower
            if random.random() < escalation_chance:
                self._add_random_hazard()

    def _update_victim_survival(self):
        """Update victim survival probabilities over time (slower decrease)"""
        for victim in self.state.victims:
            # Decrease survival probability based on time and hazard intensity (slower)
            hazard_intensity = self.state.hazards.get(victim.position, 0)
            time_factor = self.state.time_step - victim.time_discovered
            
            # Survival decreases with time and hazard intensity (much slower)
            survival_decrease = (time_factor * 0.01) + (hazard_intensity * 0.05)  # Reduced rates
            victim.survival_probability = max(0.0, victim.survival_probability - survival_decrease)
            
            # Critical victims (injury level 5) lose survival faster (but still slower)
            if victim.injury_level >= 4:
                victim.survival_probability = max(0.0, victim.survival_probability - 0.02)  # Reduced from 0.05

    def _update_rescue_team_status(self):
        """Update rescue team energy and fatigue"""
        team = self.state.rescue_team
        
        # Energy decreases with movement and rescue operations
        if team.status == "moving":
            team.energy = max(0, team.energy - 2)
        elif team.status == "rescuing":
            team.energy = max(0, team.energy - 5)
        elif team.status == "transporting":
            team.energy = max(0, team.energy - 3)
        
        # Fatigue increases as energy decreases
        team.fatigue = (100 - team.energy) / 100.0
        
        # Efficiency decreases with fatigue
        team.efficiency = max(0.3, 1.0 - (team.fatigue * 0.7))
        
        # Energy slowly recovers when idle
        if team.status == "idle" and team.energy < 100:
            team.energy = min(100, team.energy + 1)

    def _ai_move(self):
        """AI moves rescue team with advanced pathfinding to save all victims"""
        if not self.state.victims:
            return
        
        team_pos = self.state.rescue_team.position
        
        # Find the best victim using A* pathfinding
        best_victim, best_path = self._find_best_victim_with_path(team_pos)
        
        if not best_victim or not best_path:
            # No safe path to any victim, try emergency escape
            new_pos = self._emergency_escape(team_pos)
        else:
            # Move along the calculated path
            if len(best_path) > 1:
                new_pos = best_path[1]  # Next step in path
            else:
                new_pos = team_pos
        
        # Track resource movement
        self.stats['resource_movements'] = self.stats.get('resource_movements', [])
        self.stats['resource_movements'].append({
            'step': self.state.time_step,
            'resource': 'rescue_team',
            'from': team_pos,
            'to': new_pos,
            'action': 'moving_to_victim',
            'target': best_victim,
            'path_length': len(best_path) if best_path else 0,
            'path_risk': self._calculate_path_risk(team_pos, best_victim) if best_victim else 0
        })
        
        # Move if the new position is valid
        if 0 <= new_pos[0] < self.grid_size and 0 <= new_pos[1] < self.grid_size:
            self.state.rescue_team.position = new_pos
            print(f"Rescue team moved from {team_pos} to {new_pos} (target: {best_victim}, path length: {len(best_path) if best_path else 0})")

    def _check_rescues(self):
        """Check if rescue team can rescue victims with resource usage tracking"""
        team_pos = self.state.rescue_team.position
        rescued = []
        
        for victim in self.state.victims:
            if victim.position == team_pos and self.state.rescue_team.resources > 0:
                # Check if rescue is successful based on survival probability and team efficiency
                rescue_success_rate = victim.survival_probability * self.state.rescue_team.efficiency
                
                if random.random() < rescue_success_rate:
                self.state.rescue_team.resources -= 1
                self.stats['victims_saved'] += 1
                rescued.append(victim)
                    
                    # Update team status temporarily
                    self.state.rescue_team.status = "rescuing"
                    self.state.rescue_team.current_load += 1
                    
                    # Reset status after rescue to continue to next victim
                    self.state.rescue_team.status = "idle"
                
                # Determine which resources are available and used
                available_resources = self._get_available_resources_nearby(team_pos)
                used_resources = self._select_resources_for_rescue(available_resources)
                
                # Track rescue operation with specific resource usage
                self.stats['rescue_operations'] = self.stats.get('rescue_operations', [])
                self.stats['rescue_operations'].append({
                    'step': self.state.time_step,
                        'victim': victim.position,
                    'rescuer': team_pos,
                    'resources_used': used_resources,
                        'success': True,
                        'survival_probability': victim.survival_probability,
                        'injury_level': victim.injury_level
                })
                
                # Add used resources at the victim's location for visualization
                    self._add_used_resources_at_victim_location(victim.position, used_resources)
                    
                    print(f"🎉 VICTIM RESCUED at {victim.position} (survival: {victim.survival_probability:.2f}, injury: {victim.injury_level}) using resources: {used_resources}")
                else:
                    print(f"❌ RESCUE FAILED at {victim.position} (survival: {victim.survival_probability:.2f}, efficiency: {self.state.rescue_team.efficiency:.2f})")
        
        for victim in rescued:
            self.state.victims.remove(victim)

    def _get_available_resources_nearby(self, position):
        """Get resources available near the rescue team"""
        nearby_resources = []
        for resource in self.state.resources:
            r_pos = (resource[0], resource[1])
            if abs(r_pos[0] - position[0]) <= 2 and abs(r_pos[1] - position[1]) <= 2:
                if not resource[2].startswith('used_'):
                    nearby_resources.append(resource[2])
        return nearby_resources

    def _select_resources_for_rescue(self, available_resources):
        """Select which resources to use for rescue based on disaster type"""
        used_resources = ['rescue_team']  # Always use rescue team
        
        # Add medical supplies if available
        if 'medical_supplies' in available_resources:
            used_resources.append('medical_supplies')
        
        # Add disaster-specific resources
        if self.state.disaster_type == 'fire' and 'fire_truck' in available_resources:
            used_resources.append('fire_truck')
        elif self.state.disaster_type == 'flood' and 'boat' in available_resources:
            used_resources.append('boat')
        elif self.state.disaster_type == 'earthquake' and 'heavy_machinery' in available_resources:
            used_resources.append('heavy_machinery')
        elif self.state.disaster_type == 'hurricane' and 'helicopter' in available_resources:
            used_resources.append('helicopter')
        elif self.state.disaster_type == 'tornado' and 'ambulance' in available_resources:
            used_resources.append('ambulance')
        
        # If no specific resources available, add any available resource
        if len(used_resources) == 1 and available_resources:
            used_resources.append(available_resources[0])
        
        return used_resources

    def _add_used_resources_at_victim_location(self, victim_pos, resource_types):
        """Add used resources at the victim's location for visualization"""
        for resource_type in resource_types:
            if resource_type != 'rescue_team':  # Don't show rescue team as used resource
                # Add the resource at the victim's location
                self.state.resources.append((victim_pos[0], victim_pos[1], f"used_{resource_type}"))

    def _generate_path(self, start, end):
        """Generate a path from start to end using simple pathfinding"""
        path = [start]
        current = list(start)
        
        while current[0] != end[0] or current[1] != end[1]:
            if current[0] < end[0]:
                current[0] += 1
            elif current[0] > end[0]:
                current[0] -= 1
            elif current[1] < end[1]:
                current[1] += 1
            elif current[1] > end[1]:
                current[1] -= 1
            
            path.append(tuple(current))
        
        return path

    def _calculate_path_risk(self, start, end):
        """Calculate the risk level of a path from start to end"""
        total_risk = 0
        current = list(start)
        
        while current[0] != end[0] or current[1] != end[1]:
            if current[0] < end[0]:
                current[0] += 1
            elif current[0] > end[0]:
                current[0] -= 1
            elif current[1] < end[1]:
                current[1] += 1
            elif current[1] > end[1]:
                current[1] -= 1
            
            # Add risk for this position
            pos = tuple(current)
            if pos in self.state.hazards:
                total_risk += self.state.hazards[pos]
        
        return total_risk

    def _find_safe_path(self, start, end):
        """Find a safe path avoiding high-risk areas"""
        # Try direct path first
        dr = 1 if end[0] > start[0] else -1 if end[0] < start[0] else 0
        dc = 1 if end[1] > start[1] else -1 if end[1] < start[1] else 0
        
        new_pos = (start[0] + dr, start[1] + dc)
        
        # Check if this position is safe (low risk)
        if (0 <= new_pos[0] < self.grid_size and 0 <= new_pos[1] < self.grid_size and
            self.state.hazards.get(new_pos, 0) < 0.5):
            return new_pos
        
        # Try alternative directions if direct path is dangerous
        for dr_alt in [-1, 0, 1]:
            for dc_alt in [-1, 0, 1]:
                if dr_alt == 0 and dc_alt == 0:
                    continue
                alt_pos = (start[0] + dr_alt, start[1] + dc_alt)
                if (0 <= alt_pos[0] < self.grid_size and 0 <= alt_pos[1] < self.grid_size and
                    self.state.hazards.get(alt_pos, 0) < 0.3):
                    return alt_pos
        
        # If no safe path, return original position
        return start

    def _find_alternative_path(self, start, end):
        """Find alternative path when direct path is blocked"""
        # Try moving in different directions to get around obstacles
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            new_pos = (start[0] + dr, start[1] + dc)
            if (0 <= new_pos[0] < self.grid_size and 0 <= new_pos[1] < self.grid_size and
                self.state.hazards.get(new_pos, 0) < 0.7):  # Allow some risk
                return new_pos
        
        return start

    def _find_best_victim_with_path(self, start_pos):
        """Find the best victim using A* pathfinding algorithm"""
        best_victim = None
        best_path = None
        best_cost = float('inf')
        
        for victim in self.state.victims:
            path = self._astar_pathfinding(start_pos, victim.position)
            if path:
                # Calculate total cost (path length + risk + urgency)
                path_risk = sum(self.state.hazards.get(pos, 0) for pos in path[1:])
                
                # Urgency factor based on survival probability and injury level
                urgency_factor = (1.0 - victim.survival_probability) * 10 + victim.injury_level
                
                # Energy factor - prefer closer victims if team is tired
                energy_factor = 1.0 if self.state.rescue_team.energy > 50 else 1.5
                
                total_cost = (len(path) + path_risk) * energy_factor - urgency_factor
                
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_victim = victim.position
                    best_path = path
        
        return best_victim, best_path

    def _astar_pathfinding(self, start, goal):
        """A* pathfinding algorithm to find optimal path with safety fallback"""
        def heuristic(pos):
            return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        
        def get_neighbors(pos):
            neighbors = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    new_pos = (pos[0] + dr, pos[1] + dc)
                    if 0 <= new_pos[0] < self.grid_size and 0 <= new_pos[1] < self.grid_size:
                        neighbors.append(new_pos)
            return neighbors
        
        def get_cost(pos):
            # Cost based on hazard intensity (reduced penalty to allow more risk)
            hazard_cost = self.state.hazards.get(pos, 0)
            return 1 + hazard_cost * 1.5  # Reduced penalty from 2 to 1.5
        
        # A* algorithm
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start)}
        
        while open_set:
            open_set.sort()
            current = open_set.pop(0)[1]
            
            if current == goal:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path
            
            for neighbor in get_neighbors(current):
                tentative_g_score = g_score[current] + get_cost(neighbor)
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor)
                    
                    # Add to open set if not already there
                    if not any(item[1] == neighbor for item in open_set):
                        open_set.append((f_score[neighbor], neighbor))
        
        # If no optimal path found, try a simpler path with higher risk tolerance
        return self._find_simple_path(start, goal)
    
    def _find_simple_path(self, start, goal):
        """Find a simple path with higher risk tolerance when A* fails"""
        # Simple greedy pathfinding that accepts more risk
        current = start
        path = [current]
        max_steps = 50  # Prevent infinite loops
        
        for _ in range(max_steps):
            if current == goal:
                return path
            
            # Find best next step (closer to goal, accepting higher risk)
            best_next = current
            best_score = float('inf')
            
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    next_pos = (current[0] + dr, current[1] + dc)
                    if 0 <= next_pos[0] < self.grid_size and 0 <= next_pos[1] < self.grid_size:
                        # Distance to goal + risk (with lower risk penalty)
                        distance = abs(next_pos[0] - goal[0]) + abs(next_pos[1] - goal[1])
                        risk = self.state.hazards.get(next_pos, 0)
                        score = distance + risk * 0.5  # Much lower risk penalty
                        
                        if score < best_score:
                            best_score = score
                            best_next = next_pos
            
            if best_next == current:
                break  # Can't move further
                
            current = best_next
            path.append(current)
        
        return path if current == goal else None

    def _emergency_escape(self, current_pos):
        """Emergency escape when no safe path to victims exists - find safest area"""
        # Find the safest direction to move, prioritizing areas with no hazards
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        best_pos = current_pos
        lowest_risk = float('inf')
        
        # First, try to find a completely safe area (no hazards)
        for dr, dc in directions:
            new_pos = (current_pos[0] + dr, current_pos[1] + dc)
            if 0 <= new_pos[0] < self.grid_size and 0 <= new_pos[1] < self.grid_size:
                risk = self.state.hazards.get(new_pos, 0)
                if risk == 0:  # Completely safe area
                    return new_pos
                elif risk < lowest_risk:
                    lowest_risk = risk
                    best_pos = new_pos
        
        # If no safe area found, try to find the least hazardous area
        # Look for areas with very low hazard intensity
        for dr, dc in directions:
            new_pos = (current_pos[0] + dr, current_pos[1] + dc)
            if 0 <= new_pos[0] < self.grid_size and 0 <= new_pos[1] < self.grid_size:
                risk = self.state.hazards.get(new_pos, 0)
                if risk < 0.3:  # Low risk area
                    return new_pos
        
        return best_pos

    def _add_random_hazard(self):
        """Add a new random hazard to simulate disaster escalation"""
        # Find a random position not already hazardous
        attempts = 0
        while attempts < 50:
            r = random.randint(0, self.grid_size - 1)
            c = random.randint(0, self.grid_size - 1)
            if (r, c) not in self.state.hazards:
                # Add new hazard with moderate intensity
                intensity = random.uniform(0.3, 0.6)
                self.state.hazards[(r, c)] = intensity
                print(f"New hazard appeared at ({r}, {c}) with intensity {intensity:.2f}")
                break
            attempts += 1

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
            "victims": [
                {
                    "position": victim.position,
                    "survival_probability": victim.survival_probability,
                    "time_discovered": victim.time_discovered,
                    "injury_level": victim.injury_level
                }
                for victim in self.state.victims
            ],
            "resources": self.state.resources,
            "rescue_team": {
                "position": self.state.rescue_team.position,
                "resources": self.state.rescue_team.resources,
                "efficiency": self.state.rescue_team.efficiency,
                "fatigue": self.state.rescue_team.fatigue,
                "energy": self.state.rescue_team.energy,
                "max_capacity": self.state.rescue_team.max_capacity,
                "current_load": self.state.rescue_team.current_load,
                "status": self.state.rescue_team.status
            },
            "disaster_type": self.state.disaster_type,
            "metrics": self.stats,
            "telemetry": self.telemetry
        }

# ============================================================================
# FASTAPI SERVER
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 AI Disaster Response Simulation System initialized")
    yield
    # Shutdown
    print("🛑 AI Disaster Response Simulation System shutting down")

app = FastAPI(title="AI Disaster Response Simulation", lifespan=lifespan)
simulator = DisasterSimulator()

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

@app.post("/api/recommend")
async def recommend_path():
    """AI path recommendation endpoint"""
    if not simulator.state:
        return {"error": "No simulation state available"}
    
    rescue_team = simulator.state.rescue_team
    victims = simulator.state.victims
    
    if not victims:
        return {"error": "No victims to rescue"}
    
    # Find nearest victim using A* pathfinding
    nearest_victim = min(victims, key=lambda v: abs(v[0] - rescue_team.position[0]) + abs(v[1] - rescue_team.position[1]))
    
    # Generate path using simple pathfinding
    path = simulator._generate_path(rescue_team.position, nearest_victim)
    
    # Calculate path metrics
    path_length = len(path)
    estimated_time = path_length * 2  # 2 seconds per step
    risk_level = simulator._calculate_path_risk(path)
    
    return {
        "path": path,
        "target_victim": nearest_victim,
        "path_length": path_length,
        "estimated_time": estimated_time,
        "risk_level": risk_level,
        "confidence": 0.85
    }

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
    print("🔄 Auto-reload enabled - server will restart on file changes")
    try:
        uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Trying alternative startup method...")
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False, log_level="info")
