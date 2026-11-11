from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QGroupBox
from PySide6.QtCore import Signal
from typing import List, Optional
from app.models.enums import ClassType
from app.models.character import Spell
from app.models.spells import get_spells_for_class


class SpellSelectorWidget(QWidget):
    """Custom widget populating spell selection dropdowns from class spell pools."""
    selection_changed = Signal()

    def __init__(self, title: str = "Select Starting Spell", parent=None):
        super().__init__(parent)
        self.class_type: Optional[ClassType] = None
        self.available_spells: List[Spell] = []

        layout = QVBoxLayout(self)
        self.group_box = QGroupBox(title)
        group_layout = QVBoxLayout(self.group_box)
        
        self.combo = QComboBox()
        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)

        group_layout.addWidget(self.combo)
        group_layout.addWidget(self.desc_label)
        layout.addWidget(self.group_box)

        self.combo.currentIndexChanged.connect(self._on_spell_changed)

    def set_class(self, class_type: ClassType) -> None:
        """Populates dropdown with spells corresponding to character class."""
        self.class_type = class_type
        self.available_spells = get_spells_for_class(class_type)
        self.combo.blockSignals(True)
        self.combo.clear()

        for spell in self.available_spells:
            self.combo.addItem(f"{spell.name} (Cost: {spell.cost})", spell)

        self.combo.blockSignals(False)
        if self.available_spells:
            self.combo.setCurrentIndex(0)
            self._on_spell_changed(0)
        else:
            self.desc_label.setText("No spells available for this class.")

    def _on_spell_changed(self, index: int) -> None:
        spell = self.get_selected_spell()
        if spell:
            type_str = "Combat" if spell.is_combat_spell else "Non-Combat"
            self.desc_label.setText(f"<b>[{type_str}]</b> {spell.description}")
        else:
            self.desc_label.clear()
        self.selection_changed.emit()

    def get_selected_spell(self) -> Optional[Spell]:
        return self.combo.currentData()