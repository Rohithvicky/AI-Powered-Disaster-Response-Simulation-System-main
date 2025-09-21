    def _check_rescues(self):
        """Check if rescue team can rescue victims with resource usage tracking"""
        team_pos = self.state.rescue_team.position
        rescued = []
        
        for victim in self.state.victims:
            if victim.position == team_pos and self.state.rescue_team.resources > 0:
                # Check if rescue is successful based on survival probability and team efficiency
                rescue_success_rate = victim.survival_probability * self.state.rescue_team.efficiency
                
                if random.random() < rescue_success_rate:
                    self.state.rescue_team.resources -= 1
                    self.stats['victims_saved'] += 1
                    rescued.append(victim)
                    
                    # Update team status temporarily
                    self.state.rescue_team.status = "rescuing"
                    self.state.rescue_team.current_load += 1
                    
                    # Reset status after rescue to continue to next victim
                    self.state.rescue_team.status = "idle"
                    
                    # Determine which resources are available and used
                    available_resources = self._get_available_resources_nearby(team_pos)
                    used_resources = self._select_resources_for_rescue(available_resources)
                    
                    # Track rescue operation with specific resource usage
                    self.stats['rescue_operations'] = self.stats.get('rescue_operations', [])
                    self.stats['rescue_operations'].append({
                        'step': self.state.time_step,
                        'victim': victim.position,
                        'rescuer': team_pos,
                        'resources_used': used_resources,
                        'success': True,
                        'survival_probability': victim.survival_probability,
                        'injury_level': victim.injury_level
                    })
                    
                    # Add used resources at the victim's location for visualization
                    self._add_used_resources_at_victim_location(victim.position, used_resources)
                    
                    print(f"🎉 VICTIM RESCUED at {victim.position} (survival: {victim.survival_probability:.2f}, injury: {victim.injury_level}) using resources: {used_resources}")
                else:
                    print(f"❌ RESCUE FAILED at {victim.position} (survival: {victim.survival_probability:.2f}, efficiency: {self.state.rescue_team.efficiency:.2f})")
        
        for victim in rescued:
            self.state.victims.remove(victim)
