from __future__ import annotations
import math
import pandas as pd
from .core import *

try:
    from CoolProp.CoolProp import PropsSI
except Exception:
    PropsSI=None

def _proc(rows):
    return pd.DataFrame(rows,columns=["Proceso","Descripción","Restricción / modelo","Lectura física"])

def carnot(TH=900.0,TL=300.0,P1=1000.0,rv=2.0,cp=CP_AIR,R=R_AIR,k=K_AIR):
    if TH<=TL or TL<=0 or P1<=0 or rv<=1: raise ValueError("Use TH > TL > 0, P1 > 0 y rv > 1.")
    v1=R*TH/P1; v2=rv*v1
    gamma=(TH/TL)**(1/(k-1))
    v3=v2*gamma; v4=v1*gamma
    P2=R*TH/v2; P3=R*TL/v3; P4=R*TL/v4
    qin=R*TH*math.log(rv); qout=R*TL*math.log(rv); w=qin-qout; eta=w/qin
    states=pd.DataFrame([air_state(1,TH,P1,v1,cp,R),air_state(2,TH,P2,v2,cp,R),
                         air_state(3,TL,P3,v3,cp,R),air_state(4,TL,P4,v4,cp,R)])
    proc=_proc([
        ["1→2","Expansión isotérmica reversible","T = TH","Entrada de calor y trabajo de expansión"],
        ["2→3","Expansión isentrópica","s = cte","Trabajo sin transferencia de calor"],
        ["3→4","Compresión isotérmica reversible","T = TL","Rechazo de calor"],
        ["4→1","Compresión isentrópica","s = cte","Trabajo de compresión"],
    ])
    metrics=[metric(r"\eta_{th}",eta*100,"%", "Eficiencia térmica"),
             metric(r"q_{in}",qin,"kJ/kg","Calor específico entrante"),
             metric(r"q_{out}",qout,"kJ/kg","Calor específico rechazado"),
             metric(r"w_{neto}",w,"kJ/kg","Trabajo específico neto")]
    return package(states,proc,metrics,
        ["Referencia reversible superior para una máquina térmica entre TH y TL.",
         "Los cuatro procesos son reversibles."],
        {"TH":TH,"TL":TL,"diagram":"gas","schematic":"heat_engine"})

def otto(T1=300.0,P1=100.0,r=8.0,qin=800.0,cp=CP_AIR,R=R_AIR,k=K_AIR):
    if min(T1,P1,qin)<=0 or r<=1: raise ValueError("Datos inválidos.")
    cv=cp-R
    T2=T1*r**(k-1); P2=P1*r**k
    T3=T2+qin/cv; P3=P2*T3/T2
    T4=T3/r**(k-1); P4=P1*T4/T1
    v1=R*T1/P1; v2=v1/r
    qout=cv*(T4-T1); w=qin-qout; eta=w/qin
    mep=w/(v1-v2)
    states=pd.DataFrame([air_state(1,T1,P1,v1,cp,R),air_state(2,T2,P2,v2,cp,R),
                         air_state(3,T3,P3,v2,cp,R),air_state(4,T4,P4,v1,cp,R)])
    proc=_proc([
        ["1→2","Compresión isentrópica","s = cte","Compresión ideal"],
        ["2→3","Adición de calor","v = cte","Idealización de combustión"],
        ["3→4","Expansión isentrópica","s = cte","Carrera de potencia ideal"],
        ["4→1","Rechazo de calor","v = cte","Cierre del ciclo"],
    ])
    metrics=[metric(r"\eta_{th}",eta*100,"%", "Eficiencia térmica"),
             metric(r"w_{neto}",w,"kJ/kg","Trabajo específico neto"),
             metric(r"q_{in}",qin,"kJ/kg","Calor específico entrante"),
             metric(r"q_{out}",qout,"kJ/kg","Calor específico rechazado"),
             metric(r"MEP",mep,"kPa","Presión media efectiva")]
    return package(states,proc,metrics,
        ["Modelo aire-estándar de una máquina de encendido por chispa.",
         "La relación de compresión es el parámetro geométrico central."],
        {"TH":T3,"TL":T1,"diagram":"gas","schematic":"reciprocating","cycle":"Otto"})

