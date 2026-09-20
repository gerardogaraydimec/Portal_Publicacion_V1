from __future__ import annotations

import math
import re
from dataclasses import dataclass

IT_MULTIPLIERS = {
    5: 7.0,
    6: 10.0,
    7: 16.0,
    8: 25.0,
    9: 40.0,
    10: 64.0,
    11: 100.0,
    12: 160.0,
    13: 250.0,
    14: 400.0,
    15: 640.0,
    16: 1000.0,
}

SIZE_STEPS = [
    (3.0, 6.0),
    (6.0, 10.0),
    (10.0, 18.0),
    (18.0, 30.0),
    (30.0, 50.0),
    (50.0, 80.0),
    (80.0, 120.0),
    (120.0, 180.0),
    (180.0, 250.0),
    (250.0, 315.0),
    (315.0, 400.0),
    (400.0, 500.0),
]


@dataclass
class Zone:
    symbol: str
    grade: int
    lower_um: float
    upper_um: float
    tolerance_um: float
    method: str


@dataclass
class FitResult:
    ok: bool
    message: str
    nominal_mm: float
    hole: Zone | None
    shaft: Zone | None
    hole_min_mm: float | None
    hole_max_mm: float | None
    shaft_min_mm: float | None
    shaft_max_mm: float | None
    clearance_min_um: float | None
    clearance_max_um: float | None
    interference_min_um: float | None
    interference_max_um: float | None
    fit_type: str | None
    size_step: tuple[float, float] | None
    Dm_mm: float | None
    i_um: float | None


def round_half_up(x: float, ndigits: int = 0) -> float:
    factor = 10**ndigits
    return math.floor(x * factor + 0.5) / factor


def get_size_step(nominal_mm: float) -> tuple[float, float]:
    if not (3.0 < nominal_mm <= 500.0):
        raise ValueError("El modo ISO asistido trabaja con tamaños nominales mayores que 3 mm y hasta 500 mm.")
    for low, high in SIZE_STEPS:
        if low < nominal_mm <= high:
            return low, high
    raise ValueError("No se encontró el intervalo nominal correspondiente.")


def geometric_mean_step(step: tuple[float, float]) -> float:
    low, high = step
    return math.sqrt(low * high)


def tolerance_unit_i(Dm_mm: float) -> float:
    """Standard tolerance factor i in micrometres for sizes up to 500 mm."""
    return 0.45 * (Dm_mm ** (1.0 / 3.0)) + 0.001 * Dm_mm


def it_width_um(nominal_mm: float, grade: int) -> tuple[float, tuple[float, float], float, float]:
    if grade not in IT_MULTIPLIERS:
        raise ValueError("Este módulo calcula automáticamente grados IT5 a IT16.")
    step = get_size_step(nominal_mm)
    Dm = geometric_mean_step(step)
    i = tolerance_unit_i(Dm)
    width = round_half_up(IT_MULTIPLIERS[grade] * i, 0)
    return width, step, Dm, i


def shaft_zone(nominal_mm: float, letter: str, grade: int) -> Zone:
    letter = letter.lower()
    width, step, Dm, _ = it_width_um(nominal_mm, grade)

    if letter == "d":
        es = -round_half_up(16.0 * Dm**0.44, 0)
        ei = es - width
        method = r"e_s=-16D_m^{0.44}"
    elif letter == "e":
        es = -round_half_up(11.0 * Dm**0.41, 0)
        ei = es - width
        method = r"e_s=-11D_m^{0.41}"
    elif letter == "f":
        es = -round_half_up(5.5 * Dm**0.41, 0)
        ei = es - width
        method = r"e_s=-5.5D_m^{0.41}"
    elif letter == "g":
        es = -round_half_up(2.5 * Dm**0.34, 0)
        ei = es - width
        method = r"e_s=-2.5D_m^{0.34}"
    elif letter == "h":
        es = 0.0
        ei = es - width
        method = r"e_s=0"
    elif letter == "js":
        es = width / 2.0
        ei = -width / 2.0
        method = r"e_s\approx+\frac{IT}{2},\quad e_i\approx-\frac{IT}{2}"
    elif letter == "k":
        if not (4 <= grade <= 7):
            raise ValueError("Para k automático, este módulo limita el cálculo a grados IT4–IT7.")
        ei = round_half_up(0.6 * (Dm ** (1.0 / 3.0)), 0)
        es = ei + width
        method = r"e_i=+0.6\sqrt[3]{D_m}"
    elif letter == "m":
        it7, *_ = it_width_um(nominal_mm, 7)
        it6, *_ = it_width_um(nominal_mm, 6)
        ei = it7 - it6
        es = ei + width
        method = r"e_i=IT7-IT6"
    elif letter == "n":
        ei = round_half_up(5.0 * Dm**0.34, 0)
        es = ei + width
        method = r"e_i=+5D_m^{0.34}"
    else:
        raise ValueError(f"La posición de eje '{letter}' no está implementada en el modo automático.")

    return Zone(letter, grade, float(ei), float(es), float(width), method)


def hole_zone(nominal_mm: float, letter: str, grade: int) -> Zone:
    letter = letter.upper()
    width, step, Dm, _ = it_width_um(nominal_mm, grade)

    if letter == "H":
        EI = 0.0
        ES = width
        method = r"EI=0"
    elif letter in {"D", "E", "F", "G"}:
        # General symmetry with same-letter shaft fundamental deviation.
        shaft_letter = letter.lower()
        shaft_ref = shaft_zone(nominal_mm, shaft_letter, grade)
        EI = -shaft_ref.upper_um
        ES = EI + width
        method = rf"EI=-e_s({shaft_letter})"
    else:
        raise ValueError(f"La posición de agujero '{letter}' no está implementada en el modo automático.")

    return Zone(letter, grade, float(EI), float(ES), float(width), method)


