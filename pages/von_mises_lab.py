from __future__ import annotations
from pathlib import Path
import math
import numpy as np
import streamlit as st
from modules.ui_brand import render_app_header

from modules.von_mises_lab import (
    stress_tensor,
    principal_stresses,
    hydrostatic_tensor,
    deviatoric_tensor,
    invariants,
    von_mises_from_tensor,
    von_mises_plane_stress,
    principal_stresses_plane,
    principal_angle_plane,
    mohr_circle_2d,
    tresca_equivalent_from_principal,
    safety_factor,
    classify_yield_state,
    add_hydrostatic_shift,
    axial_bar_figure,
    uniaxial_flow_figure,
    yield_axis_figure,
    stress_element_2d_figure,
    principal_element_2d_figure,
    mohr_circle_figure,
    yield_plane_vm_figure,
    von_mises_cylinder_figure,
    pi_plane_figure,
    equations_1d,
    equations_2d,
    equations_3d,
)

ROOT=Path(__file__).resolve().parents[1]

st.markdown("""
<style>
.block-container{padding-top:1rem;padding-bottom:2rem;max-width:1750px;}
.brand-kicker{color:#db7810;font-weight:800;letter-spacing:.06em;font-size:.88rem;text-transform:uppercase;}
.hero{border-left:5px solid #f28e1c;background:#fff8ef;border-radius:9px;padding:11px 15px;margin:.5rem 0 1rem 0;}
.topic{border-left:4px solid #f28e1c;background:#fffaf4;border-radius:8px;padding:9px 13px;margin:.4rem 0 .7rem 0;}
.value-big{font-size:1.30rem;font-weight:800;text-align:center;margin-top:-.25rem;}
.value-caption{font-size:.82rem;color:#6b7280;text-align:center;min-height:2.1rem;}
</style>
""",unsafe_allow_html=True)


def unit_factor(unit:str)->float:
    return {"MPa":1.0,"ksi":6.894757293168361,"GPa":1000.0}[unit]


def from_mpa(value:float,unit:str)->float:
    return value/unit_factor(unit)


def fmt(x:float)->str:
    if math.isinf(x):
        return "∞"
    a=abs(x)
    if a>=1e5 or (0<a<1e-4):
        return f"{x:.3e}"
    return f"{x:.5g}"


def math_card(symbol:str,value:str,caption:str):
    with st.container(border=True):
        st.latex(symbol)
        st.markdown(f"<div class='value-big'>{value}</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='value-caption'>{caption}</div>",unsafe_allow_html=True)


def state_banner(state:str):
    if "seguro" in state.lower():
        st.success(state)
    elif "inicio" in state.lower():
        st.warning(state)
    else:
        st.error(state)


def matrix_latex(a,unit):
    conv=np.asarray(a,dtype=float)/unit_factor(unit)
    return (
        r"\begin{bmatrix}"
        + rf"{conv[0,0]:.5g}&{conv[0,1]:.5g}&{conv[0,2]:.5g}\\"
        + rf"{conv[1,0]:.5g}&{conv[1,1]:.5g}&{conv[1,2]:.5g}\\"
        + rf"{conv[2,0]:.5g}&{conv[2,1]:.5g}&{conv[2,2]:.5g}"
        + r"\end{bmatrix}"
    )


# Header
render_app_header(
    title="Von Mises Lab · Fluencia bajo esfuerzos combinados",
    subtitle="Del ensayo uniaxial al plano de fluencia y al espacio tridimensional de esfuerzos.",
    section="ELEMENTOS DE MÁQUINAS",
    logo_width=190,
)

st.markdown(
    '<div class="hero"><b>Idea central:</b> un ensayo uniaxial entrega el límite de fluencia '
    'del material. Von Mises transforma un estado multiaxial en un esfuerzo equivalente '
    'que puede compararse con ese mismo límite.</div>',
    unsafe_allow_html=True,
)

