from __future__ import annotations

import math
import streamlit as st

from modules.ui_brand import render_app_header
from modules.profiles_data import (
    FAMILY_INFO,
    compact_property_table,
    families,
    profiles_for_family,
    get_profile,
)
from modules.materials import (
    MATERIALS,
    DEFAULT_MATERIAL_BY_FAMILY,
    material_names,
    shear_modulus_gpa,
)
from modules.providers import (
    PROVIDERS,
    MARKET_FAMILIES,
    TECHNICAL_SOURCES,
    VERIFIED_DATE,
)
from modules.section_plotter import make_section_figure


st.markdown(
    """
<style>
:root{
  --gg-orange:#f28e1c;
  --gg-black:#111111;
  --gg-muted:#737986;
  --gg-line:#eceff2;
}
.block-container{
  max-width:1500px;
  padding-top:1.35rem !important;
  padding-bottom:2rem;
}
div[data-testid="stMainBlockContainer"] > div:first-child{overflow:visible!important;}
div[data-testid="stImage"],div[data-testid="stImage"] img{overflow:visible!important;}
div[data-testid="stImage"] img{object-fit:contain!important;}
.gg-profile-card{
  border:1px solid var(--gg-line);
  border-left:5px solid var(--gg-orange);
  border-radius:14px;
  padding:1rem 1.1rem;
  background:#fff;
  margin:.2rem 0 .8rem 0;
}
.gg-badge{
  display:inline-block;
  border-radius:999px;
  padding:.30rem .65rem;
  background:#111;
  color:white;
  font-size:.76rem;
  font-weight:800;
  margin-right:.35rem;
}
.gg-note{
  border:1px solid #ecece8;
  background:#f7f7f5;
  border-radius:12px;
  padding:.9rem 1rem;
  line-height:1.55;
}
.gg-warning{
  border-left:4px solid var(--gg-orange);
  background:#fff8ef;
  border-radius:9px;
  padding:.85rem 1rem;
  line-height:1.5;
}
div[data-testid="stMetric"]{
  border:1px solid var(--gg-line);
  border-radius:12px;
  padding:.55rem .7rem;
  background:#fff;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<div style="height:.18rem"></div>', unsafe_allow_html=True)

render_app_header(
    title="Biblioteca de Perfiles Estructurales · Chile",
    subtitle="Geometría · propiedades resistentes · materiales · aplicaciones en Resistencia de Materiales y diseño.",
    section="RESISTENCIA DE MATERIALES",
    logo_width=188,
)

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def latex_property_card(title: str, formula: str, caption: str):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.latex(formula)
        st.caption(caption)


def fmt_num(v):
    if v is None:
        return "—"
    return f"{v:.6g}"


def dim_cards(profile):
    items = []
    mapping = [
        ("Altura total", "h_mm", r"h", "mm",
         "Distancia total vertical de la sección."),
        ("Ancho total", "b_mm", r"b", "mm",
         "Ancho total de ala o de la sección."),
        ("Espesor de alma", "tw_mm", r"t_w", "mm",
         "Espesor de la parte central vertical del perfil."),
        ("Espesor de ala", "tf_mm", r"t_f", "mm",
         "Espesor de las alas superior e inferior."),
        ("Radio nominal", "r_mm", r"r", "mm",
         "Radio de acuerdo o transición indicado por la fuente."),
        ("Diámetro exterior", "Do_mm", r"D_o", "mm",
         "Diámetro exterior del tubo circular."),
        ("Diámetro interior", "Di_mm", r"D_i", "mm",
         "Diámetro interior del tubo circular."),
        ("Espesor de pared", "t_mm", r"t", "mm",
         "Espesor nominal de pared del perfil tubular."),
    ]
    for title, key, symbol, unit, caption in mapping:
        if profile.get(key) is not None:
            items.append((title, symbol, profile[key], unit, caption))
    return items


# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("Seleccionar perfil")

    family = st.selectbox(
        "Familia",
        families(),
        help="Elige primero la familia geométrica y después una designación.",
    )
    fam_profiles = profiles_for_family(family)
    designations = [p["designation"] for p in fam_profiles]

    default_profile = {
        "IPE": "IPE 200",
        "IPN": "IPN 160",
        "HEA": "HEA 200",
        "HEB": "HEB 200",
        "UPN": "UPN 200",
    }.get(family, designations[min(2, len(designations)-1)])

    profile_name = st.selectbox(
        "Perfil",
        designations,
        index=designations.index(default_profile) if default_profile in designations else 0,
    )
    profile = get_profile(family, profile_name)

    st.divider()
    st.header("Material para el análisis")

    default_material = DEFAULT_MATERIAL_BY_FAMILY.get(
        family, "A270ES · referencia Chile"
    )
    mats = material_names()
    material_name = st.selectbox(
        "Material",
        mats,
        index=mats.index(default_material),
        help="El perfil define la geometría; el material define propiedades mecánicas. Son selecciones independientes.",
    )
    material = MATERIALS[material_name]

    axis = st.radio(
        "Eje de análisis",
        ["x–x · eje fuerte", "y–y · eje débil"],
        help="Para secciones I/H, x–x suele ser el eje de mayor rigidez a flexión.",
    )
    axis_key = "x" if axis.startswith("x") else "y"

    st.divider()
    st.caption(
        "Herramienta académica y de preselección. Para un proyecto real deben revisarse norma, tolerancias, certificado y disponibilidad del producto."
    )

info = FAMILY_INFO[family]
st.markdown(
    f"""
<div class="gg-profile-card">
  <span class="gg-badge">{family}</span>
  <h3 style="margin:.65rem 0 .25rem 0">{profile_name}</h3>
  <div style="color:#737986">{info['name']}</div>
  <div style="margin-top:.45rem">{info['use']}</div>
</div>
""",
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "📘 Cómo usar",
    "📐 Sección y dimensiones",
    "📊 Propiedades",
    "🧱 Material",
    "🧮 Aplicaciones",
    "🛠️ Diseño y selección",
    "🇨🇱 Proveedores Chile",
])

# ---------------------------------------------------------------------
# 1. How to use
# ---------------------------------------------------------------------
with tabs[0]:
    c1, c2 = st.columns([1.12, .88], gap="large")

    with c1:
        st.subheader("Cómo leer una tabla de perfiles")
        st.write(
            "Una tabla de perfiles reúne dos tipos de información diferentes: "
            "**dimensiones físicas de la sección** y **propiedades geométricas derivadas de esa forma**. "
            "Estas últimas son las que permiten transformar una fuerza o un momento en tensiones, "
            "deformaciones o parámetros de estabilidad."
        )

        st.markdown("#### Ruta recomendada")
        st.markdown(
            """
1. **Reconoce la geometría** y los ejes x–x e y–y.
2. Identifica las dimensiones: altura, ancho y espesores.
3. Revisa qué propiedad necesita el problema: A, I, S, r, Jₜ, etc.
4. Selecciona el material solo después de entender que **perfil y material son datos distintos**.
5. Usa la pestaña **Aplicaciones** para relacionar cada propiedad con su ecuación.
6. Usa **Diseño y selección** para entender qué familias son más adecuadas según el tipo de problema.
"""
        )

        st.info(
            "La selección de una sección no termina en «qué perfil cabe». En diseño interesa saber cómo distribuye material respecto de los ejes y qué tan eficientemente resiste la solicitación dominante.",
            icon="💡",
        )

    with c2:
        st.subheader("Relaciones fundamentales")

        latex_property_card(
            "Módulo resistente elástico",
            r"S=\frac{I}{c}",
            "Relaciona la inercia de área con la distancia c a la fibra extrema. Se usa directamente en flexión elástica."
        )
        latex_property_card(
            "Radio de giro",
            r"r=\sqrt{\frac{I}{A}}",
            "Mide cómo se distribuye el área respecto del eje y aparece en problemas de esbeltez y pandeo."
        )
        latex_property_card(
            "Rigidez flexional",
            r"EI",
            "Combina la rigidez del material E con la geometría I. Controla curvatura y deformación."
        )

# ---------------------------------------------------------------------
# 2. Section and dimensions
# ---------------------------------------------------------------------
with tabs[1]:
    left, right = st.columns([1.15, .85], gap="large")

    with left:
        st.subheader(f"Sección · {profile_name}")
        st.write(
            "Las líneas **naranjas** representan ejes centroidales. "
            "Las líneas **grises** son dimensiones. Las flechas identifican espesores o radios."
        )
        fig = make_section_figure(profile)
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

    with right:
        st.subheader("Dimensiones disponibles")
        dims = dim_cards(profile)

        for i in range(0, len(dims), 2):
            cols = st.columns(2)
            for col, item in zip(cols, dims[i:i+2]):
                title, symbol, value, unit, caption = item
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{title}**")
                        st.latex(rf"{symbol}={value:g}\,\mathrm{{{unit}}}")
                        st.caption(caption)

        st.markdown("#### Cómo interpretar los símbolos")
        if profile["shape"] in {"I", "H", "IPN", "C"}:
            st.write(
                "En perfiles abiertos, el **alma** conecta las alas y resiste gran parte del cortante; "
                "las **alas** concentran material lejos del eje centroidal y son decisivas para la rigidez y resistencia a flexión."
            )
        elif profile["shape"] == "BOX":
            st.write(
                "En SHS/RHS, la pared cerrada distribuye material alrededor del perímetro. "
                "En un RHS, orientar la dimensión mayor en la dirección de flexión suele aumentar fuertemente I y S."
            )
        elif profile["shape"] == "CIRCLE":
            st.write(
                "En CHS, la simetría circular hace que las propiedades de flexión sean iguales respecto de cualquier eje centroidal del plano."
            )

        with st.expander("Referencia de los datos de esta ficha"):
            st.write(f"**{profile['source_name']}**")
            st.caption(profile["source_note"])
            if profile["source_url"]:
                st.link_button("Abrir referencia ↗", profile["source_url"])

# ---------------------------------------------------------------------
# 3. Properties
# ---------------------------------------------------------------------
with tabs[2]:
    st.subheader("Qué significa cada propiedad")

    g1, g2 = st.columns(2, gap="large")

    with g1:
        latex_property_card(
            "Área de la sección",
            rf"A={profile['A_mm2']:.6g}\,\mathrm{{mm^2}}",
            "Interviene en tensión/compresión axial, peso y algunos parámetros de estabilidad."
        )
        latex_property_card(
            "Segundo momento de área · eje x–x",
            rf"I_x={profile['Ix_mm4']:.6g}\,\mathrm{{mm^4}}",
            "Cuantifica la distribución de área respecto de x–x. A mayor Iₓ, mayor rigidez geométrica a flexión respecto de ese eje."
        )
        latex_property_card(
            "Módulo resistente elástico · eje x–x",
            rf"S_x={profile['Sx_mm3']:.6g}\,\mathrm{{mm^3}}",
            "Convierte directamente momento flector en tensión extrema mediante σ = M/S."
        )
        latex_property_card(
            "Radio de giro · eje x–x",
            rf"r_x={profile['rx_mm']:.6g}\,\mathrm{{mm}}",
            "Se usa en esbeltez KL/r y permite evaluar qué eje es más sensible al pandeo."
        )

    with g2:
        latex_property_card(
            "Segundo momento de área · eje y–y",
            rf"I_y={profile['Iy_mm4']:.6g}\,\mathrm{{mm^4}}",
            "Mide la rigidez geométrica respecto del eje y–y. En I/H suele ser muy inferior a Iₓ."
        )
        latex_property_card(
            "Módulo resistente elástico · eje y–y",
            rf"S_y={profile['Sy_mm3']:.6g}\,\mathrm{{mm^3}}",
            "Se utiliza para flexión alrededor del eje y–y."
        )
        latex_property_card(
            "Radio de giro · eje y–y",
            rf"r_y={profile['ry_mm']:.6g}\,\mathrm{{mm}}",
            "Un valor pequeño de rᵧ suele hacer que el pandeo alrededor de ese eje sea más crítico."
        )
        if profile.get("Jt_mm4") is not None:
            latex_property_card(
                "Constante torsional",
                rf"J_t={profile['Jt_mm4']:.6g}\,\mathrm{{mm^4}}",
                "Propiedad usada en torsión de Saint-Venant. En perfiles abiertos no debe reemplazarse por Iₓ + Iᵧ."
            )

    st.markdown("#### Propiedades complementarias")
    c1, c2 = st.columns(2)
    with c1:
        if profile.get("Zx_mm3") is not None:
            st.latex(rf"Z_x={profile['Zx_mm3']:.6g}\,\mathrm{{mm^3}}")
            st.caption("Módulo resistente plástico respecto de x–x. Es una propiedad geométrica asociada a plastificación total de la sección.")
        else:
            st.write("**Zₓ**: no disponible en la fuente utilizada para esta ficha.")

        if profile.get("Zy_mm3") is not None:
            st.latex(rf"Z_y={profile['Zy_mm3']:.6g}\,\mathrm{{mm^3}}")
            st.caption("Módulo resistente plástico respecto de y–y.")
        else:
            st.write("**Zᵧ**: no disponible en la fuente utilizada para esta ficha.")

    with c2:
        if profile.get("Iw_mm6") is not None:
            st.latex(rf"I_w={profile['Iw_mm6']:.6g}\,\mathrm{{mm^6}}")
            st.caption("Constante de alabeo de la sección abierta. Aparece en problemas avanzados de torsión y estabilidad lateral.")
        else:
            st.write("**I_w**: no disponible en la fuente utilizada para esta ficha.")

    st.markdown("#### Tabla resumida")
    rows = []
    for label, value, unit in compact_property_table(profile):
        rows.append({
            "Propiedad": label,
            "Valor": "—" if value is None else f"{value:.6g}",
            "Unidad": unit,
        })
    st.dataframe(rows, width="stretch", hide_index=True)

    st.markdown(
        """
<div class="gg-warning">
<b>Importante:</b> que una propiedad no aparezca en la ficha no significa que físicamente sea cero.
Significa que no está soportada por la fuente incorporada en esta biblioteca y por eso MechLab no la completa mediante una aproximación oculta.
</div>
""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------
# 4. Material
# ---------------------------------------------------------------------
with tabs[3]:
    st.subheader(f"Material seleccionado · {material_name}")

    st.markdown(
        """
<div class="gg-warning">
<b>Geometría y material son independientes.</b>
Un IPE 200, HEA 300 o RHS 200×100 puede suministrarse en diferentes grados.
Para ingeniería real debe utilizarse el grado indicado por la especificación y el certificado del material.
</div>
""",
        unsafe_allow_html=True,
    )

    G = shear_modulus_gpa(material)

    m1, m2 = st.columns(2, gap="large")

    with m1:
        latex_property_card(
            "Módulo de elasticidad",
            rf"E={material['E_GPa']:.1f}\,\mathrm{{GPa}}",
            "Relaciona tensión y deformación unitaria en el rango elástico y entra directamente en EI."
        )
        latex_property_card(
            "Coeficiente de Poisson",
            rf"\nu={material['nu']:.2f}",
            "Relaciona deformación transversal y longitudinal en elasticidad lineal."
        )
        latex_property_card(
            "Módulo de corte",
            rf"G=\frac{{E}}{{2(1+\nu)}}={G:.1f}\,\mathrm{{GPa}}",
            "Se obtiene a partir de E y ν para un material isotrópico y se usa en problemas de corte y torsión."
        )

    with m2:
        latex_property_card(
            "Límite de fluencia",
            rf"F_y={material['Fy_MPa']:.0f}\,\mathrm{{MPa}}",
            "Marca el inicio de la plastificación según la referencia seleccionada."
        )
        st.markdown("**Resistencia última**")
        st.latex(rf"F_u={material['Fu_MPa']}\,\mathrm{{MPa}}")
        st.caption("Resistencia de referencia asociada a la rotura en tracción.")
        latex_property_card(
            "Densidad",
            rf"\rho={material['rho_kg_m3']:.0f}\,\mathrm{{kg/m^3}}",
            "Permite calcular masa, peso propio e inercia de masa."
        )

    st.write(f"**Norma / referencia:** {material['standard']}")
    st.caption(material["note"])
    with st.expander("Referencia del material"):
        st.write(material["source"])
        if material["url"]:
            st.link_button("Abrir referencia ↗", material["url"])

# ---------------------------------------------------------------------
# 5. Applications
# ---------------------------------------------------------------------
with tabs[4]:
    st.subheader("De la tabla de perfiles al problema mecánico")

    axis_name = "x–x" if axis_key == "x" else "y–y"
    I = profile["Ix_mm4"] if axis_key == "x" else profile["Iy_mm4"]
    S = profile["Sx_mm3"] if axis_key == "x" else profile["Sy_mm3"]
    r = profile["rx_mm"] if axis_key == "x" else profile["ry_mm"]
    A = profile["A_mm2"]
    E = material["E_GPa"] * 1000.0
    Fy = material["Fy_MPa"]

    st.write(
        f"Para esta pestaña están activos **{profile_name}**, **{material_name}** y el **eje {axis_name}**. "
        "Los resultados son demostraciones de Resistencia de Materiales, no verificaciones normativas."
    )

    i1, i2, i3, i4, i5 = st.columns(5)
    with i1:
        N_kN = st.number_input("Fuerza axial N [kN]", value=0.0, step=10.0)
    with i2:
        V_kN = st.number_input("Cortante V [kN]", value=10.0, step=5.0)
    with i3:
        M_kNm = st.number_input("Momento M [kN·m]", value=10.0, step=5.0)
    with i4:
        L_m = st.number_input("Longitud L [m]", min_value=0.10, value=3.0, step=0.25)
    with i5:
        K = st.number_input("Factor K", min_value=0.10, value=1.0, step=0.10)

    sigma_N = N_kN*1000.0/A
    sigma_b = M_kNm*1e6/S
    sigma_plus = sigma_N + sigma_b
    sigma_minus = sigma_N - sigma_b
    L_mm = L_m*1000.0
    slenderness = K*L_mm/r
    Pcr_N = math.pi**2 * E * I / (K*L_mm)**2
    Pcr_kN = Pcr_N/1000.0
    EI_kNm2 = E*I/1e9
    mass_total = profile["mass_kg_m"]*L_m
    My_kNm = Fy*S/1e6

    st.markdown("### 1. Carga axial")
    a, b = st.columns([1, 1.35], gap="large")
    with a:
        st.latex(r"\sigma_N=\frac{N}{A}")
        st.metric("Tensión axial", f"{sigma_N:.2f} MPa")
    with b:
        st.write(
            "**Qué significa:** si la fuerza pasa por el centroide, la tensión normal se distribuye uniformemente en una sección ideal."
        )
        st.write(
            "**Propiedad que manda:** A. Para el mismo N, una mayor área reduce la tensión axial."
        )

    st.markdown("### 2. Flexión")
    a, b = st.columns([1, 1.35], gap="large")
    with a:
        st.latex(r"\sigma=\frac{My}{I}")
        st.latex(r"\sigma_{\max}=\frac{M}{S}")
        st.metric("Tensión extrema por flexión", f"{sigma_b:.2f} MPa")
        st.metric("Momento para alcanzar Fᵧ · referencia", f"{My_kNm:.2f} kN·m")
    with b:
        st.write(
            "**Qué significa:** la tensión varía linealmente desde cero en el eje neutro hasta un máximo en la fibra extrema."
        )
        st.write(
            f"Para el eje **{axis_name}**, MechLab utiliza I = {I:.4g} mm⁴ y S = {S:.4g} mm³."
        )
        st.write(
            "**Interpretación de diseño:** mover material lejos del eje neutro aumenta I y S sin aumentar el área en la misma proporción; por eso las secciones I/H son eficientes en flexión."
        )

    st.markdown("### 3. Carga axial + flexión")
    a, b = st.columns([1, 1.35], gap="large")
    with a:
        st.latex(r"\sigma=\frac{N}{A}\pm\frac{M}{S}")
        c1, c2 = st.columns(2)
        c1.metric("Fibra +", f"{sigma_plus:.2f} MPa")
        c2.metric("Fibra −", f"{sigma_minus:.2f} MPa")
    with b:
        st.write(
            "Esta superposición representa un caso elástico lineal sencillo. Permite visualizar cómo una carga axial desplaza el diagrama de tensiones producido por flexión."
        )
        st.write(
            "En estructuras reales pueden intervenir interacción normativa, segundo orden, pandeo y otros efectos que no están incluidos aquí."
        )

    st.markdown("### 4. Fuerza cortante en una viga")
    a, b = st.columns([1, 1.35], gap="large")
    with a:
        st.latex(r"τ=\frac{VQ}{I\,t}")
        st.metric("Cortante ingresado", f"{V_kN:.2f} kN")
    with b:
        st.write(
            "**Qué significa:** la tensión cortante depende de la posición dentro de la sección. Q es el primer momento de área de la porción de sección considerada y t es el espesor local."
        )
        st.write(
            "Por eso no se entrega un único valor automático de τ desde la tabla: se necesita definir el punto de evaluación. En perfiles I/H, el alma suele ser la zona dominante para el cortante vertical."
        )

    st.markdown("### 5. Rigidez y deformación")
    a, b = st.columns([1, 1.35], gap="large")
    with a:
        st.latex(r"\kappa=\frac{M}{EI}")
        st.latex(r"EI=E\,I")
        st.metric("Rigidez flexional EI", f"{EI_kNm2:.3g} kN·m²")
    with b:
        st.write(
            "**E** representa al material y **I** a la geometría. Dos vigas del mismo acero pueden deformarse de forma muy distinta si sus I son diferentes."
        )
        st.write(
            "EI es el puente natural entre esta biblioteca y un futuro módulo de deflexión de vigas."
        )

    st.markdown("### 6. Esbeltez y pandeo ideal")
    a, b = st.columns([1, 1.35], gap="large")
    with a:
        st.latex(r"\lambda=\frac{KL}{r}")
        st.latex(r"P_{cr}=\frac{\pi^2EI}{(KL)^2}")
        c1, c2 = st.columns(2)
        c1.metric("KL/r", f"{slenderness:.1f}")
        c2.metric("Pcr Euler", f"{Pcr_kN:.2f} kN")
    with b:
        st.write(
            "**r** condensa la relación entre I y A. El eje con menor r suele ser el candidato crítico para pandeo global."
        )
        st.write(
            "Euler representa una columna ideal, esbelta y perfectamente recta. No reemplaza el diseño normativo de columnas reales."
        )

    st.markdown("### 7. Torsión")
    a, b = st.columns([1, 1.35], gap="large")
    with a:
        if family == "CHS" and profile.get("Jt_mm4"):
            T_kNm = st.number_input("Torque T [kN·m]", value=1.0, step=0.5)
            tau_t = T_kNm*1e6*(profile["Do_mm"]/2)/profile["Jt_mm4"]
            st.latex(r"τ_{\max}=\frac{T\,R}{J}")
            st.metric("τ máxima · CHS", f"{tau_t:.2f} MPa")
        else:
            st.latex(r"\theta'=\frac{T}{GJ_t}")
            st.write("Cálculo directo de tensión no activado para esta geometría.")
    with b:
        if family == "CHS":
            st.write(
                "Para una sección circular, la formulación TR/J es apropiada en torsión de Saint-Venant y la distribución es especialmente simple."
            )
        else:
            st.write(
                "En secciones I, H y U la torsión es más compleja: pueden intervenir Jₜ, alabeo y tensiones no descritas por la fórmula circular Tr/J."
            )
        st.write(
            "En diseño mecánico, una sección cerrada suele ser mucho más eficiente torsionalmente que una sección abierta de masa comparable."
        )

    st.markdown("### 8. Masa y peso propio")
    a, b = st.columns([1, 1.35], gap="large")
    with a:
        st.latex(r"m=m'\,L")
        st.metric(f"Masa para L = {L_m:.2f} m", f"{mass_total:.1f} kg")
    with b:
        st.write(
            "La masa lineal es relevante en manejo, fabricación, transporte, cargas permanentes y estimaciones iniciales de estructura."
        )

# ---------------------------------------------------------------------
# 6. Design and selection
# ---------------------------------------------------------------------
with tabs[5]:
    st.subheader("Cómo utilizar los perfiles en diseño mecánico y estructural")

    st.markdown("### Pensar primero en la solicitación dominante")
    st.write(
        "La familia adecuada depende de qué acción gobierna: flexión en un eje, compresión con riesgo de pandeo, torsión, necesidad de conexiones, masa, espacio disponible o fabricación."
    )

    d1, d2 = st.columns(2, gap="large")
    with d1:
        st.markdown("#### Diseño mecánico")
        st.markdown(
            """
- **Bastidores y bancadas de maquinaria:** interesa rigidez EI, estabilidad y facilidad de soldadura/unión.
- **Skids y bases de equipos:** suelen combinar flexión, carga axial, peso propio y cargas concentradas.
- **Soportes de motores, reductores y equipos:** la deformación puede ser tan importante como la tensión.
- **Marcos de transportadores, chutes y equipos de proceso:** es común trabajar con RHS/SHS, canales o perfiles I/H según carga y fabricación.
- **Estructuras soldadas:** la geometría comercial permite disminuir fabricación respecto de secciones armadas, pero las conexiones y concentraciones de tensión deben verificarse por separado.
- **Elementos sometidos a torsión:** secciones cerradas SHS/RHS/CHS suelen tener ventajas importantes frente a perfiles abiertos.
"""
        )

    with d2:
        st.markdown("#### Diseño estructural")
        st.markdown(
            """
- **Vigas principales y secundarias:** IPE, HEA, HEB o WF aprovechan material alejado del eje neutro.
- **Columnas:** interesa la relación entre A, Iₓ, Iᵧ, rₓ y rᵧ, además de la clasificación y estabilidad de la sección.
- **Marcos resistentes:** la selección combina rigidez, resistencia, esbeltez y conexiones.
- **Arriostramientos:** CHS, SHS, ángulos u otras secciones pueden ser eficientes según conexión y carga axial.
- **Plataformas y estructuras industriales:** UPN, IPE, H y tubulares aparecen frecuentemente como vigas, columnas y miembros secundarios.
- **Diseño real:** además de la resistencia de materiales deben revisarse los estados límite exigidos por la norma aplicable.
"""
        )

    st.markdown("### Lectura rápida por familia")
    selection_rows = [
        {
            "Familia": "IPE",
            "Fortaleza geométrica": "Muy eficiente en flexión sobre eje fuerte",
            "Atención": "Eje débil y torsión",
            "Aplicaciones típicas": "Vigas y marcos",
        },
        {
            "Familia": "HEA / HEB",
            "Fortaleza geométrica": "Mayor equilibrio entre ambos ejes que IPE",
            "Atención": "Masa y conexiones",
            "Aplicaciones típicas": "Vigas, columnas y marcos",
        },
        {
            "Familia": "UPN",
            "Fortaleza geométrica": "Forma abierta práctica para soportes y marcos",
            "Atención": "Centroide excéntrico y torsión",
            "Aplicaciones típicas": "Vigas secundarias, canales, bastidores",
        },
        {
            "Familia": "SHS",
            "Fortaleza geométrica": "Comportamiento similar en x e y; sección cerrada",
            "Atención": "Conexiones y espesores reales",
            "Aplicaciones típicas": "Columnas, marcos, bastidores",
        },
        {
            "Familia": "RHS",
            "Fortaleza geométrica": "Eje fuerte definido + buena respuesta torsional",
            "Atención": "Orientación de la sección",
            "Aplicaciones típicas": "Vigas, bastidores, skids",
        },
        {
            "Familia": "CHS",
            "Fortaleza geométrica": "Simetría + buena eficiencia torsional",
            "Atención": "Conexiones",
            "Aplicaciones típicas": "Columnas, diagonales, marcos tubulares",
        },
    ]
    st.dataframe(selection_rows, width="stretch", hide_index=True)

    st.markdown("### Comparar ejes antes de seleccionar")
    ixiy = profile["Ix_mm4"]/profile["Iy_mm4"] if profile["Iy_mm4"] else float("nan")
    sxsy = profile["Sx_mm3"]/profile["Sy_mm3"] if profile["Sy_mm3"] else float("nan")
    r1, r2, r3 = st.columns(3)
    r1.metric("Iₓ / Iᵧ", f"{ixiy:.2f}")
    r2.metric("Sₓ / Sᵧ", f"{sxsy:.2f}")
    r3.metric("Masa lineal", f"{profile['mass_kg_m']:.2f} kg/m")
    st.caption(
        "Estas razones ayudan a entender la anisotropía geométrica de la sección. Una razón alta indica un eje fuerte muy dominante."
    )

    st.info(
        "La mejor sección no es necesariamente la de mayor I o mayor S. La selección real equilibra solicitaciones, deformación, estabilidad, fabricación, conexiones, disponibilidad, masa y costo.",
        icon="🧭",
    )

# ---------------------------------------------------------------------
# 7. Chile suppliers
# ---------------------------------------------------------------------
with tabs[6]:
    st.subheader("Disponibilidad comercial de referencia en Chile")
    st.write(
        f"Revisión comercial de referencia: **{VERIFIED_DATE}**. "
        "La aparición de una familia en un catálogo no garantiza stock permanente ni el grado específico del acero."
    )

    st.dataframe(MARKET_FAMILIES, width="stretch", hide_index=True)

    st.markdown("#### Proveedores y catálogos")
    for provider in PROVIDERS:
        with st.container(border=True):
            c1, c2 = st.columns([3.4, 1.0], vertical_alignment="center")
            with c1:
                st.markdown(f"**{provider['name']}**")
                st.write(provider["families"])
                st.caption(provider["note"])
            with c2:
                st.link_button("Abrir sitio ↗", provider["url"], width="stretch")

    with st.expander("Referencias técnicas complementarias"):
        source_rows = [
            {"Referencia": x["name"], "Uso": x["role"]}
            for x in TECHNICAL_SOURCES
        ]
        st.dataframe(source_rows, width="stretch", hide_index=True)
        for x in TECHNICAL_SOURCES:
            if x["url"]:
                st.link_button(f"{x['name']} ↗", x["url"])

    st.warning(
        "Antes de especificar o comprar: confirmar dimensiones nominales, masa, tolerancias, norma dimensional, grado del acero, certificado, largo comercial y stock.",
        icon="📌",
    )

st.divider()
st.caption(
    "GG DIMEC · MechLab · Biblioteca pedagógica de perfiles estructurales."
)