def classify_fit(clearance_min_um: float, clearance_max_um: float) -> str:
    eps = 1e-9
    if clearance_min_um >= -eps:
        if abs(clearance_min_um) < eps:
            return "Con juego · línea a línea posible"
        return "Con juego"
    if clearance_max_um <= eps:
        if abs(clearance_max_um) < eps:
            return "Con interferencia · línea a línea posible"
        return "Con interferencia"
    return "De transición"


def make_fit(nominal_mm: float, hole: Zone, shaft: Zone) -> FitResult:
    hole_min = nominal_mm + hole.lower_um / 1000.0
    hole_max = nominal_mm + hole.upper_um / 1000.0
    shaft_min = nominal_mm + shaft.lower_um / 1000.0
    shaft_max = nominal_mm + shaft.upper_um / 1000.0

    cmin = (hole_min - shaft_max) * 1000.0
    cmax = (hole_max - shaft_min) * 1000.0

    # Interference is expressed positive when material overlap exists.
    imax = max(0.0, -cmin)
    imin = max(0.0, -cmax)

    try:
        step = get_size_step(nominal_mm)
        Dm = geometric_mean_step(step)
        i = tolerance_unit_i(Dm)
    except Exception:
        step = None
        Dm = None
        i = None

    return FitResult(
        True,
        "OK",
        nominal_mm,
        hole,
        shaft,
        hole_min,
        hole_max,
        shaft_min,
        shaft_max,
        cmin,
        cmax,
        imin,
        imax,
        classify_fit(cmin, cmax),
        step,
        Dm,
        i,
    )


def automatic_hole_basis_fit(nominal_mm: float, hole_grade: int, shaft_letter: str, shaft_grade: int) -> FitResult:
    hole = hole_zone(nominal_mm, "H", hole_grade)
    shaft = shaft_zone(nominal_mm, shaft_letter, shaft_grade)
    return make_fit(nominal_mm, hole, shaft)


def automatic_shaft_basis_fit(nominal_mm: float, hole_letter: str, hole_grade: int, shaft_grade: int) -> FitResult:
    hole = hole_zone(nominal_mm, hole_letter, hole_grade)
    shaft = shaft_zone(nominal_mm, "h", shaft_grade)
    return make_fit(nominal_mm, hole, shaft)


def manual_fit(
    nominal_mm: float,
    hole_symbol: str,
    hole_grade: int,
    EI_um: float,
    ES_um: float,
    shaft_symbol: str,
    shaft_grade: int,
    ei_um: float,
    es_um: float,
) -> FitResult:
    if ES_um < EI_um:
        return FitResult(False, "En el agujero debe cumplirse ES ≥ EI.", nominal_mm, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
    if es_um < ei_um:
        return FitResult(False, "En el eje debe cumplirse es ≥ ei.", nominal_mm, None, None, None, None, None, None, None, None, None, None, None, None, None, None)

    hole = Zone(hole_symbol, hole_grade, EI_um, ES_um, ES_um - EI_um, "Valores ingresados desde tabla/fuente")
    shaft = Zone(shaft_symbol, shaft_grade, ei_um, es_um, es_um - ei_um, "Valores ingresados desde tabla/fuente")
    return make_fit(nominal_mm, hole, shaft)


def parse_fit_designation(text: str) -> tuple[str, int, str, int]:
    """
    Parses H7/g6, H7-g6, H7 g6 or Ø50 H7/g6 if nominal is handled elsewhere.
    """
    m = re.search(r"([A-Z]{1,2})(\d{1,2})\s*[/\-\s]\s*([a-z]{1,2})(\d{1,2})", text.strip())
    if not m:
        raise ValueError("No se pudo interpretar la designación. Usa por ejemplo H7/g6.")
    return m.group(1), int(m.group(2)), m.group(3), int(m.group(4))


def compare_designations(nominal_mm: float, designations: list[str]) -> list[dict]:
    rows = []
    for des in designations:
        Hletter, Hgrade, sletter, sgrade = parse_fit_designation(des)
        if Hletter != "H":
            rows.append({"Ajuste": des, "Estado": "Manual requerido"})
            continue
        try:
            fit = automatic_hole_basis_fit(nominal_mm, Hgrade, sletter, sgrade)
            rows.append({
                "Ajuste": des,
                "Tipo": fit.fit_type,
                "Juego mín. [µm]": round(fit.clearance_min_um),
                "Juego máx. [µm]": round(fit.clearance_max_um),
                "Agujero mín. [mm]": round(fit.hole_min_mm, 3),
                "Agujero máx. [mm]": round(fit.hole_max_mm, 3),
                "Eje mín. [mm]": round(fit.shaft_min_mm, 3),
                "Eje máx. [mm]": round(fit.shaft_max_mm, 3),
                "Estado": "Calculado",
            })
        except Exception as exc:
            rows.append({"Ajuste": des, "Estado": f"Revisar: {exc}"})
    return rows


def measured_status(value_mm: float, min_mm: float, max_mm: float) -> str:
    if value_mm < min_mm:
        return "Bajo límite"
    if value_mm > max_mm:
        return "Sobre límite"
    return "Dentro de límites"
