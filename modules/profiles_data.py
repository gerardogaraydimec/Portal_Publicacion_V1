from __future__ import annotations

from typing import Any

# Unidades internas de la biblioteca:
# dimensiones -> mm
# A -> mm²
# I, Jt -> mm⁴
# S, Z -> mm³
# Iw -> mm⁶
# masa -> kg/m

PROFILES: list[dict[str, Any]] = []


def add_profile(**kwargs):
    base = {
        "family": None,
        "designation": None,
        "shape": None,
        "h_mm": None,
        "b_mm": None,
        "tw_mm": None,
        "tf_mm": None,
        "r_mm": None,
        "Do_mm": None,
        "Di_mm": None,
        "t_mm": None,
        "mass_kg_m": None,
        "A_mm2": None,
        "Ix_mm4": None,
        "Iy_mm4": None,
        "Sx_mm3": None,
        "Sy_mm3": None,
        "rx_mm": None,
        "ry_mm": None,
        "Zx_mm3": None,
        "Zy_mm3": None,
        "Jt_mm4": None,
        "Iw_mm6": None,
        "source_kind": "",
        "source_name": "",
        "source_url": "",
        "source_note": "",
        "market_note": "",
    }
    base.update(kwargs)
    PROFILES.append(base)


# ---------------------------------------------------------------------
# IPE · base geométrica y propiedades resistentes de Mott Appendix 15,
# masa lineal de catálogo comercial métrico contemporáneo (MultiAceros).
# ---------------------------------------------------------------------
_ipe_rows = [
# d, B, tf, tw, mass, A, Ix, Sx, rx, Iy, Sy, ry
(80, 46, 5.2, 3.8, 6.0, 764, 8.014e5, 2.003e4, 32.4, 8.487e4, 3.690e3, 10.54),
(100,55,5.7,4.1,8.1,1032,1.710e6,3.420e4,40.7,1.591e5,5.786e3,12.4),
(120,64,6.3,4.4,10.4,1321,3.177e6,5.296e4,49.0,2.766e5,8.644e3,14.5),
(140,73,6.9,4.7,12.9,1643,5.412e6,7.732e4,57.4,4.491e5,1.230e4,16.5),
(160,82,7.4,5.0,15.8,2009,8.693e6,1.087e5,65.8,6.829e5,1.666e4,18.4),
(180,91,8.0,5.3,18.8,2395,1.317e7,1.463e5,74.2,1.008e6,2.216e4,20.5),
(200,100,8.5,5.6,22.4,2848,1.943e7,1.943e5,82.6,1.423e6,2.846e4,22.4),
(220,110,9.2,5.9,26.2,3337,2.772e7,2.520e5,91.1,2.048e6,3.724e4,24.8),
(240,120,9.8,6.2,30.7,3912,3.891e7,3.243e5,99.7,2.835e6,4.725e4,26.9),
(270,135,10.2,6.6,36.1,4595,5.790e7,4.289e5,112.3,4.197e6,6.218e4,30.2),
(300,150,10.7,7.1,42.2,5381,8.356e7,5.571e5,124.6,6.036e6,8.048e4,33.5),
(330,160,11.5,7.5,49.1,6261,1.177e8,7.131e5,137.1,7.878e6,9.848e4,35.5),
(360,170,12.7,8.0,57.1,7273,1.627e8,9.036e5,149.5,1.043e7,1.227e5,37.9),
(400,180,13.5,8.8,66.3,8521,2.321e8,1.161e6,165.1,1.317e7,1.464e5,39.3),
(450,190,14.6,9.4,77.7,9882,3.374e8,1.500e6,184.8,1.675e7,1.763e5,41.2),
(500,200,16.0,10.2,90.7,11552,4.820e8,1.928e6,204.3,2.141e7,2.141e5,43.1),
(550,210,17.2,11.1,106.0,13442,6.712e8,2.441e6,223.5,2.667e7,2.540e5,44.5),
(600,220,19.0,12.0,122.0,15598,9.208e8,3.069e6,243.0,3.386e7,3.078e5,46.6),
]
for row in _ipe_rows:
    d,B,tf,tw,mass,A,Ix,Sx,rx,Iy,Sy,ry = row
    add_profile(
        family="IPE", designation=f"IPE {d}", shape="I",
        h_mm=d, b_mm=B, tw_mm=tw, tf_mm=tf,
        mass_kg_m=mass, A_mm2=A, Ix_mm4=Ix, Iy_mm4=Iy,
        Sx_mm3=Sx, Sy_mm3=Sy, rx_mm=rx, ry_mm=ry,
        source_kind="Libro + catálogo comercial",
        source_name="Mott, Appendix 15-13 + catálogo MultiAceros",
        source_url="https://www.multiaceros.cl/pub/media/pdf/catalogo_perfiles.pdf",
        source_note="I, S, r y dimensiones desde la tabla SI de Mott; masa lineal desde catálogo métrico comercial. Valores para docencia y comparación.",
        market_note="Familia publicada en Chile por Cintac, MultiAceros, Perfilam y otros distribuidores."
    )


