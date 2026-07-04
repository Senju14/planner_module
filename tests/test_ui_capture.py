import sys
from pathlib import Path

# Append project root and ui_simulator to PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "ui_simulator"))

from PySide6.QtWidgets import QApplication
from ui_simulator.main_window import MainWindow
from ui_simulator.controller import capture_current_screen

def test_screen_capture():
    """
    Initializes the HMI main window, triggers capture_current_screen(),
    and asserts that screenshots/current.png is successfully written.
    """
    print("\n=== HMI UI Capture Test ===")
    
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    app.processEvents()

    # Clear prior screen capture files
    save_path = Path("screenshots/current.png")
    if save_path.exists():
        save_path.unlink()

    # Trigger capture
    success = capture_current_screen()
    
    assert success, "capture_current_screen returned failure state."
    assert save_path.exists(), "screenshots/current.png was not written to disk."
    assert save_path.stat().st_size > 0, "screenshots/current.png is empty (0 bytes)."
    
    print(f"Success: Screenshot captured and verified at '{save_path}'")
    print("===========================\n")

if __name__ == "__main__":
    test_screen_capture()
