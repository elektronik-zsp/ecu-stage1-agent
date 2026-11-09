from __future__ import annotations

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


def test_main_window_smoke(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.windowTitle() == "ECU Stage 1 Agent"
    assert window.tabs.count() == 5
