# -*- coding: utf-8 -*-
from gui.modsSettingsApi import g_modsSettingsApi, templates  # type: ignore

try:
    from helpers import getClientLanguage  # type: ignore
except ImportError:
    getClientLanguage = None

from unicorn_ares_constants import ArmorLabelSettings, PenLabelSettings, AngleLabelSettings, EffPenLabelSettings, KillLabelSettings, GunLabelSettings
from unicorn_ares_config import save_flat_config, get_config
from unicorn_ares_gui import gui_state

MOD_VERSION = "1.9.6"
mod_linkage = "unicorn_ares_armor_calculator"
modDataVersion = 7

TRANSLATIONS = {
    "en": {
        "title": "unicorn.ares Armor Calculator",
        "display": "Display",
        "armor": "Penetration / armor",
        "armor_tip": "Main line: shell penetration / effective armor.",
        "chance": "Penetration chance",
        "chance_tip": "Show calculated penetration chance as a percentage.",
        "angle": "Impact angle",
        "angle_tip": "Show the angle at which the shell hits the armor.",
        "separate_pen": "Penetration on separate line",
        "separate_pen_tip": "Show shell penetration on a separate line.",
        "kill": "Kill chance",
        "kill_tip": "Show kill chance when it is available.",
        "gun": "Gun hit",
        "gun_tip": "Mark cases where the trajectory goes through the gun.",
        "colorblind": "Colorblind mode",
        "colorblind_tip": "Replaces red with purple.",
        "position": "Position and size",
        "size": "Text size",
        "size_tip": "Size of the main text.",
        "x": "Horizontal position",
        "x_tip": "Move the indicator left or right from screen center.",
        "y": "Vertical position",
        "y_tip": "Move the indicator up or down from screen center.",
        "angle_from": "Show impact angle from",
        "angle_from_tip": "The angle is shown only from this value, in degrees."
    },
    "uk": {
        "title": "unicorn.ares Armor Calculator",
        "display": "Що показувати",
        "armor": "Пробиття / броня",
        "armor_tip": "Основний рядок: пробиття снаряда / приведена броня.",
        "chance": "Шанс пробиття",
        "chance_tip": "Показувати розрахований шанс пробиття у відсотках.",
        "angle": "Кут влучання",
        "angle_tip": "Показувати кут, під яким снаряд влучає в броню.",
        "separate_pen": "Пробиття окремим рядком",
        "separate_pen_tip": "Показувати пробиття снаряда окремим рядком.",
        "kill": "Шанс знищення",
        "kill_tip": "Показувати шанс знищення цілі, якщо він доступний.",
        "gun": "Влучання в гармату",
        "gun_tip": "Позначати випадки, коли траєкторія проходить через гармату.",
        "colorblind": "Режим дальтонізму",
        "colorblind_tip": "Замінює червоний колір на фіолетовий.",
        "position": "Позиція та розмір",
        "size": "Розмір тексту",
        "size_tip": "Розмір основного тексту.",
        "x": "Положення по горизонталі",
        "x_tip": "Зміщення індикатора ліворуч або праворуч від центру екрана.",
        "y": "Положення по вертикалі",
        "y_tip": "Зміщення індикатора вгору або вниз від центру екрана.",
        "angle_from": "Показувати кут від",
        "angle_from_tip": "Кут буде показаний лише починаючи з цього значення, у градусах."
    },
    "ru": {
        "title": "unicorn.ares Armor Calculator",
        "display": "Что показывать",
        "armor": "Пробитие / броня",
        "armor_tip": "Основная строка: пробитие снаряда / приведённая броня.",
        "chance": "Шанс пробития",
        "chance_tip": "Показывать рассчитанный шанс пробития в процентах.",
        "angle": "Угол попадания",
        "angle_tip": "Показывать угол, под которым снаряд попадает в броню.",
        "separate_pen": "Пробитие отдельной строкой",
        "separate_pen_tip": "Показывать пробитие снаряда отдельной строкой.",
        "kill": "Шанс уничтожения",
        "kill_tip": "Показывать шанс уничтожения цели, если он доступен.",
        "gun": "Попадание в орудие",
        "gun_tip": "Отмечать случаи, когда траектория проходит через орудие.",
        "colorblind": "Режим дальтонизма",
        "colorblind_tip": "Заменяет красный цвет на фиолетовый.",
        "position": "Позиция и размер",
        "size": "Размер текста",
        "size_tip": "Размер основного текста.",
        "x": "Положение по горизонтали",
        "x_tip": "Смещение индикатора влево или вправо от центра экрана.",
        "y": "Положение по вертикали",
        "y_tip": "Смещение индикатора вверх или вниз от центра экрана.",
        "angle_from": "Показывать угол от",
        "angle_from_tip": "Угол будет показан только начиная с этого значения, в градусах."
    }
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
        "modDisplayName": t["title"],
        "settingsVersion": modDataVersion,
        "enabled": True,
        "column1": [
            templates.createLabel(t["display"]),
            templates.createCheckbox(t["armor"], "armor_label_enabled", ArmorLabelSettings.ENABLED, tooltip=t["armor_tip"]),
            templates.createCheckbox(t["chance"], "pen_label_enabled", PenLabelSettings.ENABLED, tooltip=t["chance_tip"]),
            templates.createCheckbox(t["angle"], "angle_label_enabled", AngleLabelSettings.ENABLED, tooltip=t["angle_tip"]),
            templates.createCheckbox(t["separate_pen"], "eff_pen_label_enabled", EffPenLabelSettings.ENABLED, tooltip=t["separate_pen_tip"]),
            templates.createCheckbox(t["kill"], "kill_label_enabled", KillLabelSettings.ENABLED, tooltip=t["kill_tip"]),
            templates.createCheckbox(t["gun"], "gun_label_enabled", GunLabelSettings.ENABLED, tooltip=t["gun_tip"]),
            templates.createCheckbox(t["colorblind"], "colorblind", bool(cfg.get("colorblind", False)), tooltip=t["colorblind_tip"]),
        ],
        "column2": [
            templates.createLabel(t["position"]),
            templates.createSlider(t["size"], "armor_label_font_size", ArmorLabelSettings.FONT_SIZE, 10, 30, 1, tooltip=t["size_tip"]),
            templates.createSlider(t["x"], "armor_label_x_offset", ArmorLabelSettings.X_OFFSET, -300, 300, 1, tooltip=t["x_tip"]),
            templates.createSlider(t["y"], "armor_label_y_offset", ArmorLabelSettings.Y_OFFSET, -300, 300, 1, tooltip=t["y_tip"]),
            templates.createSlider(t["angle_from"], "angle_label_display_threshold", AngleLabelSettings.DISPLAY_THRESHOLD, 0, 90, 1, tooltip=t["angle_from_tip"]),
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
except Exception as error:
    print("unicorn.ares settings registration failed: %s" % error)
