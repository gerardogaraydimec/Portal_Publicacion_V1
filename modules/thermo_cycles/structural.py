from __future__ import annotations
import pandas as pd
import streamlit as st
from .ui_math import latex_number_input


def _ni(where, label, value, *, min_value=None, max_value=None, step=None, fmt="%.6g"):
    kwargs={"value":value, "format":fmt}
    if min_value is not None: kwargs["min_value"]=min_value
    if max_value is not None: kwargs["max_value"]=max_value
    if step is not None: kwargs["step"]=step
    return latex_number_input(where, label, **kwargs)


def render_structural_inputs(key: str) -> dict:
    data={"key": key}
    if key=="rankine_closed":
        c1,c2,c3,c4,c5,c6=st.columns(6)
        data["P_cond_kPa"]=_ni(c1,"P_cond [kPa]",10.0,min_value=0.7)
        data["P_FWH_kPa"]=_ni(c2,"P_extracción / FWH [kPa]",800.0,min_value=10.0)
        data["P_boiler_kPa"]=_ni(c3,"P_caldera [kPa]",8000.0,min_value=100.0)
        data["T_turb_in_C"]=_ni(c4,"T_entrada turbina [°C]",480.0,min_value=50.0)
        data["eta_t"]=_ni(c5,"η_t",0.88,min_value=0.05,max_value=1.0,step=0.01)
        data["eta_p"]=_ni(c6,"η_p",0.85,min_value=0.05,max_value=1.0,step=0.01)
        c7,c8=st.columns(2)
        data["drain_mode"]=c7.selectbox("Tratamiento de drenajes", ["Retorno por válvula","Retorno con bomba"], index=0)
        data["TTD_C"]=_ni(c8,"ΔT terminal calentador [°C]",5.0,min_value=0.0)
        return data

    if key=="rankine_multi":
        c1,c2,c3,c4,c5,c6=st.columns(6)
        data["P_cond_kPa"]=_ni(c1,"P_cond [kPa]",10.0,min_value=0.7)
        data["P_boiler_kPa"]=_ni(c2,"P_caldera [kPa]",15000.0,min_value=100.0)
        data["T_turb_in_C"]=_ni(c3,"T_entrada turbina [°C]",540.0,min_value=50.0)
        data["eta_t"]=_ni(c4,"η_t",0.88,min_value=0.05,max_value=1.0,step=0.01)
        data["eta_p"]=_ni(c5,"η_p",0.85,min_value=0.05,max_value=1.0,step=0.01)
        data["n_extract"] = int(c6.slider("N° de extracciones", min_value=2, max_value=4, value=3))
        st.markdown("##### Configuración de extracciones")
        extra=[]
        default_P=[3000.0, 900.0, 250.0, 80.0]
        default_y=[0.10, 0.08, 0.06, 0.04]
        for i in range(data["n_extract"]):
            a,b,c=st.columns([1.1,1.1,1.4])
            P=_ni(a, f"P_y{i+1} [kPa]", default_P[i], min_value=10.0)
            y=_ni(b, f"y_{i+1}", default_y[i], min_value=0.0, max_value=0.95, step=0.01)
            heater=c.selectbox(f"Calentador {i+1}", ["Abierto","Cerrado"], index=0 if i==0 else 1, key=f"heater_{i+1}")
            extra.append({"Extracción": i+1, "P_kPa": P, "y": y, "Tipo": heater})
        data["extractions"]=extra
        return data

    if key=="binary":
        c1,c2,c3,c4,c5,c6=st.columns(6)
        data["fluid_hot"]=c1.selectbox("Fluido ciclo superior", ["Agua/vapor","R245fa","n-pentano","Tolueno"], index=0)
        data["fluid_cold"]=c2.selectbox("Fluido ciclo inferior", ["Agua/vapor","R245fa","n-pentano","Amoniaco"], index=1)
        data["T_source_C"]=_ni(c3,"T_fuente alta [°C]",320.0)
        data["T_inter_C"]=_ni(c4,"T_intercambio [°C]",170.0)
        data["T_sink_C"]=_ni(c5,"T_sumidero [°C]",35.0)
        data["eta_upper"]=_ni(c6,"η ciclo superior",0.30,min_value=0.01,max_value=1.0,step=0.01)
        data["eta_lower"]=_ni(st,"η ciclo inferior",0.18,min_value=0.01,max_value=1.0,step=0.01)
        return data

    if key=="multistage_flash":
        c1,c2,c3,c4,c5,c6,c7=st.columns(7)
        data["T_evap_C"]=_ni(c1,"T_evap [°C]",-30.0)
        data["T_cond_C"]=_ni(c2,"T_cond [°C]",35.0)
        data["P_inter_kPa"]=_ni(c3,"P_intermedia [kPa]",450.0,min_value=10.0)
        data["superheat_K"]=_ni(c4,"Sobrecalentamiento [K]",5.0,min_value=0.0)
        data["subcool_K"]=_ni(c5,"Subenfriamiento [K]",5.0,min_value=0.0)
        data["eta_c1"]=_ni(c6,"η_c1",0.80,min_value=0.05,max_value=1.0,step=0.01)
        data["eta_c2"]=_ni(c7,"η_c2",0.82,min_value=0.05,max_value=1.0,step=0.01)
        return data

    if key=="multi_evap":
        c1,c2,c3,c4=st.columns(4)
        data["T_cond_C"]=_ni(c1,"T_cond [°C]",35.0)
        data["eta_c"]=_ni(c2,"η_compresor",0.80,min_value=0.05,max_value=1.0,step=0.01)
        data["subcool_K"]=_ni(c3,"Subenfriamiento [K]",5.0,min_value=0.0)
        data["n_evap"] = int(c4.slider("N° de evaporadores", min_value=2, max_value=4, value=3))
        evaps=[]
        st.markdown("##### Cargas y temperaturas por evaporador")
        for i in range(data["n_evap"]):
            a,b=st.columns(2)
            T=_ni(a, f"T_evap_{i+1} [°C]", -5.0-10*i)
            Q=_ni(b, f"Q̇_L{i+1} [kW]", 15.0+5*i, min_value=0.0)
            evaps.append({"Evaporador": i+1, "T_evap_C": T, "Qdot_kW": Q})
        data["evaps"]=evaps
        return data

    if key=="liquefaction":
        c1,c2,c3,c4,c5,c6=st.columns(6)
        data["gas"]=c1.selectbox("Gas de trabajo", ["N₂","Aire","Metano","Oxígeno"], index=0)
        data["P_high_kPa"]=_ni(c2,"P_alta [kPa]",12000.0,min_value=500.0)
        data["P_low_kPa"]=_ni(c3,"P_baja [kPa]",100.0,min_value=10.0)
        data["T_aftercool_C"]=_ni(c4,"T después de post-enfriador [°C]",25.0)
        data["eps_reg"]=_ni(c5,"ε regenerador",0.85,min_value=0.0,max_value=1.0,step=0.01)
        data["eta_c"]=_ni(c6,"η_compresor",0.80,min_value=0.05,max_value=1.0,step=0.01)
        return data

    return data


