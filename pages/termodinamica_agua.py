from __future__ import annotations
import math
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from modules.water_props import (
    TC_C, PC_KPA, TRIPLE_T_C, TRIPLE_P_KPA,
    solve_state, saturation_curve, saturation_table_T,
    saturation_table_P, table_PT
)

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
LOGO = ASSETS / "logo_card.png"

ORANGE = "#f28e1c"
BLUE = "#2474b5"
CYAN = "#6ec5e9"
DARK = "#262730"
GRAY = "#6b7280"
GREEN = "#27864b"
RED = "#c43c35"

st.markdown("""
<style>
.block-container {padding-top: 1.0rem; padding-bottom: 2rem; max-width: 1650px;}
.thermo-card {
    background:#fafafa; border:1px solid #e6e6e6; border-radius:12px;
    padding:10px 12px; min-height:84px; margin-bottom:8px;
}
.thermo-title {font-size:.83rem;color:#666;font-weight:600;margin-bottom:.22rem;}
.thermo-value {font-size:1.15rem;color:#111827;font-weight:700;word-break:break-word;}
.phase-card {
    border-left:5px solid #f28e1c;background:#fff8ef;padding:10px 14px;
    border-radius:9px;margin:.25rem 0 .75rem 0;font-weight:700;
}
.note-card {
    border:1px solid #e7e7e7;background:#fcfcfc;padding:10px 13px;border-radius:9px;
}
.brand-kicker {
    color:#db7810; font-weight:800; letter-spacing:.06em; font-size:.88rem;
    text-transform:uppercase; margin-bottom:.15rem;
}
.brand-subtitle {
    color:#6b7280; font-size:1.02rem; margin-top:.15rem;
}
.guide-step {
    border-left:4px solid #f28e1c; background:#fffaf4; padding:10px 13px;
    border-radius:7px; margin:.45rem 0;
}
</style>
""", unsafe_allow_html=True)

def fmt(x, unit="", sig=6):
    if x is None:
        return "—"
    try:
        x = float(x)
    except Exception:
        return str(x)
    if not math.isfinite(x):
        return "—"
    a = abs(x)
    if a == 0:
        s = "0"
    elif a >= 1e6 or a < 1e-4:
        s = f"{x:.4e}"
    else:
        s = f"{x:.{sig}g}"
    return f"{s} {unit}".strip()

def card(title, value):
    st.markdown(
        f'<div class="thermo-card"><div class="thermo-title">{title}</div>'
        f'<div class="thermo-value">{value}</div></div>',
        unsafe_allow_html=True
    )

@st.cache_data(show_spinner=False)
def dome_df():
    return saturation_curve(185)

@st.cache_data(show_spinner=False)
def sat_table_T_cached(t1, t2, n):
    return saturation_table_T(t1, t2, n)

@st.cache_data(show_spinner=False)
def sat_table_P_cached(p1, p2, n, logspace):
    return saturation_table_P(p1, p2, n, logspace)

@st.cache_data(show_spinner=False)
def pt_table_cached(P, t1, t2, n):
    return table_PT(P, t1, t2, n)

brand_left, brand_right = st.columns([1.0, 4.2], vertical_alignment="center")
with brand_left:
    if LOGO.exists():
        st.image(str(LOGO), width=230)
with brand_right:
    st.markdown('<div class="brand-kicker">GG DIMEC · MECHLAB · TERMODINÁMICA</div>', unsafe_allow_html=True)
    st.title("Propiedades termodinámicas del agua y vapor")
    st.markdown(
        '<div class="brand-subtitle">Visor interactivo para identificar estados, consultar propiedades '
        'y comprender las regiones termodinámicas del agua.</div>',
        unsafe_allow_html=True
    )

