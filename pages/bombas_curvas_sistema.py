from __future__ import annotations
import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from modules.ui_brand import render_app_header
from modules.pump_system_engine import (
    FluidData, PumpCurve, SystemData, FLUID_PRESETS,
    find_operating_point, curve_data, energy_profile, affinity_summary,
    sensitivity, pump_head, system_head, hydraulic_state,
)
from modules.pump_system_visual3d import render_pump_system_3d

st.markdown('''
<style>
.block-container{max-width:1480px;padding-top:1.0rem!important}
.gg-note{border:1px solid #e9e2d7;border-left:4px solid #f28e1c;border-radius:12px;padding:.72rem .9rem;background:#fffaf3}
.gg-card{border:1px solid #e7dfd2;border-radius:13px;background:#fffdf9;padding:.78rem .88rem;height:100%}
.gg-mini{font-size:.88rem;color:#555;line-height:1.4}
.gg-kv{display:grid;grid-template-columns:1fr auto;gap:.22rem .7rem;font-size:.88rem;line-height:1.35}.gg-kv b{text-align:right;color:#202126}
</style>
''', unsafe_allow_html=True)

render_app_header(
    title='Bombas · Curva del sistema y punto de operación',
    subtitle='Bomba centrífuga · Darcy–Weisbach · válvula · afinidad · serie/paralelo · NPSH · sistema hidráulico 3D.',
    section='FLUIDOS Y ENERGÍA',
    logo_width=188,
)

with st.sidebar:
    st.header('Fluido')
    fsel=st.selectbox('Fluido',['Agua · 20 °C','Agua · 60 °C','Personalizado'])
    if fsel in FLUID_PRESETS:
        fluid=FLUID_PRESETS[fsel]
        st.caption(f'ρ = {fluid.rho:.1f} kg/m³ · μ = {fluid.mu:.3e} Pa·s · pᵥ ≈ {fluid.vapor_pressure_pa/1000:.2f} kPa')
    else:
        rho=float(st.number_input('Densidad ρ [kg/m³]',min_value=.1,value=998.2))
        mu=float(st.number_input('Viscosidad μ [Pa·s]',min_value=1e-7,value=1.002e-3,format='%.4e'))
        pv=float(st.number_input('Presión de vapor pᵥ [kPa abs]',min_value=0.0,value=2.34))*1000
        fluid=FluidData('Personalizado',rho,mu,pv)

    st.divider();st.header('Bomba de referencia')
    nref=float(st.number_input('Velocidad de referencia Nref [rpm]',min_value=1.0,value=1800.0,step=50.0))
    h0=float(st.number_input('Altura a Q=0 · H₀ [m]',min_value=.1,value=38.0,step=1.0))
    qref_lps=float(st.number_input('Caudal de referencia Qref [L/s]',min_value=.1,value=20.0,step=1.0))
    href=float(st.number_input('Altura en Qref · Href [m]',min_value=.0,value=28.0,step=1.0))
    nrpm=float(st.number_input('Velocidad actual N [rpm]',min_value=1.0,value=1800.0,step=50.0))
    arrangement=st.selectbox('Configuración',['Una bomba','Serie','Paralelo'])
    count=1 if arrangement=='Una bomba' else int(st.number_input('Número de bombas',min_value=2,max_value=4,value=2,step=1))
    eta=float(st.slider('Eficiencia usada η [%]',20,95,78))/100
    curve=PumpCurve(h0,qref_lps/1000,href,nref,nrpm,arrangement,count,eta)

    st.divider();st.header('Sistema hidráulico')
    hstatic=float(st.number_input('Altura estática Δz [m]',value=10.0,step=1.0))
    eps_mm=float(st.number_input('Rugosidad ε [mm]',min_value=0.0,value=.045,step=.005,format='%.4f'))
    with st.expander('Línea de succión',expanded=False):
        ls=float(st.number_input('Longitud succión Ls [m]',min_value=.1,value=5.0,step=.5))
        ds_mm=float(st.number_input('Diámetro succión Ds [mm]',min_value=5.0,value=125.0,step=5.0))
        ks=float(st.number_input('ΣK succión',min_value=0.0,value=1.5,step=.1))
        zsurf=float(st.number_input('Nivel succión − eje bomba [m]',value=1.5,step=.5))
        ps_kpa=float(st.number_input('Presión sobre depósito succión [kPa abs]',min_value=1.0,value=101.325,step=1.0))
    with st.expander('Línea de descarga',expanded=True):
        ld=float(st.number_input('Longitud descarga Ld [m]',min_value=.1,value=45.0,step=1.0))
        dd_mm=float(st.number_input('Diámetro descarga Dd [mm]',min_value=5.0,value=100.0,step=5.0))
        kd=float(st.number_input('ΣK accesorios sin válvula',min_value=0.0,value=2.0,step=.1))
        opening=float(st.slider('Apertura de válvula [%]',5,100,100))/100
        kvfull=float(st.number_input('K válvula a 100% abierta',min_value=0.0,value=.20,step=.05))
    sys=SystemData(hstatic,ls,ds_mm/1000,ld,dd_mm/1000,eps_mm/1000,ks,kd,opening,kvfull,zsurf,ps_kpa*1000)

