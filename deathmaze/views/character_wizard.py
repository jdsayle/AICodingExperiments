from datetime import datetime
from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QFormLayout, 
    QLineEdit, QComboBox, QLabel, QMessageBox
)
from app.models.enums import ClassType, WeaponType
from app.models.character import Character, Weapon
from app.services.character_manager import CharacterManager
from views.widgets.weapon_selector import WeaponSelectorWidget
from views.widgets.spell_selector import SpellSelectorWidget
from views.widgets.starting_bonus import StartingBonusWidget


class Step1IdentityPage(QWizardPage):
    """Step 1: Character identity and class selection for all classes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 1: Identity & Class Selection")
        self.setSubTitle("Enter character name and choose a class.")

        layout = QFormLayout(self)
        self.name_edit = QLineEdit()
        self.class_combo = QComboBox()

        for c_type in ClassType:
            self.class_combo.addItem(c_type.name.replace('_', ' ').title(), c_type)

        self.created_label = QLabel(datetime.now().strftime("%Y-%m-%d %H:%M"))

        layout.addRow("Character Name:", self.name_edit)
        layout.addRow("Creation Date:", self.created_label)
        layout.addRow("Class:", self.class_combo)

        self.registerField("character_name*", self.name_edit)

    def get_selected_class(self) -> ClassType:
        return self.class_combo.currentData()


class Step2CapabilitiesPage(QWizardPage):
    """Step 2: Dynamic class stats, weapon selection, spells, and starting bonus."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 2: Class Capabilities & Gear")
        self.setSubTitle("Configure weapons, spells, and starting bonuses.")

        self.layout = QVBoxLayout(self)
        self.stats_label = QLabel()
        self.layout.addWidget(self.stats_label)

        # Custom Widgets
        self.weapon_selector = WeaponSelectorWidget()
        self.spell_selector_1 = SpellSelectorWidget(title="Primary Starting Spell")
        self.spell_selector_2 = SpellSelectorWidget(title="Secondary Spell (Option C)")
        self.bonus_widget = StartingBonusWidget()

        self.layout.addWidget(self.weapon_selector)
        self.layout.addWidget(self.spell_selector_1)
        self.layout.addWidget(self.spell_selector_2)
        self.layout.addWidget(self.bonus_widget)

        self.bonus_widget.bonus_changed.connect(self._on_bonus_changed)

    def initializePage(self) -> None:
        wizard = self.wizard()
        step1 = wizard.page(0)
        class_type: ClassType = step1.get_selected_class()

        baselines = {
            ClassType.HERO: "Base Stats: HP: 8 | Magic Resistance: 1 | Weapons: 2",
            ClassType.THIEF: "Base Stats: HP: 6 | Magic Resistance: 1 | Detrap: 1 | Weapons: 2",
            ClassType.WIZARD: "Base Stats: HP: 4 | Magic Resistance: 2 | Weapons: 2 (Daggers/Throwing Daggers)",
            ClassType.WITCH_HUNTER: "Base Stats: HP: 7 | Magic Resistance: 2 | Special: Immune to Vampire Charm",
            ClassType.HEALER: "Base Stats: HP: 4 | Magic Resistance: 1 | Weapons: 1 Dagger",
            ClassType.PEACE_MAKER: "Base Stats: HP: 6 | Magic Resistance: 1 | Negotiation: +4 | Weapons: None",
        }
        self.stats_label.setText(f"<b>{baselines.get(class_type, '')}</b>")

        self.weapon_selector.set_class(class_type)
        self.bonus_widget.set_class(class_type)

        is_magic = class_type in {ClassType.WIZARD, ClassType.WITCH_HUNTER, ClassType.HEALER, ClassType.PEACE_MAKER}
        self.spell_selector_1.setVisible(is_magic)
        if is_magic:
            self.spell_selector_1.set_class(class_type)

        self._on_bonus_changed()

    def _on_bonus_changed(self) -> None:
        step1 = self.wizard().page(0)
        class_type: ClassType = step1.get_selected_class()
        bonus = self.bonus_widget.get_selected_bonus()

        is_magic = class_type in {ClassType.WIZARD, ClassType.WITCH_HUNTER, ClassType.HEALER, ClassType.PEACE_MAKER}
        if is_magic and bonus == "c":
            self.spell_selector_2.setVisible(True)
            self.spell_selector_2.set_class(class_type)
        else:
            self.spell_selector_2.setVisible(False)


class CharacterCreationWizard(QWizard):
    """Universal 2-step character creation wizard for all DeathMaze classes."""

    def __init__(self, manager: CharacterManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("DeathMaze Deluxe - Character Creation Wizard")

        self.step1 = Step1IdentityPage()
        self.step2 = Step2CapabilitiesPage()

        self.addPage(self.step1)
        self.addPage(self.step2)

    def accept(self) -> None:
        name = self.step1.field("character_name")
        class_type = self.step1.get_selected_class()

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