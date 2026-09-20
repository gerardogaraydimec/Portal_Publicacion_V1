from __future__ import annotations

PRESETS = {
    "Eje Ø50 g6 · micrómetro": {
        "description": "Control de un eje de ajuste con tolerancia estrecha mediante varias lecturas micrométricas.",
        "nominal_mm": 50.000,
        "lsl_mm": 49.975,
        "usl_mm": 49.991,
        "readings_mm": [49.984, 49.985, 49.983, 49.984, 49.985],
        "resolution_mm": 0.001,
        "cal_correction_um": 0.0,
        "cal_U_um": 2.0,
        "cal_k": 2.0,
        "temp_C": 20.0,
        "temp_u_C": 0.5,
        "alpha_per_C": 12.0e-6,
        "method_u_um": 1.0,
        "operator_u_um": 1.0,
        "focus": "Caso conectado al módulo de ajustes: el valor medido puede quedar dentro de límites y aun así requerir revisar incertidumbre antes de declarar conformidad."
    },
    "Agujero Ø50 H7 · alesómetro": {
        "description": "Verificación de un agujero H7 usando lecturas repetidas y una cadena de medición con patrón de referencia.",
        "nominal_mm": 50.000,
        "lsl_mm": 50.000,
        "usl_mm": 50.025,
        "readings_mm": [50.011, 50.012, 50.011, 50.013, 50.012],
        "resolution_mm": 0.001,
        "cal_correction_um": 1.0,
        "cal_U_um": 3.0,
        "cal_k": 2.0,
        "temp_C": 20.5,
        "temp_u_C": 0.5,
        "alpha_per_C": 12.0e-6,
        "method_u_um": 2.0,
        "operator_u_um": 1.0,
        "focus": "Sirve para distinguir entre la repetibilidad del indicador y la incertidumbre total del resultado."
    },
    "Dimensión 250 mm · CMM / comparador dimensional": {
        "description": "Caso de dimensión mayor para visualizar cómo la temperatura adquiere mayor importancia en el presupuesto.",
        "nominal_mm": 250.000,
        "lsl_mm": 249.950,
        "usl_mm": 250.050,
        "readings_mm": [250.008, 250.006, 250.009, 250.007, 250.008],
        "resolution_mm": 0.001,
        "cal_correction_um": -1.0,
        "cal_U_um": 4.0,
        "cal_k": 2.0,
        "temp_C": 21.5,
        "temp_u_C": 0.7,
        "alpha_per_C": 12.0e-6,
        "method_u_um": 2.0,
        "operator_u_um": 1.0,
        "focus": "Muestra por qué una medición dimensional larga es más sensible a temperatura y estrategia de medición."
    },
    "Pie de metro · control general": {
        "description": "Caso de control dimensional general para mostrar que una buena resolución visual no garantiza por sí sola una incertidumbre pequeña.",
        "nominal_mm": 100.000,
        "lsl_mm": 99.900,
        "usl_mm": 100.100,
        "readings_mm": [100.020, 100.010, 100.020, 100.030, 100.020],
        "resolution_mm": 0.020,
        "cal_correction_um": 0.0,
        "cal_U_um": 20.0,
        "cal_k": 2.0,
        "temp_C": 20.0,
        "temp_u_C": 1.0,
        "alpha_per_C": 12.0e-6,
        "method_u_um": 10.0,
        "operator_u_um": 8.0,
        "focus": "Permite comparar tolerancia, resolución e incertidumbre total y entender cuándo un pie de metro deja de ser apropiado."
    },
    "Personalizado": {
        "description": "Define tus propios límites, lecturas y contribuciones de incertidumbre.",
        "nominal_mm": 50.000,
        "lsl_mm": 49.980,
        "usl_mm": 50.020,
        "readings_mm": [50.000, 50.001, 49.999, 50.000, 50.001],
        "resolution_mm": 0.001,
        "cal_correction_um": 0.0,
        "cal_U_um": 2.0,
        "cal_k": 2.0,
        "temp_C": 20.0,
        "temp_u_C": 0.5,
        "alpha_per_C": 12.0e-6,
        "method_u_um": 1.0,
        "operator_u_um": 1.0,
        "focus": "Permite construir un presupuesto simplificado de incertidumbre para una característica dimensional."
    },
}

MATERIALS = {
    "Acero al carbono · referencia": 12.0e-6,
    "Acero inoxidable austenítico · referencia": 17.0e-6,
    "Hierro fundido · referencia": 10.5e-6,
    "Aluminio · referencia": 23.0e-6,
    "Bronce · referencia": 18.0e-6,
    "Personalizado": None,
}

