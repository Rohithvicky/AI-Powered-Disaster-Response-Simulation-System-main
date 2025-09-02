"""
Rescue team management and decision-making
Handles team movement, resource usage, and strategic decisions
"""

from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
import random

@dataclass
class RescueTeam:
    """Represents a rescue team in the simulation"""
    position: Tuple[int, int]
    grid_size: int
    resources: int = 10
    max_resources: int = 10
    efficiency: float = 1.0
    fatigue: float = 0.0
    
    def move_to(self, new_position: Tuple[int, int]) -> bool:
        """Move the rescue team to a new position"""
        if self._is_valid_position(new_position):
            self.position = new_position
            self._update_fatigue(0.1)  # Moving increases fatigue
            return True
        return False
    
    def _is_valid_position(self, position: Tuple[int, int]) -> bool:
        """Check if a position is valid within the grid"""
        return (0 <= position[0] < self.grid_size and 
                0 <= position[1] < self.grid_size)
    
    def _update_fatigue(self, amount: float):
        """Update team fatigue level"""
        self.fatigue = max(0.0, min(1.0, self.fatigue + amount))
        
        # Fatigue affects efficiency
        self.efficiency = max(0.3, 1.0 - self.fatigue * 0.7)
    
    def rest(self) -> float:
        """Rest to reduce fatigue and restore efficiency"""
        fatigue_reduction = 0.2
        self.fatigue = max(0.0, self.fatigue - fatigue_reduction)
        
        # Efficiency recovers with rest
        self.efficiency = max(0.3, 1.0 - self.fatigue * 0.7)
        
        return fatigue_reduction
    
    def use_resource(self, amount: int = 1) -> bool:
        """Use team resources"""
        if self.resources >= amount:
            self.resources -= amount
            return True
        return False
    
    def collect_resource(self, amount: int = 1):
        """Collect resources"""
        self.resources = min(self.max_resources, self.resources + amount)
    
    def can_rescue_victim(self, victim_position: Tuple[int, int], 
                          hazards: Dict[Tuple[int, int], float]) -> bool:
        """Check if the team can rescue a victim at the given position"""
        # Check if team has enough resources
        if self.resources < 2:
            return False
        
        # Check if victim position is accessible
        if not self._is_valid_position(victim_position):
            return False
        
        # Check hazard level at victim position
        hazard_level = hazards.get(victim_position, 0.0)
        if hazard_level > 0.8:
            return False  # Too dangerous
        
        # Check team efficiency and fatigue
        if self.efficiency < 0.4 or self.fatigue > 0.8:
            return False
        
        return True
    
    def rescue_victim(self, victim_position: Tuple[int, int], 
                     hazards: Dict[Tuple[int, int], float]) -> Dict[str, Any]:
        """Attempt to rescue a victim"""
        if not self.can_rescue_victim(victim_position, hazards):
            return {
                'success': False,
                'reason': 'Cannot rescue victim under current conditions',
                'resources_used': 0,
                'time_taken': 0
            }
        
        # Calculate rescue difficulty based on hazard level
        hazard_level = hazards.get(victim_position, 0.0)
        base_difficulty = 1.0 + hazard_level * 2.0
        
        # Apply team efficiency
        adjusted_difficulty = base_difficulty / self.efficiency
        
        # Determine resources needed
        resources_needed = max(2, int(adjusted_difficulty))
        
        # Check if we have enough resources
        if self.resources < resources_needed:
            return {
                'success': False,
                'reason': 'Insufficient resources for rescue',
                'resources_used': 0,
                'time_taken': 0
            }
        
        # Attempt rescue
        success_probability = 0.8 * (1.0 - hazard_level) * self.efficiency
        
        if random.random() < success_probability:
            # Successful rescue
            self.use_resource(resources_needed)
            self._update_fatigue(0.3)  # Rescue is tiring
            
            return {
                'success': True,
                'reason': 'Victim rescued successfully',
                'resources_used': resources_needed,
                'time_taken': int(adjusted_difficulty * 2),
                'efficiency_gain': 0.05  # Small efficiency boost from success
            }
        else:
            # Failed rescue attempt
            self.use_resource(resources_needed // 2)  # Use some resources even if failed
            self._update_fatigue(0.2)
            
            return {
                'success': False,
                'reason': 'Rescue attempt failed',
                'resources_used': resources_needed // 2,
                'time_taken': int(adjusted_difficulty),
                'efficiency_loss': 0.02  # Small efficiency loss from failure
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current team status"""
        return {
            'position': self.position,
            'resources': self.resources,
            'max_resources': self.max_resources,
            'efficiency': self.efficiency,
            'fatigue': self.fatigue,
            'can_rescue': self.efficiency > 0.4 and self.fatigue < 0.8
        }
    
    def get_optimal_action(self, victims: List[Tuple[int, int]], 
                          resources: List[Tuple[int, int]], 
                          hazards: Dict[Tuple[int, int], float]) -> Dict[str, Any]:
        """Determine the optimal action for the rescue team"""
        actions = []
        
        # Action 1: Rescue nearest victim
        if victims:
            nearest_victim = self._find_nearest(victims)
            if nearest_victim and self.can_rescue_victim(nearest_victim, hazards):
                actions.append({
                    'type': 'rescue',
                    'target': nearest_victim,
                    'priority': 1.0,
                    'description': f'Rescue victim at {nearest_victim}'
                })
        
        # Action 2: Collect nearby resources
        if self.resources < self.max_resources * 0.7:  # If resources are low
            nearest_resource = self._find_nearest(resources)
            if nearest_resource:
                distance = self._manhattan_distance(self.position, nearest_resource)
                if distance <= 3:  # Only if very close
                    actions.append({
                        'type': 'collect',
                        'target': nearest_resource,
                        'priority': 0.8,
                        'description': f'Collect resource at {nearest_resource}'
                    })
        
        # Action 3: Rest if fatigue is high
        if self.fatigue > 0.6:
            actions.append({
                'type': 'rest',
                'target': None,
                'priority': 0.9,
                'description': 'Rest to reduce fatigue'
            })
        
        # Action 4: Move towards nearest victim if can't rescue yet
        if victims and not any(a['type'] == 'rescue' for a in actions):
            nearest_victim = self._find_nearest(victims)
            if nearest_victim:
                actions.append({
                    'type': 'move',
                    'target': nearest_victim,
                    'priority': 0.7,
                    'description': f'Move towards victim at {nearest_victim}'
                })
        
        # Sort actions by priority
        actions.sort(key=lambda x: x['priority'], reverse=True)
        
        return actions[0] if actions else {
            'type': 'wait',
            'target': None,
            'priority': 0.0,
            'description': 'Wait for better conditions'
        }
    
    def _find_nearest(self, positions: List[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """Find the nearest position from a list"""
        if not positions:
            return None
        
        nearest = None
        min_distance = float('inf')
        
        for pos in positions:
            distance = self._manhattan_distance(self.position, pos)
            if distance < min_distance:
                min_distance = distance
                nearest = pos
        
        return nearest
    
    def _manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def update_efficiency(self, change: float):
        """Update team efficiency"""
        self.efficiency = max(0.1, min(1.0, self.efficiency + change))
    
    def is_exhausted(self) -> bool:
        """Check if the team is exhausted"""
        return self.fatigue > 0.9 or self.efficiency < 0.2
    
    def can_continue_mission(self) -> bool:
        """Check if the team can continue the mission"""
        return (self.resources > 0 and 
                self.efficiency > 0.3 and 
                self.fatigue < 0.9)
