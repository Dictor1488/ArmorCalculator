# -*- coding: utf-8 -*-
import json
import logging

import BigWorld
import GUI
from PlayerEvents import g_playerEvents  # type: ignore
from frameworks.wulf import ViewModel, ViewSettings, ViewFlags, WindowFlags, WindowLayer, WindowStatus
from gui.impl.pub import ViewImpl, WindowImpl
from skeletons.gui.impl import IGuiLoader
from helpers import dependency

try:
    from openwg_gameface import ModDynAccessor
    _OPENWG_OK = True
except Exception:
    ModDynAccessor = None
    _OPENWG_OK = False

from pade_config import get_config

LOG = logging.getLogger('[unicorn.ares ArmorCalculator]')
RES_MAP_ITEM_ID = 'mods/unicorn_ares/ArmorCalculatorBattle/layoutID'

_WINDOW = None
_VIEW = None
_LAST_PAYLOAD = None
_PENDING_PAYLOAD = None
_RETRY_CALLBACK = None
_LAST_SURFACE = (220, 28, 1.0)


def _safe_float(value, default=1.0):
    try:
        return float(value)
    except Exception:
        return default


def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


class ArmorModel(ViewModel):
    def __init__(self, properties=1, commands=2):
        super(ArmorModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ArmorModel, self)._initialize()
        self._addStringProperty('payload', '{}')
        self.onReady = self._addCommand('onReady')
        self.onReady += self.__onReady
        self.onResized = self._addCommand('onResized')
        self.onResized += self.__onResized

    def __onReady(self, *args):
        _position_window(*_LAST_SURFACE)
        _flush_pending()

    def __onResized(self, sizeMap=None, *args):
        global _LAST_SURFACE
        try:
            width = max(1, _safe_int(sizeMap['width'], 220))
            height = max(1, _safe_int(sizeMap['height'], 28))
            game_scale = max(0.01, _safe_float(sizeMap.get('gameScale', 1.0), 1.0))
        except Exception:
            return
        _LAST_SURFACE = (width, height, game_scale)
        _position_window(width, height, game_scale)

    def setPayload(self, value):
        self._setString(0, value)


class ArmorView(ViewImpl):
    if _OPENWG_OK:
        viewLayoutID = ModDynAccessor(RES_MAP_ITEM_ID)
    else:
        viewLayoutID = None

    def __init__(self):
        if not _OPENWG_OK:
            raise RuntimeError('OpenWG.Gameface is required')
        settings = ViewSettings(ArmorView.viewLayoutID(), flags=ViewFlags.VIEW, model=ArmorModel())
        super(ArmorView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ArmorView, self).getViewModel()


class ArmorWindow(WindowImpl):
    def __init__(self, parent=None):
        super(ArmorWindow, self).__init__(
            WindowFlags.WINDOW,
            content=ArmorView(),
            layer=WindowLayer.VIEW,
            name='unicorn.ares ArmorCalculator',
            parent=parent
        )

    def _onReady(self):
        pass


def _get_main_window():
    try:
        loader = dependency.instance(IGuiLoader)
        manager = getattr(loader, 'windowsManager', None)
        return None if manager is None else manager.getMainWindow()
    except Exception:
        return None


def _position_window(surface_width=220, surface_height=28, game_scale=1.0):
    if _WINDOW is None:
        return
    cfg = get_config()
    main = cfg.get('armor_label', {})
    x_offset = _safe_int(main.get('x_offset', 0), 0)
    y_offset = _safe_int(main.get('y_offset', 35), 35)
    font_size = max(10, _safe_int(main.get('font_size', 16), 16))
    first_row_center = 4.0 + font_size * 0.575
    try:
        screen_w, screen_h = GUI.screenResolution()
    except Exception:
        screen_w, screen_h = 1920, 1080

    scale = max(0.01, _safe_float(game_scale, 1.0))
    target_x = int(round((screen_w - surface_width) / (2.0 * scale) + x_offset / scale))
    target_y = int(round(screen_h / (2.0 * scale) + y_offset / scale - first_row_center))
    try:
        _WINDOW.move(target_x, target_y)
    except Exception:
        LOG.exception('Failed to position GameFace window')


def _retry_load():
    global _RETRY_CALLBACK
    _RETRY_CALLBACK = None
    if _PENDING_PAYLOAD is not None:
        _push(_PENDING_PAYLOAD)


