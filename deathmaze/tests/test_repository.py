import pytest
from pathlib import Path
from app.models.character import CharacterCreationConfig
from app.models.enums import ClassType, WeaponType
from app.services.repository import JsonCharacterRepository
from app.services.character_manager import CharacterManager


def test_json_repository_crud(tmp_path: Path):
    """Test saving, retrieving, listing, and deleting characters via JsonCharacterRepository."""
    repo = JsonCharacterRepository(storage_dir=tmp_path)
    manager = CharacterManager(repo)

    # Create character via config
    config = CharacterCreationConfig(
        name="Valeria",
        class_type=ClassType.THIEF,
        selected_weapons=[WeaponType.SWORD],
        equipped_weapon=WeaponType.SWORD
    )
    hero = manager.create_character_from_config(config)
    assert manager.get_character("Valeria") is not None

    # Retrieve and check attributes
    fetched = repo.get_by_name("Valeria")
    assert fetched.name == "Valeria"
    assert fetched.class_type == ClassType.THIEF
    assert fetched.max_hp == 7 # base class HP and +1 Max HP health addition from option (a)

    # List all
    all_chars = repo.list_all()
    assert len(all_chars) == 1
    assert all_chars[0].name == "Valeria"

    # Delete
    success = repo.delete("Valeria")
    assert success is True
    assert repo.get_by_name("Valeria") is None
    assert len(repo.list_all()) == 0