from __future__ import annotations

from PySide6.QtCore import QThread, Signal
from core.mapfinder import MapCandidate, find_candidates


class MapScanWorker(QThread):
    candidates_ready = Signal(object)
    failed = Signal(str)

    def __init__(self, data: bytes, endian: str = "little") -> None:
        super().__init__()
        self.data = data
        self.endian = endian

    def run(self) -> None:
        try:
            self.candidates_ready.emit(find_candidates(self.data, self.endian))
        except Exception as exc:
            self.failed.emit(str(exc))


class AgentWorker(QThread):
    result = Signal(str)
    failed = Signal(str)

    def __init__(self, prompt: str) -> None:
        super().__init__()
        self.prompt = prompt

    def run(self) -> None:
        if self.isInterruptionRequested():
            return
        try:
            from core.agent import plan_locally
            self.result.emit(plan_locally(self.prompt))
        except Exception as exc:
            self.failed.emit(str(exc))
