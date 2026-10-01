from __future__ import annotations
import io,math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from modules.ui_brand import render_app_header
from modules.vibration_diagnostics_engine import generate_synthetic,spectrum,top_peaks,metrics,analytic_envelope
from modules.vibration_diagnostics_visual3d import render_diagnostics_3d

st.markdown('''<style>.block-container{max-width:1480px;padding-top:1rem!important}.gg-note{border:1px solid #e9e2d7;border-left:4px solid #f28e1c;border-radius:12px;padding:.72rem .9rem;background:#fffaf3}.gg-card{border:1px solid #e7dfd2;border-radius:13px;background:#fffdf9;padding:.78rem .88rem;height:100%}.gg-mini{font-size:.88rem;color:#555;line-height:1.38}</style>''',unsafe_allow_html=True)
render_app_header(title='Diagnóstico vibracional · Señal, FFT y Órdenes',subtitle='Forma de onda · espectro FFT · órdenes 1X–2X–3X · métricas · punto de medición 3D.',section='MÁQUINAS Y COMPONENTES',logo_width=188)

with st.sidebar:
    st.header('Fuente de señal');source=st.radio('Origen',['Sintética didáctica','Cargar CSV'])
    rpm=float(st.number_input('Velocidad de referencia [rpm]',min_value=0.0,value=1800.0,step=50.0))
    window=st.selectbox('Ventana FFT',['Hann','Hamming','Rectangular'])
    orientation=st.selectbox('Dirección del sensor',['Horizontal','Vertical','Axial'])
    if source=='Sintética didáctica':
        preset=st.selectbox('Firma sintética',['Personalizada','Dominante 1X','Dominante 2X','Armónicos múltiples'])
        defaults={'Personalizada':(1.0,.25,.10,.05),'Dominante 1X':(1.0,.08,.03,.01),'Dominante 2X':(.45,1.0,.18,.05),'Armónicos múltiples':(.75,.55,.38,.25)}[preset]
        fs=float(st.number_input('Frecuencia de muestreo [Hz]',min_value=20.0,value=2048.0,step=128.0));duration=float(st.number_input('Duración [s]',min_value=.2,value=4.0,step=.5))
        a1=float(st.number_input('Amplitud 1X',value=defaults[0],step=.05));a2=float(st.number_input('Amplitud 2X',value=defaults[1],step=.05));a3=float(st.number_input('Amplitud 3X',value=defaults[2],step=.05));a4=float(st.number_input('Amplitud 4X',value=defaults[3],step=.05));noise=float(st.number_input('Ruido RMS',min_value=0.0,value=.05,step=.01))
        t,x=generate_synthetic(rpm,fs,duration,a1,a2,a3,a4,noise)
    else:
        up=st.file_uploader('CSV con tiempo y señal',type=['csv'])
        if up is None:
            st.info('Carga un CSV para analizarlo. Mientras tanto se muestra una señal de ejemplo.');t,x=generate_synthetic(rpm,2048,4,1,.2,.08,.03,.03)
        else:
            df=pd.read_csv(up);num=[c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
            if len(num)<2: st.error('El CSV requiere al menos dos columnas numéricas.');st.stop()
            tc=st.selectbox('Columna de tiempo',num,index=0);sc=st.selectbox('Columna de señal',num,index=1 if len(num)>1 else 0);d=df[[tc,sc]].dropna();t=d[tc].to_numpy(float);x=d[sc].to_numpy(float)

f,amp,fs_eff=spectrum(t,x,window);met=metrics(t,x,rpm if rpm>0 else None,window);peaks=top_peaks(f,amp,8);fr=rpm/60 if rpm>0 else None;orders=(f/fr if fr else None);env=analytic_envelope(x-np.mean(x));fenv,aenv,_=spectrum(t,env,window)

m1,m2,m3,m4,m5,m6=st.columns(6);m1.metric('RMS',f'{met.rms:.3f}');m2.metric('Pico',f'{met.peak:.3f}');m3.metric('Pico–pico',f'{met.p2p:.3f}');m4.metric('Cresta',f'{met.crest:.2f}');m5.metric('Dominante',f'{met.dominant_hz:.2f} Hz');m6.metric('Orden dom.','—' if met.dominant_order is None else f'{met.dominant_order:.2f}X')
st.markdown('<div class="gg-note"><b>Ruta de diagnóstico:</b> señal temporal → preparación/ventana → FFT → frecuencia dominante y órdenes → indicadores → interpretación física. Las firmas mostradas son didácticas y no constituyen un diagnóstico automático de falla.</div>',unsafe_allow_html=True)

tabs=st.tabs(['📊 Vista compacta','🎚️ Órdenes y picos','🧩 Sensor 3D','📡 Envolvente','📘 Teoría','🧠 Interpretación'])
with tabs[0]:
    left,right=st.columns([3.25,1.1])
    with left:
        a,b=st.columns(2);ft=go.Figure();ft.add_trace(go.Scatter(x=t,y=x,line=dict(color='#c8752d',width=1.7)));ft.update_layout(height=275,title='Forma de onda',xaxis_title='t [s]',yaxis_title='Amplitud',margin=dict(l=15,r=10,t=35,b=15));a.plotly_chart(ft,use_container_width=True)
        fspec=go.Figure();fspec.add_trace(go.Scatter(x=f,y=amp,line=dict(color='#4b4c50',width=1.8)));fspec.update_layout(height=275,title='Espectro FFT',xaxis_title='f [Hz]',yaxis_title='Amplitud',margin=dict(l=15,r=10,t=35,b=15));b.plotly_chart(fspec,use_container_width=True)
        c,d=st.columns(2)
        if fr:
            ford=go.Figure()
            ford.add_trace(go.Scatter(x=orders,y=amp,mode='lines',line=dict(color='#f28e1c',width=1.8),name='Espectro'))
            for order_mark in (1.0,2.0,3.0,4.0):
                ford.add_shape(type='line',x0=order_mark,x1=order_mark,y0=0,y1=1,yref='paper',line=dict(color='#999999',width=1,dash='dot'))
            order_limit=max(1.0,min(10.0,float(np.nanmax(orders))))
            ford.update_layout(height=255,title='Espectro por órdenes',xaxis_title='Orden X',yaxis_title='Amplitud',xaxis=dict(range=[0,order_limit]),margin=dict(l=15,r=10,t=35,b=15),showlegend=False)
            c.plotly_chart(ford,use_container_width=True,key='diag_orders_compact')
        else:c.info('Ingresa rpm > 0 para convertir el espectro a órdenes.')
        hist=go.Figure();hist.add_trace(go.Histogram(x=x,nbinsx=45,marker_color='#c8752d'));hist.update_layout(height=255,title='Distribución de amplitudes',xaxis_title='Amplitud',yaxis_title='Conteo',margin=dict(l=15,r=10,t=35,b=15));d.plotly_chart(hist,use_container_width=True)
    with right:
        st.markdown('### Picos principales');rows=[]
        for hz,a in peaks:
            rows.append({'f [Hz]':hz,'Orden X':(hz/fr if fr else np.nan),'Amplitud':a})
        st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True,height=250)
        st.markdown(f'''<div class="gg-card"><div class="gg-mini"><b>fs efectiva:</b> {fs_eff:.1f} Hz<br><b>Resolución aproximada:</b> {1/(t[-1]-t[0]):.3f} Hz<br><b>Ventana:</b> {window}<br><b>RPM referencia:</b> {rpm:.1f}</div></div>''',unsafe_allow_html=True)
