from __future__ import annotations
from pathlib import Path
import math
import pandas as pd
import streamlit as st

from modules.thermo_cycles.catalog import CYCLE_FAMILIES, STRUCTURAL_CYCLES
from modules.thermo_cycles import gas, steam, refrigeration
from modules.thermo_cycles.core import rates_from_specific
from modules.thermo_cycles.schematics import schematic
from modules.thermo_cycles.plots import gas_pv_ts, fluid_ts, refrigerant_ph
from modules.thermo_cycles.pedagogy import COMMON_EQUATIONS, SOLVER_EQUATIONS
from modules.thermo_cycles.structural import render_structural_inputs, inputs_table, extractions_table, derived_metrics, structural_warnings
from modules.thermo_cycles.ui_math import latex_number_input, render_processes, render_structural_parameters, render_specific_configuration

ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/"assets"
LOGO=ASSETS/"logo_card.png"; ICON=ASSETS/"icon_web.png"

st.markdown("""
<style>
.block-container{padding-top:1rem;padding-bottom:2rem;max-width:1700px;}
.brand-kicker{color:#db7810;font-weight:800;letter-spacing:.06em;font-size:.88rem;text-transform:uppercase;}
.cycle-head{border-left:5px solid #f28e1c;background:#fff8ef;border-radius:8px;padding:10px 14px;margin:.4rem 0 .8rem 0;}
.small-muted{font-size:.86rem;color:#6b7280;}
.note-box{background:#eef4ff;border-left:4px solid #6d8bd8;padding:8px 12px;border-radius:8px;}
</style>
""",unsafe_allow_html=True)


def fmt(v):
    if v is None:return "—"
    try:v=float(v)
    except:return str(v)
    if not math.isfinite(v):return "—"
    a=abs(v)
    if a>=1e5 or (a>0 and a<1e-4):return f"{v:.3e}"
    if a>=1000:return f"{v:,.1f}".replace(","," ")
    return f"{v:.5g}"


def latex_metrics(metrics):
    if not metrics:
        st.info("No hay indicadores numéricos definidos para esta configuración.")
        return
    cols=st.columns(min(4,len(metrics)))
    for i,m in enumerate(metrics):
        with cols[i%len(cols)]:
            with st.container(border=True):
                st.latex(m["symbol"])
                st.markdown(
                    f"<div style='font-size:1.25rem;font-weight:800;text-align:center'>{fmt(m['value'])} {m.get('unit','')}</div>",
                    unsafe_allow_html=True
                )
                st.caption(m.get("description",""))


def family_type(family):
    return "refrigeration" if "refrigeración" in family.lower() else "power"


def ni(where, label, value, **kwargs):
    return latex_number_input(where, label, value, **kwargs)


