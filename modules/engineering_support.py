from __future__ import annotations

import math
from dataclasses import dataclass


MATERIALS = {
    "Acero al carbono · referencia": {
        "alpha": 12.0e-6,
        "note": "Coeficiente lineal de referencia; depende de composición y temperatura."
    },
    "Acero inoxidable austenítico · referencia": {
        "alpha": 17.0e-6,
        "note": "Valor de referencia; confirmar para el grado específico."
    },
    "Hierro fundido · referencia": {
        "alpha": 10.5e-6,
        "note": "Valor de referencia; confirmar para la fundición específica."
    },
    "Aluminio · referencia": {
        "alpha": 23.0e-6,
        "note": "Valor de referencia; confirmar aleación y rango térmico."
    },
    "Bronce · referencia": {
        "alpha": 18.0e-6,
        "note": "Valor de referencia; confirmar aleación."
    },
    "Personalizado": {
        "alpha": None,
        "note": "Ingresa el coeficiente de expansión lineal del material."
    },
}


@dataclass
class ThermalFitResult:
    hole_ref_mm: float
    shaft_ref_mm: float
    hole_op_mm: float
    shaft_op_mm: float
    clearance_ref_um: float
    clearance_op_um: float
    delta_clearance_um: float


@dataclass
class CapabilityResult:
    cp: float | None
    cpk: float | None
    cpu: float | None
    cpl: float | None
    centered_offset_um: float
    tolerance_um: float
    six_sigma_um: float


def thermal_fit(
    hole_ref_mm: float,
    shaft_ref_mm: float,
    alpha_hole_per_C: float,
    alpha_shaft_per_C: float,
    temp_ref_C: float,
    temp_hole_C: float,
    temp_shaft_C: float,
) -> ThermalFitResult:
    dTh = temp_hole_C - temp_ref_C
    dTs = temp_shaft_C - temp_ref_C

    hole_op = hole_ref_mm * (1.0 + alpha_hole_per_C * dTh)
    shaft_op = shaft_ref_mm * (1.0 + alpha_shaft_per_C * dTs)

    cref = (hole_ref_mm - shaft_ref_mm) * 1000.0
    cop = (hole_op - shaft_op) * 1000.0

    return ThermalFitResult(
        hole_ref_mm=hole_ref_mm,
        shaft_ref_mm=shaft_ref_mm,
        hole_op_mm=hole_op,
        shaft_op_mm=shaft_op,
        clearance_ref_um=cref,
        clearance_op_um=cop,
        delta_clearance_um=cop - cref,
    )


def temperature_change_for_target_clearance(
    nominal_mm: float,
    current_clearance_um: float,
    target_clearance_um: float,
    alpha_per_C: float,
    mode: str,
) -> float | None:
    """
    Approximate single-component thermal conditioning.
    mode:
      - "Calentar agujero"
      - "Enfriar eje"
    Returns magnitude of temperature change in °C.
    """
    if nominal_mm <= 0 or alpha_per_C <= 0:
        return None

    required_change_um = target_clearance_um - current_clearance_um
    if required_change_um <= 0:
        return 0.0

    required_mm = required_change_um / 1000.0
    dT = required_mm / (alpha_per_C * nominal_mm)
    return abs(dT)


def process_capability(lsl_mm: float, usl_mm: float, mean_mm: float, sigma_mm: float) -> CapabilityResult:
    if usl_mm <= lsl_mm or sigma_mm <= 0:
        return CapabilityResult(None, None, None, None, 0.0, max(0.0, (usl_mm-lsl_mm)*1000.0), max(0.0, 6*sigma_mm*1000.0))

    cp = (usl_mm - lsl_mm) / (6.0 * sigma_mm)
    cpu = (usl_mm - mean_mm) / (3.0 * sigma_mm)
    cpl = (mean_mm - lsl_mm) / (3.0 * sigma_mm)
    cpk = min(cpu, cpl)
    midpoint = 0.5 * (usl_mm + lsl_mm)

    return CapabilityResult(
        cp=cp,
        cpk=cpk,
        cpu=cpu,
        cpl=cpl,
        centered_offset_um=(mean_mm - midpoint) * 1000.0,
        tolerance_um=(usl_mm - lsl_mm) * 1000.0,
        six_sigma_um=6.0 * sigma_mm * 1000.0,
    )


def normal_curve_points(mean_mm: float, sigma_mm: float, lsl_mm: float, usl_mm: float, n: int = 260):
    if sigma_mm <= 0:
        return [], []
    xmin = min(lsl_mm, mean_mm - 4.5*sigma_mm)
    xmax = max(usl_mm, mean_mm + 4.5*sigma_mm)
    if xmax <= xmin:
        xmax = xmin + 1e-6

    xs = [xmin + (xmax-xmin)*i/(n-1) for i in range(n)]
    ys = [
        (1.0/(sigma_mm*math.sqrt(2*math.pi))) * math.exp(-0.5*((x-mean_mm)/sigma_mm)**2)
        for x in xs
    ]
    return xs, ys


