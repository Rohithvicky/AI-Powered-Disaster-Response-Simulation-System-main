from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum
import random
import math

class DisasterType(Enum):
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    FIRE = "fire"
    HURRICANE = "hurricane"
    TORNADO = "tornado"
    TSUNAMI = "tsunami"

class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Disaster:
    """Represents a disaster scenario with all its characteristics"""
    type: DisasterType
    severity: SeverityLevel
    affected_area: float  # in square kilometers
    casualties: int
    injured: int
    missing: int
    infrastructure_damage: float  # 0.0 to 1.0
    economic_impact: float  # in millions
    duration_hours: int
    spread_rate: float  # how fast the disaster spreads
    intensity: float  # 0.0 to 1.0
    location: Tuple[int, int]  # grid coordinates
    start_time: int  # simulation step when disaster started
    is_active: bool = True
    
    def __post_init__(self):
        """Calculate derived properties based on disaster type and severity"""
        self._calculate_impact_factors()
    
    def _calculate_impact_factors(self):
        """Calculate impact factors based on disaster type and severity"""
        severity_multiplier = {
            SeverityLevel.LOW: 0.3,
            SeverityLevel.MEDIUM: 0.6,
            SeverityLevel.HIGH: 0.8,
            SeverityLevel.CRITICAL: 1.0
        }
        
        type_factors = {
            DisasterType.EARTHQUAKE: {
                'casualty_rate': 0.15,
                'infrastructure_damage': 0.8,
                'spread_rate': 0.1
            },
            DisasterType.FLOOD: {
                'casualty_rate': 0.08,
                'infrastructure_damage': 0.6,
                'spread_rate': 0.3
            },
            DisasterType.FIRE: {
                'casualty_rate': 0.12,
                'infrastructure_damage': 0.7,
                'spread_rate': 0.4
            },
            DisasterType.HURRICANE: {
                'casualty_rate': 0.10,
                'infrastructure_damage': 0.9,
                'spread_rate': 0.2
            },
            DisasterType.TORNADO: {
                'casualty_rate': 0.20,
                'infrastructure_damage': 0.95,
                'spread_rate': 0.1
            },
            DisasterType.TSUNAMI: {
                'casualty_rate': 0.25,
                'infrastructure_damage': 0.85,
                'spread_rate': 0.5
            }
        }
        
        multiplier = severity_multiplier[self.severity]
        factors = type_factors[self.type]
        
        # Calculate actual impact based on affected area and factors
        self.casualties = max(1, int(self.affected_area * factors['casualty_rate'] * multiplier * 100))
        self.injured = max(0, int(self.casualties * (0.5 + random.random() * 0.3)))
        self.missing = max(0, int(self.casualties * (0.1 + random.random() * 0.2)))
        self.infrastructure_damage = min(1.0, factors['infrastructure_damage'] * multiplier)
        self.economic_impact = self.affected_area * factors['infrastructure_damage'] * multiplier * 1000
        self.spread_rate = factors['spread_rate'] * multiplier
        self.intensity = multiplier
    
    def update_disaster(self, time_step: int, resources_deployed: Dict[str, int] = None):
        """Update disaster state based on time and deployed resources"""
        if not self.is_active:
            return
        
        # Calculate resource effectiveness
        effectiveness = 0.0
        if resources_deployed:
            total_resources = sum(resources_deployed.values())
            effectiveness = min(1.0, total_resources / (self.affected_area * 10))
        
        # Update casualties based on time and resources
        time_factor = min(1.0, (time_step - self.start_time) / self.duration_hours)
        resource_reduction = effectiveness * 0.3  # Resources can reduce casualties by up to 30%
        
        # Reduce casualties over time with resource deployment
        if resources_deployed:
            self.casualties = max(0, int(self.casualties * (1 - resource_reduction * time_factor)))
            self.injured = max(0, int(self.injured * (1 - resource_reduction * time_factor * 0.5)))
        
        # Check if disaster is resolved
        if time_step - self.start_time >= self.duration_hours or self.casualties <= 0:
            self.is_active = False
    
    def get_priority_score(self) -> float:
        """Calculate priority score for resource allocation"""
        severity_scores = {
            SeverityLevel.LOW: 1.0,
            SeverityLevel.MEDIUM: 2.0,
            SeverityLevel.HIGH: 3.0,
            SeverityLevel.CRITICAL: 4.0
        }
        
        return (severity_scores[self.severity] * self.casualties * self.intensity) / (self.affected_area + 1)
    
    def get_required_resources(self) -> Dict[str, int]:
        """Get recommended resource allocation for this disaster"""
        base_resources = {
            'ambulances': 0,
            'fire_trucks': 0,
            'rescue_teams': 0,
            'medical_supplies': 0,
            'helicopters': 0,
            'boats': 0
        }
        
        severity_multiplier = {
            SeverityLevel.LOW: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.HIGH: 3,
            SeverityLevel.CRITICAL: 4
        }
        
        multiplier = severity_multiplier[self.severity]
        
        if self.type == DisasterType.EARTHQUAKE:
            base_resources['rescue_teams'] = max(1, int(self.casualties / 10) * multiplier)
            base_resources['ambulances'] = max(1, int(self.casualties / 5) * multiplier)
            base_resources['medical_supplies'] = max(50, int(self.casualties * 2) * multiplier)
            base_resources['helicopters'] = max(1, int(self.affected_area / 50) * multiplier)
        
        elif self.type == DisasterType.FLOOD:
            base_resources['boats'] = max(1, int(self.affected_area / 20) * multiplier)
            base_resources['rescue_teams'] = max(1, int(self.casualties / 15) * multiplier)
            base_resources['ambulances'] = max(1, int(self.casualties / 8) * multiplier)
            base_resources['medical_supplies'] = max(50, int(self.casualties * 1.5) * multiplier)
        
        elif self.type == DisasterType.FIRE:
            base_resources['fire_trucks'] = max(1, int(self.affected_area / 10) * multiplier)
            base_resources['rescue_teams'] = max(1, int(self.casualties / 12) * multiplier)
            base_resources['ambulances'] = max(1, int(self.casualties / 6) * multiplier)
            base_resources['helicopters'] = max(1, int(self.affected_area / 30) * multiplier)
        
        elif self.type == DisasterType.HURRICANE:
            base_resources['rescue_teams'] = max(1, int(self.casualties / 8) * multiplier)
            base_resources['ambulances'] = max(1, int(self.casualties / 4) * multiplier)
            base_resources['helicopters'] = max(1, int(self.affected_area / 25) * multiplier)
            base_resources['boats'] = max(1, int(self.affected_area / 15) * multiplier)
        
        return base_resources

