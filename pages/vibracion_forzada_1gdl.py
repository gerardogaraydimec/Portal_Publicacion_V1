from __future__ import annotations
import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from modules.ui_brand import render_app_header
from modules.vibration_forced_engine import solve_forced_vibration, steady_response, frequency_response, force_balance_residual
from modules.vibration_forced_visual3d import render_forced_vibration_3d

st.markdown('''
<style>
.block-container{max-width:1480px;padding-top:1.0rem!important}
.gg-note{border:1px solid #e9e2d7;border-left:4px solid #f28e1c;border-radius:12px;padding:.72rem .9rem;background:#fffaf3}
.gg-card{border:1px solid #e7dfd2;border-radius:13px;background:#fffdf9;padding:.78rem .88rem;height:100%}
.gg-mini{font-size:.88rem;color:#555;line-height:1.38}
.gg-kv{display:grid;grid-template-columns:1fr auto;gap:.22rem .7rem;font-size:.88rem;line-height:1.35}.gg-kv b{text-align:right;color:#202126}
[data-testid="stMetric"]{padding:.2rem 0}
</style>
''', unsafe_allow_html=True)

render_app_header(
    title='Vibración forzada · 1GDL',
    subtitle='Excitación armónica · resonancia · desfase · amplificación dinámica · transmisibilidad · visualización 3D.',
    section='MÁQUINAS Y COMPONENTES',
    logo_width=188,
)

with st.sidebar:
    st.header('Sistema 1GDL')
    m=float(st.number_input('Masa m [kg]',min_value=.001,value=100.0,step=5.0))
    k=float(st.number_input('Rigidez k [N/m]',min_value=.001,value=40000.0,step=1000.0))
    c=float(st.number_input('Amortiguamiento c [N·s/m]',min_value=0.0,value=800.0,step=50.0))
    st.divider(); st.subheader('Excitación armónica')
    F0=float(st.number_input('Amplitud F₀ [N]',min_value=0.0,value=1000.0,step=100.0))
    # frecuencia natural preliminar para dar un valor inicial cercano a interés didáctico
    fn0=math.sqrt(k/m)/(2*math.pi)
    f_exc=float(st.number_input('Frecuencia de excitación f [Hz]',min_value=0.0,value=float(round(fn0*.80,3)),step=.10,format='%.3f'))
    st.divider(); st.subheader('Ventana temporal')
    cycles=float(st.number_input('Ciclos a mostrar',min_value=1.0,value=6.0,step=1.0))

res=solve_forced_vibration(m,k,c,F0,f_exc)
if f_exc>0:
    duration=cycles/f_exc
else:
    duration=max(2.0,cycles/max(res.fn,1e-6))
t=np.linspace(0,duration,1000)
F,x,v,a,fk,fc,ft=steady_response(res,t)

fmt_inf=lambda val,suf='': ('∞' if not math.isfinite(val) else f'{val:.3f}{suf}')

m1,m2,m3,m4,m5,m6=st.columns(6)
m1.metric('fₙ',f'{res.fn:.3f} Hz')
m2.metric('ζ',f'{res.zeta:.3f}')
m3.metric('r = f/fₙ',f'{res.r:.3f}')
m4.metric('H = X/(F₀/k)',fmt_inf(res.magnification))
m5.metric('Desfase δ',f'{res.phase_deg:.1f}°')
m6.metric('Amplitud X','∞' if res.singular else f'{1000*res.amplitude_m:.2f} mm')

st.markdown('<div class="gg-note"><b>Ruta física:</b> F(t)=F₀ sin(ωt) → razón de frecuencia r → amplificación H(r,ζ) + desfase δ → respuesta x(t) → fuerza transmitida a la base.</div>',unsafe_allow_html=True)

if res.singular:
    st.error('Caso ideal singular: c = 0 y r = 1. El modelo lineal estacionario predice amplitud no acotada. Introduce amortiguamiento o cambia la frecuencia para visualizar una respuesta estacionaria finita.',icon='⚠️')

tabs=st.tabs(['📊 Vista compacta','🧩 Sistema 3D','🎯 Resonancia y aislamiento','⚙️ Fuerzas y fase','⚖️ Comparador','📘 Teoría y ecuaciones','🧠 Interpretación'])

rgrid,Hgrid,phasegrid,TRgrid=frequency_response(res.zeta,3.0,750)
Hcap=np.clip(Hgrid,0,12)
TRcap=np.clip(TRgrid,0,12)

