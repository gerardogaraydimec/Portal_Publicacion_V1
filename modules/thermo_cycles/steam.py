from __future__ import annotations
import pandas as pd
from .core import metric, package

try:
    from iapws import IAPWS97
except Exception:
    IAPWS97=None

def require():
    if IAPWS97 is None: raise RuntimeError("Falta instalar iapws.")

def ws(label,st):
    x=getattr(st,"x",None)
    try:
        x=float(x)
        if not 0<=x<=1: x=None
    except: x=None
    return {"Estado":str(label),"T [°C]":st.T-273.15,"P [kPa]":st.P*1000,
            "v [m³/kg]":st.v,"u [kJ/kg]":st.u,"h [kJ/kg]":st.h,
            "s [kJ/kg·K]":st.s,"x [-]":x}

def proc(rows):
    return pd.DataFrame(rows,columns=["Proceso","Descripción","Restricción / modelo","Equipo / lectura"])

def carnot_vapor(TH_C=300.0,TL_C=40.0):
    require()
    if TH_C<=TL_C: raise ValueError("TH debe ser mayor que TL.")
    st1=IAPWS97(T=TH_C+273.15,x=0); st2=IAPWS97(T=TH_C+273.15,x=1)
    lowg=IAPWS97(T=TL_C+273.15,x=1); lowf=IAPWS97(T=TL_C+273.15,x=0)
    st3=IAPWS97(P=lowg.P,s=st2.s); st4=IAPWS97(P=lowf.P,s=st1.s)
    qin=st2.h-st1.h; qout=st3.h-st4.h; w=qin-qout
    eta=1-(TL_C+273.15)/(TH_C+273.15)
    states=pd.DataFrame([ws(1,st1),ws(2,st2),ws(3,st3),ws(4,st4)])
    processes=proc([
        ["1→2","Adición reversible de calor","T = TH","Evaporación"],
        ["2→3","Expansión isentrópica","s = cte","Turbina ideal"],
        ["3→4","Rechazo reversible de calor","T = TL","Condensación parcial"],
        ["4→1","Compresión isentrópica bifásica","s = cte","Proceso impráctico"],
    ])
    mets=[metric(r"\eta_{th}",eta*100,"%", "Eficiencia de Carnot"),
          metric(r"q_{in}",qin,"kJ/kg","Calor entrante"),metric(r"w_{neto}",w,"kJ/kg","Trabajo neto")]
    return package(states,processes,mets,
        ["Su valor principal es mostrar por qué el Rankine reemplaza la compresión bifásica por bombeo de líquido."],
        {"TH":TH_C+273.15,"TL":TL_C+273.15,"diagram":"water","schematic":"heat_engine"})

def rankine(Pcond=10.0,Pboiler=8000.0,T3_C=480.0,eta_p=1.0,eta_t=1.0):
    require()
    if Pboiler<=Pcond or not(0<eta_p<=1 and 0<eta_t<=1): raise ValueError("Datos inválidos.")
    st1=IAPWS97(P=Pcond/1000,x=0)
    h2s=st1.h+st1.v*(Pboiler-Pcond); h2=st1.h+(h2s-st1.h)/eta_p
    st2=IAPWS97(P=Pboiler/1000,h=h2)
    st3=IAPWS97(P=Pboiler/1000,T=T3_C+273.15)
    st4s=IAPWS97(P=Pcond/1000,s=st3.s)
    h4=st3.h-eta_t*(st3.h-st4s.h); st4=IAPWS97(P=Pcond/1000,h=h4)
    wp=h2-st1.h; wt=st3.h-st4.h; qin=st3.h-h2; qout=st4.h-st1.h; w=wt-wp; eta=w/qin
    states=pd.DataFrame([ws(1,st1),ws(2,st2),ws(3,st3),ws(4,st4)])
    processes=proc([
        ["1→2","Bombeo","ηp","Bomba"],
        ["2→3","Adición de calor","P = cte","Caldera + sobrecalentador"],
        ["3→4","Expansión","ηt","Turbina"],
        ["4→1","Rechazo de calor","P = cte","Condensador"],
    ])
    mets=[metric(r"\eta_{th}",eta*100,"%", "Eficiencia térmica"),
          metric(r"w_t",wt,"kJ/kg","Trabajo turbina"),metric(r"w_p",wp,"kJ/kg","Trabajo bomba"),
          metric(r"w_{neto}",w,"kJ/kg","Trabajo neto"),metric(r"q_{in}",qin,"kJ/kg","Calor en caldera"),
          metric(r"x_4",getattr(st4,"x",None),"","Calidad de salida de turbina")]
    return package(states,processes,mets,
        ["ηp = ηt = 1 representa Rankine ideal; valores menores permiten estudiar Rankine real."],
        {"TH":st3.T,"TL":st1.T,"diagram":"water","schematic":"rankine"})

