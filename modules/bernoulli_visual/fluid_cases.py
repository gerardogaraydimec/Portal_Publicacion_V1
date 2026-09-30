from __future__ import annotations

CASES = {
    "Reducción gradual": {
        "description": "La tubería disminuye de diámetro. Para un líquido incompresible, la velocidad aumenta y la presión puede disminuir.",
        "D1_mm": 150.0,
        "D2_mm": 75.0,
        "z1_m": 0.0,
        "z2_m": 0.0,
        "p1_kPa": 250.0,
        "p2_kPa": 0.0,
        "Q_Ls": 20.0,
        "unknown": "p₂",
        "geometry": "contraction",
        "insight": "Continuidad obliga a aumentar V cuando disminuye A. Bernoulli muestra cómo esa energía cinética adicional se obtiene a costa de presión si z no cambia."
    },
    "Expansión gradual": {
        "description": "La tubería aumenta de diámetro. En el modelo ideal, la velocidad disminuye y parte de la altura de velocidad se recupera como presión.",
        "D1_mm": 75.0,
        "D2_mm": 150.0,
        "z1_m": 0.0,
        "z2_m": 0.0,
        "p1_kPa": 120.0,
        "p2_kPa": 0.0,
        "Q_Ls": 20.0,
        "unknown": "p₂",
        "geometry": "expansion",
        "insight": "La expansión ideal recupera presión. En una expansión real aparecen pérdidas, especialmente si la expansión es brusca."
    },
    "Tubería ascendente": {
        "description": "La sección final está a mayor cota. Con igual diámetro, la velocidad no cambia y el aumento de energía potencial reduce la presión.",
        "D1_mm": 100.0,
        "D2_mm": 100.0,
        "z1_m": 0.0,
        "z2_m": 8.0,
        "p1_kPa": 250.0,
        "p2_kPa": 0.0,
        "Q_Ls": 15.0,
        "unknown": "p₂",
        "geometry": "rise",
        "insight": "Cuando D₁ = D₂, V₁ = V₂. El intercambio principal ocurre entre altura de presión y altura geométrica."
    },
    "Tubería descendente": {
        "description": "La sección final está a menor cota. Con igual diámetro, la disminución de energía potencial se traduce en un aumento de presión ideal.",
        "D1_mm": 100.0,
        "D2_mm": 100.0,
        "z1_m": 8.0,
        "z2_m": 0.0,
        "p1_kPa": 100.0,
        "p2_kPa": 0.0,
        "Q_Ls": 15.0,
        "unknown": "p₂",
        "geometry": "drop",
        "insight": "Al descender, la altura geométrica disminuye. Sin pérdidas y con velocidad constante, la altura de presión aumenta."
    },
    "Boquilla ideal": {
        "description": "La presión disponible acelera el fluido en una boquilla. Se fija la salida a presión atmosférica manométrica y se resuelve el caudal.",
        "D1_mm": 100.0,
        "D2_mm": 40.0,
        "z1_m": 0.0,
        "z2_m": 0.0,
        "p1_kPa": 300.0,
        "p2_kPa": 0.0,
        "Q_Ls": 10.0,
        "unknown": "Q",
        "geometry": "nozzle",
        "insight": "Una boquilla convierte altura de presión en altura de velocidad. El modelo es ideal y no incluye coeficiente de descarga."
    },
    "Venturi ideal": {
        "description": "Dos presiones conocidas y un cambio de área permiten inferir el caudal mediante continuidad y Bernoulli.",
        "D1_mm": 150.0,
        "D2_mm": 75.0,
        "z1_m": 0.0,
        "z2_m": 0.0,
        "p1_kPa": 220.0,
        "p2_kPa": 150.0,
        "Q_Ls": 10.0,
        "unknown": "Q",
        "geometry": "venturi",
        "insight": "El Venturi relaciona diferencia de presión con caudal. En un medidor real se incorpora un coeficiente de descarga y pérdidas."
    },
}

UNKNOWN_OPTIONS = ["p₂", "p₁", "Q"]
