from __future__ import annotations

VERIFIED_DATE = "2026-09-19"

PROVIDERS = [
    {
        "name": "Cintac",
        "families": "IPE · IPN · UPN · HEA · HEB · tubulares",
        "url": "https://www.cintac.cl/vigas-laminadas/",
        "tubular_url": "https://www.cintac.cl/tubulares-grandes-dimensiones/",
        "note": "Publica cinco familias de vigas laminadas y líneas tubulares. Las vigas laminadas se informan en largos estándar de 6 y 12 m.",
    },
    {
        "name": "MultiAceros",
        "families": "IPE · IPN · UPN · HEA · HEB · perfiles y tubulares",
        "url": "https://www.multiaceros.cl/perfiles-laminados/",
        "catalog_url": "https://www.multiaceros.cl/pub/media/pdf/Catalogo-de-Productos-2024.pdf",
        "note": "Catálogo nacional con familias laminadas europeas y otros productos estructurales.",
    },
    {
        "name": "Perfilam",
        "families": "IPE · IPN · UPN · HEA · HEB · WF · ángulos · cuadrados/rectangulares",
        "url": "https://perfilam.cl/site/index.php/productos",
        "note": "Importador/distribuidor con vigas laminadas y perfiles cuadrados/rectangulares.",
    },
    {
        "name": "Küpfer",
        "families": "Aceros estructurales · UPN · HEA/HEB/IPE según stock · WF ASTM A572",
        "url": "https://kupfer.cl/aceros-estructurales.html",
        "note": "Tienda con disponibilidad por sucursal. Stock y precio son variables; confirmar al momento de especificar/comprar.",
    },
]

MARKET_FAMILIES = [
    {
        "family": "IPE",
        "detail": "Incluida en la biblioteca V0.1",
        "availability": "Alta",
        "providers": "Cintac · MultiAceros · Perfilam · Küpfer",
    },
    {
        "family": "IPN",
        "detail": "Incluida · valores recalculados no contractuales",
        "availability": "Alta",
        "providers": "Cintac · MultiAceros · Perfilam",
    },
    {
        "family": "HEA",
        "detail": "Incluida · Orange Book",
        "availability": "Alta",
        "providers": "Cintac · MultiAceros · Perfilam · Küpfer",
    },
    {
        "family": "HEB",
        "detail": "Incluida · Orange Book",
        "availability": "Alta",
        "providers": "Cintac · MultiAceros · Perfilam",
    },
    {
        "family": "UPN",
        "detail": "Incluida · Orange Book",
        "availability": "Alta",
        "providers": "Cintac · MultiAceros · Perfilam · Küpfer",
    },
    {
        "family": "SHS / RHS",
        "detail": "Incluida como biblioteca académica SI",
        "availability": "Muy alta",
        "providers": "Cintac · MultiAceros · Perfilam · otros",
    },
    {
        "family": "CHS / tubo estructural",
        "detail": "Incluida como biblioteca académica SI",
        "availability": "Muy alta",
        "providers": "Cintac · MultiAceros · otros",
    },
    {
        "family": "WF / W",
        "detail": "Detectada en mercado Chile; ficha AISC detallada planificada",
        "availability": "Media/alta",
        "providers": "Perfilam · Küpfer",
    },
    {
        "family": "L · ángulos",
        "detail": "Detectada en mercado Chile; siguiente expansión",
        "availability": "Muy alta",
        "providers": "Perfilam · MultiAceros · Cintac · otros",
    },
    {
        "family": "Canal / costanera conformada",
        "detail": "Detectada en mercado Chile; siguiente expansión",
        "availability": "Muy alta",
        "providers": "Cintac · MultiAceros · otros",
    },
]

TECHNICAL_SOURCES = [
    {
        "name": "Mott · Machine Elements in Mechanical Design",
        "role": "Base académica para propiedades A, I, S, r, J, Zp y tablas SI de IPE/tubulares.",
        "url": "",
    },
    {
        "name": "ArcelorMittal Orange Book",
        "role": "Propiedades técnicas de HEA, HEB y UPN: I, W_el, W_pl, radios, torsión y alabeo.",
        "url": "https://orangebook.arcelormittal.com/",
    },
    {
        "name": "Formulaxis",
        "role": "IPN recalculado desde geometría nominal; útil para docencia, no contractual.",
        "url": "https://formulaxis.com/es/biblioteca-perfiles/",
    },
    {
        "name": "AISC Shapes Database v16.0",
        "role": "Fuente recomendada para futura integración detallada de perfiles W/WF.",
        "url": "https://www.aisc.org/aisc/publications/steel-construction-manual/aisc-shapes-database-v160/",
    },
]