def solver_ui(name):
    if name=="gas_carnot":
        a,b,c,d=st.columns(4)
        return gas.carnot(ni(a,"T_H [K]",900.0),ni(b,"T_L [K]",300.0),ni(c,"P_1 [kPa]",1000.0),ni(d,"v_2/v_1",2.0,min_value=1.001))
    if name=="otto":
        a,b,c,d=st.columns(4)
        return gas.otto(ni(a,"T_1 [K]",300.0),ni(b,"P_1 [kPa]",100.0),ni(c,"r",8.0,min_value=1.01),ni(d,"q_in [kJ/kg]",800.0,min_value=1.0))
    if name=="diesel":
        a,b,c,d=st.columns(4)
        return gas.diesel(ni(a,"T_1 [K]",300.0),ni(b,"P_1 [kPa]",100.0),ni(c,"r",18.0,min_value=1.01),ni(d,"r_c",2.0,min_value=1.001))
    if name=="dual":
        a,b,c,d,e=st.columns(5)
        return gas.dual(ni(a,"T_1 [K]",300.0),ni(b,"P_1 [kPa]",100.0),ni(c,"r",16.0,min_value=1.01),ni(d,"α=P_3/P_2",1.5,min_value=1.001),ni(e,"r_c=v_4/v_3",1.5,min_value=1.001))
    if name=="stirling":
        a,b,c,d=st.columns(4)
        return gas.stirling(ni(a,"T_L [K]",300.0),ni(b,"T_H [K]",900.0),ni(c,"P_1 [kPa]",1000.0),ni(d,"v_max/v_min",5.0,min_value=1.001))
    if name=="ericsson":
        a,b,c,d=st.columns(4)
        return gas.ericsson(ni(a,"T_L [K]",300.0),ni(b,"T_H [K]",900.0),ni(c,"P_baja [kPa]",100.0),ni(d,"P_alta/P_baja",5.0,min_value=1.001))
    if name in ("brayton_ideal","brayton_real"):
        a,b,c,d,e,f=st.columns(6)
        T1=ni(a,"T_1 [K]",300.0); P1=ni(b,"P_1 [kPa]",100.0)
        rp=ni(c,"r_p",10.0,min_value=1.001); T3=ni(d,"T_max [K]",1400.0)
        ec=1.0 if name=="brayton_ideal" else ni(e,"η_c",0.85,min_value=0.05,max_value=1.0)
        et=1.0 if name=="brayton_ideal" else ni(f,"η_t",0.88,min_value=0.05,max_value=1.0)
        return gas.brayton(T1,P1,rp,T3,ec,et)
    if name=="brayton_regen":
        a,b,c,d,e,f,g=st.columns(7)
        return gas.brayton_regen(ni(a,"T_1 [K]",300.0),ni(b,"P_1 [kPa]",100.0),ni(c,"r_p",8.0,min_value=1.001),ni(d,"T_max [K]",1400.0),ni(e,"ε_reg",0.75,min_value=0.0,max_value=1.0),ni(f,"η_c",0.85,min_value=0.05,max_value=1.0),ni(g,"η_t",0.88,min_value=0.05,max_value=1.0))
    if name=="brayton_advanced":
        a,b,c,d,e,f,g=st.columns(7)
        return gas.brayton_ic_rr(ni(a,"T_1 [K]",300.0),ni(b,"P_1 [kPa]",100.0),ni(c,"r_p total",12.0,min_value=1.001),ni(d,"T_max [K]",1400.0),ni(e,"ε_reg",0.75,min_value=0.0,max_value=1.0),ni(f,"η_c",0.85,min_value=0.05,max_value=1.0),ni(g,"η_t",0.88,min_value=0.05,max_value=1.0))
    if name=="turbojet":
        a,b,c,d,e,f=st.columns(6)
        return gas.turbojet_ideal(ni(a,"T_0 [K]",288.15),ni(b,"P_0 [kPa]",101.325),ni(c,"M_0",0.0,min_value=0.0),ni(d,"r_p",10.0,min_value=1.001),ni(e,"T_t4 [K]",1400.0),ni(f,"η_c",0.88,min_value=0.05,max_value=1.0),0.90,0.95)
    if name=="vapor_carnot":
        a,b=st.columns(2)
        return steam.carnot_vapor(ni(a,"T_H [°C]",300.0),ni(b,"T_L [°C]",40.0))
    if name in ("rankine_ideal","rankine_real"):
        a,b,c,d,e=st.columns(5)
        pc=ni(a,"P_cond [kPa]",10.0,min_value=0.7)
        pb=ni(b,"P_caldera [kPa]",8000.0,min_value=1.0)
        T=ni(c,"T_entrada turbina [°C]",480.0)
        ep=1.0 if name=="rankine_ideal" else ni(d,"η_p",0.85,min_value=0.05,max_value=1.0)
        et=1.0 if name=="rankine_ideal" else ni(e,"η_t",0.88,min_value=0.05,max_value=1.0)
        return steam.rankine(pc,pb,T,ep,et)
    if name=="rankine_reheat":
        a,b,c,d,e,f,g=st.columns(7)
        return steam.reheat(ni(a,"P_cond [kPa]",10.0,min_value=0.7),ni(b,"P_caldera [kPa]",15000.0),ni(c,"T_3 [°C]",550.0),ni(d,"P_reheat [kPa]",3000.0),ni(e,"T_5 [°C]",550.0),ni(f,"η_t",0.88,min_value=0.05,max_value=1.0),ni(g,"η_p",0.85,min_value=0.05,max_value=1.0))
    if name=="rankine_regen_open":
        a,b,c,d=st.columns(4)
        return steam.regen_open(ni(a,"P_cond [kPa]",10.0,min_value=0.7),ni(b,"P_FWH [kPa]",800.0),ni(c,"P_caldera [kPa]",8000.0),ni(d,"T_turbina [°C]",480.0))
    if name=="cogeneration":
        a,b,c,d,e=st.columns(5)
        return steam.cogeneration_simple(ni(a,"P_caldera [kPa]",8000.0),ni(b,"T_turbina [°C]",480.0),ni(c,"P_proceso [kPa]",500.0),ni(d,"P_cond [kPa]",10.0,min_value=0.7),ni(e,"y",0.30,min_value=0.01,max_value=0.99))
    if name=="combined":
        a,b,c,d,e,f=st.columns(6)
        return steam.combined_simple(ni(a,"r_p gas",10.0,min_value=1.01),ni(b,"T_1 gas [K]",300.0),ni(c,"TIT gas [K]",1400.0),ni(d,"P_cond [kPa]",10.0,min_value=0.7),ni(e,"P_caldera vapor [kPa]",8000.0),ni(f,"T_vapor [°C]",480.0))
    if name=="basic_cop":
        a,b=st.columns(2)
        return refrigeration.basic_cop(ni(a,"Q̇_L [kW]",10.0,min_value=0.001),ni(b,"Ẇ_in [kW]",3.0,min_value=0.001))
    if name=="carnot_reverse":
        a,b=st.columns(2)
        return refrigeration.carnot_reverse(ni(a,"T_L [K]",260.0),ni(b,"T_H [K]",310.0))
    if name=="vcr_ideal":
        a,b=st.columns(2)
        return refrigeration.vapor_ideal(ni(a,"T_evap [°C]",-10.0),ni(b,"T_cond [°C]",35.0))
    if name=="vcr_real":
        a,b,c,d,e=st.columns(5)
        return refrigeration.vapor_real(ni(a,"T_evap [°C]",-10.0),ni(b,"T_cond [°C]",35.0),ni(c,"Sobrecalentamiento [K]",5.0,min_value=0.0),ni(d,"Subenfriamiento [K]",5.0,min_value=0.0),ni(e,"η_c",0.80,min_value=0.05,max_value=1.0))
    if name=="heat_pump":
        a,b,c=st.columns(3)
        return refrigeration.heat_pump(ni(a,"T_evap [°C]",0.0),ni(b,"T_cond [°C]",45.0),ni(c,"η_c",0.80,min_value=0.05,max_value=1.0))
    if name=="cascade":
        a,b,c=st.columns(3)
        return refrigeration.cascade(ni(a,"T_evap [°C]",-40.0),ni(b,"T_inter [°C]",0.0),ni(c,"T_cond [°C]",35.0))
    if name=="gas_refrigeration":
        a,b,c,d=st.columns(4)
        return refrigeration.gas_cycle(ni(a,"T_1 [K]",278.15),ni(b,"T_3 [K]",308.15),ni(c,"P_baja [kPa]",100.0),ni(d,"r_p",4.0,min_value=1.01))
    if name=="absorption":
        a,b,c=st.columns(3)
        return refrigeration.absorption_limit(ni(a,"T_fuente [K]",393.15),ni(b,"T_0 [K]",298.15),ni(c,"T_L [K]",278.15))
    raise ValueError("Solver no configurado.")


