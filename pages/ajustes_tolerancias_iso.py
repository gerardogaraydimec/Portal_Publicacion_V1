from __future__ import annotations
import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from modules.fit_iso_engine import iso286_h7_fit, manual_fit, actual_dimensions, clearance_summary
from modules.fit_visual3d import render_fit_3d

try:
    from modules.ui_brand import render_app_header
except Exception:
    render_app_header = None

st.markdown('''
<style>
.block-container{max-width:1480px;padding-top:1rem!important}
.gg-note{border:1px solid #d8e3f4;border-left:4px solid #f28e1c;border-radius:12px;padding:.78rem .95rem;background:#f5f9ff}
.gg-card{border:1px solid #e5ddd1;border-radius:14px;background:#fffdf9;padding:.85rem .95rem;height:100%}
.gg-mini{font-size:.9rem;color:#565b64;line-height:1.45}
.gg-fit{font-size:1.45rem;font-weight:700;margin:.2rem 0 .4rem 0}
.gg-clear{color:#2f6db3}.gg-transition{color:#bf6d12}.gg-interference{color:#a94343}
</style>
''', unsafe_allow_html=True)

if render_app_header:
    render_app_header(
        title='Ajustes y Tolerancias ISO · Eje–Agujero 3D',
        subtitle='ISO 286 · límites dimensionales · juego · transición · interferencia · montaje 3D.',
        section='METROLOGÍA Y CALIDAD',
        logo_width=188,
    )
else:
    st.title('⚙️ Ajustes y Tolerancias ISO · Eje–Agujero 3D')
    st.caption('ISO 286 · límites dimensionales · juego · transición · interferencia · montaje 3D')

PRESETS = ['H7/g6','H7/h6','H7/k6','H7/m6','H7/n6','H7/p6']

with st.sidebar:
    st.header('Ajuste eje–agujero')
    mode = st.radio('Modo de definición', ['ISO 286 · H7/*', 'Manual'], horizontal=False)
    nominal = float(st.number_input('Diámetro nominal [mm]', min_value=0.5, max_value=500.0, value=30.0, step=1.0))
    if mode.startswith('ISO'):
        designation = st.selectbox('Ajuste', PRESETS, index=1)
        fit = iso286_h7_fit(nominal, designation)
        st.caption(f'Rango tabulado: {fit.range_label}')
    else:
        st.subheader('Agujero')
        hole_EI = float(st.number_input('EI agujero [µm]', value=0.0, step=1.0))
        hole_ES = float(st.number_input('ES agujero [µm]', value=20.0, step=1.0))
        st.subheader('Eje')
        shaft_ei = float(st.number_input('ei eje [µm]', value=-10.0, step=1.0))
        shaft_es = float(st.number_input('es eje [µm]', value=0.0, step=1.0))
        fit = manual_fit(nominal,hole_EI,hole_ES,shaft_ei,shaft_es)
        designation = 'Manual'
    st.divider()
    st.subheader('Pieza real dentro de su zona')
    hole_pct = st.slider('Posición real del agujero [% de su tolerancia]',0,100,50,1)/100
    shaft_pct = st.slider('Posición real del eje [% de su tolerancia]',0,100,50,1)/100
    assembly = st.slider('Estado de montaje [%]',0,100,70,1)

actual_hole, actual_shaft, actual_clear = actual_dimensions(fit,hole_pct,shaft_pct)
summary = clearance_summary(fit)

fit_class = {'Juego':'gg-clear','Transición':'gg-transition','Interferencia':'gg-interference'}[fit.fit_type]

m1,m2,m3,m4,m5=st.columns(5)
m1.metric('Ajuste',fit.designation)
m2.metric('Tipo',fit.fit_type)
m3.metric('Agujero real',f'{actual_hole:.4f} mm')
m4.metric('Eje real',f'{actual_shaft:.4f} mm')
m5.metric('Juego real',f'{actual_clear*1000:+.1f} µm')

st.markdown(f'''<div class="gg-note"><b>Ruta física:</b> diámetro nominal → zonas de tolerancia de agujero y eje → dimensiones límite → <b>{fit.fit_type.lower()}</b> → comportamiento del montaje. La separación radial del 3D está exagerada para que diferencias de pocos micrómetros sean visibles.</div>''',unsafe_allow_html=True)

