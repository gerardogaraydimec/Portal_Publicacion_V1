from __future__ import annotations
import math
import pandas as pd
from .core import *

try:
    from CoolProp.CoolProp import PropsSI
except Exception:
    PropsSI=None

def require():
    if PropsSI is None: raise RuntimeError("Falta instalar CoolProp.")

def cpstate(label,fluid,P,T=None,H=None,S=None,Q=None):
    require()
    if T is not None: args=("P",P,"T",T)
    elif H is not None: args=("P",P,"H",H)
    elif S is not None: args=("P",P,"S",S)
    elif Q is not None: args=("P",P,"Q",Q)
    else: raise ValueError("Estado incompleto.")
    h=PropsSI("H",*args,fluid)/1000; s=PropsSI("S",*args,fluid)/1000
    temp=PropsSI("T",*args,fluid); rho=PropsSI("D",*args,fluid)
    try:
        q=PropsSI("Q",*args,fluid); q=None if q<0 or q>1 else q
    except: q=None
    return {"Estado":str(label),"T [°C]":temp-273.15,"P [kPa]":P/1000,
            "v [m³/kg]":1/rho,"h [kJ/kg]":h,"s [kJ/kg·K]":s,"x [-]":q}

def proc(rows):
    return pd.DataFrame(rows,columns=["Proceso","Descripción","Restricción / modelo","Equipo / lectura"])

def basic_cop(QL=10.0,W=3.0):
    if QL<=0 or W<=0: raise ValueError("Use QL > 0 y W > 0.")
    QH=QL+W; copr=QL/W; cophp=QH/W
    mets=[metric(r"COP_R",copr,"","Refrigerador"),metric(r"COP_{HP}",cophp,"","Bomba de calor"),
          metric(r"\dot Q_L",QL,"kW","Efecto de refrigeración"),metric(r"\dot W_{in}",W,"kW","Potencia de entrada"),
          metric(r"\dot Q_H",QH,"kW","Calor rechazado")]
    return package(pd.DataFrame(),proc([["Ciclo","Balance global",r"\dot Q_H=\dot Q_L+\dot W_{in}","Refrigerador / bomba de calor"]]),mets,
                   ["La misma máquina puede evaluarse como refrigerador o bomba de calor según el efecto útil."],
                   {"diagram":"none","schematic":"refrigerator"})

def carnot_reverse(TL=260.0,TH=310.0):
    if TH<=TL or TL<=0: raise ValueError("Use TH > TL > 0.")
    cr=carnot_cop_r(TH,TL); ch=carnot_cop_hp(TH,TL)
    mets=[metric(r"COP_{R,Carnot}",cr,"","COP máximo de refrigeración"),
          metric(r"COP_{HP,Carnot}",ch,"","COP máximo de bomba de calor")]
    return package(pd.DataFrame(),proc([
        ["1→2","Compresión isentrópica","s = cte","Trabajo entra"],
        ["2→3","Rechazo isotérmico","T = TH","QH sale"],
        ["3→4","Expansión isentrópica","s = cte","Trabajo recuperado"],
        ["4→1","Absorción isotérmica","T = TL","QL entra"],
    ]),mets,["Referencia reversible superior entre dos depósitos térmicos."],
        {"TH":TH,"TL":TL,"diagram":"none","schematic":"refrigerator"})

def vapor_ideal(Tevap_C=-10.0,Tcond_C=35.0,fluid="R134a"):
    require()
    Te=Tevap_C+273.15; Tc=Tcond_C+273.15
    if Tc<=Te: raise ValueError("Tcond debe ser mayor que Tevap.")
    Pl=PropsSI("P","T",Te,"Q",1,fluid); Ph=PropsSI("P","T",Tc,"Q",0,fluid)
    h1=PropsSI("H","P",Pl,"Q",1,fluid); s1=PropsSI("S","P",Pl,"Q",1,fluid)
    h2=PropsSI("H","P",Ph,"S",s1,fluid); h3=PropsSI("H","P",Ph,"Q",0,fluid); h4=h3
    ql=(h1-h4)/1000; wc=(h2-h1)/1000; qh=(h2-h3)/1000; cop=ql/wc
    states=pd.DataFrame([cpstate(1,fluid,Pl,Q=1),cpstate(2,fluid,Ph,H=h2),
                         cpstate(3,fluid,Ph,Q=0),cpstate(4,fluid,Pl,H=h4)])
    processes=proc([
        ["1→2","Compresión isentrópica","s = cte","Compresor"],
        ["2→3","Condensación","P alta = cte","Condensador"],
        ["3→4","Estrangulamiento","h = cte","Válvula"],
        ["4→1","Evaporación","P baja = cte","Evaporador"],
    ])
    mets=[metric(r"COP_R",cop,"","Coeficiente de desempeño"),
          metric(r"q_L",ql,"kJ/kg","Efecto refrigerante"),
          metric(r"w_c",wc,"kJ/kg","Trabajo compresor"),
          metric(r"q_H",qh,"kJ/kg","Calor rechazado")]
    return package(states,processes,mets,
        ["Vapor saturado entra al compresor y líquido saturado sale del condensador.",
         "La válvula introduce un proceso isoentálpico irreversible."],
        {"TH":Tc,"TL":Te,"diagram":"r134a","schematic":"vcr"})

