from enum import Enum, auto


class ClassType(Enum):
    """Supported character classes in DeathMaze Deluxe."""
    HERO = auto()
    THIEF = auto()
    WIZARD = auto()
    WITCH_HUNTER = auto()
    HEALER = auto()
    PEACE_MAKER = auto()


class WeaponType(Enum):
    """Available weapon types."""
    SWORD = auto()
    HAMMER = auto()
    AXE = auto()
    BOW_AND_ARROWS = auto()
    DAGGER = auto()
    THROWING_DAGGER = auto()


class ItemType(Enum):
    """Classifications of inventory items."""
    RING = auto()
    SPICE = auto()
    MEDALLION = auto()
    POTION = auto()
    MAGIC_RING = auto()