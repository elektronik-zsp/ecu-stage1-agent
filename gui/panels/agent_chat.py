from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QProgressBar, QPushButton, QTextEdit, QVBoxLayout, QWidget

from gui.workers import AgentWorker


class AgentChatPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._worker: AgentWorker | None = None
        self._log_path: Path | None = None
        layout = QVBoxLayout(self)
        self.history = QTextEdit()
        self.history.setReadOnly(True)
        self.history.setPlaceholderText("Local planning helper; no binary editing or API calls are enabled.")
        layout.addWidget(self.history, 1)
        row = QHBoxLayout()
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Ask about the read-only inspection workflow")
        self.send_button = QPushButton("Send")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        row.addWidget(self.entry, 1)
        row.addWidget(self.send_button)
        row.addWidget(self.cancel_button)
        layout.addLayout(row)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)
        self.send_button.clicked.connect(self.send)
        self.entry.returnPressed.connect(self.send)
        self.cancel_button.clicked.connect(self.cancel)

    def set_session_dir(self, session_dir: Path) -> None:
        session_dir.mkdir(parents=True, exist_ok=True)
        self._log_path = session_dir / "log.jsonl"

    def send(self) -> None:
        prompt = self.entry.text().strip()
        if not prompt or (self._worker is not None and self._worker.isRunning()):
            return
        self.entry.clear()
        self.history.append(f"You: {prompt}")
        self._write_log({"type": "user_prompt", "text": prompt})
        self.send_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress.setRange(0, 0)
        self._worker = AgentWorker(prompt)
        self._worker.result.connect(self._on_result)
        self._worker.failed.connect(self._on_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _write_log(self, record: dict) -> None:
        if self._log_path is not None:
            with self._log_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"utc": datetime.now(timezone.utc).isoformat(), **record}, ensure_ascii=False) + "\n")

    def _on_result(self, text: str) -> None:
        self.history.append(f"Agent: {text}")
        self._write_log({"type": "assistant_response", "text": text})

    def _on_error(self, error: str) -> None:
        self.history.append(f"Error: {error}")
        self._write_log({"type": "error", "text": error})

    def _on_finished(self) -> None:
        self.send_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress.setRange(0, 100)
        self.progress.setValue(100)

    def cancel(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.requestInterruption()
