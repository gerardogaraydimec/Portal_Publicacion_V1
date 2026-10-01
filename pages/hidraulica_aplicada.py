from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.ui_brand import render_app_header
from modules.hydraulics_applied.hydraulic_engine import cylinder_performance
from modules.hydraulics_applied.symbol_catalog_v3 import SYMBOLS, PORTS, families, symbols_in_family
from modules.hydraulics_applied.symbol_studio import render_symbol, render_valve_builder
from modules.hydraulics_applied.system_cases import SYSTEM_CASES, system_state, course_comparison_rows, diagnostic_cases
from modules.hydraulics_applied.schematic_pro import render_hydraulic_schematic
from modules.hydraulics_applied.machine_visual3d import render_machine_hydraulics_3d
from modules.hydraulics_applied.learning_cases import EXERCISES, LEARNING_PATH

st.markdown('''
<style>
:root{--gg-orange:#f28e1c;--gg-black:#202126;--gg-line:#e3e5e8;--gg-soft:#fff7ed;--gg-blue:#2a63b8;--gg-red:#d84030;--gg-yellow:#d6b72c;--gg-green:#4e9b57}
.block-container{max-width:1740px;padding-top:1rem!important;padding-bottom:2rem}
.gg-note{border:1px solid #e4ded5;background:#faf8f4;border-radius:13px;padding:.9rem 1rem;line-height:1.52}
.gg-card{border:1px solid var(--gg-line);border-radius:13px;padding:.9rem 1rem;background:#fff;height:100%;line-height:1.48}
.gg-orange{border:1px solid #f1d0a7;border-left:5px solid var(--gg-orange);border-radius:13px;padding:.9rem 1rem;background:#fffaf4;height:100%;line-height:1.48}
.gg-dark{background:#202126;color:#f7f1e8;border-radius:14px;padding:1rem 1.15rem;border:1px solid #34363c;line-height:1.52}
.gg-badge{display:inline-block;background:#fff1df;color:#9d5914;border:1px solid #f2d0a5;padding:.18rem .52rem;border-radius:999px;font-size:.76rem;font-weight:750;margin:.08rem .14rem}
.gg-step{border-top:3px solid var(--gg-orange);background:#fff;border-radius:11px;border-left:1px solid #e5e6e8;border-right:1px solid #e5e6e8;border-bottom:1px solid #e5e6e8;padding:.8rem .9rem;height:100%}
.gg-step .n{color:var(--gg-orange);font-weight:850;font-size:1.05rem}.gg-step .t{font-weight:750;margin:.12rem 0 .25rem}.gg-step .d{font-size:.86rem;color:#62666d}
[data-testid="stMetric"]{border:1px solid #e5e6e8;border-radius:12px;padding:.35rem .55rem;background:#fff}
</style>
''',unsafe_allow_html=True)

render_app_header(
    title='Hidráulica aplicada · Lectura, máquina y diagnóstico',
    subtitle='Símbolo → función → circuito → estado → máquina → medición → diagnóstico',
    section='MÁQUINAS Y COMPONENTES · POTENCIA FLUIDA',
    logo_width=188,
)

st.markdown('''<div class="gg-note"><b>Enfoque del laboratorio:</b> el objetivo ya no es mirar dibujos separados. Cada actividad conecta el <b>símbolo normalizado</b>, la <b>función del componente</b>, el <b>recorrido del aceite</b>, el <b>movimiento físico</b> y la <b>evidencia que debería medirse en terreno</b>. Los esquemas de maquinaria son reconstrucciones didácticas funcionales y no reemplazan el plano OEM del equipo específico.</div>''',unsafe_allow_html=True)

study_mode=st.sidebar.radio('Modo de estudio',['Guiado','Intermedio','Técnico'],index=0,help='Guiado muestra más nombres y ayudas. Técnico reduce ayudas y obliga a leer el plano por símbolos y puertos.')
st.sidebar.caption('La codificación de flujo usa colores funcionales; el naranja queda para destacar selección y marca GG DIMEC.')

TABS=st.tabs(['🧭 Ruta de aprendizaje','🔣 Símbolos y válvulas','🧪 Circuitos didácticos','🏭 Sistemas de planta','🚛 Camión minero','🚜 Cargador frontal','🔎 Diagnóstico','🧠 Ejercicios','🦺 Seguridad y terreno'])

