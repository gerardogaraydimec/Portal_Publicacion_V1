from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import math
import numpy as np
import pandas as pd

try:
    from iapws import IAPWS97
except ImportError as exc:
    IAPWS97 = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

TC_K = 647.096
TC_C = TC_K - 273.15
PC_MPA = 22.064
PC_KPA = PC_MPA * 1000.0
TRIPLE_T_C = 0.01
TRIPLE_P_KPA = 0.611657

def require_iapws():
    if IAPWS97 is None:
        raise RuntimeError(
            "No se encontró el paquete 'iapws'. Instálalo con: "
            "python -m pip install -r requirements.txt"
        ) from _IMPORT_ERROR

def to_celsius(TK: float) -> float:
    return float(TK) - 273.15

def to_kelvin(TC: float) -> float:
    return float(TC) + 273.15

def _quality_display(x):
    if x is None:
        return None
    try:
        xx = float(x)
    except Exception:
        return None
    if not math.isfinite(xx):
        return None
    return xx if -1e-10 <= xx <= 1.0 + 1e-10 else None

def state_dict(st, phase_override: Optional[str] = None, quality_override: Any = "auto") -> Dict[str, Any]:
    x = _quality_display(getattr(st, "x", None))
    if quality_override != "auto":
        x = quality_override
    phase = phase_override or translate_phase(getattr(st, "phase", ""))
    return {
        "T_K": float(st.T),
        "T_C": to_celsius(st.T),
        "P_MPa": float(st.P),
        "P_kPa": float(st.P) * 1000.0,
        "v": float(st.v),
        "rho": float(st.rho),
        "u": float(st.u),
        "h": float(st.h),
        "s": float(st.s),
        "cp": float(st.cp) if st.cp is not None else None,
        "cv": float(st.cv) if st.cv is not None else None,
        "w": float(st.w) if st.w is not None else None,
        "x": x,
        "region": getattr(st, "region", None),
        "phase": phase,
    }

def translate_phase(phase: Any) -> str:
    s = str(phase or "").lower()
    if "supercritical" in s:
        return "Fluido supercrítico"
    if "two" in s or "mixture" in s:
        return "Mezcla saturada líquido-vapor"
    if "saturated liquid" in s:
        return "Líquido saturado"
    if "saturated vapor" in s or "saturated vapour" in s:
        return "Vapor saturado"
    if "liquid" in s:
        return "Líquido comprimido/subenfriado"
    if "vapour" in s or "vapor" in s or "gas" in s:
        return "Vapor sobrecalentado"
    return "Estado de agua/vapor"

def sat_at_T(T_C: float) -> Tuple[Any, Any]:
    require_iapws()
    TK = to_kelvin(T_C)
    if not (TRIPLE_T_C <= T_C <= TC_C):
        raise ValueError(
            f"Para saturación por temperatura use {TRIPLE_T_C:.2f} <= T <= {TC_C:.3f} °C."
        )
    return IAPWS97(T=TK, x=0), IAPWS97(T=TK, x=1)

def sat_at_P(P_kPa: float) -> Tuple[Any, Any]:
    require_iapws()
    if not (TRIPLE_P_KPA <= P_kPa <= PC_KPA):
        raise ValueError(
            f"Para saturación por presión use {TRIPLE_P_KPA:.6g} <= P <= {PC_KPA:.0f} kPa."
        )
    P = P_kPa / 1000.0
    return IAPWS97(P=P, x=0), IAPWS97(P=P, x=1)

