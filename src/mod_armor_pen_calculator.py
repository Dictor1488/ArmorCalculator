import math
from AvatarInputHandler import gun_marker_ctrl  # type: ignore
from aih_constants import SHOT_RESULT as _SHOT_RESULT  # type: ignore
from PlayerEvents import g_playerEvents  # type: ignore
from AvatarInputHandler import AvatarInputHandler  # type: ignore
from items.components.component_constants import (  # type: ignore
    MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS,
    MODERN_HE_DAMAGE_ABSORPTION_FACTOR,
)

from pade_gui import gui_state


def log(message):
    print("pademinune's Armor Calc: " + str(message))


def get_gaussian_probability(avg_pen, armor_val):
    min_pen = avg_pen * 0.75
    max_pen = avg_pen * 1.25
    if armor_val <= min_pen:
        return 100.0
    if armor_val >= max_pen:
        return 0.0
    standard_deviation = avg_pen / 12
    z = (armor_val - avg_pen) / standard_deviation
    phi = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    return (1.0 - phi) * 100


def shell_has_penetration_loss(cls, shell):
    """Return the penetration-loss flag across supported CrosshairShotResults layouts."""
    shell_extra = cls._SHELL_EXTRA_DATA[shell.kind]
    if hasattr(shell_extra, "hasPenetrationLoss"):
        return bool(shell_extra.hasPenetrationLoss)
    return bool(getattr(shell_extra, "jetLossPPByDist", 0.0))


def get_jet_loss_pp_by_dist(cls, shell):
    """Return HEAT jet penetration loss without changing the game's shot-result semantics."""
    shell_extra = cls._SHELL_EXTRA_DATA[shell.kind]
    if hasattr(shell_extra, "hasPenetrationLoss"):
        if shell_extra.hasPenetrationLoss:
            return getattr(shell.type, "piercingPowerLossFactorByDistance", 0.0)
        return 0.0
    return getattr(shell_extra, "jetLossPPByDist", 0.0)