main_tabs=st.tabs([
    "Ruta de aprendizaje",
    "1D · Estado uniaxial",
    "2D · Esfuerzo plano",
    "3D · Espacio de esfuerzos",
    "Criterios de falla",
    "Guía de análisis",
])

# =============================================================================
# Learning route
# =============================================================================
with main_tabs[0]:
    st.markdown("## Cómo leer la herramienta")
    st.markdown(
        '<div class="topic"><b>1D</b> fija el significado físico de <b>S<sub>y</sub></b>. '
        '<b>2D</b> transforma el estado conocido a esfuerzos principales y ubica el punto en un '
        'plano de fluencia. <b>3D</b> muestra que Von Mises depende de la parte desviadora del tensor.</div>',
        unsafe_allow_html=True,
    )
    c1,c2,c3=st.columns(3)
    with c1:
        math_card(r"\sigma_{VM}=|\sigma_x|","1D","Ensayo uniaxial y calibración del criterio")
    with c2:
        math_card(r"\sigma_{VM}=\sqrt{\sigma_1^2-\sigma_1\sigma_2+\sigma_2^2}","2D","Plano principal y frontera de fluencia")
    with c3:
        math_card(r"\sigma_{VM}=\sqrt{3J_2}","3D","Parte desviadora y cilindro de Von Mises")

    st.markdown("### Los tres planos que se usan en 2D")
    p1,p2,p3=st.columns(3)
    with p1:
        st.markdown("**Plano físico x–y**")
        st.caption("Aquí se conocen σx, σy y τxy.")
    with p2:
        st.markdown("**Planos principales**")
        st.caption("El elemento rota hasta que τ = 0 y aparecen σ1 y σ2.")
    with p3:
        st.markdown("**Plano de falla σ1–σ2**")
        st.caption("Aquí se compara el punto de operación con Von Mises y Tresca.")

