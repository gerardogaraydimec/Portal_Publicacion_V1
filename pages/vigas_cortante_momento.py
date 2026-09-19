from __future__ import annotations

import streamlit as st

from modules.ui_brand import render_app_header
from modules.beam_cases import CASES, FAMILIES
from modules.beam_engine import case_summary, point_state, domain_end
from modules.beam_plotter import make_figure

st.markdown(
    """
<style>
:root{
    --gg-orange:#f28e1c;
    --gg-orange-dark:#db7810;
    --gg-black:#111111;
    --gg-muted:#737986;
    --gg-line:#eceff2;
}

/* Refinamiento V0.2: más aire arriba y ningún recorte del primer bloque/logo. */
.block-container{
    max-width:1480px;
    padding-top:1.35rem !important;
    padding-bottom:2rem;
}
div[data-testid="stMainBlockContainer"] > div:first-child{
    overflow:visible !important;
}
div[data-testid="stImage"],
div[data-testid="stImage"] img{
    overflow:visible !important;
}
div[data-testid="stImage"] img{
    object-fit:contain !important;
}

div[data-testid="stMetric"]{
    border:1px solid #eceff2;
    border-radius:12px;
    padding:.65rem .8rem;
    background:#fff;
}

div[data-testid="stVerticalBlockBorderWrapper"]{
    border-color:#eceff2 !important;
    border-radius:12px !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] .katex-display{
    margin:.25rem 0 .35rem 0 !important;
}
.gg-case-card{
    border:1px solid #eceff2;
    border-left:4px solid #f28e1c;
    border-radius:12px;
    padding:.9rem 1rem;
    background:#fff;
    margin:.25rem 0 .8rem 0;
}
.gg-note{
    border-radius:12px;
    padding:.9rem 1rem;
    background:#f7f7f5;
    border:1px solid #ecece8;
    line-height:1.52;
}
.gg-mini{
    color:#737986;
    font-size:.90rem;
}
.gg-library{
    display:inline-block;
    background:#111;
    color:#fff;
    border-radius:999px;
    padding:.28rem .68rem;
    font-size:.78rem;
    font-weight:700;
    letter-spacing:.025em;
    margin-bottom:.25rem;
}
@media (max-width:760px){
    .block-container{padding-top:1.15rem !important;}
}
</style>
""",
    unsafe_allow_html=True,
)

# Small spacer above common header helps prevent clipping inside Streamlit navigation shells.
st.markdown('<div style="height:0.20rem"></div>', unsafe_allow_html=True)

render_app_header(
    title="Diagramas de Cortante y Momento · Vigas Básicas",
    subtitle="Biblioteca clásica interactiva · apoyos · reacciones · fuerza cortante V(x) · momento flector M(x) · interpretación.",
    section="RESISTENCIA DE MATERIALES",
    logo_width=188,
)

all_case_ids = [cid for ids in FAMILIES.values() for cid in ids]

