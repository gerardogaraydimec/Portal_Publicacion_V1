from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st
from modules.ui_brand import render_app_header

from modules.mohr2d import calcular_estado, crear_figura

ROOT = Path(__file__).resolve().parent.parent


st.markdown(
    """
    <style>
    :root {--gg-orange:#f28e1c; --gg-orange-dark:#db7810;}
    div[data-testid="stFormSubmitButton"] button {background:#f28e1c !important;border-color:#f28e1c !important;color:white !important;}
    div[data-testid="stFormSubmitButton"] button:hover {background:#db7810 !important;border-color:#db7810 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Estado persistente
# ---------------------------------------------------------------------------
DEFAULTS = {
    "m2_sx_base": 200.0,
    "m2_sy_base": -100.0,
    "m2_txy_base": 150.0,
    "m2_beta_deg": 30.0,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------------
render_app_header(
    title="Círculo de Mohr 2D",
    subtitle="Transformación plana de esfuerzos · tensiones principales · esfuerzo cortante máximo · orientación del elemento.",
    section="RESISTENCIA DE MATERIALES",
    logo_width=190,
)

# ---------------------------------------------------------------------------
# Datos base: solo se aplican cuando se presiona el botón
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Estado plano de esfuerzos")
    st.caption(
        "Los valores de σx, σy y τxy se actualizan juntos para evitar "
        "recálculos innecesarios."
    )

    with st.form("form_estado_base", clear_on_submit=False):
        sx_input = st.number_input(
            "σx",
            min_value=-10000.0,
            max_value=10000.0,
            value=float(st.session_state.m2_sx_base),
            step=10.0,
            format="%.1f",
        )
        sy_input = st.number_input(
            "σy",
            min_value=-10000.0,
            max_value=10000.0,
            value=float(st.session_state.m2_sy_base),
            step=10.0,
            format="%.1f",
        )
        txy_input = st.number_input(
            "τxy",
            min_value=-10000.0,
            max_value=10000.0,
            value=float(st.session_state.m2_txy_base),
            step=10.0,
            format="%.1f",
        )

        aplicar = st.form_submit_button(
            "Actualizar estado",
            use_container_width=True,
            type="primary",
        )

    if aplicar:
        st.session_state.m2_sx_base = float(sx_input)
        st.session_state.m2_sy_base = float(sy_input)
        st.session_state.m2_txy_base = float(txy_input)

    st.divider()
    st.caption(
        "Después de actualizar el estado base, use β en la página principal "
        "para explorar la transformación."
    )

# ---------------------------------------------------------------------------
# Resultados que dependen solo del estado base
# ---------------------------------------------------------------------------
d_base = calcular_estado(
    st.session_state.m2_sx_base,
    st.session_state.m2_sy_base,
    st.session_state.m2_txy_base,
    st.session_state.m2_beta_deg,
)

st.subheader("Resultados del estado base")
r1, r2, r3, r4 = st.columns(4)
r1.metric("σ₁", f"{d_base['s1']:.2f}")
r2.metric("σ₂", f"{d_base['s2']:.2f}")
r3.metric("τmáx", f"{d_base['radio']:.2f}")
r4.metric("θp", f"{d_base['theta_p_deg']:.2f}°")

st.divider()

# ---------------------------------------------------------------------------
# Fragmento interactivo:
# al mover β se vuelve a ejecutar solo esta sección.
# ---------------------------------------------------------------------------
@st.fragment
def panel_rotacion():
    st.subheader("Transformación del elemento")

    beta_deg = st.slider(
        "β — giro físico del elemento [°]",
        min_value=0.0,
        max_value=180.0,
        value=float(st.session_state.m2_beta_deg),
        step=1.0,
        key="m2_beta_slider",
        help="En el círculo de Mohr el giro correspondiente es 2β.",
    )

    st.session_state.m2_beta_deg = float(beta_deg)

    d = calcular_estado(
        st.session_state.m2_sx_base,
        st.session_state.m2_sy_base,
        st.session_state.m2_txy_base,
        beta_deg,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("β", f"{d['beta_deg']:.2f}°")
    c2.metric("2β", f"{d['dos_beta']:.2f}°")
    c3.metric("σβ", f"{d['sigma_beta']:.2f}")
    c4.metric("τβ", f"{d['tau_beta']:.2f}")

    fig = crear_figura(
        d,
        logo_path=LOGO_PATH if LOGO_PATH.exists() else None,
    )
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    with st.expander("Ver resultados completos", expanded=False):
        st.write(f"**Esfuerzo promedio:** {d['prom']:.3f}")
        st.write(f"**Radio del círculo:** {d['radio']:.3f}")
        st.write(f"**σβ perpendicular:** {d['sigma_beta_ort']:.3f}")
        st.write(f"**Polo:** P = ({d['px']:.3f}, {d['py']:.3f})")


panel_rotacion()

with st.expander("Ecuaciones utilizadas", expanded=False):
    st.latex(r"\Delta=\frac{\sigma_x-\sigma_y}{2}")
    st.latex(r"\sigma_{prom}=\frac{\sigma_x+\sigma_y}{2}")
    st.latex(r"R=\sqrt{\Delta^2+\tau_{xy}^2}")
    st.latex(
        r"\sigma_\beta=\sigma_{prom}+\Delta\cos(2\beta)+\tau_{xy}\sin(2\beta)"
    )
    st.latex(
        r"\tau_\beta=-\Delta\sin(2\beta)+\tau_{xy}\cos(2\beta)"
    )

st.divider()
st.caption(
    "GG DIMEC · Herramienta pedagógica desarrollada en Python + Streamlit."
)