op=find_operating_point(curve,fluid,sys)
q, hp_curve, hs_curve=curve_data(curve,fluid,sys)

if not op.exists:
    st.error(op.message,icon='⚠️')

q_lps=0.0 if not op.exists else op.q_m3s*1000
head=0.0 if not op.exists else op.pump_head_m
state=op.state

m1,m2,m3,m4,m5,m6=st.columns(6)
m1.metric('Q operación','—' if not op.exists else f'{q_lps:.2f} L/s')
m2.metric('H operación','—' if not op.exists else f'{head:.2f} m')
m3.metric('V descarga','—' if state is None else f'{state.vd_ms:.2f} m/s')
m4.metric('Re descarga','—' if state is None else f'{state.re_d:.2e}')
m5.metric('P hidráulica','—' if not op.exists else f'{op.hydraulic_power_w/1000:.2f} kW')
m6.metric('P eje','—' if not op.exists else f'{op.shaft_power_w/1000:.2f} kW')

st.markdown('<div class="gg-note"><b>Ruta física:</b> curva de bomba + velocidad/serie/paralelo → pérdidas Darcy–Weisbach + pérdidas singulares + altura estática → intersección H<sub>bomba</sub>(Q)=H<sub>sistema</sub>(Q) → punto de operación, potencia y NPSH disponible.</div>',unsafe_allow_html=True)

tabs=st.tabs(['📊 Vista compacta','🌊 Sistema 3D','📈 Curvas y punto de operación','⚙️ Operación y afinidad','🔗 Serie / paralelo','💨 NPSH','⚖️ Comparador','∑ Ecuaciones','🧠 Interpretación'])

with tabs[0]:
    left,right=st.columns([3.2,1.1],gap='medium')
    with left:
        a,b=st.columns(2,gap='small')
        fig=go.Figure();fig.add_trace(go.Scatter(x=q*1000,y=hp_curve,name='Bomba',line=dict(color='#c8752d',width=3)));fig.add_trace(go.Scatter(x=q*1000,y=hs_curve,name='Sistema',line=dict(color='#4b4c50',width=2.5)))
        if op.exists:fig.add_trace(go.Scatter(x=[q_lps],y=[head],mode='markers',marker=dict(size=11,color='#f28e1c'),name='Operación'))
        fig.update_layout(height=300,title='Curva bomba–sistema',xaxis_title='Q [L/s]',yaxis_title='H [m]',margin=dict(l=15,r=10,t=38,b=15))
        a.plotly_chart(fig,use_container_width=True,key='pump_compact_curve')
        xprof,egl,hgl,zref=energy_profile(op,curve,sys)
        fe=go.Figure()
        if len(xprof):
            fe.add_trace(go.Scatter(x=xprof,y=egl,name='EGL',line=dict(color='#f28e1c',width=2.5)))
            fe.add_trace(go.Scatter(x=xprof,y=hgl,name='HGL',line=dict(color='#4fa3b7',width=2.5)))
            fe.add_trace(go.Scatter(x=xprof,y=zref,name='Nivel descarga',line=dict(color='#9a9ca1',width=1.4,dash='dot')))
        fe.update_layout(height=300,title='Líneas de energía',xaxis_title='Recorrido relativo',yaxis_title='Carga [m]',margin=dict(l=15,r=10,t=38,b=15))
        b.plotly_chart(fe,use_container_width=True,key='pump_energy')
        c,d=st.columns(2,gap='small')
        if state:
            losses=['Succión','Tubería descarga','Accesorios','Válvula'];vals=[state.suction_loss_m,state.discharge_major_loss_m,state.discharge_minor_loss_m,state.valve_loss_m]
            fl=go.Figure(go.Bar(x=losses,y=vals));fl.update_layout(height=255,title='Descomposición de pérdidas',yaxis_title='hL [m]',margin=dict(l=15,r=10,t=38,b=15));c.plotly_chart(fl,use_container_width=True,key='pump_losses')
            table_q=np.linspace(max(op.q_m3s*.4,1e-6),op.q_m3s*1.5,100);sys_h=system_head(table_q,fluid,sys);fp=go.Figure();fp.add_trace(go.Scatter(x=table_q*1000,y=sys_h,line=dict(color='#4b4c50',width=2.3)));fp.add_trace(go.Scatter(x=[q_lps],y=[head],mode='markers',marker=dict(size=10,color='#f28e1c')));fp.update_layout(height=255,title='Entorno del punto de operación',xaxis_title='Q [L/s]',yaxis_title='H sistema [m]',margin=dict(l=15,r=10,t=38,b=15),showlegend=False);d.plotly_chart(fp,use_container_width=True,key='pump_local')
    with right:
        st.markdown('### Lectura del caso')
        if state:
            st.markdown(f'''<div class="gg-card"><div class="gg-kv"><span>Configuración</span><b>{arrangement}{'' if count==1 else f' ×{count}'}</b><span>N</span><b>{nrpm:.0f} rpm</b><span>Apertura</span><b>{opening*100:.0f}%</b><span>K válvula</span><b>{state.valve_k:.2f}</b><span>f succión</span><b>{state.f_s:.4f}</b><span>f descarga</span><b>{state.f_d:.4f}</b><span>hL total</span><b>{state.total_loss_m:.2f} m</b><span>NPSHa</span><b>{op.npsha_m:.2f} m</b></div></div>''',unsafe_allow_html=True)
            if state.valve_loss_m > state.discharge_major_loss_m:
                st.warning('En este punto la válvula aporta más pérdida que la fricción distribuida de la descarga.',icon='🟠')
            else:
                st.info('La pérdida se reparte principalmente entre tuberías y accesorios según la condición actual.',icon='ℹ️')

