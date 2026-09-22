from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import numpy as np

from .beam_cases import CASES


@dataclass
class Segment:
    x0: float
    x1: float
    v: Callable[[np.ndarray], np.ndarray]
    m: Callable[[np.ndarray], np.ndarray]


def _const(value: float):
    return lambda x: np.full_like(np.asarray(x, dtype=float), float(value), dtype=float)


def domain_end(case_id: str, p: dict) -> float:
    if case_id == "simple_overhang_load":
        return float(p["L"]) + float(p["a"])
    return float(p["L"])


def _case_segments_legacy(case_id: str, p: dict) -> list[Segment]:
    L = float(p["L"])

    # 1
    if case_id == "cantilever_end_load":
        F = float(p["F"])
        return [Segment(0.0, L, _const(F), lambda x: F * (x - L))]

    # 2
    if case_id == "cantilever_point_load":
        F, a = float(p["F"]), float(p["a"])
        return [
            Segment(0.0, a, _const(F), lambda x: F * (x - a)),
            Segment(a, L, _const(0.0), _const(0.0)),
        ]

    # 3
    if case_id == "cantilever_udl":
        w = float(p["w"])
        return [
            Segment(
                0.0,
                L,
                lambda x: w * (L - x),
                lambda x: -0.5 * w * (L - x) ** 2,
            )
        ]

    # 4
    if case_id == "cantilever_end_moment":
        M0 = float(p["M0"])
        return [Segment(0.0, L, _const(0.0), _const(M0))]

    # 5
    if case_id == "simple_center_load":
        F, a = float(p["F"]), L / 2.0
        return [
            Segment(0.0, a, _const(F / 2.0), lambda x: F * x / 2.0),
            Segment(a, L, _const(-F / 2.0), lambda x: F * (L - x) / 2.0),
        ]

    # 6
    if case_id == "simple_point_load":
        F, a = float(p["F"]), float(p["a"])
        b = L - a
        RA, RB = F * b / L, F * a / L
        return [
            Segment(0.0, a, _const(RA), lambda x: RA * x),
            Segment(a, L, _const(-RB), lambda x: RB * (L - x)),
        ]

    # 7
    if case_id == "simple_udl":
        w = float(p["w"])
        return [
            Segment(
                0.0,
                L,
                lambda x: w * L / 2.0 - w * x,
                lambda x: 0.5 * w * x * (L - x),
            )
        ]

    # 8
    if case_id == "simple_point_moment":
        M0, a = float(p["M0"]), float(p["a"])
        V = M0 / L
        return [
            Segment(0.0, a, _const(V), lambda x: M0 * x / L),
            Segment(a, L, _const(V), lambda x: M0 * (x - L) / L),
        ]

    # 9
    if case_id == "simple_twin_loads":
        F, a = float(p["F"]), float(p["a"])
        c = L - a
        return [
            Segment(0.0, a, _const(F), lambda x: F * x),
            Segment(a, c, _const(0.0), _const(F * a)),
            Segment(c, L, _const(-F), lambda x: F * (L - x)),
        ]

    # 10
    if case_id == "simple_overhang_load":
        F, a = float(p["F"]), float(p["a"])
        total = L + a
        return [
            Segment(
                0.0, L,
                _const(-F * a / L),
                lambda x: -F * a * x / L,
            ),
            Segment(
                L, total,
                _const(F),
                lambda x: F * (x - total),
            ),
        ]

    # 11
    if case_id == "propped_center_load":
        F, a = float(p["F"]), L / 2.0
        R1, R2, M1 = 11.0 * F / 16.0, 5.0 * F / 16.0, 3.0 * F * L / 16.0
        return [
            Segment(0.0, a, _const(R1), lambda x: R1 * x - M1),
            Segment(a, L, _const(-R2), lambda x: R2 * (L - x)),
        ]

    # 12
    if case_id == "propped_point_load":
        F, a = float(p["F"]), float(p["a"])
        b = L - a
        R1 = F * b * (3.0 * L**2 - b**2) / (2.0 * L**3)
        R2 = F * a**2 * (3.0 * L - a) / (2.0 * L**3)
        M1 = F * b * (L**2 - b**2) / (2.0 * L**2)
        return [
            Segment(0.0, a, _const(R1), lambda x: R1 * x - M1),
            Segment(a, L, _const(-R2), lambda x: R1 * x - M1 - F * (x - a)),
        ]

    # 13
    if case_id == "propped_udl":
        w = float(p["w"])
        R1, R2, M1 = 5.0 * w * L / 8.0, 3.0 * w * L / 8.0, w * L**2 / 8.0
        return [
            Segment(
                0.0, L,
                lambda x: R1 - w * x,
                lambda x: -M1 + R1 * x - 0.5 * w * x**2,
            )
        ]

    # 14
    if case_id == "fixed_center_load":
        F, a = float(p["F"]), L / 2.0
        R = F / 2.0
        M0 = F * L / 8.0
        return [
            Segment(0.0, a, _const(R), lambda x: R * x - M0),
            Segment(a, L, _const(-R), lambda x: R * (L - x) - M0),
        ]

    # 15
    if case_id == "fixed_point_load":
        F, a = float(p["F"]), float(p["a"])
        b = L - a
        R1 = F * b**2 * (3.0 * a + b) / L**3
        R2 = F * a**2 * (3.0 * b + a) / L**3
        M1 = F * a * b**2 / L**2
        return [
            Segment(0.0, a, _const(R1), lambda x: R1 * x - M1),
            Segment(a, L, _const(-R2), lambda x: R1 * x - M1 - F * (x - a)),
        ]

    # 16
    if case_id == "fixed_udl":
        w = float(p["w"])
        R = w * L / 2.0
        M0 = w * L**2 / 12.0
        return [
            Segment(
                0.0, L,
                lambda x: R - w * x,
                lambda x: -M0 + R * x - 0.5 * w * x**2,
            )
        ]

    raise KeyError(case_id)


