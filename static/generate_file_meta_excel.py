import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.project_paths import get_path

EXCEL_FILENAME = "file_meta.xlsx"

def scan_files(base_dir: Path) -> list:
    return [
        str(p.relative_to(base_dir)).replace("\\", "/")
        for p in base_dir.rglob("*")
        if p.is_file()
    ]

def load_existing_excel(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["filepath", "include", "purpose", "status", "comment"])
    return pd.read_excel(path)

def backup_file(path: Path):
    if path.exists():
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
        path.rename(path.with_name(f"{path.stem}_{ts}{path.suffix}"))
        print(f"🛡️ Backup erstellt: {path.stem}_{ts}{path.suffix}")

def update_file_meta_excel():
    base_dir = get_path("root")
    file_list = scan_files(base_dir)
    excel_path = get_path("static", EXCEL_FILENAME, create=True)

    df_old = load_existing_excel(excel_path)
    existing_paths = set(df_old["filepath"]) if not df_old.empty else set()

    new_rows = []

    for fpath in file_list:
        if fpath not in existing_paths:
            new_rows.append({
                "filepath": fpath,
                "include": 1,
                "purpose": "",
                "status": "",
                "comment": ""
            })

    if new_rows:
        backup_file(excel_path)
        df_new = pd.concat([df_old, pd.DataFrame(new_rows)], ignore_index=True)
        df_new.to_excel(excel_path, index=False)
        print(f"✅ Neue Dateien ergänzt: {len(new_rows)} – Datei gespeichert: {EXCEL_FILENAME}")
    else:
        print("🟢 Keine neuen Dateien. Alles aktuell.")


if __name__ == "__main__":
    update_file_meta_excel()
