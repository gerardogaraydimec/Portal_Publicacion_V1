# PD-2026-0011 — Herramientas Pedagógicas de Ingeniería Mecánica

Portal público desarrollado en Python + Streamlit.

## Herramientas incluidas

- Círculo de Mohr 2D
- Círculo de Mohr 3D

## Ejecución local

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

## Estructura

- `streamlit_app.py`: entrada y navegación del portal.
- `pages/`: páginas visibles.
- `modules/`: cálculo y gráficos reutilizables.
- `assets/`: identidad gráfica.
- `docs/`: documentación de publicación y mantenimiento.

## Publicación

La aplicación está preparada para Streamlit Community Cloud usando `streamlit_app.py` como entrypoint.
