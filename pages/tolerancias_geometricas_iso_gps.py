from __future__ import annotations
import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from modules.iso_gps_engine import evaluate_case
from modules.iso_gps_visual3d import render_iso_gps_3d

st.set_page_config(page_title='ISO GPS · Tolerancias geométricas', page_icon='📐', layout='wide')

KIND_OPTIONS = ['Posición', 'Planitud', 'Perpendicularidad', 'Paralelismo', 'Circularidad', 'Cilindricidad']


def style_block():
    st.markdown('''
    <style>
    .gg-kpi{background:#f8f4ee;border:1px solid #e1d8cb;border-radius:14px;padding:14px 16px;height:100%;}
    .gg-note{background:#eef5ff;border:1px solid #cfe0ff;border-radius:12px;padding:12px 14px;}
    .gg-ok{background:#eef8f0;border:1px solid #c8e6cf;border-radius:12px;padding:10px 12px;color:#215c2e;font-weight:600;}
    .gg-bad{background:#fff2f2;border:1px solid #f0caca;border-radius:12px;padding:10px 12px;color:#8a2d2d;font-weight:600;}
    .gg-fcf{background:#21242b;color:#fff2df;border-radius:10px;padding:10px 12px;font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;font-size:1.05rem;}
    .smallmuted{color:#6d7078;font-size:0.92rem}
    </style>
    ''', unsafe_allow_html=True)


def zone_plot(kind: str, tol: float, dev: float):
    fig = go.Figure()
    if kind in ['Posición', 'Circularidad']:
        r = tol/2 if kind == 'Posición' else tol
        th = np.linspace(0, 2*np.pi, 240)
        fig.add_trace(go.Scatter(x=r*np.cos(th), y=r*np.sin(th), mode='lines', name='Zona límite'))
        rr = min(dev, tol*1.3)
        fig.add_trace(go.Scatter(x=[rr,0], y=[0,0], mode='markers+lines', name='Desviación real'))
        fig.update_xaxes(title='x [mm]', scaleanchor='y', scaleratio=1)
        fig.update_yaxes(title='y [mm]')
    elif kind in ['Planitud', 'Paralelismo']:
        fig.add_trace(go.Scatter(x=[0,1], y=[0,0], mode='lines', name='Plano límite 1'))
        fig.add_trace(go.Scatter(x=[0,1], y=[tol,tol], mode='lines', name='Plano límite 2'))
        y = np.clip(dev, 0, tol*1.4)
        fig.add_trace(go.Scatter(x=np.linspace(0,1,80), y=y*0.4*np.sin(np.linspace(0,4*np.pi,80))+y/2, mode='lines', name='Superficie real'))
        fig.update_xaxes(title='longitud normalizada')
        fig.update_yaxes(title='separación [mm]')
    elif kind == 'Perpendicularidad':
        fig.add_trace(go.Scatter(x=[0,0], y=[0,1], mode='lines', name='Referencia ideal'))
        x2 = math.tan(math.radians(min(8,max(0.5, dev*40))))
        fig.add_trace(go.Scatter(x=[0,x2], y=[0,1], mode='lines', name='Eje real'))
        fig.add_shape(type='rect', x0=-tol/2, x1=tol/2, y0=0, y1=1, line=dict(dash='dot'))
        fig.update_xaxes(title='desvío lateral [mm]')
        fig.update_yaxes(title='altura normalizada')
    else:  # Cilindricidad
        th = np.linspace(0, 2*np.pi, 240)
        r1, r2 = 10, 10+tol
        fig.add_trace(go.Scatter(x=r1*np.cos(th), y=r1*np.sin(th), mode='lines', name='Cilindro límite interno'))
        fig.add_trace(go.Scatter(x=r2*np.cos(th), y=r2*np.sin(th), mode='lines', name='Cilindro límite externo'))
        rr = 10 + dev*0.7
        fig.add_trace(go.Scatter(x=(rr+0.5*np.sin(3*th))*np.cos(th), y=(rr+0.5*np.sin(3*th))*np.sin(th), mode='lines', name='Superficie real'))
        fig.update_xaxes(title='x [mm]', scaleanchor='y', scaleratio=1)
        fig.update_yaxes(title='y [mm]')
    fig.update_layout(height=360, margin=dict(l=20,r=20,t=20,b=20), legend=dict(orientation='h'))
    return fig


