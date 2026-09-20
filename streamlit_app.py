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


vigas_cortante_momento = st.Page(
    "pages/vigas_cortante_momento.py",
    title="Cortante y Momento",
    icon="📐",
    url_path="vigas-cortante-momento",
)

biblioteca_perfiles = st.Page(
    "pages/biblioteca_perfiles_estructurales.py",
    title="Perfiles estructurales",
    icon="🏗️",
    url_path="perfiles-estructurales",
)

fluidos_continuidad_bernoulli = st.Page(
    "pages/fluidos_continuidad_bernoulli.py",
    title="Continuidad y Bernoulli",
    icon="💧",
    url_path="fluidos-continuidad-bernoulli",
)

fluidos_reales_reynolds_perdidas = st.Page(
    "pages/fluidos_reales_reynolds_perdidas.py",
    title="Flujo real en tuberías",
    icon="🌊",
    url_path="fluidos-reales-reynolds-perdidas",
)

bombas_curvas_sistema = st.Page(
    "pages/bombas_curvas_sistema.py",
    title="Bombas y Curvas de Sistema",
    icon="⚙️",
    url_path="bombas-curvas-sistema",
)

ajustes_tolerancias_iso = st.Page(
    "pages/ajustes_tolerancias_iso.py",
    title="Ajustes y Tolerancias ISO",
    icon="📏",
    url_path="ajustes-tolerancias-iso",
)

medicion_incertidumbre = st.Page(
    "pages/medicion_incertidumbre.py",
    title="Medición e Incertidumbre",
    icon="🔬",
    url_path="medicion-incertidumbre",
)

tolerancias_geometricas_iso_gps = st.Page(
    "pages/tolerancias_geometricas_iso_gps.py",
    title="Tolerancias Geométricas ISO GPS",
    icon="📐",
    url_path="tolerancias-geometricas-iso-gps",
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
        "Resistencia y Estructuras": [
            mohr2d,
            mohr3d,
            vigas_cortante_momento,
            biblioteca_perfiles,
        ],
        "Máquinas y Componentes": [
            von_mises_lab,
        ],
        "Dinámica y Vibraciones": [
            vibraciones1gdl,
            vibracion_forzada1gdl,
        ],
        "Fluidos y Energía": [
            fluidos_continuidad_bernoulli,
            fluidos_reales_reynolds_perdidas,
            bombas_curvas_sistema,
            termodinamica_agua,
            ciclos_termodinamicos,
        ],
        "Metrología y Calidad": [
            ajustes_tolerancias_iso,
            medicion_incertidumbre,
            tolerancias_geometricas_iso_gps,
        ],
    },
    position="top",
)
pg.run()
