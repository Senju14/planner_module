import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration for the Automotive HMI GUI Agent

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL")
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "1024"))
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.0"))

# Legacy local model settings (kept for optional use)
MODEL_PATH = os.getenv("MODEL_PATH", "./models/SmolVLM-256M-Instruct")

DEVICE = os.getenv("DEVICE", "auto")      # cpu | cuda | auto

MAX_STEPS = int(os.getenv("MAX_STEPS", "20"))
STEP_DELAY = float(os.getenv("STEP_DELAY", "1.5"))

MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "64"))

TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))

LOAD_IN_8BIT = os.getenv("LOAD_IN_8BIT", "False").lower() in ("true", "1", "yes")

# Modal remote execution settings
MODAL_ENABLED = os.getenv("MODAL_ENABLED", "False").lower() in ("true", "1", "yes")
MODAL_APP_NAME = os.getenv("MODAL_APP_NAME", "hmi-agent")
MODAL_GPU = os.getenv("MODAL_GPU", "A100")
MODAL_TIMEOUT = int(os.getenv("MODAL_TIMEOUT", "600"))
