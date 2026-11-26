from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox
import pytest

from app.models.enums import ClassType
from app.services.character_creation_rules import CharacterCreationRules
from app.services.character_manager import CharacterManager
from app.services.repository import JsonCharacterRepository
from views.widgets.create_character_tab import CreateCharacterTab


@pytest.fixture
def character_tab(qtbot, tmp_path):
    repo = JsonCharacterRepository(storage_dir=tmp_path / "chars")
    manager = CharacterManager(repo)
    tab = CreateCharacterTab(manager)
    qtbot.addWidget(tab)
    tab.show()
    return tab, manager


def test_step2_displays_base_stats_from_character_creation_rules(qtbot, character_tab):
    """Verify advancing to Step 2 shows base stats matching CharacterCreationRules."""
    tab, _ = character_tab

    qtbot.keyClicks(tab.name_input, "Lyra")
    thief_idx = tab.class_combo.findData(ClassType.THIEF)
    tab.class_combo.setCurrentIndex(thief_idx)

    qtbot.mouseClick(tab.btn_next, Qt.LeftButton)
    assert tab.stack.currentWidget() == tab.page2

    expected = CharacterCreationRules.BASE_STATS[ClassType.THIEF]
    stats_text = tab.stats_label.text()
    assert f"HP: {expected['hp']}" in stats_text
    assert f"Magic Resistance: {expected['mr']}" in stats_text
    assert f"Detrap Skill: {expected['detrap']}" in stats_text


def test_full_character_creation_wizard_flow(qtbot, character_tab):
    """Simulate a complete multi-step wizard walkthrough and verify character creation."""
    tab, manager = character_tab

    # --- STEP 1: Identity & Class ---
    qtbot.keyClicks(tab.name_input, "Gideon")
    hero_index = tab.class_combo.findData(ClassType.HERO)
    tab.class_combo.setCurrentIndex(hero_index)

    qtbot.mouseClick(tab.btn_next, Qt.LeftButton)
    assert tab.stack.currentWidget() == tab.page2

    # --- STEP 2: Weapons & Equipment ---
    for chk in tab.weapon_selector.findChildren(QCheckBox):
        if chk.text().lower() == "sword":
            chk.setChecked(True)
            break

    tab._on_weapon_selection_changed()
    assert tab.btn_next.isEnabled()

    qtbot.mouseClick(tab.btn_next, Qt.LeftButton)
    assert tab.stack.currentWidget() == tab.page_final

    # --- FINAL STEP: Save & Recruit ---
    created_names = []
    tab.character_created.connect(lambda name: created_names.append(name))

    qtbot.mouseClick(tab.btn_save, Qt.LeftButton)

    assert "Gideon" in created_names
    saved_char = manager.get_character("Gideon")
    assert saved_char is not None
    assert saved_char.class_type == ClassType.HERO
    # Base Hero HP + default Option A (+1)
    assert saved_char.max_hp == CharacterCreationRules.BASE_STATS[ClassType.HERO]["hp"] + 1