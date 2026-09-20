from __future__ import annotations

FLUIDS = {
    "Agua · 20 °C": {
        "rho": 998.2,
        "mu": 1.002e-3,
        "note": "Valor de referencia para agua alrededor de 20 °C."
    },
    "Agua de mar · referencia": {
        "rho": 1025.0,
        "mu": 1.08e-3,
        "note": "Valor pedagógico de referencia; depende de salinidad y temperatura."
    },
    "Aceite hidráulico ISO VG 46 · 40 °C aprox.": {
        "rho": 870.0,
        "mu": 0.0400,
        "note": "Referencia aproximada basada en ν≈46 cSt y ρ≈870 kg/m³."
    },
    "Personalizado": {
        "rho": None,
        "mu": None,
        "note": "Ingresa densidad y viscosidad dinámica."
    },
}

ROUGHNESS = {
    "Tubería hidráulicamente lisa": 0.0,
    "PVC / plástico liso · referencia": 0.0015,
    "Cobre estirado · referencia": 0.0015,
    "Acero comercial · referencia": 0.045,
    "Acero galvanizado · referencia": 0.15,
    "Hierro fundido · referencia": 0.26,
    "Hormigón liso · referencia": 0.30,
    "Personalizada": None,
}

FITTINGS = {
    "Entrada de borde vivo": {
        "K": 0.50,
        "symbol": "Entrada",
        "note": "Valor pedagógico típico; depende de la geometría real."
    },
    "Salida a depósito": {
        "K": 1.00,
        "symbol": "Salida",
        "note": "Valor pedagógico típico para descarga a gran depósito."
    },
    "Codo 90° estándar": {
        "K": 0.90,
        "symbol": "Codo 90°",
        "note": "Valor pedagógico típico; radio y fabricación modifican K."
    },
    "Codo 45°": {
        "K": 0.40,
        "symbol": "Codo 45°",
        "note": "Valor pedagógico típico."
    },
    "Tee · paso recto": {
        "K": 0.60,
        "symbol": "Tee",
        "note": "Valor pedagógico típico."
    },
    "Tee · ramal": {
        "K": 1.80,
        "symbol": "Tee ramal",
        "note": "Valor pedagógico típico."
    },
    "Válvula compuerta abierta": {
        "K": 0.15,
        "symbol": "Compuerta",
        "note": "Valor pedagógico típico; la apertura parcial incrementa fuertemente K."
    },
    "Válvula globo abierta": {
        "K": 10.0,
        "symbol": "Globo",
        "note": "Valor pedagógico típico; elevada pérdida localizada."
    },
    "Válvula bola abierta": {
        "K": 0.05,
        "symbol": "Bola",
        "note": "Valor pedagógico típico."
    },
    "Válvula de retención tipo clapeta": {
        "K": 2.0,
        "symbol": "Check",
        "note": "Valor pedagógico típico."
    },
    "K personalizado": {
        "K": None,
        "symbol": "K",
        "note": "Ingresa el coeficiente K según fabricante o fuente técnica."
    },
}

PRESETS = {
    "Agua · línea de acero industrial": {
        "fluid": "Agua · 20 °C",
        "roughness": "Acero comercial · referencia",
        "L_m": 30.0,
        "D_mm": 100.0,
        "Q_Ls": 20.0,
        "fittings": {
            "Entrada de borde vivo": 1,
            "Codo 90° estándar": 2,
            "Válvula compuerta abierta": 1,
            "Salida a depósito": 1,
        },
        "description": "Línea corta de proceso con accesorios típicos."
    },
    "Agua · tubería PVC": {
        "fluid": "Agua · 20 °C",
        "roughness": "PVC / plástico liso · referencia",
        "L_m": 80.0,
        "D_mm": 75.0,
        "Q_Ls": 8.0,
        "fittings": {
            "Entrada de borde vivo": 1,
            "Codo 90° estándar": 4,
            "Salida a depósito": 1,
        },
        "description": "Caso de tubería lisa con longitud significativa."
    },
    "Aceite hidráulico · línea de máquina": {
        "fluid": "Aceite hidráulico ISO VG 46 · 40 °C aprox.",
        "roughness": "Acero comercial · referencia",
        "L_m": 12.0,
        "D_mm": 25.0,
        "Q_Ls": 1.2,
        "fittings": {
            "Codo 90° estándar": 4,
            "Válvula de retención tipo clapeta": 1,
        },
        "description": "Caso viscoso para observar el efecto de Reynolds."
    },
}
