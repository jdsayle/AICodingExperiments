from dataclasses import dataclass, field
from typing import List, Optional
from app.models.enums import ClassType, ItemType, WeaponType


@dataclass
class Weapon:
    """Represents a weapon equipped or carried by a character."""
    name: WeaponType
    is_magical: bool = False
    combat_bonus: int = 0
    skill_bonus: int = 0


@dataclass
class Item:
    """Represents a general inventory item, potion, or treasure component."""
    name: str
    item_type: ItemType
    effect_description: str = ""
    charges_remaining: int = 0


@dataclass
class Spell:
    """Represents a magical spell with class restrictions and casting costs."""
    name: str
    cost: int
    is_combat_spell: bool
    description: str
    allowed_classes: List[ClassType] = field(default_factory=list)


class SpellcasterMixin:
    """Mixin for magic-user classes providing spell inventory and magic wound tracking."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, "spells"):
            self.spells: List[Spell] = []
        if not hasattr(self, "magic_wounds"):
            self.magic_wounds: int = 0

    def can_know_spell(self, spell: Spell) -> bool:
        """Checks if character's class is allowed to learn this spell."""
        return getattr(self, "class_type", None) in spell.allowed_classes

    def learn_spell(self, spell: Spell) -> None:
        """Adds spell to inventory if valid for class."""
        if self.can_know_spell(spell) and spell not in self.spells:
            self.spells.append(spell)

    def is_magic_user(self) -> bool:
        return True


@dataclass
class Character:
    """Core character domain model tracking stats, equipment, inventory, and health."""
    name: str
    class_type: ClassType
    level: int = 1
    created_date: str = ""
    death_date: Optional[str] = None
    
    # Health & Magic
    max_hp: int = 10
    current_hp: int = 10
    magic_wounds: int = 0  # Wounds from spell casting
    magic_resistance: int = 0
    detrap_skill: int = 0
    
    # Equipment & Inventory
    weapons: List[Weapon] = field(default_factory=list)
    equipped_weapon_index: Optional[int] = None
    items: List[Item] = field(default_factory=list)
    spells: List[Spell] = field(default_factory=list)
    
    # Currency
    bezants: int = 0
    gems: int = 0
    
    # Status Flags
    is_alive: bool = True
    is_retired: bool = False

    @property
    def effective_hp(self) -> int:
        """Returns effective hit points factoring in magic wounds."""
        return self.current_hp - self.magic_wounds

    @property
    def is_magic_user(self) -> bool:
        """Identifies if character belongs to a spell-casting class."""
        return self.class_type in {
            ClassType.WIZARD, ClassType.WITCH_HUNTER, 
            ClassType.HEALER, ClassType.PEACE_MAKER
        }