# =============================================================================
# 1D
# =============================================================================
with main_tabs[1]:
    st.markdown("## 1D · Estado uniaxial")
    st.markdown(
        '<div class="topic"><b>Qué representa:</b> una barra sometida a una única carga axial. '
        'El plano de interés es una sección normal al eje de la barra, sobre la que actúa σx.</div>',
        unsafe_allow_html=True,
    )

    left,right=st.columns([1.08,1.0],vertical_alignment="top")
    with left:
        with st.container(border=True):
            st.markdown("### Condiciones del caso")
            u1=st.selectbox("Unidad de esfuerzo",["MPa","ksi","GPa"],key="u1")
            Sy1_user=st.number_input(
                f"Límite de fluencia Sy [{u1}]",
                min_value=1e-12,
                value={"MPa":250.0,"ksi":36.0,"GPa":0.25}[u1],
                format="%.6g",key="sy1"
            )
            Sy1=Sy1_user*unit_factor(u1)

            input_mode=st.radio(
                "Forma de definir la carga",
                ["Esfuerzo σx","Fuerza F y área A","Nivel normalizado σx/Sy"],
                horizontal=True,key="mode1"
            )
            Fshown=None; Ashown=None
            if input_mode=="Esfuerzo σx":
                sx1_user=st.number_input(
                    f"σx [{u1}]",
                    value={"MPa":120.0,"ksi":17.4,"GPa":0.12}[u1],
                    format="%.6g",key="sx1"
                )
                sx1=sx1_user*unit_factor(u1)
            elif input_mode=="Fuerza F y área A":
                Fshown=st.number_input("Fuerza axial F [kN]",value=60.0,format="%.6g",key="F1")
                Ashown=st.number_input("Área resistente A [mm²]",min_value=1e-9,value=500.0,format="%.6g",key="A1")
                sx1=Fshown*1000.0/Ashown  # N/mm2 = MPa
                if u1!="MPa":
                    st.caption(f"σx = {fmt(from_mpa(sx1,u1))} {u1}")
            else:
                ratio=st.slider("σx / Sy",-2.0,2.0,0.50,0.01,key="ratio1")
                sx1=ratio*Sy1
                st.caption(f"σx = {fmt(from_mpa(sx1,u1))} {u1}")

    t1=stress_tensor(sigma_x=sx1)
    p1=principal_stresses(t1)
    inv1=invariants(t1)
    h1=hydrostatic_tensor(t1)
    d1=deviatoric_tensor(t1)
    vm1=von_mises_from_tensor(t1)
    n1=safety_factor(Sy1,vm1)
    s1=classify_yield_state(Sy1,vm1)

    with right:
        st.markdown("### Resultado del criterio")
        c1,c2,c3=st.columns(3)
        with c1:
            math_card(r"\sigma_{VM}",f"{fmt(from_mpa(vm1,u1))} {u1}","Esfuerzo equivalente")
        with c2:
            math_card(r"n=\frac{S_y}{\sigma_{VM}}",fmt(n1),"Factor de seguridad")
        with c3:
            math_card(r"\sigma_m",f"{fmt(from_mpa(np.trace(t1)/3,u1))} {u1}","Esfuerzo medio")
        state_banner(s1)

    subt=st.tabs(["Modelo físico","Desarrollo paso a paso","Gráficos","Descomposición","Interpretación"])
    with subt[0]:
        a,b=st.columns([1.15,1.0])
        with a:
            st.plotly_chart(
                axial_bar_figure(from_mpa(sx1,u1),from_mpa(Sy1,u1),Fshown,Ashown),
                use_container_width=True,config={"displaylogo":False}
            )
        with b:
            st.markdown("### Qué está ocurriendo")
            st.markdown(
                "La barra transmite una carga axial. Si se realiza un corte normal al eje $x$, "
                "la resultante interna se distribuye sobre el área resistente y genera el esfuerzo normal:"
            )
            st.latex(r"\sigma_x=\frac{F}{A}")
            st.markdown(
                "En un estado verdaderamente uniaxial no aparecen otros esfuerzos normales ni cortantes. "
                "Por eso el esfuerzo equivalente de Von Mises se reduce a la magnitud de σₓ."
            )
            st.latex(r"\sigma_{VM}=|\sigma_x|")

    with subt[1]:
        equations_1d()
        st.markdown("### Sustitución del caso actual")
        if input_mode=="Fuerza F y área A":
            st.latex(
                rf"\sigma_x=\frac{{{Fshown:.5g}\times10^3}}{{{Ashown:.5g}}}"
                rf"={sx1:.5g}\;\mathrm{{MPa}}"
            )
        st.latex(rf"\sigma_{{VM}}=|{from_mpa(sx1,u1):.5g}|={from_mpa(vm1,u1):.5g}\;{u1}")
        if vm1>0:
            st.latex(rf"n=\frac{{{from_mpa(Sy1,u1):.5g}}}{{{from_mpa(vm1,u1):.5g}}}={n1:.5g}")
        else:
            st.latex(r"n\rightarrow\infty\qquad(\sigma_{VM}=0)")

    with subt[2]:
        a,b=st.columns([1.15,1.0])
        with a:
            st.plotly_chart(uniaxial_flow_figure(from_mpa(sx1,u1),from_mpa(Sy1,u1)),
                            use_container_width=True,config={"displaylogo":False})
        with b:
            st.plotly_chart(yield_axis_figure(from_mpa(sx1,u1),from_mpa(Sy1,u1)),
                            use_container_width=True,config={"displaylogo":False})

    with subt[3]:
        st.markdown("### Del estado uniaxial al lenguaje tensorial")
        a,b=st.columns(2)
        with a:
            st.markdown("**Tensor de esfuerzos**")
            st.latex(r"\boldsymbol{\sigma}="+matrix_latex(t1,u1))
            st.markdown("**Parte hidrostática**")
            st.latex(r"\boldsymbol{\sigma}_h="+matrix_latex(h1,u1))
        with b:
            st.markdown("**Parte desviadora**")
            st.latex(r"\mathbf{s}="+matrix_latex(d1,u1))
            st.latex(rf"J_2={inv1['J2']/(unit_factor(u1)**2):.5g}\;{u1}^2")
            st.latex(
                rf"\sigma_1={from_mpa(p1[0],u1):.5g},\quad"
                rf"\sigma_2={from_mpa(p1[1],u1):.5g},\quad"
                rf"\sigma_3={from_mpa(p1[2],u1):.5g}\;{u1}"
            )

    with subt[4]:
        st.markdown(
            "**Lectura clave:** el caso 1D no intenta reemplazar el ensayo de tracción; lo utiliza como referencia. "
            "El valor Sᵧ obtenido del material se convierte en el umbral con el que posteriormente se comparará "
            "cualquier estado multiaxial mediante σVM."
        )