with tabs[1]:
    st.subheader('Sistema hidráulico 3D')
    l,r=st.columns([1,2.5],gap='medium')
    with l:
        st.markdown('''<div class="gg-card"><b>Qué representa</b><div class="gg-mini">Depósito de succión → tubería → bomba → válvula → descarga → depósito elevado. Las partículas indican el sentido de flujo. La rotación del impulsor es didáctica y no representa la geometría real de una bomba específica.</div></div>''',unsafe_allow_html=True)
        st.markdown('#### Lectura del cambio')
        st.write('Cierra o abre la válvula desde la barra lateral y observa cómo cambia simultáneamente el caudal de operación y la velocidad de las partículas.')
    with r:
        render_pump_system_3d({'q_lps':q_lps,'head_m':head,'velocity_ms':0 if state is None else state.vd_ms,'valve_opening':opening,'rpm':nrpm,'static_head_m':hstatic,'arrangement':arrangement if count==1 else f'{arrangement} ×{count}'},height=620)

with tabs[2]:
    st.subheader('Curva de bomba, curva del sistema y punto de operación')
    fig=go.Figure();fig.add_trace(go.Scatter(x=q*1000,y=hp_curve,name='H bomba',line=dict(color='#c8752d',width=3)));fig.add_trace(go.Scatter(x=q*1000,y=hs_curve,name='H sistema',line=dict(color='#4b4c50',width=2.6)))
    if op.exists:fig.add_trace(go.Scatter(x=[q_lps],y=[head],mode='markers+text',text=['Punto de operación'],textposition='top right',marker=dict(size=12,color='#f28e1c'),name='Operación'))
    fig.update_layout(height=430,xaxis_title='Q [L/s]',yaxis_title='H [m]',margin=dict(l=20,r=20,t=20,b=20));st.plotly_chart(fig,use_container_width=True,key='pump_full_curve')
    st.markdown('<div class="gg-note"><b>Idea clave:</b> el caudal no lo fija únicamente la bomba ni únicamente la tubería. El punto real aparece donde la altura que puede entregar la bomba coincide con la altura que exige el sistema.</div>',unsafe_allow_html=True)

