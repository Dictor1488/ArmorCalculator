# -*- coding: utf-8 -*-
import json
import os


DEFAULT_CONFIG = {
    "armor_label": {"enabled": True, "x_offset": 0, "y_offset": 30, "font_size": 16, "label_format": "{penetration}/{value}"},
    "pen_label": {"enabled": False, "x_offset": 0, "y_offset": 50, "font_size": 16, "label_format": "{value}%"},
    "angle_label": {"enabled": False, "x_offset": 30, "y_offset": 35, "font_size": 16, "label_format": "{value}°", "display_threshold": 65},
    "eff_pen_label": {"enabled": False, "x_offset": -30, "y_offset": 35, "font_size": 16, "label_format": "{value}"},
    "kill_label": {"enabled": False, "x_offset": 0, "y_offset": 66, "font_size": 14, "label_format": "† {value}%"},
    "gun_label": {"enabled": False, "x_offset": 0, "y_offset": -36, "font_size": 16, "label_format": "GUN"},
    "colors": {"green_chance": "6BF40D", "orange_chance": "FFAD00", "red_chance": "E90000", "ricochet": "800080"},
    "shadow": {"shadow_color": "000000", "shadow_alpha": 8, "shadow_length": 3, "shadow_strength": 7},
}

CONFIG_FOLDER = os.path.join("mods", "configs", "pademinune")
CONFIG_PATH = os.path.join(CONFIG_FOLDER, "armor-calculator.json")


def create_config():
    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)
    with open(CONFIG_PATH, "w") as file:
        json.dump(DEFAULT_CONFIG, file, indent=4)


def read_config():
    with open(CONFIG_PATH) as file:
        return json.load(file)


LEGACY_LABEL_FORMAT_FIELDS = {
    "armor_label": "armor",
    "pen_label": "prob",
    "angle_label": "angle",
    "eff_pen_label": "eff_pen",
    "kill_label": "kill_prob",
}


def migrate_label_format_placeholders(user_config):
    changed = False
    for section, old_field in LEGACY_LABEL_FORMAT_FIELDS.items():
        label_format = user_config.get(section, {}).get("label_format")
        if not label_format:
            continue
        old_placeholder = "{" + old_field + "}"
        if old_placeholder in label_format:
            user_config[section]["label_format"] = label_format.replace(old_placeholder, "{value}")
            changed = True
    return changed


def migrate_armor_label_format(user_config):
    armor_settings = user_config.get("armor_label", {})
    if armor_settings.get("label_format") == "{value}":
        armor_settings["label_format"] = "{penetration}/{value}"
        return True
    return False


def migrate_new_display_defaults(user_config):
    changed = False
    armor_settings = user_config.get("armor_label", {})
    if armor_settings.get("enabled") is True and armor_settings.get("x_offset") == 0 and armor_settings.get("y_offset") == 30 and armor_settings.get("font_size") == 20 and armor_settings.get("label_format") in ("{penetration}/{armor}", "{penetration}/{value}"):
        armor_settings["font_size"] = 16
        armor_settings["label_format"] = "{penetration}/{value}"
        changed = True
    pen_settings = user_config.get("pen_label", {})
    if pen_settings.get("enabled") is True and pen_settings.get("x_offset") == 0 and pen_settings.get("y_offset") == 50 and pen_settings.get("font_size") == 16 and pen_settings.get("label_format") == "{value}%":
        pen_settings["enabled"] = False
        changed = True
    angle_settings = user_config.get("angle_label", {})
    if angle_settings.get("enabled") is True and angle_settings.get("x_offset") == 30 and angle_settings.get("y_offset") == 35 and angle_settings.get("font_size") == 16 and angle_settings.get("label_format") == "{value}°" and angle_settings.get("display_threshold") == 65:
        angle_settings["enabled"] = False
        changed = True
    return changed


def migrate_config(user_config):
    changed = False
    for section, defaults in DEFAULT_CONFIG.items():
        if section not in user_config:
            user_config[section] = defaults.copy()
            changed = True
        else:
            for key, value in defaults.items():
                if key not in user_config[section]:
                    user_config[section][key] = value
                    changed = True
    changed = migrate_label_format_placeholders(user_config) or changed
    changed = migrate_armor_label_format(user_config) or changed
    changed = migrate_new_display_defaults(user_config) or changed
    if changed:
        with open(CONFIG_PATH, "w") as f:
            json.dump(user_config, f, indent=4)
    return user_config


def _flat_section(settings, prefix, fallback_section, include_threshold=False):
    old = user_settings.get(fallback_section, DEFAULT_CONFIG[fallback_section])
    data = {
        "enabled": settings.get(prefix + "_enabled", old["enabled"]),
        "x_offset": settings.get(prefix + "_x_offset", old["x_offset"]),
        "y_offset": settings.get(prefix + "_y_offset", old["y_offset"]),
        "font_size": settings.get(prefix + "_font_size", old["font_size"]),
        "label_format": settings.get(prefix + "_format", old["label_format"]),
    }
    if include_threshold:
        data["display_threshold"] = settings.get(prefix + "_display_threshold", old["display_threshold"])
    return data


def save_flat_config(settings):
    config = {
        "armor_label": _flat_section(settings, "armor_label", "armor_label"),
        "pen_label": _flat_section(settings, "pen_label", "pen_label"),
        "angle_label": _flat_section(settings, "angle_label", "angle_label", True),
        "eff_pen_label": _flat_section(settings, "eff_pen_label", "eff_pen_label"),
        "kill_label": _flat_section(settings, "kill_label", "kill_label"),
        "gun_label": _flat_section(settings, "gun_label", "gun_label"),
        "colors": {
            "green_chance": settings.get("color_green", user_settings["colors"]["green_chance"]),
            "orange_chance": settings.get("color_orange", user_settings["colors"]["orange_chance"]),
            "red_chance": settings.get("color_red", user_settings["colors"]["red_chance"]),
            "ricochet": settings.get("color_ricochet", user_settings["colors"]["ricochet"]),
        },
        "shadow": {
            "shadow_color": settings.get("shadow_color", user_settings["shadow"]["shadow_color"]),
            "shadow_alpha": settings.get("shadow_alpha", user_settings["shadow"]["shadow_alpha"]),
            "shadow_length": settings.get("shadow_length", user_settings["shadow"]["shadow_length"]),
            "shadow_strength": settings.get("shadow_strength", user_settings["shadow"]["shadow_strength"]),
        },
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)


if not os.path.isfile(CONFIG_PATH):
    create_config()
try:
    user_settings = migrate_config(read_config())
except Exception:
    create_config()
    user_settings = read_config()
