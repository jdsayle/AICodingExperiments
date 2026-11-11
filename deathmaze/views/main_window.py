from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QTabWidget, QScrollArea, QLabel, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt
from app.services.character_manager import CharacterManager
from views.character_wizard import CharacterCreationWizard
from views.widgets.character_card import CharacterCardWidget
from views.widgets.empty_slot_widget import EmptySlotWidget


class ActivePartyDashboardGrid(QWidget):
    """Grid container managing drops across the 3x3 tactical layout for cards and empty slots."""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setAcceptDrops(True)
        self.grid = QGridLayout(self)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        source_name = event.mimeData().text()
        pos = event.position().toPoint()
        
        # Iterate through all 3x3 cells and check which child widget contains the drop position
        for row in range(3):
            for col in range(3):
                item = self.grid.itemAtPosition(row, col)
                if item and item.widget():
                    widget = item.widget()
                    # Map position to widget coordinates or check geometry bounding box
                    widget_pos = widget.mapFrom(self, pos)
                    if widget.rect().contains(widget_pos):
                        if isinstance(widget, CharacterCardWidget):
                            target_name = widget.character.name
                            if source_name != target_name:
                                self.main_window.swap_character_positions(source_name, target_name)
                            event.acceptProposedAction()
                            return
                        elif isinstance(widget, EmptySlotWidget):
                            self.main_window.move_character_to_slot(source_name, row, col)
                            event.acceptProposedAction()
                            return
        event.ignore()

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

        sidebar_layout.addWidget(QLabel("<b>ACTIVE PARTY (Max 6 PCs + 3 NPCs)</b>"))
        self.active_list = QListWidget()
        self.active_list.itemClicked.connect(self._on_list_item_clicked)
        sidebar_layout.addWidget(self.active_list)

        self.toggle_to_tavern_btn = QPushButton("↓ Move to Tavern / Town")
        self.toggle_to_tavern_btn.clicked.connect(self._move_to_tavern)
        sidebar_layout.addWidget(self.toggle_to_tavern_btn)

        sidebar_layout.addWidget(QLabel("<b>TAVERN / TOWN (Stable)</b>"))
        self.tavern_list = QListWidget()
        self.tavern_list.itemClicked.connect(self._on_list_item_clicked)
        sidebar_layout.addWidget(self.tavern_list)

        self.toggle_to_active_btn = QPushButton("↑ Recruit to Active Party")
        self.toggle_to_active_btn.clicked.connect(self._move_to_active)
        sidebar_layout.addWidget(self.toggle_to_active_btn)

        btn_layout = QHBoxLayout()
        self.create_btn = QPushButton("+ Create")
        self.delete_btn = QPushButton("- Delete")
        self.create_btn.clicked.connect(self._open_creation_wizard)
        self.delete_btn.clicked.connect(self._delete_selected_character)

        btn_layout.addWidget(self.create_btn)
        btn_layout.addWidget(self.delete_btn)
        sidebar_layout.addLayout(btn_layout)

        main_layout.addWidget(sidebar_widget)

        # --- RIGHT TABBED WORKSPACE ---
        self.tabs = QTabWidget()

        # Tab 1: Active Party Dashboard (3x3 Tactical Grid)
        self.dashboard_tab = QWidget()
        self.dashboard_scroll = QScrollArea()
        self.dashboard_scroll.setWidgetResizable(True)
        
        self.dashboard_container = ActivePartyDashboardGrid(self)
        self.dashboard_grid = self.dashboard_container.grid
        self.dashboard_scroll.setWidget(self.dashboard_container)

        dash_layout = QVBoxLayout(self.dashboard_tab)
        dash_layout.addWidget(self.dashboard_scroll)
        self.tabs.addTab(self.dashboard_tab, "Active Party Dashboard")

        # Tab 2: Detailed Character Inspector
        self.inspector_tab = QWidget()
        self.inspector_layout = QVBoxLayout(self.inspector_tab)
        self.inspector_label = QLabel("<i>Select a character to view detailed sheet.</i>")
        self.inspector_label.setWordWrap(True)
        self.inspector_layout.addWidget(self.inspector_label)
        self.tabs.addTab(self.inspector_tab, "Detailed Inspector")

        main_layout.addWidget(self.tabs)

        self.refresh_character_lists()

    def refresh_character_lists(self) -> None:
        """Reloads active party and tavern lists, rendering the exact 3x3 tactical grid."""
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

        # Clear existing widgets from 3x3 grid
        while self.dashboard_grid.count():
            item = self.dashboard_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Map active characters to their specific (combat_row, combat_col) slots, or auto-assign if unassigned
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

        # Place unassigned characters into the next available open slots
        for char in unassigned:
            placed = False
            for r in range(3):
                for c in range(3):
                    if (r, c) not in occupied_slots:
                        occupied_slots[(r, c)] = char
                        char.combat_row = r
                        char.combat_col = c
                        placed = True
                        break
                if placed:
                    break

        # Populate the strict 3x3 grid with CharacterCards or EmptySlotWidgets
        for row in range(3):
            for col in range(3):
                if (row, col) in occupied_slots:
                    char = occupied_slots[(row, col)]
                    card = CharacterCardWidget(char)
                    card.inspect_requested.connect(self._inspect_character_by_name)
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

        # Swap their tactical coordinates
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

    def _open_creation_wizard(self) -> None:
        wizard = CharacterCreationWizard(self.manager, parent=self)
        if wizard.exec():
            self.refresh_character_lists()

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

        weapons_str = ", ".join(w.name.name.replace('_', ' ').title() for w in char.weapons) or "None"
        items_str = ", ".join(i.name for i in char.items) or "None"
        spells_str = ", ".join(s.name for s in char.spells) or "None"
        location = "Active Party" if char.is_in_party else "Tavern / Town Stable"

        details = f"""
        <h2>{char.name} ({char.class_type.name.replace('_', ' ').title()})</h2>
        <p><b>Location:</b> {location} | <b>Combat Row:</b> Row {char.combat_row + 1}, Col {char.combat_col + 1}</p>
        <p><b>Level:</b> {char.level} | <b>Created:</b> {char.created_date}</p>
        <hr>
        <p><b>Hit Points:</b> {char.effective_hp} / {char.max_hp} (Magic Wounds: {char.magic_wounds})</p>
        <p><b>Magic Resistance:</b> {char.magic_resistance} | <b>Detrap Skill:</b> {char.detrap_skill}</p>
        <p><b>Bezants:</b> {char.bezants} | <b>Gems:</b> {char.gems}</p>
        <hr>
        <p><b>Weapons:</b> {weapons_str}</p>
        <p><b>Inventory Items:</b> {items_str}</p>
        <p><b>Spells:</b> {spells_str}</p>
        """
        self.inspector_label.setText(details)
        self.tabs.setCurrentIndex(1)