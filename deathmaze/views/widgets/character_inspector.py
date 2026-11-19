from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QSpinBox, QPushButton, QGroupBox, QGridLayout, QMessageBox, QDialog
)
from PySide6.QtCore import Signal, Qt
from app.models.character import Character, Item
from app.models.enums import ItemType
from app.services.character_manager import CharacterManager
from app.services.rules_engine import RulesEngine
from views.widgets.item_picker_dialog import AddItemDialog


class CharacterInspectorWidget(QWidget):
    """Interactive control center for inspecting and modifying character stats, inventory, and spells."""

    character_updated = Signal(str)  # Emits character name when modified

    def __init__(self, manager: CharacterManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.current_character = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)

        self.placeholder_label = QLabel("<i>Select a character to view detailed sheet.</i>")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.container_layout.addWidget(self.placeholder_label)

        scroll_area.setWidget(self.container)
        main_layout.addWidget(scroll_area)

    @staticmethod
    def format_item_display(item: Item) -> str:
        """Formats an inventory item for display; shows uses for Spice/Potion and '(Used)' for spent Magic Rings."""
        item_type_name = (
            item.item_type.name.replace("_", " ").title()
            if isinstance(item.item_type, ItemType)
            else str(item.item_type)
        )
        effect_part = f" - {item.effect}" if getattr(item, "effect", None) else ""

        if item.item_type in {ItemType.SPICE, ItemType.POTION}:
            uses = getattr(item, "uses_remaining", None)
            if uses is not None:
                unit = "use" if uses == 1 else "uses"
                return f"🎒 [{item_type_name}] {item.name}{effect_part} ({uses} {unit} left)"
            return f"🎒 [{item_type_name}] {item.name}{effect_part}"

        if item.item_type == ItemType.MAGIC_RING:
            if getattr(item, "used_this_game", False):
                return f"🎒 [{item_type_name}] {item.name}{effect_part} (Used)"
            return f"🎒 [{item_type_name}] {item.name}{effect_part}"

        # Rings and Medallions: omit usage text completely
        return f"🎒 [{item_type_name}] {item.name}{effect_part}"

    def set_character(self, char: Character) -> None:
        """Loads and renders the interactive character inspector interface."""
        self.current_character = char

        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not char:
            self.container_layout.addWidget(self.placeholder_label)
            return

        # --- HEADER ---
        header_layout = QHBoxLayout()
        role_tag = "[NPC]" if char.is_npc else "[PC]"
        title_lbl = QLabel(f"<h2>{role_tag} {char.name} ({char.class_type.name.replace('_', ' ').title()})</h2>")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        self.container_layout.addLayout(header_layout)

        info_lbl = QLabel(
            f"<b>Location:</b> {'Active Party' if char.is_in_party else 'Tavern / Town Stable'} | "
            f"<b>Level:</b> {char.level} | <b>XP:</b> {char.experience} | <b>Created:</b> {char.created_date}"
        )
        self.container_layout.addWidget(info_lbl)
        self.container_layout.addWidget(self._create_divider())

        # --- STATS & STEPPERS GROUP ---
        stats_group = QGroupBox("Combat Stats & Wealth")
        stats_grid = QGridLayout(stats_group)

        row_idx = 0

        stats_grid.addWidget(QLabel("Current HP:"), row_idx, 0)
        self.hp_spin = QSpinBox()
        self.hp_spin.setRange(-10, char.max_hp)
        self.hp_spin.setValue(char.current_hp)
        self.hp_spin.valueChanged.connect(self._on_hp_changed)
        stats_grid.addWidget(self.hp_spin, row_idx, 1)
        row_idx += 1

        if char.is_magic_user:
            stats_grid.addWidget(QLabel("Magic Wounds:"), row_idx, 0)
            self.mw_spin = QSpinBox()
            self.mw_spin.setRange(0, 50)
            self.mw_spin.setValue(char.magic_wounds)
            self.mw_spin.valueChanged.connect(self._on_mw_changed)
            stats_grid.addWidget(self.mw_spin, row_idx, 1)
            row_idx += 1
        else:
            self.mw_spin = None

        stats_grid.addWidget(QLabel("Bezants (Coins):"), row_idx, 0)
        self.bezants_spin = QSpinBox()
        self.bezants_spin.setRange(0, 99999)
        self.bezants_spin.setValue(char.bezants)
        self.bezants_spin.valueChanged.connect(self._on_bezants_changed)
        stats_grid.addWidget(self.bezants_spin, row_idx, 1)
        row_idx += 1

        stats_grid.addWidget(QLabel("Gems:"), row_idx, 0)
        self.gems_spin = QSpinBox()
        self.gems_spin.setRange(0, 999)
        self.gems_spin.setValue(char.gems)
        self.gems_spin.valueChanged.connect(self._on_gems_changed)
        stats_grid.addWidget(self.gems_spin, row_idx, 1)

        self.container_layout.addWidget(stats_group)
        self.container_layout.addWidget(self._create_divider())

        # --- WEAPONS & EQUIPMENT ---
        weapons_group = QGroupBox("Weapons & Equipment")
        w_layout = QVBoxLayout(weapons_group)

        if char.weapons:
            for idx, w in enumerate(char.weapons):
                w_row = QHBoxLayout()
                w_name = w.name.name.replace('_', ' ').title()
                bonus_str = f" (+{w.skill_bonus})" if w.skill_bonus > 0 else ""
                is_equipped = (char.equipped_weapon_index == idx)

                label_text = f"⚔️ {w_name}{bonus_str} {' [EQUIPPED]' if is_equipped else ''}"
                w_row.addWidget(QLabel(label_text))
                w_row.addStretch()

                if not is_equipped:
                    equip_btn = QPushButton("Equip")
                    equip_btn.clicked.connect(lambda checked=False, i=idx: self._equip_weapon(i))
                    w_row.addWidget(equip_btn)

                w_layout.addLayout(w_row)
        else:
            w_layout.addWidget(QLabel("<i>No weapons carried.</i>"))

        self.container_layout.addWidget(weapons_group)
        self.container_layout.addWidget(self._create_divider())

        # --- INVENTORY & ITEMS ---
        items_group = QGroupBox("Inventory & Items")
        i_layout = QVBoxLayout(items_group)

        top_items_row = QHBoxLayout()
        top_items_row.addStretch()
        self.add_item_btn = QPushButton("Item")
        self.add_item_btn.clicked.connect(self._on_add_item_clicked)
        top_items_row.addWidget(self.add_item_btn)
        i_layout.addLayout(top_items_row)

        char_items = getattr(char, "items", [])
        if char_items:
            for item in char_items:
                i_row = QHBoxLayout()
                i_row.addWidget(QLabel(self.format_item_display(item)))
                i_row.addStretch()
                i_layout.addLayout(i_row)
        else:
            i_layout.addWidget(QLabel("<i>No items carried.</i>"))

        self.container_layout.addWidget(items_group)

        # --- SPELLS & CASTING ---
        if char.is_magic_user:
            self.container_layout.addWidget(self._create_divider())
            spells_group = QGroupBox("Spells & Incantations")
            s_layout = QVBoxLayout(spells_group)

            if char.spells:
                for spell in char.spells:
                    s_row = QHBoxLayout()
                    s_row.addWidget(QLabel(f"✨ {spell.name} (Cost: {spell.cost} HP) - {spell.description}"))
                    s_row.addStretch()

                    cast_btn = QPushButton("Cast")
                    cast_btn.clicked.connect(lambda checked=False, s=spell: self._cast_spell(s))
                    s_row.addWidget(cast_btn)

                    s_layout.addLayout(s_row)
            else:
                s_layout.addWidget(QLabel("<i>No spells learned.</i>"))

            self.container_layout.addWidget(spells_group)

        self.container_layout.addStretch()

    def _on_add_item_clicked(self) -> None:
        if not self.current_character:
            return
        party = [c for c in self.manager.list_characters() if getattr(c, "is_in_party", False)]
        dialog = AddItemDialog(self.current_character, party=party, parent=self)
        if dialog.exec() == QDialog.Accepted and dialog.selected_definition is not None:
            try:
                RulesEngine.grant_item(self.current_character, dialog.selected_definition, party=party)
                self._save_changes()
                self.set_character(self.current_character)
            except ValueError as e:
                QMessageBox.warning(self, "Cannot Add Item", str(e))

    def _create_divider(self) -> QWidget:
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #334155;")
        return line

    def _on_hp_changed(self, value: int) -> None:
        if self.current_character:
            self.current_character.current_hp = value
            self._save_changes()

    def _on_mw_changed(self, value: int) -> None:
        if self.current_character and self.current_character.is_magic_user:
            self.current_character.magic_wounds = value
            self._save_changes()

    def _on_bezants_changed(self, value: int) -> None:
        if self.current_character:
            self.current_character.bezants = value
            self._save_changes()

    def _on_gems_changed(self, value: int) -> None:
        if self.current_character:
            self.current_character.gems = value
            self._save_changes()

    def _equip_weapon(self, index: int) -> None:
        if self.current_character:
            self.current_character.equipped_weapon_index = index
            self._save_changes()
            self.set_character(self.current_character)

    def _cast_spell(self, spell) -> None:
        if not self.current_character:
            return

        try:
            if RulesEngine.can_cast_spell(self.current_character, spell, target_is_undead=False):
                RulesEngine.cast_spell(self.current_character, spell, target_is_undead=False)
                self._save_changes()
                self.set_character(self.current_character)
                QMessageBox.information(self, "Spell Cast", f"Successfully cast {spell.name}!")
            else:
                QMessageBox.warning(self, "Cannot Cast", f"Not enough health or class restrictions prevent casting {spell.name}.")
        except ValueError as e:
            QMessageBox.warning(self, "Spell Failed", str(e))

    def _save_changes(self) -> None:
        if self.current_character:
            try:
                self.manager.repository.save(self.current_character)
                self.character_updated.emit(self.current_character.name)
            except Exception as e:
                QMessageBox.critical(self, "Persistence Error", f"Could not save character update: {str(e)}")

    def clear(self) -> None:
        self.set_character(None)