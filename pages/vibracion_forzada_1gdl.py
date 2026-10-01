from __future__ import annotations
import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from modules.ui_brand import render_app_header
from modules.vibration_forced_engine import solve_vibration, steady_response, frequency_response, force_balance_residual
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
    subtitle='Fuerza armónica · desbalance rotatorio · excitación de base · resonancia · desfase · aislamiento · visualización 3D.',
    section='MÁQUINAS Y COMPONENTES',
    logo_width=188,
)

mode_labels = {
    'Fuerza armónica': 'force',
    'Desbalance rotatorio': 'unbalance',
    'Excitación de base': 'base',
}

with st.sidebar:
    st.header('Sistema 1GDL')
    mode_name = st.selectbox('Tipo de excitación', list(mode_labels.keys()))
    mode = mode_labels[mode_name]
    m = float(st.number_input('Masa m [kg]', min_value=.001, value=100.0, step=5.0))
    k = float(st.number_input('Rigidez k [N/m]', min_value=.001, value=40000.0, step=1000.0))
    c = float(st.number_input('Amortiguamiento c [N·s/m]', min_value=0.0, value=800.0, step=50.0))
    fn0 = math.sqrt(k / m) / (2 * math.pi)
    st.divider()
    kwargs = {'m': m, 'k': k, 'c': c}
    if mode == 'force':
        st.subheader('Excitación armónica')
        F0 = float(st.number_input('Amplitud F₀ [N]', min_value=0.0, value=1000.0, step=100.0))
        f_exc = float(st.number_input('Frecuencia de excitación f [Hz]', min_value=0.0, value=float(round(fn0 * .80, 3)), step=.10, format='%.3f'))
        kwargs.update(F0=F0, f_exc=f_exc)
    elif mode == 'unbalance':
        st.subheader('Desbalance rotatorio')
        me = float(st.number_input('Masa excéntrica mₑ [kg]', min_value=0.0, value=2.0, step=0.1, format='%.3f'))
        e_mm = float(st.number_input('Excentricidad e [mm]', min_value=0.0, value=20.0, step=1.0))
        rpm = float(st.number_input('Velocidad de giro [rpm]', min_value=0.0, value=float(round(fn0*60*0.8,1)), step=10.0))
        kwargs.update(me=me, e_m=e_mm/1000.0, rpm=rpm)
    else:
        st.subheader('Excitación de base')
        Y_mm = float(st.number_input('Amplitud de base Y [mm]', min_value=0.0, value=5.0, step=0.5, format='%.3f'))
        f_exc = float(st.number_input('Frecuencia de base f [Hz]', min_value=0.0, value=float(round(fn0 * .80, 3)), step=.10, format='%.3f'))
        kwargs.update(Y_m=Y_mm/1000.0, f_exc=f_exc)
    st.divider(); st.subheader('Ventana temporal')
    cycles = float(st.number_input('Ciclos a mostrar', min_value=1.0, value=6.0, step=1.0))

res = solve_vibration(mode, **kwargs)
if res.f_exc > 0:
    duration = cycles / res.f_exc
else:
    duration = max(2.0, cycles / max(res.fn, 1e-6))
t = np.linspace(0, duration, 1200)
resp = steady_response(res, t)
rgrid, Hgrid, phasegrid, Tgrid, extra_grid = frequency_response(mode, res.zeta, 3.0, 750)
Hcap = np.clip(Hgrid, 0, 12)
Tcap = np.clip(Tgrid, 0, 12)
residual = force_balance_residual(res, resp)

fmt_inf = lambda val, suf='': ('∞' if not math.isfinite(val) else f'{val:.3f}{suf}')

m1,m2,m3,m4,m5,m6=st.columns(6)
m1.metric('fₙ',f'{res.fn:.3f} Hz')
m2.metric('ζ',f'{res.zeta:.3f}')
m3.metric('r = f/fₙ',f'{res.r:.3f}')
m4.metric('Razón',fmt_inf(res.response_ratio))
m5.metric('Desfase δ',f'{res.phase_deg:.1f}°')
amp_mm = '∞' if res.singular else f'{1000*res.amplitude_m:.2f} mm'
m6.metric('Amplitud X', amp_mm)