with TABS[0]:
    st.subheader('Una progresión para aprender a leer hidráulica de verdad')
    cols=st.columns(6)
    for col,(n,t,d) in zip(cols,LEARNING_PATH):
        with col: st.markdown(f'<div class="gg-step"><div class="n">{n}</div><div class="t">{t}</div><div class="d">{d}</div></div>',unsafe_allow_html=True)
    st.markdown('### Cuatro principios que gobiernan casi toda la lectura inicial')
    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.latex(r'Q\Rightarrow movimiento')
        st.caption('Sin caudal no hay desplazamiento del actuador.')
    with c2:
        st.latex(r'v=Q/A')
        st.caption('El caudal disponible determina velocidad para un área dada.')
    with c3:
        st.latex(r'F=pA')
        st.caption('La presión necesaria crece con la carga resistente.')
    with c4:
        st.latex(r'P_h=\Delta p\,Q')
        st.caption('Una caída de presión con caudal sin trabajo útil termina como calor.')
    st.markdown('### Planta y equipo móvil: misma física, distinta lectura de terreno')
    st.dataframe(pd.DataFrame(course_comparison_rows(),columns=['Aspecto','Sistema estacionario','Equipo móvil']),use_container_width=True,hide_index=True)
    st.markdown('### Puertos que deben volverse familiares')
    pcols=st.columns(7)
    for col,(p,desc) in zip(pcols,PORTS.items()):
        with col: st.markdown(f'<div class="gg-card"><b style="font-size:1.15rem;color:#f28e1c">{p}</b><br><span style="font-size:.83rem">{desc}</span></div>',unsafe_allow_html=True)

with TABS[1]:
    s1,s2=st.tabs(['Biblioteca de símbolos','Constructor de válvulas'])
    with s1:
        st.subheader('Biblioteca técnica ampliada')
        family=st.selectbox('Familia',families(),key='sym_family')
        candidates=symbols_in_family(family)
        labels=[name for _,name in candidates]
        chosen_name=st.selectbox('Símbolo',labels,key='sym_name')
        key=next(k for k,n in candidates if n==chosen_name)
        meta=SYMBOLS[key]
        left,right=st.columns([1.08,.92],gap='large')
        with left: render_symbol(key,height=365)
        with right:
            st.markdown(f'### {meta["name"]}')
            st.markdown(f'<span class="gg-badge">{meta["family"]}</span><span class="gg-badge">{meta["level"]}</span>',unsafe_allow_html=True)
            st.write('**Función:**',meta['function'])
            st.write('**Cómo leerlo:**',meta['how'])
            st.write('**Condición de referencia:**',meta['rest'])
        a,b,c=st.columns(3)
        with a: st.markdown(f'<div class="gg-card"><b>Puertos / conexión</b><br>{meta["ports"]}</div>',unsafe_allow_html=True)
        with b: st.markdown(f'<div class="gg-card"><b>Qué comprobar</b><br>{meta["field"]}</div>',unsafe_allow_html=True)
        with c: st.markdown(f'<div class="gg-orange"><b>Falla o error de lectura</b><br>{meta["failure"]}</div>',unsafe_allow_html=True)
        st.caption('Los dibujos de esta biblioteca son redibujos originales para MechLab; se usan convenciones funcionales de simbología de potencia fluida.')
    with s2:
        st.subheader('Construya la válvula antes de intentar memorizarla')
        a,b,c,d=st.columns(4)
        ways=a.selectbox('Vías / puertos',[2,3,4],index=2,key='vb_ways')
        positions=b.selectbox('Posiciones',[2,3],index=1,key='vb_pos')
        if positions==3 and ways==4:
            center=c.selectbox('Centro',['Cerrado','Abierto','Tándem','Flotante'],key='vb_center')
        else:
            center='—';c.text_input('Centro',value='No aplica',disabled=True,key='vb_center_off')
        act=d.selectbox('Accionamiento',['Manual + resorte','Solenoide + resorte','Doble solenoide','Pilotaje hidráulico'],key='vb_act')
        render_valve_builder(ways,positions,center,act,height=405)
        st.markdown('''<div class="gg-orange"><b>Método de lectura:</b> 1) cuente las casillas = posiciones; 2) cuente los puertos = vías; 3) determine qué casilla es reposo por resortes/accionamientos; 4) siga flechas y bloqueos dentro de esa casilla; 5) recién entonces prediga el movimiento del actuador.</div>''',unsafe_allow_html=True)


def _payload(machine,subsystem,state,prefix):
    data=system_state(machine,subsystem,state)
    return {**data,'machine':machine,'subsystem':subsystem,'state':state,'states':SYSTEM_CASES[machine][subsystem]['states'],'study_mode':study_mode}