with tabs[0]:
    left,right=st.columns([3.25,1.15],gap='medium')
    with left:
        q1,q2=st.columns(2,gap='small')
        if not res.singular:
            figt=make_subplots(specs=[[{'secondary_y':True}]])
            figt.add_trace(go.Scatter(x=t,y=1000*x,name='x(t)',line=dict(color='#c8752d',width=2.5)),secondary_y=False)
            figt.add_trace(go.Scatter(x=t,y=F,name='F(t)',line=dict(color='#4b4c50',width=1.7,dash='dot')),secondary_y=True)
            figt.update_yaxes(title_text='x [mm]',secondary_y=False);figt.update_yaxes(title_text='F [N]',secondary_y=True)
            figt.update_layout(height=255,title='Excitación y respuesta',xaxis_title='t [s]',margin=dict(l=15,r=15,t=35,b=15),legend=dict(orientation='h',y=1.08,x=.02))
            q1.plotly_chart(figt,use_container_width=True,key='vf_time')

            figph=go.Figure();figph.add_trace(go.Scatter(x=1000*x,y=v,mode='lines',line=dict(color='#f28e1c',width=2.4)))
            figph.add_trace(go.Scatter(x=[0],y=[0],mode='markers',marker=dict(size=8,color='#202126',symbol='x')))
            figph.update_layout(height=255,title='Plano de fase',xaxis_title='x [mm]',yaxis_title='ẋ [m/s]',margin=dict(l=15,r=10,t=35,b=15),showlegend=False)
            q2.plotly_chart(figph,use_container_width=True,key='vf_phase')
        else:
            q1.warning('No hay respuesta estacionaria finita para representar en el caso singular ideal.')
            q2.warning('El plano de fase estacionario tampoco está definido en esta condición ideal.')

        q3,q4=st.columns(2,gap='small')
        figh=go.Figure();figh.add_trace(go.Scatter(x=rgrid,y=Hcap,line=dict(color='#c8752d',width=2.6),name='H'))
        if math.isfinite(res.magnification):figh.add_trace(go.Scatter(x=[res.r],y=[min(res.magnification,12)],mode='markers',marker=dict(size=9,color='#202126'),name='caso'))
        figh.add_vline(x=1,line_dash='dash',line_color='#9a9ca1');figh.update_layout(height=240,title='Amplificación dinámica',xaxis_title='r = ω/ωₙ',yaxis_title='H',margin=dict(l=15,r=10,t=35,b=15),showlegend=False)
        q3.plotly_chart(figh,use_container_width=True,key='vf_H')

        figd=go.Figure();figd.add_trace(go.Scatter(x=rgrid,y=phasegrid,line=dict(color='#4b4c50',width=2.4)))
        figd.add_trace(go.Scatter(x=[res.r],y=[res.phase_deg],mode='markers',marker=dict(size=9,color='#f28e1c')))
        figd.add_vline(x=1,line_dash='dash',line_color='#9a9ca1');figd.update_layout(height=240,title='Desfase fuerza–respuesta',xaxis_title='r = ω/ωₙ',yaxis_title='δ [°]',margin=dict(l=15,r=10,t=35,b=15),showlegend=False,yaxis=dict(range=[0,180]))
        q4.plotly_chart(figd,use_container_width=True,key='vf_delta')

    with right:
        st.markdown('### Lectura del caso')
        st.markdown(f'''
<div class="gg-card"><div class="gg-kv">
<span>m</span><b>{m:.3f} kg</b><span>k</span><b>{k:.1f} N/m</b><span>c</span><b>{c:.1f} N·s/m</b>
<span>F₀</span><b>{F0:.1f} N</b><span>f</span><b>{f_exc:.3f} Hz</b><span>fₙ</span><b>{res.fn:.3f} Hz</b>
<span>r</span><b>{res.r:.3f}</b><span>H</span><b>{fmt_inf(res.magnification)}</b><span>δ</span><b>{res.phase_deg:.1f}°</b>
<span>X</span><b>{'∞' if res.singular else f'{1000*res.amplitude_m:.2f} mm'}</b><span>Tᵣ</span><b>{fmt_inf(res.transmissibility)}</b>
</div></div>''',unsafe_allow_html=True)
        st.markdown('#### Lectura física')
        if res.r < .7:
            st.info('r ≪ 1: respuesta dominada principalmente por la rigidez. El desplazamiento sigue aproximadamente a la fuerza.',icon='↔️')
        elif res.r < 1.3:
            st.warning('Zona cercana a resonancia: la respuesta es muy sensible al amortiguamiento y a pequeños cambios de frecuencia.',icon='🎯')
        else:
            st.info('r > 1: crece el papel de la inercia y el desplazamiento se aproxima a 180° de desfase respecto de la fuerza.',icon='🧭')
        if res.r > math.sqrt(2):
            st.success('r > √2: para excitación por fuerza, la transmisibilidad de fuerza puede ser menor que 1; comienza la zona de aislamiento.',icon='✅')

