from __future__ import annotations
import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from modules.ui_brand import render_app_header
from modules.vibration_engine import solve_free_vibration, free_response, energies
from modules.vibration_visual3d import render_vibration_3d

st.markdown('''
<style>
.block-container{max-width:1480px;padding-top:1.0rem!important}
.gg-note{border:1px solid #e9e2d7;border-left:4px solid #f28e1c;border-radius:12px;padding:.72rem .9rem;background:#fffaf3}
.gg-card{border:1px solid #e7dfd2;border-radius:13px;background:#fffdf9;padding:.78rem .88rem;height:100%}
.gg-mini{font-size:.88rem;color:#555;line-height:1.38}
.gg-kv{display:grid;grid-template-columns:1fr auto;gap:.22rem .7rem;font-size:.88rem;line-height:1.35}
.gg-kv b{text-align:right;color:#202126}
[data-testid="stMetric"]{padding:.2rem 0}
</style>
''', unsafe_allow_html=True)

render_app_header(
    title='Vibraciones · 1GDL',
    subtitle='Respuesta libre · plano de fase · masa–resorte–amortiguador · energía · visualización 3D.',
    section='MÁQUINAS Y COMPONENTES',
    logo_width=188,
)

with st.sidebar:
    st.header('Sistema 1GDL')
    m=float(st.number_input('Masa m [kg]',min_value=.001,value=100.0,step=5.0))
    k=float(st.number_input('Rigidez k [N/m]',min_value=.001,value=40000.0,step=1000.0))
    c=float(st.number_input('Amortiguamiento c [N·s/m]',min_value=0.0,value=800.0,step=50.0))
    st.divider(); st.subheader('Condiciones iniciales')
    x0_mm=float(st.number_input('Desplazamiento inicial x₀ [mm]',value=20.0,step=2.0))
    v0=float(st.number_input('Velocidad inicial v₀ [m/s]',value=0.0,step=.05,format='%.3f'))
    st.divider(); st.subheader('Ventana temporal')
    duration=float(st.number_input('Duración [s]',min_value=.2,value=8.0,step=.5))

x0=x0_mm/1000.0
res=solve_free_vibration(m,k,c,x0,v0)
t=np.linspace(0,duration,1200)
x,v,a=free_response(res,t)
Ek,Ep,Et=energies(res,x,v)

# Raíces características para recuperar la lectura compacta anterior.
if res.zeta < 1-1e-7:
    r_real=-res.zeta*res.wn
    roots_txt=f'{r_real:.3f} ± j{res.wd:.3f}'
elif abs(res.zeta-1)<=1e-7:
    roots_txt=f'{-res.wn:.3f} (doble)'
else:
    s=math.sqrt(res.zeta**2-1)
    r1=-res.wn*(res.zeta-s)
    r2=-res.wn*(res.zeta+s)
    roots_txt=f'{r1:.3f}, {r2:.3f}'

m1,m2,m3,m4,m5=st.columns(5)
m1.metric('fₙ',f'{res.fn:.3f} Hz')
m2.metric('ωₙ',f'{res.wn:.3f} rad/s')
m3.metric('ζ',f'{res.zeta:.3f}')
m4.metric('c crítico',f'{res.ccrit:.1f} N·s/m')
m5.metric('Régimen',res.regime)

st.markdown('<div class="gg-note"><b>Ruta física:</b> m, k, c + condiciones iniciales → ecuación de movimiento → respuesta temporal → plano de fase → fuerzas y energía.</div>',unsafe_allow_html=True)

tabs=st.tabs(['📊 Vista compacta','🧩 Sistema 3D','⚡ Energía','⚖️ Comparador','📘 Teoría y ecuaciones','🧠 Interpretación'])

