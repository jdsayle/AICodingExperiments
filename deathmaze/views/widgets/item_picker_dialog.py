from typing import Dict, Iterable, List, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QScrollArea
)
from app.models.character import Character
from app.models.enums import ItemType
from app.models.items import ItemDefinition
from app.services.rules_engine import RulesEngine


class FlowLayoutWidget(QWidget):
    """Simple wrapping container for pill buttons."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: List[QHBoxLayout] = []
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(6)

    def set_buttons(self, buttons: List[QPushButton], per_row: int = 3) -> None:
        while self._main_layout.count():
            child = self._main_layout.takeAt(0)
            if child.layout():
                while child.layout().count():
                    w_item = child.layout().takeAt(0)
                    if w_item.widget():
                        w_item.widget().deleteLater()
            elif child.widget():
                child.widget().deleteLater()

        self._rows.clear()
        for idx in range(0, len(buttons), per_row):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(6)
            for btn in buttons[idx:idx + per_row]:
                row_layout.addWidget(btn)
            row_layout.addStretch()
            self._rows.append(row_layout)
            self._main_layout.addLayout(row_layout)


class AddItemDialog(QDialog):
    """Pill-button selector dialog for choosing an item type and item name for a character."""

    def __init__(
        self,
        character: Character,
        party: Optional[Iterable[Character]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.character = character
        self.party = list(party) if party is not None else [character]
        self.selected_type: Optional[ItemType] = None
        self.selected_definition: Optional[ItemDefinition] = None
        self.type_pills: Dict[ItemType, QPushButton] = {}
        self.name_pills: Dict[str, QPushButton] = {}

        self.setWindowTitle(f"Add Item — {character.name}")
        self.setMinimumSize(460, 340)

        available = RulesEngine.get_available_items_for_character(character)
        self._by_type: Dict[ItemType, List[ItemDefinition]] = {}
        for defn in available:
            self._by_type.setdefault(defn.item_type, []).append(defn)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<h3>Grant Item to {character.name}</h3>"))
        layout.addWidget(QLabel("<b>1. Select Item Type:</b>"))

        self.type_container = FlowLayoutWidget()
        type_buttons: List[QPushButton] = []
        for item_type in ItemType:
            if item_type in self._by_type and self._by_type[item_type]:
                label = item_type.name.replace("_", " ").title()
                btn = QPushButton(label)
                btn.setCheckable(True)
                btn.clicked.connect(lambda checked=False, t=item_type: self._select_type(t))
                self.type_pills[item_type] = btn
                type_buttons.append(btn)
        self.type_container.set_buttons(type_buttons, per_row=3)
        layout.addWidget(self.type_container)

        layout.addWidget(QLabel("<b>2. Select Item Name:</b>"))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.name_container = FlowLayoutWidget()
        scroll.setWidget(self.name_container)
        layout.addWidget(scroll)

        self.effect_preview = QLabel("<i>Select an item pill to preview its effect.</i>")
        self.effect_preview.setWordWrap(True)
        layout.addWidget(self.effect_preview)

        action_row = QHBoxLayout()
        action_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        self.confirm_btn = QPushButton("Grant Item")
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.clicked.connect(self.accept)
        action_row.addWidget(cancel_btn)
        action_row.addWidget(self.confirm_btn)
        layout.addLayout(action_row)

        if type_buttons:
            first_type = next(iter(self.type_pills.keys()))
            self._select_type(first_type)

    def _select_type(self, item_type: ItemType) -> None:
        self.selected_type = item_type
        self.selected_definition = None
        self.confirm_btn.setEnabled(False)
        self.effect_preview.setText("<i>Select an item pill to preview its effect.</i>")

        for t, pill in self.type_pills.items():
            pill.setChecked(t == item_type)

        self.name_pills.clear()
        name_buttons: List[QPushButton] = []
        for defn in self._by_type.get(item_type, []):
            btn = QPushButton(defn.name)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked=False, d=defn: self._select_definition(d))
            self.name_pills[defn.name] = btn
            name_buttons.append(btn)

        self.name_container.set_buttons(name_buttons, per_row=2)

    def _select_definition(self, defn: ItemDefinition) -> None:
        self.selected_definition = defn
        for name, pill in self.name_pills.items():
            pill.setChecked(name == defn.name)

        note = ""
        if defn.item_type == ItemType.POTION and RulesEngine.has_active_potion_appraisal(self.party):
            note = " <b>[Potion Appraisal active: +2 uses]</b>"
        elif defn.item_type == ItemType.MAGIC_RING:
            note = " <b>[1 use per game at 0 Magic Wounds; recharges on Leave Maze]</b>"

        self.effect_preview.setText(f"<b>Effect:</b> {defn.effect}{note}")
        self.confirm_btn.setEnabled(True)