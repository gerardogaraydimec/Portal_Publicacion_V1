from __future__ import annotations

import math
import statistics
from dataclasses import dataclass


@dataclass
class RepeatabilityResult:
    n: int
    mean_mm: float
    stdev_mm: float
    uA_mean_mm: float
    range_mm: float


@dataclass
class BudgetItem:
    name: str
    source_type: str
    standard_u_um: float
    sensitivity: float
    contribution_um: float
    note: str


@dataclass
class UncertaintyResult:
    corrected_value_mm: float
    correction_cal_um: float
    correction_temp_um: float
    uA_um: float
    u_resolution_um: float
    u_calibration_um: float
    u_temperature_um: float
    u_method_um: float
    u_operator_um: float
    uc_um: float
    k: float
    U_um: float
    items: list[BudgetItem]


@dataclass
class DecisionResult:
    status: str
    message: str
    lower_result_mm: float
    upper_result_mm: float
    acceptance_lsl_mm: float
    acceptance_usl_mm: float
    guard_band_um: float


def parse_readings(text: str) -> list[float]:
    """
    Recommended separator: semicolon or line break.
    Decimal point or decimal comma are accepted when semicolon/newline delimiters are used.
    If only commas are present, commas are interpreted as separators.
    """
    raw = text.strip()
    if not raw:
        raise ValueError("Ingresa al menos una lectura.")

    if ";" in raw or "\n" in raw:
        normalized = raw.replace("\n", ";")
        chunks = [c.strip() for c in normalized.split(";") if c.strip()]
        values = [float(c.replace(" ", "").replace(",", ".")) for c in chunks]
    else:
        chunks = [c.strip() for c in raw.split(",") if c.strip()]
        values = [float(c.replace(" ", "")) for c in chunks]

    if not values:
        raise ValueError("Ingresa al menos una lectura.")
    return values


def repeatability(readings_mm: list[float]) -> RepeatabilityResult:
    n = len(readings_mm)
    mean = statistics.fmean(readings_mm)
    if n >= 2:
        s = statistics.stdev(readings_mm)
        uA = s / math.sqrt(n)
    else:
        s = 0.0
        uA = 0.0
    return RepeatabilityResult(
        n=n,
        mean_mm=mean,
        stdev_mm=s,
        uA_mean_mm=uA,
        range_mm=max(readings_mm)-min(readings_mm),
    )


def resolution_standard_uncertainty(resolution_mm: float) -> float:
    """
    Quantization interval r -> rounding error assumed rectangular within ±r/2.
    Returns standard uncertainty in mm.
    """
    if resolution_mm <= 0:
        return 0.0
    return resolution_mm / (2.0 * math.sqrt(3.0))


def expanded_to_standard(U_um: float, k: float) -> float:
    if k <= 0:
        raise ValueError("El factor de cobertura debe ser positivo.")
    return U_um / k


def thermal_correction_um(
    indicated_mm: float,
    alpha_per_C: float,
    temp_C: float,
    reference_C: float = 20.0,
) -> float:
    """
    Correct a measured length at T to standard reference temperature.
    Exact linear-expansion inversion:
    L_ref = L_T / (1 + alpha*(T-Tref))
    correction = L_ref - L_T
    """
    denominator = 1.0 + alpha_per_C * (temp_C-reference_C)
    if denominator <= 0:
        raise ValueError("Condición térmica no válida.")
    L_ref = indicated_mm / denominator
    return (L_ref-indicated_mm) * 1000.0


def thermal_standard_uncertainty_um(
    nominal_mm: float,
    alpha_per_C: float,
    temp_u_C: float,
) -> float:
    """
    First-order contribution from temperature uncertainty:
    u_L ≈ |alpha * L * u_T|
    """
    return abs(alpha_per_C * nominal_mm * temp_u_C * 1000.0)