route = {
    'force': 'F(t)=F₀ sin(ωt) → r = ω/ωₙ → H(r,ζ) y desfase δ → respuesta x(t) → fuerza transmitida a la base.',
    'unbalance': 'mₑeω² → r = ω/ωₙ → fuerza de desbalance + desfase → respuesta x(t) de la máquina → fuerza transmitida.',
    'base': 'y(t)=Y sin(ωt) → r = ω/ωₙ → transmisibilidad X/Y y movimiento relativo z=x−y → fuerza transmitida al apoyo.',
}[mode]
st.markdown(f'<div class="gg-note"><b>Ruta física:</b> {route}</div>',unsafe_allow_html=True)

if res.singular:
    st.error('Caso ideal singular: la condición de resonancia sin amortiguamiento conduce a una amplitud no acotada en el modelo lineal estacionario.', icon='⚠️')

tabs=st.tabs(['📊 Vista compacta','🧩 Sistema 3D','🎯 Resonancia y aislamiento','⚙️ Fuerzas y fase','⚖️ Comparador','📘 Teoría y ecuaciones','🧠 Interpretación'])

with tabs[0]:
    left,right=st.columns([3.25,1.15],gap='medium')
    with left:
        q1,q2=st.columns(2,gap='small')
        if not res.singular:
            figt=make_subplots(specs=[[{'secondary_y':True}]])
            if mode == 'base':
                figt.add_trace(go.Scatter(x=t,y=1000*resp['x'],name='x(t)',line=dict(color='#c8752d',width=2.5)),secondary_y=False)
                figt.add_trace(go.Scatter(x=t,y=1000*resp['y'],name='y(t)',line=dict(color='#4b4c50',width=1.9,dash='dot')),secondary_y=False)
                figt.update_yaxes(title_text='Desplazamiento [mm]',secondary_y=False)
            else:
                figt.add_trace(go.Scatter(x=t,y=1000*resp['x'],name='x(t)',line=dict(color='#c8752d',width=2.5)),secondary_y=False)
                figt.add_trace(go.Scatter(x=t,y=resp['input'],name=('F(t)' if mode=='force' else 'F_d(t)'),line=dict(color='#4b4c50',width=1.7,dash='dot')),secondary_y=True)
                figt.update_yaxes(title_text='x [mm]',secondary_y=False);figt.update_yaxes(title_text=('F [N]'),secondary_y=True)
            figt.update_layout(height=255,title='Excitación y respuesta',xaxis_title='t [s]',margin=dict(l=15,r=15,t=35,b=15),legend=dict(orientation='h',y=1.08,x=.02))
            q1.plotly_chart(figt,use_container_width=True,key='vf_time')

            figph=go.Figure();figph.add_trace(go.Scatter(x=1000*resp['x'],y=resp['v'],mode='lines',line=dict(color='#f28e1c',width=2.4)))
            figph.add_trace(go.Scatter(x=[0],y=[0],mode='markers',marker=dict(size=8,color='#202126',symbol='x')))
            figph.update_layout(height=255,title='Plano de fase',xaxis_title='x [mm]',yaxis_title='ẋ [m/s]',margin=dict(l=15,r=10,t=35,b=15),showlegend=False)
            q2.plotly_chart(figph,use_container_width=True,key='vf_phase')
        else:
            q1.warning('No hay respuesta estacionaria finita para representar.')
            q2.warning('El plano de fase estacionario tampoco está definido.')

        q3,q4=st.columns(2,gap='small')
        figh=go.Figure();
        titleH='Amplificación dinámica' if mode!='base' else 'Transmisibilidad de desplazamiento'
        ylabH='H' if mode!='base' else 'X/Y'
        figh.add_trace(go.Scatter(x=rgrid,y=Hcap,line=dict(color='#c8752d',width=2.6),name='H'))
        if math.isfinite(res.response_ratio):
            figh.add_trace(go.Scatter(x=[res.r],y=[min(res.response_ratio,12)],mode='markers',marker=dict(size=9,color='#202126'),name='caso'))
        figh.add_vline(x=1,line_dash='dash',line_color='#9a9ca1'); figh.update_layout(height=240,title=titleH,xaxis_title='r = ω/ωₙ',yaxis_title=ylabH,margin=dict(l=15,r=10,t=35,b=15),showlegend=False)
        q3.plotly_chart(figh,use_container_width=True,key='vf_H')

        figd=go.Figure();figd.add_trace(go.Scatter(x=rgrid,y=phasegrid,line=dict(color='#4b4c50',width=2.4)))
        figd.add_trace(go.Scatter(x=[res.r],y=[res.phase_deg],mode='markers',marker=dict(size=9,color='#f28e1c')))
        figd.add_vline(x=1,line_dash='dash',line_color='#9a9ca1');figd.update_layout(height=240,title='Desfase excitación–respuesta',xaxis_title='r = ω/ωₙ',yaxis_title='δ [°]',margin=dict(l=15,r=10,t=35,b=15),showlegend=False,yaxis=dict(range=[0,180]))
        q4.plotly_chart(figd,use_container_width=True,key='vf_delta')

    with right:
        st.markdown('### Lectura del caso')
        extra_html = ''
        if mode == 'force':
            extra_html = f'<span>F₀</span><b>{res.input_amp:.1f} N</b><span>f</span><b>{res.f_exc:.3f} Hz</b>'
        elif mode == 'unbalance':
            extra_html = f'<span>mₑe</span><b>{res.input_amp:.2f} kg·mm</b><span>rpm</span><b>{res.f_exc*60:.1f}</b>'
        else:
            extra_html = f'<span>Y</span><b>{1000*res.base_amp_m:.2f} mm</b><span>f</span><b>{res.f_exc:.3f} Hz</b>'
        st.markdown(f'''
<div class="gg-card"><div class="gg-kv">
<span>m</span><b>{m:.3f} kg</b><span>k</span><b>{k:.1f} N/m</b><span>c</span><b>{c:.1f} N·s/m</b>
{extra_html}
<span>fₙ</span><b>{res.fn:.3f} Hz</b><span>r</span><b>{res.r:.3f}</b><span>ζ</span><b>{res.zeta:.3f}</b>
<span>{'H' if mode!='base' else 'X/Y'}</span><b>{fmt_inf(res.response_ratio)}</b><span>δ</span><b>{res.phase_deg:.1f}°</b><span>X</span><b>{amp_mm}</b>
</div></div>''', unsafe_allow_html=True)
        st.markdown('#### Lectura física')
        if res.r < .7:
            st.info('Frecuencia baja respecto de fₙ: domina la rigidez y la respuesta tiende a seguir a la excitación.', icon='↔️')
        elif res.r < 1.3:
            st.warning('Zona cercana a resonancia: la respuesta es muy sensible al amortiguamiento y a pequeños cambios de frecuencia.', icon='🎯')
        else:
            st.info('Frecuencia alta respecto de fₙ: crece el papel de la inercia y la fase se separa cada vez más de la excitación.', icon='🧭')
        if mode == 'base' and res.r > math.sqrt(2):
            st.success('r > √2: comienza a apreciarse la región útil para aislamiento vibratorio.', icon='✅')
        elif mode in ('force','unbalance') and res.r > math.sqrt(2):
            st.success('r > √2: la fuerza transmitida tiende a reducirse respecto de la zona resonante.', icon='✅')

