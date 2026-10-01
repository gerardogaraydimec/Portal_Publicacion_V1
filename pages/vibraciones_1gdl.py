from __future__ import annotations
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from modules.ui_brand import render_app_header
from modules.vibration_engine import solve_free_vibration, free_response, energies
from modules.vibration_visual3d import render_vibration_3d

st.markdown('''<style>.block-container{max-width:1480px;padding-top:1.2rem!important}.gg-note{border:1px solid #e9e2d7;border-left:4px solid #f28e1c;border-radius:12px;padding:.85rem 1rem;background:#fffaf3}.gg-card{border:1px solid #e7dfd2;border-radius:14px;background:#fffdf9;padding:1rem;height:100%}.gg-mini{font-size:.92rem;color:#555}</style>''',unsafe_allow_html=True)
render_app_header(title='Vibraciones · 1GDL',subtitle='Masa · rigidez · amortiguamiento · respuesta libre · energía · visualización 3D.',section='MÁQUINAS Y COMPONENTES',logo_width=188)

with st.sidebar:
    st.header('Sistema 1GDL')
    m=float(st.number_input('Masa m [kg]',min_value=.001,value=100.0,step=5.0))
    k=float(st.number_input('Rigidez k [N/m]',min_value=.001,value=40000.0,step=1000.0))
    c=float(st.number_input('Amortiguamiento c [N·s/m]',min_value=0.0,value=800.0,step=50.0))
    st.divider();st.subheader('Condiciones iniciales')
    x0_mm=float(st.number_input('Desplazamiento inicial x₀ [mm]',value=20.0,step=2.0))
    v0=float(st.number_input('Velocidad inicial v₀ [m/s]',value=0.0,step=.05,format='%.3f'))
    st.divider();st.subheader('Ventana temporal')
    duration=float(st.number_input('Duración [s]',min_value=.2,value=8.0,step=.5))

x0=x0_mm/1000
res=solve_free_vibration(m,k,c,x0,v0)
t=np.linspace(0,duration,1200);x,v,a=free_response(res,t);Ek,Ep,Et=energies(res,x,v)

c1,c2,c3,c4,c5=st.columns(5)
c1.metric('fₙ',f'{res.fn:.3f} Hz');c2.metric('ωₙ',f'{res.wn:.3f} rad/s');c3.metric('ζ',f'{res.zeta:.3f}');c4.metric('c crítico',f'{res.ccrit:.1f} N·s/m');c5.metric('Régimen',res.regime)

st.markdown('<div class="gg-note"><b>Ruta física:</b> parámetros m, k, c → ecuación de movimiento → frecuencias y amortiguamiento → respuesta x(t) → fuerzas internas y disipación de energía.</div>',unsafe_allow_html=True)

tabs=st.tabs(['📘 Concepto','🧩 Sistema 3D','📈 Respuesta temporal','⚡ Energía','⚖️ Comparador','∑ Ecuaciones','🧠 Interpretación'])

with tabs[0]:
    st.subheader('Sistema masa–resorte–amortiguador')
    st.latex(r'm\ddot x+c\dot x+kx=0')
    a1,a2,a3=st.columns(3)
    with a1: st.markdown('<div class="gg-card"><b>Inercia</b><div class="gg-mini">La masa se opone a cambios de velocidad. El término asociado es m·ẍ.</div></div>',unsafe_allow_html=True)
    with a2: st.markdown('<div class="gg-card"><b>Elasticidad</b><div class="gg-mini">El resorte almacena energía y genera una fuerza restauradora −kx.</div></div>',unsafe_allow_html=True)
    with a3: st.markdown('<div class="gg-card"><b>Amortiguamiento</b><div class="gg-mini">El amortiguador disipa energía mediante una fuerza −cẋ.</div></div>',unsafe_allow_html=True)
    st.markdown('### Qué determina el movimiento')
    st.latex(r'\omega_n=\sqrt{\frac{k}{m}},\qquad c_c=2\sqrt{km},\qquad \zeta=\frac{c}{c_c}')
    if res.zeta<1: st.info('ζ < 1: el sistema oscila alrededor del equilibrio con amplitud decreciente cuando c > 0.',icon='〰️')
    elif abs(res.zeta-1)<1e-6: st.info('ζ = 1: retorno no oscilatorio más rápido dentro del modelo lineal.',icon='🎯')
    else: st.info('ζ > 1: retorno no oscilatorio dominado por dos exponentes reales.',icon='🧭')

