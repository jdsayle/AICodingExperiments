import sys
from PySide6.QtWidgets import QApplication
from app.services.repository import JsonCharacterRepository
from app.services.character_manager import CharacterManager
from app.services.theme_manager import ThemeManager
from views.main_window import MainWindow


def main():
    """Application entry point for DeathMaze Deluxe Desktop App."""
    app = QApplication(sys.argv)

    # Initialize Persistence & Managers
    repository = JsonCharacterRepository(storage_dir="data/characters")
    manager = CharacterManager(repository)
    
    # Apply qt-material Theme with Settings Persistence
    theme_manager = ThemeManager(settings_path="data/settings.json")
    theme_manager.apply_theme(app)

    # Launch Main Application Window
    window = MainWindow(manager)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()