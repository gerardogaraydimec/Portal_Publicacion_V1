from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from modules.vibraciones1gdl import calcular_respuesta, fmt_complex

ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / "assets" / "logo_card.png"

st.markdown(
    """
    <style>
      .block-container {padding-top: 1rem; padding-bottom: 1.4rem; max-width: 1550px;}
      div[data-testid="stMetric"] {background:#fff7ef; border:1px solid #f2dfcc; padding:0.55rem 0.75rem; border-radius:0.75rem;}
      .regime-pill {display:inline-block; padding:.38rem .72rem; border-radius:.6rem; font-weight:700; border:1px solid #e1e1e1; background:#f7f7f7;}
      .tech-card {border:1px solid #e4e4e4; border-radius:.8rem; padding:.8rem 1rem; background:#fff;}
      .small-note {font-size:.89rem; color:#555;}
      .stButton>button {border-radius:.55rem; font-weight:650;}
      @media (max-width: 700px) {
        .block-container {padding-left:.75rem; padding-right:.75rem;}
      }
    </style>
    """,
    unsafe_allow_html=True,
)

DEFAULTS = {
    "vib1_m": 1.0,
    "vib1_k": 100.0,
    "vib1_c": 0.0,
    "vib1_x0": 0.10,
    "vib1_v0": 0.0,
    "vib1_tmax": 10.0,
}
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)


def resetear():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value


h1, h2 = st.columns([5.5, 1.15], vertical_alignment="center")
with h1:
    st.title("Vibraciones libres de un sistema de 1 GDL")
    st.caption("Sistema masa–resorte–amortiguador · respuesta temporal · plano de fase · solución característica")
with h2:
    if LOGO.exists():
        st.image(str(LOGO), use_container_width=True)

with st.container(border=True):
    st.markdown("**Parámetros del sistema y condiciones iniciales**")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.number_input(
            "Masa  m  [kg]", min_value=1.0e-6, step=0.1, format="%.6g", key="vib1_m",
            help="Sin límite superior prefijado. Ingresa directamente la masa equivalente del sistema."
        )
    with c2:
        st.number_input(
            "Rigidez  k  [N/m]", min_value=1.0e-6, step=100.0, format="%.6g", key="vib1_k",
            help="Sin límite superior prefijado. Acepta rigideces de sistemas de laboratorio y maquinaria industrial."
        )
    with c3:
        st.number_input(
            "Amortiguamiento  c  [N·s/m]", min_value=0.0, step=10.0, format="%.6g", key="vib1_c",
            help="Coeficiente viscoso equivalente. No se impone límite superior."
        )
    with c4:
        st.number_input(
            "Desplazamiento  x₀  [m]", step=0.001, format="%.6g", key="vib1_x0",
            help="Condición inicial. Puede ingresarse cualquier valor compatible con el modelo lineal."
        )
    with c5:
        st.number_input(
            "Velocidad  v₀  [m/s]", step=0.1, format="%.6g", key="vib1_v0",
            help="Condición inicial de velocidad, sin rango artificial prefijado."
        )
    with c6:
        st.number_input(
            "Tiempo máximo  [s]", min_value=1.0e-4, step=1.0, format="%.6g", key="vib1_tmax",
            help="Ventana temporal de cálculo. Para frecuencias altas conviene usar tiempos menores para visualizar correctamente los ciclos."
        )
    b1, b2 = st.columns([1, 5])
    with b1:
        st.button("Restablecer", on_click=resetear, use_container_width=True)

r = calcular_respuesta(
    st.session_state.vib1_m,
    st.session_state.vib1_k,
    st.session_state.vib1_c,
    st.session_state.vib1_x0,
    st.session_state.vib1_v0,
    st.session_state.vib1_tmax,
)