def call_update_gui(
    avg_pen,
    armor_val,
    ricochet,
    hit_body,
    hit_track,
    hit_gun,
    hit_angle_cos,
    alpha_dmg=(400, 400),
    enemy_hp=0,
):
    # Collision hit-angle cosines should already be in range, but clamping keeps
    # display code from crashing on tiny floating-point overshoots.
    hit_angle_cos = max(-1.0, min(1.0, hit_angle_cos))
    hit_angle = int(math.degrees(math.acos(hit_angle_cos)))

    prob = 0
    kill_roll_prob = 0
    if not ricochet and hit_body:
        prob = get_gaussian_probability(avg_pen, armor_val)
        kill_roll_prob = get_gaussian_probability(alpha_dmg[0], enemy_hp)
    kill_prob = int(prob * kill_roll_prob // 100)
    prob = int(prob)

    gui_state.update_gui(
        armor_val,
        prob,
        ricochet,
        hit_body,
        hit_track,
        hit_gun,
        hit_angle,
        avg_pen,
        kill_prob,
    )


log("Mod is loading")


def my_shot_result_default(
    cls, gunMarker, collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity
):
    """WoT 2.4.0 shot-result logic plus passive data collection for our GUI."""
    total_armor_val = 0.0
    ricochet = False
    hit_body = False
    hit_track = False
    hit_gun = False
    min_hit_angle_cos = 1.0

    isDestructible = cls._CrosshairShotResults__isDestructibleComponent
    collectDebug = cls._CrosshairShotResults__collectDebugPiercingData
    sendDebug = cls._CrosshairShotResults__sendDebugInfo

    result = _SHOT_RESULT.NOT_PIERCED
    isJet = False
    jetStartDist = None
    piercingPower = fullPiercingPower
    dispersion = round(piercingPower) * shell.piercingPowerRandomization
    minPiercingPower = round(round(piercingPower) - dispersion)
    maxPiercingPower = round(round(piercingPower) + dispersion)
    ignoredMaterials = set()
    debugPiercingsList = []

    has_penetration_loss = shell_has_penetration_loss(cls, shell)
    jet_loss_pp_by_dist = get_jet_loss_pp_by_dist(cls, shell)

    for cDetails in collisionsDetails:
        if not isDestructible(entity, cDetails.compName):
            break

        # tankStructure.TankPartIndexes: CHASSIS=0, HULL=1, TURRET=2, GUN=3.
        # Additional collision components can be used for extra track pairs.
        if not hit_track and (cDetails.compName == 0 or cDetails.compName >= 4):
            hit_track = True
        if cDetails.compName == 3:
            hit_gun = True

        # Keep this block equivalent to the current client implementation.
        if isJet:
            jetDist = cDetails.dist - jetStartDist
            if jetDist > 0.0:
                lossByDist = 1.0 - jetDist * jet_loss_pp_by_dist

                # This is display-only bookkeeping. It does not alter the values
                # used by the game's own shot-result calculation below.
                total_armor_val += piercingPower * (1.0 - lossByDist)

                piercingPower *= lossByDist
                minPiercingPower = round(minPiercingPower * lossByDist)
                maxPiercingPower = round(maxPiercingPower * lossByDist)

        if cDetails.matInfo is None:
            result = cls._CRIT_ONLY_SHOT_RESULT
        else:
            matInfo = cDetails.matInfo
            if (cDetails.compName, matInfo.kind) in ignoredMaterials:
                continue
            if matInfo.armor is None:
                result = _SHOT_RESULT.UNDEFINED
                continue

            hitAngleCos = cDetails.hitAngleCos if matInfo.useHitAngle else 1.0
            piercingPercent = 1000.0

            if not isJet and cls._shouldRicochet(shell, hitAngleCos, matInfo):
                ricochet = True
                min_hit_angle_cos = hitAngleCos
                collectDebug(
                    debugPiercingsList,
                    None,
                    hitAngleCos,
                    minPiercingPower,
                    maxPiercingPower,
                    piercingPercent,
                    matInfo,
                    _SHOT_RESULT.NOT_PIERCED,
                )
                break

            # The client only computes penetration armor while penetration power
            # remains. Do the same so our hook cannot change shot-result behavior.
            penetrationArmor = 0
            if piercingPower > 0.0:
                penetrationArmor = cls._computePenetrationArmor(
                    shell, hitAngleCos, matInfo
                )
                total_armor_val += penetrationArmor
                piercingPercent = (
                    100.0
                    + (penetrationArmor - piercingPower) / fullPiercingPower * 100.0
                )
                piercingPower -= penetrationArmor
                minPiercingPower = round(minPiercingPower - penetrationArmor)
                maxPiercingPower = round(maxPiercingPower - penetrationArmor)

            if matInfo.vehicleDamageFactor:
                hit_body = True
                min_hit_angle_cos = hitAngleCos
                if minPP < piercingPercent < maxPP:
                    result = _SHOT_RESULT.LITTLE_PIERCED
                elif piercingPercent <= minPP:
                    result = _SHOT_RESULT.GREAT_PIERCED
                collectDebug(
                    debugPiercingsList,
                    penetrationArmor,
                    hitAngleCos,
                    minPiercingPower,
                    maxPiercingPower,
                    piercingPercent,
                    matInfo,
                    result,
                )
                break
            else:
                debugResult = _SHOT_RESULT.NOT_PIERCED
                if minPP < piercingPercent < maxPP:
                    debugResult = _SHOT_RESULT.LITTLE_PIERCED
                elif piercingPercent <= minPP:
                    debugResult = _SHOT_RESULT.GREAT_PIERCED
                if matInfo.extra:
                    if piercingPercent <= maxPP:
                        result = cls._CRIT_ONLY_SHOT_RESULT
                collectDebug(
                    debugPiercingsList,
                    penetrationArmor,
                    hitAngleCos,
                    minPiercingPower,
                    maxPiercingPower,
                    piercingPercent,
                    matInfo,
                    debugResult,
                )

            if matInfo.collideOnceOnly:
                ignoredMaterials.add((cDetails.compName, matInfo.kind))

        # This break exists in WoT 2.4.0.5429 and is important for parity on
        # multi-layer/spaced armor.
        if piercingPower <= 0.0:
            break

        if has_penetration_loss:
            isJet = True
            mInfo = cDetails.matInfo
            armor = mInfo.armor if mInfo is not None else 0.0
            jetStartDist = cDetails.dist + armor * 0.001

    sendDebug(gunMarker, debugPiercingsList, minPP, maxPP, fullPiercingPower)
    call_update_gui(
        fullPiercingPower,
        total_armor_val,
        ricochet,
        hit_body,
        hit_track,
        hit_gun,
        min_hit_angle_cos,
        shell.armorDamage,
        entity.health,
    )
    return result


def my_shot_result_modern_he(
    cls, gunMarker, collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity
):
    """WoT 2.4.0 modern-HE shot-result logic plus passive GUI data collection."""
    total_armor_val = 0.0
    hit_body = False
    hit_track = False
    hit_gun = False
    min_hit_angle_cos = 1.0

    isDestructible = cls._CrosshairShotResults__isDestructibleComponent
    collectDebug = cls._CrosshairShotResults__collectDebugPiercingData
    sendDebug = cls._CrosshairShotResults__sendDebugInfo

    result = _SHOT_RESULT.NOT_PIERCED
    ignoredMaterials = set()
    piercingPower = fullPiercingPower
    dispersion = round(piercingPower) * shell.piercingPowerRandomization
    minPiercingPower = round(round(piercingPower) - dispersion)
    maxPiercingPower = round(round(piercingPower) + dispersion)
    explosionDamageAbsorption = 0
    debugPiercingsList = []

    for cDetails in collisionsDetails:
        if not isDestructible(entity, cDetails.compName):
            call_update_gui(
                fullPiercingPower,
                total_armor_val,
                False,
                hit_body,
                hit_track,
                hit_gun,
                min_hit_angle_cos,
                shell.armorDamage,
                entity.health,
            )
            return result

        if not hit_track and (cDetails.compName == 0 or cDetails.compName >= 4):
            hit_track = True
        if cDetails.compName == 3:
            hit_gun = True

        matInfo = cDetails.matInfo
        if (
            matInfo is not None
            and (cDetails.compName, matInfo.kind) not in ignoredMaterials
        ):
            hitAngleCos = cDetails.hitAngleCos if matInfo.useHitAngle else 1.0
            piercingPercent = 1000.0
            penetrationArmor = 0

            if fullPiercingPower > 0.0:
                penetrationArmor = cls._computePenetrationArmor(
                    shell, hitAngleCos, matInfo
                )
                piercingPercent = (
                    100.0
                    + (penetrationArmor - piercingPower) / fullPiercingPower * 100.0
                )

            if matInfo.vehicleDamageFactor:
                hit_body = True
                min_hit_angle_cos = hitAngleCos
                total_armor_val += penetrationArmor
                piercingPower -= penetrationArmor
                minPiercingPower = round(minPiercingPower - penetrationArmor)
                maxPiercingPower = round(maxPiercingPower - penetrationArmor)
                if piercingPercent <= minPP and explosionDamageAbsorption == 0:
                    result = _SHOT_RESULT.GREAT_PIERCED
                else:
                    result = _SHOT_RESULT.LITTLE_PIERCED
                collectDebug(
                    debugPiercingsList,
                    penetrationArmor,
                    hitAngleCos,
                    minPiercingPower,
                    maxPiercingPower,
                    piercingPercent,
                    matInfo,
                    result,
                )
                sendDebug(
                    gunMarker,
                    debugPiercingsList,
                    minPP,
                    maxPP,
                    fullPiercingPower,
                )
                call_update_gui(
                    fullPiercingPower,
                    total_armor_val,
                    False,
                    hit_body,
                    hit_track,
                    hit_gun,
                    min_hit_angle_cos,
                    shell.armorDamage,
                    entity.health,
                )
                return result

            if shell.type.shieldPenetration:
                shieldPenetration = (
                    penetrationArmor
                    * MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS
                )
                total_armor_val += shieldPenetration
                piercingPower -= shieldPenetration
                minPiercingPower = round(minPiercingPower - shieldPenetration)
                maxPiercingPower = round(maxPiercingPower - shieldPenetration)
                explosionDamageAbsorption += (
                    penetrationArmor * MODERN_HE_DAMAGE_ABSORPTION_FACTOR
                )

            if (
                piercingPercent > maxPP
                or not shell.type.shieldPenetration
                or explosionDamageAbsorption >= shell.type.maxDamage
            ):
                collectDebug(
                    debugPiercingsList,
                    penetrationArmor,
                    hitAngleCos,
                    minPiercingPower,
                    maxPiercingPower,
                    piercingPercent,
                    matInfo,
                    _SHOT_RESULT.NOT_PIERCED,
                )
                sendDebug(
                    gunMarker,
                    debugPiercingsList,
                    minPP,
                    maxPP,
                    fullPiercingPower,
                )
                call_update_gui(
                    fullPiercingPower,
                    total_armor_val,
                    False,
                    hit_body,
                    hit_track,
                    hit_gun,
                    min_hit_angle_cos,
                    shell.armorDamage,
                    entity.health,
                )
                return _SHOT_RESULT.NOT_PIERCED

            if matInfo.extra and piercingPercent <= maxPP:
                collectDebug(
                    debugPiercingsList,
                    penetrationArmor,
                    hitAngleCos,
                    minPiercingPower,
                    maxPiercingPower,
                    piercingPercent,
                    matInfo,
                    cls._CRIT_ONLY_SHOT_RESULT,
                )
                result = cls._CRIT_ONLY_SHOT_RESULT

            if matInfo.collideOnceOnly:
                ignoredMaterials.add((cDetails.compName, matInfo.kind))

    sendDebug(gunMarker, debugPiercingsList, minPP, maxPP, fullPiercingPower)
    call_update_gui(
        fullPiercingPower,
        total_armor_val,
        False,
        hit_body,
        hit_track,
        hit_gun,
        min_hit_angle_cos,
        shell.armorDamage,
        entity.health,
    )
    return result


original_getShotResult = gun_marker_ctrl._CrosshairShotResults.getShotResult.__func__


def my_get_shot_result(cls, gunMarker, excludeTeam=0, piercingMultiplier=1):
    result = original_getShotResult(cls, gunMarker, excludeTeam, piercingMultiplier)
    if result == _SHOT_RESULT.UNDEFINED and gui_state.is_visible():
        gui_state.hide_all()
    return result


def on_load_match():
    gui_state.hide_all()


def on_leave_match():
    gui_state.hide_all()


original_activate_postmortem = AvatarInputHandler.activatePostmortem


def my_activate_postmortem(self, *args, **kwargs):
    original_activate_postmortem(self, *args, **kwargs)
    gui_state.hide_all()


gun_marker_ctrl._CrosshairShotResults.getShotResult = classmethod(my_get_shot_result)
gun_marker_ctrl._CrosshairShotResults._CrosshairShotResults__shotResultDefault = (
    classmethod(my_shot_result_default)
)
gun_marker_ctrl._CrosshairShotResults._CrosshairShotResults__shotResultModernHE = (
    classmethod(my_shot_result_modern_he)
)
g_playerEvents.onAvatarBecomePlayer += on_load_match
g_playerEvents.onAvatarBecomeNonPlayer += on_leave_match
AvatarInputHandler.activatePostmortem = my_activate_postmortem

log("Mod has finished loading")