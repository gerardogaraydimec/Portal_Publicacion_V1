from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.ui_brand import render_app_header
from modules.hydraulics_applied.hydraulic_engine import cylinder_performance
from modules.hydraulics_applied.symbol_catalog_v3 import SYMBOLS, PORTS, families, symbols_in_family
from modules.hydraulics_applied.symbol_studio import render_symbol, render_valve_builder
from modules.hydraulics_applied.system_cases import SYSTEM_CASES, system_state, course_comparison_rows, diagnostic_cases
from modules.hydraulics_applied.schematic_pro import render_hydraulic_schematic
from modules.hydraulics_applied.machine_reference import (
    reference_available,
    render_machine_reference,
)
from modules.hydraulics_applied.learning_cases import EXERCISES, LEARNING_PATH

st.markdown('''
<style>
:root{--gg-orange:#f28e1c;--gg-black:#202126;--gg-line:#e3e5e8;--gg-soft:#fff7ed;--gg-blue:#2a63b8;--gg-red:#d84030;--gg-yellow:#d6b72c;--gg-green:#4e9b57;--gg-drain:#e58b32}
.block-container{max-width:1760px;padding-top:1rem!important;padding-bottom:2rem}
.gg-note{border:1px solid #e4ded5;background:#faf8f4;border-radius:13px;padding:.9rem 1rem;line-height:1.52}
.gg-card{border:1px solid var(--gg-line);border-radius:13px;padding:.9rem 1rem;background:#fff;height:100%;line-height:1.48}
.gg-orange{border:1px solid #f1d0a7;border-left:5px solid var(--gg-orange);border-radius:13px;padding:.9rem 1rem;background:#fffaf4;height:100%;line-height:1.48}
.gg-dark{background:#202126;color:#f7f1e8;border-radius:14px;padding:1rem 1.15rem;border:1px solid #34363c;line-height:1.52}
.gg-badge{display:inline-block;background:#fff1df;color:#9d5914;border:1px solid #f2d0a5;padding:.18rem .52rem;border-radius:999px;font-size:.76rem;font-weight:750;margin:.08rem .14rem}
.gg-step{border-top:3px solid var(--gg-orange);background:#fff;border-radius:11px;border-left:1px solid #e5e6e8;border-right:1px solid #e5e6e8;border-bottom:1px solid #e5e6e8;padding:.8rem .9rem;height:100%}
.gg-step .n{color:var(--gg-orange);font-weight:850;font-size:1.05rem}.gg-step .t{font-weight:750;margin:.12rem 0 .25rem}.gg-step .d{font-size:.86rem;color:#62666d}
.gg-signal{display:flex;gap:.45rem;flex-wrap:wrap;margin:.35rem 0 .7rem}.gg-signal span{border:1px solid #ddd;border-radius:999px;padding:.25rem .55rem;background:#fff;font-size:.8rem}.gg-signal b{color:#f28e1c}
[data-testid="stMetric"]{border:1px solid #e5e6e8;border-radius:12px;padding:.35rem .55rem;background:#fff}
</style>
''',unsafe_allow_html=True)

render_app_header(
    title='Hidráulica aplicada · Lectura, máquina y diagnóstico',
    subtitle='Símbolo → función → circuito → estado → medición → diagnóstico',
    section='MÁQUINAS Y COMPONENTES · POTENCIA FLUIDA',
    logo_width=188,
)

st.markdown('''<div class="gg-note"><b>Enfoque V4.6:</b> la prioridad es la <b>lectura hidráulica real</b>: símbolo → puerto → posición → trayectoria → actuador → medición. En maquinaria móvil se conserva una referencia visual estática para ubicar componentes, pero se elimina el 3D interactivo porque no agrega suficiente valor pedagógico frente al plano funcional.</div>''',unsafe_allow_html=True)

study_mode=st.sidebar.radio('Modo de estudio',['Guiado','Intermedio','Técnico'],index=0,help='Guiado muestra nombres y ayudas. Técnico reduce ayudas para obligar a leer puertos y símbolos.')
st.sidebar.markdown('**Código funcional de líneas**')
st.sidebar.markdown('''🔴 presión/trabajo  \n🔵 retorno  \n🟢 succión  \n🟡 pilotaje/LS  \n🟠 drenaje''')
st.sidebar.caption('El naranja GG DIMEC identifica selección o componente activo; no sustituye el código funcional del fluido.')

TABS=st.tabs(['🧭 Ruta de aprendizaje','🔣 Símbolos y válvulas','🧪 Circuitos didácticos','🏭 Sistemas de planta','🚛 Camión minero','🚜 Cargador frontal','🔎 Diagnóstico','🧠 Ejercicios','🦺 Seguridad y terreno'])


