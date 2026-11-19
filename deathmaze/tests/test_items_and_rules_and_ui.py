import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QPushButton, QDialog
from app.models.character import Character, Item
from app.models.enums import ClassType, ItemType
from app.models.items import ITEMS_CATALOG, get_item_by_name
from app.services.rules_engine import RulesEngine
from app.services.character_manager import CharacterManager
from app.services.repository import JsonCharacterRepository
from app.services.rules_engine import RulesEngine
from views.widgets.character_card import CharacterCardWidget
from views.widgets.character_inspector import CharacterInspectorWidget
from views.widgets.item_picker_dialog import AddItemDialog
from views.main_window import MainWindow


def test_granting_item_from_card_preserves_character_and_persists_item(qtbot, tmp_path, monkeypatch):
    """Regression test: granting an item via CharacterCardWidget 'Item' button must not delete the character."""
    repo = JsonCharacterRepository(storage_dir=tmp_path / "chars")
    manager = CharacterManager(repo)

    hero = make_char("Bram", ClassType.HERO, hp=8, in_party=True)
    repo.save(hero)

    win = MainWindow(manager)
    qtbot.addWidget(win)
    win.show()

    # Locate the Item button on Bram's card
    cards = win.dashboard_container.findChildren(CharacterCardWidget)
    assert len(cards) == 1
    item_btns = [b for b in cards[0].findChildren(QPushButton) if b.text() == "Item"]
    assert len(item_btns) == 1

    healing_def = get_item_by_name("Healing", ItemType.POTION)
    assert healing_def is not None

    def _fake_exec(dialog_self: AddItemDialog) -> int:
        dialog_self.selected_definition = healing_def
        return QDialog.Accepted

    monkeypatch.setattr(AddItemDialog, "exec", _fake_exec)

    item_btns[0].click()
    QTimer.singleShot(0, lambda: None)
    qtbot.wait(20)

    # Character must still exist in repository, active list, and dashboard grid
    persisted = repo.get_by_name("Bram")
    assert persisted is not None
    assert persisted.is_in_party is True
    assert len(persisted.items) == 1
    assert persisted.items[0].name == "Healing"
    assert persisted.items[0].uses_remaining == 1
    assert win.active_list.count() == 1
    assert len(win.dashboard_container.findChildren(CharacterCardWidget)) == 1

def make_char(
    name: str,
    class_type: ClassType,
    hp: int = 8,
    magic_wounds: int = 0,
    in_party: bool = True,
    alive: bool = True,
) -> Character:
    char = Character(name=name, class_type=class_type)
    char.max_hp = hp
    char.current_hp = hp
    char.magic_wounds = magic_wounds
    char.is_in_party = in_party
    char.is_alive = alive
    char.items = []
    return char


def test_catalog_has_20_items():
    assert len(ITEMS_CATALOG) == 20


def test_magic_ring_once_per_game_zero_wound_cost_and_multiple_copies():
    peacemaker = make_char("Pax", ClassType.PEACE_MAKER, hp=6, magic_wounds=1)
    hero = make_char("Conan", ClassType.HERO, hp=8)
    thief = make_char("Valeria", ClassType.THIEF, hp=6)

    sleep_def = get_item_by_name("Sleep", ItemType.MAGIC_RING)
    assert sleep_def is not None

    assert RulesEngine.can_use_item(hero, sleep_def) is False
    assert RulesEngine.can_use_item(thief, sleep_def) is False
    assert RulesEngine.can_use_item(peacemaker, sleep_def) is False

    # Grant two separate Sleep Magic Rings (do not stack)
    ring_1 = RulesEngine.grant_item(peacemaker, sleep_def, party=[peacemaker])
    ring_2 = RulesEngine.grant_item(peacemaker, sleep_def, party=[peacemaker])
    assert RulesEngine.can_use_item(peacemaker, sleep_def) is True
    assert ring_1 is not ring_2
    assert ring_1.uses_remaining == 1
    assert ring_2.uses_remaining == 1

    # First use in game: 0 wound cost, kept in inventory, marked used for this game
    RulesEngine.use_magic_ring(peacemaker, ring_1)
    assert peacemaker.magic_wounds == 1
    assert ring_1 in peacemaker.items
    assert ring_1.used_this_game is True
    assert ring_1.uses_remaining == 0

    # Cannot reuse the same ring during the same game
    assert RulesEngine.can_use_item(peacemaker, sleep_def, ring_entry=ring_1) is False
    with pytest.raises(ValueError):
        RulesEngine.use_magic_ring(peacemaker, ring_1)

    # Second copy can still be used once in the same game
    RulesEngine.use_magic_ring(peacemaker, ring_2)
    assert ring_2.used_this_game is True
    assert peacemaker.magic_wounds == 1


