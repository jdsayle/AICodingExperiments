from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QGroupBox, QApplication, QSizePolicy, QGraphicsOpacityEffect
)
from PySide6.QtCore import Signal, QSize, QMimeData, Qt, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QDrag
from app.models.character import Character


class CharacterCardWidget(QWidget):
    """Compact interactive visual summary card supporting drag-and-drop tactical reordering."""
    inspect_requested = Signal(str)
    add_item_requested = Signal(str)
    charm_broken_requested = Signal(str)

    def __init__(self, character: Character, parent=None):
        super().__init__(parent)
        self.character = character
        self._drag_start_position = QPoint()

        self.setFixedSize(QSize(375, 260))
        self.setMinimumSize(375, 260)
        self.setMaximumSize(375, 260)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setAcceptDrops(False)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity_effect)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        if character.is_npc:
            title = f"[CHARMED] {character.name}"
        else:
            title = f"[PC] {character.name} ({character.class_type.name.replace('_', ' ').title()})"

        self.group_box = QGroupBox(title)
        group_layout = QVBoxLayout(self.group_box)
        group_layout.setContentsMargins(6, 6, 6, 6)
        group_layout.setSpacing(3)

        if character.is_npc:
            info_layout = QHBoxLayout()
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.addWidget(QLabel(f"<b>Combat Strength:</b> {character.combat_strength}"))
            info_layout.addStretch()
            group_layout.addLayout(info_layout)
        else:
            info_layout = QHBoxLayout()
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.addWidget(QLabel(f"<b>Level:</b> {character.level}"))
            info_layout.addWidget(QLabel(f"<b>XP:</b> {character.experience}"))
            info_layout.addWidget(QLabel(f"<b>MR:</b> {character.magic_resistance}"))
            if character.detrap_skill > 0:
                info_layout.addWidget(QLabel(f"<b>Detrap:</b> {character.detrap_skill}"))
            group_layout.addLayout(info_layout)

        # HP Bar
        hp_layout = QHBoxLayout()
        hp_layout.setContentsMargins(0, 0, 0, 0)
        hp_layout.addWidget(QLabel("HP:"))
        self.hp_bar = QProgressBar()
        self.hp_bar.setMaximum(character.max_hp)
        self.hp_bar.setValue(character.effective_hp)
        self.hp_bar.setFormat(f"%v / %m (W: {character.magic_wounds})")
        hp_layout.addWidget(self.hp_bar)
        group_layout.addLayout(hp_layout)

        # Weapons / Equipped summary
        if character.is_npc:
            w_names = [w.name.name.replace("_", " ").title() for w in character.weapons[:2]]
            weapons_text = ", ".join(w_names) if w_names else "None"
            group_layout.addWidget(QLabel(f"<b>Weapons:</b> {weapons_text}"))
            group_layout.addStretch()

            self.charm_broken_btn = QPushButton("Charm Broken")
            self.charm_broken_btn.setFixedHeight(24)
            self.charm_broken_btn.clicked.connect(self.fade_out_and_break_charm)
            group_layout.addWidget(self.charm_broken_btn)
        else:
            weapon_display = "None"
            if character.weapons and character.equipped_weapon_index is not None:
                if 0 <= character.equipped_weapon_index < len(character.weapons):
                    w = character.weapons[character.equipped_weapon_index]
                    w_name = w.name.name.replace('_', ' ').title()
                    bonuses = []
                    if w.combat_bonus != 0:
                        bonuses.append(f"C.Bonus: +{w.combat_bonus}")
                    if w.skill_bonus != 0:
                        bonuses.append(f"Skill: +{w.skill_bonus}")
                    bonus_str = f" ({', '.join(bonuses)})" if bonuses else ""
                    weapon_display = f"{w_name}{bonus_str}"
            elif character.weapons:
                w = character.weapons[0]
                weapon_display = w.name.name.replace('_', ' ').title()
            group_layout.addWidget(QLabel(f"<b>Equipped:</b> {weapon_display}"))

            top_spells = ", ".join(s.name for s in character.spells[:2]) or "None"
            group_layout.addWidget(QLabel(f"<b>Spells:</b> {top_spells}"))

            btn_row = QHBoxLayout()
            btn_row.setContentsMargins(0, 0, 0, 0)
            btn_row.setSpacing(4)

            self.inspect_btn = QPushButton("View Full Sheet")
            self.inspect_btn.setFixedHeight(24)
            self.inspect_btn.clicked.connect(lambda: self.inspect_requested.emit(character.name))

            self.item_btn = QPushButton("Item")
            self.item_btn.setFixedHeight(24)
            self.item_btn.setFixedWidth(64)
            self.item_btn.clicked.connect(lambda: self.add_item_requested.emit(character.name))

            btn_row.addWidget(self.inspect_btn)
            btn_row.addWidget(self.item_btn)
            group_layout.addLayout(btn_row)

        layout.addWidget(self.group_box)

    def fade_out_and_break_charm(self) -> None:
        self.setEnabled(False)
        anim = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        anim.setDuration(250)
        anim.setStartValue(self.opacity_effect.opacity())
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)

        def _finished() -> None:
            self.charm_broken_requested.emit(self.character.name)

        anim.finished.connect(_finished)
        self._fade_anim = anim
        anim.start()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if not (event.buttons() & Qt.LeftButton):
            return

        distance = (event.position().toPoint() - self._drag_start_position).manhattanLength()
        if distance < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.character.name)
        drag.setMimeData(mime_data)

        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint())

        self.opacity_effect.setOpacity(0.5)
        drag.exec(Qt.MoveAction)
        self.opacity_effect.setOpacity(1.0)