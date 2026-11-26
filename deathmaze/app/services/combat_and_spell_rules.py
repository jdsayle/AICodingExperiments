from app.models.character import Character, Spell, Weapon
from app.models.enums import ClassType, WeaponType


class CombatAndSpellRules:
    """Encapsulates class weapon equip restrictions and spell casting / magic wound rules."""

    CLASS_WEAPON_RESTRICTIONS: dict[ClassType, set[WeaponType]] = {
        ClassType.HERO: {
            WeaponType.SWORD,
            WeaponType.HAMMER,
            WeaponType.AXE,
            WeaponType.BOW_AND_ARROWS,
            WeaponType.DAGGER,
            WeaponType.THROWING_DAGGER,
        },
        ClassType.THIEF: {
            WeaponType.SWORD,
            WeaponType.HAMMER,
            WeaponType.AXE,
            WeaponType.BOW_AND_ARROWS,
            WeaponType.DAGGER,
            WeaponType.THROWING_DAGGER,
        },
        ClassType.WITCH_HUNTER: {
            WeaponType.SWORD,
            WeaponType.HAMMER,
            WeaponType.AXE,
            WeaponType.BOW_AND_ARROWS,
            WeaponType.DAGGER,
            WeaponType.THROWING_DAGGER,
        },
        ClassType.WIZARD: {WeaponType.DAGGER, WeaponType.THROWING_DAGGER},
        ClassType.HEALER: {WeaponType.DAGGER},
        ClassType.PEACE_MAKER: set(),
    }

    @classmethod
    def can_equip_weapon(cls, character: Character, weapon: Weapon) -> bool:
        allowed_types = cls.CLASS_WEAPON_RESTRICTIONS.get(character.class_type, set())
        return weapon.name in allowed_types

    @classmethod
    def can_cast_spell(
        cls,
        character: Character,
        spell: Spell,
        target_is_undead: bool = False,
    ) -> bool:
        if spell not in character.spells:
            return False

        if character.class_type not in spell.allowed_classes:
            return False

        projected_health = character.current_hp - character.magic_wounds - spell.cost

        if projected_health > 0:
            return True

        if (
            character.class_type == ClassType.WITCH_HUNTER
            and spell.is_combat_spell
            and target_is_undead
        ):
            return True

        return False

    @classmethod
    def cast_spell(
        cls,
        character: Character,
        spell: Spell,
        target_is_undead: bool = False,
    ) -> None:
        if not cls.can_cast_spell(character, spell, target_is_undead):
            raise ValueError(f"Character {character.name} cannot cast spell '{spell.name}'.")

        character.magic_wounds += spell.cost

        if character.effective_hp <= 0:
            character.current_hp = max(0, character.current_hp)
            character.is_alive = False