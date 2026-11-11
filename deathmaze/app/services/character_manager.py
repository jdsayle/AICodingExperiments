from datetime import datetime
from typing import List, Optional
from app.models.character import Character, Weapon, Item, Spell
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
        """Instantiates a new character, records creation date, and saves to repository."""
        existing = self.repository.get_by_name(name)
        if existing:
            raise ValueError(f"Character with name '{name}' already exists.")

        character = Character(
            name=name,
            class_type=class_type,
            max_hp=max_hp,
            current_hp=max_hp,
            created_date=datetime.now().isoformat()
        )
        self.repository.save(character)
        return character

    def get_character(self, name: str) -> Optional[Character]:
        return self.repository.get_by_name(name)

    def list_characters(self) -> List[Character]:
        return self.repository.list_all()

    def equip_weapon(self, character_name: str, weapon: Weapon) -> None:
        """Attempts to equip a weapon using RulesEngine validation."""
        char = self.repository.get_by_name(character_name)
        if not char:
            raise ValueError(f"Character '{character_name}' not found.")

        if not RulesEngine.can_equip_weapon(char, weapon):
            raise ValueError(f"Class {char.class_type.name} cannot equip weapon {weapon.name.name}.")

        char.weapons.append(weapon)
        char.equipped_weapon_index = len(char.weapons) - 1
        self.repository.save(char)

    def cast_spell(self, character_name: str, spell_name: str, target_is_undead: bool = False) -> None:
        """Performs spell casting validation and updates character state."""
        char = self.repository.get_by_name(character_name)
        if not char:
            raise ValueError(f"Character '{character_name}' not found.")

        spell = next((s for s in char.spells if s.name == spell_name), None)
        if not spell:
            raise ValueError(f"Character does not know spell '{spell_name}'.")

        RulesEngine.cast_spell(char, spell, target_is_undead)
        self.repository.save(char)

    def delete_character(self, name: str) -> bool:
        return self.repository.delete(name)