def _port_signage():
    order=['P','T','A','B','X','Y','L']
    labels={'P':'presión/bomba','T':'retorno/tanque','A':'trabajo A','B':'trabajo B','X':'pilotaje externo','Y':'drenaje pilotaje','L':'drenaje carcasa'}
    st.markdown('<div class="gg-signal">'+''.join(f'<span><b>{p}</b> · {labels[p]}</span>' for p in order)+'</div>',unsafe_allow_html=True)


def _payload(machine,subsystem,state):
    data=system_state(machine,subsystem,state)
    return {**data,'machine':machine,'subsystem':subsystem,'state':state,'states':SYSTEM_CASES[machine][subsystem]['states'],'study_mode':study_mode}


def _reading_table(data):
    if data.get('readings'):
        st.dataframe(pd.DataFrame([{'Punto':k,'Esperado':v} for k,v in data['readings'].items()]),use_container_width=True,hide_index=True)
    else:
        st.caption('No hay lecturas definidas para este estado.')


def render_case(machine:str,subsystem:str,prefix:str,show_calc:bool=False,show_machine_reference:bool=False):
    meta=SYSTEM_CASES[machine][subsystem]
    state=st.radio('Estado / mando',meta['states'],horizontal=True,key=f'{prefix}_state')
    data=_payload(machine,subsystem,state)
    k1,k2,k3,k4=st.columns(4)
    with k1: st.markdown(f'<div class="gg-card"><b>Movimiento esperado</b><br>{data["motion"]}</div>',unsafe_allow_html=True)
    with k2: st.markdown('<div class="gg-card"><b>Cadena funcional</b><br>'+' → '.join(meta['components'])+'</div>',unsafe_allow_html=True)
    with k3: st.markdown('<div class="gg-card"><b>Qué medir</b><br>'+' · '.join(meta['field'])+'</div>',unsafe_allow_html=True)
    with k4: st.markdown('<div class="gg-orange"><b>Riesgo</b><br>'+' · '.join(meta['risks'])+'</div>',unsafe_allow_html=True)
    st.caption(meta['description'])
    _port_signage()

    st.markdown('### 1 · Plano funcional limpio')
    render_hydraulic_schematic(data,height=650)

    st.markdown('### 2 · Lectura funcional del estado')
    r1,r2,r3=st.columns(3)
    pressure_txt = ' → '.join(data.get('pressure',[])) if data.get('pressure') else 'Sin ruta de presión activa / depende del centro'
    return_txt = ' → '.join(data.get('return',[])) if data.get('return') else 'Sin retorno activo definido en este estado'
    pilot_txt = ' → '.join(data.get('pilot',[])) if data.get('pilot') else 'Sin pilotaje activo'
    with r1:
        st.markdown(f'<div class="gg-card"><b>Qué debería ocurrir</b><br>{data["motion"]}<br><br><b>Secuencia de lectura</b><br>Fuente → mando → puerto de trabajo → actuador → retorno.</div>',unsafe_allow_html=True)
    with r2:
        st.markdown('<div class="gg-card"><b>Qué observar en el plano</b><br>'+meta['learning']+'<br><br><b>Componentes de la función</b><br>'+' → '.join(meta['components'])+'</div>',unsafe_allow_html=True)
    with r3:
        st.markdown('<div class="gg-orange"><b>Qué medir para comprobar</b><br>'+' · '.join(meta['field'])+'<br><br><b>Riesgos</b><br>'+' · '.join(meta['risks'])+'</div>',unsafe_allow_html=True)

    with st.expander('Ver rutas internas activadas en este estado'):
        st.caption('Estas etiquetas corresponden a los tramos internos del modelo didáctico y sirven para comprobar que el estado seleccionado cambia realmente el circuito.')
        st.write('**Presión:**', pressure_txt)
        st.write('**Retorno:**', return_txt)
        st.write('**Pilotaje / LS:**', pilot_txt)

    st.markdown('**Lecturas esperadas en los puntos del plano**')
    _reading_table(data)

    st.markdown('#### Compare los estados antes de memorizar el circuito')
    state_rows=[]
    for s_name in meta['states']:
        s_data=_payload(machine,subsystem,s_name)
        state_rows.append({
            'Estado':s_name,
            'Movimiento / condición':s_data.get('motion','—'),
            'Lecturas clave':' · '.join(f'{k}: {v}' for k,v in s_data.get('readings',{}).items()) or '—',
        })
    st.dataframe(pd.DataFrame(state_rows),use_container_width=True,hide_index=True)

    if show_machine_reference and reference_available(machine, subsystem):
        st.markdown('### 3 · Referencia visual del equipo')
        st.caption('Esta imagen solo ayuda a ubicar físicamente los componentes. La lógica hidráulica se estudia en el plano funcional superior.')
        render_machine_reference(machine, subsystem, state)
        next_section=4
    else:
        next_section=3

    if show_calc:
        st.markdown(f'### {next_section} · Parámetros físicos y comprobación')
        a,b,c,d,e=st.columns(5)
        q=a.number_input('Q [L/min]',.1,value=80.0,step=5.0,key=f'{prefix}_q')
        bore=b.number_input('Ø pistón [mm]',10.0,value=125.0,step=5.0,key=f'{prefix}_bore')
        rod=c.number_input('Ø vástago [mm]',1.0,value=70.0,step=5.0,key=f'{prefix}_rod')
        p=d.number_input('Presión [bar]',0.0,value=160.0,step=5.0,key=f'{prefix}_p')
        load=e.number_input('Carga [kN]',0.0,value=120.0,step=10.0,key=f'{prefix}_load')
        try:
            r=cylinder_performance(q,bore,rod,p,load)
            m1,m2,m3,m4=st.columns(4)
            m1.metric('v avance',f'{r.extension_speed_m_s*1000:.1f} mm/s')
            m2.metric('v retroceso',f'{r.retraction_speed_m_s*1000:.1f} mm/s')
            m3.metric('F avance',f'{r.extension_force_n/1000:.1f} kN')
            m4.metric('F retroceso',f'{r.retraction_force_n/1000:.1f} kN')
            st.caption('Estos valores cambian con Q, diámetros y presión. No existe ya una amplificación 3D asociada a esta página.')
        except ValueError as exc:
            st.error(str(exc))