with tabs[3]:
    st.subheader('Operación, leyes de afinidad y sensibilidad')
    aff=affinity_summary(curve)
    q1,q2,q3,q4=st.columns(4);q1.metric('N/Nref',f"{aff['speed_ratio']:.3f}");q2.metric('Q escala',f"{aff['q_ratio']:.3f}×");q3.metric('H escala',f"{aff['head_ratio']:.3f}×");q4.metric('P escala',f"{aff['power_ratio']:.3f}×")
    st.latex(r'Q\propto N,\qquad H\propto N^2,\qquad P\propto N^3')
    param=st.selectbox('Estudio de sensibilidad',['rpm','diámetro descarga','apertura válvula'])
    if param=='rpm':
        vals=np.linspace(max(300,nrpm*.65),nrpm*1.30,70);key='rpm';xplot=vals;xl='N [rpm]'
    elif param=='diámetro descarga':
        vals=np.linspace(dd_mm*.75,dd_mm*1.30,70)/1000;key='diameter';xplot=vals*1000;xl='Dd [mm]'
    else:
        vals=np.linspace(.15,1.0,70);key='valve';xplot=vals*100;xl='Apertura [%]'
    sq,sh,sp=sensitivity(curve,fluid,sys,key,vals)
    c1,c2=st.columns(2)
    fs=go.Figure();fs.add_trace(go.Scatter(x=xplot,y=sq*1000,line=dict(color='#c8752d',width=2.6)));fs.update_layout(height=330,title='Caudal de operación',xaxis_title=xl,yaxis_title='Qop [L/s]',margin=dict(l=15,r=15,t=35,b=15));c1.plotly_chart(fs,use_container_width=True,key='pump_sens_q')
    fpow=go.Figure();fpow.add_trace(go.Scatter(x=xplot,y=sp/1000,line=dict(color='#4b4c50',width=2.5)));fpow.update_layout(height=330,title='Potencia de eje',xaxis_title=xl,yaxis_title='P eje [kW]',margin=dict(l=15,r=15,t=35,b=15));c2.plotly_chart(fpow,use_container_width=True,key='pump_sens_p')

with tabs[4]:
    st.subheader('Una bomba, bombas en serie y bombas en paralelo')
    curves=[]
    for arr,n in [('Una bomba',1),('Serie',2),('Paralelo',2)]:
        cc=PumpCurve(h0,qref_lps/1000,href,nref,nrpm,arr,n,eta);qq,hh,_=curve_data(cc,fluid,sys);curves.append((arr,cc,qq,hh,find_operating_point(cc,fluid,sys)))
    fg=go.Figure();
    for arr,cc,qq,hh,oo in curves:
        fg.add_trace(go.Scatter(x=qq*1000,y=hh,name=arr,line=dict(width=2.6)))
        if oo.exists:fg.add_trace(go.Scatter(x=[oo.q_m3s*1000],y=[oo.pump_head_m],mode='markers',showlegend=False,marker=dict(size=8)))
    qsmax=max(c[2][-1] for c in curves);qsys=np.linspace(0,qsmax,260);fg.add_trace(go.Scatter(x=qsys*1000,y=system_head(qsys,fluid,sys),name='Sistema',line=dict(color='#202126',width=3,dash='dash')));fg.update_layout(height=430,xaxis_title='Q [L/s]',yaxis_title='H [m]');st.plotly_chart(fg,use_container_width=True,key='pump_series_parallel')
    st.write('En **serie** se suman alturas para un mismo caudal. En **paralelo** se suman caudales a una misma altura. El nuevo punto de operación depende igualmente de la curva del sistema.')

with tabs[5]:
    st.subheader('NPSH disponible y cavitación')
    if op.exists:
        c1,c2,c3=st.columns(3);c1.metric('NPSHa',f'{op.npsha_m:.2f} m');c2.metric('p vapor',f'{fluid.vapor_pressure_pa/1000:.2f} kPa abs');c3.metric('Pérdida succión',f'{state.suction_loss_m:.2f} m')
        st.latex(r'NPSH_a=\frac{p_s-p_v}{\rho g}+(z_s-z_b)-h_{L,s}')
        has_req=st.toggle('Dispongo de NPSHr del fabricante',False)
        if has_req:
            npshr=float(st.number_input('NPSHr en este punto de operación [m]',min_value=0.0,value=3.0,step=.1))
            margin=op.npsha_m-npshr
            st.metric('Margen NPSH = NPSHa − NPSHr',f'{margin:.2f} m')
            if margin<0:st.error('NPSHa es menor que el NPSHr ingresado. El punto no satisface esa condición de fabricante.',icon='⚠️')
            else:st.success('NPSHa supera el NPSHr ingresado. El margen mostrado no sustituye el criterio específico del fabricante o norma aplicable.',icon='✅')
        else:
            st.info('Sin NPSHr del fabricante solo puede calcularse NPSHa; no corresponde concluir un margen de cavitación requerido.',icon='ℹ️')

