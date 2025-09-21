from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import random
import math
from enum import Enum

from .disaster import Disaster, DisasterManager, DisasterType, SeverityLevel
from .probabilistic_reasoning import BayesianNetwork, ProbabilityDistributions, RiskAssessment

class DecisionType(Enum):
    RESOURCE_ALLOCATION = "resource_allocation"
    EVACUATION_ORDER = "evacuation_order"
    EMERGENCY_RESPONSE = "emergency_response"
    PRIORITY_ASSIGNMENT = "priority_assignment"

@dataclass
class Decision:
    """Represents an AI decision with reasoning and expected outcomes"""
    decision_type: DecisionType
    action: str
    target_disaster_id: Optional[int]
    resources_allocated: Dict[str, int]
    reasoning: str
    expected_effectiveness: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    risk_level: str  # low, medium, high, critical
    time_to_implement: int  # hours
    cost: float  # economic cost

class AIDecisionEngine:
    """Advanced AI decision-making system for disaster response"""
    
    def __init__(self):
        self.bayesian_network = BayesianNetwork()
        self.probability_distributions = ProbabilityDistributions()
        self.risk_assessor = RiskAssessment()
        self.decision_history: List[Decision] = []
        self.learning_rate = 0.1
        self.decision_weights = {
            'casualty_reduction': 0.4,
            'resource_efficiency': 0.3,
            'time_criticality': 0.2,
            'economic_impact': 0.1
        }
    
    def make_resource_allocation_decision(self, disaster_manager: DisasterManager, 
                                        available_resources: Dict[str, int]) -> Decision:
        """Make intelligent resource allocation decisions"""
        active_disasters = disaster_manager.disasters
        if not active_disasters:
            return self._create_no_action_decision()
        
        # Get priority-ordered disasters
        priority_disasters = disaster_manager.get_disaster_priority_order()
        
        # Calculate resource allocation using multiple strategies
        allocation_strategies = [
            self._priority_based_allocation,
            self._efficiency_based_allocation,
            self._risk_balanced_allocation
        ]
        
        best_allocation = None
        best_score = -1
        
        for strategy in allocation_strategies:
            allocation, score = strategy(priority_disasters, available_resources)
            if score > best_score:
                best_allocation = allocation
                best_score = score
        
        # Create decision
        decision = Decision(
            decision_type=DecisionType.RESOURCE_ALLOCATION,
            action="Allocate resources to highest priority disasters",
            target_disaster_id=best_allocation['target_disaster'] if best_allocation else None,
            resources_allocated=best_allocation['resources'] if best_allocation else {},
            reasoning=self._generate_reasoning(best_allocation, priority_disasters),
            expected_effectiveness=best_score,
            confidence=self._calculate_confidence(best_allocation, priority_disasters),
            risk_level=self._assess_risk_level(priority_disasters),
            time_to_implement=self._calculate_implementation_time(best_allocation),
            cost=self._calculate_cost(best_allocation)
        )
        
        self.decision_history.append(decision)
        return decision
    
    def _priority_based_allocation(self, disasters: List[Disaster], 
                                 available_resources: Dict[str, int]) -> Tuple[Dict, float]:
        """Allocate resources based on disaster priority scores"""
        if not disasters:
            return {}, 0.0
        
        target_disaster = disasters[0]  # Highest priority
        required_resources = target_disaster.get_required_resources()
        
        # Allocate what we can
        allocated = {}
        for resource_type, amount in required_resources.items():
            if resource_type in available_resources:
                allocated[resource_type] = min(amount, available_resources[resource_type])
        
        # Calculate effectiveness score
        total_required = sum(required_resources.values())
        total_allocated = sum(allocated.values())
        effectiveness = total_allocated / total_required if total_required > 0 else 0
        
        return {
            'target_disaster': 0,  # Index of target disaster
            'resources': allocated
        }, effectiveness
    
    def _efficiency_based_allocation(self, disasters: List[Disaster], 
                                   available_resources: Dict[str, int]) -> Tuple[Dict, float]:
        """Allocate resources for maximum efficiency across all disasters"""
        if not disasters:
            return {}, 0.0
        
        # Calculate efficiency for each disaster
        disaster_efficiency = []
        for i, disaster in enumerate(disasters):
            required = disaster.get_required_resources()
            total_required = sum(required.values())
            casualties_per_resource = disaster.casualties / total_required if total_required > 0 else 0
            disaster_efficiency.append((i, casualties_per_resource, required))
        
        # Sort by efficiency (casualties per resource)
        disaster_efficiency.sort(key=lambda x: x[1], reverse=True)
        
        # Allocate to most efficient disasters first
        allocated = {}
        total_effectiveness = 0
        
        for disaster_idx, efficiency, required in disaster_efficiency:
            disaster = disasters[disaster_idx]
            disaster_allocation = {}
            
            for resource_type, amount in required.items():
                if resource_type in available_resources and available_resources[resource_type] > 0:
                    allocate_amount = min(amount, available_resources[resource_type])
                    disaster_allocation[resource_type] = allocate_amount
                    available_resources[resource_type] -= allocate_amount
            
            if disaster_allocation:
                allocated.update(disaster_allocation)
                total_effectiveness += efficiency * sum(disaster_allocation.values())
        
        return {
            'target_disaster': disaster_efficiency[0][0] if disaster_efficiency else 0,
            'resources': allocated
        }, total_effectiveness / len(disasters) if disasters else 0
    
    def _risk_balanced_allocation(self, disasters: List[Disaster], 
                                available_resources: Dict[str, int]) -> Tuple[Dict, float]:
        """Allocate resources balancing risk across all disasters"""
        if not disasters:
            return {}, 0.0
        
        # Calculate risk scores for each disaster
        risk_scores = []
        for i, disaster in enumerate(disasters):
            risk_score = self.risk_assessor.calculate_risk(
                disaster.casualties,
                disaster.affected_area,
                disaster.intensity
            )
            risk_scores.append((i, risk_score, disaster))
        
        # Sort by risk (highest first)
        risk_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Allocate proportionally based on risk
        total_risk = sum(score for _, score, _ in risk_scores)
        allocated = {}
        total_effectiveness = 0
        
        for disaster_idx, risk_score, disaster in risk_scores:
            if total_risk == 0:
                continue
                
            risk_proportion = risk_score / total_risk
            required = disaster.get_required_resources()
            
            disaster_allocation = {}
            for resource_type, amount in required.items():
                if resource_type in available_resources:
                    allocate_amount = min(
                        int(amount * risk_proportion),
                        available_resources[resource_type]
                    )
                    if allocate_amount > 0:
                        disaster_allocation[resource_type] = allocate_amount
                        available_resources[resource_type] -= allocate_amount
            
            if disaster_allocation:
                allocated.update(disaster_allocation)
                total_effectiveness += risk_proportion * sum(disaster_allocation.values())
        
        return {
            'target_disaster': risk_scores[0][0] if risk_scores else 0,
            'resources': allocated
        }, total_effectiveness
    
    def make_evacuation_decision(self, disaster_manager: DisasterManager) -> Decision:
        """Make evacuation decisions based on disaster severity and spread"""
        active_disasters = disaster_manager.disasters
        if not active_disasters:
            return self._create_no_action_decision()
        
        # Find disasters requiring evacuation
        evacuation_candidates = []
        for i, disaster in enumerate(active_disasters):
            if (disaster.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL] and
                disaster.spread_rate > 0.3):
                evacuation_candidates.append((i, disaster))
        
        if not evacuation_candidates:
            return self._create_no_action_decision()
        
        # Prioritize by severity and spread rate
        evacuation_candidates.sort(
            key=lambda x: (x[1].severity.value, x[1].spread_rate),
            reverse=True
        )
        
        target_disaster = evacuation_candidates[0][1]
        evacuation_radius = self._calculate_evacuation_radius(target_disaster)
        
        decision = Decision(
            decision_type=DecisionType.EVACUATION_ORDER,
            action=f"Order evacuation within {evacuation_radius}km radius",
            target_disaster_id=evacuation_candidates[0][0],
            resources_allocated={},
            reasoning=f"High severity {target_disaster.type.value} with {target_disaster.spread_rate:.1%} spread rate requires immediate evacuation",
            expected_effectiveness=0.8 if target_disaster.severity == SeverityLevel.CRITICAL else 0.6,
            confidence=0.9 if target_disaster.severity == SeverityLevel.CRITICAL else 0.7,
            risk_level="critical" if target_disaster.severity == SeverityLevel.CRITICAL else "high",
            time_to_implement=2,  # 2 hours to implement
            cost=evacuation_radius * 1000  # Cost based on evacuation radius
        )
        
        self.decision_history.append(decision)
        return decision
    
    def make_emergency_response_decision(self, disaster_manager: DisasterManager) -> Decision:
        """Make emergency response decisions for critical situations"""
        active_disasters = disaster_manager.disasters
        if not active_disasters:
            return self._create_no_action_decision()
        
        # Find critical disasters
        critical_disasters = [
            (i, d) for i, d in enumerate(active_disasters)
            if d.severity == SeverityLevel.CRITICAL and d.casualties > 100
        ]
        
        if not critical_disasters:
            return self._create_no_action_decision()
        
        target_disaster = critical_disasters[0][1]
        
        # Determine emergency response type
        if target_disaster.type == DisasterType.EARTHQUAKE:
            response_type = "Search and rescue operations"
            resources = {'rescue_teams': 10, 'helicopters': 3, 'medical_supplies': 200}
        elif target_disaster.type == DisasterType.FLOOD:
            response_type = "Water rescue and evacuation"
            resources = {'boats': 8, 'rescue_teams': 6, 'helicopters': 2}
        elif target_disaster.type == DisasterType.FIRE:
            response_type = "Fire suppression and evacuation"
            resources = {'fire_trucks': 5, 'helicopters': 4, 'rescue_teams': 8}
        else:
            response_type = "General emergency response"
            resources = {'rescue_teams': 5, 'ambulances': 3, 'medical_supplies': 100}
        
        decision = Decision(
            decision_type=DecisionType.EMERGENCY_RESPONSE,
            action=response_type,
            target_disaster_id=critical_disasters[0][0],
            resources_allocated=resources,
            reasoning=f"Critical {target_disaster.type.value} with {target_disaster.casualties} casualties requires immediate emergency response",
            expected_effectiveness=0.9,
            confidence=0.95,
            risk_level="critical",
            time_to_implement=1,  # 1 hour to implement
            cost=sum(resources.values()) * 1000
        )
        
        self.decision_history.append(decision)
        return decision
    
    def _calculate_evacuation_radius(self, disaster: Disaster) -> int:
        """Calculate evacuation radius based on disaster characteristics"""
        base_radius = {
            DisasterType.EARTHQUAKE: 5,
            DisasterType.FLOOD: 10,
            DisasterType.FIRE: 8,
            DisasterType.HURRICANE: 15,
            DisasterType.TORNADO: 3,
            DisasterType.TSUNAMI: 20
        }
        
        severity_multiplier = {
            SeverityLevel.LOW: 1.0,
            SeverityLevel.MEDIUM: 1.5,
            SeverityLevel.HIGH: 2.0,
            SeverityLevel.CRITICAL: 3.0
        }
        
        radius = base_radius[disaster.type] * severity_multiplier[disaster.severity]
        return int(radius)
    
    def _generate_reasoning(self, allocation: Dict, disasters: List[Disaster]) -> str:
        """Generate human-readable reasoning for the decision"""
        if not allocation or not disasters:
            return "No active disasters requiring resource allocation"
        
        target_idx = allocation.get('target_disaster', 0)
        if target_idx < len(disasters):
            target_disaster = disasters[target_idx]
            resources = allocation.get('resources', {})
            resource_count = sum(resources.values())
            
            return (f"Allocating {resource_count} resources to {target_disaster.type.value} "
                   f"(severity: {target_disaster.severity.value}, casualties: {target_disaster.casualties}) "
                   f"based on priority scoring and resource availability")
        
        return "Resource allocation based on disaster priority analysis"
    
    def _calculate_confidence(self, allocation: Dict, disasters: List[Disaster]) -> float:
        """Calculate confidence in the decision"""
        if not allocation or not disasters:
            return 0.0
        
        # Base confidence on resource allocation completeness
        resources = allocation.get('resources', {})
        if not resources:
            return 0.1
        
        # Calculate how well we can meet requirements
        target_idx = allocation.get('target_disaster', 0)
        if target_idx < len(disasters):
            target_disaster = disasters[target_idx]
            required = target_disaster.get_required_resources()
            
            total_required = sum(required.values())
            total_allocated = sum(resources.values())
            
            if total_required > 0:
                return min(1.0, total_allocated / total_required)
        
        return 0.5
    
    def _assess_risk_level(self, disasters: List[Disaster]) -> str:
        """Assess overall risk level"""
        if not disasters:
            return "low"
        
        max_severity = max(d.severity for d in disasters)
        total_casualties = sum(d.casualties for d in disasters)
        
        if max_severity == SeverityLevel.CRITICAL or total_casualties > 500:
            return "critical"
        elif max_severity == SeverityLevel.HIGH or total_casualties > 200:
            return "high"
        elif max_severity == SeverityLevel.MEDIUM or total_casualties > 50:
            return "medium"
        else:
            return "low"
    
    def _calculate_implementation_time(self, allocation: Dict) -> int:
        """Calculate time to implement the decision"""
        if not allocation:
            return 0
        
        resources = allocation.get('resources', {})
        if not resources:
            return 0
        
        # Base time on resource complexity
        resource_types = len(resources)
        total_resources = sum(resources.values())
        
        base_time = 1  # 1 hour base
        complexity_time = resource_types * 0.5  # 0.5 hours per resource type
        scale_time = total_resources * 0.1  # 0.1 hours per resource unit
        
        return int(base_time + complexity_time + scale_time)
    
    def _calculate_cost(self, allocation: Dict) -> float:
        """Calculate economic cost of the decision"""
        if not allocation:
            return 0.0
        
        resources = allocation.get('resources', {})
        if not resources:
            return 0.0
        
        # Cost per resource type (in thousands)
        resource_costs = {
            'ambulances': 50,
            'fire_trucks': 100,
            'rescue_teams': 25,
            'medical_supplies': 1,
            'helicopters': 200,
            'boats': 75
        }
        
        total_cost = 0
        for resource_type, amount in resources.items():
            cost_per_unit = resource_costs.get(resource_type, 10)
            total_cost += amount * cost_per_unit
        
        return total_cost
    
    def _create_no_action_decision(self) -> Decision:
        """Create a no-action decision"""
        return Decision(
            decision_type=DecisionType.RESOURCE_ALLOCATION,
            action="No action required",
            target_disaster_id=None,
            resources_allocated={},
            reasoning="No active disasters requiring immediate action",
            expected_effectiveness=0.0,
            confidence=1.0,
            risk_level="low",
            time_to_implement=0,
            cost=0.0
        )
    
    def get_decision_analytics(self) -> Dict[str, Any]:
        """Get analytics about past decisions"""
        if not self.decision_history:
            return {"total_decisions": 0}
        
        total_decisions = len(self.decision_history)
        avg_effectiveness = sum(d.expected_effectiveness for d in self.decision_history) / total_decisions
        avg_confidence = sum(d.confidence for d in self.decision_history) / total_decisions
        total_cost = sum(d.cost for d in self.decision_history)
        
        decision_types = {}
        for decision in self.decision_history:
            decision_type = decision.decision_type.value
            decision_types[decision_type] = decision_types.get(decision_type, 0) + 1
        
        return {
            "total_decisions": total_decisions,
            "average_effectiveness": avg_effectiveness,
            "average_confidence": avg_confidence,
            "total_cost": total_cost,
            "decision_type_distribution": decision_types
        }
