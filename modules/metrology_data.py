from __future__ import annotations

AUTO_HOLE_BASE_SHAFTS = ["d", "e", "f", "g", "h", "js", "k", "m", "n"]
AUTO_SHAFT_BASE_HOLES = ["D", "E", "F", "G", "H"]

COMMON_FITS = [
    {
        "designation": "H8/f7",
        "intent": "Juego amplio o movimiento libre",
        "note": "Familia ilustrativa para mecanismos donde se busca juego claramente positivo."
    },
    {
        "designation": "H7/g6",
        "intent": "Guiado con juego pequeño",
        "note": "Familia ilustrativa para guiado y posicionamiento con juego controlado."
    },
    {
        "designation": "H7/h6",
        "intent": "Juego mínimo / línea a línea posible",
        "note": "El eje h tiene desviación superior igual a cero."
    },
    {
        "designation": "H7/js6",
        "intent": "Transición centrada",
        "note": "Zona del eje centrada aproximadamente sobre la línea cero."
    },
    {
        "designation": "H7/k6",
        "intent": "Transición",
        "note": "La zona del eje se desplaza levemente sobre la línea cero."
    },
    {
        "designation": "H7/m6",
        "intent": "Transición hacia interferencia",
        "note": "Familia ilustrativa para centrado más firme; depende del tamaño."
    },
    {
        "designation": "H7/n6",
        "intent": "Transición firme",
        "note": "Zona del eje claramente desplazada sobre cero; puede producir juego pequeño o interferencia según límites."
    },
]

FUNCTION_STARTERS = {
    "Movimiento libre": ["H8/f7", "H7/g6"],
    "Guiado preciso": ["H7/g6", "H7/h6"],
    "Centrado desmontable": ["H7/h6", "H7/js6", "H7/k6"],
    "Montaje de transición": ["H7/js6", "H7/k6", "H7/m6"],
    "Transición firme": ["H7/m6", "H7/n6"],
}

PROCESS_GUIDANCE = [
    {
        "it": "IT5–IT6",
        "level": "Alta precisión",
        "processes": "Rectificado, bruñido, lapeado, mandrinado/escariado de precisión.",
        "note": "Depende fuertemente de máquina, material, estabilidad térmica y control de proceso."
    },
    {
        "it": "IT7–IT8",
        "level": "Precisión de ajuste",
        "processes": "Escariado, torneado de terminación, mandrinado, fresado fino.",
        "note": "Rango muy común para superficies funcionales de ajuste."
    },
    {
        "it": "IT9–IT11",
        "level": "Mecanizado general",
        "processes": "Torneado, fresado y taladrado bajo condiciones controladas.",
        "note": "Adecuado para muchas dimensiones funcionales no críticas."
    },
    {
        "it": "IT12–IT16",
        "level": "Proceso grueso",
        "processes": "Mecanizado desbaste, fundición, forja, estampado, según proceso.",
        "note": "Las capacidades reales deben obtenerse del proceso y proveedor específico."
    },
]

MEASUREMENT_GUIDANCE = [
    {
        "tol_um_min": 100.0,
        "instrument": "Pie de metro / calibre",
        "note": "Puede ser adecuado para control general si su resolución e incertidumbre son suficientes."
    },
    {
        "tol_um_min": 25.0,
        "instrument": "Micrómetro / alesómetro / comparador",
        "note": "Habitual cuando se requiere mayor resolución y repetibilidad."
    },
    {
        "tol_um_min": 10.0,
        "instrument": "Micrometría de alta resolución / CMM",
        "note": "Conviene revisar incertidumbre, temperatura y estrategia de medición."
    },
    {
        "tol_um_min": 0.0,
        "instrument": "Metrología de precisión especializada",
        "note": "Puede requerir CMM, sistemas neumáticos, comparadores de alta resolución o laboratorio controlado."
    },
]


MANUAL_EXAMPLES = {
    "H7/g6 · Ø50 · juego": {
        "nominal": 50.0,
        "hole_symbol": "H",
        "hole_grade": 7,
        "EI": 0.0,
        "ES": 25.0,
        "shaft_symbol": "g",
        "shaft_grade": 6,
        "ei": -25.0,
        "es": -9.0,
        "note": "Ejemplo de ajuste con juego."
    },
    "H7/k6 · Ø50 · transición": {
        "nominal": 50.0,
        "hole_symbol": "H",
        "hole_grade": 7,
        "EI": 0.0,
        "ES": 25.0,
        "shaft_symbol": "k",
        "shaft_grade": 6,
        "ei": 2.0,
        "es": 18.0,
        "note": "Ejemplo de ajuste de transición."
    },
    "H7/p6 · Ø50 · interferencia": {
        "nominal": 50.0,
        "hole_symbol": "H",
        "hole_grade": 7,
        "EI": 0.0,
        "ES": 25.0,
        "shaft_symbol": "p",
        "shaft_grade": 6,
        "ei": 26.0,
        "es": 42.0,
        "note": "Ejemplo de ajuste con interferencia. Valores de ejemplo para Ø50; para otros tamaños consulta la tabla correspondiente."
    },
}
