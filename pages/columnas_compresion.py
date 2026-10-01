from __future__ import annotations
import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from modules.ui_brand import render_app_header
from modules.resmat_sections import section_data, profile_params_from_sidebar, visual_section_payload
from modules.column_engine import solve_column, K_FACTORS, johnson_stress_mpa
from modules.column_visual3d import render_column_3d

st.markdown('''
<style>
.block-container{max-width:1480px;padding-top:1.25rem!important}
.gg-note{border:1px solid #e9e2d7;border-left:4px solid #f28e1c;border-radius:12px;padding:.85rem 1rem;background:#fffaf3}
.gg-card{border:1px solid #e7dfd2;border-radius:14px;background:#fffdf9;padding:1rem;height:100%}
.gg-mini{font-size:.92rem;color:#555}
</style>
''', unsafe_allow_html=True)
render_app_header(
    title='Columnas · Compresión y Pandeo',
    subtitle='Carga axial · esfuerzo de compresión · esbeltez · longitud efectiva · Euler · modo crítico · comparación de columnas.',
    section='RESISTENCIA Y ESTRUCTURAS', logo_width=188
)

with st.sidebar:
    st.header('Columna A')
    L=float(st.number_input('Longitud real L [m]',min_value=.1,value=3.0,step=.25))
    P=float(st.number_input('Carga axial P [kN]',min_value=0.0,value=100.0,step=10.0))
    end=st.selectbox('Condición de extremos',list(K_FACTORS.keys()))
    st.divider(); st.subheader('Material')
    mat=st.selectbox('Material',['Acero','Aluminio','Madera','Personalizado'])
    vals={'Acero':(200.,250.),'Aluminio':(69.,150.),'Madera':(12.,35.)}
    if mat=='Personalizado':
        E=float(st.number_input('E [GPa]',min_value=.001,value=200.)); fy=float(st.number_input('Límite de referencia fy [MPa]',min_value=.1,value=250.))
    else:
        E,fy=vals[mat]; st.caption(f'E={E:g} GPa · fy={fy:g} MPa (referencial)')
    st.divider(); st.subheader('Sección A')
    stype=st.selectbox('Geometría',['Rectangular','Circular maciza','Tubular circular','Perfil I / H','Canal C','Propiedades ingresadas'])
    sp=profile_params_from_sidebar(st,stype,'col_')

sec=section_data(stype,sp); res=solve_column(P,L,E,sec,end,fy)

m1,m2,m3,m4,m5=st.columns(5)
m1.metric('σ=P/A',f'{res.sigma_axial_mpa:.2f} MPa')
m2.metric('λ gobernante',f'{res.lambda_governing:.1f}')
m3.metric('Pcr Euler',f'{res.pcr_kn:.1f} kN')
m4.metric('P/Pcr',f'{res.load_ratio:.3f}')
m5.metric('Eje crítico',res.governing_axis.split(' ')[0])

st.markdown(r'''<div class="gg-note"><b>Ruta física:</b> carga axial <b>P</b> → esfuerzo uniforme <b>σ=P/A</b> → longitud efectiva <b>KL</b> → esbeltez <b>λ=KL/r</b> → carga crítica de Euler <b>Pcr</b> → modo crítico de pandeo.</div>''',unsafe_allow_html=True)

tabs=st.tabs(['📘 Concepto','🏗️ Columna 3D','📐 Esbeltez y estabilidad','🧱 Sección','⚖️ Comparador','∑ Ecuaciones','🧠 Interpretación'])

with tabs[0]:
    st.subheader('Compresión, estabilidad y pandeo no son lo mismo')
    c1,c2,c3=st.columns(3)
    with c1: st.markdown('<div class="gg-card"><b>1 · Compresión</b><div class="gg-mini">Si la carga está centrada, el estado medio previo al pandeo se lee mediante σ=P/A. En miembros cortos suele dominar la resistencia del material.</div></div>',unsafe_allow_html=True)
    with c2: st.markdown('<div class="gg-card"><b>2 · Esbeltez</b><div class="gg-mini">La estabilidad depende de KL/r. La longitud, los apoyos y el radio de giro pueden hacer que una pieza con tensión moderada sea inestable.</div></div>',unsafe_allow_html=True)
    with c3: st.markdown('<div class="gg-card"><b>3 · Pandeo</b><div class="gg-mini">Euler determina la pérdida de estabilidad de una columna ideal. El modo crítico define una forma de pandeo, no su amplitud postcrítica.</div></div>',unsafe_allow_html=True)
    st.markdown('### Eje débil')
    st.write('La columna puede pandear respecto de cualquiera de los ejes principales. El eje asociado al menor valor de **EI** produce la menor carga crítica y gobierna este modelo ideal.')
    st.latex(r'P_{cr,y}=\frac{\pi^2EI_y}{(KL)^2},\qquad P_{cr,z}=\frac{\pi^2EI_z}{(KL)^2}')
    st.markdown('<div class="gg-note"><b>Importante:</b> imperfecciones iniciales, excentricidad de la carga, tensiones residuales, pandeo local y comportamiento inelástico no están incluidos en Euler ideal.</div>',unsafe_allow_html=True)

