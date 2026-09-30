from __future__ import annotations
from pathlib import Path
import re, shutil, sys

path=Path('streamlit_app.py')
if not path.exists():
    print('No se encontró streamlit_app.py en la carpeta actual.')
    sys.exit(1)
text=path.read_text(encoding='utf-8')
backup=path.with_suffix('.py.bak_resistencia')
if not backup.exists(): shutil.copy2(path,backup)

defs='''\n# --- Resistencia de Materiales · ampliación MechLab ---\ncolumnas_compresion = st.Page(\n    "pages/columnas_compresion.py",\n    title="Columnas · Compresión y Pandeo",\n    icon="🏗️",\n    url_path="columnas-compresion",\n)\ntorsion_resistencia = st.Page(\n    "pages/torsion.py",\n    title="Torsión · Ejes y Perfiles",\n    icon="🌀",\n    url_path="torsion",\n)\n# --- fin ampliación ---\n\n'''
changed=False
if 'columnas_compresion = st.Page(' not in text:
    m=re.search(r'(?m)^\s*pg\s*=\s*st\.navigation\s*\(',text)
    if not m:
        print('No se encontró pg = st.navigation(...). No se modificó el archivo.')
        print('Usa INTEGRACION_STREAMLIT.txt para agregar las páginas manualmente.')
        sys.exit(2)
    text=text[:m.start()]+defs+text[m.start():]; changed=True

if '"Resistencia y Estructuras"' in text or "'Resistencia y Estructuras'" in text:
    pattern=r'(["\']Resistencia y Estructuras["\']\s*:\s*\[)'
    m=re.search(pattern,text)
    if m:
        tail=text[m.end():m.end()+500]
        if 'columnas_compresion' not in tail:
            ins='\n            columnas_compresion,\n            torsion_resistencia,'
            text=text[:m.end()]+ins+text[m.end():]; changed=True
else:
    print('No se encontró la sección "Resistencia y Estructuras". Se añadieron definiciones, pero debes agregar las dos variables a tu navegación manualmente.')

if changed:
    path.write_text(text,encoding='utf-8')
    print('streamlit_app.py actualizado. Respaldo:',backup)
else:
    print('El registro ya estaba aplicado; no se realizaron cambios.')
