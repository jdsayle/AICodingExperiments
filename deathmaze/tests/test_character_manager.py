import pytest
from pathlib import Path
from app.models.character import CharacterCreationConfig
from app.models.enums import ClassType, WeaponType         
from app.services.repository import JsonCharacterRepository
from app.services.character_manager import CharacterManager


@pytest.fixture
def manager(tmp_path: Path):
    repo = JsonCharacterRepository(storage_dir=tmp_path)
    return CharacterManager(repo)


def test_character_creation_and_unique_names(manager):
    """Verify character creation uniqueness rules and naming constraints."""
    config = CharacterCreationConfig(
        name="Valeria",
        class_type=ClassType.THIEF,
        selected_weapons=[WeaponType.SWORD],
        equipped_weapon=WeaponType.SWORD
    )
    char = manager.create_character_from_config(config)
    assert manager.get_character("Valeria") is not None
    assert char.max_hp == 7  # Base Thief HP plus bonus option (a) att +1 to max HP

    # Duplicate name should raise ValueError
    with pytest.raises(ValueError, match="already exists"):
        manager.create_character_from_config(config)


def test_character_stat_mutations_and_wealth(manager):
    """Verify inventory, currency updates, and stat mutations."""
    config = CharacterCreationConfig(
        name="Thorgar",
        class_type=ClassType.HERO,
        selected_weapons=[WeaponType.AXE],
        equipped_weapon=WeaponType.AXE
    )
    char = manager.create_character_from_config(config)
    
    char.bezants += 50
    char.gems += 2
    assert char.bezants == 50
    assert char.gems == 2


def test_party_recruitment_and_capacity_cap(manager):
    """Verify active party recruitment limits (max 6 characters)."""
    # Create and recruit up to 6 characters
    for i in range(6):
        name = f"Hero{i}"
        config = CharacterCreationConfig(
            name=name,
            class_type=ClassType.HERO,
            selected_weapons=[WeaponType.SWORD],
            equipped_weapon=WeaponType.SWORD
        )
        manager.create_character_from_config(config)
        manager.add_to_party(name)

    active_party = [c for c in manager.list_characters() if c.is_in_party]
    assert len(active_party) == 6

    # Adding a 7th should raise ValueError
    extra_config = CharacterCreationConfig(
        name="Hero7",
        class_type=ClassType.HERO,
        selected_weapons=[WeaponType.SWORD],
        equipped_weapon=WeaponType.SWORD
    )
    manager.create_character_from_config(extra_config)
    
    with pytest.raises(ValueError, match="Active party is full"):
        manager.add_to_party("Hero7")