with tabs[1]:
    st.subheader('Lectura por órdenes')
    if fr:
        max_order=max(1.0,min(20.0,float(np.nanmax(orders))))
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=orders,y=amp,mode='lines',line=dict(color='#c8752d',width=2),name='Espectro'))
        for order_mark in range(1,6):
            fig.add_shape(type='line',x0=float(order_mark),x1=float(order_mark),y0=0,y1=1,yref='paper',line=dict(color='#999999',width=1,dash='dot'))
            fig.add_annotation(x=float(order_mark),y=1.0,yref='paper',text=f'{order_mark}X',showarrow=False,yshift=8,font=dict(size=10,color='#666666'))
        fig.update_layout(height=390,xaxis_title='Orden X',yaxis_title='Amplitud',xaxis=dict(range=[0,max_order]),showlegend=False)
        st.plotly_chart(fig,use_container_width=True,key='diag_orders_detail')
        st.info('1X, 2X, 3X… son frecuencias sincronizadas con la velocidad de giro. Su presencia describe el contenido de la señal, pero una firma por sí sola no identifica de manera única una falla.')
    else: st.info('Ingresa una velocidad de referencia para trabajar en órdenes.')
with tabs[2]:
    st.subheader('Punto de medición y dirección del sensor')
    ampv=st.slider('Amplificación visual',.5,3.0,1.0,.1);idx=np.linspace(0,len(x)-1,min(900,len(x))).astype(int);render_diagnostics_3d({'signal':x[idx].tolist(),'duration':float(t[-1]-t[0]),'orientation':orientation,'visual_amp':ampv},height=560)
    st.caption('La máquina 3D es una representación didáctica del punto y dirección de medición; la animación se normaliza para hacer visible la vibración.')
