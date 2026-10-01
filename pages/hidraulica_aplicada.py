from __future__ import annotations
import pandas as pd
import streamlit as st

from modules.ui_brand import render_app_header
from modules.hydraulics_applied.hydraulic_data import PORTS, SYMBOL_LIBRARY, DIRECTIONAL_VALVES, DIAGNOSTICS, READING_RULES
from modules.hydraulics_applied.hydraulic_engine import cylinder_performance, valve_descriptor, motion_from_4_3_center
from modules.hydraulics_applied.hydraulic_plotter import line_language_figure, symbol_figure, directional_valve_figure, circuit_state_figure
from modules.hydraulics_applied.machine_data import MACHINE_CASES, state_paths
from modules.hydraulics_applied.machine_plotter import machine_schematic_figure
from modules.hydraulics_applied.machine_visual3d import render_machine_hydraulics_3d

st.markdown('''
<style>
:root{--gg-orange:#f28e1c;--gg-black:#202126;--gg-line:#e4e6ea;--gg-soft:#fff7ed}
.block-container{max-width:1640px;padding-top:1rem!important;padding-bottom:2rem}
.gg-note{border:1px solid #e8e5df;background:#faf9f6;border-radius:12px;padding:.9rem 1rem;line-height:1.5}
.gg-card{border:1px solid var(--gg-line);border-radius:13px;padding:.95rem 1rem;background:#fff;height:100%;line-height:1.48}
.gg-orange{border:1px solid #f2d1a8;border-left:5px solid var(--gg-orange);border-radius:13px;padding:.95rem 1rem;background:#fffaf4;height:100%}
.gg-badge{display:inline-block;background:#fff1df;color:#a55d10;border:1px solid #f2d0a5;padding:.18rem .52rem;border-radius:999px;font-size:.78rem;font-weight:750;margin:.08rem .14rem}
</style>
''',unsafe_allow_html=True)

render_app_header(
    title='Hidráulica aplicada · Planos, circuitos y maquinaria',
    subtitle='Simbología → lectura funcional → circuito → máquina → terreno',
    section='MÁQUINAS Y COMPONENTES · POTENCIA FLUIDA',
    logo_width=188,
)

st.markdown('''<div class="gg-note"><b>Propósito:</b> conectar tres niveles que normalmente se estudian separados: <b>símbolo hidráulico</b>, <b>plano funcional</b> y <b>equipo físico</b>. Los modelos de camión y cargador son didácticos y de arquitectura genérica: enseñan cómo razonar sobre el sistema sin reproducir un circuito OEM específico.</div>''',unsafe_allow_html=True)

tabs=st.tabs(['🧭 Ruta de lectura','◉ Biblioteca','⇄ Válvulas','▶ Circuito 4/3','🚛 Camión minero','🚜 Cargador frontal','🔧 Diagnóstico','📋 De plano a terreno'])

with tabs[0]:
    st.subheader('Del símbolo al equipo')
    cols=st.columns(4)
    steps=[
        ('1','Reconocer','Símbolos, puertos, líneas principales, pilotajes y drenajes.'),
        ('2','Seguir la energía','Depósito → bomba → control → actuador → retorno.'),
        ('3','Cambiar el estado','Leer qué conexiones habilita la válvula en cada posición.'),
        ('4','Ir a terreno','Ubicar físicamente bomba, manifold, mangueras, cilindros y puntos de medición.'),
    ]
    for c,(n,t,txt) in zip(cols,steps):
        with c: st.markdown(f'<div class="gg-card"><span style="color:#f28e1c;font-weight:800">{n}</span><br><b>{t}</b><br>{txt}</div>',unsafe_allow_html=True)
    st.markdown('### Reglas para leer un plano')
    c1,c2=st.columns([1.05,.95])
    with c1:
        df=pd.DataFrame([{'Paso':n,'Acción':t,'Qué buscar':txt} for n,t,txt in READING_RULES]);st.dataframe(df,use_container_width=True,hide_index=True)
    with c2:
        st.plotly_chart(line_language_figure(),use_container_width=True,key='hyd_route_lines')
    st.markdown('### Relaciones mínimas que hay que tener presentes')
    a,b,c=st.columns(3)
    with a: st.latex(r'F=pA');st.caption('La presión se relaciona con la fuerza/carga.')
    with b: st.latex(r'v=Q/A');st.caption('El caudal se relaciona con la velocidad del actuador.')
    with c: st.latex(r'P_h=\Delta p\,Q');st.caption('La potencia exige analizar presión y caudal simultáneamente.')

