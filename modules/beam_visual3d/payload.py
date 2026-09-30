from __future__ import annotations

import math
from typing import Any
import numpy as np


def _downsample(x: np.ndarray, *ys: np.ndarray, max_points: int = 180):
    x = np.asarray(x, dtype=float)
    if len(x) <= max_points:
        idx = np.arange(len(x))
    else:
        idx = np.unique(np.linspace(0, len(x) - 1, max_points).round().astype(int))
    return [arr[idx] for arr in (x, *[np.asarray(y, dtype=float) for y in ys])]


def _supports(case_id: str, p: dict) -> list[dict[str, Any]]:
    L = float(p["L"])
    if case_id.startswith("cantilever_"):
        return [{"x": 0.0, "kind": "fixed", "label": "A"}]
    if case_id.startswith("propped_"):
        return [
            {"x": 0.0, "kind": "fixed", "label": "A"},
            {"x": L, "kind": "roller", "label": "B"},
        ]
    if case_id.startswith("fixed_"):
        return [
            {"x": 0.0, "kind": "fixed", "label": "A"},
            {"x": L, "kind": "fixed", "label": "B"},
        ]
    return [
        {"x": 0.0, "kind": "pin", "label": "A"},
        {"x": L, "kind": "roller", "label": "B"},
    ]


def _loads(case_id: str, p: dict) -> list[dict[str, Any]]:
    L = float(p["L"])
    out: list[dict[str, Any]] = []

    if "udl" in case_id:
        out.append({"kind": "udl", "x0": 0.0, "x1": L, "value": float(p["w"]), "label": "w"})
        return out

    if case_id == "cantilever_end_load":
        out.append({"kind": "point", "x": L, "value": float(p["F"]), "label": "F"})
    elif case_id in {"cantilever_point_load", "simple_point_load", "propped_point_load", "fixed_point_load"}:
        out.append({"kind": "point", "x": float(p["a"]), "value": float(p["F"]), "label": "F"})
    elif case_id in {"simple_center_load", "propped_center_load", "fixed_center_load"}:
        out.append({"kind": "point", "x": L / 2.0, "value": float(p["F"]), "label": "F"})
    elif case_id == "simple_twin_loads":
        a = float(p["a"])
        out.extend([
            {"kind": "point", "x": a, "value": float(p["F"]), "label": "F"},
            {"kind": "point", "x": L - a, "value": float(p["F"]), "label": "F"},
        ])
    elif case_id == "simple_overhang_load":
        out.append({"kind": "point", "x": L + float(p["a"]), "value": float(p["F"]), "label": "F"})
    elif case_id in {"cantilever_end_moment"}:
        out.append({"kind": "moment", "x": L, "value": float(p["M0"]), "label": "M₀"})
    elif case_id == "simple_point_moment":
        out.append({"kind": "moment", "x": float(p["a"]), "value": float(p["M0"]), "label": "M₀"})

    return out


def _section_payload(section_type: str, section_params: dict) -> dict[str, Any]:
    if section_type == "Rectangular":
        return {
            "kind": "rect",
            "b": float(section_params["b_mm"]),
            "h": float(section_params["h_mm"]),
            "label": "Rectangular",
        }
    if section_type == "Circular maciza":
        return {"kind": "solid_circle", "d": float(section_params["d_mm"]), "label": "Circular maciza"}
    if section_type == "Tubular circular":
        return {
            "kind": "tube",
            "do": float(section_params["do_mm"]),
            "t": float(section_params["t_mm"]),
            "label": "Tubular circular",
        }
    return {
        "kind": "custom",
        "c": float(section_params.get("c_mm", 100.0)),
        "label": "Propiedades ingresadas",
    }


def build_beam_visual_payload(
    *,
    case_id: str,
    p: dict,
    case_title: str,
    deflection_result,
    x_probe: float,
    state: dict,
    section_type: str,
    section_params: dict,
    stress_result,
    young_gpa: float,
    inertia_mm4: float,
) -> dict[str, Any]:
    x, v, m = _downsample(
        deflection_result.x_m,
        deflection_result.deflection_m,
        deflection_result.moment_knm,
    )
    max_v = float(np.max(np.abs(v))) if len(v) else 0.0
    Lvis = max(float(x[-1] - x[0]), 1e-9)
    auto_amp = 1.0 if max_v < 1e-12 else min(max(0.11 * Lvis / max_v, 1.0), 5000.0)

    sy, ss, st = _downsample(
        stress_result.y_mm,
        stress_result.sigma_mpa,
        stress_result.tau_mpa if stress_result.tau_mpa is not None else np.zeros_like(stress_result.y_mm),
        max_points=100,
    )

    v_right = state.get("V_right")
    m_right = state.get("M_right")
    shear = float(v_right if v_right is not None else state.get("V", 0.0))
    moment = float(m_right if m_right is not None else state.get("M", 0.0))

    return {
        "case_id": case_id,
        "title": case_title,
        "length": float(x[-1]) if len(x) else float(p["L"]),
        "x": [round(float(z), 8) for z in x],
        "deflection": [float(z) for z in v],
        "moment": [float(z) for z in m],
        "x_probe": float(x_probe),
        "probe": {"V": shear, "M": moment},
        "supports": _supports(case_id, p),
        "loads": _loads(case_id, p),
        "section": _section_payload(section_type, section_params),
        "stress": {
            "y_mm": [float(z) for z in sy],
            "sigma_mpa": [float(z) for z in ss],
            "tau_mpa": [float(z) for z in st],
            "sigma_max": float(stress_result.sigma_max_abs_mpa),
            "tau_max": None if stress_result.tau_max_abs_mpa is None else float(stress_result.tau_max_abs_mpa),
        },
        "E_gpa": float(young_gpa),
        "I_mm4": float(inertia_mm4),
        "auto_amplification": float(auto_amp),
        "max_deflection_mm": float(deflection_result.max_abs_deflection_m * 1000.0),
        "max_deflection_x": float(deflection_result.max_abs_deflection_x_m),
    }