def diesel(T1=300.0,P1=100.0,r=18.0,rc=2.0,cp=CP_AIR,R=R_AIR,k=K_AIR):
    if min(T1,P1)<=0 or r<=rc or rc<=1: raise ValueError("Use r > rc > 1.")
    cv=cp-R
    T2=T1*r**(k-1); P2=P1*r**k
    T3=T2*rc; P3=P2
    T4=T3*(rc/r)**(k-1); P4=P1*T4/T1
    v1=R*T1/P1; v2=v1/r; v3=rc*v2
    qin=cp*(T3-T2); qout=cv*(T4-T1); w=qin-qout; eta=w/qin
    mep=w/(v1-v2)
    states=pd.DataFrame([air_state(1,T1,P1,v1,cp,R),air_state(2,T2,P2,v2,cp,R),
                         air_state(3,T3,P3,v3,cp,R),air_state(4,T4,P4,v1,cp,R)])
    proc=_proc([
        ["1→2","Compresión isentrópica","s = cte","Compresión"],
        ["2→3","Adición de calor","P = cte","Combustión idealizada"],
        ["3→4","Expansión isentrópica","s = cte","Carrera de potencia"],
        ["4→1","Rechazo de calor","v = cte","Cierre"],
    ])
    metrics=[metric(r"\eta_{th}",eta*100,"%", "Eficiencia térmica"),
             metric(r"w_{neto}",w,"kJ/kg","Trabajo específico neto"),
             metric(r"q_{in}",qin,"kJ/kg","Calor específico entrante"),
             metric(r"q_{out}",qout,"kJ/kg","Calor específico rechazado"),
             metric(r"MEP",mep,"kPa","Presión media efectiva")]
    return package(states,proc,metrics,
        ["Modelo aire-estándar de una máquina de encendido por compresión.",
         "La relación de corte rc describe la adición ideal de calor a presión constante."],
        {"TH":T3,"TL":T1,"diagram":"gas","schematic":"reciprocating","cycle":"Diesel"})

def dual(T1=300.0,P1=100.0,r=16.0,alpha=1.5,rc=1.5,cp=CP_AIR,R=R_AIR,k=K_AIR):
    if r<=rc or alpha<=1 or rc<=1: raise ValueError("Use r > rc > 1 y α > 1.")
    cv=cp-R
    T2=T1*r**(k-1); P2=P1*r**k
    T3=alpha*T2; P3=alpha*P2
    T4=rc*T3; P4=P3
    T5=T4*(rc/r)**(k-1); P5=P1*T5/T1
    v1=R*T1/P1; v2=v1/r; v3=v2; v4=rc*v3
    qin=cv*(T3-T2)+cp*(T4-T3); qout=cv*(T5-T1); w=qin-qout; eta=w/qin
    mep=w/(v1-v2)
    states=pd.DataFrame([air_state(1,T1,P1,v1,cp,R),air_state(2,T2,P2,v2,cp,R),
                         air_state(3,T3,P3,v3,cp,R),air_state(4,T4,P4,v4,cp,R),
                         air_state(5,T5,P5,v1,cp,R)])
    proc=_proc([
        ["1→2","Compresión isentrópica","s = cte","Compresión"],
        ["2→3","Adición de calor","v = cte","Primera fracción de calor"],
        ["3→4","Adición de calor","P = cte","Segunda fracción de calor"],
        ["4→5","Expansión isentrópica","s = cte","Expansión"],
        ["5→1","Rechazo de calor","v = cte","Cierre"],
    ])
    metrics=[metric(r"\eta_{th}",eta*100,"%", "Eficiencia térmica"),
             metric(r"w_{neto}",w,"kJ/kg","Trabajo específico neto"),
             metric(r"q_{in}",qin,"kJ/kg","Calor específico entrante"),
             metric(r"MEP",mep,"kPa","Presión media efectiva")]
    return package(states,proc,metrics,
        ["Ciclo dual: adición de calor parcialmente a volumen constante y parcialmente a presión constante."],
        {"TH":T4,"TL":T1,"diagram":"gas","schematic":"reciprocating","cycle":"Dual"})

