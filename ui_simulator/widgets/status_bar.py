from PySide6.QtCore import Qt, QTime
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

class StatusBar(QWidget):
    """
    Status bar showing system status (Wi-Fi, clock, battery percentage).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusBar")
        self.setFixedHeight(50)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)

        # WiFi label
        self.wifi_label = QLabel("📶 Connected")
        self.wifi_label.setObjectName("status_wifi")
        self.wifi_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Digital Clock label
        self.clock_label = QLabel("12:00")
        self.clock_label.setObjectName("status_clock")
        self.clock_label.setAlignment(Qt.AlignCenter)

        # Battery percentage label
        self.battery_label = QLabel("82% 🔋")
        self.battery_label.setObjectName("status_battery")
        self.battery_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(self.wifi_label)
        layout.addStretch()
        layout.addWidget(self.clock_label)
        layout.addStretch()
        layout.addWidget(self.battery_label)

    def update_time(self):
        """Updates the digital clock to the current local time."""
        self.clock_label.setText(QTime.currentTime().toString("HH:mm"))

    def update_battery(self, percentage: int, charging: bool = False):
        """Updates the battery percentage and icon/charging state."""
        charging_icon = " ⚡" if charging else " 🔋"
        self.battery_label.setText(f"{percentage}%{charging_icon}")
