import sys
import yaml
from pathlib import Path

# Dynamisch: Projektbasisverzeichnis zum Suchpfad hinzufügen
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.project_paths import get_path

def scan_files(base_dir: Path) -> list:
    """Gibt alle relativen Dateipfade unterhalb base_dir zurück"""
    return [
        str(p.relative_to(base_dir)).replace("\\", "/")
        for p in base_dir.rglob("*")
        if p.is_file()
    ]


def load_existing_meta(yaml_path: Path) -> dict:
    if not yaml_path.exists():
        return {}
    return yaml.safe_load(yaml_path.read_text(encoding='utf-8')) or {}


def generate_file_meta_yaml():
    base_dir = get_path("root")
    yaml_path = base_dir / "static" / "file_meta.yaml"

    existing = load_existing_meta(yaml_path)
    files = scan_files(base_dir)

    new_meta = {}

    for fpath in files:
        entry = existing.get(fpath, {})
        new_meta[fpath] = {
            "include": entry.get("include", 1),
            "purpose": entry.get("purpose", ""),
            "status": entry.get("status", ""),
            "comment": entry.get("comment", ""),
        }

    yaml_text = yaml.dump(new_meta, allow_unicode=True, sort_keys=True)
    yaml_path.write_text(yaml_text, encoding="utf-8")
    print(f"✅ file_meta.yaml wurde aktualisiert: {yaml_path}")


if __name__ == "__main__":
    generate_file_meta_yaml()
