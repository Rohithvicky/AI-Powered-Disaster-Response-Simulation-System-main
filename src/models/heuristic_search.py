"""
Heuristic search algorithms for optimal pathfinding in disaster scenarios
Implements A* and Best-First Search algorithms
"""

import heapq
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import math

@dataclass
class SearchNode:
    """Node for search algorithms"""
    position: Tuple[int, int]
    g_cost: float  # Cost from start to current node
    h_cost: float  # Heuristic cost from current node to goal
    parent: Optional['SearchNode'] = None
    
    @property
    def f_cost(self) -> float:
        """Total cost (g + h)"""
        return self.g_cost + self.h_cost
    
    def __lt__(self, other):
        """Comparison for priority queue"""
        return self.f_cost < other.f_cost

class HeuristicSearch:
    """Base class for heuristic search algorithms"""
    
    def __init__(self, grid_size: int):
        self.grid_size = grid_size
        self.directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Cardinal directions
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonal directions
        ]
    
    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def euclidean_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two positions"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        """Check if position is within grid bounds"""
        return 0 <= pos[0] < self.grid_size and 0 <= pos[1] < self.grid_size
    
    def get_neighbors(self, pos: Tuple[int, int], hazards: Dict[Tuple[int, int], float]) -> List[Tuple[Tuple[int, int], float]]:
        """Get valid neighboring positions with movement costs"""
        neighbors = []
        for dx, dy in self.directions:
            new_pos = (pos[0] + dx, pos[1] + dy)
            if self.is_valid_position(new_pos):
                # Base movement cost
                cost = 1.0 if abs(dx) + abs(dy) == 1 else 1.4  # Diagonal costs more
                
                # Add hazard penalty
                hazard_level = hazards.get(new_pos, 0.0)
                cost += hazard_level * 2.0  # Hazards increase movement cost
                
                neighbors.append((new_pos, cost))
        
        return neighbors

class AStarSearch(HeuristicSearch):
    """A* search algorithm implementation"""
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                  hazards: Dict[Tuple[int, int], float]) -> Optional[List[Tuple[int, int]]]:
        """
        Find optimal path using A* algorithm
        
        Args:
            start: Starting position
            goal: Goal position
            hazards: Dictionary mapping positions to hazard levels (0.0 to 1.0)
        
        Returns:
            List of positions forming the optimal path, or None if no path found
        """
        if not self.is_valid_position(start) or not self.is_valid_position(goal):
            return None
        
        # Initialize open and closed sets
        open_set = []
        closed_set = set()
        
        # Create start node
        start_node = SearchNode(
            position=start,
            g_cost=0,
            h_cost=self.manhattan_distance(start, goal)
        )
        
        heapq.heappush(open_set, start_node)
        
        # Keep track of all nodes for path reconstruction
        all_nodes = {start: start_node}
        
        while open_set:
            current = heapq.heappop(open_set)
            
            if current.position == goal:
                return self._reconstruct_path(current)
            
            closed_set.add(current.position)
            
            # Explore neighbors
            for neighbor_pos, move_cost in self.get_neighbors(current.position, hazards):
                if neighbor_pos in closed_set:
                    continue
                
                new_g_cost = current.g_cost + move_cost
                
                if neighbor_pos not in all_nodes:
                    # New node
                    neighbor_node = SearchNode(
                        position=neighbor_pos,
                        g_cost=new_g_cost,
                        h_cost=self.manhattan_distance(neighbor_pos, goal),
                        parent=current
                    )
                    all_nodes[neighbor_pos] = neighbor_node
                    heapq.heappush(open_set, neighbor_node)
                else:
                    # Existing node - check if this path is better
                    neighbor_node = all_nodes[neighbor_pos]
                    if new_g_cost < neighbor_node.g_cost:
                        neighbor_node.g_cost = new_g_cost
                        neighbor_node.parent = current
                        # Re-heapify (in practice, you might want to use a more efficient approach)
                        heapq.heapify(open_set)
        
        return None  # No path found
    
    def _reconstruct_path(self, goal_node: SearchNode) -> List[Tuple[int, int]]:
        """Reconstruct path from goal node to start"""
        path = []
        current = goal_node
        
        while current:
            path.append(current.position)
            current = current.parent
        
        return path[::-1]  # Reverse to get start to goal order

class BestFirstSearch(HeuristicSearch):
    """Best-First Search algorithm implementation"""
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                  hazards: Dict[Tuple[int, int], float]) -> Optional[List[Tuple[int, int]]]:
        """
        Find path using Best-First Search algorithm
        
        Args:
            start: Starting position
            goal: Goal position
            hazards: Dictionary mapping positions to hazard levels
        
        Returns:
            List of positions forming the path, or None if no path found
        """
        if not self.is_valid_position(start) or not self.is_valid_position(goal):
            return None
        
        # Initialize open and closed sets
        open_set = []
        closed_set = set()
        
        # Create start node
        start_node = SearchNode(
            position=start,
            g_cost=0,
            h_cost=self.manhattan_distance(start, goal)
        )
        
        heapq.heappush(open_set, start_node)
        all_nodes = {start: start_node}
        
        while open_set:
            current = heapq.heappop(open_set)
            
            if current.position == goal:
                return self._reconstruct_path(current)
            
            closed_set.add(current.position)
            
            # Explore neighbors
            for neighbor_pos, move_cost in self.get_neighbors(current.position, hazards):
                if neighbor_pos in closed_set:
                    continue
                
                if neighbor_pos not in all_nodes:
                    # New node - only consider heuristic cost for Best-First Search
                    neighbor_node = SearchNode(
                        position=neighbor_pos,
                        g_cost=current.g_cost + move_cost,
                        h_cost=self.manhattan_distance(neighbor_pos, goal),
                        parent=current
                    )
                    all_nodes[neighbor_pos] = neighbor_node
                    heapq.heappush(open_set, neighbor_node)
        
        return None  # No path found
    
    def _reconstruct_path(self, goal_node: SearchNode) -> List[Tuple[int, int]]:
        """Reconstruct path from goal node to start"""
        path = []
        current = goal_node
        
        while current:
            path.append(current.position)
            current = current.parent
        
        return path[::-1]  # Reverse to get start to goal order
