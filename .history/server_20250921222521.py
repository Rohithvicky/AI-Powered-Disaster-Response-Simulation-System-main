"""
AI Disaster Response Simulation - Main Server
Simplified and compressed version
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from typing import Dict, Any

from src.simulation.web_simulator import WebSimulator
from src.utils.config import Config

app = FastAPI(title="AI Disaster Response Simulation", version="2.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global simulator instance
simulator = None

@app.on_event("startup")
async def startup_event():
    global simulator
    config = Config()
    simulator = WebSimulator(config)
    print("🚀 AI Disaster Response Simulation System initialized")

# Static files
app.mount("/static", StaticFiles(directory="web"), name="static")

# Routes
@app.get("/")
async def serve_dashboard():
    return FileResponse("web/index.html")

@app.get("/styles.css")
async def serve_styles():
    return FileResponse("web/styles.css")

@app.get("/main.js")
async def serve_js():
    return FileResponse("web/main.js")

# API Endpoints
@app.get("/api/state")
async def get_state():
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    return {"state": simulator.serialize_state()}

@app.post("/api/reset")
async def reset_simulation():
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    simulator.reset()
    return {"message": "Simulation reset", "state": simulator.serialize_state()}

@app.post("/api/step")
async def step_simulation():
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    result = simulator.step()
    return {"message": "Simulation stepped", "result": result, "state": simulator.serialize_state()}

@app.post("/api/move")
async def move_team(data: Dict[str, int]):
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    result = simulator.move_team(data["r"], data["c"])
    return result

@app.get("/api/recommend_path")
async def recommend_path():
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    team_pos = simulator.state.rescue_team.position
    return simulator.recommend_path_to_nearest_victim(team_pos[0], team_pos[1])

@app.get("/api/risk/{r}/{c}")
async def get_risk(r: int, c: int):
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    return simulator.get_risk_at(r, c)

@app.get("/api/summary")
async def get_summary():
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    return simulator.get_summary()

if __name__ == "__main__":
    print("🚀 Starting AI Disaster Response Simulation Server...")
    print("📊 Professional Dashboard: http://localhost:8000")
    print("🔧 API Documentation: http://localhost:8000/docs")
    print("⚡ Server running on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
