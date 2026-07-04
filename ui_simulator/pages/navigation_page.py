from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QGridLayout
from PySide6.QtGui import QPixmap
from pathlib import Path
from widgets.info_card import InfoCard
from widgets.card_button import CardButton

class SearchBox(QLineEdit):
    """
    Subclassed QLineEdit that emits a focused signal when clicked.
    """
    focused = Signal()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.focused.emit()

class NavigationPage(QWidget):
    """
    Navigation page containing destination searches and a list of recent targets.
    """
    search_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NavigationPage")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Page Title
        title = QLabel("Navigation")
        title.setObjectName("nav_title")
        main_layout.addWidget(title)

        # Search Bar
        self.search_input = SearchBox()
        self.search_input.setObjectName("search_box")
        self.search_input.setPlaceholderText("Search destinations or coordinates...")
        self.search_input.setFixedHeight(50)
        self.search_input.focused.connect(self._on_search_focused)
        main_layout.addWidget(self.search_input)

        # Content Layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Map display card with overlay Grid
        self.map_card = InfoCard("map_card")
        grid = QGridLayout(self.map_card)
        grid.setContentsMargins(0, 0, 0, 0)

        # Map background image
        self.map_img_lbl = QLabel()
        self.map_img_lbl.setObjectName("map_image")
        self.map_img_lbl.setAlignment(Qt.AlignCenter)

        map_path = Path(__file__).resolve().parent.parent / "assets" / "images" / "hmi_vector_map.png"
        if map_path.exists():
            self.map_img_lbl.setPixmap(QPixmap(str(map_path)))
            self.map_img_lbl.setScaledContents(True)
        else:
            self.map_img_lbl.setText("🗺️ DIGITAL MAP READY")

        grid.addWidget(self.map_img_lbl, 0, 0)

        # Glassmorphic HUD overlay
        hud_overlay = QWidget()
        hud_overlay.setObjectName("hud_overlay")
        hud_overlay.setStyleSheet("background-color: rgba(15, 23, 42, 0.85); border-radius: 12px; margin: 15px;")
        hud_layout = QVBoxLayout(hud_overlay)
        hud_layout.setContentsMargins(20, 12, 20, 12)

        self.map_status_lbl = QLabel("🧭 READY FOR NAVIGATION\nEnter destination or select recent")
        self.map_status_lbl.setObjectName("map_status_label")
        self.map_status_lbl.setAlignment(Qt.AlignCenter)
        self.map_status_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: white; background: transparent;")
        hud_layout.addWidget(self.map_status_lbl)

        grid.addWidget(hud_overlay, 0, 0, Qt.AlignBottom | Qt.AlignHCenter)
        content_layout.addWidget(self.map_card, stretch=2)

        # Recents list card
        self.recents_card = InfoCard("recents_card")
        recents_layout = QVBoxLayout(self.recents_card)
        recents_layout.setContentsMargins(16, 16, 16, 16)
        recents_layout.setSpacing(10)

        recents_title = QLabel("Recent Destinations")
        recents_title.setObjectName("recents_title")
        recents_layout.addWidget(recents_title)

        destinations = [
            ("Home", "recent_home_btn"),
            ("Work", "recent_work_btn"),
            ("Supercharger", "recent_charger_btn"),
            ("Downtown Station", "recent_downtown_btn")
        ]

        for label, obj_name in destinations:
            btn = CardButton(label, obj_name)
            btn.clicked.connect(lambda _, lbl=label: self.start_navigation(lbl))
            recents_layout.addWidget(btn)

        recents_layout.addStretch()
        content_layout.addWidget(self.recents_card, stretch=1)

        main_layout.addLayout(content_layout, stretch=1)

    def _on_search_focused(self):
        self.search_requested.emit(self.search_input.text())

    def start_navigation(self, destination: str):
        """Starts navigating to the selected destination."""
        self.search_input.setText(destination)
        self.map_status_lbl.setText(f"🧭 NAVIGATING TO:\n{destination}\n(Route calculation optimal)")