with tabs[0]:
    left,right=st.columns([3.25,1.15],gap='medium')
    with left:
        r1,r2=st.columns(2,gap='small')
        figx=go.Figure()
        figx.add_trace(go.Scatter(x=t,y=1000*x,line=dict(color='#c8752d',width=2.6),name='x(t)'))
        figx.add_hline(y=0,line_dash='dash',line_color='#9a9ca1')
        figx.update_layout(height=255,title='Desplazamiento',xaxis_title='t [s]',yaxis_title='x [mm]',margin=dict(l=15,r=10,t=35,b=15),showlegend=False)
        r1.plotly_chart(figx,use_container_width=True,key='vib_x')

        figph=go.Figure()
        figph.add_trace(go.Scatter(x=1000*x,y=v,mode='lines',line=dict(color='#f28e1c',width=2.4),name='trayectoria'))
        figph.add_trace(go.Scatter(x=[1000*x[0]],y=[v[0]],mode='markers',marker=dict(size=8,color='#c8752d'),name='inicio'))
        figph.add_trace(go.Scatter(x=[0],y=[0],mode='markers',marker=dict(size=8,color='#202126',symbol='x'),name='equilibrio'))
        figph.update_layout(height=255,title='Plano de fase',xaxis_title='x [mm]',yaxis_title='ẋ [m/s]',margin=dict(l=15,r=10,t=35,b=15),showlegend=False)
        r2.plotly_chart(figph,use_container_width=True,key='vib_phase')

        r3,r4=st.columns(2,gap='small')
        figv=go.Figure()
        figv.add_trace(go.Scatter(x=t,y=v,line=dict(color='#4b4c50',width=2.1)))
        figv.add_hline(y=0,line_dash='dash',line_color='#b3b4b7')
        figv.update_layout(height=240,title='Velocidad',xaxis_title='t [s]',yaxis_title='ẋ [m/s]',margin=dict(l=15,r=10,t=35,b=15),showlegend=False)
        r3.plotly_chart(figv,use_container_width=True,key='vib_v')

        figa=go.Figure()
        figa.add_trace(go.Scatter(x=t,y=a,line=dict(color='#8c8e93',width=2.1)))
        figa.add_hline(y=0,line_dash='dash',line_color='#b3b4b7')
        figa.update_layout(height=240,title='Aceleración',xaxis_title='t [s]',yaxis_title='ẍ [m/s²]',margin=dict(l=15,r=10,t=35,b=15),showlegend=False)
        r4.plotly_chart(figa,use_container_width=True,key='vib_a')

    with right:
        st.markdown('### Lectura del sistema')
        st.markdown(f'''
<div class="gg-card">
<div class="gg-kv">
<span>Masa m</span><b>{m:.3f} kg</b>
<span>Rigidez k</span><b>{k:.1f} N/m</b>
<span>Amortiguamiento c</span><b>{c:.1f} N·s/m</b>
<span>ωₙ</span><b>{res.wn:.3f} rad/s</b>
<span>fₙ</span><b>{res.fn:.3f} Hz</b>
<span>ζ</span><b>{res.zeta:.3f}</b>
<span>Raíces s</span><b>{roots_txt}</b>
</div></div>
''',unsafe_allow_html=True)
        st.markdown('#### Régimen')
        if res.zeta < 1-1e-7:
            if res.zeta <= 1e-7:
                st.info('No amortiguado: trayectoria cerrada en fase y energía mecánica constante en el modelo ideal.',icon='〰️')
            else:
                st.info('Subamortiguado: el plano de fase forma una espiral hacia el equilibrio.',icon='🌀')
        elif abs(res.zeta-1)<=1e-7:
            st.info('Crítico: retorno no oscilatorio al equilibrio con raíz real doble.',icon='🎯')
        else:
            st.info('Sobreamortiguado: retorno no oscilatorio dominado por dos raíces reales negativas.',icon='🧭')
        st.latex(r'm\ddot x+c\dot x+kx=0')
        st.caption('El plano de fase usa el estado (x, ẋ): cada punto indica simultáneamente posición y velocidad.')