# ---------------------------------------------------------------------
# IPN · geometría nominal y propiedades recalculadas de Formulaxis.
# El propio sitio las marca como no contractuales.
# ---------------------------------------------------------------------
_ipn_rows = [
# h,b,tw,tf,A cm2,mass kg/m,Ix cm4,Iy cm4,Wx cm3,Wy cm3
(80,42,3.9,5.9,8.6319,6.7761,89.696,8.2239,22.424,3.9161),
(100,50,4.5,6.8,12.137,9.5277,197.85,16.05,39.571,6.4201),
(120,58,5.1,7.7,16.225,12.737,381.79,28.447,63.631,9.8094),
(140,66,5.7,8.6,20.897,16.404,670.3,46.918,95.757,14.218),
(160,74,6.3,9.5,26.151,20.529,1096.8,73.18,137.1,19.778),
(180,82,6.9,10.4,31.989,25.111,1699.4,109.16,188.82,26.625),
(200,90,7.5,11.3,38.409,30.151,2520.6,157.01,252.06,34.892),
]
for row in _ipn_rows:
    h,b,tw,tf,Acm2,mass,Ixcm4,Iycm4,Wxcm3,Wycm3 = row
    A = Acm2*100
    Ix = Ixcm4*1e4
    Iy = Iycm4*1e4
    add_profile(
        family="IPN", designation=f"IPN {h}", shape="IPN",
        h_mm=h, b_mm=b, tw_mm=tw, tf_mm=tf,
        mass_kg_m=mass, A_mm2=A, Ix_mm4=Ix, Iy_mm4=Iy,
        Sx_mm3=Wxcm3*1e3, Sy_mm3=Wycm3*1e3,
        rx_mm=(Ix/A)**0.5, ry_mm=(Iy/A)**0.5,
        source_kind="Recalculado · no contractual",
        source_name="Formulaxis · EN 10365",
        source_url=f"https://formulaxis.com/es/biblioteca-perfiles/ipn-ipn-{h}/",
        source_note="Propiedades recalculadas desde geometría nominal simplificada. Confirmar catálogo/norma para diseño contractual.",
        market_note="IPN se publica comercialmente en Chile, incluyendo Cintac, MultiAceros y Perfilam."
    )