def classify_PT(P_kPa: float, T_C: float, tol_T_C: float = 0.02) -> Dict[str, Any]:
    require_iapws()
    P_MPa = P_kPa / 1000.0
    TK = to_kelvin(T_C)
    if P_kPa <= 0:
        raise ValueError("La presión absoluta debe ser mayor que cero.")
    if TK <= 0:
        raise ValueError("La temperatura absoluta debe ser mayor que cero.")

    if P_MPa < PC_MPA and P_kPa >= TRIPLE_P_KPA:
        try:
            sf, sg = sat_at_P(P_kPa)
            Tsat_C = to_celsius(sf.T)
            if abs(T_C - Tsat_C) <= tol_T_C:
                return {
                    "underdetermined": True,
                    "phase": "Estado de saturación: calidad indeterminada con P y T solamente",
                    "Tsat_C": Tsat_C,
                    "Psat_kPa": P_kPa,
                    "sat_f": state_dict(sf, "Líquido saturado", 0.0),
                    "sat_g": state_dict(sg, "Vapor saturado", 1.0),
                }
            if T_C < Tsat_C:
                st = IAPWS97(P=P_MPa, T=TK)
                return {
                    "underdetermined": False,
                    "state": state_dict(st, "Líquido comprimido/subenfriado", None),
                    "Tsat_C": Tsat_C,
                }
            else:
                st = IAPWS97(P=P_MPa, T=TK)
                return {
                    "underdetermined": False,
                    "state": state_dict(st, "Vapor sobrecalentado", None),
                    "Tsat_C": Tsat_C,
                }
        except Exception:
            # Para presiones por debajo del punto triple o estados fuera de la línea LV,
            # dejar que IF97 decida el estado dentro de su dominio.
            pass

    st = IAPWS97(P=P_MPa, T=TK)
    phase = translate_phase(getattr(st, "phase", ""))
    if P_MPa >= PC_MPA and TK >= TC_K:
        phase = "Fluido supercrítico"
    elif P_MPa >= PC_MPA and TK < TC_K:
        phase = "Líquido comprimido de alta presión"
    return {"underdetermined": False, "state": state_dict(st, phase, None)}

def solve_state(mode: str, **kwargs) -> Dict[str, Any]:
    require_iapws()

    if mode == "P-T":
        return classify_PT(float(kwargs["P_kPa"]), float(kwargs["T_C"]))

    if mode == "T-x":
        T_C = float(kwargs["T_C"])
        x = float(kwargs["x"])
        if not 0 <= x <= 1:
            raise ValueError("La calidad x debe estar entre 0 y 1.")
        sf, sg = sat_at_T(T_C)
        st = IAPWS97(T=to_kelvin(T_C), x=x)
        if x <= 1e-12:
            phase = "Líquido saturado"
        elif x >= 1 - 1e-12:
            phase = "Vapor saturado"
        else:
            phase = "Mezcla saturada líquido-vapor"
        return {
            "underdetermined": False,
            "state": state_dict(st, phase, x),
            "sat_f": state_dict(sf, "Líquido saturado", 0.0),
            "sat_g": state_dict(sg, "Vapor saturado", 1.0),
        }

    if mode == "P-x":
        P_kPa = float(kwargs["P_kPa"])
        x = float(kwargs["x"])
        if not 0 <= x <= 1:
            raise ValueError("La calidad x debe estar entre 0 y 1.")
        sf, sg = sat_at_P(P_kPa)
        st = IAPWS97(P=P_kPa/1000.0, x=x)
        if x <= 1e-12:
            phase = "Líquido saturado"
        elif x >= 1 - 1e-12:
            phase = "Vapor saturado"
        else:
            phase = "Mezcla saturada líquido-vapor"
        return {
            "underdetermined": False,
            "state": state_dict(st, phase, x),
            "sat_f": state_dict(sf, "Líquido saturado", 0.0),
            "sat_g": state_dict(sg, "Vapor saturado", 1.0),
        }

    if mode == "P-h":
        st = IAPWS97(P=float(kwargs["P_kPa"])/1000.0, h=float(kwargs["h"]))
        return {"underdetermined": False, "state": state_dict(st)}

    if mode == "P-s":
        st = IAPWS97(P=float(kwargs["P_kPa"])/1000.0, s=float(kwargs["s"]))
        return {"underdetermined": False, "state": state_dict(st)}

    if mode == "h-s":
        st = IAPWS97(h=float(kwargs["h"]), s=float(kwargs["s"]))
        return {"underdetermined": False, "state": state_dict(st)}

    raise ValueError(f"Modo no reconocido: {mode}")

def saturation_curve(n: int = 180) -> pd.DataFrame:
    require_iapws()
    n = int(np.clip(n, 50, 320))
    # Se evita exactamente el punto crítico para mejorar robustez numérica.
    T_vals = np.linspace(TRIPLE_T_C, TC_C - 0.03, n)
    rows = []
    for TC in T_vals:
        try:
            f, g = sat_at_T(float(TC))
            rows.append({
                "T_C": TC, "P_kPa": f.P*1000.0,
                "vf": f.v, "vg": g.v,
                "uf": f.u, "ug": g.u,
                "hf": f.h, "hg": g.h,
                "sf": f.s, "sg": g.s,
            })
        except Exception:
            continue
    return pd.DataFrame(rows)

