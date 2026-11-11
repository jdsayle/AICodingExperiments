from PySide6.QtWidgets import QWidget, QVBoxLayout, QRadioButton, QButtonGroup, QGroupBox
from PySide6.QtCore import Signal
from app.models.enums import ClassType


class StartingBonusWidget(QWidget):
    """Widget managing mutually exclusive starting bonus options (a), (b), or (c)."""
    bonus_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.group_box = QGroupBox("Choose Starting Bonus Option")
        self.group_layout = QVBoxLayout(self.group_box)

        self.button_group = QButtonGroup(self)
        self.radio_a = QRadioButton("(a) +1 Max HP")
        self.radio_b = QRadioButton("(b) +1 Weapon Skill Bonus")
        self.radio_c = QRadioButton("(c) Special Option")

        self.button_group.addButton(self.radio_a, 0)
        self.button_group.addButton(self.radio_b, 1)
        self.button_group.addButton(self.radio_c, 2)

        self.group_layout.addWidget(self.radio_a)
        self.group_layout.addWidget(self.radio_b)
        self.group_layout.addWidget(self.radio_c)
        self.layout.addWidget(self.group_box)

        self.radio_a.setChecked(True)
        self.button_group.idToggled.connect(lambda: self.bonus_changed.emit())

    def set_class(self, class_type: ClassType) -> None:
        """Adapts option (c) text according to class rules."""
        if class_type in {ClassType.HERO, ClassType.PEACE_MAKER}:
            self.radio_c.setText("(c) +1 Magic Resistance")
            self.radio_c.setEnabled(True)
        elif class_type == ClassType.THIEF:
            self.radio_c.setText("(c) +1 Detrap Skill")
            self.radio_c.setEnabled(True)
        elif class_type in {ClassType.WIZARD, ClassType.WITCH_HUNTER, ClassType.HEALER}:
            self.radio_c.setText("(c) Learn a Second Spell")
            self.radio_c.setEnabled(True)
        else:
            self.radio_c.setEnabled(False)

        if class_type == ClassType.PEACE_MAKER:
            self.radio_b.setEnabled(False)
            if self.radio_b.isChecked():
                self.radio_a.setChecked(True)
        else:
            self.radio_b.setEnabled(True)

    def get_selected_bonus(self) -> str:
        selected_id = self.button_group.checkedId()
        return ["a", "b", "c"][selected_id] if selected_id != -1 else "a"