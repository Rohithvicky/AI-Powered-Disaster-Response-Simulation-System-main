#!/usr/bin/env python3
"""
FastAPI backend for the web-based AI Disaster Response Simulation System
"""

import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.simulation.web_simulator import WebSimulator

app = FastAPI(title="AI Disaster Response Simulation API")

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sim = WebSimulator()

class MoveRequest(BaseModel):
    i: int
    j: int

# API endpoints
@app.get("/api/state")
def get_state() -> Dict[str, Any]:
    return {"state": sim.serialize_state(), "stats": sim.stats}

@app.post("/api/reset")
def reset() -> Dict[str, Any]:
    sim.reset()
    return {"ok": True, "state": sim.serialize_state(), "stats": sim.stats}

@app.post("/api/step")
def step() -> Dict[str, Any]:
    return sim.step()

@app.post("/api/move")
def move(req: MoveRequest) -> Dict[str, Any]:
    ok = sim.move_team(req.i, req.j)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid move")
    return {"ok": True, "state": sim.serialize_state()}

@app.get("/api/recommend_path")
def recommend_path() -> Dict[str, Any]:
    return {"path": sim.recommend_path_to_nearest_victim()}

@app.get("/api/risk")
def risk(i: int, j: int) -> Dict[str, Any]:
    return {"risk": sim.risk_at(i, j)}

@app.post("/api/collect")
def collect() -> Dict[str, Any]:
    res = sim.collect_here()
    return {**res, "state": sim.serialize_state(), "stats": sim.stats}

@app.post("/api/rescue")
def rescue() -> Dict[str, Any]:
    res = sim.rescue_here()
    return {**res, "state": sim.serialize_state(), "stats": sim.stats}

# Static frontend without shadowing /api routes
if os.path.isdir("web"):
    app.mount("/static", StaticFiles(directory="web"), name="static")

@app.get("/")
def root() -> FileResponse:
    return FileResponse(os.path.join("web", "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_server:app", host="0.0.0.0", port=8000, reload=False)
