from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


class MapTableWidget(QTableWidget):
    """Table for detected, read-only heuristic candidates."""

    def __init__(self, parent=None) -> None:
        super().__init__(0, 5, parent)
        self.setHorizontalHeaderLabels(["Name", "Address", "Dimensions", "Confidence", "Status"])
        self.setEditTriggers(QTableWidget.NoEditTriggers)

    def add_candidate(self, name: str, address: int, rows: int, cols: int, confidence: float) -> None:
        row = self.rowCount()
        self.insertRow(row)
        values = [name, f"0x{address:X}", f"{rows}x{cols}", f"{confidence:.2f}",
                  "high" if confidence >= .85 else "medium" if confidence >= .72 else "low"]
        for col, value in enumerate(values):
            self.setItem(row, col, QTableWidgetItem(value))
        color = "#b7e4c7" if confidence >= .85 else "#ffe8a1" if confidence >= .72 else "#f4b4b4"
        self.item(row, 3).setBackground(color)