with tabs[1]:
    st.subheader('Sistema 3D excitado armónicamente')
    l,r=st.columns([1,2.4],gap='medium')
    with l:
        vamp=st.slider('Amplificación visual del desplazamiento',0.5,2.5,1.0,.1,key='vf_amp')
        speed=st.slider('Velocidad de animación',0.25,2.0,1.0,.25,key='vf_speed')
        show_force=st.toggle('Mostrar fuerza excitadora F(t)',value=True)
        show_motion=st.toggle('Mostrar sentido de movimiento v(t)',value=True)
        show_trans=st.toggle('Mostrar fuerza transmitida Fₜ',value=True)
        show_internal=st.toggle('Mostrar fuerzas internas Fₖ y F꜀',value=False)
        st.markdown('''<div class="gg-card"><b>Lectura del visor</b><div class="gg-mini">
<b>Naranja:</b> fuerza excitadora F(t).<br><b>Marfil:</b> sentido instantáneo v(t).<br><b>Gris:</b> fuerza transmitida a la base Fₜ=kx+cẋ.<br><b>Cobre / gris oscuro:</b> fuerzas de resorte y amortiguador cuando se activan.<br><br>La diferencia temporal entre F(t) y x(t) hace visible el <b>desfase δ</b>.</div></div>''',unsafe_allow_html=True)
    with r:
        if res.singular:
            st.warning('El caso singular ideal no puede animarse como una respuesta estacionaria finita.')
        else:
            idx=np.linspace(0,len(t)-1,520).astype(int)
            render_forced_vibration_3d({'t':t[idx].tolist(),'x':x[idx].tolist(),'v':v[idx].tolist(),'F':F[idx].tolist(),'fk':fk[idx].tolist(),'fc':fc[idx].tolist(),'ft':ft[idx].tolist(),'m':m,'k':k,'c':c,'duration':duration,'visual_amp':vamp,'speed':speed,'r':res.r,'H':res.magnification,'phase_deg':res.phase_deg,'show_force':show_force,'show_motion':show_motion,'show_transmitted':show_trans,'show_internal':show_internal},height=620)
    st.caption('La animación representa la solución estacionaria armónica. La amplificación visual solo cambia la escala del movimiento en pantalla.')

with tabs[2]:
    st.subheader('Resonancia, amplificación e aislamiento')
    c1,c2=st.columns(2)
    fh=go.Figure();fh.add_trace(go.Scatter(x=rgrid,y=Hcap,name='H',line=dict(color='#c8752d',width=2.7)));fh.add_vline(x=1,line_dash='dash',line_color='#8e9095');fh.add_trace(go.Scatter(x=[res.r],y=[min(res.magnification,12) if math.isfinite(res.magnification) else 12],mode='markers',marker=dict(size=10,color='#202126'),name='caso'))
    fh.update_layout(height=345,xaxis_title='r = ω/ωₙ',yaxis_title='H (recortado a 12 solo para visualización)',margin=dict(l=20,r=20,t=15,b=20));c1.plotly_chart(fh,use_container_width=True,key='vf_res')
    ftr=go.Figure();ftr.add_trace(go.Scatter(x=rgrid,y=TRcap,name='Tᵣ',line=dict(color='#4b4c50',width=2.7)));ftr.add_hline(y=1,line_dash='dash',line_color='#9a9ca1');ftr.add_vline(x=math.sqrt(2),line_dash='dot',line_color='#c8752d');ftr.add_trace(go.Scatter(x=[res.r],y=[min(res.transmissibility,12) if math.isfinite(res.transmissibility) else 12],mode='markers',marker=dict(size=10,color='#f28e1c'),name='caso'))
    ftr.update_layout(height=345,xaxis_title='r = ω/ωₙ',yaxis_title='Transmisibilidad de fuerza Tᵣ',margin=dict(l=20,r=20,t=15,b=20));c2.plotly_chart(ftr,use_container_width=True,key='vf_tr')
    a1,a2,a3,a4=st.columns(4)
    a1.metric('r actual',f'{res.r:.3f}')
    a2.metric('Tᵣ actual',fmt_inf(res.transmissibility))
    a3.metric('r pico H','—' if res.resonant_ratio is None else f'{res.resonant_ratio:.3f}')
    a4.metric('f pico H','—' if res.resonant_frequency_hz is None else f'{res.resonant_frequency_hz:.3f} Hz')
    st.markdown('<div class="gg-note"><b>Clave:</b> la resonancia de desplazamiento no está exactamente en r=1 cuando existe amortiguamiento. Para ζ&lt;1/√2, el máximo de H ocurre en r=√(1−2ζ²). La zona de aislamiento de fuerza comienza al superar r=√2.</div>',unsafe_allow_html=True)

