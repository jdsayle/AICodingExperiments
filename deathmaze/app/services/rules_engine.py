from app.models.character import Character, Spell, Weapon, CharacterCreationConfig
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

    BASE_STATS = {
        ClassType.HERO: {"hp": 8, "mr": 1, "detrap": 0},
        ClassType.THIEF: {"hp": 6, "mr": 1, "detrap": 1},
        ClassType.WIZARD: {"hp": 4, "mr": 2, "detrap": 0},
        ClassType.WITCH_HUNTER: {"hp": 7, "mr": 2, "detrap": 0},
        ClassType.HEALER: {"hp": 4, "mr": 1, "detrap": 0},
        ClassType.PEACE_MAKER: {"hp": 6, "mr": 1, "detrap": 0},
    }

    @classmethod
    def initialize_character_stats(cls, character: Character, class_type: ClassType) -> None:
        """Applies base stats based on class type rules."""
        stats = cls.BASE_STATS.get(class_type, {"hp": 6, "mr": 1, "detrap": 0})
        character.max_hp = stats["hp"]
        character.current_hp = stats["hp"]
        character.magic_resistance = stats["mr"]
        character.detrap_skill = stats["detrap"]

    @classmethod
    def apply_starting_bonuses(cls, character: Character, config: 'CharacterCreationConfig') -> None:
        """Applies starting bonuses (A, B, C, D) using RulesEngine logic."""
        bonus = config.bonus_option.lower()
        
        if bonus == "a":
            character.max_hp += 1
            character.current_hp += 1
        elif bonus == "b":
            if character.class_type == ClassType.PEACE_MAKER:
                character.magic_resistance += 1
            elif len(character.weapons) == 1:
                character.weapons[0].skill_bonus += 1
            elif len(character.weapons) > 1 and config.bonus_weapon_target:
                matched = False
                for w in character.weapons:
                    if w.name == config.bonus_weapon_target:
                        w.skill_bonus += 1
                        matched = True
                        break
                if not matched and character.weapons:
                    character.weapons[0].skill_bonus += 1
            elif character.weapons:
                character.weapons[0].skill_bonus += 1
        elif bonus == "c":
            if character.class_type in {ClassType.HERO, ClassType.WITCH_HUNTER, ClassType.HEALER}:
                character.magic_resistance += 1
            elif character.class_type == ClassType.THIEF:
                character.detrap_skill += 1
            elif character.class_type == ClassType.WIZARD:
                character.magic_resistance += 1
            elif character.class_type == ClassType.PEACE_MAKER and config.secondary_spell:
                if config.secondary_spell not in character.spells:
                    character.spells.append(config.secondary_spell)
        elif bonus == "d":
            if character.is_magic_user and config.secondary_spell:
                if config.secondary_spell not in character.spells:
                    character.spells.append(config.secondary_spell)

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