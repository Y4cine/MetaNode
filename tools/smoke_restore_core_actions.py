#!/usr/bin/env python3
"""Headless smoke for restored core actions.

Checks:
- selection sync
- insert child + sibling
- rename
- delete
- move
- edit content
- save/reload
"""

from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtWidgets import QApplication, QInputDialog

from app.shell.wiring import create_main_window


def _process(app):
    app.processEvents()


def run() -> int:
    app = QApplication.instance() or QApplication([])
    window = create_main_window()

    names = iter(["Child A", "Sibling B", "Renamed B"])
    original_get_text = QInputDialog.getText

    def fake_get_text(*args, **kwargs):
        try:
            return next(names), True
        except StopIteration:
            return "Fallback", True

    QInputDialog.getText = fake_get_text

    try:
        window.file_manager.new_file()
        _process(app)

        window.tree_area.select_node_by_id("root")
        _process(app)
        root_item = window.tree_area.currentItem()
        if root_item is None:
            raise RuntimeError("Root item not selected")

        window.tree_area.add_child_to(root_item)
        _process(app)

        root_children = window.model.get_children("root")
        if len(root_children) < 1:
            raise RuntimeError("Child creation failed")
        child_a_id = root_children[0]["id"]

        window.tree_area.select_node_by_id(child_a_id)
        _process(app)
        if not hasattr(window.right_area, "_node") or window.right_area._node is None:
            raise RuntimeError("Inspector did not receive selected node")
        if window.right_area._node.id != child_a_id:
            raise RuntimeError("Selection sync failed")

        child_item = window.tree_area.currentItem()
        window.tree_area.add_sibling_after(child_item)
        _process(app)

        root_children = window.model.get_children("root")
        if len(root_children) < 2:
            raise RuntimeError("Sibling creation failed")
        sibling_b_id = root_children[1]["id"]

        window.tree_area.select_node_by_id(sibling_b_id)
        _process(app)
        sibling_item = window.tree_area.currentItem()
        window.tree_area.rename_item(sibling_item)
        _process(app)
        if window.model.get_node(sibling_b_id)["title"] != "Renamed B":
            raise RuntimeError("Rename failed")

        window.tree_area.delete_item(window.tree_area.currentItem())
        _process(app)
        if window.model.get_node(sibling_b_id) is not None:
            raise RuntimeError("Delete failed")

        child_a_id = window.model.get_children("root")[0]["id"]
        new_child_id = window.model.insert_child("root", "Movable")
        _process(app)
        if not new_child_id:
            raise RuntimeError("Preparation for move failed")

        window.tree_area.request_move.emit(new_child_id, child_a_id, -1)
        _process(app)
        moved_children = window.model.get_children(child_a_id)
        if new_child_id not in [c["id"] for c in moved_children]:
            raise RuntimeError("Move failed")

        window.tree_area.select_node_by_id(child_a_id)
        _process(app)
        panel = window.right_area.content_stack.panel_views[0]
        editor = panel.content_editor
        editor.title_input.setText("Edited Title")
        editor.text_edit.setPlainText("Edited Text")
        panel._write_back_current()
        _process(app)

        out_file = Path(tempfile.mkdtemp()) / "restore_smoke.json"
        window.model.save_to_file(str(out_file))
        window.model.load_from_file(str(out_file))
        _process(app)

        reloaded_child = window.model.get_node(child_a_id)
        if reloaded_child is None:
            raise RuntimeError("Reload failed")
        if not reloaded_child.get("contents"):
            raise RuntimeError("Content missing after reload")

        print("SMOKE_RESTORE_CORE_ACTIONS_OK")
        return 0
    finally:
        QInputDialog.getText = original_get_text
        window.close()
        app.quit()


if __name__ == "__main__":
    raise SystemExit(run())
