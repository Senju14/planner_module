import sys
from pathlib import Path

# Append project root and ui_simulator to PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "ui_simulator"))

from PySide6.QtWidgets import QApplication
from ui_simulator.main_window import MainWindow

def test_ui_state_collection():
    """
    Launches HMI, calls collect_ui_state(), and asserts it returns correct metadata.
    """
    print("\n=== HMI UI State Collection Test ===")
    app = QApplication.instance() or QApplication([])

    window = MainWindow()
    window.show()
    app.processEvents()

    # Collect active screen state
    state = window.controller.collect_ui_state()

    # Assert base format
    assert isinstance(state, dict), "UI state must be a dict."
    assert "screen" in state, "UI state must specify the active 'screen' identifier."
    assert state["screen"] == "home", "Default active screen must be 'home'."
    assert "widgets" in state, "UI state must contain 'widgets' list."
    assert isinstance(state["widgets"], list), "'widgets' must be a list of widget definitions."
    assert len(state["widgets"]) > 0, "Widgets list should not be empty."

    # Validate widget properties
    for widget in state["widgets"]:
        assert "id" in widget, "Widget definition must have an 'id'."
        assert "type" in widget, "Widget definition must have a 'type'."
        assert "text" in widget, "Widget definition must have a 'text' label."
        assert "enabled" in widget, "Widget definition must specify 'enabled' state."
        assert "visible" in widget, "Widget definition must specify 'visible' state."
        assert "geometry" in widget, "Widget definition must specify 'geometry' list."

        # Verify property datatypes
        assert isinstance(widget["id"], str), "'id' must be a string."
        assert isinstance(widget["type"], str), "'type' must be a string."
        assert isinstance(widget["text"], str), "'text' must be a string."
        assert isinstance(widget["enabled"], bool), "'enabled' must be a boolean."
        assert isinstance(widget["visible"], bool), "'visible' must be a boolean."
        assert isinstance(widget["geometry"], list), "'geometry' must be a list."
        assert len(widget["geometry"]) == 4, "'geometry' list must specify [x, y, w, h]."
        
        # Verify geometry values are valid coordinates/bounds
        x, y, w, h = widget["geometry"]
        assert isinstance(x, int) and isinstance(y, int), "Coordinates must be integers."
        assert isinstance(w, int) and isinstance(h, int), "Dimensions must be integers."
        assert w >= 0 and h >= 0, "Width and height must be non-negative."

    print("Success: collect_ui_state() returns valid and verified widget metadata.")
    print("====================================\n")

if __name__ == "__main__":
    test_ui_state_collection()