with tabs[1]:
    st.subheader('Biblioteca técnica de símbolos')
    categories=list(dict.fromkeys(v['category'] for v in SYMBOL_LIBRARY.values()))
    cat=st.selectbox('Familia',categories,key='hyd_lib_cat')
    names=[k for k,v in SYMBOL_LIBRARY.items() if v['category']==cat]
    name=st.selectbox('Componente',names,key='hyd_lib_name')
    item=SYMBOL_LIBRARY[name]
    c1,c2=st.columns([.95,1.05],gap='large')
    with c1: st.plotly_chart(symbol_figure(item['symbol'],name),use_container_width=True,key=f"hyd_sym_{item['symbol']}")
    with c2:
        st.markdown(f'## {name}')
        st.markdown(f'<span class="gg-badge">{item["category"]}</span>',unsafe_allow_html=True)
        st.write('**Función:**',item['function']);st.write('**Puertos:**',item['ports']);st.write('**Condición de referencia:**',item['rest']);st.write('**Cómo reconocerlo:**',item['reading'])
    q1,q2,q3=st.columns(3)
    with q1: st.markdown(f'<div class="gg-orange"><b>Principio físico</b><br>{item["principle"]}</div>',unsafe_allow_html=True)
    with q2: st.markdown(f'<div class="gg-card"><b>Qué revisar en terreno</b><br>{item["field"]}</div>',unsafe_allow_html=True)
    with q3: st.markdown('<div class="gg-card"><b>Anomalías frecuentes</b><br>'+'<br>'.join('• '+x for x in item['failures'])+'</div>',unsafe_allow_html=True)

with tabs[2]:
    st.subheader('Válvulas direccionales · una posición a la vez')
    valve=st.selectbox('Configuración',list(DIRECTIONAL_VALVES.keys()),index=4,key='hyd_valve')
    desc=valve_descriptor(valve,DIRECTIONAL_VALVES)
    positions=['Izquierda','Derecha'] if desc['positions']==2 else ['Izquierda','Centro','Derecha']
    pos=st.radio('Posición a estudiar',positions,horizontal=True,index=1 if len(positions)==3 else 0,key='hyd_valve_pos')
    act=st.selectbox('Accionamiento',['Solenoide + retorno por resorte','Palanca + retorno por resorte','Pilotaje hidráulico'],key='hyd_act')
    c1,c2=st.columns([1.25,.75])
    with c1: st.plotly_chart(directional_valve_figure(valve,pos,act),use_container_width=True,key='hyd_dir_fig')
    with c2:
        st.metric('Vías',desc['ports']);st.metric('Posiciones',desc['positions']);st.write('**Reposo:**',desc['rest'])
        key_map={'Izquierda':'left','Centro':'center','Derecha':'right'};st.write('**Estado seleccionado:**',DIRECTIONAL_VALVES[valve].get(key_map[pos],'No aplica'))
        st.write('**Aplicación típica:**',DIRECTIONAL_VALVES[valve]['use'])

with tabs[3]:
    st.subheader('Circuito base 4/3 · estado, movimiento y números')
    center=st.selectbox('Tipo de centro',['4/3 centro cerrado','4/3 centro tándem','4/3 centro flotante','4/3 centro abierto'],key='hyd_center')
    state=st.radio('Estado',['Izquierda','Centro','Derecha'],horizontal=True,index=1,key='hyd_state')
    c1,c2=st.columns([1.25,.75])
    with c1: st.plotly_chart(circuit_state_figure(center,state),use_container_width=True,key=f'hyd_base_{center}_{state}')
    with c2:
        st.markdown('<div class="gg-orange"><b>Movimiento esperado</b><br>'+motion_from_4_3_center(center,state)+'</div>',unsafe_allow_html=True)
        st.write('La lectura debe hacerse siempre en el orden: **fuente → control → actuador → retorno**.')
    with st.expander('Relacionar el circuito con fuerza y velocidad',expanded=True):
        a,b,c,d,e=st.columns(5)
        flow=a.number_input('Q [L/min]',.1,value=120.0,step=5.0,key='hyd_q')
        bore=b.number_input('Ø pistón [mm]',10.0,value=160.0,step=5.0,key='hyd_bore')
        rod=c.number_input('Ø vástago [mm]',1.0,value=90.0,step=5.0,key='hyd_rod')
        pressure=d.number_input('Presión [bar]',0.0,value=180.0,step=5.0,key='hyd_p')
        load=e.number_input('Carga [kN]',0.0,value=150.0,step=10.0,key='hyd_load')
        try:
            r=cylinder_performance(flow,bore,rod,pressure,load);x1,x2,x3,x4=st.columns(4)
            x1.metric('v avance',f'{r.extension_speed_m_s*1000:.1f} mm/s');x2.metric('v retroceso',f'{r.retraction_speed_m_s*1000:.1f} mm/s');x3.metric('F avance',f'{r.extension_force_n/1000:.1f} kN');x4.metric('F retroceso',f'{r.retraction_force_n/1000:.1f} kN')
        except ValueError as exc: st.error(str(exc))


