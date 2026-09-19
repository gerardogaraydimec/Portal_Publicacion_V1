from __future__ import annotations
import re
from typing import Any
import streamlit as st

# Etiquetas visibles de entrada en notación matemática consistente.
EXACT_LABELS = {
    "T_H": r"T_H", "T_L": r"T_L", "T_0": r"T_0", "T_1": r"T_1", "T_3": r"T_3", "T_5": r"T_5",
    "P_0": r"P_0", "P_1": r"P_1", "P_baja": r"P_{baja}", "P_cond": r"P_{cond}", "P_caldera": r"P_{caldera}",
    "P_FWH": r"P_{FWH}", "P_reheat": r"P_{RH}", "P_proceso": r"P_{proceso}", "P_intermedia": r"P_{int}",
    "P_alta": r"P_{alta}", "T_cond": r"T_{cond}", "T_evap": r"T_{evap}", "T_inter": r"T_{int}",
    "T_fuente": r"T_{fuente}", "T_sumidero": r"T_{sum}", "T_vapor": r"T_{vapor}", "T_max": r"T_{max}",
    "T_t4": r"T_{t4}", "M_0": r"M_0", "r": r"r", "r_c": r"r_c", "r_p": r"r_p", "y": r"y",
    "η_c": r"\eta_c", "η_t": r"\eta_t", "η_p": r"\eta_p", "η_c1": r"\eta_{c,1}", "η_c2": r"\eta_{c,2}",
    "ε_reg": r"\varepsilon_{reg}", "η_compresor": r"\eta_c", "ε regenerador": r"\varepsilon_{reg}",
    "Sobrecalentamiento": r"\Delta T_{sh}", "Subenfriamiento": r"\Delta T_{sc}",
    "Q̇_L": r"\dot Q_L", "Ẇ_in": r"\dot W_{in}", "ṁ": r"\dot m",
    "TIT gas": r"T_{turb,in}", "T_1 gas": r"T_{1,g}", "P_caldera vapor": r"P_{caldera,v}",
    "T_entrada turbina": r"T_{t,in}", "T_turbina": r"T_{t,in}", "P_extracción / FWH": r"P_y=P_{FWH}",
    "ΔT terminal calentador": r"\Delta T_{TTD}", "T_fuente alta": r"T_{fuente}", "T_intercambio": r"T_{int}",
    "η ciclo superior": r"\eta_A", "η ciclo inferior": r"\eta_B", "T después de post-enfriador": r"T_{post}",
    "r_p gas": r"r_{p,g}", "r_p total": r"r_{p,tot}", "v_2/v_1": r"v_2/v_1", "v_max/v_min": r"v_{max}/v_{min}",
    "q_in": r"q_{in}",
}


def split_unit(label: str) -> tuple[str, str]:
    m=re.match(r"^(.*?)\s*\[([^\]]+)\]\s*$", label)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return label.strip(), ""


def label_to_latex(label: str) -> str:
    base,_=split_unit(label)
    if base in EXACT_LABELS:
        return EXACT_LABELS[base]
    m=re.fullmatch(r"P_y(\d+)", base)
    if m: return rf"P_{{y,{m.group(1)}}}"
    m=re.fullmatch(r"y_(\d+)", base)
    if m: return rf"y_{{{m.group(1)}}}"
    m=re.fullmatch(r"T_evap_(\d+)", base)
    if m: return rf"T_{{evap,{m.group(1)}}}"
    m=re.fullmatch(r"Q̇_L(\d+)", base)
    if m: return rf"\dot Q_{{L,{m.group(1)}}}"
    if base=="α=P_3/P_2": return r"\alpha=P_3/P_2"
    if base=="r_c=v_4/v_3": return r"r_c=v_4/v_3"
    if base=="P_alta/P_baja": return r"P_{alta}/P_{baja}"
    # Fallback visual consistente para variables simples con subíndice.
    m=re.fullmatch(r"([A-Za-z]+)_([A-Za-z0-9]+)", base)
    if m: return rf"{m.group(1)}_{{{m.group(2)}}}"
    return rf"\mathrm{{{base.replace(' ', r'\ ')}}}"