with tabs[1]:
    st.subheader('Sistema 3D y lectura del fenómeno')
    l,rcol=st.columns([1,2.4],gap='medium')
    with l:
        vamp=st.slider('Amplificación visual del desplazamiento',0.5,2.5,1.0,.1,key='vf_amp')
        speed=st.slider('Velocidad de animación',0.25,2.0,1.0,.25,key='vf_speed')
        show_motion=st.toggle('Mostrar sentido de movimiento v(t)',value=True)
        show_trans=st.toggle('Mostrar fuerza transmitida Fₜ',value=True)
        show_internal=st.toggle('Mostrar Fₖ y F꜀',value=False)
        show_base=st.toggle('Mostrar movimiento de base / excitación', value=(mode=='base'))
        st.markdown(f'''<div class="gg-card"><b>Modo activo</b><div class="gg-mini">{res.note}<br><br>
        <b>Naranja:</b> {'movimiento de base y(t)' if mode=='base' else ('fuerza aplicada F(t)' if mode=='force' else 'fuerza de desbalance proyectada')}<br>
        <b>Marfil:</b> sentido instantáneo del movimiento de la masa.<br>
        <b>Gris:</b> fuerza transmitida al apoyo.<br>
        <b>Cobre / grafito:</b> fuerza de resorte y de amortiguador cuando se activan.</div></div>''',unsafe_allow_html=True)
    with rcol:
        if res.singular:
            st.warning('El caso singular ideal no puede animarse como una respuesta estacionaria finita.')
        else:
            idx=np.linspace(0,len(t)-1,560).astype(int)
            render_forced_vibration_3d({
                'mode': mode,
                't': t[idx].tolist(), 'x': resp['x'][idx].tolist(), 'v': resp['v'][idx].tolist(), 'input': resp['input'][idx].tolist(),
                'fk': resp['fk'][idx].tolist(), 'fc': resp['fc'][idx].tolist(), 'ft': resp['ft'][idx].tolist(), 'y': resp['y'][idx].tolist(),
                'theta': resp['rotor_theta'][idx].tolist(), 'duration': duration, 'visual_amp': vamp, 'speed': speed,
                'r': res.r, 'H': res.response_ratio, 'phase_deg': res.phase_deg,
                'show_motion': show_motion, 'show_transmitted': show_trans, 'show_internal': show_internal, 'show_base': show_base
            }, height=620)
    st.caption('La animación representa la respuesta estacionaria del modelo lineal. La amplificación visual solo cambia la escala del movimiento en pantalla.')

