from AvatarInputHandler import gun_marker_ctrl  # type: ignore
from aih_constants import SHOT_RESULT as _SHOT_RESULT  # type: ignore

from mod_armor_pen_calculator import call_update_gui


def my_shot_result_default_current_api(
    cls, gunMarker, collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity
):
    """Armor calculator override adapted to the current WoT shell API."""
    total_armor_val = 0.0
    ricochet = False
    hit_body = False
    hit_track = False
    min_hit_angle_cos = 1

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

    shellExtraData = cls._SHELL_EXTRA_DATA[shell.kind]
    hasPenetrationLoss = getattr(shellExtraData, "hasPenetrationLoss", False)
    if hasPenetrationLoss:
        jetLossPPByDist = getattr(
            shell.type, "piercingPowerLossFactorByDistance", 0.0
        )
    else:
        jetLossPPByDist = 0.0

    for cDetails in collisionsDetails:
        if not isDestructible(entity, cDetails.compName):
            break

        if not hit_track and (cDetails.compName == 0 or cDetails.compName >= 4):
            hit_track = True

        if isJet:
            jetDist = cDetails.dist - jetStartDist
            if jetDist > 0.0:
                lossByDist = 1.0 - jetDist * jetLossPPByDist

                lost_pen = max(0, piercingPower * (1 - lossByDist))
                total_armor_val += lost_pen

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
                if matInfo.extra and piercingPercent <= maxPP:
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

        if piercingPower <= 0.0:
            break

        if hasPenetrationLoss:
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
        min_hit_angle_cos,
        shell.armorDamage,
        entity.health,
    )

    return result


gun_marker_ctrl._CrosshairShotResults._CrosshairShotResults__shotResultDefault = (
    classmethod(my_shot_result_default_current_api)
)
