from pathlib import Path
import streamlit as st
from PIL import Image

ROOT = Path(__file__).resolve().parent
ICON = ROOT / "assets" / "icon_web.png"

st.set_page_config(
    page_title="Herramientas Pedagógicas de Ingeniería",
    page_icon=Image.open(ICON) if ICON.exists() else "⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inicio = st.Page("pages/inicio.py", title="Inicio", icon="🏠", default=True)
mohr2d = st.Page("pages/mohr_2d.py", title="Mohr 2D", icon="⭕", url_path="mohr-2d")
mohr3d = st.Page("pages/mohr_3d.py", title="Mohr 3D", icon="🧊", url_path="mohr-3d")

pg = st.navigation(
    {
        "Portal": [inicio],
        "Resistencia de Materiales": [mohr2d, mohr3d],
    },
    position="top",
)
pg.run()
