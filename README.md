# Console-Based AI Disaster Response Simulation System

A comprehensive, console-based disaster response simulation system that models real-world disasters using AI algorithms and probabilistic reasoning. This system is designed for training, educational purposes, and research in disaster response optimization.

## 🚀 Features

### Core Simulation Engine
- **Scenario Generation**: Randomly generate disaster environments (earthquakes, floods, fires, storms)
- **Grid-Based Environment**: Interactive grid maps with hazards, resources, and victims
- **Real-Time Simulation**: Dynamic disaster evolution with uncertain outcomes
- **Interactive Decision-Making**: User-guided rescue strategies and resource allocation

### AI Algorithms & Decision Making
- **Heuristic Search**: A* and Best-First Search algorithms for optimal pathfinding
- **Probabilistic Reasoning**: Bayesian networks for handling uncertainty in disasters
- **Risk Assessment**: Dynamic risk calculation and survival probability estimation
- **Optimal Action Selection**: AI-guided rescue team decision-making

### Console Interface
- **Color-Coded Grid Display**: Visual representation of the disaster environment
- **Real-Time Metrics**: Live updates on rescue progress and efficiency
- **Interactive Controls**: User commands for simulation control
- **Progress Tracking**: Comprehensive statistics and performance metrics

### Web App (FastAPI + Static Frontend)
- **Endpoints**: `/api/state`, `/api/step`, `/api/reset`, `/api/move`, `/api/recommend_path`, `/api/collect`, `/api/rescue`
- **Frontend**: Served from `/` - open `http://127.0.0.1:8000`
- **Controls**: Step, recommend, move-by-click, collect, and rescue

## 🛠️ Technology Stack

- **Programming Language**: Python 3.8+
- **Backend**: FastAPI + Uvicorn
- **Frontend**: HTML/CSS/JS (static)
- **AI Algorithms**: A*, Best-First Search, Bayesian Networks
- **Console UI**: Colorama for cross-platform colored output

## 🚦 Getting Started (Web)

1. Install deps
```bash
python -m pip install -r requirements.txt --disable-pip-version-check
```
2. Start server (local only)
```bash
python -m uvicorn web_server:app --host 127.0.0.1 --port 8000
```
3. Open the app
```text
http://127.0.0.1:8000
```

## 📁 Project Structure

```
src/
├── models/                 # AI algorithms and models
│   ├── heuristic_search.py    # A* and Best-First Search
│   └── probabilistic_reasoning.py  # Bayesian networks
├── simulation/            # Core simulation engine
│   ├── disaster_simulator.py   # Console simulator
│   ├── scenario_generator.py   # Scenario creation
│   ├── rescue_team.py         # Rescue team management
│   └── web_simulator.py       # Step-based simulator for web API
├── interface/             # Console interface
│   └── console_interface.py   # Console display and input
└── utils/                 # Utilities and configuration
    └── config.py              # Configuration management

web/
├── index.html
├── main.js
└── styles.css
```

## API Quick Reference
- `GET /api/state` → current state + stats
- `POST /api/step` → advance simulation by one step
- `POST /api/reset` → new scenario
- `POST /api/move` → body `{i,j}`
- `GET /api/recommend_path` → suggested path to nearest victim
- `GET /api/risk?i=..&j=..` → hazard risk at cell
- `POST /api/collect` → collect resource at team location
- `POST /api/rescue` → attempt rescue at team location

## Console Usage
```bash
python main.py
```

```bash
python test_system.py
```

## Notes
- Bind to `127.0.0.1` for local browsing on Windows.
- If port is busy, use `--port 8080` and open `http://127.0.0.1:8080`.
