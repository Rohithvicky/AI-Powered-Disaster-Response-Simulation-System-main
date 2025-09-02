"""
Step-based web simulator wrapper for disaster response
Reuses scenario generator, heuristic search, and rescue team logic
"""

from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import random
import math

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
        # Telemetry histories for charts
        self.telemetry: Dict[str, List[Any]] = {
            'risk_history': [],
            'victims_saved_history': [],
            'remaining_history': [],
            'resources_used_history': [],
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
        self.telemetry = {
            'risk_history': [self.stats['total_risk']],
            'victims_saved_history': [0],
            'remaining_history': [len(victims)],
            'resources_used_history': [0],
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
        return {'done': done, 'state': self.serialize_state(), 'stats': self.stats, 'telemetry': self.telemetry}

    def serialize_state(self) -> Dict[str, Any]:
        s = self.state
        return {
            'time_step': s.time_step,
            'grid_size': s.grid_size,
            'grid': s.grid,
            'hazards': [[i, j, float(self.state.hazards.get((i, j), 0.0))] for i in range(s.grid_size) for j in range(s.grid_size) if (i, j) in self.state.hazards],
            'victims': s.victims,
            'resources': s.resources,
            'rescue_team': {'position': s.rescue_team.position, 'resources': s.rescue_team.resources, 'efficiency': s.rescue_team.efficiency, 'fatigue': s.rescue_team.fatigue},
            'survival_probabilities': self._survival_probabilities(),
        }

    def move_team(self, i: int, j: int) -> bool:
        if not self.state:
            return False
        return self.state.rescue_team.move_to((i, j))

    def collect_here(self) -> Dict[str, Any]:
        pos = self.state.rescue_team.position
        if pos in self.state.resources:
            self.state.resources.remove(pos)
            self.state.rescue_team.collect_resource(2)
            return {'ok': True, 'message': 'Collected resources'}
        return {'ok': False, 'message': 'No resources here'}

    def rescue_here(self) -> Dict[str, Any]:
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

    def recommend_path_to_nearest_victim(self) -> Dict[str, Any]:
        if not self.state or not self.state.victims:
            return { 'path': [], 'length': 0, 'risk': 0.0, 'expected_survival': 0.0 }
        start = self.state.rescue_team.position
        target = min(self.state.victims, key=lambda v: self.astar.manhattan_distance(start, v))
        path = self.astar.find_path(start, target, self.state.hazards)
        if not path:
            path = self.best_first.find_path(start, target, self.state.hazards) or []
        # Compute path risk as sum of hazard intensity along the path
        risk = sum(self.state.hazards.get(p, 0.0) for p in path)
        # Estimate survival probability for target
        expected_survival = self._survival_for_victim(target, arrival_steps=max(0, len(path)-1))
        return { 'path': path, 'length': len(path), 'risk': risk, 'expected_survival': expected_survival, 'target': target }

    def risk_at(self, i: int, j: int) -> float:
        return float(self.state.hazards.get((i, j), 0.0)) if self.state else 0.0

    def _survival_probabilities(self) -> List[Tuple[int, int, float]]:
        probs: List[Tuple[int, int, float]] = []
        for v in self.state.victims:
            probs.append((v[0], v[1], self._survival_for_victim(v)))
        return probs

    def _survival_for_victim(self, victim: Tuple[int, int], arrival_steps: int = 0) -> float:
        # Distance component
        dist = self.astar.manhattan_distance(self.state.rescue_team.position, victim)
        # Hazard intensity at victim
        hz = self.state.hazards.get(victim, 0.0)
        # Time delay (current time + arrival)
        delay = self.state.time_step + arrival_steps
        # Simple Bayesian-inspired combination using exponentials
        base = 0.9 * math.exp(-0.08 * dist) * (1 - 0.6 * hz)
        decay = math.exp(-0.03 * delay)
        prob = max(0.0, min(1.0, base * decay))
        return prob

    def summary(self) -> Dict[str, Any]:
        survivors_remaining = max(0, self.stats['initial_victims'] - self.stats['victims_saved'])
        time_eff = (self.stats['victims_saved'] / max(1, (self.stats['resources_used'] + self.stats['time_steps'])))
        # Align efficiency metric with prompt
        eff_prompt = time_eff
        survival_probs = self.bayes.get_conditional_probability('survival_probability', {'disaster_severity': 'medium'})
        return {
            'initial_victims': self.stats['initial_victims'],
            'victims_saved': self.stats['victims_saved'],
            'victims_remaining': survivors_remaining,
            'resources_used': self.stats['resources_used'],
            'time_steps': self.stats['time_steps'],
            'efficiency_score': eff_prompt,
            'time_efficiency': time_eff,
            'survival_probability_reference': survival_probs,
        }

    def _update_hazards(self):
        new_haz = {}
        size = self.state.grid_size
        for (i, j), intensity in list(self.state.hazards.items()):
            # Terrain-aware spread based on disaster type
            if random.random() < 0.05:
                neighbors = self.astar.get_neighbors((i, j), self.state.hazards)
                for (ni, nj), _ in neighbors:
                    if (ni, nj) in self.state.hazards:
                        continue
                    terrain = self.state.grid[ni][nj]
                    bias = self.generator.disaster_spread_bias(terrain)
                    # Higher bias -> higher chance to ignite/spread
                    if random.random() < 0.25 * bias:
                        new_haz[(ni, nj)] = max(0.05, min(1.0, intensity * 0.6 * bias))
            # Existing hazards evolve
            change = random.uniform(-0.05, 0.08)
            new_haz[(i, j)] = max(0.0, min(1.0, intensity + change))
        self.state.hazards.update(new_haz)

    def _ai_act(self):
        if not self.state.victims:
            return
        path_info = self.recommend_path_to_nearest_victim()
        path = path_info['path']
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
        # Prompt-defined efficiency metric
        denom = max(1, (self.stats['resources_used'] + self.stats['time_steps']))
        self.stats['efficiency_score'] = self.stats['victims_saved'] / denom
        # Update telemetry histories
        remaining = max(0, self.stats['initial_victims'] - self.stats['victims_saved'])
        self.telemetry['risk_history'].append(total_risk)
        self.telemetry['victims_saved_history'].append(self.stats['victims_saved'])
        self.telemetry['remaining_history'].append(remaining)
        self.telemetry['resources_used_history'].append(self.stats['resources_used'])

    def _is_done(self) -> bool:
        if not self.state.victims:
            return True
        max_steps = self.config.get("simulation", "max_time_steps", 100)
        return self.state.time_step >= max_steps
