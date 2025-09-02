"""
Step-based web simulator wrapper for disaster response
Reuses scenario generator, heuristic search, and rescue team logic
"""

from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import random

from src.utils.config import Config
from src.simulation.scenario_generator import ScenarioGenerator
from src.simulation.rescue_team import RescueTeam
from src.models.heuristic_search import AStarSearch, BestFirstSearch
from src.models.probabilistic_reasoning import BayesianNetwork, RiskAssessment

@dataclass
class WebSimState:
    time_step: int
    grid_size: int
    grid: List[List[str]]
    hazards: Dict[Tuple[int, int], float]
    victims: List[Tuple[int, int]]
    resources: List[Tuple[int, int]]
    rescue_team: RescueTeam

class WebSimulator:
    """Step-based simulation suitable for web control"""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.generator = ScenarioGenerator(self.config)
        size = self.config.get("simulation", "grid_size", 20)
        self.astar = AStarSearch(size)
        self.best_first = BestFirstSearch(size)
        self.bayes = BayesianNetwork()
        self.risk = RiskAssessment(self.bayes)
        self.state: Optional[WebSimState] = None
        self.stats: Dict[str, Any] = {
            'victims_saved': 0,
            'resources_used': 0,
            'time_steps': 0,
            'total_risk': 0.0,
            'efficiency_score': 0.0,
            'initial_victims': 0,
            'initial_resources': 0,
        }
        self.reset()

    def reset(self):
        size = self.config.get("simulation", "grid_size", 20)
        disaster_type = random.choice(self.config.get("simulation", "disaster_types", ["earthquake"]))
        grid = self.generator.generate_grid(size)
        hazards = self.generator.generate_hazards(size, disaster_type)
        victims = self.generator.generate_victims(size)
        resources = self.generator.generate_resources(size)
        team = RescueTeam((0, 0), size)
        self.state = WebSimState(
            time_step=0,
            grid_size=size,
            grid=grid,
            hazards=hazards,
            victims=victims,
            resources=resources,
            rescue_team=team,
        )
        self.stats = {
            'victims_saved': 0,
            'resources_used': 0,
            'time_steps': 0,
            'total_risk': sum(hazards.values()),
            'efficiency_score': 0.0,
            'initial_victims': len(victims),
            'initial_resources': len(resources),
        }

    def step(self) -> Dict[str, Any]:
        if not self.state:
            self.reset()
        self.state.time_step += 1
        self.stats['time_steps'] += 1
        self._update_hazards()
        self._ai_act()
        self._check_rescues()
        self._update_metrics()
        done = self._is_done()
        return {'done': done, 'state': self.serialize_state(), 'stats': self.stats}

    def serialize_state(self) -> Dict[str, Any]:
        s = self.state
        return {
            'time_step': s.time_step,
            'grid_size': s.grid_size,
            'grid': s.grid,
            'hazards': [[i, j, float(self.state.hazards.get((i, j), 0.0))] for i in range(s.grid_size) for j in range(s.grid_size) if (i, j) in self.state.hazards],
            'victims': s.victims,
            'resources': s.resources,
            'rescue_team': {'position': s.rescue_team.position, 'resources': s.rescue_team.resources, 'efficiency': s.rescue_team.efficiency, 'fatigue': s.rescue_team.fatigue}
        }

    def move_team(self, i: int, j: int) -> bool:
        if not self.state:
            return False
        return self.state.rescue_team.move_to((i, j))

    def collect_here(self) -> Dict[str, Any]:
        """Collect resources at the team's current position if available."""
        pos = self.state.rescue_team.position
        if pos in self.state.resources:
            self.state.resources.remove(pos)
            self.state.rescue_team.collect_resource(2)
            return {'ok': True, 'message': 'Collected resources'}
        return {'ok': False, 'message': 'No resources here'}

    def rescue_here(self) -> Dict[str, Any]:
        """Attempt a rescue at the team's current position and update stats."""
        pos = self.state.rescue_team.position
        if pos not in self.state.victims:
            return {'ok': False, 'message': 'No victim here'}
        result = self.state.rescue_team.rescue_victim(pos, self.state.hazards)
        self.stats['resources_used'] += result.get('resources_used', 0)
        if result.get('success'):
            if pos in self.state.victims:
                self.state.victims.remove(pos)
            self.stats['victims_saved'] += 1
        return {'ok': result.get('success', False), 'detail': result}

    def recommend_path_to_nearest_victim(self) -> List[Tuple[int, int]]:
        if not self.state or not self.state.victims:
            return []
        start = self.state.rescue_team.position
        target = min(self.state.victims, key=lambda v: self.astar.manhattan_distance(start, v))
        path = self.astar.find_path(start, target, self.state.hazards)
        if not path:
            path = self.best_first.find_path(start, target, self.state.hazards) or []
        return path

    def risk_at(self, i: int, j: int) -> float:
        return float(self.state.hazards.get((i, j), 0.0)) if self.state else 0.0

    def summary(self) -> Dict[str, Any]:
        """Return a summary report of the current run with probabilistic context."""
        survivors_remaining = max(0, self.stats['initial_victims'] - self.stats['victims_saved'])
        time_eff = (self.stats['victims_saved'] / self.stats['time_steps']) if self.stats['time_steps'] else 0.0
        survival_probs = self.bayes.get_conditional_probability('survival_probability', {'disaster_severity': 'medium'})
        return {
            'initial_victims': self.stats['initial_victims'],
            'victims_saved': self.stats['victims_saved'],
            'victims_remaining': survivors_remaining,
            'resources_used': self.stats['resources_used'],
            'time_steps': self.stats['time_steps'],
            'efficiency_score': self.stats['efficiency_score'],
            'time_efficiency': time_eff,
            'survival_probability_reference': survival_probs,
        }

    def _update_hazards(self):
        new_haz = {}
        for (i, j), intensity in list(self.state.hazards.items()):
            if random.random() < 0.05:
                for (ni, nj), _ in self.astar.get_neighbors((i, j), self.state.hazards):
                    if (ni, nj) not in self.state.hazards and random.random() < 0.25:
                        new_haz[(ni, nj)] = max(0.05, intensity * 0.6)
            delta = random.uniform(-0.05, 0.08)
            new_haz[(i, j)] = max(0.0, min(1.0, intensity + delta))
        self.state.hazards.update(new_haz)

    def _ai_act(self):
        if not self.state.victims:
            return
        path = self.recommend_path_to_nearest_victim()
        if path and len(path) > 1:
            self.state.rescue_team.move_to(path[1])

    def _check_rescues(self):
        rescued = [v for v in self.state.victims if v == self.state.rescue_team.position]
        for v in rescued:
            self.state.victims.remove(v)
            self.stats['victims_saved'] += 1

    def _update_metrics(self):
        total_risk = sum(self.state.hazards.values())
        self.stats['total_risk'] = total_risk
        if self.stats['time_steps'] > 0:
            rate = self.stats['victims_saved'] / self.stats['time_steps']
            self.stats['efficiency_score'] = max(0.0, rate - total_risk * 0.05)

    def _is_done(self) -> bool:
        if not self.state.victims:
            return True
        max_steps = self.config.get("simulation", "max_time_steps", 100)
        return self.state.time_step >= max_steps
