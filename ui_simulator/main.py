import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# Dynamically add parent/current dir to system path to ensure clean import of main_window, controller, pages, and widgets
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from main_window import MainWindow

def load_stylesheet(app: QApplication):
    """Loads the stylesheet from the style.qss file."""
    style_file = current_dir / "style.qss"
    if style_file.exists():
        with open(style_file, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

def main():
    app = QApplication(sys.argv)
    load_stylesheet(app)

    window = MainWindow()
    window.show()
    app.processEvents()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()