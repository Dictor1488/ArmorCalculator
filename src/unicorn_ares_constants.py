# -*- coding: utf-8 -*-
from unicorn_ares_config import user_settings, DEFAULT_CONFIG


def safe_get_setting(label, attribute):
    default = DEFAULT_CONFIG[label][attribute]
    if label not in user_settings or attribute not in user_settings[label]:
        return default
    return user_settings[label][attribute]


class Colors(object):
    RED = "E90000"
    YELLOW = "FFFF00"
    GREEN = "6BF40D"
    PURPLE = "A970FF"

    @classmethod
    def get_color_from_prob(cls, prob, colorblind=False):
        if prob <= 7:
            return cls.PURPLE if colorblind else cls.RED
        if prob >= 93:
            return cls.GREEN
        return cls.YELLOW


class ArmorLabelSettings(object):
    ENABLED = safe_get_setting("armor_label", "enabled")
    LABEL_FORMAT = DEFAULT_CONFIG["armor_label"]["label_format"]
    FONT_SIZE = safe_get_setting("armor_label", "font_size")
    X_OFFSET = safe_get_setting("armor_label", "x_offset")
    Y_OFFSET = safe_get_setting("armor_label", "y_offset")


class PenLabelSettings(object):
    ENABLED = safe_get_setting("pen_label", "enabled")
    LABEL_FORMAT = DEFAULT_CONFIG["pen_label"]["label_format"]
    FONT_SIZE = safe_get_setting("pen_label", "font_size")
    X_OFFSET = safe_get_setting("pen_label", "x_offset")
    Y_OFFSET = safe_get_setting("pen_label", "y_offset")


class AngleLabelSettings(object):
    ENABLED = safe_get_setting("angle_label", "enabled")
    LABEL_FORMAT = DEFAULT_CONFIG["angle_label"]["label_format"]
    FONT_SIZE = safe_get_setting("angle_label", "font_size")
    X_OFFSET = safe_get_setting("angle_label", "x_offset")
    Y_OFFSET = safe_get_setting("angle_label", "y_offset")
    DISPLAY_THRESHOLD = safe_get_setting("angle_label", "display_threshold")


class EffPenLabelSettings(object):
    ENABLED = safe_get_setting("eff_pen_label", "enabled")
    LABEL_FORMAT = DEFAULT_CONFIG["eff_pen_label"]["label_format"]
    FONT_SIZE = safe_get_setting("eff_pen_label", "font_size")
    X_OFFSET = safe_get_setting("eff_pen_label", "x_offset")
    Y_OFFSET = safe_get_setting("eff_pen_label", "y_offset")


class KillLabelSettings(object):
    ENABLED = safe_get_setting("kill_label", "enabled")
    LABEL_FORMAT = DEFAULT_CONFIG["kill_label"]["label_format"]
    FONT_SIZE = safe_get_setting("kill_label", "font_size")
    X_OFFSET = safe_get_setting("kill_label", "x_offset")
    Y_OFFSET = safe_get_setting("kill_label", "y_offset")


class GunLabelSettings(object):
    ENABLED = safe_get_setting("gun_label", "enabled")
    LABEL_FORMAT = DEFAULT_CONFIG["gun_label"]["label_format"]
    FONT_SIZE = safe_get_setting("gun_label", "font_size")
    X_OFFSET = safe_get_setting("gun_label", "x_offset")
    Y_OFFSET = safe_get_setting("gun_label", "y_offset")
