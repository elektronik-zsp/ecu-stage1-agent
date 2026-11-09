from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtWidgets import QDialog, QDoubleSpinBox, QFormLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget


class SettingsDialog(QDialog):
    """Local UI preferences; API key storage is intentionally not exposed until API use exists."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.endian = QLineEdit("little")
        self.endian.setReadOnly(True)
        form.addRow("Default byte order (informational)", self.endian)
        self.increase = QDoubleSpinBox()
        self.increase.setRange(1, 20)
        self.increase.setValue(15)
        self.increase.setSuffix("% (display only)")
        self.increase.setEnabled(False)
        form.addRow("Global cap", self.increase)
        layout.addLayout(form)
        layout.addWidget(QWidget())
        close = QPushButton("Close")
        close.clicked.connect(self.accept)
        layout.addWidget(close)


class ProfilesDialog(QDialog):
    """Read-only viewer for bundled illustrative JSON profiles."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Engine profiles (read-only)")
        layout = QVBoxLayout(self)
        self.editor = QLineEdit()
        self.editor.setReadOnly(True)
        layout.addWidget(self.editor)
        profile = Path("data/profiles/generic.json")
        if profile.exists():
            self.editor.setText(json.dumps(json.loads(profile.read_text(encoding="utf-8")), indent=2))
        else:
            self.editor.setText("No profile file found.")
        close = QPushButton("Close")
        close.clicked.connect(self.accept)
        layout.addWidget(close)