with st.expander("Alcance y criterio de cálculo", expanded=False):
    st.markdown(
        "La herramienta trabaja con **agua ordinaria y vapor de agua** usando la formulación "
        "industrial **IAPWS-IF97**. Las tablas que aparecen en pantalla son **calculadas**, "
        "no transcripciones del libro."
    )
    st.markdown("**Enfoque pedagógico**")
    st.latex(
        r"\text{dos propiedades intensivas independientes}"
        r"\;\Longrightarrow\;"
        r"\text{estado termodinámico}"
        r"\;\Longrightarrow\;"
        r"\{P,T,v,u,h,s,\rho,\ldots\}"
    )
    st.markdown(
        "La idea es **identificar primero la región o fase** y sólo después interpretar las "
        "propiedades. En la región bifásica, presión y temperatura están vinculadas por la "
        "condición de saturación; por ello se necesita una propiedad adicional, como la "
        "calidad $x$, para fijar un estado específico entre líquido saturado y vapor saturado."
    )

mode = st.selectbox(
    "Par de propiedades de entrada",
    ["P-T", "T-x", "P-x", "P-h", "P-s", "h-s"],
    help="P absoluta. Para T-x y P-x se trabaja sobre la línea/región de saturación."
)

with st.form("th_state_form"):
    a,b,c,d = st.columns([1,1,1,1.4])
    kwargs = {}

    if mode == "P-T":
        kwargs["P_kPa"] = a.number_input("P absoluta [kPa]", value=101.325, format="%.8g")
        kwargs["T_C"] = b.number_input("T [°C]", value=120.0, format="%.8g")
        c.markdown("**Uso típico**")
        c.caption("Líquido comprimido, vapor sobrecalentado o detección de saturación.")
    elif mode == "T-x":
        kwargs["T_C"] = a.number_input("T [°C]", value=100.0, format="%.8g")
        kwargs["x"] = b.number_input("Calidad x [-]", value=0.5, step=0.01, format="%.6f")
        c.markdown("**Rango de saturación**")
        c.caption(f"{TRIPLE_T_C:.2f} a {TC_C:.3f} °C")
    elif mode == "P-x":
        kwargs["P_kPa"] = a.number_input("P absoluta [kPa]", value=101.325, format="%.8g")
        kwargs["x"] = b.number_input("Calidad x [-]", value=0.5, step=0.01, format="%.6f")
        c.markdown("**Rango de saturación**")
        c.caption(f"{TRIPLE_P_KPA:.6g} a {PC_KPA:.0f} kPa")
    elif mode == "P-h":
        kwargs["P_kPa"] = a.number_input("P absoluta [kPa]", value=1000.0, format="%.8g")
        kwargs["h"] = b.number_input("h [kJ/kg]", value=2800.0, format="%.8g")
        c.caption("Útil para procesos, turbinas, válvulas y balances.")
    elif mode == "P-s":
        kwargs["P_kPa"] = a.number_input("P absoluta [kPa]", value=1000.0, format="%.8g")
        kwargs["s"] = b.number_input("s [kJ/kg·K]", value=6.5, format="%.8g")
        c.caption("Útil para procesos isentrópicos y análisis de equipos.")
    else:
        kwargs["h"] = a.number_input("h [kJ/kg]", value=2800.0, format="%.8g")
        kwargs["s"] = b.number_input("s [kJ/kg·K]", value=6.5, format="%.8g")
        c.caption("Par útil para localizar estados en el diagrama de Mollier.")

    calc = d.form_submit_button("Calcular estado", use_container_width=True)

if calc or "th_result" not in st.session_state or st.session_state.get("th_mode") != mode:
    try:
        st.session_state.th_result = solve_state(mode, **kwargs)
        st.session_state.th_mode = mode
        st.session_state.th_kwargs = kwargs
        st.session_state.th_error = None
    except Exception as exc:
        st.session_state.th_error = str(exc)

if st.session_state.get("th_error"):
    st.error(st.session_state.th_error)
    st.stop()

res = st.session_state.get("th_result")
if not res:
    st.stop()

