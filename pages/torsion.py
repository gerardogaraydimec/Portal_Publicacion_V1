from __future__ import annotations
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from modules.ui_brand import render_app_header
from modules.resmat_sections import section_data, profile_params_from_sidebar, visual_section_payload
from modules.torsion_engine import solve_torsion
from modules.torsion_visual3d import render_torsion_3d

st.markdown('''<style>.block-container{max-width:1480px;padding-top:1.35rem!important}.gg-note{border:1px solid #e9e2d7;border-left:4px solid #f28e1c;border-radius:12px;padding:.85rem 1rem;background:#fffaf3}</style>''',unsafe_allow_html=True)
render_app_header(title='Torsión · Ejes y Perfiles',subtitle='Torque · constante torsional · esfuerzo cortante · ángulo de giro · rigidez torsional · alabeo.',section='RESISTENCIA Y ESTRUCTURAS',logo_width=188)

with st.sidebar:
    st.header('Carga torsional')
    T=float(st.number_input('Torque T [kN·m]',value=2.0,step=.25))
    L=float(st.number_input('Longitud L [m]',min_value=.05,value=2.0,step=.1))
    st.divider(); st.subheader('Material')
    mat=st.selectbox('Material',['Acero','Aluminio','Personalizado'])
    if mat=='Acero': G=79.3; st.caption('G = 79.3 GPa')
    elif mat=='Aluminio': G=26.0; st.caption('G = 26 GPa')
    else: G=float(st.number_input('Módulo de corte G [GPa]',min_value=.001,value=79.3))
    st.divider(); st.subheader('Sección')
    stype=st.selectbox('Geometría',['Circular maciza','Tubular circular','Rectangular','Perfil I / H','Canal C','Propiedades ingresadas'])
    sp=profile_params_from_sidebar(st,stype,'tor_')

sec=section_data(stype,sp); res=solve_torsion(T,L,G,stype,sp,sec)

a,b,c,d=st.columns(4)
a.metric('Jt',f'{res.jt_mm4:.3e} mm⁴'); b.metric('Giro φ',f'{res.twist_deg:.3f}°'); c.metric('Rigidez GJ/L',f'{res.stiffness_knm_per_rad:.2f} kN·m/rad'); d.metric('τmáx', '—' if res.tau_max_mpa is None else f'{res.tau_max_mpa:.2f} MPa')

tabs=st.tabs(['📘 Concepto','🌀 Torsión 3D','📊 Esfuerzo y giro','📐 Sección','∑ Ecuaciones','🧠 Interpretación'])
with tabs[0]:
    st.subheader('Qué hace un torque')
    st.write('Un torque aplicado alrededor del eje longitudinal produce **esfuerzos cortantes** y **giro**. En ejes circulares macizos o tubulares, la hipótesis de Saint-Venant entrega una relación especialmente clara entre T, J, τ y φ.')
    st.latex(r'\tau(r)=\frac{T r}{J},\qquad \phi=\frac{T L}{GJ}')
    st.markdown('<div class="gg-note"><b>Lectura física:</b> aumentar J o G reduce el giro. En una sección circular, τ es cero en el centro y crece linealmente hasta la superficie exterior.</div>',unsafe_allow_html=True)
    st.write('En secciones no circulares, las secciones pueden alabear y la distribución de τ deja de ser radial. En perfiles abiertos delgados, la rigidez torsional de Saint-Venant suele ser muy baja; si el alabeo está restringido aparecen efectos adicionales que este módulo introductorio no calcula.')
with tabs[1]:
    st.subheader('Modelo visual 3D del giro')
    amp=st.slider('Amplificación visual del giro',1.0,25.0,8.0,1.0)
    phi_display=max(-2.2,min(2.2,res.twist_rad*amp))
    render_torsion_3d({'phi_display':phi_display,'phi_real':res.twist_rad,'type':stype,'section':visual_section_payload(stype,sp)},height=650)
    st.caption(f'φ real = {res.twist_deg:.4f}°. La hélice y las secciones se muestran con amplificación {amp:.0f}×, limitada solo para visualización.')
with tabs[2]:
    st.subheader('Respuesta a lo largo del eje')
    x=np.linspace(0,L,150); phi=res.twist_rad*x/L
    fig=go.Figure(); fig.add_trace(go.Scatter(x=x,y=np.degrees(phi),line=dict(color='#c8752d',width=3),name='φ(x)')); fig.update_layout(height=390,xaxis_title='x [m]',yaxis_title='Giro [°]',margin=dict(l=20,r=20,t=15,b=20),showlegend=False); st.plotly_chart(fig,use_container_width=True)
    if stype in ('Circular maciza','Tubular circular'):
        if stype=='Circular maciza': R=sp['d_mm']/2; ri=0
        else: R=sp['do_mm']/2; ri=R-sp['t_mm']
        rr=np.linspace(ri,R,120); tau=T*1e6*rr/res.jt_mm4
        fig2=go.Figure(); fig2.add_trace(go.Scatter(x=rr,y=tau,line=dict(color='#f28e1c',width=3))); fig2.update_layout(height=350,xaxis_title='r [mm]',yaxis_title='τ [MPa]',margin=dict(l=20,r=20,t=15,b=20)); st.plotly_chart(fig2,use_container_width=True)
    else:
        st.info(res.tau_mode,icon='ℹ️')
with tabs[3]:
    st.subheader('Propiedades torsionales')
    c1,c2,c3,c4=st.columns(4); c1.metric('Área',f'{sec.area_mm2:.0f} mm²'); c2.metric('Iz',f'{sec.iz_mm4:.3e}'); c3.metric('Iy',f'{sec.iy_mm4:.3e}'); c4.metric('Jt',f'{sec.jt_mm4:.3e}')
    st.write(sec.note or 'Sección con propiedades torsionales calculadas desde su geometría.')
with tabs[4]:
    st.latex(r'J_{circ}=\frac{\pi d^4}{32}')
    st.latex(r'J_{tubo}=\frac{\pi(D_o^4-D_i^4)}{32}')
    st.latex(r'\tau=\frac{Tr}{J}\quad\text{(secciones circulares)}')
    st.latex(r'\frac{d\phi}{dx}=\frac{T(x)}{GJ_t},\qquad \phi=\int_0^L\frac{T(x)}{GJ_t}\,dx')
    st.latex(r'k_t=\frac{GJ_t}{L}')
    st.write('Para rectángulos y perfiles abiertos el módulo usa constantes torsionales aproximadas de Saint-Venant. El alabeo restringido no está incluido.')
with tabs[5]:
    st.write(res.tau_mode)
    if stype in ('Perfil I / H','Canal C'):
        st.warning('Los perfiles abiertos pueden ser muy eficientes a flexión y, al mismo tiempo, poco rígidos a torsión. Esta comparación es una de las razones para distinguir Iz/Iy de Jt.',icon='🌀')
    if abs(res.twist_deg)>5: st.warning('El giro calculado es grande. La hipótesis de pequeñas deformaciones y el uso lineal de Saint-Venant deben revisarse para interpretar el caso físicamente.')
    else: st.success('El giro calculado permanece moderado dentro de este modelo elástico lineal. Esto no constituye una verificación normativa de diseño.')
