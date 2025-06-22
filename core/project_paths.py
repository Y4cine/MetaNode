from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

FOLDERS = {
    "root": BASE_DIR,
    "resources": BASE_DIR / "resources",
    "schemas": BASE_DIR / "schemas",
    "static": BASE_DIR / "static",
    "specs": BASE_DIR / "specs",
    "utils": BASE_DIR / "utils",
    "icons": BASE_DIR / "resources" / "icons",
}


def get_path(folder: str, filename: str = None, create: bool = False) -> Path:
    """
    Gibt Pfad zum Ordner oder zu einer Datei im Ordner zurück.
    
    :param folder: Einer der Keys aus FOLDERS
    :param filename: Optionaler Dateiname (relativ zu diesem Ordner)
    :param create: Wenn True, wird der Ordner (ggf. samt Unterordnern) angelegt
    :return: Path-Objekt
    """
    if folder not in FOLDERS:
        raise ValueError(f"Unknown folder alias '{folder}'. Valid: {list(FOLDERS.keys())}")

    path = FOLDERS[folder]
    
    if filename:
        path = path / filename

    if create:
        path.parent.mkdir(parents=True, exist_ok=True)

    return path


def file_exists(folder: str, filename: str) -> bool:
    """Prüft, ob Datei existiert."""
    return get_path(folder, filename).exists()
