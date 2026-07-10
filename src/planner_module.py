import json
import time
import logging
import shutil
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable
from src.prompt import SYSTEM_PROMPT, ACTION_SCHEMA
from ui_simulator.controller import capture_current_screen
import jsonschema
from PySide6.QtCore import QEventLoop, QMetaObject, Qt
from PySide6.QtWidgets import QApplication
from src.config import STEP_DELAY

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def run_in_background_with_event_loop(func, *args, **kwargs):
    """
    Runs a blocking function (like VLM generate network calls) in a background thread
    while spinning a local QEventLoop on the main GUI thread.
    This keeps the PySide6 HMI window responsive and avoids 'Not Responding' freezes.
    """
    loop = QEventLoop()
    result_box = []
    error_box = []
    
    def worker():
        try:
            res = func(*args, **kwargs)
            result_box.append(res)
        except Exception as e:
            error_box.append(e)
        finally:
            # Wake up the event loop in the main thread in a thread-safe way
            QMetaObject.invokeMethod(loop, "quit", Qt.QueuedConnection)
            
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    
    # Run the local event loop (keeps GUI responsive)
    loop.exec()
    
    if error_box:
        raise error_box[0]
    return result_box[0]

class Planner:
    """
    Formulates prompt configurations and resolves VLM action payloads.
    """
    def __init__(self, vlm):
        self.vlm = vlm
        self._max_retries = 3
    
    def predict(self, instruction: str, ui: dict, image_path: str = "screenshots/current.png", attempt: int = 0, feedback: Optional[str] = None, previous_response: Optional[str] = None) -> dict:
        """
        Builds the prompt and calls the VLM backend to predict the next HMI action.
        Implements feedback-driven retry logic with JSON schema validation.
        """
        prompt = f"Instruction\n{instruction}\nUI\n{json.dumps(ui, indent=2)}\n\nPredict next action.\n"
        if feedback and previous_response:
            prompt += (
                f"\n\n[FEEDBACK] Your previous response was: '{previous_response}'\n"
                f"However, it failed validation with the following error: {feedback}\n"
                f"Please correct this issue and output ONLY a valid JSON object matching the schema."
            )
        
        response = None
        try:
            try:
                # Run VLM generate call in background thread to prevent PySide6 GUI freezes
                response = run_in_background_with_event_loop(
                    self.vlm.generate, SYSTEM_PROMPT, prompt, image_path=image_path
                )
            except TypeError as te:
                if "image_path" in str(te) or "unexpected keyword argument" in str(te):
                    response = run_in_background_with_event_loop(
                        self.vlm.generate, SYSTEM_PROMPT, prompt
                    )
                else:
                    raise te
            return self._parse_and_validate(response)
        except (json.JSONDecodeError, jsonschema.ValidationError, ValueError) as e:
            logger.error(f"[PLANNER] Failed to parse/validate response (attempt {attempt + 1}): {e}")
            if attempt < self._max_retries:
                logger.info(f"[PLANNER] Retrying prediction with error feedback... ({attempt + 2}/{self._max_retries + 1})")
                return self.predict(
                    instruction=instruction,
                    ui=ui,
                    image_path=image_path,
                    attempt=attempt + 1,
                    feedback=str(e),
                    previous_response=response
                )
            logger.error(f"[PLANNER] Max retries exceeded. Returning safe fallback.")
            return {"action": "ERROR", "target_coordinates": [0, 0], "text_value": str(e)}
        except Exception as e:
            logger.error(f"[PLANNER] Unexpected VLM error: {e}")
            return {"action": "ERROR", "target_coordinates": [0, 0], "text_value": str(e)}
    
    def _parse_and_validate(self, response: str) -> dict:
        """Parse JSON response and validate against ACTION_SCHEMA."""
        cleaned = response.strip()
        
        # Clean potential markdown wrapping
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        if cleaned.upper() == "DONE":
            return {"action": "DONE", "target_coordinates": [0, 0], "text_value": ""}
        
        # Extract JSON substring if surrounded by conversational filler
        if not (cleaned.startswith("{") and cleaned.endswith("}")):
            start_idx = cleaned.find("{")
            end_idx = cleaned.rfind("}")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                cleaned = cleaned[start_idx:end_idx + 1]
        
        parsed = json.loads(cleaned)
        
        # Normalize DONE action pre-validation to satisfy tests/mock responses that omit fields
        if parsed.get("action", "").upper() == "DONE":
            parsed["target_coordinates"] = parsed.get("target_coordinates", [0, 0])
            parsed["text_value"] = parsed.get("text_value", "")
            
        # Handle case where VLM returns full bounds [x, y, width, height] instead of [x, y]
        coords = parsed.get("target_coordinates")
        if isinstance(coords, list) and len(coords) == 4:
            parsed["target_coordinates"] = [
                int(coords[0] + coords[2] / 2),
                int(coords[1] + coords[3] / 2)
            ]
            
        jsonschema.validate(instance=parsed, schema=ACTION_SCHEMA)
        
        action_upper = parsed.get("action", "").upper()
        parsed["action"] = action_upper
        
        if action_upper == "DONE":
            parsed["target_coordinates"] = [0, 0]
            parsed["text_value"] = ""
        elif action_upper == "TYPE":
            parsed["target_coordinates"] = [0, 0]
        elif action_upper == "SWIPE":
            direction = parsed.get("text_value", "UP")
            parsed["text_value"] = direction.upper()
            if parsed["text_value"] not in ("UP", "DOWN"):
                parsed["text_value"] = "UP"
        
        return parsed


