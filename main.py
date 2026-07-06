import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import argparse

project_root = Path(__file__).resolve().parent
ui_sim_dir = project_root / "ui_simulator"

for directory in (project_root, ui_sim_dir):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from main_window import MainWindow
from src.config import MAX_STEPS, GROQ_API_KEY
from src.planner_module import Planner, PlannerLoop
from src.executor import execute
from src.vlm_backend import GroqVLM

def create_vlm_backend():
    api_key = os.environ.get("GROQ_API_KEY", GROQ_API_KEY)
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Please set it in your environment or .env file.")
    print("[AGENT] Using Groq API backend with qwen/qwen3.6-27b")
    return GroqVLM(api_key=api_key)

def main():
    parser = argparse.ArgumentParser(description="Automotive HMI GUI Agent")
    parser.add_argument("--instruction", "-i", type=str, help="Instruction to execute")
    args = parser.parse_args()
    
    instruction_file = project_root / "instruction.txt"
    if not instruction_file.exists():
        with open(instruction_file, "w", encoding="utf-8") as f:
            f.write("Open Vehicle Settings")
        print(f"[AGENT] Created default instruction configuration at '{instruction_file}'")
    
    with open(instruction_file, "r", encoding="utf-8") as f:
        instruction = f.read().strip()
    
    if args.instruction:
        instruction = args.instruction
    
    print(f"[AGENT] Launching Automotive HMI GUI Agent...")
    print(f"[AGENT] Target Goal: '{instruction}'")
    print(f"[AGENT] Max Loop Steps: {MAX_STEPS}")
    
    app = QApplication(sys.argv)
    
    style_file = ui_sim_dir / "style.qss"
    if style_file.exists():
        with open(style_file, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    
    window = MainWindow()
    window.show()
    app.processEvents()
    
    vlm_backend = create_vlm_backend()
    planner = Planner(vlm_backend)
    loop = PlannerLoop(
        planner,
        execute,
        window.controller,
        MAX_STEPS
    )
    
    QTimer.singleShot(1000, lambda: [loop.run(instruction), app.quit()])
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()