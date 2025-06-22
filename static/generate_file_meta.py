import sys
import yaml
from pathlib import Path
from datetime import datetime
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.project_paths import get_path


def scan_files(base_dir: Path) -> list:
    return [
        str(p.relative_to(base_dir)).replace("\\", "/")
        for p in base_dir.rglob("*")
        if p.is_file()
    ]


def load_meta(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def backup_file(path: Path):
    if path.exists():
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        backup_path = path.with_name(f"{path.stem}_{timestamp}{path.suffix}")
        shutil.copy(path, backup_path)
        print(f"🛡️ Backup geschrieben: {backup_path.name}")


def update_file_meta():
    base_dir = get_path("root")
    yaml_path = get_path("static", "file_meta.yaml", create=True)

    existing = load_meta(yaml_path)
    files = scan_files(base_dir)

    updated = False

    for f in files:
        if f not in existing:
            existing[f] = {
                "include": 1,
                "purpose": "",
                "status": "",
                "comment": ""
            }
            updated = True

    if updated:
        backup_file(yaml_path)
        yaml_text = yaml.dump(existing, allow_unicode=True, sort_keys=True)
        yaml_path.write_text(yaml_text, encoding="utf-8")
        print("✅ file_meta.yaml wurde ergänzt und gesichert.")
    else:
        print("🟢 Keine neuen Dateien – file_meta.yaml bleibt unverändert.")


if __name__ == "__main__":
    update_file_meta()