with tabs[1]:
    st.subheader('Modo crítico 3D')
    c1,c2=st.columns([1,2])
    with c1:
        show=st.toggle('Mostrar modo crítico',value=True)
        amp=st.slider('Amplificación visual del modo',0.25,2.0,1.0,.05)
        show_original=st.toggle('Mostrar eje recto de referencia',value=True)
        st.markdown('<div class="gg-card"><b>Cómo leer el 3D</b><div class="gg-mini">La curva naranja es un <b>modo crítico normalizado</b>. Su amplitud se controla solo para poder verlo: no se calcula a partir de P/Pcr y no representa una deformación postcrítica real.</div></div>',unsafe_allow_html=True)
        st.metric('Longitud efectiva KL',f'{res.effective_length_m:.3f} m')
        st.metric('r mínimo',f'{res.rmin_mm:.2f} mm')
        st.metric('I mínimo',f'{res.imin_mm4:.3e} mm⁴')
    with c2:
        render_column_3d({
            'end':end,'load_ratio':res.load_ratio,'show_buckling':show,'visual_amp':amp,
            'show_original':show_original,'section':visual_section_payload(stype,sp),
            'buckling_axis':res.governing_axis[0],'axis_label':res.governing_axis,
        },height=690)
    st.caption('La geometría 3D conserva la forma de la sección seleccionada. La deformada se amplifica solo con fines didácticos.')

with tabs[2]:
    st.subheader('Esbeltez y estabilidad de Euler')
    c1,c2=st.columns([.9,1.5],gap='large')
    with c1:
        st.metric('Factor K',f'{res.K:.3f}')
        st.metric('Longitud efectiva KL',f'{res.effective_length_m:.3f} m')
        st.metric('λy',f'{res.lambda_y:.1f}')
        st.metric('λz',f'{res.lambda_z:.1f}')
        st.metric('Pcr,y',f'{res.pcr_y_kn:.1f} kN')
        st.metric('Pcr,z',f'{res.pcr_z_kn:.1f} kN')
        if res.euler_yield_intersection:
            st.caption(f'Intersección Euler–fy: λ ≈ {res.euler_yield_intersection:.1f}. Transición Johnson–Euler clásica: Cc ≈ {res.johnson_transition:.1f}. Son referencias didácticas, no límites normativos.')
    with c2:
        lam=np.linspace(10,max(260,res.lambda_governing*1.55),360)
        euler=np.pi**2*(E*1000)/lam**2
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=lam,y=euler,name='Euler elástico',line=dict(color='#c8752d',width=3)))
        if res.johnson_transition:
            lj=np.linspace(0.1,res.johnson_transition,180); sj=np.array([max(0,johnson_stress_mpa(v,E,fy)) for v in lj])
            fig.add_trace(go.Scatter(x=lj,y=sj,name='Johnson (referencia)',line=dict(color='#4b4c50',width=2,dash='dash')))
        fig.add_vline(x=res.lambda_governing,line_color='#f28e1c',line_dash='dot')
        fig.add_hline(y=fy,line_color='#777a80',line_dash='dot')
        fig.update_layout(height=470,xaxis_title='Esbeltez λ',yaxis_title='Tensión crítica ideal [MPa]',margin=dict(l=20,r=20,t=20,b=20),legend=dict(orientation='h'))
        st.plotly_chart(fig,use_container_width=True)
        st.caption('Johnson se muestra solo como puente didáctico hacia comportamiento inelástico. El diseño real debe seguir la norma aplicable.')

