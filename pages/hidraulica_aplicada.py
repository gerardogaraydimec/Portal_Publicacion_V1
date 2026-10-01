from __future__ import annotations
import pandas as pd
import streamlit as st

from modules.ui_brand import render_app_header
from modules.hydraulics_applied.hydraulic_data import SYMBOL_LIBRARY, DIRECTIONAL_VALVES, DIAGNOSTICS, READING_RULES
from modules.hydraulics_applied.hydraulic_engine import cylinder_performance, valve_descriptor, motion_from_4_3_center
from modules.hydraulics_applied.hydraulic_plotter import line_language_figure, symbol_figure, directional_valve_figure, circuit_state_figure
from modules.hydraulics_applied.system_cases import SYSTEM_CASES, system_state, course_comparison_rows, diagnostic_cases
from modules.hydraulics_applied.animated_system import render_animated_hydraulic_system
from modules.hydraulics_applied.machine_visual3d import render_machine_hydraulics_3d

st.markdown('''
<style>
:root{--gg-orange:#f28e1c;--gg-black:#202126;--gg-line:#e4e6ea;--gg-soft:#fff7ed;--gg-blue:#2a63b8;--gg-red:#d84030;--gg-yellow:#d6b72c}
.block-container{max-width:1700px;padding-top:1rem!important;padding-bottom:2rem}
.gg-note{border:1px solid #e8e5df;background:#faf9f6;border-radius:12px;padding:.9rem 1rem;line-height:1.5}
.gg-card{border:1px solid var(--gg-line);border-radius:13px;padding:.95rem 1rem;background:#fff;height:100%;line-height:1.48}
.gg-orange{border:1px solid #f2d1a8;border-left:5px solid var(--gg-orange);border-radius:13px;padding:.95rem 1rem;background:#fffaf4;height:100%}
.gg-dark{background:#202126;color:#f8f2e9;border-radius:14px;padding:1.05rem 1.15rem;border:1px solid #3a3c42}
.gg-badge{display:inline-block;background:#fff1df;color:#a55d10;border:1px solid #f2d0a5;padding:.18rem .52rem;border-radius:999px;font-size:.78rem;font-weight:750;margin:.08rem .14rem}
.gg-route{font-weight:750;letter-spacing:.01em}.gg-route .p{color:#d84030}.gg-route .r{color:#2a63b8}.gg-route .c{color:#a88b08}.gg-route .s{color:#3e854a}
</style>
''',unsafe_allow_html=True)

render_app_header(
    title='Hidráulica aplicada · Sistemas de planta y equipos móviles',
    subtitle='Componente → plano funcional → estado → movimiento → medición → diagnóstico',
    section='MÁQUINAS Y COMPONENTES · POTENCIA FLUIDA',
    logo_width=188,
)

st.markdown('''<div class="gg-note"><b>Propósito:</b> estudiar la hidráulica como ocurre en terreno: no basta con reconocer un símbolo. Hay que seguir el recorrido del aceite, entender qué componente sostiene o mueve la carga, relacionar el plano con la máquina y decidir dónde medir. Esta versión separa explícitamente <b>sistemas estacionarios</b> y <b>equipos móviles</b>, e incorpora una vista animada inspirada en la lógica del video aportado.</div>''',unsafe_allow_html=True)

TABS=st.tabs(['🧭 Arquitectura','🏭 Sistemas estacionarios','🚛 Camión minero','🚜 Cargador frontal','◉ Componentes','⇄ Válvulas','🔧 Diagnóstico','🦺 Terreno y seguridad'])

with TABS[0]:
    st.subheader('La misma hidráulica, dos contextos de aplicación')
    st.markdown('La lectura funcional es la misma, pero la forma de inspeccionar cambia según el equipo, la maniobra y el riesgo.')
    df=pd.DataFrame(course_comparison_rows(),columns=['Aspecto','Sistema de planta / estacionario','Equipo móvil'])
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.markdown('### Secuencia funcional base')
    cols=st.columns(7)
    seq=[('1','Depósito','almacena'),('2','Bomba','genera caudal'),('3','Presión','limita/protege'),('4','Direccional','dirige'),('5','Actuador','hace trabajo'),('6','Retorno','devuelve'),('7','Filtro','protege')]
    for col,(n,t,s) in zip(cols,seq):
        with col: st.markdown(f'<div class="gg-card"><b style="color:#f28e1c">{n}</b><br><b>{t}</b><br><span style="font-size:.86rem;color:#666">{s}</span></div>',unsafe_allow_html=True)
    st.markdown('### Lenguaje de líneas usado en las animaciones')
    a,b=st.columns([1.0,1.2])
    with a:
        st.plotly_chart(line_language_figure(),use_container_width=True,key='hydv2_lines')
    with b:
        st.markdown('''<div class="gg-dark"><b>Rojo</b> · presión / potencia activa<br><b>Azul</b> · retorno a tanque<br><b>Verde</b> · succión desde depósito<br><b>Amarillo</b> · pilotaje / load sensing / señal de control<br><br><b>Idea clave:</b> la bomba entrega caudal; la presión aparece cuando ese caudal encuentra resistencia. El actuador solo se mueve si existe caudal, ruta de retorno y fuerza hidráulica suficiente.</div>''',unsafe_allow_html=True)
    st.markdown('### Relaciones mínimas')
    c1,c2,c3,c4=st.columns(4)
    with c1: st.latex(r'F=pA');st.caption('Presión + área → fuerza')
    with c2: st.latex(r'v=Q/A');st.caption('Caudal + área → velocidad')
    with c3: st.latex(r'P_h=\Delta p\,Q');st.caption('Potencia hidráulica')
    with c4: st.latex(r'p_{req}\approx F_{res}/A');st.caption('La carga define presión requerida')


