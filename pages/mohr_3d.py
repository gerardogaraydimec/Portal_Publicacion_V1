from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from PIL import Image
import streamlit as st

from modules.plotly3d import crear_figura_3d_interactiva
from modules.plotlymohr import crear_figura_mohr_interactiva

from modules.mohr3d import recopilar_datos

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "assets" / "logo_card.png"

st.markdown(
    """
    <style>
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .block-container {
        max-width: 100%;
        padding-top: 0.15rem;
        padding-bottom: 0.25rem;
        padding-left: 0.65rem;
        padding-right: 0.65rem;
    }
    h1 {
        font-size: 1.18rem !important;
        margin: 0 0 0.12rem 0 !important;
        line-height: 1.05 !important;
    }
    div[data-testid="stVerticalBlock"] {gap: 0.15rem;}
    div[data-testid="stHorizontalBlock"] {gap: 0.35rem;}
    div[data-testid="stNumberInput"] label,
    div[data-testid="stSlider"] label {
        font-size: 0.72rem !important;
        margin-bottom: -0.2rem !important;
    }
    div[data-testid="stNumberInput"] input {
        min-height: 1.65rem !important;
        height: 1.65rem !important;
        font-size: 0.76rem !important;
        padding-top: 0.10rem !important;
        padding-bottom: 0.10rem !important;
    }
    div[data-baseweb="slider"] {
        margin-top: -0.45rem !important;
        margin-bottom: -0.30rem !important;
    }
    div[data-testid="stFormSubmitButton"] button {
        min-height: 1.75rem;
        height: 1.75rem;
        font-size: 0.75rem;
        padding: 0.10rem 0.50rem;
    }
    div[data-testid="stTabs"] button {
        padding-top: 0.20rem !important;
        padding-bottom: 0.20rem !important;
        font-size: 0.80rem !important;
    }
    .mini-note {font-size: 0.68rem; color: #666; margin-top: -0.10rem; margin-bottom: 0.05rem;}
    .logo-box {background: #fff7ef; border: none; border-radius: 0.55rem; padding: 0; overflow: hidden;}
    .eq-note {font-size: 0.75rem; color: #333; line-height: 1.35;}

    /* Identidad GG DIMEC */
    :root {
        --gg-orange: #f28e1c;
        --gg-orange-dark: #db7810;
    }

    /* Botón Aplicar tensor */
    div[data-testid="stFormSubmitButton"] button {
        background-color: var(--gg-orange) !important;
        border-color: var(--gg-orange) !important;
        color: white !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: var(--gg-orange-dark) !important;
        border-color: var(--gg-orange-dark) !important;
        color: white !important;
    }

    /* Slider: track activo, thumb y valor */
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: var(--gg-orange) !important;
        border-color: var(--gg-orange) !important;
    }
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div:first-child {
        background-color: var(--gg-orange) !important;
    }
    div[data-testid="stSlider"] [data-testid="stThumbValue"] {
        color: var(--gg-orange-dark) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DEFAULTS = {
    "m3_sx_base": 220.0,
    "m3_sy_base": -80.0,
    "m3_sz_base": 40.0,
    "m3_txy_base": 150.0,
    "m3_tyz_base": 90.0,
    "m3_tzx_base": -60.0,
    "m3_phi": 20.0,
    "m3_theta": 30.0,
    "m3_psi": -25.0,
    "m3_alpha_n": 25.0,
    "m3_beta_n": 20.0,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.markdown("<h1>Círculo de Mohr 3D · Herramienta compacta</h1>", unsafe_allow_html=True)
st.markdown("<div class='mini-note'>PD-2026-0011 · Portal público · Círculo de Mohr 3D</div>", unsafe_allow_html=True)

@st.fragment
def tablero():
    with st.form("m3_form_tensor_compacto", clear_on_submit=False):
        c = st.columns([1,1,1,1,1,1,0.92], gap="small")
        labels = [
            (r"$\sigma_x$", "m3_sx_base", "sx"),
            (r"$\sigma_y$", "m3_sy_base", "sy"),
            (r"$\sigma_z$", "m3_sz_base", "sz"),
            (r"$\tau_{xy}$", "m3_txy_base", "txy"),
            (r"$\tau_{yz}$", "m3_tyz_base", "tyz"),
            (r"$\tau_{zx}$", "m3_tzx_base", "tzx"),
        ]
        nuevos = {}
        for col, (label, key, name) in zip(c[:6], labels):
            with col:
                nuevos[name] = st.number_input(label, value=float(st.session_state[key]), step=10.0, format="%.1f", key=f"m3_input_{name}")
        with c[6]:
            aplicar = st.form_submit_button("Aplicar tensor", use_container_width=True, type="primary")

    if aplicar:
        st.session_state.m3_sx_base = float(nuevos["sx"])
        st.session_state.m3_sy_base = float(nuevos["sy"])
        st.session_state.m3_sz_base = float(nuevos["sz"])
        st.session_state.m3_txy_base = float(nuevos["txy"])
        st.session_state.m3_tyz_base = float(nuevos["tyz"])
        st.session_state.m3_tzx_base = float(nuevos["tzx"])

    a = st.columns(5, gap="small")
    with a[0]:
        phi = st.slider(r"$\phi_x\ [^\circ]$", -180.0, 180.0, float(st.session_state.m3_phi), 1.0, key="m3_phi_widget")
    with a[1]:
        theta = st.slider(r"$\theta_y\ [^\circ]$", -180.0, 180.0, float(st.session_state.m3_theta), 1.0, key="m3_theta_widget")
    with a[2]:
        psi = st.slider(r"$\psi_z\ [^\circ]$", -180.0, 180.0, float(st.session_state.m3_psi), 1.0, key="m3_psi_widget")
    with a[3]:
        alpha_n = st.slider(r"$\alpha_n\ [^\circ]$", -180.0, 180.0, float(st.session_state.m3_alpha_n), 1.0, key="m3_alpha_widget")
    with a[4]:
        beta_n = st.slider(r"$\beta_n\ [^\circ]$", -89.0, 89.0, float(st.session_state.m3_beta_n), 1.0, key="m3_beta_widget")

    st.session_state.m3_phi = float(phi)
    st.session_state.m3_theta = float(theta)
    st.session_state.m3_psi = float(psi)
    st.session_state.m3_alpha_n = float(alpha_n)
    st.session_state.m3_beta_n = float(beta_n)

    datos = recopilar_datos(
        st.session_state.m3_sx_base,
        st.session_state.m3_sy_base,
        st.session_state.m3_sz_base,
        st.session_state.m3_txy_base,
        st.session_state.m3_tyz_base,
        st.session_state.m3_tzx_base,
        phi, theta, psi, alpha_n, beta_n,
    )

    # Ambos gráficos son ahora interactivos y nítidos en navegador.
    g1, g2 = st.columns([1, 1], gap="small")

    with g1:
        fig_mohr = crear_figura_mohr_interactiva(datos)
        st.plotly_chart(
            fig_mohr,
            use_container_width=True,
            config={
                "displaylogo": False,
                "scrollZoom": True,
                "responsive": True,
                "doubleClick": "reset+autosize",
            },
            key="m3_mohr_interactivo",
        )

    with g2:
        fig3d = crear_figura_3d_interactiva(datos)
        st.plotly_chart(
            fig3d,
            use_container_width=True,
            config={
                "displaylogo": False,
                "scrollZoom": True,
                "responsive": True,
                "doubleClick": "reset+autosize",
                "modeBarButtonsToRemove": ["lasso3d", "select2d"],
            },
            key="m3_estado_3d_interactivo",
        )

    tcol, lcol = st.columns([5.4, 1.15], gap="small")
    sigma1, sigma2, sigma3 = datos["principal_stresses"]
    activo = datos["active_state"]
    tm = datos["tensor_rotado"]
    e = datos["rotated_states"]

    with tcol:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Resultados", "Tensor rotado", "Caras", "Ecuaciones", "Cómo usar"])

        with tab1:
            r1, r2, r3, r4 = st.columns(4)
            with r1:
                st.latex(rf"\sigma_1 = {sigma1:.2f}")
                st.latex(rf"\sigma_2 = {sigma2:.2f}")
                st.latex(rf"\sigma_3 = {sigma3:.2f}")
            with r2:
                st.latex(rf"\tau_{{max}}^{{3D}} = {datos['tau_max']:.2f}")
                st.latex(rf"\sigma_{{vm}} = {datos['von_mises']:.2f}")
                st.latex(rf"\sigma_m = {datos['mean_stress']:.2f}")
            with r3:
                st.latex(rf"J_2 = {datos['j2']:.2f}")
                st.latex(rf"\sigma_{{n^*}} = {activo['sigma_n']:.2f}")
                st.latex(rf"\tau_{{n^*}} = {activo['tau_n']:.2f}")
            with r4:
                st.latex(rf"C_{{13}} = {datos['circles'][0]['radius']:.2f}")
                st.latex(rf"C_{{12}} = {datos['circles'][1]['radius']:.2f}")
                st.latex(rf"C_{{23}} = {datos['circles'][2]['radius']:.2f}")

        with tab2:
            st.markdown("<div class='eq-note'>Tensor de esfuerzos rotado:</div>", unsafe_allow_html=True)
            st.latex(
                r"\boldsymbol{\sigma}'="
                + r"\begin{bmatrix}"
                + rf"{tm[0,0]:.2f} & {tm[0,1]:.2f} & {tm[0,2]:.2f}\\"
                + rf"{tm[1,0]:.2f} & {tm[1,1]:.2f} & {tm[1,2]:.2f}\\"
                + rf"{tm[2,0]:.2f} & {tm[2,1]:.2f} & {tm[2,2]:.2f}"
                + r"\end{bmatrix}"
            )
            st.latex(r"\mathrm{diag}(\boldsymbol{\sigma}') = [" + rf"{tm[0,0]:.2f},\ {tm[1,1]:.2f},\ {tm[2,2]:.2f}]" )

        with tab3:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.latex(rf"x':\ \sigma_n = {e[0]['sigma_n']:.2f}")
                st.latex(rf"x':\ \tau_n = {e[0]['tau_n']:.2f}")
            with c2:
                st.latex(rf"y':\ \sigma_n = {e[1]['sigma_n']:.2f}")
                st.latex(rf"y':\ \tau_n = {e[1]['tau_n']:.2f}")
            with c3:
                st.latex(rf"z':\ \sigma_n = {e[2]['sigma_n']:.2f}")
                st.latex(rf"z':\ \tau_n = {e[2]['tau_n']:.2f}")
            st.markdown("<div class='eq-note'>Plano activo en el sistema girado:</div>", unsafe_allow_html=True)
            n_local = activo["normal_local"]
            st.latex(r"\mathbf{n}^* = [" + rf"{n_local[0]:.3f},\ {n_local[1]:.3f},\ {n_local[2]:.3f}]" )

        with tab4:
            st.markdown("<div class='eq-note'>Relaciones utilizadas en la herramienta:</div>", unsafe_allow_html=True)
            st.latex(r"\mathbf{R} = R_z(\psi)\,R_y(\theta)\,R_x(\phi)")
            st.latex(r"\boldsymbol{\sigma}' = \mathbf{R}^{T}\,\boldsymbol{\sigma}\,\mathbf{R}")
            st.latex(r"\mathbf{t}^{(n)} = \boldsymbol{\sigma}\,\mathbf{n}")
            st.latex(r"\sigma_n = \mathbf{n}^T\,\boldsymbol{\sigma}\,\mathbf{n}")
            st.latex(r"\boldsymbol{\tau}^{(n)} = \mathbf{t}^{(n)} - \sigma_n\,\mathbf{n}")
            st.latex(r"\tau_n = \|\boldsymbol{\tau}^{(n)}\|")
            st.latex(r"\sigma_{vm} = \sqrt{\frac{(\sigma_x-\sigma_y)^2+(\sigma_y-\sigma_z)^2+(\sigma_z-\sigma_x)^2}{2}+3(\tau_{xy}^2+\tau_{yz}^2+\tau_{zx}^2)}")
            st.latex(r"J_2 = \frac{1}{2}\,\mathbf{s}:\mathbf{s},\quad \mathbf{s}=\boldsymbol{\sigma}-\sigma_m\mathbf{I}")

        with tab5:
            st.markdown("### Uso de la herramienta")
            u1, u2 = st.columns(2, gap="large")

            with u1:
                st.markdown("**1. Definir el tensor de esfuerzos**")
                st.markdown(
                    "Ingrese los seis componentes del estado tridimensional y presione "
                    "**Aplicar tensor**. Los valores deben utilizar una unidad consistente."
                )
                st.latex(
                    r"\boldsymbol{\sigma}="
                    r"\begin{bmatrix}"
                    r"\sigma_x & \tau_{xy} & \tau_{zx}\\"
                    r"\tau_{xy} & \sigma_y & \tau_{yz}\\"
                    r"\tau_{zx} & \tau_{yz} & \sigma_z"
                    r"\end{bmatrix}"
                )

                st.markdown("**2. Girar el sistema de referencia**")
                st.markdown(
                    r"Los controles $\phi_x$, $\theta_y$ y $\psi_z$ modifican la orientación "
                    r"del sistema $x',y',z'$. La herramienta utiliza la secuencia:"
                )
                st.latex(r"\mathbf{R}=R_z(\psi)\,R_y(\theta)\,R_x(\phi)")

                st.markdown("**3. Definir el plano activo**")
                st.markdown(
                    r"$\alpha_n$ controla el azimut y $\beta_n$ la elevación de la normal "
                    r"$\mathbf{n}^*$ del plano activo en el sistema girado."
                )

            with u2:
                st.markdown("**Lectura del Círculo de Mohr 3D**")
                st.markdown(
                    "- **C₁₃ azul:** círculo exterior entre las tensiones principales extremas.\n"
                    "- **C₁₂ verde y C₂₃ rojo:** delimitan zonas excluidas; sus interiores se muestran en blanco.\n"
                    "- **Círculos abiertos:** estados asociados a los planos globales.\n"
                    "- **Cuadrados:** estados asociados a las caras del sistema girado.\n"
                    "- **Estrella $n^*$:** estado correspondiente al plano activo.\n"
                    "- **Interacción:** rueda para zoom, arrastrar para desplazar y doble clic para restablecer."
                )

                st.markdown("**Lectura del estado de esfuerzos 3D**")
                st.markdown(
                    "- **Gris:** cubo original.\n"
                    "- **Café:** cubo rotado.\n"
                    "- **Celeste:** plano activo $n^*$.\n"
                    "- **Naranjo:** componente normal.\n"
                    "- **Negro:** componente cortante.\n"
                    "- **Morado:** vector de tracción total.\n"
                    "- Las direcciones principales σ₁, σ₂ y σ₃ se muestran como ejes auxiliares.\n"
                    "- **Interacción:** arrastrar para orbitar, rueda para zoom y doble clic para restablecer."
                )

                st.info(
                    "Los resultados principales no dependen de la orientación visual de la cámara. "
                    "Girar o acercar el modelo 3D solo cambia la perspectiva de observación."
                )

    with lcol:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_container_width=True)

    with st.expander("Ver detalle matemático adicional", expanded=False):
        st.markdown("<div class='eq-note'>Este bloque queda abajo para no ensuciar la vista principal.</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.latex(r"\sigma_m = \frac{1}{3}\,\mathrm{tr}(\boldsymbol{\sigma})")
            st.latex(r"\tau_{max}^{3D} = \frac{\sigma_1 - \sigma_3}{2}")
        with c2:
            st.latex(r"\boldsymbol{\sigma} = \begin{bmatrix} \sigma_x & \tau_{xy} & \tau_{zx} \\ \tau_{xy} & \sigma_y & \tau_{yz} \\ \tau_{zx} & \tau_{yz} & \sigma_z \end{bmatrix}")

tablero()
