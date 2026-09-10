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
    "colors": {"green_chance": "6BF40D", "orange_chance": "FFFF00", "red_chance": "E90000", "ricochet": "E90000"},
    "shadow": {"shadow_color": "000000", "shadow_alpha": 8, "shadow_length": 3, "shadow_strength": 7},
}

CONFIG_FOLDER = os.path.join("mods", "configs", "unicorn.ares")
CONFIG_PATH = os.path.join(CONFIG_FOLDER, "armor-calculator.json")
LEGACY_CONFIG_PATH = os.path.join("mods", "configs", "pademinune", "armor-calculator.json")


def create_config():
    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)
    with open(CONFIG_PATH, "w") as file:
        json.dump(DEFAULT_CONFIG, file, indent=4)


def read_config():
    with open(CONFIG_PATH) as file:
        return json.load(file)


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

    # Formats, colors and shadow are intentionally hardcoded now.
    for section in ("armor_label", "pen_label", "angle_label", "eff_pen_label", "kill_label", "gun_label"):
        user_config[section]["label_format"] = DEFAULT_CONFIG[section]["label_format"]
    user_config["colors"] = DEFAULT_CONFIG["colors"].copy()
    user_config["shadow"] = DEFAULT_CONFIG["shadow"].copy()

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
        "label_format": DEFAULT_CONFIG[fallback_section]["label_format"],
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
        "colors": DEFAULT_CONFIG["colors"].copy(),
        "shadow": DEFAULT_CONFIG["shadow"].copy(),
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)


if not os.path.isfile(CONFIG_PATH):
    # Keep old user toggles/positions when upgrading, but move them under unicorn.ares.
    if os.path.isfile(LEGACY_CONFIG_PATH):
        if not os.path.exists(CONFIG_FOLDER):
            os.makedirs(CONFIG_FOLDER)
        try:
            with open(LEGACY_CONFIG_PATH) as src:
                legacy = json.load(src)
            with open(CONFIG_PATH, "w") as dst:
                json.dump(legacy, dst, indent=4)
        except Exception:
            create_config()
    else:
        create_config()

try:
    user_settings = migrate_config(read_config())
except Exception:
    create_config()
    user_settings = read_config()