def _case_segments(case_id: str, p: dict) -> list[Segment]:
    """
    Internal-force sign convention used in the course material:
      dV/dx = w(x), with distributed load w positive downward
      dM/dx = -V(x)

    The original library moments are preserved. The shear field is therefore
    the negative of the legacy implementation so that all 16 cases satisfy
    dM/dx=-V consistently.
    """
    legacy = _case_segments_legacy(case_id, p)
    return [
        Segment(
            seg.x0,
            seg.x1,
            lambda x, f=seg.v: -np.asarray(f(x), dtype=float),
            seg.m,
        )
        for seg in legacy
    ]


def reactions(case_id: str, p: dict) -> list[dict]:
    L = float(p["L"])

    if case_id == "cantilever_end_load":
        F = float(p["F"])
        return [
            {"symbol": "R_A", "value": F, "unit": "kN", "sense": "↑"},
            {"symbol": "M_A", "value": F * L, "unit": "kN·m", "sense": "↺"},
        ]

    if case_id == "cantilever_point_load":
        F, a = float(p["F"]), float(p["a"])
        return [
            {"symbol": "R_A", "value": F, "unit": "kN", "sense": "↑"},
            {"symbol": "M_A", "value": F * a, "unit": "kN·m", "sense": "↺"},
        ]

    if case_id == "cantilever_udl":
        w = float(p["w"])
        return [
            {"symbol": "R_A", "value": w * L, "unit": "kN", "sense": "↑"},
            {"symbol": "M_A", "value": w * L**2 / 2.0, "unit": "kN·m", "sense": "↺"},
        ]

    if case_id == "cantilever_end_moment":
        M0 = float(p["M0"])
        return [
            {"symbol": "R_A", "value": 0.0, "unit": "kN", "sense": ""},
            {"symbol": "|M_A|", "value": abs(M0), "unit": "kN·m", "sense": "opuesto a M₀"},
        ]

    if case_id == "simple_center_load":
        F = float(p["F"])
        return [
            {"symbol": "R_A", "value": F / 2.0, "unit": "kN", "sense": "↑"},
            {"symbol": "R_B", "value": F / 2.0, "unit": "kN", "sense": "↑"},
        ]

    if case_id == "simple_point_load":
        F, a = float(p["F"]), float(p["a"])
        b = L - a
        return [
            {"symbol": "R_A", "value": F * b / L, "unit": "kN", "sense": "↑"},
            {"symbol": "R_B", "value": F * a / L, "unit": "kN", "sense": "↑"},
        ]

    if case_id == "simple_udl":
        w = float(p["w"])
        return [
            {"symbol": "R_A", "value": w * L / 2.0, "unit": "kN", "sense": "↑"},
            {"symbol": "R_B", "value": w * L / 2.0, "unit": "kN", "sense": "↑"},
        ]

    if case_id == "simple_point_moment":
        M0 = float(p["M0"])
        return [
            {"symbol": "R_A", "value": M0 / L, "unit": "kN", "sense": "↑" if M0 >= 0 else "↓"},
            {"symbol": "R_B", "value": -M0 / L, "unit": "kN", "sense": "↓" if M0 >= 0 else "↑"},
        ]

    if case_id == "simple_twin_loads":
        F = float(p["F"])
        return [
            {"symbol": "R_A", "value": F, "unit": "kN", "sense": "↑"},
            {"symbol": "R_B", "value": F, "unit": "kN", "sense": "↑"},
        ]

    if case_id == "simple_overhang_load":
        F, a = float(p["F"]), float(p["a"])
        return [
            {"symbol": "R_A", "value": F * a / L, "unit": "kN", "sense": "↓"},
            {"symbol": "R_B", "value": F * (L + a) / L, "unit": "kN", "sense": "↑"},
        ]

    if case_id == "propped_center_load":
        F = float(p["F"])
        return [
            {"symbol": "R_A", "value": 11.0 * F / 16.0, "unit": "kN", "sense": "↑"},
            {"symbol": "R_B", "value": 5.0 * F / 16.0, "unit": "kN", "sense": "↑"},
            {"symbol": "M_A", "value": 3.0 * F * L / 16.0, "unit": "kN·m", "sense": "↺"},
        ]

    if case_id == "propped_point_load":
        F, a = float(p["F"]), float(p["a"])
        b = L - a
        R1 = F * b * (3.0 * L**2 - b**2) / (2.0 * L**3)
        R2 = F * a**2 * (3.0 * L - a) / (2.0 * L**3)
        M1 = F * b * (L**2 - b**2) / (2.0 * L**2)
        return [
            {"symbol": "R_A", "value": R1, "unit": "kN", "sense": "↑"},
            {"symbol": "R_B", "value": R2, "unit": "kN", "sense": "↑"},
            {"symbol": "M_A", "value": M1, "unit": "kN·m", "sense": "↺"},
        ]

    if case_id == "propped_udl":
        w = float(p["w"])
        return [
            {"symbol": "R_A", "value": 5.0 * w * L / 8.0, "unit": "kN", "sense": "↑"},
            {"symbol": "R_B", "value": 3.0 * w * L / 8.0, "unit": "kN", "sense": "↑"},
            {"symbol": "M_A", "value": w * L**2 / 8.0, "unit": "kN·m", "sense": "↺"},
        ]

    if case_id == "fixed_center_load":
        F = float(p["F"])
        return [
            {"symbol": "R_A", "value": F / 2.0, "unit": "kN", "sense": "↑"},
            {"symbol": "R_B", "value": F / 2.0, "unit": "kN", "sense": "↑"},
            {"symbol": "M_A", "value": F * L / 8.0, "unit": "kN·m", "sense": "↺"},
            {"symbol": "M_B", "value": F * L / 8.0, "unit": "kN·m", "sense": "↻"},
        ]

    if case_id == "fixed_point_load":
        F, a = float(p["F"]), float(p["a"])
        b = L - a
        R1 = F * b**2 * (3.0 * a + b) / L**3
        R2 = F * a**2 * (3.0 * b + a) / L**3
        M1 = F * a * b**2 / L**2
        M2 = F * a**2 * b / L**2
        return [
            {"symbol": "R_A", "value": R1, "unit": "kN", "sense": "↑"},
            {"symbol": "R_B", "value": R2, "unit": "kN", "sense": "↑"},
            {"symbol": "M_A", "value": M1, "unit": "kN·m", "sense": "↺"},
            {"symbol": "M_B", "value": M2, "unit": "kN·m", "sense": "↻"},
        ]

    if case_id == "fixed_udl":
        w = float(p["w"])
        return [
            {"symbol": "R_A", "value": w * L / 2.0, "unit": "kN", "sense": "↑"},
            {"symbol": "R_B", "value": w * L / 2.0, "unit": "kN", "sense": "↑"},
            {"symbol": "M_A", "value": w * L**2 / 12.0, "unit": "kN·m", "sense": "↺"},
            {"symbol": "M_B", "value": w * L**2 / 12.0, "unit": "kN·m", "sense": "↻"},
        ]

    raise KeyError(case_id)


