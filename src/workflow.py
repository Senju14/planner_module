import uuid
import os
from src.planner import Planner
from src.mocks import MockVision, MockExecutor
from src.logger import Logger
from src.models import (
    PlannerRequest, PlannerResponse, WorkflowRequest, WorkflowResponse,
    ExecutionStep, StepStatus, ActionType
)


class Workflow:

    def __init__(self, max_iterations: int = 10, screenshot_dir: str = "screenshots"):
        self.planner = Planner()
        self.vision = MockVision()
        self.executor = MockExecutor()
        self.logger = Logger()
        self.max_iterations = max_iterations
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def run(self, instruction: str, max_iterations: int | None = None) -> WorkflowResponse:
        iterations = max_iterations or self.max_iterations
        workflow_id = str(uuid.uuid4())[:8]

        self.logger.start_workflow(workflow_id, instruction)

        current_instruction = instruction
        final_status = "success"

        last_action = None
        repeat_count = 0
        max_repeats = 3

        for i in range(iterations):
            step_number = i + 1
            print(f"Iteration {step_number}/{iterations}")

            ui_elements = self.vision.get_ui_elements()
            print(f"Vision: {len(ui_elements)} UI elements detected")

            request = PlannerRequest(
                instruction=current_instruction,
                ui_elements=ui_elements
            )
            action = self.planner.generate_action(request)
            print(f"Planner: {action.action.value} (confidence: {action.confidence:.2f})")

            if action.confidence < 0.3:
                self._log_failed_step(
                    step_number, action.action,
                    f"Confidence too low ({action.confidence:.2f})"
                )
                final_status = "failed"
                break

            current_key = (action.action.value, tuple(action.target_coordinates) if action.target_coordinates else None)
            if current_key == last_action:
                repeat_count += 1
            else:
                repeat_count = 0
            last_action = current_key

            if repeat_count >= max_repeats:
                print(f"Stuck detected after {repeat_count + 1} repeats, marking as DONE")
                action = PlannerResponse(
                    action=ActionType.DONE,
                    target_coordinates=None,
                    text_value="",
                    confidence=1.0,
                    reason="Stuck loop detected",
                    done=True
                )

            success, error_msg = self.executor.execute_action(action)

            screenshot_path = self.vision.capture_screenshot()

            step = ExecutionStep(
                step_number=step_number,
                action=action.action,
                target_coordinates=action.target_coordinates,
                text_value=action.text_value,
                confidence=action.confidence,
                reason=action.reason,
                status=StepStatus.SUCCESS if success else StepStatus.FAILED,
                error_message=error_msg if not success else "",
                screenshot_path=screenshot_path
            )
            self.logger.log_step(step)

            if not success:
                print(f"Step {step_number} failed: {error_msg}")
                final_status = "failed"
                break

            if action.action == ActionType.DONE or action.done:
                print(f"Task completed at step {step_number}")
                final_status = "success"
                break

            if action.action == ActionType.CLICK:
                current_instruction = f"Continue: {instruction}"

        else:
            print(f"Max iterations ({iterations}) reached without completion")
            final_status = "failed"

        log = self.logger.complete_workflow(final_status)
        log.instruction = instruction

        report = self.logger.generate_summary(log)
        response = self.logger.build_workflow_response(log, report)

        log_path = f"workflow_log_{workflow_id}.json"
        self.logger.export_json(log, report, log_path)

        return response

    def _log_failed_step(self, step_number: int, action: ActionType, error_message: str, reason: str = ""):
        step = ExecutionStep(
            step_number=step_number,
            action=action,
            target_coordinates=None,
            text_value="",
            confidence=0.0,
            reason=reason or error_message,
            status=StepStatus.FAILED,
            error_message=error_message
        )
        self.logger.log_step(step)

    def run_single(self, request: PlannerRequest) -> PlannerResponse:
        return self.planner.generate_action(request)