# ----- Cabecera -----
c1,c2=st.columns([1,4.5],vertical_alignment="center")
with c1:
    if LOGO.exists(): st.image(str(LOGO),width=220)
with c2:
    st.markdown('<div class="brand-kicker">GG DIMEC · MECHLAB · TERMODINÁMICA</div>',unsafe_allow_html=True)
    st.title("Analizador de ciclos termodinámicos")
    st.caption("Selecciona un ciclo, modifica sus condiciones y estudia su comportamiento energético, diagramas, ecuaciones y desempeño.")

family=st.selectbox("Familia de ciclos",list(CYCLE_FAMILIES.keys()))
entry=st.selectbox("Ciclo / configuración",CYCLE_FAMILIES[family],format_func=lambda x:x["title"])
st.markdown(f"<div class='cycle-head'><b>{entry['title']}</b><br><span class='small-muted'>El análisis se centra en el ciclo seleccionado: componentes, estados, procesos, calor, trabajo, potencia y segunda ley.</span></div>",unsafe_allow_html=True)

result=None
struct=None
struct_data=None
struct_metrics=[]
warns=[]

if entry["mode"]=="solver":
    try:
        with st.container(border=True):
            st.markdown("#### Condiciones del ciclo")
            result=solver_ui(entry["solver"])
    except Exception as exc:
        st.error(str(exc))
else:
    struct=STRUCTURAL_CYCLES[entry["key"]]
    with st.container(border=True):
        st.markdown("#### Condiciones del ciclo")
        struct_data=render_structural_inputs(entry["key"])
    st.markdown("<div class='note-box'>Configuración avanzada para análisis estructural del ciclo. En esta versión ya se pueden ingresar condiciones base también para los casos complejos, manteniendo un enfoque pedagógico y de pre-diseño.</div>",unsafe_allow_html=True)
    struct_metrics=derived_metrics(struct_data)
    warns=structural_warnings(struct_data)
    for w in warns:
        st.warning(w)