with tabs[3]:
    st.subheader('Balance dinámico y relación de fase')
    if res.singular:
        st.warning('El balance estacionario no se representa en el caso ideal singular.')
    else:
        c1,c2=st.columns([2.2,1])
        with c1:
            ff=go.Figure();ff.add_trace(go.Scatter(x=t,y=F,name='F aplicada',line=dict(color='#f28e1c',width=2.4)));ff.add_trace(go.Scatter(x=t,y=fk,name='F resorte = −kx'));ff.add_trace(go.Scatter(x=t,y=fc,name='F amort. = −cẋ'));ff.add_trace(go.Scatter(x=t,y=m*a,name='m ẍ',line=dict(width=2.2,dash='dash')));ff.update_layout(height=350,xaxis_title='t [s]',yaxis_title='Fuerza [N]',margin=dict(l=20,r=20,t=15,b=20),legend=dict(orientation='h'));c1.plotly_chart(ff,use_container_width=True,key='vf_forces')
        with c2:
            st.latex(r'm\ddot x+c\dot x+kx=F_0\sin\omega t')
            st.latex(r'F+k(-x)+c(-\dot x)=m\ddot x')
            residual=force_balance_residual(F,a,fk,fc,m)
            st.metric('Error máx. del balance numérico',f'{np.nanmax(np.abs(residual)):.2e} N')
            st.caption('La pequeña diferencia numérica proviene del redondeo de la solución evaluada; analíticamente el balance se satisface.')
        # phasor mini chart, normalized vectors
        ph=math.radians(res.phase_deg)
        figp=go.Figure()
        figp.add_trace(go.Scatter(x=[0,1],y=[0,0],mode='lines+markers',name='F referencia'))
        figp.add_trace(go.Scatter(x=[0,math.cos(-ph)],y=[0,math.sin(-ph)],mode='lines+markers',name='x respuesta'))
        figp.update_layout(height=300,title='Fasores normalizados: la respuesta x retrasa a F en δ',xaxis=dict(range=[-1.2,1.2],scaleanchor='y',scaleratio=1,title='cos'),yaxis=dict(range=[-1.2,1.2],title='sin'),margin=dict(l=20,r=20,t=40,b=20));st.plotly_chart(figp,use_container_width=True,key='vf_phasor')

with tabs[4]:
    st.subheader('Comparador A/B')
    st.write('El caso A es el sistema principal. El caso B conserva la misma fuerza F₀ y la misma frecuencia de excitación, y cambia m, k y c. Así puedes ver cómo se desplazan la resonancia, el desfase y la amplitud.')
    b1,b2,b3=st.columns(3)
    mb=float(b1.number_input('B · masa m [kg]',min_value=.001,value=float(m),step=5.0,key='vfb_m'))
    kb=float(b2.number_input('B · rigidez k [N/m]',min_value=.001,value=float(k*1.5),step=1000.0,key='vfb_k'))
    cb=float(b3.number_input('B · amortiguamiento c [N·s/m]',min_value=0.0,value=float(c),step=50.0,key='vfb_c'))
    rb=solve_forced_vibration(mb,kb,cb,F0,f_exc)
    rgA,HA,phA,TRA=frequency_response(res.zeta,3.0,700);rgB,HB,phB,TRB=frequency_response(rb.zeta,3.0,700)
    c1,c2=st.columns(2)
    fg=go.Figure();fg.add_trace(go.Scatter(x=rgA,y=np.clip(HA,0,12),name='A'));fg.add_trace(go.Scatter(x=rgB,y=np.clip(HB,0,12),name='B'));fg.add_trace(go.Scatter(x=[res.r],y=[min(res.magnification,12) if math.isfinite(res.magnification) else 12],mode='markers',name='A actual'));fg.add_trace(go.Scatter(x=[rb.r],y=[min(rb.magnification,12) if math.isfinite(rb.magnification) else 12],mode='markers',name='B actual'));fg.update_layout(height=330,xaxis_title='r',yaxis_title='H',margin=dict(l=20,r=20,t=15,b=20));c1.plotly_chart(fg,use_container_width=True,key='vf_cmp_H')
    if not res.singular and not rb.singular:
        Fb,xb,vb,ab,fkb,fcb,ftb=steady_response(rb,t)
        ftm=go.Figure();ftm.add_trace(go.Scatter(x=t,y=1000*x,name='A'));ftm.add_trace(go.Scatter(x=t,y=1000*xb,name='B'));ftm.update_layout(height=330,xaxis_title='t [s]',yaxis_title='x [mm]',margin=dict(l=20,r=20,t=15,b=20));c2.plotly_chart(ftm,use_container_width=True,key='vf_cmp_time')
    else:
        c2.warning('Uno de los casos está en la singularidad ideal sin amortiguamiento y no tiene respuesta estacionaria finita.')
    p1,p2,p3,p4=st.columns(4)
    p1.metric('fₙ B / A',f'{rb.fn/res.fn:.3f}')
    p2.metric('ζ B / A','—' if res.zeta==0 else f'{rb.zeta/res.zeta:.3f}')
    p3.metric('X B / A','—' if res.singular or rb.singular or res.amplitude_m==0 else f'{rb.amplitude_m/res.amplitude_m:.3f}')
    p4.metric('Tᵣ B / A','—' if res.singular or rb.singular or res.transmissibility==0 else f'{rb.transmissibility/res.transmissibility:.3f}')

