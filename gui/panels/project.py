from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from core.identify import FileIdentity


class ProjectPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Project"))
        self.file_label = QLabel("No file loaded")
        self.file_label.setWordWrap(True)
        layout.addWidget(self.file_label)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Property", "Value"])
        self.tree.setColumnWidth(0, 100)
        layout.addWidget(self.tree, 1)
        layout.addWidget(QLabel("Engine profile"))
        self.profile_combo = QComboBox()
        self.profile_combo.addItem("Generic (illustrative only)", "generic")
        layout.addWidget(self.profile_combo)

    def set_identity(self, identity: FileIdentity) -> None:
        self.file_label.setText(identity.source_name or "Loaded binary")
        self.tree.clear()
        values = (
            ("Family", identity.family), ("SW", identity.sw_number or "unknown"),
            ("HW", identity.hw_number or "unknown"), ("Size", f"{identity.size_bytes:,} bytes"),
            ("Dump type", identity.dump_type), ("CRC32", identity.crc32),
            ("SHA256", identity.sha256),
            ("Warnings", "; ".join(identity.warnings) or "none"),
        )
        for key, value in values:
            QTreeWidgetItem(self.tree, [key, value])
