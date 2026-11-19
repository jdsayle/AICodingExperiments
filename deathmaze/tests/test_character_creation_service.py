import pytest
from pathlib import Path
from app.models.character import CharacterCreationConfig, Spell
from app.models.enums import ClassType, WeaponType
from app.services.repository import JsonCharacterRepository
from app.services.character_manager import CharacterManager
from app.services.rules_engine import RulesEngine


@pytest.fixture
def manager(tmp_path: Path):
    repo = JsonCharacterRepository(storage_dir=tmp_path)
    return CharacterManager(repo)


def test_create_hero_with_bonus_a(manager):
    """Verify Hero creation with Option A (+1 HP) using configuration object."""
    config = CharacterCreationConfig(
        name="Sir Boros",
        class_type=ClassType.HERO,
        selected_weapons=[WeaponType.SWORD],
        equipped_weapon=WeaponType.SWORD,
        bonus_option="a"
    )

    char = manager.create_character_from_config(config)

    assert char.name == "Sir Boros"
    assert char.class_type == ClassType.HERO
    assert char.max_hp == 9  # Base 8 + 1
    assert char.current_hp == 9
    assert len(char.weapons) == 1
    assert char.weapons[0].name == WeaponType.SWORD


def test_create_wizard_with_spells_and_bonus(manager):
    """Verify Wizard creation with primary/secondary spells and bonus option D."""
    primary = Spell(name="Blast", cost=1, is_combat_spell=True, description="Test", allowed_classes=[ClassType.WIZARD])
    secondary = Spell(name="Heal", cost=2, is_combat_spell=False, description="Test", allowed_classes=[ClassType.WIZARD])

    config = CharacterCreationConfig(
        name="Elminster",
        class_type=ClassType.WIZARD,
        selected_weapons=[WeaponType.DAGGER],
        equipped_weapon=WeaponType.DAGGER,
        primary_spell=primary,
        secondary_spell=secondary,
        bonus_option="d"
    )

    char = manager.create_character_from_config(config)

    assert char.name == "Elminster"
    assert char.class_type == ClassType.WIZARD
    assert char.max_hp == 4  # Base Wizard HP
    assert primary in char.spells
    assert secondary in char.spells