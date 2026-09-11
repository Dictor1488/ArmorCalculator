# -*- coding: utf-8 -*-
import math

import BigWorld
from AvatarInputHandler import gun_marker_ctrl  # type: ignore
from DestructibleEntity import DestructibleEntity  # type: ignore
from Vehicle import Vehicle as VehicleEntity  # type: ignore
from PlayerEvents import g_playerEvents  # type: ignore
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider  # type: ignore

from unicorn_ares_gui import gui_state


_SESSION = dependency.instance(IBattleSessionProvider)
_RESOLVER = gun_marker_ctrl.createShotResultResolver()
_SUBSCRIBED = False
_RETRY = None


def _log(message):
    print('unicorn.ares crosshair bridge: ' + str(message))


def _safe_health(entity):
    try:
        return int(getattr(entity, 'health', 0))
    except Exception:
        return 0


def _get_jet_loss(shell):
    try:
        extra = _RESOLVER._SHELL_EXTRA_DATA[shell.kind]
        if hasattr(extra, 'jetLossPPByDist'):
            return float(getattr(extra, 'jetLossPPByDist', 0.0))
        if getattr(extra, 'hasPenetrationLoss', False):
            return float(getattr(shell.type, 'piercingPowerLossFactorByDistance', 0.0))
    except Exception:
        pass
    return 0.0


def _compute_effective_armor(hit_point, direction, collision, shell):
    if collision is None:
        return (0.0, False, False, False, False, 1.0)

    entity = collision.entity
    try:
        details = _RESOLVER._getAllCollisionDetails(hit_point, direction, entity)
    except Exception:
        return (0.0, False, False, False, False, 1.0)

    if not details:
        return (0.0, False, False, False, False, 1.0)

    total_armor = 0.0
    ignored = set()
    ricochet = False
    hit_body = False
    hit_track = False
    hit_gun = False
    hit_angle_cos = 1.0
    jet_start = None
    jet_loss_by_dist = _get_jet_loss(shell)

    for item in details:
        try:
            if not _RESOLVER._CrosshairShotResults__isDestructibleComponent(entity, item.compName):
                break
        except Exception:
            break

        if not hit_track and (item.compName == 0 or item.compName >= 4):
            hit_track = True
        if item.compName == 3:
            hit_gun = True

        material = item.matInfo
        if material is None or material.armor is None:
            continue

        key = (item.compName, material.kind)
        if key in ignored:
            continue

        angle_cos = item.hitAngleCos if material.useHitAngle else 1.0

        if jet_start is not None and jet_loss_by_dist > 0.0:
            air_dist = item.dist - jet_start
            if air_dist > 0.0:
                # Express HEAT air loss as equivalent armor so the displayed
                # effective value follows the same penetration budget.
                try:
                    player = BigWorld.player()
                    v_desc = player.getVehicleDescriptor() if player is not None else None
                    base_pp = v_desc.shot.piercingPower[0] if v_desc is not None else 0.0
                    total_armor += max(0.0, base_pp * air_dist * jet_loss_by_dist)
                except Exception:
                    pass

        try:
            penetration_armor = _RESOLVER._computePenetrationArmor(shell, angle_cos, material)
        except Exception:
            penetration_armor = 0.0

        total_armor += penetration_armor

        try:
            this_ricochet = bool(_RESOLVER._shouldRicochet(shell, angle_cos, material))
        except Exception:
            this_ricochet = False

        if this_ricochet:
            ricochet = True
            hit_angle_cos = angle_cos
            break

        if material.collideOnceOnly:
            ignored.add(key)

        if material.vehicleDamageFactor:
            hit_body = True
            hit_angle_cos = angle_cos
            break

        if jet_start is None and jet_loss_by_dist > 0.0:
            jet_start = item.dist + float(material.armor) * 0.001

    return (float(total_armor), ricochet, hit_body, hit_track, hit_gun, hit_angle_cos)


def _compute_and_show(hit_point, direction, collision):
    if collision is None:
        gui_state.hide_all()
        return

    entity = collision.entity
    if not isinstance(entity, (VehicleEntity, DestructibleEntity)):
        gui_state.hide_all()
        return

    player = BigWorld.player()
    if player is None:
        gui_state.hide_all()
        return

    try:
        v_desc = player.getVehicleDescriptor()
        shot = v_desc.shot
        shell = shot.shell
        distance = (hit_point - player.getOwnVehiclePosition()).length
        current_pen = _RESOLVER._computePiercingPowerAtDist(shot.piercingPower, distance, shot.maxDistance, 1)
        if isinstance(current_pen, (tuple, list)):
            current_pen = current_pen[0]
        current_pen = float(current_pen)
    except Exception as error:
        _log('compute failed: %s' % error)
        gui_state.hide_all()
        return

    armor, ricochet, hit_body, hit_track, hit_gun, angle_cos = _compute_effective_armor(hit_point, direction, collision, shell)

    angle_cos = max(-1.0, min(1.0, float(angle_cos)))
    hit_angle = int(math.degrees(math.acos(angle_cos)))

    # The GUI calculates chance itself from penetration/armor. Pass the
    # current penetration value as avg_pen so distance is reflected.
    prob = 0
    if not ricochet and hit_body:
        min_pen = current_pen * 0.75
        max_pen = current_pen * 1.25
        if armor <= min_pen:
            prob = 100
        elif armor >= max_pen:
            prob = 0
        else:
            sigma = current_pen / 12.0
            z = (armor - current_pen) / sigma
            phi = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
            prob = int((1.0 - phi) * 100.0)

    gui_state.update_gui(
        armor,
        prob,
        ricochet,
        hit_body,
        hit_track,
        hit_gun,
        hit_angle,
        current_pen,
        0,
    )


def _on_marker_changed(marker_type, hit_point, direction, collision):
    _compute_and_show(hit_point, direction, collision)


def _subscribe():
    global _SUBSCRIBED, _RETRY
    _RETRY = None
    if _SUBSCRIBED:
        return
    try:
        crosshair = _SESSION.shared.crosshair
        if crosshair is None:
            raise RuntimeError('crosshair controller is not ready')
        crosshair.onGunMarkerStateChanged += _on_marker_changed
        _SUBSCRIBED = True
        _log('subscribed to onGunMarkerStateChanged')
    except Exception:
        _RETRY = BigWorld.callback(0.25, _subscribe)


def _unsubscribe(*args, **kwargs):
    global _SUBSCRIBED, _RETRY
    if _RETRY is not None:
        try:
            BigWorld.cancelCallback(_RETRY)
        except Exception:
            pass
        _RETRY = None
    if not _SUBSCRIBED:
        return
    try:
        crosshair = _SESSION.shared.crosshair
        if crosshair is not None:
            crosshair.onGunMarkerStateChanged -= _on_marker_changed
    except Exception:
        pass
    _SUBSCRIBED = False


def _on_avatar_player(*args, **kwargs):
    _subscribe()


def _on_avatar_non_player(*args, **kwargs):
    _unsubscribe()
    gui_state.hide_all()


g_playerEvents.onAvatarBecomePlayer += _on_avatar_player
g_playerEvents.onAvatarBecomeNonPlayer += _on_avatar_non_player
_log('loaded')
