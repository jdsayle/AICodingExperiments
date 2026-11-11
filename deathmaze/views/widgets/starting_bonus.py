from PySide6.QtWidgets import QWidget, QVBoxLayout, QRadioButton, QButtonGroup, QGroupBox
from PySide6.QtCore import Signal
from app.models.enums import ClassType


class StartingBonusWidget(QWidget):
    """Widget managing mutually exclusive starting bonus options (a), (b), (c), or (d)."""
    bonus_changed = Signal(str)  # Passes the selected bonus key ('a', 'b', 'c', or 'd')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.group_box = QGroupBox("Choose Starting Bonus Option")
        self.group_layout = QVBoxLayout(self.group_box)

        self.button_group = QButtonGroup(self)
        self.radio_a = QRadioButton("(a) Increase Max HP by +1")
        self.radio_b = QRadioButton("(b) Gain skill with one weapon you have chosen earlier")
        self.radio_c = QRadioButton("(c) Special Option")
        self.radio_d = QRadioButton("(d) Learn a second spell")

        self.button_group.addButton(self.radio_a, 0)
        self.button_group.addButton(self.radio_b, 1)
        self.button_group.addButton(self.radio_c, 2)
        self.button_group.addButton(self.radio_d, 3)

        self.group_layout.addWidget(self.radio_a)
        self.group_layout.addWidget(self.radio_b)
        self.group_layout.addWidget(self.radio_c)
        self.group_layout.addWidget(self.radio_d)
        self.layout.addWidget(self.group_box)

        self.radio_a.setChecked(True)
        self.button_group.idToggled.connect(self._emit_bonus_changed)

    def _emit_bonus_changed(self, button_id: int, checked: bool) -> None:
        if checked:
            bonus_key = self.get_selected_bonus()
            self.bonus_changed.emit(bonus_key)

    def configure_for_class(self, class_type: ClassType) -> None:
        """Configures available starting options and text labels based on class rules."""
        if class_type in {ClassType.HERO, ClassType.THIEF}:
            self.radio_b.setText("(b) Gain skill with one weapon you have chosen earlier")
            self.radio_b.setEnabled(True)
            self.radio_d.setVisible(False)
            if class_type == ClassType.HERO:
                self.radio_c.setText("(c) Increase your Magic Resistance by +1")
            else:
                self.radio_c.setText("(c) Increase your Detrap Skill by +1")
            self.radio_c.setEnabled(True)

        elif class_type in {ClassType.WIZARD, ClassType.WITCH_HUNTER, ClassType.HEALER}:
            self.radio_b.setText("(b) Gain skill with one weapon you have chosen earlier")
            self.radio_b.setEnabled(True)
            self.radio_c.setText("(c) Increase your Magic Resistance by +1")
            self.radio_c.setEnabled(True)
            self.radio_d.setText("(d) Learn a second spell")
            self.radio_d.setVisible(True)
            self.radio_d.setEnabled(True)

        elif class_type == ClassType.PEACE_MAKER:
            self.radio_b.setText("(b) Increase Magic Resistance by +1")
            self.radio_b.setEnabled(True)
            self.radio_c.setText("(c) Learn a second spell")
            self.radio_c.setEnabled(True)
            self.radio_d.setVisible(False)

        if not self.radio_a.isChecked() and not self.radio_b.isChecked() and not self.radio_c.isChecked() and not self.radio_d.isChecked():
            self.radio_a.setChecked(True)

    def get_selected_bonus(self) -> str:
        selected_id = self.button_group.checkedId()
        keys = ["a", "b", "c", "d"]
        return keys[selected_id] if 0 <= selected_id < len(keys) else "a"