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
            # Higher initial survival probability - victims should be more resilient
            survival_prob = max(0.6, 1.0 - (injury_level - 1) * 0.08)  # Higher base survival
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
        """Update victim survival probabilities over time (much slower decrease)"""
        dead_victims = []
        
        for victim in self.state.victims:
            # Decrease survival probability based on time and hazard intensity (much slower)
            hazard_intensity = self.state.hazards.get(victim.position, 0)
            time_factor = self.state.time_step - victim.time_discovered
            
            # Much slower survival decrease - victims should last longer
            survival_decrease = (time_factor * 0.005) + (hazard_intensity * 0.02)  # Much reduced rates
            victim.survival_probability = max(0.0, victim.survival_probability - survival_decrease)
            
            # Critical victims (injury level 4-5) lose survival faster but still slowly
            if victim.injury_level >= 4:
                victim.survival_probability = max(0.0, victim.survival_probability - 0.01)  # Much reduced
            
            # Only mark victims as dead if survival probability is extremely low (almost impossible to rescue)
            if victim.survival_probability <= 0.01:  # Much lower threshold
                dead_victims.append(victim)
        
        # Remove dead victims from the simulation
        for dead_victim in dead_victims:
            self.state.victims.remove(dead_victim)
            print(f"💀 Victim at {dead_victim.position} has died (survival: {dead_victim.survival_probability:.2f})")

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
            print("No victims to rescue - mission complete!")
            return
        
        team_pos = self.state.rescue_team.position
        print(f"AI Move: Team at {team_pos}, {len(self.state.victims)} victims available")
        
        # Find the best victim using A* pathfinding
        best_victim, best_path = self._find_best_victim_with_path(team_pos)
        
        if not best_victim or not best_path:
            print("No viable victims or safe paths found, trying emergency escape")
            # No safe path to any victim, try emergency escape
            new_pos = self._emergency_escape(team_pos)
        else:
            print(f"Found path to victim at {best_victim.position}, path length: {len(best_path)}")
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
            'target': best_victim.position if best_victim else None,
            'path_length': len(best_path) if best_path else 0,
            'path_risk': self._calculate_path_risk(team_pos, best_victim.position) if best_victim else 0
        })
        
        # Move if the new position is valid
        if 0 <= new_pos[0] < self.grid_size and 0 <= new_pos[1] < self.grid_size:
            self.state.rescue_team.position = new_pos
            print(f"Rescue team moved from {team_pos} to {new_pos} (target: {best_victim.position if best_victim else None}, path length: {len(best_path) if best_path else 0})")

    def _check_rescues(self):
        """Check if rescue team can rescue victims with resource usage tracking"""
        team_pos = self.state.rescue_team.position
        rescued = []
        
        for victim in self.state.victims:
            if victim.position == team_pos and self.state.rescue_team.resources > 0:
                # Check if rescue is successful based on survival probability and team efficiency
                # Make rescue more likely - base success rate + survival bonus
                base_success_rate = 0.7  # 70% base success rate
                survival_bonus = victim.survival_probability * 0.3  # Up to 30% bonus
                rescue_success_rate = min(0.95, base_success_rate + survival_bonus)  # Cap at 95%
                
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

    def _find_best_victim_with_path(self, team_pos):
        """Find the best victim to rescue using A* pathfinding"""
        best_victim = None
        best_path = None
        best_cost = float('inf')
        
        for victim in self.state.victims:
            # Skip victims with very low survival probability (essentially dead)
            if victim.survival_probability < 0.1:
                continue
                
            path = self._astar_pathfinding(team_pos, victim.position)
            if path:
                # Calculate total cost considering path length, risk, urgency, and energy
                path_length = len(path)
                path_risk = self._calculate_path_risk(team_pos, victim.position)
                urgency_factor = 1.0 - victim.survival_probability  # Higher urgency for lower survival
                energy_factor = 1.0 - (self.state.rescue_team.energy / 100.0)  # Higher cost when low energy
                
                total_cost = path_length + (path_risk * 2.0) + (urgency_factor * 3.0) + (energy_factor * 1.0)
                
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_victim = victim
                    best_path = path
        
        return best_victim, best_path

    def _astar_pathfinding(self, start, goal):
        """A* pathfinding algorithm to find optimal path"""
        def get_cost(pos):
            r, c = pos
            if not (0 <= r < self.grid_size and 0 <= c < self.grid_size):
                return float('inf')
            
            # Base movement cost
            base_cost = 1.0
            
            # Hazard penalty (reduced for better pathfinding)
            hazard_cost = self.state.hazards.get(pos, 0) * 1.5
            
            # Terrain penalty
            terrain = self.state.grid[r][c]
            terrain_cost = 0
            if terrain == 'R':  # Rocky terrain
                terrain_cost = 0.5
            elif terrain == 'W':  # Water
                terrain_cost = 0.3
            
            return base_cost + hazard_cost + terrain_cost
        
        def heuristic(pos):
            return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        
        # A* algorithm
        import heapq
        open_set = [(heuristic(start), start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start)}
        closed_set = set()
        
        while open_set:
            current_f, current = heapq.heappop(open_set)
            
            if current in closed_set:
                continue
                
            closed_set.add(current)
            
            if current == goal:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return path[::-1]
            
            # Check all 8 directions
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    neighbor = (current[0] + dr, current[1] + dc)
                    
                    if not (0 <= neighbor[0] < self.grid_size and 0 <= neighbor[1] < self.grid_size):
                        continue
                    
                    if neighbor in closed_set:
                        continue
                    
                    tentative_g_score = g_score[current] + get_cost(neighbor)
                    
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = g_score[neighbor] + heuristic(neighbor)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        # Fallback to simple pathfinding if A* fails
        return self._find_simple_path(start, goal)

    def _find_simple_path(self, start, goal):
        """Simple greedy pathfinding as fallback"""
        path = [start]
        current = start
        
        while current != goal:
            # Try to move towards goal
            dr = 1 if goal[0] > current[0] else -1 if goal[0] < current[0] else 0
            dc = 1 if goal[1] > current[1] else -1 if goal[1] < current[1] else 0
            
            next_pos = (current[0] + dr, current[1] + dc)
            
            # If diagonal move is blocked, try horizontal or vertical
            if not (0 <= next_pos[0] < self.grid_size and 0 <= next_pos[1] < self.grid_size):
                if dr != 0:
                    next_pos = (current[0] + dr, current[1])
                elif dc != 0:
                    next_pos = (current[0], current[1] + dc)
                else:
                    break
            
            if not (0 <= next_pos[0] < self.grid_size and 0 <= next_pos[1] < self.grid_size):
                break
                
            current = next_pos
            path.append(current)
            
            # Prevent infinite loops
            if len(path) > self.grid_size * 2:
                break
        
        return path if current == goal else None

    def _calculate_path_risk(self, start, goal):
        """Calculate total risk along a path"""
        path = self._astar_pathfinding(start, goal)
        if not path:
            return float('inf')
        
        total_risk = 0
        for pos in path:
            total_risk += self.state.hazards.get(pos, 0)
        
        return total_risk

    def _emergency_escape(self, current_pos):
        """Find the safest adjacent cell when no path to victims exists"""
        safe_positions = []
        
        # Check all 8 directions
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_pos = (current_pos[0] + dr, current_pos[1] + dc)
                
                if 0 <= new_pos[0] < self.grid_size and 0 <= new_pos[1] < self.grid_size:
                    risk = self.state.hazards.get(new_pos, 0)
                    safe_positions.append((new_pos, risk))
        
        if not safe_positions:
            return current_pos
        
        # Sort by risk (safest first)
        safe_positions.sort(key=lambda x: x[1])
        
        # Return the safest position
        return safe_positions[0][0]

    def _get_available_resources_nearby(self, position):
        """Get available resources near a position"""
        nearby_resources = []
        for r, c, resource_type in self.state.resources:
            distance = abs(r - position[0]) + abs(c - position[1])
            if distance <= 2:  # Within 2 cells
                nearby_resources.append((r, c, resource_type))
        return nearby_resources

    def _select_resources_for_rescue(self, available_resources):
        """Select appropriate resources for rescue operation"""
        if not available_resources:
            return ["medical_supplies"]  # Default resource aligns with UI icons
        
        # Select 1-2 random resources from available ones
        num_resources = min(2, len(available_resources))
        selected = random.sample(available_resources, num_resources)
        return [resource[2] for resource in selected]  # Return resource types

    def _add_used_resources_at_victim_location(self, position, used_resources):
        """Add used resources at victim location for visualization"""
        # Ensure resources list exists
        if not isinstance(self.state.resources, list):
            self.state.resources = []

        r, c = position
        for res in used_resources:
            # Normalize resource key and add used_ marker
            normalized = res
            # Only allow known resource types
            allowed = {"ambulance", "fire_truck", "helicopter", "boat", "medical_supplies", "heavy_machinery"}
            if normalized not in allowed:
                normalized = "medical_supplies"
            used_key = f"used_{normalized}"
            self.state.resources.append((r, c, used_key))
            # Count usage in stats
            self.stats['resources_used'] = self.stats.get('resources_used', 0) + 1

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
            # Only expose used resources to the frontend to avoid clutter
            "resources": [
                (r, c, t) for (r, c, t) in self.state.resources
                if isinstance(t, str) and t.startswith('used_')
            ],
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
    nearest_victim = min(victims, key=lambda v: abs(v.position[0] - rescue_team.position[0]) + abs(v.position[1] - rescue_team.position[1]))
    
    # Generate path using A* pathfinding
    path = simulator._astar_pathfinding(rescue_team.position, nearest_victim.position)
    
    # Calculate path metrics
    path_length = len(path) if path else 0
    estimated_time = path_length * 2  # 2 seconds per step
    risk_level = simulator._calculate_path_risk(rescue_team.position, nearest_victim.position) if path else 0
    
    return {
        "path": path,
        "target_victim": nearest_victim.position,
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