def stirling(TL=300.0,TH=900.0,P1=1000.0,rv=5.0,R=R_AIR,cp=CP_AIR):
    if TH<=TL or rv<=1 or P1<=0: raise ValueError("Datos inválidos.")
    v1=R*TL/P1; v2=v1; v3=rv*v1; v4=v3
    P2=R*TH/v2; P3=R*TH/v3; P4=R*TL/v4
    qin=R*TH*math.log(rv); qout=R*TL*math.log(rv); w=qin-qout; eta=w/qin
    states=pd.DataFrame([air_state(1,TL,P1,v1,cp,R),air_state(2,TH,P2,v2,cp,R),
                         air_state(3,TH,P3,v3,cp,R),air_state(4,TL,P4,v4,cp,R)])
    proc=_proc([
        ["1→2","Calentamiento regenerativo","v = cte","Regenerador entrega calor"],
        ["2→3","Expansión isotérmica","T = TH","Calor externo entra"],
        ["3→4","Enfriamiento regenerativo","v = cte","Calor al regenerador"],
        ["4→1","Compresión isotérmica","T = TL","Calor externo sale"],
    ])
    metrics=[metric(r"\eta_{th}",eta*100,"%", "Eficiencia térmica ideal"),
             metric(r"w_{neto}",w,"kJ/kg","Trabajo específico neto"),
             metric(r"q_{in,ext}",qin,"kJ/kg","Calor externo entrante")]
    return package(states,proc,metrics,
        ["Con regeneración perfecta y reversibilidad, iguala la eficiencia de Carnot entre TH y TL."],
        {"TH":TH,"TL":TL,"diagram":"gas","schematic":"heat_engine"})

def ericsson(TL=300.0,TH=900.0,P_low=100.0,rp=5.0,R=R_AIR,cp=CP_AIR):
    if TH<=TL or rp<=1 or P_low<=0: raise ValueError("Datos inválidos.")
    P_high=P_low*rp
    s1=air_state(1,TH,P_high,cp=cp,R=R); s2=air_state(2,TH,P_low,cp=cp,R=R)
    s3=air_state(3,TL,P_low,cp=cp,R=R); s4=air_state(4,TL,P_high,cp=cp,R=R)
    qin=R*TH*math.log(rp); qout=R*TL*math.log(rp); w=qin-qout; eta=w/qin
    states=pd.DataFrame([s1,s2,s3,s4])
    proc=_proc([
        ["1→2","Expansión isotérmica","T = TH","Calor externo entra"],
        ["2→3","Enfriamiento regenerativo","P = cte","Calor al regenerador"],
        ["3→4","Compresión isotérmica","T = TL","Calor externo sale"],
        ["4→1","Calentamiento regenerativo","P = cte","Calor desde regenerador"],
    ])
    metrics=[metric(r"\eta_{th}",eta*100,"%", "Eficiencia térmica ideal"),
             metric(r"w_{neto}",w,"kJ/kg","Trabajo específico neto"),
             metric(r"q_{in,ext}",qin,"kJ/kg","Calor externo entrante")]
    return package(states,proc,metrics,
        ["Con regeneración perfecta y reversibilidad, iguala Carnot."],
        {"TH":TH,"TL":TL,"diagram":"gas","schematic":"heat_engine"})

def brayton(T1=300.0,P1=100.0,rp=10.0,T3=1400.0,eta_c=1.0,eta_t=1.0,cp=CP_AIR,R=R_AIR,k=K_AIR):
    if rp<=1 or T3<=T1 or not(0<eta_c<=1) or not(0<eta_t<=1): raise ValueError("Datos inválidos.")
    n=(k-1)/k
    P2=P1*rp; T2s=T1*rp**n; T2=T1+(T2s-T1)/eta_c
    P3=P2; P4=P1; T4s=T3/rp**n; T4=T3-eta_t*(T3-T4s)
    wc=cp*(T2-T1); wt=cp*(T3-T4); qin=cp*(T3-T2); qout=cp*(T4-T1); w=wt-wc
    eta=w/qin
    states=pd.DataFrame([air_state(1,T1,P1,cp=cp,R=R),air_state(2,T2,P2,cp=cp,R=R),
                         air_state(3,T3,P3,cp=cp,R=R),air_state(4,T4,P4,cp=cp,R=R)])
    proc=_proc([
        ["1→2","Compresión","ηc aplicada","Compresor"],
        ["2→3","Adición de calor","P = cte","Calentador / combustión idealizada"],
        ["3→4","Expansión","ηt aplicada","Turbina"],
        ["4→1","Rechazo de calor","P = cte","Cierre aire-estándar"],
    ])
    metrics=[metric(r"\eta_{th}",eta*100,"%", "Eficiencia térmica"),
             metric(r"w_c",wc,"kJ/kg","Trabajo específico del compresor"),
             metric(r"w_t",wt,"kJ/kg","Trabajo específico de turbina"),
             metric(r"w_{neto}",w,"kJ/kg","Trabajo específico neto"),
             metric(r"BWR",wc/wt,"","Back-work ratio")]
    return package(states,proc,metrics,
        ["ηc = ηt = 1 reproduce Brayton ideal; valores menores permiten estudiar desviación real."],
        {"TH":T3,"TL":T1,"diagram":"gas","schematic":"brayton"})