# =============================================================================
# 2D
# =============================================================================
with main_tabs[2]:
    st.markdown("## 2D · Estado general de esfuerzo plano")
    st.markdown(
        '<div class="topic"><b>Ruta de trabajo:</b> plano físico x–y → planos principales → '
        'círculo de Mohr → plano de fluencia σ1–σ2 → verificación de diseño.</div>',
        unsafe_allow_html=True,
    )

    left,right=st.columns([1.08,1.0],vertical_alignment="top")
    with left:
        with st.container(border=True):
            st.markdown("### Condiciones del estado plano")
            u2=st.selectbox("Unidad de esfuerzo",["MPa","ksi","GPa"],key="u2")
            Sy2_user=st.number_input(
                f"Límite de fluencia Sy [{u2}]",
                min_value=1e-12,
                value={"MPa":250.0,"ksi":36.0,"GPa":0.25}[u2],
                format="%.6g",key="sy2"
            )
            sx2_user=st.number_input(f"σx [{u2}]",value={"MPa":120.0,"ksi":17.4,"GPa":0.12}[u2],format="%.6g",key="sx2")
            sy2_user=st.number_input(f"σy [{u2}]",value={"MPa":40.0,"ksi":5.8,"GPa":0.04}[u2],format="%.6g",key="sy2n")
            txy2_user=st.number_input(f"τxy [{u2}]",value={"MPa":35.0,"ksi":5.1,"GPa":0.035}[u2],format="%.6g",key="txy2")
            show_tresca=st.toggle("Superponer criterio de Tresca",value=True,key="show_tresca")

    Sy2=Sy2_user*unit_factor(u2)
    sx2=sx2_user*unit_factor(u2); sy2=sy2_user*unit_factor(u2); txy2=txy2_user*unit_factor(u2)
    sp1,sp2=principal_stresses_plane(sx2,sy2,txy2)
    theta_p=principal_angle_plane(sx2,sy2,txy2)
    theta_deg=np.degrees(theta_p)
    mohr=mohr_circle_2d(sx2,sy2,txy2)
    vm2=von_mises_plane_stress(sx2,sy2,txy2)
    tr2=tresca_equivalent_from_principal(sp1,sp2,0.0)
    nvm2=safety_factor(Sy2,vm2)
    ntr2=safety_factor(Sy2,tr2)
    state2=classify_yield_state(Sy2,vm2)

    with right:
        st.markdown("### Resultados principales")
        r1,r2,r3,r4=st.columns(4)
        with r1:
            math_card(r"\sigma_1",f"{fmt(from_mpa(sp1,u2))} {u2}","Principal mayor")
        with r2:
            math_card(r"\sigma_2",f"{fmt(from_mpa(sp2,u2))} {u2}","Principal menor")
        with r3:
            math_card(r"\sigma_{VM}",f"{fmt(from_mpa(vm2,u2))} {u2}","Von Mises")
        with r4:
            math_card(r"n_{VM}",fmt(nvm2),"Factor de seguridad")
        state_banner(state2)

    subt=st.tabs([
        "Planos de trabajo",
        "Desarrollo matemático",
        "Círculo de Mohr",
        "Plano de fluencia",
        "Von Mises vs Tresca",
        "Interpretación",
    ])

    with subt[0]:
        a,b=st.columns(2)
        with a:
            st.plotly_chart(
                stress_element_2d_figure(from_mpa(sx2,u2),from_mpa(sy2,u2),from_mpa(txy2,u2)),
                use_container_width=True,config={"displaylogo":False}
            )
            st.caption("Plano físico x–y: aquí se introducen las componentes conocidas del estado.")
        with b:
            st.plotly_chart(
                principal_element_2d_figure(from_mpa(sp1,u2),from_mpa(sp2,u2),theta_deg),
                use_container_width=True,config={"displaylogo":False}
            )
            st.caption("Planos principales: el elemento se orienta de manera que el esfuerzo cortante desaparece.")

        st.markdown("### Cómo se conectan estos planos")
        st.latex(r"(\sigma_x,\sigma_y,\tau_{xy})\xrightarrow{\;\theta_p\;}(\sigma_1,\sigma_2,\tau=0)")
        st.markdown(
            "El **plano de fluencia** no representa una nueva cara física del elemento. "
            "Es un espacio gráfico de diseño donde cada estado se representa por el punto (σ₁, σ₂)."
        )

    with subt[1]:
        a,b=st.columns([1,1.05])
        with a:
            equations_2d()
        with b:
            st.markdown("### Sustitución del caso actual")
            st.latex(
                rf"\sigma_{{avg}}=\frac{{{from_mpa(sx2,u2):.5g}+{from_mpa(sy2,u2):.5g}}}{{2}}"
                rf"={from_mpa(mohr['center'],u2):.5g}\;{u2}"
            )
            st.latex(
                rf"R=\sqrt{{\left(\frac{{{from_mpa(sx2,u2):.5g}-{from_mpa(sy2,u2):.5g}}}{{2}}\right)^2"
                rf"+({from_mpa(txy2,u2):.5g})^2}}={from_mpa(mohr['radius'],u2):.5g}\;{u2}"
            )
            st.latex(rf"\theta_p={theta_deg:.5g}^\circ")
            st.latex(rf"\sigma_1={from_mpa(sp1,u2):.5g}\;{u2}")
            st.latex(rf"\sigma_2={from_mpa(sp2,u2):.5g}\;{u2}")
            st.latex(rf"\sigma_{{VM}}={from_mpa(vm2,u2):.5g}\;{u2}")
            st.latex(rf"n_{{VM}}={nvm2:.5g}")

    with subt[2]:
        st.plotly_chart(
            mohr_circle_figure(
                from_mpa(sx2,u2),from_mpa(sy2,u2),from_mpa(txy2,u2),
                from_mpa(mohr["center"],u2),from_mpa(mohr["radius"],u2),
                from_mpa(sp1,u2),from_mpa(sp2,u2)
            ),
            use_container_width=True,config={"displaylogo":False}
        )
        st.markdown(
            "El círculo de Mohr responde a una pregunta de **transformación**: "
            "¿qué combinación de esfuerzo normal y cortante actúa sobre un plano de determinada orientación?"
        )

    with subt[3]:
        st.plotly_chart(
            yield_plane_vm_figure(
                from_mpa(sp1,u2),from_mpa(sp2,u2),from_mpa(Sy2,u2),
                nvm2,show_tresca
            ),
            use_container_width=True,config={"displaylogo":False}
        )
        st.markdown(
            "La línea radial desde el origen representa un **camino de carga proporcional**. "
            "La intersección con la frontera de Von Mises permite interpretar geométricamente el factor de seguridad."
        )
        st.latex(r"n_{VM}=\frac{\text{distancia hasta la frontera}}{\text{distancia hasta el estado actual}}")

    with subt[4]:
        a,b=st.columns(2)
        with a:
            math_card(r"\sigma_{VM}",f"{fmt(from_mpa(vm2,u2))} {u2}","Energía de distorsión")
            math_card(r"n_{VM}",fmt(nvm2),"Factor de seguridad Von Mises")
        with b:
            math_card(r"\sigma_{Tresca}",f"{fmt(from_mpa(tr2,u2))} {u2}","Máxima diferencia principal")
            math_card(r"n_{Tresca}",fmt(ntr2),"Factor de seguridad Tresca")
        st.markdown(
            "Para materiales dúctiles bajo carga estática, ambos criterios buscan predecir el **inicio de fluencia**. "
            "Tresca se basa en el máximo esfuerzo cortante; Von Mises se basa en la energía de distorsión."
        )

    with subt[5]:
        st.markdown("### Lectura integrada")
        st.markdown(
            "1. Se conoce el estado en el sistema x–y.\n"
            "2. Se obtienen los esfuerzos principales y la orientación principal.\n"
            "3. Mohr ayuda a visualizar la transformación.\n"
            "4. El punto (σ₁, σ₂) se lleva al plano de falla.\n"
            "5. Von Mises reduce la combinación completa a un único esfuerzo equivalente.\n"
            "6. Ese valor se compara con Sᵧ mediante el factor de seguridad."
        )

