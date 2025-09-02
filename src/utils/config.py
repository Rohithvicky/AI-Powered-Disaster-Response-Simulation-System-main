"""
Configuration module for the disaster response simulation system
"""

import json
import os
from typing import Dict, Any

class Config:
    """Configuration class for simulation parameters"""
    
    def __init__(self, config_file: str = None):
        """Initialize configuration with default values or from file"""
        self.config_file = config_file or "config.json"
        self.config = self._load_default_config()
        
        if os.path.exists(self.config_file):
            self._load_from_file()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values"""
        return {
            "simulation": {
                "grid_size": 20,
                "max_time_steps": 100,
                "disaster_types": ["earthquake", "flood", "fire", "storm"],
                "victim_count_range": (5, 15),
                "resource_count_range": (3, 8),
                "hazard_intensity_range": (0.1, 0.9)
            },
            "ai": {
                "heuristic_weight": 0.7,
                "exploration_weight": 0.3,
                "probability_threshold": 0.6,
                "max_search_depth": 10
            },
            "display": {
                "refresh_rate": 0.5,
                "show_probabilities": True,
                "show_paths": True,
                "color_output": True
            }
        }
    
    def _load_from_file(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                file_config = json.load(f)
                self._merge_config(file_config)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    
    def _merge_config(self, file_config: Dict[str, Any]):
        """Merge file configuration with default config"""
        for section, values in file_config.items():
            if section in self.config:
                if isinstance(values, dict):
                    self.config[section].update(values)
                else:
                    self.config[section] = values
            else:
                self.config[section] = values
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def save(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def get_simulation_config(self) -> Dict[str, Any]:
        """Get simulation configuration section"""
        return self.config.get("simulation", {})
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration section"""
        return self.config.get("ai", {})
    
    def get_display_config(self) -> Dict[str, Any]:
        """Get display configuration section"""
        return self.config.get("display", {})