def inputs_table(data: dict) -> pd.DataFrame:
    rows=[]
    units={"P_cond_kPa":"kPa","P_FWH_kPa":"kPa","P_boiler_kPa":"kPa","T_turb_in_C":"°C","eta_t":"—","eta_p":"—",
           "TTD_C":"°C","T_source_C":"°C","T_inter_C":"°C","T_sink_C":"°C","eta_upper":"—","eta_lower":"—",
           "T_evap_C":"°C","T_cond_C":"°C","P_inter_kPa":"kPa","superheat_K":"K","subcool_K":"K","eta_c1":"—","eta_c2":"—",
           "eta_c":"—","P_high_kPa":"kPa","P_low_kPa":"kPa","T_aftercool_C":"°C","eps_reg":"—"}
    for k,v in data.items():
        if k in {"key","extractions","evaps"}:
            continue
        rows.append({"Parámetro":k, "Valor":v, "Unidad":units.get(k,"—")})
    return pd.DataFrame(rows)


def extractions_table(data: dict) -> pd.DataFrame | None:
    xs=data.get("extractions")
    if xs:
        return pd.DataFrame(xs)
    evs=data.get("evaps")
    if evs:
        return pd.DataFrame(evs)
    return None


def derived_metrics(data: dict) -> list[dict]:
    key=data.get("key")
    metrics=[]
    if key=="rankine_closed":
        rp = data["P_boiler_kPa"]/data["P_cond_kPa"] if data["P_cond_kPa"]>0 else None
        metrics=[
            {"symbol":r"r_p = P_{caldera}/P_{cond}","value":rp,"unit":"","description":"Razón global de presión del ciclo."},
            {"symbol":r"P_y","value":data["P_FWH_kPa"],"unit":"kPa","description":"Presión de extracción / calentador."},
            {"symbol":r"\Delta T_{TTD}","value":data["TTD_C"],"unit":"°C","description":"Aproximación térmica terminal del calentador."},
        ]
    elif key=="rankine_multi":
        ys=[e["y"] for e in data.get("extractions",[])]
        ps=[e["P_kPa"] for e in data.get("extractions",[])]
        ytot=sum(ys)
        metrics=[
            {"symbol":r"n_{ext}","value":data.get("n_extract",0),"unit":"","description":"Número de extracciones activas."},
            {"symbol":r"\sum y_i","value":ytot,"unit":"","description":"Fracción total extraída desde la turbina."},
            {"symbol":r"1-\sum y_i","value":1-ytot,"unit":"","description":"Fracción de flujo que llega al condensador."},
            {"symbol":r"\overline{P}_y","value":(sum(ps)/len(ps) if ps else None),"unit":"kPa","description":"Presión media de extracción."},
        ]
    elif key=="binary":
        metrics=[
            {"symbol":r"\Delta T_{fuente-int}","value":data["T_source_C"]-data["T_inter_C"],"unit":"°C","description":"Salto térmico disponible en el ciclo superior."},
            {"symbol":r"\Delta T_{int-sum}","value":data["T_inter_C"]-data["T_sink_C"],"unit":"°C","description":"Salto térmico utilizable en el ciclo inferior."},
            {"symbol":r"\eta_{A}","value":data["eta_upper"],"unit":"","description":"Eficiencia supuesta del ciclo superior."},
            {"symbol":r"\eta_{B}","value":data["eta_lower"],"unit":"","description":"Eficiencia supuesta del ciclo inferior."},
        ]
    elif key=="multistage_flash":
        metrics=[
            {"symbol":r"P_{int}","value":data["P_inter_kPa"],"unit":"kPa","description":"Presión intermedia de la cámara flash."},
            {"symbol":r"\Delta T_{sc}","value":data["subcool_K"],"unit":"K","description":"Subenfriamiento a la salida del condensador."},
            {"symbol":r"\Delta T_{sh}","value":data["superheat_K"],"unit":"K","description":"Sobrecalentamiento a la salida del evaporador."},
            {"symbol":r"\eta_{c,eq}","value":0.5*(data["eta_c1"]+data["eta_c2"]),"unit":"","description":"Promedio simple de eficiencias de compresión."},
        ]
    elif key=="multi_evap":
        qtot=sum(v["Qdot_kW"] for v in data.get("evaps",[]))
        metrics=[
            {"symbol":r"n_{evap}","value":data.get("n_evap",0),"unit":"","description":"Número de evaporadores activos."},
            {"symbol":r"\dot Q_{L,tot}","value":qtot,"unit":"kW","description":"Carga frigorífica total."},
            {"symbol":r"T_{cond}","value":data["T_cond_C"],"unit":"°C","description":"Temperatura de condensación."},
            {"symbol":r"\eta_c","value":data["eta_c"],"unit":"","description":"Eficiencia supuesta del compresor común."},
        ]
    elif key=="liquefaction":
        metrics=[
            {"symbol":r"r_p=P_{alta}/P_{baja}","value":data["P_high_kPa"]/data["P_low_kPa"],"unit":"","description":"Razón de presión de compresión."},
            {"symbol":r"\varepsilon_{reg}","value":data["eps_reg"],"unit":"","description":"Efectividad del regenerador."},
            {"symbol":r"T_{post}","value":data["T_aftercool_C"],"unit":"°C","description":"Temperatura después del post-enfriador."},
            {"symbol":r"\eta_c","value":data["eta_c"],"unit":"","description":"Eficiencia del compresor."},
        ]
    return metrics


