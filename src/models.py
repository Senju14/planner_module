from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ActionType(str, Enum):
    CLICK = "CLICK"
    TYPE = "TYPE"
    SWIPE = "SWIPE"
    WAIT = "WAIT"
    DONE = "DONE"


class UIElement(BaseModel):
    id: str
    class_name: str
    bounds: List[int]  # [x1, y1, x2, y2]
    text: Optional[str] = None
    content_description: Optional[str] = None


class PlannerRequest(BaseModel):
    instruction: str
    ui_elements: List[UIElement]


class PlannerResponse(BaseModel):
    action: ActionType = Field(description="Action to perform: CLICK, TYPE, SWIPE, WAIT, DONE")
    target_coordinates: Optional[List[int]] = Field(default=None, description="[x, y] coordinates")
    text_value: str = Field(default="", description="Text to type if action is TYPE")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    reason: str = Field(default="", description="Brief reason for the action")
    done: bool = Field(default=False, description="Whether the task is complete")


class StepStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class ExecutionStep(BaseModel):
    step_number: int
    action: ActionType
    target_coordinates: Optional[List[int]] = None
    text_value: str = ""
    confidence: float = 1.0
    reason: str = ""
    status: StepStatus = StepStatus.SUCCESS
    error_message: str = ""
    screenshot_path: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ExecutionLog(BaseModel):
    workflow_id: str
    instruction: str
    steps: List[ExecutionStep] = []
    final_status: str = "running"  # running, success, failed
    started_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    total_duration_ms: Optional[float] = None


class FailedStepDetail(BaseModel):
    step_number: int
    action: ActionType
    reason: str
    error_message: str
    root_cause: str = ""


class SummaryReport(BaseModel):
    total_steps: int
    successful_steps: int
    failed_steps: int
    completion_rate: float  # percentage 0-100
    failed_details: List[FailedStepDetail] = []
    total_duration_ms: float
    final_status: str


class WorkflowRequest(BaseModel):
    instruction: str
    initial_screenshot: Optional[str] = None  # base64 encoded or path


class WorkflowResponse(BaseModel):
    final_status: str  # success, failed
    execution_log: ExecutionLog
    summary_report: SummaryReport