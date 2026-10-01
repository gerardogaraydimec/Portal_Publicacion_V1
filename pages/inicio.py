from __future__ import annotations
import streamlit as st

from modules.ui_brand import render_app_header

st.set_page_config(page_title='MechLab · Laboratorio de Ingeniería Mecánica', page_icon='⚙️', layout='wide')

CSS = r'''
<style>
.block-container{max-width:1480px;padding-top:1.0rem!important;padding-bottom:3rem!important}
:root{
  --gg-orange:#f28e1c;
  --gg-copper:#c8752d;
  --gg-graphite:#202126;
  --gg-ivory:#fbf7f0;
  --gg-border:#e6ded2;
  --gg-muted:#6d6a65;
}
.gg-hero{
  background:linear-gradient(120deg,#fffaf3 0%,#f8f3eb 62%,#f3ebe0 100%);
  border:1px solid var(--gg-border);
  border-radius:20px;
  padding:1.25rem 1.35rem;
  margin:.25rem 0 1rem 0;
}
.gg-hero-title{font-size:1.55rem;font-weight:800;color:var(--gg-graphite);line-height:1.12;margin-bottom:.35rem}
.gg-hero-text{font-size:1.02rem;line-height:1.55;color:#4e4c48;max-width:1100px}
.gg-route{display:grid;grid-template-columns:repeat(5,1fr);gap:.55rem;margin:.8rem 0 1.1rem 0}
.gg-route-item{background:#fff;border:1px solid var(--gg-border);border-radius:13px;padding:.76rem .75rem;text-align:center;min-height:84px}
.gg-route-n{display:inline-flex;align-items:center;justify-content:center;width:27px;height:27px;border-radius:50%;background:var(--gg-orange);color:white;font-weight:800;margin-bottom:.25rem}
.gg-route-b{font-size:.91rem;font-weight:760;color:var(--gg-graphite)}
.gg-route-s{font-size:.78rem;color:var(--gg-muted);line-height:1.28;margin-top:.12rem}
.gg-section-title{font-size:1.34rem;font-weight:800;color:var(--gg-graphite);margin:.35rem 0 .6rem 0}
.gg-area-card{background:white;border:1px solid var(--gg-border);border-radius:16px;padding:1rem 1.05rem;height:100%;box-shadow:0 1px 0 rgba(32,33,38,.025)}
.gg-area-head{display:flex;gap:.65rem;align-items:flex-start;margin-bottom:.48rem}
.gg-icon{font-size:1.55rem;line-height:1}
.gg-area-name{font-size:1.06rem;font-weight:800;color:var(--gg-graphite);line-height:1.18}
.gg-area-desc{font-size:.87rem;color:var(--gg-muted);line-height:1.38;margin-top:.16rem}
.gg-module{padding:.22rem 0;font-size:.88rem;line-height:1.35;color:#42413e}
.gg-module b{color:#26272b}
.gg-pill{display:inline-block;background:#fff3e3;border:1px solid #f2d3aa;color:#a95c19;font-size:.70rem;font-weight:750;border-radius:999px;padding:.12rem .42rem;margin-left:.25rem;vertical-align:1px}
.gg-pill-gray{background:#f2f2f2;border-color:#dddddd;color:#666}
.gg-callout{border:1px solid #d9e6f7;border-left:4px solid #6a91c7;background:#f5f9ff;border-radius:12px;padding:.82rem 1rem;color:#3d4754;font-size:.91rem;line-height:1.45}
.gg-warning{border:1px solid #eadcc9;border-left:4px solid var(--gg-copper);background:#fffaf4;border-radius:12px;padding:.82rem 1rem;color:#554b40;font-size:.90rem;line-height:1.45}
.gg-stat{background:var(--gg-graphite);border-radius:14px;padding:.82rem .9rem;color:#f8f1e7;height:100%}
.gg-stat-n{font-size:1.28rem;font-weight:800;color:#ffad45}
.gg-stat-t{font-size:.80rem;color:#ddd7cf;line-height:1.3}
.gg-list{margin:.25rem 0 0 0;padding-left:1.1rem;color:#484743;font-size:.89rem;line-height:1.52}
.gg-footer{margin-top:1.4rem;border-top:1px solid var(--gg-border);padding-top:.8rem;color:#74716c;font-size:.80rem;line-height:1.45}
@media(max-width:900px){.gg-route{grid-template-columns:1fr 1fr}.gg-route-item:last-child{grid-column:1/-1}}
</style>
'''
st.markdown(CSS, unsafe_allow_html=True)

