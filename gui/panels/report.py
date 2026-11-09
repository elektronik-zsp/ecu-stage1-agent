from __future__ import annotations

from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget


class ReportPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text, 1)
        row = QHBoxLayout()
        self.save_button = QPushButton("Save report")
        self.copy_button = QPushButton("Copy report")
        row.addWidget(self.save_button)
        row.addWidget(self.copy_button)
        layout.addLayout(row)
        self.save_button.clicked.connect(self.save_report)
        self.copy_button.clicked.connect(self.copy_report)

    def save_report(self) -> None:
        path, selected_filter = QFileDialog.getSaveFileName(self, "Save report", "ecu_report.md", "Markdown (*.md);;HTML (*.html)")
        if not path:
            return
        content = self.text.toPlainText()
        if path.lower().endswith(".html"):
            from core.report import build_html_report
            content = build_html_report(content)
        try:
            with open(path, "w", encoding="utf-8") as stream:
                stream.write(content)
        except OSError as exc:
            QMessageBox.critical(self, "Save failed", str(exc))

    def copy_report(self) -> None:
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.text.toPlainText())