class PlannerLoop:
    """
    Loop runner coordinating screen capture, UI state collection, action execution, and logging.
    Designed for high availability and continuous operation.
    """
    def __init__(self, planner: Planner, executor: Callable[[dict], bool], controller, max_steps: int = 20):
        self.planner = planner
        self.executor = executor
        self.controller = controller
        self.max_steps = max_steps
        self._step_history: list[dict] = []
        self._running = False
        self._error_count = 0
        self._max_consecutive_errors = 5
    
    def run(self, instruction: str) -> bool:
        """Runs the step loop up to max_steps or until 'DONE' is emitted.
        
        Returns:
            True if completed successfully, False if errored or exceeded max steps
        """
        self._running = True
        self._step_history = []
        self._error_count = 0
        
        Path("screenshots").mkdir(exist_ok=True)
        Path("outputs").mkdir(exist_ok=True)
        
        logger.info(f"\n[LOOP] Starting autonomous agent execution loop.")
        
        final_outcome = "Failed"
        failure_reason = "Max steps exceeded without completing task"
        start_time_overall = time.time()
        
        try:
            for step in range(self.max_steps):
                if not self._running:
                    logger.info("[LOOP] Execution halted by external signal.")
                    failure_reason = "Execution halted by external signal"
                    break
                
                step_num = step + 1
                start_time = time.time()
                logger.info("\n" + "=" * 60)
                logger.info(f"STEP {step_num}/{self.max_steps}")
                
                # --- Pipeline Stage 1: Receive Instruction ---
                logger.info(f"[STAGE 1/5: Receive Instruction] Target: '{instruction}'")
                
                try:
                    # --- Pipeline Stage 2: Vision UI Scan ---
                    logger.info("[STAGE 2/5: Vision UI Scan] Scanning current view...")
                    ui = self._safe_capture_screen(step_num)
                    if ui is None:
                        logger.error("[STAGE 2/5] Vision UI Scan returned empty state. Skipping step.")
                        self._error_count += 1
                        self._log_step(
                            step=step_num,
                            instruction=instruction,
                            ui={},
                            action={"action": "SCAN_ERROR", "target_coordinates": [0, 0], "text_value": ""},
                            exec_result="failed",
                            elapsed=time.time() - start_time,
                            error_message="Vision UI scan returned empty state"
                        )
                        if self._error_count >= self._max_consecutive_errors:
                            logger.critical(f"[LOOP] Max consecutive errors ({self._max_consecutive_errors}) reached. Exiting.")
                            failure_reason = f"Max consecutive errors ({self._max_consecutive_errors}) reached during screen capture"
                            break
                        continue
                    logger.info(f"[STAGE 2/5] Current Screen: {ui.get('screen', 'unknown')}")
                    
                    # Copy current screenshot to step screenshot
                    current_screenshot = Path("screenshots/current.png")
                    step_screenshot_path = f"screenshots/step_{step_num}.png"
                    if current_screenshot.exists():
                        shutil.copy(str(current_screenshot), step_screenshot_path)
                    else:
                        step_screenshot_path = ""
                    
                    # --- Pipeline Stage 3: Planner Action Translation ---
                    logger.info("[STAGE 3/5: Planner Action Translation] Querying VLM for next action...")
                    action = self.planner.predict(instruction, ui, image_path="screenshots/current.png")
                    logger.info(f"[STAGE 3/5] Translated Action: {json.dumps(action)}")
                    
                    if action.get("action") == "ERROR":
                        err_msg = action.get("text_value", "Unknown error")
                        logger.error(f"[STAGE 3/5] Planner returned error: {err_msg}")
                        self._error_count += 1
                        self._log_step(
                            step=step_num,
                            instruction=instruction,
                            ui=ui,
                            action=action,
                            exec_result="failed",
                            elapsed=time.time() - start_time,
                            error_message=f"Planner error: {err_msg}",
                            screenshot_path=step_screenshot_path
                        )
                        if self._error_count >= self._max_consecutive_errors:
                            logger.critical("[LOOP] Max consecutive errors reached. Exiting.")
                            failure_reason = f"Max consecutive errors reached during action translation: {err_msg}"
                            break
                        continue
                    
                    # Reset error count on successful action generation
                    self._error_count = 0
                    
                    # Check if action is DONE to terminate
                    if action.get("action") == "DONE":
                        logger.info("[LOOP] Mission completed successfully! Exiting loop.")
                        self._log_step(
                            step=step_num,
                            instruction=instruction,
                            ui=ui,
                            action=action,
                            exec_result="success_done",
                            elapsed=time.time() - start_time,
                            screenshot_path=step_screenshot_path
                        )
                        final_outcome = "Success"
                        failure_reason = ""
                        break
                    
                    # --- Pipeline Stage 4: Execution & Screenshot Capture ---
                    logger.info(f"[STAGE 4/5: Execution & Screenshot Capture] Executing action {action.get('action')}...")
                    exec_result = self._safe_execute(action)
                    
                    # Let PySide6 process GUI update events and capture resulting screenshot
                    app = QApplication.instance()
                    if app:
                        app.processEvents()
                    
                    capture_success = capture_current_screen()
                    logger.info(f"[STAGE 4/5] Execution result: {exec_result}. Screenshot capture success: {capture_success}")
                    
                    # --- Pipeline Stage 5: Logging ---
                    logger.info("[STAGE 5/5: Logging] Recording step details...")
                    self._log_step(
                        step=step_num,
                        instruction=instruction,
                        ui=ui,
                        action=action,
                        exec_result=exec_result,
                        elapsed=time.time() - start_time,
                        screenshot_path=step_screenshot_path
                    )
                    logger.info(f"[STAGE 5/5] Elapsed step time: {time.time() - start_time:.2f}s")
                    
                    # Delay between steps for visual smoothness and to prevent rate limits
                    time.sleep(STEP_DELAY)
                    
                    if exec_result != "success":
                        self._error_count += 1
                        if self._error_count >= self._max_consecutive_errors:
                            logger.critical("[LOOP] Max consecutive errors reached. Exiting.")
                            failure_reason = f"Max consecutive execution failures reached: {exec_result}"
                            break
                    
                except Exception as e:
                    logger.error(f"[LOOP] Exception occurred in step {step_num}: {e}")
                    self._error_count += 1
                    self._log_step(
                        step=step_num,
                        instruction=instruction,
                        ui={},
                        action={"action": "EXCEPTION", "target_coordinates": [0, 0], "text_value": ""},
                        exec_result="failed",
                        elapsed=time.time() - start_time,
                        error_message=f"Exception: {e}"
                    )
                    if self._error_count >= self._max_consecutive_errors:
                        logger.critical("[LOOP] Max consecutive errors reached. Exiting.")
                        failure_reason = f"Max consecutive exceptions reached: {e}"
                        break
                
                logger.info("=" * 60)
            else:
                failure_reason = f"Exceeded maximum steps limit ({self.max_steps})"
            
            logger.info("[LOOP] Autonomous execution loop finished.")
            
        except Exception as e:
            logger.critical(f"[LOOP] Critical loop failure: {e}")
            failure_reason = f"Critical loop crash: {e}"
            
        finally:
            self._running = False
            total_elapsed = time.time() - start_time_overall
            self._generate_reports(instruction, final_outcome, failure_reason, total_elapsed)
            
        return final_outcome == "Success"
    
    def _safe_capture_screen(self, step: int) -> Optional[dict]:
        """Safely capture screen and collect UI state with error handling."""
        try:
            capture_current_screen()
            ui = self.controller.collect_ui_state()
            return ui
        except Exception as e:
            logger.error(f"[LOOP] Screen capture failed at step {step}: {e}")
            return None
    
    def _safe_execute(self, action: dict) -> Optional[str]:
        """Safely execute action with error handling."""
        try:
            exec_result = self.executor(action)
            return "success" if exec_result else "failed"
        except Exception as e:
            logger.error(f"[LOOP] Execution failed: {e}")
            return f"error: {e}"
    
    def _log_step(self, step: int, instruction: str, ui: dict, action: dict, exec_result: Optional[str], elapsed: float, error_message: str = "", screenshot_path: str = ""):
        """Log step data to history."""
        self._step_history.append({
            "step": step,
            "timestamp": datetime.now().isoformat(),
            "instruction": instruction,
            "screen": ui.get("screen", "unknown") if ui else "unknown",
            "action": action,
            "execution_result": exec_result,
            "elapsed_time": elapsed,
            "error_message": error_message,
            "screenshot": screenshot_path
        })
    
    def _generate_reports(self, instruction: str, outcome: str, failure_reason: str, total_elapsed: float):
        """Generates execution_log.json and summary_report.md under outputs/ directory."""
        log_file = Path("outputs/execution_log.json")
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(self._step_history, f, indent=2, ensure_ascii=False)
            logger.info(f"[REPORT] Saved execution log to {log_file}")
        except Exception as e:
            logger.error(f"[REPORT] Failed to save execution log: {e}")

        total_steps = len(self._step_history)
        successful_steps_count = sum(1 for step in self._step_history if step["execution_result"] in ("success", "success_done"))
        failed_steps_count = total_steps - successful_steps_count
        
        if outcome == "Success":
            completion_rate = 100.0
        else:
            if total_steps > 0:
                completion_rate = (successful_steps_count / total_steps) * 100.0
            else:
                completion_rate = 0.0

        report_file = Path("outputs/summary_report.md")
        
        report_md = f"""# Vision-Based UI Navigation Agent - Summary Report

## Task Overview
- **User Instruction**: {instruction}
- **Execution Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Total Steps Run**: {total_steps}
- **Total Elapsed Time**: {total_elapsed:.2f} seconds

## Final Task Outcome
- **Status**: **{outcome}**
"""
        if outcome == "Failed":
            report_md += f"- **Root Cause of Failure**: {failure_reason}\n"
            
        report_md += f"""- **Quantitative Task Completion Rate**: {completion_rate:.1f}%

## Quantitative Performance
- **Successful Steps**: {successful_steps_count}
- **Failed Steps**: {failed_steps_count}

## Step-by-Step Execution Summary
| Step | Screen | Action Type | Coordinates | Value/Text | Execution Result | Elapsed (s) | Error Message |
|------|--------|-------------|-------------|------------|------------------|-------------|---------------|
"""
        for step in self._step_history:
            act = step["action"]
            coords = str(act.get("target_coordinates", [0, 0]))
            val = act.get("text_value", "")
            if not val:
                val = "-"
            
            report_md += f"| {step['step']} | {step['screen']} | {act.get('action')} | {coords} | {val} | {step['execution_result']} | {step['elapsed_time']:.2f} | {step['error_message'] or '-'} |\n"

        report_md += "\n## Detailed Step Breakdown\n"
        for step in self._step_history:
            act = step["action"]
            status_symbol = "✅" if step["execution_result"] in ("success", "success_done") else "❌"
            report_md += f"### Step {step['step']}: {act.get('action')} {status_symbol}\n"
            report_md += f"- **Screen**: `{step['screen']}`\n"
            report_md += f"- **Action Details**: `Coordinates: {act.get('target_coordinates')}`, `Value: {act.get('text_value')}`\n"
            report_md += f"- **Execution Result**: `{step['execution_result']}`\n"
            if step['error_message']:
                report_md += f"- **Error Detail**: {step['error_message']}\n"
            if step['screenshot']:
                report_md += f"- **Visual Capture**: ![Step {step['step']} screenshot](../{step['screenshot']})\n"
            report_md += "\n"

        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_md)
            logger.info(f"[REPORT] Saved summary report to {report_file}")
            
            print("\n" + "="*80)
            print("AGENT EXECUTION SUMMARY REPORT")
            print("="*80)
            print(f"Goal: {instruction}")
            print(f"Outcome: {outcome}")
            print(f"Completion Rate: {completion_rate:.1f}%")
            print(f"Steps: {successful_steps_count} succeeded, {failed_steps_count} failed.")
            if outcome == "Failed":
                print(f"Failure Reason: {failure_reason}")
            print("="*80 + "\n")
        except Exception as e:
            logger.error(f"[REPORT] Failed to save summary report: {e}")
    
    def get_history(self) -> list[dict]:
        """Return recorded step history."""
        return self._step_history.copy()
    
    def stop(self):
        """Signal the loop to stop execution."""
        self._running = False