def test_leave_maze_resets_only_living_active_party():
    active_alive = make_char("Aldric", ClassType.WIZARD, hp=6, magic_wounds=2, in_party=True, alive=True)
    active_alive.current_hp = 2
    sleep_def = get_item_by_name("Sleep", ItemType.MAGIC_RING)
    ring = RulesEngine.grant_item(active_alive, sleep_def, party=[active_alive])
    RulesEngine.use_magic_ring(active_alive, ring)

    active_dead = make_char("Fallen", ClassType.HERO, hp=8, magic_wounds=3, in_party=True, alive=False)
    active_dead.current_hp = 0

    tavern_wizard = make_char("TavernWiz", ClassType.WIZARD, hp=5, magic_wounds=2, in_party=False, alive=True)
    tavern_wizard.current_hp = 1

    RulesEngine.leave_maze([active_alive, active_dead, tavern_wizard])

    assert active_alive.current_hp == active_alive.max_hp
    assert active_alive.magic_wounds == 0
    assert ring.used_this_game is False
    assert ring.uses_remaining == 1

    # Dead active party member and tavern character untouched
    assert active_dead.current_hp == 0
    assert active_dead.magic_wounds == 3
    assert tavern_wizard.current_hp == 1
    assert tavern_wizard.magic_wounds == 2


def test_stacking_and_potion_appraisal_add_two_uses():
    p1 = make_char("P1", ClassType.HERO, in_party=True)
    p2 = make_char("P2", ClassType.THIEF, in_party=True)

    healing = get_item_by_name("Healing", ItemType.POTION)
    appraisal = get_item_by_name("Potion Appraisal", ItemType.MEDALLION)
    mustard = get_item_by_name("Mustard", ItemType.SPICE)

    # First potion without appraisal -> 1 use
    item_p1 = RulesEngine.grant_item(p1, healing, party=[p1, p2])
    assert item_p1.uses_remaining == 1

    # Give P2 Potion Appraisal medallion
    RulesEngine.grant_item(p2, appraisal, party=[p1, p2])

    # Adding another Healing potion stacks +2 uses -> 3 uses total
    RulesEngine.grant_item(p1, healing, party=[p1, p2])
    assert len([i for i in p1.items if i.name == "Healing"]) == 1
    assert item_p1.uses_remaining == 3

    # Spice stacks onto existing entry
    item_s1 = RulesEngine.grant_item(p1, mustard, party=[p1, p2])
    item_s2 = RulesEngine.grant_item(p1, mustard, party=[p1, p2])
    assert item_s1 is item_s2
    assert item_s1.uses_remaining == 2


def test_pill_dialog_filters_restricted_magic_rings_and_duplicate_non_consumables(qtbot):
    hero = make_char("Conan", ClassType.HERO)
    res1 = get_item_by_name("Resistance +1", ItemType.RING)
    RulesEngine.grant_item(hero, res1, party=[hero])

    dlg = AddItemDialog(hero, party=[hero])
    qtbot.addWidget(dlg)

    # Magic Ring type pill should not be shown for HERO
    assert ItemType.MAGIC_RING not in dlg.type_pills

    # Ring type pill should omit already-owned "Resistance +1" but include "Resistance +2"
    dlg._select_type(ItemType.RING)
    assert "Resistance +1" not in dlg.name_pills
    assert "Resistance +2" in dlg.name_pills


def test_inspector_and_card_item_button_and_used_magic_ring_tag(qtbot, tmp_path):
    repo = JsonCharacterRepository(storage_dir=tmp_path / "chars")
    manager = CharacterManager(repo)

    wiz = make_char("Merlin", ClassType.WIZARD, hp=6, in_party=True)
    sleep_def = get_item_by_name("Sleep", ItemType.MAGIC_RING)
    ring = RulesEngine.grant_item(wiz, sleep_def, party=[wiz])
    RulesEngine.use_magic_ring(wiz, ring)
    wiz.items.append(Item(name="Healing", item_type=ItemType.POTION, effect="Heals 1d6", uses_remaining=2))
    wiz.items.append(Item(name="Oratory", item_type=ItemType.MEDALLION, effect="+2 to Negotiation (Cumulative)", uses_remaining=None))
    repo.save(wiz)

    card = CharacterCardWidget(wiz)
    qtbot.addWidget(card)
    item_btns = [b for b in card.findChildren(QPushButton) if b.text() == "Item"]
    assert len(item_btns) == 1

    inspector = CharacterInspectorWidget(manager)
    qtbot.addWidget(inspector)
    inspector.set_character(wiz)

    labels = [lbl.text() for lbl in inspector.findChildren(QLabel)]
    assert any("Sleep" in t and "(Used)" in t for t in labels)
    assert any("Healing" in t and "(2 uses left)" in t for t in labels)
    assert any("Oratory" in t and "use" not in t.lower() for t in labels)

    win = MainWindow(manager)
    qtbot.addWidget(win)
    leave_btns = [b for b in win.findChildren(QPushButton) if b.text() == "Leave Maze"]
    assert len(leave_btns) == 1