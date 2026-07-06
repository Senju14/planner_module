from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMainWindow, QStackedWidget
from controller import UIController
from widgets.sidebar import Sidebar
from widgets.status_bar import StatusBar
from pages.home_page import HomePage
from pages.navigation_page import NavigationPage
from pages.vehicle_page import VehiclePage
from pages.settings_page import SettingsPage
from pages.keyboard_page import KeyboardPage

class MainWindow(QMainWindow):
    """
    Main application shell managing global layout, layout nesting, timers, and pages.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoOS Simulator")
        self.resize(1024, 576)
        self.setMinimumSize(800, 450)

        # UI Navigation Controller
        self.controller = UIController(self)

        # Central widget layout
        root = QWidget()
        self.setCentralWidget(root)

        main_layout = QHBoxLayout(root)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left panel (Navigation Sidebar)
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        # Right panel (Main content area containing Status Bar & Page Stack)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Top Status Bar
        self.status_bar = StatusBar()
        right_layout.addWidget(self.status_bar)

        # Central Page Stack
        self.stack = QStackedWidget()
        right_layout.addWidget(self.stack, stretch=1)
        main_layout.addWidget(right_panel, stretch=1)

        # Instantiating page views
        self.home_page = HomePage()
        self.nav_page = NavigationPage()
        self.vehicle_page = VehiclePage()
        self.settings_page = SettingsPage()
        self.keyboard_page = KeyboardPage()

        # Mapping pages for easy lookup
        self.pages = {
            "home": self.home_page,
            "navigation": self.nav_page,
            "vehicle": self.vehicle_page,
            "settings": self.settings_page,
            "keyboard": self.keyboard_page
        }

        # Adding pages to stack
        for page_widget in self.pages.values():
            self.stack.addWidget(page_widget)

        # Signal and Slot connections
        self.sidebar.navigation_requested.connect(self.controller.goto)
        self.controller.page_changed.connect(self._on_page_changed)

        # Navigation and Keyboard coordination
        self.nav_page.search_requested.connect(self._on_search_requested)
        self.keyboard_page.submitted.connect(self._on_keyboard_submitted)

        # Home charging state updates Status Bar
        self.home_page.charging_state_changed.connect(
            lambda charging: self.status_bar.update_battery(self.home_page.battery_pct, charging)
        )

        # 1-second system clock update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.status_bar.update_time)
        self.timer.start(1000)
        self.status_bar.update_time()

        # Set default view
        self.controller.goto("home")

    def _on_page_changed(self, page_name: str):
        if page_name in self.pages:
            self.stack.setCurrentWidget(self.pages[page_name])
            self.sidebar.set_active_page(page_name)

    def _on_search_requested(self, text: str):
        self.keyboard_page.set_text(text)
        self.controller.goto("keyboard")

    def _on_keyboard_submitted(self, text: str):
        self.nav_page.start_navigation(text)
        self.controller.back()