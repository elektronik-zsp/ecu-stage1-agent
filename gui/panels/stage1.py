from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTableWidget, QVBoxLayout, QWidget


class Stage1Panel(QWidget):
    """Read-only planning placeholder; no calibration edits are enabled."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Stage 1 planning is disabled in this prototype. No calibration values or map edits are generated.\n"
            "Only verified map definitions and qualified vehicle-specific validation could support a future workflow."
        ))
        self.steps = QTableWidget(0, 4)
        self.steps.setHorizontalHeaderLabels(["Map", "Operation", "Proposed value", "Profile limit"])
        self.steps.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.steps)
