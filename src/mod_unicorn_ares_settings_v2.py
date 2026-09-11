# -*- coding: utf-8 -*-
from gui.modsSettingsApi import g_modsSettingsApi, templates  # type: ignore

try:
    from helpers import getClientLanguage  # type: ignore
except ImportError:
    getClientLanguage = None

from unicorn_ares_constants import ArmorLabelSettings, PenLabelSettings, AngleLabelSettings, EffPenLabelSettings, KillLabelSettings, GunLabelSettings
from unicorn_ares_config import save_flat_config, get_config
from unicorn_ares_gui import gui_state

MOD_VERSION = "1.8.5"
mod_linkage = "unicorn_ares_armor_calculator"
modDataVersion = 6

TRANSLATIONS = {
    "en": ["unicorn.ares Armor Calculator", "Display", "Penetration / armor", "Penetration chance", "Impact angle", "Separate penetration", "Kill chance", "Gun blocking", "Position and size", "Text size", "Horizontal position", "Vertical position", "Show impact angle from", "Colorblind mode"],
    "uk": ["unicorn.ares Armor Calculator", "Що показувати", "Пробиття / броня", "Шанс пробиття", "Кут влучання", "Пробиття окремим рядком", "Шанс знищення", "Влучання в гармату", "Позиція та розмір", "Розмір тексту", "Положення по горизонталі", "Положення по вертикалі", "Показувати кут від", "Режим дальтонізму"],
    "ru": ["unicorn.ares Armor Calculator", "Что показывать", "Пробитие / броня", "Шанс пробития", "Угол попадания", "Пробитие отдельной строкой", "Шанс уничтожения", "Попадание в орудие", "Позиция и размер", "Размер текста", "Положение по горизонтали", "Положение по вертикали", "Показывать угол от", "Режим дальтонизма"],
}


def _lang():
    if getClientLanguage is not None:
        try:
            value = getClientLanguage()
            if value in TRANSLATIONS:
                return value
        except Exception:
            pass
    return "en"


def _texts():
    return TRANSLATIONS[_lang()]


def _template():
    t = _texts()
    cfg = get_config()
    return {
        "modDisplayName": t[0],
        "settingsVersion": modDataVersion,
        "enabled": True,
        "column1": [
            templates.createLabel(t[1]),
            templates.createCheckbox("armor_label_enabled", t[2], "Основний рядок: пробиття снаряда / приведена броня.", ArmorLabelSettings.ENABLED),
            templates.createCheckbox("pen_label_enabled", t[3], "Показувати розрахований шанс пробиття у відсотках.", PenLabelSettings.ENABLED),
            templates.createCheckbox("angle_label_enabled", t[4], "Показувати кут, під яким снаряд влучає в броню.", AngleLabelSettings.ENABLED),
            templates.createCheckbox("eff_pen_label_enabled", t[5], "Показувати пробиття снаряда окремим рядком.", EffPenLabelSettings.ENABLED),
            templates.createCheckbox("kill_label_enabled", t[6], "Показувати шанс знищення цілі, якщо він доступний.", KillLabelSettings.ENABLED),
            templates.createCheckbox("gun_label_enabled", t[7], "Позначати випадки, коли траєкторія проходить через гармату.", GunLabelSettings.ENABLED),
            templates.createCheckbox("colorblind", t[13], "Замінює червоний колір на фіолетовий.", bool(cfg.get("colorblind", False))),
        ],
        "column2": [
            templates.createLabel(t[8]),
            templates.createSlider("armor_label_font_size", t[9], "Розмір основного тексту.", 10, 30, 1, ArmorLabelSettings.FONT_SIZE),
            templates.createSlider("armor_label_x_offset", t[10], "Зміщення індикатора ліворуч або праворуч від центру екрана.", -300, 300, 1, ArmorLabelSettings.X_OFFSET),
            templates.createSlider("armor_label_y_offset", t[11], "Зміщення індикатора вгору або вниз від центру екрана.", -300, 300, 1, ArmorLabelSettings.Y_OFFSET),
            templates.createSlider("angle_label_display_threshold", t[12], "Кут буде показаний лише починаючи з цього значення, у градусах.", 0, 90, 1, AngleLabelSettings.DISPLAY_THRESHOLD),
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


def _on_settings_save(linkage, settings):
    if linkage != mod_linkage:
        return
    _apply(settings)


try:
    g_modsSettingsApi.setModTemplate(mod_linkage, _template(), _on_settings_save, None)
    print("unicorn.ares settings v%s registered via setModTemplate" % MOD_VERSION)
except Exception as error:
    print("unicorn.ares settings v%s registration failed: %s" % (MOD_VERSION, error))
