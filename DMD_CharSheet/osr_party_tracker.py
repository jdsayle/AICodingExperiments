import flet as ft
import json
import os

import character_creation
import game_catalogs

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "osr_campaign_party.json")
DEFAULT_CAMPAIGN_NAME = "DeathMaze: Deluxe"
LEGACY_CAMPAIGN_NAMES = {"DeathMaze Deluxe", "Dungeon of the Iron Lord"}

class CharacterManagerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "OSR Party & Campaign Tracker"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.padding = 20

        # Pre-populated dummy characters for immediate testing of UI, editing, and saving
        self.party_data = {
            "campaign_name": DEFAULT_CAMPAIGN_NAME,
            "characters": [
                {
                    "name": "Thrain Stonebreaker",
                    "class_name": "Fighter",
                    "strength": 16,
                    "hp_current": 10,
                    "hp_max": 12,
                    "magic_current": 0,
                    "magic_max": 0,
                    "inventory": [{"name": "Rations", "quantity": 5, "effects": "Restores hunger"}, {"name": "Torch", "quantity": 3, "effects": "Burns for 1 hour"}],
                    "weapons": [{"name": "Battleaxe", "attack_modifier": "+2", "damage": "1d8"}],
                    "spells": []
                },
                {
                    "name": "Aurelia the Gray",
                    "class_name": "Magic-User",
                    "strength": 9,
                    "hp_current": 4,
                    "hp_max": 4,
                    "magic_current": 2,
                    "magic_max": 3,
                    "inventory": [{"name": "Spellbook", "quantity": 1, "effects": "Contains arcane formulas"}, {"name": "Dagger", "quantity": 1, "effects": "Light melee"}],
                    "weapons": [{"name": "Dagger", "attack_modifier": "+0", "damage": "1d4"}],
                    "spells": [{"name": "Magic Missile", "description": "1d6+1 force damage, auto-hits"}]
                }
            ]
        }

        # UI Components
        self.party_grid = ft.GridView(
            expand=1,
            runs_count=4,
            max_extent=320,
            spacing=15,
            run_spacing=15,
        )
        
        self.campaign_title_text = ft.Text(
            self.party_data["campaign_name"], 
            size=20, 
            weight=ft.FontWeight.BOLD
        )

        # Attempt to load saved party from disk if it exists; otherwise keep dummy test data
        self.load_party_from_disk(init=True)
        self.build_ui()

    def build_ui(self):
        # Top Toolbar using modern ft.Button and ft.IconButton components
        self.theme_toggle_switch = ft.Switch(
            value=False,
            thumb_icon=ft.Icons.WB_SUNNY,
            tooltip="Switch to dark mode",
            on_change=self.toggle_theme,
        )
        toolbar = ft.Row([
            ft.Row([
                self.campaign_title_text,
                ft.IconButton(icon=ft.Icons.EDIT, tooltip="Edit Campaign Name", on_click=self.open_campaign_edit_dialog)
            ], alignment=ft.MainAxisAlignment.START),
            ft.Row([
                ft.Button(content="Add Character", icon="person_add", on_click=self.start_character_creation),
                ft.Button(content="Save Party", icon="save", on_click=self.save_party_to_disk),
                self.theme_toggle_switch,
            ], alignment=ft.MainAxisAlignment.END)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.home_view = ft.View(
            route="/",
            controls=[toolbar, ft.Divider(), self.party_grid],
        )
        self.page.on_route_change = self.handle_route_change
        self.page.on_view_pop = self.handle_view_pop
        self.handle_route_change()
        self.refresh_grid()

    def start_character_creation(self, e):
        self.page.navigate("/character/create")

    def handle_route_change(self, e=None):
        route = self.page.route
        self.page.views.clear()
        self.page.views.append(self.home_view)

        if route == "/character/create":
            self.page.views.append(
                character_creation.build_class_selection_view(
                    on_select=lambda class_name: self.page.navigate(
                        character_creation.route_for_class(class_name)
                    ),
                    on_cancel=lambda: self.page.navigate("/"),
                )
            )
        else:
            class_name = character_creation.class_for_route(route)
            if class_name:
                self.page.views.append(
                    character_creation.build_character_form_view(
                        class_name=class_name,
                        on_save=self.add_created_character,
                        on_back=lambda: self.page.navigate("/character/create"),
                        on_cancel=lambda: self.page.navigate("/"),
                    )
                )

        self.page.update()

    def handle_view_pop(self, e):
        if e.view is not None and e.view in self.page.views:
            self.page.views.remove(e.view)
        if self.page.views:
            self.page.navigate(self.page.views[-1].route)
        else:
            self.page.navigate("/")

    def add_created_character(self, character):
        self.party_data["characters"].append(character)
        self.refresh_grid()
        self.page.navigate("/")

    def toggle_theme(self, e):
        is_dark = e.control.value
        self.page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        self.theme_toggle_switch.thumb_icon = (
            ft.Icons.NIGHTLIGHT if is_dark else ft.Icons.WB_SUNNY
        )
        self.theme_toggle_switch.tooltip = (
            "Switch to light mode" if is_dark else "Switch to dark mode"
        )
        self.refresh_grid()

    def refresh_grid(self):
        self.party_grid.controls.clear()
        secondary_text_color = (
            ft.Colors.GREY_400
            if self.page.theme_mode == ft.ThemeMode.DARK
            else ft.Colors.GREY_700
        )
        tertiary_text_color = (
            ft.Colors.GREY_500
            if self.page.theme_mode == ft.ThemeMode.DARK
            else ft.Colors.GREY_700
        )
        
        for index, char in enumerate(self.party_data["characters"]):
            is_hero = char.get("class_name") == "Hero"
            is_thief = char.get("class_name") == "Thief"
            
            inv_count = len(char.get("inventory", []))
            wpn_count = len(char.get("weapons", []))
            spell_count = len(char.get("spells", []))
            can_have_spells = char.get("class_name") in game_catalogs.SPELLCASTING_CLASSES
            special_items = char.get(
                "special_items",
                char.get("hero_items", {}),
            )
            inv_count += sum(
                item.get("quantity", 0)
                for item in special_items.values()
                if isinstance(item, dict)
            )
            if is_hero:
                weapon_skill_text = ", ".join(
                    f"+{weapon.get('weapon_skill', 0)}, {weapon['name']}"
                    for weapon in char.get("weapons", [])
                    if weapon.get("weapon_skill", 0) > 0
                ) or "None"
                character_stats = ft.Row(
                    [
                        ft.Text(f"HP: {char['hp_current']} / {char['hp_max']}", weight=ft.FontWeight.W_500),
                        ft.Text(f"MR: {char.get('magic_resistance', 1)} / 5"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
                class_details = [
                    ft.Text(f"Level: {char.get('level', 1)}"),
                    ft.Text(f"Weapon Skill: {weapon_skill_text}", size=12),
                    ft.Text(
                        f"XP: {char.get('experience_points', 0)} | "
                        f"Beazants: {char.get('beazants', 0)}",
                        size=12,
                        color=tertiary_text_color,
                    ),
                ]
            elif is_thief:
                weapon_skill_text = ", ".join(
                    f"+{weapon.get('weapon_skill', 0)}, {weapon['name']}"
                    for weapon in char.get("weapons", [])
                    if weapon.get("weapon_skill", 0) > 0
                ) or "None"
                character_stats = ft.Row(
                    [
                        ft.Text(
                            f"HP: {char['hp_current']} / {char['hp_max']}",
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(f"MR: {char.get('magic_resistance', 1)} / 5"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
                class_details = [
                    ft.Text(f"Level: {char.get('level', 1)}"),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.REMOVE_ROUNDED,
                                icon_size=18,
                                tooltip="Decrease Detrap",
                                disabled=char.get("detrap", 1) <= 0,
                                on_click=lambda e, idx=index: self.adjust_detrap(idx, -1),
                            ),
                            ft.Text(f"Detrap: {char.get('detrap', 1)}"),
                            ft.IconButton(
                                icon=ft.Icons.ADD_ROUNDED,
                                icon_size=18,
                                tooltip="Increase Detrap",
                                disabled=char.get("detrap", 1) >= 5,
                                on_click=lambda e, idx=index: self.adjust_detrap(idx, 1),
                            ),
                        ],
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text(f"Weapon Skill: {weapon_skill_text}", size=12),
                ]
            else:
                character_stats = ft.Row(
                    [
                        ft.Text(f"HP: {char['hp_current']} / {char['hp_max']}", weight=ft.FontWeight.W_500),
                        ft.Text(f"STR: {char['strength']}"),
                        ft.Text(f"MAG: {char['magic_current']}/{char['magic_max']}" if char['magic_max'] > 0 else "MAG: N/A"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
                class_details = []

            card_details = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            char["name"],
                            weight=ft.FontWeight.BOLD,
                            size=16,
                        ),
                        ft.Text(
                            f"Class: {char.get('class_name', 'Adventurer')}",
                            size=12,
                            color=secondary_text_color,
                        ),
                        ft.Divider(height=10),
                        character_stats,
                        *class_details,
                        ft.Divider(height=10),
                        ft.Text(
                            f"Items: {inv_count} | Weapons: {wpn_count} | "
                            f"Spells: {spell_count}"
                            if can_have_spells
                            else f"Items: {inv_count} | Weapons: {wpn_count}",
                            size=11,
                            color=tertiary_text_color,
                        ),
                    ],
                    spacing=5,
                ),
                padding=15,
                on_click=lambda e, idx=index: self.open_character_details(idx),
                ink=True,
                tooltip="View character details",
            )
            card_actions = ft.Row(
                [
                    ft.OutlinedButton(content="Manage Sheet", icon="edit_note", on_click=lambda e, idx=index: self.open_character_dialog(idx)),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, tooltip="Remove", on_click=lambda e, idx=index: self.delete_character(idx))
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )

            card = ft.Card(
                expand=True,
                content=ft.Column(
                    [
                        card_details,
                        ft.Container(expand=True),
                        card_actions,
                    ],
                    spacing=0,
                    expand=True,
                ),
            )
            self.party_grid.controls.append(card)
        
        self.page.update()

    def open_character_details(self, char_index):
        char = self.party_data["characters"][char_index]
        class_name = char.get("class_name", "Adventurer")
        spellcaster = class_name in game_catalogs.SPELLCASTING_CLASSES

        stat_lines = [
            f"Health: {char.get('hp_current', 0)} / {char.get('hp_max', 0)}"
        ]
        if "strength" in char:
            stat_lines.append(f"Strength: {char['strength']}")
        if "magic_current" in char or "magic_max" in char:
            stat_lines.append(
                f"Magic: {char.get('magic_current', 0)} / {char.get('magic_max', 0)}"
            )
        for key, label in (
            ("level", "Level"),
            ("magic_resistance", "Magic Resistance"),
            ("detrap", "Detrap"),
            ("experience_points", "Experience Points"),
            ("beazants", "Beazants"),
        ):
            if key in char:
                stat_lines.append(f"{label}: {char[key]}")

        weapons = char.get("weapons", [])
        weapon_lines = [
            " | ".join(
                [
                    str(weapon.get("name", "Weapon")),
                    *(
                        [f"Attack: {weapon['attack_modifier']}"]
                        if weapon.get("attack_modifier")
                        else []
                    ),
                    *(
                        [f"Damage: {weapon['damage']}"]
                        if weapon.get("damage")
                        else []
                    ),
                    *(
                        [f"Weapon Skill: +{weapon['weapon_skill']}"]
                        if weapon.get("weapon_skill", 0)
                        else []
                    ),
                ]
            )
            for weapon in weapons
        ]
        inventory_lines = [
            f"{item.get('name', 'Item')} (x{item.get('quantity', 0)})"
            + (f" - {item['effects']}" if item.get("effects") else "")
            for item in char.get("inventory", [])
        ]
        special_items = char.get(
            "special_items",
            char.get("hero_items", {}),
        )
        for category, item in special_items.items():
            if isinstance(item, dict) and item.get("name"):
                inventory_lines.append(
                    f"{category}: {item['name']} (x{item.get('quantity', 0)})"
                )

        detail_controls = [
            ft.Text(class_name),
            ft.Text("Stats", weight=ft.FontWeight.BOLD),
            *[ft.Text(line) for line in stat_lines],
            ft.Divider(),
            ft.Text("Weapons & Bonuses", weight=ft.FontWeight.BOLD),
            *[
                ft.Text(line)
                for line in (weapon_lines or ["No weapons recorded."])
            ],
            ft.Divider(),
            ft.Text("Items", weight=ft.FontWeight.BOLD),
            *[
                ft.Text(line)
                for line in (inventory_lines or ["No items recorded."])
            ],
        ]
        if spellcaster:
            spells = char.get("spells", [])
            detail_controls.extend(
                [
                    ft.Divider(),
                    ft.Text("Spells", weight=ft.FontWeight.BOLD),
                    *[
                        ft.Text(
                            f"{spell.get('name', 'Unnamed spell')} "
                            f"({max(0, int(spell.get('uses_remaining', 1)))} uses) "
                            f"- {spell.get('description', '')}",
                            color=(
                                ft.Colors.GREY_500
                                if int(spell.get("uses_remaining", 1)) <= 0
                                else None
                            ),
                        )
                        for spell in spells
                    ],
                    *([] if spells else [ft.Text("No spells recorded.")]),
                ]
            )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(char.get("name", "Character Details")),
            content=ft.Container(
                width=560,
                height=560,
                content=ft.Column(detail_controls, scroll=ft.ScrollMode.AUTO, tight=True),
            ),
            actions=[
                ft.TextButton(
                    content="Close",
                    on_click=lambda e: self.page.pop_dialog(),
                )
            ],
        )
        self.page.show_dialog(dialog)

    def adjust_detrap(self, char_index, amount):
        char = self.party_data["characters"][char_index]
        char["detrap"] = max(0, min(5, char.get("detrap", 1) + amount))
        self.refresh_grid()

    def build_special_items_editor(self, existing_items):
        item_fields = {}
        item_rows = []
        for category in game_catalogs.ITEM_CATEGORIES:
            existing_item = existing_items.get(category, {})
            existing_name = existing_item.get("name")
            options = list(game_catalogs.ITEM_OPTIONS[category])
            if existing_name and existing_name not in options:
                options.append(existing_name)
            dropdown = ft.Dropdown(
                label=category,
                hint_text="Options will be added later",
                options=[ft.dropdown.Option(item) for item in options],
                value=existing_name,
                disabled=not options,
            )
            quantity = ft.TextField(
                label="Quantity",
                value=str(existing_item.get("quantity", 0)),
                width=120,
                keyboard_type=ft.KeyboardType.NUMBER,
                disabled=not (options and existing_name),
            )

            def update_quantity_state(e, quantity_field=quantity):
                quantity_field.disabled = not bool(e.control.value)
                quantity_field.update()

            dropdown.on_select = update_quantity_state
            item_fields[category] = (dropdown, quantity)
            item_rows.append(ft.Row([dropdown, quantity]))

        def get_item_values():
            return {
                category: {
                    "name": dropdown.value,
                    "quantity": (
                        int(quantity.value or "0") if dropdown.value else 0
                    ),
                }
                for category, (dropdown, quantity) in item_fields.items()
            }

        return item_rows, get_item_values

    def open_campaign_edit_dialog(self, e):
        txt_name = ft.TextField(
            label="Campaign Name",
            value=self.campaign_title_text.value,
        )

        def save_name(e):
            campaign_name = (txt_name.value or "").strip()
            if not campaign_name:
                txt_name.error_text = "Campaign name cannot be blank."
                self.page.update()
                return
            txt_name.error_text = None
            self.party_data["campaign_name"] = campaign_name
            self.campaign_title_text.value = campaign_name
            self.page.pop_dialog()
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Campaign Name"),
            content=txt_name,
            actions=[
                ft.TextButton(content="Cancel", on_click=lambda e: self.page.pop_dialog()),
                ft.Button(content="Save", on_click=save_name)
            ]
        )
        self.page.show_dialog(dialog)

    def open_thief_sheet_dialog(self, char_index):
        char = self.party_data["characters"][char_index]
        fields = {
            "name": ft.TextField(label="Character Name", value=char.get("name", "")),
            "level": ft.TextField(
                label="Level",
                value=str(char.get("level", 1)),
                keyboard_type=ft.KeyboardType.NUMBER,
            ),
            "hp_current": ft.TextField(
                label="Current Health",
                value=str(char.get("hp_current", 6)),
                keyboard_type=ft.KeyboardType.NUMBER,
            ),
            "hp_max": ft.TextField(
                label="Maximum Health",
                value=str(char.get("hp_max", 6)),
                keyboard_type=ft.KeyboardType.NUMBER,
            ),
            "magic_resistance": ft.TextField(
                label="Magic Resistance (max 5)",
                value=str(char.get("magic_resistance", 1)),
                keyboard_type=ft.KeyboardType.NUMBER,
            ),
            "detrap": ft.TextField(
                label="Detrap (max 5)",
                value=str(char.get("detrap", 1)),
                keyboard_type=ft.KeyboardType.NUMBER,
            ),
        }
        weapons = char.get("weapons", [])
        weapon_skill_fields = [
            ft.TextField(
                label=f"{weapon.get('name', 'Weapon')} Skill",
                value=str(weapon.get("weapon_skill", 0)),
                width=180,
                keyboard_type=ft.KeyboardType.NUMBER,
            )
            for weapon in weapons
        ]
        existing_special_items = char.get(
            "special_items",
            char.get("hero_items", {}),
        )
        item_rows, get_item_values = self.build_special_items_editor(
            existing_special_items
        )

        def save_thief_sheet(e):
            try:
                values = {
                    key: int(field.value or "0")
                    for key, field in fields.items()
                    if key != "name"
                }
                skill_values = [
                    int(field.value or "0") for field in weapon_skill_fields
                ]
                item_values = get_item_values()
                if any(value < 0 for value in values.values()) or any(
                    skill < 0 for skill in skill_values
                ) or any(
                    item["quantity"] < 0 for item in item_values.values()
                ):
                    raise ValueError
                if values["level"] < 1:
                    fields["level"].error_text = "Level must be at least 1."
                    fields["level"].update()
                    return
                if values["detrap"] > 5:
                    fields["detrap"].error_text = "Detrap cannot exceed 5."
                    fields["detrap"].update()
                    return
                if values["magic_resistance"] > 5:
                    fields["magic_resistance"].error_text = (
                        "Magic Resistance cannot exceed 5."
                    )
                    fields["magic_resistance"].update()
                    return
                if values["hp_current"] > values["hp_max"]:
                    fields["hp_current"].error_text = (
                        "Current Health cannot exceed Maximum Health."
                    )
                    fields["hp_current"].update()
                    return
                if not (fields["name"].value or "").strip():
                    fields["name"].error_text = "Character name cannot be blank."
                    fields["name"].update()
                    return
            except ValueError:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("Enter valid non-negative whole numbers for Thief stats.")
                )
                self.page.snack_bar.open = True
                self.page.update()
                return

            char.update(values)
            char["name"] = fields["name"].value.strip()
            char["weapons"] = [
                {**weapon, "weapon_skill": skill_values[slot]}
                for slot, weapon in enumerate(weapons)
            ]
            char["special_items"] = item_values
            char.pop("hero_items", None)
            self.page.pop_dialog()
            self.refresh_grid()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Manage Thief Sheet"),
            content=ft.Container(
                width=600,
                height=500,
                content=ft.Column(
                    [
                        fields["name"],
                        ft.Row([fields["level"], fields["magic_resistance"]]),
                        ft.Row([fields["hp_current"], fields["hp_max"]]),
                        fields["detrap"],
                        ft.Text("Weapon Skill", weight=ft.FontWeight.BOLD),
                        *weapon_skill_fields,
                        ft.Divider(),
                        ft.Text("Rings, Spices, Medallions, and Potions"),
                        *item_rows,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    tight=True,
                ),
            ),
            actions=[
                ft.TextButton(
                    content="Cancel",
                    on_click=lambda e: self.page.pop_dialog(),
                ),
                ft.Button(content="Save", on_click=save_thief_sheet),
            ],
        )
        self.page.show_dialog(dialog)

    def open_hero_sheet_dialog(self, char_index):
        char = self.party_data["characters"][char_index]
        fields = {
            "name": ft.TextField(label="Character Name", value=char.get("name", "")),
            "level": ft.TextField(
                label="Level",
                value=str(char.get("level", 1)),
                keyboard_type=ft.KeyboardType.NUMBER,
            ),
            "hp_current": ft.TextField(
                label="Current Health",
                value=str(char.get("hp_current", 8)),
                keyboard_type=ft.KeyboardType.NUMBER,
            ),
            "hp_max": ft.TextField(
                label="Maximum Health",
                value=str(char.get("hp_max", 8)),
                keyboard_type=ft.KeyboardType.NUMBER,
            ),
            "magic_resistance": ft.TextField(
                label="Magic Resistance (max 5)",
                value=str(char.get("magic_resistance", 1)),
                keyboard_type=ft.KeyboardType.NUMBER,
            ),
            "experience_points": ft.TextField(
                label="Experience Points",
                value=str(char.get("experience_points", 0)),
                keyboard_type=ft.KeyboardType.NUMBER,
            ),
            "beazants": ft.TextField(
                label="Beazants",
                value=str(char.get("beazants", 0)),
                keyboard_type=ft.KeyboardType.NUMBER,
            ),
        }
        weapons = char.get("weapons", [])
        weapon_skill_fields = [
            ft.TextField(
                label=f"{weapon.get('name', 'Weapon')} Skill",
                value=str(weapon.get("weapon_skill", 0)),
                width=180,
                keyboard_type=ft.KeyboardType.NUMBER,
            )
            for weapon in weapons
        ]
        existing_special_items = char.get(
            "special_items",
            char.get("hero_items", {}),
        )
        item_rows, get_item_values = self.build_special_items_editor(
            existing_special_items
        )

        def save_hero_sheet(e):
            try:
                values = {
                    key: int(field.value or "0")
                    for key, field in fields.items()
                    if key != "name"
                }
                skill_values = [int(field.value or "0") for field in weapon_skill_fields]
                item_values = get_item_values()
                if any(value < 0 for value in values.values()) or any(
                    value < 0 for value in skill_values
                ) or any(
                    item["quantity"] < 0 for item in item_values.values()
                ):
                    raise ValueError
                if values["level"] < 1:
                    fields["level"].error_text = "Level must be at least 1."
                    fields["level"].update()
                    return
                if values["magic_resistance"] > 5:
                    fields["magic_resistance"].error_text = "Magic Resistance cannot exceed 5."
                    fields["magic_resistance"].update()
                    return
                if values["hp_current"] > values["hp_max"]:
                    fields["hp_current"].error_text = "Current Health cannot exceed Maximum Health."
                    fields["hp_current"].update()
                    return
                if not (fields["name"].value or "").strip():
                    fields["name"].error_text = "Character name cannot be blank."
                    fields["name"].update()
                    return
            except ValueError:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("Enter valid non-negative whole numbers for Hero stats.")
                )
                self.page.snack_bar.open = True
                self.page.update()
                return

            for field in list(fields.values()) + weapon_skill_fields:
                field.error_text = None
            char.update(values)
            char["name"] = fields["name"].value.strip()
            char["weapons"] = [
                {**weapon, "weapon_skill": skill_values[slot]}
                for slot, weapon in enumerate(weapons)
            ]
            char["special_items"] = item_values
            char.pop("hero_items", None)
            self.page.pop_dialog()
            self.refresh_grid()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Manage Hero Sheet"),
            content=ft.Container(
                width=680,
                height=650,
                content=ft.Column(
                    [
                        fields["name"],
                        ft.Row([fields["level"], fields["magic_resistance"]]),
                        ft.Row([fields["hp_current"], fields["hp_max"]]),
                        ft.Row([fields["experience_points"], fields["beazants"]]),
                        ft.Text("Weapon Skill", weight=ft.FontWeight.BOLD),
                        *weapon_skill_fields,
                        ft.Divider(),
                        ft.Text("Rings, Spices, Medallions, and Potions"),
                        *item_rows,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    tight=True,
                ),
            ),
            actions=[
                ft.TextButton(content="Cancel", on_click=lambda e: self.page.pop_dialog()),
                ft.Button(content="Save", on_click=save_hero_sheet),
            ],
        )
        self.page.show_dialog(dialog)

    def open_character_dialog(self, char_index=None):
        if not isinstance(char_index, int):
            char_index = None
        elif self.party_data["characters"][char_index].get("class_name") == "Hero":
            self.open_hero_sheet_dialog(char_index)
            return
        elif self.party_data["characters"][char_index].get("class_name") == "Thief":
            self.open_thief_sheet_dialog(char_index)
            return

        is_edit = char_index is not None
        char = self.party_data["characters"][char_index] if is_edit else {
            "name": "",
            "class_name": "Fighter",
            "strength": 10,
            "hp_current": 8,
            "hp_max": 8,
            "magic_current": 0,
            "magic_max": 0,
            "inventory": [],
            "weapons": [],
        }
        can_have_spells = char.get("class_name") in game_catalogs.SPELLCASTING_CLASSES

        txt_name = ft.TextField(label="Character Name", value=char["name"])
        txt_class = ft.TextField(label="Class / Role", value=char["class_name"])
        txt_str = ft.TextField(label="Strength", value=str(char["strength"]), keyboard_type=ft.KeyboardType.NUMBER)
        txt_hp_curr = ft.TextField(label="Current HP", value=str(char["hp_current"]), keyboard_type=ft.KeyboardType.NUMBER)
        txt_hp_max = ft.TextField(label="Max HP", value=str(char["hp_max"]), keyboard_type=ft.KeyboardType.NUMBER)
        txt_mag_curr = ft.TextField(label="Current Magic", value=str(char["magic_current"]), keyboard_type=ft.KeyboardType.NUMBER)
        txt_mag_max = ft.TextField(label="Max Magic", value=str(char["magic_max"]), keyboard_type=ft.KeyboardType.NUMBER)

        inv_list_column = ft.Column(scroll=ft.ScrollMode.AUTO, height=120)
        wpn_list_column = ft.Column(scroll=ft.ScrollMode.AUTO, height=120)
        spell_list_column = ft.Column(scroll=ft.ScrollMode.AUTO, height=120)
        item_rows, get_item_values = self.build_special_items_editor(
            char.get("special_items", char.get("hero_items", {}))
        )
        special_items_section = ft.Column(
            [
                ft.Divider(),
                ft.Text("Rings, Spices, Medallions, and Potions"),
                *item_rows,
            ],
        )

        working_inv = list(char["inventory"])
        working_wpn = list(char["weapons"])
        working_spells = [
            {
                **spell,
                "uses_remaining": max(0, int(spell.get("uses_remaining", 1))),
            }
            for spell in char.get("spells", [])
        ] if can_have_spells else []

        def render_sublists():
            inv_list_column.controls.clear()
            for idx, item in enumerate(working_inv):
                inv_list_column.controls.append(
                    ft.Row([
                        ft.Text(f"{item['name']} (x{item['quantity']}) - Eff: {item['effects']}", size=12, expand=True),
                        ft.IconButton(icon=ft.Icons.DELETE, icon_size=16, on_click=lambda e, i=idx: remove_item(i))
                    ])
                )
            wpn_list_column.controls.clear()
            for idx, wpn in enumerate(working_wpn):
                wpn_list_column.controls.append(
                    ft.Row([
                        ft.Text(f"{wpn['name']} | Mod: {wpn['attack_modifier']} | Dmg: {wpn['damage']}", size=12, expand=True),
                        ft.IconButton(icon=ft.Icons.DELETE, icon_size=16, on_click=lambda e, i=idx: remove_wpn(i))
                    ])
                )
            if can_have_spells:
                spell_list_column.controls.clear()
                for idx, spell in enumerate(working_spells):
                    uses_remaining = spell["uses_remaining"]
                    spell_list_column.controls.append(
                        ft.Row([
                            ft.Text(
                                f"{spell['name']} - {spell.get('description', '')} "
                                f"(Uses: {uses_remaining})",
                                size=12,
                                expand=True,
                                color=(
                                    ft.Colors.GREY_500
                                    if uses_remaining == 0
                                    else None
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.REMOVE,
                                icon_size=16,
                                tooltip="Record spell used",
                                disabled=uses_remaining == 0,
                                on_click=lambda e, i=idx: adjust_spell_uses(i, -1),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ADD,
                                icon_size=16,
                                tooltip="Increase available uses",
                                on_click=lambda e, i=idx: adjust_spell_uses(i, 1),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_size=16,
                                tooltip="Remove spell",
                                on_click=lambda e, i=idx: remove_spell(i),
                            ),
                        ])
                    )
            self.page.update()

        def remove_item(i):
            working_inv.pop(i)
            render_sublists()

        def remove_wpn(i):
            working_wpn.pop(i)
            render_sublists()

        def remove_spell(i):
            working_spells.pop(i)
            render_sublists()

        def adjust_spell_uses(i, amount):
            spell = working_spells[i]
            spell["uses_remaining"] = max(0, spell["uses_remaining"] + amount)
            render_sublists()

        def open_add_item_dlg(e):
            i_name = ft.TextField(label="Item Name")
            i_qty = ft.TextField(label="Quantity", value="1", keyboard_type=ft.KeyboardType.NUMBER)
            i_eff = ft.TextField(label="Item Effects / Properties")

            def confirm_item(e):
                working_inv.append({"name": i_name.value, "quantity": int(i_qty.value or 1), "effects": i_eff.value})
                self.page.dialog = main_dlg
                render_sublists()

            self.page.dialog = ft.AlertDialog(
                title=ft.Text("Add Inventory Item"),
                content=ft.Column([i_name, i_qty, i_eff], tight=True),
                actions=[ft.TextButton(content="Add", on_click=confirm_item)]
            )
            self.page.update()

        def open_add_wpn_dlg(e):
            w_name = ft.TextField(label="Weapon Name")
            w_mod = ft.TextField(label="Attack Modifier (e.g. +1)")
            w_dmg = ft.TextField(label="Damage (e.g. 1d8)")

            def confirm_wpn(e):
                working_wpn.append({"name": w_name.value, "attack_modifier": w_mod.value, "damage": w_dmg.value})
                self.page.dialog = main_dlg
                render_sublists()

            self.page.dialog = ft.AlertDialog(
                title=ft.Text("Add Weapon"),
                content=ft.Column([w_name, w_mod, w_dmg], tight=True),
                actions=[ft.TextButton(content="Add", on_click=confirm_wpn)]
            )
            self.page.update()

        def open_add_spell_dlg(e):
            s_name = ft.TextField(label="Spell Name")
            s_desc = ft.TextField(label="Effect / Details")

            def confirm_spell(e):
                name = (s_name.value or "").strip()
                if not name:
                    s_name.error_text = "Spell name is required."
                    s_name.update()
                    return
                working_spells.append(
                    {
                        "name": name,
                        "description": (s_desc.value or "").strip(),
                        "uses_remaining": 1,
                    }
                )
                self.page.dialog = main_dlg
                render_sublists()

            self.page.dialog = ft.AlertDialog(
                title=ft.Text("Add Spell"),
                content=ft.Column([s_name, s_desc], tight=True),
                actions=[ft.TextButton(content="Add", on_click=confirm_spell)]
            )
            self.page.update()

        render_sublists()

        def save_character(e):
            try:
                char_data = {
                    "name": txt_name.value or "Unnamed",
                    "class_name": txt_class.value or "Adventurer",
                    "strength": int(txt_str.value or 10),
                    "hp_current": int(txt_hp_curr.value or 1),
                    "hp_max": int(txt_hp_max.value or 1),
                    "magic_current": int(txt_mag_curr.value or 0),
                    "magic_max": int(txt_mag_max.value or 0),
                    "inventory": working_inv,
                    "weapons": working_wpn,
                }
                special_items = get_item_values()
                if any(item["quantity"] < 0 for item in special_items.values()):
                    raise ValueError
                char_data["special_items"] = special_items
                if char_data["class_name"] in game_catalogs.SPELLCASTING_CLASSES:
                    char_data["spells"] = working_spells
                if is_edit:
                    self.party_data["characters"][char_index] = char_data
                else:
                    self.party_data["characters"].append(char_data)
                
                self.page.dialog.open = False
                self.refresh_grid()
            except ValueError:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(
                        "Enter valid non-negative whole numbers for character "
                        "stats and special item quantities."
                    )
                )
                self.page.snack_bar.open = True
                self.page.update()

        manage_controls = [
            txt_name,
            ft.Row([txt_class, txt_str]),
            ft.Row([txt_hp_curr, txt_hp_max, txt_mag_curr, txt_mag_max]),
            ft.Divider(),
            ft.Row([ft.Text("Weapons", weight=ft.FontWeight.BOLD), ft.TextButton(content="+ Add", on_click=open_add_wpn_dlg)]),
            wpn_list_column,
            ft.Divider(),
            ft.Row([ft.Text("Inventory & Effects", weight=ft.FontWeight.BOLD), ft.TextButton(content="+ Add", on_click=open_add_item_dlg)]),
            inv_list_column,
            special_items_section,
        ]
        if can_have_spells:
            manage_controls.extend(
                [
                    ft.Divider(),
                    ft.Row([ft.Text("Spells", weight=ft.FontWeight.BOLD), ft.TextButton(content="+ Add", on_click=open_add_spell_dlg)]),
                    spell_list_column,
                ]
            )

        main_dlg = ft.AlertDialog(
            title=ft.Text("Edit Character Sheet" if is_edit else "New Character"),
            content=ft.Container(
                content=ft.Column(manage_controls, scroll=ft.ScrollMode.AUTO, tight=True),
                width=500,
                height=550
            ),
            actions=[
                ft.TextButton(content="Cancel", on_click=lambda e: setattr(self.page.dialog, 'open', False) or self.page.update()),
                ft.Button(content="Save Character", on_click=save_character)
            ]
        )

        self.page.dialog = main_dlg
        self.page.dialog.open = True
        self.page.update()

    def delete_character(self, index):
        del self.party_data["characters"][index]
        self.refresh_grid()

    def save_party_to_disk(self, e):
        with open(SAVE_FILE, "w") as f:
            json.dump(self.party_data, f, indent=4)
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Party successfully saved to {SAVE_FILE}"))
        self.page.snack_bar.open = True
        self.page.update()

    def load_party_from_disk(self, init=False):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    self.party_data = json.load(f)
                characters = []
                for character in self.party_data.get("characters", []):
                    character_type = str(
                        character.pop("char_type", "PC")
                    ).strip().upper()
                    if character_type != "PC":
                        continue
                    legacy_items = character.pop("hero_items", None)
                    if legacy_items is not None:
                        special_items = character.setdefault("special_items", {})
                        for category, item in legacy_items.items():
                            special_items.setdefault(category, item)
                    characters.append(character)
                self.party_data["characters"] = characters
                campaign_name = self.party_data.get("campaign_name")
                if not campaign_name or campaign_name in LEGACY_CAMPAIGN_NAMES:
                    campaign_name = DEFAULT_CAMPAIGN_NAME
                self.party_data["campaign_name"] = campaign_name
                self.campaign_title_text.value = self.party_data["campaign_name"]
                if not init:
                    self.refresh_grid()
                    self.page.snack_bar = ft.SnackBar(ft.Text("Party loaded successfully!"))
                    self.page.snack_bar.open = True
                    self.page.update()
            except Exception:
                pass
        else:
            self.party_data["campaign_name"] = DEFAULT_CAMPAIGN_NAME
            self.campaign_title_text.value = DEFAULT_CAMPAIGN_NAME

def main(page: ft.Page):
    CharacterManagerApp(page)

if __name__ == "__main__":
    ft.run(main)