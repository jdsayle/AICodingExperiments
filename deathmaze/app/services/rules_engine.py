from typing import Iterable, List, Optional

from app.models.character import Character, Item, Spell, Weapon, CharacterCreationConfig
from app.models.enums import ClassType, ItemType, WeaponType
from app.models.items import ITEMS_CATALOG, ItemDefinition, get_item_by_name
from app.services.item_rules import ItemRules
from app.services.party_rules import PartyRules
from app.services.character_creation_rules import CharacterCreationRules
from app.services.combat_and_spell_rules import CombatAndSpellRules

class RulesEngine:
    """Encapsulates core OSR rules for DeathMaze Deluxe including weapon restrictions, spell casting, and item rules."""

    MAGIC_RING_WOUND_COSTS: dict[str, int] = {
        "sleep": 2,
        "neutralize poison": 1,
        "heal": 2,
        "blast": 1,
    }

    # --- Weapon & Spell Rules (Forwarded to CombatAndSpellRules) ---

    CLASS_WEAPON_RESTRICTIONS = CombatAndSpellRules.CLASS_WEAPON_RESTRICTIONS

    @classmethod
    def can_equip_weapon(cls, character: Character, weapon: Weapon) -> bool:
        return CombatAndSpellRules.can_equip_weapon(character, weapon)

    @classmethod
    def can_cast_spell(
        cls,
        character: Character,
        spell: Spell,
        target_is_undead: bool = False,
    ) -> bool:
        return CombatAndSpellRules.can_cast_spell(
            character,
            spell,
            target_is_undead=target_is_undead,
        )

    @classmethod
    def cast_spell(
        cls,
        character: Character,
        spell: Spell,
        target_is_undead: bool = False,
    ) -> None:
        return CombatAndSpellRules.cast_spell(
            character,
            spell,
            target_is_undead=target_is_undead,
        )

    # --- Character Creation & Starting Bonus Rules (Forwarded to CharacterCreationRules) ---

    BASE_STATS = CharacterCreationRules.BASE_STATS

    @classmethod
    def is_magic_user_class(cls, class_type: ClassType) -> bool:
        return CharacterCreationRules.is_magic_user_class(class_type)

    @classmethod
    def initialize_character_stats(cls, character: Character, class_type: ClassType) -> None:
        return CharacterCreationRules.initialize_character_stats(character, class_type)

    @classmethod
    def apply_starting_bonuses(cls, character: Character, config: "CharacterCreationConfig") -> None:
        return CharacterCreationRules.apply_starting_bonuses(character, config)
    

    CHARMED_ALLOWED_WEAPONS: tuple[WeaponType, ...] = (
        WeaponType.SWORD,
        WeaponType.DAGGER,
        WeaponType.BOW_AND_ARROWS,
    )

    # --- Item & Magic Ring Rules (Forwarded to ItemRules) ---

    MAGIC_RING_WOUND_COSTS = ItemRules.MAGIC_RING_WOUND_COSTS

    @classmethod
    def get_magic_ring_wound_cost(cls, item: ItemDefinition) -> int:
        return ItemRules.get_magic_ring_wound_cost(item)

    @classmethod
    def has_active_potion_appraisal(cls, party: Optional[Iterable[Character]]) -> bool:
        return ItemRules.has_active_potion_appraisal(party)

    @classmethod
    def can_add_item(cls, character: Character, item: ItemDefinition) -> bool:
        return ItemRules.can_add_item(character, item)

    @classmethod
    def get_available_items_for_character(cls, character: Character) -> List[ItemDefinition]:
        return ItemRules.get_available_items_for_character(character)

    @classmethod
    def can_use_item(
        cls,
        character: Character,
        item: ItemDefinition,
        ring_entry: Optional[Item] = None,
    ) -> bool:
        return ItemRules.can_use_item(character, item, ring_entry=ring_entry)

    @classmethod
    def grant_item(
        cls,
        character: Character,
        item: ItemDefinition,
        party: Optional[Iterable[Character]] = None,
    ) -> Item:
        return ItemRules.grant_item(character, item, party=party)

    @classmethod
    def use_magic_ring(cls, character: Character, ring_entry: Item) -> None:
        return ItemRules.use_magic_ring(character, ring_entry)

    @classmethod
    def consume_item_use(cls, character: Character, entry: Item) -> None:
        return ItemRules.consume_item_use(character, entry)

    @classmethod
    def trade_item(cls, from_char: Character, to_char: Character, entry: Item) -> None:
        return ItemRules.trade_item(from_char, to_char, entry)

    
    # --- Party, Charmed NPC & Leave Maze Rules (Forwarded to PartyRules) ---

    CHARMED_ALLOWED_WEAPONS = PartyRules.CHARMED_ALLOWED_WEAPONS

    @classmethod
    def get_first_open_party_slot(
        cls,
        party: Iterable[Character],
        exclude_name: Optional[str] = None,
    ) -> Optional[tuple[int, int]]:
        return PartyRules.get_first_open_party_slot(party, exclude_name=exclude_name)

    @classmethod
    def validate_add_charmed_npc(
        cls,
        party: Iterable[Character],
        name: str,
        current_hp: int,
        max_hp: int,
        combat_strength: int,
        weapons: Optional[List[Weapon]] = None,
    ) -> None:
        return PartyRules.validate_add_charmed_npc(
            party=party,
            name=name,
            current_hp=current_hp,
            max_hp=max_hp,
            combat_strength=combat_strength,
            weapons=weapons,
        )

    @classmethod
    def create_charmed_npc(
        cls,
        party: Iterable[Character],
        name: str,
        current_hp: int,
        max_hp: int,
        combat_strength: int,
        weapon_types: Optional[List[WeaponType]] = None,
    ) -> Character:
        return PartyRules.create_charmed_npc(
            party=party,
            name=name,
            current_hp=current_hp,
            max_hp=max_hp,
            combat_strength=combat_strength,
            weapon_types=weapon_types,
        )

    @classmethod
    def leave_maze(cls, party: Iterable[Character]) -> dict[str, List[Character]]:
        return PartyRules.leave_maze(party)