def build_uncertainty_budget(
    readings_mm: list[float],
    resolution_mm: float,
    cal_correction_um: float,
    cal_U_um: float,
    cal_k: float,
    nominal_mm: float,
    temp_C: float,
    temp_u_C: float,
    alpha_per_C: float,
    method_u_um: float,
    operator_u_um: float,
    coverage_k: float = 2.0,
    reference_C: float = 20.0,
) -> UncertaintyResult:
    rep = repeatability(readings_mm)

    uA_um = rep.uA_mean_mm * 1000.0
    u_res_um = resolution_standard_uncertainty(resolution_mm) * 1000.0
    u_cal_um = expanded_to_standard(cal_U_um, cal_k)
    c_temp_um = thermal_correction_um(rep.mean_mm, alpha_per_C, temp_C, reference_C)
    u_temp_um = thermal_standard_uncertainty_um(nominal_mm, alpha_per_C, temp_u_C)

    corrected = rep.mean_mm + cal_correction_um/1000.0 + c_temp_um/1000.0

    items = [
        BudgetItem(
            "Repetibilidad del promedio",
            "Tipo A",
            uA_um,
            1.0,
            uA_um,
            r"u_A=s/\sqrt{n}",
        ),
        BudgetItem(
            "Resolución",
            "Tipo B",
            u_res_um,
            1.0,
            u_res_um,
            r"u_r=r/(2\sqrt{3})",
        ),
        BudgetItem(
            "Calibración",
            "Tipo B",
            u_cal_um,
            1.0,
            u_cal_um,
            r"u_{cal}=U_{cal}/k_{cal}",
        ),
        BudgetItem(
            "Temperatura",
            "Tipo B",
            u_temp_um,
            1.0,
            u_temp_um,
            r"u_T\approx |\alpha D\,u(T)|",
        ),
        BudgetItem(
            "Método / alineación / contacto",
            "Tipo B",
            max(0.0, method_u_um),
            1.0,
            max(0.0, method_u_um),
            "Contribución estándar ingresada",
        ),
        BudgetItem(
            "Operador / lectura",
            "Tipo B",
            max(0.0, operator_u_um),
            1.0,
            max(0.0, operator_u_um),
            "Contribución estándar ingresada",
        ),
    ]

    uc = math.sqrt(sum(item.contribution_um**2 for item in items))
    U = coverage_k * uc

    return UncertaintyResult(
        corrected_value_mm=corrected,
        correction_cal_um=cal_correction_um,
        correction_temp_um=c_temp_um,
        uA_um=uA_um,
        u_resolution_um=u_res_um,
        u_calibration_um=u_cal_um,
        u_temperature_um=u_temp_um,
        u_method_um=max(0.0, method_u_um),
        u_operator_um=max(0.0, operator_u_um),
        uc_um=uc,
        k=coverage_k,
        U_um=U,
        items=items,
    )


def decision_interval_rule(
    measured_mm: float,
    U_um: float,
    lsl_mm: float,
    usl_mm: float,
) -> DecisionResult:
    if usl_mm <= lsl_mm:
        raise ValueError("USL debe ser mayor que LSL.")

    U_mm = U_um / 1000.0
    low = measured_mm-U_mm
    high = measured_mm+U_mm

    if low >= lsl_mm and high <= usl_mm:
        status = "Conformidad demostrada"
        message = "El intervalo expandido completo queda dentro de la zona de especificación."
    elif high < lsl_mm or low > usl_mm:
        status = "No conformidad demostrada"
        message = "El intervalo expandido completo queda fuera de la zona de especificación."
    else:
        status = "Zona de decisión"
        message = "El intervalo expandido intersecta al menos un límite de especificación."

    return DecisionResult(
        status=status,
        message=message,
        lower_result_mm=low,
        upper_result_mm=high,
        acceptance_lsl_mm=lsl_mm,
        acceptance_usl_mm=usl_mm,
        guard_band_um=0.0,
    )


def decision_guard_band(
    measured_mm: float,
    U_um: float,
    lsl_mm: float,
    usl_mm: float,
    guard_band_um: float,
) -> DecisionResult:
    if usl_mm <= lsl_mm:
        raise ValueError("USL debe ser mayor que LSL.")

    g_mm = max(0.0, guard_band_um)/1000.0
    acc_lsl = lsl_mm + g_mm
    acc_usl = usl_mm - g_mm

    if acc_lsl > acc_usl:
        status = "Regla inviable"
        message = "La banda de guarda consume toda la tolerancia."
    elif acc_lsl <= measured_mm <= acc_usl:
        status = "Aceptado por regla configurada"
        message = "El valor medido está dentro de la zona de aceptación reducida."
    else:
        status = "Fuera de zona de aceptación"
        message = "El valor medido no está dentro de la zona de aceptación definida por la banda de guarda."

    U_mm = U_um/1000.0
    return DecisionResult(
        status=status,
        message=message,
        lower_result_mm=measured_mm-U_mm,
        upper_result_mm=measured_mm+U_mm,
        acceptance_lsl_mm=acc_lsl,
        acceptance_usl_mm=acc_usl,
        guard_band_um=max(0.0, guard_band_um),
    )


def tolerance_uncertainty_ratio(lsl_mm: float, usl_mm: float, U_um: float) -> float | None:
    if usl_mm <= lsl_mm or U_um <= 0:
        return None
    tolerance_um = (usl_mm-lsl_mm)*1000.0
    return tolerance_um/U_um


def max_uncertainty_for_target_ratio(lsl_mm: float, usl_mm: float, target_ratio: float) -> float | None:
    if usl_mm <= lsl_mm or target_ratio <= 0:
        return None
    return (usl_mm-lsl_mm)*1000.0/target_ratio


