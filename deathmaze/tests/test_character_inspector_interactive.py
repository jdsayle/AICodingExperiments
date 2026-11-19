import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton
from app.models.enums import ClassType, WeaponType
from app.services.repository import JsonCharacterRepository
from app.services.character_manager import CharacterManager
from app.models.character import CharacterCreationConfig, Weapon
from views.widgets.character_inspector import CharacterInspectorWidget


def test_interactive_inspector_stat_mutations(qtbot, tmp_path):
    """Verify that changing values in the interactive inspector updates and persists character state."""
    repo = JsonCharacterRepository(storage_dir=tmp_path / "characters")
    manager = CharacterManager(repo)

    config = CharacterCreationConfig(
        name="TestName",
        class_type=ClassType.HERO,
        selected_weapons=[WeaponType.SWORD],
        equipped_weapon=WeaponType.SWORD
    )
    char = manager.create_character_from_config(config)

    inspector = CharacterInspectorWidget(manager)
    qtbot.addWidget(inspector)
    inspector.set_character(char)

    # Modify HP spinbox
    inspector.hp_spin.setValue(7)
    assert char.current_hp == 7

    # Verify persistence using the correct character name
    reloaded = manager.get_character("TestName")
    assert reloaded.current_hp == 7

    # Modify Bezants
    inspector.bezants_spin.setValue(250)
    assert char.bezants == 250
    assert manager.get_character("TestName").bezants == 250


def test_interactive_inspector_weapon_equipping(qtbot, tmp_path):
    """Verify that clicking 'Equip' on a secondary weapon correctly updates equipped weapon index and persists."""
    repo = JsonCharacterRepository(storage_dir=tmp_path / "characters")
    manager = CharacterManager(repo)

    # Create character with multiple weapons (e.g., Sword and Dagger)
    config = CharacterCreationConfig(
        name="Viggo",
        class_type=ClassType.HERO,
        selected_weapons=[WeaponType.SWORD, WeaponType.DAGGER],
        equipped_weapon=WeaponType.SWORD  # Sword is index 0
    )
    char = manager.create_character_from_config(config)
    assert char.equipped_weapon_index == 0

    inspector = CharacterInspectorWidget(manager)
    qtbot.addWidget(inspector)
    inspector.set_character(char)

    # Find the 'Equip' button for the second weapon (Dagger, index 1)
    equip_buttons = inspector.findChildren(QPushButton)
    equip_button_found = False
    for btn in equip_buttons:
        if btn.text() == "Equip":
            # Click the equip button to switch equipped weapon to index 1
            qtbot.mouseClick(btn, Qt.LeftButton)
            equip_button_found = True
            break

    assert equip_button_found, "Could not find 'Equip' button in inspector layout."

    # Verify character and persistent store reflect the updated equipped weapon index
    assert char.equipped_weapon_index == 1
    reloaded = manager.get_character("Viggo")
    assert reloaded.equipped_weapon_index == 1