import json
import uuid
from src.models import UIElement, PlannerResponse, ActionType


class MockVision:

    @staticmethod
    def get_ui_elements() -> list[UIElement]:
        return [
            UIElement(id="btn_settings", class_name="android.widget.Button", bounds=[100, 200, 300, 400], text="Settings", content_description="Settings button"),
            UIElement(id="txt_welcome", class_name="android.widget.TextView", bounds=[100, 500, 300, 600], text="Welcome", content_description="Welcome text"),
            UIElement(id="input_search", class_name="android.widget.EditText", bounds=[50, 100, 350, 150], text="Search...", content_description="Search input field"),
            UIElement(id="btn_profile", class_name="android.widget.Button", bounds=[400, 200, 500, 300], text="Profile", content_description="Profile button"),
            UIElement(id="btn_back", class_name="android.widget.ImageButton", bounds=[0, 0, 60, 60], text="", content_description="Navigate back"),
        ]

    @staticmethod
    def capture_screenshot() -> str:
        screenshot_id = str(uuid.uuid4())[:8]
        filepath = f"screenshots/screenshot_{screenshot_id}.png"
        print(f"Screenshot captured: {filepath}")
        return filepath


class MockExecutor:

    @staticmethod
    def execute_action(action: PlannerResponse) -> tuple[bool, str]:
        print(f"Executing: {action.action.value}", end="")
        if action.target_coordinates:
            print(f" at {action.target_coordinates}", end="")
        if action.text_value:
            print(f" text='{action.text_value}'", end="")
        print()

        if action.action == ActionType.CLICK:
            if action.target_coordinates:
                return True, ""
            return False, "No target coordinates provided for CLICK action"

        elif action.action == ActionType.TYPE:
            if action.text_value:
                return True, ""
            return False, "No text_value provided for TYPE action"

        elif action.action == ActionType.SWIPE:
            if action.target_coordinates and len(action.target_coordinates) == 4:
                return True, ""
            return False, "Invalid coordinates for SWIPE action (need [x1, y1, x2, y2])"

        elif action.action == ActionType.WAIT:
            return True, ""

        elif action.action == ActionType.DONE:
            return True, ""

        return False, f"Unknown action type: {action.action}"


class MockLLM:

    @staticmethod
    def generate_json_response(instruction: str, ui_elements: list[UIElement]) -> str:
        instruction_lower = instruction.lower()

        if any(word in instruction_lower for word in ["done", "finish", "complete", "stop", "exit"]):
            return json.dumps({"action": "DONE", "target_coordinates": None, "text_value": "", "confidence": 1.0, "reason": "Task marked as complete by user instruction", "done": True})

        if any(word in instruction_lower for word in ["type", "search", "input", "enter", "find"]):
            text_to_type = ""
            for prefix in ["search for ", "type ", "input ", "enter ", "find "]:
                if prefix in instruction_lower:
                    text_to_type = instruction_lower.split(prefix)[-1].strip().strip("'\"")
                    break
            if not text_to_type:
                text_to_type = instruction_lower.replace("type", "").replace("search", "").strip()
            return json.dumps({"action": "TYPE", "target_coordinates": [200, 125], "text_value": text_to_type, "confidence": 0.9, "reason": f"Type action for instruction: {instruction}", "done": False})

        if any(word in instruction_lower for word in ["click", "tap", "open", "press", "select", "go to"]):
            target_text = instruction_lower
            for prefix in ["click ", "tap ", "open ", "press ", "select ", "go to "]:
                if prefix in target_text:
                    target_text = target_text.split(prefix)[-1].strip()
                    break

            for elem in ui_elements:
                elem_text = (elem.text or "").lower()
                elem_desc = (elem.content_description or "").lower()
                if target_text in elem_text or target_text in elem_desc:
                    x = (elem.bounds[0] + elem.bounds[2]) // 2
                    y = (elem.bounds[1] + elem.bounds[3]) // 2
                    return json.dumps({"action": "CLICK", "target_coordinates": [x, y], "text_value": "", "confidence": 0.95, "reason": f"Found matching element: {elem.text or elem.content_description}", "done": False})

            for elem in ui_elements:
                if "button" in elem.class_name.lower() or "btn" in elem.id.lower():
                    x = (elem.bounds[0] + elem.bounds[2]) // 2
                    y = (elem.bounds[1] + elem.bounds[3]) // 2
                    return json.dumps({"action": "CLICK", "target_coordinates": [x, y], "text_value": "", "confidence": 0.7, "reason": f"No exact match, clicking first button: {elem.text or elem.id}", "done": False})

        if any(word in instruction_lower for word in ["swipe", "scroll", "slide"]):
            return json.dumps({"action": "SWIPE", "target_coordinates": [200, 500, 200, 300], "text_value": "", "confidence": 0.85, "reason": "Swipe up action for scrolling", "done": False})

        if any(word in instruction_lower for word in ["wait", "loading", "please wait"]):
            return json.dumps({"action": "WAIT", "target_coordinates": None, "text_value": "", "confidence": 0.8, "reason": "Waiting for UI to load or stabilize", "done": False})

        return json.dumps({"action": "WAIT", "target_coordinates": None, "text_value": "", "confidence": 0.3, "reason": f"Could not map instruction to action: '{instruction}'", "done": False})