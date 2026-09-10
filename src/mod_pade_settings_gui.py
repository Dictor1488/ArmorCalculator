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
    Colors,
    ShadowSettings,
)
from pade_config import save_flat_config
from pade_gui import gui_state


mod_linkage = "pade_armor_calculator"
modDataVersion = 3


TRANSLATIONS = {
    "en": {
        "mod_name": "pademinune's Armor Penetration Calculator",
        "armor_section": "Armor Label",
        "armor_enable": "Enable Armor Label",
        "armor_enable_tip": "Show or hide the penetration/armor label.",
        "armor_size": "Armor Label Font Size",
        "armor_x": "Armor Label Horizontal Offset",
        "armor_y": "Armor Label Vertical Offset",
        "armor_format": "Armor Label Format",
        "armor_format_tip": "{penetration} is current penetration and {armor}/{value} is effective armor.",
        "prob_section": "Probability Label",
        "prob_enable": "Enable Probability Label",
        "prob_enable_tip": "Show or hide the penetration probability label.",
        "prob_size": "Probability Font Size",
        "prob_x": "Probability Horizontal Offset",
        "prob_y": "Probability Vertical Offset",
        "prob_format": "Probability Format",
        "prob_format_tip": "{value} is the penetration chance.",
        "angle_section": "Impact Angle Label",
        "angle_enable": "Enable Impact Angle Label",
        "angle_enable_tip": "Show or hide the shell impact angle.",
        "angle_size": "Impact Angle Font Size",
        "angle_x": "Impact Angle Horizontal Offset",
        "angle_y": "Impact Angle Vertical Offset",
        "angle_format": "Impact Angle Format",
        "angle_format_tip": "{value} is the impact angle in degrees.",
        "angle_threshold": "Angle Display Threshold",
        "angle_threshold_tip": "Minimum angle at which the label is shown. Set 0 to always show it.",
        "eff_section": "Effective Penetration Label",
        "eff_enable": "Enable Effective Penetration Label",
        "eff_enable_tip": "Show or hide the shell's current penetration as a separate label.",
        "eff_size": "Effective Penetration Font Size",
        "eff_x": "Effective Penetration Horizontal Offset",
        "eff_y": "Effective Penetration Vertical Offset",
        "eff_format": "Effective Penetration Format",
        "eff_format_tip": "{value} is the current penetration.",
        "kill_section": "Kill Chance Label",
        "kill_enable": "Enable Kill Chance Label",
        "kill_enable_tip": "Show or hide the estimated penetration-and-kill chance.",
        "kill_size": "Kill Chance Font Size",
        "kill_x": "Kill Chance Horizontal Offset",
        "kill_y": "Kill Chance Vertical Offset",
        "kill_format": "Kill Chance Format",
        "kill_format_tip": "{value} is the estimated kill chance.",
        "gun_section": "Gun Blocking Label",
        "gun_enable": "Enable Gun Blocking Label",
        "gun_enable_tip": "Show a label when the current shot line intersects the enemy gun collision model.",
        "gun_size": "Gun Label Font Size",
        "gun_x": "Gun Label Horizontal Offset",
        "gun_y": "Gun Label Vertical Offset",
        "gun_format": "Gun Label Format",
        "gun_format_tip": "Text shown when the enemy gun is in the shot path. {value} resolves to GUN.",
        "colors_section": "Colors",
        "color_high": "High Penetration Chance",
        "color_medium": "Medium Penetration Chance",
        "color_low": "Low Penetration Chance",
        "color_ricochet": "Ricochet",
        "shadow_section": "Shadow",
        "shadow_color": "Shadow Color",
        "shadow_alpha": "Shadow Opacity",
        "shadow_length": "Shadow Blur",
        "shadow_strength": "Shadow Strength",
    },
    "uk": {
        "mod_name": "Калькулятор пробиття броні pademinune",
        "armor_section": "Пробиття / броня",
        "armor_enable": "Показувати пробиття та броню",
        "armor_enable_tip": "Показує або приховує напис поточного пробиття та ефективної броні.",
        "armor_size": "Розмір шрифту пробиття / броні",
        "armor_x": "Горизонтальне зміщення пробиття / броні",
        "armor_y": "Вертикальне зміщення пробиття / броні",
        "armor_format": "Формат пробиття / броні",
        "armor_format_tip": "{penetration} — поточне пробиття, {armor}/{value} — ефективна броня.",
        "prob_section": "Імовірність пробиття",
        "prob_enable": "Показувати шанс пробиття",
        "prob_enable_tip": "Показує або приховує розрахункову ймовірність пробиття.",
        "prob_size": "Розмір шрифту шансу",
        "prob_x": "Горизонтальне зміщення шансу",
        "prob_y": "Вертикальне зміщення шансу",
        "prob_format": "Формат шансу пробиття",
        "prob_format_tip": "{value} замінюється шансом пробиття.",
        "angle_section": "Кут влучання",
        "angle_enable": "Показувати кут влучання",
        "angle_enable_tip": "Показує або приховує кут входження снаряда в броню.",
        "angle_size": "Розмір шрифту кута",
        "angle_x": "Горизонтальне зміщення кута",
        "angle_y": "Вертикальне зміщення кута",
        "angle_format": "Формат кута",
        "angle_format_tip": "{value} замінюється кутом у градусах.",
        "angle_threshold": "Поріг показу кута",
        "angle_threshold_tip": "Мінімальний кут для показу. Значення 0 показує його завжди.",
        "eff_section": "Окремий напис пробиття",
        "eff_enable": "Показувати окреме пробиття",
        "eff_enable_tip": "Показує або приховує окремий напис поточного пробиття снаряда.",
        "eff_size": "Розмір шрифту пробиття",
        "eff_x": "Горизонтальне зміщення пробиття",
        "eff_y": "Вертикальне зміщення пробиття",
        "eff_format": "Формат окремого пробиття",
        "eff_format_tip": "{value} замінюється поточним пробиттям.",
        "kill_section": "Шанс добивання",
        "kill_enable": "Показувати шанс добивання",
        "kill_enable_tip": "Показує або приховує оцінений шанс пробити та знищити ціль.",
        "kill_size": "Розмір шрифту шансу добивання",
        "kill_x": "Горизонтальне зміщення добивання",
        "kill_y": "Вертикальне зміщення добивання",
        "kill_format": "Формат шансу добивання",
        "kill_format_tip": "{value} замінюється шансом добивання.",
        "gun_section": "Перекриття гарматою",
        "gun_enable": "Показувати перекриття гарматою",
        "gun_enable_tip": "Показує напис, коли траєкторія пострілу проходить через collision-модель гармати противника.",
        "gun_size": "Розмір шрифту напису гармати",
        "gun_x": "Горизонтальне зміщення напису гармати",
        "gun_y": "Вертикальне зміщення напису гармати",
        "gun_format": "Формат напису гармати",
        "gun_format_tip": "Текст при попаданні в модель гармати. {value} замінюється на GUN.",
        "colors_section": "Кольори",
        "color_high": "Високий шанс пробиття",
        "color_medium": "Середній шанс пробиття",
        "color_low": "Низький шанс пробиття",
        "color_ricochet": "Рикошет",
        "shadow_section": "Тінь тексту",
        "shadow_color": "Колір тіні",
        "shadow_alpha": "Прозорість тіні",
        "shadow_length": "Розмиття тіні",
        "shadow_strength": "Сила тіні",
    },
    "ru": {
        "mod_name": "Калькулятор пробития брони pademinune",
        "armor_section": "Пробитие / броня",
        "armor_enable": "Показывать пробитие и броню",
        "armor_enable_tip": "Показывает или скрывает текущее пробитие и эффективную броню.",
        "armor_size": "Размер шрифта пробития / брони",
        "armor_x": "Горизонтальное смещение пробития / брони",
        "armor_y": "Вертикальное смещение пробития / брони",
        "armor_format": "Формат пробития / брони",
        "armor_format_tip": "{penetration} — текущее пробитие, {armor}/{value} — эффективная броня.",
        "prob_section": "Вероятность пробития",
        "prob_enable": "Показывать шанс пробития",
        "prob_enable_tip": "Показывает или скрывает расчётную вероятность пробития.",
        "prob_size": "Размер шрифта шанса",
        "prob_x": "Горизонтальное смещение шанса",
        "prob_y": "Вертикальное смещение шанса",
        "prob_format": "Формат шанса пробития",
        "prob_format_tip": "{value} заменяется шансом пробития.",
        "angle_section": "Угол попадания",
        "angle_enable": "Показывать угол попадания",
        "angle_enable_tip": "Показывает или скрывает угол входа снаряда в броню.",
        "angle_size": "Размер шрифта угла",
        "angle_x": "Горизонтальное смещение угла",
        "angle_y": "Вертикальное смещение угла",
        "angle_format": "Формат угла",
        "angle_format_tip": "{value} заменяется углом в градусах.",
        "angle_threshold": "Порог показа угла",
        "angle_threshold_tip": "Минимальный угол для показа. Значение 0 показывает его всегда.",
        "eff_section": "Отдельная надпись пробития",
        "eff_enable": "Показывать отдельное пробитие",
        "eff_enable_tip": "Показывает или скрывает отдельное текущее пробитие снаряда.",
        "eff_size": "Размер шрифта пробития",
        "eff_x": "Горизонтальное смещение пробития",
        "eff_y": "Вертикальное смещение пробития",
        "eff_format": "Формат отдельного пробития",
        "eff_format_tip": "{value} заменяется текущим пробитием.",
        "kill_section": "Шанс добивания",
        "kill_enable": "Показывать шанс добивания",
        "kill_enable_tip": "Показывает или скрывает оценённый шанс пробить и уничтожить цель.",
        "kill_size": "Размер шрифта шанса добивания",
        "kill_x": "Горизонтальное смещение добивания",
        "kill_y": "Вертикальное смещение добивания",
        "kill_format": "Формат шанса добивания",
        "kill_format_tip": "{value} заменяется шансом добивания.",
        "gun_section": "Перекрытие орудием",
        "gun_enable": "Показывать перекрытие орудием",
        "gun_enable_tip": "Показывает надпись, когда линия выстрела проходит через collision-модель орудия противника.",
        "gun_size": "Размер шрифта надписи орудия",
        "gun_x": "Горизонтальное смещение надписи орудия",
        "gun_y": "Вертикальное смещение надписи орудия",
        "gun_format": "Формат надписи орудия",
        "gun_format_tip": "Текст при попадании в модель орудия. {value} заменяется на GUN.",
        "colors_section": "Цвета",
        "color_high": "Высокий шанс пробития",
        "color_medium": "Средний шанс пробития",
        "color_low": "Низкий шанс пробития",
        "color_ricochet": "Рикошет",
        "shadow_section": "Тень текста",
        "shadow_color": "Цвет тени",
        "shadow_alpha": "Прозрачность тени",
        "shadow_length": "Размытие тени",
        "shadow_strength": "Сила тени",
    },
}


