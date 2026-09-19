from pathlib import Path
import streamlit as st
from PIL import Image

ROOT = Path(__file__).resolve().parent
ICON = ROOT / "assets" / "icon_web.png"

st.set_page_config(
    page_title="GG DIMEC MechLab",
    page_icon=Image.open(ICON) if ICON.exists() else "⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inicio = st.Page("pages/inicio.py", title="Inicio", icon="🏠", default=True)
mohr2d = st.Page("pages/mohr_2d.py", title="Mohr 2D", icon="⭕", url_path="mohr-2d")
mohr3d = st.Page("pages/mohr_3d.py", title="Mohr 3D", icon="🧊", url_path="mohr-3d")
vibraciones1gdl = st.Page(
    "pages/vibraciones_1gdl.py",
    title="Vibraciones libres 1-GDL",
    icon="〰️",
    url_path="vibraciones-1gdl",
)
vibracion_forzada1gdl = st.Page(
    "pages/vibracion_forzada_1gdl.py",
    title="Vibración forzada 1-GDL",
    icon="📈",
    url_path="vibracion-forzada-1gdl",
)

termodinamica_agua = st.Page(
    "pages/termodinamica_agua.py",
    title="Propiedades del agua y vapor",
    icon="💧",
    url_path="agua-vapor",
)

ciclos_termodinamicos = st.Page(
    "pages/ciclos_termodinamicos.py",
    title="Ciclos termodinámicos",
    icon="♨️",
    url_path="ciclos-termodinamicos",
)


von_mises_lab = st.Page(
    "pages/von_mises_lab.py",
    title="Von Mises Lab",
    icon="🧩",
    url_path="von-mises",
)

pg = st.navigation(
    {
        "Portal": [inicio],
        "Resistencia de Materiales": [mohr2d, mohr3d],
        "Vibraciones y Dinámica": [vibraciones1gdl, vibracion_forzada1gdl],
        "Termodinámica": [termodinamica_agua, ciclos_termodinamicos],
        "Elementos de Máquinas": [von_mises_lab],
    },
    position="top",
)
pg.run()
