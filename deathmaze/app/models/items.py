from dataclasses import dataclass
from typing import Optional
from app.models.enums import ClassType, ItemType


ALL_CLASSES: frozenset[ClassType] = frozenset(ClassType)
NON_HERO_THIEF_CLASSES: frozenset[ClassType] = frozenset(
    ct for ct in ClassType if ct not in {ClassType.HERO, ClassType.THIEF}
)


@dataclass(frozen=True)
class ItemDefinition:
    """Static catalog definition of an item in DeathMaze."""
    name: str
    item_type: ItemType
    effect: str
    allowed_classes: frozenset[ClassType] = ALL_CLASSES
    is_consumable: bool = False
    stacks_uses: bool = False
    default_uses: Optional[int] = None
    magic_wound_cost: int = 0


ITEMS_CATALOG: tuple[ItemDefinition, ...] = (
    # --- Rings (All Classes, unique per name, non-stacking) ---
    ItemDefinition(
        name="Resistance +1",
        item_type=ItemType.RING,
        effect="+1 to Magic Resistance",
        allowed_classes=ALL_CLASSES,
        is_consumable=False,
        stacks_uses=False,
        default_uses=None,
    ),
    ItemDefinition(
        name="Resistance +2",
        item_type=ItemType.RING,
        effect="+2 to Magic Resistance",
        allowed_classes=ALL_CLASSES,
        is_consumable=False,
        stacks_uses=False,
        default_uses=None,
    ),
    # --- Spices (All Classes, 1-time use, stacking) ---
    ItemDefinition(
        name="Mustard",
        item_type=ItemType.SPICE,
        effect="Heals 1d6",
        allowed_classes=ALL_CLASSES,
        is_consumable=True,
        stacks_uses=True,
        default_uses=1,
    ),
    ItemDefinition(
        name="Sesame",
        item_type=ItemType.SPICE,
        effect="Detraps Doors or Chests",
        allowed_classes=ALL_CLASSES,
        is_consumable=True,
        stacks_uses=True,
        default_uses=1,
    ),
    ItemDefinition(
        name="Spinach",
        item_type=ItemType.SPICE,
        effect="1d6 Combat Bonus (1 Combat)",
        allowed_classes=ALL_CLASSES,
        is_consumable=True,
        stacks_uses=True,
        default_uses=1,
    ),
    ItemDefinition(
        name="Red Pepper",
        item_type=ItemType.SPICE,
        effect="1d6 Wound to Monster",
        allowed_classes=ALL_CLASSES,
        is_consumable=True,
        stacks_uses=True,
        default_uses=1,
    ),
    ItemDefinition(
        name="Cannabis",
        item_type=ItemType.SPICE,
        effect="Two Attacks on same monster",
        allowed_classes=ALL_CLASSES,
        is_consumable=True,
        stacks_uses=True,
        default_uses=1,
    ),
    ItemDefinition(
        name="Cloves",
        item_type=ItemType.SPICE,
        effect="Locks Doors",
        allowed_classes=ALL_CLASSES,
        is_consumable=True,
        stacks_uses=True,
        default_uses=1,
    ),
    # --- Medallions (All Classes, unique per name, non-stacking) ---
    ItemDefinition(
        name="Neutralize Poison",
        item_type=ItemType.MEDALLION,
        effect="Immunized to Poison",
        allowed_classes=ALL_CLASSES,
        is_consumable=False,
        stacks_uses=False,
        default_uses=None,
    ),
    ItemDefinition(
        name="Potion Appraisal",
        item_type=ItemType.MEDALLION,
        effect="No Need to Test Potion (2 doses)",
        allowed_classes=ALL_CLASSES,
        is_consumable=False,
        stacks_uses=False,
        default_uses=None,
    ),
    ItemDefinition(
        name="Oratory",
        item_type=ItemType.MEDALLION,
        effect="+2 to Negotiation (Cumulative)",
        allowed_classes=ALL_CLASSES,
        is_consumable=False,
        stacks_uses=False,
        default_uses=None,
    ),
    ItemDefinition(
        name="Dexterity",
        item_type=ItemType.MEDALLION,
        effect="+2 Combat Bonus (Bow and Throwing Dagger only)",
        allowed_classes=ALL_CLASSES,
        is_consumable=False,
        stacks_uses=False,
        default_uses=None,
    ),
    # --- Potions (All Classes, 1-time use unless Potion Appraisal active, stacking) ---
    ItemDefinition(
        name="Healing",
        item_type=ItemType.POTION,
        effect="Heals 1d6",
        allowed_classes=ALL_CLASSES,
        is_consumable=True,
        stacks_uses=True,
        default_uses=1,
    ),
    ItemDefinition(
        name="Strength",
        item_type=ItemType.POTION,
        effect="1d6 Combat Bonus (1 Combat)",
        allowed_classes=ALL_CLASSES,
        is_consumable=True,
        stacks_uses=True,
        default_uses=1,
    ),
    ItemDefinition(
        name="Charm Person",
        item_type=ItemType.POTION,
        effect="Hero, Wizard, Thief, Orc, Goblin",
        allowed_classes=ALL_CLASSES,
        is_consumable=True,
        stacks_uses=True,
        default_uses=1,
    ),
    ItemDefinition(
        name="Charm Monster",
        item_type=ItemType.POTION,
        effect="Other Monsters",
        allowed_classes=ALL_CLASSES,
        is_consumable=True,
        stacks_uses=True,
        default_uses=1,
    ),
    # --- Magic Rings (NOT USABLE BY HERO OR THIEF; consumable once/game at 0 wounds; multiple copies allowed, non-stacking) ---
    ItemDefinition(
        name="Sleep",
        item_type=ItemType.MAGIC_RING,
        effect="Remove Monster",
        allowed_classes=NON_HERO_THIEF_CLASSES,
        is_consumable=True,
        stacks_uses=False,
        default_uses=1,
        magic_wound_cost=2,
    ),
    ItemDefinition(
        name="Neutralize Poison",
        item_type=ItemType.MAGIC_RING,
        effect="Cancels Poison Effects",
        allowed_classes=NON_HERO_THIEF_CLASSES,
        is_consumable=True,
        stacks_uses=False,
        default_uses=1,
        magic_wound_cost=1,
    ),
    ItemDefinition(
        name="Heal",
        item_type=ItemType.MAGIC_RING,
        effect="Heals 1d6",
        allowed_classes=NON_HERO_THIEF_CLASSES,
        is_consumable=True,
        stacks_uses=False,
        default_uses=1,
        magic_wound_cost=2,
    ),
    ItemDefinition(
        name="Blast",
        item_type=ItemType.MAGIC_RING,
        effect="2 Damage to Monster (First Row)",
        allowed_classes=NON_HERO_THIEF_CLASSES,
        is_consumable=True,
        stacks_uses=False,
        default_uses=1,
        magic_wound_cost=1,
    ),
)


def get_item_by_name(name: str, item_type: Optional[ItemType] = None) -> Optional[ItemDefinition]:
    """Looks up an item definition by name (and optional ItemType)."""
    for item in ITEMS_CATALOG:
        if item.name.lower() == name.lower():
            if item_type is None or item.item_type == item_type:
                return item
    return None