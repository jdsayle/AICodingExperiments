from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QGroupBox
from PySide6.QtCore import Signal, QSize
from app.models.character import Character


class CharacterCardWidget(QWidget):
    """Interactive visual summary card for a single character in the active party."""
    inspect_requested = Signal(str)

    def __init__(self, character: Character, parent=None):
        super().__init__(parent)
        self.character = character

        # Increased fixed uniform card dimensions for widescreen 1920x1200 layouts
        self.setFixedSize(QSize(450, 300))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.group_box = QGroupBox(f"{character.name} ({character.class_type.name.replace('_', ' ').title()})")
        group_layout = QVBoxLayout(self.group_box)
        group_layout.setContentsMargins(10, 10, 10, 10)

        # HP Bar
        hp_layout = QHBoxLayout()
        hp_layout.addWidget(QLabel("HP:"))
        self.hp_bar = QProgressBar()
        self.hp_bar.setMaximum(character.max_hp)
        self.hp_bar.setValue(character.effective_hp)
        self.hp_bar.setFormat(f"%v / %m (Wounds: {character.magic_wounds})")
        hp_layout.addWidget(self.hp_bar)
        group_layout.addLayout(hp_layout)

        # Equipped Weapon
        weapon_name = "None"
        if character.weapons and character.equipped_weapon_index is not None:
            if 0 <= character.equipped_weapon_index < len(character.weapons):
                weapon_name = character.weapons[character.equipped_weapon_index].name.name.replace('_', ' ').title()
        elif character.weapons:
            weapon_name = character.weapons[0].name.name.replace('_', ' ').title()
        group_layout.addWidget(QLabel(f"<b>Equipped:</b> {weapon_name}"))

        # Quick Inventory / Spells summary (top items)
        top_items = ", ".join(i.name for i in character.items[:3]) or "None"
        group_layout.addWidget(QLabel(f"<b>Items:</b> {top_items}"))

        top_spells = ", ".join(s.name for s in character.spells[:3]) or "None"
        group_layout.addWidget(QLabel(f"<b>Spells:</b> {top_spells}"))

        # View Full Sheet Button
        self.inspect_btn = QPushButton("View Full Sheet")
        self.inspect_btn.clicked.connect(lambda: self.inspect_requested.emit(character.name))
        group_layout.addWidget(self.inspect_btn)

        layout.addWidget(self.group_box)