from __future__ import annotations

FLUIDS = {
    "Agua · 20 °C": {
        "rho": 998.2,
        "mu": 1.002e-3,
        "pv_kPa_abs": 2.34,
        "note": "Valores de referencia alrededor de 20 °C."
    },
    "Agua de mar · referencia": {
        "rho": 1025.0,
        "mu": 1.08e-3,
        "pv_kPa_abs": 2.34,
        "note": "Referencia pedagógica; depende de salinidad y temperatura."
    },
    "Aceite hidráulico ISO VG 46 · 40 °C aprox.": {
        "rho": 870.0,
        "mu": 0.0400,
        "pv_kPa_abs": 0.10,
        "note": "Referencia aproximada para trabajo pedagógico."
    },
    "Personalizado": {
        "rho": None,
        "mu": None,
        "pv_kPa_abs": None,
        "note": "Ingresa propiedades del fluido."
    },
}

ROUGHNESS = {
    "Tubería hidráulicamente lisa": 0.0,
    "PVC / plástico liso · referencia": 0.0015,
    "Cobre estirado · referencia": 0.0015,
    "Acero comercial · referencia": 0.045,
    "Acero galvanizado · referencia": 0.15,
    "Hierro fundido · referencia": 0.26,
    "Personalizada": None,
}

FITTINGS = {
    "Entrada de borde vivo": 0.50,
    "Salida a depósito": 1.00,
    "Codo 90° estándar": 0.90,
    "Codo 45°": 0.40,
    "Tee · paso recto": 0.60,
    "Tee · ramal": 1.80,
    "Válvula compuerta abierta": 0.15,
    "Válvula globo abierta": 10.0,
    "Válvula bola abierta": 0.05,
    "Válvula de retención tipo clapeta": 2.0,
    "K personalizado": None,
}

PRESETS = {
    "Transferencia entre estanques": {
        "description": "Bombeo desde un estanque abierto inferior hacia un estanque abierto elevado. La bomba debe vencer altura estática y pérdidas.",
        "fluid": "Agua · 20 °C",
        "roughness": "Acero comercial · referencia",
        "z1_m": 0.0,
        "z2_m": 18.0,
        "p1_kPa_g": 0.0,
        "p2_kPa_g": 0.0,
        "L_m": 120.0,
        "D_mm": 100.0,
        "fittings": {
            "Entrada de borde vivo": 1,
            "Codo 90° estándar": 4,
            "Válvula compuerta abierta": 1,
            "Válvula de retención tipo clapeta": 1,
            "Salida a depósito": 1,
        },
        "pump": {
            "H0_m": 46.0,
            "Qbep_Ls": 24.0,
            "Hbep_m": 34.0,
            "Qend_Ls": 40.0,
            "Hend_m": 12.0,
            "eta_max": 0.78,
        },
        "focus": "Permite ver con claridad cómo la altura estática desplaza la curva del sistema y cómo las pérdidas crecen con el caudal."
    },
    "Recirculación de agua industrial": {
        "description": "Circuito cerrado de recirculación. La altura estática neta es aproximadamente cero y la bomba trabaja principalmente contra las pérdidas.",
        "fluid": "Agua · 20 °C",
        "roughness": "Acero comercial · referencia",
        "z1_m": 0.0,
        "z2_m": 0.0,
        "p1_kPa_g": 0.0,
        "p2_kPa_g": 0.0,
        "L_m": 85.0,
        "D_mm": 80.0,
        "fittings": {
            "Codo 90° estándar": 6,
            "Válvula compuerta abierta": 2,
            "Tee · paso recto": 2,
        },
        "pump": {
            "H0_m": 35.0,
            "Qbep_Ls": 14.0,
            "Hbep_m": 25.0,
            "Qend_Ls": 25.0,
            "Hend_m": 8.0,
            "eta_max": 0.76,
        },
        "focus": "Es un buen caso para entender que una bomba puede ser necesaria aun cuando no exista diferencia de altura geométrica."
    },
    "Alimentación a recipiente presurizado": {
        "description": "La descarga debe llegar a un recipiente con presión positiva. La bomba debe aportar energía para presión, elevación y pérdidas.",
        "fluid": "Agua · 20 °C",
        "roughness": "Acero comercial · referencia",
        "z1_m": 0.0,
        "z2_m": 6.0,
        "p1_kPa_g": 0.0,
        "p2_kPa_g": 220.0,
        "L_m": 60.0,
        "D_mm": 80.0,
        "fittings": {
            "Entrada de borde vivo": 1,
            "Codo 90° estándar": 4,
            "Válvula de retención tipo clapeta": 1,
            "Válvula globo abierta": 1,
        },
        "pump": {
            "H0_m": 65.0,
            "Qbep_Ls": 12.0,
            "Hbep_m": 48.0,
            "Qend_Ls": 22.0,
            "Hend_m": 18.0,
            "eta_max": 0.74,
        },
        "focus": "Muestra que una diferencia de presión puede ser tan importante como la diferencia de cota en la altura total requerida."
    },
    "Circuito de refrigeración de máquina": {
        "description": "Circuito de proceso compacto con baja altura estática pero pérdidas significativas en tubería y accesorios.",
        "fluid": "Agua · 20 °C",
        "roughness": "Acero comercial · referencia",
        "z1_m": 0.0,
        "z2_m": 1.5,
        "p1_kPa_g": 0.0,
        "p2_kPa_g": 20.0,
        "L_m": 35.0,
        "D_mm": 50.0,
        "fittings": {
            "Codo 90° estándar": 8,
            "Válvula bola abierta": 2,
            "Válvula de retención tipo clapeta": 1,
            "Tee · paso recto": 2,
        },
        "pump": {
            "H0_m": 42.0,
            "Qbep_Ls": 8.0,
            "Hbep_m": 30.0,
            "Qend_Ls": 14.0,
            "Hend_m": 10.0,
            "eta_max": 0.70,
        },
        "focus": "Conecta directamente con diseño de skids, refrigeración, lubricación y servicios auxiliares de maquinaria."
    },
}
