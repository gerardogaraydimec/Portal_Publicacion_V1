Set-Location $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    & $venvPython -m streamlit run streamlit_app.py
    exit $LASTEXITCODE
}

if (Get-Command py -ErrorAction SilentlyContinue) {
    py -m streamlit run streamlit_app.py
    exit $LASTEXITCODE
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    python -m streamlit run streamlit_app.py
    exit $LASTEXITCODE
}

Write-Error "No se encontró Python ni el entorno .venv."
exit 1
