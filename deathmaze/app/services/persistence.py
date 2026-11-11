import json
from dataclasses import asdict
from typing import Dict, Any
from app.models.character import Character, Weapon, Item, Spell
from app.models.enums import ClassType, ItemType, WeaponType


class CharacterSerializer:
    """Handles serialization and deserialization of Character domain models to/from JSON."""

    @staticmethod
    def to_dict(character: Character) -> Dict[str, Any]:
        data = asdict(character)
        data["class_type"] = character.class_type.name
        
        # Ensure created_date and death_date are cleanly saved as YYYY-MM-DD
        if data.get("created_date"):
            data["created_date"] = data["created_date"][:10]
        if data.get("death_date"):
            data["death_date"] = data["death_date"][:10]

        for weapon in data["weapons"]:
            weapon["name"] = WeaponType(weapon["name"]).name if isinstance(weapon["name"], WeaponType) else weapon["name"]
        for item in data["items"]:
            item["item_type"] = ItemType(item["item_type"]).name if isinstance(item["item_type"], ItemType) else item["item_type"]
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

        items = [
            Item(
                name=i["name"],
                item_type=ItemType[i["item_type"]],
                effect_description=i.get("effect_description", ""),
                charges_remaining=i.get("charges_remaining", 0)
            )
            for i in data.get("items", [])
        ]

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