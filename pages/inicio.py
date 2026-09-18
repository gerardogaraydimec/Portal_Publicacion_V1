from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / "assets" / "logo_card.png"

st.markdown(
    """
    <style>
    .block-container {max-width: 1180px; padding-top: 1.2rem;}
    .home-card {
        border: 1px solid #ececec;
        border-radius: 14px;
        padding: 1.05rem 1.15rem;
        background: #ffffff;
        min-height: 180px;
    }
    .home-kicker {color:#f28e1c;font-weight:700;letter-spacing:.02em;}
    </style>
    """,
    unsafe_allow_html=True,
)

c_logo, c_title = st.columns([1.1, 3.6], vertical_alignment="center")
with c_logo:
    if LOGO.exists():
        st.image(str(LOGO), use_container_width=True)
with c_title:
    st.markdown('<div class="home-kicker">PD-2026-0011</div>', unsafe_allow_html=True)
    st.title("Herramientas Pedagógicas de Ingeniería Mecánica")
    st.write(
        "Aplicaciones interactivas desarrolladas en Python para apoyar el estudio, "
        "la visualización y la comprensión de conceptos de ingeniería mecánica."
    )

st.divider()
st.subheader("Herramientas disponibles")

c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown(
        """
        <div class="home-card">
        <h3>Círculo de Mohr 2D</h3>
        <p>Transformación plana de esfuerzos, tensiones principales, corte máximo y giro del elemento.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/mohr_2d.py", label="Abrir herramienta 2D", icon="↗️")

with c2:
    st.markdown(
        """
        <div class="home-card">
        <h3>Círculo de Mohr 3D</h3>
        <p>Tensor tridimensional, tensiones principales, visualización interactiva 3D y plano activo.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/mohr_3d.py", label="Abrir herramienta 3D", icon="↗️")

st.divider()
st.subheader("Propósito")
st.write(
    "Este portal se irá ampliando progresivamente con nuevas herramientas, códigos y recursos pedagógicos. "
    "El objetivo es disponer de material técnico accesible desde cualquier navegador, sin instalar ejecutables."
)

st.caption("GG DIMEC · Tecnología aplicada a formación e ingeniería.")