# ---------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("Selección del caso")

    family = st.selectbox(
        "Tipo de viga",
        list(FAMILIES.keys()),
        help="Selecciona primero la condición de apoyo y luego uno de los casos elementales disponibles.",
    )

    ids = FAMILIES[family]
    labels = {cid: CASES[cid]["title"] for cid in ids}
    case_id = st.selectbox(
        "Caso de carga",
        ids,
        format_func=lambda cid: labels[cid],
    )

    case = CASES[case_id]

    st.divider()
    st.subheader("Parámetros")

    L_label = (
        "Longitud entre apoyos L [m]"
        if case_id == "simple_overhang_load"
        else "Longitud L [m]"
    )
    L = st.number_input(
        L_label,
        min_value=0.10,
        value=6.0,
        step=0.25,
        format="%.2f",
    )
    p = {"L": float(L)}

    if "F" in case["parameters"]:
        p["F"] = float(st.number_input(
            "Carga F [kN]",
            min_value=0.0,
            value=20.0,
            step=1.0,
            format="%.2f",
        ))

    if "w" in case["parameters"]:
        p["w"] = float(st.number_input(
            "Carga distribuida w [kN/m]",
            min_value=0.0,
            value=5.0,
            step=0.5,
            format="%.2f",
        ))

    if "M0" in case["parameters"]:
        p["M0"] = float(st.number_input(
            "Momento M₀ [kN·m]",
            value=30.0,
            step=2.5,
            format="%.2f",
            help="M₀ positivo se representa en sentido antihorario.",
        ))

    if "a" in case["parameters"]:
        a_mode = case.get("a_mode", "position")

        if a_mode == "position":
            amin = max(0.01, 0.01 * L)
            amax = max(amin + 1e-6, 0.99 * L)
            default_a = min(max(0.40 * L, amin), amax)
            p["a"] = float(st.number_input(
                "Posición de la carga a [m]",
                min_value=float(amin),
                max_value=float(amax),
                value=float(default_a),
                step=max(0.01, L/100.0),
                format="%.3f",
                help="a se mide desde el extremo izquierdo de la viga.",
            ))

        elif a_mode == "symmetric_offset":
            amin = max(0.01, 0.01 * L)
            amax = max(amin + 1e-6, 0.49 * L)
            default_a = min(max(0.25 * L, amin), amax)
            p["a"] = float(st.number_input(
                "Separación simétrica a [m]",
                min_value=float(amin),
                max_value=float(amax),
                value=float(default_a),
                step=max(0.01, L/100.0),
                format="%.3f",
                help="Las cargas se ubican en x=a y x=L−a; por eso debe cumplirse a<L/2.",
            ))

        elif a_mode == "overhang_length":
            p["a"] = float(st.number_input(
                "Longitud del voladizo a [m]",
                min_value=0.01,
                value=max(0.50, 0.30 * L),
                step=max(0.01, L/100.0),
                format="%.3f",
                help="L es la distancia entre apoyos y a es la longitud exterior hasta la carga.",
            ))

    st.divider()
    st.caption(
        "Unidades: m · kN · kN/m · kN·m. "
        "Cada selección corresponde a un caso elemental; no se superponen cargas."
    )
    st.success("Biblioteca completa · 16 casos clásicos disponibles", icon="✅")

summary = case_summary(case_id, p)
case_number = all_case_ids.index(case_id) + 1

st.markdown(
    f"""
<div class="gg-case-card">
<div class="gg-library">CASO {case_number:02d} / 16</div><br>
<b>{summary['family']} · {summary['title']}</b><br>
<span class="gg-mini">{summary['classification']} · Caso elemental sin superposición de cargas.</span>
</div>
""",
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "📘 Cómo usar",
    "📊 Esquema y diagramas",
    "∑ Ecuaciones",
    "🧠 Interpretación",
])

