from PySide6.QtWidgets import QLabel
from app.models.character import Item
from app.models.enums import ItemType
from app.services.repository import JsonCharacterRepository
from app.services.character_manager import CharacterManager, CharacterCreationConfig
from views.widgets.character_inspector import CharacterInspectorWidget
from app.models.enums import ClassType, ItemType, WeaponType

def test_interactive_inspector_inventory_display_and_usage_text(qtbot, tmp_path):
    """Verify Inventory & Items renders consumable uses (1 use left vs. 2 uses left) and omits usage text for non-consumables."""
    repo = JsonCharacterRepository(storage_dir=tmp_path / "characters")
    manager = CharacterManager(repo)

    config = CharacterCreationConfig(
        name="Aldric",
        class_type=ClassType.WIZARD,
        selected_weapons=[WeaponType.DAGGER],
        equipped_weapon=WeaponType.DAGGER,
    )
    char = manager.create_character_from_config(config)
    char.items = [
        Item(name="Healing", item_type=ItemType.POTION, effect="Heals 1d6", uses_remaining=1),
        Item(name="Mustard", item_type=ItemType.SPICE, effect="Heals 1d6", uses_remaining=2),
        Item(name="Resistance +1", item_type=ItemType.RING, effect="+1 to Magic Resistance", uses_remaining=None),
        Item(name="Oratory", item_type=ItemType.MEDALLION, effect="+2 to Negotiation (Cumulative)", uses_remaining=None),
        Item(name="Sleep", item_type=ItemType.MAGIC_RING, effect="Remove Monster", uses_remaining=None),
    ]

    inspector = CharacterInspectorWidget(manager)
    qtbot.addWidget(inspector)
    inspector.set_character(char)

    labels_text = [lbl.text() for lbl in inspector.findChildren(QLabel)]

    assert any("Healing" in t and "(1 use left)" in t for t in labels_text)
    assert any("Mustard" in t and "(2 uses left)" in t for t in labels_text)

    non_consumable_labels = [
        t for t in labels_text
        if any(name in t for name in ("Resistance +1", "Oratory", "Sleep"))
    ]
    assert len(non_consumable_labels) == 3
    assert all("use" not in t.lower() for t in non_consumable_labels)