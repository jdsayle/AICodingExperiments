from collections.abc import Callable

import flet as ft

import game_catalogs


CHARACTER_CLASSES = game_catalogs.CHARACTER_CLASSES

_CLASS_ROUTES = {
    class_name.lower().replace(" ", "-"): class_name
    for class_name in CHARACTER_CLASSES
}


def route_for_class(class_name: str) -> str:
    slug = class_name.lower().replace(" ", "-")
    if slug not in _CLASS_ROUTES:
        raise ValueError(f"Unknown character class: {class_name}")
    return f"/character/create/{slug}"


def class_for_route(route: str) -> str | None:
    return _CLASS_ROUTES.get(route.rsplit("/", 1)[-1])


def build_hero_creation_view(
    on_save: Callable[[dict[str, object]], None],
    on_back: Callable[[], None],
    on_cancel: Callable[[], None],
) -> ft.View:
    name_field = ft.TextField(label="Character Name", autofocus=True)
    weapon_options = [
        ft.dropdown.Option(name) for name in game_catalogs.weapons_for_class("Hero")
    ]
    weapon_one = ft.Dropdown(label="Weapon 1", options=weapon_options)
    weapon_two = ft.Dropdown(label="Weapon 2", options=weapon_options)
    advancement = ft.Dropdown(
        label="Choose one advancement",
        options=[
            ft.dropdown.Option(key="health", text="Increase Health by 1"),
            ft.dropdown.Option(key="weapon_skill", text="Gain +1 Weapon Skill"),
        ],
    )
    skill_weapon = ft.Dropdown(
        label="Weapon receiving +1 Weapon Skill",
        options=[],
        disabled=True,
    )
    starting_health = ft.Text("Starting Health: 8")

    def update_weapon_skill_options(e):
        skill_weapon.options = [
            ft.dropdown.Option(key=str(slot), text=f"Weapon {slot + 1}: {weapon}")
            for slot, weapon in enumerate((weapon_one.value, weapon_two.value))
            if weapon
        ]
        skill_weapon.value = None
        skill_weapon.update()

    def update_advancement(e):
        is_health = advancement.value == "health"
        starting_health.value = f"Starting Health: {9 if is_health else 8}"
        skill_weapon.disabled = advancement.value != "weapon_skill"
        if skill_weapon.disabled:
            skill_weapon.value = None
        else:
            update_weapon_skill_options(e)
        starting_health.update()
        skill_weapon.update()

    weapon_one.on_select = update_weapon_skill_options
    weapon_two.on_select = update_weapon_skill_options
    advancement.on_select = update_advancement

    def save_hero(e):
        required_fields = (
            (name_field, (name_field.value or "").strip(), "Character name is required."),
            (weapon_one, weapon_one.value, "Choose Weapon 1."),
            (weapon_two, weapon_two.value, "Choose Weapon 2."),
            (advancement, advancement.value, "Choose one advancement."),
        )
        for field, value, message in required_fields:
            if not value:
                field.error_text = message
                field.update()
                return
            field.error_text = None

        if advancement.value == "weapon_skill" and skill_weapon.value not in {"0", "1"}:
            skill_weapon.error_text = "Choose which weapon receives +1 Weapon Skill."
            skill_weapon.update()
            return

        selected_weapons = [weapon_one.value, weapon_two.value]
        skill_slot = int(skill_weapon.value) if advancement.value == "weapon_skill" else None
        weapon_records = [
            {
                "name": weapon,
                "attack_modifier": "+0",
                "damage": "",
                "weapon_skill": 1 if slot == skill_slot else 0,
                "combat_bonus": 0,
                "equipped": slot == 0,
            }
            for slot, weapon in enumerate(selected_weapons)
        ]
        on_save(
            {
                "name": (name_field.value or "").strip(),
                "class_name": "Hero",
                "level": 1,
                "hp_current": 9 if advancement.value == "health" else 8,
                "hp_max": 9 if advancement.value == "health" else 8,
                "magic_current": 0,
                "magic_max": 0,
                "magic_resistance": 1,
                "experience_points": 0,
                "beazants": 0,
                "weapons": weapon_records,
                "inventory": [],
                "special_items": {
                    category: []
                    for category in game_catalogs.ITEM_CATEGORIES
                },
            }
        )

    return ft.View(
        route=route_for_class("Hero"),
        appbar=ft.AppBar(title=ft.Text("Create Hero")),
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Container(
                    width=720,
                    padding=24,
                    bgcolor=ft.Colors.SURFACE,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        blur_radius=18,
                        spread_radius=1,
                        color=ft.Colors.BLACK_26,
                        offset=ft.Offset(0, 6),
                    ),
                    content=ft.Column(
                        [
                            ft.Text("Hero creation", size=20, weight=ft.FontWeight.BOLD),
                            name_field,
                            ft.Text("Level: 1  |  Magic Resistance: 1 / 5"),
                            ft.Text("Choose two weapons (duplicates are allowed)."),
                            ft.Row([weapon_one, weapon_two]),
                            ft.Divider(),
                            ft.Text("Choose exactly one advancement."),
                            advancement,
                            starting_health,
                            skill_weapon,
                            ft.Row(
                                [
                                    ft.TextButton(
                                        content="Back to Classes",
                                        on_click=lambda e: on_back(),
                                    ),
                                    ft.TextButton(
                                        content="Cancel",
                                        on_click=lambda e: on_cancel(),
                                    ),
                                    ft.Button(
                                        content="Create Character",
                                        on_click=save_hero,
                                    ),
                                ]
                            ),
                        ],
                        spacing=12,
                        scroll=ft.ScrollMode.AUTO,
                        width=672,
                    ),
                ),
            )
        ],
    )