render_app_header(
    title='MechLab · Laboratorio de Ingeniería Mecánica',
    subtitle='Explora fenómenos, construye modelos, calcula, compara y desarrolla criterio de ingeniería a partir del comportamiento de máquinas y sistemas mecánicos.',
    section='PORTAL',
    logo_width=188,
)

st.markdown('''
<div class="gg-hero">
  <div class="gg-hero-title">Un laboratorio digital para comprender antes de calcular</div>
  <div class="gg-hero-text">
    MechLab organiza herramientas de ingeniería mecánica alrededor de una idea común: partir del fenómeno físico,
    representarlo con un modelo comprensible, resolverlo con ecuaciones y gráficos, y terminar interpretando qué significa
    el resultado para una máquina, componente o sistema. El 3D se usa cuando ayuda a ver el fenómeno; no para decorar la interfaz.
  </div>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="gg-route">
  <div class="gg-route-item"><div class="gg-route-n">1</div><div class="gg-route-b">Fenómeno</div><div class="gg-route-s">¿Qué está ocurriendo físicamente?</div></div>
  <div class="gg-route-item"><div class="gg-route-n">2</div><div class="gg-route-b">Modelo</div><div class="gg-route-s">Idealizaciones, variables y supuestos.</div></div>
  <div class="gg-route-item"><div class="gg-route-n">3</div><div class="gg-route-b">Cálculo</div><div class="gg-route-s">Ecuaciones, diagramas y resultados.</div></div>
  <div class="gg-route-item"><div class="gg-route-n">4</div><div class="gg-route-b">Visualización</div><div class="gg-route-s">3D, animaciones y respuesta del sistema.</div></div>
  <div class="gg-route-item"><div class="gg-route-n">5</div><div class="gg-route-b">Interpretación</div><div class="gg-route-s">Comparar, explicar y tomar decisiones.</div></div>
</div>
''', unsafe_allow_html=True)

st.markdown('<div class="gg-section-title">Mapa actual de MechLab</div>', unsafe_allow_html=True)

row1 = st.columns(3, gap='medium')
with row1[0]:
    st.markdown('''
<div class="gg-area-card">
 <div class="gg-area-head"><div class="gg-icon">🏗️</div><div><div class="gg-area-name">Resistencia y Estructuras</div><div class="gg-area-desc">De cargas internas y tensiones a estabilidad, torsión y comportamiento de secciones.</div></div></div>
 <div class="gg-module"><b>Vigas</b> · V(x), M(x), tensiones, deflexión y corte 3D <span class="gg-pill">3D</span></div>
 <div class="gg-module"><b>Columnas</b> · compresión, esbeltez y pandeo de Euler <span class="gg-pill">3D</span></div>
 <div class="gg-module"><b>Torsión</b> · giro, esfuerzo cortante y comparación de secciones <span class="gg-pill">3D</span></div>
 <div class="gg-module"><b>Mohr 2D / 3D</b> · transformación y estado de tensiones</div>
 <div class="gg-module"><b>Von Mises</b> · lectura de estado equivalente</div>
 <div class="gg-module"><b>Perfiles estructurales</b> · propiedades geométricas y secciones</div>
</div>''', unsafe_allow_html=True)

with row1[1]:
    st.markdown('''
<div class="gg-area-card">
 <div class="gg-area-head"><div class="gg-icon">🌀</div><div><div class="gg-area-name">Dinámica y Vibraciones</div><div class="gg-area-desc">Del movimiento libre a resonancia, absorbedores y diagnóstico vibracional.</div></div></div>
 <div class="gg-module"><b>1GDL libre</b> · x(t), v(t), a(t), energía y plano de fase <span class="gg-pill">3D</span></div>
 <div class="gg-module"><b>1GDL forzada</b> · fuerza armónica, desbalance y excitación de base <span class="gg-pill">3D</span></div>
 <div class="gg-module"><b>2GDL / TMD</b> · modos, antirresonancia y absorbedor dinámico <span class="gg-pill">3D</span></div>
 <div class="gg-module"><b>Diagnóstico</b> · señal temporal, FFT, órdenes, waterfall y sensores <span class="gg-pill">3D</span></div>
 <div class="gg-module"><b>Comparadores</b> · respuesta A/B para observar sensibilidad de parámetros</div>
</div>''', unsafe_allow_html=True)

