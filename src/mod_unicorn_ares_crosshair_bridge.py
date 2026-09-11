# -*- coding: utf-8 -*-
import math

import BigWorld
import constants
from AvatarInputHandler import gun_marker_ctrl  # type: ignore
from DestructibleEntity import DestructibleEntity  # type: ignore
from Vehicle import Vehicle as VehicleEntity  # type: ignore
from PlayerEvents import g_playerEvents  # type: ignore
from helpers import dependency
from items.components.component_constants import (  # type: ignore
    MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS,
    MODERN_HE_DAMAGE_ABSORPTION_FACTOR,
)
from skeletons.gui.battle_session import IBattleSessionProvider  # type: ignore

from unicorn_ares_gui import gui_state


_SESSION = dependency.instance(IBattleSessionProvider)
_RESOLVER = gun_marker_ctrl.createShotResultResolver()
_SUBSCRIBED = False
_RETRY = None


def _gaussian_probability(avg_value, target_value):
    try:
        avg_value = float(avg_value)
        target_value = float(target_value)
    except Exception:
        return 0.0
    if avg_value <= 0.0:
        return 0.0
    min_value = avg_value * 0.75
    max_value = avg_value * 1.25
    if target_value <= min_value:
        return 100.0
    if target_value >= max_value:
        return 0.0
    sigma = avg_value / 12.0
    z = (target_value - avg_value) / sigma
    phi = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    return (1.0 - phi) * 100.0


def _shell_has_penetration_loss(shell):
    try:
        extra = _RESOLVER._SHELL_EXTRA_DATA[shell.kind]
        if hasattr(extra, 'hasPenetrationLoss'):
            return bool(extra.hasPenetrationLoss)
        return bool(getattr(extra, 'jetLossPPByDist', 0.0))
    except Exception:
        return False


def _get_jet_loss(shell):
    try:
        extra = _RESOLVER._SHELL_EXTRA_DATA[shell.kind]
        if hasattr(extra, 'hasPenetrationLoss'):
            if not extra.hasPenetrationLoss:
                return 0.0
            return float(getattr(shell.type, 'piercingPowerLossFactorByDistance', 0.0))
        return float(getattr(extra, 'jetLossPPByDist', 0.0))
    except Exception:
        return 0.0


def _is_modern_he(shell):
    try:
        return (shell.kind == constants.SHELL_TYPES.HIGH_EXPLOSIVE and
                shell.type.mechanics == constants.SHELL_MECHANICS_TYPE.MODERN)
    except Exception:
        return False


def _collision_flags(item, hit_track, hit_gun):
    if not hit_track and (item.compName == 0 or item.compName >= 4):
        hit_track = True
    if item.compName == 3:
        hit_gun = True
    return hit_track, hit_gun


def _compute_default_armor(hit_point, direction, entity, shell, full_pen):
    try:
        details = _RESOLVER._getAllCollisionDetails(hit_point, direction, entity)
    except Exception:
        details = None
    if not details:
        return (0.0, False, False, False, False, 1.0)

    total_armor = 0.0
    ignored = set()
    ricochet = False
    hit_body = False
    hit_track = False
    hit_gun = False
    hit_angle_cos = 1.0

    piercing_power = max(0.0, float(full_pen))
    is_jet = False
    jet_start = None
    has_penetration_loss = _shell_has_penetration_loss(shell)
    jet_loss_by_dist = _get_jet_loss(shell)

    for item in details:
        try:
            if not _RESOLVER._CrosshairShotResults__isDestructibleComponent(entity, item.compName):
                # Match the native resolver: once the trace leaves a destructible
                # component, collisions after it are not part of this armor path.
                break
        except Exception:
            break

        hit_track, hit_gun = _collision_flags(item, hit_track, hit_gun)

        if is_jet and jet_start is not None and jet_loss_by_dist > 0.0:
            try:
                jet_dist = float(item.dist) - float(jet_start)
            except Exception:
                jet_dist = 0.0
            if jet_dist > 0.0 and piercing_power > 0.0:
                loss_by_dist = max(0.0, 1.0 - jet_dist * jet_loss_by_dist)
                lost_penetration = piercing_power * (1.0 - loss_by_dist)
                # Express HEAT air loss as equivalent consumed penetration, in mm.
                # The previous bridge incorrectly added only distance*factor to armor.
                total_armor += max(0.0, lost_penetration)
                piercing_power *= loss_by_dist

        material = item.matInfo
        if material is None or material.armor is None:
            continue

        key = (item.compName, material.kind)
        if key in ignored:
            continue

        angle_cos = item.hitAngleCos if material.useHitAngle else 1.0

        try:
            this_ricochet = (not is_jet and
                             bool(_RESOLVER._shouldRicochet(shell, angle_cos, material)))
        except Exception:
            this_ricochet = False

        if this_ricochet:
            ricochet = True
            hit_angle_cos = angle_cos
            try:
                if piercing_power > 0.0:
                    total_armor += _RESOLVER._computePenetrationArmor(shell, angle_cos, material)
            except Exception:
                pass
            break

        penetration_armor = 0.0
        if piercing_power > 0.0:
            try:
                penetration_armor = float(_RESOLVER._computePenetrationArmor(shell, angle_cos, material))
            except Exception:
                penetration_armor = 0.0
            total_armor += penetration_armor
            piercing_power -= penetration_armor

        if material.vehicleDamageFactor:
            hit_body = True
            hit_angle_cos = angle_cos
            break

        if material.collideOnceOnly:
            ignored.add(key)

        if piercing_power <= 0.0:
            break

        if has_penetration_loss:
            is_jet = True
            try:
                jet_start = float(item.dist) + float(material.armor) * 0.001
            except Exception:
                jet_start = None

    return (float(total_armor), ricochet, hit_body, hit_track, hit_gun, hit_angle_cos)


