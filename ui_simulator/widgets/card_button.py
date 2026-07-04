from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

class CardButton(QPushButton):
    """
    A custom reusable button styled for the automotive HMI cards.
    Supports toggle/checkable states and is styled via QSS.
    """
    def __init__(self, text: str = "", object_name: str = "", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        if object_name:
            self.setObjectName(object_name)
        
        # Standard height for automotive buttons
        self.setFixedHeight(50)