# =============================================================================
# 3D
# =============================================================================
with main_tabs[3]:
    st.markdown("## 3D · Estado general de esfuerzos")
    st.markdown(
        '<div class="topic"><b>Idea geométrica:</b> la parte hidrostática desplaza el estado '
        'a lo largo del eje σ1 = σ2 = σ3. La parte desviadora determina la distancia radial '
        'respecto de ese eje y, por lo tanto, la aproximación a la superficie de fluencia.</div>',
        unsafe_allow_html=True,
    )

    left,right=st.columns([1.15,1.0],vertical_alignment="top")
    with left:
        with st.container(border=True):
            st.markdown("### Componentes del tensor")
            u3=st.selectbox("Unidad de esfuerzo",["MPa","ksi","GPa"],key="unit_3d")
            default=lambda x: x if u3=="MPa" else (x/6.894757293168361 if u3=="ksi" else x/1000.0)
            Sy3_user=st.number_input(f"Límite de fluencia Sy [{u3}]",min_value=1e-12,value=default(250.0),format="%.6g",key="yield_strength_3d")
            a,b,c=st.columns(3)
            sx3u=a.number_input(f"σx [{u3}]",value=default(120.0),format="%.6g",key="sigma_x_3d")
            sy3u=b.number_input(f"σy [{u3}]",value=default(50.0),format="%.6g",key="sigma_y_3d")
            sz3u=c.number_input(f"σz [{u3}]",value=default(-20.0),format="%.6g",key="sigma_z_3d")
            d,e,f=st.columns(3)
            txy3u=d.number_input(f"τxy [{u3}]",value=default(30.0),format="%.6g",key="tau_xy_3d")
            tyz3u=e.number_input(f"τyz [{u3}]",value=default(15.0),format="%.6g",key="tau_yz_3d")
            tzx3u=f.number_input(f"τzx [{u3}]",value=default(-10.0),format="%.6g",key="tau_zx_3d")
            delta_ratio=st.slider(
                "Cambio hidrostático pedagógico Δσh / Sy",
                min_value=-2.0,max_value=2.0,value=0.0,step=0.05,key="hydrostatic_shift_3d"
            )

    fact=unit_factor(u3)
    Sy3=Sy3_user*fact
    t3=stress_tensor(sx3u*fact,sy3u*fact,sz3u*fact,txy3u*fact,tyz3u*fact,tzx3u*fact)
    p3=principal_stresses(t3)
    vm3=von_mises_from_tensor(t3)
    n3=safety_factor(Sy3,vm3)
    state3=classify_yield_state(Sy3,vm3)
    mean3=float(np.trace(t3)/3.0)
    inv3=invariants(t3)
    hyd3=hydrostatic_tensor(t3); dev3=deviatoric_tensor(t3)
    shifted=add_hydrostatic_shift(t3,delta_ratio*Sy3)
    p3s=principal_stresses(shifted)
    vm3s=von_mises_from_tensor(shifted)

    with right:
        st.markdown("### Resultado del criterio")
        c1,c2,c3,c4=st.columns(4)
        with c1:
            math_card(r"\sigma_{VM}",f"{fmt(from_mpa(vm3,u3))} {u3}","Equivalente")
        with c2:
            math_card(r"n_{VM}",fmt(n3),"Factor de seguridad")
        with c3:
            math_card(r"\sigma_m",f"{fmt(from_mpa(mean3,u3))} {u3}","Parte media")
        with c4:
            math_card(r"J_2",f"{fmt(inv3['J2']/(fact**2))} {u3}²","Invariante desviador")
        state_banner(state3)

    subt=st.tabs([
        "Tensor y principales",
        "Cilindro de Von Mises",
        "Plano π",
        "Prueba hidrostática",
        "Ecuaciones",
        "Interpretación",
    ])

    with subt[0]:
        a,b=st.columns(2)
        with a:
            st.markdown("### Tensor de esfuerzos")
            st.latex(r"\boldsymbol{\sigma}="+matrix_latex(t3,u3))
            st.markdown("### Parte hidrostática")
            st.latex(r"\boldsymbol{\sigma}_h="+matrix_latex(hyd3,u3))
        with b:
            st.markdown("### Tensor desviador")
            st.latex(r"\mathbf{s}="+matrix_latex(dev3,u3))
            st.markdown("### Esfuerzos principales")
            st.latex(
                rf"\sigma_1={from_mpa(p3[0],u3):.5g},\quad"
                rf"\sigma_2={from_mpa(p3[1],u3):.5g},\quad"
                rf"\sigma_3={from_mpa(p3[2],u3):.5g}\;{u3}"
            )

    with subt[1]:
        st.plotly_chart(
            von_mises_cylinder_figure(
                from_mpa(p3[0],u3),from_mpa(p3[1],u3),from_mpa(p3[2],u3),
                from_mpa(Sy3,u3),
                shifted_principal=(
                    from_mpa(p3s[0],u3),from_mpa(p3s[1],u3),from_mpa(p3s[2],u3)
                ) if delta_ratio!=0 else None
            ),
            use_container_width=True,config={"displaylogo":False}
        )
        st.markdown(
            "La superficie de fluencia es un cilindro circular alrededor del eje hidrostático. "
            "El punto fluye cuando su distancia radial alcanza el radio correspondiente a Sᵧ."
        )

    with subt[2]:
        st.plotly_chart(
            pi_plane_figure(
                from_mpa(p3[0],u3),from_mpa(p3[1],u3),from_mpa(p3[2],u3),
                from_mpa(Sy3,u3)
            ),
            use_container_width=True,config={"displaylogo":False}
        )
        st.markdown(
            "El plano π es perpendicular al eje hidrostático. "
            "En este corte, Von Mises aparece como un círculo y Tresca como un hexágono."
        )

    with subt[3]:
        st.markdown("### Experimento conceptual")
        st.markdown(
            "El control **Δσh/Sy** suma la misma cantidad a los tres esfuerzos normales principales. "
            "Eso cambia el nivel hidrostático, pero no modifica las diferencias entre esfuerzos principales."
        )
        a,b=st.columns(2)
        with a:
            math_card(r"\sigma_{VM,\;original}",f"{fmt(from_mpa(vm3,u3))} {u3}","Antes del desplazamiento")
        with b:
            math_card(r"\sigma_{VM,\;desplazado}",f"{fmt(from_mpa(vm3s,u3))} {u3}","Después del desplazamiento")
        st.latex(r"\Delta\sigma_h\mathbf{I}\quad\Rightarrow\quad J_2=\text{cte}\quad\Rightarrow\quad\sigma_{VM}=\text{cte}")

    with subt[4]:
        equations_3d()

    with subt[5]:
        st.markdown(
            "La presión hidrostática cambia el **volumen** pero no la distorsión angular que gobierna "
            "este criterio de fluencia. Por eso Von Mises responde a la parte desviadora del tensor."
        )
        st.warning(
            "Esta interpretación corresponde a la aplicación del criterio de Von Mises a materiales dúctiles. "
            "No debe extrapolarse automáticamente a materiales cuya falla dependa fuertemente de la presión."
        )