CONCEPTS = [
    {
        "term": "Mensurando",
        "short": "Magnitud que se pretende medir.",
        "engineering": "Antes de medir hay que definir exactamente qué dimensión, condición, dirección, temperatura y método representan el resultado."
    },
    {
        "term": "Indicación",
        "short": "Valor que entrega el sistema de medición.",
        "engineering": "No es automáticamente el resultado final: puede requerir correcciones y evaluación de incertidumbre."
    },
    {
        "term": "Resultado de medición",
        "short": "Valor atribuido al mensurando acompañado de información relevante.",
        "engineering": "En este módulo se expresa como valor corregido y, cuando corresponde, incertidumbre expandida."
    },
    {
        "term": "Error de medición",
        "short": "Diferencia entre un valor medido y un valor de referencia.",
        "engineering": "No debe confundirse con incertidumbre. El error puede ser desconocido; la incertidumbre cuantifica la duda asociada al resultado."
    },
    {
        "term": "Corrección",
        "short": "Compensación aplicada a un efecto sistemático estimado.",
        "engineering": "Ejemplo: corrección indicada en un certificado de calibración o corrección térmica a 20 °C."
    },
    {
        "term": "Precisión",
        "short": "Cercanía entre indicaciones repetidas bajo condiciones definidas.",
        "engineering": "Se relaciona con dispersión; no significa necesariamente cercanía al valor verdadero."
    },
    {
        "term": "Repetibilidad",
        "short": "Precisión bajo un mismo conjunto de condiciones de medición.",
        "engineering": "Mismo método, equipo, operador, lugar y condiciones durante un intervalo corto."
    },
    {
        "term": "Reproducibilidad",
        "short": "Precisión bajo condiciones de medición diferentes.",
        "engineering": "Puede involucrar distintos operadores, equipos, laboratorios o periodos."
    },
    {
        "term": "Resolución",
        "short": "Menor cambio que puede producir un cambio perceptible en la indicación.",
        "engineering": "Una resolución de 1 µm no significa una incertidumbre de 1 µm."
    },
    {
        "term": "Calibración",
        "short": "Operación que relaciona indicaciones con valores de referencia y sus incertidumbres.",
        "engineering": "Calibrar no es lo mismo que ajustar el instrumento."
    },
    {
        "term": "Trazabilidad metrológica",
        "short": "Propiedad de un resultado relacionado con una referencia mediante una cadena documentada de calibraciones.",
        "engineering": "La cadena debe incluir contribuciones de incertidumbre."
    },
    {
        "term": "Incertidumbre de medición",
        "short": "Parámetro no negativo que caracteriza la dispersión de valores atribuidos al mensurando.",
        "engineering": "Permite juzgar qué tan concluyente es una medición respecto de una especificación."
    },
]

QUALITY_CHECKLIST = [
    "Plano/especificación vigente y característica claramente identificada.",
    "Mensurando definido: ubicación, orientación, condición superficial y temperatura.",
    "Equipo apropiado para rango, resolución y geometría.",
    "Estado de calibración vigente y certificado disponible.",
    "Correcciones del certificado aplicadas cuando corresponda.",
    "Pieza y equipo limpios, sin rebabas o contaminación.",
    "Temperatura y estabilización térmica verificadas.",
    "Fuerza de medición, alineación y estrategia de contacto controladas.",
    "Número de lecturas suficiente para el propósito.",
    "Resultado registrado con unidad, equipo, operador y fecha.",
    "Incertidumbre y regla de decisión definidas si se declara conformidad.",
]


INSTRUMENT_GUIDANCE = [
    {
        "instrument": "Pie de metro / calibre",
        "best_for": "Control dimensional general, diámetros y longitudes con tolerancias relativamente amplias.",
        "watch": "Presión manual, paralaje/lectura, limpieza de mordazas, alineación y resolución.",
    },
    {
        "instrument": "Micrómetro exterior",
        "best_for": "Diámetros exteriores y espesores con tolerancias estrechas.",
        "watch": "Fuerza de medición, temperatura, limpieza, alineación y forma local de la superficie.",
    },
    {
        "instrument": "Alesómetro / comparador interior",
        "best_for": "Diámetros interiores y evaluación comparativa respecto de un patrón.",
        "watch": "Punto de inversión, patrón de puesta a cero, orientación, ovalidad y conicidad.",
    },
    {
        "instrument": "CMM",
        "best_for": "Dimensiones, posición, orientación y geometrías complejas con estrategia programada.",
        "watch": "Sistema de coordenadas, palpado, compensaciones, estrategia, temperatura y modelo de incertidumbre.",
    },
]