with tabs[2]:
    st.subheader('Resonancia, amplificación e aislamiento')
    c1,c2=st.columns(2)
    fh=go.Figure(); fh.add_trace(go.Scatter(x=rgrid,y=Hcap,name='resp',line=dict(color='#c8752d',width=2.7))); fh.add_vline(x=1,line_dash='dash',line_color='#8e9095');
    if mode == 'base':
        fh.update_layout(title='Transmisibilidad X/Y', yaxis_title='X/Y')
    elif mode == 'unbalance':
        fh.update_layout(title='Respuesta normalizada X/e', yaxis_title='X/e')
    else:
        fh.update_layout(title='Amplificación H = X/(F₀/k)', yaxis_title='H')
    if math.isfinite(res.response_ratio): fh.add_trace(go.Scatter(x=[res.r],y=[min(res.response_ratio,12)],mode='markers',marker=dict(size=9,color='#202126')))
    fh.update_layout(height=320, xaxis_title='r = ω/ωₙ', margin=dict(l=15,r=15,t=35,b=15), showlegend=False)
    c1.plotly_chart(fh,use_container_width=True,key='vf_res_curve')

    ftg=go.Figure(); ftg.add_trace(go.Scatter(x=rgrid,y=Tcap,name='T',line=dict(color='#4b4c50',width=2.6))); ftg.add_vline(x=1,line_dash='dash',line_color='#8e9095');
    if mode=='base' and extra_grid is not None:
        ftg.add_trace(go.Scatter(x=rgrid,y=np.clip(extra_grid,0,12),name='Z/Y',line=dict(color='#f28e1c',width=2.0,dash='dot')))
        ftg.update_layout(title='X/Y y movimiento relativo Z/Y', yaxis_title='Razón')
    else:
        ftg.update_layout(title='Transmisibilidad de fuerza', yaxis_title='Tᵣ')
    if math.isfinite(res.transmissibility): ftg.add_trace(go.Scatter(x=[res.r],y=[min(res.transmissibility,12)],mode='markers',marker=dict(size=9,color='#f28e1c')))
    ftg.update_layout(height=320, xaxis_title='r = ω/ωₙ', margin=dict(l=15,r=15,t=35,b=15))
    c2.plotly_chart(ftg,use_container_width=True,key='vf_tr_curve')

