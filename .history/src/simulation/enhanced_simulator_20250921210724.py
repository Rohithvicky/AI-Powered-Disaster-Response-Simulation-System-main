from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import random
import time
from datetime import datetime, timedelta

from ..models.disaster import Disaster, DisasterManager, DisasterType, SeverityLevel
from ..models.ai_decision_engine import AIDecisionEngine, Decision, DecisionType
from ..models.probabilistic_reasoning import BayesianNetwork, RiskAssessment
from ..models.heuristic_search import AStarSearch, BestFirstSearch
from .scenario_generator import ScenarioGenerator
from .rescue_team import RescueTeam

@dataclass
class SimulationMetrics:
    """Comprehensive simulation metrics"""
    time_steps: int = 0
    total_casualties: int = 0
    casualties_saved: int = 0
    casualties_prevented: int = 0
    resources_used: int = 0
    resources_remaining: int = 0
    economic_impact: float = 0.0
    response_efficiency: float = 0.0
    decision_accuracy: float = 0.0
    evacuation_orders: int = 0
    emergency_responses: int = 0
    disasters_resolved: int = 0
    active_disasters: int = 0
    total_cost: float = 0.0
    average_response_time: float = 0.0

class EnhancedDisasterSimulator:
    """Enhanced disaster response simulation with comprehensive AI decision-making"""
    
    def __init__(self, grid_size: int = 20):
        self.grid_size = grid_size
        self.scenario_generator = ScenarioGenerator()
        self.disaster_manager = DisasterManager()
        self.ai_decision_engine = AIDecisionEngine()
        self.rescue_teams: List[RescueTeam] = []
        self.metrics = SimulationMetrics()
        self.simulation_start_time = None
        self.current_time = 0
        self.is_running = False
        self.auto_mode = False
        self.decision_history: List[Decision] = []
        self.performance_history: List[Dict] = []
        
        # Initialize rescue teams
        self._initialize_rescue_teams()
    
    def _initialize_rescue_teams(self):
        """Initialize rescue teams with different specializations"""
        team_specializations = [
            {"type": "search_rescue", "efficiency": 0.9, "max_fatigue": 100},
            {"type": "medical", "efficiency": 0.8, "max_fatigue": 80},
            {"type": "fire_suppression", "efficiency": 0.85, "max_fatigue": 90},
            {"type": "water_rescue", "efficiency": 0.75, "max_fatigue": 85},
            {"type": "logistics", "efficiency": 0.7, "max_fatigue": 70}
        ]
        
        for i, spec in enumerate(team_specializations):
            team = RescueTeam(
                position=(random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)),
                resources={"medical_supplies": 50, "equipment": 30},
                efficiency=spec["efficiency"],
                fatigue=0,
                specialization=spec["type"],
                max_fatigue=spec["max_fatigue"]
            )
            self.rescue_teams.append(team)
    
    def start_simulation(self, auto_mode: bool = False):
        """Start the simulation"""
        self.simulation_start_time = datetime.now()
        self.current_time = 0
        self.is_running = True
        self.auto_mode = auto_mode
        self.metrics = SimulationMetrics()
        
        # Generate initial disaster scenario
        self._generate_initial_scenario()
        
        print(f"🚨 Enhanced Disaster Response Simulation Started")
        print(f"📊 Grid Size: {self.grid_size}x{self.grid_size}")
        print(f"🤖 AI Mode: {'Automatic' if auto_mode else 'Interactive'}")
        print(f"👥 Rescue Teams: {len(self.rescue_teams)}")
        print(f"🌪️  Active Disasters: {len(self.disaster_manager.disasters)}")
    
    def _generate_initial_scenario(self):
        """Generate initial disaster scenario"""
        # Generate 1-3 random disasters
        num_disasters = random.randint(1, 3)
        
        for _ in range(num_disasters):
            disaster = self.disaster_manager.generate_random_disaster(self.grid_size)
            disaster.start_time = self.current_time
            self.disaster_manager.add_disaster(disaster)
        
        # Update metrics
        self.metrics.active_disasters = len(self.disaster_manager.disasters)
        self.metrics.total_casualties = sum(d.casualties for d in self.disaster_manager.disasters)
    
    def step_simulation(self) -> Dict[str, Any]:
        """Execute one simulation step"""
        if not self.is_running:
            return {"error": "Simulation not running"}
        
        self.current_time += 1
        self.metrics.time_steps = self.current_time
        
        # Update disasters
        self.disaster_manager.update_all_disasters(self.current_time)
        
        # Make AI decisions
        if self.auto_mode:
            self._execute_ai_decisions()
        
        # Update rescue teams
        self._update_rescue_teams()
        
        # Update metrics
        self._update_metrics()
        
        # Check for new disasters (random chance)
        if random.random() < 0.1:  # 10% chance per step
            self._spawn_new_disaster()
        
        return self._get_simulation_state()
    
    def _execute_ai_decisions(self):
        """Execute AI decision-making process"""
        # Get available resources
        available_resources = self._get_available_resources()
        
        # Make resource allocation decision
        allocation_decision = self.ai_decision_engine.make_resource_allocation_decision(
            self.disaster_manager, available_resources
        )
        
        if allocation_decision.resources_allocated:
            self._execute_resource_allocation(allocation_decision)
        
        # Make evacuation decision
        evacuation_decision = self.ai_decision_engine.make_evacuation_decision(self.disaster_manager)
        if evacuation_decision.action != "No action required":
            self._execute_evacuation(evacuation_decision)
            self.metrics.evacuation_orders += 1
        
        # Make emergency response decision
        emergency_decision = self.ai_decision_engine.make_emergency_response_decision(self.disaster_manager)
        if emergency_decision.action != "No action required":
            self._execute_emergency_response(emergency_decision)
            self.metrics.emergency_responses += 1
        
        # Store decisions
        self.decision_history.extend([
            allocation_decision, evacuation_decision, emergency_decision
        ])
    
    def _get_available_resources(self) -> Dict[str, int]:
        """Get currently available resources"""
        available = {}
        for resource_type, total in self.disaster_manager.global_resources.items():
            allocated = self.disaster_manager.allocated_resources[resource_type]
            available[resource_type] = total - allocated
        return available
    
    def _execute_resource_allocation(self, decision: Decision):
        """Execute resource allocation decision"""
        if decision.target_disaster_id is not None:
            success = self.disaster_manager.allocate_resources(
                decision.target_disaster_id,
                decision.resources_allocated
            )
            if success:
                self.metrics.resources_used += sum(decision.resources_allocated.values())
                self.metrics.total_cost += decision.cost
    
    def _execute_evacuation(self, decision: Decision):
        """Execute evacuation decision"""
        if decision.target_disaster_id is not None:
            disaster = self.disaster_manager.disasters[decision.target_disaster_id]
            # Simulate evacuation effectiveness
            evacuation_effectiveness = decision.expected_effectiveness
            casualties_reduced = int(disaster.casualties * evacuation_effectiveness * 0.3)
            disaster.casualties = max(0, disaster.casualties - casualties_reduced)
            self.metrics.casualties_prevented += casualties_reduced
    
    def _execute_emergency_response(self, decision: Decision):
        """Execute emergency response decision"""
        if decision.target_disaster_id is not None:
            disaster = self.disaster_manager.disasters[decision.target_disaster_id]
            # Simulate emergency response effectiveness
            response_effectiveness = decision.expected_effectiveness
            casualties_saved = int(disaster.casualties * response_effectiveness * 0.4)
            disaster.casualties = max(0, disaster.casualties - casualties_saved)
            self.metrics.casualties_saved += casualties_saved
    
    def _update_rescue_teams(self):
        """Update rescue team states and actions"""
        for team in self.rescue_teams:
            # Find nearest disaster
            nearest_disaster = self._find_nearest_disaster(team.position)
            
            if nearest_disaster:
                # Move towards disaster
                self._move_team_towards_disaster(team, nearest_disaster)
                
                # Perform rescue operations
                if self._is_team_at_disaster(team, nearest_disaster):
                    self._perform_rescue_operations(team, nearest_disaster)
            
            # Update fatigue
            team.fatigue = min(team.max_fatigue, team.fatigue + 1)
            
            # Rest if too fatigued
            if team.fatigue > team.max_fatigue * 0.8:
                team.rest()
    
    def _find_nearest_disaster(self, position: Tuple[int, int]) -> Optional[Disaster]:
        """Find the nearest active disaster to a position"""
        if not self.disaster_manager.disasters:
            return None
        
        min_distance = float('inf')
        nearest_disaster = None
        
        for disaster in self.disaster_manager.disasters:
            distance = abs(disaster.location[0] - position[0]) + abs(disaster.location[1] - position[1])
            if distance < min_distance:
                min_distance = distance
                nearest_disaster = disaster
        
        return nearest_disaster
    
    def _move_team_towards_disaster(self, team: RescueTeam, disaster: Disaster):
        """Move rescue team towards disaster location"""
        target_x, target_y = disaster.location
        current_x, current_y = team.position
        
        # Simple pathfinding - move one step towards target
        if current_x < target_x:
            new_x = min(self.grid_size - 1, current_x + 1)
        elif current_x > target_x:
            new_x = max(0, current_x - 1)
        else:
            new_x = current_x
        
        if current_y < target_y:
            new_y = min(self.grid_size - 1, current_y + 1)
        elif current_y > target_y:
            new_y = max(0, current_y - 1)
        else:
            new_y = current_y
        
        team.position = (new_x, new_y)
    
    def _is_team_at_disaster(self, team: RescueTeam, disaster: Disaster) -> bool:
        """Check if team is at disaster location"""
        return team.position == disaster.location
    
    def _perform_rescue_operations(self, team: RescueTeam, disaster: Disaster):
        """Perform rescue operations at disaster site"""
        if disaster.casualties <= 0:
            return
        
        # Calculate rescue effectiveness based on team specialization
        effectiveness = team.efficiency
        if team.specialization == "medical" and disaster.type in [DisasterType.EARTHQUAKE, DisasterType.TORNADO]:
            effectiveness *= 1.2
        elif team.specialization == "fire_suppression" and disaster.type == DisasterType.FIRE:
            effectiveness *= 1.3
        elif team.specialization == "water_rescue" and disaster.type == DisasterType.FLOOD:
            effectiveness *= 1.2
        
        # Perform rescue
        casualties_saved = min(
            disaster.casualties,
            int(disaster.casualties * effectiveness * 0.1)  # Save up to 10% per operation
        )
        
        disaster.casualties = max(0, disaster.casualties - casualties_saved)
        self.metrics.casualties_saved += casualties_saved
        
        # Use resources
        team.use_resource("medical_supplies", casualties_saved)
        team.fatigue += casualties_saved * 2
    
    def _spawn_new_disaster(self):
        """Spawn a new disaster during simulation"""
        disaster = self.disaster_manager.generate_random_disaster(self.grid_size)
        disaster.start_time = self.current_time
        self.disaster_manager.add_disaster(disaster)
        self.metrics.active_disasters = len(self.disaster_manager.disasters)
    
    def _update_metrics(self):
        """Update simulation metrics"""
        # Update disaster counts
        self.metrics.active_disasters = len(self.disaster_manager.disasters)
        self.metrics.disasters_resolved = len(self.disaster_manager.disaster_history)
        
        # Update casualty counts
        self.metrics.total_casualties = sum(d.casualties for d in self.disaster_manager.disasters)
        
        # Update resource metrics
        total_resources = sum(self.disaster_manager.global_resources.values())
        allocated_resources = sum(self.disaster_manager.allocated_resources.values())
        self.metrics.resources_remaining = total_resources - allocated_resources
        
        # Calculate response efficiency
        if self.metrics.time_steps > 0:
            self.metrics.response_efficiency = (
                self.metrics.casualties_saved + self.metrics.casualties_prevented
            ) / (self.metrics.resources_used + self.metrics.time_steps + 1)
        
        # Calculate decision accuracy
        if self.decision_history:
            total_confidence = sum(d.confidence for d in self.decision_history)
            self.metrics.decision_accuracy = total_confidence / len(self.decision_history)
        
        # Calculate average response time
        if self.metrics.emergency_responses > 0:
            self.metrics.average_response_time = self.metrics.time_steps / self.metrics.emergency_responses
        
        # Store performance snapshot
        self.performance_history.append({
            "time_step": self.metrics.time_steps,
            "active_disasters": self.metrics.active_disasters,
            "casualties_saved": self.metrics.casualties_saved,
            "response_efficiency": self.metrics.response_efficiency,
            "resources_used": self.metrics.resources_used
        })
    
    def _get_simulation_state(self) -> Dict[str, Any]:
        """Get current simulation state"""
        return {
            "time_step": self.metrics.time_steps,
            "is_running": self.is_running,
            "auto_mode": self.auto_mode,
            "metrics": {
                "time_steps": self.metrics.time_steps,
                "total_casualties": self.metrics.total_casualties,
                "casualties_saved": self.metrics.casualties_saved,
                "casualties_prevented": self.metrics.casualties_prevented,
                "resources_used": self.metrics.resources_used,
                "resources_remaining": self.metrics.resources_remaining,
                "economic_impact": self.metrics.economic_impact,
                "response_efficiency": self.metrics.response_efficiency,
                "decision_accuracy": self.metrics.decision_accuracy,
                "evacuation_orders": self.metrics.evacuation_orders,
                "emergency_responses": self.metrics.emergency_responses,
                "disasters_resolved": self.metrics.disasters_resolved,
                "active_disasters": self.metrics.active_disasters,
                "total_cost": self.metrics.total_cost,
                "average_response_time": self.metrics.average_response_time
            },
            "disasters": [
                {
                    "id": i,
                    "type": disaster.type.value,
                    "severity": disaster.severity.value,
                    "casualties": disaster.casualties,
                    "injured": disaster.injured,
                    "missing": disaster.missing,
                    "affected_area": disaster.affected_area,
                    "location": disaster.location,
                    "is_active": disaster.is_active,
                    "priority_score": disaster.get_priority_score()
                }
                for i, disaster in enumerate(self.disaster_manager.disasters)
            ],
            "rescue_teams": [
                {
                    "id": i,
                    "position": team.position,
                    "specialization": team.specialization,
                    "efficiency": team.efficiency,
                    "fatigue": team.fatigue,
                    "resources": team.resources
                }
                for i, team in enumerate(self.rescue_teams)
            ],
            "resource_utilization": self.disaster_manager.get_resource_utilization(),
            "ai_analytics": self.ai_decision_engine.get_decision_analytics()
        }
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.is_running = False
        self.auto_mode = False
        
        print(f"🛑 Simulation Stopped")
        print(f"📊 Final Metrics:")
        print(f"   Time Steps: {self.metrics.time_steps}")
        print(f"   Casualties Saved: {self.metrics.casualties_saved}")
        print(f"   Response Efficiency: {self.metrics.response_efficiency:.2f}")
        print(f"   Disasters Resolved: {self.metrics.disasters_resolved}")
    
    def get_simulation_summary(self) -> Dict[str, Any]:
        """Get comprehensive simulation summary"""
        duration = (datetime.now() - self.simulation_start_time).total_seconds() if self.simulation_start_time else 0
        
        return {
            "simulation_duration_seconds": duration,
            "final_metrics": self.metrics.__dict__,
            "disaster_summary": {
                "total_disasters": len(self.disaster_manager.disasters) + len(self.disaster_manager.disaster_history),
                "active_disasters": len(self.disaster_manager.disasters),
                "resolved_disasters": len(self.disaster_manager.disaster_history)
            },
            "ai_performance": self.ai_decision_engine.get_decision_analytics(),
            "performance_history": self.performance_history[-10:],  # Last 10 steps
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on simulation performance"""
        recommendations = []
        
        if self.metrics.response_efficiency < 0.5:
            recommendations.append("Consider improving resource allocation strategies")
        
        if self.metrics.decision_accuracy < 0.7:
            recommendations.append("AI decision confidence is low - review decision algorithms")
        
        if self.metrics.average_response_time > 5:
            recommendations.append("Response time is high - consider pre-positioning resources")
        
        if self.metrics.casualties_saved < self.metrics.total_casualties * 0.3:
            recommendations.append("Low casualty rescue rate - improve rescue team coordination")
        
        if not recommendations:
            recommendations.append("Simulation performed well - maintain current strategies")
        
        return recommendations
