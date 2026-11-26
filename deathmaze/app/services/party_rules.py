from typing import Iterable, List, Optional

from app.models.character import Character, Weapon
from app.models.enums import ClassType, ItemType, WeaponType


class PartyRules:
    """Encapsulates active party composition, 3x3 grid slot assignment, Charmed NPCs, and Leave Maze rules."""

    MAX_PARTY_SIZE: int = 9
    CHARMED_ALLOWED_WEAPONS: tuple[WeaponType, ...] = (
        WeaponType.SWORD,
        WeaponType.DAGGER,
        WeaponType.BOW_AND_ARROWS,
    )

    @classmethod
    def get_first_open_party_slot(
        cls,
        party: Iterable[Character],
        exclude_name: Optional[str] = None,
    ) -> Optional[tuple[int, int]]:
        occupied = {
            (c.combat_row, c.combat_col)
            for c in party
            if getattr(c, "is_in_party", False)
            and 0 <= c.combat_row < 3
            and 0 <= c.combat_col < 3
            and (exclude_name is None or c.name != exclude_name)
        }
        for r in range(3):
            for c in range(3):
                if (r, c) not in occupied:
                    return (r, c)
        return None

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
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Charmed NPC requires a name.")

        party_list = list(party)
        name_exists = any(
            getattr(c, "name", "").strip().lower() == clean_name.lower()
            for c in party_list
        )
        if name_exists:
            raise ValueError(f"A character named '{clean_name}' already exists.")
        if max_hp < 1:
            raise ValueError("Max HP must be at least 1.")
        if current_hp > max_hp:
            raise ValueError("Current HP cannot exceed Max HP.")
        if weapons and len(weapons) > 2:
            raise ValueError("A Charmed NPC can have at most 2 weapons.")
        for w in (weapons or []):
            if w.name not in cls.CHARMED_ALLOWED_WEAPONS:
                raise ValueError(f"Weapon '{w.name.name}' is not allowed for Charmed NPCs.")

        active_party = [c for c in party_list if getattr(c, "is_in_party", False)]
        if len(active_party) >= cls.MAX_PARTY_SIZE:
            raise ValueError(
                f"Party is full (maximum {cls.MAX_PARTY_SIZE} total party members between PCs and NPCs)."
            )

        active_pcs = [c for c in active_party if not getattr(c, "is_npc", False)]
        if len(active_pcs) < 1:
            raise ValueError(
                "At least one Player Character must be in the active party to add a Charmed NPC."
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
        party_list = list(party)
        selected_types = list(weapon_types or [])[:2]
        weapons = [Weapon(name=wt) for wt in selected_types]
        cls.validate_add_charmed_npc(
            party=party_list,
            name=name,
            current_hp=current_hp,
            max_hp=max_hp,
            combat_strength=combat_strength,
            weapons=weapons,
        )

        open_slot = cls.get_first_open_party_slot(party_list)
        if open_slot is None:
            raise ValueError(
                f"Party is full (maximum {cls.MAX_PARTY_SIZE} total party members between PCs and NPCs)."
            )
        slot_row, slot_col = open_slot

        return Character(
            name=name.strip(),
            class_type=ClassType.HERO,
            level=1,
            experience=0,
            max_hp=max_hp,
            current_hp=current_hp,
            combat_strength=combat_strength,
            weapons=weapons,
            equipped_weapon_index=0 if weapons else None,
            items=[],
            spells=[],
            bezants=0,
            gems=0,
            is_alive=True,
            is_retired=False,
            is_in_party=True,
            is_npc=True,
            combat_row=slot_row,
            combat_col=slot_col,
        )

    @classmethod
    def leave_maze(cls, party: Iterable[Character]) -> dict[str, List[Character]]:
        """
        Resets HP and magic_wounds and recharges Magic Rings for living active-party PCs,
        and identifies Charmed NPCs to remove from the party and delete.
        """
        reset_pcs: List[Character] = []
        removed_npcs: List[Character] = []

        for char in party:
            if getattr(char, "is_in_party", False) and getattr(char, "is_npc", False):
                char.is_in_party = False
                removed_npcs.append(char)
            elif getattr(char, "is_in_party", False) and getattr(char, "is_alive", False):
                char.current_hp = char.max_hp
                char.magic_wounds = 0
                for item in getattr(char, "items", []):
                    if item.item_type == ItemType.MAGIC_RING:
                        item.used_this_game = False
                        item.uses_remaining = 1
                reset_pcs.append(char)

        return {"reset": reset_pcs, "removed_npcs": removed_npcs}