def _get_language():
    language = "en"
    if getClientLanguage is not None:
        try:
            language = str(getClientLanguage()).lower().replace("-", "_")
        except Exception:
            language = "en"
    if language.startswith("uk") or language.startswith("ua"):
        return "uk"
    if language.startswith("ru"):
        return "ru"
    return "en"


TEXT = TRANSLATIONS[_get_language()]


def tr(key):
    return TEXT.get(key, TRANSLATIONS["en"].get(key, key))


def section(key):
    return templates.createLabel("<b>— %s —</b>" % tr(key))


def tooltip(header_key, body_key):
    return "{HEADER}%s{/HEADER}{BODY}%s{/BODY}" % (tr(header_key), tr(body_key))


def generic_tip(key):
    return tooltip(key, key + "_tip") if key + "_tip" in TEXT or key + "_tip" in TRANSLATIONS["en"] else None


def label_controls(prefix, settings, names, include_threshold=False):
    section_key, enable_key, size_key, x_key, y_key, format_key = names
    controls = [
        section(section_key),
        templates.createCheckbox(tr(enable_key), prefix + "_enabled", settings.ENABLED, tooltip=generic_tip(enable_key)),
        templates.createSlider(tr(size_key), prefix + "_font_size", settings.FONT_SIZE, 5, 100, 1, format="{{value}}px"),
        templates.createNumericStepper(tr(x_key), prefix + "_x_offset", settings.X_OFFSET, -2000, 2000, 1, manual=True),
        templates.createNumericStepper(tr(y_key), prefix + "_y_offset", settings.Y_OFFSET, -2000, 2000, 1, manual=True),
        templates.createInput(tr(format_key), prefix + "_format", settings.LABEL_FORMAT, tooltip=generic_tip(format_key)),
    ]
    if include_threshold:
        controls.append(
            templates.createNumericStepper(
                tr("angle_threshold"),
                prefix + "_display_threshold",
                settings.DISPLAY_THRESHOLD,
                0,
                90,
                1,
                manual=True,
                tooltip=generic_tip("angle_threshold"),
            )
        )
    controls.append(templates.createEmpty(10))
    return controls


