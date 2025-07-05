# undo_manager_helper.py
"""
Provides combined undo/redo logic for MainWindow, delegating to right panel or model as needed.
"""

def do_combined_undo(main_window):
    if hasattr(main_window.right_area, 'undo') and main_window.right_area.undo.can_undo():
        main_window.right_area.do_undo()
    elif main_window.model.can_undo():
        main_window.model.undo()
        main_window.tree_area.load_model(main_window.model)

def do_combined_redo(main_window):
    if hasattr(main_window.right_area, 'undo') and main_window.right_area.undo.can_redo():
        main_window.right_area.do_redo()
    elif main_window.model.can_redo():
        main_window.model.redo()
        main_window.tree_area.load_model(main_window.model)
        if getattr(main_window, 'last_node_id', None):
            main_window.tree_area.select_node_by_id(main_window.last_node_id)