with TABS[0]:
    st.subheader('Una progresión para aprender a leer hidráulica de verdad')
    cols=st.columns(6)
    for col,(n,t,d) in zip(cols,LEARNING_PATH):
        with col: st.markdown(f'<div class="gg-step"><div class="n">{n}</div><div class="t">{t}</div><div class="d">{d}</div></div>',unsafe_allow_html=True)
    st.markdown('### Cuatro principios que gobiernan la lectura inicial')
    c1,c2,c3,c4=st.columns(4)
    with c1: st.latex(r'Q\Rightarrow movimiento');st.caption('Sin caudal no hay desplazamiento del actuador.')
    with c2: st.latex(r'v=Q/A');st.caption('El caudal efectivo determina velocidad para un área dada.')
    with c3: st.latex(r'F=pA');st.caption('La presión necesaria aumenta con la carga resistente.')
    with c4: st.latex(r'P_{loss}\approx\Delta p\,Q');st.caption('Caída de presión con caudal sin trabajo útil se transforma en calor.')
    st.markdown('### Planta y equipo móvil')
    st.dataframe(pd.DataFrame(course_comparison_rows(),columns=['Aspecto','Sistema estacionario','Equipo móvil']),use_container_width=True,hide_index=True)
    st.markdown('### Señalética de puertos')
    _port_signage()
    pcols=st.columns(7)
    for col,(p,desc) in zip(pcols,PORTS.items()):
        with col: st.markdown(f'<div class="gg-card"><b style="font-size:1.15rem;color:#f28e1c">{p}</b><br><span style="font-size:.83rem">{desc}</span></div>',unsafe_allow_html=True)

