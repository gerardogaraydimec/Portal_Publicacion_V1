from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class SectionStressResult:
    y_mm: np.ndarray
    sigma_mpa: np.ndarray
    tau_mpa: np.ndarray | None
    shear_flow_n_per_mm: np.ndarray | None
    width_mm: np.ndarray | None
    sigma_top_mpa: float
    sigma_bottom_mpa: float
    sigma_max_abs_mpa: float
    tau_max_abs_mpa: float | None
    tau_max_y_mm: float | None
    q_max_abs_n_per_mm: float | None
    c_mm: float
    shear_available: bool
    note: str


def extreme_fiber_distance_mm(section_type: str, params: dict) -> float:
    if section_type == "Rectangular":
        return float(params["h_mm"]) / 2.0
    if section_type == "Circular maciza":
        return float(params["d_mm"]) / 2.0
    if section_type == "Tubular circular":
        return float(params["do_mm"]) / 2.0
    if section_type == "Propiedades ingresadas":
        c = float(params.get("c_mm", 0.0))
        if c <= 0:
            raise ValueError("Para propiedades ingresadas, c debe ser mayor que cero.")
        return c
    raise KeyError(section_type)


def _section_width_mm(section_type: str, params: dict, y: np.ndarray) -> np.ndarray | None:
    y = np.asarray(y, dtype=float)

    if section_type == "Rectangular":
        b = float(params["b_mm"])
        h = float(params["h_mm"])
        return np.where(np.abs(y) <= h / 2.0 + 1e-12, b, 0.0)

    if section_type == "Circular maciza":
        r = float(params["d_mm"]) / 2.0
        inside = np.maximum(r * r - y * y, 0.0)
        return 2.0 * np.sqrt(inside)

    if section_type == "Tubular circular":
        ro = float(params["do_mm"]) / 2.0
        t = float(params["t_mm"])
        ri = ro - t
        outer = np.sqrt(np.maximum(ro * ro - y * y, 0.0))
        inner = np.sqrt(np.maximum(ri * ri - y * y, 0.0))
        return 2.0 * np.maximum(outer - inner, 0.0)

    if section_type == "Propiedades ingresadas":
        return None

    raise KeyError(section_type)


def _first_moment_from_top(y: np.ndarray, width: np.ndarray) -> np.ndarray:
    """Numerically evaluate Q(y)=int_y^c eta*t(eta)deta [mm^3]."""
    y = np.asarray(y, dtype=float)
    width = np.asarray(width, dtype=float)
    integrand = y * width
    q = np.zeros_like(y)
    for i in range(len(y) - 2, -1, -1):
        dy = y[i + 1] - y[i]
        q[i] = q[i + 1] + 0.5 * (integrand[i + 1] + integrand[i]) * dy
    return q


def section_stress_response(
    section_type: str,
    params: dict,
    inertia_mm4: float,
    moment_knm: float,
    shear_kn: float,
    n: int = 801,
) -> SectionStressResult:
    """
    Normal stress follows sigma_x=-M*y/I.
    Shear stress follows tau_xy=VQ/(I*t) for the supported solid/annular shapes.

    Units:
      M [kN*m] -> N*mm using 1e6
      V [kN]   -> N using 1e3
      I [mm^4]
      sigma,tau [N/mm^2 = MPa]
      q=tau*t [N/mm]
    """
    I = float(inertia_mm4)
    if I <= 0:
        raise ValueError("I debe ser mayor que cero.")

    c = extreme_fiber_distance_mm(section_type, params)
    y = np.linspace(-c, c, int(max(101, n)), dtype=float)

    M_nmm = float(moment_knm) * 1e6
    sigma = -(M_nmm / I) * y

    width = _section_width_mm(section_type, params, y)
    tau = None
    q_flow = None
    tau_max = None
    tau_y = None
    q_max = None

    if width is not None:
        Q = _first_moment_from_top(y, width)
        tau = np.zeros_like(y)
        mask = width > max(1e-9, 1e-8 * float(np.max(width)))
        V_n = float(shear_kn) * 1e3
        tau[mask] = V_n * Q[mask] / (I * width[mask])
        tau[~mask] = 0.0
        q_flow = tau * width

        idx_tau = int(np.argmax(np.abs(tau)))
        tau_max = abs(float(tau[idx_tau]))
        tau_y = float(y[idx_tau])
        q_max = abs(float(q_flow[int(np.argmax(np.abs(q_flow)))]))
        shear_available = True
        note = (
            "La distribución de corte se calcula con τ=VQ/(It). "
            "En los bordes libres Q tiende a cero; en secciones simétricas el máximo suele aparecer cerca del eje neutro."
        )
    else:
        shear_available = False
        note = (
            "Con A, I y c ingresados se puede evaluar flexión normal, pero no τ=VQ/(It) sin conocer la geometría local t(y) y Q(y)."
        )

    return SectionStressResult(
        y_mm=y,
        sigma_mpa=sigma,
        tau_mpa=tau,
        shear_flow_n_per_mm=q_flow,
        width_mm=width,
        sigma_top_mpa=float(sigma[-1]),
        sigma_bottom_mpa=float(sigma[0]),
        sigma_max_abs_mpa=abs(float(sigma[int(np.argmax(np.abs(sigma)))])),
        tau_max_abs_mpa=tau_max,
        tau_max_y_mm=tau_y,
        q_max_abs_n_per_mm=q_max,
        c_mm=c,
        shear_available=shear_available,
        note=note,
    )
