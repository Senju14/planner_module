from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QButtonGroup
from widgets.card_button import CardButton

class Sidebar(QWidget):
    """
    Sidebar navigation widget containing buttons to navigate between primary views.
    """
    navigation_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(10)

        # HMI Logo
        logo = QLabel("AutoOS")
        logo.setAlignment(Qt.AlignCenter)
        logo.setObjectName("SidebarLogo")
        layout.addWidget(logo)

        # Spacer
        layout.addSpacing(20)

        # Nav Buttons Group
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        self.home_btn = self._create_nav_btn("Home", "home", "home_button")
        self.nav_btn = self._create_nav_btn("Navigation", "navigation", "navigation_button")
        self.vehicle_btn = self._create_nav_btn("Vehicle", "vehicle", "vehicle_button")
        self.settings_btn = self._create_nav_btn("Settings", "settings", "settings_button")

        layout.addWidget(self.home_btn)
        layout.addWidget(self.nav_btn)
        layout.addWidget(self.vehicle_btn)
        layout.addWidget(self.settings_btn)

        layout.addStretch()

        # Set default active
        self.home_btn.setChecked(True)

    def _create_nav_btn(self, label: str, target: str, obj_name: str) -> CardButton:
        btn = CardButton(label, obj_name)
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.navigation_requested.emit(target))
        self.btn_group.addButton(btn)
        return btn

    def set_active_page(self, page_name: str):
        """Highlights the button corresponding to the active page."""
        btn_map = {
            "home": self.home_btn,
            "navigation": self.nav_btn,
            "vehicle": self.vehicle_btn,
            "settings": self.settings_btn
        }
        if page_name in btn_map:
            btn_map[page_name].setChecked(True)