tabs=st.tabs(["Análisis del ciclo","Esquema del ciclo","Estados y procesos","Ecuaciones","Diagramas","Energía y potencia","Segunda ley","Guía de análisis"])

with tabs[0]:
    if result:
        st.markdown("### Indicadores del ciclo")
        latex_metrics(result["metrics"])
        if result.get("notes"):
            st.markdown("### Interpretación")
            for n in result["notes"]: st.markdown(f"- {n}")
    else:
        st.markdown("### Resumen conceptual")
        st.markdown(struct["summary"])
        st.markdown("### Indicadores de configuración")
        latex_metrics(struct_metrics)
        st.markdown("### Condiciones activas")
        render_structural_parameters(struct_data)
        extra=extractions_table(struct_data)
        if extra is not None:
            st.markdown("### Configuración específica")
            render_specific_configuration(struct_data)

with tabs[1]:
    kind=(result or {}).get("meta",{}).get("schematic",entry.get("schematic","heat_engine"))
    context = struct_data if struct_data else (result or {}).get("meta",{})
    st.plotly_chart(schematic(kind,entry["title"],context=context),use_container_width=True,config={"displaylogo":False})
    st.caption("Esquemas conceptuales originales con simbología de componentes (bomba, turbina, compresor, intercambiador, válvula, etc.). Se privilegió legibilidad y una lógica visual cercana a la enseñanza clásica de ciclos.")

with tabs[2]:
    if result:
        if not result["states"].empty:
            st.markdown("#### Estados")
            st.markdown(r"Variables de estado: $T$, $P$, $v$, $h$, $u$, $s$ y $x$, según corresponda al ciclo.")
            st.dataframe(result["states"],use_container_width=True,hide_index=True)
        if not result["processes"].empty:
            st.markdown("#### Procesos")
            render_processes(result["processes"])
    else:
        st.markdown("#### Condiciones ingresadas")
        render_structural_parameters(struct_data)
        extra=extractions_table(struct_data)
        if extra is not None:
            st.markdown("#### Arreglo específico")
            render_specific_configuration(struct_data)
        st.markdown("#### Procesos y componentes")
        df=pd.DataFrame(struct["processes"],columns=["Tramo / componente","Proceso","Condición","Función"])
        render_processes(df)

with tabs[3]:
    eq_family="refrigeration" if family_type(family)=="refrigeration" else "power"
    st.markdown("#### Relaciones generales")
    for eq,desc in COMMON_EQUATIONS[eq_family]:
        st.latex(eq); st.caption(desc)
    st.markdown("#### Relaciones características del ciclo")
    if result:
        solver=entry.get("solver")
        for eq in SOLVER_EQUATIONS.get(solver,[]): st.latex(eq)
    else:
        for eq in struct["equations"]: st.latex(eq)
        if entry["key"]=="rankine_multi":
            st.latex(r"\dot m_{cond}=\left(1-\sum_i y_i\right)\dot m")
            st.latex(r"\dot W_t=\sum_j \dot m_j(h_{in,j}-h_{out,j})")
        if entry["key"]=="multi_evap":
            st.latex(r"\dot Q_{L,tot}=\sum_i \dot Q_{L,i}")

with tabs[4]:
    if result and not result["states"].empty:
        d=result.get("meta",{}).get("diagram")
        if d=="gas":
            pv,ts=gas_pv_ts(result["states"])
            a,b=st.columns(2)
            with a:
                if pv: st.plotly_chart(pv,use_container_width=True,config={"displaylogo":False})
            with b:
                if ts: st.plotly_chart(ts,use_container_width=True,config={"displaylogo":False})
        elif d=="water":
            fig=fluid_ts(result["states"],"water")
            if fig: st.plotly_chart(fig,use_container_width=True,config={"displaylogo":False})
        elif d=="r134a":
            a,b=st.columns(2)
            with a:
                fig=fluid_ts(result["states"],"r134a")
                if fig: st.plotly_chart(fig,use_container_width=True,config={"displaylogo":False})
            with b:
                ph=refrigerant_ph(result["states"])
                if ph: st.plotly_chart(ph,use_container_width=True,config={"displaylogo":False})
        else:
            st.info("Este ciclo se analiza principalmente mediante su esquema y balances.")
    else:
        st.info("Para estas configuraciones complejas la app privilegia, por ahora, esquema, balances y estructura del ciclo. El ingreso de condiciones ya quedó habilitado para apoyar el estudio y el pre-diseño.")

