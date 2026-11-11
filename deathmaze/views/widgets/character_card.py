from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QProgressBar, QGroupBox, QApplication, QSizePolicy, QGraphicsOpacityEffect
)
from PySide6.QtCore import Signal, QSize, QMimeData, Qt, QPoint
from PySide6.QtGui import QDrag
from app.models.character import Character


class CharacterCardWidget(QWidget):
    """Compact interactive visual summary card supporting drag-and-drop tactical reordering."""
    inspect_requested = Signal(str)

    def __init__(self, character: Character, parent=None):
        super().__init__(parent)
        self.character = character
        self._drag_start_position = QPoint()

        # Strict fixed sizing (375x260) to prevent layout shrinkage
        self.setFixedSize(QSize(375, 260))
        self.setMinimumSize(375, 260)
        self.setMaximumSize(375, 260)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setAcceptDrops(False)

        # Setup opacity effect for 50% transparency cue during drag
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity_effect)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        role_badge = "[NPC]" if character.is_npc else "[PC]"
        self.group_box = QGroupBox(f"{role_badge} {character.name} ({character.class_type.name.replace('_', ' ').title()})")
        group_layout = QVBoxLayout(self.group_box)
        group_layout.setContentsMargins(6, 6, 6, 6)
        group_layout.setSpacing(3)

        # Level & XP
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

        # Equipped Weapon & Skill/Combat Bonus
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

        # Known Spells summary
        top_spells = ", ".join(s.name for s in character.spells[:2]) or "None"
        group_layout.addWidget(QLabel(f"<b>Spells:</b> {top_spells}"))

        # View Full Sheet Button
        self.inspect_btn = QPushButton("View Full Sheet")
        self.inspect_btn.setFixedHeight(24)
        self.inspect_btn.clicked.connect(lambda: self.inspect_requested.emit(character.name))
        group_layout.addWidget(self.inspect_btn)

        layout.addWidget(self.group_box)

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

        # Set original card to 50% opacity while dragging
        self.opacity_effect.setOpacity(0.5)

        # Execute drag (blocks until dropped or cancelled)
        drag.exec(Qt.MoveAction)

        # Immediately restore original card to 100% opacity when drag concludes
        self.opacity_effect.setOpacity(1.0)