# =============================================================================
# Failure criteria
# =============================================================================
with main_tabs[4]:
    st.markdown("## Criterios de falla · dónde se ubica Von Mises")
    st.markdown(
        "No todos los materiales ni todas las formas de falla deben evaluarse con el mismo criterio. "
        "Aquí se organiza el problema antes de elegir una ecuación."
    )

    c1,c2=st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### Material dúctil · carga estática")
            st.latex(r"\text{Falla de interés: inicio de fluencia}")
            st.markdown("**Von Mises / energía de distorsión**")
            st.caption("Compara un esfuerzo equivalente con el límite de fluencia.")
            st.markdown("**Tresca / máximo esfuerzo cortante**")
            st.caption("Compara la máxima diferencia entre esfuerzos principales con el límite de fluencia.")
    with c2:
        with st.container(border=True):
            st.markdown("### Material frágil · carga estática")
            st.latex(r"\text{Falla de interés: fractura}")
            st.markdown("Se utilizan criterios de fractura, no el criterio de fluencia de Von Mises.")
            st.caption("Ejemplos tratados en textos de diseño: esfuerzo normal máximo, Coulomb–Mohr y Mohr modificado.")

    st.markdown("### Comparación directa para el estado 2D actual")
    a,b=st.columns(2)
    with a:
        math_card(r"\sigma_{VM}",f"{fmt(from_mpa(vm2,u2))} {u2}","Criterio de energía de distorsión")
        math_card(r"n_{VM}",fmt(nvm2),"Margen respecto de Sy")
    with b:
        math_card(r"\sigma_{Tresca}",f"{fmt(from_mpa(tr2,u2))} {u2}","Criterio de máximo esfuerzo cortante")
        math_card(r"n_{Tresca}",fmt(ntr2),"Margen respecto de Sy")

    st.info(
        "Esta aplicación se concentra en **fluencia estática de materiales dúctiles**. "
        "Los criterios de fractura frágil se muestran para ubicar conceptualmente el problema, "
        "pero no se calculan en esta versión."
    )