def reheat(Pcond=10.0,Pboiler=15000.0,T3_C=550.0,Preheat=3000.0,T5_C=550.0,eta_t=1.0,eta_p=1.0):
    require()
    if not(Pboiler>Preheat>Pcond>0): raise ValueError("Use Pcaldera > Precalentamiento > Pcond.")
    st1=IAPWS97(P=Pcond/1000,x=0)
    h2s=st1.h+st1.v*(Pboiler-Pcond); h2=st1.h+(h2s-st1.h)/eta_p; st2=IAPWS97(P=Pboiler/1000,h=h2)
    st3=IAPWS97(P=Pboiler/1000,T=T3_C+273.15)
    st4s=IAPWS97(P=Preheat/1000,s=st3.s); h4=st3.h-eta_t*(st3.h-st4s.h); st4=IAPWS97(P=Preheat/1000,h=h4)
    st5=IAPWS97(P=Preheat/1000,T=T5_C+273.15)
    st6s=IAPWS97(P=Pcond/1000,s=st5.s); h6=st5.h-eta_t*(st5.h-st6s.h); st6=IAPWS97(P=Pcond/1000,h=h6)
    wp=h2-st1.h; wt=(st3.h-st4.h)+(st5.h-st6.h); qin=(st3.h-st2.h)+(st5.h-st4.h); w=wt-wp; eta=w/qin
    states=pd.DataFrame([ws(1,st1),ws(2,st2),ws(3,st3),ws(4,st4),ws(5,st5),ws(6,st6)])
    processes=proc([
        ["1→2","Bombeo","ηp","Bomba"],["2→3","Calentamiento principal","P = cte","Caldera"],
        ["3→4","Expansión HP","ηt","Turbina HP"],["4→5","Recalentamiento","P = cte","Recalentador"],
        ["5→6","Expansión LP","ηt","Turbina LP"],["6→1","Condensación","P = cte","Condensador"],
    ])
    mets=[metric(r"\eta_{th}",eta*100,"%", "Eficiencia térmica"),metric(r"w_t",wt,"kJ/kg","Trabajo turbinas"),
          metric(r"w_{neto}",w,"kJ/kg","Trabajo neto"),metric(r"q_{in}",qin,"kJ/kg","Calor total"),
          metric(r"x_6",getattr(st6,"x",None),"","Calidad final")]
    return package(states,processes,mets,
        ["El recalentamiento busca mejorar la calidad durante la expansión final y elevar el trabajo de turbina."],
        {"TH":max(st3.T,st5.T),"TL":st1.T,"diagram":"water","schematic":"rankine_reheat"})

def regen_open(Pcond=10.0,Pfwh=800.0,Pboiler=8000.0,T5_C=480.0):
    require()
    if not(Pboiler>Pfwh>Pcond>0): raise ValueError("Use Pcaldera > PFWH > Pcond.")
    st1=IAPWS97(P=Pcond/1000,x=0)
    h2=st1.h+st1.v*(Pfwh-Pcond); st2=IAPWS97(P=Pfwh/1000,h=h2)
    st3=IAPWS97(P=Pfwh/1000,x=0)
    h4=st3.h+st3.v*(Pboiler-Pfwh); st4=IAPWS97(P=Pboiler/1000,h=h4)
    st5=IAPWS97(P=Pboiler/1000,T=T5_C+273.15)
    st6=IAPWS97(P=Pfwh/1000,s=st5.s); st7=IAPWS97(P=Pcond/1000,s=st6.s)
    y=(st3.h-h2)/(st6.h-h2); y=max(0,min(1,y))
    wt=(st5.h-st6.h)+(1-y)*(st6.h-st7.h)
    wp=(1-y)*(h2-st1.h)+(h4-st3.h)
    qin=st5.h-h4; w=wt-wp; eta=w/qin
    states=pd.DataFrame([ws(1,st1),ws(2,st2),ws(3,st3),ws(4,st4),ws(5,st5),ws(6,st6),ws(7,st7)])
    processes=proc([
        ["1→2","Bomba 1","flujo 1-y","Eleva condensado a PFWH"],
        ["2 + 6 → 3","Mezcla adiabática","masa + energía","Calentador abierto"],
        ["3→4","Bomba 2","flujo total","Eleva a Pcaldera"],
        ["4→5","Caldera","P = cte","Añade calor"],
        ["5→6","Turbina 1","s = cte","Extracción y"],
        ["6→7","Turbina 2","s = cte","Expansión restante"],
        ["7→1","Condensador","P = cte","Rechazo de calor"],
    ])
    mets=[metric(r"\eta_{th}",eta*100,"%", "Eficiencia térmica"),
          metric(r"y",y*100,"%", "Fracción de extracción"),
          metric(r"w_{neto}",w,"kJ/kg","Trabajo neto"),metric(r"q_{in}",qin,"kJ/kg","Calor en caldera")]
    return package(states,processes,mets,
        ["La extracción eleva la temperatura del agua de alimentación y la temperatura media de adición de calor."],
        {"TH":st5.T,"TL":st1.T,"diagram":"water","schematic":"rankine_regen"})

