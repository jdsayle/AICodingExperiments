from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QTabWidget, QScrollArea, QLabel, QMessageBox, QGridLayout, QDialog
)
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QTimer
from app.services.character_manager import CharacterManager
from app.services.rules_engine import RulesEngine
from views.widgets.character_card import CharacterCardWidget
from views.widgets.empty_slot_widget import EmptySlotWidget
from views.widgets.create_character_tab import CreateCharacterTab
from views.widgets.character_inspector import CharacterInspectorWidget
from views.widgets.item_picker_dialog import AddItemDialog
from views.widgets.add_charmed_dialog import AddCharmedDialog


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

        if isinstance(target_widget, CharacterCardWidget):
            start_pos_a = source_widget.pos()
            end_pos_a = target_widget.pos()

            start_pos_b = target_widget.pos()
            end_pos_b = source_widget.pos()

            overlay_a = QLabel(self)
            overlay_a.setPixmap(source_widget.grab())
            overlay_a.setGeometry(start_pos_a.x(), start_pos_a.y(), source_widget.width(), source_widget.height())
            overlay_a.show()

            overlay_b = QLabel(self)
            overlay_b.setPixmap(target_widget.grab())
            overlay_b.setGeometry(start_pos_b.x(), start_pos_b.y(), target_widget.width(), target_widget.height())
            overlay_b.show()

            source_widget.hide()
            target_widget.hide()

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

            self.anim_group = QParallelAnimationGroup(self)
            self.anim_group.addAnimation(anim_a)
            self.anim_group.addAnimation(anim_b)

            def on_swap_finished():
                overlay_a.deleteLater()
                overlay_b.deleteLater()
                self.main_window.swap_character_positions(source_name, target_name)

            self.anim_group.finished.connect(on_swap_finished)
            self.anim_group.start()

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