# ---------------------------------------------------------------------
# HEA / HEB · propiedades de sección de ArcelorMittal Orange Book.
# Conversión cm -> mm aplicada al cargar.
# ---------------------------------------------------------------------
_he_rows = {
"HEA": [
# name,mass,h,b,tw,tf,r,Ix,Iy,rx,ry,Welx,Wely,Wplx,Wply,Iw(dm6),It(cm4),A(cm2)
("HEA 100",16.7,96,100,5,8,12,349,134,4.06,2.51,72.8,27,83.0,41.1,0.00258,5.28,21.2),
("HEA 160",30.4,152,160,6,9,15,1670,616,6.57,3.98,220,77,245,118,0.0314,12.1,38.8),
("HEA 180",35.5,171,180,6,9.5,15,2510,925,7.45,4.52,294,103,325,156,0.0602,14.9,45.3),
("HEA 200",42.3,190,200,6.5,10,18,3690,1340,8.28,4.98,389,134,430,204,0.108,21.0,53.8),
("HEA 220",50.5,210,220,7,11,18,5410,1960,9.17,5.51,515,178,568,271,0.193,28.6,64.3),
("HEA 240",60.3,230,240,7.5,12,21,7760,2770,10.1,6.00,675,231,745,352,0.328,42.1,76.8),
("HEA 260",68.2,250,260,7.5,12.5,24,10400,3670,11.0,6.50,836,282,920,430,0.516,54.2,86.8),
("HEA 280",76.4,270,280,8,13,24,13700,4760,11.9,7.00,1010,340,1110,518,0.785,63.5,97.3),
("HEA 300",88.3,290,300,8.5,14,27,18300,6310,12.7,7.49,1260,421,1380,641,1.20,87.8,112),
("HEA 320",97.6,310,300,9,15.5,27,22900,6980,13.6,7.49,1480,466,1630,710,1.51,112,124),
("HEA 400",125,390,300,11,19,27,45100,8560,16.8,7.34,2310,571,2560,873,2.94,193,159),
("HEA 450",140,440,300,11.5,21,27,63700,9460,18.9,7.29,2900,631,3220,966,4.15,250,178),
("HEA 500",155,490,300,12,23,27,87000,10400,21.0,7.24,3550,691,3950,1060,5.64,318,198),
],
"HEB": [
("HEB 100",20.4,100,100,6,10,12,450,167,4.16,2.53,89.9,33,104,51.4,0.00338,9.33,26.0),
("HEB 160",42.6,160,160,8,13,15,2490,889,6.78,4.05,312,111,354,170,0.0479,31.3,54.3),
("HEB 180",51.2,180,180,8.5,14,15,3830,1360,7.66,4.57,426,151,481,231,0.0938,42.2,65.3),
("HEB 200",61.3,200,200,9,15,18,5700,2000,8.54,5.07,570,200,642,306,0.171,59.7,78.1),
("HEB 220",71.5,220,220,9.5,16,18,8090,2840,9.43,5.59,736,258,827,394,0.295,77.0,91.0),
("HEB 240",83.2,240,240,10,17,21,11300,3920,10.3,6.08,938,327,1050,498,0.487,104,106),
("HEB 260",93,260,260,10,17.5,24,14900,5140,11.2,6.58,1150,395,1280,602,0.754,127,118),
("HEB 280",103,280,280,10.5,18,24,19300,6600,12.1,7.09,1380,471,1530,718,1.13,146,131),
("HEB 300",117,300,300,11,19,27,25200,8560,13.0,7.58,1680,571,1870,870,1.69,189,149),
("HEB 320",127,320,300,11.5,20.5,27,30800,9240,13.8,7.57,1930,616,2150,939,2.07,230,161),
("HEB 400",155,400,300,13.5,24,27,57700,10800,17.1,7.40,2880,721,3230,1100,3.82,361,198),
("HEB 450",171,450,300,14,26,27,79900,11700,19.1,7.33,3550,781,3980,1200,5.26,448,218),
("HEB 500",187,500,300,14.5,28,27,107000,12600,21.2,7.27,4290,842,4820,1290,7.02,548,239),
]
}
for fam, rows in _he_rows.items():
    for row in rows:
        name,mass,h,b,tw,tf,r,Ix,Iy,rx,ry,Welx,Wely,Wplx,Wply,Iw_dm6,It_cm4,A_cm2 = row
        add_profile(
            family=fam, designation=name, shape="H",
            h_mm=h, b_mm=b, tw_mm=tw, tf_mm=tf, r_mm=r,
            mass_kg_m=mass, A_mm2=A_cm2*100,
            Ix_mm4=Ix*1e4, Iy_mm4=Iy*1e4,
            Sx_mm3=Welx*1e3, Sy_mm3=Wely*1e3,
            rx_mm=rx*10, ry_mm=ry*10,
            Zx_mm3=Wplx*1e3, Zy_mm3=Wply*1e3,
            Jt_mm4=It_cm4*1e4,
            Iw_mm6=Iw_dm6*1e12,
            source_kind="Catálogo técnico",
            source_name="ArcelorMittal Orange Book",
            source_url="https://orangebook.arcelormittal.com/node/16",
            source_note="Propiedades tabuladas del Orange Book. Verificar edición/norma aplicable para especificación contractual.",
            market_note=f"{fam} se comercializa en Chile por distribuidores como Cintac, MultiAceros, Perfilam y Küpfer."
        )