def vapor_real(Tevap_C=-10.0,Tcond_C=35.0,superheat=5.0,subcool=5.0,eta_c=0.8,fluid="R134a"):
    require()
    if not(0<eta_c<=1): raise ValueError("0 < ηc ≤ 1.")
    Te=Tevap_C+273.15; Tc=Tcond_C+273.15
    Pl=PropsSI("P","T",Te,"Q",1,fluid); Ph=PropsSI("P","T",Tc,"Q",0,fluid)
    T1=Te+superheat; h1=PropsSI("H","P",Pl,"T",T1,fluid); s1=PropsSI("S","P",Pl,"T",T1,fluid)
    h2s=PropsSI("H","P",Ph,"S",s1,fluid); h2=h1+(h2s-h1)/eta_c
    T3=Tc-subcool; h3=PropsSI("H","P",Ph,"T",T3,fluid); h4=h3
    ql=(h1-h4)/1000; wc=(h2-h1)/1000; qh=(h2-h3)/1000; cop=ql/wc
    states=pd.DataFrame([cpstate(1,fluid,Pl,T=T1),cpstate(2,fluid,Ph,H=h2),
                         cpstate(3,fluid,Ph,T=T3),cpstate(4,fluid,Pl,H=h4)])
    processes=proc([
        ["1→2","Compresión real adiabática","ηc","Compresor"],
        ["2→3","Condensación + subenfriamiento","P alta ≈ cte","Condensador"],
        ["3→4","Estrangulamiento","h = cte","Válvula"],
        ["4→1","Evaporación + sobrecalentamiento","P baja ≈ cte","Evaporador"],
    ])
    mets=[metric(r"COP_R",cop,"","Coeficiente de desempeño"),
          metric(r"q_L",ql,"kJ/kg","Efecto refrigerante"),metric(r"w_c",wc,"kJ/kg","Trabajo compresor"),
          metric(r"\eta_c",eta_c*100,"%", "Eficiencia isentrópica compresor")]
    return package(states,processes,mets,
        ["Introduce sobrecalentamiento, subenfriamiento y compresión no isentrópica."],
        {"TH":Tc,"TL":Te,"diagram":"r134a","schematic":"vcr"})

def heat_pump(Tevap_C=0.0,Tcond_C=45.0,eta_c=0.8,fluid="R134a"):
    r=vapor_real(Tevap_C,Tcond_C,5,5,eta_c,fluid)
    qh=next(m["value"] for m in r["metrics"] if m["symbol"]==r"q_L")+next(m["value"] for m in r["metrics"] if m["symbol"]==r"w_c")
    wc=next(m["value"] for m in r["metrics"] if m["symbol"]==r"w_c")
    r["metrics"].insert(0,metric(r"COP_{HP}",qh/wc,"","Coeficiente de desempeño como bomba de calor"))
    r["meta"]["schematic"]="heat_pump"
    return r

def gas_cycle(T1=278.15,T3=308.15,P1=100.0,rp=4.0):
    if rp<=1: raise ValueError("rp > 1.")
    n=(K_AIR-1)/K_AIR
    P2=P1*rp; T2=T1*rp**n; P3=P2; P4=P1; T4=T3/rp**n
    wc=CP_AIR*(T2-T1); wt=CP_AIR*(T3-T4); ql=CP_AIR*(T1-T4); w=wc-wt; cop=ql/w
    states=pd.DataFrame([air_state(1,T1,P1),air_state(2,T2,P2),air_state(3,T3,P3),air_state(4,T4,P4)])
    processes=proc([
        ["1→2","Compresión isentrópica","s=cte","Compresor"],
        ["2→3","Rechazo de calor","P alta=cte","Intercambiador"],
        ["3→4","Expansión isentrópica","s=cte","Turbina"],
        ["4→1","Absorción de calor","P baja=cte","Espacio frío"],
    ])
    mets=[metric(r"COP_R",cop,"","Coeficiente de desempeño"),metric(r"q_L",ql,"kJ/kg","Efecto refrigerante"),
          metric(r"w_{c}",wc,"kJ/kg","Compresor"),metric(r"w_t",wt,"kJ/kg","Turbina")]
    return package(states,processes,mets,["Brayton invertido ideal: el refrigerante permanece gaseoso."],
                   {"TH":T3,"TL":T4,"diagram":"gas","schematic":"gas_refrigeration"})