def _compute_modern_he_armor(hit_point, direction, entity, shell, full_pen):
    try:
        details = _RESOLVER._getAllCollisionDetails(hit_point, direction, entity)
    except Exception:
        details = None
    if not details:
        return (0.0, False, False, False, False, 1.0)

    total_armor = 0.0
    ignored = set()
    hit_body = False
    hit_track = False
    hit_gun = False
    hit_angle_cos = 1.0
    piercing_power = max(0.0, float(full_pen))
    explosion_absorption = 0.0

    try:
        _min_pp, max_pp = _RESOLVER._computePiercingPowerRandomization(shell)
    except Exception:
        max_pp = 100.0

    for item in details:
        try:
            if not _RESOLVER._CrosshairShotResults__isDestructibleComponent(entity, item.compName):
                break
        except Exception:
            break

        hit_track, hit_gun = _collision_flags(item, hit_track, hit_gun)
        material = item.matInfo
        if material is None or material.armor is None:
            continue

        key = (item.compName, material.kind)
        if key in ignored:
            continue

        angle_cos = item.hitAngleCos if material.useHitAngle else 1.0
        try:
            penetration_armor = float(_RESOLVER._computePenetrationArmor(shell, angle_cos, material)) if full_pen > 0.0 else 0.0
        except Exception:
            penetration_armor = 0.0

        piercing_percent = 1000.0
        if full_pen > 0.0:
            piercing_percent = 100.0 + (penetration_armor - piercing_power) / float(full_pen) * 100.0

        if material.vehicleDamageFactor:
            total_armor += penetration_armor
            hit_body = True
            hit_angle_cos = angle_cos
            break

        if getattr(shell.type, 'shieldPenetration', False):
            shield_penetration = penetration_armor * MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS
            total_armor += shield_penetration
            piercing_power -= shield_penetration
            explosion_absorption += penetration_armor * MODERN_HE_DAMAGE_ABSORPTION_FACTOR

        if (piercing_percent > max_pp or
                not getattr(shell.type, 'shieldPenetration', False) or
                explosion_absorption >= getattr(shell.type, 'maxDamage', 0.0)):
            break

        if material.collideOnceOnly:
            ignored.add(key)

    return (float(total_armor), False, hit_body, hit_track, hit_gun, hit_angle_cos)


def _compute_effective_armor(hit_point, direction, collision, shell, full_pen):
    if collision is None:
        return (0.0, False, False, False, False, 1.0)
    entity = collision.entity
    if _is_modern_he(shell):
        return _compute_modern_he_armor(hit_point, direction, entity, shell, full_pen)
    return _compute_default_armor(hit_point, direction, entity, shell, full_pen)


def _get_shot(player, gun_marker_state):
    v_desc = player.getVehicleDescriptor()
    try:
        slot = v_desc.gunInstallations[gun_marker_state.gunInstallationIndex]
        if slot.isMainInstallation():
            return v_desc.shot
        return slot.gun.shots[0]
    except Exception:
        return v_desc.shot


def _distance_to_hit(player, hit_point):
    try:
        return (hit_point - player.getOwnVehiclePosition()).length
    except Exception:
        try:
            return player.position.flatDistTo(hit_point)
        except Exception:
            return 0.0


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

    try:
        if getattr(entity, 'health', 1) <= 0:
            gui_state.hide_all()
            return
    except Exception:
        pass

    player = BigWorld.player()
    if player is None:
        gui_state.hide_all()
        return

    try:
        shot = _get_shot(player, gun_marker_state)
        shell = shot.shell
        distance = _distance_to_hit(player, hit_point)
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
        hit_point, direction, collision, shell, current_pen
    )

    angle_cos = max(-1.0, min(1.0, float(angle_cos)))
    hit_angle = int(math.degrees(math.acos(angle_cos)))

    prob = 0
    if not ricochet and hit_body and current_pen > 0.0:
        prob = int(_gaussian_probability(current_pen, armor))

    kill_prob = 0
    if prob > 0 and hit_body:
        try:
            alpha_damage = shell.armorDamage
            if isinstance(alpha_damage, (tuple, list)):
                alpha_damage = alpha_damage[0]
            enemy_hp = float(getattr(entity, 'health', 0.0))
            kill_roll_prob = _gaussian_probability(alpha_damage, enemy_hp)
            kill_prob = int(prob * kill_roll_prob // 100)
        except Exception:
            kill_prob = 0

    gui_state.update_gui(
        armor,
        prob,
        ricochet,
        hit_body,
        hit_track,
        hit_gun,
        hit_angle,
        current_pen,
        kill_prob,
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


def _on_avatar_ready(*args, **kwargs):
    _subscribe()


def _on_avatar_non_player(*args, **kwargs):
    _unsubscribe()
    gui_state.hide_all()


# Subscribe only after the avatar is fully ready. This mirrors the current
# battle lifecycle used by other stable GameFace mods and avoids early retries
# while the battle controllers are still being rebuilt.
g_playerEvents.onAvatarReady += _on_avatar_ready
g_playerEvents.onAvatarBecomeNonPlayer += _on_avatar_non_player
