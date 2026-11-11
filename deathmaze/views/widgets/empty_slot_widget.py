from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QSize


class EmptySlotWidget(QWidget):
    """Compact visual placeholder widget representing an empty tactical 3x3 slot."""

    def __init__(self, row: int, col: int, parent=None):
        super().__init__(parent)
        self.target_row = row
        self.target_col = col
        self.setFixedSize(QSize(300, 200))
        self.setAcceptDrops(False)

        layout = QVBoxLayout(self)
        label = QLabel(f"<b>Open Spot</b><br>Row {row + 1}, Col {col + 1}")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #888888; font-size: 13px;")
        layout.addWidget(label)

        self.setStyleSheet("""
            EmptySlotWidget {
                border: 2px dashed rgba(150, 150, 150, 120);
                background-color: rgba(200, 200, 200, 15);
                border-radius: 6px;
            }
        """)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        char_name = event.mimeData().text()
        main_window = self.window()
        if hasattr(main_window, "move_character_to_slot"):
            main_window.move_character_to_slot(char_name, self.target_row, self.target_col)
        event.acceptProposedAction()