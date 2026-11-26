from app.models.character import Character, CharacterCreationConfig
from app.models.enums import ClassType


class CharacterCreationRules:
    """Encapsulates class base stats, magic-user classification, and starting bonus rules."""

    BASE_STATS: dict[ClassType, dict[str, int]] = {
        ClassType.HERO: {"hp": 8, "mr": 1, "detrap": 0},
        ClassType.THIEF: {"hp": 6, "mr": 1, "detrap": 1},
        ClassType.WIZARD: {"hp": 4, "mr": 2, "detrap": 0},
        ClassType.WITCH_HUNTER: {"hp": 7, "mr": 2, "detrap": 0},
        ClassType.HEALER: {"hp": 4, "mr": 1, "detrap": 0},
        ClassType.PEACE_MAKER: {"hp": 6, "mr": 1, "detrap": 0},
    }

    @classmethod
    def is_magic_user_class(cls, class_type: ClassType) -> bool:
        return class_type in Character.MAGIC_USER_CLASSES

    @classmethod
    def initialize_character_stats(cls, character: Character, class_type: ClassType) -> None:
        stats = cls.BASE_STATS.get(class_type, {"hp": 6, "mr": 1, "detrap": 0})
        character.max_hp = stats["hp"]
        character.current_hp = stats["hp"]
        character.magic_resistance = stats["mr"]
        character.detrap_skill = stats["detrap"]

    @classmethod
    def apply_starting_bonuses(cls, character: Character, config: CharacterCreationConfig) -> None:
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