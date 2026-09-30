from __future__ import annotations

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
    elif case_id == "cantilever_end_moment":
        out.append({"kind": "moment", "x": L, "value": float(p["M0"]), "label": "M₀"})
    elif case_id == "simple_point_moment":
        out.append({"kind": "moment", "x": float(p["a"]), "value": float(p["M0"]), "label": "M₀"})

    return out


def _section_payload(section_type: str, section_params: dict, length_m: float) -> dict[str, Any]:
    """
    Store the real section dimensions and a *uniform* display scale.
    The display scale is used only to keep slender beams visible in 3D; it
    preserves section proportions and never changes stress/deflection values.
    """
    L = max(float(length_m), 1e-9)

    if section_type == "Rectangular":
        b_m = float(section_params["b_mm"]) / 1000.0
        h_m = float(section_params["h_mm"]) / 1000.0
        max_dim = max(b_m, h_m, 1e-12)
        visual_scale = max(1.0, min(30.0, 0.045 * L / max_dim))
        return {
            "kind": "rect",
            "b_mm": float(section_params["b_mm"]),
            "h_mm": float(section_params["h_mm"]),
            "b_m": b_m,
            "h_m": h_m,
            "visual_scale": visual_scale,
            "geometry_known": True,
            "label": "Rectangular",
        }

    if section_type == "Circular maciza":
        d_m = float(section_params["d_mm"]) / 1000.0
        visual_scale = max(1.0, min(30.0, 0.045 * L / max(d_m, 1e-12)))
        return {
            "kind": "solid_circle",
            "d_mm": float(section_params["d_mm"]),
            "d_m": d_m,
            "visual_scale": visual_scale,
            "geometry_known": True,
            "label": "Circular maciza",
        }

    if section_type == "Tubular circular":
        do_m = float(section_params["do_mm"]) / 1000.0
        t_m = float(section_params["t_mm"]) / 1000.0
        di_m = max(do_m - 2.0 * t_m, 0.0)
        visual_scale = max(1.0, min(30.0, 0.045 * L / max(do_m, 1e-12)))
        return {
            "kind": "tube",
            "do_mm": float(section_params["do_mm"]),
            "t_mm": float(section_params["t_mm"]),
            "do_m": do_m,
            "di_m": di_m,
            "t_m": t_m,
            "visual_scale": visual_scale,
            "geometry_known": True,
            "label": "Tubular circular",
        }

    # With A and I only, the actual section shape is unknown. The 3D view must
    # not imply a geometry that was never supplied.
    return {
        "kind": "custom",
        "visual_scale": 1.0,
        "geometry_known": False,
        "label": "Geometría no definida (solo A e I)",
        "c_mm": float(section_params.get("c_mm", 100.0)),
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
    auto_amp = 1.0 if max_v < 1e-12 else min(max(0.10 * Lvis / max_v, 1.0), 5000.0)

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

    length = float(x[-1]) if len(x) else float(p["L"])

    return {
        "case_id": case_id,
        "title": case_title,
        "length": length,
        "x": [round(float(z), 8) for z in x],
        # IMPORTANT: v is sent with its physical sign. The 3D scene uses +Y up,
        # so a negative Euler-Bernoulli deflection is displayed downward.
        "deflection": [float(z) for z in v],
        "moment": [float(z) for z in m],
        "x_probe": float(x_probe),
        "probe": {"V": shear, "M": moment},
        "supports": _supports(case_id, p),
        "loads": _loads(case_id, p),
        "section": _section_payload(section_type, section_params, length),
        "stress": {
            "y_mm": [float(z) for z in sy],
            "sigma_mpa": [float(z) for z in ss],
            "tau_mpa": [float(z) for z in st],
            "sigma_max": float(stress_result.sigma_max_abs_mpa),
            "sigma_top": float(stress_result.sigma_top_mpa),
            "sigma_bottom": float(stress_result.sigma_bottom_mpa),
            "tau_max": None if stress_result.tau_max_abs_mpa is None else float(stress_result.tau_max_abs_mpa),
            "tau_max_y_mm": None if stress_result.tau_max_y_mm is None else float(stress_result.tau_max_y_mm),
            "c_mm": float(stress_result.c_mm),
            "shear_available": bool(stress_result.shear_available),
            "note": str(stress_result.note),
        },
        "E_gpa": float(young_gpa),
        "I_mm4": float(inertia_mm4),
        "auto_amplification": float(auto_amp),
        "max_deflection_mm": float(deflection_result.max_abs_deflection_m * 1000.0),
        "max_deflection_x": float(deflection_result.max_abs_deflection_x_m),
    }
