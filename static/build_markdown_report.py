from core.project_paths import get_path
import sys
import yaml
import hashlib
import json
from pathlib import Path

# Dynamisch: Projektbasisverzeichnis zum Suchpfad hinzufügen
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def build_markdown_report(
    root_dir: Path,
    file_meta: dict,
    current_hashes: dict,
    previous_hashes: dict,
    specs_path: Path,
    todos_path: Path,
    output_path: Path
):
    def read_text_file(path):
        return path.read_text(encoding='utf-8') if path.exists() else ""

    specs_content = read_text_file(specs_path)
    todos_content = read_text_file(todos_path)

    # Änderungserkennung
    new_files = set(current_hashes) - set(previous_hashes)
    deleted_files = set(previous_hashes) - set(current_hashes)
    changed_files = {
        path for path in current_hashes
        if path in previous_hashes and current_hashes[path] != previous_hashes[path]
    }

    # Markdown Aufbau
    lines = []
    lines.append("# 📦 Projektübersicht\n")

    # Kapitel: Specs
    lines.append("## 📘 Specs\n")
    lines.append(specs_content.strip())
    lines.append("")

    # Kapitel: Todos
    lines.append("## ✅ ToDos\n")
    lines.append(todos_content.strip())
    lines.append("")

    # Kapitel: Strukturierte Übersicht
    lines.append("## 🗂 Strukturierte Dateien\n")

    for path_str in sorted(file_meta.keys()):
        meta = file_meta[path_str]
        if meta.get("include", 0) != 1:
            continue

        abs_path = root_dir / path_str
        code_block = ""
        if abs_path.exists():
            try:
                code_block = abs_path.read_text(encoding='utf-8')
            except Exception as e:
                code_block = f"# Fehler beim Lesen: {e}"

        lines.append(f"### `{path_str}`")
        lines.append("")
        lines.append(f"- 📝 Zweck: {meta.get('purpose', '')}")
        lines.append(f"- 📊 Status: {meta.get('status', '')}")
        lines.append(f"- 💬 Kommentar: {meta.get('comment', '')}")
        lines.append("")
        lines.append("```python")
        lines.append(code_block.strip())
        lines.append("```")
        lines.append("")

    # Zusammenfassung als Fußnote
    lines.append("---")
    lines.append(
        f"**Änderungsübersicht:** 🆕 {len(new_files)} neu, 🔁 {len(changed_files)} geändert, ❌ {len(deleted_files)} gelöscht"
    )

    # Schreiben
    output_path.write_text("\n".join(lines), encoding='utf-8')
    print(f"📄 Markdown-Dokument gespeichert unter: {output_path}")


root_dir = get_path("root")
file_meta = {}
current_hashes = {}
previous_hashes = {}
specs_path = get_path("specs", "specs.md")
todos_path = get_path("specs", "todos.md")
output_path = get_path("static", "projektübersicht.md", create=True)

build_markdown_report(
    root_dir,
    file_meta,
    current_hashes,
    previous_hashes,
    specs_path,
    todos_path,
    output_path
)