def render_case(machine:str,subsystem:str,prefix:str,show_calc:bool=False):
    meta=SYSTEM_CASES[machine][subsystem]
    state=st.radio('Estado / mando',meta['states'],horizontal=True,key=f'{prefix}_state')
    data=_payload(machine,subsystem,state,prefix)
    k1,k2,k3,k4=st.columns(4)
    with k1: st.markdown(f'<div class="gg-card"><b>Movimiento</b><br>{data["motion"]}</div>',unsafe_allow_html=True)
    with k2: st.markdown('<div class="gg-card"><b>Componentes</b><br>'+' · '.join(meta['components'])+'</div>',unsafe_allow_html=True)
    with k3: st.markdown('<div class="gg-card"><b>Qué medir</b><br>'+' · '.join(meta['field'])+'</div>',unsafe_allow_html=True)
    with k4: st.markdown('<div class="gg-orange"><b>Riesgo</b><br>'+' · '.join(meta['risks'])+'</div>',unsafe_allow_html=True)
    st.caption(meta['description'])
    st.markdown('### 1 · Plano funcional')
    render_hydraulic_schematic(data,height=742)
    st.markdown('### 2 · Modelo físico 3D')
    controls_col,scene_col=st.columns([.22,.78],gap='medium')
    with controls_col:
        amp=st.slider('Amplificación visual',.5,2.2,1.0,.1,key=f'{prefix}_amp')
        speed=st.slider('Velocidad animación',.25,2.0,1.0,.25,key=f'{prefix}_speed')
        st.markdown(f'<div class="gg-dark"><b>Qué observar</b><br>{meta["learning"]}</div>',unsafe_allow_html=True)
        st.markdown('**Lecturas esperadas**')
        if data['readings']:
            st.dataframe(pd.DataFrame([{'Punto':k,'Esperado':v} for k,v in data['readings'].items()]),use_container_width=True,hide_index=True)
    with scene_col:
        render_machine_hydraulics_3d({**data,'visual_amp':amp,'speed':speed},height=640)
    if show_calc:
        with st.expander('Relacionar el circuito con fuerza y velocidad',expanded=False):
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
            except ValueError as exc: st.error(str(exc))

with TABS[2]:
    st.subheader('Circuitos didácticos · pasar del símbolo a la función')
    choices=list(SYSTEM_CASES['Sistema estacionario'].keys())
    subsystem=st.selectbox('Circuito',choices,key='did_sub')
    render_case('Sistema estacionario',subsystem,'did',show_calc=subsystem in ('Cilindro 4/3 básico','Carga vertical + contrabalance','Avance regenerativo'))

with TABS[3]:
    st.subheader('Sistemas de planta · potencia, secuencia y carga')
    subsystem=st.selectbox('Sistema',list(SYSTEM_CASES['Sistema estacionario'].keys()),key='plant_sub')
    render_case('Sistema estacionario',subsystem,'plant',show_calc=True)

with TABS[4]:
    st.subheader('Camión minero · plano funcional + ubicación física')
    subsystem=st.selectbox('Sistema',list(SYSTEM_CASES['Camión minero'].keys()),key='truck_sub')
    render_case('Camión minero',subsystem,'truck')

with TABS[5]:
    st.subheader('Cargador frontal · implementos, LS y articulación')
    subsystem=st.selectbox('Sistema',list(SYSTEM_CASES['Cargador frontal'].keys()),key='loader_sub')
    render_case('Cargador frontal',subsystem,'loader')

with TABS[6]:
    st.subheader('Diagnóstico guiado · síntoma ≠ causa')
    cases=diagnostic_cases();symptom=st.selectbox('Síntoma observado',list(cases.keys()),key='diag_case');case=cases[symptom]
    st.markdown(f'<div class="gg-orange"><b>Principio físico</b><br>{case["physics"]}</div>',unsafe_allow_html=True)
    st.markdown('### Proceso de descarte')
    cols=st.columns(len(case['first']))
    for i,(col,step) in enumerate(zip(cols,case['first']),1):
        with col: st.markdown(f'<div class="gg-step"><div class="n">{i}</div><div class="t">Comprobar</div><div class="d">{step}</div></div>',unsafe_allow_html=True)
    st.markdown('### Qué evidencia cambia la hipótesis')
    ev1,ev2=st.columns([1.2,.8])
    with ev1:
        for e in case['evidence']: st.markdown(f'- {e}')
    with ev2: st.markdown(f'<div class="gg-dark"><b>Error a evitar</b><br>{case["avoid"]}</div>',unsafe_allow_html=True)
    st.markdown('### Plantilla de diagnóstico técnico')
    st.dataframe(pd.DataFrame([
        ['1','Síntoma','Describir lo observado sin inferir causa.'],
        ['2','Estado del circuito','Identificar posición de válvulas y carga.'],
        ['3','Predicción','Definir qué P, Q y movimiento deberían existir.'],
        ['4','Medición','Elegir el punto que discrimina entre hipótesis.'],
        ['5','Aislamiento','Separar fuente, control, actuador y carga.'],
        ['6','Conclusión','Solo concluir cuando la evidencia contradiga/soporte una causa.'],
    ],columns=['Paso','Acción','Criterio']),use_container_width=True,hide_index=True)