def machine_tab(machine:str,prefix:str):
    st.subheader(machine+' · circuito y modelo conectados')
    subs=list(MACHINE_CASES[machine].keys())
    subsystem=st.selectbox('Sistema a estudiar',subs,key=f'{prefix}_sub')
    info=MACHINE_CASES[machine][subsystem]
    state=st.radio('Estado / mando',info['states'],horizontal=True,key=f'{prefix}_state')
    paths=state_paths(machine,subsystem,state)
    top1,top2,top3=st.columns(3)
    with top1: st.markdown(f'<div class="gg-card"><b>Movimiento</b><br>{paths["motion"]}</div>',unsafe_allow_html=True)
    with top2: st.markdown('<div class="gg-card"><b>Componentes</b><br>'+' · '.join(info['components'])+'</div>',unsafe_allow_html=True)
    with top3: st.markdown('<div class="gg-card"><b>Qué medir en terreno</b><br>'+' · '.join(info['field'])+'</div>',unsafe_allow_html=True)
    st.caption(info['description'])
    c1,c2=st.columns([1.05,1.25],gap='medium')
    with c1:
        st.markdown('### Plano funcional')
        st.plotly_chart(machine_schematic_figure(machine,subsystem,state,paths),use_container_width=True,key=f'{prefix}_schem')
        st.write('**Ruta de presión:**', ' → '.join(paths['pressure']) if paths['pressure'] else 'sin ruta activa')
        st.write('**Retorno:**', ' → '.join(paths['return']) if paths['return'] else 'sin retorno principal activo')
        if paths['pilot']: st.write('**Mando / LS:**',' → '.join(paths['pilot']))
    with c2:
        st.markdown('### Modelo 3D de la máquina')
        amp=st.slider('Amplificación visual',.5,2.5,1.0,.1,key=f'{prefix}_amp')
        speed=st.slider('Velocidad de animación',.25,2.0,1.0,.25,key=f'{prefix}_speed')
        render_machine_hydraulics_3d({'machine':machine,'subsystem':subsystem,'state':state,'motion':paths['motion'],'visual_amp':amp,'speed':speed},height=610)
    st.markdown('### Cómo llevarlo a terreno')
    q1,q2,q3,q4=st.columns(4)
    for col,title,txt in zip([q1,q2,q3,q4],['1 · Identifique','2 · Siga líneas','3 · Mida','4 · Compare'],['Ubique físicamente bomba, banco, actuadores y retorno.','Relacione P/T/A/B con mangueras y manifolds reales.','Seleccione presión/caudal/temperatura según el síntoma.','Compare valor real con el comportamiento esperado del plano.']):
        with col: st.markdown(f'<div class="gg-card"><b>{title}</b><br>{txt}</div>',unsafe_allow_html=True)

with tabs[4]: machine_tab('Camión minero','truck')
with tabs[5]: machine_tab('Cargador frontal','loader')

with tabs[6]:
    st.subheader('Diagnóstico inicial · síntoma → plano → dato → comprobación')
    symptom=st.selectbox('Síntoma',list(DIAGNOSTICS.keys()),key='hyd_diag')
    cols=st.columns(2)
    for i,step in enumerate(DIAGNOSTICS[symptom]):
        with cols[i%2]: st.markdown(f'<div class="gg-card"><b>CONTROL {i+1}</b><br>{step}</div>',unsafe_allow_html=True)
    st.markdown('### Tres preguntas físicas que no se deben perder')
    a,b,c=st.columns(3)
    with a: st.latex(r'Q=0\Rightarrow v=0');st.caption('¿Llega caudal?')
    with b: st.latex(r'v=Q/A');st.caption('¿El caudal es suficiente?')
    with c: st.latex(r'p_{req}\approx F/A');st.caption('¿La presión vence la carga?')

with tabs[7]:
    st.subheader('De plano a máquina · método de trabajo')
    rows=[
        ['Depósito / tanque','Depósito físico, respiradero, visor de nivel','nivel, espuma, temperatura, contaminación'],
        ['Bomba','Bomba sobre motor/transmisión o grupo hidráulico','ruido, succión, presión, caudal, drenaje'],
        ['P','Manguera/tubería principal de presión','presión en carga, pulsación, temperatura'],
        ['T','Retorno hacia tanque','contrapresión, temperatura, restricciones'],
        ['A / B','Líneas de trabajo hacia cilindro/motor','presiones diferenciales y sentido de movimiento'],
        ['X / LS','Pilotaje / load sensing','presión de mando y respuesta del control'],
        ['L / Y','Drenaje de carcasa o pilotaje','contrapresión y fuga interna'],
    ]
    st.dataframe(pd.DataFrame(rows,columns=['En el plano','En la máquina','Qué comprobar']),use_container_width=True,hide_index=True)
    st.markdown('### Cierre de lectura')
    st.markdown('''<div class="gg-orange"><b>La meta no es memorizar un diagrama.</b><br>La meta es poder tomar un plano hidráulico, identificar la función, ubicar los componentes reales en una máquina, predecir qué debería ocurrir y decidir dónde medir para comprobarlo.</div>''',unsafe_allow_html=True)

with st.expander('Alcance y referencias'):
    st.write('Base del módulo previo: programa MEC-373 UTFSM, Festo Didactic TP 501, CASE How to Read Symbols in a Hydraulic Schematic, Hydraulic Course Manual y BFPA Fluid Power Engineer’s Data Book.')
    st.write('El video aportado se usa como referencia conceptual para conectar circuitos con funciones de maquinaria móvil. Los esquemas y modelos de esta herramienta son redibujos didácticos originales y genéricos; no pretenden reproducir documentación OEM ni sustituir manuales de servicio.')
