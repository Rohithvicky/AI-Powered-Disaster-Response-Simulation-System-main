"""
Probabilistic reasoning module for handling uncertainty in disaster scenarios
Implements Bayesian networks and probability distributions
"""

import random
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

@dataclass
class ProbabilityNode:
    """Node in a Bayesian network"""
    name: str
    probabilities: Dict[str, float]  # State -> probability
    parents: List[str] = None
    
    def __post_init__(self):
        if self.parents is None:
            self.parents = []
    
    def get_probability(self, state: str) -> float:
        """Get probability for a given state"""
        return self.probabilities.get(state, 0.0)

class BayesianNetwork:
    """Simple Bayesian network implementation for disaster scenarios"""
    
    def __init__(self):
        self.nodes = {}
        self._initialize_disaster_network()
    
    def _initialize_disaster_network(self):
        """Initialize the disaster response Bayesian network"""
        
        # Disaster severity node (root)
        self.nodes['disaster_severity'] = ProbabilityNode(
            name='disaster_severity',
            probabilities={
                'low': 0.3,
                'medium': 0.5,
                'high': 0.2
            }
        )
        
        # Response time node (depends on severity)
        self.nodes['response_time'] = ProbabilityNode(
            name='response_time',
            probabilities={
                'fast': 0.4,
                'medium': 0.4,
                'slow': 0.2
            },
            parents=['disaster_severity']
        )
        
        # Resource availability node (depends on severity and response time)
        self.nodes['resource_availability'] = ProbabilityNode(
            name='resource_availability',
            probabilities={
                'high': 0.3,
                'medium': 0.5,
                'low': 0.2
            },
            parents=['disaster_severity', 'response_time']
        )
        
        # Survival probability node (depends on all above)
        self.nodes['survival_probability'] = ProbabilityNode(
            name='survival_probability',
            probabilities={
                'high': 0.4,
                'medium': 0.4,
                'low': 0.2
            },
            parents=['disaster_severity', 'response_time', 'resource_availability']
        )
    
    def get_conditional_probability(self, node_name: str, evidence: Dict[str, str]) -> Dict[str, float]:
        """Get conditional probabilities for a node given evidence"""
        node = self.nodes.get(node_name)
        if not node:
            return {}
        
        # Simple conditional probability calculation
        # In a real implementation, you'd use more sophisticated inference algorithms
        
        if node_name == 'survival_probability':
            return self._calculate_survival_probability(evidence)
        elif node_name == 'resource_availability':
            return self._calculate_resource_probability(evidence)
        elif node_name == 'response_time':
            return self._calculate_response_probability(evidence)
        else:
            return node.probabilities
    
    def _calculate_survival_probability(self, evidence: Dict[str, str]) -> Dict[str, float]:
        """Calculate survival probability based on evidence"""
        severity = evidence.get('disaster_severity', 'medium')
        response = evidence.get('response_time', 'medium')
        resources = evidence.get('resource_availability', 'medium')
        
        # Base probabilities
        base_probs = {'high': 0.4, 'medium': 0.4, 'low': 0.2}
        
        # Adjust based on evidence
        if severity == 'high':
            base_probs = {'high': 0.2, 'medium': 0.3, 'low': 0.5}
        elif severity == 'low':
            base_probs = {'high': 0.6, 'medium': 0.3, 'low': 0.1}
        
        if response == 'slow':
            for key in base_probs:
                base_probs[key] *= 0.7
        elif response == 'fast':
            for key in base_probs:
                base_probs[key] *= 1.2
        
        if resources == 'low':
            for key in base_probs:
                base_probs[key] *= 0.6
        elif resources == 'high':
            for key in base_probs:
                base_probs[key] *= 1.3
        
        # Normalize
        total = sum(base_probs.values())
        return {k: v/total for k, v in base_probs.items()}
    
    def _calculate_resource_probability(self, evidence: Dict[str, str]) -> Dict[str, float]:
        """Calculate resource availability probability based on evidence"""
        severity = evidence.get('disaster_severity', 'medium')
        response = evidence.get('response_time', 'medium')
        
        base_probs = {'high': 0.3, 'medium': 0.5, 'low': 0.2}
        
        if severity == 'high':
            base_probs = {'high': 0.1, 'medium': 0.3, 'low': 0.6}
        elif severity == 'low':
            base_probs = {'high': 0.5, 'medium': 0.4, 'low': 0.1}
        
        if response == 'slow':
            for key in base_probs:
                base_probs[key] *= 0.8
        elif response == 'fast':
            for key in base_probs:
                base_probs[key] *= 1.1
        
        total = sum(base_probs.values())
        return {k: v/total for k, v in base_probs.items()}
    
    def _calculate_response_probability(self, evidence: Dict[str, str]) -> Dict[str, float]:
        """Calculate response time probability based on evidence"""
        severity = evidence.get('disaster_severity', 'medium')
        
        base_probs = {'fast': 0.4, 'medium': 0.4, 'slow': 0.2}
        
        if severity == 'high':
            base_probs = {'fast': 0.2, 'medium': 0.4, 'slow': 0.4}
        elif severity == 'low':
            base_probs = {'fast': 0.6, 'medium': 0.3, 'slow': 0.1}
        
        return base_probs

