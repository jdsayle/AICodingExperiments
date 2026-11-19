import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.models.character import Character, Item
from app.models.enums import ItemType
from app.services.persistence import CharacterSerializer


def _serialize_item(item: Item) -> Dict[str, Any]:
    item_type_val = item.item_type.value if isinstance(item.item_type, ItemType) else str(item.item_type)
    uses = None if item.item_type in {ItemType.RING, ItemType.MEDALLION} else item.uses_remaining
    return {
        "name": item.name,
        "item_type": item_type_val,
        "effect": item.effect,
        "uses_remaining": uses,
        "used_this_game": bool(getattr(item, "used_this_game", False)),
    }


def _deserialize_item(raw: Dict[str, Any]) -> Item:
    raw_type = raw.get("item_type", "")
    if isinstance(raw_type, ItemType):
        item_type = raw_type
    else:
        try:
            item_type = ItemType(raw_type)
        except ValueError:
            item_type = ItemType[str(raw_type).upper().replace(" ", "_")]

    effect = raw.get("effect", raw.get("effect_description", ""))

    if item_type in {ItemType.RING, ItemType.MEDALLION}:
        uses: Optional[int] = None
    else:
        raw_uses = raw.get("uses_remaining")
        if raw_uses is None:
            raw_uses = raw.get("charges_remaining")
        uses = int(raw_uses) if raw_uses is not None else (1 if item_type == ItemType.MAGIC_RING else None)

    return Item(
        name=raw["name"],
        item_type=item_type,
        effect=effect,
        uses_remaining=uses,
        used_this_game=bool(raw.get("used_this_game", False)),
    )


class BaseCharacterRepository(ABC):
    """Abstract repository interface for character persistence."""

    @abstractmethod
    def save(self, character: Character) -> None:
        """Saves or updates a character."""
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Character]:
        """Retrieves a character by their unique name."""
        pass

    @abstractmethod
    def list_all(self) -> List[Character]:
        """Returns all stored characters."""
        pass

    @abstractmethod
    def delete(self, name: str) -> bool:
        """Deletes a character by name. Returns True if successful."""
        pass


class JsonCharacterRepository(BaseCharacterRepository):
    """File-based JSON repository storing each character as a separate JSON file in a directory."""

    def __init__(self, storage_dir: str | Path = "data/characters"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, name: str) -> Path:
        # Sanitize name for filename use
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
        return self.storage_dir / f"{safe_name}.json"

    def save(self, character: Character) -> None:
        file_path = self._get_file_path(character.name)
        data = CharacterSerializer.to_dict(character)
        data["items"] = [_serialize_item(item) for item in getattr(character, "items", [])]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_by_name(self, name: str) -> Optional[Character]:
        file_path = self._get_file_path(name)
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                character = CharacterSerializer.from_dict(data)
                if character is not None:
                    raw_items = data.get("items", [])
                    character.items = [_deserialize_item(entry) for entry in raw_items]
                return character
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def list_all(self) -> List[Character]:
        characters = []
        for file_path in self.storage_dir.glob("*.json"):
            char = self.get_by_name(file_path.stem)
            if char:
                characters.append(char)
        return characters

    def delete(self, name: str) -> bool:
        file_path = self._get_file_path(name)
        if file_path.exists():
            file_path.unlink()
            return True
        return False