def build_thief_creation_view(
    on_save: Callable[[dict[str, object]], None],
    on_back: Callable[[], None],
    on_cancel: Callable[[], None],
) -> ft.View:
    name_field = ft.TextField(label="Character Name", autofocus=True)
    weapon_options = [
        ft.dropdown.Option(name) for name in game_catalogs.weapons_for_class("Thief")
    ]
    weapon_one = ft.Dropdown(label="Weapon 1", options=weapon_options)
    weapon_two = ft.Dropdown(label="Weapon 2", options=weapon_options)
    advancement = ft.Dropdown(
        label="Choose one advancement",
        options=[
            ft.dropdown.Option(key="health", text="Increase Health by 1"),
            ft.dropdown.Option(key="weapon_skill", text="Gain +1 Weapon Skill"),
            ft.dropdown.Option(key="detrap", text="Increase Detrap by 1"),
        ],
    )
    skill_weapon = ft.Dropdown(
        label="Weapon receiving +1 Weapon Skill",
        options=[],
        disabled=True,
    )
    starting_health = ft.Text("Starting Health: 6")
    starting_detrap = ft.Text("Starting Detrap: 1")

    def update_weapon_skill_options(e):
        skill_weapon.options = [
            ft.dropdown.Option(key=str(slot), text=f"Weapon {slot + 1}: {weapon}")
            for slot, weapon in enumerate((weapon_one.value, weapon_two.value))
            if weapon
        ]
        skill_weapon.value = None
        skill_weapon.update()

    def update_advancement(e):
        is_health = advancement.value == "health"
        is_detrap = advancement.value == "detrap"
        starting_health.value = f"Starting Health: {7 if is_health else 6}"
        starting_detrap.value = f"Starting Detrap: {2 if is_detrap else 1}"
        skill_weapon.disabled = advancement.value != "weapon_skill"
        if skill_weapon.disabled:
            skill_weapon.value = None
        else:
            update_weapon_skill_options(e)
        starting_health.update()
        starting_detrap.update()
        skill_weapon.update()

    weapon_one.on_select = update_weapon_skill_options
    weapon_two.on_select = update_weapon_skill_options
    advancement.on_select = update_advancement

    def save_thief(e):
        required_fields = (
            (name_field, (name_field.value or "").strip(), "Character name is required."),
            (weapon_one, weapon_one.value, "Choose Weapon 1."),
            (weapon_two, weapon_two.value, "Choose Weapon 2."),
            (advancement, advancement.value, "Choose one advancement."),
        )
        for field, value, message in required_fields:
            if not value:
                field.error_text = message
                field.update()
                return
            field.error_text = None

        if advancement.value == "weapon_skill" and skill_weapon.value not in {"0", "1"}:
            skill_weapon.error_text = "Choose which weapon receives +1 Weapon Skill."
            skill_weapon.update()
            return

        selected_weapons = [weapon_one.value, weapon_two.value]
        skill_slot = int(skill_weapon.value) if advancement.value == "weapon_skill" else None
        weapon_records = [
            {
                "name": weapon,
                "attack_modifier": "+0",
                "damage": "",
                "weapon_skill": 1 if slot == skill_slot else 0,
                "combat_bonus": 0,
                "equipped": slot == 0,
            }
            for slot, weapon in enumerate(selected_weapons)
        ]
        on_save(
            {
                "name": (name_field.value or "").strip(),
                "class_name": "Thief",
                "level": 1,
                "hp_current": 7 if advancement.value == "health" else 6,
                "hp_max": 7 if advancement.value == "health" else 6,
                "magic_current": 0,
                "magic_max": 0,
                "magic_resistance": 1,
                "detrap": 2 if advancement.value == "detrap" else 1,
                "experience_points": 0,
                "beazants": 0,
                "weapons": weapon_records,
                "inventory": [],
            }
        )

    return ft.View(
        route=route_for_class("Thief"),
        appbar=ft.AppBar(title=ft.Text("Create Thief")),
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Container(
                    width=720,
                    padding=24,
                    bgcolor=ft.Colors.SURFACE,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        blur_radius=18,
                        spread_radius=1,
                        color=ft.Colors.BLACK_26,
                        offset=ft.Offset(0, 6),
                    ),
                    content=ft.Column(
                        [
                            ft.Text("Thief creation", size=20, weight=ft.FontWeight.BOLD),
                            name_field,
                            ft.Text("Level: 1  |  Magic Resistance: 1 / 5"),
                            ft.Text("Choose two weapons (duplicates are allowed)."),
                            ft.Row([weapon_one, weapon_two]),
                            ft.Divider(),
                            ft.Text("Choose exactly one advancement."),
                            advancement,
                            starting_health,
                            starting_detrap,
                            skill_weapon,
                            ft.Row(
                                [
                                    ft.TextButton(
                                        content="Back to Classes",
                                        on_click=lambda e: on_back(),
                                    ),
                                    ft.TextButton(
                                        content="Cancel",
                                        on_click=lambda e: on_cancel(),
                                    ),
                                    ft.Button(
                                        content="Create Character",
                                        on_click=save_thief,
                                    ),
                                ]
                            ),
                        ],
                        spacing=12,
                        scroll=ft.ScrollMode.AUTO,
                        width=672,
                    ),
                ),
            )
        ],
    )


