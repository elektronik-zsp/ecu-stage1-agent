from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from core.report import NOCHK_WARNING


class NOCHKWarningDialog(QMessageBox):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Checksum warning")
        self.setIcon(QMessageBox.Warning)
        self.setText(NOCHK_WARNING)
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