# =============================================================================
# Analysis guide
# =============================================================================
with main_tabs[5]:
    st.markdown("## Guía de análisis")
    st.markdown("""
### 1 · Identificar el tipo de problema
Determina si estás frente a un material dúctil y a una condición estática donde el evento de interés es la fluencia.

### 2 · Definir el estado de esfuerzos
- En 1D basta con σₓ.
- En esfuerzo plano se necesitan σₓ, σᵧ y τxy.
- En 3D se requiere el tensor completo.

### 3 · Transformar cuando corresponda
Los esfuerzos principales permiten separar la orientación geométrica del estado respecto de la intensidad de la combinación.

### 4 · Evaluar el criterio
Von Mises reduce el estado multiaxial a un esfuerzo equivalente σVM.

### 5 · Comparar con la resistencia
""")
    st.latex(r"n=\frac{S_y}{\sigma_{VM}}")
    st.markdown("""
### 6 · Interpretar físicamente
- **n > 1:** estado bajo el límite de fluencia.
- **n = 1:** inicio de fluencia.
- **n < 1:** el estado supera el límite de fluencia.

### 7 · Revisar el criterio adecuado
Von Mises no es un criterio universal de falla. Debe usarse dentro del dominio físico para el cual corresponde.
""")

st.divider()
st.markdown("**GG DIMEC · MechLab** | Von Mises Lab")
st.caption("V1.0 · Versión integrada en GG DIMEC MechLab.")