# ---------------------------------------------------------------------
# UPN · Orange Book
# ---------------------------------------------------------------------
_upn_rows = [
# size,mass,h,b,tw,tf,r,Ix,Iy,rx,ry,Welx,Wely,Wplx,Wply,Iw dm6,It cm4,A cm2
(80,8.6,80,45,6,8,8,106,19.4,3.10,1.33,26.5,6,32.3,11.9,0.000180,2.20,11.0),
(100,10.6,100,50,6,8.5,8.5,206,29.3,3.91,1.47,41.2,8,49,16.2,0.000410,2.81,13.5),
(120,13.4,120,55,7,9,9,364,43.2,4.62,1.59,60.7,11,72.6,21.2,0.000900,4.15,17.0),
(140,16.0,140,60,7,10,10,605,62.7,5.45,1.75,86.4,15,103,28.3,0.00180,5.68,20.4),
(160,18.8,160,65,7.5,10.5,10.5,925,85.3,6.21,1.89,116,18,138,35.2,0.00326,7.39,24.0),
(180,22.0,180,70,8,11,11,1350,114,6.95,2.02,150,22,179,42.9,0.00557,9.55,28.0),
(200,25.3,200,75,8.5,11.5,11.5,1910,148,7.70,2.14,191,27,228,51.8,0.00907,11.9,32.2),
(220,29.4,220,80,9,12.5,12.5,2690,197,8.48,2.30,245,34,292,64.1,0.0146,16.0,37.4),
(240,33.2,240,85,9.5,13,13,3600,248,9.22,2.42,300,40,358,75.7,0.0221,19.7,42.3),
(260,37.9,260,90,10,14,14,4820,317,9.99,2.56,371,48,442,91.6,0.0333,25.5,48.3),
(280,41.8,280,95,10,15,15,6280,399,10.9,2.74,448,57,532,109,0.0485,31.0,53.3),
(300,46.2,300,100,10,16,16,8030,495,11.7,2.90,535,68,632,130,0.0691,37.4,58.8),
(320,59.5,320,100,14,17.5,17.5,10900,597,12.1,2.81,679,81,826,152,0.0961,66.7,75.8),
(350,60.6,350,100,14,16,16,12800,570,12.9,2.72,734,75,918,143,0.114,61.2,77.3),
(380,63.1,380,102,13.5,16,16,15800,615,14.0,2.77,829,79,1010,148,0.146,59.1,80.4),
(400,71.8,400,110,14,18,18,20400,846,14.9,3.04,1020,102,1240,190,0.221,81.6,91.5),
]
for row in _upn_rows:
    size,mass,h,b,tw,tf,r,Ix,Iy,rx,ry,Welx,Wely,Wplx,Wply,Iw_dm6,It_cm4,A_cm2 = row
    add_profile(
        family="UPN", designation=f"UPN {size}", shape="C",
        h_mm=h, b_mm=b, tw_mm=tw, tf_mm=tf, r_mm=r,
        mass_kg_m=mass, A_mm2=A_cm2*100,
        Ix_mm4=Ix*1e4, Iy_mm4=Iy*1e4,
        Sx_mm3=Welx*1e3, Sy_mm3=Wely*1e3,
        rx_mm=rx*10, ry_mm=ry*10,
        Zx_mm3=Wplx*1e3, Zy_mm3=Wply*1e3,
        Jt_mm4=It_cm4*1e4, Iw_mm6=Iw_dm6*1e12,
        source_kind="Catálogo técnico",
        source_name="ArcelorMittal Orange Book",
        source_url="https://orangebook.arcelormittal.com/node/265",
        source_note="Propiedades tabuladas de canal UPN. El dibujo MechLab es esquemático y no reproduce los radios/taper exactos.",
        market_note="UPN tiene amplia presencia comercial en Chile."
    )


