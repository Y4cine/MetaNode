# core/command_registry.py
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon, QKeySequence

# Zentrale Registry
_registry = {}

def register_command(
    id: str,
    label: str,
    callback=None,
    shortcut: str = None,
    icon: str = None,
    tooltip: str = None,
    checkable: bool = False
):
    """
    Registriert eine neue Aktion. Kann mehrfach aufgerufen werden – letzter Eintrag gewinnt.
    """
    action = QAction(label)
    if shortcut:
        action.setShortcut(QKeySequence(shortcut))
    if icon:
        action.setIcon(QIcon(icon))
    if tooltip:
        action.setToolTip(tooltip)
    if callback:
        action.triggered.connect(callback)
    action.setCheckable(checkable)

    _registry[id] = action


def get_action(id: str) -> QAction:
    return _registry.get(id)


def all_actions() -> dict:
    """Gibt alle registrierten Aktionen zurück (für Debugging oder Toolbar-Bau)."""
    return dict(_registry)
