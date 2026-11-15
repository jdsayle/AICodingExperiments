import pytest
from PySide6.QtCore import Qt
from app.models.enums import ClassType, WeaponType
from app.services.repository import JsonCharacterRepository
from app.services.character_manager import CharacterManager
from views.widgets.character_inspector import CharacterInspectorWidget


def test_interactive_inspector_stat_mutations(qtbot, tmp_path):
    """Verify that changing values in the interactive inspector updates and persists character state."""
    repo = JsonCharacterRepository(storage_dir=tmp_path / "characters")
    manager = CharacterManager(repo)
    
    char = manager.create_character("Aragorn", ClassType.HERO, max_hp=10)
    inspector = CharacterInspectorWidget(manager)
    qtbot.addWidget(inspector)

    inspector.set_character(char)

    # Modify HP spinbox
    inspector.hp_spin.setValue(7)
    assert char.current_hp == 7

    # Verify persistence
    reloaded = manager.get_character("Aragorn")
    assert reloaded.current_hp == 7

    # Modify Bezants
    inspector.bezants_spin.setValue(250)
    assert char.bezants == 250
    assert manager.get_character("Aragorn").bezants == 250