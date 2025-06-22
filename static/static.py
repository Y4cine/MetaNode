
import os
from core.project_paths import resource_path, exists
# Nach dem Kernel-Reset: Erneut das Skript zur Ordnerstruktur-Erstellung ausführen

struktur_definition = """
main.py,1,Startpunkt
ui/ui_main_window.py,1,Hauptfenster
ui/ui_tree_view.py,1,Baumdarstellung
models/node_model.py,1,Datenmodell Knoten
models/content_model.py,1,Datenmodell Content
models/metadata_model.py,0,liegt in static_data.txt
widgets/content_editor_widget.py,1,Editor für Content
widgets/metadata_widget.py,1,Metadateneditor
widgets/content_list_widget.py,1,Content-Liste
core/undo_manager.py,1,Undo-System
core/schema_registry.py,1,Schema-Lader
resources/beispielbaum.json,1,Beispielstruktur
specs/_project_spec.md,1,Projektbeschreibung
specs/chatgpt_ignore.txt,1,Ignorierliste
specs/project_dump.txt,1,GPT-Exportstruktur
static/static_data.txt,1,Ausgelagerte Daten
"""


base_dir = "/mnt/data/TreeEditor"  # Zieldirectory

created_files = []

for line in struktur_definition.strip().splitlines():
    if not line.strip() or line.strip().startswith("#"):
        continue
    parts = line.strip().split(",")
    if len(parts) < 2:
        continue
    rel_path, export_flag = parts[0].strip(), parts[1].strip()
    comment = parts[2].strip() if len(parts) > 2 else ""
    if export_flag != "1":
        continue

    abs_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    if not os.path.exists(abs_path):
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(f"# {rel_path} - {comment}\n")
        created_files.append(rel_path)


