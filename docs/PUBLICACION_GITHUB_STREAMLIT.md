# Guía de publicación — GitHub + Streamlit Community Cloud

## 1. Repositorio GitHub

Nombre sugerido:
`ggdimec-herramientas-pedagogicas`

Para máxima difusión, usar repositorio público.

Desde Visual Studio Code:
1. Abrir esta carpeta como proyecto.
2. Source Control → Initialize Repository, si todavía no existe Git.
3. Commit inicial: `Publicación inicial portal pedagógico`.
4. Publicar el repositorio en GitHub o asociarlo al remoto existente.
5. Push de la rama `main`.

No subir `.venv`; está excluido mediante `.gitignore`.

## 2. Probar antes de publicar

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Validar:
- Inicio.
- Mohr 2D.
- Mohr 3D.
- Navegación superior.
- Logo e icono.

## 3. Streamlit Community Cloud

1. Ingresar a `share.streamlit.io` usando GitHub.
2. Conectar/autorizAR la cuenta GitHub si es la primera vez.
3. `Create app`.
4. Seleccionar el repositorio.
5. Branch: `main`.
6. Main file path: `streamlit_app.py`.
7. Elegir subdominio público, por ejemplo:
   `ggdimec-ingenieria`
   o
   `ggdimec-herramientas`
8. `Deploy`.

La URL final tendrá la forma:
`https://<subdominio>.streamlit.app`

## 4. Actualizaciones futuras

El flujo normal será:

VS Code → modificar → probar localmente → commit → push a GitHub → Streamlit actualiza la app.

## 5. Nueva herramienta futura

1. Crear su módulo en `modules/`.
2. Crear su página en `pages/`.
3. Registrar la página con `st.Page(...)` en `streamlit_app.py`.
4. Probar localmente.
5. Commit + push.

No es necesario crear otra web ni otra cuenta Streamlit.
