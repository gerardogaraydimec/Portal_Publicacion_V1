"""Lanzador de compatibilidad para PD-2026-0011 / MechLab.

Permite seguir usando:
    streamlit run app.py

aunque el archivo principal real del portal sea streamlit_app.py.
No contiene la aplicación: simplemente ejecuta el archivo principal existente.
"""
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "streamlit_app.py"

if not TARGET.exists():
    raise FileNotFoundError(
        "No se encontró 'streamlit_app.py' en la raíz del proyecto. "
        "Copia este app.py en la misma carpeta donde está streamlit_app.py."
    )

runpy.run_path(str(TARGET), run_name="__main__")
