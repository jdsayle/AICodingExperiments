import json
from pathlib import Path
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet


class ThemeManager:
    """Manages application styling via qt-material and persists user preferences."""

    DEFAULT_THEME = "dark_amber.xml"

    def __init__(self, settings_path: str | Path = "data/settings.json"):
        self.settings_path = Path(settings_path)
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)

    def load_theme(self) -> str:
        """Loads saved theme preference from JSON settings or returns default."""
        if not self.settings_path.exists():
            return self.DEFAULT_THEME
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("theme", self.DEFAULT_THEME)
        except (json.JSONDecodeError, OSError):
            return self.DEFAULT_THEME

    def save_theme(self, theme_name: str) -> None:
        """Saves active theme preference to JSON settings file."""
        data = {"theme": theme_name}
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def apply_theme(self, app: QApplication, theme_name: str | None = None) -> str:
        """Applies qt-material stylesheet to the application instance."""
        target_theme = theme_name or self.load_theme()
        try:
            apply_stylesheet(app, theme=target_theme)
            self.save_theme(target_theme)
        except Exception:
            # Fall back to default theme if specified theme file fails
            apply_stylesheet(app, theme=self.DEFAULT_THEME)
            self.save_theme(self.DEFAULT_THEME)
            target_theme = self.DEFAULT_THEME
        return target_theme