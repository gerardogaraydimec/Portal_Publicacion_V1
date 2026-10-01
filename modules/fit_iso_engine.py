from __future__ import annotations
from dataclasses import dataclass

# Tabla didáctica de referencia ISO 286 para las combinaciones H7/* más usadas.
# Desviaciones en micrómetros (µm). Los límites superiores de cada rango son inclusivos.
# Para el agujero H7: EI = 0 y ES = IT7.
_RANGES = [
    (0.0, 3.0), (3.0, 6.0), (6.0, 10.0), (10.0, 18.0),
    (18.0, 30.0), (30.0, 50.0), (50.0, 80.0), (80.0, 120.0),
    (120.0, 180.0), (180.0, 250.0), (250.0, 315.0), (315.0, 400.0),
    (400.0, 500.0),
]

_H7_ES = [10, 12, 15, 18, 21, 25, 30, 35, 40, 46, 52, 57, 63]

# Shaft deviations: (upper es, lower ei), µm
_SHAFTS = {
    'g6': [(-2,-8),(-4,-12),(-5,-14),(-6,-17),(-7,-20),(-9,-25),(-10,-29),(-12,-34),(-14,-39),(-15,-44),(-17,-49),(-18,-54),(-20,-60)],
    'h6': [(0,-6),(0,-8),(0,-9),(0,-11),(0,-13),(0,-16),(0,-19),(0,-22),(0,-25),(0,-29),(0,-32),(0,-36),(0,-40)],
    'k6': [(6,0),(9,1),(10,1),(12,1),(15,2),(18,2),(21,2),(25,3),(28,3),(33,4),(36,4),(40,4),(45,5)],
    'm6': [(8,2),(12,4),(15,6),(18,7),(21,8),(25,9),(30,11),(35,13),(40,15),(46,17),(52,20),(57,21),(63,23)],
    'n6': [(10,4),(16,8),(19,10),(23,12),(28,15),(33,17),(39,20),(45,23),(52,27),(60,31),(66,34),(73,37),(80,40)],
    'p6': [(12,6),(20,12),(24,15),(29,18),(35,22),(42,26),(51,32),(59,37),(68,43),(79,50),(88,56),(98,62),(108,68)],
}

_PRESET_PURPOSE = {
    'H7/g6': 'Ajuste con juego fino; facilita montaje y movimiento relativo controlado.',
    'H7/h6': 'Ajuste con juego mínimo posible igual a cero; centrado preciso y montaje deslizante.',
    'H7/k6': 'Ajuste de transición; puede producir pequeño juego o pequeña interferencia.',
    'H7/m6': 'Transición hacia apriete; aumenta la probabilidad de interferencia.',
    'H7/n6': 'Transición/apriete más marcado; útil cuando se busca mayor fijación.',
    'H7/p6': 'Ajuste de interferencia; normalmente requiere montaje por presión o diferencia térmica.',
}

@dataclass(frozen=True)
class FitResult:
    nominal_mm: float
    designation: str
    hole_EI_um: float
    hole_ES_um: float
    shaft_ei_um: float
    shaft_es_um: float
    hole_min_mm: float
    hole_max_mm: float
    shaft_min_mm: float
    shaft_max_mm: float
    clearance_min_mm: float
    clearance_max_mm: float
    fit_type: str
    purpose: str
    range_label: str


def _range_index(d: float) -> int:
    if not (0 < d <= 500):
        raise ValueError('El diámetro nominal automático debe estar entre 0 y 500 mm.')
    for i, (lo, hi) in enumerate(_RANGES):
        if (i == 0 and d <= hi) or (lo < d <= hi):
            return i
    raise ValueError('Diámetro fuera del rango de la tabla.')


def _classify(clear_min: float, clear_max: float) -> str:
    # clear = hole - shaft. Positive => juego; negative => interferencia.
    eps = 1e-12
    if clear_min >= -eps:
        return 'Juego'
    if clear_max <= eps:
        return 'Interferencia'
    return 'Transición'


