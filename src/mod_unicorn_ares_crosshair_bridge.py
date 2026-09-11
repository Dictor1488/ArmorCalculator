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
                continue
        except Exception:
            continue

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
                try:
                    total_armor += max(0.0, air_dist * jet_loss_by_dist)
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


def _get_shot(player, gun_marker_state):
    v_desc = player.getVehicleDescriptor()
    try:
        slot = v_desc.gunInstallations[gun_marker_state.gunInstallationIndex]
        if slot.isMainInstallation():
            return v_desc.shot
        return slot.gun.shots[0]
    except Exception:
        return v_desc.shot


def _compute_and_show(gun_marker_state):
    if gun_marker_state is None:
        gui_state.hide_all()
        return

    collision = getattr(gun_marker_state, 'collData', None)
    hit_point = getattr(gun_marker_state, 'position', None)
    direction = getattr(gun_marker_state, 'direction', None)
    if collision is None or hit_point is None or direction is None:
        gui_state.hide_all()
        return

    entity = getattr(collision, 'entity', None)
    if entity is None or not isinstance(entity, (VehicleEntity, DestructibleEntity)):
        gui_state.hide_all()
        return

    player = BigWorld.player()
    if player is None:
        gui_state.hide_all()
        return

    try:
        shot = _get_shot(player, gun_marker_state)
        shell = shot.shell
        distance = player.position.flatDistTo(hit_point)
        current_pen = gun_marker_ctrl.computePiercingPowerAtDist(
            shot.piercingPower, distance, shot.maxDistance, 1
        )
        if isinstance(current_pen, (tuple, list)):
            current_pen = current_pen[0]
        current_pen = float(current_pen)
    except Exception:
        gui_state.hide_all()
        return

    armor, ricochet, hit_body, hit_track, hit_gun, angle_cos = _compute_effective_armor(
        hit_point, direction, collision, shell
    )

    angle_cos = max(-1.0, min(1.0, float(angle_cos)))
    hit_angle = int(math.degrees(math.acos(angle_cos)))

    prob = 0
    if not ricochet and hit_body and current_pen > 0.0:
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


def _on_marker_changed(marker_type, gun_marker_state, support_markers_info):
    _compute_and_show(gun_marker_state)


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
