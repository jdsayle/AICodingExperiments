import pytest
from pathlib import Path
from app.models.character import Character, Weapon, Item
from app.models.enums import ClassType, ItemType, WeaponType
from app.services.repository import JsonCharacterRepository
from app.services.character_manager import CharacterManager


@pytest.fixture
def manager(tmp_path):
    repo = JsonCharacterRepository(storage_dir=tmp_path / "characters")
    return CharacterManager(repo)


def test_character_creation_and_unique_names(manager):
    """Verify character creation enforces unique names and initializes stats correctly."""
    char1 = manager.create_character("Thor", ClassType.HERO, max_hp=10)
    assert char1.name == "Thor"
    assert char1.current_hp == 10
    assert char1.max_hp == 10

    # Attempting to create duplicate name should raise ValueError
    with pytest.raises(ValueError):
        manager.create_character("Thor", ClassType.THIEF)


def test_character_stat_mutations_and_wealth(manager):
    """Verify health changes, magic wounds, experience, and currency updates persist correctly."""
    char = manager.create_character("Loki", ClassType.WIZARD, max_hp=8)
    
    # Simulate taking damage and adding magic wounds
    char.current_hp = 6
    char.magic_wounds = 2
    assert char.effective_hp == 4

    # Update wealth and XP
    char.bezants = 150
    char.gems = 3
    char.experience = 250
    manager.repository.save(char)

    # Reload from repository to verify persistence
    reloaded = manager.get_character("Loki")
    assert reloaded.current_hp == 6
    assert reloaded.magic_wounds == 2
    assert reloaded.effective_hp == 4
    assert reloaded.bezants == 150
    assert reloaded.gems == 3
    assert reloaded.experience == 250


def test_party_recruitment_and_capacity_cap(manager):
    """Verify active party recruitment respects the maximum limit of 6 player characters."""
    # Create 7 characters
    for i in range(7):
        manager.create_character(f"Hero_{i}", ClassType.HERO)

    # Recruit first 6 into party
    for i in range(6):
        manager.add_to_party(f"Hero_{i}")

    active_party = [c for c in manager.list_characters() if c.is_in_party]
    assert len(active_party) == 6

    # Adding the 7th should raise a ValueError due to party being full
    with pytest.raises(ValueError):
        manager.add_to_party("Hero_6")

def test_character_retirement_and_effective_hp():
    """Verify character effective HP calculation with magic wounds and retirement status."""
    char = Character(
        name="Sir Reginald",
        class_type=ClassType.HERO,
        max_hp=12,
        current_hp=10,
        magic_wounds=3
    )
    # Effective HP should be current_hp (10) - magic_wounds (3) = 7
    assert char.effective_hp == 7
    
    # Verify retirement flag initialization and state change
    assert char.is_retired is False
    char.is_retired = True
    assert char.is_retired is True