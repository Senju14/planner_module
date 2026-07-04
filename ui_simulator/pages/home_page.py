from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from pathlib import Path
from widgets.info_card import InfoCard
from widgets.card_button import CardButton

class HomePage(QWidget):
    """
    Home page containing status overview, climate controls, battery, and vehicle cards.
    """
    charging_state_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HomePage")

        self.temperature = 22
        self.charging = False
        self.battery_pct = 82

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header Title
        title_label = QLabel("Welcome to AutoOS")
        title_label.setObjectName("home_title")
        main_layout.addWidget(title_label)

        # Map Placeholder
        self.map_placeholder = InfoCard("map_placeholder")
        map_layout = QVBoxLayout(self.map_placeholder)
        map_layout.setContentsMargins(0, 0, 0, 0)
        
        map_lbl = QLabel()
        map_lbl.setObjectName("home_map_label")
        map_lbl.setAlignment(Qt.AlignCenter)
        
        map_path = Path(__file__).resolve().parent.parent / "assets" / "images" / "hmi_vector_map.png"
        if map_path.exists():
            pixmap = QPixmap(str(map_path))
            map_lbl.setPixmap(pixmap)
            map_lbl.setScaledContents(True)
        else:
            map_lbl.setText("🗺️ DIGITAL MAP DISPLAY\n(Navigation Systems Active)")
            map_lbl.setAlignment(Qt.AlignCenter)
            
        map_layout.addWidget(map_lbl)
        main_layout.addWidget(self.map_placeholder, stretch=3)

        # Bottom Cards layout (Climate, Battery, Vehicle Info)
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        # Climate Control Card
        self.climate_card = InfoCard("climate_card")
        climate_layout = QVBoxLayout(self.climate_card)
        climate_layout.setContentsMargins(16, 16, 16, 16)
        climate_lbl = QLabel("Cabin Climate")
        climate_lbl.setObjectName("climate_label")

        self.temp_lbl = QLabel(f"{self.temperature}°C")
        self.temp_lbl.setObjectName("temperature_value")

        btn_layout = QHBoxLayout()
        self.temp_down_btn = CardButton("-", "temp_down_btn")
        self.temp_down_btn.clicked.connect(self._decrease_temp)
        self.temp_up_btn = CardButton("+", "temp_up_btn")
        self.temp_up_btn.clicked.connect(self._increase_temp)
        btn_layout.addWidget(self.temp_down_btn)
        btn_layout.addWidget(self.temp_up_btn)

        climate_layout.addWidget(climate_lbl)
        climate_layout.addWidget(self.temp_lbl)
        climate_layout.addLayout(btn_layout)
        bottom_layout.addWidget(self.climate_card, 1)

        # Battery Card
        self.battery_card = InfoCard("battery_card")
        battery_layout = QVBoxLayout(self.battery_card)
        battery_layout.setContentsMargins(16, 16, 16, 16)
        battery_lbl = QLabel("Energy Level")
        battery_lbl.setObjectName("battery_label")

        self.battery_val_lbl = QLabel(f"{self.battery_pct}%")
        self.battery_val_lbl.setObjectName("battery_value")

        self.charge_toggle_btn = CardButton("Start Charging", "charge_toggle_btn")
        self.charge_toggle_btn.clicked.connect(self._toggle_charging)

        battery_layout.addWidget(battery_lbl)
        battery_layout.addWidget(self.battery_val_lbl)
        battery_layout.addWidget(self.charge_toggle_btn)
        bottom_layout.addWidget(self.battery_card, 1)

        # Vehicle Info Card
        self.vehicle_card = InfoCard("vehicle_card")
        vehicle_layout = QHBoxLayout(self.vehicle_card)
        vehicle_layout.setContentsMargins(16, 16, 16, 16)
        
        # Left Text panel
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        
        vehicle_lbl = QLabel("Vehicle Info")
        vehicle_lbl.setObjectName("vehicle_info_title")
        self.status_desc_lbl = QLabel("All Doors Secured")
        self.status_desc_lbl.setObjectName("vehicle_status_desc")
        tires_lbl = QLabel("Tire Pressure: 36 PSI")
        tires_lbl.setObjectName("vehicle_tires_desc")
        
        text_layout.addWidget(vehicle_lbl)
        text_layout.addWidget(self.status_desc_lbl)
        text_layout.addStretch()
        text_layout.addWidget(tires_lbl)
        
        # Right Image panel
        image_lbl = QLabel()
        image_lbl.setObjectName("vehicle_car_image")
        image_lbl.setAlignment(Qt.AlignCenter)
        
        ev_path = Path(__file__).resolve().parent.parent / "assets" / "images" / "futuristic_ev_render.png"
        if ev_path.exists():
            pixmap = QPixmap(str(ev_path))
            image_lbl.setPixmap(pixmap.scaled(200, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
        vehicle_layout.addWidget(text_container, stretch=2)
        vehicle_layout.addWidget(image_lbl, stretch=1)
        bottom_layout.addWidget(self.vehicle_card, 1)

        main_layout.addLayout(bottom_layout, stretch=2)

    def _increase_temp(self):
        self.temperature += 1
        self.temp_lbl.setText(f"{self.temperature}°C")

    def _decrease_temp(self):
        self.temperature -= 1
        self.temp_lbl.setText(f"{self.temperature}°C")

    def _toggle_charging(self):
        self.charging = not self.charging
        if self.charging:
            self.charge_toggle_btn.setText("Stop Charging")
            self.battery_val_lbl.setText(f"{self.battery_pct}% ⚡")
        else:
            self.charge_toggle_btn.setText("Start Charging")
            self.battery_val_lbl.setText(f"{self.battery_pct}%")
        self.charging_state_changed.emit(self.charging)
