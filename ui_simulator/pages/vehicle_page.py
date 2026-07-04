from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QButtonGroup
from widgets.info_card import InfoCard
from widgets.card_button import CardButton

class VehiclePage(QWidget):
    """
    Vehicle settings page containing controls for driving mode, lights, doors, mirrors, and charging.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VehiclePage")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header Title
        title = QLabel("Vehicle Settings")
        title.setObjectName("vehicle_title")
        main_layout.addWidget(title)

        # Top row: Driving Modes & Lights control
        top_row = QHBoxLayout()
        top_row.setSpacing(20)

        # Driving Modes Card
        modes_card = InfoCard("modes_card")
        modes_layout = QVBoxLayout(modes_card)
        modes_layout.setContentsMargins(16, 16, 16, 16)
        modes_title = QLabel("Dynamics Mode")
        modes_title.setObjectName("modes_title")
        modes_layout.addWidget(modes_title)

        modes_btn_layout = QHBoxLayout()
        self.modes_group = QButtonGroup(self)
        self.modes_group.setExclusive(True)

        self.mode_eco = self._add_mode_btn("Eco", "mode_eco_btn", modes_btn_layout)
        self.mode_comfort = self._add_mode_btn("Comfort", "mode_comfort_btn", modes_btn_layout)
        self.mode_sport = self._add_mode_btn("Sport", "mode_sport_btn", modes_btn_layout)
        self.mode_comfort.setChecked(True)

        modes_layout.addLayout(modes_btn_layout)
        top_row.addWidget(modes_card, 1)

        # Lights Card
        lights_card = InfoCard("lights_card")
        lights_layout = QVBoxLayout(lights_card)
        lights_layout.setContentsMargins(16, 16, 16, 16)
        lights_title = QLabel("Headlights Mode")
        lights_title.setObjectName("lights_title")
        lights_layout.addWidget(lights_title)

        lights_btn_layout = QHBoxLayout()
        self.lights_group = QButtonGroup(self)
        self.lights_group.setExclusive(True)

        self.lights_auto = self._add_light_btn("Auto", "lights_auto_btn", lights_btn_layout)
        self.lights_on = self._add_light_btn("On", "lights_on_btn", lights_btn_layout)
        self.lights_off = self._add_light_btn("Off", "lights_off_btn", lights_btn_layout)
        self.lights_auto.setChecked(True)

        lights_layout.addLayout(lights_btn_layout)
        top_row.addWidget(lights_card, 1)

        main_layout.addLayout(top_row, stretch=1)

        # Middle Row: Doors list & Mirrors/Charging side-by-side
        middle_row = QHBoxLayout()
        middle_row.setSpacing(20)

        # Door access card
        doors_card = InfoCard("doors_card")
        doors_layout = QVBoxLayout(doors_card)
        doors_layout.setContentsMargins(16, 16, 16, 16)
        doors_title = QLabel("Access Control")
        doors_title.setObjectName("doors_title")
        doors_layout.addWidget(doors_title)

        doors_grid = QVBoxLayout()
        row1 = QHBoxLayout()
        self.btn_door_fl = CardButton("Front Left: Lock", "door_fl_btn")
        self.btn_door_fl.setCheckable(True)
        self.btn_door_fl.clicked.connect(lambda: self._toggle_door(self.btn_door_fl, "Front Left"))
        self.btn_door_fr = CardButton("Front Right: Lock", "door_fr_btn")
        self.btn_door_fr.setCheckable(True)
        self.btn_door_fr.clicked.connect(lambda: self._toggle_door(self.btn_door_fr, "Front Right"))
        row1.addWidget(self.btn_door_fl)
        row1.addWidget(self.btn_door_fr)

        row2 = QHBoxLayout()
        self.btn_door_rl = CardButton("Rear Left: Lock", "door_rl_btn")
        self.btn_door_rl.setCheckable(True)
        self.btn_door_rl.clicked.connect(lambda: self._toggle_door(self.btn_door_rl, "Rear Left"))
        self.btn_door_rr = CardButton("Rear Right: Lock", "door_rr_btn")
        self.btn_door_rr.setCheckable(True)
        self.btn_door_rr.clicked.connect(lambda: self._toggle_door(self.btn_door_rr, "Rear Right"))
        row2.addWidget(self.btn_door_rl)
        row2.addWidget(self.btn_door_rr)

        row3 = QHBoxLayout()
        self.btn_hood = CardButton("Hood: Closed", "hood_btn")
        self.btn_hood.setCheckable(True)
        self.btn_hood.clicked.connect(lambda: self._toggle_hood_trunk(self.btn_hood, "Hood"))
        self.btn_trunk = CardButton("Trunk: Closed", "trunk_btn")
        self.btn_trunk.setCheckable(True)
        self.btn_trunk.clicked.connect(lambda: self._toggle_hood_trunk(self.btn_trunk, "Trunk"))
        row3.addWidget(self.btn_hood)
        row3.addWidget(self.btn_trunk)

        doors_grid.addLayout(row1)
        doors_grid.addLayout(row2)
        doors_grid.addLayout(row3)
        doors_layout.addLayout(doors_grid)
        middle_row.addWidget(doors_card, stretch=2)

        # Right sidebar widgets
        right_panel = QVBoxLayout()
        right_panel.setSpacing(20)

        # Mirrors Card
        mirrors_card = InfoCard("mirrors_card")
        mirrors_layout = QVBoxLayout(mirrors_card)
        mirrors_layout.setContentsMargins(16, 16, 16, 16)
        mirrors_title = QLabel("Side Mirrors")
        mirrors_title.setObjectName("mirrors_title")
        mirrors_layout.addWidget(mirrors_title)

        mirrors_btn_layout = QHBoxLayout()
        self.mirror_fold = CardButton("Folded", "mirror_fold_btn")
        self.mirror_fold.setCheckable(True)
        self.mirror_fold.clicked.connect(self._toggle_mirror_fold)
        self.mirror_heat = CardButton("Heat: Off", "mirror_heat_btn")
        self.mirror_heat.setCheckable(True)
        self.mirror_heat.clicked.connect(self._toggle_mirror_heat)
        mirrors_btn_layout.addWidget(self.mirror_fold)
        mirrors_btn_layout.addWidget(self.mirror_heat)
        mirrors_layout.addLayout(mirrors_btn_layout)
        right_panel.addWidget(mirrors_card, 1)

        # Charging Config Card
        charging_card = InfoCard("charging_card")
        charging_layout = QVBoxLayout(charging_card)
        charging_layout.setContentsMargins(16, 16, 16, 16)
        charging_title = QLabel("Charging limit")
        charging_title.setObjectName("charging_limit_title")
        charging_layout.addWidget(charging_title)

        self.charge_slider_lbl = QLabel("Limit: 80%")
        self.charge_slider_lbl.setObjectName("charge_limit_label")
        charging_layout.addWidget(self.charge_slider_lbl)

        self.charge_slider = QSlider(Qt.Horizontal)
        self.charge_slider.setObjectName("charge_limit_slider")
        self.charge_slider.setRange(50, 100)
        self.charge_slider.setValue(80)
        self.charge_slider.valueChanged.connect(self._on_charge_limit_changed)
        charging_layout.addWidget(self.charge_slider)

        self.charge_port = CardButton("Port: Closed", "charge_port_btn")
        self.charge_port.setCheckable(True)
        self.charge_port.clicked.connect(self._toggle_charge_port)
        charging_layout.addWidget(self.charge_port)

        right_panel.addWidget(charging_card, 2)
        middle_row.addLayout(right_panel, stretch=1)

        main_layout.addLayout(middle_row, stretch=2)

    def _add_mode_btn(self, name: str, obj_name: str, layout: QHBoxLayout) -> CardButton:
        btn = CardButton(name, obj_name)
        btn.setCheckable(True)
        self.modes_group.addButton(btn)
        layout.addWidget(btn)
        return btn

    def _add_light_btn(self, name: str, obj_name: str, layout: QHBoxLayout) -> CardButton:
        btn = CardButton(name, obj_name)
        btn.setCheckable(True)
        self.lights_group.addButton(btn)
        layout.addWidget(btn)
        return btn

    def _toggle_door(self, btn: CardButton, name: str):
        if btn.isChecked():
            btn.setText(f"{name}: Unlock")
        else:
            btn.setText(f"{name}: Lock")

    def _toggle_hood_trunk(self, btn: CardButton, name: str):
        if btn.isChecked():
            btn.setText(f"{name}: Open")
        else:
            btn.setText(f"{name}: Closed")

    def _toggle_mirror_fold(self):
        if self.mirror_fold.isChecked():
            self.mirror_fold.setText("Unfolded")
        else:
            self.mirror_fold.setText("Folded")

    def _toggle_mirror_heat(self):
        if self.mirror_heat.isChecked():
            self.mirror_heat.setText("Heat: On")
        else:
            self.mirror_heat.setText("Heat: Off")

    def _on_charge_limit_changed(self, val: int):
        self.charge_slider_lbl.setText(f"Limit: {val}%")

    def _toggle_charge_port(self):
        if self.charge_port.isChecked():
            self.charge_port.setText("Port: Open")
        else:
            self.charge_port.setText("Port: Closed")
