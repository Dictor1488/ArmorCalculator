from pade_constants import Colors
from gambiter import g_guiFlash  # type: ignore
from gambiter.flash import COMPONENT_TYPE, COMPONENT_ALIGN  # type: ignore

GREEN_TRACK_ALIAS = "unicorn_ares_GreenTrack"
YELLOW_TRACK_ALIAS = "unicorn_ares_YellowTrack"


class TrackState:
    ENABLED = True
    track_visible = False
    _last_track_color = None


def update_track_label(color):
    if color not in (Colors.GREEN, Colors.YELLOW):
        return
    if color == TrackState._last_track_color and TrackState.track_visible:
        return

    previous_color = TrackState._last_track_color
    if previous_color == Colors.GREEN:
        g_guiFlash.updateComponent(GREEN_TRACK_ALIAS, {"visible": False})
    elif previous_color == Colors.YELLOW:
        g_guiFlash.updateComponent(YELLOW_TRACK_ALIAS, {"visible": False})

    if color == Colors.GREEN:
        g_guiFlash.updateComponent(GREEN_TRACK_ALIAS, {"visible": True})
    else:
        g_guiFlash.updateComponent(YELLOW_TRACK_ALIAS, {"visible": True})

    TrackState._last_track_color = color
    TrackState.track_visible = True


def hide_track_label():
    if not TrackState.track_visible:
        return

    if TrackState._last_track_color == Colors.GREEN:
        g_guiFlash.updateComponent(GREEN_TRACK_ALIAS, {"visible": False})
    elif TrackState._last_track_color == Colors.YELLOW:
        g_guiFlash.updateComponent(YELLOW_TRACK_ALIAS, {"visible": False})

    TrackState._last_track_color = None
    TrackState.track_visible = False


green_track_properties = {
    "image": "img://gui/unicorn.ares/crosshair-32-green.png",
    "alpha": 1,
    "x": 0,
    "y": 0,
    "alignX": COMPONENT_ALIGN.CENTER,
    "alignY": COMPONENT_ALIGN.CENTER,
    "visible": False,
}

yellow_track_properties = {
    "image": "img://gui/unicorn.ares/crosshair-32-orange.png",
    "alpha": 1,
    "x": 0,
    "y": 0,
    "alignX": COMPONENT_ALIGN.CENTER,
    "alignY": COMPONENT_ALIGN.CENTER,
    "visible": False,
}


g_guiFlash.createComponent(GREEN_TRACK_ALIAS, COMPONENT_TYPE.IMAGE, green_track_properties)
g_guiFlash.createComponent(YELLOW_TRACK_ALIAS, COMPONENT_TYPE.IMAGE, yellow_track_properties)
