from core.project_paths import get_path
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def scan_files(base_dir: Path) -> set:
    return {
        str(p.relative_to(base_dir)).replace("\\", "/")
        for p in base_dir.rglob("*")
        if p.is_file()
    }


def load_existing_excel(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["filepath", "include", "purpose", "status", "comment"])
    return pd.read_excel(path)


def generate_diff_excel():
    base_dir = get_path("root")
    excel_path = get_path("static", "file_meta.xlsx")
    df_old = load_existing_excel(excel_path)

    files_on_disk = scan_files(base_dir)
    files_in_excel = set(df_old["filepath"]) if not df_old.empty else set()

    new_files = files_on_disk - files_in_excel
    deleted_files = files_in_excel - files_on_disk

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    diff_path = get_path(
        "static", f"file_meta_diff_{timestamp}.xlsx", create=True)

    rows_new = [{"filepath": f, "include": 1, "purpose": "",
                 "status": "", "comment": ""} for f in sorted(new_files)]
    rows_missing = [{"filepath": f, "note": "file missing on disk"}
                    for f in sorted(deleted_files)]

    with pd.ExcelWriter(diff_path, engine="openpyxl") as writer:
        if rows_new:
            pd.DataFrame(rows_new).to_excel(
                writer, sheet_name="new_files", index=False)
        if rows_missing:
            pd.DataFrame(rows_missing).to_excel(
                writer, sheet_name="missing_files", index=False)

    print(f"🧾 Diff-Datei erzeugt: {diff_path.name}")
    if not rows_new and not rows_missing:
        print("🟢 Keine Unterschiede gefunden. Alles aktuell.")


if __name__ == "__main__":
    generate_diff_excel()
