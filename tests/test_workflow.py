from src.workflow import Workflow
from src.models import PlannerRequest, UIElement, ActionType


def test_workflow_completes_successfully():
    workflow = Workflow(max_iterations=5)
    response = workflow.run(instruction="Go to settings", max_iterations=5)
    assert response.final_status == "success"
    assert response.summary_report.total_steps >= 1
    assert response.summary_report.completion_rate == 100.0
    assert len(response.execution_log.steps) >= 1


def test_workflow_done_immediately():
    workflow = Workflow(max_iterations=5)
    response = workflow.run(instruction="done", max_iterations=5)
    assert response.final_status == "success"
    assert len(response.execution_log.steps) == 1
    assert response.execution_log.steps[0].action == ActionType.DONE


def test_workflow_fails_max_iterations():
    workflow = Workflow(max_iterations=3)
    response = workflow.run(instruction="Do nothing", max_iterations=3)
    assert response.final_status == "failed"


def test_workflow_logs_steps():
    workflow = Workflow(max_iterations=5)
    response = workflow.run(instruction="click settings", max_iterations=5)
    assert len(response.execution_log.steps) >= 1
    last_step = response.execution_log.steps[-1]
    assert last_step.action in [ActionType.CLICK, ActionType.DONE]


def test_workflow_summary_report():
    workflow = Workflow(max_iterations=5)
    response = workflow.run(instruction="click settings", max_iterations=5)
    report = response.summary_report
    assert report.total_steps >= 1
    assert report.successful_steps >= 1
    assert report.completion_rate > 0
    assert report.total_duration_ms >= 0
    assert report.final_status in ["success", "failed"]


def test_workflow_run_single():
    workflow = Workflow()
    request = PlannerRequest(
        instruction="click settings",
        ui_elements=[UIElement(id="1", class_name="Button", bounds=[100, 200, 300, 400], text="Settings")]
    )
    response = workflow.run_single(request)
    assert response.action == ActionType.CLICK
    assert response.target_coordinates == [200, 300]


def test_workflow_with_type_instruction():
    workflow = Workflow(max_iterations=5)
    response = workflow.run(instruction="search for pandas", max_iterations=5)
    assert response.final_status in ["success", "failed"]
    if response.final_status == "success":
        assert response.summary_report.completion_rate == 100.0


def test_workflow_with_swipe_instruction():
    workflow = Workflow(max_iterations=5)
    response = workflow.run(instruction="scroll down", max_iterations=5)
    assert response.final_status in ["success", "failed"]


def test_workflow_execution_log_has_timestamps():
    workflow = Workflow(max_iterations=5)
    response = workflow.run(instruction="click settings", max_iterations=5)
    for step in response.execution_log.steps:
        assert step.timestamp is not None
        assert len(step.timestamp) > 0


def test_workflow_step_numbers_are_sequential():
    workflow = Workflow(max_iterations=5)
    response = workflow.run(instruction="done", max_iterations=5)
    for i, step in enumerate(response.execution_log.steps, 1):
        assert step.step_number == i


def test_workflow_screenshot_after_each_step():
    workflow = Workflow(max_iterations=5)
    response = workflow.run(instruction="click settings", max_iterations=5)
    for step in response.execution_log.steps:
        if step.status.value == "success":
            assert step.screenshot_path is not None