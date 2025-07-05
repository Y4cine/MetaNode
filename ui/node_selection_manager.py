# node_selection_manager.py
"""
Handles node selection logic for MainWindow, delegating to right panel or JSON editor as needed.
"""
from models.node_model import Node
from widgets.json_editor import JsonEditor

def on_node_selected(main_window, node_id):
    from PyQt5.QtWidgets import QMessageBox
    from PyQt5.QtCore import QObject
    from ui.json_editor_manager import JsonEditorManager
    if not JsonEditorManager.try_leave_global_json_editor(main_window.right_area):
        return
    node_wrapper = main_window.model.find_node(node_id)
    if node_wrapper:
        raw_node = node_wrapper.node
        node_obj = Node(raw_node, main_window.meta_schema, main_window.content_schema)
        if isinstance(main_window.right_area, JsonEditor):
            main_window.right_area.set_node(node_obj)
            def on_global_json_saved():
                new_data = main_window.right_area.get_content()
                main_window.model.load_from_dict(new_data)
                main_window.tree_area.load_model(main_window.model)
            main_window.right_area.content_saved.connect(on_global_json_saved)
        else:
            main_window.right_area.switch_node(node_obj, main_window.model, main_window.meta_schema, main_window.content_schema)
    main_window.last_node_id = node_id
