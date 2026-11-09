from __future__ import annotations

from PySide6.QtWidgets import QMessageBox
from gui.main_window import MainWindow


def test_main_window_has_all_tabs(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.tabs.count() == 5
    assert [window.tabs.tabText(i) for i in range(5)] == ["Maps", "Stage 1", "Diff", "Agent AI", "Report"]


def test_open_synthetic_file_updates_identity(qtbot, tmp_path) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    path = tmp_path / "sample.bin"
    path.write_bytes(b"EDC17 " + bytes(256))
    window.open_file(str(path))
    assert window.identity is not None
    assert window.identity.size_bytes == 262
    assert window.original == window.working
    assert window.project_panel.file_label.text() == "sample.bin"
    if window._scan_worker is not None:
        qtbot.waitUntil(lambda: not window._scan_worker.isRunning(), timeout=10000)
