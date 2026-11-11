from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QPushButton, QGroupBox
)
from PySide6.QtCore import Signal
from app.models.character import Character


class CharacterCardWidget(QFrame):
    """Stat card widget for fast multi-character combat and party monitoring."""
    inspect_requested = Signal(str)

    def __init__(self, character: Character, parent=None):
        super().__init__(parent)
        self.character = character
        self.setFrameShape(QFrame.StyledPanel)
        self.setLineWidth(2)
        
        layout = QVBoxLayout(self)

        # Header: Name & Class
        header_layout = QHBoxLayout()
        name_label = QLabel(f"<b>{character.name}</b>")
        class_label = QLabel(f"<i>{character.class_type.name.replace('_', ' ').title()}</i>")
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(class_label)
        layout.addLayout(header_layout)

        # Health & Wounds
        self.hp_bar = QProgressBar()
        self.hp_bar.setMaximum(character.max_hp)
        self.hp_bar.setValue(max(0, character.effective_hp))
        self.hp_bar.setFormat(f"HP: {character.effective_hp}/{character.max_hp}")
        layout.addWidget(self.hp_bar)

        if character.magic_wounds > 0:
            mw_label = QLabel(f"<font color='#ff6b6b'>Magic Wounds: {character.magic_wounds}</font>")
            layout.addWidget(mw_label)

        # Equipped Weapon
        equipped_w = "None"
        if character.equipped_weapon_index is not None and 0 <= character.equipped_weapon_index < len(character.weapons):
            w = character.weapons[character.equipped_weapon_index]
            equipped_w = w.name.name.replace('_', ' ').title()
        elif character.weapons:
            equipped_w = character.weapons[0].name.name.replace('_', ' ').title()
        layout.addWidget(QLabel(f"<b>Weapon:</b> {equipped_w}"))

        # Quick Access Items / Spells
        quick_box = QGroupBox("Quick Access")
        quick_layout = QVBoxLayout(quick_box)

        # Show top items
        for item in character.items[:3]:
            quick_layout.addWidget(QLabel(f"🧪 {item.name}"))

        # Show top spells for magic users
        if character.is_magic_user:
            for spell in character.spells[:3]:
                quick_layout.addWidget(QLabel(f"✨ {spell.name} (Cost: {spell.cost})"))

        if not character.items and not (character.is_magic_user and character.spells):
            quick_layout.addWidget(QLabel("<i>No items/spells equipped</i>"))

        layout.addWidget(quick_box)

        # Action Button
        inspect_btn = QPushButton("View Full Sheet")
        inspect_btn.clicked.connect(lambda: self.inspect_requested.emit(character.name))
        layout.addWidget(inspect_btn)