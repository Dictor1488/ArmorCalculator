from pade_constants import (
    Colors,
    ArmorLabelSettings,
    PenLabelSettings,
    AngleLabelSettings,
    EffPenLabelSettings,
    KillLabelSettings,
    GunLabelSettings,
    ShadowSettings,
)
import pade_track
from gambiter import g_guiFlash  # type: ignore
from gambiter.flash import COMPONENT_TYPE, COMPONENT_ALIGN  # type: ignore


def log(message):
    print("unicorn.ares Armor Calc: " + str(message))


ARMOR_ALIAS = "unicorn_ares_ArmorLabel"
PEN_ALIAS = "unicorn_ares_PenLabel"
ANGLE_ALIAS = "unicorn_ares_AngleLabel"
EFF_PEN_ALIAS = "unicorn_ares_EffPenLabel"
KILL_ALIAS = "unicorn_ares_KillLabel"
GUN_ALIAS = "unicorn_ares_GunLabel"


class GuiState(object):
    def __init__(self):
        self.armor_label = Label(ARMOR_ALIAS, ArmorLabelSettings)
        self.pen_label = Label(PEN_ALIAS, PenLabelSettings)
        self.angle_label = AngleLabel(ANGLE_ALIAS, AngleLabelSettings)
        self.eff_pen_label = Label(EFF_PEN_ALIAS, EffPenLabelSettings)
        self.kill_label = Label(KILL_ALIAS, KillLabelSettings)
        self.gun_label = Label(GUN_ALIAS, GunLabelSettings)
        self.labels = [self.armor_label, self.pen_label, self.angle_label, self.eff_pen_label, self.kill_label, self.gun_label]

    def is_visible(self):
        return any(label.visible for label in self.labels)

    def hide_all(self):
        for label in self.labels:
            if label.visible:
                label.hide()
        if pade_track.TrackState.ENABLED and pade_track.TrackState.track_visible:
            pade_track.hide_track_label()

    def update_gui(self, armor_value, prob, ricochet, hit_body, hit_track, hit_gun, hit_angle, avg_pen, kill_prob):
        armor_value = int(armor_value)
        avg_pen = int(avg_pen)
        armor_format_values = {"value": armor_value, "armor": armor_value, "penetration": avg_pen}

        if ricochet:
            color = Colors.RED
            if self.armor_label.settings.ENABLED:
                self.armor_label.update_gui(armor_value, color, armor_format_values)
            if self.pen_label.settings.ENABLED:
                self.pen_label.update_gui(0, color)
            if self.angle_label.settings.ENABLED:
                self.angle_label.update_gui(hit_angle, color)
            if self.eff_pen_label.settings.ENABLED:
                self.eff_pen_label.update_gui(avg_pen, color)
            if self.kill_label.visible:
                self.kill_label.hide()
        elif not hit_body:
            color = Colors.RED
            if armor_value > 0 and self.armor_label.settings.ENABLED:
                self.armor_label.update_gui(armor_value, color, armor_format_values)
                for label in (self.pen_label, self.angle_label, self.eff_pen_label, self.kill_label):
                    if label.visible:
                        label.hide()
            else:
                self.hide_all()
        else:
            color = Colors.get_color_from_prob(prob)
            if self.armor_label.settings.ENABLED:
                self.armor_label.update_gui(armor_value, color, armor_format_values)
            if self.pen_label.settings.ENABLED:
                self.pen_label.update_gui(int(prob), color)
            if self.angle_label.settings.ENABLED:
                self.angle_label.update_gui(hit_angle, color)
            if self.eff_pen_label.settings.ENABLED:
                self.eff_pen_label.update_gui(avg_pen, color)
            if self.kill_label.settings.ENABLED:
                if kill_prob > 0:
                    self.kill_label.update_gui(kill_prob, Colors.get_color_from_prob(kill_prob))
                elif self.kill_label.visible:
                    self.kill_label.hide()

        if self.gun_label.settings.ENABLED:
            if hit_gun:
                self.gun_label.update_gui("GUN", Colors.YELLOW)
            elif self.gun_label.visible:
                self.gun_label.hide()

        if pade_track.TrackState.ENABLED:
            if hit_track and color in (Colors.GREEN, Colors.YELLOW):
                pade_track.update_track_label(color)
            elif pade_track.TrackState.track_visible:
                pade_track.hide_track_label()

    def update_properties(self):
        for label in self.labels:
            label.update_properties()


class Label(object):
    def __init__(self, alias, settings):
        self.alias = alias
        self.settings = settings
        self.visible = False
        self.last_text = None
        g_guiFlash.createComponent(alias, COMPONENT_TYPE.LABEL, {
            "isHtml": True,
            "text": "",
            "glowfilter": _build_glowfilter(),
            "alignX": COMPONENT_ALIGN.CENTER,
            "alignY": COMPONENT_ALIGN.CENTER,
            "x": settings.X_OFFSET,
            "y": settings.Y_OFFSET,
            "visible": False,
        })

    def hide(self):
        if self.visible:
            g_guiFlash.updateComponent(self.alias, {"visible": False})
            self.visible = False
            self.last_text = None

    def update_gui(self, value, color, format_values=None):
        values = {"value": value}
        if format_values:
            values.update(format_values)
        try:
            interior_text = self.settings.LABEL_FORMAT.format(**values)
        except (KeyError, ValueError):
            interior_text = str(value)
        new_text = "<font size='{font_size}' color='#{color}' face='$FieldFont'>{interior_text}</font>".format(
            font_size=self.settings.FONT_SIZE, color=color, interior_text=interior_text
        )
        if new_text == self.last_text and self.visible:
            return
        self.last_text = new_text
        self.visible = True
        g_guiFlash.updateComponent(self.alias, {"text": new_text, "visible": True})

    def update_properties(self):
        if not self.settings.ENABLED:
            self.hide()
        g_guiFlash.updateComponent(self.alias, {
            "x": self.settings.X_OFFSET,
            "y": self.settings.Y_OFFSET,
            "glowfilter": _build_glowfilter(),
        })


class AngleLabel(Label):
    def update_gui(self, value, color, format_values=None):
        if value < self.settings.DISPLAY_THRESHOLD:
            self.hide()
            return
        super(AngleLabel, self).update_gui(value, color, format_values)


def _build_glowfilter():
    return {
        "color": int(ShadowSettings.COLOR, 16),
        "alpha": ShadowSettings.ALPHA / 10.0,
        "blurX": ShadowSettings.LENGTH,
        "blurY": ShadowSettings.LENGTH,
        "strength": ShadowSettings.STRENGTH,
        "quality": 2,
    }


log("Creating GUI components")
gui_state = GuiState()
log("GUI components created")