def render_input_label(where, label: str):
    _,unit=split_unit(label)
    latex=label_to_latex(label)
    suffix=f" [{unit}]" if unit else ""
    where.markdown(f"${latex}${suffix}")


def latex_number_input(where, label: str, value: float, **kwargs):
    render_input_label(where,label)
    return where.number_input(label, value=value, format=kwargs.pop("format","%.6g"), label_visibility="collapsed", **kwargs)


FORMULA_MAP = {
    r"\dot Q_H=\dot Q_L+\dot W_{in}": r"\dot Q_H=\dot Q_L+\dot W_{in}",
    "s = cte": r"s=\mathrm{cte}", "s=cte": r"s=\mathrm{cte}",
    "v = cte": r"v=\mathrm{cte}", "P = cte": r"P=\mathrm{cte}", "P=cte": r"P=\mathrm{cte}",
    "P ≈ cte": r"P\approx\mathrm{cte}", "P alta = cte": r"P_{alta}=\mathrm{cte}",
    "P baja = cte": r"P_{baja}=\mathrm{cte}", "P alta ≈ cte": r"P_{alta}\approx\mathrm{cte}",
    "P baja ≈ cte": r"P_{baja}\approx\mathrm{cte}", "T = TH": r"T=T_H", "T = TL": r"T=T_L",
    "ηc": r"\eta_c", "ηt": r"\eta_t", "ηp": r"\eta_p", "ηn": r"\eta_n", "ηc aplicada": r"\eta_c", "ηt aplicada": r"\eta_t",
    "ε": r"\varepsilon", "T3 = T1 idealizado": r"T_3\approx T_1", "Ptotal ≈ cte": r"P_t\approx\mathrm{cte}",
    "trabajo turbina = trabajo compresor": r"w_t=w_c", "flujo 1-y": r"\dot m\,(1-y)", "flujo total": r"\dot m",
    "masa + energía": r"\sum \dot m_{in}=\sum \dot m_{out},\quad \sum \dot m h_{in}=\sum \dot m h_{out}",
    "aprox. isentrópica": r"s_{out}\approx s_{in}", "QH,baja = QL,alta": r"\dot Q_{H,baja}=\dot Q_{L,alta}",
    "Tsource↔T0": r"T_{fuente}\leftrightarrow T_0", "TL↔T0": r"T_L\leftrightarrow T_0",
}


def formula_to_latex(text: Any) -> str | None:
    if text is None: return None
    s=str(text).strip()
    if not s: return None
    if s in FORMULA_MAP: return FORMULA_MAP[s]
    if s.startswith("\\"): return s
    # Casos simples adicionales
    if "=" in s and all(x not in s.lower() for x in ["balance", "trabajo", "flujo"]):
        s=s.replace("≈", r"\approx").replace("cte", r"\mathrm{cte}")
        return s
    return None


def process_path_to_latex(text: Any) -> str | None:
    if text is None: return None
    s=str(text).strip()
    if re.fullmatch(r"\d+→\d+",s):
        a,b=s.split("→"); return rf"{a}\rightarrow {b}"
    if re.fullmatch(r"\d+→\w+",s):
        a,b=s.split("→"); return rf"{a}\rightarrow \mathrm{{{b}}}"
    return None


def render_processes(df):
    if df is None or df.empty:
        return
    h=st.columns([0.9,2.0,1.8,1.7])
    h[0].markdown("**Proceso**"); h[1].markdown("**Descripción**"); h[2].markdown("**Restricción / modelo**"); h[3].markdown("**Equipo / lectura**")
    for _,row in df.iterrows():
        with st.container(border=True):
            c=st.columns([0.9,2.0,1.8,1.7], vertical_alignment="center")
            p=process_path_to_latex(row.iloc[0])
            c[0].markdown(f"${p}$" if p else str(row.iloc[0]))
            c[1].write(str(row.iloc[1]))
            f=formula_to_latex(row.iloc[2])
            c[2].markdown(f"${f}$" if f else str(row.iloc[2]))
            c[3].write(str(row.iloc[3]))