with row1[2]:
    st.markdown('''
<div class="gg-area-card">
 <div class="gg-area-head"><div class="gg-icon">🌊</div><div><div class="gg-area-name">Fluidos y Energía</div><div class="gg-area-desc">Conecta conservación de energía, régimen de flujo, pérdidas y operación hidráulica.</div></div></div>
 <div class="gg-module"><b>Continuidad y Bernoulli</b> · presión, velocidad y energía <span class="gg-pill">3D</span></div>
 <div class="gg-module"><b>Reynolds y pérdidas</b> · régimen, fricción, HGL/EGL y comparación <span class="gg-pill">3D</span></div>
 <div class="gg-module"><b>Bombas y sistema</b> · curva H–Q, punto de operación, válvula y afinidad <span class="gg-pill">3D</span></div>
 <div class="gg-module"><b>Propiedades del agua</b> · estados y propiedades termodinámicas</div>
 <div class="gg-module"><b>Ciclos termodinámicos</b> · análisis energético de procesos y ciclos</div>
</div>''', unsafe_allow_html=True)

row2 = st.columns([1.0, 1.0, 1.0], gap='medium')
with row2[0]:
    st.markdown('''
<div class="gg-area-card">
 <div class="gg-area-head"><div class="gg-icon">📏</div><div><div class="gg-area-name">Metrología y Calidad</div><div class="gg-area-desc">Comprende especificación dimensional, geometría real y decisión de conformidad.</div></div></div>
 <div class="gg-module"><b>ISO GPS</b> · datums, zonas geométricas y conformidad <span class="gg-pill">3D</span></div>
 <div class="gg-module"><b>Ajustes y tolerancias ISO</b> · juego, transición e interferencia <span class="gg-pill">3D</span></div>
 <div class="gg-module"><b>Medición e incertidumbre</b> · dispersión, resolución y decisión metrológica</div>
</div>''', unsafe_allow_html=True)

with row2[1]:
    st.markdown('''
<div class="gg-area-card">
 <div class="gg-area-head"><div class="gg-icon">⚙️</div><div><div class="gg-area-name">Máquinas y Componentes</div><div class="gg-area-desc">La capa de aplicación: conecta las herramientas con componentes y sistemas mecánicos reales.</div></div></div>
 <div class="gg-module"><b>Ejes, soportes, rotores y bombas</b> aparecen como casos físicos en los distintos laboratorios.</div>
 <div class="gg-module"><b>Comparación de diseños</b> permite observar cómo geometría y parámetros cambian la respuesta.</div>
 <div class="gg-module"><b>Lectura de máquinas</b> prioriza fenómeno → modelo → cálculo → interpretación.</div>
 <div class="gg-module"><span class="gg-pill gg-pill-gray">en expansión</span> Esta área seguirá integrando aplicaciones de los módulos fundamentales.</div>
</div>''', unsafe_allow_html=True)

with row2[2]:
    st.markdown('''
<div class="gg-area-card">
 <div class="gg-area-head"><div class="gg-icon">🧭</div><div><div class="gg-area-name">Cómo recorrer MechLab</div><div class="gg-area-desc">No es necesario estudiar los módulos en un único orden.</div></div></div>
 <div class="gg-module"><b>Para aprender:</b> parte en “Cómo usar / Concepto”, modifica una variable y observa qué cambia.</div>
 <div class="gg-module"><b>Para resolver:</b> define el modelo, revisa unidades y usa luego diagramas y ecuaciones.</div>
 <div class="gg-module"><b>Para comparar:</b> usa A/B cuando esté disponible y cambia una variable cada vez.</div>
 <div class="gg-module"><b>Para interpretar:</b> termina siempre en la pestaña de lectura o interpretación.</div>
</div>''', unsafe_allow_html=True)

