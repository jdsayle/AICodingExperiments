from typing import Iterable, List, Optional

from app.models.character import Character, Item, Spell, Weapon, CharacterCreationConfig
from app.models.enums import ClassType, ItemType, WeaponType
from app.models.items import ITEMS_CATALOG, ItemDefinition, get_item_by_name


class RulesEngine:
    """Encapsulates core OSR rules for DeathMaze Deluxe including weapon restrictions, spell casting, and item rules."""

    MAGIC_RING_WOUND_COSTS: dict[str, int] = {
        "sleep": 2,
        "neutralize poison": 1,
        "heal": 2,
        "blast": 1,
    }

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
        ClassType.PEACE_MAKER: set(),
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
    def apply_starting_bonuses(cls, character: Character, config: 'CharacterCreationConfig') -> None:
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
        allowed_types = cls.CLASS_WEAPON_RESTRICTIONS.get(character.class_type, set())
        return weapon.name in allowed_types

    @classmethod
    def can_cast_spell(
        cls,
        character: Character,
        spell: Spell,
        target_is_undead: bool = False
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
        target_is_undead: bool = False
    ) -> None:
        if not cls.can_cast_spell(character, spell, target_is_undead):
            raise ValueError(f"Character {character.name} cannot cast spell '{spell.name}'.")

        character.magic_wounds += spell.cost

        if character.effective_hp <= 0:
            character.current_hp = max(0, character.current_hp)
            character.is_alive = False

    # --- Item & Magic Ring Rules ---

    @classmethod
    def get_magic_ring_wound_cost(cls, item: ItemDefinition) -> int:
        if item.magic_wound_cost > 0:
            return item.magic_wound_cost
        return cls.MAGIC_RING_WOUND_COSTS.get(item.name.lower(), 0)

    @classmethod
    def has_active_potion_appraisal(cls, party: Optional[Iterable[Character]]) -> bool:
        if not party:
            return False
        for member in party:
            if not getattr(member, "is_in_party", False):
                continue
            for entry in getattr(member, "items", []):
                if entry.item_type == ItemType.MEDALLION and entry.name.lower() == "potion appraisal":
                    return True
        return False

    @classmethod
    def can_add_item(cls, character: Character, item: ItemDefinition) -> bool:
        """Checks class restrictions and non-consumable uniqueness (Ring & Medallion only once)."""
        if character.class_type not in item.allowed_classes:
            return False

        if item.item_type in {ItemType.RING, ItemType.MEDALLION}:
            already_owned = any(
                existing.item_type == item.item_type and existing.name.lower() == item.name.lower()
                for existing in getattr(character, "items", [])
            )
            if already_owned:
                return False

        return True

    @classmethod
    def get_available_items_for_character(cls, character: Character) -> List[ItemDefinition]:
        return [defn for defn in ITEMS_CATALOG if cls.can_add_item(character, defn)]

    @classmethod
    def can_use_item(
        cls,
        character: Character,
        item: ItemDefinition,
        ring_entry: Optional[Item] = None,
    ) -> bool:
        if character.class_type not in item.allowed_classes:
            return False

        if item.item_type == ItemType.MAGIC_RING:
            if ring_entry is not None:
                if ring_entry.used_this_game:
                    return False
                if ring_entry.uses_remaining is not None and ring_entry.uses_remaining <= 0:
                    return False
                return True

            # Check if at least one unused matching Magic Ring exists in inventory
            unused_rings = [
                existing for existing in getattr(character, "items", [])
                if existing.item_type == ItemType.MAGIC_RING
                and existing.name.lower() == item.name.lower()
                and not existing.used_this_game
                and (existing.uses_remaining is None or existing.uses_remaining > 0)
            ]
            return len(unused_rings) > 0

        return True

    @classmethod
    def grant_item(
        cls,
        character: Character,
        item: ItemDefinition,
        party: Optional[Iterable[Character]] = None,
    ) -> Item:
        """
        Adds an item to a character's inventory:
        - Spice / Potion: stacks uses onto existing matching entry.
          Potions acquire +2 uses when Potion Appraisal is in the active party, else +1 use.
        - Ring / Medallion: unique per name, non-stacking (uses_remaining = None).
        - Magic Ring: allows multiple distinct entries, non-stacking, starts with 1 use (once per game).
        """
        if not hasattr(character, "items"):
            character.items = []

        if item.item_type in {ItemType.RING, ItemType.MEDALLION}:
            already_owned = any(
                existing.item_type == item.item_type and existing.name.lower() == item.name.lower()
                for existing in character.items
            )
            if already_owned:
                raise ValueError(f"{character.name} already has {item.item_type.name.replace('_', ' ').title()} '{item.name}'.")

        if item.item_type == ItemType.POTION:
            effective_party = list(party) if party is not None else [character]
            if character not in effective_party:
                effective_party.append(character)
            uses_to_add = 2 if cls.has_active_potion_appraisal(effective_party) else 1

            existing_potion = next(
                (i for i in character.items if i.item_type == ItemType.POTION and i.name.lower() == item.name.lower()),
                None,
            )
            if existing_potion is not None:
                current_uses = existing_potion.uses_remaining if existing_potion.uses_remaining is not None else 0
                existing_potion.uses_remaining = current_uses + uses_to_add
                return existing_potion

            new_potion = Item(
                name=item.name,
                item_type=ItemType.POTION,
                effect=item.effect,
                uses_remaining=uses_to_add,
                used_this_game=False,
            )
            character.items.append(new_potion)
            return new_potion

        if item.item_type == ItemType.SPICE:
            uses_to_add = item.default_uses if item.default_uses is not None else 1
            existing_spice = next(
                (i for i in character.items if i.item_type == ItemType.SPICE and i.name.lower() == item.name.lower()),
                None,
            )
            if existing_spice is not None:
                current_uses = existing_spice.uses_remaining if existing_spice.uses_remaining is not None else 0
                existing_spice.uses_remaining = current_uses + uses_to_add
                return existing_spice

            new_spice = Item(
                name=item.name,
                item_type=ItemType.SPICE,
                effect=item.effect,
                uses_remaining=uses_to_add,
                used_this_game=False,
            )
            character.items.append(new_spice)
            return new_spice

        if item.item_type == ItemType.MAGIC_RING:
            # Always create a distinct entry (do not stack)
            new_ring = Item(
                name=item.name,
                item_type=ItemType.MAGIC_RING,
                effect=item.effect,
                uses_remaining=1,
                used_this_game=False,
            )
            character.items.append(new_ring)
            return new_ring

        # Ring or Medallion
        new_gear = Item(
            name=item.name,
            item_type=item.item_type,
            effect=item.effect,
            uses_remaining=None,
            used_this_game=False,
        )
        character.items.append(new_gear)
        return new_gear

    @classmethod
    def use_magic_ring(cls, character: Character, ring_entry: Item) -> None:
        """
        Casts the Magic Ring's spell once per game at 0 Magic Wound cost.
        Keeps the ring in inventory so it can be recharged when leaving/re-entering the DeathMaze.
        """
        if ring_entry.item_type != ItemType.MAGIC_RING:
            raise ValueError(f"Item '{ring_entry.name}' is not a Magic Ring.")

        defn = get_item_by_name(ring_entry.name, ItemType.MAGIC_RING)
        if defn is None or not cls.can_use_item(character, defn, ring_entry=ring_entry):
            raise ValueError(
                f"Character {character.name} ({character.class_type.name}) cannot use Magic Ring '{ring_entry.name}'."
            )

        ring_entry.used_this_game = True
        ring_entry.uses_remaining = 0

    @classmethod
    def leave_maze(cls, party: Iterable[Character]) -> List[Character]:
        """
        Resets HP (current_hp = max_hp), clears magic_wounds = 0, and recharges Magic Rings
        (used_this_game = False, uses_remaining = 1) ONLY for living characters in the ACTIVE PARTY.
        """
        reset_characters: List[Character] = []
        for char in party:
            if getattr(char, "is_in_party", False) and getattr(char, "is_alive", False):
                char.current_hp = char.max_hp
                char.magic_wounds = 0
                for item in getattr(char, "items", []):
                    if item.item_type == ItemType.MAGIC_RING:
                        item.used_this_game = False
                        item.uses_remaining = 1
                reset_characters.append(char)
        return reset_characters

    @classmethod
    def consume_item_use(cls, character: Character, entry: Item) -> None:
        """Decrements uses on a consumable Spice or Potion and removes it once exhausted."""
        if entry not in getattr(character, "items", []):
            raise ValueError(f"Item '{entry.name}' not found in {character.name}'s inventory.")

        if entry.item_type == ItemType.MAGIC_RING:
            cls.use_magic_ring(character, entry)
            return

        if entry.item_type not in {ItemType.SPICE, ItemType.POTION}:
            return

        if entry.uses_remaining is None:
            character.items.remove(entry)
            return

        entry.uses_remaining -= 1
        if entry.uses_remaining <= 0:
            character.items.remove(entry)

    @classmethod
    def trade_item(cls, from_char: Character, to_char: Character, entry: Item) -> None:
        """Transfers an item entry from one character's inventory to another's."""
        if entry not in getattr(from_char, "items", []):
            raise ValueError(f"Item '{entry.name}' not found in {from_char.name}'s inventory.")

        if not hasattr(to_char, "items"):
            to_char.items = []

        from_char.items.remove(entry)
        to_char.items.append(entry)