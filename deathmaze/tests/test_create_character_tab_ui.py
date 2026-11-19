import pytest
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox
from app.models.enums import ClassType
from app.services.repository import JsonCharacterRepository
from app.services.character_manager import CharacterManager
from views.widgets.create_character_tab import CreateCharacterTab


@pytest.fixture
def character_tab(qtbot, tmp_path: Path):
    repo = JsonCharacterRepository(storage_dir=tmp_path)
    manager = CharacterManager(repo)
    tab = CreateCharacterTab(manager)
    qtbot.addWidget(tab)
    return tab, manager


def test_wizard_step1_validation(qtbot, character_tab):
    """Verify that Step 1 correctly validates name input and enables/disables the Next button."""
    tab, manager = character_tab

    # Initially empty name should disable Next button and show error
    assert not tab.btn_next.isEnabled()
    assert tab.error_label.text() == "Character name is required."

    # Type a valid unique name
    qtbot.keyClicks(tab.name_input, "Aria")
    assert tab.btn_next.isEnabled()
    assert tab.error_label.text() == ""


def test_full_character_creation_wizard_flow(qtbot, character_tab):
    """Simulate a complete multi-step wizard walkthrough and verify character creation."""
    tab, manager = character_tab

    # --- STEP 1: Identity & Class ---
    qtbot.keyClicks(tab.name_input, "Gideon")
    
    # Select 'HERO' in class dropdown
    hero_index = tab.class_combo.findData(ClassType.HERO)
    tab.class_combo.setCurrentIndex(hero_index)

    # Click Next to go to Step 2 (Weapon & Gear)
    qtbot.mouseClick(tab.btn_next, Qt.LeftButton)
    assert tab.stack.currentWidget() == tab.page2

    # --- STEP 2: Weapons & Equipment ---
    # Select a weapon checkbox inside the weapon selector
    for chk in tab.weapon_selector.findChildren(QCheckBox):
        if chk.text().lower() == "sword":
            chk.setChecked(True)
            break

    # Trigger weapon selection changed update
    tab._on_weapon_selection_changed()
    assert tab.btn_next.isEnabled()

    # Click Next to go to Final Step (Starting Bonuses)
    qtbot.mouseClick(tab.btn_next, Qt.LeftButton) # leaves the default selection (a) increase Max HP +1
    assert tab.stack.currentWidget() == tab.page_final

    # --- FINAL STEP: Save & Recruit ---
    # Track signal emission
    created_names = []
    tab.character_created.connect(lambda name: created_names.append(name))

    # Click Save & Recruit button
    qtbot.mouseClick(tab.btn_save, Qt.LeftButton)

    # Verify character was created and emitted
    assert "Gideon" in created_names
    saved_char = manager.get_character("Gideon")
    assert saved_char is not None
    assert saved_char.class_type == ClassType.HERO
    assert saved_char.max_hp == 9  # Base Hero HP (8) + Option A (+1) = 9