fn_hz = r.wn / (2.0 * np.pi)
natural_rpm = 60.0 * fn_hz

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Frecuencia natural ωₙ", f"{r.wn:.4g} rad/s")
m2.metric("Frecuencia natural fₙ", f"{fn_hz:.4g} Hz")
m3.metric("Equivalente Nₙ", f"{natural_rpm:.4g} rpm")
m4.metric("Amortiguamiento crítico ccr", f"{r.ccr:.4g} N·s/m")
m5.metric("Razón de amortiguamiento ζ", f"{r.zeta:.5g}")
m6.metric("Frecuencia amortiguada ωd", "—" if r.wd is None else f"{r.wd:.4g} rad/s")

cycles_shown = fn_hz * float(st.session_state.vib1_tmax)
points_per_cycle = (len(r.t) / cycles_shown) if cycles_shown > 0 else float("inf")
if cycles_shown > 0 and points_per_cycle < 20:
    st.warning(
        f"La ventana seleccionada contiene aproximadamente {cycles_shown:.0f} ciclos y la gráfica dispone de "
        f"{points_per_cycle:.1f} puntos por ciclo. Para inspección visual fina, reduce el tiempo máximo. "
        "El cálculo analítico sigue siendo válido; la advertencia se refiere a la resolución de la visualización."
    )

regime_bg = {
    "Sistema no amortiguado": "#eef3f5",
    "Subamortiguado": "#edf7ff",
    "Amortiguación crítica": "#eef8ee",
    "Sobreamortiguado": "#fff0e8",
}.get(r.regime, "#f7f7f7")
st.markdown(
    f'<span class="regime-pill" style="background:{regime_bg}">{r.regime}</span>',
    unsafe_allow_html=True,
)

# Respuesta temporal: tres gráficos compactos y coordinados.
fig_t = make_subplots(
    rows=3,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.075,
    subplot_titles=("Desplazamiento x(t)", "Velocidad v(t)", "Aceleración a(t)"),
)
fig_t.add_trace(go.Scatter(x=r.t, y=r.x, mode="lines", name="x(t)", line=dict(width=2, color="#1E88E5")), row=1, col=1)
fig_t.add_trace(go.Scatter(x=r.t, y=r.v, mode="lines", name="v(t)", line=dict(width=2, color="#E53935")), row=2, col=1)
fig_t.add_trace(go.Scatter(x=r.t, y=r.a, mode="lines", name="a(t)", line=dict(width=2, color="#43A047")), row=3, col=1)
fig_t.update_xaxes(title_text="Tiempo [s]", row=3, col=1, showgrid=True, gridcolor="#eeeeee")
fig_t.update_xaxes(showgrid=True, gridcolor="#eeeeee", row=1, col=1)
fig_t.update_xaxes(showgrid=True, gridcolor="#eeeeee", row=2, col=1)
fig_t.update_yaxes(title_text="x [m]", row=1, col=1, showgrid=True, gridcolor="#eeeeee")
fig_t.update_yaxes(title_text="v [m/s]", row=2, col=1, showgrid=True, gridcolor="#eeeeee")
fig_t.update_yaxes(title_text="a [m/s²]", row=3, col=1, showgrid=True, gridcolor="#eeeeee")
fig_t.update_layout(
    height=670,
    margin=dict(l=35, r=10, t=50, b=25),
    showlegend=False,
    hovermode="x unified",
    template="plotly_white",
    uirevision="vibraciones-tiempo",
)

fig_p = go.Figure()
fig_p.add_trace(go.Scatter(
    x=r.x,
    y=r.v,
    mode="lines",
    line=dict(width=2.5, color="#8E24AA"),
    name="Trayectoria",
    hovertemplate="x=%{x:.5f} m<br>v=%{y:.5f} m/s<extra></extra>",
))
fig_p.add_trace(go.Scatter(
    x=[r.x[0]], y=[r.v[0]], mode="markers", marker=dict(size=9, color="#f28e1c"), name="Estado inicial",
    hovertemplate="Estado inicial<br>x=%{x:.5f} m<br>v=%{y:.5f} m/s<extra></extra>",
))
fig_p.update_layout(
    title="Plano de fase (x vs v)",
    xaxis_title="Posición x [m]",
    yaxis_title="Velocidad v [m/s]",
    height=520,
    margin=dict(l=35, r=15, t=55, b=40),
    template="plotly_white",
    legend=dict(orientation="h", y=1.02, x=0.5, xanchor="center", yanchor="bottom"),
    uirevision="vibraciones-fase",
)

