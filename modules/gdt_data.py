from __future__ import annotations

CONTROL_FAMILIES = {
    "Forma": [
        {
            "name": "Rectitud",
            "symbol": "—",
            "zone": "Dos líneas paralelas o una zona cilíndrica, según el elemento controlado.",
            "datum": "No requiere referencia especificada.",
            "use": "Ejes, generatrices, guías y elementos donde interesa limitar curvatura o desviación local/global."
        },
        {
            "name": "Planitud",
            "symbol": "▱",
            "zone": "Dos planos paralelos separados por la tolerancia.",
            "datum": "No requiere referencia especificada.",
            "use": "Superficies de apoyo, sellado, montaje y bases."
        },
        {
            "name": "Redondez",
            "symbol": "○",
            "zone": "Dos círculos concéntricos en una sección transversal.",
            "datum": "No requiere referencia especificada.",
            "use": "Diámetros rotacionales donde interesa la forma de cada sección."
        },
        {
            "name": "Cilindricidad",
            "symbol": "⌭",
            "zone": "Dos cilindros coaxiales que contienen toda la superficie.",
            "datum": "No requiere referencia especificada.",
            "use": "Asientos de rodamientos, sellos y superficies cilíndricas funcionales."
        },
    ],
    "Orientación": [
        {
            "name": "Paralelismo",
            "symbol": "∥",
            "zone": "Dos líneas o planos paralelos orientados respecto de la referencia especificada.",
            "datum": "Normalmente requiere referencia especificada.",
            "use": "Guías, caras opuestas, alojamientos y superficies que deben mantener orientación."
        },
        {
            "name": "Perpendicularidad",
            "symbol": "⟂",
            "zone": "Dos planos paralelos o una zona cilíndrica a 90° de la referencia especificada.",
            "datum": "Normalmente requiere referencia especificada.",
            "use": "Hombros de eje, caras de apoyo, bridas y taladros respecto de una base."
        },
    ],
    "Localización": [
        {
            "name": "Posición",
            "symbol": "⌖",
            "zone": "Habitualmente una zona cilíndrica alrededor de la posición teórica exacta.",
            "datum": "Frecuentemente usa una o más referencias especificadas.",
            "use": "Patrones de agujeros, pasadores, ejes, centros y elementos de montaje."
        },
    ],
    "Oscilación": [
        {
            "name": "Oscilación circular",
            "symbol": "↗",
            "zone": "Variación permitida en cada sección durante una revolución respecto de un eje de referencia.",
            "datum": "Requiere un eje de referencia de rotación.",
            "use": "Caras, diámetros y superficies rotacionales."
        },
        {
            "name": "Oscilación total",
            "symbol": "↗↗",
            "zone": "Variación total de la superficie durante rotación y barrido axial.",
            "datum": "Requiere un eje de referencia de rotación.",
            "use": "Control combinado de superficie rotacional a lo largo de toda su extensión."
        },
    ],
}

DATUM_EXAMPLES = [
    {
        "name": "Base mecanizada + lateral + extremo",
        "A": "Plano de apoyo principal",
        "B": "Cara lateral de orientación",
        "C": "Cara extrema de localización",
        "use": "Carcasas, bases, placas y mecanizados prismáticos."
    },
    {
        "name": "Eje + cara axial",
        "A": "Eje derivado de un diámetro funcional",
        "B": "Cara de hombro",
        "C": "No siempre necesario",
        "use": "Componentes rotacionales, poleas, acoples y bridas."
    },
    {
        "name": "Plano + patrón de agujeros",
        "A": "Superficie primaria",
        "B": "Eje/centro derivado del patrón",
        "C": "Elemento adicional de orientación angular",
        "use": "Bridas y uniones apernadas."
    },
]

INSPECTION_METHODS = [
    {
        "method": "Mesa de granito + reloj comparador",
        "best_for": "Planitud, paralelismo, perpendicularidad y oscilación circular.",
        "limits": "Depende de fijación, acceso, referencia física y habilidad del operador."
    },
    {
        "method": "Micrómetro / alesómetro",
        "best_for": "Tamaño y forma local; apoyo a redondez/cilindricidad por secciones.",
        "limits": "No reemplaza una evaluación completa de zona geométrica."
    },
    {
        "method": "CMM",
        "best_for": "Referencias A-B-C, posición, orientación, perfiles y geometrías complejas.",
        "limits": "Resultado depende de estrategia de palpado, alineación y software."
    },
    {
        "method": "Escaneo 3D / óptico",
        "best_for": "Cobertura superficial, comparación CAD y mapas de desviación.",
        "limits": "No toda especificación GPS se verifica automáticamente con un mapa de colores."
    },
]

ENGINEERING_CASES = {
    "Brida con patrón de agujeros": {
        "description": "Controlar posición del patrón respecto de una cara primaria y una referencia secundaria.",
        "primary": "Posición",
        "datums": "A | B | C",
        "question": "¿Los agujeros ensamblarán con la pieza de acoplamiento sin forzar el patrón?"
    },
    "Alojamiento de rodamiento": {
        "description": "Combinar tamaño, cilindricidad y orientación del alojamiento respecto de una cara funcional.",
        "primary": "Cilindricidad + perpendicularidad",
        "datums": "A",
        "question": "¿El rodamiento apoyará correctamente y mantendrá alineación funcional?"
    },
    "Eje con hombro": {
        "description": "Controlar el asiento cilíndrico y la cara de hombro respecto del eje funcional.",
        "primary": "Oscilación + perpendicularidad",
        "datums": "A",
        "question": "¿La pieza rotará sin excentricidad ni bamboleo excesivo?"
    },
}
