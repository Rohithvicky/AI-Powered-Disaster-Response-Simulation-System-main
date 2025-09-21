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

# Import our existing simulation components
from src.simulation.web_simulator import WebSimulator
from src.utils.config import Config

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
    config = Config()
    simulator = WebSimulator(config)
    print("🚀 AI Disaster Response Simulation System initialized")

@app.get("/")
async def serve_dashboard():
    """Serve the enhanced professional dashboard"""
    return FileResponse("web/index.html")

@app.get("/styles.css")
async def serve_styles():
    """Serve the CSS"""
    return FileResponse("web/styles.css")

@app.get("/main.js")
async def serve_js():
    """Serve the JavaScript"""
    return FileResponse("web/main.js")

@app.get("/favicon.ico")
async def serve_favicon():
    """Serve favicon - return no content"""
    from fastapi.responses import Response
    return Response(status_code=204)

@app.get("/api/state")
async def get_simulation_state():
    """Get current simulation state"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        if simulator.state is None:
            # Initialize if not already done
            simulator.reset()
        
        state = simulator.serialize_state()
        
        # Transform the state to match what the enhanced dashboard expects
        enhanced_state = {
            "time_step": state.get("time_step", 0),
            "grid_size": state.get("grid_size", 20),
            "grid": state.get("grid", []),
            "hazards": state.get("hazards", []),
            "victims": state.get("victims", []),
            "resources": state.get("resources", []),
            "rescue_team": state.get("rescue_team", {}),
            "survival_probabilities": state.get("survival_probabilities", []),
            "metrics": {
                "time_steps": state.get("time_step", 0),
                "total_casualties": len(state.get("victims", [])),
                "casualties_saved": simulator.stats.get("victims_saved", 0),
                "casualties_prevented": 0,
                "resources_used": simulator.stats.get("resources_used", 0),
                "resources_remaining": simulator.stats.get("initial_resources", 0) - simulator.stats.get("resources_used", 0),
                "economic_impact": 0.0,
                "response_efficiency": simulator.stats.get("efficiency_score", 0.0),
                "decision_accuracy": 0.8,
                "evacuation_orders": 0,
                "emergency_responses": 0,
                "disasters_resolved": 0,
                "active_disasters": len([h for h in state.get("hazards", []) if h[2] > 0.5]),
                "total_cost": 0.0,
                "average_response_time": 2.5
            },
            "disasters": [
                {
                    "id": i,
                    "type": "hazard",
                    "severity": "high" if h[2] > 0.8 else "medium" if h[2] > 0.5 else "low",
                    "casualties": int(h[2] * 100),
                    "injured": int(h[2] * 50),
                    "missing": int(h[2] * 20),
                    "affected_area": h[2] * 10,
                    "location": [h[0], h[1]],
                    "is_active": h[2] > 0.5,
                    "priority_score": h[2]
                }
                for i, h in enumerate(state.get("hazards", []))
                if h[2] > 0.5
            ],
            "rescue_teams": [
                {
                    "id": 0,
                    "position": state.get("rescue_team", {}).get("position", [0, 0]),
                    "specialization": "general",
                    "efficiency": state.get("rescue_team", {}).get("efficiency", 1.0),
                    "fatigue": state.get("rescue_team", {}).get("fatigue", 0),
                    "max_fatigue": 100,
                    "resources": state.get("rescue_team", {}).get("resources", 10)
                }
            ],
            "resource_utilization": {
                "ambulances": 20.0,
                "fire_trucks": 15.0,
                "rescue_teams": 30.0,
                "medical_supplies": 25.0,
                "helicopters": 10.0,
                "boats": 5.0
            },
            "ai_analytics": {
                "total_decisions": 0,
                "average_effectiveness": 0.8,
                "average_confidence": 0.85,
                "total_cost": 0.0,
                "decision_type_distribution": {}
            }
        }
        
        return {
            "success": True,
            "state": enhanced_state,
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
        simulator.reset()
        simulation_running = True
        simulation_paused = False
        
        return {
            "success": True,
            "message": "Simulation started successfully",
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
        simulator.reset()
        simulation_running = False
        simulation_paused = False
        
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
        result = simulator.step()
        
        # Get the updated state after stepping
        state = simulator.serialize_state()
        
        # Transform the state to match what the enhanced dashboard expects
        enhanced_state = {
            "time_step": state.get("time_step", 0),
            "grid_size": state.get("grid_size", 20),
            "grid": state.get("grid", []),
            "hazards": state.get("hazards", []),
            "victims": state.get("victims", []),
            "resources": state.get("resources", []),
            "rescue_team": state.get("rescue_team", {}),
            "survival_probabilities": state.get("survival_probabilities", []),
            "metrics": {
                "time_steps": state.get("time_step", 0),
                "total_casualties": len(state.get("victims", [])),
                "casualties_saved": simulator.stats.get("victims_saved", 0),
                "casualties_prevented": 0,
                "resources_used": simulator.stats.get("resources_used", 0),
                "resources_remaining": simulator.stats.get("initial_resources", 0) - simulator.stats.get("resources_used", 0),
                "economic_impact": 0.0,
                "response_efficiency": simulator.stats.get("efficiency_score", 0.0),
                "decision_accuracy": 0.8,
                "evacuation_orders": 0,
                "emergency_responses": 0,
                "disasters_resolved": 0,
                "active_disasters": len([h for h in state.get("hazards", []) if h[2] > 0.5]),
                "total_cost": 0.0,
                "average_response_time": 2.5
            },
            "disasters": [
                {
                    "id": i,
                    "type": "hazard",
                    "severity": "high" if h[2] > 0.8 else "medium" if h[2] > 0.5 else "low",
                    "casualties": int(h[2] * 100),
                    "injured": int(h[2] * 50),
                    "missing": int(h[2] * 20),
                    "affected_area": h[2] * 10,
                    "location": [h[0], h[1]],
                    "is_active": h[2] > 0.5,
                    "priority_score": h[2]
                }
                for i, h in enumerate(state.get("hazards", []))
                if h[2] > 0.5
            ],
            "rescue_teams": [
                {
                    "id": 0,
                    "position": state.get("rescue_team", {}).get("position", [0, 0]),
                    "specialization": "general",
                    "efficiency": state.get("rescue_team", {}).get("efficiency", 1.0),
                    "fatigue": state.get("rescue_team", {}).get("fatigue", 0),
                    "max_fatigue": 100,
                    "resources": state.get("rescue_team", {}).get("resources", 10)
                }
            ],
            "resource_utilization": {
                "ambulances": 20.0,
                "fire_trucks": 15.0,
                "rescue_teams": 30.0,
                "medical_supplies": 25.0,
                "helicopters": 10.0,
                "boats": 5.0
            },
            "ai_analytics": {
                "total_decisions": 0,
                "average_effectiveness": 0.8,
                "average_confidence": 0.85,
                "total_cost": 0.0,
                "decision_type_distribution": {}
            }
        }
        
        return {
            "success": True,
            "result": {
                "state": enhanced_state
            },
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
    """Get all active disasters (simplified)"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        # Return simplified disaster data
        disasters = []
        if simulator.state and hasattr(simulator.state, 'hazards'):
            for (i, j), intensity in simulator.state.hazards.items():
                if intensity > 0.5:  # Consider high-intensity hazards as disasters
                    disasters.append({
                        "id": len(disasters),
                        "type": "hazard",
                        "severity": "high" if intensity > 0.8 else "medium",
                        "casualties": int(intensity * 100),
                        "location": [i, j],
                        "is_active": True,
                        "priority_score": intensity
                    })
        
        return {
            "success": True,
            "disasters": disasters,
            "count": len(disasters)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting disasters: {str(e)}")

@app.get("/api/rescue_teams")
async def get_rescue_teams():
    """Get all rescue teams"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        teams = []
        if simulator.state and hasattr(simulator.state, 'rescue_team'):
            team = simulator.state.rescue_team
            teams.append({
                "id": 0,
                "position": team.position,
                "specialization": "general",
                "efficiency": team.efficiency,
                "fatigue": team.fatigue,
                "max_fatigue": 100,
                "resources": team.resources
            })
        
        return {
            "success": True,
            "teams": teams,
            "count": len(teams)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting rescue teams: {str(e)}")

@app.get("/api/resources")
async def get_resources():
    """Get resource status"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        # Simplified resource data
        global_resources = {
            'ambulances': 10,
            'fire_trucks': 5,
            'rescue_teams': 8,
            'medical_supplies': 500,
            'helicopters': 3,
            'boats': 4
        }
        
        allocated_resources = {
            'ambulances': 2,
            'fire_trucks': 1,
            'rescue_teams': 3,
            'medical_supplies': 100,
            'helicopters': 1,
            'boats': 1
        }
        
        utilization = {}
        for resource in global_resources:
            total = global_resources[resource]
            allocated = allocated_resources[resource]
            utilization[resource] = (allocated / total * 100) if total > 0 else 0
        
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

@app.get("/api/metrics")
async def get_metrics():
    """Get current simulation metrics"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        stats = simulator.stats if simulator else {}
        return {
            "success": True,
            "metrics": {
                "time_steps": stats.get('time_steps', 0),
                "total_casualties": stats.get('initial_victims', 0),
                "casualties_saved": stats.get('victims_saved', 0),
                "casualties_prevented": 0,
                "resources_used": stats.get('resources_used', 0),
                "resources_remaining": stats.get('initial_resources', 0) - stats.get('resources_used', 0),
                "economic_impact": 0.0,
                "response_efficiency": stats.get('efficiency_score', 0.0),
                "decision_accuracy": 0.8,
                "evacuation_orders": 0,
                "emergency_responses": 0,
                "disasters_resolved": 0,
                "active_disasters": len(simulator.state.hazards) if simulator.state else 0,
                "total_cost": 0.0,
                "average_response_time": 2.5
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")

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

@app.get("/api/legend")
async def get_legend():
    """Get simulation legend"""
    return {
        "success": True,
        "legend": {
            "terrain": {
                "G": {"name": "Green Area", "color": "#10b981", "description": "Safe zones and parks"},
                "W": {"name": "Water", "color": "#06b6d4", "description": "Rivers and lakes"},
                "R": {"name": "Urban Red", "color": "#ef4444", "description": "High-risk urban areas"},
                "U": {"name": "Urban", "color": "#6b7280", "description": "Urban infrastructure"}
            },
            "elements": {
                "hazards": {"name": "Hazards", "color": "rgba(239, 68, 68, 0.7)", "description": "Disaster zones with varying intensity"},
                "victims": {"name": "Victims", "color": "#f59e0b", "description": "People needing rescue"},
                "resources": {"name": "Resources", "color": "#10b981", "description": "Medical supplies and equipment"},
                "rescue_team": {"name": "Rescue Team", "color": "#3b82f6", "description": "Emergency response team"}
            }
        }
    }

@app.get("/api/telemetry")
async def get_telemetry():
    """Get simulation telemetry data"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        return {
            "success": True,
            "telemetry": simulator.telemetry,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting telemetry: {str(e)}")

@app.get("/api/summary")
async def get_simulation_summary():
    """Get simulation summary"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulation not initialized")
    
    try:
        stats = simulator.stats
        return {
            "success": True,
            "summary": {
                "total_steps": stats.get("time_steps", 0),
                "victims_saved": stats.get("victims_saved", 0),
                "resources_used": stats.get("resources_used", 0),
                "efficiency_score": stats.get("efficiency_score", 0.0),
                "initial_victims": stats.get("initial_victims", 0),
                "initial_resources": stats.get("initial_resources", 0),
                "total_risk": stats.get("total_risk", 0.0)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")

# Mount static files
app.mount("/static", StaticFiles(directory="web"), name="static")

if __name__ == "__main__":
    print("🚀 Starting AI Disaster Response Simulation Server...")
    print("📊 Professional Dashboard: http://localhost:8000")
    print("🔧 API Documentation: http://localhost:8000/docs")
    print("⚡ Server running on http://127.0.0.1:8000")
    
    uvicorn.run(
        "working_web_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
