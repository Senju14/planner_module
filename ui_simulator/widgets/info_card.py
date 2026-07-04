from PySide6.QtWidgets import QFrame

class InfoCard(QFrame):
    """
    A custom reusable information card widget with rounded corners.
    Acts as a container for other widgets.
    """
    def __init__(self, object_name: str = "Card", parent=None):
        super().__init__(parent)
        self.setObjectName(object_name)
