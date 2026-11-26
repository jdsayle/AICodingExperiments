from pathlib import Path
import pytest

from app.models.character import Character, CharacterCreationConfig, Spell, Weapon
from app.models.enums import ClassType, WeaponType
from app.services.character_creation_rules import CharacterCreationRules
from app.services.character_manager import CharacterManager
from app.services.repository import JsonCharacterRepository


@pytest.fixture
def manager(tmp_path: Path) -> CharacterManager:
    repo = JsonCharacterRepository(storage_dir=tmp_path)
    return CharacterManager(repo)


def test_base_stats_and_magic_user_classification():
    """Verify CharacterCreationRules base stats lookup and magic-user class checks."""
    assert CharacterCreationRules.BASE_STATS[ClassType.HERO]["hp"] == 8
    assert CharacterCreationRules.BASE_STATS[ClassType.THIEF]["detrap"] == 1
    assert CharacterCreationRules.BASE_STATS[ClassType.WIZARD]["mr"] == 2

    assert CharacterCreationRules.is_magic_user_class(ClassType.WIZARD) is True
    assert CharacterCreationRules.is_magic_user_class(ClassType.PEACE_MAKER) is True
    assert CharacterCreationRules.is_magic_user_class(ClassType.HERO) is False
    assert CharacterCreationRules.is_magic_user_class(ClassType.THIEF) is False


def test_initialize_stats_and_starting_bonuses_directly():
    """Verify CharacterCreationRules stat initialization and bonus options."""
    fighter = Character(name="Boros", class_type=ClassType.HERO)
    fighter.weapons = [
        Weapon(name=WeaponType.SWORD),
        Weapon(name=WeaponType.AXE),
    ]
    CharacterCreationRules.initialize_character_stats(fighter, ClassType.HERO)
    assert fighter.max_hp == 8
    assert fighter.current_hp == 8

    bonus_b_cfg = CharacterCreationConfig(
        name="Boros",
        class_type=ClassType.HERO,
        bonus_option="b",
        bonus_weapon_target=WeaponType.AXE,
    )
    CharacterCreationRules.apply_starting_bonuses(fighter, bonus_b_cfg)
    assert fighter.weapons[1].skill_bonus == 1
    assert fighter.weapons[0].skill_bonus == 0


def test_create_hero_with_bonus_a(manager: CharacterManager):
    """Verify Hero creation with Option A (+1 HP) using configuration object."""
    config = CharacterCreationConfig(
        name="Sir Boros",
        class_type=ClassType.HERO,
        selected_weapons=[WeaponType.SWORD],
        equipped_weapon=WeaponType.SWORD,
        bonus_option="a",
    )

    char = manager.create_character_from_config(config)

    assert char.name == "Sir Boros"
    assert char.class_type == ClassType.HERO
    assert char.max_hp == CharacterCreationRules.BASE_STATS[ClassType.HERO]["hp"] + 1
    assert char.current_hp == char.max_hp
    assert len(char.weapons) == 1
    assert char.weapons[0].name == WeaponType.SWORD


def test_create_wizard_with_spells_and_bonus(manager: CharacterManager):
    """Verify Wizard creation with primary/secondary spells and bonus option D."""
    primary = Spell(
        name="Blast",
        cost=1,
        is_combat_spell=True,
        description="Test",
        allowed_classes=[ClassType.WIZARD],
    )
    secondary = Spell(
        name="Heal",
        cost=2,
        is_combat_spell=False,
        description="Test",
        allowed_classes=[ClassType.WIZARD],
    )

    config = CharacterCreationConfig(
        name="Elminster",
        class_type=ClassType.WIZARD,
        selected_weapons=[WeaponType.DAGGER],
        equipped_weapon=WeaponType.DAGGER,
        primary_spell=primary,
        secondary_spell=secondary,
        bonus_option="d",
    )

    char = manager.create_character_from_config(config)

    assert char.name == "Elminster"
    assert char.class_type == ClassType.WIZARD
    assert char.max_hp == CharacterCreationRules.BASE_STATS[ClassType.WIZARD]["hp"]
    assert primary in char.spells
    assert secondary in char.spells