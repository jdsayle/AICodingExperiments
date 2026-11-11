from app.models.character import Character, Spell, Weapon
from app.models.enums import ClassType, WeaponType


class RulesEngine:
    """Encapsulates core OSR rules for DeathMaze Deluxe including weapon restrictions and spell casting validation."""

    # Allowed weapon types per class rules
    CLASS_WEAPON_RESTRICTIONS = {
        ClassType.HERO: {
            WeaponType.SWORD, WeaponType.HAMMER, WeaponType.AXE,
            WeaponType.BOW_AND_ARROWS, WeaponType.DAGGER, WeaponType.THROWING_DAGGER
        },
        ClassType.THIEF: {
            WeaponType.SWORD, WeaponType.HAMMER, WeaponType.AXE,
            WeaponType.BOW_AND_ARROWS, WeaponType.DAGGER, WeaponType.THROWING_DAGGER
        },
        ClassType.WITCH_HUNTER: {
            WeaponType.SWORD, WeaponType.HAMMER, WeaponType.AXE,
            WeaponType.BOW_AND_ARROWS, WeaponType.DAGGER, WeaponType.THROWING_DAGGER
        },
        ClassType.WIZARD: {WeaponType.DAGGER, WeaponType.THROWING_DAGGER},
        ClassType.HEALER: {WeaponType.DAGGER},
        ClassType.PEACE_MAKER: set(),  # Peace makers cannot use weapons
    }

    @classmethod
    def can_equip_weapon(cls, character: Character, weapon: Weapon) -> bool:
        """Validates whether a character class is permitted to use the specified weapon type."""
        allowed_types = cls.CLASS_WEAPON_RESTRICTIONS.get(character.class_type, set())
        return weapon.name in allowed_types

    @classmethod
    def can_cast_spell(
        cls, 
        character: Character, 
        spell: Spell, 
        target_is_undead: bool = False
    ) -> bool:
        """
        Validates if a character can cast a specific spell.
        
        Rules:
        - Character must know/possess the spell and belong to an allowed class.
        - Standard check: current_hp - magic_wounds - spell.cost > 0.
        - Witch Hunter Exception: Witch Hunters CAN cast an attack spell against Undead targets 
          even if it results in health dropping to 0 or less (suicidal/sacrificial spell).
        """
        if spell not in character.spells:
            return False
            
        if character.class_type not in spell.allowed_classes:
            return False

        projected_health = character.current_hp - character.magic_wounds - spell.cost

        # Standard check: must keep health strictly above 0
        if projected_health > 0:
            return True

        # Witch Hunter Undead Exception Rule
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
        target_is_undead: bool = False
    ) -> None:
        """
        Executes a spell cast, applying magic wounds and handling character death/status updates.
        Raises ValueError if casting is invalid.
        """
        if not cls.can_cast_spell(character, spell, target_is_undead):
            raise ValueError(f"Character {character.name} cannot cast spell '{spell.name}'.")

        character.magic_wounds += spell.cost

        # If effective health drops to 0 or below, mark character as dead
        if character.effective_hp <= 0:
            character.current_hp = max(0, character.current_hp)
            character.is_alive = False