def brayton_regen(T1=300.0,P1=100.0,rp=8.0,T3=1400.0,eps=0.75,eta_c=1.0,eta_t=1.0):
    b=brayton(T1,P1,rp,T3,eta_c,eta_t)
    st=b["states"]
    T2=float(st.loc[st["Estado"]=="2","T [K]"].iloc[0]); T4=float(st.loc[st["Estado"]=="4","T [K]"].iloc[0])
    e=max(0,min(1,eps)) if T4>T2 else 0.0
    T2r=T2+e*(T4-T2); T4r=T4-(T2r-T2)
    wc=CP_AIR*(T2-T1); wt=CP_AIR*(T3-T4); qin=CP_AIR*(T3-T2r); qout=CP_AIR*(T4r-T1)
    eta=(wt-wc)/qin
    P2=P1*rp
    states=pd.DataFrame([
        air_state(1,T1,P1),air_state(2,T2,P2),air_state("2r",T2r,P2),
        air_state(3,T3,P2),air_state(4,T4,P1),air_state("4r",T4r,P1)
    ])
    proc=_proc([
        ["1→2","Compresión","ηc","Compresor"],
        ["2→2r","Regeneración","ε","Recupera calor del escape"],
        ["2r→3","Adición externa de calor","P = cte","Menor qin externo"],
        ["3→4","Expansión","ηt","Turbina"],
        ["4→4r","Regeneración","ε","Entrega calor"],
        ["4r→1","Rechazo","P = cte","Cierre"],
    ])
    metrics=[metric(r"\eta_{th}",eta*100,"%", "Eficiencia térmica"),
             metric(r"\varepsilon_{reg}",e*100,"%", "Efectividad del regenerador"),
             metric(r"w_{neto}",wt-wc,"kJ/kg","Trabajo específico neto"),
             metric(r"q_{in,ext}",qin,"kJ/kg","Calor externo requerido")]
    return package(states,proc,metrics,
        ["La regeneración reduce el calor externo cuando T4 > T2."],
        {"TH":T3,"TL":T1,"diagram":"gas","schematic":"brayton_regen"})

def brayton_ic_rr(T1=300.0,P1=100.0,rp=12.0,Tmax=1400.0,eps=0.75,eta_c=1.0,eta_t=1.0):
    if rp<=1 or Tmax<=T1: raise ValueError("Datos inválidos.")
    n=(K_AIR-1)/K_AIR; rs=math.sqrt(rp)
    # etapa compresor 1
    P2=P1*rs; T2s=T1*rs**n; T2=T1+(T2s-T1)/eta_c
    # intercooling perfecto
    T3=T1; P3=P2
    P4=P1*rp; T4s=T3*rs**n; T4=T3+(T4s-T3)/eta_c
    # turbina etapa 1
    P5=P4; T5=Tmax
    P6=P2; T6s=T5/rs**n; T6=T5-eta_t*(T5-T6s)
    # reheat
    P7=P6; T7=Tmax
    P8=P1; T8s=T7/rs**n; T8=T7-eta_t*(T7-T8s)
    e=max(0,min(1,eps)) if T8>T4 else 0.0
    T4r=T4+e*(T8-T4); T8r=T8-(T4r-T4)
    wc=CP_AIR*((T2-T1)+(T4-T3))
    wt=CP_AIR*((T5-T6)+(T7-T8))
    qin=CP_AIR*((T5-T4r)+(T7-T6))
    w=wt-wc; eta=w/qin
    states=pd.DataFrame([
        air_state(1,T1,P1),air_state(2,T2,P2),air_state(3,T3,P3),air_state(4,T4,P4),
        air_state("4r",T4r,P4),air_state(5,T5,P5),air_state(6,T6,P6),
        air_state(7,T7,P7),air_state(8,T8,P8),air_state("8r",T8r,P8)])
    proc=_proc([
        ["1→2","Compresión etapa 1","ηc","Compresor 1"],
        ["2→3","Interenfriamiento","P ≈ cte","T3 = T1 idealizado"],
        ["3→4","Compresión etapa 2","ηc","Compresor 2"],
        ["4→4r","Regeneración","ε","Precalentamiento"],
        ["4r→5","Adición de calor","P = cte","Calentamiento"],
        ["5→6","Expansión etapa 1","ηt","Turbina 1"],
        ["6→7","Recalentamiento","P = cte","Restablece Tmax"],
        ["7→8","Expansión etapa 2","ηt","Turbina 2"],
        ["8→8r","Regeneración","ε","Recuperación"],
    ])
    metrics=[metric(r"\eta_{th}",eta*100,"%", "Eficiencia térmica"),
             metric(r"w_c",wc,"kJ/kg","Trabajo total compresores"),
             metric(r"w_t",wt,"kJ/kg","Trabajo total turbinas"),
             metric(r"w_{neto}",w,"kJ/kg","Trabajo neto"),
             metric(r"\varepsilon_{reg}",e*100,"%", "Efectividad")]
    return package(states,proc,metrics,
        ["Se adopta división equitativa de relaciones de presión, interenfriamiento perfecto y recalentamiento hasta Tmax."],
        {"TH":Tmax,"TL":T1,"diagram":"gas","schematic":"brayton_advanced"})

