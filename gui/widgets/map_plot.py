from __future__ import annotations

from PySide6.QtWidgets import QLabel


class MapPlotWidget(QLabel):
    """Placeholder visualization; real map data must be explicitly identified first."""

    def __init__(self, parent=None) -> None:
        super().__init__("Select a verified map to display a heatmap", parent)
        self.setMinimumSize(320, 220)
        self.setWordWrap(True)