def cascade(Tevap_C=-40.0,Tinter_C=0.0,Tcond_C=35.0,fluid="R134a"):
    require()
    if not(Tevap_C<Tinter_C<Tcond_C): raise ValueError("Use Tevap < Tinter < Tcond.")
    low=vapor_ideal(Tevap_C,Tinter_C,fluid)
    high=vapor_ideal(Tinter_C,Tcond_C,fluid)
    qH_low=next(m["value"] for m in low["metrics"] if m["symbol"]==r"q_H")
    qL_high=next(m["value"] for m in high["metrics"] if m["symbol"]==r"q_L")
    ratio=qH_low/qL_high
    qL=next(m["value"] for m in low["metrics"] if m["symbol"]==r"q_L")
    wcL=next(m["value"] for m in low["metrics"] if m["symbol"]==r"w_c")
    wcH=next(m["value"] for m in high["metrics"] if m["symbol"]==r"w_c")
    cop=qL/(wcL+ratio*wcH)
    mets=[metric(r"COP_R",cop,"","COP global"),
          metric(r"\dot m_H/\dot m_L",ratio,"","Relación de flujos másicos"),
          metric(r"q_L",qL,"kJ/kg etapa baja","Efecto refrigerante de referencia")]
    processes=proc([
        ["Etapa baja","Evapora a baja temperatura","ciclo VCR ideal","Entrega calor al intercambiador cascada"],
        ["Intercambiador","QH,baja = QL,alta","balance de energía","Acopla los dos ciclos"],
        ["Etapa alta","Rechaza calor al ambiente","ciclo VCR ideal","Condensador final"],
    ])
    return package(pd.DataFrame(),processes,mets,
        ["Sistema ideal de dos etapas acopladas por un intercambiador en cascada."],
        {"TH":Tcond_C+273.15,"TL":Tevap_C+273.15,"diagram":"none","schematic":"cascade"})

def refrigerant_compare(Tevap_C=-10.0,Tcond_C=35.0,fluids=None):
    require()
    fluids=fluids or ["R134a","R1234yf","R290","R717","R32"]
    rows=[]
    for f in fluids:
        try:
            r=vapor_ideal(Tevap_C,Tcond_C,f)
            cop=next(m["value"] for m in r["metrics"] if m["symbol"]==r"COP_R")
            Pe=PropsSI("P","T",Tevap_C+273.15,"Q",1,f)/1000
            Pc=PropsSI("P","T",Tcond_C+273.15,"Q",0,f)/1000
            hfg=(PropsSI("H","T",Tevap_C+273.15,"Q",1,f)-PropsSI("H","T",Tevap_C+273.15,"Q",0,f))/1000
            rows.append({"Fluido":f,"COP ideal":cop,"P evap [kPa]":Pe,"P cond [kPa]":Pc,"hfg evap [kJ/kg]":hfg})
        except: pass
    return package(pd.DataFrame(rows),pd.DataFrame(),
        [metric(r"N_{fluidos}",len(rows),"","Fluidos comparados")],
        ["La selección real también depende de seguridad, ambiente, costo, compatibilidad y rango de operación."],
        {"diagram":"none","schematic":"refrigerator"})

def absorption_limit(Tsource=393.15,T0=298.15,TL=278.15):
    if not(Tsource>T0>TL>0): raise ValueError("Use Tfuente > T0 > TL.")
    eta=1-T0/Tsource; copr=TL/(T0-TL); cop=eta*copr
    mets=[metric(r"COP_{max}",cop,"","Límite reversible"),
          metric(r"\eta_{Carnot}",eta*100,"%", "Máquina térmica equivalente"),
          metric(r"COP_{R,Carnot}",copr,"","Refrigerador reversible equivalente")]
    return package(pd.DataFrame(),proc([
        ["Fuente→motor térmico","Conversión reversible límite","Tsource↔T0","Produce trabajo equivalente"],
        ["Trabajo→refrigerador","Carnot invertido","TL↔T0","Produce refrigeración"],
    ]),mets,["Referencia de segunda ley para absorción; no modela equilibrio NH3-H2O o H2O-LiBr."],
        {"TH":T0,"TL":TL,"diagram":"none","schematic":"absorption"})
