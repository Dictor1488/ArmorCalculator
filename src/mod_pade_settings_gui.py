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
        "position_section": "Main label",
        "armor_size": "Font size",
        "armor_x": "Horizontal offset",
        "armor_y": "Vertical offset",
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
        "position_section": "Головний напис",
        "armor_size": "Розмір шрифту",
        "armor_x": "Горизонтальне зміщення",
        "armor_y": "Вертикальне зміщення",
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
        "position_section": "Основная надпись",
        "armor_size": "Размер шрифта",
        "armor_x": "Горизонтальное смещение",
        "armor_y": "Вертикальное смещение",
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
    return language if language in TRANSLATIONS else "en"


def _t(key):
    return TRANSLATIONS[_get_language()].get(key, key)


def _settings_data():
    return {
        "armor_label_enabled": ArmorLabelSettings.ENABLED,
        "pen_label_enabled": PenLabelSettings.ENABLED,
        "angle_label_enabled": AngleLabelSettings.ENABLED,
        "eff_pen_label_enabled": EffPenLabelSettings.ENABLED,
        "kill_label_enabled": KillLabelSettings.ENABLED,
        "gun_label_enabled": GunLabelSettings.ENABLED,
        "armor_label_font_size": ArmorLabelSettings.FONT_SIZE,
        "armor_label_x_offset": ArmorLabelSettings.X_OFFSET,
        "armor_label_y_offset": ArmorLabelSettings.Y_OFFSET,
        "angle_label_display_threshold": AngleLabelSettings.DISPLAY_THRESHOLD,
    }


def _template():
    return {
        "modDisplayName": _t("mod_name"),
        "settingsVersion": modDataVersion,
        "enabled": True,
        "column1": [
            templates.createLabel(_t("main_section")),
            templates.createCheckbox("armor_label_enabled", _t("armor_enable"), "", ArmorLabelSettings.ENABLED),
            templates.createCheckbox("pen_label_enabled", _t("prob_enable"), "", PenLabelSettings.ENABLED),
            templates.createCheckbox("angle_label_enabled", _t("angle_enable"), "", AngleLabelSettings.ENABLED),
            templates.createCheckbox("eff_pen_label_enabled", _t("eff_enable"), "", EffPenLabelSettings.ENABLED),
            templates.createCheckbox("kill_label_enabled", _t("kill_enable"), "", KillLabelSettings.ENABLED),
            templates.createCheckbox("gun_label_enabled", _t("gun_enable"), "", GunLabelSettings.ENABLED),
        ],
        "column2": [
            templates.createLabel(_t("position_section")),
            templates.createSlider("armor_label_font_size", _t("armor_size"), "", 10, 30, 1, ArmorLabelSettings.FONT_SIZE),
            templates.createSlider("armor_label_x_offset", _t("armor_x"), "", -300, 300, 1, ArmorLabelSettings.X_OFFSET),
            templates.createSlider("armor_label_y_offset", _t("armor_y"), "", -300, 300, 1, ArmorLabelSettings.Y_OFFSET),
            templates.createSlider("angle_label_display_threshold", _t("angle_threshold"), "", 0, 90, 1, AngleLabelSettings.DISPLAY_THRESHOLD),
        ],
    }


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


try:
    g_modsSettingsApi.registerMod(mod_linkage, _template(), _settings_data(), _apply)
except Exception:
    pass