if res.get("underdetermined"):
    st.markdown(f'<div class="phase-card">{res["phase"]}</div>', unsafe_allow_html=True)
    st.warning(
        "Con P y T exactamente sobre saturación no se puede determinar la calidad. "
        "Se muestran los extremos líquido saturado (x=0) y vapor saturado (x=1)."
    )
    f = res["sat_f"]; g = res["sat_g"]
    r1,r2 = st.columns(2)
    with r1:
        st.markdown("#### Líquido saturado")
        c1,c2 = st.columns(2)
        with c1: card("T", fmt(f["T_C"], "°C")); card("v_f", fmt(f["v"], "m³/kg"))
        with c2: card("P", fmt(f["P_kPa"], "kPa")); card("h_f", fmt(f["h"], "kJ/kg"))
    with r2:
        st.markdown("#### Vapor saturado")
        c1,c2 = st.columns(2)
        with c1: card("T", fmt(g["T_C"], "°C")); card("v_g", fmt(g["v"], "m³/kg"))
        with c2: card("P", fmt(g["P_kPa"], "kPa")); card("h_g", fmt(g["h"], "kJ/kg"))
    state = None
else:
    state = res["state"]
    st.markdown(f'<div class="phase-card">Estado identificado: {state["phase"]}</div>', unsafe_allow_html=True)

    r1 = st.columns(4)
    r2 = st.columns(4)
    with r1[0]: card("Temperatura", fmt(state["T_C"], "°C"))
    with r1[1]: card("Presión absoluta", fmt(state["P_kPa"], "kPa"))
    with r1[2]: card("Volumen específico v", fmt(state["v"], "m³/kg"))
    with r1[3]: card("Densidad ρ", fmt(state["rho"], "kg/m³"))
    with r2[0]: card("Energía interna u", fmt(state["u"], "kJ/kg"))
    with r2[1]: card("Entalpía h", fmt(state["h"], "kJ/kg"))
    with r2[2]: card("Entropía s", fmt(state["s"], "kJ/kg·K"))
    with r2[3]: card("Calidad x", fmt(state["x"], "") if state["x"] is not None else "No aplica")

tabs = st.tabs(["Estado", "Diagramas", "Tablas de agua", "Ecuaciones", "Tutorial de uso"])

with tabs[0]:
    st.markdown("### Interpretación del estado")
    if state:
        st.markdown(
            f"El punto calculado corresponde a **{state['phase']}**. "
            f"El motor IF97 reporta la región **{state['region']}**."
        )
        if state["x"] is not None:
            st.latex(r"x=\frac{m_g}{m_f+m_g}")
            st.caption("x = 0 corresponde a líquido saturado y x = 1 a vapor saturado.")
    else:
        st.markdown(
            "El par P-T fija la línea de saturación, pero no una posición única dentro de la mezcla. "
            "Es necesario agregar x, v, u, h o s."
        )

    st.markdown("### Punto crítico del agua")
    p1,p2 = st.columns(2)
    with p1: card("T crítica", fmt(TC_C, "°C"))
    with p2: card("P crítica", fmt(PC_KPA, "kPa"))

