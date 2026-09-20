from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from modules.fluid_real_engine import solve_losses

G = 9.80665


@dataclass
class PumpCurve:
    H0_m: float
    Qbep_m3s: float
    Hbep_m: float
    Qend_m3s: float
    Hend_m: float
    eta_max: float
    coeffs: tuple[float, float, float]


@dataclass
class OperatingPoint:
    found: bool
    message: str
    Q_m3s: float | None
    H_m: float | None
    system_head_m: float | None
    pump_head_m: float | None
    eta: float | None
    hydraulic_power_kW: float | None
    shaft_power_kW: float | None
    pump_each_flow_m3s: float | None
    bep_ratio: float | None


def fit_pump_curve(H0_m: float, Qbep_Ls: float, Hbep_m: float, Qend_Ls: float, Hend_m: float, eta_max: float) -> PumpCurve:
    qb = Qbep_Ls / 1000.0
    qe = Qend_Ls / 1000.0
    if qb <= 0 or qe <= qb:
        raise ValueError("Se requiere Q_BEP > 0 y Q_end > Q_BEP.")
    if H0_m <= 0 or Hbep_m < 0 or Hend_m < 0:
        raise ValueError("Las alturas de la bomba deben ser no negativas y H0 positiva.")
    if not (0 < eta_max <= 1):
        raise ValueError("La eficiencia máxima debe estar entre 0 y 1.")

    q = np.array([0.0, qb, qe], dtype=float)
    h = np.array([H0_m, Hbep_m, Hend_m], dtype=float)
    coeffs = tuple(np.polyfit(q, h, 2))
    return PumpCurve(H0_m, qb, Hbep_m, qe, Hend_m, eta_max, coeffs)


def base_pump_head(curve: PumpCurve, Q_m3s: float) -> float:
    a, b, c = curve.coeffs
    H = a * Q_m3s**2 + b * Q_m3s + c
    return max(0.0, float(H))


def base_efficiency(curve: PumpCurve, Q_m3s: float) -> float:
    if Q_m3s <= 0 or curve.Qbep_m3s <= 0:
        return 0.0

    # Pedagogical smooth efficiency curve centered at BEP.
    width = 0.90 * curve.Qbep_m3s
    ratio = (Q_m3s - curve.Qbep_m3s) / max(width, 1e-12)
    eta = curve.eta_max * (1.0 - ratio**2)
    return max(0.05, min(curve.eta_max, eta))


def single_pump_head(curve: PumpCurve, Q_m3s: float, speed_ratio: float = 1.0) -> float:
    if speed_ratio <= 0:
        return 0.0
    q_equiv = Q_m3s / speed_ratio
    return (speed_ratio**2) * base_pump_head(curve, q_equiv)


def single_pump_efficiency(curve: PumpCurve, Q_m3s: float, speed_ratio: float = 1.0) -> float:
    if speed_ratio <= 0:
        return 0.0
    q_equiv = Q_m3s / speed_ratio
    return base_efficiency(curve, q_equiv)


def pump_group_head(
    curve: PumpCurve,
    Q_total_m3s: float,
    speed_ratio: float = 1.0,
    arrangement: str = "1 bomba",
    pump_count: int = 1,
) -> float:
    pump_count = max(1, int(pump_count))

    if arrangement == "Serie":
        return pump_count * single_pump_head(curve, Q_total_m3s, speed_ratio)
    if arrangement == "Paralelo":
        return single_pump_head(curve, Q_total_m3s / pump_count, speed_ratio)
    return single_pump_head(curve, Q_total_m3s, speed_ratio)


def pump_group_efficiency_and_each_flow(
    curve: PumpCurve,
    Q_total_m3s: float,
    speed_ratio: float = 1.0,
    arrangement: str = "1 bomba",
    pump_count: int = 1,
) -> tuple[float, float]:
    pump_count = max(1, int(pump_count))
    if arrangement == "Paralelo":
        q_each = Q_total_m3s / pump_count
    else:
        q_each = Q_total_m3s
    eta = single_pump_efficiency(curve, q_each, speed_ratio)
    return eta, q_each


def static_head(rho: float, z1_m: float, z2_m: float, p1_kPa_g: float, p2_kPa_g: float) -> float:
    return (z2_m - z1_m) + ((p2_kPa_g - p1_kPa_g) * 1000.0) / (rho * G)