with tabs[6]:
    st.subheader('Comparador A/B')
    st.caption('El caso A es el actual. El caso B conserva la bomba de referencia y el fluido, pero puede cambiar rpm, diámetro de descarga, válvula y configuración.')
    b1,b2,b3,b4=st.columns(4)
    with b1:nB=float(st.number_input('N_B [rpm]',min_value=1.0,value=float(nrpm),step=50.0,key='pb_n'))
    with b2:dB=float(st.number_input('Dd_B [mm]',min_value=5.0,value=float(dd_mm*1.10),step=5.0,key='pb_d'))
    with b3:oB=float(st.slider('Apertura_B [%]',5,100,int(opening*100),key='pb_o'))/100
    with b4:arrB=st.selectbox('Configuración_B',['Una bomba','Serie','Paralelo'],key='pb_arr')
    ncountB=1 if arrB=='Una bomba' else 2
    curveB=PumpCurve(h0,qref_lps/1000,href,nref,nB,arrB,ncountB,eta)
    sysB=SystemData(hstatic,ls,ds_mm/1000,ld,dB/1000,eps_mm/1000,ks,kd,oB,kvfull,zsurf,ps_kpa*1000)
    opB=find_operating_point(curveB,fluid,sysB)
    ca,cb,cc,cd=st.columns(4);ca.metric('Q A','—' if not op.exists else f'{q_lps:.2f} L/s');cb.metric('Q B','—' if not opB.exists else f'{opB.q_m3s*1000:.2f} L/s');cc.metric('P eje A','—' if not op.exists else f'{op.shaft_power_w/1000:.2f} kW');cd.metric('P eje B','—' if not opB.exists else f'{opB.shaft_power_w/1000:.2f} kW')
    qa,hpa,hsa=curve_data(curve,fluid,sys);qb,hpb,hsb=curve_data(curveB,fluid,sysB)
    fc=go.Figure();fc.add_trace(go.Scatter(x=qa*1000,y=hpa,name='Bomba A',line=dict(color='#c8752d',width=2.6)));fc.add_trace(go.Scatter(x=qa*1000,y=hsa,name='Sistema A',line=dict(color='#c8752d',width=1.8,dash='dot')));fc.add_trace(go.Scatter(x=qb*1000,y=hpb,name='Bomba B',line=dict(color='#4b4c50',width=2.6)));fc.add_trace(go.Scatter(x=qb*1000,y=hsb,name='Sistema B',line=dict(color='#4b4c50',width=1.8,dash='dot')));fc.update_layout(height=400,xaxis_title='Q [L/s]',yaxis_title='H [m]');st.plotly_chart(fc,use_container_width=True,key='pump_compare')

with tabs[7]:
    st.subheader('Ecuaciones principales')
    st.latex(r'H_b(Q)=H_{0,N}-aQ^2')
    st.latex(r'H_{0,N}=\left(\frac{N}{N_{ref}}\right)^2H_{0,ref}')
    st.latex(r'H_s(Q)=\Delta z+h_{L,s}(Q)+h_{L,d}(Q)')
    st.latex(r'h_f=f\frac{L}{D}\frac{V^2}{2g},\qquad h_m=\sum K\frac{V^2}{2g}')
    st.latex(r'H_b(Q_{op})=H_s(Q_{op})')
    st.latex(r'P_h=\rho gQH,\qquad P_{eje}=\frac{P_h}{\eta}')
    st.latex(r'Q\propto N,\qquad H\propto N^2,\qquad P\propto N^3')
    st.write('Para la válvula se usa una relación **didáctica** entre apertura y K. Para diseño real debe emplearse la característica K/Cv/Kv del fabricante correspondiente.')

with tabs[8]:
    st.subheader('Interpretación')
    if op.exists:
        st.markdown(f'''<div class="gg-card"><b>Punto actual</b><div class="gg-mini">La intersección ocurre en <b>Q = {q_lps:.2f} L/s</b> y <b>H = {head:.2f} m</b>. El sistema pierde <b>{state.total_loss_m:.2f} m</b> por fricción y singularidades, además de la altura estática de <b>{hstatic:.2f} m</b>.</div></div>''',unsafe_allow_html=True)
        if opening<.45:st.warning('La válvula está considerablemente estrangulada en el modelo didáctico. Observa cómo aumenta K, se empina la curva del sistema y disminuye Qop.',icon='🔧')
        if nrpm!=nref:st.info('La velocidad de la bomba difiere de la referencia. La curva se ha escalado mediante leyes de afinidad.',icon='⚙️')
        if arrangement!='Una bomba':st.info(f'Configuración activa: {arrangement} con {count} bombas. La combinación modifica la curva disponible antes de intersectar al sistema.',icon='🔗')
        st.markdown('<div class="gg-note"><b>Alcance:</b> esta herramienta es para comprensión, análisis preliminar y comparación. Una selección industrial requiere curvas reales H–Q, eficiencia, potencia y NPSHr del fabricante, además de condiciones de instalación verificadas.</div>',unsafe_allow_html=True)