# ---------------------------------------------------------------------
# SHS / RHS · Mott Appendix 15-16.
# Masa de referencia derivada de A y ρ=7850 kg/m³ para uniformidad.
# ---------------------------------------------------------------------
_hss_rows = [
# short,long,t,A,Ix,Sx,rx,Iy,Sy,ry
(10,20,2,104,4.619e3,462,6.66,1.379e3,276,3.64),
(20,20,2,144,7.872e3,787,7.39,7.872e3,787,7.39),
(20,30,3,264,2.887e4,1925,10.5,1.451e4,1451,7.41),
(30,30,3,324,3.985e4,2657,11.1,3.985e4,2657,11.1),
(20,40,3,324,6.081e4,3041,13.7,1.889e4,1889,7.64),
(40,40,3,444,1.020e5,5099,15.2,1.020e5,5099,15.2),
(30,50,3,444,1.421e5,5685,17.9,6.181e4,4121,11.8),
(50,50,3,564,2.085e5,8340,19.2,2.085e5,8340,19.2),
(40,80,4,896,7.113e5,1.778e4,28.2,2.301e5,1.150e4,16.0),
(80,80,3,924,9.145e5,2.286e4,31.5,9.145e5,2.286e4,31.5),
(50,100,4,1136,1.441e6,2.883e4,35.6,4.737e5,1.895e4,20.4),
(100,100,4,1536,2.363e6,4.727e4,39.2,2.363e6,4.727e4,39.2),
(50,150,4,1536,4.041e6,5.388e4,51.3,6.858e5,2.743e4,21.1),
(150,150,5,2900,1.017e7,1.357e5,59.2,1.017e7,1.357e5,59.2),
(200,200,4,3136,2.009e7,2.009e5,80.0,2.009e7,2.009e5,80.0),
(100,200,4,2336,1.240e7,1.240e5,72.9,4.208e6,8.415e4,42.4),
(50,200,4,1936,8.561e6,8.561e4,66.5,8.979e5,3.592e4,21.5),
(250,250,8,7744,7.567e7,6.054e5,98.9,7.567e7,6.054e5,98.9),
(300,300,8,9344,1.329e8,8.859e5,119.3,1.329e8,8.859e5,119.3),
(300,300,12.5,14375,1.984e8,1.323e6,117.5,1.984e8,1.323e6,117.5),
]
for short,long,t,A,Ix,Sx,rx,Iy,Sy,ry in _hss_rows:
    fam = "SHS" if short == long else "RHS"
    designation = f"{fam} {long}×{short}×{t:g}"
    add_profile(
        family=fam, designation=designation, shape="BOX",
        h_mm=long, b_mm=short, t_mm=t,
        mass_kg_m=A*0.00785,
        A_mm2=A, Ix_mm4=Ix, Iy_mm4=Iy,
        Sx_mm3=Sx, Sy_mm3=Sy, rx_mm=rx, ry_mm=ry,
        source_kind="Libro · geometría idealizada",
        source_name="Mott, Appendix 15-16",
        source_url="",
        source_note="La tabla supone esquinas perfectamente cuadradas; perfiles comerciales reales incorporan radios. Masa de referencia derivada con ρ=7850 kg/m³.",
        market_note="Tubulares cuadrados y rectangulares son de amplia disponibilidad en Chile; verificar espesor real y norma del fabricante."
    )


# ---------------------------------------------------------------------
# CHS / tubo circular · Mott Appendix 15-19.
# ---------------------------------------------------------------------
_chs_rows = [
# Do,Di,t,A,I,S,r,J,Zp
(10,8,1.0,28.27,289.8,57.96,3.20,579.6,115.9),
(10,6,2.0,50.27,427.3,85.45,2.92,854.5,170.9),
(20,17,1.5,87.18,3754,375.4,6.56,7508.3,750.8),
(20,15,2.5,137.4,5369,536.9,6.25,1.074e4,1074),
(30,26,2.0,175.9,1.733e4,1155,9.92,3.466e4,2311),
(30,22,4.0,326.7,2.826e4,1884,9.30,5.652e4,3768),
(45,40,2.5,333.8,7.563e4,3361,15.05,1.513e5,6722),
(45,37,4.0,515.2,1.093e5,4857,14.56,2.186e5,9715),
(60,52,4.0,703.7,2.773e5,9242,19.85,5.545e5,1.848e4),
(60,48,6.0,1017.9,3.756e5,1.252e4,19.21,7.512e5,2.504e4),
(75,70,2.5,569.4,3.746e5,9.988e3,25.65,7.491e5,1.998e4),
(75,65,5.0,1100,6.769e5,1.805e4,24.81,1.354e6,3.610e4),
(90,84,3.0,820,7.767e5,1.726e4,30.78,1.553e6,3.452e4),
(90,80,5.0,1335,1.210e6,2.689e4,30.10,2.420e6,5.378e4),
(110,104,3.0,1008,1.444e6,2.626e4,37.85,2.889e6,5.252e4),
(110,100,5.0,1649,2.278e6,4.142e4,37.17,4.556e6,8.284e4),
(130,124,3.0,1197,2.415e6,3.715e4,44.91,4.829e6,7.429e4),
(130,120,5.0,1963,3.841e6,5.909e4,44.23,7.682e6,1.182e5),
(150,144,3.0,1385,3.744e6,4.992e4,51.98,7.488e6,9.983e4),
(150,140,5.0,2278,5.993e6,7.991e4,51.30,1.199e7,1.598e5),
]
for Do,Di,t,A,I,S,r,J,Zp in _chs_rows:
    add_profile(
        family="CHS", designation=f"CHS Ø{Do}×{t:g}", shape="CIRCLE",
        Do_mm=Do, Di_mm=Di, t_mm=t, h_mm=Do, b_mm=Do,
        mass_kg_m=A*0.00785, A_mm2=A,
        Ix_mm4=I, Iy_mm4=I, Sx_mm3=S, Sy_mm3=S,
        rx_mm=r, ry_mm=r, Jt_mm4=J, Zx_mm3=Zp, Zy_mm3=Zp,
        source_kind="Libro",
        source_name="Mott, Appendix 15-19",
        source_url="",
        source_note="Para sección circular, la tabla incluye propiedades de flexión I,S,r y torsión J,Zp. Masa de referencia derivada con ρ=7850 kg/m³.",
        market_note="Tubos redondos estructurales son comunes en Chile; verificar si el producto corresponde a CHS/HSS estructural y su norma."
    )