class ProbabilityDistributions:
    """Utility class for various probability distributions"""
    
    @staticmethod
    def normal_distribution(mean: float, std_dev: float, x: float) -> float:
        """Calculate probability density for normal distribution"""
        return (1 / (std_dev * math.sqrt(2 * math.pi))) * \
               math.exp(-0.5 * ((x - mean) / std_dev) ** 2)
    
    @staticmethod
    def exponential_distribution(lambda_param: float, x: float) -> float:
        """Calculate probability density for exponential distribution"""
        if x < 0:
            return 0
        return lambda_param * math.exp(-lambda_param * x)
    
    @staticmethod
    def uniform_distribution(a: float, b: float, x: float) -> float:
        """Calculate probability density for uniform distribution"""
        if a <= x <= b:
            return 1 / (b - a)
        return 0
    
    @staticmethod
    def sample_normal(mean: float, std_dev: float) -> float:
        """Sample from normal distribution"""
        return random.gauss(mean, std_dev)
    
    @staticmethod
    def sample_exponential(lambda_param: float) -> float:
        """Sample from exponential distribution"""
        return random.expovariate(lambda_param)
    
    @staticmethod
    def sample_uniform(a: float, b: float) -> float:
        """Sample from uniform distribution"""
        return random.uniform(a, b)

class RiskAssessment:
    """Risk assessment using probabilistic reasoning"""
    
    def __init__(self, bayesian_network: BayesianNetwork):
        self.network = bayesian_network
    
    def assess_survival_risk(self, position: Tuple[int, int], 
                           hazards: Dict[Tuple[int, int], float],
                           resources_nearby: int) -> float:
        """Assess survival risk at a given position"""
        
        # Base risk from hazards
        hazard_risk = hazards.get(position, 0.0)
        
        # Resource factor (more resources = lower risk)
        resource_factor = max(0.1, 1.0 - (resources_nearby * 0.1))
        
        # Calculate total risk
        total_risk = hazard_risk * resource_factor
        
        # Apply uncertainty using probability distributions
        uncertainty = ProbabilityDistributions.sample_normal(0.0, 0.1)
        total_risk = max(0.0, min(1.0, total_risk + uncertainty))
        
        return total_risk
    
    def estimate_recovery_time(self, disaster_severity: str, 
                             response_time: str, 
                             resource_level: str) -> float:
        """Estimate recovery time based on various factors"""
        
        # Base recovery times (in time steps)
        base_times = {
            'low': 10,
            'medium': 25,
            'high': 50
        }
        
        # Multipliers for different factors
        response_multipliers = {
            'fast': 0.7,
            'medium': 1.0,
            'slow': 1.5
        }
        
        resource_multipliers = {
            'high': 0.6,
            'medium': 1.0,
            'low': 1.8
        }
        
        base_time = base_times.get(disaster_severity, 25)
        response_factor = response_multipliers.get(response_time, 1.0)
        resource_factor = resource_multipliers.get(resource_level, 1.0)
        
        estimated_time = base_time * response_factor * resource_factor
        
        # Add uncertainty
        uncertainty = ProbabilityDistributions.sample_normal(0.0, 0.2)
        estimated_time = max(1, estimated_time * (1 + uncertainty))
        
        return estimated_time
    
    def calculate_evacuation_success_probability(self, 
                                              distance_to_safety: float,
                                              hazard_intensity: float,
                                              evacuation_speed: float) -> float:
        """Calculate probability of successful evacuation"""
        
        # Base success probability decreases with distance and hazard intensity
        base_probability = 0.9 * math.exp(-distance_to_safety * 0.1) * (1 - hazard_intensity * 0.5)
        
        # Speed factor (faster evacuation = higher success)
        speed_factor = min(1.5, evacuation_speed / 2.0)
        
        success_prob = base_probability * speed_factor
        
        # Ensure probability is between 0 and 1
        return max(0.0, min(1.0, success_prob))