def system_head(
    Q_m3s: float,
    rho: float,
    mu: float,
    L_m: float,
    D_mm: float,
    epsilon_mm: float,
    K_total: float,
    z1_m: float,
    z2_m: float,
    p1_kPa_g: float,
    p2_kPa_g: float,
) -> tuple[float, float, float, float]:
    hs = static_head(rho, z1_m, z2_m, p1_kPa_g, p2_kPa_g)

    losses = solve_losses(
        rho=rho,
        mu=mu,
        L_m=L_m,
        D_mm=D_mm,
        Q_Ls=Q_m3s * 1000.0,
        epsilon_mm=epsilon_mm,
        K_total=K_total,
    )
    if not losses.ok:
        raise ValueError(losses.message)

    h_total = hs + losses.hL_total_m
    return h_total, hs, losses.hf_major_m, losses.hm_minor_m


def find_operating_point(
    curve: PumpCurve,
    rho: float,
    mu: float,
    L_m: float,
    D_mm: float,
    epsilon_mm: float,
    K_total: float,
    z1_m: float,
    z2_m: float,
    p1_kPa_g: float,
    p2_kPa_g: float,
    speed_ratio: float = 1.0,
    arrangement: str = "1 bomba",
    pump_count: int = 1,
    q_scan_max_factor: float = 1.75,
) -> OperatingPoint:
    if speed_ratio <= 0:
        return OperatingPoint(False, "La razón de velocidad debe ser positiva.", None, None, None, None, None, None, None, None, None)

    q_base_limit = curve.Qend_m3s * speed_ratio
    if arrangement == "Paralelo":
        q_max = q_base_limit * max(1, pump_count) * q_scan_max_factor
    else:
        q_max = q_base_limit * q_scan_max_factor

    q_vals = np.linspace(0.0, max(q_max, 1e-6), 900)

    def diff(q):
        hp = pump_group_head(curve, q, speed_ratio, arrangement, pump_count)
        hs, *_ = system_head(q, rho, mu, L_m, D_mm, epsilon_mm, K_total, z1_m, z2_m, p1_kPa_g, p2_kPa_g)
        return hp - hs

    diffs = []
    for q in q_vals:
        try:
            diffs.append(diff(float(q)))
        except Exception:
            diffs.append(math.nan)

    root_bracket = None
    for i in range(len(q_vals) - 1):
        d1, d2 = diffs[i], diffs[i + 1]
        if not math.isfinite(d1) or not math.isfinite(d2):
            continue
        if d1 == 0:
            root_bracket = (q_vals[i], q_vals[i])
            break
        if d1 * d2 < 0:
            root_bracket = (q_vals[i], q_vals[i + 1])
            break

    if root_bracket is None:
        return OperatingPoint(
            False,
            "No se encontró intersección entre la curva de la bomba y la curva del sistema dentro del rango explorado.",
            None, None, None, None, None, None, None, None, None
        )

    qa, qb = root_bracket
    if qa == qb:
        q_op = float(qa)
    else:
        fa = diff(float(qa))
        for _ in range(80):
            qm = 0.5 * (qa + qb)
            fm = diff(float(qm))
            if abs(fm) < 1e-10:
                qa = qb = qm
                break
            if fa * fm <= 0:
                qb = qm
            else:
                qa = qm
                fa = fm
        q_op = float(0.5 * (qa + qb))

    hp = pump_group_head(curve, q_op, speed_ratio, arrangement, pump_count)
    hs, *_ = system_head(q_op, rho, mu, L_m, D_mm, epsilon_mm, K_total, z1_m, z2_m, p1_kPa_g, p2_kPa_g)
    eta, q_each = pump_group_efficiency_and_each_flow(curve, q_op, speed_ratio, arrangement, pump_count)

    ph_kw = rho * G * q_op * hp / 1000.0
    shaft_kw = ph_kw / eta if eta > 0 else math.inf
    qbep_scaled = curve.Qbep_m3s * speed_ratio
    bep_ratio = q_each / qbep_scaled if qbep_scaled > 0 else math.nan

    return OperatingPoint(
        True,
        "OK",
        q_op,
        hp,
        hs,
        hp,
        eta,
        ph_kw,
        shaft_kw,
        q_each,
        bep_ratio,
    )


def affinity_scaled_values(Q1: float, H1: float, P1: float, N2_over_N1: float) -> tuple[float, float, float]:
    s = N2_over_N1
    return Q1 * s, H1 * s**2, P1 * s**3


def npsh_available(
    rho: float,
    p_surface_abs_kPa: float,
    pv_abs_kPa: float,
    z_surface_minus_pump_m: float,
    hL_suction_m: float,
) -> float:
    return (
        (p_surface_abs_kPa * 1000.0) / (rho * G)
        + z_surface_minus_pump_m
        - hL_suction_m
        - (pv_abs_kPa * 1000.0) / (rho * G)
    )
