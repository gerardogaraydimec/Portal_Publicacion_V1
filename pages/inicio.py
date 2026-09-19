from pathlib import Path
import streamlit as st
from modules.ui_brand import render_app_header

ROOT = Path(__file__).resolve().parent.parent

st.markdown(
    """
    <style>
    .block-container {max-width: 1180px; padding-top: 1.2rem;}
    .home-card {
        border: 1px solid #ececec;
        border-radius: 14px;
        padding: 1.05rem 1.15rem;
        background: #ffffff;
        min-height: 178px;
    }
    .home-kicker {color:#f28e1c;font-weight:700;letter-spacing:.02em;}
    </style>
    """,
    unsafe_allow_html=True,
)

render_app_header(
    title="GG DIMEC MechLab",
    subtitle="Herramientas interactivas para aprender, analizar y visualizar ingeniería mecánica directamente desde el navegador.",
    section="PORTAL PEDAGÓGICO",
    logo_width=190,
)

st.subheader("Herramientas disponibles")

c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown("""
        <div class="home-card"><h3>Círculo de Mohr 2D</h3>
        <p>Transformación plana de esfuerzos, tensiones principales, corte máximo y giro del elemento.</p></div>
    """, unsafe_allow_html=True)
    st.page_link("pages/mohr_2d.py", label="Abrir Mohr 2D", icon="↗️")
with c2:
    st.markdown("""
        <div class="home-card"><h3>Círculo de Mohr 3D</h3>
        <p>Tensor tridimensional, tensiones principales, visualización interactiva 3D y plano activo.</p></div>
    """, unsafe_allow_html=True)
    st.page_link("pages/mohr_3d.py", label="Abrir Mohr 3D", icon="↗️")

c3, c4 = st.columns(2, gap="large")
with c3:
    st.markdown("""
        <div class="home-card"><h3>Vibraciones libres 1-GDL</h3>
        <p>Respuesta libre masa–resorte–amortiguador, frecuencia natural, amortiguamiento, respuesta temporal y plano de fase.</p></div>
    """, unsafe_allow_html=True)
    st.page_link("pages/vibraciones_1gdl.py", label="Abrir Vibraciones libres 1-GDL", icon="↗️")
with c4:
    st.markdown("""
        <div class="home-card"><h3>Vibración forzada 1-GDL</h3>
        <p>Excitación armónica, resonancia, magnificación, fase, fuerzas, transmisibilidad y respuesta completa del sistema.</p></div>
    """, unsafe_allow_html=True)
    st.page_link("pages/vibracion_forzada_1gdl.py", label="Abrir Vibración forzada 1-GDL", icon="↗️")

c5, c6 = st.columns(2, gap="large")
with c5:
    st.markdown("""
        <div class="home-card"><h3>Propiedades del agua y vapor</h3>
        <p>Estados termodinámicos, regiones de fase, tablas calculadas y diagramas T-v, P-v, T-s y h-s para agua y vapor.</p></div>
    """, unsafe_allow_html=True)
    st.page_link("pages/termodinamica_agua.py", label="Abrir Propiedades del agua y vapor", icon="↗️")
with c6:
    st.markdown("""
        <div class="home-card"><h3>Ciclos termodinámicos</h3>
        <p>Análisis de ciclos de potencia, vapor, gas, combinados, refrigeración y configuraciones regenerativas avanzadas.</p></div>
    """, unsafe_allow_html=True)
    st.page_link("pages/ciclos_termodinamicos.py", label="Abrir Ciclos termodinámicos", icon="↗️")


c7, c8 = st.columns(2, gap="large")
with c7:
    st.markdown("""
        <div class="home-card"><h3>Von Mises Lab</h3>
        <p>Fluencia de materiales dúctiles desde el estado uniaxial hasta el espacio 3D de esfuerzos, con Mohr, Von Mises, Tresca, cilindro de fluencia y plano π.</p></div>
    """, unsafe_allow_html=True)
    st.page_link("pages/von_mises_lab.py", label="Abrir Von Mises Lab", icon="↗️")

st.divider()
st.subheader("Propósito")
st.write(
    "MechLab se ampliará progresivamente con nuevas herramientas de resistencia de materiales, dinámica, "
    "vibraciones, termodinámica, mecanismos, simulación y otras áreas de ingeniería mecánica. "
    "El objetivo es disponer de recursos técnicos accesibles desde cualquier navegador, sin instalar ejecutables."
)
st.caption("GG DIMEC · Tecnología Avanzada en Soluciones Reales.")
