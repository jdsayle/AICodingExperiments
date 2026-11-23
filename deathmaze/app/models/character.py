from dataclasses import dataclass, field
from typing import List, Optional
from app.models.enums import ClassType, ItemType, WeaponType


@dataclass
class Weapon:
    name: WeaponType
    is_magical: bool = False
    combat_bonus: int = 0
    skill_bonus: int = 0


@dataclass
class Item:
    name: str
    item_type: ItemType
    effect: str = ""
    uses_remaining: Optional[int] = None
    used_this_game: bool = False

    @property
    def effect_description(self) -> str:
        return self.effect

    @effect_description.setter
    def effect_description(self, value: str) -> None:
        self.effect = value


@dataclass
class Spell:
    name: str
    cost: int
    is_combat_spell: bool
    description: str
    allowed_classes: List[ClassType] = field(default_factory=list)


class SpellcasterMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, "spells"):
            self.spells: List[Spell] = []
        if not hasattr(self, "magic_wounds"):
            self.magic_wounds: int = 0

    def can_know_spell(self, spell: Spell) -> bool:
        return getattr(self, "class_type", None) in spell.allowed_classes

    def learn_spell(self, spell: Spell) -> None:
        if self.can_know_spell(spell) and spell not in self.spells:
            self.spells.append(spell)

    def is_magic_user(self) -> bool:
        return True


@dataclass
class CharacterCreationConfig:
    name: str
    class_type: ClassType
    selected_weapons: List[WeaponType] = field(default_factory=list)
    equipped_weapon: Optional[WeaponType] = None
    primary_spell: Optional[Spell] = None
    secondary_spell: Optional[Spell] = None
    bonus_option: str = "a"  # "a", "b", "c", or "d"
    bonus_weapon_target: Optional[WeaponType] = None


@dataclass
class Character:
    MAGIC_USER_CLASSES = frozenset({
        ClassType.WIZARD,
        ClassType.WITCH_HUNTER,
        ClassType.HEALER,
        ClassType.PEACE_MAKER,
    })

    name: str
    class_type: ClassType
    level: int = 1
    experience: int = 0
    created_date: str = ""
    death_date: Optional[str] = None

    # Health & Magic
    max_hp: int = 10
    current_hp: int = 10
    magic_wounds: int = 0
    magic_resistance: int = 0
    detrap_skill: int = 0
    combat_strength: int = 0

    # Equipment & Inventory
    weapons: List[Weapon] = field(default_factory=list)
    equipped_weapon_index: Optional[int] = None
    items: List[Item] = field(default_factory=list)
    spells: List[Spell] = field(default_factory=list)

    # Currency
    bezants: int = 0
    gems: int = 0

    # Status Flags & Tactical Placement
    is_alive: bool = True
    is_retired: bool = False
    is_in_party: bool = False  # True = ACTIVE party, False = TAVERN/TOWN
    is_npc: bool = False       # True = Charmed Monster / NPC (Max 3 in party)
    combat_row: int = 0        # 0 = Front Row, 1 = Back Row, 2 = NPC Row
    combat_col: int = 0        # 0, 1, or 2 (Column within the row)

    @property
    def effective_hp(self) -> int:
        return self.current_hp - self.magic_wounds

    @property
    def is_magic_user(self) -> bool:
        return self.class_type in self.MAGIC_USER_CLASSES