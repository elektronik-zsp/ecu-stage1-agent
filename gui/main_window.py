from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QMainWindow, QMessageBox,
                               QTabWidget, QToolBar, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
                               QWidget, QTableWidget, QTableWidgetItem, QTextEdit, QLineEdit,
                               QPushButton, QProgressBar, QStatusBar, QComboBox)
from core.identify import FileIdentity, identify_dump
from core.diffing import diff_bytes
from core.report import build_markdown_report, NOCHK_WARNING
from gui.workers import AgentWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ECU Stage 1 Agent")
        self.resize(1250, 800)
        self.original: bytes | None = None
        self.working: bytes | None = None
        self.file_path: Path | None = None
        self.identity: FileIdentity | None = None
        self._worker: AgentWorker | None = None
        self.setAcceptDrops(True)
        self._create_ui()

    def _create_ui(self) -> None:
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)
        open_action = toolbar.addAction("Open")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        save_action = toolbar.addAction("Save copy _NOCHK")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_copy)
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        root = QWidget()
        layout = QHBoxLayout(root)
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabels(["Project", "Value"])
        self.project_tree.setMinimumWidth(280)
        self.profile = QComboBox()
        self.profile.addItem("No vehicle-specific profile loaded")
        left = QVBoxLayout()
        left.addWidget(QLabel("Project"))
        left.addWidget(QPushButton("Open file (.bin/.ori)", clicked=self.open_file))
        left.addWidget(self.project_tree)
        left.addWidget(QLabel("Engine profile"))
        left.addWidget(self.profile)
        layout.addLayout(left, 1)
        self.tabs = QTabWidget()
        self.tabs.addTab(self._simple_table(["Name", "Address", "Size", "Confidence", "Status"]), "Maps")
        self.tabs.addTab(self._stage_tab(), "Stage 1")
        self.tabs.addTab(self._diff_tab(), "Diff")
        self.tabs.addTab(self._agent_tab(), "Agent AI")
        self.tabs.addTab(self._report_tab(), "Report")
        layout.addWidget(self.tabs, 4)
        self.setCentralWidget(root)

    @staticmethod
    def _simple_table(headers: list[str]) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(table)
        widget.table = table  # type: ignore[attr-defined]
        return widget

    def _stage_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("No real map definitions or tuning recipes are bundled."))
        layout.addWidget(QLabel("Any future edit must pass core safety checks and remain within a declared map."))
        return widget

    def _diff_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.diff_text = QTextEdit()
        self.diff_text.setReadOnly(True)
        layout.addWidget(self.diff_text)
        return widget

    def _agent_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.agent_history = QTextEdit()
        self.agent_history.setReadOnly(True)
        self.agent_entry = QLineEdit()
        self.agent_entry.setPlaceholderText("Ask about the inspection workflow")
        send = QPushButton("Send")
        send.clicked.connect(self.send_prompt)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_agent)
        self.progress = QProgressBar()
        row = QHBoxLayout()
        row.addWidget(self.agent_entry)
        row.addWidget(send)
        row.addWidget(self.cancel_button)
        layout.addWidget(self.agent_history)
        layout.addLayout(row)
        layout.addWidget(self.progress)
        return widget

    def _report_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        layout.addWidget(self.report_text)
        return widget

    def open_file(self, path: str | None = None) -> None:
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Open ECU file", "", "ECU files (*.bin *.ori);;All files (*)")
        if not path:
            return
        try:
            data = Path(path).read_bytes()
            self.original = data
            self.working = data
            self.file_path = Path(path)
            self.identity = identify_dump(data, path)
            self._update_project()
            self._update_views()
            self.status.showMessage(f"Opened read-only original: {path}")
        except OSError as exc:
            QMessageBox.critical(self, "Open failed", str(exc))

    def _update_project(self) -> None:
        assert self.identity is not None
        self.project_tree.clear()
        for key, value in (("Family", self.identity.family), ("SW", self.identity.sw_number or "unknown"),
                           ("HW", self.identity.hw_number or "unknown"), ("Size", str(self.identity.size_bytes)),
                           ("CRC32", self.identity.crc32), ("SHA256", self.identity.sha256),
                           ("Warnings", "; ".join(self.identity.warnings) or "none")):
            QTreeWidgetItem(self.project_tree, [key, value])

    def _update_views(self) -> None:
        if self.identity is None or self.working is None:
            return
        report = diff_bytes(self.original or b"", self.working)
        self.diff_text.setPlainText("No edits. Original file remains unchanged." if not report.regions else
                                    "\n".join(f"0x{r.start:X}: {r.length} bytes; critical={r.critical}" for r in report.regions))
        self.report_text.setPlainText(build_markdown_report(self.identity, list(self.identity.warnings)))

    def save_copy(self) -> None:
        if self.working is None or self.file_path is None:
            QMessageBox.information(self, "No file", "Open a file before saving a copy.")
            return
        answer = QMessageBox.warning(self, "Checksum warning", NOCHK_WARNING,
                                     QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if answer != QMessageBox.Ok:
            return
        suggested = self.file_path.with_name(f"{self.file_path.stem}_stage1_NOCHK.bin")
        path, _ = QFileDialog.getSaveFileName(self, "Save copy", str(suggested), "Binary files (*.bin)")
        if path:
            Path(path).write_bytes(self.working)
            self.status.showMessage("Saved copy; checksum correction was not performed.")

    def send_prompt(self) -> None:
        prompt = self.agent_entry.text().strip()
        if not prompt or (self._worker is not None and self._worker.isRunning()):
            return
        self.agent_history.append(f"You: {prompt}")
        self.agent_entry.clear()
        self.progress.setRange(0, 0)
        self._worker = AgentWorker(prompt)
        self._worker.result.connect(self._agent_done)
        self._worker.failed.connect(self._agent_failed)
        self._worker.finished.connect(lambda: self.progress.setRange(0, 100))
        self._worker.start()

    def _agent_done(self, text: str) -> None:
        self.agent_history.append(f"Agent: {text}")

    def _agent_failed(self, error: str) -> None:
        self.agent_history.append(f"Error: {error}")

    def cancel_agent(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.requestInterruption()
            self.agent_history.append("Cancellation requested; local planner may finish immediately.")

    def dragEnterEvent(self, event) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:  # noqa: N802
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if Path(path).suffix.lower() in {".bin", ".ori"}:
                self.open_file(path)