def discontinuities(case_id: str, p: dict) -> dict:
    L = float(p["L"])

    v_jumps = {
        "cantilever_point_load": [float(p.get("a", 0.0))],
        "simple_center_load": [L / 2.0],
        "simple_point_load": [float(p.get("a", 0.0))],
        "simple_twin_loads": [float(p.get("a", 0.0)), L - float(p.get("a", 0.0))],
        "simple_overhang_load": [L],
        "propped_center_load": [L / 2.0],
        "propped_point_load": [float(p.get("a", 0.0))],
        "fixed_center_load": [L / 2.0],
        "fixed_point_load": [float(p.get("a", 0.0))],
    }.get(case_id, [])

    m_jumps = {
        "simple_point_moment": [float(p.get("a", 0.0))],
    }.get(case_id, [])

    return {"V": v_jumps, "M": m_jumps}


def sample_segments(case_id: str, p: dict, n_per_segment: int = 350) -> list[dict]:
    output = []
    for seg in _case_segments(case_id, p):
        xs = np.linspace(seg.x0, seg.x1, max(2, n_per_segment))
        output.append({
            "x": xs,
            "V": np.asarray(seg.v(xs), dtype=float),
            "M": np.asarray(seg.m(xs), dtype=float),
            "x0": seg.x0,
            "x1": seg.x1,
        })
    return output