with tabs[1]:
    st.subheader('Sistema masa–resorte–amortiguador en 3D')
    l,r=st.columns([1,2.4],gap='medium')
    with l:
        vamp=st.slider('Amplificación visual del desplazamiento',0.5,2.5,1.0,.1)
        speed=st.slider('Velocidad de animación',0.25,2.0,1.0,.25)
        show_motion=st.toggle('Flecha de movimiento v(t)',value=True)
        show_forces=st.toggle('Fuerzas −kx y −cẋ',value=True)
        show_dimension=st.toggle('Mostrar desplazamiento respecto del equilibrio',value=True)
        st.markdown('''<div class="gg-card"><b>Lectura del visor</b><div class="gg-mini">
<b>Marfil:</b> sentido instantáneo de movimiento v(t).<br>
<b>Naranja:</b> fuerza del resorte Fₖ = −kx.<br>
<b>Gris:</b> fuerza viscosa F꜀ = −cẋ.<br><br>
La flecha fija <b>+x</b> define el sentido positivo. La línea de equilibrio permanece inmóvil mientras la masa oscila.
</div></div>''',unsafe_allow_html=True)
    with r:
        idx=np.linspace(0,len(t)-1,520).astype(int)
        render_vibration_3d({
            't':t[idx].tolist(),
            'x':x[idx].tolist(),
            'v':v[idx].tolist(),
            'a':a[idx].tolist(),
            'm':m,'k':k,'c':c,
            'fn':res.fn,'zeta':res.zeta,'regime':res.regime,
            'duration':duration,'visual_amp':vamp,'speed':speed,
            'show_motion':show_motion,'show_forces':show_forces,'show_dimension':show_dimension,
        },height=625)
    st.caption('La amplitud geométrica del movimiento puede amplificarse para lectura visual. x(t), ẋ(t), ẍ(t) y las fuerzas se calculan con los valores físicos reales.')

with tabs[2]:
    st.subheader('Intercambio y disipación de energía')
    e1,e2=st.columns([2.2,1])
    with e1:
        qe=go.Figure()
        qe.add_trace(go.Scatter(x=t,y=Ek,name='Cinética ½mẋ²'))
        qe.add_trace(go.Scatter(x=t,y=Ep,name='Elástica ½kx²'))
        qe.add_trace(go.Scatter(x=t,y=Et,name='Mecánica total',line=dict(width=3,color='#c8752d')))
        qe.update_layout(height=380,xaxis_title='t [s]',yaxis_title='Energía [J]',margin=dict(l=20,r=20,t=15,b=20))
        st.plotly_chart(qe,use_container_width=True,key='vib_energy')
    with e2:
        st.latex(r'E_k=\frac12m\dot x^2')
        st.latex(r'E_p=\frac12kx^2')
        st.latex(r'\dot E=-c\dot x^2')
        if c==0:
            st.info('Con c = 0 la energía mecánica total se conserva dentro del modelo ideal.',icon='♻️')
        else:
            st.info('Con c > 0 la energía mecánica disminuye porque el amortiguador disipa energía.',icon='⚡')

with tabs[3]:
    st.subheader('Comparador A/B')
    st.write('El caso A corresponde al sistema principal. El caso B cambia m, k y c manteniendo las mismas condiciones iniciales.')
    b1,b2,b3=st.columns(3)
    mb=float(b1.number_input('B · masa m [kg]',min_value=.001,value=float(m),step=5.0,key='vb_m'))
    kb=float(b2.number_input('B · rigidez k [N/m]',min_value=.001,value=float(k*1.5),step=1000.0,key='vb_k'))
    cb=float(b3.number_input('B · amortiguamiento c [N·s/m]',min_value=0.0,value=float(c),step=50.0,key='vb_c'))
    rb=solve_free_vibration(mb,kb,cb,x0,v0)
    xb,vb,ab=free_response(rb,t)
    p1,p2=st.columns(2)
    qcmp=go.Figure()
    qcmp.add_trace(go.Scatter(x=t,y=1000*x,name='A',line=dict(width=2.4)))
    qcmp.add_trace(go.Scatter(x=t,y=1000*xb,name='B',line=dict(width=2.4)))
    qcmp.update_layout(height=330,xaxis_title='t [s]',yaxis_title='x [mm]',margin=dict(l=20,r=20,t=15,b=20))
    p1.plotly_chart(qcmp,use_container_width=True,key='vib_cmp_time')
    qphase=go.Figure()
    qphase.add_trace(go.Scatter(x=1000*x,y=v,name='A',mode='lines'))
    qphase.add_trace(go.Scatter(x=1000*xb,y=vb,name='B',mode='lines'))
    qphase.update_layout(height=330,xaxis_title='x [mm]',yaxis_title='ẋ [m/s]',margin=dict(l=20,r=20,t=15,b=20))
    p2.plotly_chart(qphase,use_container_width=True,key='vib_cmp_phase')
    q1,q2,q3,q4=st.columns(4)
    q1.metric('fₙ B / A',f'{rb.fn/res.fn:.3f}')
    q2.metric('ζ B / A',f'{rb.zeta/max(res.zeta,1e-12):.3f}' if res.zeta>0 else '—')
    q3.metric('cᶜ B / A',f'{rb.ccrit/res.ccrit:.3f}')
    q4.metric('Tₙ B / A',f'{rb.period/res.period:.3f}')

