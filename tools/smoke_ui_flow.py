#!/usr/bin/env python3
"""Headless smoke flow: create/select/edit/save/reopen."""

from pathlib import Path
import tempfile
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtWidgets import QApplication

from app.shell.ui.main_window import MainWindow


def run() -> int:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()

    try:
        window.file_manager.new_file()
        window.on_node_selected("root")

        panel = window.right_area.content_stack.panel_views[0]
        editor = panel.content_editor
        editor.title_input.setText("Flow Smoke Title")
        editor.text_edit.setPlainText("Flow Smoke Text")
        panel._write_back_current()

        updated = window.right_area.update_and_return_node()
        node_wrapper = window.model.find_node(updated.id)
        node_wrapper.node.update(updated.to_dict())
        window.model.mark_dirty()

        out_file = Path(tempfile.mkdtemp()) / "flow_smoke.json"
        window.model.save_to_file(str(out_file))

        window.model.load_from_file(str(out_file))
        window.tree_area.load_model(window.model)
        window.on_node_selected("root")

        root = window.model.find_node("root")
        if root is None:
            raise RuntimeError("Root node not found after reload")

        contents = root.node.get("contents", [])
        if not contents:
            raise RuntimeError("No contents found after reload")

        if contents[0].get("title") != "Flow Smoke Title":
            raise RuntimeError("Saved title mismatch after reload")

        if contents[0].get("data", {}).get("text") != "Flow Smoke Text":
            raise RuntimeError("Saved text mismatch after reload")

        print("SMOKE_UI_FLOW_OK")
        return 0
    finally:
        window.close()
        app.quit()


if __name__ == "__main__":
    raise SystemExit(run())