def resolution_ratio(lsl_mm: float, usl_mm: float, resolution_mm: float) -> float | None:
    if usl_mm <= lsl_mm or resolution_mm <= 0:
        return None
    return (usl_mm-lsl_mm)/resolution_mm


def uncertainty_percentages(items: list[BudgetItem]) -> list[dict]:
    total_variance = sum(i.contribution_um**2 for i in items)
    rows = []
    for item in items:
        pct = 0.0 if total_variance <= 0 else 100.0*(item.contribution_um**2)/total_variance
        rows.append({
            "Fuente": item.name,
            "Tipo": item.source_type,
            "Incertidumbre estándar [µm]": item.standard_u_um,
            "Contribución [µm]": item.contribution_um,
            "Varianza [%]": pct,
            "Modelo": item.note,
        })
    return rows


@dataclass
class GeometryErrorResult:
    cosine_error_um: float
    abbe_error_um: float
    force_deformation_um: float
    combined_geometry_um: float


def cosine_error_um(length_mm: float, angle_deg: float) -> float:
    """
    Difference between true length and projected length for an angular misalignment.
    Delta = L - L*cos(theta)
    """
    theta = math.radians(angle_deg)
    return abs(length_mm * (1.0 - math.cos(theta)) * 1000.0)


def abbe_error_um(offset_mm: float, angle_deg: float) -> float:
    """
    First-order Abbe error magnitude: e ≈ h*tan(theta)
    """
    theta = math.radians(angle_deg)
    return abs(offset_mm * math.tan(theta) * 1000.0)


def geometry_error_model(
    length_mm: float,
    cosine_angle_deg: float,
    abbe_offset_mm: float,
    abbe_angle_deg: float,
    force_deformation_um: float,
) -> GeometryErrorResult:
    c = cosine_error_um(length_mm, cosine_angle_deg)
    a = abbe_error_um(abbe_offset_mm, abbe_angle_deg)
    f = max(0.0, force_deformation_um)
    combined = math.sqrt(c**2 + a**2 + f**2)
    return GeometryErrorResult(
        cosine_error_um=c,
        abbe_error_um=a,
        force_deformation_um=f,
        combined_geometry_um=combined,
    )


def combine_with_custom_items(
    base: UncertaintyResult,
    custom_rows: list[dict],
) -> UncertaintyResult:
    """
    Adds user-defined standard uncertainty sources to an existing budget.
    Each row may contain:
      name, standard_u_um, sensitivity, source_type, note
    """
    extra_items = []
    for idx, row in enumerate(custom_rows):
        name = str(row.get("name", "")).strip()
        if not name:
            continue

        try:
            u = float(row.get("standard_u_um", 0.0) or 0.0)
        except (TypeError, ValueError):
            u = 0.0
        try:
            c = float(row.get("sensitivity", 1.0) or 1.0)
        except (TypeError, ValueError):
            c = 1.0

        if not math.isfinite(u):
            u = 0.0
        if not math.isfinite(c):
            c = 1.0

        source_type = str(row.get("source_type", "Tipo B") or "Tipo B")
        note = str(row.get("note", "Fuente personalizada") or "Fuente personalizada")

        u = max(0.0, u)
        contribution = abs(c) * u

        extra_items.append(
            BudgetItem(
                name=name,
                source_type=source_type,
                standard_u_um=u,
                sensitivity=c,
                contribution_um=contribution,
                note=note,
            )
        )

    items = list(base.items) + extra_items
    uc = math.sqrt(sum(item.contribution_um**2 for item in items))
    U = base.k * uc

    return UncertaintyResult(
        corrected_value_mm=base.corrected_value_mm,
        correction_cal_um=base.correction_cal_um,
        correction_temp_um=base.correction_temp_um,
        uA_um=base.uA_um,
        u_resolution_um=base.u_resolution_um,
        u_calibration_um=base.u_calibration_um,
        u_temperature_um=base.u_temperature_um,
        u_method_um=base.u_method_um,
        u_operator_um=base.u_operator_um,
        uc_um=uc,
        k=base.k,
        U_um=U,
        items=items,
    )


def result_summary_text(
    characteristic: str,
    lsl_mm: float,
    usl_mm: float,
    result_mm: float,
    U_um: float,
    k: float,
    decision: str,
    instrument: str,
    temperature_C: float,
    operator: str,
    calibration_ref: str,
) -> str:
    return (
        f"Característica: {characteristic}\n"
        f"Especificación: {lsl_mm:.3f} a {usl_mm:.3f} mm\n"
        f"Resultado: {result_mm:.3f} mm ± {U_um:.0f} µm (k={k:.1f})\n"
        f"Decisión: {decision}\n"
        f"Equipo: {instrument}\n"
        f"Temperatura: {temperature_C:.1f} °C\n"
        f"Operador: {operator}\n"
        f"Calibración: {calibration_ref}"
    )
