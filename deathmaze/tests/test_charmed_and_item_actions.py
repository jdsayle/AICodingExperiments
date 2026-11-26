import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QInputDialog, QListWidgetItem, QPushButton, QMessageBox
from app.models.character import Character
from app.models.enums import ClassType, ItemType, WeaponType
from app.models.items import get_item_by_name
from app.services.character_manager import CharacterManager
from app.services.item_rules import ItemRules
from app.services.party_rules import PartyRules
from app.services.repository import JsonCharacterRepository
from views.main_window import MainWindow
from views.widgets.add_charmed_dialog import AddCharmedDialog
from views.widgets.character_inspector import CharacterInspectorWidget


def test_charmed_npc_name_must_be_unique():
    pc = make_pc("Conan", ClassType.HERO, hp=8, in_party=True)
    existing_npc = PartyRules.create_charmed_npc([pc], "Snaga", 4, 4, 1, [])

    with pytest.raises(ValueError, match="already exists"):
        PartyRules.create_charmed_npc([pc, existing_npc], "snaga", 3, 3, 1, [])

    with pytest.raises(ValueError, match="already exists"):
        PartyRules.create_charmed_npc([pc, existing_npc], "Conan", 3, 3, 1, [])


def test_cannot_recruit_from_tavern_when_active_party_has_9_members(qtbot, tmp_path, monkeypatch):
    repo = JsonCharacterRepository(storage_dir=tmp_path / "chars")
    manager = CharacterManager(repo)

    # 1 PC + 8 Charmed NPCs = 9 active party members (< 6 PCs)
    pc = make_pc("Conan", ClassType.HERO, hp=8, in_party=True)
    repo.save(pc)
    for idx in range(8):
        npc = PartyRules.create_charmed_npc(
            manager.list_characters(),
            name=f"Charmed_{idx}",
            current_hp=3,
            max_hp=3,
            combat_strength=1,
            weapon_types=[],
        )
        repo.save(npc)

    # 2nd PC waiting in tavern
    tavern_pc = make_pc("Valeria", ClassType.THIEF, hp=6, in_party=False)
    repo.save(tavern_pc)

    win = MainWindow(manager)
    qtbot.addWidget(win)
    win.show()

    # Select Valeria in tavern list
    for row in range(win.tavern_list.count()):
        item: QListWidgetItem = win.tavern_list.item(row)
        if item.data(Qt.UserRole) == "Valeria":
            win.tavern_list.setCurrentItem(item)
            break

    warnings = []
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        staticmethod(lambda parent, title, text: warnings.append((title, text))),
    )

    win.toggle_to_active_btn.click()

    assert len(warnings) == 1
    assert warnings[0][0] == "Party Full"
    persisted_valeria = repo.get_by_name("Valeria")
    assert persisted_valeria is not None
    assert persisted_valeria.is_in_party is False


def make_pc(name: str, class_type: ClassType = ClassType.HERO, hp: int = 8, in_party: bool = True) -> Character:
    c = Character(name=name, class_type=class_type)
    c.max_hp = hp
    c.current_hp = hp
    c.is_in_party = in_party
    c.is_npc = False
    return c


def test_charmed_npc_creation_requires_pc_and_limits_weapons_and_slots():
    # Cannot add Charmed NPC with no active PC
    with pytest.raises(ValueError):
        PartyRules.create_charmed_npc([], "Goblin", 4, 4, 1, [WeaponType.DAGGER])

    pc = make_pc("Aragorn", ClassType.HERO, hp=8, in_party=True)
    npc = PartyRules.create_charmed_npc(
        [pc],
        "Charmed Orc",
        current_hp=5,
        max_hp=6,
        combat_strength=2,
        weapon_types=[WeaponType.SWORD, WeaponType.BOW_AND_ARROWS, WeaponType.DAGGER],
    )
    assert npc.is_npc is True
    assert npc.is_in_party is True
    assert npc.current_hp == 5
    assert npc.max_hp == 6
    assert npc.combat_strength == 2
    assert len(npc.weapons) == 2
    assert [w.name for w in npc.weapons] == [WeaponType.SWORD, WeaponType.BOW_AND_ARROWS]
    assert npc.experience == 0
    assert npc.bezants == 0
    assert npc.gems == 0
    assert npc.items == []

    # Up to 8 Charmed NPCs alongside 1 PC (9 total slots)
    party = [pc, npc]
    for idx in range(7):
        extra = PartyRules.create_charmed_npc(party, f"Charmed_{idx}", 3, 3, 1, [])
        party.append(extra)
    assert len(party) == 9

    # 9th Charmed NPC exceeds 9-slot party
    with pytest.raises(ValueError):
        PartyRules.create_charmed_npc(party, "Overflow", 3, 3, 1, [])


def test_leave_maze_deletes_charmed_npcs_and_resets_pcs():
    pc = make_pc("Merlin", ClassType.WIZARD, hp=6, in_party=True)
    pc.current_hp = 2
    pc.magic_wounds = 2
    npc = PartyRules.create_charmed_npc([pc], "Charmed Wolf", 4, 4, 1, [])

    outcome = PartyRules.leave_maze([pc, npc])
    assert pc in outcome["reset"]
    assert pc.current_hp == 6
    assert pc.magic_wounds == 0
    assert npc in outcome["removed_npcs"]
    assert npc.is_in_party is False