with tabs[3]:
    st.subheader('Propiedades que controlan la estabilidad')
    x1,x2,x3,x4,x5=st.columns(5)
    x1.metric('A',f'{sec.area_mm2:.0f} mm²');x2.metric('Iz',f'{sec.iz_mm4:.3e}');x3.metric('Iy',f'{sec.iy_mm4:.3e}');x4.metric('rz',f'{sec.rz_mm:.2f} mm');x5.metric('ry',f'{sec.ry_mm:.2f} mm')
    if abs(sec.iy_mm4-sec.iz_mm4)/max(sec.iy_mm4,sec.iz_mm4)>.15:
        st.warning('La sección es marcadamente anisótropa respecto de sus ejes principales: orientar el perfil cambia fuertemente la estabilidad.',icon='📐')
    else:
        st.info('Las rigideces respecto de ambos ejes son similares; el pandeo flexional ideal no presenta una dirección débil tan marcada.',icon='ℹ️')
    st.write('El radio de giro resume la relación entre distribución de área e inercia:')
    st.latex(r'r_y=\sqrt{I_y/A},\qquad r_z=\sqrt{I_z/A}')

with tabs[4]:
    st.subheader('Comparador de columnas')
    st.write('El caso **A** es la columna que ya definiste en la barra lateral. Para una comparación limpia, conserva el mismo **P, L, E** y cambia en B solo la geometría o la condición de extremos que quieras estudiar.')
    q1,q2=st.columns(2)
    with q1:
        st.markdown('#### Caso A · actual')
        st.write(f'**{stype}** · {end}')
        st.write(f'P = {P:g} kN · L = {L:g} m · E = {E:g} GPa')
    with q2:
        st.markdown('#### Caso B · comparación')
        end_b=st.selectbox('Condición de extremos B',list(K_FACTORS.keys()),index=list(K_FACTORS.keys()).index(end),key='cmp_end_b')
        stype_b=st.selectbox('Geometría B',['Rectangular','Circular maciza','Tubular circular','Perfil I / H','Canal C','Propiedades ingresadas'],index=0,key='cmp_type_b')
        sp_b=profile_params_from_sidebar(st,stype_b,'cmp_col_b_')
    sec_b=section_data(stype_b,sp_b); res_b=solve_column(P,L,E,sec_b,end_b,fy)

    st.markdown('### Resultados comparados')
    rows=[
        ('A [mm²]',sec.area_mm2,sec_b.area_mm2),('Imin [mm⁴]',res.imin_mm4,res_b.imin_mm4),('rmin [mm]',res.rmin_mm,res_b.rmin_mm),
        ('K',res.K,res_b.K),('KL [m]',res.effective_length_m,res_b.effective_length_m),('λ',res.lambda_governing,res_b.lambda_governing),
        ('Pcr [kN]',res.pcr_kn,res_b.pcr_kn),('P/Pcr',res.load_ratio,res_b.load_ratio),('σ=P/A [MPa]',res.sigma_axial_mpa,res_b.sigma_axial_mpa),
    ]
    import pandas as pd
    df=pd.DataFrame(rows,columns=['Magnitud','Caso A','Caso B'])
    st.dataframe(df,use_container_width=True,hide_index=True)

    r1,r2,r3,r4=st.columns(4)
    r1.metric('Pcr B / A',f'{res_b.pcr_kn/res.pcr_kn:.3f}×')
    r2.metric('λ B / A',f'{res_b.lambda_governing/res.lambda_governing:.3f}×')
    r3.metric('rmin B / A',f'{res_b.rmin_mm/res.rmin_mm:.3f}×')
    r4.metric('Área B / A',f'{sec_b.area_mm2/sec.area_mm2:.3f}×')

    st.markdown('### Comparación 3D del modo crítico')
    amp_cmp=st.slider('Amplificación visual común',0.25,1.6,.85,.05,key='cmp_amp')
    v1,v2=st.columns(2)
    with v1:
        st.markdown('**A · '+stype+'**')
        render_column_3d({'end':end,'load_ratio':res.load_ratio,'show_buckling':True,'visual_amp':amp_cmp,'show_original':True,'section':visual_section_payload(stype,sp),'buckling_axis':res.governing_axis[0],'axis_label':res.governing_axis},height=500)
    with v2:
        st.markdown('**B · '+stype_b+'**')
        render_column_3d({'end':end_b,'load_ratio':res_b.load_ratio,'show_buckling':True,'visual_amp':amp_cmp,'show_original':True,'section':visual_section_payload(stype_b,sp_b),'buckling_axis':res_b.governing_axis[0],'axis_label':res_b.governing_axis},height=500)
    st.caption('Los dos modos se muestran con la misma amplificación visual. La amplitud no representa deformación postcrítica; sirve para comparar forma modal, eje de pandeo y condiciones de extremo.')

    figc=go.Figure()
    figc.add_bar(name='Caso A',x=['Pcr'],y=[res.pcr_kn])
    figc.add_bar(name='Caso B',x=['Pcr'],y=[res_b.pcr_kn])
    figc.update_layout(height=310,barmode='group',yaxis_title='Pcr [kN]',margin=dict(l=20,r=20,t=10,b=20),legend=dict(orientation='h'))
    st.plotly_chart(figc,use_container_width=True)

    if res_b.pcr_kn>res.pcr_kn:
        st.info('En este modelo ideal, el caso B aumenta Pcr respecto de A. Revisa si el cambio proviene de mayor Imin, menor K o ambas cosas.',icon='🔎')
    elif res_b.pcr_kn<res.pcr_kn:
        st.info('En este modelo ideal, el caso B reduce Pcr respecto de A. Observa la combinación entre Imin, radio de giro y longitud efectiva.',icon='🔎')
    else:
        st.info('Ambos casos producen prácticamente la misma carga crítica ideal.',icon='🔎')

