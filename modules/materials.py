from __future__ import annotations

# La biblioteca de materiales es deliberadamente independiente de la geometría
# del perfil. Elegir un IPE, HEA, RHS, etc. NO implica por sí mismo un grado.

MATERIALS = {
    "A270ES · referencia Chile": {
        "standard": "NCh203 / catálogo técnico chileno",
        "E_GPa": 200.0,
        "nu": 0.30,
        "rho_kg_m3": 7850.0,
        "Fy_MPa": 270.0,
        "Fu_MPa": "410–510",
        "elongation": "22 / 20 / 18 % según espesor",
        "source": "Catálogo Técnico Aceros AZA",
        "url": "https://www.aza.cl/2024/wp-content/uploads/2024/07/Catalogo-Tecnico-2024-QR.pdf",
        "note": "Fy y Fu según catálogo técnico. E, ν y ρ son valores de referencia de acero estructural usados para docencia.",
    },
    "A345ES · referencia Chile": {
        "standard": "NCh203 / catálogo técnico chileno",
        "E_GPa": 200.0,
        "nu": 0.30,
        "rho_kg_m3": 7850.0,
        "Fy_MPa": 345.0,
        "Fu_MPa": "510–610",
        "elongation": "20 / 18 / 16 % según espesor",
        "source": "Catálogo Técnico Aceros AZA",
        "url": "https://www.aza.cl/2024/wp-content/uploads/2024/07/Catalogo-Tecnico-2024-QR.pdf",
        "note": "Fy y Fu según catálogo técnico. E, ν y ρ son valores de referencia para cálculos académicos.",
    },
    "ASTM A36": {
        "standard": "ASTM A36",
        "E_GPa": 200.0,
        "nu": 0.30,
        "rho_kg_m3": 7850.0,
        "Fy_MPa": 248.0,
        "Fu_MPa": 400.0,
        "elongation": "21 % (referencia Mott)",
        "source": "Mott · Appendix 7",
        "url": "",
        "note": "Mott entrega mínimos de referencia Fy≈248 MPa y Fu≈400 MPa. Verificar especificación y certificado del producto real.",
    },
    "ASTM A572 Gr 50": {
        "standard": "ASTM A572 Grade 50",
        "E_GPa": 200.0,
        "nu": 0.30,
        "rho_kg_m3": 7850.0,
        "Fy_MPa": 345.0,
        "Fu_MPa": 448.0,
        "elongation": "21 % (referencia Mott)",
        "source": "Mott · Appendix 7",
        "url": "",
        "note": "Grado publicado en Chile para determinadas vigas WF. Confirmar grado exacto del perfil adquirido.",
    },
    "ASTM A992": {
        "standard": "ASTM A992",
        "E_GPa": 200.0,
        "nu": 0.30,
        "rho_kg_m3": 7850.0,
        "Fy_MPa": 345.0,
        "Fu_MPa": 448.0,
        "elongation": "21 % (referencia Mott)",
        "source": "Mott · Appendix 7",
        "url": "",
        "note": "Mott lo asocia principalmente a perfiles W. No asumir que un WF local es A992 sin certificado.",
    },
    "ASTM A500 Gr B · sección conformada": {
        "standard": "ASTM A500 Grade B",
        "E_GPa": 200.0,
        "nu": 0.30,
        "rho_kg_m3": 7850.0,
        "Fy_MPa": 317.0,
        "Fu_MPa": 400.0,
        "elongation": "23 % (referencia Mott)",
        "source": "Mott · Appendix 7",
        "url": "",
        "note": "Valor Mott para A500 Gr B en sección conformada (square/rectangular). Revisar edición de ASTM y certificado.",
    },
    "ASTM A500 Gr B · redondo": {
        "standard": "ASTM A500 Grade B",
        "E_GPa": 200.0,
        "nu": 0.30,
        "rho_kg_m3": 7850.0,
        "Fy_MPa": 290.0,
        "Fu_MPa": 400.0,
        "elongation": "23 % (referencia Mott)",
        "source": "Mott · Appendix 7",
        "url": "",
        "note": "Valor Mott para tubo estructural redondo A500 Gr B. Confirmar norma vigente y certificado.",
    },
}


DEFAULT_MATERIAL_BY_FAMILY = {
    "IPE": "A270ES · referencia Chile",
    "IPN": "A270ES · referencia Chile",
    "HEA": "A270ES · referencia Chile",
    "HEB": "A270ES · referencia Chile",
    "UPN": "A270ES · referencia Chile",
    "SHS": "ASTM A500 Gr B · sección conformada",
    "RHS": "ASTM A500 Gr B · sección conformada",
    "CHS": "ASTM A500 Gr B · redondo",
}


def material_names():
    return list(MATERIALS.keys())


def shear_modulus_gpa(material: dict) -> float:
    return material["E_GPa"] / (2.0 * (1.0 + material["nu"]))
