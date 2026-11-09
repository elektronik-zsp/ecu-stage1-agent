from __future__ import annotations

from PySide6.QtCore import QThread, Signal
from core.agent import plan_locally


class AgentWorker(QThread):
    result = Signal(str)
    failed = Signal(str)

    def __init__(self, prompt: str) -> None:
        super().__init__()
        self.prompt = prompt

    def run(self) -> None:
        try:
            self.result.emit(plan_locally(self.prompt))
        except Exception as exc:  # defensive UI boundary
            self.failed.emit(str(exc))
