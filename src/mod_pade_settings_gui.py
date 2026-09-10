# -*- coding: utf-8 -*-
from gui.modsSettingsApi import g_modsSettingsApi, templates  # type: ignore

try:
    from helpers import getClientLanguage  # type: ignore
except ImportError:
    getClientLanguage = None

from pade_constants import (
    ArmorLabelSettings,
    PenLabelSettings,
    AngleLabelSettings,
    EffPenLabelSettings,
    KillLabelSettings,
    GunLabelSettings,
)
from pade_config import save_flat_config
from pade_gui import gui_state


mod_linkage = "unicorn_ares_armor_calculator"
modDataVersion = 4


TRANSLATIONS = {
    "en": {
        "mod_name": "unicorn.ares Armor Calculator",
        "main_section": "Display",
        "armor_enable": "Penetration / armor",
        "prob_enable": "Penetration chance",
        "angle_enable": "Impact angle",
        "eff_enable": "Separate penetration",
        "kill_enable": "Kill chance",
        "gun_enable": "Gun blocking",
        "position_section": "Position & size",
        "armor_size": "Main label size",
        "armor_x": "Main label X",
        "armor_y": "Main label Y",
        "angle_threshold": "Angle threshold",
    },
    "uk": {
        "mod_name": "unicorn.ares Armor Calculator",
        "main_section": "Відображення",
        "armor_enable": "Пробиття / броня",
        "prob_enable": "Шанс пробиття",
        "angle_enable": "Кут влучання",
        "eff_enable": "Окреме пробиття",
        "kill_enable": "Шанс добивання",
        "gun_enable": "Перекриття гарматою",
        "position_section": "Позиція та розмір",
        "armor_size": "Розмір головного напису",
        "armor_x": "Головний напис X",
        "armor_y": "Головний напис Y",
        "angle_threshold": "Поріг кута",
    },
    "ru": {
        "mod_name": "unicorn.ares Armor Calculator",
        "main_section": "Отображение",
        "armor_enable": "Пробитие / броня",
        "prob_enable": "Шанс пробития",
        "angle_enable": "Угол попадания",
        "eff_enable": "Отдельное пробитие",
        "kill_enable": "Шанс добивания",
        "gun_enable": "Перекрытие орудием",
        "position_section": "Позиция и размер",
        "armor_size": "Размер основной надписи",
        "armor_x": "Основная надпись X",
        "armor_y": "Основная надпись Y",
        "angle_threshold": "Порог угла",
    },
}


def _get_language():
    language = "en"
    if getClientLanguage is not None:
        try:
            language = getClientLanguage()
        except Exception:
            pass
    if language not in TRANSLATIONS:
        language = "en"
    return language


def _t(key):
    return TRANSLATIONS[_get_language()].get(key, key)


def _checkbox(var_name, label, value):
    return templates.createCheckbox(var_name, label, "", value)


def _slider(var_name, label, value, minimum, maximum, step=1):
    return templates.createSlider(var_name, label, "", minimum, maximum, step, value)


def _settings_template():
    column = [
        templates.createLabel(_t("main_section")),
        _checkbox("armor_label_enabled", _t("armor_enable"), ArmorLabelSettings.ENABLED),
        _checkbox("pen_label_enabled", _t("prob_enable"), PenLabelSettings.ENABLED),
        _checkbox("angle_label_enabled", _t("angle_enable"), AngleLabelSettings.ENABLED),
        _checkbox("eff_pen_label_enabled", _t("eff_enable"), EffPenLabelSettings.ENABLED),
        _checkbox("kill_label_enabled", _t("kill_enable"), KillLabelSettings.ENABLED),
        _checkbox("gun_label_enabled", _t("gun_enable"), GunLabelSettings.ENABLED),
        templates.createLabel(_t("position_section")),
        _slider("armor_label_font_size", _t("armor_size"), ArmorLabelSettings.FONT_SIZE, 10, 30),
        _slider("armor_label_x_offset", _t("armor_x"), ArmorLabelSettings.X_OFFSET, -300, 300),
        _slider("armor_label_y_offset", _t("armor_y"), ArmorLabelSettings.Y_OFFSET, -300, 300),
        _slider("angle_label_display_threshold", _t("angle_threshold"), AngleLabelSettings.DISPLAY_THRESHOLD, 0, 90),
    ]
    return templates.createModTemplate(mod_linkage, _t("mod_name"), column)


def _apply(settings):
    save_flat_config(settings)

    ArmorLabelSettings.ENABLED = settings.get("armor_label_enabled", ArmorLabelSettings.ENABLED)
    PenLabelSettings.ENABLED = settings.get("pen_label_enabled", PenLabelSettings.ENABLED)
    AngleLabelSettings.ENABLED = settings.get("angle_label_enabled", AngleLabelSettings.ENABLED)
    EffPenLabelSettings.ENABLED = settings.get("eff_pen_label_enabled", EffPenLabelSettings.ENABLED)
    KillLabelSettings.ENABLED = settings.get("kill_label_enabled", KillLabelSettings.ENABLED)
    GunLabelSettings.ENABLED = settings.get("gun_label_enabled", GunLabelSettings.ENABLED)

    ArmorLabelSettings.FONT_SIZE = settings.get("armor_label_font_size", ArmorLabelSettings.FONT_SIZE)
    ArmorLabelSettings.X_OFFSET = settings.get("armor_label_x_offset", ArmorLabelSettings.X_OFFSET)
    ArmorLabelSettings.Y_OFFSET = settings.get("armor_label_y_offset", ArmorLabelSettings.Y_OFFSET)
    AngleLabelSettings.DISPLAY_THRESHOLD = settings.get("angle_label_display_threshold", AngleLabelSettings.DISPLAY_THRESHOLD)

    gui_state.update_properties()


def _register():
    try:
        g_modsSettingsApi.registerMod(mod_linkage, _settings_template, _apply)
    except TypeError:
        try:
            g_modsSettingsApi.registerMod(mod_linkage, _t("mod_name"), _settings_template, _apply)
        except Exception:
            pass
    except Exception:
        pass


_register()
