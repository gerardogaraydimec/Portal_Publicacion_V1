from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

G = 9.80665


@dataclass(frozen=True)
class ReynoldsResult:
    area_m2: float
    velocity_ms: float
    reynolds: float
    regime: str
    regime_key: str
    relative_roughness: float
    friction_factor: float
    friction_method: str
    velocity_head_m: float
    major_loss_m: float
    minor_loss_m: float
    total_loss_m: float
    pressure_drop_pa: float
    wall_shear_pa: float
    hydraulic_power_w: float


FLUID_PRESETS = {
    "Agua · 20 °C": (998.2, 1.002e-3),
    "Aire · 20 °C": (1.204, 1.825e-5),
}

ROUGHNESS_PRESETS_MM = {
    "Tubo muy liso / PVC": 0.0015,
    "Acero comercial": 0.045,
    "Hierro fundido": 0.26,
}


def classify_regime(reynolds: float) -> tuple[str, str]:
    if reynolds < 2300.0:
        return "Laminar", "laminar"
    if reynolds < 4000.0:
        return "Transición", "transition"
    return "Turbulento", "turbulent"


def churchill_friction_factor(re: float, rel_roughness: float) -> float:
    """Darcy friction factor. Smooth across laminar/transition/turbulent regimes."""
    re = max(float(re), 1e-9)
    rr = max(float(rel_roughness), 0.0)
    if re < 1e-6:
        return math.inf
    if re < 20.0:
        return 64.0 / re
    term = (7.0 / re) ** 0.9 + 0.27 * rr
    term = max(term, 1e-15)
    A = (2.457 * math.log(1.0 / term)) ** 16
    B = (37530.0 / re) ** 16
    return 8.0 * ((8.0 / re) ** 12 + 1.0 / (A + B) ** 1.5) ** (1.0 / 12.0)


def colebrook_friction_factor(re: float, rel_roughness: float) -> float:
    """Darcy friction factor for turbulent flow using Haaland seed + fixed-point Colebrook."""
    re = max(float(re), 1.0)
    rr = max(float(rel_roughness), 0.0)
    seed_den = -1.8 * math.log10((rr / 3.7) ** 1.11 + 6.9 / re)
    f = 1.0 / max(seed_den * seed_den, 1e-12)
    for _ in range(25):
        rhs = -2.0 * math.log10(rr / 3.7 + 2.51 / (re * math.sqrt(max(f, 1e-12))))
        new_f = 1.0 / max(rhs * rhs, 1e-12)
        if abs(new_f - f) < 1e-10:
            return new_f
        f = new_f
    return f


def friction_factor(re: float, rel_roughness: float) -> tuple[float, str]:
    if re <= 0:
        return 0.0, "Sin flujo"
    if re < 2300.0:
        return 64.0 / re, "Laminar: f = 64/Re"
    if re < 4000.0:
        return churchill_friction_factor(re, rel_roughness), "Transición: correlación continua de Churchill (aproximación)"
    return colebrook_friction_factor(re, rel_roughness), "Turbulento: ecuación de Colebrook-White"


