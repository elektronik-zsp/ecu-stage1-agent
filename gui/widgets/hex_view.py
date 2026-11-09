from __future__ import annotations

from PySide6.QtWidgets import QTextEdit


class HexViewWidget(QTextEdit):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)

    def set_bytes(self, data: bytes, start: int = 0, length: int = 256) -> None:
        chunk = data[start:start + length]
        lines = [f"{start + offset:08X}: " + " ".join(f"{byte:02X}" for byte in chunk[offset:offset + 16])
                 for offset in range(0, len(chunk), 16)]
        self.setPlainText("\n".join(lines))