with TABS[1]:
    s1,s2=st.tabs(['Biblioteca de símbolos','Constructor de válvulas'])
    with s1:
        st.subheader(f'Biblioteca técnica · {len(SYMBOLS)} símbolos/elementos')
        family=st.selectbox('Familia',families(),key='sym_family')
        candidates=symbols_in_family(family); labels=[name for _,name in candidates]
        chosen_name=st.selectbox('Símbolo',labels,key='sym_name'); key=next(k for k,n in candidates if n==chosen_name);meta=SYMBOLS[key]
        left,right=st.columns([1.08,.92],gap='large')
        with left: render_symbol(key,height=365)
        with right:
            st.markdown(f'### {meta["name"]}')
            st.markdown(f'<span class="gg-badge">{meta["family"]}</span><span class="gg-badge">{meta["level"]}</span>',unsafe_allow_html=True)
            st.write('**Función:**',meta['function']);st.write('**Cómo leerlo:**',meta['how']);st.write('**Condición de referencia:**',meta['rest'])
        a,b,c=st.columns(3)
        with a: st.markdown(f'<div class="gg-card"><b>Puertos / conexión</b><br>{meta["ports"]}</div>',unsafe_allow_html=True)
        with b: st.markdown(f'<div class="gg-card"><b>Qué comprobar</b><br>{meta["field"]}</div>',unsafe_allow_html=True)
        with c: st.markdown(f'<div class="gg-orange"><b>Falla o error de lectura</b><br>{meta["failure"]}</div>',unsafe_allow_html=True)
    with s2:
        st.subheader('Construya la válvula antes de intentar memorizarla')
        a,b,c,d=st.columns(4)
        ways=a.selectbox('Vías / puertos',[2,3,4],index=2,key='vb_ways')
        valid_positions=[2,3] if ways==4 else [2]
        positions=b.selectbox('Posiciones',valid_positions,index=(1 if ways==4 else 0),key='vb_pos')
        if positions==3 and ways==4:
            center=c.selectbox('Centro',['Cerrado','Abierto','Tándem','Flotante'],key='vb_center')
            act_options=['Palanca + centrado por resortes','Doble solenoide + centrado por resortes','Doble pilotaje hidráulico + centrado por resortes','Solenoide pilotado + centrado por resortes']
        else:
            center='—'
            c.text_input('Centro',value='No aplica',disabled=True,key='vb_center_off')
            act_options=['Manual + resorte','Solenoide + resorte','Pilotaje hidráulico + resorte','Doble solenoide con detent']
        act=d.selectbox('Accionamiento',act_options,key='vb_act')
        render_valve_builder(ways,positions,center,act,height=445)
        st.markdown('''<div class="gg-orange"><b>Método de lectura:</b> 1) casillas = posiciones; 2) líneas externas = vías/puertos; 3) identifique reposo por resorte/accionamiento; 4) siga flechas y bloqueos; 5) prediga P, T, A y B; 6) recién entonces prediga movimiento.</div>''',unsafe_allow_html=True)

with TABS[2]:
    st.subheader('Circuitos didácticos · plano → estado → lectura → medición')
    st.caption('El valor pedagógico está en leer correctamente el plano, entender la posición de la válvula y predecir el comportamiento.')
    subsystem=st.selectbox('Circuito',list(SYSTEM_CASES['Sistema estacionario'].keys()),key='did_sub')
    render_case('Sistema estacionario',subsystem,'did',show_calc=subsystem in ('Cilindro 4/3 básico','Carga vertical + contrabalance','Avance regenerativo'),show_machine_reference=False)

with TABS[3]:
    st.subheader('Sistemas de planta · potencia, secuencia y carga')
    st.caption('Aquí priorizamos plano funcional, secuencia y comprobación física. No se utiliza 3D interactivo en esta página.')
    subsystem=st.selectbox('Sistema',list(SYSTEM_CASES['Sistema estacionario'].keys()),key='plant_sub')
    render_case('Sistema estacionario',subsystem,'plant',show_calc=True,show_machine_reference=False)

with TABS[4]:
    st.subheader('Camión minero · circuito funcional + máquina')
    subsystem=st.selectbox('Sistema',list(SYSTEM_CASES['Camión minero'].keys()),key='truck_sub')
    render_case('Camión minero',subsystem,'truck',show_machine_reference=True)

with TABS[5]:
    st.subheader('Cargador frontal · implementos, LS y articulación')
    subsystem=st.selectbox('Sistema',list(SYSTEM_CASES['Cargador frontal'].keys()),key='loader_sub')
    render_case('Cargador frontal',subsystem,'loader',show_machine_reference=True)

with TABS[6]:
    st.subheader('Diagnóstico guiado · primero prediga, después mida')
    cases=diagnostic_cases();symptom=st.selectbox('Síntoma observado',list(cases.keys()),key='diag_case');case=cases[symptom]
    machine,subsystem,state=case['visual'];data=_payload(machine,subsystem,state)
    left,right=st.columns([1.45,.55],gap='large')
    with left:
        st.markdown('#### Esquema de referencia para razonar')
        render_hydraulic_schematic({**data,'study_mode':'Guiado'},height=590)
    with right:
        st.markdown(f'<div class="gg-orange"><b>Principio físico</b><br>{case["physics"]}</div>',unsafe_allow_html=True)
        st.markdown('#### Qué comprobar primero')
        for i,step in enumerate(case['first'],1): st.markdown(f'**{i}.** {step}')
        st.markdown(f'<div class="gg-dark"><b>Qué medir</b><br>{case["measurement"]}</div>',unsafe_allow_html=True)
    st.markdown('### Evidencia que cambia la hipótesis')
    ecols=st.columns(len(case['evidence']))
    for i,(col,e) in enumerate(zip(ecols,case['evidence']),1):
        with col: st.markdown(f'<div class="gg-step"><div class="n">{i}</div><div class="t">Evidencia</div><div class="d">{e}</div></div>',unsafe_allow_html=True)
    st.warning('Error a evitar: '+case['avoid'])