with tabs[1]:
    st.subheader('Movimiento 3D del sistema')
    l,r=st.columns([1,2])
    with l:
        vamp=st.slider('Amplificación visual',0.5,2.0,1.0,.1)
        speed=st.slider('Velocidad de animación',0.25,2.0,1.0,.25)
        st.markdown('<div class="gg-card"><b>Qué representa el visor</b><div class="gg-mini">La masa se desplaza según x(t). El resorte y el amortiguador cambian de longitud con ella. Las flechas representan las fuerzas restauradora −kx y disipativa −cẋ. La línea vertical marca la posición de equilibrio.</div></div>',unsafe_allow_html=True)
    with r:
        idx=np.linspace(0,len(t)-1,500).astype(int)
        render_vibration_3d({'t':t[idx].tolist(),'x':x[idx].tolist(),'v':v[idx].tolist(),'m':m,'k':k,'c':c,'fn':res.fn,'zeta':res.zeta,'regime':res.regime,'duration':duration,'visual_amp':vamp,'speed':speed},height=690)
    st.caption('La escala geométrica del desplazamiento se amplifica para lectura visual. Los valores numéricos de x(t), v(t) y a(t) permanecen físicos.')

with tabs[2]:
    st.subheader('Respuesta temporal')
    q=go.Figure();q.add_trace(go.Scatter(x=t,y=1000*x,name='x(t)',line=dict(color='#c8752d',width=3)));q.update_layout(height=360,xaxis_title='t [s]',yaxis_title='x [mm]',margin=dict(l=20,r=20,t=15,b=20));st.plotly_chart(q,use_container_width=True)
    c1,c2=st.columns(2)
    qv=go.Figure();qv.add_trace(go.Scatter(x=t,y=v,line=dict(color='#4b4c50',width=2)));qv.update_layout(height=310,xaxis_title='t [s]',yaxis_title='v [m/s]',margin=dict(l=20,r=20,t=15,b=20));c1.plotly_chart(qv,use_container_width=True)
    qa=go.Figure();qa.add_trace(go.Scatter(x=t,y=a,line=dict(color='#f28e1c',width=2)));qa.update_layout(height=310,xaxis_title='t [s]',yaxis_title='a [m/s²]',margin=dict(l=20,r=20,t=15,b=20));c2.plotly_chart(qa,use_container_width=True)

with tabs[3]:
    st.subheader('Intercambio y disipación de energía')
    qe=go.Figure();qe.add_trace(go.Scatter(x=t,y=Ek,name='Cinética ½mv²'));qe.add_trace(go.Scatter(x=t,y=Ep,name='Elástica ½kx²'));qe.add_trace(go.Scatter(x=t,y=Et,name='Mecánica total',line=dict(width=3)));qe.update_layout(height=410,xaxis_title='t [s]',yaxis_title='Energía [J]',margin=dict(l=20,r=20,t=15,b=20));st.plotly_chart(qe,use_container_width=True)
    if c==0: st.info('Con c = 0 la energía mecánica total se conserva dentro del modelo ideal.',icon='♻️')
    else: st.info('Con c > 0 la energía mecánica disminuye porque el amortiguador disipa potencia instantánea c·ẋ².',icon='⚡')