def iso286_h7_fit(nominal_mm: float, designation: str) -> FitResult:
    if not designation.startswith('H7/'):
        raise ValueError('Esta versión automática trabaja con sistema base agujero H7/*.')
    shaft = designation.split('/', 1)[1]
    if shaft not in _SHAFTS:
        raise ValueError(f'Ajuste automático no disponible: {designation}')
    i = _range_index(float(nominal_mm))
    lo, hi = _RANGES[i]
    hole_EI, hole_ES = 0.0, float(_H7_ES[i])
    shaft_es, shaft_ei = map(float, _SHAFTS[shaft][i])
    nom = float(nominal_mm)
    hmin, hmax = nom + hole_EI/1000, nom + hole_ES/1000
    smin, smax = nom + shaft_ei/1000, nom + shaft_es/1000
    cmin = hmin - smax
    cmax = hmax - smin
    return FitResult(
        nominal_mm=nom,
        designation=designation,
        hole_EI_um=hole_EI,
        hole_ES_um=hole_ES,
        shaft_ei_um=shaft_ei,
        shaft_es_um=shaft_es,
        hole_min_mm=hmin,
        hole_max_mm=hmax,
        shaft_min_mm=smin,
        shaft_max_mm=smax,
        clearance_min_mm=cmin,
        clearance_max_mm=cmax,
        fit_type=_classify(cmin, cmax),
        purpose=_PRESET_PURPOSE.get(designation, ''),
        range_label=f'>{lo:g}–{hi:g} mm' if lo > 0 else f'0–{hi:g} mm',
    )


def manual_fit(nominal_mm: float, hole_EI_um: float, hole_ES_um: float, shaft_ei_um: float, shaft_es_um: float) -> FitResult:
    nom = float(nominal_mm)
    if hole_EI_um > hole_ES_um:
        raise ValueError('Para el agujero, EI debe ser menor o igual que ES.')
    if shaft_ei_um > shaft_es_um:
        raise ValueError('Para el eje, ei debe ser menor o igual que es.')
    hmin, hmax = nom + hole_EI_um/1000, nom + hole_ES_um/1000
    smin, smax = nom + shaft_ei_um/1000, nom + shaft_es_um/1000
    cmin, cmax = hmin - smax, hmax - smin
    return FitResult(
        nominal_mm=nom,
        designation='Manual',
        hole_EI_um=float(hole_EI_um),
        hole_ES_um=float(hole_ES_um),
        shaft_ei_um=float(shaft_ei_um),
        shaft_es_um=float(shaft_es_um),
        hole_min_mm=hmin,
        hole_max_mm=hmax,
        shaft_min_mm=smin,
        shaft_max_mm=smax,
        clearance_min_mm=cmin,
        clearance_max_mm=cmax,
        fit_type=_classify(cmin,cmax),
        purpose='Definido manualmente por el usuario.',
        range_label='Manual',
    )


def actual_dimensions(fit: FitResult, hole_pct: float, shaft_pct: float) -> tuple[float, float, float]:
    hp = min(1.0, max(0.0, float(hole_pct)))
    sp = min(1.0, max(0.0, float(shaft_pct)))
    dh = fit.hole_min_mm + hp * (fit.hole_max_mm - fit.hole_min_mm)
    ds = fit.shaft_min_mm + sp * (fit.shaft_max_mm - fit.shaft_min_mm)
    return dh, ds, dh-ds


def clearance_summary(fit: FitResult) -> dict:
    if fit.fit_type == 'Juego':
        return {
            'label1':'Juego mínimo', 'value1_mm':max(0.0,fit.clearance_min_mm),
            'label2':'Juego máximo', 'value2_mm':max(0.0,fit.clearance_max_mm),
        }
    if fit.fit_type == 'Interferencia':
        return {
            'label1':'Interferencia mínima', 'value1_mm':max(0.0,-fit.clearance_max_mm),
            'label2':'Interferencia máxima', 'value2_mm':max(0.0,-fit.clearance_min_mm),
        }
    return {
        'label1':'Juego máximo posible', 'value1_mm':max(0.0,fit.clearance_max_mm),
        'label2':'Interferencia máxima posible', 'value2_mm':max(0.0,-fit.clearance_min_mm),
    }