# ---------------------------------------------------------------------
# Tab 1: How to use
# ---------------------------------------------------------------------
with tabs[0]:
    c1, c2 = st.columns([1.15, 0.85], gap="large")

    with c1:
        st.subheader("Qué hace esta herramienta")
        st.write(
            "Este módulo funciona como una **tabla clásica de vigas llevada a un entorno interactivo**. "
            "Selecciona una configuración básica, modifica sus parámetros y observa cómo cambian "
            "las reacciones, el diagrama de fuerza cortante y el diagrama de momento flector."
        )

        st.markdown("#### Flujo recomendado")
        st.markdown(
            """
1. **Selecciona el tipo de viga y el caso elemental.**
2. **Modifica** longitud, carga y posición cuando corresponda.
3. En **Esquema y diagramas**, mueve la posición de análisis `x`.
4. Revisa en **Ecuaciones** las expresiones analíticas del caso.
5. Usa **Interpretación** para relacionar la forma de los diagramas con el comportamiento físico.
"""
        )

        st.markdown("#### Alcance de la biblioteca")
        st.write(
            "La versión actual reúne **16 configuraciones clásicas**: voladizos, vigas simplemente apoyadas, "
            "vigas empotradas con apoyo simple y vigas empotradas en ambos extremos. "
            "No combina cargas ni permite construir una viga arbitraria: el foco es comprender bien cada caso base."
        )

        if "Hiperestática" in summary["classification"]:
            st.warning(
                "En los casos hiperestáticos, las reacciones mostradas corresponden a las soluciones clásicas "
                "de viga prismática bajo comportamiento lineal elástico y pequeñas deformaciones.",
                icon="📌",
            )

    with c2:
        st.subheader("Convención y lectura")
        st.latex(r"V(x)=\frac{dM(x)}{dx}")
        st.latex(r"\Delta M=\int V(x)\,dx")
        st.markdown(
            """
<div class="gg-note">
<b>Idea clave:</b><br>
• Una <b>carga puntual</b> produce un salto en V.<br>
• Una <b>carga distribuida uniforme</b> hace que V sea lineal y M parabólico.<br>
• Un <b>momento concentrado</b> produce un salto directo en M.<br>
• Si V=0 en un tramo, M permanece constante.<br>
• Un cambio de signo de M indica un <b>punto de contraflexión</b>.
</div>
""",
            unsafe_allow_html=True,
        )
        st.caption(
            "La coordenada x se mide desde el extremo izquierdo. "
            "En el caso con voladizo exterior, L corresponde a la distancia entre apoyos y la longitud total es L+a."
        )

# ---------------------------------------------------------------------
# Tab 2: diagrams
# ---------------------------------------------------------------------
with tabs[1]:
    total = domain_end(case_id, p)

    if case_id == "simple_overhang_load":
        default_x = p["L"]
    elif case_id == "simple_twin_loads":
        default_x = p["L"] / 2.0
    elif case.get("a_mode") == "position":
        default_x = p["a"]
    else:
        default_x = total / 2.0

    x_probe = st.slider(
        "Posición de análisis x [m]",
        min_value=0.0,
        max_value=float(total),
        value=float(default_x),
        step=max(0.001, total/350.0),
        key=f"x_probe_{case_id}",
        help="La línea naranja recorre simultáneamente el esquema, V(x) y M(x).",
    )

    state = point_state(case_id, p, x_probe)

    st.markdown("#### Reacciones")
    reactions = summary["reactions"]

    reaction_symbol_latex = {
        "R_A": r"R_A",
        "R_B": r"R_B",
        "M_A": r"M_A",
        "M_B": r"M_B",
        "|M_A|": r"\left|M_A\right|",
    }
    reaction_unit_latex = {
        "kN": r"\mathrm{kN}",
        "kN·m": r"\mathrm{kN\cdot m}",
    }

    cols = st.columns(len(reactions))
    for col, r in zip(cols, reactions):
        symbol_tex = reaction_symbol_latex.get(r["symbol"], r["symbol"])
        unit_tex = reaction_unit_latex.get(r["unit"], rf"\mathrm{{{r['unit']}}}")
        with col:
            with st.container(border=True):
                st.latex(
                    rf"{symbol_tex} = {r['value']:.3f}\,{unit_tex}"
                )
                if r["sense"]:
                    st.caption(f"Sentido: {r['sense']}")

    st.markdown("#### Lectura en la sección seleccionada")
    if state["V_left"] is not None and abs(state["V_left"] - state["V_right"]) > 1e-7:
        c1, c2, c3 = st.columns(3)
        c1.metric("x", f"{x_probe:.3f} m")
        c2.metric("V(x⁻)", f"{state['V_left']:.3f} kN")
        c3.metric("V(x⁺)", f"{state['V_right']:.3f} kN")
        st.caption(
            "La sección coincide con una discontinuidad de cortante; "
            "se muestran los valores inmediatamente a izquierda y derecha."
        )

    elif state["M_left"] is not None and abs(state["M_left"] - state["M_right"]) > 1e-7:
        c1, c2, c3 = st.columns(3)
        c1.metric("x", f"{x_probe:.3f} m")
        c2.metric("M(x⁻)", f"{state['M_left']:.3f} kN·m")
        c3.metric("M(x⁺)", f"{state['M_right']:.3f} kN·m")
        st.caption(
            "La sección coincide con un momento concentrado; "
            "el diagrama de momento presenta una discontinuidad."
        )

    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("x", f"{x_probe:.3f} m")
        c2.metric("V(x)", f"{state['V']:.3f} kN")
        c3.metric("M(x)", f"{state['M']:.3f} kN·m")

    fig = make_figure(case_id, p, x_probe)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

    ext = summary["extrema"]
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Máximo |V|", f"{ext['V_abs']:.3f} kN")
    e2.metric("Máximo |M|", f"{ext['M_abs']:.3f} kN·m")
    e3.metric("M máximo", f"{ext['M_max']:.3f} kN·m")
    e4.metric("M mínimo", f"{ext['M_min']:.3f} kN·m")

    st.caption(
        f"|V|max en x ≈ {ext['V_x']:.3f} m · "
        f"|M|max en x ≈ {ext['M_abs_x']:.3f} m."
    )

