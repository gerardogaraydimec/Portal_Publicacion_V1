from __future__ import annotations
from pathlib import Path
import re,shutil,sys
p=Path('streamlit_app.py')
if not p.exists(): print('No se encontró streamlit_app.py en la carpeta actual.');sys.exit(1)
text=p.read_text(encoding='utf-8');backup=p.with_suffix('.py.bak_vibraciones_expansion')
if not backup.exists(): shutil.copy2(p,backup)
defs='''\n# --- Vibraciones · ampliación MechLab ---\nvibraciones_2gdl = st.Page(\n    "pages/vibraciones_2gdl.py",\n    title="Vibraciones · 2GDL y TMD",\n    icon="🎼",\n    url_path="vibraciones-2gdl",\n)\ndiagnostico_vibracional = st.Page(\n    "pages/diagnostico_vibracional.py",\n    title="Diagnóstico vibracional · FFT y Órdenes",\n    icon="📡",\n    url_path="diagnostico-vibracional",\n)\n# --- fin ampliación vibraciones ---\n\n'''
changed=False
if 'vibraciones_2gdl = st.Page(' not in text:
    m=re.search(r'(?m)^\s*pg\s*=\s*st\.navigation\s*\(',text)
    if not m: print('No se encontró pg = st.navigation(...). Usa INTEGRACION_STREAMLIT.txt.');sys.exit(2)
    text=text[:m.start()]+defs+text[m.start():];changed=True
section_patterns=[r'(["\']Máquinas y Componentes["\']\s*:\s*\[)',r'(["\']Maquinas y Componentes["\']\s*:\s*\[)',r'(["\']Máquinas y componentes["\']\s*:\s*\[)']
found=False
for pat in section_patterns:
    m=re.search(pat,text)
    if m:
        found=True;tail=text[m.end():m.end()+1200]
        if 'vibraciones_2gdl' not in tail:
            ins='\n            vibraciones_2gdl,\n            diagnostico_vibracional,'
            text=text[:m.end()]+ins+text[m.end():];changed=True
        break
if not found: print('No se encontró la sección Máquinas y Componentes. Se agregaron las definiciones; revisa INTEGRACION_STREAMLIT.txt para insertar las variables manualmente.')
if changed:
    p.write_text(text,encoding='utf-8');print('streamlit_app.py actualizado. Respaldo:',backup)
else: print('El registro ya estaba aplicado; no se realizaron cambios.')
