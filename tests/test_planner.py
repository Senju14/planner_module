import sys
import json
from pathlib import Path

# Append project root to PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.planner_module import Planner

class MockVLMBackend:
    """Mock VLM generator mimicking different return patterns from LLMs."""
    def __init__(self, response_value: str):
        self.response_value = response_value

    def generate(self, system_prompt: str, prompt: str) -> str:
        return self.response_value

def test_planner_robustness():
    """
    Tests that the Planner predicts actions cleanly, stripping markdown wrappers,
    and falls back to DONE actions correctly.
    """
    print("\n=== Planner Prompt and JSON Parser Test ===")

    # Case 1: Standard clean JSON action
    vlm_clean = MockVLMBackend('{"action": "CLICK", "target_coordinates": [100, 200], "text_value": ""}')
    planner_clean = Planner(vlm_clean)
    res = planner_clean.predict("Click Sidebar", {"screen": "home"})
    assert res["action"] == "CLICK", "Failed to extract clean action."
    assert res["target_coordinates"] == [100, 200]
    print("1. Standard JSON format parse. Passed.")

    # Case 2: Markdown block wrapped JSON (Common in LLM outputs)
    vlm_md = MockVLMBackend('```json\n{"action": "TYPE", "target_coordinates": [50, 50], "text_value": "search"}\n```')
    planner_md = Planner(vlm_md)
    res = planner_md.predict("Type text", {"screen": "home"})
    assert res["action"] == "TYPE", "Failed to extract markdown wrapped action."
    assert res["text_value"] == "search"
    print("2. Markdown-wrapped JSON block parse. Passed.")

    # Case 3: Raw DONE string fallback
    vlm_done_raw = MockVLMBackend('DONE')
    planner_done_raw = Planner(vlm_done_raw)
    res = planner_done_raw.predict("Finish", {"screen": "home"})
    assert res["action"] == "DONE", "Failed to resolve raw DONE string."
    print("3. Raw DONE string parser fallback. Passed.")

    # Case 4: JSON DONE object
    vlm_done_json = MockVLMBackend('{"action": "DONE"}')
    planner_done_json = Planner(vlm_done_json)
    res = planner_done_json.predict("Finish", {"screen": "home"})
    assert res["action"] == "DONE", "Failed to resolve JSON DONE object."
    print("4. JSON DONE object parser fallback. Passed.")

    print("Success: All Planner JSON and Prompt tests passed.")
    print("==========================================\n")

if __name__ == "__main__":
    test_planner_robustness()
