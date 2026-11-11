from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel, QGroupBox
from PySide6.QtCore import Signal
from typing import List
from app.models.enums import ClassType, WeaponType
from app.services.rules_engine import RulesEngine


class WeaponSelectorWidget(QWidget):
    """Custom widget enforcing class-based weapon count and type restrictions."""
    selection_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.class_type: ClassType = ClassType.HERO
        self.checkboxes: List[QCheckBox] = []
        
        self.layout = QVBoxLayout(self)
        self.group_box = QGroupBox("Starting Weapons")
        self.group_layout = QVBoxLayout(self.group_box)
        self.info_label = QLabel()
        self.group_layout.addWidget(self.info_label)
        self.layout.addWidget(self.group_box)

    def set_class(self, class_type: ClassType) -> None:
        """Rebuilds available weapon options based on class restrictions."""
        self.class_type = class_type
        for cb in self.checkboxes:
            self.group_layout.removeWidget(cb)
            cb.deleteLater()
        self.checkboxes.clear()

        if self.class_type == ClassType.PEACE_MAKER:
            self.info_label.setText("Peace Makers cannot equip any weapons.")
            return

        max_count = 1 if self.class_type == ClassType.HEALER else 2
        self.info_label.setText(f"Select up to {max_count} weapon(s):")

        allowed_weapons = RulesEngine.CLASS_WEAPON_RESTRICTIONS.get(self.class_type, set())
        for w_type in WeaponType:
            if w_type in allowed_weapons:
                cb = QCheckBox(w_type.name.replace('_', ' ').title())
                cb.setProperty("weapon_type", w_type)
                cb.stateChanged.connect(self._on_check_changed)
                self.group_layout.addWidget(cb)
                self.checkboxes.append(cb)

    def _on_check_changed(self) -> None:
        max_allowed = 1 if self.class_type == ClassType.HEALER else 2
        selected = self.get_selected_weapons()
        
        if len(selected) >= max_allowed:
            for cb in self.checkboxes:
                if not cb.isChecked():
                    cb.setEnabled(False)
        else:
            for cb in self.checkboxes:
                cb.setEnabled(True)

        self.selection_changed.emit()

    def get_selected_weapons(self) -> List[WeaponType]:
        return [cb.property("weapon_type") for cb in self.checkboxes if cb.isChecked()]