def system_view(machine:str,prefix:str):
    subs=list(SYSTEM_CASES[machine].keys())
    subsystem=st.selectbox('Sistema a estudiar',subs,key=f'{prefix}_sub')
    meta=SYSTEM_CASES[machine][subsystem]
    state=st.radio('Estado / mando',meta['states'],horizontal=True,key=f'{prefix}_state')
    data=system_state(machine,subsystem,state)
    payload={
        'machine':machine,'subsystem':subsystem,'state':state,'states':meta['states'],
        'motion':data['motion'],'machine_value':data['machine_value'],'pressure':data['pressure'],
        'return':data['return'],'pilot':data['pilot'],'suction':data['suction'],'drain':data.get('drain',[]),
        'notes':data.get('notes',[]),'active_components':data.get('active_components',[]),
    }
    k1,k2,k3,k4=st.columns(4)
    with k1: st.markdown(f'<div class="gg-card"><b>Movimiento</b><br>{data["motion"]}</div>',unsafe_allow_html=True)
    with k2: st.markdown('<div class="gg-card"><b>Componentes críticos</b><br>'+' · '.join(meta['components'])+'</div>',unsafe_allow_html=True)
    with k3: st.markdown('<div class="gg-card"><b>Qué medir</b><br>'+' · '.join(meta['field'])+'</div>',unsafe_allow_html=True)
    with k4: st.markdown('<div class="gg-orange"><b>Riesgo</b><br>'+' · '.join(meta['risks'])+'</div>',unsafe_allow_html=True)
    st.caption(meta['description'])
    st.markdown('### Vista funcional animada · plano + actuador + máquina')
    render_animated_hydraulic_system(payload,height=690)
    st.markdown('### Rutas activas del estado seleccionado')
    r1,r2,r3=st.columns(3)
    with r1: st.markdown('<div class="gg-card"><b style="color:#d84030">Presión</b><br>'+(' → '.join(data['pressure']) if data['pressure'] else 'Sin ruta de presión activa')+'</div>',unsafe_allow_html=True)
    with r2: st.markdown('<div class="gg-card"><b style="color:#2a63b8">Retorno</b><br>'+(' → '.join(data['return']) if data['return'] else 'Sin retorno principal activo')+'</div>',unsafe_allow_html=True)
    with r3: st.markdown('<div class="gg-card"><b style="color:#a88b08">Mando / LS</b><br>'+(' → '.join(data['pilot']) if data['pilot'] else 'Sin señal destacada')+'</div>',unsafe_allow_html=True)
    with st.expander('Modelo físico 3D · relación con la máquina',expanded=True):
        a,b=st.columns([.28,.72])
        with a:
            amp=st.slider('Amplificación visual',.5,2.5,1.0,.1,key=f'{prefix}_amp')
            speed=st.slider('Velocidad',.25,2.0,1.0,.25,key=f'{prefix}_speed')
            st.markdown('**Qué buscar**')
            st.write('• qué actuador está asociado al mando')
            st.write('• qué parte de la máquina se mueve')
            st.write('• qué líneas deberían presurizarse')
            st.write('• qué elemento sostiene/controla la carga')
        with b:
            p3={**payload,'visual_amp':amp,'speed':speed}
            render_machine_hydraulics_3d(p3,height=610)
    if machine!='Sistema estacionario':
        st.markdown('### Traducción a terreno')
        t1,t2,t3,t4=st.columns(4)
        items=[('1 · Función','¿Qué maniobra intenta hacer el operador?'),('2 · Actuador','¿Qué cilindro/motor produce esa maniobra?'),('3 · Ruta','¿Qué líneas deben tener presión y retorno?'),('4 · Dato','¿Dónde medir para confirmar la hipótesis?')]
        for col,(tt,tx) in zip([t1,t2,t3,t4],items):
            with col: st.markdown(f'<div class="gg-card"><b>{tt}</b><br>{tx}</div>',unsafe_allow_html=True)

