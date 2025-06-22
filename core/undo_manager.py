import copy
from typing import Any, List


class UndoManager:
    def __init__(self):
        self.stack: List[Any] = []
        self.index: int = -1

    def push(self, snapshot: Any):
        # entferne Redo-Pfad
        self.stack = self.stack[:self.index + 1]
        self.stack.append(copy.deepcopy(snapshot))
        self.index += 1

    def can_undo(self) -> bool:
        return self.index > 0

    def can_redo(self) -> bool:
        return self.index < len(self.stack) - 1

    def undo(self) -> Any:
        if self.can_undo():
            self.index -= 1
            return copy.deepcopy(self.stack[self.index])
        return None

    def redo(self) -> Any:
        if self.can_redo():
            self.index += 1
            return copy.deepcopy(self.stack[self.index])
        return None

    def reset(self):
        self.stack.clear()
        self.index = -1
