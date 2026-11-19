import pytest
from pathlib import Path
from PySide6.QtWidgets import QMessageBox
from app.models.enums import ClassType, WeaponType
from app.services.repository import JsonCharacterRepository
from app.services.character_manager import CharacterManager
from app.models.character import CharacterCreationConfig
from app.services.theme_manager import ThemeManager
from views.main_window import MainWindow


@pytest.fixture
def manager(tmp_path):
    repo = JsonCharacterRepository(storage_dir=tmp_path / "characters")
    return CharacterManager(repo)


def test_theme_manager_persistence(tmp_path: Path):
    """Verify theme settings save and load correctly across sessions."""
    settings_file = tmp_path / "settings.json"
    tm = ThemeManager(settings_path=settings_file)

    assert tm.load_theme() == "dark_amber.xml"

    tm.save_theme("dark_teal.xml")
    assert tm.load_theme() == "dark_teal.xml"


def test_main_window_initialization(qtbot, manager):
    """Verify MainWindow initializes cleanly with empty repository."""
    window = MainWindow(manager)
    qtbot.addWidget(window)
    window.show()

    assert window.active_list.count() == 0
    assert window.tavern_list.count() == 0
    assert window.tabs.count() == 2


def test_main_window_character_deletion_flow(qtbot, manager, monkeypatch):
    """Verify character deletion workflow and QMessageBox confirmation popup."""
    config = CharacterCreationConfig(
        name="Conan",  # Match the character being added to party
        class_type=ClassType.HERO,
        selected_weapons=[WeaponType.SWORD],
        equipped_weapon=WeaponType.SWORD
    )
    manager.create_character_from_config(config)
    manager.add_to_party("Conan")  # Ensure Conan is in the active party
    
    window = MainWindow(manager)
    qtbot.addWidget(window)
    window.show()

    # Conan will now be in the active party list upon refresh
    assert window.active_list.count() == 1

    # Select character in active list
    window.active_list.setCurrentRow(0)

    # Monkeypatch QMessageBox to auto-confirm deletion
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Yes)

    window._delete_selected_character()
    assert window.active_list.count() == 0
    assert manager.get_character("Conan") is None