with tabs[4]:
    st.subheader('Comparador A/B')
    st.write('El caso A corresponde al sistema definido en la barra lateral. El caso B permite cambiar m, k y c manteniendo las mismas condiciones iniciales para comparar solamente el sistema dinámico.')
    b1,b2,b3=st.columns(3)
    mb=float(b1.number_input('B · masa m [kg]',min_value=.001,value=float(m),step=5.0,key='vb_m'))
    kb=float(b2.number_input('B · rigidez k [N/m]',min_value=.001,value=float(k*1.5),step=1000.0,key='vb_k'))
    cb=float(b3.number_input('B · amortiguamiento c [N·s/m]',min_value=0.0,value=float(c),step=50.0,key='vb_c'))
    rb=solve_free_vibration(mb,kb,cb,x0,v0);xb,vb,ab=free_response(rb,t)
    qcmp=go.Figure();qcmp.add_trace(go.Scatter(x=t,y=1000*x,name='A'));qcmp.add_trace(go.Scatter(x=t,y=1000*xb,name='B'));qcmp.update_layout(height=390,xaxis_title='t [s]',yaxis_title='x [mm]',margin=dict(l=20,r=20,t=15,b=20));st.plotly_chart(qcmp,use_container_width=True)
    m1,m2,m3,m4=st.columns(4);m1.metric('fₙ B / A',f'{rb.fn/res.fn:.3f}');m2.metric('ζ B / A',f'{rb.zeta/max(res.zeta,1e-12):.3f}' if res.zeta>0 else '—');m3.metric('cᶜ B / A',f'{rb.ccrit/res.ccrit:.3f}');m4.metric('Tₙ B / A',f'{rb.period/res.period:.3f}')
    st.markdown('**Lectura:** aumentar k eleva la frecuencia natural; aumentar m la reduce; modificar c cambia principalmente el decaimiento y el carácter oscilatorio a través de ζ.')

with tabs[5]:
    st.subheader('Ecuaciones organizadas por significado')
    st.markdown('**Ecuación de movimiento**');st.latex(r'm\ddot x+c\dot x+kx=0')
    st.markdown('**Propiedades naturales**');st.latex(r'\omega_n=\sqrt{\frac{k}{m}},\qquad f_n=\frac{\omega_n}{2\pi},\qquad T_n=\frac{2\pi}{\omega_n}')
    st.markdown('**Amortiguamiento**');st.latex(r'c_c=2\sqrt{km},\qquad \zeta=\frac{c}{c_c}')
    st.markdown('**Caso subamortiguado**');st.latex(r'\omega_d=\omega_n\sqrt{1-\zeta^2}')
    st.latex(r'x(t)=e^{-\zeta\omega_n t}\left[x_0\cos(\omega_d t)+\frac{v_0+\zeta\omega_n x_0}{\omega_d}\sin(\omega_d t)\right]')
    st.markdown('**Energía**');st.latex(r'E_k=\frac12m\dot x^2,\qquad E_p=\frac12kx^2,\qquad \dot E=-c\dot x^2')

with tabs[6]:
    st.subheader('Interpretación')
    p1,p2=st.columns(2)
    with p1:
        st.markdown(f'<div class="gg-card"><b>Dinámica del sistema</b><div class="gg-mini">fₙ = <b>{res.fn:.3f} Hz</b>, ζ = <b>{res.zeta:.3f}</b> y el régimen es <b>{res.regime}</b>. Estos tres datos condensan gran parte del comportamiento libre del sistema.</div></div>',unsafe_allow_html=True)
        if res.wd: st.markdown(f'<div class="gg-card"><b>Frecuencia amortiguada</b><div class="gg-mini">fᵈ = <b>{res.fd:.3f} Hz</b>. Es menor que fₙ porque el amortiguamiento modifica la frecuencia de la oscilación libre.</div></div>',unsafe_allow_html=True)
    with p2:
        if res.log_decrement is not None: st.markdown(f'<div class="gg-card"><b>Decaimiento</b><div class="gg-mini">Decremento logarítmico δ = <b>{res.log_decrement:.3f}</b>. Relaciona dos máximos separados por un período amortiguado.</div></div>',unsafe_allow_html=True)
        if res.tau_decay is not None: st.markdown(f'<div class="gg-card"><b>Escala temporal</b><div class="gg-mini">Tiempo característico de decaimiento ≈ <b>{res.tau_decay:.3f} s</b>. Es una guía para interpretar cuánto tarda la respuesta en reducirse.</div></div>',unsafe_allow_html=True)
        st.info('Este módulo estudia vibración libre. La excitación armónica, resonancia, transmisibilidad y desfase permanecen en la herramienta existente de Vibración Forzada, que mejoraremos en la etapa siguiente.',icon='ℹ️')
