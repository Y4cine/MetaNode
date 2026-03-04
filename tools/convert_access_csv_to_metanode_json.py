#!/usr/bin/env python3
"""Convert Access CSV exports into MetaNode JSON tree format.

Expected source format is the Access export shown in resources/qExport2Word.txt,
including semicolon delimiter, quoted fields and multiline text cells.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


TEXT_FIELDS = [
    ("Content1", "Content 1"),
    ("Content2", "Content 2"),
    ("Content3", "Content 3"),
    ("SensorenAktoren", "Sensoren/Aktoren"),
    ("Screenshot", "Screenshot"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Access CSV export to MetaNode JSON structure."
    )
    parser.add_argument("input_csv", type=Path, help="Path to Access CSV export file")
    parser.add_argument("output_json", type=Path, help="Path to output JSON file")
    parser.add_argument(
        "--input-encoding",
        default="auto",
        help="Input encoding (e.g. cp1252, utf-8, utf-16). Default: auto-detect",
    )
    parser.add_argument(
        "--root-title",
        default="Imported Access Export",
        help="Title for the MetaNode root object",
    )
    return parser.parse_args()


def _normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "").lstrip("\ufeff")


def _looks_mojibake(text: str) -> bool:
    suspicious = ("Ã", "Â", "â€", "â€“", "â€”", "â€œ", "â€\x9d", "â€™")
    return any(token in text for token in suspicious)


def _try_repair_mojibake(text: str) -> str:
    if not _looks_mojibake(text):
        return text

    repaired_variants: List[str] = [text]
    for source_encoding in ("latin-1", "cp1252"):
        try:
            repaired_variants.append(text.encode(source_encoding).decode("utf-8"))
        except UnicodeError:
            continue

    def score(candidate: str) -> int:
        penalty = 0
        penalty += candidate.count("\ufffd") * 100
        penalty += candidate.count("Ã") * 10
        penalty += candidate.count("Â") * 6
        penalty += candidate.count("â€") * 8
        return penalty

    return min(repaired_variants, key=score)


def _decode_auto(raw: bytes) -> str:
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")

    candidate_encodings: List[str] = [
        "utf-8",
        "cp1252",
        "cp1250",
        "latin-1",
        "utf-16-le",
        "utf-16-be",
    ]

    decoded_candidates: List[str] = []
    for encoding in candidate_encodings:
        try:
            decoded_candidates.append(raw.decode(encoding))
        except UnicodeDecodeError:
            continue

    if not decoded_candidates:
        return raw.decode("latin-1", errors="replace")

    def score(text: str) -> int:
        penalty = 0
        penalty += text.count("\ufffd") * 100
        penalty += text.count("\x00") * 30
        penalty += text.count("Ã") * 10
        penalty += text.count("Â") * 6
        penalty += text.count("â€") * 8
        if "id;parentid;" not in text.lower():
            penalty += 200
        return penalty

    return min(decoded_candidates, key=score)


def read_text_with_fallback(path: Path, input_encoding: str = "auto") -> str:
    raw = path.read_bytes()

    if input_encoding and input_encoding.lower() != "auto":
        text = raw.decode(input_encoding)
        return _normalize_text(_try_repair_mojibake(text))

    decoded = _decode_auto(raw)
    return _normalize_text(_try_repair_mojibake(decoded))


def find_header_start(text: str) -> int:
    lines = text.splitlines(keepends=True)
    offset = 0
    for line in lines:
        normalized = line.strip().replace('"', "")
        if normalized.lower().startswith("id;parentid;"):
            return offset
        offset += len(line)
    raise ValueError("CSV header not found. Expected header starting with ID;parentID;...")


def clean_value(value: str | None) -> str:
    if value is None:
        return ""
    cleaned = _normalize_text(value).strip()
    if cleaned in {"-", ""}:
        return ""
    return cleaned


def default_content_metadata() -> Dict[str, str]:
    return {
        "audience": "",
        "lang": "",
        "main": "",
        "status": "",
        "version": "",
    }


def build_contents(row: Dict[str, str]) -> List[Dict]:
    contents: List[Dict] = []
    for field_name, content_title in TEXT_FIELDS:
        text = clean_value(row.get(field_name))
        if not text:
            continue
        contents.append(
            {
                "content_type": "text",
                "title": content_title,
                "data": {"text": text},
                "renderer": "text_blocks",
                "metadata": default_content_metadata(),
            }
        )
    return contents


def build_node(row: Dict[str, str]) -> Dict:
    node_id = clean_value(row.get("ID"))
    if not node_id:
        raise ValueError("Encountered row without ID")

    title = clean_value(row.get("Titel_")) or f"Node {node_id}"
    depth_raw = clean_value(row.get("Depth"))

    metadata = {
        "print": "",
        "status": "",
        "source_pathPos": clean_value(row.get("pathPos")),
        "source_depth": int(depth_raw) if depth_raw.isdigit() else depth_raw,
        "source_db": clean_value(row.get("DB")),
        "source_len_img": clean_value(row.get("len_img")),
    }

    return {
        "id": node_id,
        "title": title,
        "contents": build_contents(row),
        "children": [],
        "metadata": metadata,
    }


def sort_key_for_row(row: Dict[str, str], index: int) -> Tuple[str, int]:
    return clean_value(row.get("pathPos")), index


def parse_rows(text: str) -> List[Dict[str, str]]:
    header_start = find_header_start(text)
    csv_payload = text[header_start:]
    reader = csv.DictReader(io.StringIO(csv_payload), delimiter=";", quotechar='"')
    return [row for row in reader if any((v or "").strip() for v in row.values())]


def convert(rows: List[Dict[str, str]], root_title: str) -> Dict:
    root = {
        "id": "root",
        "title": root_title,
        "contents": [
            {
                "content_type": "text",
                "title": "Import Info",
                "data": {"text": "Imported from Access CSV export."},
                "renderer": "text_blocks",
                "metadata": default_content_metadata(),
            }
        ],
        "children": [],
        "metadata": {"print": "", "status": ""},
    }

    row_with_index = [(idx, row) for idx, row in enumerate(rows)]
    nodes_by_id: Dict[str, Dict] = {}
    row_by_id: Dict[str, Dict[str, str]] = {}

    for _, row in row_with_index:
        node = build_node(row)
        node_id = node["id"]
        nodes_by_id[node_id] = node
        row_by_id[node_id] = row

    children_by_parent: Dict[str, List[Tuple[int, str]]] = {}
    top_level: List[Tuple[int, str]] = []

    for idx, row in row_with_index:
        node_id = clean_value(row.get("ID"))
        parent_id = clean_value(row.get("parentID"))

        if parent_id and parent_id in nodes_by_id:
            children_by_parent.setdefault(parent_id, []).append((idx, node_id))
        else:
            top_level.append((idx, node_id))

    for parent_id, entries in children_by_parent.items():
        parent = nodes_by_id[parent_id]
        entries.sort(key=lambda item: sort_key_for_row(row_by_id[item[1]], item[0]))
        parent["children"] = [nodes_by_id[node_id] for _, node_id in entries]

    top_level.sort(key=lambda item: sort_key_for_row(row_by_id[item[1]], item[0]))
    root["children"] = [nodes_by_id[node_id] for _, node_id in top_level]

    return root


def main() -> int:
    try:
        args = parse_args()

        if not args.input_csv.exists():
            print(f"Input file not found: {args.input_csv}", file=sys.stderr)
            return 2

        text = read_text_with_fallback(args.input_csv, args.input_encoding)
        rows = parse_rows(text)
        if not rows:
            print("No data rows found in CSV export.", file=sys.stderr)
            return 3

        tree = convert(rows, args.root_title)
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(tree, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"Converted {len(rows)} rows -> {args.output_json}")
        return 0
    except UnicodeDecodeError as exc:
        print(f"Encoding error while reading input: {exc}", file=sys.stderr)
        print(
            "Hint: Use --input-encoding cp1252 (or utf-16) if Access exported in a legacy codepage.",
            file=sys.stderr,
        )
        return 4
    except ValueError as exc:
        print(f"Input format error: {exc}", file=sys.stderr)
        print(
            "Hint: If you saw 'SyntaxError: Non-UTF-8 code ... in qExport2Word.txt', "
            "then qExport2Word.txt was likely started as a Python script.",
            file=sys.stderr,
        )
        print(
            "Run this instead:\n"
            "  python tools/convert_access_csv_to_metanode_json.py "
            "resources/qExport2Word.txt resources/qExport2Word.json",
            file=sys.stderr,
        )
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
