import uvicorn
from fastapi import FastAPI, HTTPException
from src.models import (
    PlannerRequest, PlannerResponse,
    WorkflowRequest, WorkflowResponse,
)
from src.planner import Planner
from src.workflow import Workflow

app = FastAPI(title="Planner Module API", version="2.0.0", docs_url="/docs", redoc_url="/redoc")

planner = Planner()
workflow_engine = Workflow(max_iterations=10)
workflow_logs: dict[str, WorkflowResponse] = {}


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "Planner Module API is running.",
        "version": "2.0.0",
        "endpoints": {
            "GET /": "Health check",
            "POST /planner": "Generate single action",
            "POST /workflow": "Run multi-step workflow",
            "GET /workflow/{id}": "Get workflow log",
            "GET /docs": "Swagger UI"
        }
    }


@app.post("/planner", response_model=PlannerResponse)
def run_planner(request: PlannerRequest):
    try:
        return planner.generate_action(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planner error: {str(e)}")


@app.post("/workflow", response_model=WorkflowResponse)
def run_workflow(request: WorkflowRequest):
    try:
        response = workflow_engine.run(instruction=request.instruction, max_iterations=10)
        workflow_id = response.execution_log.workflow_id
        workflow_logs[workflow_id] = response
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")


@app.get("/workflow/{workflow_id}")
def get_workflow_log(workflow_id: str):
    if workflow_id not in workflow_logs:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found.")
    return workflow_logs[workflow_id]


@app.get("/workflow")
def list_workflow_logs():
    return {
        "total_workflows": len(workflow_logs),
        "workflow_ids": list(workflow_logs.keys()),
        "workflows": [
            {
                "id": wid,
                "status": w.execution_log.final_status,
                "steps": len(w.execution_log.steps),
                "completion_rate": w.summary_report.completion_rate,
                "duration_ms": w.summary_report.total_duration_ms
            }
            for wid, w in workflow_logs.items()
        ]
    }


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True, log_level="info")