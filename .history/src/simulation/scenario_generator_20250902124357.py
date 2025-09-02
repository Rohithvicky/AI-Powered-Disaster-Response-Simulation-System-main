"""
Scenario generator for creating random disaster environments
Generates hazards, victims, resources, and grid layouts
"""

import random
import math
from typing import Dict, List, Tuple, Any

class ScenarioGenerator:
    """Generates random disaster scenarios"""
    
    def __init__(self, config):
        self.config = config
        self.current_disaster_type = None
    
    def generate_grid(self, size: int) -> List[List[str]]:
        grid = []
        for i in range(size):
            row = []
            for j in range(size):
                terrain = self._generate_terrain(i, j, size)
                row.append(terrain)
            grid.append(row)
        return grid
    
    def _generate_terrain(self, i: int, j: int, size: int) -> str:
        center_distance = math.sqrt((i - size/2)**2 + (j - size/2)**2)
        if center_distance < size * 0.3:
            terrain_types = ['U', 'R', 'S']
            weights = [0.6, 0.3, 0.1]
        elif center_distance < size * 0.6:
            terrain_types = ['R', 'U', 'G']
            weights = [0.4, 0.4, 0.2]
        else:
            terrain_types = ['G', 'R', 'W']
            weights = [0.6, 0.3, 0.1]
        return random.choices(terrain_types, weights=weights)[0]
    
    def generate_hazards(self, size: int, disaster_type: str) -> Dict[Tuple[int, int], float]:
        self.current_disaster_type = disaster_type
        hazards = {}
        if disaster_type == "earthquake":
            hazards = self._generate_earthquake_hazards(size)
        elif disaster_type == "flood":
            hazards = self._generate_flood_hazards(size)
        elif disaster_type == "fire":
            hazards = self._generate_fire_hazards(size)
        elif disaster_type == "storm":
            hazards = self._generate_storm_hazards(size)
        else:
            hazards = self._generate_earthquake_hazards(size)
        return hazards
    
    def _generate_earthquake_hazards(self, size: int) -> Dict[Tuple[int, int], float]:
        hazards = {}
        epicenter = (random.randint(size//4, 3*size//4), random.randint(size//4, 3*size//4))
        for i in range(size):
            for j in range(size):
                distance = math.sqrt((i - epicenter[0])**2 + (j - epicenter[1])**2)
                if distance < size * 0.3:
                    intensity = max(0.1, 1.0 - distance / (size * 0.3))
                    if random.random() < 0.8:
                        hazards[(i, j)] = intensity
                elif distance < size * 0.6:
                    intensity = max(0.05, 0.5 - distance / (size * 0.6))
                    if random.random() < 0.5:
                        hazards[(i, j)] = intensity
        return hazards
    
    def _generate_flood_hazards(self, size: int) -> Dict[Tuple[int, int], float]:
        hazards = {}
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge in ['top', 'bottom']:
            flood_line = random.randint(size//4, 3*size//4)
            for i in range(size):
                for j in range(size):
                    if (edge == 'top' and i <= flood_line) or (edge == 'bottom' and i >= flood_line):
                        distance = abs(i - flood_line)
                        intensity = max(0.1, 1.0 - distance / (size * 0.4))
                        if random.random() < 0.7:
                            hazards[(i, j)] = intensity
        else:
            flood_line = random.randint(size//4, 3*size//4)
            for i in range(size):
                for j in range(size):
                    if (edge == 'left' and j <= flood_line) or (edge == 'right' and j >= flood_line):
                        distance = abs(j - flood_line)
                        intensity = max(0.1, 1.0 - distance / (size * 0.4))
                        if random.random() < 0.7:
                            hazards[(i, j)] = intensity
        return hazards
    
    def _generate_fire_hazards(self, size: int) -> Dict[Tuple[int, int], float]:
        hazards = {}
        num_sources = random.randint(2, 4)
        sources = [(random.randint(0, size-1), random.randint(0, size-1)) for _ in range(num_sources)]
        for i in range(size):
            for j in range(size):
                min_distance = min(math.sqrt((i - s[0])**2 + (j - s[1])**2) for s in sources)
                if min_distance < size * 0.4:
                    intensity = max(0.1, 1.0 - min_distance / (size * 0.4))
                    if random.random() < 0.6:
                        hazards[(i, j)] = intensity
        return hazards
    
    def _generate_storm_hazards(self, size: int) -> Dict[Tuple[int, int], float]:
        hazards = {}
        storm_type = random.choice(['diagonal', 'horizontal', 'vertical'])
        if storm_type == 'diagonal':
            start = random.randint(0, size//2)
            for i in range(size):
                for j in range(size):
                    if abs(i - j - start) < size * 0.2:
                        hazards[(i, j)] = random.uniform(0.3, 0.8)
        elif storm_type == 'horizontal':
            line = random.randint(size//4, 3*size//4)
            for i in range(size):
                for j in range(size):
                    if abs(i - line) < size * 0.15:
                        hazards[(i, j)] = random.uniform(0.4, 0.9)
        else:
            line = random.randint(size//4, 3*size//4)
            for i in range(size):
                for j in range(size):
                    if abs(j - line) < size * 0.15:
                        hazards[(i, j)] = random.uniform(0.4, 0.9)
        return hazards

    def disaster_spread_bias(self, terrain: str) -> float:
        """Return spread multiplier based on disaster type and terrain.
        Higher values increase probability of spread.
        """
        t = self.current_disaster_type or 'earthquake'
        if t == 'flood':
            return 1.6 if terrain == 'W' else 1.1 if terrain == 'R' else 0.9
        if t == 'fire':
            return 1.6 if terrain == 'G' else 1.1 if terrain == 'U' else 0.8
        if t == 'earthquake':
            return 1.5 if terrain in ('U','S') else 1.0
        if t == 'storm':
            return 1.2
        return 1.0
    
    def generate_victims(self, size: int) -> List[Tuple[int, int]]:
        """Generate victim positions"""
        victims = []
        victim_count = random.randint(
            self.config.get("simulation", "victim_count_range", (5, 15))[0],
            self.config.get("simulation", "victim_count_range", (5, 15))[1]
        )
        
        # Avoid placing victims at the starting position (0, 0)
        available_positions = [(i, j) for i in range(size) for j in range(size) 
                             if (i, j) != (0, 0)]
        
        # Place victims randomly, avoiding duplicates
        victim_positions = random.sample(available_positions, min(victim_count, len(available_positions)))
        
        for pos in victim_positions:
            victims.append(pos)
        
        return victims
    
    def generate_resources(self, size: int) -> List[Tuple[int, int]]:
        """Generate resource positions"""
        resources = []
        resource_count = random.randint(
            self.config.get("simulation", "resource_count_range", (3, 8))[0],
            self.config.get("simulation", "resource_count_range", (3, 8))[1]
        )
        
        # Avoid placing resources at the starting position
        available_positions = [(i, j) for i in range(size) for j in range(size) 
                             if (i, j) != (0, 0)]
        
        # Place resources randomly, avoiding duplicates
        resource_positions = random.sample(available_positions, min(resource_count, len(available_positions)))
        
        for pos in resource_positions:
            resources.append(pos)
        
        return resources
    
    def generate_disaster_scenario(self, size: int) -> Dict[str, Any]:
        """Generate a complete disaster scenario"""
        disaster_type = random.choice(self.config.get("simulation", "disaster_types", ["earthquake"]))
        
        return {
            'grid': self.generate_grid(size),
            'hazards': self.generate_hazards(size, disaster_type),
            'victims': self.generate_victims(size),
            'resources': self.generate_resources(size),
            'disaster_type': disaster_type,
            'severity': random.choice(['low', 'medium', 'high'])
        }