tabs=st.tabs(['📊 Vista compacta','🧩 Montaje 3D','📐 Zonas de tolerancia','⚖️ Comparador','🔎 Interpretación'])

def zones_figure(f):
    fig=go.Figure()
    fig.add_trace(go.Bar(x=['Agujero H7' if f.designation!='Manual' else 'Agujero'],y=[f.hole_ES_um-f.hole_EI_um],base=[f.hole_EI_um],name='Agujero',width=.48))
    shaft_name=f.designation.split('/')[-1] if '/' in f.designation else 'Eje'
    fig.add_trace(go.Bar(x=[f'Eje {shaft_name}'],y=[f.shaft_es_um-f.shaft_ei_um],base=[f.shaft_ei_um],name='Eje',width=.48))
    fig.add_hline(y=0,line_dash='dash',line_color='#555')
    fig.update_layout(height=360,barmode='group',margin=dict(l=20,r=20,t=25,b=20),yaxis_title='Desviación respecto del nominal [µm]',showlegend=False)
    return fig

def clearance_interval_figure(f):
    fig=go.Figure()
    c0,c1=f.clearance_min_mm*1000,f.clearance_max_mm*1000
    fig.add_trace(go.Scatter(x=[c0,c1],y=[1,1],mode='lines+markers',line=dict(width=8),marker=dict(size=11),name='intervalo'))
    fig.add_vline(x=0,line_dash='dash',line_color='#555')
    fig.update_layout(height=280,margin=dict(l=20,r=20,t=25,b=20),xaxis_title='Agujero − eje [µm]',yaxis=dict(visible=False,range=[.6,1.4]),showlegend=False)
    return fig

with tabs[0]:
    left,right=st.columns([1.35,1.0],gap='medium')
    with left:
        st.plotly_chart(zones_figure(fit),use_container_width=True,key='fit_zones_compact')
        st.plotly_chart(clearance_interval_figure(fit),use_container_width=True,key='fit_interval_compact')
    with right:
        st.markdown(f'''<div class="gg-card"><div class="gg-mini">Clasificación</div><div class="gg-fit {fit_class}">{fit.fit_type}</div><b>{summary['label1']}:</b> {summary['value1_mm']*1000:.1f} µm<br><b>{summary['label2']}:</b> {summary['value2_mm']*1000:.1f} µm<br><br><b>Agujero:</b> {fit.hole_min_mm:.4f} a {fit.hole_max_mm:.4f} mm<br><b>Eje:</b> {fit.shaft_min_mm:.4f} a {fit.shaft_max_mm:.4f} mm</div>''',unsafe_allow_html=True)
        st.markdown(f'''<div class="gg-card"><b>Uso didáctico del ajuste</b><div class="gg-mini">{fit.purpose}</div></div>''',unsafe_allow_html=True)
        if actual_clear>0:
            st.success(f'La pareja real seleccionada tiene {actual_clear*1000:.1f} µm de juego diametral.')
        elif actual_clear<0:
            st.warning(f'La pareja real seleccionada tiene {-actual_clear*1000:.1f} µm de interferencia diametral.')
        else:
            st.info('La pareja real seleccionada queda exactamente en condición límite, sin juego ni interferencia.')

with tabs[1]:
    c1,c2=st.columns([1,2.4],gap='medium')
    with c1:
        st.markdown('### Cómo leer el 3D')
        st.write('El eje se desplaza hacia el alojamiento según el control **Estado de montaje** de la barra lateral.')
        st.write('La zona coloreada identifica visualmente si el ajuste corresponde a juego, transición o interferencia.')
        st.caption('La diferencia radial está amplificada. No representa a escala real los micrómetros de tolerancia.')
        st.markdown(f'''<div class="gg-card"><b>Dimensión real actual</b><div class="gg-mini">Agujero = {actual_hole:.4f} mm<br>Eje = {actual_shaft:.4f} mm<br>Diferencia = {actual_clear*1000:+.1f} µm</div></div>''',unsafe_allow_html=True)
    with c2:
        render_fit_3d({
            'designation':fit.designation,'fit_type':fit.fit_type,'nominal_mm':fit.nominal_mm,
            'hole_EI_um':fit.hole_EI_um,'hole_ES_um':fit.hole_ES_um,'shaft_ei_um':fit.shaft_ei_um,'shaft_es_um':fit.shaft_es_um,
            'actual_hole_mm':actual_hole,'actual_shaft_mm':actual_shaft,'actual_clearance_mm':actual_clear,'assembly':assembly
        },height=620)

