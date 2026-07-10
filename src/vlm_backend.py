import os
import base64
import io
import json
import time
import urllib.request
from pathlib import Path
from typing import Optional
from PIL import Image
from src.config import OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_BASE_URL, OPENROUTER_MAX_TOKENS, OPENROUTER_TEMPERATURE

class OpenRouterVLM:
    def __init__(self, api_key: Optional[str] = None, model: str = OPENROUTER_MODEL, max_tokens: int = OPENROUTER_MAX_TOKENS, temperature: float = OPENROUTER_TEMPERATURE, base_url: Optional[str] = None):
        if api_key is None:
            api_key = os.environ.get("OPENROUTER_API_KEY", OPENROUTER_API_KEY)
        if not api_key:
            raise ValueError("[OpenRouterVLM] OPENROUTER_API_KEY is required. Set via environment variable or config.")
        
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        raw_url = (base_url or os.environ.get("OPENROUTER_BASE_URL", OPENROUTER_BASE_URL)).strip().rstrip("/")
        if raw_url and not raw_url.endswith("/api/v1"):
            raw_url = f"{raw_url}/api/v1"
        self.base_url = raw_url

        # Check if the model supports vision based on standard name patterns
        model_lower = self.model.lower()
        self.is_vision = ("vision" in model_lower) or ("-vl" in model_lower) or ("gemini" in model_lower) or ("gpt-" in model_lower) or ("claude" in model_lower)
        print(f"[OpenRouterVLM] Initialized with model: {self.model} (Vision Support: {self.is_vision})")

    def _encode_image(self, image_path: str) -> tuple[str, str]:
        path = Path(image_path)
        if not path.exists():
            raise ValueError(f"[OpenRouterVLM] Image not found at {image_path}")
        
        with Image.open(path) as img:
            img_resized = img.resize((256, 144), Image.Resampling.LANCZOS)
            buffered = io.BytesIO()
            img_resized.convert("RGB").save(buffered, format="JPEG", quality=70)
            b64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return b64_data, "image/jpeg"
    
    def generate(self, system_prompt: str, prompt: str, image_path: str = "screenshots/current.png", image_base64: Optional[str] = None) -> str:
        # Build user message content based on vision capabilities
        if self.is_vision:
            mime_type = "image/png"
            if image_base64 is None:
                image_base64, mime_type = self._encode_image(image_path)
            user_content = [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{image_base64}"
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        else:
            user_content = prompt

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/planner_module",
            "X-Title": "Automotive HMI Agent"
        }
        
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    if "choices" not in res_data or not res_data["choices"]:
                        raise RuntimeError(f"OpenRouter API returned an empty completion: {res_data}")
                    return res_data["choices"][0]["message"]["content"].strip()
            except urllib.error.HTTPError as e:
                # Handle rate limits gracefully using retry backoff
                if e.code == 429 and attempt < max_retries - 1:
                    print(f"[OpenRouterVLM] Rate limited (429). Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                raise RuntimeError(f"[OpenRouterVLM] API call failed with status {e.code}: {e.read().decode('utf-8', errors='ignore')}")
            except Exception as e:
                raise RuntimeError(f"[OpenRouterVLM] API call failed: {e}")

    def estimate_max_steps(self, instruction: str) -> int:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a task estimator. Estimate the maximum number of GUI action steps (clicks, typing, swipes) required to complete the user instruction. Return ONLY a single integer (e.g. 8)."
                },
                {
                    "role": "user",
                    "content": f"Instruction: {instruction}"
                }
            ],
            "max_tokens": 10,
            "temperature": 0.0
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/planner_module",
            "X-Title": "Automotive HMI Agent"
        }
        
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    val = res_data["choices"][0]["message"]["content"].strip()
                    import re
                    nums = re.findall(r'\d+', val)
                    if nums:
                        return max(10, int(nums[0]) * 2)
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < max_retries - 1:
                    print(f"[OpenRouterVLM] Step estimation rate limited (429). Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                break
            except Exception as e:
                print(f"[OpenRouterVLM] Warning during step estimation: {e}")
                break
            
        import re
        sub_actions = len(re.split(r'\.|\band\b|\bthen\b', instruction.lower()))
        return max(5, sub_actions * 3)
