from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout


class ConfirmLowConfidenceDialog(QDialog):
    def __init__(self, parent=None, map_name: str = "", confidence: float = 0.0) -> None:
        super().__init__(parent)
        self.setWindowTitle("Low confidence candidate")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Candidate {map_name!r} has confidence {confidence:.2f}."))
        layout.addWidget(QLabel("It is shown for inspection only; this prototype does not apply binary edits."))
        button = QPushButton("Close")
        button.clicked.connect(self.accept)
        layout.addWidget(button)