with tabs[5]:
    mdot=ni(st,"ṁ [kg/s]",1.0,min_value=0.000001)
    if result:
        st.markdown("#### Magnitudes específicas")
        latex_metrics(result["metrics"])
        rates=rates_from_specific(result["metrics"],mdot)
        if rates:
            st.markdown("#### Tasas y potencia")
            latex_metrics(rates)
    else:
        st.markdown("#### Relaciones para pasar a potencia y tasas")
        st.latex(r"\dot W=\dot m\,w")
        st.latex(r"\dot Q=\dot m\,q")
        if entry["key"]=="rankine_multi":
            ysum=sum(e["y"] for e in struct_data.get("extractions",[]))
            st.latex(r"\dot m_{cond}=\left(1-\sum_i y_i\right)\dot m")
            st.caption(f"Con las extracciones actuales: 1 - Σyᵢ = {fmt(1-ysum)}")
        elif entry["key"]=="multi_evap":
            qtot=sum(e["Qdot_kW"] for e in struct_data.get("evaps",[]))
            st.caption(f"Carga frigorífica total ingresada: {fmt(qtot)} kW")
        elif entry["key"]=="binary":
            st.latex(r"\dot W_{neto,tot}=\dot W_A+\dot W_B")
        st.info("En los casos estructurales esta pestaña queda orientada a enseñanza y pre-dimensionamiento. El solver detallado se puede incorporar después sin cambiar la lógica de la interfaz.")

with tabs[6]:
    st.markdown("### Evaluación con segunda ley")
    for eq,desc in COMMON_EQUATIONS["secondlaw"]:
        st.latex(eq); st.caption(desc)
    T0=ni(st,"T_0 [K]",298.15,min_value=1.0)
    if result:
        meta=result.get("meta",{})
        TH=meta.get("TH"); TL=meta.get("TL")
        if TH and TL and TH>TL:
            if family_type(family)=="refrigeration":
                st.latex(r"COP_{R,rev}=\frac{T_L}{T_H-T_L}")
                st.caption(f"Referencia reversible con los límites actuales: {TL/(TH-TL):.4g}")
            else:
                st.latex(r"\eta_{rev}=1-\frac{T_L}{T_H}")
                st.caption(f"Referencia reversible con los límites actuales: {(1-TL/TH)*100:.4g} %")
    else:
        st.markdown("Para estos ciclos complejos, la segunda ley se interpreta sobre todo identificando **irreversibilidades** en turbinas, compresores, válvulas de expansión, mezclas, regeneradores y transferencias de calor con ΔT finito.")

with tabs[7]:
    st.markdown("### Ruta para analizar este ciclo")
    if struct:
        for x in struct["study"]: st.markdown(f"- {x}")
        st.markdown("#### Cómo usar esta configuración")
        st.markdown("- Define primero el nivel térmico del ciclo: presiones, temperaturas y eficiencias base.")
        st.markdown("- Luego configura la arquitectura compleja: extracciones, evaporadores, cámara flash o regenerador, según corresponda.")
        st.markdown("- Usa el esquema para seguir el flujo principal y las derivaciones de masa/energía.")
        st.markdown("- Contrasta siempre lo ingresado con las ecuaciones de balance de masa y energía mostradas en la app.")
    else:
        st.markdown("""
1. Ubica los **componentes y estados** en el esquema.
2. Revisa qué condición caracteriza cada proceso: isentrópico, isobárico, isócoro, isotérmico, regenerativo o isoentálpico.
3. Relaciona cada componente con su intercambio de **calor** y/o **trabajo**.
4. Comprueba los estados en los diagramas disponibles.
5. Modifica **un parámetro a la vez** y observa el efecto sobre eficiencia, COP, trabajo, calor y calidad.
6. Introduce $\\dot m$ para pasar de magnitudes específicas a **potencia y tasas de calor**.
7. Compara el ciclo con su referencia reversible y revisa dónde aparecen irreversibilidades.
""")
        if result and result.get("notes"):
            st.markdown("#### Puntos particulares del ciclo")
            for n in result["notes"]: st.markdown(f"- {n}")

st.divider()
st.markdown("**GG DIMEC · MechLab** | Analizador unificado de Ciclos Termodinámicos")
st.caption("V1.0 · cierre del módulo de ciclos: notación matemática consistente en entradas, procesos y relaciones, con esquemas originales GG DIMEC.")
