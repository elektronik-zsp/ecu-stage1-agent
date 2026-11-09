from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget

from core.mapfinder import MapCandidate


class MapsPanel(QWidget):
    """Displays read-only database matches and heuristic raw-grid candidates."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Map candidates (read-only; heuristic results require expert verification)"))
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Name / source", "Address", "Dimensions", "Confidence", "Status"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._selection_changed)
        layout.addWidget(self.table, 2)
        details = QHBoxLayout()
        self.grid = QTableWidget(0, 0)
        self.grid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.grid.setMaximumHeight(300)
        details.addWidget(self.grid, 2)
        self.info = QTextEdit()
        self.info.setReadOnly(True)
        self.info.setPlaceholderText("Select a candidate to inspect raw uint16 values.")
        details.addWidget(self.info, 1)
        layout.addLayout(details, 2)
        self._data: bytes = b""
        self._candidates: list[MapCandidate] = []

    def set_candidates(self, data: bytes, candidates: list[MapCandidate], database_matches: list[dict] | None = None) -> None:
        self._data = data
        self._candidates = candidates
        self.table.setRowCount(0)
        for match in database_matches or []:
            self._append_row(str(match["name"]), int(match["address"]), int(match["rows"]),
                             int(match["cols"]), 1.0, "SW database")
        for index, candidate in enumerate(candidates):
            self._append_row(f"Heuristic #{index + 1}", candidate.address, candidate.rows,
                             candidate.cols, candidate.confidence, "unverified")
        self.grid.clear()
        self.info.clear()

    def _append_row(self, name: str, address: int, rows: int, cols: int, confidence: float, status: str) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        items = [QTableWidgetItem(name), QTableWidgetItem(f"0x{address:X}"),
                 QTableWidgetItem(f"{rows}x{cols}"), QTableWidgetItem(f"{confidence:.2f}"), QTableWidgetItem(status)]
        color = QColor("#b7e4c7") if confidence >= .85 else QColor("#ffe8a1") if confidence >= .65 else QColor("#f4b4b4")
        items[3].setBackground(color)
        for col, item in enumerate(items):
            self.table.setItem(row, col, item)

    def _selection_changed(self) -> None:
        row = self.table.currentRow()
        database_count = self.table.rowCount() - len(self._candidates)
        index = row - database_count
        if row < 0 or index < 0 or index >= len(self._candidates):
            self.grid.setRowCount(0)
            self.grid.setColumnCount(0)
            self.info.setPlainText("Database match details are read-only and require a verified map definition.")
            return
        candidate = self._candidates[index]
        self.grid.setRowCount(candidate.rows)
        self.grid.setColumnCount(candidate.cols)
        self.grid.setHorizontalHeaderLabels([str(i + 1) for i in range(candidate.cols)])
        self.grid.setVerticalHeaderLabels([str(i + 1) for i in range(candidate.rows)])
        import struct
        fmt = "<H"
        values: list[int] = []
        for r in range(candidate.rows):
            for c in range(candidate.cols):
                pos = candidate.address + 2 * (r * candidate.cols + c)
                value = struct.unpack_from(fmt, self._data, pos)[0]
                values.append(value)
                self.grid.setItem(r, c, QTableWidgetItem(str(value)))
        self.info.setPlainText(
            f"Read-only raw uint16 grid\nAddress: 0x{candidate.address:X}\n"
            f"Confidence: {candidate.confidence:.3f}\n"
            f"Min/max raw: {min(values)}/{max(values)}\n"
            "No physical unit is inferred from heuristic data."
        )