def solve_reynolds_losses(
    *,
    rho_kgm3: float,
    mu_pas: float,
    diameter_m: float,
    length_m: float,
    roughness_m: float,
    minor_k: float,
    flow_rate_m3s: float | None = None,
    velocity_ms: float | None = None,
) -> ReynoldsResult:
    if rho_kgm3 <= 0 or mu_pas <= 0:
        raise ValueError("ρ y μ deben ser mayores que cero.")
    if diameter_m <= 0 or length_m <= 0:
        raise ValueError("D y L deben ser mayores que cero.")
    if roughness_m < 0 or minor_k < 0:
        raise ValueError("ε y K no pueden ser negativos.")

    area = math.pi * diameter_m**2 / 4.0
    if velocity_ms is None:
        if flow_rate_m3s is None or flow_rate_m3s < 0:
            raise ValueError("Debe especificarse un caudal no negativo.")
        velocity = flow_rate_m3s / area
    else:
        if velocity_ms < 0:
            raise ValueError("La velocidad no puede ser negativa.")
        velocity = velocity_ms
        flow_rate_m3s = velocity * area

    re = rho_kgm3 * velocity * diameter_m / mu_pas
    regime, regime_key = classify_regime(re)
    rr = roughness_m / diameter_m
    f, method = friction_factor(re, rr)
    vh = velocity**2 / (2.0 * G)
    major = 0.0 if velocity == 0 else f * (length_m / diameter_m) * vh
    minor = minor_k * vh
    total = major + minor
    dp = rho_kgm3 * G * total
    tauw = 0.0 if velocity == 0 else f * rho_kgm3 * velocity**2 / 8.0
    hydraulic_power = dp * float(flow_rate_m3s or 0.0)

    return ReynoldsResult(
        area_m2=area,
        velocity_ms=velocity,
        reynolds=re,
        regime=regime,
        regime_key=regime_key,
        relative_roughness=rr,
        friction_factor=f,
        friction_method=method,
        velocity_head_m=vh,
        major_loss_m=major,
        minor_loss_m=minor,
        total_loss_m=total,
        pressure_drop_pa=dp,
        wall_shear_pa=tauw,
        hydraulic_power_w=hydraulic_power,
    )


def normalized_velocity_profile(re: float, regime_key: str, points: int = 121) -> tuple[np.ndarray, np.ndarray, str]:
    """Returns r/R and u/Umean for a pedagogical fully-developed profile."""
    rr = np.linspace(-1.0, 1.0, points)
    ar = np.abs(rr)
    lam = 2.0 * (1.0 - rr**2)

    n = 7.0
    umax_over_mean = ((n + 1.0) * (2.0 * n + 1.0)) / (2.0 * n**2)
    turb = umax_over_mean * np.maximum(1.0 - ar, 0.0) ** (1.0 / n)

    if regime_key == "laminar":
        return rr, lam, "Perfil parabólico completamente desarrollado: u/U = 2[1-(r/R)²]."
    if regime_key == "turbulent":
        return rr, turb, "Perfil turbulento didáctico mediante ley de potencia 1/7; no sustituye una correlación de capa límite específica."
    blend = max(0.0, min(1.0, (re - 2300.0) / 1700.0))
    prof = (1.0 - blend) * lam + blend * turb
    return rr, prof, "Zona de transición: visualización interpolada entre perfiles laminar y turbulento; el comportamiento real depende de perturbaciones y condiciones de entrada."


def energy_profile(
    result: ReynoldsResult,
    length_m: float,
    minor_location_ratio: float = 0.70,
    points: int = 180,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Relative energy lines. Inlet EGL = 0. Minor loss represented as a step at a user-defined schematic location."""
    x = np.linspace(0.0, length_m, points)
    ratio = max(0.0, min(1.0, minor_location_ratio))
    xm = ratio * length_m
    distributed = result.major_loss_m * x / max(length_m, 1e-12)
    step = np.where(x >= xm, result.minor_loss_m, 0.0)
    cumulative_loss = distributed + step
    egl = -cumulative_loss
    hgl = egl - result.velocity_head_m
    return x, cumulative_loss, egl, hgl


def moody_curves(relative_roughness_values: list[float] | None = None) -> dict[float, tuple[np.ndarray, np.ndarray]]:
    if relative_roughness_values is None:
        relative_roughness_values = [0.0, 1e-4, 5e-4, 1e-3, 5e-3, 1e-2]
    re = np.logspace(math.log10(500.0), math.log10(1e7), 280)
    out: dict[float, tuple[np.ndarray, np.ndarray]] = {}
    for rr in relative_roughness_values:
        ff = np.array([friction_factor(float(v), rr)[0] for v in re])
        out[rr] = (re, ff)
    return out
