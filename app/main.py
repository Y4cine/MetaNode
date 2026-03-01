import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication

if __package__ is None or __package__ == "":
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from app.shell.wiring import create_main_window


def main():
    app = QApplication(sys.argv)
    window = create_main_window()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
