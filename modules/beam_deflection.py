from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from .beam_engine import sample_segments, domain_end
from .resmat_sections import section_data


@dataclass(frozen=True)
class SectionProperties:
    area_mm2: float
    inertia_mm4: float
    radius_gyration_mm: float
    description: str


@dataclass(frozen=True)
class DeflectionResult:
    x_m: np.ndarray
    moment_knm: np.ndarray
    curvature_1_m: np.ndarray
    slope_rad: np.ndarray
    deflection_m: np.ndarray
    max_abs_deflection_m: float
    max_abs_deflection_x_m: float
    max_abs_slope_rad: float
    support_residual_mm: float


def section_properties(section_type: str, params: dict) -> SectionProperties:
    """Return section properties used by the beam solver.

    For I/H and C profiles, bending is taken about the horizontal centroidal z axis.
    """
    data = section_data(section_type, params)
    return SectionProperties(
        data.area_mm2, data.iz_mm4, data.rz_mm,
        f"{data.name} · A={data.area_mm2:.1f} mm² · Iz={data.iz_mm4:.3e} mm⁴"
    )

def _merge_moment_samples(case_id: str, beam_params: dict, n_per_segment: int = 1200):
    """Create a monotonic x-M array, keeping the right-hand value at exact jumps."""
    segs = sample_segments(case_id, beam_params, n_per_segment=n_per_segment)
    xs: list[float] = []
    ms: list[float] = []
    tol = 1e-12

    for seg in segs:
        for x, m in zip(seg["x"], seg["M"]):
            xf = float(x)
            mf = float(m)
            if xs and abs(xf - xs[-1]) <= tol:
                xs[-1] = xf
                ms[-1] = mf
            else:
                xs.append(xf)
                ms.append(mf)

    return np.asarray(xs, dtype=float), np.asarray(ms, dtype=float)


def _cumtrapz(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    out = np.zeros_like(y, dtype=float)
    if len(y) < 2:
        return out
    dx = np.diff(x)
    out[1:] = np.cumsum(0.5 * (y[:-1] + y[1:]) * dx)
    return out


def _support_location(case_id: str, beam_params: dict) -> float:
    # In the overhang case, the second support remains at x=L even though
    # the beam domain extends to L+a.
    return float(beam_params["L"])


def euler_bernoulli_response(
    case_id: str,
    beam_params: dict,
    young_gpa: float,
    inertia_mm4: float,
    n_per_segment: int = 1200,
) -> DeflectionResult:
    """
    Numerically integrate M/EI for the existing beam library.

    Sign convention follows the moment diagram already implemented in beam_engine.
    x is in m, M in kN·m, E in GPa, I in mm^4.
    """
    E = float(young_gpa) * 1e9
    I = float(inertia_mm4) * 1e-12
    if E <= 0 or I <= 0:
        raise ValueError("E e I deben ser mayores que cero.")

    x, m_knm = _merge_moment_samples(case_id, beam_params, n_per_segment=n_per_segment)
    if len(x) < 3:
        raise ValueError("No hay suficientes puntos para integrar la deformación.")

    m_nm = m_knm * 1e3
    curvature = m_nm / (E * I)

    theta0 = _cumtrapz(curvature, x)
    v0 = _cumtrapz(theta0, x)

    # Boundary constants depend on the support family.
    if case_id.startswith("simple_"):
        support_x = _support_location(case_id, beam_params)
        v_at_support = float(np.interp(support_x, x, v0))
        c1 = -v_at_support / support_x
        c2 = 0.0
    else:
        # Cantilevers, propped cantilevers and fixed-fixed cases all have
        # v(0)=0 and theta(0)=0 at the left fixed support.
        c1 = 0.0
        c2 = 0.0

    theta = theta0 + c1
    v = v0 + c1 * x + c2

    idx_v = int(np.argmax(np.abs(v)))
    idx_t = int(np.argmax(np.abs(theta)))

    # Kinematic residual at the relevant right support.
    if case_id.startswith("simple_") or case_id.startswith("propped_"):
        sx = _support_location(case_id, beam_params)
        residual = float(np.interp(sx, x, v)) * 1e3
    elif case_id.startswith("fixed_"):
        residual = max(abs(float(v[-1])) * 1e3, abs(float(theta[-1])) * 1e3)
    else:
        residual = 0.0

    return DeflectionResult(
        x_m=x,
        moment_knm=m_knm,
        curvature_1_m=curvature,
        slope_rad=theta,
        deflection_m=v,
        max_abs_deflection_m=abs(float(v[idx_v])),
        max_abs_deflection_x_m=float(x[idx_v]),
        max_abs_slope_rad=abs(float(theta[idx_t])),
        support_residual_mm=float(residual),
    )


def response_at_x(result: DeflectionResult, x_m: float) -> dict:
    x = float(np.clip(x_m, result.x_m[0], result.x_m[-1]))
    return {
        "x_m": x,
        "moment_knm": float(np.interp(x, result.x_m, result.moment_knm)),
        "curvature_1_m": float(np.interp(x, result.x_m, result.curvature_1_m)),
        "slope_rad": float(np.interp(x, result.x_m, result.slope_rad)),
        "deflection_m": float(np.interp(x, result.x_m, result.deflection_m)),
    }


def classic_reference(case_id: str, beam_params: dict, young_gpa: float, inertia_mm4: float):
    """Closed-form maximum deflection for selected benchmark cases."""
    E = float(young_gpa) * 1e9
    I = float(inertia_mm4) * 1e-12
    L = float(beam_params["L"])

    if case_id == "cantilever_end_load":
        F = float(beam_params["F"]) * 1e3
        return F * L**3 / (3.0 * E * I)
    if case_id == "cantilever_udl":
        w = float(beam_params["w"]) * 1e3
        return w * L**4 / (8.0 * E * I)
    if case_id == "simple_center_load":
        F = float(beam_params["F"]) * 1e3
        return F * L**3 / (48.0 * E * I)
    if case_id == "simple_udl":
        w = float(beam_params["w"]) * 1e3
        return 5.0 * w * L**4 / (384.0 * E * I)
    if case_id == "fixed_center_load":
        F = float(beam_params["F"]) * 1e3
        return F * L**3 / (192.0 * E * I)
    if case_id == "fixed_udl":
        w = float(beam_params["w"]) * 1e3
        return w * L**4 / (384.0 * E * I)
    return None


def slenderness_hint(length_m: float, radius_gyration_mm: float) -> float:
    """Geometric slenderness indicator L/r_g used only as a descriptive aid."""
    return float(length_m) * 1000.0 / float(radius_gyration_mm)
