from __future__ import annotations

import streamlit as st

from modules.ui_brand import render_app_header
from modules.beam_cases import CASES, FAMILIES
from modules.beam_engine import case_summary, point_state, domain_end
from modules.beam_plotter import make_figure
from modules.beam_deflection import (
    section_properties,
    euler_bernoulli_response,
    response_at_x,
    classic_reference,
    slenderness_hint,
)
from modules.beam_deflection_plotter import make_deflection_figure, make_section_figure
from modules.beam_stress import section_stress_response
from modules.beam_stress_plotter import make_stress_distribution_figure

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
    title="Vigas · Cortante, Momento y Deflexión",
    subtitle="Cargas · reacciones · V(x) · M(x) · σx(y) · τxy(y) · curvatura κ(x) · pendiente θ(x) · deflexión v(x).",
    section="RESISTENCIA Y ESTRUCTURAS",
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
    st.subheader("Material y sección")

    material = st.selectbox(
        "Material",
        ["Acero · E=200 GPa", "Aluminio · E=69 GPa", "Madera · E=12 GPa", "Personalizado"],
        help="E se utiliza para la rigidez a flexión EI y para la deformación de la viga.",
    )
    material_E = {
        "Acero · E=200 GPa": 200.0,
        "Aluminio · E=69 GPa": 69.0,
        "Madera · E=12 GPa": 12.0,
    }
    if material == "Personalizado":
        young_gpa = float(st.number_input("Módulo de Young E [GPa]", min_value=0.001, value=200.0, step=1.0, format="%.3f"))
    else:
        young_gpa = material_E[material]
        st.caption(f"E = {young_gpa:g} GPa")

    section_type = st.selectbox(
        "Sección transversal",
        ["Rectangular", "Circular maciza", "Tubular circular", "Propiedades ingresadas"],
    )
    section_params = {}
    if section_type == "Rectangular":
        section_params["b_mm"] = float(st.number_input("Ancho b [mm]", min_value=1.0, value=100.0, step=5.0))
        section_params["h_mm"] = float(st.number_input("Altura h [mm]", min_value=1.0, value=200.0, step=5.0))
    elif section_type == "Circular maciza":
        section_params["d_mm"] = float(st.number_input("Diámetro d [mm]", min_value=1.0, value=100.0, step=5.0))
    elif section_type == "Tubular circular":
        section_params["do_mm"] = float(st.number_input("Diámetro exterior Dₒ [mm]", min_value=2.0, value=120.0, step=5.0))
        section_params["t_mm"] = float(st.number_input("Espesor t [mm]", min_value=0.5, value=8.0, step=0.5))
    else:
        section_params["area_mm2"] = float(st.number_input("Área A [mm²]", min_value=1.0, value=20000.0, step=100.0))
        section_params["inertia_mm4"] = float(st.number_input("Segundo momento de área I [mm⁴]", min_value=1.0, value=6.6667e7, step=1.0e6, format="%.3e"))
        section_params["c_mm"] = float(st.number_input("Distancia a fibra extrema c [mm]", min_value=0.1, value=100.0, step=5.0, help="Se requiere para calcular σ=−My/I cuando la geometría no está dibujada."))

    st.divider()
    st.caption(
        "Unidades de cargas: m · kN · kN/m · kN·m. "
        "Propiedades de sección: mm, mm² y mm⁴."
    )
    st.success("Biblioteca completa · 16 casos clásicos disponibles", icon="✅")

summary = case_summary(case_id, p)
case_number = all_case_ids.index(case_id) + 1

