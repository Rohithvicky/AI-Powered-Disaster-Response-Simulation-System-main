from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import random

# Import our enhanced simulation components
from src.simulation.enhanced_simulator import EnhancedDisasterSimulator
from src.models.disaster import DisasterManager, DisasterType, SeverityLevel
from src.models.ai_decision_engine import AIDecisionEngine, DecisionType

app = FastAPI(
    title="AI Disaster Response Simulation API",
    description="Professional AI-powered disaster response simulation system",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global simulation instance
simulator = None
simulation_running = False
simulation_paused = False

@app.on_event("startup")
async def startup_event():
    """Initialize the simulation system on startup"""
    global simulator
    simulator = EnhancedDisasterSimulator(grid_size=20)
    print("🚀 Enhanced AI Disaster Response Simulation System initialized")

@app.get("/")
async def serve_enhanced_dashboard():
    """Serve the enhanced professional dashboard"""
    return FileResponse("web/enhanced_index.html")

@app.get("/api/state")
async def get_simulation_state():
    """Get current simulation state"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        state = simulator._get_simulation_state()
        return {
            "success": True,
            "state": state,
            "timestamp": datetime.now().isoformat(),
            "simulation_running": simulation_running,
            "simulation_paused": simulation_paused
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting simulation state: {str(e)}")

@app.post("/api/start")
async def start_simulation(data: Dict[str, Any] = None):
    """Start the simulation"""
    global simulation_running, simulation_paused
    
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    if simulation_running:
        raise HTTPException(status_code=400, detail="Simulation already running")
    
    try:
        auto_mode = data.get("auto_mode", True) if data else True
        simulator.start_simulation(auto_mode=auto_mode)
        simulation_running = True
        simulation_paused = False
        
        return {
            "success": True,
            "message": "Simulation started successfully",
            "auto_mode": auto_mode,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting simulation: {str(e)}")

@app.post("/api/stop")
async def stop_simulation():
    """Stop the simulation"""
    global simulation_running, simulation_paused
    
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    if not simulation_running:
        raise HTTPException(status_code=400, detail="Simulation not running")
    
    try:
        simulator.stop_simulation()
        simulation_running = False
        simulation_paused = False
        
        return {
            "success": True,
            "message": "Simulation stopped successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping simulation: {str(e)}")

@app.post("/api/reset")
async def reset_simulation():
    """Reset the simulation to initial state"""
    global simulation_running, simulation_paused
    
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        simulator.stop_simulation()
        simulation_running = False
        simulation_paused = False
        
        # Reinitialize simulator
        simulator = EnhancedDisasterSimulator(grid_size=20)
        
        return {
            "success": True,
            "message": "Simulation reset successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting simulation: {str(e)}")

@app.post("/api/step")
async def step_simulation():
    """Execute one simulation step"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    if not simulation_running:
        raise HTTPException(status_code=400, detail="Simulation not running")
    
    try:
        result = simulator.step_simulation()
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stepping simulation: {str(e)}")

@app.post("/api/pause")
async def pause_simulation():
    """Pause the simulation"""
    global simulation_paused
    
    if not simulation_running:
        raise HTTPException(status_code=400, detail="Simulation not running")
    
    simulation_paused = True
    return {
        "success": True,
        "message": "Simulation paused",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/resume")
async def resume_simulation():
    """Resume the simulation"""
    global simulation_paused
    
    if not simulation_running:
        raise HTTPException(status_code=400, detail="Simulation not running")
    
    simulation_paused = False
    return {
        "success": True,
        "message": "Simulation resumed",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/disasters")
async def get_disasters():
    """Get all active disasters"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        disasters = simulator.disaster_manager.disasters
        disaster_data = []
        
        for i, disaster in enumerate(disasters):
            disaster_data.append({
                "id": i,
                "type": disaster.type.value,
                "severity": disaster.severity.value,
                "casualties": disaster.casualties,
                "injured": disaster.injured,
                "missing": disaster.missing,
                "affected_area": disaster.affected_area,
                "location": disaster.location,
                "is_active": disaster.is_active,
                "priority_score": disaster.get_priority_score(),
                "required_resources": disaster.get_required_resources()
            })
        
        return {
            "success": True,
            "disasters": disaster_data,
            "count": len(disaster_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting disasters: {str(e)}")

@app.get("/api/rescue_teams")
async def get_rescue_teams():
    """Get all rescue teams"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        teams = simulator.rescue_teams
        team_data = []
        
        for i, team in enumerate(teams):
            team_data.append({
                "id": i,
                "position": team.position,
                "specialization": team.specialization,
                "efficiency": team.efficiency,
                "fatigue": team.fatigue,
                "max_fatigue": team.max_fatigue,
                "resources": team.resources
            })
        
        return {
            "success": True,
            "teams": team_data,
            "count": len(team_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting rescue teams: {str(e)}")

@app.get("/api/resources")
async def get_resources():
    """Get resource status"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        global_resources = simulator.disaster_manager.global_resources
        allocated_resources = simulator.disaster_manager.allocated_resources
        utilization = simulator.disaster_manager.get_resource_utilization()
        
        return {
            "success": True,
            "global_resources": global_resources,
            "allocated_resources": allocated_resources,
            "utilization": utilization,
            "available_resources": {
                resource: global_resources[resource] - allocated_resources[resource]
                for resource in global_resources
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting resources: {str(e)}")

@app.post("/api/allocate_resources")
async def allocate_resources(data: Dict[str, Any]):
    """Allocate resources to a specific disaster"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        disaster_id = data.get("disaster_id")
        resources = data.get("resources", {})
        
        if disaster_id is None:
            raise HTTPException(status_code=400, detail="disaster_id is required")
        
        success = simulator.disaster_manager.allocate_resources(disaster_id, resources)
        
        if success:
            return {
                "success": True,
                "message": f"Resources allocated to disaster {disaster_id}",
                "allocated_resources": resources
            }
        else:
            return {
                "success": False,
                "message": "Failed to allocate resources - insufficient availability"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error allocating resources: {str(e)}")

@app.get("/api/ai_decisions")
async def get_ai_decisions():
    """Get AI decision history"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        decisions = simulator.decision_history
        decision_data = []
        
        for decision in decisions:
            decision_data.append({
                "decision_type": decision.decision_type.value,
                "action": decision.action,
                "target_disaster_id": decision.target_disaster_id,
                "resources_allocated": decision.resources_allocated,
                "reasoning": decision.reasoning,
                "expected_effectiveness": decision.expected_effectiveness,
                "confidence": decision.confidence,
                "risk_level": decision.risk_level,
                "time_to_implement": decision.time_to_implement,
                "cost": decision.cost
            })
        
        return {
            "success": True,
            "decisions": decision_data,
            "count": len(decision_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting AI decisions: {str(e)}")

@app.get("/api/analytics")
async def get_analytics():
    """Get comprehensive simulation analytics"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        ai_analytics = simulator.ai_decision_engine.get_decision_analytics()
        simulation_summary = simulator.get_simulation_summary()
        
        return {
            "success": True,
            "ai_analytics": ai_analytics,
            "simulation_summary": simulation_summary,
            "performance_history": simulator.performance_history[-20:],  # Last 20 steps
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")

@app.get("/api/metrics")
async def get_metrics():
    """Get current simulation metrics"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        metrics = simulator.metrics
        return {
            "success": True,
            "metrics": {
                "time_steps": metrics.time_steps,
                "total_casualties": metrics.total_casualties,
                "casualties_saved": metrics.casualties_saved,
                "casualties_prevented": metrics.casualties_prevented,
                "resources_used": metrics.resources_used,
                "resources_remaining": metrics.resources_remaining,
                "economic_impact": metrics.economic_impact,
                "response_efficiency": metrics.response_efficiency,
                "decision_accuracy": metrics.decision_accuracy,
                "evacuation_orders": metrics.evacuation_orders,
                "emergency_responses": metrics.emergency_responses,
                "disasters_resolved": metrics.disasters_resolved,
                "active_disasters": metrics.active_disasters,
                "total_cost": metrics.total_cost,
                "average_response_time": metrics.average_response_time
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")

@app.get("/api/settings")
async def get_settings():
    """Get current simulation settings"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        return {
            "success": True,
            "settings": {
                "grid_size": simulator.grid_size,
                "auto_mode": simulator.auto_mode,
                "real_time_mode": simulator.realTimeMode,
                "simulation_running": simulation_running,
                "simulation_paused": simulation_paused
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting settings: {str(e)}")

@app.post("/api/settings")
async def update_settings(data: Dict[str, Any]):
    """Update simulation settings"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        if "grid_size" in data:
            simulator.grid_size = data["grid_size"]
        
        if "auto_mode" in data:
            simulator.auto_mode = data["auto_mode"]
        
        if "real_time_mode" in data:
            simulator.realTimeMode = data["real_time_mode"]
        
        return {
            "success": True,
            "message": "Settings updated successfully",
            "settings": {
                "grid_size": simulator.grid_size,
                "auto_mode": simulator.auto_mode,
                "real_time_mode": simulator.realTimeMode
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating settings: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "simulation_initialized": simulator is not None,
        "simulation_running": simulation_running,
        "simulation_paused": simulation_paused
    }

# Mount static files
app.mount("/static", StaticFiles(directory="web"), name="static")

if __name__ == "__main__":
    print("🚀 Starting Enhanced AI Disaster Response Simulation Server...")
    print("📊 Professional Dashboard: http://localhost:8000")
    print("🔧 API Documentation: http://localhost:8000/docs")
    print("⚡ Server running on http://127.0.0.1:8000")
    
    uvicorn.run(
        "enhanced_web_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