with tabs[5]:
    st.subheader('Ecuaciones ordenadas por significado')
    st.markdown('**1 · Compresión axial**'); st.latex(r'\sigma_c=\frac{P}{A}')
    st.markdown('**2 · Propiedades geométricas**'); st.latex(r'r_y=\sqrt{\frac{I_y}{A}},\qquad r_z=\sqrt{\frac{I_z}{A}}')
    st.markdown('**3 · Condición de extremos**'); st.latex(r'L_e=KL')
    st.markdown('**4 · Esbeltez**'); st.latex(r'\lambda_y=\frac{KL}{r_y},\qquad \lambda_z=\frac{KL}{r_z}')
    st.markdown('**5 · Euler por eje principal**'); st.latex(r'P_{cr,y}=\frac{\pi^2EI_y}{(KL)^2},\qquad P_{cr,z}=\frac{\pi^2EI_z}{(KL)^2}')
    st.markdown('**6 · Forma equivalente en tensión**'); st.latex(r'\sigma_{cr,E}=\frac{\pi^2E}{\lambda^2}')
    st.markdown('**7 · Referencia Johnson–Euler**'); st.latex(r'C_c=\sqrt{\frac{2\pi^2E}{f_y}}')
    st.write('El factor K y la ecuación de Euler describen una idealización. El pandeo real exige considerar imperfecciones, excentricidad, inelasticidad, pandeo local y la norma de diseño correspondiente.')

with tabs[6]:
    st.subheader('Interpretación del caso')
    c1,c2=st.columns(2)
    with c1:
        st.markdown(f'<div class="gg-card"><b>Compresión</b><div class="gg-mini">La carga P = {P:.1f} kN produce un esfuerzo medio σ = <b>{res.sigma_axial_mpa:.2f} MPa</b>. Esta lectura por sí sola no determina la estabilidad de la columna.</div></div>',unsafe_allow_html=True)
        st.markdown(f'<div class="gg-card"><b>Estabilidad</b><div class="gg-mini">El eje gobernante es <b>{res.governing_axis}</b>, con rmin = <b>{res.rmin_mm:.2f} mm</b>, λ = <b>{res.lambda_governing:.1f}</b> y Pcr = <b>{res.pcr_kn:.1f} kN</b>.</div></div>',unsafe_allow_html=True)
    with c2:
        if res.load_ratio<.5: st.success('P está bastante por debajo de Pcr de Euler en esta idealización. Esto no constituye una verificación normativa.')
        elif res.load_ratio<1: st.warning('P se aproxima a Pcr ideal. La sensibilidad a imperfecciones y excentricidad crece fuertemente.')
        else: st.error('P iguala o supera Pcr de Euler: la configuración recta pierde estabilidad en este modelo ideal.')
        st.markdown('<div class="gg-note"><b>Qué queda fuera:</b> imperfección inicial, carga excéntrica, interacción flexo-compresión, pandeo local, pandeo lateral/torsional, tensiones residuales y reglas normativas de resistencia.</div>',unsafe_allow_html=True)