def result_gauge(ratio: float):
    ratio_pct = min(150, max(0, ratio*100))
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=ratio_pct,
        number={'suffix':' %'},
        gauge={
            'axis': {'range':[0,150]},
            'bar': {'thickness':0.3},
            'steps':[
                {'range':[0,100], 'color':'#dff3e6'},
                {'range':[100,150], 'color':'#fde2e2'},
            ],
            'threshold': {'line': {'color':'#c8752d','width':4}, 'thickness':0.8, 'value':100}
        },
        title={'text':'Uso de tolerancia'}
    ))
    fig.update_layout(height=260, margin=dict(l=20,r=20,t=30,b=20))
    return fig


def explanation(kind: str) -> str:
    texts = {
        'Posición': 'La tolerancia de posición controla la ubicación de un eje, centro o agujero respecto de datums. La zona suele ser un cilindro de diámetro t centrado en la posición teórica verdadera.',
        'Planitud': 'La planitud controla una superficie sin recurrir a datums. Toda la superficie debe quedar entre dos planos paralelos separados por t.',
        'Perpendicularidad': 'La perpendicularidad controla la orientación de un eje o superficie respecto de un datum, comúnmente una base A.',
        'Paralelismo': 'El paralelismo controla que la superficie o eje mantenga una orientación paralela respecto de un datum de referencia.',
        'Circularidad': 'La circularidad controla la forma de cada sección circular en forma independiente, sin datums.',
        'Cilindricidad': 'La cilindricidad controla simultáneamente circularidad, rectitud y generatrices de toda la superficie cilíndrica, sin datums.',
    }
    return texts[kind]


style_block()

st.title('📐 ISO GPS · Tolerancias geométricas 3D')
st.caption('GG DIMEC · MECHLAB · METROLOGÍA Y CALIDAD')

with st.sidebar:
    st.header('Configuración didáctica')
    kind = st.selectbox('Tipo de tolerancia', KIND_OPTIONS, index=0)
    tol = st.slider('Tolerancia [mm]', 0.02, 1.00, 0.20, 0.01)
    dev = st.slider('Desviación real [mm]', 0.00, 1.20, 0.12, 0.01)
    hole_d = st.slider('Diámetro nominal del agujero/eje [mm]', 8.0, 40.0, 18.0, 1.0)
    actual_angle = st.slider('Ángulo de desvío [°]', -6.0, 6.0, 1.5, 0.1)
    actual_dir = st.slider('Dirección de desvío [° en planta]', 0, 360, 35, 1)
    ampl = st.slider('Amplificación visual', 0.5, 4.0, 1.8, 0.1)
    st.markdown('---')
    st.markdown('**Datums por defecto**')
    st.markdown('- A: base\n- B: cara lateral\n- C: cara posterior')

res = evaluate_case(kind, tol, dev)
dx = math.cos(math.radians(actual_dir)) * dev * ampl / 20
ndy = math.sin(math.radians(actual_dir)) * dev * ampl / 20

payload = {
    'kind': kind,
    'tol_mm': float(tol),
    'deviation_mm': float(dev),
    'pass_ok': bool(res.pass_ok),
    'hole_d_mm': float(hole_d),
    'actual_dx': float(dx),
    'actual_dy': float(ndy),
    'angular_deg': float(actual_angle),
    'basic_x': 0.55,
    'basic_y': 0.0,
}

c1, c2, c3 = st.columns([1.1, 1.1, 1.0])
with c1:
    st.markdown('<div class="gg-kpi"><div class="smallmuted">Marco de control geométrico</div><div class="gg-fcf">'+res.feature_control_frame+'</div></div>', unsafe_allow_html=True)
with c2:
    state_class = 'gg-ok' if res.pass_ok else 'gg-bad'
    state_txt = 'CUMPLE' if res.pass_ok else 'NO CUMPLE'
    st.markdown(f'<div class="gg-kpi"><div class="smallmuted">Verificación</div><div class="{state_class}">{state_txt}</div><div style="margin-top:8px">Desviación = <b>{dev:.3f} mm</b><br>Tolerancia = <b>{tol:.3f} mm</b></div></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="gg-kpi"><div class="smallmuted">Concepto clave</div><div style="font-size:0.98rem;line-height:1.5">'+explanation(kind)+'</div></div>', unsafe_allow_html=True)

st.markdown('<div class="gg-note"><b>Cómo leer la pieza:</b> la pieza 3D muestra una referencia didáctica con datums A, B y C. La zona naranja representa la <b>zona de tolerancia</b>; el elemento rojo/naranjo representa el <b>elemento real</b> medido o manufacturado.</div>', unsafe_allow_html=True)

