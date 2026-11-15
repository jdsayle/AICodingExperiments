from PySide6.QtWidgets import QWidget, QGridLayout, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from views.widgets.character_card import CharacterCardWidget
from views.widgets.empty_slot_widget import EmptySlotWidget


class ActivePartyDashboardGrid(QWidget):
    """Grid container managing drops, dual-card swaps, and 275ms sliding animations across the 3x3 tactical layout."""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setAcceptDrops(True)
        self.grid = QGridLayout(self)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        source_name = event.mimeData().text()
        pos = event.position().toPoint()
        
        target_widget = None
        target_row, target_col = -1, -1
        source_widget = None

        # Find source widget and target widget/slot under drop coordinates
        for row in range(3):
            for col in range(3):
                item = self.grid.itemAtPosition(row, col)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, CharacterCardWidget) and widget.character.name == source_name:
                        source_widget = widget
                    
                    widget_pos = widget.mapFrom(self, pos)
                    if widget.rect().contains(widget_pos):
                        target_widget = widget
                        target_row, target_col = row, col

        if not source_widget or not target_widget:
            event.ignore()
            return

        target_name = target_widget.character.name if isinstance(target_widget, CharacterCardWidget) else None

        if source_name == target_name:
            event.ignore()
            return

        # --- CASE A: CARD-TO-CARD SWAP (DUAL PARALLEL SLIDING ANIMATION) ---
        if isinstance(target_widget, CharacterCardWidget):
            start_pos_a = source_widget.pos()
            end_pos_a = target_widget.pos()
            
            start_pos_b = target_widget.pos()
            end_pos_b = source_widget.pos()

            # Create visual overlay for Card 1 (Dragged card)
            overlay_a = QLabel(self)
            overlay_a.setPixmap(source_widget.grab())
            overlay_a.setGeometry(start_pos_a.x(), start_pos_a.y(), source_widget.width(), source_widget.height())
            overlay_a.show()

            # Create visual overlay for Card 2 (Target card being displaced)
            overlay_b = QLabel(self)
            overlay_b.setPixmap(target_widget.grab())
            overlay_b.setGeometry(start_pos_b.x(), start_pos_b.y(), target_widget.width(), target_widget.height())
            overlay_b.show()

            # Hide both original cards during flight
            source_widget.hide()
            target_widget.hide()

            # Setup animations for both cards (~275ms cinematic feel)
            anim_a = QPropertyAnimation(overlay_a, b"pos", self)
            anim_a.setDuration(275)
            anim_a.setStartValue(start_pos_a)
            anim_a.setEndValue(end_pos_a)
            anim_a.setEasingCurve(QEasingCurve.OutCubic)

            anim_b = QPropertyAnimation(overlay_b, b"pos", self)
            anim_b.setDuration(275)
            anim_b.setStartValue(start_pos_b)
            anim_b.setEndValue(end_pos_b)
            anim_b.setEasingCurve(QEasingCurve.OutCubic)

            # Group them to run in parallel
            self.anim_group = QParallelAnimationGroup(self)
            self.anim_group.addAnimation(anim_a)
            self.anim_group.addAnimation(anim_b)

            def on_swap_finished():
                overlay_a.deleteLater()
                overlay_b.deleteLater()
                self.main_window.swap_character_positions(source_name, target_name)

            self.anim_group.finished.connect(on_swap_finished)
            self.anim_group.start()

        # --- CASE B: MOVE TO EMPTY SLOT (SINGLE SLIDING ANIMATION) ---
        elif isinstance(target_widget, EmptySlotWidget):
            start_pos = source_widget.pos()
            end_pos = target_widget.pos()

            overlay = QLabel(self)
            overlay.setPixmap(source_widget.grab())
            overlay.setGeometry(start_pos.x(), start_pos.y(), source_widget.width(), source_widget.height())
            overlay.show()

            source_widget.hide()

            self.anim = QPropertyAnimation(overlay, b"pos", self)
            self.anim.setDuration(275)
            self.anim.setStartValue(start_pos)
            self.anim.setEndValue(end_pos)
            self.anim.setEasingCurve(QEasingCurve.OutCubic)

            def on_move_finished():
                overlay.deleteLater()
                self.main_window.move_character_to_slot(source_name, target_row, target_col)

            self.anim.finished.connect(on_move_finished)
            self.anim.start()

        event.acceptProposedAction()