def saturation_table_T(Tmin_C: float, Tmax_C: float, n: int) -> pd.DataFrame:
    require_iapws()
    Tmin_C = max(float(Tmin_C), TRIPLE_T_C)
    Tmax_C = min(float(Tmax_C), TC_C - 0.001)
    if Tmin_C >= Tmax_C:
        raise ValueError("T mín debe ser menor que T máx dentro de la región de saturación.")
    n = int(np.clip(n, 2, 200))
    rows = []
    for TC in np.linspace(Tmin_C, Tmax_C, n):
        f, g = sat_at_T(float(TC))
        rows.append({
            "T [°C]": TC,
            "Psat [kPa]": f.P*1000.0,
            "vf [m³/kg]": f.v,
            "vg [m³/kg]": g.v,
            "uf [kJ/kg]": f.u,
            "ufg [kJ/kg]": g.u-f.u,
            "ug [kJ/kg]": g.u,
            "hf [kJ/kg]": f.h,
            "hfg [kJ/kg]": g.h-f.h,
            "hg [kJ/kg]": g.h,
            "sf [kJ/kg·K]": f.s,
            "sfg [kJ/kg·K]": g.s-f.s,
            "sg [kJ/kg·K]": g.s,
        })
    return pd.DataFrame(rows)

def saturation_table_P(Pmin_kPa: float, Pmax_kPa: float, n: int, logspace: bool = True) -> pd.DataFrame:
    require_iapws()
    Pmin_kPa = max(float(Pmin_kPa), TRIPLE_P_KPA)
    Pmax_kPa = min(float(Pmax_kPa), PC_KPA - 0.01)
    if Pmin_kPa >= Pmax_kPa:
        raise ValueError("P mín debe ser menor que P máx dentro de la región de saturación.")
    n = int(np.clip(n, 2, 200))
    vals = np.geomspace(Pmin_kPa, Pmax_kPa, n) if logspace else np.linspace(Pmin_kPa, Pmax_kPa, n)
    rows = []
    for Pk in vals:
        f, g = sat_at_P(float(Pk))
        rows.append({
            "P [kPa]": Pk,
            "Tsat [°C]": to_celsius(f.T),
            "vf [m³/kg]": f.v,
            "vg [m³/kg]": g.v,
            "uf [kJ/kg]": f.u,
            "ufg [kJ/kg]": g.u-f.u,
            "ug [kJ/kg]": g.u,
            "hf [kJ/kg]": f.h,
            "hfg [kJ/kg]": g.h-f.h,
            "hg [kJ/kg]": g.h,
            "sf [kJ/kg·K]": f.s,
            "sfg [kJ/kg·K]": g.s-f.s,
            "sg [kJ/kg·K]": g.s,
        })
    return pd.DataFrame(rows)

def table_PT(P_kPa: float, Tmin_C: float, Tmax_C: float, n: int) -> pd.DataFrame:
    require_iapws()
    n = int(np.clip(n, 2, 200))
    rows = []
    for TC in np.linspace(float(Tmin_C), float(Tmax_C), n):
        try:
            result = classify_PT(float(P_kPa), float(TC))
            if result["underdetermined"]:
                rows.append({
                    "P [kPa]": P_kPa, "T [°C]": TC,
                    "Estado": "Saturación (x indeterminada)",
                    "v [m³/kg]": np.nan, "u [kJ/kg]": np.nan,
                    "h [kJ/kg]": np.nan, "s [kJ/kg·K]": np.nan,
                })
            else:
                st = result["state"]
                rows.append({
                    "P [kPa]": st["P_kPa"], "T [°C]": st["T_C"],
                    "Estado": st["phase"], "v [m³/kg]": st["v"],
                    "u [kJ/kg]": st["u"], "h [kJ/kg]": st["h"],
                    "s [kJ/kg·K]": st["s"],
                })
        except Exception:
            continue
    return pd.DataFrame(rows)