STRUCT_PARAM_LATEX = {
    "P_cond_kPa":r"P_{cond}", "P_FWH_kPa":r"P_{FWH}", "P_boiler_kPa":r"P_{caldera}", "T_turb_in_C":r"T_{t,in}",
    "eta_t":r"\eta_t", "eta_p":r"\eta_p", "TTD_C":r"\Delta T_{TTD}", "T_source_C":r"T_{fuente}",
    "T_inter_C":r"T_{int}", "T_sink_C":r"T_{sum}", "eta_upper":r"\eta_A", "eta_lower":r"\eta_B",
    "T_evap_C":r"T_{evap}", "T_cond_C":r"T_{cond}", "P_inter_kPa":r"P_{int}", "superheat_K":r"\Delta T_{sh}",
    "subcool_K":r"\Delta T_{sc}", "eta_c1":r"\eta_{c,1}", "eta_c2":r"\eta_{c,2}", "eta_c":r"\eta_c",
    "P_high_kPa":r"P_{alta}", "P_low_kPa":r"P_{baja}", "T_aftercool_C":r"T_{post}", "eps_reg":r"\varepsilon_{reg}",
    "n_extract":r"n_{ext}", "n_evap":r"n_{evap}",
}
STRUCT_UNITS = {
    "P_cond_kPa":"kPa", "P_FWH_kPa":"kPa", "P_boiler_kPa":"kPa", "T_turb_in_C":"°C", "TTD_C":"°C",
    "T_source_C":"°C", "T_inter_C":"°C", "T_sink_C":"°C", "T_evap_C":"°C", "T_cond_C":"°C", "P_inter_kPa":"kPa",
    "superheat_K":"K", "subcool_K":"K", "P_high_kPa":"kPa", "P_low_kPa":"kPa", "T_aftercool_C":"°C",
}


def render_structural_parameters(data: dict):
    rows=[]
    for k,v in data.items():
        if k in {"key","extractions","evaps","drain_mode","fluid_hot","fluid_cold","gas"}: continue
        rows.append((STRUCT_PARAM_LATEX.get(k,rf"\mathrm{{{k}}}"), v, STRUCT_UNITS.get(k,"—")))
    if not rows: return
    h=st.columns([1.3,1.2,0.8]); h[0].markdown("**Parámetro**"); h[1].markdown("**Valor**"); h[2].markdown("**Unidad**")
    for sym,val,unit in rows:
        with st.container(border=True):
            c=st.columns([1.3,1.2,0.8],vertical_alignment="center")
            c[0].markdown(f"${sym}$")
            c[1].write(val)
            c[2].write(unit)


def render_specific_configuration(data: dict):
    xs=data.get("extractions") or []
    if xs:
        h=st.columns([0.8,1.1,1.0,1.2]); h[0].markdown("**Extracción**"); h[1].markdown("**Presión**"); h[2].markdown("**Fracción**"); h[3].markdown("**Calentador**")
        for e in xs:
            i=e["Extracción"]
            with st.container(border=True):
                c=st.columns([0.8,1.1,1.0,1.2],vertical_alignment="center")
                c[0].markdown(f"$y_{{{i}}}$")
                c[1].markdown(f"$P_{{y,{i}}}$ = {e['P_kPa']:.6g} kPa")
                c[2].markdown(f"$y_{{{i}}}$ = {e['y']:.6g}")
                c[3].write(e["Tipo"])
        return
    evs=data.get("evaps") or []
    if evs:
        h=st.columns([0.8,1.3,1.3]); h[0].markdown("**Evaporador**"); h[1].markdown("**Temperatura**"); h[2].markdown("**Carga**")
        for e in evs:
            i=e["Evaporador"]
            with st.container(border=True):
                c=st.columns([0.8,1.3,1.3],vertical_alignment="center")
                c[0].write(i)
                c[1].markdown(f"$T_{{evap,{i}}}$ = {e['T_evap_C']:.6g} °C")
                c[2].markdown(f"$\\dot Q_{{L,{i}}}$ = {e['Qdot_kW']:.6g} kW")
