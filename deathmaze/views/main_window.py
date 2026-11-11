from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
    QPushButton, QTabWidget, QScrollArea, QLabel, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt
from app.services.character_manager import CharacterManager
from views.character_wizard import CharacterCreationWizard
from views.widgets.character_card import CharacterCardWidget


class MainWindow(QMainWindow):
    """Main window integrating left sidebar character management and right tabbed workspace."""

    def __init__(self, manager: CharacterManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("DeathMaze Deluxe - Desktop Manager")
        self.resize(1100, 700)

        # Central Split Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- LEFT SIDEBAR ---
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_widget.setFixedWidth(260)

        sidebar_layout.addWidget(QLabel("<h3>Character Roster</h3>"))
        self.char_list = QListWidget()
        self.char_list.currentTextChanged.connect(self._on_sidebar_selection_changed)
        sidebar_layout.addWidget(self.char_list)

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

        # Tab 1: Active Party Dashboard (Grid of Stat Cards)
        self.dashboard_tab = QWidget()
        self.dashboard_scroll = QScrollArea()
        self.dashboard_scroll.setWidgetResizable(True)
        self.dashboard_container = QWidget()
        self.dashboard_grid = QGridLayout(self.dashboard_container)
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

        # Initial Refresh
        self.refresh_character_list()

    def refresh_character_list(self) -> None:
        """Reloads character list from repository and updates dashboard stat cards."""
        self.char_list.clear()
        characters = self.manager.list_characters()

        # Populate sidebar list
        for char in characters:
            self.char_list.addItem(char.name)

        # Clear and rebuild Dashboard Grid
        while self.dashboard_grid.count():
            item = self.dashboard_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cols = 2
        for idx, char in enumerate(characters):
            card = CharacterCardWidget(char)
            card.inspect_requested.connect(self._inspect_character_by_name)
            row, col = divmod(idx, cols)
            self.dashboard_grid.addWidget(card, row, col)

    def _open_creation_wizard(self) -> None:
        """Launches CharacterCreationWizard modally and refreshes list on success."""
        wizard = CharacterCreationWizard(self.manager, parent=self)
        if wizard.exec():
            self.refresh_character_list()

    def _delete_selected_character(self) -> None:
        """Deletes selected character with QMessageBox confirmation guard."""
        current_item = self.char_list.currentItem()
        if not current_item:
            return

        char_name = current_item.text()
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to permanently delete '{char_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.manager.delete_character(char_name)
            self.refresh_character_list()

    def _on_sidebar_selection_changed(self, name: str) -> None:
        if name:
            self._inspect_character_by_name(name)

    def _inspect_character_by_name(self, name: str) -> None:
        """Populates Detailed Character Inspector tab with full stats and switches tab."""
        char = self.manager.get_character(name)
        if not char:
            return

        weapons_str = ", ".join(w.name.name.replace('_', ' ').title() for w in char.weapons) or "None"
        items_str = ", ".join(i.name for i in char.items) or "None"
        spells_str = ", ".join(s.name for s in char.spells) or "None"

        details = f"""
        <h2>{char.name} ({char.class_type.name.replace('_', ' ').title()})</h2>
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
        self.tabs.setCurrentIndex(1)  # Switch to Inspector tab