with TABS[7]:
    st.subheader('Ejercicios de lectura y resolución')
    level=st.radio('Nivel',['Todos','Básico','Intermedio','Avanzado'],horizontal=True,index=0,key='ex_level')
    pool=[x for x in EXERCISES if level=='Todos' or x['level']==level]
    ex_title=st.selectbox('Caso',[x['title'] for x in pool],key='ex_case')
    ex=next(x for x in pool if x['title']==ex_title)
    st.markdown(f'<span class="gg-badge">{ex["level"]}</span>',unsafe_allow_html=True)
    st.markdown(f'<div class="gg-card"><b>Caso</b><br>{ex["case"]}</div>',unsafe_allow_html=True)
    choice=st.radio(ex['question'],ex['options'],key=f'ex_answer_{ex["id"]}')
    if st.button('Comprobar razonamiento',key=f'ex_check_{ex["id"]}'):
        if choice==ex['answer']:
            st.success('La selección es coherente con la evidencia del caso.')
        else:
            st.warning('Esa opción no es la que mejor discrimina la causa en este caso.')
        st.markdown(f'<div class="gg-orange"><b>Explicación</b><br>{ex["explanation"]}</div>',unsafe_allow_html=True)
        st.info('En terreno: '+ex['field'])

with TABS[8]:
    st.subheader('Seguridad y traducción a terreno')
    st.markdown('''<div class="gg-dark"><b>Equipo detenido no significa energía cero.</b><br>La presión puede permanecer atrapada en cámaras, mangueras, manifolds y acumuladores; además una carga elevada conserva energía potencial. La intervención real debe seguir el procedimiento de aislamiento y descarga aplicable al equipo.</div>''',unsafe_allow_html=True)
    st.markdown('### Método de trabajo antes de tocar una conexión')
    items=[
        ('1','Identifique la función','Qué maniobra debería ejecutar y qué carga existe.'),
        ('2','Lea el plano','Ubique fuente, control, protección, actuador, retorno, pilotaje y drenajes.'),
        ('3','Ubique físicamente','Encuentre componentes y mangueras reales sin asumir que la disposición coincide con el plano.'),
        ('4','Prediga','Qué presión, caudal y movimiento espera en el estado seleccionado.'),
        ('5','Mida','Use puntos de prueba e instrumentos apropiados antes de desmontar.'),
        ('6','Aísle y verifique','Bloquee, descargue, soporte la carga y confirme ausencia de energía antes de intervenir.'),
    ]
    cols=st.columns(3)
    for i,item in enumerate(items):
        with cols[i%3]: st.markdown(f'<div class="gg-step"><div class="n">{item[0]}</div><div class="t">{item[1]}</div><div class="d">{item[2]}</div></div>',unsafe_allow_html=True)
    st.markdown('### Del plano a la máquina')
    rows=[
        ['P','Línea de alimentación','Presión disponible y caída hasta la carga'],['T','Retorno','Contrapresión y temperatura'],['A/B','Líneas de trabajo','Presión diferencial y sentido de movimiento'],['X/LS','Señal de pilotaje / carga','Presión de mando, margen y respuesta'],['Y/L','Drenaje','Contrapresión y fuga interna'],['M','Punto de medición','Dato que permite aceptar o descartar una hipótesis']]
    st.dataframe(pd.DataFrame(rows,columns=['Plano','En el equipo','Qué verificar']),use_container_width=True,hide_index=True)

with st.expander('Base técnica utilizada para esta versión'):
    st.write('La biblioteca y los ejercicios se construyeron a partir de los materiales aportados sobre lectura de simbología, hidráulica industrial, diseño de circuitos, troubleshooting y mantenimiento. Se privilegió una progresión de técnico: reconocer → leer → seguir flujo → relacionar con máquina → medir → diagnosticar.')
    st.write('Los esquemas de maquinaria móvil son funcionales y genéricos. Para un equipo real, la validación final debe hacerse contra el esquema hidráulico y manual de servicio del fabricante y la configuración específica de la máquina.')
