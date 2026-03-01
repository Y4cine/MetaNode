import json

from app.features.document.tree_data import TreeDataModel


def _tree():
    return {
        "id": "root",
        "title": "Root",
        "metadata": {},
        "contents": [],
        "children": [],
    }


def test_save_as_sets_file_path_and_followup_save_uses_it(tmp_path):
    model = TreeDataModel()
    model.load_from_dict(_tree())

    out_file = tmp_path / "saved.json"
    model.save_to_file(str(out_file))

    assert model.file_path == str(out_file)

    model.find_node("root").title = "Changed"
    model.mark_dirty()
    model.save_to_file()

    with out_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["title"] == "Changed"
