from __future__ import annotations
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from modules.ui_brand import render_app_header
from modules.resmat_sections import section_data, profile_params_from_sidebar, visual_section_payload
from modules.column_engine import solve_column, K_FACTORS
from modules.column_visual3d import render_column_3d

st.markdown('''<style>.block-container{max-width:1480px;padding-top:1.35rem!important}.gg-note{border:1px solid #e9e2d7;border-left:4px solid #f28e1c;border-radius:12px;padding:.85rem 1rem;background:#fffaf3}</style>''',unsafe_allow_html=True)
render_app_header(title='Columnas · Compresión y Pandeo',subtitle='Carga axial · esfuerzo de compresión · esbeltez · longitud efectiva · pandeo de Euler · eje crítico.',section='RESISTENCIA Y ESTRUCTURAS',logo_width=188)

with st.sidebar:
    st.header('Columna')
    L=float(st.number_input('Longitud real L [m]',min_value=.1,value=3.0,step=.25))
    P=float(st.number_input('Carga axial P [kN]',min_value=0.0,value=100.0,step=10.0))
    end=st.selectbox('Condición de extremos',list(K_FACTORS.keys()))
    st.divider(); st.subheader('Material')
    mat=st.selectbox('Material',['Acero','Aluminio','Madera','Personalizado'])
    vals={'Acero':(200.,250.),'Aluminio':(69.,150.),'Madera':(12.,35.)}
    if mat=='Personalizado': E=float(st.number_input('E [GPa]',min_value=.001,value=200.)); fy=float(st.number_input('Límite de referencia fy [MPa]',min_value=.1,value=250.))
    else: E,fy=vals[mat]; st.caption(f'E={E:g} GPa · fy={fy:g} MPa (referencial)')
    st.divider(); st.subheader('Sección')
    stype=st.selectbox('Geometría',['Rectangular','Circular maciza','Tubular circular','Perfil I / H','Canal C','Propiedades ingresadas'])
    sp=profile_params_from_sidebar(st,stype,'col_')

sec=section_data(stype,sp); res=solve_column(P,L,E,sec,end,fy)

a,b,c,d=st.columns(4)
a.metric('σ=P/A',f'{res.sigma_axial_mpa:.2f} MPa'); b.metric('λ gobernante',f'{res.lambda_governing:.1f}'); c.metric('Pcr Euler',f'{res.pcr_kn:.1f} kN'); d.metric('P/Pcr',f'{res.load_ratio:.3f}')

tabs=st.tabs(['📘 Concepto','🏗️ Columna 3D','📐 Esbeltez y Euler','🧱 Sección','∑ Ecuaciones','🧠 Interpretación'])
with tabs[0]:
    st.subheader('Compresión no es lo mismo que pandeo')
    st.write('Una barra corta bajo carga axial se estudia principalmente por **esfuerzo de compresión**. Al aumentar la esbeltez, la pérdida de estabilidad puede ocurrir antes de que el material alcance su resistencia: aparece el **pandeo**.')
    st.latex(r'\sigma_c=\frac{P}{A}')
    st.latex(r'\lambda=\frac{K L}{r},\qquad r=\sqrt{\frac{I}{A}}')
    st.markdown('<div class="gg-note"><b>Idea clave:</b> una columna puede tener una tensión axial moderada y, aun así, ser inestable si es suficientemente esbelta. Por eso el eje con menor I y menor radio de giro suele gobernar.</div>',unsafe_allow_html=True)
    st.write('La ecuación de Euler representa una columna ideal: recta, prismática, material elástico lineal, carga centrada y pequeñas deformaciones previas al pandeo. Imperfecciones, excentricidad, tensiones residuales y comportamiento inelástico reducen la capacidad real.')
with tabs[1]:
    st.subheader('Modelo visual de estabilidad')
    show=st.toggle('Mostrar modo de pandeo amplificado',value=True)
    render_column_3d({'end':end,'ratio':res.load_ratio,'show_buckling':show,'section':visual_section_payload(stype,sp)},height=650)
    st.caption('La deformada se amplifica para estudiar el modo de inestabilidad; no representa una amplitud postcrítica calculada.')
with tabs[2]:
    c1,c2=st.columns([1,1],gap='large')
    with c1:
        st.metric('K',f'{res.K:.3f}'); st.metric('Longitud efectiva KL',f'{res.effective_length_m:.3f} m'); st.metric('Eje gobernante',res.governing_axis)
        st.write(f'λy = **{res.lambda_y:.1f}** · λz = **{res.lambda_z:.1f}**')
        if res.euler_yield_limit: st.write(f'Cruce elástico orientativo √(2π²E/fy): **{res.euler_yield_limit:.1f}**. Cerca o bajo ese orden de esbeltez, Euler deja de ser una descripción suficiente del comportamiento real.')
    with c2:
        lam=np.linspace(max(10,res.lambda_governing*.35),max(220,res.lambda_governing*1.5),300); sigma=np.pi**2*(E*1000)/lam**2
        fig=go.Figure(); fig.add_trace(go.Scatter(x=lam,y=sigma,name='Euler',line=dict(color='#c8752d',width=3))); fig.add_vline(x=res.lambda_governing,line_color='#f28e1c',line_dash='dash'); fig.add_hline(y=fy,line_color='#34353a',line_dash='dot'); fig.update_layout(height=420,xaxis_title='Esbeltez λ',yaxis_title='σcr [MPa]',margin=dict(l=20,r=20,t=20,b=20),showlegend=False); st.plotly_chart(fig,use_container_width=True)
with tabs[3]:
    st.subheader('Propiedades que controlan la estabilidad')
    x1,x2,x3,x4=st.columns(4); x1.metric('A',f'{sec.area_mm2:.0f} mm²'); x2.metric('Iz',f'{sec.iz_mm4:.3e} mm⁴'); x3.metric('Iy',f'{sec.iy_mm4:.3e} mm⁴'); x4.metric('rmin',f'{min(sec.ry_mm,sec.rz_mm):.2f} mm')
    st.write('En perfiles I/H y C, la inercia respecto de los dos ejes es muy distinta. Para pandeo flexional ideal, el eje de **menor I** suele producir la menor carga crítica.')
with tabs[4]:
    st.latex(r'\sigma_c=P/A')
    st.latex(r'L_e=KL')
    st.latex(r'\lambda_y=KL/r_y,\quad \lambda_z=KL/r_z')
    st.latex(r'P_{cr}=\frac{\pi^2 E I_{min}}{(KL)^2}')
    st.latex(r'\sigma_{cr,E}=\frac{\pi^2E}{\lambda^2}')
    st.write('Factores K usados: articulada–articulada 1.0; empotrada–libre 2.0; empotrada–empotrada 0.5; empotrada–articulada 0.699.')
with tabs[5]:
    if res.load_ratio<.5: st.success('La carga seleccionada está bastante por debajo de Pcr de Euler en este modelo ideal. Esto no constituye una verificación normativa de diseño.')
    elif res.load_ratio<1: st.warning('La carga se aproxima a la carga crítica ideal. La sensibilidad a imperfecciones y excentricidad aumenta fuertemente.')
    else: st.error('La carga iguala o supera Pcr de Euler del modelo ideal: la configuración recta es inestable en esta idealización.')
    st.write('Para diseño real deben usarse las curvas, factores de reducción, límites de esbeltez y combinaciones de carga exigidos por la norma aplicable. Este módulo está orientado a comprender la mecánica, no a reemplazar una comprobación normativa.')