with tabs[3]:
    st.subheader('Fuerzas, fases y equilibrio dinámico')
    c1,c2=st.columns(2)
    if not res.singular:
        figforces=go.Figure()
        if mode == 'base':
            figforces.add_trace(go.Scatter(x=t,y=1000*resp['y'],name='y(t) [mm]',line=dict(color='#202126',width=1.8,dash='dot')))
        else:
            figforces.add_trace(go.Scatter(x=t,y=resp['input'],name=('F(t)' if mode=='force' else 'F_d(t)'),line=dict(color='#202126',width=1.8,dash='dot')))
        figforces.add_trace(go.Scatter(x=t,y=-resp['fk'],name='-Fₖ = k z',line=dict(color='#c8752d',width=2.0)))
        figforces.add_trace(go.Scatter(x=t,y=-resp['fc'],name='-F꜀ = c ż',line=dict(color='#6d7076',width=2.0)))
        figforces.add_trace(go.Scatter(x=t,y=res.m*resp['a'],name='m x¨',line=dict(color='#b0b2b6',width=2.0,dash='dash')))
        figforces.update_layout(height=340,title='Balance dinámico',xaxis_title='t [s]',yaxis_title='Magnitud',margin=dict(l=15,r=15,t=35,b=15),legend=dict(orientation='h',y=1.1,x=0))
        c1.plotly_chart(figforces,use_container_width=True,key='vf_forces')

        figres=go.Figure(); figres.add_trace(go.Scatter(x=t, y=residual, line=dict(color='#f28e1c', width=2.2))); figres.add_hline(y=0,line_dash='dash',line_color='#8e9095')
        figres.update_layout(height=340,title='Residual del equilibrio dinámico',xaxis_title='t [s]',yaxis_title='Residual',margin=dict(l=15,r=15,t=35,b=15),showlegend=False)
        c2.plotly_chart(figres,use_container_width=True,key='vf_residual')
    st.markdown('<div class="gg-note"><b>Idea clave:</b> el desfase aparece porque las fuerzas de resorte, amortiguamiento e inercia no alcanzan sus máximos al mismo tiempo. Cerca de resonancia, pequeños cambios de frecuencia producen cambios grandes en amplitud y fase.</div>',unsafe_allow_html=True)

with tabs[4]:
    st.subheader('Comparador A/B bajo la misma excitación')
    st.caption('El Caso A corresponde a los datos de la barra lateral. El Caso B modifica m, k y c, manteniendo la misma excitación seleccionada.')
    b1,b2,b3=st.columns(3)
    with b1:
        mB=float(st.number_input('m_B [kg]',min_value=.001,value=float(m),step=5.0,key='cmp_mB'))
    with b2:
        kB=float(st.number_input('k_B [N/m]',min_value=.001,value=float(k),step=1000.0,key='cmp_kB'))
    with b3:
        cB=float(st.number_input('c_B [N·s/m]',min_value=0.0,value=float(c),step=50.0,key='cmp_cB'))
    kwargsB = dict(kwargs)
    kwargsB.update(m=mB,k=kB,c=cB)
    resB = solve_vibration(mode, **kwargsB)
    tB = t
    respB = steady_response(resB, tB)

    cm1,cm2,cm3,cm4=st.columns(4)
    cm1.metric('A · razón', fmt_inf(res.response_ratio))
    cm2.metric('B · razón', fmt_inf(resB.response_ratio))
    cm3.metric('A · amplitud X', '∞' if res.singular else f'{1000*res.amplitude_m:.2f} mm')
    cm4.metric('B · amplitud X', '∞' if resB.singular else f'{1000*resB.amplitude_m:.2f} mm')

    g1,g2=st.columns(2)
    figcmp=go.Figure()
    if not res.singular:
        figcmp.add_trace(go.Scatter(x=t,y=1000*resp['x'],name='x_A(t)',line=dict(color='#c8752d',width=2.4)))
    if not resB.singular:
        figcmp.add_trace(go.Scatter(x=tB,y=1000*respB['x'],name='x_B(t)',line=dict(color='#4b4c50',width=2.2)))
    figcmp.update_layout(height=320,title='Comparación temporal',xaxis_title='t [s]',yaxis_title='x [mm]',margin=dict(l=15,r=15,t=35,b=15))
    g1.plotly_chart(figcmp,use_container_width=True,key='vf_cmp_time')

    rB,H_B,_,T_B,extraB = frequency_response(mode,resB.zeta,3.0,750)
    figcmp2=go.Figure(); figcmp2.add_trace(go.Scatter(x=rgrid,y=np.clip(Hgrid,0,12),name='Caso A',line=dict(color='#c8752d',width=2.5))); figcmp2.add_trace(go.Scatter(x=rB,y=np.clip(H_B,0,12),name='Caso B',line=dict(color='#4b4c50',width=2.3)))
    figcmp2.add_vline(x=1,line_dash='dash',line_color='#8e9095'); figcmp2.update_layout(height=320,title=('Curva X/Y' if mode=='base' else 'Curva de respuesta'),xaxis_title='r = ω/ωₙ',yaxis_title=('X/Y' if mode=='base' else 'Razón'),margin=dict(l=15,r=15,t=35,b=15))
    g2.plotly_chart(figcmp2,use_container_width=True,key='vf_cmp_curve')

