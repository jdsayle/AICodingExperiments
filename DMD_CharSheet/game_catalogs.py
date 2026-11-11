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
SPELL_CATALOG: dict[str, tuple[tuple[str, int], ...]] = {
    "Combat Spells": (
        ("Blast", 1),
        ("Charm", 3),
        ("Explosion", 1),
        ("Lightning", 2),
        ("Sleep", 2),
    ),
    "Non-Combat Spells": (
        ("Heal", 2),
        ("Lock", 1),
        ("Mage Armor", 1),
        ("Neutralize Poison", 1),
        ("Stone-To-Flesh", 3),
        ("Strength", 2),
    ),
    "Negotiation Spells": (("Oratory", 1),),
}
SPELL_COSTS = {
    spell_name: cost
    for spell_entries in SPELL_CATALOG.values()
    for spell_name, cost in spell_entries
}
SPELL_CATEGORIES = {
    spell_name: category
    for category, spell_entries in SPELL_CATALOG.items()
    for spell_name, _cost in spell_entries
}

# None means that class's weapon restrictions have not been defined yet.
CLASS_WEAPON_OPTIONS: dict[str, tuple[str, ...] | None] = {
    "Hero": WEAPONS,
    "Thief": WEAPONS,
    "Wizard": ("Dagger", "Throwing Dagger"),
    "Witch Hunter": None,
    "Healer": None,
    "Peace Keeper": None,
    "Charmed Monster": None,
}

ITEM_CATEGORIES = ("Rings", "Spices", "Medallions", "Potions", "Armor")
ITEM_OPTIONS: dict[str, tuple[str, ...]] = {
    "Rings": ("Resistance +1", "Resistance +2"),
    "Spices": (
        "Mustard",
        "Sesame",
        "Spinach",
        "Red Pepper",
        "Cannabis",
        "Cloves",
    ),
    "Medallions": (
        "Neutralize Poison",
        "Potion Appraisal",
        "Oratory",
        "Dexterity",
    ),
    "Potions": (
        "Healing",
        "Strength",
        "Charm Person",
        "Charm Monster",
    ),
    "Armor": (),
}
RING_RESISTANCE_BONUSES = {"Resistance +1": 1, "Resistance +2": 2}

STARTING_MAGIC_RESISTANCE = {
    "Hero": 1,
    "Thief": 1,
    "Wizard": 2,
    "Witch Hunter": 2,
    "Healer": 1,
    "Peace Keeper": 1,
}


def weapons_for_class(class_name: str) -> tuple[str, ...]:
    try:
        weapons = CLASS_WEAPON_OPTIONS[class_name]
    except KeyError as error:
        raise ValueError(f"Unknown character class: {class_name}") from error
    if weapons is None:
        raise ValueError(f"Weapon restrictions are not defined for {class_name}.")
    return weapons
