import json
import re
from pydantic import ValidationError
from src.models import PlannerRequest, PlannerResponse, ActionType
from src.mocks import MockLLM


class Planner:

    VALID_ACTIONS = {"CLICK", "TYPE", "SWIPE", "WAIT", "DONE"}

    def __init__(self):
        self.llm = MockLLM()

    def generate_action(self, request: PlannerRequest) -> PlannerResponse:
        llm_output = self.llm.generate_json_response(
            instruction=request.instruction,
            ui_elements=request.ui_elements
        )
        return self._parse_llm_output(llm_output)

    def _parse_llm_output(self, llm_output: str) -> PlannerResponse:
        try:
            parsed = json.loads(llm_output)
            return self._validate_and_build(parsed)
        except (json.JSONDecodeError, ValidationError):
            pass

        try:
            json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', llm_output, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(1).strip())
                return self._validate_and_build(parsed)
        except (json.JSONDecodeError, ValidationError, AttributeError):
            pass

        try:
            json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                return self._validate_and_build(parsed)
        except (json.JSONDecodeError, ValidationError, AttributeError):
            pass

        try:
            action = self._fuzzy_find_action(llm_output)
            if action:
                return PlannerResponse(
                    action=action,
                    target_coordinates=None,
                    text_value="",
                    confidence=0.5,
                    reason=f"Fuzzy matched action: {action}",
                    done=(action == "DONE")
                )
        except (ValidationError, ValueError):
            pass

        return PlannerResponse(
            action=ActionType.WAIT,
            target_coordinates=None,
            text_value="",
            confidence=0.1,
            reason="Failed to parse LLM output, defaulting to WAIT",
            done=False
        )

    def _validate_and_build(self, data: dict) -> PlannerResponse:
        action = data.get("action", "WAIT").upper()
        if action not in self.VALID_ACTIONS:
            action = "WAIT"

        target_coords = data.get("target_coordinates")
        if target_coords is not None:
            if not isinstance(target_coords, list):
                target_coords = None
            elif len(target_coords) not in (2, 4):
                target_coords = None
            else:
                target_coords = [int(c) for c in target_coords]

        done = data.get("done", False)
        if action == "DONE":
            done = True

        return PlannerResponse(
            action=action,
            target_coordinates=target_coords,
            text_value=str(data.get("text_value", "")),
            confidence=float(data.get("confidence", 1.0)),
            reason=str(data.get("reason", "")),
            done=done
        )

    def _fuzzy_find_action(self, text: str) -> str | None:
        text_upper = text.upper()
        for action in ["DONE", "CLICK", "TYPE", "SWIPE", "WAIT"]:
            if action in text_upper:
                return action
        return None