from __future__ import annotations

from PySide6.QtWidgets import QTextEdit


class HexViewWidget(QTextEdit):
    """Read-only side-by-side byte comparison with changed bytes marked."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)

    def set_bytes(self, data: bytes, start: int = 0, length: int = 256) -> None:
        self.set_comparison(data, data, start, length)

    def set_comparison(self, original: bytes, modified: bytes, start: int = 0, length: int = 256) -> None:
        end = min(max(len(original), len(modified)), start + length)
        lines: list[str] = []
        for base in range(start, end, 16):
            old = original[base:base + 16]
            new = modified[base:base + 16]
            old_text = " ".join(f"{value:02X}" for value in old)
            new_text = " ".join(f"{value:02X}" for value in new)
            marker = "  < changed" if old != new else ""
            lines.append(f"{base:08X}: {old_text:<47} | {new_text}{marker}")
        self.setPlainText("ORIGINAL                                         | WORKING COPY\n" + "\n".join(lines))
