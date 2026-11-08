MELEE_WEAPONS = ("Sword", "Hammer", "Axe", "Dagger")
RANGED_WEAPONS = ("Throwing Dagger", "Bow")
WEAPONS = MELEE_WEAPONS + RANGED_WEAPONS
WEAPON_CATALOG = {
    "melee": MELEE_WEAPONS,
    "ranged": RANGED_WEAPONS,
}

CHARACTER_CLASSES = (
    "Hero",
    "Thief",
    "Wizard",
    "Witch Hunter",
    "Healer",
    "Peace Keeper",
    "Charmed Monster",
)
SPELLCASTING_CLASSES = (
    "Wizard",
    "Witch Hunter",
    "Healer",
    "Peace Keeper",
    "Magic-User",
)

# None means that class's weapon restrictions have not been defined yet.
CLASS_WEAPON_OPTIONS: dict[str, tuple[str, ...] | None] = {
    "Hero": WEAPONS,
    "Thief": WEAPONS,
    "Wizard": None,
    "Witch Hunter": None,
    "Healer": None,
    "Peace Keeper": None,
    "Charmed Monster": None,
}

ITEM_CATEGORIES = ("Rings", "Spices", "Medallions", "Potions")
ITEM_OPTIONS: dict[str, tuple[str, ...]] = {
    category: () for category in ITEM_CATEGORIES
}


def weapons_for_class(class_name: str) -> tuple[str, ...]:
    try:
        weapons = CLASS_WEAPON_OPTIONS[class_name]
    except KeyError as error:
        raise ValueError(f"Unknown character class: {class_name}") from error
    if weapons is None:
        raise ValueError(f"Weapon restrictions are not defined for {class_name}.")
    return weapons
