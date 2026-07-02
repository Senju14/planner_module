import json
import time
from datetime import datetime
from typing import List
from src.models import (
    ExecutionStep, ExecutionLog, SummaryReport,
    FailedStepDetail, StepStatus, WorkflowResponse
)


class Logger:

    def __init__(self):
        self.workflow_id: str = ""
        self.steps: List[ExecutionStep] = []
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    def start_workflow(self, workflow_id: str, instruction: str):
        self.workflow_id = workflow_id
        self.steps = []
        self.start_time = time.time()
        self.end_time = 0.0
        print(f"WORKFLOW STARTED | ID: {workflow_id} | Instruction: {instruction}")

    def log_step(self, step: ExecutionStep):
        self.steps.append(step)
        status_str = "[OK]" if step.status == StepStatus.SUCCESS else "[FAIL]" if step.status == StepStatus.FAILED else "[SKIP]"
        print(f"  {status_str} Step {step.step_number}: {step.action.value} (confidence: {step.confidence:.2f})")
        if step.reason:
            print(f"     Reason: {step.reason}")
        if step.error_message:
            print(f"     Error: {step.error_message}")

    def complete_workflow(self, final_status: str) -> ExecutionLog:
        self.end_time = time.time()
        duration_ms = (self.end_time - self.start_time) * 1000

        log = ExecutionLog(
            workflow_id=self.workflow_id,
            instruction=self.steps[0].reason if self.steps else "",
            steps=self.steps,
            final_status=final_status,
            started_at=datetime.fromtimestamp(self.start_time).isoformat(),
            completed_at=datetime.now().isoformat(),
            total_duration_ms=round(duration_ms, 2)
        )

        print(f"WORKFLOW COMPLETED | Status: {final_status.upper()} | Duration: {duration_ms:.0f}ms | Steps: {len(self.steps)}")
        return log

    def generate_summary(self, log: ExecutionLog) -> SummaryReport:
        total = len(log.steps)
        successful = sum(1 for s in log.steps if s.status == StepStatus.SUCCESS)
        failed = sum(1 for s in log.steps if s.status == StepStatus.FAILED)
        completion_rate = (successful / total * 100) if total > 0 else 0.0

        failed_details = []
        for s in log.steps:
            if s.status == StepStatus.FAILED:
                root_cause = self._analyze_root_cause(s)
                failed_details.append(FailedStepDetail(
                    step_number=s.step_number,
                    action=s.action,
                    reason=s.reason,
                    error_message=s.error_message,
                    root_cause=root_cause
                ))

        report = SummaryReport(
            total_steps=total,
            successful_steps=successful,
            failed_steps=failed,
            completion_rate=round(completion_rate, 2),
            failed_details=failed_details,
            total_duration_ms=log.total_duration_ms or 0.0,
            final_status=log.final_status
        )

        print(f"SUMMARY: {total} steps, {successful} success, {failed} failed, {completion_rate:.1f}% completion")
        return report

    def build_workflow_response(self, log: ExecutionLog, report: SummaryReport) -> WorkflowResponse:
        return WorkflowResponse(
            final_status=log.final_status,
            execution_log=log,
            summary_report=report
        )

    def _analyze_root_cause(self, step: ExecutionStep) -> str:
        error_lower = step.error_message.lower()
        if "timeout" in error_lower or "time out" in error_lower:
            return "UI element not found within timeout period"
        elif "not found" in error_lower or "no such" in error_lower:
            return "UI element not present on screen"
        elif "permission" in error_lower:
            return "Missing required permissions"
        elif "crash" in error_lower or "exception" in error_lower:
            return "Application crashed or threw exception"
        elif "invalid" in error_lower:
            return "Invalid action or parameters"
        elif "confidence" in error_lower:
            return "Low confidence in action selection"
        else:
            return f"Execution error: {step.error_message}" if step.error_message else "Unknown error"

    def export_json(self, log: ExecutionLog, report: SummaryReport, filepath: str = "workflow_log.json"):
        output = {
            "execution_log": log.model_dump(),
            "summary_report": report.model_dump()
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Log exported to: {filepath}")