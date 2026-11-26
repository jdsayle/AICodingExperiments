from typing import Iterable, List, Optional

from app.models.character import Character, Item
from app.models.enums import ItemType
from app.models.items import ITEMS_CATALOG, ItemDefinition, get_item_by_name


class ItemRules:
    """Encapsulates inventory, stacking, item usage, trading, and Magic Ring rules."""

    MAGIC_RING_WOUND_COSTS: dict[str, int] = {
        "sleep": 2,
        "neutralize poison": 1,
        "heal": 2,
        "blast": 1,
    }

    @classmethod
    def get_magic_ring_wound_cost(cls, item: ItemDefinition) -> int:
        if getattr(item, "magic_wound_cost", 0) > 0:
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
                raise ValueError(
                    f"{character.name} already has {item.item_type.name.replace('_', ' ').title()} '{item.name}'."
                )

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
            new_ring = Item(
                name=item.name,
                item_type=ItemType.MAGIC_RING,
                effect=item.effect,
                uses_remaining=1,
                used_this_game=False,
            )
            character.items.append(new_ring)
            return new_ring

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