def ensure_window():
    global _WINDOW, _VIEW, _RETRY_CALLBACK
    if _WINDOW is not None:
        return True
    if not _OPENWG_OK:
        return False
    parent = _get_main_window()
    if parent is None or getattr(parent, 'proxy', None) is None or getattr(parent, 'windowStatus', None) != WindowStatus.LOADED:
        if _RETRY_CALLBACK is None:
            _RETRY_CALLBACK = BigWorld.callback(0.1, _retry_load)
        return False
    try:
        _WINDOW = ArmorWindow(parent=parent)
        _WINDOW.load()
        _VIEW = _WINDOW.content
        return True
    except Exception:
        LOG.exception('Failed to load GameFace ArmorCalculator')
        _WINDOW = None
        _VIEW = None
        return False


def destroy_window(*args, **kwargs):
    global _WINDOW, _VIEW, _LAST_PAYLOAD, _PENDING_PAYLOAD, _RETRY_CALLBACK
    if _RETRY_CALLBACK is not None:
        try:
            BigWorld.cancelCallback(_RETRY_CALLBACK)
        except Exception:
            pass
    _RETRY_CALLBACK = None
    if _WINDOW is not None:
        try:
            _WINDOW.destroy()
        except Exception:
            pass
    _WINDOW = None
    _VIEW = None
    _LAST_PAYLOAD = None
    _PENDING_PAYLOAD = None


def _flush_pending():
    if _PENDING_PAYLOAD is not None:
        _push(_PENDING_PAYLOAD, force=True)


def _push(payload, force=False):
    global _LAST_PAYLOAD, _PENDING_PAYLOAD
    _PENDING_PAYLOAD = payload
    if not ensure_window() or _VIEW is None:
        return
    try:
        raw = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    except Exception:
        return
    if not force and raw == _LAST_PAYLOAD:
        return
    try:
        with _VIEW.viewModel.transaction() as model:
            model.setPayload(raw)
        _LAST_PAYLOAD = raw
    except Exception:
        LOG.exception('Failed to push GameFace state')


class GuiState(object):
    def __init__(self):
        self.visible = False
        self.last_args = None

    def is_visible(self):
        return self.visible

    def hide_all(self):
        self.visible = False
        self.last_args = None
        _push({'visible': False})

    def update_gui(self, armor_value, prob, ricochet, hit_body, hit_track, hit_gun, hit_angle, avg_pen, kill_prob):
        armor_value = int(armor_value)
        avg_pen = int(avg_pen)
        prob = int(prob)
        hit_angle = int(hit_angle)
        kill_prob = int(kill_prob)
        self.last_args = (armor_value, prob, bool(ricochet), bool(hit_body), bool(hit_track), bool(hit_gun), hit_angle, avg_pen, kill_prob)

        if not hit_body and armor_value <= 0:
            self.hide_all()
            return

        cfg = get_config()
        colorblind = bool(cfg.get('colorblind', False))
        colors = cfg.get('colors', {})
        if ricochet or prob <= 7:
            color = colors.get('colorblind_red', 'A970FF') if colorblind else colors.get('red_chance', 'E90000')
        elif prob >= 93:
            color = colors.get('green_chance', '6BF40D')
        else:
            color = colors.get('medium_chance', 'FFFF00')

        angle_cfg = cfg.get('angle_label', {})
        body_details = bool(hit_body or ricochet)
        payload = {
            'visible': True,
            'armorEnabled': bool(cfg.get('armor_label', {}).get('enabled', True)),
            'chanceEnabled': bool(cfg.get('pen_label', {}).get('enabled', False) and body_details),
            'angleEnabled': bool(angle_cfg.get('enabled', False) and body_details and hit_angle >= _safe_int(angle_cfg.get('display_threshold', 65), 65)),
            'effPenEnabled': bool(cfg.get('eff_pen_label', {}).get('enabled', False) and body_details),
            'killEnabled': bool(cfg.get('kill_label', {}).get('enabled', False) and hit_body and kill_prob > 0),
            'gunEnabled': bool(cfg.get('gun_label', {}).get('enabled', False) and hit_gun),
            'armorText': '%d/%d' % (avg_pen, armor_value),
            'chanceText': '%d%%' % prob,
            'angleText': u'%d\N{DEGREE SIGN}' % hit_angle,
            'effPenText': '%d' % avg_pen,
            'killText': u'\N{DAGGER} %d%%' % kill_prob,
            'gunText': 'GUN',
            'color': '#' + color,
            'fontSize': max(10, _safe_int(cfg.get('armor_label', {}).get('font_size', 16), 16))
        }
        self.visible = True
        _push(payload)

    def update_properties(self):
        _position_window(*_LAST_SURFACE)
        if self.last_args is not None:
            self.update_gui(*self.last_args)


gui_state = GuiState()
g_playerEvents.onAvatarBecomeNonPlayer += destroy_window