with TABS[7]:
    st.subheader('Ejercicios de lectura y resolución · con esquema')
    level=st.radio('Nivel',['Todos','Básico','Intermedio','Avanzado'],horizontal=True,index=0,key='ex_level')
    pool=[x for x in EXERCISES if level=='Todos' or x['level']==level];ex_title=st.selectbox('Caso',[x['title'] for x in pool],key='ex_case');ex=next(x for x in pool if x['title']==ex_title)
    machine,subsystem,state=ex['visual'];data=_payload(machine,subsystem,state)
    l,r=st.columns([1.25,.75],gap='large')
    with l:
        st.markdown(f'**Apoyo visual · foco:** {ex["focus"]}')
        render_hydraulic_schematic({**data,'study_mode':'Guiado'},height=570)
    with r:
        st.markdown(f'<span class="gg-badge">{ex["level"]}</span>',unsafe_allow_html=True)
        st.markdown(f'<div class="gg-card"><b>Caso</b><br>{ex["case"]}</div>',unsafe_allow_html=True)
        choice=st.radio(ex['question'],ex['options'],key=f'ex_answer_{ex["id"]}')
        if st.button('Comprobar razonamiento',key=f'ex_check_{ex["id"]}',use_container_width=True):
            if choice==ex['answer']:st.success('La selección es coherente con la evidencia del caso.')
            else:st.warning('Esa opción no es la que mejor discrimina la causa en este caso.')
            st.markdown(f'<div class="gg-orange"><b>Explicación</b><br>{ex["explanation"]}</div>',unsafe_allow_html=True)
            st.info('En terreno: '+ex['field'])

with TABS[8]:
    st.subheader('Seguridad y traducción a terreno')
    st.markdown('''<div class="gg-dark"><b>Equipo detenido no significa energía cero.</b><br>La presión puede permanecer atrapada en cámaras, mangueras, manifolds y acumuladores; además una carga elevada conserva energía potencial. La intervención real debe seguir el procedimiento de aislamiento y descarga aplicable al equipo.</div>''',unsafe_allow_html=True)
    st.markdown('### Método antes de tocar una conexión')
    items=[('1','Identifique la función','Qué maniobra debería ejecutar y qué carga existe.'),('2','Lea el plano','Fuente, control, protección, actuador, retorno, pilotaje y drenajes.'),('3','Ubique físicamente','Encuentre componentes y mangueras reales sin asumir que la disposición coincide con el plano.'),('4','Prediga','Qué presión, caudal y movimiento espera en el estado seleccionado.'),('5','Mida','Use puntos de prueba e instrumentos apropiados antes de desmontar.'),('6','Aísle y verifique','Bloquee, descargue, soporte la carga y confirme ausencia de energía antes de intervenir.')]
    cols=st.columns(3)
    for i,item in enumerate(items):
        with cols[i%3]: st.markdown(f'<div class="gg-step"><div class="n">{item[0]}</div><div class="t">{item[1]}</div><div class="d">{item[2]}</div></div>',unsafe_allow_html=True)
    rows=[['P','Línea de alimentación','Presión disponible y caída hasta la carga'],['T','Retorno','Contrapresión y temperatura'],['A/B','Líneas de trabajo','Presión diferencial y sentido de movimiento'],['X/LS','Señal de pilotaje / carga','Presión de mando, margen y respuesta'],['Y/L','Drenaje','Contrapresión y fuga interna'],['M','Punto de medición','Dato que permite aceptar o descartar una hipótesis']]
    st.dataframe(pd.DataFrame(rows,columns=['Plano','En el equipo','Qué verificar']),use_container_width=True,hide_index=True)

with st.expander('Base técnica y alcance de esta versión'):
    st.write('La biblioteca, los circuitos y los ejercicios se construyen con los materiales aportados sobre lectura de símbolos, fundamentos hidráulicos, diseño de circuitos, mantenimiento y troubleshooting. La progresión es: reconocer → leer → seguir flujo → relacionar con el equipo → medir → diagnosticar.')
    st.write('Los circuitos móviles son funcionales y genéricos. Para una máquina real debe utilizarse el esquema hidráulico y el manual de servicio del fabricante correspondiente a su configuración.')
