from app.features.document import DocumentStore


def _base_tree():
    return {
        "id": "root",
        "title": "Root",
        "metadata": {},
        "contents": [],
        "children": [
            {
                "id": "n1",
                "title": "Node 1",
                "metadata": {},
                "contents": [],
                "children": [],
            }
        ],
    }


def test_insert_child_and_sibling_keep_structure_consistent():
    store = DocumentStore()
    store.load_from_dict(_base_tree())

    child_id = store.insert_child("root", "Child")
    sibling_id = store.insert_sibling_after("n1", "Sibling")

    root_children = store.get_children("root")
    child_ids = [c["id"] for c in root_children]

    assert child_id in child_ids
    assert sibling_id in child_ids
    assert len(set(child_ids)) == len(child_ids)


def test_delete_rename_move_invariants():
    store = DocumentStore()
    store.load_from_dict(_base_tree())
    child_id = store.insert_child("n1", "Inner")

    assert store.rename_node("n1", "Renamed")
    assert store.get_node("n1")["title"] == "Renamed"

    assert store.move_node(child_id, "root", 0)
    root_children = store.get_children("root")
    assert root_children[0]["id"] == child_id

    assert store.delete_node(child_id)
    root_children_after = store.get_children("root")
    assert child_id not in [c["id"] for c in root_children_after]


def test_apply_patch_and_update_content():
    store = DocumentStore()
    store.load_from_dict(_base_tree())

    patch_ok = store.apply_patch(
        "n1",
        {
            "title": "Patched",
            "metadata": {"lang": "DE"},
            "contents": [{"title": "A", "data": {"text": "B"}, "metadata": {}, "renderer": "text_blocks", "content_type": "text"}],
        },
    )
    assert patch_ok
    node = store.get_node("n1")
    assert node["title"] == "Patched"
    assert node["metadata"]["lang"] == "DE"
    assert node["contents"][0]["title"] == "A"

    content_ok = store.update_node_content(
        "n1",
        [{"title": "New", "data": {"text": "X"}, "metadata": {}, "renderer": "text_blocks", "content_type": "text"}],
    )
    assert content_ok
    assert store.get_node("n1")["contents"][0]["title"] == "New"