with tabs[1]:
    st.markdown("### Curvas de propiedades del agua")
    df = dome_df()

    # T-v
    fig_tv = go.Figure()
    xpoly = np.concatenate([df["vf"].to_numpy(), df["vg"].to_numpy()[::-1]])
    ypoly = np.concatenate([df["T_C"].to_numpy(), df["T_C"].to_numpy()[::-1]])
    fig_tv.add_trace(go.Scatter(x=xpoly,y=ypoly,fill="toself",
                                fillcolor="rgba(110,197,233,0.16)",
                                line=dict(color="rgba(0,0,0,0)"),
                                hoverinfo="skip",showlegend=False))
    fig_tv.add_trace(go.Scatter(x=df["vf"],y=df["T_C"],name="Líquido saturado",
                                line=dict(color=BLUE,width=2.5)))
    fig_tv.add_trace(go.Scatter(x=df["vg"],y=df["T_C"],name="Vapor saturado",
                                line=dict(color=RED,width=2.5)))
    if state:
        fig_tv.add_trace(go.Scatter(x=[state["v"]],y=[state["T_C"]],mode="markers",
                                    name="Estado",marker=dict(size=12,color=ORANGE,symbol="diamond")))
    fig_tv.update_layout(title="Diagrama T-v",xaxis_title="v [m³/kg]",yaxis_title="T [°C]",
                         xaxis_type="log",height=475,hovermode="closest",
                         margin=dict(l=20,r=20,t=55,b=35))

    # P-v
    fig_pv = go.Figure()
    ypolyP = np.concatenate([df["P_kPa"].to_numpy(), df["P_kPa"].to_numpy()[::-1]])
    fig_pv.add_trace(go.Scatter(x=xpoly,y=ypolyP,fill="toself",
                                fillcolor="rgba(110,197,233,0.16)",
                                line=dict(color="rgba(0,0,0,0)"),
                                hoverinfo="skip",showlegend=False))
    fig_pv.add_trace(go.Scatter(x=df["vf"],y=df["P_kPa"],name="Líquido saturado",
                                line=dict(color=BLUE,width=2.5)))
    fig_pv.add_trace(go.Scatter(x=df["vg"],y=df["P_kPa"],name="Vapor saturado",
                                line=dict(color=RED,width=2.5)))
    if state:
        fig_pv.add_trace(go.Scatter(x=[state["v"]],y=[state["P_kPa"]],mode="markers",
                                    name="Estado",marker=dict(size=12,color=ORANGE,symbol="diamond")))
    fig_pv.update_layout(title="Diagrama P-v",xaxis_title="v [m³/kg]",yaxis_title="P [kPa]",
                         xaxis_type="log",yaxis_type="log",height=475,
                         margin=dict(l=20,r=20,t=55,b=35))

    q1,q2 = st.columns(2,gap="small")
    with q1: st.plotly_chart(fig_tv,use_container_width=True,config={"displaylogo":False})
    with q2: st.plotly_chart(fig_pv,use_container_width=True,config={"displaylogo":False})

    # T-s
    fig_ts = go.Figure()
    xpoly_s = np.concatenate([df["sf"].to_numpy(), df["sg"].to_numpy()[::-1]])
    ypoly_s = np.concatenate([df["T_C"].to_numpy(), df["T_C"].to_numpy()[::-1]])
    fig_ts.add_trace(go.Scatter(x=xpoly_s,y=ypoly_s,fill="toself",
                                fillcolor="rgba(110,197,233,0.16)",
                                line=dict(color="rgba(0,0,0,0)"),
                                hoverinfo="skip",showlegend=False))
    fig_ts.add_trace(go.Scatter(x=df["sf"],y=df["T_C"],name="Líquido saturado",line=dict(color=BLUE,width=2.5)))
    fig_ts.add_trace(go.Scatter(x=df["sg"],y=df["T_C"],name="Vapor saturado",line=dict(color=RED,width=2.5)))
    if state:
        fig_ts.add_trace(go.Scatter(x=[state["s"]],y=[state["T_C"]],mode="markers",
                                    name="Estado",marker=dict(size=12,color=ORANGE,symbol="diamond")))
    fig_ts.update_layout(title="Diagrama T-s",xaxis_title="s [kJ/kg·K]",yaxis_title="T [°C]",
                         height=475,margin=dict(l=20,r=20,t=55,b=35))

    # h-s / Mollier
    fig_hs = go.Figure()
    fig_hs.add_trace(go.Scatter(x=df["sf"],y=df["hf"],name="Líquido saturado",line=dict(color=BLUE,width=2.5)))
    fig_hs.add_trace(go.Scatter(x=df["sg"],y=df["hg"],name="Vapor saturado",line=dict(color=RED,width=2.5)))
    if state:
        fig_hs.add_trace(go.Scatter(x=[state["s"]],y=[state["h"]],mode="markers",
                                    name="Estado",marker=dict(size=12,color=ORANGE,symbol="diamond")))
    fig_hs.update_layout(title="Diagrama h-s (base Mollier)",xaxis_title="s [kJ/kg·K]",
                         yaxis_title="h [kJ/kg]",height=475,
                         margin=dict(l=20,r=20,t=55,b=35))
    q3,q4 = st.columns(2,gap="small")
    with q3: st.plotly_chart(fig_ts,use_container_width=True,config={"displaylogo":False})
    with q4: st.plotly_chart(fig_hs,use_container_width=True,config={"displaylogo":False})

    st.caption(
        "V0.1 muestra el domo de saturación y el estado calculado. "
        "En versiones posteriores agregaremos isolíneas y trayectorias de procesos."
    )

