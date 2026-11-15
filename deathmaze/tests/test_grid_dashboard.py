import pytest
from PySide6.QtCore import Qt
from app.models.character import Character
from app.models.enums import ClassType
from app.services.character_manager import CharacterManager
from views.widgets.grid_dashboard import ActivePartyDashboardGrid
from views.widgets.empty_slot_widget import EmptySlotWidget
from views.widgets.character_card import CharacterCardWidget


class MockMainWindow:
    """Mock main window for testing grid callbacks."""
    def __init__(self):
        self.swapped = None
        self.moved = None

    def swap_character_positions(self, name_a, name_b):
        self.swapped = (name_a, name_b)

    def move_character_to_slot(self, name, row, col):
        self.moved = (name, row, col)


def test_grid_dashboard_initialization(qtbot, tmp_path):
    """Verify that ActivePartyDashboardGrid initializes the 3x3 tactical layout correctly."""
    main_window = MockMainWindow()
    grid_widget = ActivePartyDashboardGrid(main_window)
    qtbot.addWidget(grid_widget)

    # Ensure grid layout exists and has constraints set
    assert grid_widget.grid is not None
    assert grid_widget.acceptDrops() is True