class MainWindow(QMainWindow):
    """Main window integrating split ACTIVE / TAVERN sidebar and right tabbed workspace."""

    def __init__(self, manager: CharacterManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("DeathMaze Deluxe - Desktop Manager")
        self.resize(1150, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- LEFT SIDEBAR (ACTIVE & TAVERN/TOWN) ---
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_widget.setFixedWidth(280)

        sidebar_layout.addWidget(QLabel("<b>ACTIVE PARTY</b>"))
        self.active_list = QListWidget()
        self.active_list.itemClicked.connect(self._on_list_item_clicked)
        sidebar_layout.addWidget(self.active_list)

        self.toggle_to_tavern_btn = QPushButton("↓ Move to Tavern / Town")
        self.toggle_to_tavern_btn.clicked.connect(self._move_to_tavern)
        sidebar_layout.addWidget(self.toggle_to_tavern_btn)

        self.add_charmed_btn = QPushButton("+ Add Charmed")
        self.add_charmed_btn.clicked.connect(self._on_add_charmed_clicked)
        sidebar_layout.addWidget(self.add_charmed_btn)

        self.leave_maze_btn = QPushButton("Leave Maze")
        self.leave_maze_btn.clicked.connect(self._on_leave_maze_clicked)
        sidebar_layout.addWidget(self.leave_maze_btn)

        sidebar_layout.addWidget(QLabel("<b>TAVERN / TOWN</b>"))
        self.tavern_list = QListWidget()
        self.tavern_list.itemClicked.connect(self._on_list_item_clicked)
        sidebar_layout.addWidget(self.tavern_list)

        self.toggle_to_active_btn = QPushButton("↑ Recruit to Active Party")
        self.toggle_to_active_btn.clicked.connect(self._move_to_active)
        sidebar_layout.addWidget(self.toggle_to_active_btn)

        btn_layout = QHBoxLayout()
        self.create_btn = QPushButton("+ Create")
        self.delete_btn = QPushButton("- Delete")
        self.create_btn.clicked.connect(self.open_create_character_tab)
        self.delete_btn.clicked.connect(self._delete_selected_character)

        btn_layout.addWidget(self.create_btn)
        btn_layout.addWidget(self.delete_btn)
        sidebar_layout.addLayout(btn_layout)

        main_layout.addWidget(sidebar_widget)

        # --- RIGHT TABBED WORKSPACE ---
        self.tabs = QTabWidget()

        self.dashboard_tab = QWidget()
        self.dashboard_scroll = QScrollArea()
        self.dashboard_scroll.setWidgetResizable(True)

        self.dashboard_container = ActivePartyDashboardGrid(self)
        self.dashboard_grid = self.dashboard_container.grid
        self.dashboard_scroll.setWidget(self.dashboard_container)

        dash_layout = QVBoxLayout(self.dashboard_tab)
        dash_layout.addWidget(self.dashboard_scroll)
        self.tabs.addTab(self.dashboard_tab, "Active Party Dashboard")

        self.inspector_tab = QWidget()
        self.inspector_layout = QVBoxLayout(self.inspector_tab)
        self.inspector_widget = CharacterInspectorWidget(self.manager)
        self.inspector_layout.addWidget(self.inspector_widget)
        self.tabs.addTab(self.inspector_tab, "Detailed Inspector")

        main_layout.addWidget(self.tabs)

        self.refresh_character_lists()
        self.showNormal()

    def _on_add_charmed_clicked(self) -> None:
        all_chars = self.manager.list_characters()
        active_party = [c for c in all_chars if getattr(c, "is_in_party", False)]
        if len(active_party) >= 9:
            QMessageBox.warning(
                self,
                "Party Full",
                "The party is full (maximum of 9 total party members between PCs and NPCs).",
            )
            return

        dialog = AddCharmedDialog(all_chars, parent=self)
        if dialog.exec() == QDialog.Accepted and dialog.created_npc is not None:
            latest_chars = self.manager.list_characters()
            latest_active = [c for c in latest_chars if getattr(c, "is_in_party", False)]
            if len(latest_active) >= 9:
                QMessageBox.warning(
                    self,
                    "Party Full",
                    "The party is full (maximum of 9 total party members between PCs and NPCs).",
                )
                return

            open_slot = RulesEngine.get_first_open_party_slot(
                latest_active,
                exclude_name=dialog.created_npc.name,
            )
            if open_slot is None:
                QMessageBox.warning(
                    self,
                    "Party Full",
                    "The party is full (maximum of 9 total party members between PCs and NPCs).",
                )
                return

            dialog.created_npc.combat_row, dialog.created_npc.combat_col = open_slot
            self.manager.repository.save(dialog.created_npc)
            self.refresh_character_lists()

    def _on_charm_broken_requested(self, npc_name: str) -> None:
        self.manager.delete_character(npc_name)
        if (
            self.inspector_widget.current_character is not None
            and self.inspector_widget.current_character.name == npc_name
        ):
            self.inspector_widget.clear()
        self.refresh_character_lists()

    def _on_leave_maze_clicked(self) -> None:
        all_chars = self.manager.list_characters()
        outcome = RulesEngine.leave_maze(all_chars)
        for char in outcome["reset"]:
            self.manager.repository.save(char)
        for npc in outcome["removed_npcs"]:
            self.manager.delete_character(npc.name)
        self.refresh_character_lists()
        if self.inspector_widget.current_character:
            refreshed = self.manager.get_character(self.inspector_widget.current_character.name)
            if refreshed:
                self.inspector_widget.set_character(refreshed)
            else:
                self.inspector_widget.clear()

    def _on_card_add_item_requested(self, char_name: str) -> None:
            char = self.manager.get_character(char_name)
            if not char:
                QMessageBox.warning(self, "Character Not Found", f"Could not find character '{char_name}'.")
                return

            party = [c for c in self.manager.list_characters() if getattr(c, "is_in_party", False)]
            dialog = AddItemDialog(char, party=party, parent=self)
            if dialog.exec() == QDialog.Accepted and dialog.selected_definition is not None:
                try:
                    RulesEngine.grant_item(char, dialog.selected_definition, party=party)
                    self.manager.repository.save(char)
                except ValueError as e:
                    QMessageBox.warning(self, "Cannot Add Item", str(e))
                    return
                except Exception as e:
                    QMessageBox.critical(self, "Save Error", f"Failed to save '{char.name}' after granting item: {e}")
                    return

                if (
                    self.inspector_widget.current_character is not None
                    and self.inspector_widget.current_character.name == char.name
                ):
                    refreshed = self.manager.get_character(char.name) or char
                    self.inspector_widget.set_character(refreshed)

                QTimer.singleShot(0, self.refresh_character_lists)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
                event.accept()
                return
        super().keyPressEvent(event)

    def refresh_character_lists(self) -> None:
        self.active_list.clear()
        self.tavern_list.clear()
        characters = self.manager.list_characters()

        active_characters = []
        for char in characters:
            role_tag = "[NPC]" if char.is_npc else "[PC]"
            item = QListWidgetItem(f"{role_tag} {char.name} ({char.class_type.name.replace('_', ' ').title()})")
            item.setData(Qt.UserRole, char.name)
            if char.is_in_party:
                self.active_list.addItem(item)
                active_characters.append(char)
            else:
                self.tavern_list.addItem(item)

        while self.dashboard_grid.count():
            item = self.dashboard_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        occupied_slots = {}
        unassigned = []

        for char in active_characters:
            if 0 <= char.combat_row < 3 and 0 <= char.combat_col < 3:
                key = (char.combat_row, char.combat_col)
                if key not in occupied_slots:
                    occupied_slots[key] = char
                else:
                    unassigned.append(char)
            else:
                unassigned.append(char)

        for char in unassigned:
            placed = False
            for r in range(3):
                for c in range(3):
                    if (r, c) not in occupied_slots:
                        occupied_slots[(r, c)] = char
                        char.combat_row = r
                        char.combat_col = c
                        self.manager.repository.save(char)
                        placed = True
                        break
                if placed:
                    break

        for row in range(3):
            for col in range(3):
                if (row, col) in occupied_slots:
                    char = occupied_slots[(row, col)]
                    card = CharacterCardWidget(char)
                    card.inspect_requested.connect(self._inspect_character_by_name)
                    card.add_item_requested.connect(self._on_card_add_item_requested)
                    card.charm_broken_requested.connect(self._on_charm_broken_requested)
                    self.dashboard_grid.addWidget(card, row, col)
                else:
                    empty_slot = EmptySlotWidget(row, col)
                    self.dashboard_grid.addWidget(empty_slot, row, col)

        self.dashboard_grid.setRowStretch(3, 1)
        self.dashboard_grid.setColumnStretch(3, 1)

    def swap_character_positions(self, name_a: str, name_b: str) -> None:
        char_a = self.manager.get_character(name_a)
        char_b = self.manager.get_character(name_b)
        if not char_a or not char_b:
            return

        temp_row, temp_col = char_a.combat_row, char_a.combat_col
        char_a.combat_row, char_a.combat_col = char_b.combat_row, char_b.combat_col
        char_b.combat_row, char_b.combat_col = temp_row, temp_col

        self.manager.repository.save(char_a)
        self.manager.repository.save(char_b)
        self.refresh_character_lists()

    def move_character_to_slot(self, char_name: str, target_row: int, target_col: int) -> None:
        char = self.manager.get_character(char_name)
        if not char:
            return

        char.combat_row = target_row
        char.combat_col = target_col
        self.manager.repository.save(char)
        self.refresh_character_lists()

    def open_create_character_tab(self) -> None:
        for index in range(self.tabs.count()):
            widget = self.tabs.widget(index)
            if isinstance(widget, CreateCharacterTab):
                self.tabs.setCurrentIndex(index)
                return

        create_tab = CreateCharacterTab(self.manager, self)
        create_tab.character_created.connect(self.handle_character_created)
        create_tab.cancelled.connect(self.close_create_character_tab)

        tab_index = self.tabs.addTab(create_tab, "+ Create Character")
        self.tabs.setCurrentIndex(tab_index)

    def close_create_character_tab(self) -> None:
        for index in range(self.tabs.count()):
            widget = self.tabs.widget(index)
            if isinstance(widget, CreateCharacterTab):
                self.tabs.removeTab(index)
                widget.deleteLater()
                break

        self.tabs.setCurrentIndex(0)

    def handle_character_created(self, char_name: str) -> None:
        char = self.manager.get_character(char_name)
        if not char:
            self.close_create_character_tab()
            return

        all_chars = self.manager.list_characters()
        active_pcs = [c for c in all_chars if c.is_in_party and not c.is_npc and c.is_alive and not c.is_retired]

        if len(active_pcs) < 6 and not char.is_npc:
            char.is_in_party = True
            self._assign_first_available_grid_slot(char, all_chars)
        else:
            char.is_in_party = False

        self.manager.repository.save(char)
        self.close_create_character_tab()
        self.refresh_character_lists()

    def _assign_first_available_grid_slot(self, char, all_chars) -> None:
        occupied = {(c.combat_row, c.combat_col) for c in all_chars if c.is_in_party and c.name != char.name}
        for r in range(3):
            for c in range(3):
                if (r, c) not in occupied:
                    char.combat_row = r
                    char.combat_col = c
                    return

    def _delete_selected_character(self) -> None:
        selected_item = self.active_list.currentItem() or self.tavern_list.currentItem()
        if not selected_item:
            return

        char_name = selected_item.data(Qt.UserRole)
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to permanently delete '{char_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.manager.delete_character(char_name)
            self.refresh_character_lists()

    def _move_to_active(self) -> None:
        selected = self.tavern_list.currentItem()
        if not selected:
            return
        char_name = selected.data(Qt.UserRole)

        all_chars = self.manager.list_characters()
        active_party = [c for c in all_chars if getattr(c, "is_in_party", False)]
        if len(active_party) >= 9:
            QMessageBox.warning(
                self,
                "Party Full",
                "The party is full (maximum of 9 total party members between PCs and NPCs).",
            )
            return

        try:
            self.manager.add_to_party(char_name)
            self.refresh_character_lists()
        except ValueError as e:
            QMessageBox.warning(self, "Party Full", str(e))

    def _move_to_tavern(self) -> None:
        selected = self.active_list.currentItem()
        if not selected:
            return
        char_name = selected.data(Qt.UserRole)
        self.manager.remove_from_party(char_name)
        self.refresh_character_lists()

    def _on_list_item_clicked(self, item: QListWidgetItem) -> None:
        char_name = item.data(Qt.UserRole)
        self._inspect_character_by_name(char_name)

    def _inspect_character_by_name(self, name: str) -> None:
        char = self.manager.get_character(name)
        if not char:
            return

        self.inspector_widget.set_character(char)
        self.tabs.setCurrentIndex(1)