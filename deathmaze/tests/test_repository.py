import pytest
from pathlib import Path
from app.models.character import Character, Weapon, Item, Spell
from app.models.enums import ClassType, ItemType, WeaponType
from app.services.persistence import CharacterSerializer
from app.services.repository import JsonCharacterRepository
from app.services.character_manager import CharacterManager


def test_character_serialization_roundtrip():
    """Verify that serializing and deserializing a fully loaded character preserves all fields."""
    char = Character(
        name="Sir Arthur",
        class_type=ClassType.HERO,
        level=2,
        max_hp=15,
        current_hp=12,
        magic_wounds=2,
        magic_resistance=3,
        detrap_skill=1,
        bezants=100,
        gems=5
    )
    char.weapons.append(Weapon(name=WeaponType.SWORD, is_magical=True, combat_bonus=2))
    char.items.append(Item(name="Healing Potion", item_type=ItemType.POTION, charges_remaining=1))
    char.spells.append(Spell(name="Light", cost=1, is_combat_spell=False, description="Illumination", allowed_classes=[ClassType.HERO]))

    json_data = CharacterSerializer.to_json(char)
    reconstructed = CharacterSerializer.from_json(json_data)

    assert reconstructed.name == char.name
    assert reconstructed.class_type == char.class_type
    assert reconstructed.level == char.level
    assert reconstructed.max_hp == char.max_hp
    assert reconstructed.current_hp == char.current_hp
    assert reconstructed.magic_wounds == char.magic_wounds
    assert reconstructed.bezants == char.bezants
    assert len(reconstructed.weapons) == 1
    assert reconstructed.weapons[0].name == WeaponType.SWORD
    assert reconstructed.weapons[0].is_magical is True
    assert len(reconstructed.items) == 1
    assert reconstructed.items[0].item_type == ItemType.POTION
    assert len(reconstructed.spells) == 1
    assert reconstructed.spells[0].name == "Light"


def test_json_repository_crud(tmp_path: Path):
    """Test saving, retrieving, listing, and deleting characters via JsonCharacterRepository."""
    repo = JsonCharacterRepository(storage_dir=tmp_path)
    manager = CharacterManager(repo)

    # Create character
    hero = manager.create_character("Valeria", ClassType.THIEF, max_hp=12)
    assert manager.get_character("Valeria") is not None

    # Retrieve and check attributes
    fetched = repo.get_by_name("Valeria")
    assert fetched.name == "Valeria"
    assert fetched.class_type == ClassType.THIEF
    assert fetched.max_hp == 12

    # List all
    all_chars = repo.list_all()
    assert len(all_chars) == 1
    assert all_chars[0].name == "Valeria"

    # Delete
    success = repo.delete("Valeria")
    assert success is True
    assert repo.get_by_name("Valeria") is None
    assert len(repo.list_all()) == 0