def build_wizard_creation_view(
    on_save: Callable[[dict[str, object]], None],
    on_back: Callable[[], None],
    on_cancel: Callable[[], None],
) -> ft.View:
    name_field = ft.TextField(label="Character Name", autofocus=True)
    weapon_options = [
        ft.dropdown.Option(name)
        for name in game_catalogs.weapons_for_class("Wizard")
    ]
    weapon_one = ft.Dropdown(label="Weapon 1", options=weapon_options)
    weapon_two = ft.Dropdown(label="Weapon 2", options=weapon_options)
    advancement = ft.Dropdown(
        label="Choose one advancement",
        options=[
            ft.dropdown.Option(key="health", text="Increase Health by 1"),
            ft.dropdown.Option(
                key="magic_resistance",
                text="Increase Magic Resistance by 1",
            ),
            ft.dropdown.Option(key="weapon_skill", text="Gain +1 Weapon Skill"),
            ft.dropdown.Option(key="second_spell", text="Choose a second spell"),
        ],
    )
    skill_weapon = ft.Dropdown(
        label="Weapon receiving +1 Weapon Skill",
        options=[],
        disabled=True,
    )
    starting_health = ft.Text("Starting Health: 4")
    starting_magic_resistance = ft.Text("Starting Magic Resistance: 2 / 5")

    def create_spell_fields(index):
        category_field = ft.Dropdown(
            label=f"Spell {index} Type",
            options=[
                ft.dropdown.Option(category)
                for category in game_catalogs.SPELL_CATALOG
            ],
        )
        spell_field = ft.Dropdown(
            label=f"Spell {index}",
            options=[],
            disabled=True,
        )

        def update_spell_options(e):
            spell_entries = game_catalogs.SPELL_CATALOG.get(
                category_field.value,
                (),
            )
            spell_field.options = [
                ft.dropdown.Option(
                    key=name,
                    text=f"{name} (Cost: {cost})",
                )
                for name, cost in spell_entries
            ]
            if spell_field.value not in {
                option.key for option in spell_field.options
            }:
                spell_field.value = None
            spell_field.disabled = not bool(category_field.value)
            spell_field.update()

        category_field.on_select = update_spell_options
        return category_field, spell_field

    first_spell_category, first_spell = create_spell_fields(1)
    second_spell_category, second_spell = create_spell_fields(2)
    second_spell_fields = ft.Column(
        [second_spell_category, second_spell],
        spacing=8,
        visible=False,
    )

    def update_weapon_skill_options(e=None):
        skill_weapon.options = [
            ft.dropdown.Option(
                key=str(slot),
                text=f"Weapon {slot + 1}: {weapon}",
            )
            for slot, weapon in enumerate((weapon_one.value, weapon_two.value))
            if weapon
        ]
        if skill_weapon.value not in {
            option.key for option in skill_weapon.options
        }:
            skill_weapon.value = None
        skill_weapon.update()

    def update_weapon_options(e):
        for dropdown, other in (
            (weapon_one, weapon_two),
            (weapon_two, weapon_one),
        ):
            dropdown.options = [
                ft.dropdown.Option(name)
                for name in game_catalogs.weapons_for_class("Wizard")
            ]
            dropdown.update()
        update_weapon_skill_options()

    def update_advancement(e):
        health = 5 if advancement.value == "health" else 4
        resistance = 3 if advancement.value == "magic_resistance" else 2
        second_spell_fields.visible = advancement.value == "second_spell"
        starting_health.value = f"Starting Health: {health}"
        starting_magic_resistance.value = (
            f"Starting Magic Resistance: {resistance} / 5"
        )
        skill_weapon.disabled = advancement.value != "weapon_skill"
        if skill_weapon.disabled:
            skill_weapon.value = None
        else:
            update_weapon_skill_options()
        starting_health.update()
        starting_magic_resistance.update()
        second_spell_fields.update()
        skill_weapon.update()

    weapon_one.on_select = update_weapon_options
    weapon_two.on_select = update_weapon_options
    advancement.on_select = update_advancement

    def save_wizard(e):
        required_fields = (
            (name_field, (name_field.value or "").strip(), "Character name is required."),
            (weapon_one, weapon_one.value, "Choose Weapon 1."),
            (weapon_two, weapon_two.value, "Choose Weapon 2."),
            (advancement, advancement.value, "Choose one advancement."),
            (first_spell_category, first_spell_category.value, "Choose a spell type."),
            (first_spell, first_spell.value, "Choose a starting spell."),
        )
        for field, value, message in required_fields:
            if not value:
                field.error_text = message
                field.update()
                return
            field.error_text = None

        if advancement.value == "second_spell":
            for field, message in (
                (second_spell_category, "Choose a type for the second spell."),
                (second_spell, "Choose a second spell."),
            ):
                if not field.value:
                    field.error_text = message
                    field.update()
                    return
                field.error_text = None

        if advancement.value == "weapon_skill" and skill_weapon.value not in {
            "0",
            "1",
        }:
            skill_weapon.error_text = "Choose which weapon receives +1 Weapon Skill."
            skill_weapon.update()
            return

        selected_weapons = [weapon_one.value, weapon_two.value]
        skill_slot = (
            int(skill_weapon.value)
            if advancement.value == "weapon_skill"
            else None
        )
        weapon_records = [
            {
                "name": weapon,
                "attack_modifier": "+0",
                "damage": "",
                "weapon_skill": 1 if slot == skill_slot else 0,
                "combat_bonus": 0,
                "equipped": slot == 0,
            }
            for slot, weapon in enumerate(selected_weapons)
        ]
        def spell_record(category_field, spell_field):
            spell_costs = dict(
                game_catalogs.SPELL_CATALOG[category_field.value]
            )
            return {
                "name": spell_field.value,
                "category": category_field.value,
                "cost": spell_costs[spell_field.value],
                "uses_remaining": 1,
            }

        selected_spells = [
            spell_record(first_spell_category, first_spell)
        ]
        if advancement.value == "second_spell":
            selected_spells.append(
                spell_record(second_spell_category, second_spell)
            )
        health = 5 if advancement.value == "health" else 4
        magic_resistance = (
            3 if advancement.value == "magic_resistance" else 2
        )
        on_save(
            {
                "name": (name_field.value or "").strip(),
                "class_name": "Wizard",
                "strength": 10,
                "level": 1,
                "hp_current": health,
                "hp_max": health,
                "magic_current": 0,
                "magic_max": 0,
                "magic_resistance": magic_resistance,
                "experience_points": 0,
                "beazants": 0,
                "weapons": weapon_records,
                "inventory": [],
                "spells": selected_spells,
                "magic_damage": 0,
            }
        )

    return ft.View(
        route=route_for_class("Wizard"),
        appbar=ft.AppBar(title=ft.Text("Create Wizard")),
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Container(
                    width=720,
                    padding=24,
                    bgcolor=ft.Colors.SURFACE,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        blur_radius=18,
                        spread_radius=1,
                        color=ft.Colors.BLACK_26,
                        offset=ft.Offset(0, 6),
                    ),
                    content=ft.Column(
                        [
                            ft.Text(
                                "Wizard creation",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                            name_field,
                            ft.Text("Level: 1"),
                            starting_health,
                            starting_magic_resistance,
                            ft.Text(
                                "Choose two weapons (duplicates are allowed)."
                            ),
                            ft.Row([weapon_one, weapon_two]),
                            ft.Text(
                                "Choose one starting spell. Spell costs are "
                                "paid with health and can be used once per "
                                "dungeon."
                            ),
                            first_spell_category,
                            first_spell,
                            ft.Divider(),
                            ft.Text("Choose exactly one advancement."),
                            advancement,
                            skill_weapon,
                            second_spell_fields,
                            ft.Row(
                                [
                                    ft.TextButton(
                                        content="Back to Classes",
                                        on_click=lambda e: on_back(),
                                    ),
                                    ft.TextButton(
                                        content="Cancel",
                                        on_click=lambda e: on_cancel(),
                                    ),
                                    ft.Button(
                                        content="Create Character",
                                        on_click=save_wizard,
                                    ),
                                ]
                            ),
                        ],
                        spacing=12,
                        scroll=ft.ScrollMode.AUTO,
                        width=672,
                    ),
                ),
            )
        ],
    )


