from __future__ import annotations

import math
from dataclasses import dataclass

G = 9.80665


@dataclass
class LossResult:
    ok: bool
    message: str
    rho: float
    mu: float
    nu: float
    L_m: float
    D_m: float
    Q_m3s: float
    A_m2: float
    V_ms: float
    Re: float
    regime: str
    epsilon_m: float
    rel_roughness: float
    f: float | None
    f_method: str
    f_haaland: float | None
    f_swamee_jain: float | None
    hf_major_m: float | None
    K_total: float
    hm_minor_m: float | None
    hL_total_m: float | None
    dp_major_Pa: float | None
    dp_minor_Pa: float | None
    dp_total_Pa: float | None
    velocity_head_m: float
    transition_warning: bool


def area(D_m: float) -> float:
    return math.pi * D_m**2 / 4.0


def reynolds(rho: float, V: float, D: float, mu: float) -> float:
    return rho * V * D / mu


def regime_from_re(Re: float) -> str:
    if Re < 2300:
        return "Laminar"
    if Re < 4000:
        return "Transición"
    return "Turbulento"


def friction_laminar(Re: float) -> float:
    return 64.0 / Re


def friction_haaland(Re: float, rel_roughness: float) -> float:
    if Re <= 0:
        return math.nan
    term = (rel_roughness / 3.7) ** 1.11 + 6.9 / Re
    return 1.0 / (-1.8 * math.log10(term)) ** 2


def friction_swamee_jain(Re: float, rel_roughness: float) -> float:
    if Re <= 0:
        return math.nan
    return 0.25 / (math.log10(rel_roughness / 3.7 + 5.74 / (Re ** 0.9))) ** 2


def friction_colebrook(Re: float, rel_roughness: float, tol: float = 1e-10, max_iter: int = 100) -> float:
    """Darcy friction factor from Colebrook-White for turbulent flow."""
    f = friction_haaland(Re, rel_roughness)
    for _ in range(max_iter):
        rhs = -2.0 * math.log10(rel_roughness / 3.7 + 2.51 / (Re * math.sqrt(f)))
        f_new = 1.0 / (rhs * rhs)
        if abs(f_new - f) < tol:
            return f_new
        f = f_new
    return f


def transitional_reference(Re: float, rel_roughness: float) -> float:
    """Pedagogical interpolation only; transition does not have one unique design f."""
    f_2300 = friction_laminar(2300.0)
    f_4000 = friction_colebrook(4000.0, rel_roughness)
    t = (Re - 2300.0) / (4000.0 - 2300.0)
    return (1 - t) * f_2300 + t * f_4000


def solve_losses(
    rho: float,
    mu: float,
    L_m: float,
    D_mm: float,
    Q_Ls: float,
    epsilon_mm: float,
    K_total: float,
) -> LossResult:
    if rho <= 0 or mu <= 0 or L_m < 0 or D_mm <= 0 or Q_Ls < 0 or epsilon_mm < 0 or K_total < 0:
        return LossResult(
            False, "Revisa los datos: densidad, viscosidad y diámetro deben ser positivos; las demás magnitudes no pueden ser negativas.",
            rho, mu, math.nan, L_m, math.nan, math.nan, math.nan, math.nan, math.nan, "",
            math.nan, math.nan, None, "", None, None, None, K_total, None, None, None, None, None, math.nan, False
        )

    D = D_mm / 1000.0
    Q = Q_Ls / 1000.0
    A = area(D)
    V = Q / A if A > 0 else 0.0
    nu = mu / rho
    Re = reynolds(rho, V, D, mu) if mu > 0 else math.inf
    regime = regime_from_re(Re)
    epsilon = epsilon_mm / 1000.0
    rel_roughness = epsilon / D
    velocity_head = V**2 / (2 * G)

    if Q == 0 or Re == 0:
        f = None
        f_method = "Sin flujo"
        fh = fsj = None
        hf = hm = hL = 0.0
        dp_major = dp_minor = dp_total = 0.0
        transition_warning = False
    else:
        fh = friction_haaland(Re, rel_roughness) if Re >= 2300 else None
        fsj = friction_swamee_jain(Re, rel_roughness) if Re >= 2300 else None

        if regime == "Laminar":
            f = friction_laminar(Re)
            f_method = "Laminar · 64/Re"
            transition_warning = False
        elif regime == "Turbulento":
            f = friction_colebrook(Re, rel_roughness)
            f_method = "Colebrook–White"
            transition_warning = False
        else:
            f = transitional_reference(Re, rel_roughness)
            f_method = "Estimación pedagógica en transición"
            transition_warning = True

        hf = f * (L_m / D) * velocity_head
        hm = K_total * velocity_head
        hL = hf + hm
        dp_major = rho * G * hf
        dp_minor = rho * G * hm
        dp_total = rho * G * hL

    return LossResult(
        True, "OK",
        rho, mu, nu, L_m, D, Q, A, V, Re, regime,
        epsilon, rel_roughness, f, f_method, fh, fsj,
        hf, K_total, hm, hL, dp_major, dp_minor, dp_total,
        velocity_head, transition_warning
    )


def equivalent_length(K: float, D_m: float, f: float | None) -> float | None:
    if f is None or f <= 0:
        return None
    return K * D_m / f
