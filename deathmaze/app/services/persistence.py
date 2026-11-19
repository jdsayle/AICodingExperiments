import json
from dataclasses import asdict
from typing import Dict, Any
from app.models.character import Character, Weapon, Item, Spell
from app.models.enums import ClassType, ItemType, WeaponType


def _normalize_item_type(raw_type: Any) -> ItemType:
    if isinstance(raw_type, ItemType):
        return raw_type
    name_str = str(raw_type).strip().upper().replace(" ", "_")
    if name_str in ItemType.__members__:
        return ItemType[name_str]
    for member in ItemType:
        if member.name.lower() == str(raw_type).strip().lower():
            return member
    raise KeyError(f"Unknown ItemType: {raw_type}")

def _normalize_uses_remaining(item_type: ItemType, raw_uses: Any) -> int | None:
    if item_type in {ItemType.RING, ItemType.MEDALLION}:
        return None
    if raw_uses is None:
        return 1 if item_type == ItemType.MAGIC_RING else None
    return int(raw_uses)


class CharacterSerializer:
    """Handles serialization and deserialization of Character domain models to/from JSON."""

    @staticmethod
    def to_dict(character: Character) -> Dict[str, Any]:
        data = asdict(character)
        data["class_type"] = character.class_type.name

        if data.get("created_date"):
            data["created_date"] = data["created_date"][:10]
        if data.get("death_date"):
            data["death_date"] = data["death_date"][:10]

        for weapon in data["weapons"]:
            weapon["name"] = WeaponType(weapon["name"]).name if isinstance(weapon["name"], WeaponType) else weapon["name"]
        for item in data["items"]:
            it = _normalize_item_type(item["item_type"])
            item["item_type"] = it.name
            item["uses_remaining"] = _normalize_uses_remaining(it, item.get("uses_remaining"))
        for spell in data["spells"]:
            spell["allowed_classes"] = [
                c.name if isinstance(c, ClassType) else c for c in spell["allowed_classes"]
            ]
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Character:
        weapons = [
            Weapon(
                name=WeaponType[w["name"]],
                is_magical=w.get("is_magical", False),
                combat_bonus=w.get("combat_bonus", 0),
                skill_bonus=w.get("skill_bonus", 0)
            )
            for w in data.get("weapons", [])
        ]

        items = []
        for raw_item in data.get("items", []):
            if not isinstance(raw_item, dict) or "name" not in raw_item or "item_type" not in raw_item:
                continue
            try:
                it = _normalize_item_type(raw_item["item_type"])
            except KeyError:
                continue

            raw_uses = raw_item.get("uses_remaining")
            if raw_uses is None:
                raw_uses = raw_item.get("charges_remaining")

            uses = _normalize_uses_remaining(it, raw_uses)
            effect_val = raw_item.get("effect", raw_item.get("effect_description", ""))
            items.append(
                Item(
                    name=str(raw_item["name"]),
                    item_type=it,
                    effect=str(effect_val) if effect_val is not None else "",
                    uses_remaining=uses,
                    used_this_game=bool(raw_item.get("used_this_game", False)),
                )
            )

        spells = [
            Spell(
                name=s["name"],
                cost=s["cost"],
                is_combat_spell=s["is_combat_spell"],
                description=s.get("description", ""),
                allowed_classes=[ClassType[c] for c in s.get("allowed_classes", [])]
            )
            for s in data.get("spells", [])
        ]

        raw_created = data.get("created_date", "")
        formatted_created = raw_created[:10] if raw_created else ""

        raw_death = data.get("death_date")
        formatted_death = raw_death[:10] if raw_death else None

        return Character(
            name=data["name"],
            class_type=ClassType[data["class_type"]],
            level=data.get("level", 1),
            experience=data.get("experience", 0),
            created_date=formatted_created,
            death_date=formatted_death,
            max_hp=data.get("max_hp", 10),
            current_hp=data.get("current_hp", 10),
            magic_wounds=data.get("magic_wounds", 0),
            magic_resistance=data.get("magic_resistance", 0),
            detrap_skill=data.get("detrap_skill", 0),
            weapons=weapons,
            equipped_weapon_index=data.get("equipped_weapon_index"),
            items=items,
            spells=spells,
            bezants=data.get("bezants", 0),
            gems=data.get("gems", 0),
            is_alive=data.get("is_alive", True),
            is_retired=data.get("is_retired", False),
            is_in_party=data.get("is_in_party", False),
            is_npc=data.get("is_npc", False),
            combat_row=data.get("combat_row", 0),
            combat_col=data.get("combat_col", 0)
        )

    @classmethod
    def to_json(cls, char: Character) -> str:
        return json.dumps(cls.to_dict(char), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> Character:
        return cls.from_dict(json.loads(json_str))