import pytest
from PySide6.QtCore import Qt
from app.models.enums import ClassType, WeaponType
from app.services.repository import JsonCharacterRepository
from app.services.character_manager import CharacterManager
from views.character_wizard import CharacterCreationWizard


@pytest.fixture
def manager(tmp_path):
    repo = JsonCharacterRepository(storage_dir=tmp_path)
    return CharacterManager(repo)


def test_wizard_creation_hero(qtbot, manager):
    """Verify 2-step creation wizard for a Hero."""
    wizard = CharacterCreationWizard(manager)
    qtbot.addWidget(wizard)
    wizard.show()

    wizard.step1.name_edit.setText("Thorin")
    wizard.step1.class_combo.setCurrentIndex(0)  # HERO
    wizard.next()

    cb_sword = next(cb for cb in wizard.step2.weapon_selector.checkboxes if cb.property("weapon_type") == WeaponType.SWORD)
    cb_sword.setChecked(True)
    wizard.step2.bonus_widget.radio_a.setChecked(True)
    wizard.accept()

    saved = manager.get_character("Thorin")
    assert saved is not None
    assert saved.class_type == ClassType.HERO
    assert saved.max_hp == 9
    assert len(saved.weapons) == 1


def test_wizard_creation_wizard_class(qtbot, manager):
    """Verify 2-step creation wizard for a Wizard with spell selection."""
    wizard = CharacterCreationWizard(manager)
    qtbot.addWidget(wizard)
    wizard.show()

    wizard.step1.name_edit.setText("Gandalf")
    wizard.step1.class_combo.setCurrentIndex(2)  # WIZARD
    wizard.next()

    assert wizard.step2.spell_selector_1.isVisible() is True
    wizard.step2.bonus_widget.radio_c.setChecked(True)
    assert wizard.step2.spell_selector_2.isVisible() is True
    wizard.accept()

    saved = manager.get_character("Gandalf")
    assert saved is not None
    assert saved.class_type == ClassType.WIZARD
    assert saved.is_magic_user is True
    assert len(saved.spells) >= 1