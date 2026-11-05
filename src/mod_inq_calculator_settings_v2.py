# -*- coding: utf-8 -*-
# Prefer the Gameface Aslain menu, while retaining the legacy settings fallback.
try:
    from gui.aslainMenu import g_modsSettingsApi, templates  # type: ignore
    _ASLAIN_MENU = True
except ImportError:
    from gui.modsSettingsApi import g_modsSettingsApi, templates  # type: ignore
    _ASLAIN_MENU = False


try:
    from helpers import getClientLanguage  # type: ignore
except ImportError:
    getClientLanguage = None

from inq_calculator_constants import ArmorLabelSettings, PenLabelSettings, AngleLabelSettings, EffPenLabelSettings, KillLabelSettings, GunLabelSettings
from inq_calculator_config import save_flat_config, get_config
from inq_calculator_gui import gui_state

MOD_VERSION = "2.0.1"
mod_linkage = "inq_calculator_calculator"
modDataVersion = 14
_PREVIEW_REFRESHING = False

TRANSLATIONS = {
    "en": {
        "title": "Inq Calculator",
        "display": "Main indicators",
        "armor": "Penetration / effective armor",
        "armor_tip": "Shows current shell penetration first, then effective armor at the aiming point. Example: 250 / 230.",
        "chance": "Penetration chance",
        "chance_tip": "Estimated penetration probability. Example: 85%. Shown only for an armor hit.",
        "angle": "Impact angle",
        "angle_tip": "Impact angle in degrees. Example: 65°. Displayed only for armor hits above the configured threshold.",
        "separate_pen": "Shell penetration on a separate line",
        "separate_pen_tip": "Repeats the current shell penetration without armor. Example: 250.",
        "kill": "Kill chance",
        "kill_tip": "Estimated chance to destroy the target, if available and above zero. Example: † 75%.",
        "gun": "Gun hit",
        "gun_tip": "Displays GUN when the trajectory crosses the enemy gun.",
        "colorblind": "Colorblind mode",
        "colorblind_tip": "Replaces red with purple; yellow and green stay unchanged.",
        "position": "Text placement and size",
        "size": "Text size",
        "size_tip": "Changes the font size of all displayed lines (10–30 px).",
        "x": "Horizontal position",
        "x_tip": "Moves the entire indicator horizontally: negative is left, positive is right.",
        "y": "Vertical position",
        "y_tip": "Moves the entire indicator vertically: negative is up, positive is down.",
        "angle_from": "Show impact angle from",
        "angle_from_tip": "Show the impact angle only from the configured angle (0–90°).",
        "extra": "Additional indicators",
        "accessibility": "Accessibility",
        "display_note": "Choose which lines appear near the crosshair.",
        "position_note": "Size and position apply to the entire indicator.",
        "preview_title": "HUD PREVIEW",
        "preview_note": "Sample values only. This shows how enabled lines will look."
    },
    "uk": {
        "title": "Inq Calculator",
        "display": "Основні показники",
        "armor": "Пробиття / приведена броня",
        "armor_tip": "Спочатку пробиття поточного снаряда, потім приведена броня в точці прицілювання. Приклад: 250 / 230.",
        "chance": "Шанс пробиття",
        "chance_tip": "Розрахунковий шанс пробиття. Приклад: 85%. Показується лише за наявності влучання в броню.",
        "angle": "Кут влучання",
        "angle_tip": "Кут влучання у градусах. Приклад: 65°. Показується для влучання в броню, якщо досягнуто заданого порога.",
        "separate_pen": "Пробиття снаряда окремим рядком",
        "separate_pen_tip": "Окремо дублює пробиття поточного снаряда без значення броні. Приклад: 250.",
        "kill": "Шанс знищення",
        "kill_tip": "Розрахунковий шанс знищити ціль, якщо він доступний і більший за нуль. Приклад: † 75%.",
        "gun": "Влучання в гармату",
        "gun_tip": "Показує GUN, якщо траєкторія проходить через гармату противника.",
        "colorblind": "Режим дальтонізму",
        "colorblind_tip": "Замінює червоний на фіолетовий; жовтий та зелений не змінюються.",
        "position": "Розташування та розмір тексту",
        "size": "Розмір тексту",
        "size_tip": "Змінює розмір шрифту всіх рядків (10–30 px).",
        "x": "Положення по горизонталі",
        "x_tip": "Зсуває весь індикатор горизонтально: мінус — ліворуч, плюс — праворуч.",
        "y": "Положення по вертикалі",
        "y_tip": "Зсуває весь індикатор вертикально: мінус — вгору, плюс — вниз.",
        "angle_from": "Показувати кут від",
        "angle_from_tip": "Кут показується лише від установленого значення (0–90°).",
        "extra": "Додаткові показники",
        "accessibility": "Доступність",
        "display_note": "Виберіть, які рядки показувати біля прицілу.",
        "position_note": "Розмір і зміщення застосовуються до всього індикатора.",
        "preview_title": "ПОПЕРЕДНІЙ ПЕРЕГЛЯД HUD",
        "preview_note": "Демонстраційні значення. Тут показано вигляд увімкнених рядків."
    },
    "ru": {
        "title": "Inq Calculator",
        "display": "Основные показатели",
        "armor": "Пробитие / приведённая броня",
        "armor_tip": "Сначала пробитие текущего снаряда, затем приведённая броня в точке прицеливания. Пример: 250 / 230.",
        "chance": "Шанс пробития",
        "chance_tip": "Расчётный шанс пробития. Пример: 85%. Показывается только при попадании в броню.",
        "angle": "Угол попадания",
        "angle_tip": "Угол попадания в градусах. Пример: 65°. Показывается при попадании в броню, если достигнут заданный порог.",
        "separate_pen": "Пробитие снаряда отдельной строкой",
        "separate_pen_tip": "Отдельно повторяет пробитие текущего снаряда без значения брони. Пример: 250.",
        "kill": "Шанс уничтожения",
        "kill_tip": "Расчётный шанс уничтожить цель, если доступен и больше нуля. Пример: † 75%.",
        "gun": "Попадание в орудие",
        "gun_tip": "Показывает GUN, если траектория проходит через орудие противника.",
        "colorblind": "Режим дальтонизма",
        "colorblind_tip": "Заменяет красный на фиолетовый; жёлтый и зелёный не меняются.",
        "position": "Расположение и размер текста",
        "size": "Размер текста",
        "size_tip": "Меняет размер шрифта всех строк (10–30 px).",
        "x": "Положение по горизонтали",
        "x_tip": "Сдвигает весь индикатор по горизонтали: минус — влево, плюс — вправо.",
        "y": "Положение по вертикали",
        "y_tip": "Сдвигает весь индикатор по вертикали: минус — вверх, плюс — вниз.",
        "angle_from": "Показывать угол от",
        "angle_from_tip": "Угол показывается только от установленного значения (0–90°).",
        "extra": "Дополнительные показатели",
        "accessibility": "Доступность",
        "display_note": "Выберите, какие строки показывать возле прицела.",
        "position_note": "Размер и смещение применяются ко всему индикатору.",
        "preview_title": "ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР HUD",
        "preview_note": "Демонстрационные значения. Здесь показан вид включённых строк."
    }
}


