from __future__ import annotations

import math
import streamlit as st

from modules.ui_brand import render_app_header
from modules.metrology_data import (
    AUTO_HOLE_BASE_SHAFTS,
    AUTO_SHAFT_BASE_HOLES,
    COMMON_FITS,
    FUNCTION_STARTERS,
    PROCESS_GUIDANCE,
    MEASUREMENT_GUIDANCE,
    MANUAL_EXAMPLES,
)
from modules.tolerance_engine import (
    automatic_hole_basis_fit,
    automatic_shaft_basis_fit,
    manual_fit,
    compare_designations,
    it_width_um,
    get_size_step,
    geometric_mean_step,
    tolerance_unit_i,
    measured_status,
)
from modules.engineering_support import (
    MATERIALS,
    thermal_fit,
    temperature_change_for_target_clearance,
    process_capability,
    normal_curve_points,
    mounting_guidance,
    operational_checks,
    suggested_quality_plan,
)

from modules.tolerance_plotter import (
    make_tolerance_zone_figure,
    make_fit_interval_figure,
    make_it_grade_figure,
    make_process_cost_figure,
    make_measurement_position_figure,
    make_capability_figure,
    make_thermal_clearance_figure,
)


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
.gg-case{
  border:1px solid var(--gg-line);
  border-left:5px solid var(--gg-orange);
  border-radius:14px;
  padding:1rem 1.1rem;
  background:#fff;
  margin:.25rem 0 .85rem 0;
}
.gg-note{
  border:1px solid #ecece8;
  background:#f7f7f5;
  border-radius:12px;
  padding:.95rem 1rem;
  line-height:1.58;
}
.gg-warning{
  border-left:4px solid var(--gg-orange);
  background:#fff8ef;
  border-radius:9px;
  padding:.85rem 1rem;
  line-height:1.55;
}
.gg-step{
  border:1px solid var(--gg-line);
  border-radius:12px;
  padding:.9rem 1rem;
  background:#fff;
  margin-bottom:.55rem;
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
    title="Ajustes y Tolerancias ISO · Diseño, Fabricación, Calidad y Montaje",
    subtitle="Tolerancias · ajustes · fabricación · capacidad de proceso · control de calidad · montaje · temperatura · verificación.",
    section="METROLOGÍA Y FABRICACIÓN",
    logo_width=188,
)


def latex_card(title: str, formula: str, caption: str):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.latex(formula)
        st.caption(caption)


def render_fit_summary(fit, key_prefix="fit"):

    if not fit.ok:
        st.error(fit.message)
        return

    h1, h2, h3, h4 = st.columns(4)
    h1.metric("Agujero mín.", f"{fit.hole_min_mm:.3f} mm")
    h2.metric("Agujero máx.", f"{fit.hole_max_mm:.3f} mm")
    h3.metric("Eje mín.", f"{fit.shaft_min_mm:.3f} mm")
    h4.metric("Eje máx.", f"{fit.shaft_max_mm:.3f} mm")

    c1, c2, c3 = st.columns(3)
    c1.metric("Juego mínimo", f"{fit.clearance_min_um:.0f} µm")
    c2.metric("Juego máximo", f"{fit.clearance_max_um:.0f} µm")
    c3.metric("Tipo de ajuste", fit.fit_type)

    st.plotly_chart(
        make_tolerance_zone_figure(fit),
        width="stretch",
        config={"displaylogo": False},
        key=f"{key_prefix}_zone",
    )
    st.plotly_chart(
        make_fit_interval_figure(fit),
        width="stretch",
        config={"displaylogo": False},
        key=f"{key_prefix}_interval",
    )


tabs = st.tabs([
    "📘 Cómo usar",
    "🧠 Lógica de tablas",
    "⚙️ Ajuste ISO asistido",
    "📋 Intérprete de tabla",
    "🔍 Comparador de ajustes",
    "🏭 Fabricación",
    "✅ Control de calidad",
    "🔧 Montaje y operación",
    "🔬 Verificación metrológica",
])

