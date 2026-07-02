from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "2.0.0"


def test_planner_endpoint_click():
    response = client.post("/planner", json={
        "instruction": "click settings",
        "ui_elements": [
            {
                "id": "btn1",
                "class_name": "android.widget.Button",
                "bounds": [100, 200, 300, 400],
                "text": "Settings",
                "content_description": "Settings button"
            }
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "CLICK"
    assert data["target_coordinates"] == [200, 300]
    assert data["done"] is False
    assert 0.0 <= data["confidence"] <= 1.0


def test_planner_endpoint_type():
    response = client.post("/planner", json={
        "instruction": "search for cat videos",
        "ui_elements": [
            {
                "id": "input_1",
                "class_name": "android.widget.EditText",
                "bounds": [50, 100, 350, 150],
                "text": "Search...",
                "content_description": "Search input field"
            }
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "TYPE"
    assert data["text_value"] != ""
    assert data["done"] is False


def test_planner_endpoint_done():
    response = client.post("/planner", json={
        "instruction": "done",
        "ui_elements": []
    })
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "DONE"
    assert data["done"] is True


def test_planner_endpoint_invalid_input():
    response = client.post("/planner", json={
        "instruction": "",
        "ui_elements": []
    })
    assert response.status_code == 200
    data = response.json()
    assert "action" in data


def test_workflow_endpoint_success():
    response = client.post("/workflow", json={
        "instruction": "click settings",
        "initial_screenshot": None
    })
    assert response.status_code == 200
    data = response.json()
    assert data["final_status"] in ["success", "failed"]
    assert "execution_log" in data
    assert "summary_report" in data
    assert data["summary_report"]["total_steps"] >= 1


def test_workflow_endpoint_done():
    response = client.post("/workflow", json={
        "instruction": "done",
        "initial_screenshot": None
    })
    assert response.status_code == 200
    data = response.json()
    assert data["final_status"] == "success"
    assert len(data["execution_log"]["steps"]) == 1
    assert data["execution_log"]["steps"][0]["action"] == "DONE"


def test_list_workflow_logs():
    client.post("/workflow", json={
        "instruction": "done",
        "initial_screenshot": None
    })
    response = client.get("/workflow")
    assert response.status_code == 200
    data = response.json()
    assert data["total_workflows"] >= 1
    assert len(data["workflow_ids"]) >= 1


def test_get_nonexistent_workflow():
    response = client.get("/workflow/nonexistent-id")
    assert response.status_code == 404