import json
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QAbstractButton, QLineEdit, QScrollArea
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest

def execute(action: dict) -> bool:
    """
    Executes the JSON action received from the planner on the running PySide6 HMI window.
    """
    print(f"\n[EXECUTOR] Executing action: {json.dumps(action)}")

    app = QApplication.instance()
    if not app:
        print("[EXECUTOR] Error: No running QApp instance found.")
        return False

    main_window = None
    for widget in app.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            main_window = widget
            break

    if not main_window:
        print("[EXECUTOR] Error: MainWindow not found.")
        return False

    controller = getattr(main_window, "controller", None)
    if not controller:
        print("[EXECUTOR] Error: UIController reference not found on MainWindow.")
        return False

    action_name = action.get("action", "").upper()
    target_coords = action.get("target_coordinates", [0, 0])
    text_value = action.get("text_value", "")

    if action_name == "CLICK":
        x, y = target_coords[0], target_coords[1]
        state = controller.collect_ui_state()
        
        # Filter visible widgets containing the coordinates
        matching_widgets = []
        for w_info in state["widgets"]:
            if not w_info["visible"]:
                continue
            wx, wy, ww, wh = w_info["geometry"]
            if wx <= x <= wx + ww and wy <= y <= wy + wh:
                matching_widgets.append(w_info)
                
        if not matching_widgets:
            print(f"[EXECUTOR] Error: No visible interactive widget found at [{x}, {y}].")
            return False
            
        # Sort by geometry area (w * h) ascending to find the smallest leaf widget
        matching_widgets.sort(key=lambda w: w["geometry"][2] * w["geometry"][3])
        target_info = matching_widgets[0]
        
        target_widget = main_window.findChild(QWidget, target_info["id"])
        if not target_widget:
            print(f"[EXECUTOR] Error: Widget with id '{target_info['id']}' not found in active window.")
            return False

        print(f"[EXECUTOR] Clicking widget: id={target_widget.objectName()}, type={target_widget.__class__.__name__}")
        
        if isinstance(target_widget, QAbstractButton):
            target_widget.click()
        else:
            target_widget.setFocus()
            local_pos = target_widget.mapFrom(main_window, QPoint(x, y))
            QTest.mouseClick(target_widget, Qt.LeftButton, pos=local_pos)
        
        app.processEvents()
        return True

    elif action_name == "TYPE":
        focused_widget = app.focusWidget()
        if not focused_widget:
            print("[EXECUTOR] Error: No widget is currently focused to receive TYPE action.")
            return False

        if isinstance(focused_widget, QLineEdit):
            print(f"[EXECUTOR] Typing '{text_value}' into focused widget: id={focused_widget.objectName()}")
            focused_widget.setText(text_value)
            focused_widget.textEdited.emit(text_value)
            focused_widget.returnPressed.emit()
            app.processEvents()
            return True
        else:
            print(f"[EXECUTOR] Warning: Focused widget is not a QLineEdit (type={focused_widget.__class__.__name__}).")
            return False

    elif action_name == "SWIPE":
        scroll_area = None
        for sa in main_window.findChildren(QScrollArea):
            if sa.isVisible() and sa.isVisibleTo(main_window):
                scroll_area = sa
                break

        if not scroll_area:
            print("[EXECUTOR] Error: No active QScrollArea found to perform SWIPE action.")
            return False

        v_bar = scroll_area.verticalScrollBar()
        direction = text_value.upper()
        step = 250

        print(f"[EXECUTOR] Performing SWIPE {direction} on scroll area.")
        if "UP" in direction:
            v_bar.setValue(v_bar.value() + step)
        elif "DOWN" in direction:
            v_bar.setValue(v_bar.value() - step)
        else:
            v_bar.setValue(v_bar.value() + step)

        app.processEvents()
        return True

    else:
        print(f"[EXECUTOR] Error: Unknown action type '{action_name}'.")
        return False