with TABS[1]:
    st.subheader('Sistemas estacionarios · unidad hidráulica, cilindro y prensa')
    st.markdown('En planta, los puntos de medición suelen ser más estables y las tuberías son fijas. El foco es reconstruir la secuencia de energía y separar problemas de <b>presión</b>, <b>caudal</b> y <b>carga</b>.',unsafe_allow_html=True)
    system_view('Sistema estacionario','stat')
    with st.expander('Calcular fuerza y velocidad del cilindro',expanded=False):
        a,b,c,d,e=st.columns(5)
        q=a.number_input('Q [L/min]',.1,value=80.0,step=5.0,key='stat_q');bore=b.number_input('Ø pistón [mm]',10.0,value=125.0,step=5.0,key='stat_bore');rod=c.number_input('Ø vástago [mm]',1.0,value=70.0,step=5.0,key='stat_rod');p=d.number_input('Presión [bar]',0.0,value=160.0,step=5.0,key='stat_p');load=e.number_input('Carga [kN]',0.0,value=120.0,step=10.0,key='stat_load')
        try:
            r=cylinder_performance(q,bore,rod,p,load);m1,m2,m3,m4=st.columns(4);m1.metric('v avance',f'{r.extension_speed_m_s*1000:.1f} mm/s');m2.metric('v retroceso',f'{r.retraction_speed_m_s*1000:.1f} mm/s');m3.metric('F avance',f'{r.extension_force_n/1000:.1f} kN');m4.metric('F retroceso',f'{r.retraction_force_n/1000:.1f} kN')
        except ValueError as exc: st.error(str(exc))

with TABS[2]:
    st.subheader('Camión minero · sistemas interconectados')
    st.markdown('La vista de levante incorpora los estados <b>Raise</b>, <b>Raise snub / overcenter</b>, <b>Hold</b>, <b>Float</b> y <b>Lower</b> para acercarse a la lógica de la animación de referencia, sin copiar un circuito OEM.',unsafe_allow_html=True)
    system_view('Camión minero','truck')

with TABS[3]:
    st.subheader('Cargador frontal · implementos y dirección articulada')
    st.markdown('El cargador conecta banco de implementos, cilindros de levante, cilindro de tilt y dirección articulada. La intención es leer la maniobra completa, no solo el carrete de la válvula.')
    system_view('Cargador frontal','loader')

with TABS[4]:
    st.subheader('Biblioteca técnica · símbolo, componente real y función')
    categories=list(dict.fromkeys(v['category'] for v in SYMBOL_LIBRARY.values()))
    cat=st.selectbox('Familia',categories,key='hyd2_lib_cat')
    names=[k for k,v in SYMBOL_LIBRARY.items() if v['category']==cat]
    name=st.selectbox('Componente',names,key='hyd2_lib_name')
    item=SYMBOL_LIBRARY[name]
    c1,c2=st.columns([.9,1.1])
    with c1: st.plotly_chart(symbol_figure(item['symbol'],name),use_container_width=True,key=f'hyd2_sym_{item["symbol"]}')
    with c2:
        st.markdown(f'## {name}');st.markdown(f'<span class="gg-badge">{item["category"]}</span>',unsafe_allow_html=True);st.write('**Función:**',item['function']);st.write('**Puertos:**',item['ports']);st.write('**Cómo reconocerlo:**',item['reading']);st.write('**Qué revisar en terreno:**',item['field'])
        st.markdown('**Anomalías frecuentes**')
        for x in item['failures']: st.write('• '+x)

with TABS[5]:
    st.subheader('Válvulas direccionales · leer una posición a la vez')
    valve=st.selectbox('Configuración',list(DIRECTIONAL_VALVES.keys()),index=4,key='hyd2_valve')
    desc=valve_descriptor(valve,DIRECTIONAL_VALVES)
    positions=['Izquierda','Derecha'] if desc['positions']==2 else ['Izquierda','Centro','Derecha']
    pos=st.radio('Posición a estudiar',positions,horizontal=True,index=1 if len(positions)==3 else 0,key='hyd2_valve_pos')
    act=st.selectbox('Accionamiento',['Solenoide + retorno por resorte','Palanca + retorno por resorte','Pilotaje hidráulico'],key='hyd2_act')
    c1,c2=st.columns([1.25,.75])
    with c1: st.plotly_chart(directional_valve_figure(valve,pos,act),use_container_width=True,key='hyd2_dir_fig')
    with c2:
        st.metric('Vías',desc['ports']);st.metric('Posiciones',desc['positions']);st.write('**Reposo:**',desc['rest']);key_map={'Izquierda':'left','Centro':'center','Derecha':'right'};st.write('**Estado:**',DIRECTIONAL_VALVES[valve].get(key_map[pos],'No aplica'));st.write('**Aplicación:**',DIRECTIONAL_VALVES[valve]['use'])
    st.markdown('### Circuito 4/3 de práctica')
    center=st.selectbox('Centro',['4/3 centro cerrado','4/3 centro tándem','4/3 centro flotante','4/3 centro abierto'],key='hyd2_center')
    state=st.radio('Estado',['Izquierda','Centro','Derecha'],horizontal=True,index=1,key='hyd2_state')
    c3,c4=st.columns([1.25,.75])
    with c3: st.plotly_chart(circuit_state_figure(center,state),use_container_width=True,key='hyd2_base_circuit')
    with c4: st.markdown('<div class="gg-orange"><b>Movimiento esperado</b><br>'+motion_from_4_3_center(center,state)+'</div>',unsafe_allow_html=True)