column1 = []
column1 += label_controls(
    "armor_label",
    ArmorLabelSettings,
    ("armor_section", "armor_enable", "armor_size", "armor_x", "armor_y", "armor_format"),
)
column1 += label_controls(
    "pen_label",
    PenLabelSettings,
    ("prob_section", "prob_enable", "prob_size", "prob_x", "prob_y", "prob_format"),
)
column1 += label_controls(
    "angle_label",
    AngleLabelSettings,
    ("angle_section", "angle_enable", "angle_size", "angle_x", "angle_y", "angle_format"),
    include_threshold=True,
)
column1 += label_controls(
    "eff_pen_label",
    EffPenLabelSettings,
    ("eff_section", "eff_enable", "eff_size", "eff_x", "eff_y", "eff_format"),
)

column2 = []
column2 += label_controls(
    "kill_label",
    KillLabelSettings,
    ("kill_section", "kill_enable", "kill_size", "kill_x", "kill_y", "kill_format"),
)
column2 += label_controls(
    "gun_label",
    GunLabelSettings,
    ("gun_section", "gun_enable", "gun_size", "gun_x", "gun_y", "gun_format"),
)
column2 += [
    section("colors_section"),
    templates.createColorChoice(tr("color_high"), "color_green", Colors.GREEN),
    templates.createColorChoice(tr("color_medium"), "color_orange", Colors.ORANGE),
    templates.createColorChoice(tr("color_low"), "color_red", Colors.RED),
    templates.createColorChoice(tr("color_ricochet"), "color_ricochet", Colors.PURPLE),
    templates.createEmpty(10),
    section("shadow_section"),
    templates.createColorChoice(tr("shadow_color"), "shadow_color", ShadowSettings.COLOR),
    templates.createSlider(tr("shadow_alpha"), "shadow_alpha", ShadowSettings.ALPHA, 0, 10, 1, format="{{value}}"),
    templates.createSlider(tr("shadow_length"), "shadow_length", ShadowSettings.LENGTH, 0, 10, 1, format="{{value}}"),
    templates.createSlider(tr("shadow_strength"), "shadow_strength", ShadowSettings.STRENGTH, 0, 10, 1, format="{{value}}"),
]


