from __future__ import annotations
from pathlib import Path
import re, shutil, sys
p=Path('streamlit_app.py')
if not p.exists():
    print('No se encontró streamlit_app.py en la carpeta actual.');sys.exit(1)
text=p.read_text(encoding='utf-8')
backup=p.with_suffix('.py.bak_hidraulica_aplicada')
if not backup.exists(): shutil.copy2(p,backup)
defs='''\n# --- Hidráulica aplicada · GG DIMEC MechLab ---\nhidraulica_aplicada = st.Page(\n    "pages/hidraulica_aplicada.py",\n    title="Hidráulica aplicada · Maquinaria",\n    icon="🛠️",\n    url_path="hidraulica-aplicada",\n)\n# --- fin hidráulica aplicada ---\n\n'''
changed=False
if 'hidraulica_aplicada = st.Page(' not in text:
    m=re.search(r'(?m)^\s*pg\s*=\s*st\.navigation\s*\(',text)
    if not m:
        print('No se encontró pg = st.navigation(...). Usa INTEGRACION_STREAMLIT.txt.');sys.exit(2)
    text=text[:m.start()]+defs+text[m.start():];changed=True
patterns=[r'(["\']Máquinas y Componentes["\']\s*:\s*\[)',r'(["\']Maquinas y Componentes["\']\s*:\s*\[)',r'(["\']Máquinas y componentes["\']\s*:\s*\[)']
found=False
for pat in patterns:
    m=re.search(pat,text)
    if m:
        found=True
        tail=text[m.end():m.end()+1400]
        if 'hidraulica_aplicada' not in tail:
            text=text[:m.end()]+'\n            hidraulica_aplicada,'+text[m.end():];changed=True
        break
if not found:
    print('No se encontró la sección Máquinas y Componentes. Se agregaron las definiciones; inserta hidraulica_aplicada manualmente según INTEGRACION_STREAMLIT.txt.')
if changed:
    p.write_text(text,encoding='utf-8');print('streamlit_app.py actualizado. Respaldo:',backup)
else:
    print('El registro ya estaba aplicado; no se realizaron cambios.')
