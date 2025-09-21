# Realistic Disaster Response System

## 🌪️ **How Disasters Work Now**

### **Disaster Spread Mechanics**
- **Realistic Spreading**: Disasters spread based on terrain type and intensity
- **Terrain Susceptibility**: 
  - 🔥 **Fire**: Spreads faster through grass (G) and urban (U) areas
  - 🌊 **Flood**: Affects grass (G) and urban (U) areas more
  - 🌍 **Earthquake**: Damages urban (U) and rock (R) areas more severely
- **Intensity Changes**: Hazards can intensify or weaken over time
- **New Hazards**: Random new hazards appear (10% chance each step)

### **Smart Rescue Team Behavior**
- **Risk Assessment**: Rescuer calculates path risk to each victim
- **Safest Victim First**: Chooses victim with lowest risk path
- **Disaster Avoidance**: Avoids high-risk areas (intensity > 0.5)
- **Alternative Paths**: Finds safer routes when direct path is blocked
- **Strategic Movement**: Balances distance vs. safety

## 🎯 **Rescue Strategy**

### **Victim Prioritization**
1. **Calculate Risk**: For each victim, calculate total path risk
2. **Consider Distance**: Factor in distance (closer = better)
3. **Choose Safest**: Select victim with lowest combined risk + distance
4. **Smart Pathfinding**: Find safe route avoiding high-risk areas

### **Movement Rules**
- **Safe Movement**: Prefers paths with risk < 0.5
- **Alternative Routes**: If direct path blocked, find safer alternative
- **Risk Tolerance**: Will accept some risk (up to 0.7) if necessary
- **Stuck Prevention**: If completely blocked, tries to move away from danger

## 🚨 **Disaster Types & Behavior**

### **Fire** 🔥
- **Spreads**: Fast through grass and urban areas
- **Intensity**: Can grow quickly in dry conditions
- **Resources Needed**: Fire trucks, helicopters for air drops

### **Flood** 🌊
- **Spreads**: From edges inward, affects low-lying areas
- **Terrain**: Grass and urban areas most affected
- **Resources Needed**: Boats, helicopters for rescue

### **Earthquake** 🌍
- **Spreads**: Affects urban and rocky areas most
- **Intensity**: Can cause secondary hazards
- **Resources Needed**: Heavy machinery, medical supplies

### **Hurricane** 🌀
- **Spreads**: Circular pattern with eye wall
- **Intensity**: Strongest at eye wall, calm in center
- **Resources Needed**: Helicopters, emergency shelters

### **Tornado** 🌪️
- **Spreads**: Spiral pattern from center
- **Intensity**: Varies with distance from center
- **Resources Needed**: Ambulances, medical supplies

## 🎮 **What You'll See**

### **Visual Indicators**
- **Red Areas**: High-risk disaster zones (avoid these!)
- **Orange Areas**: Medium-risk zones (caution)
- **Yellow Areas**: Low-risk zones (safer)
- **Rescuer Movement**: Shows risk level of chosen path
- **AI Decisions**: Displays risk assessment for each move

### **Sound Effects**
- **Resource Sounds**: Play when resources are used
- **Success Sounds**: Play when rescue is successful
- **No Duplicates**: Each rescue triggers sounds only once

### **Realistic Scenarios**
- **Disaster Growth**: Watch disasters spread and intensify
- **Strategic Rescues**: Rescuer chooses safest victims first
- **Risk Management**: See how rescuer avoids dangerous areas
- **Resource Usage**: Used resources appear at rescue locations

## 🧪 **Testing the System**

1. **Start Simulation**: Click "Start" button
2. **Watch Disasters**: Observe how they spread over time
3. **Follow Rescuer**: See how it chooses safest paths
4. **Listen for Sounds**: Hear resource sounds when rescues happen
5. **Check AI Decisions**: See risk assessments in the panel

## 🎯 **Key Improvements**

✅ **Realistic Disaster Spread**: Disasters now spread based on terrain and type
✅ **Smart Pathfinding**: Rescuer avoids high-risk areas
✅ **Strategic Victim Selection**: Chooses safest victims first
✅ **Risk Assessment**: Shows risk level for each movement
✅ **Disaster Escalation**: New hazards can appear over time
✅ **Terrain Effects**: Different terrains affect disaster spread
✅ **Sound Management**: No duplicate sounds per rescue

The system now provides a realistic disaster response simulation where rescuers must make strategic decisions to save victims while avoiding dangerous areas! 🚨🚑
