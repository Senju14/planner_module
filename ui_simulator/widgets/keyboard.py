from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit

class VirtualKeyboard(QWidget):
    """
    A virtual keyboard widget for TYPE action simulation in the HMI.
    Emits submitted signal with current text when ENTER is clicked.
    """
    submitted = Signal(str)
    cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VirtualKeyboard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Input display
        self.input_field = QLineEdit()
        self.input_field.setObjectName("keyboard_input")
        self.input_field.setPlaceholderText("Type location or search settings...")
        self.input_field.setReadOnly(True)  # Read-only so it's controlled strictly via keyboard keys
        self.input_field.setFixedHeight(50)
        layout.addWidget(self.input_field)

        # Key rows layout
        rows = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
            ["z", "x", "c", "v", "b", "n", "m"],
        ]

        for row in rows:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(8)
            for key in row:
                btn = QPushButton(key.upper())
                btn.setObjectName(f"key_{key}")
                btn.setCursor(Qt.PointingHandCursor)
                btn.setFixedSize(55, 55)
                btn.clicked.connect(lambda _, k=key: self._on_key_clicked(k))
                row_layout.addWidget(btn)
            layout.addLayout(row_layout)

        # Control keys row
        control_layout = QHBoxLayout()
        control_layout.setSpacing(8)

        clear_btn = QPushButton("CLEAR")
        clear_btn.setObjectName("key_clear")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setFixedHeight(55)
        clear_btn.clicked.connect(self._on_clear_clicked)
        control_layout.addWidget(clear_btn, 1)

        space_btn = QPushButton("SPACE")
        space_btn.setObjectName("key_space")
        space_btn.setCursor(Qt.PointingHandCursor)
        space_btn.setFixedHeight(55)
        space_btn.clicked.connect(lambda: self._on_key_clicked(" "))
        control_layout.addWidget(space_btn, 2)

        back_btn = QPushButton("⌫")
        back_btn.setObjectName("key_backspace")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setFixedHeight(55)
        back_btn.clicked.connect(self._on_back_clicked)
        control_layout.addWidget(back_btn, 1)

        enter_btn = QPushButton("ENTER")
        enter_btn.setObjectName("key_enter")
        enter_btn.setCursor(Qt.PointingHandCursor)
        enter_btn.setFixedHeight(55)
        enter_btn.clicked.connect(self._on_enter_clicked)
        control_layout.addWidget(enter_btn, 1.5)

        layout.addLayout(control_layout)

    def _on_key_clicked(self, char: str):
        self.input_field.setText(self.input_field.text() + char)

    def _on_back_clicked(self):
        current_text = self.input_field.text()
        if current_text:
            self.input_field.setText(current_text[:-1])

    def _on_clear_clicked(self):
        self.input_field.setText("")

    def _on_enter_clicked(self):
        self.submitted.emit(self.input_field.text())

    def set_text(self, text: str):
        """Allows pre-populating the keyboard input field."""
        self.input_field.setText(text)

    def get_text(self) -> str:
        """Returns the current input string."""
        return self.input_field.text()
