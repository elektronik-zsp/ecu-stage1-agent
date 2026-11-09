from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QTabWidget, QToolBar, QVBoxLayout, QWidget

from core.diffing import diff_bytes
from core.identify import FileIdentity, identify_dump
from core.mapfinder import MapCandidate
from core.report import NOCHK_WARNING, build_markdown_report
from gui.dialogs.settings import ProfilesDialog, SettingsDialog
from gui.panels.agent_chat import AgentChatPanel
from gui.panels.diff import DiffPanel
from gui.panels.maps import MapsPanel
from gui.panels.project import ProjectPanel
from gui.panels.report import ReportPanel
from gui.panels.stage1 import Stage1Panel
from gui.workers import MapScanWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ECU Stage 1 Agent")
        self.resize(1350, 850)
        self.setAcceptDrops(True)
        self.original: bytes | None = None
        self.working: bytes | None = None
        self.file_path: Path | None = None
        self.identity: FileIdentity | None = None
        self._scan_worker: MapScanWorker | None = None
        self._recent_files: list[str] = []
        self._build_ui()

    def _build_ui(self) -> None:
        self._build_menu()
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)
        open_action = toolbar.addAction("Open")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        save_action = toolbar.addAction("Save copy _NOCHK")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_copy)
        central = QWidget()
        layout = QHBoxLayout(central)
        self.project_panel = ProjectPanel()
        layout.addWidget(self.project_panel, 1)
        self.tabs = QTabWidget()
        self.maps_panel = MapsPanel()
        self.stage1_panel = Stage1Panel()
        self.diff_panel = DiffPanel()
        self.agent_panel = AgentChatPanel()
        self.report_panel = ReportPanel()
        for panel, title in ((self.maps_panel, "Maps"), (self.stage1_panel, "Stage 1"),
                             (self.diff_panel, "Diff"), (self.agent_panel, "Agent AI"),
                             (self.report_panel, "Report")):
            self.tabs.addTab(panel, title)
        layout.addWidget(self.tabs, 4)
        self.setCentralWidget(central)
        self.statusBar().showMessage("Ready — read-only inspection mode")

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("File")
        open_action = QAction("Open file…", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        save_action = QAction("Save copy _NOCHK…", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_copy)
        file_menu.addAction(save_action)
        self.recent_menu = file_menu.addMenu("Recent files")
        tools = self.menuBar().addMenu("Tools")
        scan_action = tools.addAction("Scan maps (read-only)")
        scan_action.triggered.connect(self.scan_maps)
        tools.addAction("Settings…", self.open_settings)
        tools.addAction("Profiles…", self.open_profiles)

    def open_file(self, path: str | None = None) -> None:
        if not isinstance(path, str) or not path:
            path, _ = QFileDialog.getOpenFileName(self, "Open ECU file", "", "ECU files (*.bin *.ori);;All files (*)")
        if not path:
            return
        try:
            data = Path(path).read_bytes()
            self.original = bytes(data)
            self.working = bytes(data)
            self.file_path = Path(path)
            self.identity = identify_dump(self.original, path)
            self.project_panel.set_identity(self.identity)
            self.diff_panel.set_data(self.original, self.working)
            self.report_panel.text.setPlainText(build_markdown_report(self.identity, self.identity.warnings))
            self._remember_file(path)
            self.agent_panel.set_session_dir(Path("sessions") / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
            self.statusBar().showMessage(f"Opened read-only: {path}")
            self.scan_maps()
        except OSError as exc:
            QMessageBox.critical(self, "Open failed", str(exc))

    def _remember_file(self, path: str) -> None:
        normalized = str(Path(path).resolve())
        self._recent_files = [normalized] + [item for item in self._recent_files if item != normalized]
        self._recent_files = self._recent_files[:10]
        self.recent_menu.clear()
        for recent in self._recent_files:
            action = self.recent_menu.addAction(recent)
            action.triggered.connect(lambda checked=False, item=recent: self.open_file(item))

    def scan_maps(self) -> None:
        if self.original is None:
            self.statusBar().showMessage("Open a file before scanning.")
            return
        if self._scan_worker is not None and self._scan_worker.isRunning():
            return
        self.statusBar().showMessage("Scanning read-only map candidates…")
        self._scan_worker = MapScanWorker(self.original)
        self._scan_worker.candidates_ready.connect(self._maps_ready)
        self._scan_worker.failed.connect(lambda error: self.statusBar().showMessage(f"Scan failed: {error}"))
        self._scan_worker.start()

    def _maps_ready(self, candidates: object) -> None:
        assert self.original is not None
        typed = [candidate for candidate in candidates if isinstance(candidate, MapCandidate)]
        self.maps_panel.set_candidates(self.original, typed)
        self.statusBar().showMessage(f"Read-only scan complete: {len(typed)} heuristic candidates; no edits made.")

    def save_copy(self) -> None:
        if self.working is None or self.file_path is None:
            QMessageBox.information(self, "No file", "Open a file first.")
            return
        warning = QMessageBox(self)
        warning.setWindowTitle("Checksum warning")
        warning.setIcon(QMessageBox.Warning)
        warning.setText(NOCHK_WARNING)
        warning.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        warning.setDefaultButton(QMessageBox.Cancel)
        if warning.exec() != QMessageBox.Ok:
            return
        suggested = self.file_path.with_name(f"{self.file_path.stem}_stage1_NOCHK.bin")
        output, _ = QFileDialog.getSaveFileName(self, "Save copy", str(suggested), "Binary files (*.bin)")
        if not output:
            return
        try:
            Path(output).write_bytes(self.working)
            self.statusBar().showMessage("Unmodified copy saved; checksum correction was not performed.")
        except OSError as exc:
            QMessageBox.critical(self, "Save failed", str(exc))

    def open_settings(self) -> None:
        SettingsDialog(self).exec()

    def open_profiles(self) -> None:
        ProfilesDialog(self).exec()

    def _refresh_diff(self) -> None:
        if self.original is not None and self.working is not None:
            report = diff_bytes(self.original, self.working)
            self.diff_panel.set_data(self.original, self.working)
            if report.critical_out_of_bounds:
                self.statusBar().showMessage("Critical: unexpected byte changes detected.")

    def dragEnterEvent(self, event) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:  # noqa: N802
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if Path(path).suffix.lower() in {".bin", ".ori"}:
                self.open_file(path)
                event.acceptProposedAction()
                return