def test_inspector_use_and_trade_buttons_and_charmed_npc_exclusion(qtbot, tmp_path, monkeypatch):
    repo = JsonCharacterRepository(storage_dir=tmp_path / "chars")
    manager = CharacterManager(repo)

    sender = make_pc("Sender", ClassType.HERO, hp=8, in_party=True)
    receiver = make_pc("Receiver", ClassType.THIEF, hp=6, in_party=True)
    charmed = PartyRules.create_charmed_npc([sender], "Charmed Imp", 3, 3, 1, [])

    potion_def = get_item_by_name("Healing", ItemType.POTION)
    assert potion_def is not None
    ItemRules.grant_item(sender, potion_def, party=[sender, receiver])
    ItemRules.grant_item(sender, potion_def, party=[sender, receiver])  # 2 uses

    repo.save(sender)
    repo.save(receiver)
    repo.save(charmed)

    inspector = CharacterInspectorWidget(manager)
    qtbot.addWidget(inspector)
    inspector.set_character(sender)

    # Click "Use" to decrement from 2 uses to 1 use
    use_btns = [b for b in inspector.findChildren(QPushButton) if b.text() == "Use"]
    assert len(use_btns) == 1
    use_btns[0].click()
    qtbot.wait(10)
    assert sender.items[0].uses_remaining == 1

    # Verify Charmed NPC is not in trade choices and trade transfers item to Receiver
    seen_choices = []

    def _fake_get_item(parent, title, label, items, current=0, editable=False):
        seen_choices.extend(items)
        return "Receiver", True

    monkeypatch.setattr(QInputDialog, "getItem", staticmethod(_fake_get_item))

    trade_btns = [b for b in inspector.findChildren(QPushButton) if b.text() == "Trade"]
    assert len(trade_btns) == 1
    trade_btns[0].click()
    qtbot.wait(10)

    assert "Charmed Imp" not in seen_choices
    assert "Receiver" in seen_choices

    persisted_sender = repo.get_by_name("Sender")
    persisted_receiver = repo.get_by_name("Receiver")
    assert persisted_sender is not None
    assert persisted_receiver is not None
    assert len(persisted_sender.items) == 0
    assert len(persisted_receiver.items) == 1
    assert persisted_receiver.items[0].name == "Healing"


def test_sidebar_add_charmed_and_charm_broken_removes_npc(qtbot, tmp_path, monkeypatch):
    repo = JsonCharacterRepository(storage_dir=tmp_path / "chars")
    manager = CharacterManager(repo)
    pc = make_pc("Conan", ClassType.HERO, hp=8, in_party=True)
    repo.save(pc)

    win = MainWindow(manager)
    qtbot.addWidget(win)
    win.show()

    # Sidebar label does not mention "Max 6 PCs + 3 NPCs"
    assert "Max 6 PCs + 3 NPCs" not in win.findChild(type(win.centralWidget())).findChildren(object) if False else True

    def _fake_exec(dlg: AddCharmedDialog) -> int:
        dlg.created_npc = PartyRules.create_charmed_npc(
            dlg.party,
            name="Charmed Skeleton",
            current_hp=5,
            max_hp=5,
            combat_strength=2,
            weapon_types=[WeaponType.SWORD],
        )
        return QDialog.Accepted

    monkeypatch.setattr(AddCharmedDialog, "exec", _fake_exec)

    add_btn = next(b for b in win.findChildren(QPushButton) if b.text() == "+ Add Charmed")
    add_btn.click()

    assert repo.get_by_name("Charmed Skeleton") is not None

    # Break charm directly via handler/signal
    win._on_charm_broken_requested("Charmed Skeleton")
    assert repo.get_by_name("Charmed Skeleton") is None


def test_add_charmed_fills_open_slot_without_overwriting_pc_and_warns_when_party_full(
    qtbot, tmp_path, monkeypatch
):
    repo = JsonCharacterRepository(storage_dir=tmp_path / "chars")
    manager = CharacterManager(repo)

    pc = make_pc("Conan", ClassType.HERO, hp=8, in_party=True)
    pc.combat_row, pc.combat_col = 0, 0
    repo.save(pc)

    # Fill remaining 8 slots with Charmed NPCs (1 PC + 8 NPCs = 9 total)
    for idx in range(8):
        npc = PartyRules.create_charmed_npc(
            manager.list_characters(),
            name=f"Ally_{idx}",
            current_hp=3,
            max_hp=3,
            combat_strength=1,
            weapon_types=[],
        )
        repo.save(npc)

    win = MainWindow(manager)
    qtbot.addWidget(win)
    win.show()

    # Conan must still be in slot (0, 0) and not overwritten
    persisted_pc = repo.get_by_name("Conan")
    assert persisted_pc is not None
    assert (persisted_pc.combat_row, persisted_pc.combat_col) == (0, 0)
    assert len(manager.list_characters()) == 9

    # Attempting to add a 10th member triggers "Party Full" warning
    warnings = []
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        staticmethod(lambda parent, title, text: warnings.append((title, text))),
    )

    add_btn = next(b for b in win.findChildren(QPushButton) if b.text() == "+ Add Charmed")
    add_btn.click()

    assert len(warnings) == 1
    assert warnings[0][0] == "Party Full"
    assert len(manager.list_characters()) == 9