from datetime import datetime
from typing import List, Optional
from app.models.character import Character, Weapon, CharacterCreationConfig
from app.models.enums import ClassType, WeaponType
from app.services.repository import BaseCharacterRepository
from app.services.rules_engine import RulesEngine


class CharacterManager:
    """High-level service coordinating character lifecycles, persistence, and rule enforcement."""

    def __init__(self, repository: BaseCharacterRepository):
        self.repository = repository

    # def create_character(
    #     self, 
    #     name: str, 
    #     class_type: ClassType, 
    #     max_hp: int = 10
    # ) -> Character:
    #     existing = self.repository.get_by_name(name)
    #     if existing:
    #         raise ValueError(f"Character with name '{name}' already exists. Names must be unique.")

    #     character = Character(
    #         name=name,
    #         class_type=class_type,
    #         max_hp=max_hp,
    #         current_hp=max_hp,
    #         created_date=datetime.now().isoformat(),
    #         is_in_party=False  # Defaults to Tavern/Town
    #     )
    #     self.repository.save(character)
    #     return character

    def create_character_from_config(self, config: CharacterCreationConfig) -> Character:
        """Orchestrates secure character creation using RulesEngine and the repository."""
        existing = self.repository.get_by_name(config.name)
        if existing:
            raise ValueError(f"Character with name '{config.name}' already exists. Names must be unique.")

        character = Character(
            name=config.name,
            class_type=config.class_type,
            created_date=datetime.now().strftime("%Y-%m-%d"),
            is_in_party=False
        )

        RulesEngine.initialize_character_stats(character, config.class_type)

        if config.class_type == ClassType.PEACE_MAKER:
            pass
        elif config.class_type == ClassType.HEALER:
            character.weapons.append(Weapon(name=WeaponType.DAGGER))
            character.equipped_weapon_index = 0
        else:
            for w_type in config.selected_weapons:
                character.weapons.append(Weapon(name=w_type))
            
            if character.weapons and config.equipped_weapon:
                for idx, w in enumerate(character.weapons):
                    if w.name == config.equipped_weapon:
                        character.equipped_weapon_index = idx
                        break

        RulesEngine.apply_starting_bonuses(character, config)

        if character.is_magic_user and config.primary_spell:
            if config.primary_spell not in character.spells:
                character.spells.append(config.primary_spell)

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