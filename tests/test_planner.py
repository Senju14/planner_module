from src.models import PlannerRequest, UIElement, ActionType
from src.planner import Planner


def test_planner_generates_click_for_settings():
    planner = Planner()
    request = PlannerRequest(
        instruction="click settings",
        ui_elements=[UIElement(id="1", class_name="Button", bounds=[100, 200, 300, 400], text="Settings")]
    )
    response = planner.generate_action(request)
    assert response.action == ActionType.CLICK
    assert response.target_coordinates == [200, 300]
    assert response.done is False
    assert response.confidence > 0.5


def test_planner_generates_click_for_open():
    planner = Planner()
    request = PlannerRequest(
        instruction="open profile",
        ui_elements=[UIElement(id="1", class_name="Button", bounds=[400, 200, 500, 300], text="Profile")]
    )
    response = planner.generate_action(request)
    assert response.action == ActionType.CLICK
    assert response.target_coordinates == [450, 250]
    assert response.done is False


def test_planner_generates_type_for_search():
    planner = Planner()
    request = PlannerRequest(
        instruction="search for cat videos",
        ui_elements=[
            UIElement(id="1", class_name="EditText", bounds=[50, 100, 350, 150], text="Search...")
        ]
    )
    response = planner.generate_action(request)
    assert response.action == ActionType.TYPE
    assert response.text_value != ""
    assert response.done is False


def test_planner_generates_type_input():
    planner = Planner()
    request = PlannerRequest(
        instruction="type hello world",
        ui_elements=[
            UIElement(id="1", class_name="EditText", bounds=[50, 100, 350, 150], text="Input")
        ]
    )
    response = planner.generate_action(request)
    assert response.action == ActionType.TYPE
    assert "hello" in response.text_value.lower() or "world" in response.text_value.lower()
    assert response.done is False


def test_planner_generates_done_for_finish():
    planner = Planner()
    request = PlannerRequest(
        instruction="finish the task",
        ui_elements=[]
    )
    response = planner.generate_action(request)
    assert response.action == ActionType.DONE
    assert response.done is True


def test_planner_generates_done_for_complete():
    planner = Planner()
    request = PlannerRequest(
        instruction="complete",
        ui_elements=[UIElement(id="1", class_name="Button", bounds=[0, 0, 10, 10], text="Done")]
    )
    response = planner.generate_action(request)
    assert response.action == ActionType.DONE
    assert response.done is True


def test_planner_generates_swipe():
    planner = Planner()
    request = PlannerRequest(
        instruction="swipe up",
        ui_elements=[UIElement(id="1", class_name="ListView", bounds=[0, 0, 400, 800], text="")]
    )
    response = planner.generate_action(request)
    assert response.action == ActionType.SWIPE
    assert response.target_coordinates is not None
    assert len(response.target_coordinates) == 4


def test_planner_generates_wait():
    planner = Planner()
    request = PlannerRequest(
        instruction="please wait",
        ui_elements=[UIElement(id="1", class_name="ProgressBar", bounds=[0, 0, 10, 10], text="Loading...")]
    )
    response = planner.generate_action(request)
    assert response.action == ActionType.WAIT
    assert response.done is False


def test_planner_fallback_on_unknown():
    planner = Planner()
    request = PlannerRequest(
        instruction="xyznonsense12345",
        ui_elements=[]
    )
    response = planner.generate_action(request)
    assert response.action in [ActionType.WAIT, ActionType.DONE]
    assert isinstance(response.done, bool)


def test_planner_response_is_valid():
    planner = Planner()
    request = PlannerRequest(
        instruction="click settings",
        ui_elements=[UIElement(id="1", class_name="Button", bounds=[0, 0, 10, 10], text="Settings")]
    )
    response = planner.generate_action(request)
    assert isinstance(response.action, ActionType)
    assert isinstance(response.done, bool)
    assert isinstance(response.confidence, float)
    assert 0.0 <= response.confidence <= 1.0
    assert isinstance(response.reason, str)
    assert isinstance(response.text_value, str)


def test_planner_no_ui_elements():
    planner = Planner()
    request = PlannerRequest(
        instruction="click something",
        ui_elements=[]
    )
    response = planner.generate_action(request)
    assert response.action in [ActionType.CLICK, ActionType.WAIT, ActionType.DONE]
    assert isinstance(response.done, bool)


def test_planner_with_multiple_elements():
    planner = Planner()
    request = PlannerRequest(
        instruction="open profile",
        ui_elements=[
            UIElement(id="1", class_name="Button", bounds=[100, 200, 300, 400], text="Settings"),
            UIElement(id="2", class_name="Button", bounds=[400, 200, 500, 300], text="Profile"),
            UIElement(id="3", class_name="TextView", bounds=[100, 500, 300, 600], text="Welcome"),
        ]
    )
    response = planner.generate_action(request)
    assert response.action == ActionType.CLICK
    assert response.target_coordinates == [450, 250]