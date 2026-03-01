from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_main_module_imports():
    import main

    assert hasattr(main, "main")


def test_minimal_model_roundtrip(tmp_path: Path):
    from models.tree_data import TreeDataModel

    model = TreeDataModel()
    model.load_from_dict(
        {
            "id": "root",
            "title": "Neue Struktur",
            "children": [],
            "metadata": {},
            "contents": [
                {
                    "content_type": "text",
                    "title": "Smoke Title",
                    "renderer": "text_blocks",
                    "data": {"text": "Smoke Text"},
                    "metadata": {},
                }
            ],
        }
    )

    target_file = tmp_path / "smoke_doc.json"
    model.save_to_file(str(target_file))
    model.load_from_file(str(target_file))

    root = model.find_node("root")
    assert root is not None
    contents = root.node.get("contents", [])
    assert contents
    assert contents[0]["title"] == "Smoke Title"
    assert contents[0]["data"]["text"] == "Smoke Text"