def _lang():
    if getClientLanguage is not None:
        try:
            value = str(getClientLanguage() or "").lower().replace("-", "_")
            short = value.split("_", 1)[0]
            if short in TRANSLATIONS:
                return short
        except Exception:
            pass
    return "en"


def _texts():
    return TRANSLATIONS[_lang()]


def _section_divider():
    # Plain label compatible with ModsSettingsAPI 1.7.1.
    return templates.createLabel(u'────────────────────────────')


def _preview_settings():
    cfg = get_config()
    values = {}
    for name in ('armor_label', 'pen_label', 'angle_label', 'eff_pen_label',
                 'kill_label', 'gun_label'):
        values[name + '_enabled'] = bool(cfg.get(name, {}).get('enabled', False))
    values['armor_label_font_size'] = cfg.get('armor_label', {}).get('font_size', 16)
    values['armor_label_x_offset'] = cfg.get('armor_label', {}).get('x_offset', 0)
    values['armor_label_y_offset'] = cfg.get('armor_label', {}).get('y_offset', 35)
    values['angle_label_display_threshold'] = cfg.get('angle_label', {}).get('display_threshold', 65)
    values['colorblind'] = bool(cfg.get('colorblind', False))
    return values


def _preview_label(settings):
    # HTML preview is enabled only for the Gameface Aslain menu.
    rows = []
    if settings.get('armor_label_enabled', True):
        rows.append('250 / 230')
    if settings.get('pen_label_enabled', False):
        rows.append('85%')
    if settings.get('angle_label_enabled', False):
        try:
            threshold = int(settings.get('angle_label_display_threshold', 65))
        except (TypeError, ValueError):
            threshold = 65
        if threshold <= 75:
            rows.append(u'75\N{DEGREE SIGN}')
    if settings.get('eff_pen_label_enabled', False):
        rows.append('250')
    if settings.get('kill_label_enabled', False):
        rows.append(u'\N{DAGGER} 75%')
    if settings.get('gun_label_enabled', False):
        rows.append('GUN')
    if not rows:
        rows = [u'\N{EM DASH}']

    try:
        font_size = max(12, min(20, int(settings.get('armor_label_font_size', 16)) - 1))
    except (TypeError, ValueError):
        font_size = 15

    color = 'A970FF' if settings.get('colorblind', False) else '6BF40D'
    # A self-contained block in column1; do not set span=2.
    # Use simple table attributes, rather than div background CSS.
    markup = (
        u'<table width="320" bgcolor="#141C24" border="0" cellspacing="0" cellpadding="8">'
        u'<tr><td>'
        u'<font color="#9AA8B7" size="11"><b>INQ CALCULATOR • HUD</b></font><br><br>'
        u'<p align="center"><font color="#%s" size="%d"><b>%s</b></font></p>'
        u'</td></tr>'
        u'</table>'
    ) % (color, font_size, u'<br>'.join(rows))
    return templates.createLabel(markup, useHTML=True)