def structural_warnings(data: dict) -> list[str]:
    notes=[]
    key=data.get("key")
    if key=="rankine_multi":
        ytot=sum(e["y"] for e in data.get("extractions",[]))
        if ytot>=1.0:
            notes.append("La suma de fracciones extraídas es igual o mayor que 1.0; físicamente no quedaría flujo hacia etapas posteriores y el condensador.")
        elif ytot>0.5:
            notes.append("La suma de extracciones es alta. Revise si la configuración representa un estudio conceptual o un diseño muy intensivo en regeneración.")
        ps=[e["P_kPa"] for e in data.get("extractions",[])]
        if any(ps[i] <= ps[i+1] for i in range(len(ps)-1)):
            notes.append("Se recomienda que las presiones de extracción decrezcan a lo largo de la expansión de la turbina.")
    if key=="multi_evap":
        Ts=[e["T_evap_C"] for e in data.get("evaps",[])]
        if any(T>=data["T_cond_C"] for T in Ts):
            notes.append("Cada temperatura de evaporación debe ser menor que la temperatura de condensación." )
    if key=="liquefaction" and data["P_high_kPa"]<=data["P_low_kPa"]:
        notes.append("La presión alta debe ser mayor que la presión baja para que el ciclo de licuefacción tenga sentido físico.")
    return notes