def mounting_guidance(fit_type: str, clearance_min_um: float, clearance_max_um: float) -> list[str]:
    fit_lower = (fit_type or "").lower()
    notes = []

    if "juego" in fit_lower:
        notes.extend([
            "Evaluar montaje manual o deslizante y verificar que el juego mínimo siga siendo suficiente en operación.",
            "Si existe movimiento relativo, revisar lubricación, contaminación, desgaste y temperatura.",
            "Si el ajuste tiene función de posicionamiento, un juego excesivo puede afectar concentricidad o repetibilidad."
        ])
    elif "interferencia" in fit_lower:
        notes.extend([
            "Evaluar montaje por prensa, calentamiento del alojamiento, enfriamiento del eje o una combinación controlada.",
            "No definir la fuerza de montaje solo con la interferencia diametral: también importan longitud de contacto, espesores, módulo elástico, Poisson y fricción.",
            "Revisar tensiones de montaje, deformación del cubo/alojamiento y posibilidad de desmontaje."
        ])
    else:
        notes.extend([
            "El montaje puede resultar con juego o interferencia según las dimensiones reales fabricadas.",
            "Si la repetibilidad de montaje es crítica, conviene controlar más estrechamente el proceso o seleccionar otra clase.",
            "Definir explícitamente si se acepta montaje manual, ligero a presión o térmico."
        ])

    if clearance_min_um < 0 < clearance_max_um:
        notes.append("La zona de transición cruza la condición línea a línea; el método de montaje puede variar pieza a pieza.")

    return notes


def operational_checks(
    rotating: bool,
    sliding: bool,
    shock_vibration: bool,
    frequent_disassembly: bool,
    lubrication_required: bool,
    contamination: bool,
    thermal_gradient: bool,
    thin_wall: bool,
) -> list[str]:
    checks = []

    if rotating:
        checks.append("Rotación: revisar centrado, estabilidad del ajuste y comportamiento dinámico a la velocidad de servicio.")
    if sliding:
        checks.append("Deslizamiento: verificar juego mínimo en caliente, lubricación y riesgo de gripado.")
    if shock_vibration:
        checks.append("Choque/vibración: revisar micromovimiento, fretting y pérdida de posicionamiento.")
    if frequent_disassembly:
        checks.append("Desmontaje frecuente: evitar interferencias innecesarias y considerar desgaste de las superficies de ajuste.")
    if lubrication_required:
        checks.append("Lubricación: confirmar que el juego permita formación/distribución de película según el mecanismo.")
    if contamination:
        checks.append("Contaminación: considerar partículas, sellado y riesgo de bloqueo en ajustes de juego reducido.")
    if thermal_gradient:
        checks.append("Gradiente térmico: calcular el ajuste a temperatura de operación; el juego a 20 °C puede no representar la condición real.")
    if thin_wall:
        checks.append("Pared delgada: una interferencia puede ovalizar o expandir el componente; evaluar deformación estructural.")

    if not checks:
        checks.append("No se seleccionaron condiciones especiales. Mantener revisión de carga, temperatura, lubricación, montaje y mantenibilidad.")

    return checks


def suggested_quality_plan(characteristic: str, criticality: str, stage: str) -> list[dict]:
    criticality = criticality.lower()
    stage = stage.lower()

    rows = [
        {
            "Etapa": "Recepción / preparación",
            "Control": "Identificación de material y plano vigente",
            "Registro": "Trazabilidad de lote / revisión documental",
        },
        {
            "Etapa": "Proceso",
            "Control": f"Dimensión funcional: {characteristic}",
            "Registro": "Registro dimensional con equipo identificado",
        },
        {
            "Etapa": "Final",
            "Control": "Límites dimensionales y estado superficial relevante",
            "Registro": "Informe final / hoja de inspección",
        },
    ]

    if "alta" in criticality:
        rows.insert(2, {
            "Etapa": "Proceso",
            "Control": "Verificación intermedia antes de operación irreversible",
            "Registro": "Liberación de etapa / punto de espera",
        })
        rows.append({
            "Etapa": "Metrología",
            "Control": "Confirmación de equipo, calibración y regla de decisión",
            "Registro": "Evidencia metrológica / incertidumbre cuando aplique",
        })

    if "montaje" in stage:
        rows.append({
            "Etapa": "Montaje",
            "Control": "Temperatura de piezas, limpieza, lubricación y método de inserción",
            "Registro": "Checklist de montaje",
        })

    return rows
