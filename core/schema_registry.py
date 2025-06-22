# schema_registry.py
import json
import os
from typing import Dict
from core.project_paths import get_path, file_exists


class SchemaRegistry:
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.cache: Dict[str, Dict] = {}

    def load_schema(self, name: str) -> Dict:
        if name in self.cache:
            return self.cache[name]
        filename = f"{name}.json"
        path = get_path("schemas", filename)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.cache[name] = data
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema not found: {path}")

    def get(self, name: str) -> Dict:
        """Alias für load_schema."""
        return self.load_schema(name)
