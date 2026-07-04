from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from widgets.keyboard import VirtualKeyboard

class KeyboardPage(QWidget):
    """
    Page containing the virtual keyboard, acting as the destination for the TYPE action.
    """
    submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("KeyboardPage")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header Title
        title = QLabel("Virtual Keyboard Input")
        title.setObjectName("keyboard_title")
        layout.addWidget(title)

        # Virtual Keyboard
        self.keyboard = VirtualKeyboard()
        self.keyboard.submitted.connect(self.submitted.emit)
        layout.addWidget(self.keyboard)
        layout.addStretch()

    def set_text(self, text: str):
        """Pre-populate keyboard text field."""
        self.keyboard.set_text(text)
        self.keyboard.input_field.setFocus()