with tabs[2]:
    st.markdown("### Tablas calculadas de agua")
    table_kind = st.radio(
        "Tipo",
        ["Saturación por temperatura", "Saturación por presión", "Tabla a presión constante"],
        horizontal=True
    )

    if table_kind == "Saturación por temperatura":
        with st.form("th_satT"):
            c1,c2,c3,c4 = st.columns(4)
            t1 = c1.number_input("T mín [°C]",value=0.01,format="%.6g")
            t2 = c2.number_input("T máx [°C]",value=300.0,format="%.6g")
            nn = c3.number_input("N° filas",min_value=2,max_value=200,value=31,step=1)
            goT = c4.form_submit_button("Generar tabla",use_container_width=True)
        if goT:
            try:
                st.session_state.th_table_df = sat_table_T_cached(float(t1),float(t2),int(nn))
            except Exception as exc:
                st.error(str(exc))
        if "th_table_df" in st.session_state:
            st.dataframe(st.session_state.th_table_df,use_container_width=True,hide_index=True)

    elif table_kind == "Saturación por presión":
        with st.form("th_satP"):
            c1,c2,c3,c4,c5 = st.columns(5)
            p1 = c1.number_input("P mín [kPa]",value=1.0,format="%.6g")
            p2 = c2.number_input("P máx [kPa]",value=10000.0,format="%.6g")
            nn = c3.number_input("N° filas",min_value=2,max_value=200,value=31,step=1)
            scale = c4.selectbox("Espaciado",["Logarítmico","Lineal"])
            goP = c5.form_submit_button("Generar tabla",use_container_width=True)
        if goP:
            try:
                st.session_state.th_table_df = sat_table_P_cached(
                    float(p1),float(p2),int(nn),scale=="Logarítmico"
                )
            except Exception as exc:
                st.error(str(exc))
        if "th_table_df" in st.session_state:
            st.dataframe(st.session_state.th_table_df,use_container_width=True,hide_index=True)

    else:
        with st.form("th_constP"):
            c1,c2,c3,c4,c5 = st.columns(5)
            pfix = c1.number_input("P [kPa]",value=500.0,format="%.6g")
            t1 = c2.number_input("T mín [°C]",value=50.0,format="%.6g")
            t2 = c3.number_input("T máx [°C]",value=500.0,format="%.6g")
            nn = c4.number_input("N° filas",min_value=2,max_value=200,value=31,step=1)
            goPT = c5.form_submit_button("Generar tabla",use_container_width=True)
        if goPT:
            try:
                st.session_state.th_table_df = pt_table_cached(float(pfix),float(t1),float(t2),int(nn))
            except Exception as exc:
                st.error(str(exc))
        if "th_table_df" in st.session_state:
            st.dataframe(st.session_state.th_table_df,use_container_width=True,hide_index=True)

    if "th_table_df" in st.session_state:
        csv = st.session_state.th_table_df.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar CSV",csv,"tabla_agua_mechlab.csv","text/csv")

with tabs[3]:
    st.markdown("### Relaciones fundamentales")
    st.markdown("Para una mezcla saturada líquido-vapor:")
    st.latex(r"y=y_f+x\,y_{fg}")
    st.latex(r"y_{fg}=y_g-y_f")
    st.latex(r"x=\frac{y-y_f}{y_g-y_f}")
    st.markdown(r"donde \(y\) puede representar \(v\), \(u\), \(h\) o \(s\).")
    st.markdown("### Identificación del estado")
    st.markdown(r"""
Para una presión \(P<P_c\), se compara la temperatura del estado con \(T_{sat}(P)\):

\[
T<T_{sat}\Rightarrow \text{líquido comprimido}
\]

\[
T=T_{sat}\Rightarrow \text{estado de saturación}
\]

\[
T>T_{sat}\Rightarrow \text{vapor sobrecalentado}
\]

Dentro del domo se requiere la calidad \(x\) u otra propiedad independiente para fijar el estado.
""")

