from PySide6.QtCore import QObject, Signal, QPoint
from PySide6.QtWidgets import QWidget, QAbstractButton, QLineEdit, QLabel, QFrame, QApplication, QMainWindow

class UIController(QObject):
    """
    Manages navigation, history, and active screen UI state aggregation.
    """
    page_changed = Signal(str)

    def __init__(self, main_window: QMainWindow = None):
        super().__init__()
        self.main_window = main_window
        self.current_page_name = "home"
        self.history = []

    def goto(self, page: str, save_history: bool = True):
        """Navigates to the specified page and saves history."""
        if save_history and self.current_page_name != page:
            self.history.append(self.current_page_name)
        self.current_page_name = page
        self.page_changed.emit(page)

    def back(self):
        """Navigates back to the previous page in history."""
        if self.history:
            prev_page = self.history.pop()
            self.goto(prev_page, save_history=False)

    def current_page(self) -> str:
        """Returns the identifier of the current active page."""
        return self.current_page_name

    def collect_ui_state(self) -> dict:
        """
        Dynamically inspects the active Qt widget hierarchy.
        Returns a serializable dictionary representing target interactive widgets,
        their geometries, texts, and visibility states.
        """
        state = {
            "screen": self.current_page_name,
            "widgets": []
        }

        # Resolve main window reference if not set
        if not self.main_window:
            app = QApplication.instance()
            if app:
                for widget in app.topLevelWidgets():
                    if isinstance(widget, QMainWindow):
                        self.main_window = widget
                        break

        if not self.main_window:
            return state

        for widget in self.main_window.findChildren(QWidget):
            name = widget.objectName()
            if not name:
                continue

            # Skip keyboard individual keys to save VLM tokens
            if name.startswith("key_"):
                continue

            # Determine if widget is visible within current window hierarchy
            is_visible = widget.isVisible() and widget.isVisibleTo(self.main_window)
            if not is_visible:
                continue


            # Map coordinates to the MainWindow top-left corner
            if is_visible:
                pos = widget.mapTo(self.main_window, QPoint(0, 0))
                x, y = pos.x(), pos.y()
            else:
                x, y = 0, 0

            w = widget.width()
            h = widget.height()

            # Retrieve widget text value safely
            text = ""
            if hasattr(widget, "text") and callable(widget.text):
                text = widget.text()
            elif hasattr(widget, "placeholderText") and callable(widget.placeholderText):
                text = widget.placeholderText()
            elif hasattr(widget, "currentText") and callable(widget.currentText):
                text = widget.currentText()

            # Classify widget types
            if isinstance(widget, QAbstractButton):
                widget_type = "button"
            elif isinstance(widget, QLineEdit):
                widget_type = "input"
            elif isinstance(widget, QLabel):
                widget_type = "label"
            elif isinstance(widget, QFrame):
                widget_type = "card"
            else:
                widget_type = "widget"

            state["widgets"].append({
                "id": name,
                "text": text,
                "type": widget_type,
                "enabled": widget.isEnabled(),
                "visible": is_visible,
                "geometry": [x, y, w, h]
            })

        return state

def capture_current_screen() -> bool:
    """
    Captures the screenshot of the active MainWindow of the simulator
    and saves it to screenshots/current.png.
    """
    app = QApplication.instance()
    if not app:
        print("[CAPTURE] Error: No running QApp instance found.")
        return False

    main_window = None
    for widget in app.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            main_window = widget
            break

    if not main_window:
        print("[CAPTURE] Error: MainWindow not found.")
        return False

    from pathlib import Path
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    save_path = screenshots_dir / "current.png"

    pixmap = main_window.grab()
    success = pixmap.save(str(save_path), "PNG")
    if success:
        print(f"[CAPTURE] Screenshot saved successfully to {save_path}")
    else:
        print(f"[CAPTURE] Error: Failed to save screenshot to {save_path}")
    return success