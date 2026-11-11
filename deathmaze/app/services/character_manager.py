from datetime import datetime
from typing import List, Optional
from app.models.character import Character, Weapon
from app.models.enums import ClassType
from app.services.repository import BaseCharacterRepository
from app.services.rules_engine import RulesEngine


class CharacterManager:
    """High-level service coordinating character lifecycles, persistence, and rule enforcement."""

    def __init__(self, repository: BaseCharacterRepository):
        self.repository = repository

    def create_character(
        self, 
        name: str, 
        class_type: ClassType, 
        max_hp: int = 10
    ) -> Character:
        existing = self.repository.get_by_name(name)
        if existing:
            raise ValueError(f"Character with name '{name}' already exists. Names must be unique.")

        character = Character(
            name=name,
            class_type=class_type,
            max_hp=max_hp,
            current_hp=max_hp,
            created_date=datetime.now().isoformat(),
            is_in_party=False  # Defaults to Tavern/Town
        )
        self.repository.save(character)
        return character

    def get_character(self, name: str) -> Optional[Character]:
        return self.repository.get_by_name(name)

    def list_characters(self) -> List[Character]:
        return self.repository.list_all()

    def add_to_party(self, name: str) -> None:
        """Recruits character into ACTIVE party, enforcing a max cap of 6."""
        char = self.repository.get_by_name(name)
        if not char:
            raise ValueError(f"Character '{name}' not found.")
        
        active_party = [c for c in self.repository.list_all() if c.is_in_party]
        if len(active_party) >= 6 and not char.is_in_party:
            raise ValueError("Active party is full (maximum 6 characters).")

        char.is_in_party = True
        self.repository.save(char)

    def remove_from_party(self, name: str) -> None:
        """Returns character from ACTIVE party back to TAVERN/TOWN."""
        char = self.repository.get_by_name(name)
        if not char:
            raise ValueError(f"Character '{name}' not found.")
        
        char.is_in_party = False
        self.repository.save(char)

    def delete_character(self, name: str) -> bool:
        return self.repository.delete(name)