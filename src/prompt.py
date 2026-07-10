ACTION_SCHEMA = {
    "type": "object",
    "required": ["action", "target_coordinates", "text_value"],
    "properties": {
        "action": {
            "type": "string",
            "enum": ["CLICK", "TYPE", "SWIPE", "DONE"],
            "description": "The action to execute"
        },
        "target_coordinates": {
            "type": "array",
            "items": {"type": "integer"},
            "minItems": 2,
            "maxItems": 2,
            "description": "[x, y] coordinate pair on the screen; use [0, 0] for TYPE and DONE actions"
        },
        "text_value": {
            "type": "string",
            "description": "The text to type for TYPE actions, or the direction ('UP' or 'DOWN') for SWIPE actions; empty string otherwise"
        }
    },
    "additionalProperties": False
}

SYSTEM_PROMPT = """You are an Automotive HMI UI Planning Agent. Decide the next action based on the screenshot and UI JSON state to achieve the goal.

Respond ONLY with a raw JSON object matching the schema:
{"action": "CLICK"|"TYPE"|"SWIPE"|"DONE", "target_coordinates": [x, y], "text_value": "string"}

Action Specifications:
1. CLICK: [x, y] targets the center of target widget. Set text_value to "".
2. TYPE: [0, 0]. Set text_value to the string to type.
3. SWIPE: [0, 0]. Set text_value to "UP" (scroll down) or "DOWN" (scroll up).
4. DONE: [0, 0]. Set text_value to "". Use ONLY when the instruction is fully achieved.

Rules:
- Output ONLY the raw JSON object. No explanations. No markdown formatting.
- Verify coordinates against the widget geometry in the JSON.
- CRITICAL: You must CLICK on a textbox to focus it BEFORE using the TYPE action. However, if the current screen is already 'keyboard', the textbox is ALREADY focused and you MUST use the TYPE action immediately. DO NOT CLICK it again.
"""
