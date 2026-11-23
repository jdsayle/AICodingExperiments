from typing import Iterable, List, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QSpinBox, QPushButton, QLabel, QMessageBox
)
from app.models.character import Character
from app.models.enums import WeaponType
from app.services.rules_engine import RulesEngine


WEAPON_PILL_OPTIONS: tuple[tuple[str, WeaponType], ...] = (
    ("Sword", WeaponType.SWORD),
    ("Dagger", WeaponType.DAGGER),
    ("Bow", WeaponType.BOW_AND_ARROWS),
)


class AddCharmedDialog(QDialog):
    """Dialog for adding a Charmed NPC with name, HP, combat strength, and up to 2 weapon pills."""

    def __init__(self, party: Iterable[Character], parent=None):
        super().__init__(parent)
        self.party = list(party)
        self.created_npc: Optional[Character] = None
        self._selected_weapons: List[WeaponType] = []
        self._weapon_pills: dict[WeaponType, QPushButton] = {}

        self.setWindowTitle("Add Charmed NPC")
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h3>Add Charmed Ally</h3>"))

        form = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Charmed Goblin")
        form.addRow("Name:", self.name_input)

        self.current_hp_spin = QSpinBox()
        self.current_hp_spin.setRange(1, 999)
        self.current_hp_spin.setValue(4)
        form.addRow("Current HP:", self.current_hp_spin)

        self.max_hp_spin = QSpinBox()
        self.max_hp_spin.setRange(1, 999)
        self.max_hp_spin.setValue(4)
        form.addRow("Max HP:", self.max_hp_spin)

        self.combat_strength_spin = QSpinBox()
        self.combat_strength_spin.setRange(-10, 99)
        self.combat_strength_spin.setValue(0)
        form.addRow("Combat Strength:", self.combat_strength_spin)

        layout.addLayout(form)

        layout.addWidget(QLabel("<b>Weapons (Select up to 2):</b>"))
        pills_row = QHBoxLayout()
        for label, w_type in WEAPON_PILL_OPTIONS:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked=False, wt=w_type: self._toggle_weapon(wt))
            self._weapon_pills[w_type] = btn
            pills_row.addWidget(btn)
        pills_row.addStretch()
        layout.addLayout(pills_row)

        note_lbl = QLabel("<i>Charmed NPCs cannot gain XP, Bezants/Gems, or items, and leave when exiting the maze.</i>")
        note_lbl.setWordWrap(True)
        layout.addWidget(note_lbl)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        confirm_btn = QPushButton("Add Charmed")
        confirm_btn.clicked.connect(self._on_confirm)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(confirm_btn)
        layout.addLayout(btn_row)

    def _toggle_weapon(self, w_type: WeaponType) -> None:
        if w_type in self._selected_weapons:
            self._selected_weapons.remove(w_type)
            self._weapon_pills[w_type].setChecked(False)
            return

        if len(self._selected_weapons) >= 2:
            self._weapon_pills[w_type].setChecked(False)
            QMessageBox.information(self, "Weapon Limit", "You can select at most 2 weapons for a Charmed NPC.")
            return

        self._selected_weapons.append(w_type)
        self._weapon_pills[w_type].setChecked(True)

    def _on_confirm(self) -> None:
        try:
            self.created_npc = RulesEngine.create_charmed_npc(
                party=self.party,
                name=self.name_input.text(),
                current_hp=self.current_hp_spin.value(),
                max_hp=self.max_hp_spin.value(),
                combat_strength=self.combat_strength_spin.value(),
                weapon_types=self._selected_weapons,
            )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Charmed NPC", str(e))