st.markdown('<div class="gg-section-title">Qué significa el 3D en MechLab</div>', unsafe_allow_html=True)
a,b = st.columns([1.05,1.0], gap='medium')
with a:
    st.markdown('''
<div class="gg-callout"><b>El 3D es una herramienta de comprensión.</b><br>
La animación puede amplificar desplazamientos, giros o deformaciones para volver visibles fenómenos que en escala real serían imperceptibles. Los valores numéricos continúan siendo los del modelo físico. Cuando una representación es didáctica —por ejemplo partículas de flujo, modos de pandeo o giro amplificado— la herramienta lo indica explícitamente.</div>
''', unsafe_allow_html=True)
with b:
    st.markdown('''
<div class="gg-warning"><b>Alcance.</b><br>
MechLab no reemplaza CFD, FEA, software de rotodinámica, tablas normativas certificadas ni procedimientos de metrología industrial. Su propósito es construir comprensión, apoyar el estudio, explorar sensibilidad y desarrollar criterio antes de pasar a herramientas de mayor fidelidad.</div>
''', unsafe_allow_html=True)

st.markdown('<div class="gg-section-title">Una misma forma de trabajar en todo el portal</div>', unsafe_allow_html=True)
s1,s2,s3,s4 = st.columns(4, gap='medium')
with s1:
    st.markdown('<div class="gg-stat"><div class="gg-stat-n">01</div><div class="gg-stat-t"><b>Configura</b><br>Define geometría, material, carga, fluido o condición de operación.</div></div>', unsafe_allow_html=True)
with s2:
    st.markdown('<div class="gg-stat"><div class="gg-stat-n">02</div><div class="gg-stat-t"><b>Observa</b><br>Usa el 3D y los gráficos para reconocer el fenómeno.</div></div>', unsafe_allow_html=True)
with s3:
    st.markdown('<div class="gg-stat"><div class="gg-stat-n">03</div><div class="gg-stat-t"><b>Comprueba</b><br>Revisa ecuaciones, magnitudes, unidades y supuestos.</div></div>', unsafe_allow_html=True)
with s4:
    st.markdown('<div class="gg-stat"><div class="gg-stat-n">04</div><div class="gg-stat-t"><b>Interpreta</b><br>Explica qué cambia, por qué cambia y qué significa para el sistema.</div></div>', unsafe_allow_html=True)

with st.expander('📚 Ver rutas de estudio sugeridas', expanded=False):
    x,y,z = st.columns(3)
    with x:
        st.markdown('''**Resistencia de materiales**
- Tensiones y Mohr
- Vigas
- Columnas
- Torsión
- Von Mises
- Perfiles y geometría''')
    with y:
        st.markdown('''**Dinámica de máquinas**
- Vibración libre 1GDL
- Vibración forzada
- Desbalance / base
- 2GDL y TMD
- Diagnóstico FFT / órdenes''')
    with z:
        st.markdown('''**Fluidos y sistemas hidráulicos**
- Continuidad y Bernoulli
- Reynolds
- Pérdidas
- Bombas y curva del sistema
- Energía y operación''')

with st.expander('🧪 Buenas prácticas al usar los laboratorios', expanded=False):
    st.markdown('''
- Cambia **una variable a la vez** cuando estés estudiando sensibilidad.
- Verifica siempre **unidades, signos y condiciones de borde** antes de interpretar resultados.
- Usa la vista 3D para comprender geometría y fenómeno; usa los gráficos para leer magnitud y tendencia.
- Si una deformación está amplificada visualmente, no la confundas con la escala física real.
- En normas, tolerancias, diseño y diagnóstico, diferencia entre una **herramienta didáctica** y un procedimiento de aceptación industrial.
- Cuando exista comparador A/B, formula primero una hipótesis y luego comprueba qué cambió.
''')

st.markdown('''
<div class="gg-footer">
<b>GG DIMEC · MechLab</b> — entorno de aprendizaje y exploración de ingeniería mecánica. Navega por las áreas desde el menú superior.
Las herramientas evolucionan de forma incremental procurando mantener una misma lógica visual y conceptual en todo el portal.
</div>
''', unsafe_allow_html=True)