with tabs[3]:
    st.subheader('Envolvente de la señal')
    a,b=st.columns(2);fe=go.Figure();fe.add_trace(go.Scatter(x=t,y=env,line=dict(color='#c8752d',width=1.8)));fe.update_layout(height=300,title='Envolvente temporal',xaxis_title='t [s]',yaxis_title='Envolvente');a.plotly_chart(fe,use_container_width=True);fes=go.Figure();fes.add_trace(go.Scatter(x=fenv,y=aenv,line=dict(color='#4b4c50',width=1.8)));fes.update_layout(height=300,title='Espectro de envolvente',xaxis_title='f [Hz]',yaxis_title='Amplitud');b.plotly_chart(fes,use_container_width=True)
    st.caption('La envolvente se incluye como herramienta exploratoria. Para diagnóstico de rodamientos reales suelen requerirse selección de banda, filtrado y conocimiento de frecuencias geométricas del rodamiento.')
with tabs[4]:
    st.latex(r'x_{RMS}=\sqrt{\frac{1}{T}\int_0^T x^2(t)\,dt}')
    st.latex(r'C_f=\frac{x_{pico}}{x_{RMS}}')
    st.latex(r'X(f)=\mathcal F\{x(t)\}')
    st.latex(r'\text{Orden}=\frac{f}{f_{rot}},\qquad f_{rot}=\frac{RPM}{60}')
    st.write('La ventana reduce fuga espectral cuando el registro no contiene un número entero de ciclos. La resolución en frecuencia depende principalmente de la duración total del registro.')
with tabs[5]:
    st.subheader('Interpretación descriptiva')
    if peaks:
        hz,a=peaks[0];ordtxt=f' ({hz/fr:.2f}X)' if fr else ''
        st.success(f'El componente espectral dominante del registro está cerca de {hz:.2f} Hz{ordtxt}, con amplitud aproximada {a:.3f}.')
    if met.crest>4: st.warning('El factor de cresta es elevado en este registro. Eso indica picos relativamente altos respecto del RMS, pero no determina por sí mismo su causa.')
    st.warning('No uses este módulo como diagnóstico automático de condición. En terreno deben considerarse dirección y ubicación del sensor, carga de la máquina, velocidad, historial, unidades, montaje del sensor y comparación con una línea base.')
