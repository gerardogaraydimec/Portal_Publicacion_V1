from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class PositionResult:
    dx_mm: float
    dy_mm: float
    radial_offset_mm: float
    diametral_position_error_mm: float
    tolerance_mm: float
    margin_mm: float
    status: str


@dataclass
class MMRResult:
    feature_type: str
    maximum_material_size_mm: float
    actual_size_mm: float
    specified_geom_tol_mm: float
    bonus_tol_mm: float
    available_geom_tol_mm: float
    virtual_condition_mm: float


@dataclass
class RunoutResult:
    readings_mm: list[float]
    tir_mm: float
    min_mm: float
    max_mm: float
    tolerance_mm: float
    status: str


def positional_error_2d(dx_mm: float, dy_mm: float, tolerance_diam_mm: float) -> PositionResult:
    radial = math.hypot(dx_mm, dy_mm)
    diam = 2.0 * radial
    margin = tolerance_diam_mm - diam
    return PositionResult(
        dx_mm=dx_mm,
        dy_mm=dy_mm,
        radial_offset_mm=radial,
        diametral_position_error_mm=diam,
        tolerance_mm=tolerance_diam_mm,
        margin_mm=margin,
        status="Dentro de zona" if margin >= -1e-12 else "Fuera de zona",
    )


def mmr_bonus(
    feature_type: str,
    maximum_material_size_mm: float,
    actual_size_mm: float,
    specified_geom_tol_mm: float,
) -> MMRResult:
    """
    Pedagogical MMR/MMC-style relationship for cylindrical features of size.

    Internal feature (hole): departing from MMS means actual size increases.
      bonus = actual - MMS
      virtual condition ≈ MMS - t

    External feature (shaft): departing from MMS means actual size decreases.
      bonus = MMS - actual
      virtual condition ≈ MMS + t

    This is a simplified teaching model for functional interpretation and
    must not replace the complete ISO 2692 rules.
    """
    ft = feature_type.lower()
    if "agujero" in ft or "intern" in ft:
        bonus = max(0.0, actual_size_mm - maximum_material_size_mm)
        virtual = maximum_material_size_mm - specified_geom_tol_mm
        normalized = "Agujero / elemento interno"
    else:
        bonus = max(0.0, maximum_material_size_mm - actual_size_mm)
        virtual = maximum_material_size_mm + specified_geom_tol_mm
        normalized = "Eje / elemento externo"

    return MMRResult(
        feature_type=normalized,
        maximum_material_size_mm=maximum_material_size_mm,
        actual_size_mm=actual_size_mm,
        specified_geom_tol_mm=specified_geom_tol_mm,
        bonus_tol_mm=bonus,
        available_geom_tol_mm=specified_geom_tol_mm + bonus,
        virtual_condition_mm=virtual,
    )


def runout(readings_mm: list[float], tolerance_mm: float) -> RunoutResult:
    if not readings_mm:
        raise ValueError("Se requiere al menos una lectura.")
    mn = min(readings_mm)
    mx = max(readings_mm)
    tir = mx - mn
    return RunoutResult(
        readings_mm=list(readings_mm),
        tir_mm=tir,
        min_mm=mn,
        max_mm=mx,
        tolerance_mm=tolerance_mm,
        status="Cumple" if tir <= tolerance_mm + 1e-12 else "No cumple",
    )


def parse_series(text: str) -> list[float]:
    raw = text.strip()
    if not raw:
        raise ValueError("Ingresa al menos una lectura.")
    if ";" in raw or "\n" in raw:
        chunks = [c.strip() for c in raw.replace("\n", ";").split(";") if c.strip()]
        return [float(c.replace(",", ".")) for c in chunks]
    return [float(c.strip()) for c in raw.split(",") if c.strip()]


def dof_after_datums(primary: bool, secondary: bool, tertiary: bool) -> dict:
    """
    Pedagogical 3-2-1 restriction count for a prismatic setup.
    """
    constrained = 0
    notes = []
    if primary:
        constrained += 3
        notes.append("Datum primario: restringe 3 grados de libertad.")
    if secondary:
        constrained += 2
        notes.append("Datum secundario: restringe 2 grados adicionales.")
    if tertiary:
        constrained += 1
        notes.append("Datum terciario: restringe el último grado de libertad.")
    constrained = min(constrained, 6)
    return {
        "constrained": constrained,
        "free": 6 - constrained,
        "notes": notes,
    }
