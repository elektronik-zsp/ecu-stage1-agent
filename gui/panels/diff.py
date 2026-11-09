from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from gui.widgets.hex_view import HexViewWidget


class DiffPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.summary = QLabel("Open a file to compare original and working copy.")
        layout.addWidget(self.summary)
        self.hex = HexViewWidget()
        layout.addWidget(self.hex, 1)

    def set_data(self, original: bytes, modified: bytes) -> None:
        if original == modified:
            self.summary.setText("No changes. Original is read-only; working copy is unchanged.")
        else:
            self.summary.setText("Difference detected. Any undeclared byte changes are critical.")
        self.hex.set_comparison(original, modified)
