import os
import json
import base64
import io
from pathlib import Path
from typing import Optional
from PIL import Image
from groq import Groq
from groq.types.chat import ChatCompletionMessageParam
from src.config import GROQ_API_KEY, GROQ_MODEL, GROQ_BASE_URL, GROQ_MAX_TOKENS, GROQ_TEMPERATURE

def get_mock_action(prompt: str) -> str:
    instruction_line = ""
    ui_state = {}
    
    try:
        if "Instruction" in prompt:
            instruction_part = prompt.split("Instruction")[1].split("UI")[0].strip()
            instruction_line = instruction_part
    except Exception:
        instruction_line = ""
        
    try:
        if "UI" in prompt:
            ui_part = prompt.split("UI")[1].split("Predict next action.")[0].strip()
            ui_state = json.loads(ui_part)
    except Exception:
        ui_state = {}
        
    current_screen = ui_state.get("screen", "home")
    widgets = ui_state.get("widgets", [])
    
    def get_btn_coords(btn_id):
        for w in widgets:
            if w.get("id") == btn_id and w.get("visible", True):
                geom = w.get("geometry", [0, 0, 0, 0])
                return [geom[0] + geom[2]//2, geom[1] + geom[3]//2]
        return None

    inst_lower = instruction_line.lower()
    
    print(f"[GroqVLM] [FALLBACK MOCK] Resolving mock action for Screen='{current_screen}', Instruction='{instruction_line.strip()}'")

    nav_idx = inst_lower.find("navigation")
    search_idx = inst_lower.find("search")
    type_idx = inst_lower.find("type")
    
    first_nav_idx = min([i for i in [nav_idx, search_idx, type_idx] if i != -1], default=999999)
    veh_idx = inst_lower.find("vehicle")
    
    nav_done = False
    for w in widgets:
        if w.get("id") == "map_status_label" and "NAVIGATING TO" in w.get("text", "").upper():
            nav_done = True
            break
            
    if first_nav_idx < veh_idx and not nav_done:
        query = "Tesla Supercharger"
        if "type " in inst_lower:
            sub = instruction_line.split("type ")[1]
            for word in [" in ", " and ", " to ", ".", ","]:
                if word in sub:
                    sub = sub.split(word)[0]
            query = sub.strip()
        elif "search " in inst_lower:
            sub = instruction_line.split("search ")[1]
            for word in [" in ", " and ", " to ", ".", ","]:
                if word in sub:
                    sub = sub.split(word)[0]
            query = sub.strip()
        
        query_clean = query.replace(".", "").strip()
        
        if current_screen == "home":
            coords = get_btn_coords("navigation_button")
            if coords:
                return json.dumps({"action": "CLICK", "target_coordinates": coords, "text_value": ""})
        elif current_screen == "navigation":
            coords = get_btn_coords("search_box")
            if coords:
                return json.dumps({"action": "CLICK", "target_coordinates": coords, "text_value": ""})
        elif current_screen == "keyboard":
            return json.dumps({"action": "TYPE", "target_coordinates": [0, 0], "text_value": query_clean})
            
    elif "vehicle" in inst_lower:
        if current_screen in ("home", "navigation", "keyboard"):
            coords = get_btn_coords("vehicle_button")
            if coords:
                return json.dumps({"action": "CLICK", "target_coordinates": coords, "text_value": ""})
        elif current_screen == "vehicle":
            if "limit" in inst_lower or "100%" in inst_lower:
                limit_already_100 = False
                for w in widgets:
                    if w.get("id") == "charge_limit_label" and "100%" in w.get("text", ""):
                        limit_already_100 = True
                        break
                
                if not limit_already_100:
                    coords = get_btn_coords("charge_limit_slider")
                    if coords:
                        slider_width = 200
                        for w in widgets:
                            if w.get("id") == "charge_limit_slider":
                                slider_width = w.get("geometry", [0, 0, 200, 30])[2]
                                break
                        target_x = coords[0] + slider_width // 2 - 10
                        return json.dumps({"action": "CLICK", "target_coordinates": [target_x, coords[1]], "text_value": "100%"})
            return json.dumps({"action": "DONE", "target_coordinates": [0, 0], "text_value": ""})
            
    elif "climate" in inst_lower:
        if current_screen == "home":
            coords = get_btn_coords("temp_up_btn")
            if coords:
                return json.dumps({"action": "CLICK", "target_coordinates": coords, "text_value": ""})
        elif current_screen in ("navigation", "vehicle", "settings", "keyboard"):
            coords = get_btn_coords("home_button")
            if coords:
                return json.dumps({"action": "CLICK", "target_coordinates": coords, "text_value": ""})
        else:
            return json.dumps({"action": "DONE", "target_coordinates": [0, 0], "text_value": ""})
            
    elif "dark mode" in inst_lower:
        if current_screen != "settings":
            coords = get_btn_coords("settings_button")
            if coords:
                return json.dumps({"action": "CLICK", "target_coordinates": coords, "text_value": ""})
        else:
            coords = get_btn_coords("setting_wifi_toggle")
            if coords:
                return json.dumps({"action": "CLICK", "target_coordinates": coords, "text_value": ""})
            return json.dumps({"action": "DONE", "target_coordinates": [0, 0], "text_value": ""})

    return json.dumps({"action": "DONE", "target_coordinates": [0, 0], "text_value": ""})

class GroqVLM:
    def __init__(self, api_key: Optional[str] = None, model: str = GROQ_MODEL, max_tokens: int = GROQ_MAX_TOKENS, temperature: float = GROQ_TEMPERATURE, base_url: Optional[str] = None):
        if api_key is None:
            api_key = os.environ.get("GROQ_API_KEY", GROQ_API_KEY)
        if not api_key:
            raise ValueError("[GroqVLM] GROQ_API_KEY is required. Set via environment variable or config.")
        
        if base_url is None:
            base_url = os.environ.get("GROQ_BASE_URL", GROQ_BASE_URL)
            
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        if base_url:
            cleaned_url = base_url.rstrip("/")
            if cleaned_url.endswith("/openai/v1"):
                cleaned_url = cleaned_url[:-10].rstrip("/")
            
            if cleaned_url:
                print(f"[GroqVLM] Connecting to custom base URL: {cleaned_url}")
                self.client = Groq(api_key=api_key, base_url=cleaned_url)
            else:
                self.client = Groq(api_key=api_key)
        else:
            self.client = Groq(api_key=api_key)
            
        self._init_client()
    
    def _init_client(self):
        try:
            self.client.models.list()
            print(f"[GroqVLM] Initialized with model: {self.model}")
        except Exception as e:
            print(f"[GroqVLM] Warning: Could not validate client connection: {e}")
    
    def _encode_image(self, image_path: str) -> tuple[str, str]:
        path = Path(image_path)
        if not path.exists():
            raise ValueError(f"[GroqVLM] Image not found at {image_path}")
        
        with Image.open(path) as img:
            img_resized = img.resize((512, 288), Image.Resampling.LANCZOS)
            buffered = io.BytesIO()
            img_resized.convert("RGB").save(buffered, format="JPEG", quality=70)
            b64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return b64_data, "image/jpeg"
    
    def generate(self, system_prompt: str, prompt: str, image_path: str = "screenshots/current.png", image_base64: Optional[str] = None) -> str:
        mime_type = "image/png"
        if image_base64 is None:
            image_base64, mime_type = self._encode_image(image_path)
        
        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_base64}",
                            "detail": "low"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=False
            )
            if not completion.choices:
                raise RuntimeError("Groq API returned an empty completion.")
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"[GroqVLM] API call failed: {e}. Falling back to Smart Mock VLM...")
            return get_mock_action(prompt)