def build_class_selection_view(
    on_select: Callable[[str], None],
    on_cancel: Callable[[], None],
) -> ft.View:
    divider_color = ft.Colors.GREY_500

    def class_button(class_name: str) -> ft.Button:
        def select_class(e):
            on_select(class_name)

        return ft.Button(
            content=class_name,
            width=260,
            height=48,
            style=ft.ButtonStyle(
                shape=ft.BeveledRectangleBorder(
                    radius=12,
                    side=ft.BorderSide(width=1, color=ft.Colors.GREY_700),
                )
            ),
            on_click=select_class,
        )

    left_column = ft.Container(
        width=280,
        height=220,
        alignment=ft.Alignment.TOP_CENTER,
        content=ft.Column(
            controls=[class_button(name) for name in CHARACTER_CLASSES[:3]],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )
    right_column = ft.Container(
        width=280,
        height=220,
        alignment=ft.Alignment.TOP_CENTER,
        content=ft.Column(
            controls=[class_button(name) for name in CHARACTER_CLASSES[3:6]],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    def cancel_creation(e):
        on_cancel()

    return ft.View(
        route="/character/create",
        appbar=ft.AppBar(title=ft.Text("Choose a Character Class")),
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Container(
                    width=680,
                    padding=24,
                    bgcolor=ft.Colors.SURFACE,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        blur_radius=18,
                        spread_radius=1,
                        color=ft.Colors.BLACK_26,
                        offset=ft.Offset(0, 6),
                    ),
                    content=ft.Column(
                        [
                            ft.Text(
                                "Select a class to begin character creation.",
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Row(
                                controls=[
                                    left_column,
                                    ft.VerticalDivider(
                                        width=1,
                                        color=divider_color,
                                        thickness=1,
                                    ),
                                    right_column,
                                ],
                                width=600,
                                height=220,
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                                spacing=8,
                            ),
                            ft.Divider(color=divider_color, thickness=1),
                            ft.Row(
                                controls=[class_button("Charmed Monster")],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Button(
                                content="Cancel",
                                on_click=cancel_creation,
                            ),
                        ],
                        spacing=16,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ),
            )
        ],
    )


def build_character_form_view(
    class_name: str,
    on_save: Callable[[dict[str, object]], None],
    on_back: Callable[[], None],
    on_cancel: Callable[[], None],
) -> ft.View:
    if class_name == "Hero":
        return build_hero_creation_view(on_save, on_back, on_cancel)
    if class_name == "Thief":
        return build_thief_creation_view(on_save, on_back, on_cancel)
    if class_name == "Wizard":
        return build_wizard_creation_view(on_save, on_back, on_cancel)

    name_field = ft.TextField(label="Character Name", autofocus=True)

    def save_character(e):
        name = (name_field.value or "").strip()
        if not name:
            name_field.error_text = "Character name cannot be blank."
            name_field.update()
            return

        character = {
            "name": name,
            "class_name": class_name,
            "strength": 10,
            "hp_current": 8,
            "hp_max": 8,
            "magic_current": 0,
            "magic_max": 0,
            "experience_points": 0,
            "beazants": 0,
            "inventory": [],
            "weapons": [],
        }
        if class_name in game_catalogs.STARTING_MAGIC_RESISTANCE:
            character["magic_resistance"] = (
                game_catalogs.STARTING_MAGIC_RESISTANCE[class_name]
            )
        if class_name in game_catalogs.SPELLCASTING_CLASSES:
            character["spells"] = []
        on_save(character)

    character_details = [
        ft.Text("Character details", size=18, weight=ft.FontWeight.BOLD),
        ft.Text(f"Class: {class_name}"),
    ]
    if class_name in game_catalogs.STARTING_MAGIC_RESISTANCE:
        character_details.append(
            ft.Text(
                "Starting Magic Resistance: "
                f"{game_catalogs.STARTING_MAGIC_RESISTANCE[class_name]} / 5"
            )
        )
    character_details.extend(
        [
            ft.Text(
                "Class-specific stats, weapons, and abilities will be added "
                "as each class is implemented."
            ),
            name_field,
            ft.Row(
                [
                    ft.TextButton(
                        content="Back to Classes",
                        on_click=lambda e: on_back(),
                    ),
                    ft.TextButton(
                        content="Cancel",
                        on_click=lambda e: on_cancel(),
                    ),
                    ft.Button(
                        content="Create Character",
                        on_click=save_character,
                    ),
                ]
            ),
        ]
    )

    return ft.View(
        route=route_for_class(class_name),
        appbar=ft.AppBar(title=ft.Text(f"Create {class_name}")),
        controls=[
            ft.Column(
                character_details,
                spacing=16,
                width=600,
            )
        ],
    )
