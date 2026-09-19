from __future__ import annotations
import math
from typing import Any, Dict
import pandas as pd

R_AIR = 0.287      # kJ/kg-K
CP_AIR = 1.004     # kJ/kg-K
CV_AIR = CP_AIR - R_AIR
K_AIR = CP_AIR/CV_AIR
G = 9.80665

def air_entropy_rel(T, P, Tref=300.0, Pref=100.0, cp=CP_AIR, R=R_AIR):
    return cp*math.log(T/Tref) - R*math.log(P/Pref)

def air_state(i, T, P, v=None, cp=CP_AIR, R=R_AIR):
    if v is None:
        v = R*T/P
    return {
        "Estado": str(i),
        "T [K]": float(T),
        "T [°C]": float(T)-273.15,
        "P [kPa]": float(P),
        "v [m³/kg]": float(v),
        "h [kJ/kg]": float(cp*T),
        "u [kJ/kg]": float((cp-R)*T),
        "s* [kJ/kg·K]": float(air_entropy_rel(T,P,cp=cp,R=R)),
    }

def metric(symbol, value, unit="", description=""):
    return {"symbol": symbol, "value": value, "unit": unit, "description": description}

def package(states, processes, metrics, notes=None, meta=None):
    return {
        "states": states if isinstance(states,pd.DataFrame) else pd.DataFrame(states),
        "processes": processes if isinstance(processes,pd.DataFrame) else pd.DataFrame(processes),
        "metrics": metrics,
        "notes": notes or [],
        "meta": meta or {},
    }

def rates_from_specific(metrics, mdot):
    """Convierte automáticamente magnitudes específicas kJ/kg a tasas kW."""
    out=[]
    if mdot is None or mdot <= 0:
        return out
    for m in metrics:
        unit=m.get("unit","")
        sym=m.get("symbol","")
        val=m.get("value")
        if val is None:
            continue
        if unit == "kJ/kg":
            if sym.startswith(r"w") or r"\dot" not in sym and "w_" in sym:
                rsym = r"\dot W" + sym[1:] if sym.startswith("w") else r"\dot W"
            elif sym.startswith(r"q") or "q_" in sym:
                rsym = r"\dot Q" + sym[1:] if sym.startswith("q") else r"\dot Q"
            else:
                continue
            out.append(metric(rsym, mdot*float(val), "kW", f"Con ṁ = {mdot:g} kg/s"))
    return out

def cycle_first_law_residual(qin, qout, wnet):
    return (qin-qout)-wnet

def carnot_eta(TH,TL):
    return 1-TL/TH

def carnot_cop_r(TH,TL):
    return TL/(TH-TL)

def carnot_cop_hp(TH,TL):
    return TH/(TH-TL)
