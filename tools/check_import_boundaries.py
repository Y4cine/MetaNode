#!/usr/bin/env python3
"""Checks feature-package import boundaries.

Rules:
- Analyze only modules under app/features/<feature>/.
- Forbidden: cross-feature imports except to app.features.document.
- Allowed from features:
  - app.shared.*
  - app.features.<same_feature>.*
  - app.features.document.*
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
FEATURES_ROOT = ROOT / "app" / "features"


def iter_feature_files() -> Iterable[Path]:
    for file_path in FEATURES_ROOT.rglob("*.py"):
        if file_path.name == "__pycache__":
            continue
        yield file_path


def feature_name_from_path(file_path: Path) -> str:
    return file_path.relative_to(FEATURES_ROOT).parts[0]


def import_to_feature(module_name: str) -> str | None:
    prefix = "app.features."
    if not module_name.startswith(prefix):
        return None
    remainder = module_name[len(prefix) :]
    if not remainder:
        return None
    return remainder.split(".")[0]


def check_file(file_path: Path) -> List[Tuple[int, str, str]]:
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))
    own_feature = feature_name_from_path(file_path)
    violations: List[Tuple[int, str, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name
                target_feature = import_to_feature(module_name)
                if not target_feature:
                    continue
                if target_feature in {own_feature, "document"}:
                    continue
                violations.append(
                    (
                        node.lineno,
                        module_name,
                        f"Feature '{own_feature}' darf '{module_name}' nicht importieren.",
                    )
                )
        elif isinstance(node, ast.ImportFrom):
            if node.level != 0 or not node.module:
                continue
            module_name = node.module
            if module_name.startswith("app.shared"):
                continue
            target_feature = import_to_feature(module_name)
            if not target_feature:
                continue
            if target_feature in {own_feature, "document"}:
                continue
            violations.append(
                (
                    node.lineno,
                    module_name,
                    f"Feature '{own_feature}' darf '{module_name}' nicht importieren.",
                )
            )

    return violations


def main() -> int:
    all_violations: List[Tuple[Path, int, str, str]] = []

    for file_path in iter_feature_files():
        violations = check_file(file_path)
        for line, module_name, message in violations:
            all_violations.append((file_path, line, module_name, message))

    if all_violations:
        print("Import-Boundary-Verletzungen gefunden:")
        for file_path, line, _module_name, message in all_violations:
            rel = file_path.relative_to(ROOT)
            print(f"- {rel}:{line}: {message}")
        return 1

    print("OK: Keine verbotenen Cross-Feature-Imports gefunden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