def cogeneration_simple(Pboiler=8000.0,Tin_C=480.0,Pprocess=500.0,Pcond=10.0,y=0.3):
    """Ciclo simple de cogeneración con extracción y condensación del resto."""
    require()
    if not(Pboiler>Pprocess>Pcond>0) or not(0<y<1): raise ValueError("Datos inválidos.")
    st1=IAPWS97(P=Pcond/1000,x=0)
    h2=st1.h+st1.v*(Pboiler-Pcond); st2=IAPWS97(P=Pboiler/1000,h=h2)
    st3=IAPWS97(P=Pboiler/1000,T=Tin_C+273.15)
    st4=IAPWS97(P=Pprocess/1000,s=st3.s)
    st5=IAPWS97(P=Pcond/1000,s=st4.s)
    process_liq=IAPWS97(P=Pprocess/1000,x=0)
    wt=(st3.h-st4.h)+(1-y)*(st4.h-st5.h)
    wp=h2-st1.h
    qin=st3.h-h2
    qproc=y*(st4.h-process_liq.h)
    w=wt-wp; util=(w+qproc)/qin
    states=pd.DataFrame([ws(1,st1),ws(2,st2),ws(3,st3),ws(4,st4),ws(5,st5)])
    processes=proc([
        ["1→2","Bomba","aprox. isentrópica","Bomba"],["2→3","Caldera","P=cte","Calor de combustible"],
        ["3→4","Expansión a presión de proceso","s=cte","Turbina"],
        ["4→proceso","Extracción y","calor útil","Proceso industrial"],
        ["4→5","Expansión remanente","s=cte","Turbina LP"],["5→1","Condensación","P=cte","Condensador"],
    ])
    mets=[metric(r"\eta_{util}",util*100,"%", "Factor de utilización"),
          metric(r"w_{neto}",w,"kJ/kg","Trabajo eléctrico específico"),
          metric(r"q_{proc}",qproc,"kJ/kg","Calor útil específico"),
          metric(r"y",y*100,"%", "Fracción extraída")]
    return package(states,processes,mets,
        ["Cogeneración: producir simultáneamente trabajo y calor útil; por eso la métrica central no es sólo ηth."],
        {"TH":st3.T,"TL":st1.T,"diagram":"water","schematic":"cogeneration"})

def combined_simple(rp=10.0,T1=300.0,T3=1400.0,Pcond=10.0,Pboiler=8000.0,Tsteam_C=480.0,hrsg_eff=0.85):
    """Acoplamiento didáctico: Brayton simple + Rankine; calor residual disponible alimenta Rankine."""
    from .gas import brayton
    gt=brayton(T1,100.0,rp,T3)
    stg=gt["states"]
    T4=float(stg.loc[stg["Estado"]=="4","T [K]"].iloc[0])
    qavail=max(0,CP_AIR*(T4-420.0))*hrsg_eff  # enfriamiento gases hasta 420 K
    st=rankine(Pcond,Pboiler,Tsteam_C,1.0,1.0)
    qsteam=next(m["value"] for m in st["metrics"] if m["symbol"]==r"q_{in}")
    wsteam=next(m["value"] for m in st["metrics"] if m["symbol"]==r"w_{neto}")
    ratio=0 if qsteam<=0 else qavail/qsteam
    wgt=next(m["value"] for m in gt["metrics"] if m["symbol"]==r"w_{neto}")
    qgt=CP_AIR*(T3-float(stg.loc[stg["Estado"]=="2","T [K]"].iloc[0]))
    wtot=wgt+ratio*wsteam
    eta=wtot/qgt
    metrics=[metric(r"\eta_{comb}",eta*100,"%", "Eficiencia térmica combinada"),
             metric(r"w_{GT}",wgt,"kJ/kg aire","Trabajo neto ciclo gas"),
             metric(r"\dot m_s/\dot m_a",ratio,"kg vapor/kg aire","Relación de flujos"),
             metric(r"w_{comb}",wtot,"kJ/kg aire","Trabajo combinado referido al aire")]
    processes=pd.DataFrame([
        ["Brayton","Turbina de gas","genera trabajo y gases calientes","Ciclo superior"],
        ["HRSG","Recuperación de calor","acopla ambos ciclos","Intercambiador"],
        ["Rankine","Turbina de vapor","usa calor residual","Ciclo inferior"],
    ],columns=["Bloque","Función","Relación","Lectura"])
    states=pd.DataFrame()
    return package(states,processes,metrics,
        ["Modelo pedagógico simplificado del acoplamiento gas-vapor; la HRSG se representa mediante una efectividad global."],
        {"TH":T3,"TL":T1,"diagram":"none","schematic":"combined"})