with TABS[6]:
    st.subheader('Diagnóstico inicial · síntoma no es causa')
    cases=diagnostic_cases();sym=st.selectbox('Condición observada',list(cases.keys()),key='hyd2_diag_case');case=cases[sym]
    st.markdown(f'<div class="gg-orange"><b>Interpretación inicial</b><br>{case["interpretation"]}</div>',unsafe_allow_html=True)
    st.markdown('### Qué verificar antes de cambiar componentes')
    cols=st.columns(3)
    for i,ch in enumerate(case['checks']):
        with cols[i%3]: st.markdown(f'<div class="gg-card"><b>{i+1:02d}</b><br>{ch}</div>',unsafe_allow_html=True)
    st.markdown('### Diagnósticos del módulo previo')
    symptom=st.selectbox('Síntoma adicional',list(DIAGNOSTICS.keys()),key='hyd2_diag_old')
    for i,step in enumerate(DIAGNOSTICS[symptom]): st.write(f'{i+1}. {step}')
    st.markdown('### Tres preguntas físicas')
    a,b,c=st.columns(3)
    with a: st.latex(r'Q=0\Rightarrow v=0');st.caption('¿Llega caudal?')
    with b: st.latex(r'v=Q/A');st.caption('¿El caudal disponible explica la velocidad?')
    with c: st.latex(r'p_{req}\approx F/A');st.caption('¿La presión vence la carga?')

with TABS[7]:
    st.subheader('Terreno y seguridad · observar, medir y verificar')
    st.markdown('''<div class="gg-dark"><b>Equipo detenido no significa equipo seguro.</b><br>La presión puede quedar atrapada en líneas, cilindros o acumuladores. Antes de intervenir: aislar, bloquear, descargar presión, asegurar mecánicamente la carga y verificar energía cero.</div>''',unsafe_allow_html=True)
    st.markdown('### Del plano al equipo')
    rows=[
        ['Depósito','tanque, respiradero, visor','nivel, espuma, temperatura, contaminación'],
        ['Bomba','bomba sobre motor/transmisión o central','ruido, vibración, caudal, succión, drenaje'],
        ['P','línea principal de presión','presión en carga, pulsación, temperatura'],
        ['T','retorno a tanque','contrapresión, temperatura, restricción'],
        ['A / B','mangueras hacia actuador','presión diferencial, sentido, fugas'],
        ['X / LS','pilotaje / load sensing','presión de mando y respuesta'],
        ['L / Y','drenaje de carcasa/pilotaje','contrapresión y fuga interna'],
        ['Acumulador','recipiente cargado con gas','presión almacenada y procedimiento de descarga'],
    ]
    st.dataframe(pd.DataFrame(rows,columns=['En el plano','En la máquina','Qué comprobar']),use_container_width=True,hide_index=True)
    st.markdown('### Secuencia de trabajo')
    steps=[('1','Asegurar','LOTO, carga apoyada, zona segura.'),('2','Observar','Fugas, ruido, vibración, temperatura, nivel.'),('3','Medir','Presión, caudal, temperatura en puntos definidos.'),('4','Interpretar','Comparar dato real con estado esperado del plano.'),('5','Intervenir','Solo con condición segura y evidencia suficiente.'),('6','Verificar','Probar reparación y registrar condición final.')]
    cols=st.columns(3)
    for i,(n,t,tx) in enumerate(steps):
        with cols[i%3]: st.markdown(f'<div class="gg-card"><b style="color:#f28e1c">{n} · {t}</b><br>{tx}</div>',unsafe_allow_html=True)

with st.expander('Alcance de los modelos'):
    st.write('Los circuitos de maquinaria móvil son redibujos didácticos originales basados en la lógica funcional visible en el video aportado y en el material de curso. No sustituyen esquemas OEM ni manuales de servicio. En especial, funciones como overcenter/snubbing, freno y prioridades/load-sensing pueden variar entre fabricantes y modelos.')