FAMILY_ORDER = ["IPE", "IPN", "HEA", "HEB", "UPN", "SHS", "RHS", "CHS"]

FAMILY_INFO = {
    "IPE": {
        "name": "IPE · doble T de alas paralelas",
        "use": "Vigas sometidas principalmente a flexión respecto del eje fuerte.",
        "market": "Muy habitual en catálogos chilenos de vigas laminadas.",
    },
    "IPN": {
        "name": "IPN · doble T de alas inclinadas",
        "use": "Vigas y elementos estructurales clásicos; geometría de alas inclinadas.",
        "market": "Disponible en Chile, aunque en proyectos nuevos suele convivir con IPE.",
    },
    "HEA": {
        "name": "HEA · H de alas anchas aligerada",
        "use": "Vigas y columnas; buena rigidez en ambos ejes respecto de un IPE equivalente.",
        "market": "Muy presente en distribuidores chilenos de perfiles laminados.",
    },
    "HEB": {
        "name": "HEB · H de alas anchas",
        "use": "Columnas y vigas robustas; mayor masa y rigidez que HEA de igual serie.",
        "market": "Muy presente en distribuidores chilenos.",
    },
    "UPN": {
        "name": "UPN · canal laminado",
        "use": "Vigas secundarias, marcos, soportes y fabricación mecanoestructural.",
        "market": "Muy habitual en Chile.",
    },
    "SHS": {
        "name": "SHS · tubular estructural cuadrado",
        "use": "Marcos y columnas con respuesta similar en ambos ejes principales.",
        "market": "Amplia disponibilidad nacional en perfiles tubulares.",
    },
    "RHS": {
        "name": "RHS · tubular estructural rectangular",
        "use": "Vigas, marcos y elementos donde interesa orientar el eje fuerte.",
        "market": "Amplia disponibilidad nacional.",
    },
    "CHS": {
        "name": "CHS · tubular estructural circular",
        "use": "Columnas, arriostramientos y elementos con simetría geométrica.",
        "market": "Disponible como tubo/perfil estructural; confirmar norma y espesor.",
    },
}


def families() -> list[str]:
    return FAMILY_ORDER.copy()


def profiles_for_family(family: str) -> list[dict[str, Any]]:
    return [p for p in PROFILES if p["family"] == family]


def get_profile(family: str, designation: str) -> dict[str, Any]:
    for p in PROFILES:
        if p["family"] == family and p["designation"] == designation:
            return p
    raise KeyError((family, designation))


def compact_property_table(p: dict[str, Any]) -> list[tuple[str, Any, str]]:
    return [
        ("Área A", p["A_mm2"], "mm²"),
        ("Masa lineal", p["mass_kg_m"], "kg/m"),
        ("Iₓ", p["Ix_mm4"], "mm⁴"),
        ("Iᵧ", p["Iy_mm4"], "mm⁴"),
        ("Sₓ / Wₓ,el", p["Sx_mm3"], "mm³"),
        ("Sᵧ / Wᵧ,el", p["Sy_mm3"], "mm³"),
        ("rₓ", p["rx_mm"], "mm"),
        ("rᵧ", p["ry_mm"], "mm"),
        ("Zₓ / Wₓ,pl", p["Zx_mm3"], "mm³"),
        ("Zᵧ / Wᵧ,pl", p["Zy_mm3"], "mm³"),
        ("Jₜ", p["Jt_mm4"], "mm⁴"),
        ("Iᵥ / Iw", p["Iw_mm6"], "mm⁶"),
    ]