def _on_live_settings(*args, **kwargs):
    global _PREVIEW_REFRESHING
    if not _ASLAIN_MENU or _PREVIEW_REFRESHING:
        return
    if not hasattr(g_modsSettingsApi, 'reloadModTemplate'):
        return
    if args and isinstance(args[0], (str, unicode)) and args[0] != mod_linkage:
        return
    pending = None
    for arg in args:
        if isinstance(arg, dict):
            pending = arg
            break
    if pending is None:
        return
    try:
        _PREVIEW_REFRESHING = True
        g_modsSettingsApi.reloadModTemplate(mod_linkage, _template(pending))
    except Exception as error:
        print("me.inq preview refresh failed: %s" % error)
    finally:
        _PREVIEW_REFRESHING = False


def _template(preview_settings=None):
    t = _texts()
    cfg = get_config()
    template = {
        "modDisplayName": t["title"],
        # No settingsVersion: Aslain migrates matching saved control values.
        "enabled": True,
        "column1": [
            templates.createLabel(t["display"]),
            templates.createLabel(t["display_note"]),
            templates.createCheckbox(t["armor"], "armor_label_enabled", ArmorLabelSettings.ENABLED, tooltip=t["armor_tip"]),
            templates.createCheckbox(t["chance"], "pen_label_enabled", PenLabelSettings.ENABLED, tooltip=t["chance_tip"]),
            _section_divider(),
            templates.createLabel(t["extra"]),
            templates.createCheckbox(t["angle"], "angle_label_enabled", AngleLabelSettings.ENABLED, tooltip=t["angle_tip"]),
            templates.createCheckbox(t["separate_pen"], "eff_pen_label_enabled", EffPenLabelSettings.ENABLED, tooltip=t["separate_pen_tip"]),
            templates.createCheckbox(t["kill"], "kill_label_enabled", KillLabelSettings.ENABLED, tooltip=t["kill_tip"]),
            templates.createCheckbox(t["gun"], "gun_label_enabled", GunLabelSettings.ENABLED, tooltip=t["gun_tip"]),
            _section_divider(),
            templates.createLabel(t["accessibility"]),
            templates.createCheckbox(t["colorblind"], "colorblind", bool(cfg.get("colorblind", False)), tooltip=t["colorblind_tip"]),
        ],
        "column2": [
            templates.createLabel(t["position"]),
            templates.createLabel(t["position_note"]),
            templates.createSlider(t["size"], "armor_label_font_size", ArmorLabelSettings.FONT_SIZE, 10, 30, 1, tooltip=t["size_tip"]),
            templates.createSlider(t["x"], "armor_label_x_offset", ArmorLabelSettings.X_OFFSET, -300, 300, 1, tooltip=t["x_tip"]),
            templates.createSlider(t["y"], "armor_label_y_offset", ArmorLabelSettings.Y_OFFSET, -300, 300, 1, tooltip=t["y_tip"]),
            templates.createSlider(t["angle_from"], "angle_label_display_threshold", AngleLabelSettings.DISPLAY_THRESHOLD, 0, 90, 1, tooltip=t["angle_from_tip"]),
        ],
    }
    if _ASLAIN_MENU:
        try:
            preview_values = _preview_settings()
            if preview_settings:
                preview_values.update(preview_settings)
            template['column1'].insert(0, templates.createLabel(t['preview_note']))
            template['column1'].insert(0, _preview_label(preview_values))
            template['column1'].insert(0, templates.createLabel(t['preview_title']))
        except Exception as error:
            print("me.inq preview setup failed: %s" % error)
    return template


def _apply(settings):
    if not settings:
        return
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


def _is_our_linkage(linkage):
    return linkage == mod_linkage or linkage == (mod_linkage,)


def _on_settings_save(linkage, settings):
    if not _is_our_linkage(linkage):
        return
    _apply(settings)


def _register_settings():
    template = _template()
    # Always register the current template so labels and help text update.
    # setModTemplate returns persisted control values and preserves user choices.
    # getModSettings alone only reads values and may leave the old panel registered.
    saved = g_modsSettingsApi.setModTemplate(mod_linkage, template, _on_settings_save, None)
    if saved:
        _apply(saved)
    if _ASLAIN_MENU and hasattr(g_modsSettingsApi, 'registerLiveSettingsChange'):
        try:
            g_modsSettingsApi.registerLiveSettingsChange(mod_linkage, _on_live_settings,
                                                        fullsettings=True)
        except Exception as error:
            print("me.inq preview live hook failed: %s" % error)


try:
    _register_settings()
except Exception as error:
    print("me.inq settings registration failed: %s" % error)