with tabs[5]:
    st.subheader('Teoría y ecuaciones')
    st.markdown('### Ecuación del sistema')
    if mode == 'force':
        st.latex(r'm\ddot x + c\dot x + kx = F_0\sin(\omega t)')
        st.latex(r'H=\frac{X}{F_0/k}=\frac{1}{\sqrt{(1-r^2)^2+(2\zeta r)^2}}')
    elif mode == 'unbalance':
        st.latex(r'm\ddot x + c\dot x + kx = m_e e\,\omega^2\sin(\omega t)')
        st.latex(r'F_{d,0}=m_e e\,\omega^2')
        st.latex(r'\frac{X}{e}=\frac{m_e}{m}\,\frac{r^2}{\sqrt{(1-r^2)^2+(2\zeta r)^2}}')
    else:
        st.latex(r'm\ddot x + c(\dot x-\dot y) + k(x-y) = 0')
        st.latex(r'\frac{X}{Y}=\frac{\sqrt{1+(2\zeta r)^2}}{\sqrt{(1-r^2)^2+(2\zeta r)^2}}')
        st.latex(r'\frac{Z}{Y}=\frac{r^2}{\sqrt{(1-r^2)^2+(2\zeta r)^2}},\qquad z=x-y')
    st.latex(r'\omega_n=\sqrt{\frac{k}{m}},\qquad f_n=\frac{\omega_n}{2\pi},\qquad c_c=2\sqrt{km},\qquad \zeta=\frac{c}{c_c},\qquad r=\frac{\omega}{\omega_n}')
    st.latex(r'F_t = kz + c\dot z')
    st.write('Estas ecuaciones corresponden al régimen estacionario armónico lineal. La visualización 3D es didáctica y no reemplaza un modelo multigrado, no lineal o de rotor completo.')

with tabs[6]:
    st.subheader('Interpretación y lectura de diseño')
    c1,c2=st.columns(2)
    with c1:
        st.markdown(f'''<div class="gg-card"><b>Resultado principal</b><div class="gg-mini">La respuesta estacionaria del sistema tiene una amplitud <b>{amp_mm}</b> y un desfase de <b>{res.phase_deg:.1f}°</b>. {'La fuerza transmitida al apoyo tiene amplitud ' + fmt_inf(res.transmitted_force_amp_n, ' N') + '.' if math.isfinite(res.transmitted_force_amp_n) else 'La fuerza transmitida diverge en el caso ideal singular.'}</div></div>''',unsafe_allow_html=True)
        if mode == 'unbalance':
            st.markdown(f'''<div class="gg-card"><b>Lectura tipo máquina</b><div class="gg-mini">Con <b>mₑe = {res.input_amp:.2f} kg·mm</b> y <b>{res.f_exc*60:.1f} rpm</b>, la fuerza excitadora alcanza <b>{res.force_amp_n:.1f} N</b>. Aumentar rpm incrementa tanto la fuerza de desbalance como la razón de frecuencia.</div></div>''',unsafe_allow_html=True)
        elif mode == 'base':
            st.markdown(f'''<div class="gg-card"><b>Lectura de aislación</b><div class="gg-mini">La base se mueve con <b>Y = {1000*res.base_amp_m:.2f} mm</b>. El movimiento relativo del aislador es <b>{1000*res.relative_amp_m:.2f} mm</b>, dato clave para revisar carrera disponible y fuerza transmitida.</div></div>''',unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div class="gg-card"><b>Observaciones</b><div class="gg-mini">{res.note}<br><br>Residual máximo del balance dinámico: <b>{np.nanmax(np.abs(residual)):.3e}</b>.</div></div>''',unsafe_allow_html=True)
        if res.r < 0.7:
            st.success('Estás en una zona controlada principalmente por rigidez. Es útil para comprender respuesta casi cuasiestática.', icon='✅')
        elif res.r < 1.3:
            st.warning('La zona cercana a resonancia suele ser la más crítica en máquinas y soportes. El amortiguamiento cumple un papel decisivo.', icon='⚠️')
        else:
            st.info('Por sobre la resonancia aparecen efectos de aislamiento o desacople parcial, dependiendo del tipo de excitación y de lo que se quiera controlar.', icon='ℹ️')