# ---------------------------------------------------------------------
# Tab 3: equations
# ---------------------------------------------------------------------
with tabs[2]:
    eq = summary["equations"]

    st.subheader("Reacciones")
    for formula in eq["reactions"]:
        st.latex(formula)

    st.subheader("Fuerza cortante")
    for formula in eq["shear"]:
        st.latex(formula)

    st.subheader("Momento flector")
    for formula in eq["moment"]:
        st.latex(formula)

    st.markdown(
        """
<div class="gg-note">
<b>Cómo leer una expresión por tramos</b><br>
Una carga puntual cambia el valor del cortante al cruzar su posición. Un momento concentrado
cambia directamente el valor del momento. Por eso algunos casos requieren ecuaciones diferentes
antes y después del punto de aplicación.
</div>
""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------
# Tab 4: interpretation
# ---------------------------------------------------------------------
with tabs[3]:
    st.subheader("Qué deberías observar")
    a, b, c = st.columns(3)
    a.markdown(f"**Tipo de estructura**\n\n{summary['classification']}")
    b.markdown(f"**Forma de V(x)**\n\n{summary['v_shape']}")
    c.markdown(f"**Forma de M(x)**\n\n{summary['m_shape']}")

    st.markdown("#### Lectura física del caso")
    st.info(summary["insight"], icon="💡")

    internal_zeros = [
        z for z in summary["moment_zeros"]
        if z > 1e-5 * summary["domain_end"]
        and z < (1 - 1e-5) * summary["domain_end"]
    ]
    if internal_zeros:
        st.markdown("#### Puntos internos donde M(x)=0")
        st.write(
            " · ".join([f"x ≈ **{z:.3f} m**" for z in internal_zeros])
        )
        if "Hiperestática" in summary["classification"]:
            st.caption(
                "Cuando el momento cambia de signo en esos puntos, corresponden a puntos de contraflexión del caso ideal."
            )

    st.markdown("#### Preguntas para estudiar")
    st.markdown(
        """
- ¿Dónde cambia de valor el cortante y qué carga o reacción provoca ese cambio?
- ¿Dónde la pendiente del diagrama de momento cambia?
- ¿Coincide un extremo de M con un punto donde V es cero o cambia de signo?
- ¿Qué efecto tiene aumentar L manteniendo la carga?
- ¿Qué parte del diagrama cambia de forma y qué parte solo cambia de escala?
- En los casos hiperestáticos, ¿qué efecto tiene restringir el giro de los extremos?
"""
    )

    st.markdown("#### Siguiente nivel")
    st.write(
        "El módulo se mantiene enfocado en **carga → reacciones → cortante → momento**. "
        "Pendiente y deformación se trabajarán como una extensión separada para conservar claridad pedagógica."
    )

st.divider()
st.caption(
    "GG DIMEC · MechLab · Herramienta pedagógica de Resistencia de Materiales · "
    "Biblioteca completa de 16 casos elementales clásicos."
)
