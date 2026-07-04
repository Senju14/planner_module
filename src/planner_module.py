import json
import time
from src.prompt import SYSTEM_PROMPT
from ui_simulator.controller import capture_current_screen

class Planner:
    """
    Formulates prompt configurations and resolves VLM action payloads.
    """
    def __init__(self, vlm):
        self.vlm = vlm

    def predict(self, instruction: str, ui: dict) -> dict:
        """
        Builds the prompt and calls the VLM backend to predict the next HMI action.
        """
        prompt = f"Instruction\n{instruction}\nUI\n{json.dumps(ui, indent=2)}\n\nPredict next action.\n"

        response = self.vlm.generate(SYSTEM_PROMPT, prompt)

        # Strip markdown wrappers
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        if cleaned.upper() == "DONE":
            return {"action": "DONE", "target_coordinates": [0, 0], "text_value": ""}

        return json.loads(cleaned)


class PlannerLoop:
    """
    Loop runner coordinating screen capture, UI state collection, action execution, and logging.
    """
    def __init__(self, planner: Planner, executor, controller, max_steps: int):
        self.planner = planner
        self.executor = executor
        self.controller = controller
        self.max_steps = max_steps

    def run(self, instruction: str):
        """Runs the step loop up to max_steps or until 'DONE' is emitted."""
        print(f"\n[LOOP] Starting autonomous agent for instruction: '{instruction}'")

        for step in range(self.max_steps):
            start_time = time.time()
            print("\n" + "=" * 50)
            print(f"STEP {step + 1}")
            print(f"Instruction: {instruction}")
            print("=" * 50)

            # 1. Capture HMI screen
            capture_current_screen()

            # 2. Collect dynamic UI state directly from controller memory
            ui = self.controller.collect_ui_state()
            current_screen = ui.get("screen", "unknown")
            print(f"Current Screen: {current_screen}")

            # 3. Request next action from VLM planner
            action = self.planner.predict(instruction, ui)
            print(f"Action: {json.dumps(action)}")

            # 4. Check if mission is complete
            action_name = action.get("action", "").upper()
            if action_name == "DONE":
                print("[LOOP] Planner reported mission completion. Exiting loop.")
                break

            # 5. Execute predicted action on widgets
            exec_result = self.executor(action)
            print(f"Execution Result: {exec_result}")

            # 6. Capture screen again to verify visual transition
            capture_current_screen()

            elapsed_time = time.time() - start_time
            print(f"Elapsed Time: {elapsed_time:.2f}s")
            print("=" * 50)

        print("[LOOP] Autonomous execution loop finished.")
