from typing import Dict, List
from app.models.enums import ClassType
from app.models.character import Spell

# Catalog of all DeathMaze Deluxe spells by magic class
WIZARD_SPELLS: List[Spell] = [
    Spell("Blast", cost=1, is_combat_spell=True, description="Target single first row monster. Suffers 2 Wounds unless resisted.", allowed_classes=[ClassType.WIZARD]),
    Spell("Charm", cost=3, is_combat_spell=True, description="Target single monster. If failed resist, joins player party.", allowed_classes=[ClassType.WIZARD]),
    Spell("Explosion", cost=1, is_combat_spell=True, description="All monsters and adventurers suffer 1 wound if fail resist.", allowed_classes=[ClassType.WIZARD]),
    Spell("Lightning", cost=2, is_combat_spell=True, description="Target single monster. Suffers 1D6+2 wounds on fail resist.", allowed_classes=[ClassType.WIZARD]),
    Spell("Heal", cost=2, is_combat_spell=False, description="Heal 1d6 wounds on single character. Cannot heal magic wounds.", allowed_classes=[ClassType.WIZARD]),
    Spell("Lock", cost=1, is_combat_spell=False, description="Lock a door, same as Cloves.", allowed_classes=[ClassType.WIZARD]),
    Spell("Mage Armor", cost=1, is_combat_spell=False, description="Creates 1D3 bonus hit point field against upcoming non-magic wounds.", allowed_classes=[ClassType.WIZARD]),
    Spell("Neutralize Poison", cost=1, is_combat_spell=False, description="Negates poison effects immediately after occurrence.", allowed_classes=[ClassType.WIZARD]),
    Spell("Oratory", cost=1, is_combat_spell=False, description="+4 to negotiation die-roll when attempting monster negotiation.", allowed_classes=[ClassType.WIZARD]),
    Spell("Sleep", cost=2, is_combat_spell=True, description="Monster falls asleep and removed from marching order if fail resist.", allowed_classes=[ClassType.WIZARD]),
    Spell("Strength", cost=2, is_combat_spell=False, description="Adds 1D6 Combat Bonus to player's attack for one combat session.", allowed_classes=[ClassType.WIZARD]),
    Spell("Stone-to-Flesh", cost=3, is_combat_spell=False, description="Returns character turned to stone back to life outside combat.", allowed_classes=[ClassType.WIZARD]),
]

WITCH_HUNTER_SPELLS: List[Spell] = [
    Spell("Protection From Undead", cost=1, is_combat_spell=True, description="Undead that fail resist cannot attack Witch Hunter.", allowed_classes=[ClassType.WITCH_HUNTER]),
    Spell("Light Ray", cost=2, is_combat_spell=True, description="Undead monster suffers 1D6+2 wounds if fails resist.", allowed_classes=[ClassType.WITCH_HUNTER]),
    Spell("Righteous Fury", cost=2, is_combat_spell=True, description="Berserk: +1 to hit in combat, +3 against Undead.", allowed_classes=[ClassType.WITCH_HUNTER]),
    Spell("Redeem Traitor", cost=3, is_combat_spell=True, description="Returns charmed character back to the party.", allowed_classes=[ClassType.WITCH_HUNTER]),
    Spell("Dispell Undead", cost=1, is_combat_spell=True, description="Kills undead target (Cost: 1 Skeletons/Bats, 3 Mummies, 4 Vampires).", allowed_classes=[ClassType.WITCH_HUNTER]),
    Spell("Wrath of God", cost=6, is_combat_spell=True, description="Each attacking monster suffers 2D6+2 Wounds on fail resist.", allowed_classes=[ClassType.WITCH_HUNTER]),
]

HEALER_SPELLS: List[Spell] = [
    Spell("Heal", cost=1, is_combat_spell=False, description="Target immediately cures 1D6 wounds.", allowed_classes=[ClassType.HEALER]),
    Spell("Dispel Poison", cost=1, is_combat_spell=False, description="Nullifies poison damage if cast immediately after poisoning.", allowed_classes=[ClassType.HEALER]),
    Spell("Premonition", cost=1, is_combat_spell=False, description="Immediately detraps any discovered trap.", allowed_classes=[ClassType.HEALER]),
    Spell("Heavy Heal", cost=2, is_combat_spell=False, description="Target immediately cures 2D6+1 wounds.", allowed_classes=[ClassType.HEALER]),
    Spell("Magic Shield", cost=3, is_combat_spell=True, description="Target character becomes immune to damage-causing spells.", allowed_classes=[ClassType.HEALER]),
    Spell("Resurrection", cost=5, is_combat_spell=False, description="Brings recently deceased character back with full HP.", allowed_classes=[ClassType.HEALER]),
]

PEACE_MAKER_SPELLS: List[Spell] = [
    Spell("Sleep", cost=1, is_combat_spell=True, description="Monster falls asleep (monsters get +1 to resist roll).", allowed_classes=[ClassType.PEACE_MAKER]),
    Spell("Cow", cost=2, is_combat_spell=False, description="Forces automatic 'Cow' result on Negotiation Table without resist roll.", allowed_classes=[ClassType.PEACE_MAKER]),
    Spell("Fair Fight", cost=2, is_combat_spell=True, description="Disables monster special abilities and balances numbers.", allowed_classes=[ClassType.PEACE_MAKER]),
    Spell("Hesitate", cost=2, is_combat_spell=True, description="Allows party to cast heal spells and drink potions right before combat.", allowed_classes=[ClassType.PEACE_MAKER]),
    Spell("Cease Fire", cost=3, is_combat_spell=True, description="Acts as 'Agreement' on Negotiation Table during active combat.", allowed_classes=[ClassType.PEACE_MAKER]),
    Spell("Friends", cost=3, is_combat_spell=False, description="Forces monsters to surrender half their Bezants and magic items.", allowed_classes=[ClassType.PEACE_MAKER]),
    Spell("Skin Saver", cost=4, is_combat_spell=False, description="Prevents any dungeon monster from attacking until party attacks.", allowed_classes=[ClassType.PEACE_MAKER]),
]

CLASS_SPELL_POOLS: Dict[ClassType, List[Spell]] = {
    ClassType.WIZARD: WIZARD_SPELLS,
    ClassType.WITCH_HUNTER: WITCH_HUNTER_SPELLS,
    ClassType.HEALER: HEALER_SPELLS,
    ClassType.PEACE_MAKER: PEACE_MAKER_SPELLS,
}


def get_spells_for_class(class_type: ClassType) -> List[Spell]:
    """Returns available spell list for a given class."""
    return CLASS_SPELL_POOLS.get(class_type, [])