class DisasterManager:
    """Manages multiple disasters and their interactions"""
    
    def __init__(self):
        self.disasters: List[Disaster] = []
        self.disaster_history: List[Disaster] = []
        self.global_resources: Dict[str, int] = {
            'ambulances': 20,
            'fire_trucks': 15,
            'rescue_teams': 25,
            'medical_supplies': 1000,
            'helicopters': 8,
            'boats': 12
        }
        self.allocated_resources: Dict[str, int] = {key: 0 for key in self.global_resources.keys()}
    
    def generate_random_disaster(self, grid_size: int) -> Disaster:
        """Generate a random disaster scenario"""
        disaster_type = random.choice(list(DisasterType))
        severity = random.choice(list(SeverityLevel))
        
        # Generate random parameters
        affected_area = random.uniform(5, 100)  # 5-100 square km
        casualties = random.randint(10, 500)
        duration_hours = random.randint(6, 72)  # 6 hours to 3 days
        location = (random.randint(0, grid_size-1), random.randint(0, grid_size-1))
        
        disaster = Disaster(
            type=disaster_type,
            severity=severity,
            affected_area=affected_area,
            casualties=casualties,
            injured=0,  # Will be calculated in __post_init__
            missing=0,  # Will be calculated in __post_init__
            infrastructure_damage=0.0,  # Will be calculated in __post_init__
            economic_impact=0.0,  # Will be calculated in __post_init__
            duration_hours=duration_hours,
            spread_rate=0.0,  # Will be calculated in __post_init__
            intensity=0.0,  # Will be calculated in __post_init__
            location=location,
            start_time=0
        )
        
        return disaster
    
    def add_disaster(self, disaster: Disaster):
        """Add a new disaster to the active list"""
        self.disasters.append(disaster)
    
    def update_all_disasters(self, time_step: int):
        """Update all active disasters"""
        for disaster in self.disasters[:]:  # Use slice to avoid modification during iteration
            disaster.update_disaster(time_step, self.allocated_resources)
            if not disaster.is_active:
                self.disaster_history.append(disaster)
                self.disasters.remove(disaster)
    
    def get_disaster_priority_order(self) -> List[Disaster]:
        """Get disasters ordered by priority for resource allocation"""
        return sorted(self.disasters, key=lambda d: d.get_priority_score(), reverse=True)
    
    def allocate_resources(self, disaster_id: int, resources: Dict[str, int]) -> bool:
        """Allocate resources to a specific disaster"""
        if disaster_id >= len(self.disasters):
            return False
        
        # Check if resources are available
        for resource_type, amount in resources.items():
            if self.allocated_resources[resource_type] + amount > self.global_resources[resource_type]:
                return False
        
        # Allocate resources
        for resource_type, amount in resources.items():
            self.allocated_resources[resource_type] += amount
        
        return True
    
    def get_total_impact(self) -> Dict[str, float]:
        """Get total impact across all active disasters"""
        total_casualties = sum(d.casualties for d in self.disasters)
        total_injured = sum(d.injured for d in self.disasters)
        total_missing = sum(d.missing for d in self.disasters)
        total_economic_impact = sum(d.economic_impact for d in self.disasters)
        total_affected_area = sum(d.affected_area for d in self.disasters)
        
        return {
            'total_casualties': total_casualties,
            'total_injured': total_injured,
            'total_missing': total_missing,
            'total_economic_impact': total_economic_impact,
            'total_affected_area': total_affected_area,
            'active_disasters': len(self.disasters)
        }
    
    def get_resource_utilization(self) -> Dict[str, float]:
        """Get resource utilization percentage"""
        utilization = {}
        for resource_type in self.global_resources:
            total = self.global_resources[resource_type]
            allocated = self.allocated_resources[resource_type]
            utilization[resource_type] = (allocated / total * 100) if total > 0 else 0
        return utilization
