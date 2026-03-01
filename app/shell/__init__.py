"""Shell facade: composition root and app wiring entry points."""

from app.shell.main_window import MainWindow
from app.shell.wiring import wire_application

__all__ = ["MainWindow", "wire_application"]