template = {
    "modDisplayName": tr("mod_name"),
    "enabled": True,
    "column1": column1,
    "column2": column2,
}


def apply_label_settings(settings_class, new_settings, prefix, include_threshold=False):
    settings_class.ENABLED = new_settings[prefix + "_enabled"]
    settings_class.FONT_SIZE = new_settings[prefix + "_font_size"]
    settings_class.X_OFFSET = new_settings[prefix + "_x_offset"]
    settings_class.Y_OFFSET = new_settings[prefix + "_y_offset"]
    settings_class.LABEL_FORMAT = new_settings[prefix + "_format"]
    if include_threshold:
        settings_class.DISPLAY_THRESHOLD = new_settings[prefix + "_display_threshold"]


def on_settings_save(linkage, new_settings):
    if linkage != mod_linkage:
        return

    apply_label_settings(ArmorLabelSettings, new_settings, "armor_label")
    apply_label_settings(PenLabelSettings, new_settings, "pen_label")
    apply_label_settings(AngleLabelSettings, new_settings, "angle_label", True)
    apply_label_settings(EffPenLabelSettings, new_settings, "eff_pen_label")
    apply_label_settings(KillLabelSettings, new_settings, "kill_label")
    apply_label_settings(GunLabelSettings, new_settings, "gun_label")

    Colors.GREEN = new_settings["color_green"]
    Colors.ORANGE = new_settings["color_orange"]
    Colors.RED = new_settings["color_red"]
    Colors.PURPLE = new_settings["color_ricochet"]

    ShadowSettings.COLOR = new_settings["shadow_color"]
    ShadowSettings.ALPHA = new_settings["shadow_alpha"]
    ShadowSettings.LENGTH = new_settings["shadow_length"]
    ShadowSettings.STRENGTH = new_settings["shadow_strength"]

    save_flat_config(new_settings)
    gui_state.update_properties()


g_modsSettingsApi.setModTemplate(mod_linkage, template, on_settings_save, None)
