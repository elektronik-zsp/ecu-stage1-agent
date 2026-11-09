from __future__ import annotations

import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("ECU Stage 1 Agent")
    app.setOrganizationName("ECU Stage 1 Agent")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
