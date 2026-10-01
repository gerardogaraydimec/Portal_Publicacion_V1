from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass
class IsoGpsResult:
    kind: str
    tolerance_mm: float
    deviation_mm: float
    pass_ok: bool
    ratio: float
    feature_control_frame: str
    interpretation: str


def feature_control_frame(kind: str, tolerance_mm: float, datums: tuple[str, ...] = ()) -> str:
    symbol_map = {
        'Posición': '⌖',
        'Planitud': '⏥',
        'Perpendicularidad': '⟂',
        'Paralelismo': '∥',
        'Circularidad': '○',
        'Cilindricidad': '⌭',
    }
    sym = symbol_map.get(kind, '⌖')
    datum_txt = ' | '.join(datums) if datums else ''
    if datum_txt:
        return f"{sym} | ⌀ {tolerance_mm:.3f} | {datum_txt}"
    return f"{sym} | {tolerance_mm:.3f}"


def evaluate_case(kind: str, tolerance_mm: float, deviation_mm: float) -> IsoGpsResult:
    datums = {
        'Posición': ('A', 'B', 'C'),
        'Perpendicularidad': ('A',),
        'Paralelismo': ('A',),
        'Planitud': (),
        'Circularidad': (),
        'Cilindricidad': (),
    }.get(kind, ())
    pass_ok = deviation_mm <= tolerance_mm + 1e-12
    ratio = deviation_mm / tolerance_mm if tolerance_mm > 0 else math.inf
    fcf = feature_control_frame(kind, tolerance_mm, datums)
    if kind == 'Posición':
        interp = 'El eje real debe quedar dentro de un cilindro de tolerancia centrado en la posición teórica verdadera.'
    elif kind == 'Planitud':
        interp = 'La superficie real debe quedar contenida entre dos planos paralelos separados por la tolerancia.'
    elif kind == 'Perpendicularidad':
        interp = 'El eje o superficie real debe mantenerse perpendicular al datum de referencia dentro de la zona de tolerancia.'
    elif kind == 'Paralelismo':
        interp = 'La superficie real debe mantenerse paralela al datum de referencia dentro de dos planos límite.'
    elif kind == 'Circularidad':
        interp = 'Cada sección circular debe quedar entre dos circunferencias concéntricas separadas radialmente por la tolerancia.'
    else:
        interp = 'La superficie cilíndrica completa debe quedar entre dos cilindros coaxiales separados radialmente por la tolerancia.'
    return IsoGpsResult(kind, tolerance_mm, deviation_mm, pass_ok, ratio, fcf, interp)