def point_state(case_id: str, p: dict, x: float, tol: float = 1e-8) -> dict:
    x = float(x)
    segs = _case_segments(case_id, p)
    candidates = []

    for i, seg in enumerate(segs):
        if seg.x0 - tol <= x <= seg.x1 + tol:
            candidates.append({
                "segment": i,
                "V": float(np.asarray(seg.v(np.array([x])))[0]),
                "M": float(np.asarray(seg.m(np.array([x])))[0]),
            })

    if not candidates:
        raise ValueError("x fuera del dominio de la viga.")

    if len(candidates) == 1:
        return {
            "x": x,
            "V": candidates[0]["V"],
            "M": candidates[0]["M"],
            "V_left": None,
            "V_right": None,
            "M_left": None,
            "M_right": None,
        }

    left, right = candidates[0], candidates[-1]
    return {
        "x": x,
        "V": right["V"],
        "M": right["M"],
        "V_left": left["V"],
        "V_right": right["V"],
        "M_left": left["M"],
        "M_right": right["M"],
    }


def extrema(case_id: str, p: dict) -> dict:
    samples = sample_segments(case_id, p, n_per_segment=1600)
    pts = []
    for s in samples:
        for x, v, m in zip(s["x"], s["V"], s["M"]):
            pts.append((float(x), float(v), float(m)))

    max_v = max(pts, key=lambda t: abs(t[1]))
    max_m_abs = max(pts, key=lambda t: abs(t[2]))
    max_m = max(pts, key=lambda t: t[2])
    min_m = min(pts, key=lambda t: t[2])

    return {
        "V_abs": abs(max_v[1]),
        "V_x": max_v[0],
        "M_abs": abs(max_m_abs[2]),
        "M_abs_x": max_m_abs[0],
        "M_max": max_m[2],
        "M_max_x": max_m[0],
        "M_min": min_m[2],
        "M_min_x": min_m[0],
    }


def zero_crossings(case_id: str, p: dict, field: str = "M") -> list[float]:
    samples = sample_segments(case_id, p, n_per_segment=2200)
    roots = []
    for s in samples:
        xs = s["x"]
        ys = s[field]
        for i in range(len(xs) - 1):
            y0, y1 = ys[i], ys[i + 1]
            x0, x1 = xs[i], xs[i + 1]
            if abs(y0) < 1e-10:
                roots.append(float(x0))
            if y0 * y1 < 0:
                xr = x0 - y0 * (x1 - x0) / (y1 - y0)
                roots.append(float(xr))
        if abs(ys[-1]) < 1e-10:
            roots.append(float(xs[-1]))

    # unique, excluding almost-identical duplicates
    unique = []
    for r in sorted(roots):
        if not unique or abs(r - unique[-1]) > max(1e-5, 1e-5 * domain_end(case_id, p)):
            unique.append(r)
    return unique


