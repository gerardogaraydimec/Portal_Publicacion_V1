from __future__ import annotations
import numpy as np
import pandas as pd
import plotly.graph_objects as go

try:
    from iapws import IAPWS97
except Exception:
    IAPWS97=None
try:
    from CoolProp.CoolProp import PropsSI
except Exception:
    PropsSI=None

ORANGE="#f28e1c"; BLUE="#2474b5"; RED="#c43c35"

def gas_pv_ts(states):
    if states.empty or "v [m³/kg]" not in states.columns: return None,None
    cyc=pd.concat([states,states.iloc[[0]]],ignore_index=True)
    pv=go.Figure(go.Scatter(x=cyc["v [m³/kg]"],y=cyc["P [kPa]"],mode="lines+markers+text",
                            text=cyc["Estado"],textposition="top center",line=dict(color=ORANGE,width=3)))
    pv.update_layout(title="P-v",xaxis_title="v [m³/kg]",yaxis_title="P [kPa]",height=430,margin=dict(l=20,r=20,t=45,b=25))
    ts=None
    if "s* [kJ/kg·K]" in states.columns and "T [K]" in states.columns:
        ts=go.Figure(go.Scatter(x=cyc["s* [kJ/kg·K]"],y=cyc["T [K]"],mode="lines+markers+text",
                                text=cyc["Estado"],textposition="top center",line=dict(color=ORANGE,width=3)))
        ts.update_layout(title="T-s",xaxis_title="s* [kJ/kg·K]",yaxis_title="T [K]",height=430,margin=dict(l=20,r=20,t=45,b=25))
    return pv,ts

def water_dome(n=150):
    if IAPWS97 is None: return pd.DataFrame()
    rows=[]
    for tc in np.linspace(0.02,373.9,n):
        try:
            f=IAPWS97(T=tc+273.15,x=0); g=IAPWS97(T=tc+273.15,x=1)
            rows.append((f.s,tc,g.s))
        except: pass
    return pd.DataFrame(rows,columns=["sf","T","sg"])

def r134a_dome(n=150,fluid="R134a"):
    if PropsSI is None: return pd.DataFrame()
    rows=[]
    try:
        tmin=PropsSI("Ttriple",fluid)+1; tmax=PropsSI("Tcrit",fluid)-.5
    except: return pd.DataFrame()
    for t in np.linspace(tmin,tmax,n):
        try:
            rows.append((PropsSI("S","T",t,"Q",0,fluid)/1000,t-273.15,PropsSI("S","T",t,"Q",1,fluid)/1000))
        except: pass
    return pd.DataFrame(rows,columns=["sf","T","sg"])

def fluid_ts(states,kind="water"):
    if states.empty or "s [kJ/kg·K]" not in states.columns: return None
    d=water_dome() if kind=="water" else r134a_dome()
    fig=go.Figure()
    if not d.empty:
        fig.add_trace(go.Scatter(x=d["sf"],y=d["T"],name="Líquido saturado",line=dict(color=BLUE,width=2)))
        fig.add_trace(go.Scatter(x=d["sg"],y=d["T"],name="Vapor saturado",line=dict(color=RED,width=2)))
    cyc=pd.concat([states,states.iloc[[0]]],ignore_index=True)
    fig.add_trace(go.Scatter(x=cyc["s [kJ/kg·K]"],y=cyc["T [°C]"],mode="lines+markers+text",
                             text=cyc["Estado"],textposition="top center",name="Ciclo",
                             line=dict(color=ORANGE,width=3),marker=dict(size=9)))
    fig.update_layout(title="T-s",xaxis_title="s [kJ/kg·K]",yaxis_title="T [°C]",height=490,margin=dict(l=20,r=20,t=50,b=30))
    return fig

def refrigerant_ph(states,fluid="R134a"):
    if states.empty or "h [kJ/kg]" not in states.columns: return None
    cyc=pd.concat([states,states.iloc[[0]]],ignore_index=True)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=cyc["h [kJ/kg]"],y=cyc["P [kPa]"],mode="lines+markers+text",
                             text=cyc["Estado"],textposition="top center",line=dict(color=ORANGE,width=3)))
    fig.update_yaxes(type="log")
    fig.update_layout(title="P-h",xaxis_title="h [kJ/kg]",yaxis_title="P [kPa]",height=490,margin=dict(l=20,r=20,t=50,b=30))
    return fig
