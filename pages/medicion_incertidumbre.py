from __future__ import annotations

import math
import pandas as pd
import streamlit as st

from modules.ui_brand import render_app_header
from modules.measurement_data import PRESETS, MATERIALS, CONCEPTS, QUALITY_CHECKLIST, INSTRUMENT_GUIDANCE
from modules.uncertainty_engine import (
    parse_readings,
    repeatability,
    build_uncertainty_budget,
    uncertainty_percentages,
    decision_interval_rule,
    decision_guard_band,
    tolerance_uncertainty_ratio,
    max_uncertainty_for_target_ratio,
    resolution_ratio,
    combine_with_custom_items,
    geometry_error_model,
    result_summary_text,
)
from modules.uncertainty_plotter import (
    make_measurement_chain_figure,
    make_repeatability_figure,
    make_uncertainty_budget_figure,
    make_conformity_figure,
    make_temperature_correction_figure,
    make_instrument_suitability_figure,
    make_shaft_measurement_schematic,
    make_hole_measurement_schematic,
    make_temperature_model_schematic,
    make_cosine_error_schematic,
    make_abbe_error_schematic,
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
.gg-concept{
  border:1px solid var(--gg-line);
  border-radius:12px;
  padding:.8rem .9rem;
  background:#fff;
  min-height:155px;
}
div[data-testid="stMetric"]{
  border:1px solid var(--gg-line);
  border-radius:12px;
  padding:.55rem .7rem;
  background:#fff;
}
.gg-kpi-card{
  border:1px solid var(--gg-line);
  border-radius:12px;
  background:#fff;
  padding:.9rem 1rem;
  min-height:132px;
  display:flex;
  flex-direction:column;
  justify-content:space-between;
}
.gg-kpi-title{
  font-size:.95rem;
  font-weight:700;
  color:#444;
  margin-bottom:.35rem;
}
.gg-kpi-value{
  font-size:clamp(1.45rem, 2.3vw, 2.55rem);
  font-weight:800;
  line-height:1.08;
  color:#1f2430;
  white-space:normal;
  word-break:break-word;
  overflow-wrap:anywhere;
}
.gg-kpi-sub{
  font-size:.84rem;
  color:#737986;
  margin-top:.35rem;
}
.gg-budget-head{
  font-size:.82rem;
  font-weight:800;
  color:#5f6672;
  text-transform:none;
}
.gg-budget-row{
  padding:.28rem 0 .12rem 0;
  border-bottom:1px solid #f0f2f5;
}
.gg-flow-card{
  border:1px solid var(--gg-line);
  border-radius:14px;
  background:#fff;
  padding:1rem 1rem .8rem 1rem;
  min-height:170px;
}
.gg-flow-arrow{
  text-align:center;
  font-size:2rem;
  color:var(--gg-orange);
  font-weight:800;
  margin-top:3.2rem;
}
</style>
""",
    unsafe_allow_html=True,
)

render_app_header(
    title="Medición e Incertidumbre · ¿La pieza cumple?",
    subtitle="Modelo de medición · repetibilidad · calibración · temperatura · incertidumbre · decisión de conformidad · plan de control.",
    section="METROLOGÍA Y FABRICACIÓN",
    logo_width=188,
)


def latex_card(title: str, formula: str, caption: str):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.latex(formula)
        st.caption(caption)


def fmt_um(value: float) -> str:
    return f"{value:.0f} µm"


MODEL_LATEX = {
    "Repetibilidad del promedio": r"u_A=\frac{s}{\sqrt{n}}",
    "Resolución": r"u_r=\frac{r}{2\sqrt{3}}",
    "Calibración": r"u_{cal}=\frac{U_{cal}}{k_{cal}}",
    "Temperatura": r"u_T\approx\left|\alpha D\right|u(T)",
    "Método / alineación / contacto": r"u_m=\text{contribución estándar del método}",
    "Operador / lectura": r"u_o=\text{contribución estándar ingresada}",
    "Geometría / Abbe residual": r"u_g=\text{efecto geométrico residual}",
    "Deformación por fuerza de medición": r"u_F=\text{efecto de contacto o deformación}",
    "Fuente adicional": r"u_{add}=\text{fuente personalizada}",
}


def render_kpi_card(title: str, value: str, subtitle: str = ""):
    st.markdown(
        f"""
<div class="gg-kpi-card">
  <div class="gg-kpi-title">{title}</div>
  <div class="gg-kpi-value">{value}</div>
  {f'<div class=\"gg-kpi-sub\">{subtitle}</div>' if subtitle else ''}
</div>
""",
        unsafe_allow_html=True,
    )


def render_budget_table_latex(budget_rows):
    st.markdown("### Desglose del presupuesto")
    cols = st.columns([2.2, 0.9, 1.6, 1.4, 1.1, 2.0], gap="small")
    headers = ["Fuente", "Tipo", "Incertidumbre estándar [µm]", "Contribución [µm]", "Varianza [%]", "Modelo"]
    for c, h in zip(cols, headers):
        c.markdown(f'<div class="gg-budget-head">{h}</div>', unsafe_allow_html=True)
    st.markdown('<div class="gg-budget-row"></div>', unsafe_allow_html=True)

    for idx, row in enumerate(budget_rows):
        cols = st.columns([2.2, 0.9, 1.6, 1.4, 1.1, 2.0], gap="small")
        cols[0].markdown(f"<div class='gg-budget-row'><b>{row['Fuente']}</b></div>", unsafe_allow_html=True)
        cols[1].markdown(f"<div class='gg-budget-row'>{row['Tipo']}</div>", unsafe_allow_html=True)
        cols[2].markdown(f"<div class='gg-budget-row'>{row['Incertidumbre estándar [µm]']:.0f}</div>", unsafe_allow_html=True)
        cols[3].markdown(f"<div class='gg-budget-row'>{row['Contribución [µm]']:.0f}</div>", unsafe_allow_html=True)
        cols[4].markdown(f"<div class='gg-budget-row'>{row['Varianza [%]']:.1f}</div>", unsafe_allow_html=True)
        with cols[5]:
            st.latex(MODEL_LATEX.get(row['Fuente'], r"u=\text{modelo no especificado}"))


def render_temperature_model_cards():
    c1, c2, c3, c4, c5 = st.columns([1.2, 0.18, 1.0, 0.18, 1.2], gap="small")
    with c1:
        st.markdown('<div class="gg-flow-card"><div style="font-size:.82rem;font-weight:800;color:#f28e1c;letter-spacing:.04em">ENTRADA</div><div style="margin-top:.3rem"></div></div>', unsafe_allow_html=True)
        st.latex(r"L_T")
        st.caption("Dimensión indicada a la temperatura real de la pieza o del sistema de medición, $T$.")
    with c2:
        st.markdown('<div class="gg-flow-arrow">→</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="gg-flow-card"><div style="font-size:.82rem;font-weight:800;color:#f28e1c;letter-spacing:.04em">CORRECCIÓN</div><div style="margin-top:.3rem"></div></div>', unsafe_allow_html=True)
        st.latex(r"C_T")
        st.caption(r"Corrección aplicada para referir el resultado a la temperatura patrón de $20\,^{\circ}\mathrm{C}$.")
    with c4:
        st.markdown('<div class="gg-flow-arrow">→</div>', unsafe_allow_html=True)
    with c5:
        st.markdown('<div class="gg-flow-card"><div style="font-size:.82rem;font-weight:800;color:#f28e1c;letter-spacing:.04em">SALIDA</div><div style="margin-top:.3rem"></div></div>', unsafe_allow_html=True)
        st.latex(r"L_{20}")
        st.caption(r"Resultado corregido y expresado a la referencia de $20\,^{\circ}\mathrm{C}$.")


# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("Caso de medición")
    preset_name = st.selectbox("Configuración", list(PRESETS.keys()))
    preset = PRESETS[preset_name]

    st.divider()
    st.header("Especificación")
    nominal_mm = st.number_input(
        "Dimensión nominal [mm]",
        value=float(preset["nominal_mm"]),
        step=0.001,
        format="%.3f",
        key=f"unc_nominal_{preset_name}",
    )
    lsl_mm = st.number_input(
        "Límite inferior LSL [mm]",
        value=float(preset["lsl_mm"]),
        step=0.001,
        format="%.3f",
        key=f"unc_lsl_{preset_name}",
    )
    usl_mm = st.number_input(
        "Límite superior USL [mm]",
        value=float(preset["usl_mm"]),
        step=0.001,
        format="%.3f",
        key=f"unc_usl_{preset_name}",
    )

    st.divider()
    st.header("Lecturas")
    readings_default = "; ".join(f"{v:.3f}" for v in preset["readings_mm"])
    readings_text = st.text_area(
        "Lecturas [mm]",
        value=readings_default,
        help="Separa lecturas con punto y coma. Puedes usar coma decimal, por ejemplo: 49,984; 49,985.",
        key=f"unc_readings_{preset_name}",
    )
    resolution_mm = st.number_input(
        "Resolución del instrumento [mm]",
        min_value=0.000001,
        value=float(preset["resolution_mm"]),
        step=0.001,
        format="%.3f",
        key=f"unc_res_{preset_name}",
    )

    st.divider()
    st.header("Calibración")
    cal_correction_um = st.number_input(
        "Corrección a aplicar [µm]",
        value=float(preset["cal_correction_um"]),
        step=1.0,
        format="%.0f",
        key=f"unc_cal_corr_{preset_name}",
    )
    cal_U_um = st.number_input(
        "Incertidumbre expandida del certificado [µm]",
        min_value=0.0,
        value=float(preset["cal_U_um"]),
        step=1.0,
        format="%.0f",
        key=f"unc_cal_U_{preset_name}",
    )
    cal_k = st.number_input(
        "Factor de cobertura del certificado",
        min_value=0.1,
        value=float(preset["cal_k"]),
        step=0.1,
        format="%.1f",
        key=f"unc_cal_k_{preset_name}",
    )
    st.latex(rf"U_{{cal}}={cal_U_um:.0f}\,\mathrm{{\mu m}},\qquad k_{{cal}}={cal_k:.1f}")

    st.divider()
    st.header("Temperatura")
    material_name = st.selectbox(
        "Material de la pieza",
        list(MATERIALS.keys()),
        index=0,
        key=f"unc_material_{preset_name}",
    )
    if MATERIALS[material_name] is None:
        alpha = st.number_input(
            "Coeficiente α [1/°C]",
            min_value=1e-7,
            value=float(preset["alpha_per_C"]),
            format="%.8f",
            key=f"unc_alpha_{preset_name}",
        )
    else:
        alpha = float(MATERIALS[material_name])
        st.latex(rf"\alpha={alpha:.2e}\,\mathrm{{^\circ C^{{-1}}}}")

    temp_C = st.number_input(
        "Temperatura de la pieza [°C]",
        value=float(preset["temp_C"]),
        step=0.5,
        key=f"unc_temp_{preset_name}",
    )
    temp_u_C = st.number_input(
        "Incertidumbre estándar de temperatura [°C]",
        min_value=0.0,
        value=float(preset["temp_u_C"]),
        step=0.1,
        key=f"unc_temp_u_{preset_name}",
    )
    st.latex(rf"u(T)={temp_u_C:.1f}\,^\circ\mathrm{{C}}")

    st.divider()
    st.header("Otras contribuciones")
    method_u_um = st.number_input(
        "Método / alineación / contacto · incertidumbre estándar [µm]",
        min_value=0.0,
        value=float(preset["method_u_um"]),
        step=1.0,
        format="%.0f",
        key=f"unc_method_{preset_name}",
    )
    operator_u_um = st.number_input(
        "Operador / lectura · incertidumbre estándar [µm]",
        min_value=0.0,
        value=float(preset["operator_u_um"]),
        step=1.0,
        format="%.0f",
        key=f"unc_operator_{preset_name}",
    )

    coverage_k = st.slider(
        "Factor de cobertura final",
        min_value=1.0, max_value=3.0,
        value=2.0, step=0.1,
        key=f"unc_final_k_{preset_name}",
    )
    st.latex(rf"k={coverage_k:.1f}")

try:
    readings = parse_readings(readings_text)
except Exception as exc:
    st.error(f"No fue posible leer las mediciones: {exc}")
    st.stop()

if usl_mm <= lsl_mm:
    st.error("El límite superior USL debe ser mayor que el límite inferior LSL.")
    st.stop()

rep = repeatability(readings)

try:
    base_budget = build_uncertainty_budget(
        readings_mm=readings,
        resolution_mm=resolution_mm,
        cal_correction_um=cal_correction_um,
        cal_U_um=cal_U_um,
        cal_k=cal_k,
        nominal_mm=nominal_mm,
        temp_C=temp_C,
        temp_u_C=temp_u_C,
        alpha_per_C=alpha,
        method_u_um=method_u_um,
        operator_u_um=operator_u_um,
        coverage_k=coverage_k,
    )
except Exception as exc:
    st.error(str(exc))
    st.stop()

budget = base_budget
tolerance_um = (usl_mm-lsl_mm)*1000.0

st.markdown(
    f"""
<div class="gg-case">
  <div style="font-size:.78rem;font-weight:800;color:#f28e1c;letter-spacing:.08em">CASO DE MEDICIÓN</div>
  <h3 style="margin:.35rem 0 .25rem 0">{preset_name}</h3>
  <div style="color:#737986">{preset['description']}</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="gg-note">
<b>Qué conviene observar:</b> {preset['focus']}
</div>
""",
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "📘 Cómo usar",
    "🧠 Conceptos",
    "📊 Repetibilidad",
    "🧮 Presupuesto de incertidumbre",
    "🌡️ Correcciones y temperatura",
    "✅ Conformidad",
    "🔧 Selección del sistema",
    "🏭 Plan de medición",
])

# ---------------------------------------------------------------------
# Cómo usar
# ---------------------------------------------------------------------
with tabs[0]:
    c1, c2 = st.columns([1.05, .95], gap="large")

    with c1:
        st.subheader("De una lectura a una decisión de ingeniería")
        st.write(
            "El instrumento entrega una indicación, pero el resultado de medición requiere definir el mensurando, "
            "aplicar correcciones conocidas y evaluar cuánto podemos dudar razonablemente del valor obtenido."
        )

        st.plotly_chart(
            make_measurement_chain_figure(),
            width="stretch",
            config={"displaylogo": False},
            key="unc_measurement_chain",
        )

        st.markdown("#### Ruta de cálculo")
        route = [
            ("1. Define la especificación", "Identifica los límites $LSL$ y $USL$, la unidad y la condición de referencia de la característica."),
            ("2. Define el mensurando", "Aclara exactamente qué dimensión se mide, dónde, en qué dirección, a qué temperatura y bajo qué método."),
            ("3. Obtén lecturas repetidas", r"Con $x_1, x_2,\ldots,x_n$ se estima el promedio $\bar{x}$ y la dispersión experimental $s$."),
            ("4. Aplica correcciones conocidas", "El modelo puede incluir una corrección de calibración $C_{cal}$ y una corrección térmica $C_T$."),
            ("5. Convierte cada fuente a incertidumbre estándar", "Cada contribución debe expresarse como $u_i$ para poder compararla y combinarla."),
            ("6. Combina las contribuciones", "Para fuentes tratadas como independientes se usa $u_c=\\sqrt{\\sum(c_i u_i)^2}$."),
            ("7. Expande la incertidumbre", "El resultado se informa mediante $U=k\\,u_c$, con un factor de cobertura $k$ definido para el propósito."),
            ("8. Aplica una regla de decisión", "El resultado $y\\pm U$ se compara con $LSL$ y $USL$ bajo una regla de decisión definida."),
            ("9. Registra el resultado", "La decisión debe trazarse a pieza, plano, método, equipo, fecha, operador, ambiente y referencia de calibración."),
        ]
        for title, body in route:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.markdown(body)

    st.markdown("### Cómo se ve una medición dimensional bien planteada")
    st.write(
        "Antes de hablar de incertidumbre conviene visualizar cómo se obtiene físicamente la indicación. "
        "Un mismo instrumento puede producir resultados distintos si cambia la alineación, el contacto, la posición o la estrategia de búsqueda."
    )

    s1, s2 = st.columns(2, gap="large")
    with s1:
        st.markdown("#### Medición exterior de un eje")
        st.plotly_chart(
            make_shaft_measurement_schematic(),
            width="stretch",
            config={"displaylogo": False},
            key="unc_shaft_setup",
        )
        st.markdown(
            "La magnitud buscada es el diámetro $D$. El eje de medición debe coincidir con la sección y dirección que representan el mensurando."
        )
    with s2:
        st.markdown("#### Medición interior de un agujero")
        st.plotly_chart(
            make_hole_measurement_schematic(),
            width="stretch",
            config={"displaylogo": False},
            key="unc_hole_setup",
        )
        st.markdown(
            "En un alesómetro la lectura depende de la orientación y del punto de inversión. "
            "Por eso el método forma parte del modelo de medición y no puede separarse del resultado."
        )

    st.markdown(
        """
<div class="gg-note">
<b>Clave para ingeniería:</b> la incertidumbre no pertenece solamente al instrumento. 
Pertenece al <i>resultado de medición</i> obtenido con una pieza, método, operador, ambiente y cadena de calibración determinados.
</div>
""",
        unsafe_allow_html=True,
    )

    c1b, c2b = st.columns([1.05, .95], gap="large")
    with c1b:
        st.markdown("### Modelo matemático del resultado")
        st.latex(r"y=\bar{x}+C_{cal}+C_T")
        st.markdown(
            "Aquí $\\bar{x}$ es el promedio de las indicaciones, $C_{cal}$ es una corrección conocida asociada a calibración "
            "y $C_T$ corrige la dimensión a la temperatura de referencia. "
            "Las demás fuentes se modelan como incertidumbres cuando no se dispone de una corrección determinista."
        )
        st.latex(r"u_c=\sqrt{\sum_i(c_i u_i)^2}")
        st.markdown(
            "Cada $u_i$ es una incertidumbre estándar y $c_i$ es su coeficiente de sensibilidad. "
            "En este módulo varias contribuciones actúan directamente sobre una dimensión, por lo que se usa $c_i=1$."
        )
        st.latex(r"U=k\,u_c")
        st.markdown(
            "La incertidumbre expandida $U$ no es un error máximo conocido. "
            "Es una forma de expresar un intervalo asociado al resultado bajo el modelo y factor de cobertura seleccionados."
        )

    with c2b:
        latex_card(
            "Promedio",
            r"\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i",
            "Valor central de las lecturas repetidas."
        )
        latex_card(
            "Tipo A del promedio",
            r"u_A=\frac{s}{\sqrt{n}}",
            "Estimación estadística asociada al promedio de n lecturas."
        )
        latex_card(
            "Incertidumbre combinada",
            r"u_c=\sqrt{\sum_i(c_i u_i)^2}",
            "Combinación cuadrática para contribuciones tratadas como independientes."
        )
        latex_card(
            "Incertidumbre expandida",
            r"U=k\,u_c",
            "Incertidumbre informada después de aplicar el factor de cobertura."
        )
        latex_card(
            "Resultado",
            r"y\pm U",
            "La medición se interpreta junto con su incertidumbre, no como un número aislado."
        )

        st.markdown(
            """
<div class="gg-warning">
<b>Convención de MechLab:</b> las dimensiones se presentan hasta 0.001 mm y las incertidumbres se muestran en micras enteras. 
Los cálculos internos conservan precisión adicional para evitar acumulación de redondeo.
</div>
""",
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------
# Concepts
# ---------------------------------------------------------------------
with tabs[1]:
    st.subheader("Conceptos que conviene separar")

    st.write(
        "En metrología varios términos se usan como si fueran sinónimos. Esta separación es importante porque cada uno responde una pregunta distinta."
    )

    for i in range(0, len(CONCEPTS), 3):
        cols = st.columns(3)
        for col, item in zip(cols, CONCEPTS[i:i+3]):
            with col:
                st.markdown(
                    f"""
<div class="gg-concept">
<b style="color:#f28e1c">{item['term']}</b><br><br>
{item['short']}<br><br>
<span style="color:#737986">{item['engineering']}</span>
</div>
""",
                    unsafe_allow_html=True,
                )

    st.markdown("### Tres confusiones típicas")
    st.markdown(
        r"""
- **$\mathrm{Resolución}\neq\mathrm{incertidumbre}$:** un instrumento puede indicar $0.001\,\mathrm{mm}$ y tener una incertidumbre total bastante mayor.
- **$\mathrm{Calibración}\neq\mathrm{ajuste}$:** la calibración establece relaciones metrológicas; el ajuste modifica el instrumento para cambiar su respuesta.
- **$\mathrm{Precisión}\neq\mathrm{exactitud}$:** un conjunto de lecturas puede ser muy agrupado y aun estar desplazado por un efecto sistemático.
"""
    )

# ---------------------------------------------------------------------
# Repeatability
# ---------------------------------------------------------------------
with tabs[2]:
    st.subheader("Repetibilidad y contribución Tipo A")

    st.plotly_chart(
        make_repeatability_figure(readings, rep.mean_mm),
        width="stretch",
        config={"displaylogo": False},
        key="unc_repeatability_chart",
    )

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Número de lecturas", str(rep.n))
    r2.metric("Promedio", f"{rep.mean_mm:.3f} mm")
    r3.metric("Desviación estándar s", fmt_um(rep.stdev_mm*1000.0))
    r4.metric("Rango", fmt_um(rep.range_mm*1000.0))

    st.latex(r"s=\sqrt{\frac{\sum_{i=1}^{n}(x_i-\bar{x})^2}{n-1}}")
    st.latex(r"u_A(\bar{x})=\frac{s}{\sqrt{n}}")
    st.latex(rf"u_A(\bar{{x}})\approx {budget.uA_um:.0f}\,\mathrm{{\mu m}}")

    st.markdown("#### Qué significa cada término")
    st.markdown(
        r"""
- $x_i$: lectura individual.
- $\bar{x}$: promedio de las lecturas.
- $s$: desviación estándar muestral de las lecturas individuales.
- $n$: número de lecturas.
- $u_A(\bar{x})$: incertidumbre estándar Tipo A asociada al promedio.
"""
    )

    st.markdown("#### Qué representa realmente")
    st.write(
        "La desviación estándar describe la dispersión de lecturas individuales. "
        "Si el resultado se define como el promedio de n lecturas, la contribución Tipo A asociada a ese promedio disminuye con la raíz de n."
    )

    st.info(
        "Repetir muchas veces una medición no elimina incertidumbres sistemáticas como calibración, temperatura, alineación o método.",
        icon="📌"
    )

# ---------------------------------------------------------------------
# Budget
# ---------------------------------------------------------------------
with tabs[3]:
    st.subheader("Presupuesto de incertidumbre")

    st.write(
        "Todas las fuentes deben llevarse a incertidumbre estándar antes de combinarlas. "
        "El presupuesto base incluye repetibilidad, resolución, calibración, temperatura, método y operador. "
        "Además puedes agregar fuentes propias para adaptar el modelo a una medición real de taller o laboratorio."
    )

    b1, b2 = st.columns([1.05, .95], gap="large")

    with b1:
        st.markdown("### Modelo matemático")
        st.latex(r"y=f(x_1,x_2,\ldots,x_n)")
        st.markdown(
            "El resultado de medición se modela como una función de magnitudes de entrada. "
            "Cada entrada puede afectar el resultado con una sensibilidad distinta."
        )

        st.latex(r"c_i=\frac{\partial f}{\partial x_i}")
        st.markdown(
            "El coeficiente de sensibilidad $c_i$ indica cuánto cambia el resultado cuando cambia la entrada $x_i$."
        )

        st.latex(r"u_i(y)=|c_i|\,u(x_i)")
        st.markdown(
            "Cada fuente se expresa como una contribución estándar al resultado."
        )

        st.latex(r"u_A=\frac{s}{\sqrt{n}}")
        st.latex(r"u_r=\frac{r/2}{\sqrt{3}}=\frac{r}{2\sqrt{3}}")
        st.markdown(
            r"Para una indicación cuantizada en pasos de resolución $r$, se modela el redondeo dentro de $\pm r/2$ con distribución rectangular."
        )

        st.latex(r"u_{cal}=\frac{U_{cal}}{k_{cal}}")
        st.markdown(
            r"Si el certificado entrega una incertidumbre expandida $U_{cal}$ con factor $k_{cal}$, primero se transforma a incertidumbre estándar."
        )

        st.latex(r"u_T\approx \left|\frac{\partial L}{\partial T}\right|u(T)\approx |\alpha D\,u(T)|")

        st.latex(r"u_c=\sqrt{\sum_i\left[c_i\,u(x_i)\right]^2}")
        st.latex(r"U=k\,u_c")

        st.markdown(
            r"""
En el presupuesto base:

- $u_A$: repetibilidad del promedio.
- $u_r$: resolución.
- $u_{cal}$: calibración.
- $u_T$: temperatura.
- $u_m$: método, alineación y contacto.
- $u_o$: operador y lectura.
"""
        )

    with b2:
        st.markdown("### Fuentes adicionales editables")
        st.write(
            "Agrega aquí efectos que no estén representados por el presupuesto base. "
            "Por ejemplo: error residual de Abbe, deformación por fuerza, patrón maestro, deriva, fijación o una contribución específica del proceso."
        )

        custom_default = pd.DataFrame([
            {
                "Fuente": "Geometría / Abbe residual",
                "Tipo": "Tipo B",
                "u estándar [µm]": 0.0,
                "Sensibilidad": 1.0,
                "Nota": "Usar solo si el efecto residual no fue corregido por otro modelo.",
            },
            {
                "Fuente": "Deformación por fuerza de medición",
                "Tipo": "Tipo B",
                "u estándar [µm]": 0.0,
                "Sensibilidad": 1.0,
                "Nota": "Pieza, contacto o palpador deformable.",
            },
            {
                "Fuente": "Fuente adicional",
                "Tipo": "Tipo B",
                "u estándar [µm]": 0.0,
                "Sensibilidad": 1.0,
                "Nota": "",
            },
        ])

        custom_df = st.data_editor(
            custom_default,
            num_rows="dynamic",
            width="stretch",
            hide_index=True,
            key="unc_custom_budget_editor",
            column_config={
                "u estándar [µm]": st.column_config.NumberColumn(
                    "u estándar [µm]",
                    min_value=0.0,
                    step=1.0,
                    format="%.0f",
                ),
                "Sensibilidad": st.column_config.NumberColumn(
                    "Sensibilidad",
                    step=0.1,
                    format="%.2f",
                ),
            },
        )

        custom_rows = []
        for _, row in custom_df.iterrows():
            custom_rows.append({
                "name": row.get("Fuente", ""),
                "source_type": row.get("Tipo", "Tipo B"),
                "standard_u_um": row.get("u estándar [µm]", 0.0),
                "sensitivity": row.get("Sensibilidad", 1.0),
                "note": row.get("Nota", ""),
            })

        budget = combine_with_custom_items(base_budget, custom_rows)

        st.plotly_chart(
            make_uncertainty_budget_figure(budget.items),
            width="stretch",
            config={"displaylogo": False},
            key="unc_budget_chart",
        )

    st.markdown("### Resultado del presupuesto")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Resultado corregido", f"{budget.corrected_value_mm:.3f} mm")
    m2.metric("Incertidumbre estándar combinada", fmt_um(budget.uc_um))
    m3.metric("Factor de cobertura", f"{budget.k:.1f}")
    m4.metric("Incertidumbre expandida", fmt_um(budget.U_um))

    st.latex(
        rf"y={budget.corrected_value_mm:.3f}\,\mathrm{{mm}}\pm {budget.U_um:.0f}\,\mathrm{{\mu m}}\qquad (k={budget.k:.1f})"
    )

    budget_rows = uncertainty_percentages(budget.items)
    for row in budget_rows:
        row["Incertidumbre estándar [µm]"] = round(row["Incertidumbre estándar [µm]"])
        row["Contribución [µm]"] = round(row["Contribución [µm]"])
        row["Varianza [%]"] = round(row["Varianza [%]"], 1)

    render_budget_table_latex(budget_rows)

    st.markdown("#### Cómo leer este presupuesto")
    st.write(
        "La fuente que domina la varianza merece la primera revisión. "
        "Si la temperatura o la geometría dominan, mejorar la resolución del instrumento puede tener poco efecto. "
        "Si domina repetibilidad, conviene revisar técnica, fijación, superficie, fuerza de medición y estabilidad del proceso."
    )

    st.markdown(
        """
<div class="gg-warning">
<b>Presupuesto editable:</b> una fuente conocida y corregible debería modelarse primero como corrección. 
La incertidumbre representa la duda residual asociada al resultado, no un lugar donde esconder errores sistemáticos conocidos.
</div>
""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------
# Corrections & temperature
# ---------------------------------------------------------------------
with tabs[4]:
    st.subheader("Correcciones conocidas y temperatura de referencia")

    corrected_after_cal = rep.mean_mm + budget.correction_cal_um/1000.0

    st.markdown("### Modelo de resultado")
    st.latex(r"y=\bar{x}+C_{cal}+C_T")
    st.latex(rf"\bar{{x}}={rep.mean_mm:.3f}\,\mathrm{{mm}}")
    st.latex(rf"C_{{cal}}={budget.correction_cal_um:+.0f}\,\mathrm{{\mu m}}")
    st.latex(rf"C_T={budget.correction_temp_um:+.0f}\,\mathrm{{\mu m}}")
    st.latex(rf"y={budget.corrected_value_mm:.3f}\,\mathrm{{mm}}")

    st.markdown("### Corrección térmica a la temperatura de referencia")
    render_temperature_model_cards()
    st.latex(
        r"L_{20}=\frac{L_T}{1+\alpha\left(T-20\,^{\circ}\mathrm{C}\right)}"
    )
    st.latex(r"C_T=L_{20}-L_T")
    st.markdown(
        r"La corrección $C_T$ modifica el valor atribuido a la dimensión para referirlo a $20\,^{\circ}\mathrm{C}$. "
        "La incertidumbre térmica, en cambio, cuantifica cuánto puede variar ese resultado por no conocer exactamente la temperatura."
    )
    st.latex(
        r"u_T\approx\left|\frac{\partial L}{\partial T}\right|u(T)"
        r"\approx |\alpha D\,u(T)|"
    )

    st.plotly_chart(
        make_temperature_correction_figure(
            corrected_after_cal,
            budget.corrected_value_mm,
            20.0,
            temp_C,
        ),
        width="stretch",
        config={"displaylogo": False},
        key="unc_temperature_chart",
    )

    t1, t2, t3 = st.columns(3)
    t1.metric("Temperatura pieza", f"{temp_C:.1f} °C")
    t2.metric("Incertidumbre estándar de temperatura", f"{temp_u_C:.1f} °C")
    t3.metric("Contribución térmica estándar", fmt_um(budget.u_temperature_um))

    st.write(
        "La corrección térmica cambia el valor atribuido a la dimensión; la incertidumbre de temperatura agrega duda al resultado. "
        "Son conceptos diferentes y ambos pueden coexistir."
    )

    st.warning(
        "El modelo térmico mostrado supone expansión lineal uniforme y un coeficiente conocido. "
        "Grandes gradientes térmicos, piezas complejas o instrumentos con comportamiento térmico significativo requieren un modelo más completo.",
        icon="🌡️"
    )

    st.markdown(
        """
<div class="gg-note">
<b>Separación de alcance:</b> en este módulo la temperatura se trata como parte del <b>modelo de medición</b>: corrección a la referencia y contribución de incertidumbre. 
El efecto de la temperatura sobre el <b>juego o interferencia funcional durante montaje y operación</b> pertenece al módulo Ajustes y Tolerancias ISO, donde se comparan eje y alojamiento a sus temperaturas de servicio.
</div>
""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# Conformity
# ---------------------------------------------------------------------
with tabs[5]:
    st.subheader("Conformidad · el valor medido no basta")

    rule_mode = st.radio(
        "Regla de decisión a explorar",
        [
            "Intervalo expandido dentro/fuera de especificación",
            "Banda de guarda configurable",
        ],
        horizontal=True,
        key="unc_decision_mode",
    )

    if rule_mode.startswith("Intervalo"):
        decision = decision_interval_rule(
            budget.corrected_value_mm,
            budget.U_um,
            lsl_mm,
            usl_mm,
        )
        acc_lsl = lsl_mm
        acc_usl = usl_mm
    else:
        guard_default = round(budget.U_um)
        guard_um = st.number_input(
            "Banda de guarda [µm]",
            min_value=0.0,
            value=float(guard_default),
            step=1.0,
            format="%.0f",
            key="unc_guard_band",
        )
        st.latex(r"A_{LSL}=LSL+g,\qquad A_{USL}=USL-g")
        decision = decision_guard_band(
            budget.corrected_value_mm,
            budget.U_um,
            lsl_mm,
            usl_mm,
            guard_um,
        )
        acc_lsl = decision.acceptance_lsl_mm
        acc_usl = decision.acceptance_usl_mm

    st.plotly_chart(
        make_conformity_figure(
            lsl_mm,
            usl_mm,
            budget.corrected_value_mm,
            budget.U_um,
            acc_lsl,
            acc_usl,
        ),
        width="stretch",
        config={"displaylogo": False},
        key="unc_conformity_chart",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi_card("Resultado corregido", f"{budget.corrected_value_mm:.3f} mm")
    with c2:
        render_kpi_card("U expandida", fmt_um(budget.U_um))
    with c3:
        render_kpi_card("Decisión", decision.status)

    st.markdown(f"**Lectura:** {decision.message}")

    st.markdown("### Ecuaciones de la decisión")
    st.latex(r"I_y=[y-U,\;y+U]")
    st.latex(r"\text{Conformidad demostrada:}\quad y-U\ge LSL\quad\land\quad y+U\le USL")
    st.latex(r"\text{No conformidad demostrada:}\quad y+U<LSL\quad\lor\quad y-U>USL")
    st.markdown(
        "Si ninguna de esas condiciones se cumple, el intervalo asociado a la medición intersecta un límite y la decisión depende de la regla acordada."
    )

    st.markdown("### Por qué aparece una zona de decisión")
    st.write(
        "Cuando el intervalo asociado a la incertidumbre se acerca a un límite, el valor indicado por sí solo no permite separar de manera contundente conformidad y no conformidad. "
        "La regla de decisión define cómo se gestiona ese riesgo."
    )

    st.markdown(
        """
<div class="gg-warning">
<b>Importante:</b> la regla con banda de guarda de esta pestaña es configurable y didáctica. 
La regla contractual debe provenir del sistema de calidad, cliente, norma o acuerdo aplicable. 
No utilices automáticamente g = U como regla universal.
</div>
""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------
# Instrument/system selection
# ---------------------------------------------------------------------
with tabs[6]:
    st.subheader("Selección del sistema · instrumento, geometría y técnica")

    st.write(
        "Elegir un instrumento no consiste solo en revisar su resolución. "
        "También debe ser compatible con la tolerancia, la geometría, el acceso, la fuerza de medición, "
        "la temperatura y la incertidumbre total del método."
    )

    target_ratio = st.select_slider(
        "Relación tolerancia / U que quieres explorar como criterio interno",
        options=[2, 3, 4, 5, 10],
        value=4,
        key="unc_target_ratio",
    )

    current_ratio = tolerance_uncertainty_ratio(lsl_mm, usl_mm, budget.U_um)
    max_U = max_uncertainty_for_target_ratio(lsl_mm, usl_mm, target_ratio)
    res_ratio = resolution_ratio(lsl_mm, usl_mm, resolution_mm)

    st.markdown("### 1. Relaciones de capacidad metrológica")
    st.latex(r"T=USL-LSL")
    st.latex(r"R_{T/U}=\frac{T}{U}")
    st.latex(r"R_{T/r}=\frac{T}{r}")

    st.markdown(
        "Estas relaciones ayudan a dimensionar el sistema, pero no sustituyen un presupuesto de incertidumbre "
        "ni constituyen por sí solas una regla universal de aceptación."
    )

    st.plotly_chart(
        make_instrument_suitability_figure(
            tolerance_um,
            budget.U_um,
            resolution_mm*1000.0,
            target_ratio,
        ),
        width="stretch",
        config={"displaylogo": False},
        key="unc_system_suitability_chart",
    )

    s1, s2, s3 = st.columns(3)
    s1.metric("Tolerancia total", fmt_um(tolerance_um))
    s2.metric("Tolerancia / incertidumbre", "—" if current_ratio is None else f"{current_ratio:.1f}")
    s3.metric("Tolerancia / resolución", "—" if res_ratio is None else f"{res_ratio:.1f}")

    if max_U is not None:
        st.latex(
            rf"U_{{objetivo}}\le\frac{{T}}{{{target_ratio}}}\approx {max_U:.0f}\,\mathrm{{\mu m}}"
        )

    st.markdown("### 2. Instrumentos típicos y qué vigilar")
    st.dataframe(INSTRUMENT_GUIDANCE, width="stretch", hide_index=True)

    st.markdown("### 3. Errores geométricos de medición")
    st.write(
        "La geometría del montaje puede generar errores aun cuando el instrumento esté calibrado. "
        "Dos casos clásicos son el error de coseno y el error de Abbe."
    )

    g1, g2 = st.columns(2, gap="large")

    with g1:
        st.markdown("#### Error de coseno")
        cosine_length = st.number_input(
            "Longitud / dimensión asociada [mm]",
            min_value=1.0,
            value=float(max(nominal_mm, 10.0)),
            step=1.0,
            key="unc_cosine_length",
        )
        cosine_angle = st.number_input(
            "Desalineación angular θ [°]",
            min_value=0.0,
            max_value=10.0,
            value=0.10,
            step=0.05,
            format="%.2f",
            key="unc_cosine_angle",
        )
        st.plotly_chart(
            make_cosine_error_schematic(cosine_angle),
            width="stretch",
            config={"displaylogo": False},
            key="unc_cosine_schematic",
        )
        st.latex(r"L_m=L\cos\theta")
        st.latex(r"\Delta L_{\cos}=L-L_m=L(1-\cos\theta)")
        st.latex(r"\Delta L_{\cos}\approx L\frac{\theta^2}{2}\qquad(\theta\ \text{pequeño})")

    with g2:
        st.markdown("#### Error de Abbe")
        abbe_offset = st.number_input(
            "Separación entre línea de medida y referencia h [mm]",
            min_value=0.0,
            value=25.0,
            step=1.0,
            key="unc_abbe_offset",
        )
        abbe_angle = st.number_input(
            "Error angular θ [°]",
            min_value=0.0,
            max_value=10.0,
            value=0.05,
            step=0.05,
            format="%.2f",
            key="unc_abbe_angle",
        )
        st.plotly_chart(
            make_abbe_error_schematic(abbe_offset, abbe_angle),
            width="stretch",
            config={"displaylogo": False},
            key="unc_abbe_schematic",
        )
        st.latex(r"e_A=h\tan\theta")
        st.latex(r"e_A\approx h\,\theta\qquad(\theta\ \text{pequeño y en radianes})")

    force_def_um = st.number_input(
        "Deformación estimada por fuerza de medición [µm]",
        min_value=0.0,
        value=0.0,
        step=1.0,
        format="%.0f",
        key="unc_force_deformation",
    )

    geom = geometry_error_model(
        cosine_length,
        cosine_angle,
        abbe_offset,
        abbe_angle,
        force_def_um,
    )

    gm1, gm2, gm3, gm4 = st.columns(4)
    gm1.metric("Error de coseno", fmt_um(geom.cosine_error_um))
    gm2.metric("Error de Abbe", fmt_um(geom.abbe_error_um))
    gm3.metric("Deformación", fmt_um(geom.force_deformation_um))
    gm4.metric("Combinación orientativa", fmt_um(geom.combined_geometry_um))

    st.markdown(
        """
<div class="gg-note">
<b>Cómo llevar esto al presupuesto:</b> si el efecto tiene signo y magnitud conocidos, conviene corregirlo. 
Si queda una duda residual, esa parte puede incorporarse como una contribución de incertidumbre en la pestaña Presupuesto.
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### 4. Fuerza, contacto y deformación")
    st.write(
        "En piezas delgadas, materiales blandos, puntas pequeñas o grandes fuerzas de contacto, "
        "el propio acto de medir puede cambiar la geometría. "
        "La fuerza de medición debe formar parte del método cuando su efecto sea comparable con la tolerancia."
    )

    st.markdown("### 5. Preguntas antes de seleccionar el sistema")
    st.markdown(
        """
- ¿El instrumento puede acceder físicamente a la característica?
- ¿La geometría que se quiere medir es tamaño, forma, orientación o posición?
- ¿La resolución es suficiente, pero también lo es la incertidumbre total?
- ¿La fuerza de medición puede deformar la pieza?
- ¿Existe desalineación angular o separación de Abbe?
- ¿La estrategia permite detectar ovalidad, conicidad o variación local?
- ¿La temperatura de pieza e instrumento está controlada o compensada?
- ¿La inspección será de producción, recepción o laboratorio?
"""
    )

# ---------------------------------------------------------------------
# Measurement plan
# ---------------------------------------------------------------------
with tabs[7]:
    st.subheader("Plan de medición y registro de ingeniería")

    st.write(
        "Una medición útil para ingeniería debe poder repetirse, auditarse e interpretarse. "
        "La ficha final necesita identificar qué se midió, con qué sistema, bajo qué condiciones y con qué criterio se tomó la decisión."
    )

    p1, p2 = st.columns(2, gap="large")
    with p1:
        characteristic = st.text_input(
            "Característica",
            value=f"Dimensión {nominal_mm:.3f} mm",
            key="unc_plan_characteristic",
        )
        instrument_id = st.text_input(
            "Equipo / identificación",
            value="Micrómetro / ID interno",
            key="unc_plan_instrument",
        )
        drawing_ref = st.text_input(
            "Plano / especificación",
            value="Plano Rev. vigente",
            key="unc_plan_drawing",
        )
        operator = st.text_input(
            "Operador",
            value="Inspector / técnico",
            key="unc_plan_operator",
        )

    with p2:
        location = st.text_input(
            "Ubicación / sección de medición",
            value="Zona funcional definida en plano",
            key="unc_plan_location",
        )
        method = st.text_input(
            "Método",
            value="Lecturas repetidas y promedio",
            key="unc_plan_method",
        )
        environment = st.text_input(
            "Condición ambiental",
            value=f"{temp_C:.1f} °C",
            key="unc_plan_environment",
        )
        traceability = st.text_input(
            "Referencia de calibración",
            value="Certificado vigente",
            key="unc_plan_traceability",
        )

    st.markdown("### Resultado listo para control de calidad")
    st.latex(
        rf"y={budget.corrected_value_mm:.3f}\,\mathrm{{mm}}\pm {budget.U_um:.0f}\,\mathrm{{\mu m}}\qquad(k={budget.k:.1f})"
    )

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        render_kpi_card("LSL", f"{lsl_mm:.3f} mm")
    with f2:
        render_kpi_card("USL", f"{usl_mm:.3f} mm")
    with f3:
        render_kpi_card("Resultado", f"{budget.corrected_value_mm:.3f} mm")
    with f4:
        render_kpi_card("Decisión", decision.status)

    st.markdown(
        f"""
<div class="gg-case">
  <div style="font-size:.78rem;font-weight:800;color:#f28e1c;letter-spacing:.08em">FICHA DE RESULTADO</div>
  <h3 style="margin:.35rem 0 .45rem 0">{characteristic}</h3>
  <div><b>Resultado:</b> {budget.corrected_value_mm:.3f} mm ± {budget.U_um:.0f} µm (k={budget.k:.1f})</div>
  <div><b>Especificación:</b> {lsl_mm:.3f} a {usl_mm:.3f} mm</div>
  <div><b>Decisión:</b> {decision.status}</div>
  <div><b>Equipo:</b> {instrument_id}</div>
  <div><b>Método:</b> {method}</div>
  <div><b>Temperatura:</b> {environment}</div>
  <div><b>Calibración:</b> {traceability}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### Checklist previo a liberar el resultado")
    checked = 0
    for idx, item in enumerate(QUALITY_CHECKLIST):
        if st.checkbox(item, value=False, key=f"unc_quality_check_{idx}"):
            checked += 1

    st.metric("Checklist completado", f"{checked}/{len(QUALITY_CHECKLIST)}")

    st.markdown("### Registro técnico")
    summary_rows = [
        {"Campo": "Característica", "Valor": characteristic},
        {"Campo": "Plano / especificación", "Valor": drawing_ref},
        {"Campo": "Límites", "Valor": f"{lsl_mm:.3f} a {usl_mm:.3f} mm"},
        {"Campo": "Resultado", "Valor": f"{budget.corrected_value_mm:.3f} mm ± {budget.U_um:.0f} µm"},
        {"Campo": "Factor de cobertura", "Valor": f"{budget.k:.1f}"},
        {"Campo": "Decisión", "Valor": decision.status},
        {"Campo": "Equipo", "Valor": instrument_id},
        {"Campo": "Método", "Valor": method},
        {"Campo": "Temperatura / ambiente", "Valor": environment},
        {"Campo": "Calibración", "Valor": traceability},
        {"Campo": "Operador", "Valor": operator},
        {"Campo": "Ubicación", "Valor": location},
    ]
    st.dataframe(summary_rows, width="stretch", hide_index=True)

    report_text = result_summary_text(
        characteristic=characteristic,
        lsl_mm=lsl_mm,
        usl_mm=usl_mm,
        result_mm=budget.corrected_value_mm,
        U_um=budget.U_um,
        k=budget.k,
        decision=decision.status,
        instrument=instrument_id,
        temperature_C=temp_C,
        operator=operator,
        calibration_ref=traceability,
    )

    st.download_button(
        "Descargar resumen TXT",
        data=report_text.encode("utf-8"),
        file_name="resultado_medicion_mechlab.txt",
        mime="text/plain",
        key="unc_download_summary",
    )

    st.markdown(
        """
<div class="gg-note">
<b>Criterio de liberación:</b> una ficha técnicamente completa debe identificar la característica, la especificación, el resultado, 
la incertidumbre, el equipo, la trazabilidad, el método, la condición ambiental y la regla de decisión utilizada.
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()
st.caption(
    "GG DIMEC · MechLab · Metrología y Fabricación · Medición, incertidumbre y conformidad."
)
