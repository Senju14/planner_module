from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QCheckBox, QSlider, QHBoxLayout
from widgets.info_card import InfoCard

class SettingsPage(QWidget):
    """
    Settings page containing exactly 25 options inside a scrollable view for SWIPE actions testing.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsPage")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Page Title
        title = QLabel("System Settings")
        title.setObjectName("settings_title")
        main_layout.addWidget(title)

        # Scroll Area Setup
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("settings_scroll_area")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Content Widget
        scroll_widget = QWidget()
        scroll_widget.setObjectName("settings_scroll_content")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(12)
        scroll_layout.setContentsMargins(10, 10, 10, 10)

        # Settings Items Definition (25 Items)
        settings_data = [
            ("Wireless Connection (Wi-Fi)", "toggle", "setting_wifi_toggle"),
            ("Bluetooth Sharing", "toggle", "setting_bluetooth_toggle"),
            ("Cellular Hotspot Setup", "toggle", "setting_cellular_toggle"),
            ("Display Panel Brightness", "slider", "setting_brightness_slider"),
            ("Acoustic Media Volume", "slider", "setting_volume_slider"),
            ("Voice Assistance Prompts", "toggle", "setting_voice_guidance"),
            ("Auto High Beam Activation", "toggle", "setting_auto_high_beams"),
            ("Rain Sensing Smart Wipers", "toggle", "setting_auto_wipers"),
            ("Lane Departure Warnings", "toggle", "setting_lane_warning"),
            ("Lane Keeping Assist System", "toggle", "setting_lane_assist"),
            ("Forward Collision Warning Alert", "toggle", "setting_collision_warning"),
            ("Emergency Automatic Braking", "toggle", "setting_emergency_braking"),
            ("Traction Control Safeguard", "toggle", "setting_traction_control"),
            ("Speed Limit Visual Warning", "toggle", "setting_speed_warning"),
            ("Blind Spot Side Cameras", "toggle", "setting_blind_spot"),
            ("Sentry Guard Security Mode", "toggle", "setting_sentry_mode"),
            ("Cabin Overheat Protection System", "toggle", "setting_cabin_protection"),
            ("Valet Parking Limit Mode", "toggle", "setting_valet_mode"),
            ("Mobile Remote Connectivity", "toggle", "setting_mobile_access"),
            ("Auto Dimming Side Mirrors", "toggle", "setting_auto_dim_mirrors"),
            ("Walk Away Proximity Locking", "toggle", "setting_walk_away_lock"),
            ("Child Safety Rear Door Locks", "toggle", "setting_child_lock"),
            ("System Speech Volume Control", "slider", "setting_nav_volume_slider"),
            ("Cabin Ambient Lighting Dimmer", "slider", "setting_ambient_light_slider"),
            ("Automatic Software Update Sync", "toggle", "setting_software_update"),
        ]

        for label_text, type_, obj_name in settings_data:
            item_card = InfoCard(f"card_{obj_name}")
            item_layout = QHBoxLayout(item_card)
            item_layout.setContentsMargins(16, 12, 16, 12)

            lbl = QLabel(label_text)
            lbl.setObjectName(f"lbl_{obj_name}")
            lbl.setStyleSheet("font-size: 15px; color: #f3f4f6;")
            item_layout.addWidget(lbl)
            item_layout.addStretch()

            if type_ == "toggle":
                control = QCheckBox()
                control.setObjectName(obj_name)
                control.setCursor(Qt.PointingHandCursor)
                control.setChecked(True)
                item_layout.addWidget(control)
            elif type_ == "slider":
                control = QSlider(Qt.Horizontal)
                control.setObjectName(obj_name)
                control.setRange(0, 100)
                control.setValue(70)
                control.setFixedWidth(200)
                item_layout.addWidget(control)

            scroll_layout.addWidget(item_card)

        scroll_layout.addStretch()
        self.scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(self.scroll_area)
