import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from app.models.character import Character
from app.services.persistence import CharacterSerializer


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
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_by_name(self, name: str) -> Optional[Character]:
        file_path = self._get_file_path(name)
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return CharacterSerializer.from_dict(data)
        except (json.JSONDecodeError, KeyError):
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