section_props = section_properties(section_type, section_params)
deflection_result = euler_bernoulli_response(
    case_id,
    p,
    young_gpa=young_gpa,
    inertia_mm4=section_props.inertia_mm4,
)

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
    "📐 Sección y material",
    "🧱 Tensiones en la sección",
    "〰️ Deflexión",
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
            "El módulo sigue la secuencia completa de análisis de vigas: "
            "**cargas → reacciones → V(x) → M(x) → tensiones en la sección → curvatura → pendiente → deflexión**. "
            "La idea es conectar el equilibrio global con lo que ocurre dentro de una sección transversal y, finalmente, con la deformada."
        )

        st.markdown("#### Flujo recomendado")
        st.markdown(
            """
1. Selecciona **apoyos, caso de carga y dimensiones**.
2. Define **material y sección transversal**.
3. En **Esquema y diagramas**, mueve la posición `x` y observa reacciones, `V(x)` y `M(x)`.
4. En **Tensiones en la sección**, conecta `M(x)` con `σx(y)` y `V(x)` con `τxy(y)`.
5. En **Deflexión**, observa `κ(x)`, `θ(x)` y `v(x)`.
6. Usa **Ecuaciones** para revisar la cadena diferencial completa y las expresiones del caso seleccionado.
"""
        )

        st.markdown("#### Regla de los cortes")
        st.info(
            "Cuando cambia una carga o aparece una fuerza/momento concentrado, el análisis debe plantearse por tramos. "
            "Conviene imaginar cortes **antes, en torno y después** de la discontinuidad para identificar correctamente V(x) y M(x).",
            icon="✂️",
        )

        if "Hiperestática" in summary["classification"]:
            st.warning(
                "En los casos hiperestáticos, las reacciones mostradas corresponden a soluciones clásicas de viga prismática, "
                "material lineal elástico y pequeñas deformaciones.",
                icon="📌",
            )

    with c2:
        st.subheader("Convención de signos usada")
        st.latex(r"w>0\;\text{hacia abajo}")
        st.latex(r"\frac{dV}{dx}=w(x)")
        st.latex(r"\frac{dM}{dx}=-V(x)")
        st.latex(r"\frac{d^2M}{dx^2}=-w(x)")
        st.markdown(
            """
<div class="gg-note">
<b>Lectura rápida:</b><br>
• Una <b>fuerza puntual</b> produce un salto en V.<br>
• Una <b>carga distribuida</b> cambia la pendiente de V.<br>
• Un <b>momento concentrado</b> produce un salto directo en M.<br>
• Si V=0 en un tramo, M permanece constante.<br>
• Donde V cambia de signo puede aparecer un extremo de M.<br>
• Un cambio de signo de M identifica una posible <b>contraflexión</b>.
</div>
""",
            unsafe_allow_html=True,
        )
        st.caption(
            "La coordenada x se mide desde el extremo izquierdo. La convención se mantiene igual en diagramas, ecuaciones y tensiones."
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

    st.info(
        "La línea naranja representa el corte imaginario. Al moverla puedes comparar directamente la posición x con V(x), M(x) y, en la pestaña siguiente, con las tensiones de esa sección.",
        icon="✂️",
    )

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
# Tab 3: section and material
# ---------------------------------------------------------------------
with tabs[2]:
    st.subheader("Geometría, eje neutro y rigidez a flexión")
    c1, c2 = st.columns([0.92, 1.08], gap="large")

    with c1:
        st.plotly_chart(
            make_section_figure(section_type, section_params),
            use_container_width=True,
            config={"displaylogo": False},
            key=f"section_{section_type}",
        )

    with c2:
        st.markdown(f"### {section_props.description}")
        a, b, c = st.columns(3)
        a.metric("Área A", f"{section_props.area_mm2:,.1f} mm²")
        b.metric("Segundo momento I", f"{section_props.inertia_mm4:,.3e} mm⁴")
        c.metric("Radio de giro rᵍ", f"{section_props.radius_gyration_mm:.2f} mm")

        st.markdown("#### Eje neutro")
        st.write(
            "Para las secciones simétricas incluidas aquí, el eje neutro pasa por el centroide y corresponde a **y=0**. "
            "En flexión simple, allí el esfuerzo normal σx es nulo."
        )
        st.latex(r"\int_A y\,dA=0")

        st.markdown("#### Rigidez a flexión")
        ei_knm2 = young_gpa * 1e9 * section_props.inertia_mm4 * 1e-12 / 1e3
        st.latex(rf"E = {young_gpa:g}\,\mathrm{{GPa}}")
        st.latex(rf"EI = {ei_knm2:,.3f}\,\mathrm{{kN\,m^2}}")

    if section_type == "Rectangular":
        st.latex(r"A=bh")
        st.latex(r"I=\frac{bh^3}{12}")
        st.info(
            "En una sección rectangular, la altura h entra al cubo en I. Por eso aumentar h suele ser mucho más efectivo que aumentar b para reducir deflexión y tensión de flexión.",
            icon="📌",
        )
    elif section_type == "Circular maciza":
        st.latex(r"A=\frac{\pi d^2}{4}")
        st.latex(r"I=\frac{\pi d^4}{64}")
    elif section_type == "Tubular circular":
        st.latex(r"A=\frac{\pi}{4}\left(D_o^2-D_i^2\right)")
        st.latex(r"I=\frac{\pi}{64}\left(D_o^4-D_i^4\right)")
        st.caption("Con Dᵢ = Dₒ − 2t.")
    else:
        st.write(
            "Con A, I y c ingresados se puede calcular rigidez y esfuerzo normal por flexión. "
            "Para obtener la distribución de corte τ=VQ/(It) se necesita además la geometría local de la sección."
        )

    slender = slenderness_hint(p["L"], section_props.radius_gyration_mm)
    st.markdown("#### Indicador geométrico")
    st.latex(rf"\frac{{L}}{{r_g}} = {slender:.1f}")
    st.caption(
        "Es un indicador geométrico descriptivo; no se usa como criterio normativo ni como límite automático de validez."
    )

# ---------------------------------------------------------------------
# Tab 4: section stresses
# ---------------------------------------------------------------------
with tabs[3]:
    st.subheader("De V(x) y M(x) a las tensiones de la sección")

    # At an exact discontinuity, the internal force may have a left and a right value.
    v_jump = state["V_left"] is not None and abs(state["V_left"] - state["V_right"]) > 1e-7
    m_jump = state["M_left"] is not None and abs(state["M_left"] - state["M_right"]) > 1e-7

    side = "Derecha x⁺"
    if v_jump or m_jump:
        side = st.radio(
            "La sección coincide con una discontinuidad. Elige el lado del corte:",
            ["Izquierda x⁻", "Derecha x⁺"],
            horizontal=True,
            key=f"stress_side_{case_id}",
        )

    if side == "Izquierda x⁻":
        shear_for_stress = state["V_left"] if state["V_left"] is not None else state["V"]
        moment_for_stress = state["M_left"] if state["M_left"] is not None else state["M"]
    else:
        shear_for_stress = state["V_right"] if state["V_right"] is not None else state["V"]
        moment_for_stress = state["M_right"] if state["M_right"] is not None else state["M"]

    stress = section_stress_response(
        section_type,
        section_params,
        inertia_mm4=section_props.inertia_mm4,
        moment_knm=moment_for_stress,
        shear_kn=shear_for_stress,
    )

    a, b, c, d = st.columns(4)
    a.metric("x", f"{x_probe:.3f} m")
    b.metric("V usado", f"{shear_for_stress:.3f} kN")
    c.metric("M usado", f"{moment_for_stress:.3f} kN·m")
    d.metric("|σ|max", f"{stress.sigma_max_abs_mpa:.3f} MPa")

    st.plotly_chart(
        make_stress_distribution_figure(stress),
        use_container_width=True,
        config={"displaylogo": False},
        key=f"stress_{case_id}_{section_type}",
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("σ superior", f"{stress.sigma_top_mpa:.3f} MPa")
    c2.metric("σ inferior", f"{stress.sigma_bottom_mpa:.3f} MPa")
    if stress.shear_available:
        c3.metric("|τ|max", f"{stress.tau_max_abs_mpa:.3f} MPa")
        c4.metric("y de |τ|max", f"{stress.tau_max_y_mm:.2f} mm")
    else:
        c3.metric("|τ|max", "—")
        c4.metric("Flujo q", "—")

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("#### Flexión normal")
        st.latex(r"\sigma_x(x,y)=-\frac{M(x)}{I_z}y")
        st.write(
            "La distribución es lineal: el eje neutro tiene σx=0 y las fibras extremas concentran el mayor valor absoluto. "
            "El signo indica tracción o compresión según la convención adoptada."
        )
    with right:
        st.markdown("#### Corte en la sección")
        st.latex(r"\tau_{xy}(x,y)=\frac{V(x)Q(y)}{I_z\,t(y)}")
        st.latex(r"q(y)=\tau_{xy}\,t(y)=\frac{VQ}{I_z}")
        st.write(stress.note)
        if stress.q_max_abs_n_per_mm is not None:
            st.caption(f"Máximo |q| ≈ {stress.q_max_abs_n_per_mm:.3f} N/mm (numéricamente igual a kN/m).")

    if section_type == "Rectangular":
        st.markdown("#### Caso rectangular")
        st.latex(r"\tau_{xy}(y)=\frac{3V}{2A}\left(1-\frac{4y^2}{h^2}\right)")
        st.caption("La distribución es parabólica, nula en las superficies superior/inferior y máxima en el eje neutro.")

# ---------------------------------------------------------------------
# Tab 5: deflection
# ---------------------------------------------------------------------
with tabs[4]:
    st.subheader("Pendiente y curva elástica · Euler–Bernoulli")

    probe_def = response_at_x(deflection_result, x_probe)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("x", f"{x_probe:.3f} m")
    c2.metric("M(x)", f"{probe_def['moment_knm']:.3f} kN·m")
    c3.metric("θ(x)", f"{probe_def['slope_rad']*1e3:.4f} mrad")
    c4.metric("v(x)", f"{probe_def['deflection_m']*1e3:.4f} mm")

    st.plotly_chart(
        make_deflection_figure(deflection_result, x_probe=x_probe),
        use_container_width=True,
        config={"displaylogo": False},
        key=f"deflection_{case_id}",
    )

    a, b, c = st.columns(3)
    a.metric("Máximo |v|", f"{deflection_result.max_abs_deflection_m*1e3:.4f} mm")
    b.metric("Ubicación", f"x ≈ {deflection_result.max_abs_deflection_x_m:.3f} m")
    c.metric("Máximo |θ|", f"{deflection_result.max_abs_slope_rad*1e3:.4f} mrad")

    st.markdown("#### De momento a deformación")
    e1, e2, e3 = st.columns(3)
    with e1:
        st.latex(r"\kappa(x)=\frac{M(x)}{EI}")
        st.caption("Curvatura de la línea neutra.")
    with e2:
        st.latex(r"\frac{d\theta}{dx}=\frac{M(x)}{EI}")
        st.caption("La curvatura modifica la rotación de la sección.")
    with e3:
        st.latex(r"\theta\approx\frac{dv}{dx}")
        st.caption("Para pequeñas pendientes, integrar nuevamente entrega la deflexión.")

    reference = classic_reference(case_id, p, young_gpa, section_props.inertia_mm4)
    if reference is not None:
        err = abs(deflection_result.max_abs_deflection_m - reference) / max(abs(reference), 1e-30) * 100.0
        st.markdown("#### Verificación con solución clásica")
        r1, r2, r3 = st.columns(3)
        r1.metric("Referencia analítica", f"{reference*1e3:.4f} mm")
        r2.metric("Integración MechLab", f"{deflection_result.max_abs_deflection_m*1e3:.4f} mm")
        r3.metric("Diferencia", f"{err:.3f} %")

    if deflection_result.support_residual_mm > 0.005:
        st.warning(
            f"Residuo cinemático numérico ≈ {deflection_result.support_residual_mm:.4f} mm. "
            "Aumentar la resolución de integración puede ser necesario para esta combinación.",
            icon="⚠️",
        )

    st.markdown(
        """
<div class="gg-note">
<b>Qué representa esta curva:</b><br>
La deformada se obtiene integrando la curvatura asociada al diagrama de momento y aplicando las condiciones cinemáticas de los apoyos. 
En esta etapa se utiliza <b>Euler–Bernoulli</b>: la deformación por corte no se incorpora todavía al valor de v(x).
</div>
""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------
# Tab 6: equations
# ---------------------------------------------------------------------
with tabs[5]:
    eq = summary["equations"]

    st.subheader("Cadena diferencial usada en el módulo")
    e1, e2, e3, e4 = st.columns(4)
    with e1:
        st.latex(r"\frac{dV}{dx}=w(x)")
        st.caption("w positivo hacia abajo.")
    with e2:
        st.latex(r"\frac{dM}{dx}=-V(x)")
        st.caption("V controla la pendiente de M.")
    with e3:
        st.latex(r"\frac{d\theta}{dx}=\frac{M}{EI}")
        st.caption("M/EI es la curvatura.")
    with e4:
        st.latex(r"\theta\approx\frac{dv}{dx}")
        st.caption("Pequeñas pendientes.")

    st.latex(r"\frac{d^2M}{dx^2}=-w(x)")
    st.latex(r"EI\frac{d^2v}{dx^2}=M(x)")
    st.latex(r"\frac{d^4v}{dx^4}=-\frac{w(x)}{EI}")

    st.subheader("Reacciones del caso seleccionado")
    for formula in eq["reactions"]:
        st.latex(formula)

    st.subheader("Fuerza cortante V(x)")
    for formula in eq["shear"]:
        st.latex(formula)

    st.subheader("Momento flector M(x)")
    for formula in eq["moment"]:
        st.latex(formula)

    st.subheader("Tensiones en la sección")
    st.latex(r"\sigma_x=-\frac{M}{I_z}y")
    st.latex(r"\tau_{xy}=\frac{VQ}{I_z t}")
    st.latex(r"q=\tau t=\frac{VQ}{I_z}")

    st.markdown(
        """
<div class="gg-note">
<b>Lectura integrada:</b><br>
Las cargas externas y los apoyos fijan las reacciones. Los cortes entregan V(x) y M(x). 
Luego, M determina la distribución de esfuerzo normal y la curvatura, mientras V determina la distribución de corte. 
La integración de la curvatura con las condiciones cinemáticas de los apoyos entrega θ(x) y v(x).
</div>
""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------
# Tab 7: interpretation
# ---------------------------------------------------------------------
with tabs[6]:
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
        st.write(" · ".join([f"x ≈ **{z:.3f} m**" for z in internal_zeros]))
        if "Hiperestática" in summary["classification"]:
            st.caption("Si M cambia de signo, esos puntos corresponden a contraflexión del modelo ideal.")

    st.markdown("#### Conexión entre diagramas y sección")
    st.markdown(
        f"""
- La carga y los apoyos determinan **V(x)** y **M(x)**.
- En la sección elegida, **M(x)** genera `σx(y)` y **V(x)** genera `τxy(y)`.
- Con la sección actual, `I = {section_props.inertia_mm4:,.3e} mm⁴` y `E = {young_gpa:g} GPa`.
- La rigidez **EI** controla la curvatura y, por integración, la deformada.
- El máximo desplazamiento calculado es **{deflection_result.max_abs_deflection_m*1e3:.4f} mm** en `x ≈ {deflection_result.max_abs_deflection_x_m:.3f} m`.
"""
    )

    st.markdown("#### Preguntas para estudiar")
    st.markdown(
        """
- ¿Qué ocurre con V al atravesar una fuerza puntual?
- ¿Cómo cambia M cuando V es constante? ¿Y cuando V es lineal?
- ¿Dónde se ubica el eje neutro y por qué σx es cero allí?
- ¿Por qué |σx| es máximo en las fibras extremas?
- En una sección rectangular, ¿por qué τ es máximo cerca del eje neutro y cero en las superficies libres?
- ¿Qué representa Q en la expresión τ=VQ/(It)?
- ¿Dónde la pendiente θ(x) vale cero y cómo se relaciona con un extremo de v(x)?
- ¿Cómo cambia la deflexión al aumentar E o I?
"""
    )

    st.markdown("#### Próximas ampliaciones")
    st.write(
        "La base queda preparada para incorporar secciones compuestas, teorema de ejes paralelos, perfiles de pared delgada, flujo de corte avanzado y centro de cortadura. "
        "Después de consolidar esa lectura, la comparación Euler–Bernoulli / Timoshenko permitirá añadir explícitamente la deformación por corte."
    )

st.divider()
st.caption(
    "GG DIMEC · MechLab · Resistencia y Estructuras · "
    "Vigas: cargas, corte, flexión, tensiones y deflexión."
)
