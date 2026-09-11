# -*- coding: utf-8 -*-
"""Lightweight Armor Calculator lifecycle hooks.

Armor/penetration calculation now lives exclusively in
mod_unicorn_ares_crosshair_bridge.py and uses WoT's own shot-result resolver.
Keeping a second patched copy of _CrosshairShotResults here caused duplicate
GUI updates and made HE/HEAT behaviour depend on which callback ran last.
"""

from AvatarInputHandler import AvatarInputHandler  # type: ignore
from PlayerEvents import g_playerEvents  # type: ignore

from unicorn_ares_gui import gui_state


def log(message):
    print("unicorn.ares Armor Calculator: " + str(message))


log("Mod is loading")


def on_load_match(*args, **kwargs):
    gui_state.hide_all()


def on_leave_match(*args, **kwargs):
    gui_state.hide_all()


# Preserve the useful old behaviour: never leave the armor readout hanging
# when the player switches into postmortem mode. No shot-result internals are
# patched anymore; the crosshair bridge is the single calculation source.
_original_activate_postmortem = AvatarInputHandler.activatePostmortem


def _activate_postmortem(self, *args, **kwargs):
    result = _original_activate_postmortem(self, *args, **kwargs)
    gui_state.hide_all()
    return result


AvatarInputHandler.activatePostmortem = _activate_postmortem
g_playerEvents.onAvatarReady += on_load_match
g_playerEvents.onAvatarBecomeNonPlayer += on_leave_match
