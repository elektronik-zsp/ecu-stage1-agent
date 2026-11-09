from __future__ import annotations

from PySide6.QtWidgets import QLabel


class MapPlotWidget(QLabel):
    """Placeholder: visualization is withheld until a verified map is selected."""
    def __init__(self, parent=None) -> None:
        super().__init__("No verified physical-unit map available", parent)
        self.setWordWrap(True)
