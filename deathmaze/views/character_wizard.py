from datetime import datetime
from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
from app.models.character import Character, Weapon, Item
from app.models.enums import ClassType
from app.services.character_manager import CharacterManager
from views.widgets.weapon_selector import WeaponSelectorWidget
from views.widgets.spell_selector import SpellSelectorWidget
from views.widgets.starting_bonus import StartingBonusWidget


class Step1IdentityAndClass(QWizardPage):
    """Wizard Step 1: Character Identity, Class Selection, and Live Unique Name Validation."""

    def __init__(self, manager: CharacterManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setTitle("Step 1: Identity & Class Selection")
        self.setSubTitle("Enter a unique character name and choose your OSR character class.")

        layout = QVBoxLayout(self)

        # Name Input
        layout.addWidget(QLabel("Character Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Please enter a character name")
        self.name_input.textChanged.connect(self.completeChanged)
        layout.addWidget(self.name_input)

        # Duplicate Name / Validation Error Label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        layout.addWidget(self.error_label)

        # Class Selection
        layout.addWidget(QLabel("Character Class:"))
        self.class_combo = QComboBox()
        for ct in ClassType:
            self.class_combo.addItem(ct.name.replace('_', ' ').title(), ct)
        layout.addWidget(self.class_combo)

        # Register fields for QWizard flow
        self.registerField("character_name*", self.name_input)

    def isComplete(self) -> bool:
        """Enforces that the name is non-empty and unique in the repository."""
        name = self.name_input.text().strip()
        if not name:
            self.error_label.setText("")
            return False

        # Check if character name already exists
        if self.manager.get_character(name):
            self.error_label.setText("Name already claimed")
            return False

        self.error_label.setText("")
        return True

    def get_selected_class(self) -> ClassType:
        return self.class_combo.currentData()


class Step2Capabilities(QWizardPage):
    """Wizard Step 2: Dynamic weapons, starting bonuses, and spells configuration."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 2: Capabilities & Equipment")
        self.setSubTitle("Configure your starting weapons, spells, and mutual exclusive bonuses.")

        self.layout = QVBoxLayout(self)

        # Stat Summary Label
        self.stats_label = QLabel()
        self.layout.addWidget(self.stats_label)

        # Weapon Selector Widget
        self.weapon_selector = WeaponSelectorWidget()
        self.layout.addWidget(self.weapon_selector)

        # Spell Selectors (for Magic Users)
        self.spell_selector_1 = SpellSelectorWidget()
        self.spell_selector_2 = SpellSelectorWidget()
        self.spell_selector_1.setVisible(False)
        self.spell_selector_2.setVisible(False)
        
        self.layout.addWidget(QLabel("Primary Spell:"))
        self.layout.addWidget(self.spell_selector_1)
        self.layout.addWidget(QLabel("Secondary Spell (Bonus Option C):"))
        self.layout.addWidget(self.spell_selector_2)

        # Starting Bonus Widget
        self.bonus_widget = StartingBonusWidget()
        self.bonus_widget.bonus_changed.connect(self._on_bonus_changed)
        self.layout.addWidget(self.bonus_widget)

    def initializePage(self) -> None:
        """Dynamically build widgets based on Step 1 class selection."""
        wizard = self.wizard()
        class_type = wizard.step1.get_selected_class()

        base_stats = {
            ClassType.HERO: {"hp": 8, "mr": 1, "detrap": 0},
            ClassType.THIEF: {"hp": 6, "mr": 1, "detrap": 1},
            ClassType.WIZARD: {"hp": 4, "mr": 2, "detrap": 0},
            ClassType.WITCH_HUNTER: {"hp": 7, "mr": 2, "detrap": 0},
            ClassType.HEALER: {"hp": 4, "mr": 1, "detrap": 0},
            ClassType.PEACE_MAKER: {"hp": 6, "mr": 1, "detrap": 0},
        }[class_type]

        stats_text = (
            f"<b>Base Stats:</b> HP: {base_stats['hp']} | "
            f"Magic Resistance: {base_stats['mr']} | "
            f"Detrap Skill: {base_stats['detrap']}"
        )
        self.stats_label.setText(stats_text)

        # Configure Weapon Selector
        self.weapon_selector.set_class(class_type)

        # Configure Spells & Bonuses
        is_magic = class_type in {
            ClassType.WIZARD, ClassType.WITCH_HUNTER, 
            ClassType.HEALER, ClassType.PEACE_MAKER
        }

        if is_magic:
            self.spell_selector_1.set_class(class_type)
            self.spell_selector_1.setVisible(True)
            self.spell_selector_2.set_class(class_type)
            self.spell_selector_2.setVisible(False)  # Hidden unless bonus C is chosen
        else:
            self.spell_selector_1.setVisible(False)
            self.spell_selector_2.setVisible(False)

        self.bonus_widget.configure_for_class(class_type)

    def _on_bonus_changed(self, bonus_key: str) -> None:
        wizard = self.wizard()
        class_type = wizard.step1.get_selected_class()
        is_magic = class_type in {
            ClassType.WIZARD, ClassType.WITCH_HUNTER, 
            ClassType.HEALER, ClassType.PEACE_MAKER
        }
        if is_magic and bonus_key == "c":
            self.spell_selector_2.setVisible(True)
        else:
            self.spell_selector_2.setVisible(False)


class CharacterCreationWizard(QWizard):
    """Universal 2-Step Character Creation Wizard."""

    def __init__(self, manager: CharacterManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("DeathMaze Deluxe - Character Creation")
        self.resize(600, 500)

        self.step1 = Step1IdentityAndClass(manager, self)
        self.step2 = Step2Capabilities(self)

        self.addPage(self.step1)
        self.addPage(self.step2)

    def accept(self) -> None:
        name = self.step1.field("character_name").strip()
        class_type = self.step1.get_selected_class()

        # Final safety check against race conditions or direct inputs
        if self.manager.get_character(name):
            QMessageBox.warning(
                self, 
                "Name Conflict", 
                f"A character named '{name}' already exists. Please choose a unique name."
            )
            self.setCurrentId(0)
            return

        base_stats = {
            ClassType.HERO: {"hp": 8, "mr": 1, "detrap": 0},
            ClassType.THIEF: {"hp": 6, "mr": 1, "detrap": 1},
            ClassType.WIZARD: {"hp": 4, "mr": 2, "detrap": 0},
            ClassType.WITCH_HUNTER: {"hp": 7, "mr": 2, "detrap": 0},
            ClassType.HEALER: {"hp": 4, "mr": 1, "detrap": 0},
            ClassType.PEACE_MAKER: {"hp": 6, "mr": 1, "detrap": 0},
        }[class_type]

        char = Character(
            name=name,
            class_type=class_type,
            max_hp=base_stats["hp"],
            current_hp=base_stats["hp"],
            magic_resistance=base_stats["mr"],
            detrap_skill=base_stats["detrap"],
            created_date=datetime.now().isoformat()
        )

        for w_type in self.step2.weapon_selector.get_selected_weapons():
            char.weapons.append(Weapon(name=w_type))

        bonus = self.step2.bonus_widget.get_selected_bonus()
        if bonus == "a":
            char.max_hp += 1
            char.current_hp += 1
        elif bonus == "b" and char.weapons:
            char.weapons[0].skill_bonus += 1
        elif bonus == "c":
            if class_type in {ClassType.HERO, ClassType.PEACE_MAKER}:
                char.magic_resistance += 1
            elif class_type == ClassType.THIEF:
                char.detrap_skill += 1
            elif char.is_magic_user:
                spell2 = self.step2.spell_selector_2.get_selected_spell()
                if spell2 and spell2 not in char.spells:
                    char.spells.append(spell2)

        if char.is_magic_user:
            spell1 = self.step2.spell_selector_1.get_selected_spell()
            if spell1 and spell1 not in char.spells:
                char.spells.append(spell1)

        try:
            self.manager.repository.save(char)
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save character: {str(e)}")