with tabs[4]:
    st.subheader('Teoría y ecuaciones')
    a1,a2,a3=st.columns(3)
    with a1:
        st.markdown('<div class="gg-card"><b>Inercia</b><div class="gg-mini">La masa se opone al cambio del movimiento. Su término es m·ẍ.</div></div>',unsafe_allow_html=True)
    with a2:
        st.markdown('<div class="gg-card"><b>Elasticidad</b><div class="gg-mini">El resorte genera una fuerza restauradora Fₖ = −kx y almacena energía.</div></div>',unsafe_allow_html=True)
    with a3:
        st.markdown('<div class="gg-card"><b>Amortiguamiento</b><div class="gg-mini">El amortiguador genera F꜀ = −cẋ y disipa energía mecánica.</div></div>',unsafe_allow_html=True)
    st.markdown('**Ecuación de movimiento**')
    st.latex(r'm\ddot x+c\dot x+kx=0')
    st.markdown('**Ecuación característica**')
    st.latex(r'm s^2+c s+k=0')
    st.markdown('**Propiedades naturales**')
    st.latex(r'\omega_n=\sqrt{\frac{k}{m}},\qquad f_n=\frac{\omega_n}{2\pi},\qquad T_n=\frac{2\pi}{\omega_n}')
    st.markdown('**Amortiguamiento**')
    st.latex(r'c_c=2\sqrt{km},\qquad \zeta=\frac{c}{c_c}')
    st.markdown('**Caso subamortiguado**')
    st.latex(r'\omega_d=\omega_n\sqrt{1-\zeta^2}')
    st.latex(r'x(t)=e^{-\zeta\omega_n t}\left[x_0\cos(\omega_d t)+\frac{v_0+\zeta\omega_n x_0}{\omega_d}\sin(\omega_d t)\right]')
    st.markdown('**Estado en el plano de fase**')
    st.latex(r'\mathbf z(t)=\begin{bmatrix}x(t)\\\dot x(t)\end{bmatrix}')

with tabs[5]:
    st.subheader('Interpretación')
    p1,p2=st.columns(2)
    with p1:
        st.markdown(f'<div class="gg-card"><b>Dinámica del sistema</b><div class="gg-mini">fₙ = <b>{res.fn:.3f} Hz</b>, ζ = <b>{res.zeta:.3f}</b> y el régimen es <b>{res.regime}</b>. Las raíces características son <b>{roots_txt}</b>.</div></div>',unsafe_allow_html=True)
        if res.wd:
            st.markdown(f'<div class="gg-card"><b>Frecuencia amortiguada</b><div class="gg-mini">fᵈ = <b>{res.fd:.3f} Hz</b>. El plano de fase permite ver simultáneamente el decaimiento de posición y velocidad.</div></div>',unsafe_allow_html=True)
    with p2:
        if res.log_decrement is not None:
            st.markdown(f'<div class="gg-card"><b>Decaimiento</b><div class="gg-mini">Decremento logarítmico δ = <b>{res.log_decrement:.3f}</b>.</div></div>',unsafe_allow_html=True)
        if res.tau_decay is not None:
            st.markdown(f'<div class="gg-card"><b>Escala temporal</b><div class="gg-mini">Tiempo característico de decaimiento ≈ <b>{res.tau_decay:.3f} s</b>.</div></div>',unsafe_allow_html=True)
        st.info('Este módulo sigue dedicado a vibración libre. La herramienta existente de Vibración Forzada permanece separada y no ha sido modificada.',icon='ℹ️')