def turbojet_ideal(T0=288.15,P0=101.325,M0=0.0,rp=10.0,Tt4=1400.0,eta_c=1.0,eta_t=1.0,eta_n=1.0):
    """Modelo turbojet simple, cp y gamma constantes, nozzle expandido idealmente a P0."""
    if rp<=1 or Tt4<=T0 or not(0<eta_c<=1 and 0<eta_t<=1 and 0<eta_n<=1):
        raise ValueError("Datos inválidos.")
    gamma=K_AIR; Rj=R_AIR*1000; cpj=CP_AIR*1000
    a0=math.sqrt(gamma*Rj*T0); V0=M0*a0
    Tt0=T0*(1+(gamma-1)/2*M0**2)
    Pt0=P0*(1+(gamma-1)/2*M0**2)**(gamma/(gamma-1))
    Pt2=Pt0; Tt2=Tt0
    Pt3=Pt2*rp
    Tt3s=Tt2*rp**((gamma-1)/gamma)
    Tt3=Tt2+(Tt3s-Tt2)/eta_c
    wc=cpj*(Tt3-Tt2)
    # turbine work balances compressor
    Tt5=Tt4-wc/cpj
    Tt5s=Tt4-(Tt4-Tt5)/eta_t
    Pt5=Pt3*(Tt5s/Tt4)**(gamma/(gamma-1))
    if Pt5<=P0:
        Ve=0.0
    else:
        Te_is=Tt5*(P0/Pt5)**((gamma-1)/gamma)
        Ve=math.sqrt(max(0,2*eta_n*cpj*(Tt5-Te_is)))
    specific_thrust=Ve-V0
    f=cpj*(Tt4-Tt3)/43e6  # crude fuel-air ratio using LHV 43 MJ/kg
    prop_eff = 0 if Ve<=0 or V0<=0 else 2*V0/(Ve+V0)
    states=pd.DataFrame([
        {"Estado":"0","T [K]":T0,"P [kPa]":P0,"V [m/s]":V0},
        {"Estado":"2","T [K]":Tt2,"P [kPa]":Pt2,"V [m/s]":None},
        {"Estado":"3","T [K]":Tt3,"P [kPa]":Pt3,"V [m/s]":None},
        {"Estado":"4","T [K]":Tt4,"P [kPa]":Pt3,"V [m/s]":None},
        {"Estado":"5","T [K]":Tt5,"P [kPa]":Pt5,"V [m/s]":None},
        {"Estado":"e","T [K]":None,"P [kPa]":P0,"V [m/s]":Ve},
    ])
    proc=_proc([
        ["0→2","Difusor","adiabático ideal","Convierte energía cinética en presión total"],
        ["2→3","Compresión","ηc","Compresor"],
        ["3→4","Adición de calor","Ptotal ≈ cte","Combustor idealizado"],
        ["4→5","Expansión","trabajo turbina = trabajo compresor","Turbina"],
        ["5→e","Expansión en tobera","ηn","Aceleración del chorro"],
    ])
    metrics=[metric(r"F/\dot m_a",specific_thrust,"N/(kg/s)","Empuje específico aproximado"),
             metric(r"V_e",Ve,"m/s","Velocidad de salida"),
             metric(r"f",f,"kg combustible/kg aire","Relación combustible-aire aproximada"),
             metric(r"\eta_p",prop_eff*100,"%" if prop_eff else "%","Eficiencia propulsiva aproximada")]
    return package(states,proc,metrics,
        ["Modelo pedagógico simple sin pérdidas de presión en cámara ni postcombustión.",
         "El empuje específico aproxima F/ṁa ≈ Ve - V0 para tobera perfectamente expandida."],
        {"TH":Tt4,"TL":T0,"diagram":"none","schematic":"turbojet"})
