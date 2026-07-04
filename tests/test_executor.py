import sys
import json
from pathlib import Path

# Append project root and ui_simulator to PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "ui_simulator"))

from PySide6.QtWidgets import QApplication
from ui_simulator.main_window import MainWindow
from src.executor import execute

def test_executor_actions():
    """
    Simulates a sequence of CLICK, TYPE, and SWIPE executor calls on the active HMI
    to verify page navigation, text typing, and settings scrolling.
    """
    print("\n=== HMI Action Executor Test ===")
    app = QApplication.instance() or QApplication([])
    
    # Initialize main window
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Assert starting state
    assert window.controller.current_page() == "home", "Start page must be 'home'"
    print("1. Start page is Home. Passed.")
    
    # Action 1: Click Navigation Button
    # navigation_button is located in the left sidebar around [100, 150].
    click_nav_action = {
        "action": "CLICK",
        "target_coordinates": [100, 150],
        "text_value": ""
    }
    success = execute(click_nav_action)
    assert success, "Failed to execute CLICK on navigation_button."
    assert window.controller.current_page() == "navigation", "Should have navigated to 'navigation'."
    print("2. Switch to Navigation view via CLICK. Passed.")
    
    # Action 2: Click Search Box
    state = window.controller.collect_ui_state()
    search_geom = None
    for widget in state["widgets"]:
        if widget["id"] == "search_box":
            search_geom = widget["geometry"]
            break
    assert search_geom is not None, "search_box not found in UI state list."
    
    click_x = search_geom[0] + search_geom[2] // 2
    click_y = search_geom[1] + search_geom[3] // 2
    click_search_action = {
        "action": "CLICK",
        "target_coordinates": [click_x, click_y],
        "text_value": ""
    }
    success = execute(click_search_action)
    assert success, "Failed to execute CLICK on search_box."
    assert window.controller.current_page() == "keyboard", "Should have navigated to 'keyboard'."
    print("3. Switch to Keyboard input view via CLICK on Search Box. Passed.")
    
    # Action 3: Type text into focused widget (keyboard_input)
    type_action = {
        "action": "TYPE",
        "target_coordinates": [0, 0],
        "text_value": "Seattle Supercharger"
    }
    success = execute(type_action)
    assert success, "Failed to execute TYPE action on keyboard."
    assert window.keyboard_page.keyboard.get_text() == "Seattle Supercharger", "Text typing mismatch."
    print("4. TYPE action into keyboard. Passed.")
    
    # Action 4: Click Enter on Virtual Keyboard to submit and return
    state = window.controller.collect_ui_state()
    enter_geom = None
    for widget in state["widgets"]:
        if widget["id"] == "key_enter" and widget["visible"]:
            enter_geom = widget["geometry"]
            break
    assert enter_geom is not None, "key_enter button not visible in UI state."
    
    click_enter_x = enter_geom[0] + enter_geom[2] // 2
    click_enter_y = enter_geom[1] + enter_geom[3] // 2
    click_enter_action = {
        "action": "CLICK",
        "target_coordinates": [click_enter_x, click_enter_y],
        "text_value": ""
    }
    success = execute(click_enter_action)
    assert success, "Failed to execute CLICK on key_enter."
    
    # Page must return to Navigation page with updated search query
    assert window.controller.current_page() == "navigation", "Should have returned to 'navigation'."
    assert window.nav_page.search_input.text() == "Seattle Supercharger", "Search string mismatch."
    print("5. ENTER key clicked. Returned to Navigation with correct query. Passed.")
    
    # Action 5: Navigate to Settings Page
    click_settings_action = {
        "action": "CLICK",
        "target_coordinates": [100, 270],
        "text_value": ""
    }
    success = execute(click_settings_action)
    assert success, "Failed to navigate to Settings."
    assert window.controller.current_page() == "settings", "Should have navigated to 'settings'."
    print("6. Switch to Settings view. Passed.")
    
    # Action 6: SWIPE settings scroll area
    scroll_bar = window.settings_page.scroll_area.verticalScrollBar()
    initial_scroll = scroll_bar.value()
    assert initial_scroll == 0, f"Start scroll must be 0, got {initial_scroll}."
    
    swipe_action = {
        "action": "SWIPE",
        "target_coordinates": [500, 500],
        "text_value": "UP"
    }
    success = execute(swipe_action)
    assert success, "Failed to execute SWIPE action."
    new_scroll = scroll_bar.value()
    assert new_scroll > initial_scroll, f"Scroll area did not scroll. Value: {new_scroll}"
    print(f"7. SWIPE UP (scroll page down) successful. Scroll position moved from {initial_scroll} to {new_scroll}. Passed.")
    print("================================\n")

if __name__ == "__main__":
    test_executor_actions()