with tabs[2]:
    a,b=st.columns([1.2,1.0])
    with a:
        st.plotly_chart(zones_figure(fit),use_container_width=True,key='fit_zones_detail')
    with b:
        st.markdown('### Límites dimensionales')
        st.write(f'**Nominal:** Ø {nominal:.3f} mm')
        st.write(f'**Agujero:** {fit.hole_min_mm:.4f} … {fit.hole_max_mm:.4f} mm')
        st.write(f'**Eje:** {fit.shaft_min_mm:.4f} … {fit.shaft_max_mm:.4f} mm')
        st.write(f'**Desviaciones agujero:** EI = {fit.hole_EI_um:+.0f} µm · ES = {fit.hole_ES_um:+.0f} µm')
        st.write(f'**Desviaciones eje:** ei = {fit.shaft_ei_um:+.0f} µm · es = {fit.shaft_es_um:+.0f} µm')
        st.markdown('### Relaciones')
        st.latex(r'D_{H,min}=D_N+EI,\qquad D_{H,max}=D_N+ES')
        st.latex(r'D_{S,min}=D_N+ei,\qquad D_{S,max}=D_N+es')
        st.latex(r'J_{min}=D_{H,min}-D_{S,max}')
        st.latex(r'J_{max}=D_{H,max}-D_{S,min}')

with tabs[3]:
    st.subheader('Comparador A/B')
    st.caption('El Caso A es el ajuste principal. El Caso B usa el mismo diámetro nominal y permite comparar otra combinación H7/*.')
    bfit_name=st.selectbox('Ajuste B',PRESETS,index=min(5,PRESETS.index(fit.designation)+1) if fit.designation in PRESETS else 0,key='fit_compare_select')
    fitB=iso286_h7_fit(nominal,bfit_name)
    sB=clearance_summary(fitB)
    c1,c2,c3,c4=st.columns(4)
    c1.metric('A · tipo',fit.fit_type)
    c2.metric('B · tipo',fitB.fit_type)
    c3.metric('A · rango [µm]',f'{fit.clearance_min_mm*1000:+.0f} … {fit.clearance_max_mm*1000:+.0f}')
    c4.metric('B · rango [µm]',f'{fitB.clearance_min_mm*1000:+.0f} … {fitB.clearance_max_mm*1000:+.0f}')
    p1,p2=st.columns(2)
    p1.plotly_chart(zones_figure(fit),use_container_width=True,key='fit_compare_A')
    p2.plotly_chart(zones_figure(fitB),use_container_width=True,key='fit_compare_B')
    st.markdown(f'''<div class="gg-note"><b>{fit.designation}</b>: {fit.purpose}<br><b>{fitB.designation}</b>: {fitB.purpose}</div>''',unsafe_allow_html=True)

with tabs[4]:
    st.subheader('Interpretación del ajuste')
    if fit.fit_type=='Juego':
        st.markdown('**Juego:** incluso en la condición más desfavorable, el agujero no queda menor que el eje. El montaje puede realizarse sin presión por interferencia.')
    elif fit.fit_type=='Interferencia':
        st.markdown('**Interferencia:** el eje puede ser mayor que el agujero en toda la zona del ajuste. El montaje requiere considerar presión, temperatura, materiales y tensiones de contacto.')
    else:
        st.markdown('**Transición:** según las dimensiones reales fabricadas, el mismo ajuste puede quedar con pequeño juego o pequeña interferencia.')
    st.markdown('### Sistema base agujero')
    st.write('En los presets automáticos se mantiene el agujero **H7**, cuya desviación inferior EI es 0; el tipo de ajuste cambia al mover la zona del eje mediante g6, h6, k6, m6, n6 o p6.')
    st.markdown('### Lectura del signo')
    st.latex(r'J=D_{agujero}-D_{eje}')
    st.write('Si **J > 0** hay juego. Si **J < 0** existe interferencia. Si el intervalo posible de J cruza cero, el ajuste es de transición.')
    st.markdown('### Alcance')
    st.info('El módulo es didáctico. Los presets automáticos cubren combinaciones H7/* comunes hasta Ø500 mm. Para especificación contractual o fabricación, verifica siempre la edición aplicable de ISO 286 y los requisitos particulares del plano, proceso y montaje.')
