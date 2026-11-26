from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.models.character import CharacterCreationConfig
from app.models.enums import ClassType, WeaponType
from app.services.character_creation_rules import CharacterCreationRules
from app.services.character_manager import CharacterManager
from views.widgets.spell_selector import SpellSelectorWidget
from views.widgets.starting_bonus import StartingBonusWidget
from views.widgets.weapon_selector import WeaponSelectorWidget


class CreateCharacterTab(QWidget):
    """Dedicated tab view for creating a character with dynamic steps, progress stepper, and centered card layout."""

    character_created = Signal(str)  # Emits new character name upon save
    cancelled = Signal()             # Emits when user cancels or discards

    def __init__(self, manager: CharacterManager, parent=None):
        super().__init__(parent)
        self.manager = manager

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        self.setStyleSheet(self._build_wizard_stylesheet())

        # --- TOP: Dynamic Progress Stepper Indicator ---
        self.stepper_container = QWidget()
        self.stepper_inner_layout = QHBoxLayout(self.stepper_container)
        self.stepper_inner_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stepper_container)

        # --- CENTER: Scrollable Centered Card Container ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")

        card_container = QWidget()
        card_layout = QVBoxLayout(card_container)
        card_layout.setAlignment(Qt.AlignCenter)

        self.card_frame = QFrame()
        self.card_frame.setObjectName("WizardCard")
        self.card_frame.setFixedWidth(540)

        card_inner_layout = QVBoxLayout(self.card_frame)
        self.stack = QStackedWidget()

        # --- PAGE 1: Identity & Class ---
        self.page1 = QWidget()
        p1_layout = QVBoxLayout(self.page1)

        p1_layout.addWidget(QLabel("<h2>Step 1: Identity & Class</h2>"))
        p1_layout.addWidget(QLabel("<font color='#94a3b8'>Choose a unique name and profession for your adventurer.</font>"))
        p1_layout.addSpacing(10)

        p1_layout.addWidget(QLabel("<b>Character Name:</b>"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter a unique character name")
        self.name_input.textChanged.connect(self._validate_step1)
        p1_layout.addWidget(self.name_input)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #f87171; font-weight: bold;")
        p1_layout.addWidget(self.error_label)

        p1_layout.addSpacing(10)
        p1_layout.addWidget(QLabel("<b>Character Class:</b>"))
        self.class_combo = QComboBox()
        self._apply_dark_dropdown_fix(self.class_combo)
        for ct in ClassType:
            self.class_combo.addItem(ct.name.replace("_", " ").title(), ct)
        self.class_combo.currentIndexChanged.connect(self._validate_step1)
        p1_layout.addWidget(self.class_combo)
        p1_layout.addStretch()
        self.stack.addWidget(self.page1)

        # --- PAGE 2: Weapon Selection & Equipment ---
        self.page2 = QWidget()
        p2_layout = QVBoxLayout(self.page2)

        p2_layout.addWidget(QLabel("<h2>Step 2: Weapon & Combat Gear</h2>"))
        p2_layout.addWidget(QLabel("<font color='#94a3b8'>Select starting weapons and choose your equipped weapon.</font>"))
        p2_layout.addSpacing(10)

        self.stats_label = QLabel()
        p2_layout.addWidget(self.stats_label)

        self.weapon_selector = WeaponSelectorWidget()
        self._connect_weapon_checkbox_signals()
        p2_layout.addWidget(self.weapon_selector)

        self.equipped_label = QLabel("<b>Equip Weapon (Required):</b>")
        self.equipped_combo = QComboBox()
        self._apply_dark_dropdown_fix(self.equipped_combo)
        p2_layout.addWidget(self.equipped_label)
        p2_layout.addWidget(self.equipped_combo)

        self.equipped_label.setVisible(False)
        self.equipped_combo.setVisible(False)

        p2_layout.addStretch()
        self.stack.addWidget(self.page2)

        # --- PAGE 3 (Magic Users Only): Spell Selection ---
        self.page3 = QWidget()
        p3_layout = QVBoxLayout(self.page3)

        p3_layout.addWidget(QLabel("<h2>Spell Selection</h2>"))
        p3_layout.addWidget(QLabel("<font color='#94a3b8'>Select your starting magical spells.</font>"))
        p3_layout.addSpacing(10)

        self.spell_selector_1 = SpellSelectorWidget()
        self._style_sub_widgets(self.spell_selector_1)
        p3_layout.addWidget(QLabel("<b>Primary Spell:</b>"))
        p3_layout.addWidget(self.spell_selector_1)
        p3_layout.addStretch()
        self.stack.addWidget(self.page3)

        # --- FINAL PAGE: Starting Bonuses ---
        self.page_final = QWidget()
        p_final_layout = QVBoxLayout(self.page_final)

        p_final_layout.addWidget(QLabel("<h2>Starting Bonuses</h2>"))
        p_final_layout.addWidget(QLabel("<font color='#94a3b8'>Choose your starting advantage or bonus feature.</font>"))
        p_final_layout.addSpacing(10)

        self.bonus_widget = StartingBonusWidget()
        self._style_sub_widgets(self.bonus_widget)
        self.bonus_widget.bonus_changed.connect(self._on_bonus_changed)
        p_final_layout.addWidget(self.bonus_widget)

        self.weapon_label_bonus_b = QLabel("<b>Weapon for Skill Bonus (+1):</b>")
        self.weapon_combo_bonus_b = QComboBox()
        self._apply_dark_dropdown_fix(self.weapon_combo_bonus_b)
        self.weapon_label_bonus_b.setVisible(False)
        self.weapon_combo_bonus_b.setVisible(False)

        p_final_layout.addWidget(self.weapon_label_bonus_b)
        p_final_layout.addWidget(self.weapon_combo_bonus_b)

        self.spell_selector_2 = SpellSelectorWidget()
        self._style_sub_widgets(self.spell_selector_2)
        self.spell_selector_2.setVisible(False)
        self.spell_label_2 = QLabel("<b>Secondary Spell (Bonus Option D / C):</b>")
        self.spell_label_2.setVisible(False)

        p_final_layout.addWidget(self.spell_label_2)
        p_final_layout.addWidget(self.spell_selector_2)
        p_final_layout.addStretch()
        self.stack.addWidget(self.page_final)

        card_inner_layout.addWidget(self.stack)
        card_layout.addWidget(self.card_frame)
        scroll_area.setWidget(card_container)
        main_layout.addWidget(scroll_area)

        # --- DIVIDER LINE ---
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #334155;")
        main_layout.addWidget(line)

        # --- BOTTOM: Sticky Action Footer ---
        footer_layout = QHBoxLayout()

        self.btn_back = QPushButton("< Back")
        self.btn_back.setVisible(False)
        self.btn_back.clicked.connect(self._on_back_clicked)

        self.btn_cancel = QPushButton("Cancel / Discard")
        self.btn_cancel.clicked.connect(self._on_cancel_clicked)

        self.btn_next = QPushButton("Next >")
        self.btn_next.clicked.connect(self._on_next_clicked)

        self.btn_save = QPushButton("Save & Recruit")
        self.btn_save.setVisible(False)
        self.btn_save.clicked.connect(self._on_save_clicked)

        footer_layout.addWidget(self.btn_cancel)
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_back)
        footer_layout.addWidget(self.btn_next)
        footer_layout.addWidget(self.btn_save)

        main_layout.addLayout(footer_layout)

        self._update_stepper_indicators(0)
        self._validate_step1()

    @staticmethod
    def _build_wizard_stylesheet() -> str:
        return """
            QWidget {
                color: #f8fafc;
            }
            QFrame#WizardCard {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 20px;
            }
            QLabel {
                color: #f8fafc;
            }
            QLineEdit, QComboBox {
                background-color: #0f172a;
                color: #f8fafc;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 6px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #475569;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QComboBox QAbstractItemView {
                background-color: #0f172a;
                color: #f8fafc;
                selection-background-color: #38bdf8;
                selection-color: #0f172a;
                border: 1px solid #475569;
            }
            QPushButton {
                background-color: #334155;
                color: #f8fafc;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #475569;
            }
            QPushButton:disabled {
                background-color: #1e293b;
                color: #64748b;
                border: 1px solid #1e293b;
            }
        """

    def _apply_dark_dropdown_fix(self, combo: QComboBox) -> None:
        """Forces QComboBox popup view to adhere to dark theme colors, bypassing native OS style overrides."""
        view = QListView(combo)
        combo.setView(view)
        view.setStyleSheet("""
            QListView {
                background-color: #0f172a;
                color: #f8fafc;
                selection-background-color: #38bdf8;
                selection-color: #0f172a;
                border: 1px solid #475569;
            }
        """)

    def _style_sub_widgets(self, widget: QWidget) -> None:
        """Recursively finds all QComboBox widgets inside sub-components and applies the dark dropdown fix."""
        for combo in widget.findChildren(QComboBox):
            self._apply_dark_dropdown_fix(combo)

    def _connect_weapon_checkbox_signals(self) -> None:
        """Connects checkbox toggles once so selection changes are not handled multiple times."""
        for chk in self.weapon_selector.findChildren(QCheckBox):
            if not chk.property("_weapon_signal_connected"):
                chk.toggled.connect(self._on_weapon_selection_changed)
                chk.setProperty("_weapon_signal_connected", True)

    def _effective_weapons_for_class(self, class_type: ClassType) -> list[WeaponType]:
        """Returns the effective starting weapon list for the given class."""
        if class_type == ClassType.HEALER:
            return [WeaponType.DAGGER]
        if class_type == ClassType.PEACE_MAKER:
            return []
        return list(self.weapon_selector.get_selected_weapons())

    def _requires_secondary_spell(self, class_type: ClassType, bonus_key: str) -> bool:
        """Returns True when the selected class and bonus option grant a secondary spell."""
        if not self._is_magic_user():
            return False
        return bonus_key == "d" or (class_type == ClassType.PEACE_MAKER and bonus_key == "c")

    def _is_magic_user(self) -> bool:
        ct = self.class_combo.currentData()
        return isinstance(ct, ClassType) and CharacterCreationRules.is_magic_user_class(ct)

    def _get_total_steps(self) -> int:
        return 4 if self._is_magic_user() else 3

    def _update_stepper_indicators(self, current_step_idx: int) -> None:
        while self.stepper_inner_layout.count():
            item = self.stepper_inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total = self._get_total_steps()
        step_names = ["Identity & Class", "Weapon & Gear"]
        if total == 4:
            step_names.append("Spell Selection")
        step_names.append("Starting Bonuses")

        for i, name in enumerate(step_names):
            lbl_text = f"<b>{i + 1}. {name}</b>" if i == current_step_idx else f"{i + 1}. {name}"
            lbl = QLabel(lbl_text)
            if i != current_step_idx:
                lbl.setStyleSheet("color: #64748b;")
            else:
                lbl.setStyleSheet("color: #38bdf8; font-weight: bold;")

            self.stepper_inner_layout.addWidget(lbl)

            if i < total - 1:
                arrow = QLabel(">")
                arrow.setStyleSheet("color: #64748b;")
                self.stepper_inner_layout.addWidget(arrow)

        self.stepper_inner_layout.addStretch()

    def _validate_step1(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            self.error_label.setText("Character name is required.")
            self.btn_next.setEnabled(False)
            return

        if self.manager.get_character(name):
            self.error_label.setText("Name already claimed. Please choose a unique name.")
            self.btn_next.setEnabled(False)
            return

        self.error_label.setText("")
        self.btn_next.setEnabled(True)

    def _on_weapon_selection_changed(self) -> None:
        class_type = self.class_combo.currentData()
        if class_type in {ClassType.PEACE_MAKER, ClassType.HEALER}:
            self.equipped_label.setVisible(False)
            self.equipped_combo.setVisible(False)
            self.btn_next.setEnabled(True)
            return

        selected_weapons = self.weapon_selector.get_selected_weapons()
        self.equipped_combo.clear()

        if selected_weapons:
            for w_type in selected_weapons:
                display_name = w_type.name.replace("_", " ").title() if isinstance(w_type, WeaponType) else str(w_type)
                self.equipped_combo.addItem(display_name, w_type)
            self.equipped_label.setVisible(True)
            self.equipped_combo.setVisible(True)
            self.btn_next.setEnabled(True)
        else:
            self.equipped_label.setVisible(False)
            self.equipped_combo.setVisible(False)
            self.btn_next.setEnabled(False)

    def _on_next_clicked(self) -> None:
        name = self.name_input.text().strip()
        if not name or self.manager.get_character(name):
            return

        current_widget = self.stack.currentWidget()
        is_magic = self._is_magic_user()
        class_type = self.class_combo.currentData()

        if current_widget == self.page1:
            base_stats = CharacterCreationRules.BASE_STATS.get(
                class_type, {"hp": 6, "mr": 1, "detrap": 0}
            )
            self.stats_label.setText(
                f"<b>Base Stats:</b> HP: {base_stats['hp']} | "
                f"Magic Resistance: {base_stats['mr']} | "
                f"Detrap Skill: {base_stats['detrap']}"
            )

            if class_type in {ClassType.PEACE_MAKER, ClassType.HEALER}:
                self.weapon_selector.setVisible(False)
                self.equipped_label.setVisible(False)
                self.equipped_combo.setVisible(False)
                self.btn_next.setEnabled(True)
            else:
                self.weapon_selector.setVisible(True)
                self.weapon_selector.set_class(class_type)
                self._connect_weapon_checkbox_signals()
                self._on_weapon_selection_changed()

            self.stack.setCurrentWidget(self.page2)
            self._update_stepper_indicators(1)
            self.btn_back.setVisible(True)

        elif current_widget == self.page2:
            if is_magic:
                self.spell_selector_1.set_class(class_type)
                self._style_sub_widgets(self.spell_selector_1)
                self.stack.setCurrentWidget(self.page3)
                self._update_stepper_indicators(2)
            else:
                self.bonus_widget.configure_for_class(class_type)
                self._style_sub_widgets(self.bonus_widget)
                self._prepare_bonus_b_options()
                self.stack.setCurrentWidget(self.page_final)
                self._update_stepper_indicators(2)
                self.btn_next.setVisible(False)
                self.btn_save.setVisible(True)

        elif current_widget == self.page3 and is_magic:
            self.bonus_widget.configure_for_class(class_type)
            self._style_sub_widgets(self.bonus_widget)
            self._prepare_bonus_b_options()
            self.stack.setCurrentWidget(self.page_final)
            self._update_stepper_indicators(3)
            self.btn_next.setVisible(False)
            self.btn_save.setVisible(True)

    def _prepare_bonus_b_options(self) -> None:
        """Populates the Option B weapon dropdown based on the effective weapons for the class."""
        class_type = self.class_combo.currentData()
        self.weapon_combo_bonus_b.clear()

        weapons_list = self._effective_weapons_for_class(class_type)
        for w_type in weapons_list:
            display_name = w_type.name.replace("_", " ").title() if isinstance(w_type, WeaponType) else str(w_type)
            self.weapon_combo_bonus_b.addItem(display_name, w_type)

        bonus = self.bonus_widget.get_selected_bonus()
        show_bonus_b = bonus == "b" and len(weapons_list) > 1
        self.weapon_label_bonus_b.setVisible(show_bonus_b)
        self.weapon_combo_bonus_b.setVisible(show_bonus_b)

    def _on_back_clicked(self) -> None:
        current_widget = self.stack.currentWidget()
        is_magic = self._is_magic_user()

        if current_widget == self.page_final:
            if is_magic:
                self.stack.setCurrentWidget(self.page3)
                self._update_stepper_indicators(2)
                self.btn_next.setVisible(True)
                self.btn_save.setVisible(False)
            else:
                self.stack.setCurrentWidget(self.page2)
                self._update_stepper_indicators(1)
                self.btn_next.setVisible(True)
                self.btn_save.setVisible(False)
                self._on_weapon_selection_changed()
        elif current_widget == self.page3:
            self.stack.setCurrentWidget(self.page2)
            self._update_stepper_indicators(1)
            self._on_weapon_selection_changed()
        elif current_widget == self.page2:
            self.stack.setCurrentWidget(self.page1)
            self._update_stepper_indicators(0)
            self.btn_back.setVisible(False)
            self.btn_next.setEnabled(True)

    def _on_bonus_changed(self, bonus_key: str) -> None:
        class_type = self.class_combo.currentData()
        weapons_list = self._effective_weapons_for_class(class_type)

        if bonus_key == "b" and len(weapons_list) > 1:
            self.weapon_combo_bonus_b.clear()
            for w_type in weapons_list:
                display_name = w_type.name.replace("_", " ").title() if isinstance(w_type, WeaponType) else str(w_type)
                self.weapon_combo_bonus_b.addItem(display_name, w_type)
            self.weapon_label_bonus_b.setVisible(True)
            self.weapon_combo_bonus_b.setVisible(True)
        else:
            self.weapon_label_bonus_b.setVisible(False)
            self.weapon_combo_bonus_b.setVisible(False)

        needs_secondary_spell = self._requires_secondary_spell(class_type, bonus_key)
        if needs_secondary_spell:
            self.spell_selector_2.set_class(class_type)
            self._style_sub_widgets(self.spell_selector_2)
        self.spell_selector_2.setVisible(needs_secondary_spell)
        self.spell_label_2.setVisible(needs_secondary_spell)

    def _on_cancel_clicked(self) -> None:
        reply = QMessageBox.question(
            self,
            "Discard Changes",
            "Are you sure you want to discard your unsaved character creation changes?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.cancelled.emit()

    def _on_save_clicked(self) -> None:
        name = self.name_input.text().strip()
        class_type = self.class_combo.currentData()

        if self.manager.get_character(name):
            QMessageBox.warning(self, "Name Conflict", f"A character named '{name}' already exists.")
            return

        selected_weapons = self._effective_weapons_for_class(class_type)

        equipped_weapon = None
        if selected_weapons and self.equipped_combo.isVisible():
            equipped_weapon = self.equipped_combo.currentData()

        primary_spell = self.spell_selector_1.get_selected_spell() if self._is_magic_user() else None

        bonus = self.bonus_widget.get_selected_bonus()
        secondary_spell = (
            self.spell_selector_2.get_selected_spell()
            if self._requires_secondary_spell(class_type, bonus)
            else None
        )

        bonus_weapon_target = (
            self.weapon_combo_bonus_b.currentData()
            if bonus == "b" and len(selected_weapons) > 1
            else None
        )

        config = CharacterCreationConfig(
            name=name,
            class_type=class_type,
            selected_weapons=selected_weapons,
            equipped_weapon=equipped_weapon,
            primary_spell=primary_spell,
            secondary_spell=secondary_spell,
            bonus_option=bonus,
            bonus_weapon_target=bonus_weapon_target,
        )

        try:
            char = self.manager.create_character_from_config(config)
            self.character_created.emit(char.name)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save character: {str(e)}")