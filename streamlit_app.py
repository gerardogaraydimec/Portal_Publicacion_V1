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
    title="Vibraciones 1-GDL",
    icon="〰️",
    url_path="vibraciones-1gdl",
)

pg = st.navigation(
    {
        "Portal": [inicio],
        "Resistencia de Materiales": [mohr2d, mohr3d],
        "Vibraciones y Dinámica": [vibraciones1gdl],
    },
    position="top",
)
pg.run()
