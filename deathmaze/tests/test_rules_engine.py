import pytest
from app.models.character import Character, Spell, Weapon
from app.models.enums import ClassType, WeaponType
from app.services.rules_engine import RulesEngine


def test_weapon_restrictions():
    """Verify class-based weapon equipping restrictions."""
    hero = Character(name="Conan", class_type=ClassType.HERO)
    wizard = Character(name="Gandalf", class_type=ClassType.WIZARD)
    peacemaker = Character(name="Buddha", class_type=ClassType.PEACE_MAKER)

    sword = Weapon(name=WeaponType.SWORD)
    dagger = Weapon(name=WeaponType.DAGGER)

    # Hero can use both
    assert RulesEngine.can_equip_weapon(hero, sword) is True
    assert RulesEngine.can_equip_weapon(hero, dagger) is True

    # Wizard can use dagger, but not sword
    assert RulesEngine.can_equip_weapon(wizard, dagger) is True
    assert RulesEngine.can_equip_weapon(wizard, sword) is False

    # Peace Maker cannot use any weapons
    assert RulesEngine.can_equip_weapon(peacemaker, dagger) is False
    assert RulesEngine.can_equip_weapon(peacemaker, sword) is False


def test_standard_spell_casting_lock():
    """Verify that standard magic users are locked out of casting if it results in death/0 health."""
    wizard = Character(
        name="Merlin", 
        class_type=ClassType.WIZARD, 
        current_hp=5, 
        magic_wounds=0
    )
    expensive_spell = Spell(
        name="Fireball",
        cost=6,  # Exceeds current HP (5)
        is_combat_spell=True,
        description="Massive fire damage",
        allowed_classes=[ClassType.WIZARD]
    )
    wizard.spells.append(expensive_spell)

    # Should not be able to cast since projected health would be -1
    assert RulesEngine.can_cast_spell(wizard, expensive_spell, target_is_undead=False) is False

    with pytest.raises(ValueError):
        RulesEngine.cast_spell(wizard, expensive_spell, target_is_undead=False)


def test_witch_hunter_undead_exception():
    """Verify Witch Hunters can sacrifice themselves (hp <= 0) to cast combat spells on Undead."""
    witch_hunter = Character(
        name="Van Helsing",
        class_type=ClassType.WITCH_HUNTER,
        current_hp=4,
        magic_wounds=0
    )
    exorcism_spell = Spell(
        name="Divine Smiting",
        cost=5,  # Higher than current_hp (4), would be fatal
        is_combat_spell=True,
        description="Holy damage to undead",
        allowed_classes=[ClassType.WITCH_HUNTER]
    )
    witch_hunter.spells.append(exorcism_spell)

    # Normal target (not undead): should be blocked
    assert RulesEngine.can_cast_spell(witch_hunter, exorcism_spell, target_is_undead=False) is False

    # Undead target: should be allowed under the exception rule
    assert RulesEngine.can_cast_spell(witch_hunter, exorcism_spell, target_is_undead=True) is True

    # Cast successfully and verify character dies from the sacrifice
    RulesEngine.cast_spell(witch_hunter, exorcism_spell, target_is_undead=True)
    assert witch_hunter.magic_wounds == 5
    assert witch_hunter.effective_hp == -1
    assert witch_hunter.is_alive is False