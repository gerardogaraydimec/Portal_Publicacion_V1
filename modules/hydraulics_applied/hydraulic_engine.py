from __future__ import annotations
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class CylinderResult:
    piston_area_m2: float
    annulus_area_m2: float
    extension_speed_m_s: float
    retraction_speed_m_s: float
    extension_force_n: float
    retraction_force_n: float
    pressure_for_load_bar_extension: float
    pressure_for_load_bar_retraction: float
    hydraulic_power_kw: float


def cylinder_performance(
    flow_l_min: float,
    bore_mm: float,
    rod_mm: float,
    pressure_bar: float,
    load_kn: float,
) -> CylinderResult:
    if flow_l_min <= 0 or bore_mm <= 0 or rod_mm < 0 or pressure_bar < 0 or load_kn < 0:
        raise ValueError("Los parámetros deben ser no negativos y el caudal/diámetro deben ser mayores que cero.")
    if rod_mm >= bore_mm:
        raise ValueError("El diámetro de vástago debe ser menor que el diámetro del pistón.")

    q = flow_l_min / 1000.0 / 60.0
    d = bore_mm / 1000.0
    dr = rod_mm / 1000.0
    ap = math.pi * d**2 / 4.0
    ar = math.pi * dr**2 / 4.0
    aa = ap - ar
    p = pressure_bar * 1e5
    load = load_kn * 1000.0

    return CylinderResult(
        piston_area_m2=ap,
        annulus_area_m2=aa,
        extension_speed_m_s=q/ap,
        retraction_speed_m_s=q/aa,
        extension_force_n=p*ap,
        retraction_force_n=p*aa,
        pressure_for_load_bar_extension=(load/ap)/1e5 if load > 0 else 0.0,
        pressure_for_load_bar_retraction=(load/aa)/1e5 if load > 0 else 0.0,
        hydraulic_power_kw=(p*q)/1000.0,
    )


def classify_pressure_state(required_bar: float, relief_bar: float) -> str:
    if relief_bar <= 0:
        return "Sin criterio de alivio"
    ratio = required_bar / relief_bar
    if ratio < 0.75:
        return "Margen amplio frente al alivio"
    if ratio < 0.95:
        return "Cercano al ajuste de alivio"
    if ratio <= 1.02:
        return "En zona del alivio"
    return "La carga exigiría más presión que el ajuste de alivio"


def active_paths(valve_name: str, position: str, directional_data: dict) -> list[tuple[str, str]]:
    data = directional_data[valve_name]
    key = {"Izquierda": "left", "Centro": "center", "Derecha": "right"}[position]
    desc = data.get(key, "")
    paths: list[tuple[str, str]] = []
    if "P → A" in desc:
        paths.append(("P", "A"))
    if "P → B" in desc:
        paths.append(("P", "B"))
    if "B → T" in desc:
        paths.append(("B", "T"))
    if "A → T" in desc:
        paths.append(("A", "T"))
    if "P → T" in desc:
        paths.append(("P", "T"))
    if "A y B → T" in desc:
        paths.extend([("A", "T"), ("B", "T")])
    if "P, A, B y T comunicados" in desc:
        paths.extend([("P", "T"), ("A", "T"), ("B", "T")])
    return paths


def motion_from_4_3_center(valve_name: str, position: str) -> str:
    if position == "Izquierda":
        return "Extensión del cilindro"
    if position == "Derecha":
        return "Retracción del cilindro"
    if "centro tándem" in valve_name.lower():
        return "Actuador bloqueado; bomba descargada a tanque"
    if "centro flotante" in valve_name.lower():
        return "Actuador libre hidráulicamente hacia tanque; P bloqueado"
    if "centro abierto" in valve_name.lower():
        return "Puertos comunicados; comportamiento depende de carga y arquitectura"
    return "Actuador bloqueado; P también bloqueado"


def valve_descriptor(valve_name: str, directional_data: dict) -> dict:
    d = directional_data[valve_name]
    return {
        "ports": d["ports"],
        "positions": d["positions"],
        "rest": d["rest"],
    }
