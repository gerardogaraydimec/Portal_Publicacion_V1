from __future__ import annotations

import math
from dataclasses import dataclass

G = 9.80665


@dataclass
class FluidResult:
    ok: bool
    message: str
    D1_m: float
    D2_m: float
    A1_m2: float
    A2_m2: float
    Q_m3s: float | None
    V1_ms: float | None
    V2_ms: float | None
    p1_Pa: float | None
    p2_Pa: float | None
    z1_m: float
    z2_m: float
    pressure_head_1_m: float | None
    pressure_head_2_m: float | None
    velocity_head_1_m: float | None
    velocity_head_2_m: float | None
    HGL1_m: float | None
    HGL2_m: float | None
    EGL1_m: float | None
    EGL2_m: float | None


def area_from_diameter(D_m: float) -> float:
    return math.pi * D_m**2 / 4.0


def solve_ideal_bernoulli(
    rho: float,
    D1_mm: float,
    D2_mm: float,
    z1_m: float,
    z2_m: float,
    p1_kPa: float,
    p2_kPa: float,
    Q_Ls: float,
    unknown: str,
) -> FluidResult:
    if rho <= 0:
        return FluidResult(False, "La densidad debe ser positiva.", 0,0,0,0,None,None,None,None,None,z1_m,z2_m,None,None,None,None,None,None,None,None)
    if D1_mm <= 0 or D2_mm <= 0:
        return FluidResult(False, "Los diámetros deben ser positivos.", 0,0,0,0,None,None,None,None,None,z1_m,z2_m,None,None,None,None,None,None,None,None)

    D1 = D1_mm / 1000.0
    D2 = D2_mm / 1000.0
    A1 = area_from_diameter(D1)
    A2 = area_from_diameter(D2)
    p1 = p1_kPa * 1000.0
    p2 = p2_kPa * 1000.0

    if unknown == "Q":
        coeff = (1.0 / A2**2) - (1.0 / A1**2)
        head_available = (p1 - p2) / (rho * G) + (z1_m - z2_m)

        if abs(coeff) < 1e-14:
            return FluidResult(
                False,
                "Con áreas iguales, Bernoulli no permite determinar Q a partir de estas dos presiones: la altura de velocidad se cancela.",
                D1,D2,A1,A2,None,None,None,p1,p2,z1_m,z2_m,None,None,None,None,None,None,None,None
            )

        q2 = 2.0 * G * head_available / coeff
        if q2 < 0:
            return FluidResult(
                False,
                "Los datos no producen un caudal real positivo en la dirección 1 → 2 bajo el modelo ideal. Revisa presiones, cotas o diámetros.",
                D1,D2,A1,A2,None,None,None,p1,p2,z1_m,z2_m,None,None,None,None,None,None,None,None
            )
        Q = math.sqrt(q2)
    else:
        Q = Q_Ls / 1000.0
        if Q < 0:
            return FluidResult(
                False,
                "Esta versión considera Q positivo en la dirección 1 → 2.",
                D1,D2,A1,A2,None,None,None,p1,p2,z1_m,z2_m,None,None,None,None,None,None,None,None
            )

    V1 = Q / A1
    V2 = Q / A2

    if unknown == "p₂":
        H1 = p1/(rho*G) + V1**2/(2*G) + z1_m
        p2 = rho*G*(H1 - V2**2/(2*G) - z2_m)
    elif unknown == "p₁":
        H2 = p2/(rho*G) + V2**2/(2*G) + z2_m
        p1 = rho*G*(H2 - V1**2/(2*G) - z1_m)
    elif unknown != "Q":
        return FluidResult(
            False, "Incógnita no reconocida.",
            D1,D2,A1,A2,None,None,None,p1,p2,z1_m,z2_m,None,None,None,None,None,None,None,None
        )

    ph1 = p1/(rho*G)
    ph2 = p2/(rho*G)
    vh1 = V1**2/(2*G)
    vh2 = V2**2/(2*G)
    hgl1 = z1_m + ph1
    hgl2 = z2_m + ph2
    egl1 = hgl1 + vh1
    egl2 = hgl2 + vh2

    return FluidResult(
        True, "OK",
        D1,D2,A1,A2,Q,V1,V2,p1,p2,z1_m,z2_m,
        ph1,ph2,vh1,vh2,hgl1,hgl2,egl1,egl2
    )


def mass_flow_rate(rho: float, Q_m3s: float) -> float:
    return rho * Q_m3s


def pump_power(rho: float, Q_m3s: float, head_m: float, efficiency: float) -> tuple[float, float]:
    """Returns hydraulic and shaft power in kW."""
    hydraulic = rho * G * Q_m3s * head_m / 1000.0
    if efficiency <= 0:
        return hydraulic, math.inf
    shaft = hydraulic / efficiency
    return hydraulic, shaft
