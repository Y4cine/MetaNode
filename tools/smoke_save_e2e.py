#!/usr/bin/env python3
"""Headless smoke test for save-as then save flow.

Verifies:
1) First save triggers save-as dialog exactly once.
2) Second save reuses remembered file path (no second dialog).
3) Persisted JSON contains latest edited state.
"""

from pathlib import Path
import json
import tempfile
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtWidgets import QApplication, QFileDialog

from app.shell.wiring import create_main_window


def run() -> int:
    app = QApplication.instance() or QApplication([])
    window = create_main_window()
    old_get_save = QFileDialog.getSaveFileName

    try:
        window.file_manager.new_file()

        out_file = Path(tempfile.mkdtemp()) / "save_e2e.json"
        call_counter = {"count": 0}

        def fake_get_save(*args, **kwargs):
            call_counter["count"] += 1
            return str(out_file), "JSON-Dateien (*.json)"

        QFileDialog.getSaveFileName = fake_get_save

        root = window.model.find_node("root")
        root.title = "First Save"
        window.model.mark_dirty()
        window.file_manager.save_file()

        root = window.model.find_node("root")
        root.title = "Second Save"
        window.model.mark_dirty()
        window.file_manager.save_file()

        data = json.loads(out_file.read_text(encoding="utf-8"))

        if not out_file.exists():
            raise RuntimeError("Output file was not created")
        if data.get("title") != "Second Save":
            raise RuntimeError("Second save did not persist updated data")
        if call_counter["count"] != 1:
            raise RuntimeError(
                f"Save dialog called {call_counter['count']} times, expected 1"
            )

        print("SMOKE_SAVE_E2E_OK")
        return 0
    finally:
        QFileDialog.getSaveFileName = old_get_save
        window.close()
        app.quit()


if __name__ == "__main__":
    raise SystemExit(run())