with tabs[4]:
    st.markdown("### Tutorial de uso")
    st.markdown(
        "Esta pestaña está pensada para aprender a usar el visor **sin convertirlo en una calculadora ciega**. "
        "La secuencia correcta es: datos conocidos → identificación de región → propiedades → interpretación."
    )

    st.markdown('<div class="guide-step"><b>Paso 1 · Identifica qué datos conoces</b><br>'
                'Selecciona el par de propiedades de entrada. Por ejemplo, si conoces presión y temperatura, '
                'usa <b>P–T</b>. Si el estado está dentro del domo y conoces la calidad, usa <b>P–x</b> o <b>T–x</b>.'
                '</div>', unsafe_allow_html=True)

    st.markdown('<div class="guide-step"><b>Paso 2 · Usa presión absoluta</b><br>'
                'Las propiedades termodinámicas se calculan con presión absoluta. Si tu dato es manométrico, '
                'debes convertirlo antes de ingresarlo.'
                '</div>', unsafe_allow_html=True)

    st.markdown('<div class="guide-step"><b>Paso 3 · Calcula y mira primero el estado</b><br>'
                'Antes de usar h, u, s o v, revisa si el agua está como líquido comprimido, líquido saturado, '
                'mezcla líquido–vapor, vapor saturado, vapor sobrecalentado o fluido supercrítico.'
                '</div>', unsafe_allow_html=True)

    st.markdown('<div class="guide-step"><b>Paso 4 · Ubica el punto en los diagramas</b><br>'
                'Los diagramas T–v, P–v, T–s y h–s muestran el mismo estado desde distintas parejas de propiedades. '
                'El domo delimita la región de mezcla saturada.'
                '</div>', unsafe_allow_html=True)

    st.markdown('<div class="guide-step"><b>Paso 5 · Si hay mezcla, interpreta la calidad</b><br>'
                'La calidad x representa la fracción másica de vapor. x = 0 es líquido saturado y x = 1 es vapor saturado.'
                '</div>', unsafe_allow_html=True)

    st.latex(r"x=\frac{m_g}{m_f+m_g}")
    st.latex(r"y=y_f+x\,y_{fg}")

    st.markdown("### Ejemplos rápidos")
    ex1, ex2, ex3 = st.columns(3)
    with ex1:
        st.markdown("**Ejemplo A · Vapor sobrecalentado**")
        st.code("P = 500 kPa\nT = 250 °C", language="text")
        st.caption("Selecciona P–T. La aplicación debe identificar vapor sobrecalentado.")
    with ex2:
        st.markdown("**Ejemplo B · Mezcla saturada**")
        st.code("T = 100 °C\nx = 0.50", language="text")
        st.caption("Selecciona T–x. Obtendrás propiedades intermedias entre f y g.")
    with ex3:
        st.markdown("**Ejemplo C · Saturación indeterminada**")
        st.code("P ≈ 101.325 kPa\nT ≈ 100 °C", language="text")
        st.caption("P y T sobre saturación no bastan para conocer x.")

    st.markdown("### Cómo leer las letras")
    st.markdown(
        "**f** = líquido saturado · **g** = vapor saturado · **fg** = diferencia entre vapor y líquido · "
        "**x** = calidad · **v** = volumen específico · **u** = energía interna · "
        "**h** = entalpía · **s** = entropía."
    )

    st.markdown("### Qué no debe hacerse")
    st.warning(
        "No uses una propiedad calculada sin verificar antes la región. "
        "Tampoco interpretes la calidad fuera de la región bifásica: allí x no es una propiedad aplicable."
    )

    st.markdown("### Objetivo pedagógico")
    st.info(
        "El visor busca conectar tres formas de representar el mismo problema: "
        "la identificación del estado, las propiedades numéricas y su posición en los diagramas."
    )

st.divider()
st.markdown(
    "**GG DIMEC · MechLab**  |  Tecnología aplicada a la enseñanza y análisis de Ingeniería Mecánica"
)
st.caption(
    "Propiedades calculadas mediante IAPWS-IF97. "
    "Uso pedagógico y de análisis preliminar; verifique requisitos normativos y de diseño cuando corresponda."
)