tabs = st.tabs(['📊 Vista compacta', '🧩 Pieza 3D', '📐 Zona de tolerancia', '🔎 Interpretación'])

with tabs[0]:
    a,b = st.columns([1.0,1.2])
    with a:
        st.plotly_chart(result_gauge(res.ratio), use_container_width=True, key='iso_gps_gauge_compacta')
    with b:
        st.plotly_chart(zone_plot(kind, tol, dev), use_container_width=True, key='iso_gps_zone_compacta')
    st.markdown('### Lectura rápida')
    bullets = {
        'Posición': 'El centro/eje real debe quedar dentro del cilindro de tolerancia de diámetro t ubicado en la posición teórica verdadera.',
        'Planitud': 'Toda la superficie debe quedar entre dos planos paralelos separados por t.',
        'Perpendicularidad': 'La orientación del eje o superficie real respecto del datum A debe mantenerse dentro de la zona especificada.',
        'Paralelismo': 'La superficie real debe conservar una separación uniforme respecto del datum de referencia.',
        'Circularidad': 'Cada corte transversal circular se evalúa de forma independiente respecto de dos circunferencias concéntricas.',
        'Cilindricidad': 'Toda la superficie cilíndrica se evalúa simultáneamente respecto de dos cilindros coaxiales.',
    }
    st.write('• ' + bullets[kind])
    st.write('• Resultado actual: **{}**.'.format('cumple' if res.pass_ok else 'no cumple'))
    st.write('• Uso de tolerancia: **{:.1f} %**.'.format(res.ratio*100))

with tabs[1]:
    render_iso_gps_3d(payload, height=620)

with tabs[2]:
    left, right = st.columns([1.2,1.0])
    with left:
        st.plotly_chart(zone_plot(kind, tol, dev), use_container_width=True, key='iso_gps_zone_detalle')
    with right:
        st.markdown('### Marco conceptual')
        st.markdown(f'**Tolerancia seleccionada:** {kind}')
        st.markdown(f'**Marco de control:** `{res.feature_control_frame}`')
        st.markdown(f'**Interpretación base:** {res.interpretation}')
        if kind in ['Posición', 'Perpendicularidad', 'Paralelismo']:
            st.markdown('**Datums usados:** A, B y C / o A según el control mostrado.')
        else:
            st.markdown('**Datums usados:** no requiere datums en este ejemplo didáctico.')
        st.markdown('### Idea pedagógica')
        st.write('Se busca que el alumno relacione **pieza ideal → zona de tolerancia → pieza real**, no solo el símbolo del marco de control.')

with tabs[3]:
    st.markdown('### Explicación paso a paso')
    st.write(explanation(kind))
    st.markdown('#### Secuencia de lectura sugerida')
    if kind == 'Posición':
        st.markdown('1. Identificar datums **A**, **B** y **C**.\n2. Ubicar la posición teórica verdadera.\n3. Construir un cilindro de diámetro **t**.\n4. Verificar que el eje real quede dentro del cilindro.')
    elif kind == 'Planitud':
        st.markdown('1. Tomar la superficie completa.\n2. Construir dos planos paralelos separados por **t**.\n3. Verificar que toda la superficie real quede contenida entre ellos.')
    elif kind == 'Perpendicularidad':
        st.markdown('1. Reconocer el datum de referencia.\n2. Definir la zona de orientación perpendicular.\n3. Verificar el eje o superficie real respecto del datum.')
    elif kind == 'Paralelismo':
        st.markdown('1. Definir el datum base.\n2. Construir dos planos paralelos separados por **t**.\n3. Verificar que la superficie real se mantenga dentro de la zona.')
    elif kind == 'Circularidad':
        st.markdown('1. Analizar una sección circular.\n2. Trazar dos circunferencias concéntricas.\n3. Revisar que el perfil real permanezca entre ambas.')
    else:
        st.markdown('1. Considerar la superficie cilíndrica completa.\n2. Construir dos cilindros coaxiales límite.\n3. Verificar que toda la superficie real quede contenida entre ellos.')
    st.markdown('#### Ecuación resumen')
    st.latex(r"\text{Cumple si }\; \text{desviación real} \le \text{tolerancia especificada}")
    st.latex(rf"{dev:.3f}\;\mathrm{{mm}} \le {tol:.3f}\;\mathrm{{mm}}")
    if res.pass_ok:
        st.success('El caso actual cumple con la tolerancia especificada.')
    else:
        st.error('El caso actual no cumple con la tolerancia especificada.')