# ---------------------------------------------------------------------
# Cómo usar
# ---------------------------------------------------------------------
with tabs[0]:
    c1, c2 = st.columns([1.05, .95], gap="large")

    with c1:
        st.subheader("Qué problema resuelve este módulo")
        st.write(
            "Las tablas de ajustes suelen usarse de forma mecánica: se busca un diámetro, una letra y un grado, "
            "pero muchas veces se pierde la relación entre la designación, la zona de tolerancia, los límites reales y la función del ajuste."
        )

        st.markdown("#### Ruta de trabajo")
        route = [
            ("1. Define la dimensión nominal", "La línea cero representa exactamente la dimensión nominal. Todas las desviaciones se miden respecto de esa referencia."),
            ("2. Identifica el sistema", "En sistema base agujero se mantiene H como referencia; en sistema base eje se mantiene h como referencia."),
            ("3. Lee letra y grado por separado", "La letra posiciona la zona de tolerancia respecto de la línea cero. El número IT define el ancho de esa zona."),
            ("4. Obtén las desviaciones límite", "Para agujeros se usan ES y EI; para ejes, es y ei. Con ellas se calculan las dimensiones máxima y mínima."),
            ("5. Calcula los límites reales", "La designación deja de ser abstracta cuando se transforma en dimensiones máximas y mínimas de fabricación."),
            ("6. Determina el tipo de ajuste", "Se comparan el agujero mínimo/máximo con el eje mínimo/máximo para obtener juego o interferencia extrema."),
            ("7. Conecta con fabricación", "Una tolerancia más estrecha exige un proceso más capaz, más control y normalmente mayor costo."),
            ("8. Evalúa capacidad y control", "No basta con lograr una pieza buena: el proceso debe demostrar estabilidad, centrado y capacidad para repetir la dimensión."),
            ("9. Revisa montaje y operación", "El juego o interferencia en taller puede cambiar por temperatura, carga, lubricación, contaminación, vibración y estrategia de montaje."),
            ("10. Conecta con medición", "Una dimensión solo puede verificarse correctamente si el sistema de medición tiene resolución e incertidumbre adecuadas."),
        ]
        for title, body in route:
            st.markdown(f"<div class='gg-step'><b>{title}</b><br>{body}</div>", unsafe_allow_html=True)

    with c2:
        latex_card(
            "Dimensiones del agujero",
            r"D_{\max}=D_N+\frac{ES}{1000},\qquad D_{\min}=D_N+\frac{EI}{1000}",
            "Las desviaciones ES y EI se expresan aquí en micrómetros."
        )
        latex_card(
            "Dimensiones del eje",
            r"d_{\max}=D_N+\frac{es}{1000},\qquad d_{\min}=D_N+\frac{ei}{1000}",
            "Las letras minúsculas corresponden al eje."
        )
        latex_card(
            "Juego mínimo",
            r"J_{\min}=D_{\min}-d_{\max}",
            "La condición más ajustada entre agujero y eje."
        )
        latex_card(
            "Juego máximo",
            r"J_{\max}=D_{\max}-d_{\min}",
            "La condición más holgada entre agujero y eje."
        )

        st.markdown(
            """
<div class="gg-note">
<b>Idea central:</b> la tabla no es el objetivo. La tabla es una forma compacta de entregar la posición y el ancho de las zonas de tolerancia. 
El objetivo real es comprender qué dimensiones se pueden fabricar, qué juego o interferencia resultará y cómo se verificará.
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
<div class="gg-note">
<b>Convención dimensional de MechLab:</b> las dimensiones lineales se muestran hasta la milésima de milímetro (0.001 mm), equivalente a una micra. Las desviaciones, juegos e interferencias se presentan en micras enteras. 
Los cálculos internos conservan mayor precisión, pero la interfaz evita mostrar falsa resolución submicrométrica.
</div>
""",
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------
# Lógica de tablas
# ---------------------------------------------------------------------
with tabs[1]:
    st.subheader("Cómo se construye la lógica detrás de la tabla")

    nominal_logic = st.number_input(
        "Dimensión nominal para explorar [mm]",
        min_value=3.1, max_value=500.0,
        value=50.0, step=1.0,
        key="logic_nominal"
    )

    step = get_size_step(nominal_logic)
    Dm = geometric_mean_step(step)
    i_um = tolerance_unit_i(Dm)

    st.markdown("### 1. Primero se identifica el intervalo nominal")
    st.latex(rf"{step[0]:.0f}<D_N\le {step[1]:.0f}\ \mathrm{{mm}}")
    st.write(
        "El cálculo no utiliza directamente el diámetro nominal para todas las relaciones. "
        "Primero se identifica el intervalo dimensional y se trabaja con su media geométrica."
    )

    st.latex(r"D_m=\sqrt{D_1D_2}")
    st.latex(rf"D_m=\sqrt{{{step[0]:.0f}\times {step[1]:.0f}}}={Dm:.3f}\,\mathrm{{mm}}")

    st.markdown("### 2. Unidad de tolerancia")
    st.latex(r"i=0.45\sqrt[3]{D_m}+0.001D_m")
    st.latex(rf"i={i_um:.4f}\,\mathrm{{\mu m}}")

    st.markdown("### 3. El grado IT define el ancho")
    grades = list(range(5, 17))
    it_values = {}
    for g in grades:
        value, *_ = it_width_um(nominal_logic, g)
        it_values[g] = value

    selected_grade_logic = st.select_slider(
        "Selecciona un grado para destacar",
        options=grades,
        value=7,
        key="logic_grade"
    )
    st.plotly_chart(
        make_it_grade_figure(nominal_logic, it_values, [selected_grade_logic]),
        width="stretch",
        config={"displaylogo": False},
        key="logic_it_chart",
    )

    st.latex(rf"IT{selected_grade_logic}={it_values[selected_grade_logic]:.0f}\,\mathrm{{\mu m}}")

    st.markdown("### 4. La letra define la posición")
    l1, l2 = st.columns(2)
    with l1:
        st.markdown("#### Agujero")
        st.write(
            "Las letras mayúsculas identifican posiciones de zona para agujeros. "
            "En el sistema base agujero, H tiene desviación inferior igual a cero."
        )
        st.latex(r"EI_H=0")
    with l2:
        st.markdown("#### Eje")
        st.write(
            "Las letras minúsculas identifican posiciones de zona para ejes. "
            "En el sistema base eje, h tiene desviación superior igual a cero."
        )
        st.latex(r"es_h=0")

    st.info(
        "Esta pestaña reproduce la lógica de cálculo y no una copia de las tablas normativas. "
        "Para documentación contractual o clases no incluidas en el modo automático, utiliza la tabla ISO 286-2 correspondiente y el Intérprete de tabla.",
        icon="📘"
    )

# ---------------------------------------------------------------------
# Auto fit
# ---------------------------------------------------------------------
with tabs[2]:
    st.subheader("Ajuste ISO asistido")

    mode = st.radio(
        "Sistema de referencia",
        ["Base agujero H", "Base eje h"],
        horizontal=True,
        key="auto_system"
    )

    nominal = st.number_input(
        "Dimensión nominal $D_N$ [mm]",
        min_value=3.1, max_value=500.0,
        value=50.0, step=1.0,
        key="auto_nominal"
    )

    if mode == "Base agujero H":
        a1, a2, a3 = st.columns(3)
        with a1:
            hole_grade = st.selectbox("Grado del agujero H", [6, 7, 8, 9, 10], index=1)
        with a2:
            shaft_letter = st.selectbox("Posición del eje", AUTO_HOLE_BASE_SHAFTS, index=AUTO_HOLE_BASE_SHAFTS.index("g"))
        with a3:
            shaft_grade = st.selectbox("Grado del eje", [5, 6, 7, 8], index=1)

        designation = f"H{hole_grade}/{shaft_letter}{shaft_grade}"
        st.markdown(f"### Designación analizada: `{designation}`")

        try:
            fit = automatic_hole_basis_fit(nominal, hole_grade, shaft_letter, shaft_grade)
        except Exception as exc:
            st.error(str(exc))
            fit = None

    else:
        a1, a2, a3 = st.columns(3)
        with a1:
            hole_letter = st.selectbox("Posición del agujero", AUTO_SHAFT_BASE_HOLES, index=AUTO_SHAFT_BASE_HOLES.index("G"))
        with a2:
            hole_grade = st.selectbox("Grado del agujero", [6, 7, 8, 9, 10], index=1, key="shaftbase_hole_grade")
        with a3:
            shaft_grade = st.selectbox("Grado del eje h", [5, 6, 7, 8], index=1, key="shaftbase_shaft_grade")

        designation = f"{hole_letter}{hole_grade}/h{shaft_grade}"
        st.markdown(f"### Designación analizada: `{designation}`")

        try:
            fit = automatic_shaft_basis_fit(nominal, hole_letter, hole_grade, shaft_grade)
        except Exception as exc:
            st.error(str(exc))
            fit = None

    if fit is not None:
        st.markdown("#### Paso 1 · Ancho de las zonas")
        z1, z2 = st.columns(2)
        with z1:
            st.latex(rf"T_H=ES-EI={fit.hole.tolerance_um:.0f}\,\mathrm{{\mu m}}")
            st.latex(rf"{fit.hole.method}")
        with z2:
            st.latex(rf"T_s=es-ei={fit.shaft.tolerance_um:.0f}\,\mathrm{{\mu m}}")
            st.latex(rf"{fit.shaft.method}")

        st.markdown("#### Paso 2 · Desviaciones")
        d1, d2 = st.columns(2)
        with d1:
            st.latex(rf"ES={fit.hole.upper_um:.0f}\,\mathrm{{\mu m}}")
            st.latex(rf"EI={fit.hole.lower_um:.0f}\,\mathrm{{\mu m}}")
        with d2:
            st.latex(rf"es={fit.shaft.upper_um:.0f}\,\mathrm{{\mu m}}")
            st.latex(rf"ei={fit.shaft.lower_um:.0f}\,\mathrm{{\mu m}}")

        st.markdown("#### Paso 3 · Límites y tipo de ajuste")
        render_fit_summary(fit, key_prefix="auto_fit")

        st.markdown("#### Cómo interpretar la clasificación")
        if "juego" in fit.fit_type.lower():
            st.write(
                "Aun en la combinación más ajustada, el agujero no queda menor que el eje. "
                "Existe juego positivo o, en el límite, contacto línea a línea."
            )
        elif "interferencia" in fit.fit_type.lower():
            st.write(
                "Aun en la combinación más holgada, el eje no queda menor que el agujero. "
                "El montaje requiere deformación elástica, presión, temperatura u otra estrategia de ensamblaje."
            )
        else:
            st.write(
                "Dependiendo de las dimensiones reales dentro de tolerancia, el conjunto puede quedar con pequeño juego o con interferencia. "
                "Por eso se denomina ajuste de transición."
            )

        st.warning(
            "El modo asistido implementa un subconjunto didáctico de posiciones frecuentes. "
            "Para clases no disponibles o para liberar documentación de fabricación, verifica las desviaciones con ISO 286-2 o la fuente normativa que utilice tu organización.",
            icon="⚠️"
        )

# ---------------------------------------------------------------------
# Manual table interpreter
# ---------------------------------------------------------------------
with tabs[3]:
    st.subheader("Intérprete de tabla · usa tus valores normativos")

    st.write(
        "Esta es la herramienta más directa para trabajar con una tabla ISO, un manual corporativo o una especificación de cliente. "
        "Tú ingresas las desviaciones que obtuviste de la fuente y MechLab hace el resto: límites, gráfico y clasificación del ajuste."
    )

    example_name = st.selectbox(
        "Ejemplo rápido o ingreso manual",
        list(MANUAL_EXAMPLES.keys()) + ["Personalizado"],
        key="manual_example"
    )

    if example_name == "Personalizado":
        ex = {
            "nominal": 50.0,
            "hole_symbol": "H",
            "hole_grade": 7,
            "EI": 0.0,
            "ES": 25.0,
            "shaft_symbol": "g",
            "shaft_grade": 6,
            "ei": -25.0,
            "es": -9.0,
            "note": "Ingresa los valores tomados desde tu tabla o especificación."
        }
    else:
        ex = MANUAL_EXAMPLES[example_name]
        st.info(ex["note"])

    nominal_m = st.number_input(
        "Dimensión nominal [mm]",
        min_value=0.001, value=float(ex["nominal"]), step=1.0,
        key=f"manual_nominal_{example_name}"
    )

    m1, m2 = st.columns(2, gap="large")
    with m1:
        st.markdown("### Agujero")
        hole_symbol = st.text_input("Símbolo de agujero", value=ex["hole_symbol"], max_chars=3, key=f"mhole_{example_name}")
        hole_grade_m = st.number_input("Grado IT del agujero", min_value=1, max_value=18, value=int(ex["hole_grade"]), step=1, key=f"mhg_{example_name}")
        EI = st.number_input("Desviación inferior $EI$ [µm]", value=float(ex["EI"]), step=1.0, key=f"mEI_{example_name}")
        ES = st.number_input("Desviación superior $ES$ [µm]", value=float(ex["ES"]), step=1.0, key=f"mES_{example_name}")

    with m2:
        st.markdown("### Eje")
        shaft_symbol = st.text_input("Símbolo de eje", value=ex["shaft_symbol"], max_chars=3, key=f"mshaft_{example_name}")
        shaft_grade_m = st.number_input("Grado IT del eje", min_value=1, max_value=18, value=int(ex["shaft_grade"]), step=1, key=f"msg_{example_name}")
        ei = st.number_input("Desviación inferior $ei$ [µm]", value=float(ex["ei"]), step=1.0, key=f"mei_{example_name}")
        es = st.number_input("Desviación superior $es$ [µm]", value=float(ex["es"]), step=1.0, key=f"mes_{example_name}")

    fit_manual = manual_fit(
        nominal_m,
        hole_symbol,
        int(hole_grade_m),
        EI,
        ES,
        shaft_symbol,
        int(shaft_grade_m),
        ei,
        es,
    )

    if not fit_manual.ok:
        st.error(fit_manual.message)
    else:
        render_fit_summary(fit_manual, key_prefix="manual_fit")

        st.markdown("#### La tabla se transforma en cuatro dimensiones reales")
        st.latex(
            rf"D_{{min}}={nominal_m:.3f}+\frac{{{EI:.0f}}}{{1000}}={fit_manual.hole_min_mm:.3f}\,\mathrm{{mm}}"
        )
        st.latex(
            rf"D_{{max}}={nominal_m:.3f}+\frac{{{ES:.0f}}}{{1000}}={fit_manual.hole_max_mm:.3f}\,\mathrm{{mm}}"
        )
        st.latex(
            rf"d_{{min}}={nominal_m:.3f}+\frac{{{ei:.0f}}}{{1000}}={fit_manual.shaft_min_mm:.3f}\,\mathrm{{mm}}"
        )
        st.latex(
            rf"d_{{max}}={nominal_m:.3f}+\frac{{{es:.0f}}}{{1000}}={fit_manual.shaft_max_mm:.3f}\,\mathrm{{mm}}"
        )

# ---------------------------------------------------------------------
# Comparator
# ---------------------------------------------------------------------
with tabs[4]:
    st.subheader("Comparador de ajustes")

    comp_nominal = st.number_input(
        "Dimensión nominal para comparar [mm]",
        min_value=3.1, max_value=500.0,
        value=50.0, step=1.0,
        key="compare_nominal"
    )

    desired_function = st.selectbox(
        "Función que quieres explorar",
        list(FUNCTION_STARTERS.keys()),
        key="compare_function"
    )

    starters = FUNCTION_STARTERS[desired_function]
    st.write(
        f"Familias de partida para explorar **{desired_function.lower()}**: "
        + ", ".join(f"`{x}`" for x in starters)
        + "."
    )
    st.caption(
        "No existe un ajuste universal para una función. Carga, temperatura, lubricación, material, longitud de contacto, montaje y proceso de fabricación también influyen."
    )

    available_designations = [row["designation"] for row in COMMON_FITS]
    selected_fits = st.multiselect(
        "Ajustes a comparar",
        available_designations,
        default=starters,
        key="compare_designations"
    )

    if selected_fits:
        rows = compare_designations(comp_nominal, selected_fits)
        # Add pedagogical intent text.
        intent_map = {row["designation"]: row for row in COMMON_FITS}
        for row in rows:
            if row["Ajuste"] in intent_map:
                row["Lectura funcional"] = intent_map[row["Ajuste"]]["intent"]
        st.dataframe(rows, width="stretch", hide_index=True)

    st.markdown("### Qué cambia cuando mueves la letra")
    st.write(
        "Si mantienes los grados IT y desplazas la letra del eje desde f → g → h → js → k → m → n, "
        "la zona se desplaza progresivamente hacia la línea cero y luego hacia la zona de interferencia."
    )

    st.markdown("### Qué cambia cuando mueves el número")
    st.write(
        "Si mantienes la letra y cambias el grado IT, cambias principalmente el ancho de la zona. "
        "Un número IT menor implica una banda más estrecha y una exigencia de fabricación mayor."
    )

# ---------------------------------------------------------------------
# Manufacturing
# ---------------------------------------------------------------------
with tabs[5]:
    st.subheader("Tolerancia y proceso de fabricación")

    fab_nominal = st.number_input(
        "Dimensión nominal de referencia [mm]",
        min_value=3.1, max_value=500.0,
        value=50.0, step=1.0,
        key="fab_nominal"
    )

    it_vals = {}
    for g in range(5, 17):
        val, *_ = it_width_um(fab_nominal, g)
        it_vals[g] = val

    fab_grade = st.select_slider(
        "Grado IT que quieres analizar",
        options=list(range(5, 17)),
        value=7,
        key="fab_grade"
    )

    st.plotly_chart(
        make_it_grade_figure(fab_nominal, it_vals, [fab_grade]),
        width="stretch",
        config={"displaylogo": False},
        key="fab_it_chart",
    )

    st.latex(rf"IT{fab_grade}={it_vals[fab_grade]:.0f}\,\mathrm{{\mu m}}")

    st.markdown("### La tolerancia tiene consecuencias productivas")
    st.plotly_chart(
        make_process_cost_figure(),
        width="stretch",
        config={"displaylogo": False},
        key="fab_process_chart",
    )
    st.caption(
        "La curva representa exigencia relativa de proceso, no costo monetario. "
        "Una banda más estrecha suele exigir más capacidad de máquina, control, estabilidad y verificación."
    )

    st.markdown("### Orientación de procesos")
    st.dataframe(PROCESS_GUIDANCE, width="stretch", hide_index=True)

    st.markdown("### Ruta de fabricación orientativa")

    feature_type = st.radio(
        "Tipo de característica",
        ["Agujero", "Eje"],
        horizontal=True,
        key="fab_feature_type"
    )
    fab_material = st.selectbox(
        "Material / familia",
        [
            "Acero",
            "Acero inoxidable",
            "Hierro fundido",
            "Aluminio",
            "Otro / revisar proceso",
        ],
        key="fab_material"
    )
    fab_criticality = st.selectbox(
        "Criticidad funcional",
        ["Normal", "Alta"],
        key="fab_criticality"
    )

    if feature_type == "Agujero":
        if fab_grade <= 6:
            route_rows = [
                {"Etapa": "1", "Operación": "Generación previa", "Objetivo": "Crear agujero con material suficiente para terminación."},
                {"Etapa": "2", "Operación": "Mandrinado / semiacabado", "Objetivo": "Corregir posición y aproximar dimensión."},
                {"Etapa": "3", "Operación": "Escariado, mandrinado fino, rectificado o bruñido", "Objetivo": "Conseguir dimensión y calidad final."},
                {"Etapa": "4", "Operación": "Desbarbado + limpieza", "Objetivo": "Eliminar material que afecte montaje o medición."},
                {"Etapa": "5", "Operación": "Estabilización térmica + inspección", "Objetivo": "Verificar dimensión bajo condición metrológica definida."},
            ]
        else:
            route_rows = [
                {"Etapa": "1", "Operación": "Taladrado / generación", "Objetivo": "Crear geometría inicial."},
                {"Etapa": "2", "Operación": "Mandrinado / escariado / acabado según IT", "Objetivo": "Llevar la dimensión dentro de tolerancia."},
                {"Etapa": "3", "Operación": "Desbarbado + limpieza", "Objetivo": "Preparar superficie para inspección y montaje."},
                {"Etapa": "4", "Operación": "Inspección", "Objetivo": "Confirmar límites dimensionales y condición superficial relevante."},
            ]
    else:
        if fab_grade <= 6:
            route_rows = [
                {"Etapa": "1", "Operación": "Torneado de desbaste", "Objetivo": "Generar geometría dejando sobrematerial."},
                {"Etapa": "2", "Operación": "Torneado de semiacabado", "Objetivo": "Controlar geometría y aproximar dimensión."},
                {"Etapa": "3", "Operación": "Rectificado / superacabado según necesidad", "Objetivo": "Conseguir dimensión y calidad final."},
                {"Etapa": "4", "Operación": "Limpieza + estabilización", "Objetivo": "Preparar la pieza para medición final."},
                {"Etapa": "5", "Operación": "Micrometría / comparación / CMM según requisito", "Objetivo": "Verificar la característica funcional."},
            ]
        else:
            route_rows = [
                {"Etapa": "1", "Operación": "Torneado", "Objetivo": "Generar y terminar el diámetro."},
                {"Etapa": "2", "Operación": "Acabado local si aplica", "Objetivo": "Corregir dimensión y superficie."},
                {"Etapa": "3", "Operación": "Limpieza", "Objetivo": "Eliminar residuos que afecten la medición."},
                {"Etapa": "4", "Operación": "Inspección", "Objetivo": "Confirmar dimensión final."},
            ]

    st.dataframe(route_rows, width="stretch", hide_index=True)

    if fab_criticality == "Alta":
        st.info(
            "Para una característica de alta criticidad conviene definir un punto de control antes de una operación irreversible, "
            "registrar identificación de equipo y pieza, y asegurar trazabilidad de la medición.",
            icon="✅"
        )

    st.markdown("### Variables que pueden sacar una dimensión de tolerancia")
    st.markdown(
        """
- desgaste o compensación de herramienta;
- temperatura de pieza, máquina y ambiente;
- flexión o sujeción durante mecanizado;
- rebaba y contaminación antes de medir;
- ovalidad, conicidad o forma no capturada por una sola lectura;
- deformación después de liberar la pieza;
- estrategia de medición distinta entre producción y control final;
- cambios de lote de material o tratamiento.
"""
    )

    st.markdown(
        """
<div class="gg-warning">
<b>No uses esta tabla como capacidad contractual de proceso.</b> La capacidad real depende de máquina, herramienta, material, longitud, geometría, temperatura, operador, estrategia y estabilidad estadística. 
Para liberar fabricación, utiliza datos del proceso real o del proveedor.
</div>
""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------
# Quality control
# ---------------------------------------------------------------------
with tabs[6]:
    st.subheader("Control de calidad · capacidad del proceso y plan de inspección")

    st.write(
        "El control de calidad debe responder dos preguntas distintas: "
        "¿la pieza medida cumple hoy? y ¿el proceso es capaz de repetir esa característica de forma consistente?"
    )

    q1, q2 = st.columns([.9, 1.1], gap="large")

    with q1:
        st.markdown("### Característica a controlar")
        qc_nominal = st.number_input(
            "Dimensión nominal [mm]",
            min_value=3.1, max_value=500.0,
            value=50.0, step=1.0,
            key="qc_nominal"
        )
        qc_feature = st.selectbox(
            "Característica",
            ["Agujero H7", "Eje g6", "Límites personalizados"],
            key="qc_feature"
        )

        if qc_feature == "Agujero H7":
            qc_fit = automatic_hole_basis_fit(qc_nominal, 7, "g", 6)
            lsl = qc_fit.hole_min_mm
            usl = qc_fit.hole_max_mm
            feature_label = f"Ø{qc_nominal:.2f} H7"
        elif qc_feature == "Eje g6":
            qc_fit = automatic_hole_basis_fit(qc_nominal, 7, "g", 6)
            lsl = qc_fit.shaft_min_mm
            usl = qc_fit.shaft_max_mm
            feature_label = f"Ø{qc_nominal:.2f} g6"
        else:
            lsl = st.number_input(
                "Límite inferior LSL [mm]",
                value=49.975,
                step=0.001,
                format="%.3f",
                key="qc_lsl"
            )
            usl = st.number_input(
                "Límite superior USL [mm]",
                value=49.991,
                step=0.001,
                format="%.3f",
                key="qc_usl"
            )
            feature_label = "Característica personalizada"

        midpoint = 0.5*(lsl+usl)
        tol_width = usl-lsl
        mean_default = midpoint
        sigma_default = max(tol_width/8.0, 0.0001)

        mean_mm = st.number_input(
            "Media del proceso μ [mm]",
            value=float(mean_default),
            step=0.001,
            format="%.3f",
            key=f"qc_mean_{qc_feature}"
        )
        sigma_mm = st.number_input(
            "Desviación estándar σ [mm]",
            min_value=0.000001,
            value=float(sigma_default),
            step=0.001,
            format="%.3f",
            key=f"qc_sigma_{qc_feature}"
        )

        cap = process_capability(lsl, usl, mean_mm, sigma_mm)

        st.latex(r"C_p=\frac{USL-LSL}{6\sigma}")
        st.latex(
            r"C_{pk}=\min\left("
            r"\frac{USL-\mu}{3\sigma},"
            r"\frac{\mu-LSL}{3\sigma}"
            r"\right)"
        )

        cpa, cpb = st.columns(2)
        cpa.metric("Cp", "—" if cap.cp is None else f"{cap.cp:.3f}")
        cpb.metric("Cpk", "—" if cap.cpk is None else f"{cap.cpk:.3f}")

        st.caption(
            "Cp compara dispersión con tolerancia; Cpk incorpora además el descentramiento. "
            "Los valores objetivo deben definirse por cliente, organización y criticidad; MechLab no impone un umbral universal."
        )

    with q2:
        xs, ys = normal_curve_points(mean_mm, sigma_mm, lsl, usl)
        st.plotly_chart(
            make_capability_figure(xs, ys, lsl, usl, mean_mm),
            width="stretch",
            config={"displaylogo": False},
            key="qc_capability_chart",
        )

        qcm1, qcm2, qcm3 = st.columns(3)
        qcm1.metric("Tolerancia total", f"{cap.tolerance_um:.0f} µm")
        qcm2.metric("6σ del proceso", f"{cap.six_sigma_um:.0f} µm")
        qcm3.metric("Descentrado de media", f"{cap.centered_offset_um:.0f} µm")

    st.markdown("### Qué revisar antes de usar Cp/Cpk")
    st.markdown(
        """
- confirmar que el proceso sea suficientemente estable para interpretar capacidad;
- separar variación del proceso de errores del sistema de medición;
- utilizar datos representativos del mismo proceso, máquina, material y condición;
- revisar tendencias, cambios de herramienta, temperatura y correcciones del operador;
- no usar Cp/Cpk como sustituto de un plan de control ni de la ingeniería del proceso.
"""
    )

    st.markdown("### Plan de control orientativo")
    qc_criticality = st.selectbox(
        "Criticidad de la característica",
        ["Normal", "Alta"],
        key="qc_criticality"
    )
    qc_stage = st.selectbox(
        "Alcance del control",
        ["Fabricación", "Fabricación + montaje"],
        key="qc_stage"
    )

    qc_plan = suggested_quality_plan(
        feature_label,
        qc_criticality,
        qc_stage,
    )
    st.dataframe(qc_plan, width="stretch", hide_index=True)

    st.markdown(
        """
<div class="gg-note">
<b>Gestión de medición:</b> para uso industrial conviene controlar identificación del equipo, estado de calibración, método, ambiente, registros y competencia del personal. 
La gestión de procesos de medición forma parte del enfoque de ISO 10012:2026, mientras que las decisiones de conformidad cerca de los límites deben considerar incertidumbre y regla de decisión.
</div>
""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------
# Mounting and operation
# ---------------------------------------------------------------------
with tabs[7]:
    st.subheader("Montaje y condición operacional")

    st.write(
        "El ajuste calculado a temperatura de referencia no siempre es el ajuste que existirá durante el montaje o la operación. "
        "Temperatura, materiales, lubricación, vibración y posibilidad de desmontaje pueden cambiar el criterio de selección."
    )

    st.markdown("### 1. Define la condición dimensional de partida")

    mount_example = st.selectbox(
        "Ejemplo de ajuste",
        list(MANUAL_EXAMPLES.keys()) + ["Personalizado"],
        index=2,
        key="mount_example"
    )

    if mount_example == "Personalizado":
        mount_nominal = st.number_input("Nominal [mm]", value=50.0, step=1.0, key="mount_nominal_custom")
        mEI = st.number_input("EI [µm]", value=0.0, step=1.0, key="mount_EI")
        mES = st.number_input("ES [µm]", value=25.0, step=1.0, key="mount_ES")
        mei = st.number_input("ei [µm]", value=26.0, step=1.0, key="mount_ei")
        mes = st.number_input("es [µm]", value=42.0, step=1.0, key="mount_es")
        mount_fit = manual_fit(mount_nominal, "H", 7, mEI, mES, "eje", 6, mei, mes)
    else:
        mex = MANUAL_EXAMPLES[mount_example]
        mount_nominal = float(mex["nominal"])
        mount_fit = manual_fit(
            mount_nominal,
            mex["hole_symbol"],
            int(mex["hole_grade"]),
            float(mex["EI"]),
            float(mex["ES"]),
            mex["shaft_symbol"],
            int(mex["shaft_grade"]),
            float(mex["ei"]),
            float(mex["es"]),
        )
        st.info(mex["note"])

    condition = st.selectbox(
        "Condición dimensional para evaluar",
        ["Más ajustada", "Media", "Más holgada"],
        key="mount_condition"
    )

    if condition == "Más ajustada":
        hole_ref = mount_fit.hole_min_mm
        shaft_ref = mount_fit.shaft_max_mm
    elif condition == "Más holgada":
        hole_ref = mount_fit.hole_max_mm
        shaft_ref = mount_fit.shaft_min_mm
    else:
        hole_ref = 0.5*(mount_fit.hole_min_mm + mount_fit.hole_max_mm)
        shaft_ref = 0.5*(mount_fit.shaft_min_mm + mount_fit.shaft_max_mm)

    mcol1, mcol2 = st.columns(2, gap="large")

    with mcol1:
        st.markdown("### 2. Materiales y temperaturas")
        hole_material = st.selectbox("Material del agujero/alojamiento", list(MATERIALS.keys()), key="mount_hole_mat")
        shaft_material = st.selectbox("Material del eje", list(MATERIALS.keys()), key="mount_shaft_mat")

        if MATERIALS[hole_material]["alpha"] is None:
            alpha_h = st.number_input(
                "Coef. expansión agujero αₕ [1/°C]",
                min_value=1e-7, value=12e-6, format="%.8f",
                key="mount_alpha_h"
            )
        else:
            alpha_h = MATERIALS[hole_material]["alpha"]
            st.latex(rf"\alpha_h={alpha_h:.2e}\,\mathrm{{^\circ C^{{-1}}}}")

        if MATERIALS[shaft_material]["alpha"] is None:
            alpha_s = st.number_input(
                "Coef. expansión eje αₛ [1/°C]",
                min_value=1e-7, value=12e-6, format="%.8f",
                key="mount_alpha_s"
            )
        else:
            alpha_s = MATERIALS[shaft_material]["alpha"]
            st.latex(rf"\alpha_s={alpha_s:.2e}\,\mathrm{{^\circ C^{{-1}}}}")

        temp_ref = st.number_input(
            "Temperatura de referencia [°C]",
            value=20.0, step=1.0,
            key="mount_temp_ref"
        )
        temp_h = st.number_input(
            "Temperatura del alojamiento en operación [°C]",
            value=60.0, step=5.0,
            key="mount_temp_h"
        )
        temp_s = st.number_input(
            "Temperatura del eje en operación [°C]",
            value=80.0, step=5.0,
            key="mount_temp_s"
        )

    with mcol2:
        thermal = thermal_fit(
            hole_ref,
            shaft_ref,
            alpha_h,
            alpha_s,
            temp_ref,
            temp_h,
            temp_s,
        )

        st.markdown("### 3. Ajuste a temperatura de operación")
        st.latex(r"D(T)=D_0\left[1+\alpha\left(T-T_0\right)\right]")
        st.latex(r"d(T)=d_0\left[1+\alpha\left(T-T_0\right)\right]")
        st.latex(r"J(T)=D(T)-d(T)")

        tm1, tm2, tm3 = st.columns(3)
        tm1.metric("Juego en referencia", f"{thermal.clearance_ref_um:.0f} µm")
        tm2.metric("Juego en operación", f"{thermal.clearance_op_um:.0f} µm")
        tm3.metric("Cambio térmico", f"{thermal.delta_clearance_um:+.0f} µm")

        st.plotly_chart(
            make_thermal_clearance_figure(
                thermal.clearance_ref_um,
                thermal.clearance_op_um,
            ),
            width="stretch",
            config={"displaylogo": False},
            key="mount_thermal_chart",
        )

    st.caption(
        "ISO 1 establece 20 °C como temperatura normal de referencia para propiedades geométricas y dimensionales, salvo especificación explícita diferente. "
        "El cálculo térmico mostrado es lineal y utiliza coeficientes de referencia; para grandes gradientes o materiales sensibles, utiliza datos de material específicos."
    )

    st.markdown("### 4. Condición de montaje")
    guidance = mounting_guidance(
        mount_fit.fit_type,
        mount_fit.clearance_min_um,
        mount_fit.clearance_max_um,
    )
    for note in guidance:
        st.markdown(f"- {note}")

    if thermal.clearance_ref_um < 0:
        st.markdown("#### Estimación térmica para facilitar montaje")
        target_clearance = st.number_input(
            "Juego temporal deseado para montaje [µm]",
            min_value=0.0,
            value=20.0,
            step=5.0,
            key="mount_target_clearance"
        )
        method = st.radio(
            "Estrategia térmica simplificada",
            ["Calentar agujero", "Enfriar eje"],
            horizontal=True,
            key="mount_thermal_method"
        )
        alpha_used = alpha_h if method == "Calentar agujero" else alpha_s

        dT_req = temperature_change_for_target_clearance(
            mount_nominal,
            thermal.clearance_ref_um,
            target_clearance,
            alpha_used,
            method,
        )
        if dT_req is not None:
            st.latex(
                r"\Delta T\approx"
                r"\frac{J_{objetivo}-J_{actual}}{\alpha D_N}"
            )
            st.latex(rf"\Delta T\approx {dT_req:.1f}\,^\circ\mathrm{{C}}")
            st.warning(
                "Esta es una estimación geométrica de expansión/contracción, no una temperatura de montaje autorizada. "
                "Antes de aplicarla deben revisarse límites del material, tratamientos térmicos, lubricantes, sellos, seguridad y procedimiento de montaje.",
                icon="⚠️"
            )

    st.markdown("### 5. Condiciones operacionales que deben acompañar la selección")
    oc1, oc2 = st.columns(2)
    with oc1:
        rotating = st.checkbox("Existe rotación", value=True, key="op_rotating")
        sliding = st.checkbox("Existe deslizamiento relativo", value=False, key="op_sliding")
        shock = st.checkbox("Choque o vibración significativa", value=False, key="op_shock")
        disassembly = st.checkbox("Desmontaje frecuente", value=False, key="op_disassembly")
    with oc2:
        lubrication = st.checkbox("Lubricación funcional requerida", value=True, key="op_lubrication")
        contamination = st.checkbox("Ambiente contaminado / partículas", value=False, key="op_contamination")
        thermal_gradient = st.checkbox("Gradiente térmico relevante", value=True, key="op_thermal")
        thin_wall = st.checkbox("Alojamiento o cubo de pared delgada", value=False, key="op_thinwall")

    checks = operational_checks(
        rotating,
        sliding,
        shock,
        disassembly,
        lubrication,
        contamination,
        thermal_gradient,
        thin_wall,
    )
    for item in checks:
        st.markdown(f"- {item}")

    st.markdown(
        """
<div class="gg-warning">
<b>Uso ingenieril:</b> la selección final del ajuste debe considerar carga, material, geometría, longitud de contacto, temperatura, velocidad, lubricación, montaje, desmontaje y deformación. 
Para un ajuste por interferencia sometido a carga, el siguiente nivel es verificar presión de contacto, tensiones y fuerza de montaje mediante elasticidad o un modelo específico del conjunto.
</div>
""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------
with tabs[8]:
    st.subheader("Verificación dimensional")

    st.write(
        "Después de diseñar y fabricar viene la pregunta metrológica: ¿cómo verifico que la pieza está dentro de los límites?"
    )

    v1, v2 = st.columns([.95, 1.05], gap="large")
    with v1:
        ver_nominal = st.number_input(
            "Dimensión nominal [mm]",
            min_value=3.1, max_value=500.0,
            value=50.0, step=1.0,
            key="verify_nominal"
        )
        ver_h_grade = st.selectbox("Agujero H · grado", [6, 7, 8, 9], index=1)
        ver_s_letter = st.selectbox("Eje · posición", AUTO_HOLE_BASE_SHAFTS, index=AUTO_HOLE_BASE_SHAFTS.index("g"))
        ver_s_grade = st.selectbox("Eje · grado", [5, 6, 7, 8], index=1)

        try:
            fit_v = automatic_hole_basis_fit(ver_nominal, ver_h_grade, ver_s_letter, ver_s_grade)
        except Exception as exc:
            st.error(str(exc))
            fit_v = None

    with v2:
        if fit_v is not None:
            measured_hole = st.number_input(
                "Medición del agujero [mm]",
                value=(fit_v.hole_min_mm + fit_v.hole_max_mm)/2,
                step=0.001,
                format="%.3f",
            )
            measured_shaft = st.number_input(
                "Medición del eje [mm]",
                value=(fit_v.shaft_min_mm + fit_v.shaft_max_mm)/2,
                step=0.001,
                format="%.3f",
            )

            hole_status = measured_status(measured_hole, fit_v.hole_min_mm, fit_v.hole_max_mm)
            shaft_status = measured_status(measured_shaft, fit_v.shaft_min_mm, fit_v.shaft_max_mm)

            st.metric("Estado del agujero", hole_status)
            st.metric("Estado del eje", shaft_status)

    if fit_v is not None:
        st.plotly_chart(
            make_measurement_position_figure(
                measured_hole, fit_v.hole_min_mm, fit_v.hole_max_mm, "Medición agujero"
            ),
            width="stretch",
            config={"displaylogo": False},
            key="verify_hole_chart",
        )
        st.plotly_chart(
            make_measurement_position_figure(
                measured_shaft, fit_v.shaft_min_mm, fit_v.shaft_max_mm, "Medición eje"
            ),
            width="stretch",
            config={"displaylogo": False},
            key="verify_shaft_chart",
        )

        actual_clearance_um = (measured_hole - measured_shaft) * 1000.0
        st.latex(
            rf"J_{{medido}}=D_{{medido}}-d_{{medido}}={actual_clearance_um:.0f}\,\mathrm{{\mu m}}"
        )

        controlling_tol = min(fit_v.hole.tolerance_um, fit_v.shaft.tolerance_um)
        target_resolution_um = controlling_tol / 10.0

        st.markdown("### Orientación para elegir instrumento")
        st.latex(
            rf"T_{{más\ estrecha}}={controlling_tol:.0f}\,\mathrm{{\mu m}}"
        )
        st.latex(
            rf"r_{{orientativa}}\le\frac{{T}}{{10}}\approx {target_resolution_um:.0f}\,\mathrm{{\mu m}}"
        )
        st.caption(
            "La relación 10:1 se usa aquí solo como orientación pedagógica de resolución. "
            "La aceptación formal exige considerar incertidumbre, calibración, ambiente y regla de decisión."
        )

        recommendation = None
        for row in MEASUREMENT_GUIDANCE:
            if controlling_tol >= row["tol_um_min"]:
                recommendation = row
                break

        if recommendation:
            st.markdown(f"**Instrumentación que conviene evaluar:** {recommendation['instrument']}")
            st.write(recommendation["note"])

        st.markdown("### Qué falta para declarar conformidad metrológica")
        st.write(
            "Que una lectura quede dentro de los límites dimensionales es solo una primera evaluación. "
            "Una decisión formal de conformidad debe considerar la incertidumbre del proceso de medición, trazabilidad, temperatura, estrategia de palpado y regla de decisión."
        )

        st.markdown("#### Referencia térmica y decisión")
        st.latex(r"T_{ref}=20\,^\circ\mathrm{C}")
        st.write(
            "Para especificación y verificación dimensional, la temperatura normal de referencia es 20 °C salvo que se especifique otra. "
            "Si la pieza se mide lejos de esa condición, debe evaluarse el efecto térmico o la compensación utilizada."
        )
        st.write(
            "Cuando el resultado queda próximo a un límite, la aceptación no debería basarse solo en comparar el valor indicado con LSL/USL. "
            "La incertidumbre y la regla de decisión deben formar parte del criterio de conformidad."
        )

st.divider()
st.caption(
    "GG DIMEC · MechLab · Metrología y Fabricación · Herramienta pedagógica para ajustes y tolerancias."
)