def equations(case_id: str, p: dict) -> dict:
    if case_id == "cantilever_end_load":
        return {
            "reactions": [r"R_A=F", r"M_A=FL"],
            "shear": [r"V(x)=-F,\qquad 0\le x<L"],
            "moment": [r"M(x)=F(x-L),\qquad 0\le x\le L"],
        }

    if case_id == "cantilever_point_load":
        return {
            "reactions": [r"R_A=F", r"M_A=Fa"],
            "shear": [
                r"V(x)=-F,\qquad 0\le x<a",
                r"V(x)=0,\qquad a<x\le L",
            ],
            "moment": [
                r"M(x)=F(x-a),\qquad 0\le x\le a",
                r"M(x)=0,\qquad a\le x\le L",
            ],
        }

    if case_id == "cantilever_udl":
        return {
            "reactions": [r"R_A=wL", r"M_A=\frac{wL^2}{2}"],
            "shear": [r"V(x)=-w(L-x)"],
            "moment": [r"M(x)=-\frac{w}{2}(L-x)^2"],
        }

    if case_id == "cantilever_end_moment":
        return {
            "reactions": [r"R_A=0", r"|M_A|=|M_0|"],
            "shear": [r"V(x)=0"],
            "moment": [r"M(x)=M_0"],
        }

    if case_id == "simple_center_load":
        return {
            "reactions": [r"R_A=R_B=\frac{F}{2}"],
            "shear": [
                r"V(x)=-\frac{F}{2},\qquad 0<x<\frac{L}{2}",
                r"V(x)=+\frac{F}{2},\qquad \frac{L}{2}<x<L",
            ],
            "moment": [
                r"M(x)=\frac{F}{2}x,\qquad 0\le x\le\frac{L}{2}",
                r"M(x)=\frac{F}{2}(L-x),\qquad \frac{L}{2}\le x\le L",
            ],
        }

    if case_id == "simple_point_load":
        return {
            "reactions": [r"b=L-a", r"R_A=\frac{Fb}{L}", r"R_B=\frac{Fa}{L}"],
            "shear": [
                r"V(x)=-R_A,\qquad 0<x<a",
                r"V(x)=+R_B,\qquad a<x<L",
            ],
            "moment": [
                r"M(x)=\frac{Fb}{L}x,\qquad 0\le x\le a",
                r"M(x)=\frac{Fa}{L}(L-x),\qquad a\le x\le L",
            ],
        }

    if case_id == "simple_udl":
        return {
            "reactions": [r"R_A=R_B=\frac{wL}{2}"],
            "shear": [r"V(x)=wx-\frac{wL}{2}"],
            "moment": [r"M(x)=\frac{wx}{2}(L-x)"],
        }

    if case_id == "simple_point_moment":
        return {
            "reactions": [r"R_A=+\frac{M_0}{L}", r"R_B=-\frac{M_0}{L}"],
            "shear": [r"V(x)=-\frac{M_0}{L}"],
            "moment": [
                r"M(x)=\frac{M_0}{L}x,\qquad 0\le x<a",
                r"M(x)=\frac{M_0}{L}(x-L),\qquad a<x\le L",
            ],
        }

    if case_id == "simple_twin_loads":
        return {
            "reactions": [r"R_A=R_B=F"],
            "shear": [
                r"V(x)=-F,\qquad 0<x<a",
                r"V(x)=0,\qquad a<x<L-a",
                r"V(x)=+F,\qquad L-a<x<L",
            ],
            "moment": [
                r"M(x)=Fx,\qquad 0\le x\le a",
                r"M(x)=Fa,\qquad a\le x\le L-a",
                r"M(x)=F(L-x),\qquad L-a\le x\le L",
            ],
        }

    if case_id == "simple_overhang_load":
        return {
            "reactions": [
                r"|R_A|=\frac{Fa}{L}\quad(\text{hacia abajo})",
                r"R_B=\frac{F(L+a)}{L}",
            ],
            "shear": [
                r"V(x)=+\frac{Fa}{L},\qquad 0<x<L",
                r"V(x)=-F,\qquad L<x<L+a",
            ],
            "moment": [
                r"M(x)=-\frac{Fa}{L}x,\qquad 0\le x\le L",
                r"M(x)=F(x-L-a),\qquad L\le x\le L+a",
            ],
        }

    if case_id == "propped_center_load":
        return {
            "reactions": [
                r"R_A=\frac{11F}{16}",
                r"R_B=\frac{5F}{16}",
                r"M_A=\frac{3FL}{16}",
            ],
            "shear": [
                r"V(x)=-\frac{11F}{16},\qquad 0<x<\frac{L}{2}",
                r"V(x)=+\frac{5F}{16},\qquad \frac{L}{2}<x<L",
            ],
            "moment": [
                r"M(x)=\frac{F}{16}(11x-3L),\qquad 0\le x\le\frac{L}{2}",
                r"M(x)=\frac{5F}{16}(L-x),\qquad \frac{L}{2}\le x\le L",
            ],
        }

    if case_id == "propped_point_load":
        return {
            "reactions": [
                r"b=L-a",
                r"R_A=\frac{Fb}{2L^3}(3L^2-b^2)",
                r"R_B=\frac{Fa^2}{2L^3}(3L-a)",
                r"M_A=\frac{Fb}{2L^2}(L^2-b^2)",
            ],
            "shear": [
                r"V(x)=-R_A,\qquad 0<x<a",
                r"V(x)=+R_B,\qquad a<x<L",
            ],
            "moment": [
                r"M(x)=R_Ax-M_A,\qquad 0\le x\le a",
                r"M(x)=R_Ax-M_A-F(x-a),\qquad a\le x\le L",
            ],
        }

    if case_id == "propped_udl":
        return {
            "reactions": [
                r"R_A=\frac{5wL}{8}",
                r"R_B=\frac{3wL}{8}",
                r"M_A=\frac{wL^2}{8}",
            ],
            "shear": [r"V(x)=wx-\frac{5wL}{8}"],
            "moment": [r"M(x)=-\frac{w}{8}(4x^2-5Lx+L^2)"],
        }

    if case_id == "fixed_center_load":
        return {
            "reactions": [
                r"R_A=R_B=\frac{F}{2}",
                r"M_A=M_B=\frac{FL}{8}",
            ],
            "shear": [
                r"V(x)=-\frac{F}{2},\qquad 0<x<\frac{L}{2}",
                r"V(x)=+\frac{F}{2},\qquad \frac{L}{2}<x<L",
            ],
            "moment": [
                r"M(x)=\frac{F}{8}(4x-L),\qquad 0\le x\le\frac{L}{2}",
                r"M(x)=\frac{F}{8}(3L-4x),\qquad \frac{L}{2}\le x\le L",
            ],
        }

    if case_id == "fixed_point_load":
        return {
            "reactions": [
                r"b=L-a",
                r"R_A=\frac{Fb^2}{L^3}(3a+b)",
                r"R_B=\frac{Fa^2}{L^3}(3b+a)",
                r"M_A=\frac{Fab^2}{L^2}",
                r"M_B=\frac{Fa^2b}{L^2}",
            ],
            "shear": [
                r"V(x)=-R_A,\qquad 0<x<a",
                r"V(x)=+R_B,\qquad a<x<L",
            ],
            "moment": [
                r"M(x)=R_Ax-M_A,\qquad 0\le x\le a",
                r"M(x)=R_Ax-M_A-F(x-a),\qquad a\le x\le L",
            ],
        }

    if case_id == "fixed_udl":
        return {
            "reactions": [
                r"R_A=R_B=\frac{wL}{2}",
                r"M_A=M_B=\frac{wL^2}{12}",
            ],
            "shear": [r"V(x)=\frac{w}{2}(2x-L)"],
            "moment": [r"M(x)=\frac{w}{12}(6Lx-6x^2-L^2)"],
        }

    raise KeyError(case_id)


def case_summary(case_id: str, p: dict) -> dict:
    data = CASES[case_id]
    return {
        **data,
        "reactions": reactions(case_id, p),
        "equations": equations(case_id, p),
        "extrema": extrema(case_id, p),
        "discontinuities": discontinuities(case_id, p),
        "moment_zeros": zero_crossings(case_id, p, field="M"),
        "domain_end": domain_end(case_id, p),
    }