left, right = st.columns([1.08, 0.92], gap="medium")
with left:
    st.plotly_chart(fig_t, use_container_width=True, config={"displaylogo": False, "scrollZoom": True})
with right:
    st.plotly_chart(fig_p, use_container_width=True, config={"displaylogo": False, "scrollZoom": True})
    with st.container(border=True):
        st.markdown("**Solución característica**")
        st.latex(r"m\ddot{x}+c\dot{x}+kx=0")
        s1, s2 = st.columns(2)
        s1.markdown(f"$s_1 =$ `{fmt_complex(r.s1)}`")
        s2.markdown(f"$s_2 =$ `{fmt_complex(r.s2)}`")
        c1, c2 = st.columns(2)
        c1.markdown(f"$C_1 =$ `{fmt_complex(r.c1)}`")
        c2.markdown(f"$C_2 =$ `{fmt_complex(r.c2)}`")

with st.expander("Ecuaciones y criterio de régimen"):
    st.markdown(
        """
        Para el sistema libre lineal:
        """
    )
    st.latex(r"m\ddot{x}+c\dot{x}+kx=0")
    st.latex(r"\omega_n=\sqrt{\frac{k}{m}},\qquad c_{cr}=2\sqrt{km},\qquad \zeta=\frac{c}{c_{cr}}")
    st.markdown(
        "- **No amortiguado:** $c=0$\n"
        "- **Subamortiguado:** $0<\\zeta<1$\n"
        "- **Críticamente amortiguado:** $\\zeta=1$\n"
        "- **Sobreamortiguado:** $\\zeta>1$"
    )
    if r.regime == "Amortiguación crítica":
        st.latex(r"x(t)=\left[C_1+C_2t\right]e^{-\omega_n t}")
    elif r.regime == "Subamortiguado":
        st.latex(r"x(t)=e^{-\zeta\omega_n t}\left[A\cos(\omega_dt)+B\sin(\omega_dt)\right]")
        st.latex(r"\omega_d=\omega_n\sqrt{1-\zeta^2}")
    elif r.regime == "Sistema no amortiguado":
        st.latex(r"x(t)=x_0\cos(\omega_n t)+\frac{v_0}{\omega_n}\sin(\omega_n t)")
    else:
        st.latex(r"x(t)=C_1e^{s_1t}+C_2e^{s_2t}")

with st.expander("Cómo usar esta herramienta"):
    st.markdown(
        """
        1. Ajusta **m**, **k** y **c** para definir el sistema masa–resorte–amortiguador. Los campos no tienen límites superiores artificiales; puedes escribir directamente valores de escala industrial.
        2. Define las condiciones iniciales **x₀** y **v₀**.
        3. Modifica el tiempo máximo para observar la evolución de la respuesta. En máquinas de alta frecuencia usa ventanas temporales más cortas.
        4. Compara la respuesta temporal con el **plano de fase**, las raíces de la ecuación característica y las frecuencias natural y amortiguada.
        5. La conversión de $f_n$ a rpm facilita comparar la frecuencia propia con velocidades de giro de maquinaria.
        6. Prueba valores de amortiguamiento cercanos a $c_{cr}$ para distinguir los regímenes subamortiguado, crítico y sobreamortiguado.
        """
    )
    st.caption(
        "Esta versión modela vibración libre lineal de un sistema equivalente de un grado de libertad. "
        "Es útil para evaluación modal preliminar, pero todavía no incluye excitación armónica, desbalance, transmisibilidad ni respuesta forzada."
    )
