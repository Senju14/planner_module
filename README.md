# Planner Module

Planner Module for Vision UI Navigation Agent. It takes user instructions and UI elements, then outputs structured JSON actions (CLICK, TYPE, SWIPE, WAIT, DONE).

## Introduction

This is the core decision-making component of a Vision UI Navigation Agent. The system runs in a multi-step loop:

1. Vision scans the UI and detects elements
2. Planner decides the next action based on instruction + UI elements
3. Executor performs the action
4. Logger records the step
5. Repeat until task is done or max iterations reached

## Goal

Automate UI navigation using visual inputs. The agent receives screenshots and user instructions, identifies UI elements, maps instructions to actions, and executes navigation steps autonomously.

## How to Run

### 1. Setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start API

```powershell
python app.py
```

Open http://localhost:8000/docs for Swagger UI.

### 3. Run Tests

```powershell
pytest .\tests\ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/planner` | Generate one action |
| POST | `/workflow` | Run full workflow |
| GET | `/workflow/{id}` | Get workflow log |
| GET | `/workflow` | List all logs |

## Project Structure

```
planner_module/
├── app.py              # FastAPI server
├── requirements.txt    # Dependencies
├── src/
│   ├── models.py       # Data models
│   ├── prompt.py       # System prompt
│   ├── planner.py      # Action planner
│   ├── workflow.py     # Multi-step loop
│   ├── mocks.py        # Mock modules
│   └── logger.py       # Logger + summary
└── tests/
    ├── test_app.py
    ├── test_planner.py
    └── test_workflow.py