import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Inject project_root and ui_simulator directories into PYTHONPATH
project_root = Path(__file__).resolve().parent
ui_sim_dir = project_root / "ui_simulator"

for directory in (project_root, ui_sim_dir):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from main_window import MainWindow
from src.config import MAX_STEPS
from src.planner_module import Planner, PlannerLoop
from src.executor import execute
from src.vlm_backend import FakeVLM

def main():
    # Load or generate the instruction.txt config file
    instruction_file = project_root / "instruction.txt"
    if not instruction_file.exists():
        with open(instruction_file, "w", encoding="utf-8") as f:
            f.write("Open Vehicle Settings")
        print(f"[AGENT] Created default instruction configuration at '{instruction_file}'")

    with open(instruction_file, "r", encoding="utf-8") as f:
        instruction = f.read().strip()

    # Allow CLI argument override
    if len(sys.argv) > 1:
        instruction = " ".join(sys.argv[1:])

    print(f"[AGENT] Launching Automotive HMI Local GUI Agent...")
    print(f"[AGENT] Target Goal: '{instruction}'")
    print(f"[AGENT] Max Loop Steps: {MAX_STEPS}")

    # Initialize PySide6 application
    app = QApplication(sys.argv)

    # Load HMI stylesheet
    style_file = ui_sim_dir / "style.qss"
    if style_file.exists():
        with open(style_file, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    # Build HMI Window
    window = MainWindow()
    window.show()

    # Process events to render window
    app.processEvents()

    # Instantiate Planner and Loop
    planner = Planner(FakeVLM())
    loop = PlannerLoop(
        planner,
        execute,
        window.controller,  # Pass active controller directly
        MAX_STEPS
    )

    # Trigger loop execution after 1 second on the main GUI thread,
    # and quit the application cleanly when done.
    QTimer.singleShot(1000, lambda: [loop.run(instruction), app.quit()])

    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()