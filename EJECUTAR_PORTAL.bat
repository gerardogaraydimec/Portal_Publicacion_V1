@echo off
setlocal
cd /d "%~dp0"

echo ===============================================
echo   PD-2026-0011 - Iniciando Portal MechLab
echo ===============================================
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m streamlit run streamlit_app.py
    goto :fin
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -m streamlit run streamlit_app.py
    goto :fin
)

where python >nul 2>nul
if %errorlevel%==0 (
    python -m streamlit run streamlit_app.py
    goto :fin
)

echo.
echo ERROR: No se encontro Python ni el entorno .venv.
echo Abre VS Code y revisa la instalacion de Python.

:fin
echo.
pause
endlocal