with tabs[5]:
    st.subheader('Ecuaciones organizadas por lectura física')
    st.markdown('**1 · Ecuación de movimiento**');st.latex(r'm\ddot x+c\dot x+kx=F_0\sin(\omega t)')
    st.markdown('**2 · Propiedades del sistema**');st.latex(r'\omega_n=\sqrt{\frac{k}{m}},\qquad c_c=2\sqrt{km},\qquad \zeta=\frac{c}{c_c},\qquad r=\frac{\omega}{\omega_n}')
    st.markdown('**3 · Solución estacionaria**');st.latex(r'x(t)=X\sin(\omega t-\delta)')
    st.latex(r'X=\frac{F_0/k}{\sqrt{(1-r^2)^2+(2\zeta r)^2}}')
    st.latex(r'H=\frac{X}{F_0/k}=\frac{1}{\sqrt{(1-r^2)^2+(2\zeta r)^2}}')
    st.latex(r'\delta=\operatorname{atan2}(2\zeta r,1-r^2)')
    st.markdown('**4 · Fuerza transmitida a la base**');st.latex(r'F_T(t)=kx+c\dot x')
    st.latex(r'T_R=\frac{F_{T,0}}{F_0}=\frac{\sqrt{1+(2\zeta r)^2}}{\sqrt{(1-r^2)^2+(2\zeta r)^2}}')
    st.markdown('**5 · Pico de desplazamiento**');st.latex(r'r_{\mathrm{pico}}=\sqrt{1-2\zeta^2}\quad (\zeta<1/\sqrt{2})')

with tabs[6]:
    st.subheader('Interpretación')
    c1,c2=st.columns(2)
    with c1:
        if res.singular:
            st.error('En el modelo ideal sin amortiguamiento y exactamente en resonancia, la solución estacionaria armónica deja de ser finita. Físicamente siempre existirán no linealidades, pérdidas o límites que el modelo lineal no incorpora.',icon='⚠️')
        else:
            st.markdown(f'''<div class="gg-card"><b>Este caso</b><div class="gg-mini">La excitación trabaja a r = <b>{res.r:.3f}</b>. La amplificación dinámica es H = <b>{res.magnification:.3f}</b>, por lo que la amplitud estacionaria resulta X = <b>{1000*res.amplitude_m:.2f} mm</b>. La respuesta retrasa a la fuerza en <b>{res.phase_deg:.1f}°</b>.</div></div>''',unsafe_allow_html=True)
    with c2:
        if res.r < 1:
            st.info('Por debajo de la frecuencia natural, la respuesta permanece relativamente próxima en fase a la fuerza. Al acercarse a resonancia, el desfase aumenta rápidamente.',icon='📉')
        elif abs(res.r-1)<.08:
            st.warning('Estás muy cerca de resonancia. El amortiguamiento controla fuertemente la amplitud y la respuesta se aproxima a 90° de desfase.',icon='🎯')
        else:
            st.info('Por encima de resonancia, la respuesta tiende hacia 180° de desfase. Si además r > √2, aparece la región de aislamiento de fuerza.',icon='🧭')
        st.caption('Este módulo representa respuesta armónica estacionaria lineal. No incluye holguras, fricción seca, rigidez no lineal, impactos ni saturación del actuador.')
