"""Central shell wiring placeholder.

Phase 1 intentionally keeps behavior unchanged; this module provides a stable
location for explicit signal/slot composition in later phases.
"""

from models.node_model import Node

from app.features.document import DocumentStore
from app.shell.main_window import MainWindow


def wire_application(main_window):
    if not isinstance(main_window.model, DocumentStore):
        main_window.model = DocumentStore(main_window.model)

    def show_node_in_inspector(node_id):
        if not node_id:
            return
        node_dict = main_window.model.get_node(node_id)
        if not node_dict:
            if hasattr(main_window.right_area, "load_node"):
                main_window.right_area.load_node(None)
            return
        node_obj = Node(node_dict, main_window.meta_schema, main_window.content_schema)
        if hasattr(main_window.right_area, "switch_node"):
            main_window.right_area.switch_node(
                node_obj,
                main_window.model,
                main_window.meta_schema,
                main_window.content_schema,
            )
        elif hasattr(main_window.right_area, "load_node"):
            main_window.right_area.load_node(node_obj)
        main_window.last_node_id = node_id

    def refresh_tree_and_keep_selection(selected_id=None):
        main_window.tree_area.refresh_from_store(main_window.model)
        if selected_id:
            main_window.tree_area.select_node_by_id(selected_id)

    def handle_insert_child(parent_id, title):
        new_id = main_window.model.insert_child(parent_id, title)
        refresh_tree_and_keep_selection(new_id)
        if new_id:
            show_node_in_inspector(new_id)

    def handle_insert_sibling(node_id, title):
        new_id = main_window.model.insert_sibling_after(node_id, title)
        refresh_tree_and_keep_selection(new_id)
        if new_id:
            show_node_in_inspector(new_id)

    def handle_delete(node_id):
        node = main_window.model.find_node(node_id)
        fallback_id = node.parent.id if node and node.parent else "root"
        if main_window.model.delete_node(node_id):
            refresh_tree_and_keep_selection(fallback_id)
            show_node_in_inspector(fallback_id)

    def handle_rename(node_id, title):
        if main_window.model.rename_node(node_id, title):
            refresh_tree_and_keep_selection(node_id)
            show_node_in_inspector(node_id)

    def handle_move(node_id, new_parent_id, index):
        target_index = None if index < 0 else index
        if main_window.model.move_node(node_id, new_parent_id, target_index):
            refresh_tree_and_keep_selection(node_id)
            show_node_in_inspector(node_id)

    def handle_patch(node_id, patch):
        if main_window.model.apply_patch(node_id, patch):
            refresh_tree_and_keep_selection(node_id)

    try:
        main_window.tree_area.node_selected.disconnect(main_window.on_node_selected)
    except Exception:
        pass

    main_window.tree_area.node_selected.connect(show_node_in_inspector)
    main_window.tree_area.request_insert_child.connect(handle_insert_child)
    main_window.tree_area.request_insert_sibling_after.connect(handle_insert_sibling)
    main_window.tree_area.request_delete.connect(handle_delete)
    main_window.tree_area.request_rename.connect(handle_rename)
    main_window.tree_area.request_move.connect(handle_move)

    if hasattr(main_window.right_area, "request_apply_patch"):
        main_window.right_area.request_apply_patch.connect(handle_patch)

    refresh_tree_and_keep_selection(main_window.last_node_id or "root")
    return main_window


def create_main_window():
    window = MainWindow()
    return wire_application(window)
