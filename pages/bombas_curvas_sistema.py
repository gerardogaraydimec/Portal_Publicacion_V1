from __future__ import annotations

import math
import streamlit as st

from modules.ui_brand import render_app_header
from modules.pump_data import FLUIDS, ROUGHNESS, FITTINGS, PRESETS
from modules.pump_engine import (
    fit_pump_curve,
    find_operating_point,
    static_head,
    system_head,
    pump_group_head,
    affinity_scaled_values,
    npsh_available,
)
from modules.pump_plotter import (
    make_system_schematic,
    sample_curves,
    make_operating_curve_figure,
    make_efficiency_figure,
    make_head_components_figure,
    make_affinity_figure,
    make_npsh_schematic,
    make_sensitivity_figure,
)


st.markdown(
    """
<style>
:root{
  --gg-orange:#f28e1c;
  --gg-black:#111111;
  --gg-muted:#737986;
  --gg-line:#eceff2;
}
.block-container{
  max-width:1500px;
  padding-top:1.35rem !important;
  padding-bottom:2rem;
}
div[data-testid="stMainBlockContainer"] > div:first-child{overflow:visible!important;}
.gg-case{
  border:1px solid var(--gg-line);
  border-left:5px solid var(--gg-orange);
  border-radius:14px;
  padding:1rem 1.1rem;
  background:#fff;
  margin:.25rem 0 .85rem 0;
}
.gg-note{
  border:1px solid #ecece8;
  background:#f7f7f5;
  border-radius:12px;
  padding:.95rem 1rem;
  line-height:1.58;
}
.gg-warning{
  border-left:4px solid var(--gg-orange);
  background:#fff8ef;
  border-radius:9px;
  padding:.85rem 1rem;
  line-height:1.55;
}
.gg-step{
  border:1px solid var(--gg-line);
  border-radius:12px;
  padding:.9rem 1rem;
  background:#fff;
  margin-bottom:.55rem;
}
div[data-testid="stMetric"]{
  border:1px solid var(--gg-line);
  border-radius:12px;
  padding:.55rem .7rem;
  background:#fff;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<div style="height:.18rem"></div>', unsafe_allow_html=True)

render_app_header(
    title="Bombas Centrífugas · Curva de Sistema y Punto de Operación",
    subtitle="Altura del sistema · curva de bomba · punto de operación · eficiencia · potencia · afinidad · NPSH.",
    section="MECÁNICA DE FLUIDOS · MÁQUINAS HIDRÁULICAS",
    logo_width=188,
)


def latex_card(title: str, formula: str, caption: str):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.latex(formula)
        st.caption(caption)


# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("Caso de aplicación")
    preset_name = st.selectbox("Configuración", list(PRESETS.keys()))
    preset = PRESETS[preset_name]

    st.divider()
    st.header("Fluido")
    fluid_name = st.selectbox(
        "Fluido",
        list(FLUIDS.keys()),
        index=list(FLUIDS.keys()).index(preset["fluid"]),
        key=f"pump_fluid_{preset_name}",
    )
    fluid = FLUIDS[fluid_name]

    if fluid["rho"] is None:
        rho = st.number_input("Densidad $\\rho$ [kg/m³]", min_value=1.0, value=1000.0, step=10.0)
        mu = st.number_input("Viscosidad dinámica $\\mu$ [Pa·s]", min_value=1e-6, value=1.0e-3, format="%.6f")
        pv_default = st.number_input("Presión de vapor $p_v$ [kPa abs]", min_value=0.0, value=2.34, step=0.1)
    else:
        rho = float(fluid["rho"])
        mu = float(fluid["mu"])
        pv_default = float(fluid["pv_kPa_abs"])
        st.latex(rf"\rho={rho:.1f}\,\mathrm{{kg/m^3}}")
        st.latex(rf"\mu={mu:.4g}\,\mathrm{{Pa\cdot s}}")

    st.divider()
    st.header("Condiciones del sistema")
    z1 = st.number_input("Cota de origen $z_1$ [m]", value=float(preset["z1_m"]), step=0.5, key=f"z1_{preset_name}")
    z2 = st.number_input("Cota de destino $z_2$ [m]", value=float(preset["z2_m"]), step=0.5, key=f"z2_{preset_name}")
    p1 = st.number_input("Presión de origen $p_1$ [kPa(g)]", value=float(preset["p1_kPa_g"]), step=10.0, key=f"p1_{preset_name}")
    p2 = st.number_input("Presión de destino $p_2$ [kPa(g)]", value=float(preset["p2_kPa_g"]), step=10.0, key=f"p2_{preset_name}")

    st.divider()
    st.header("Tubería")
    L_m = st.number_input("Longitud $L$ [m]", min_value=0.0, value=float(preset["L_m"]), step=1.0, key=f"L_{preset_name}")
    D_mm = st.number_input("Diámetro interior $D$ [mm]", min_value=1.0, value=float(preset["D_mm"]), step=5.0, key=f"D_{preset_name}")
    rough_name = st.selectbox(
        "Superficie interior",
        list(ROUGHNESS.keys()),
        index=list(ROUGHNESS.keys()).index(preset["roughness"]),
        key=f"rough_{preset_name}",
    )
    if ROUGHNESS[rough_name] is None:
        epsilon_mm = st.number_input("Rugosidad absoluta $\\varepsilon$ [mm]", min_value=0.0, value=0.045, step=0.005, format="%.4f")
    else:
        epsilon_mm = float(ROUGHNESS[rough_name])
        st.latex(rf"\varepsilon={epsilon_mm:.4g}\,\mathrm{{mm}}")

    st.divider()
    st.header("Accesorios")
    selected = st.multiselect(
        "Elementos con pérdida localizada",
        list(FITTINGS.keys()),
        default=list(preset["fittings"].keys()),
        key=f"pump_fittings_{preset_name}",
    )

    accessory_rows = []
    for name in selected:
        default_count = int(preset["fittings"].get(name, 1))
        count = st.number_input(
            f"Cantidad · {name}",
            min_value=0,
            value=default_count,
            step=1,
            key=f"pump_n_{preset_name}_{name}",
        )
        if FITTINGS[name] is None:
            kval = st.number_input(
                f"Coeficiente $K$ · {name}",
                min_value=0.0,
                value=1.0,
                step=0.1,
                key=f"pump_K_{preset_name}_{name}",
            )
        else:
            kval = float(FITTINGS[name])
        accessory_rows.append({
            "name": name,
            "count": int(count),
            "K": kval,
            "K_total": kval * int(count),
        })

    K_total = sum(row["K_total"] for row in accessory_rows)

    st.divider()
    st.header("Curva de la bomba")
    pump_preset = preset["pump"]

    H0 = st.number_input("Altura a caudal cero $H_0$ [m]", min_value=0.1, value=float(pump_preset["H0_m"]), step=1.0)
    Qbep = st.number_input("Caudal de referencia BEP $Q_{BEP}$ [L/s]", min_value=0.1, value=float(pump_preset["Qbep_Ls"]), step=1.0)
    Hbep = st.number_input("Altura en BEP $H_{BEP}$ [m]", min_value=0.0, value=float(pump_preset["Hbep_m"]), step=1.0)
    Qend = st.number_input("Caudal final de referencia $Q_{end}$ [L/s]", min_value=0.2, value=float(pump_preset["Qend_Ls"]), step=1.0)
    Hend = st.number_input("Altura final de referencia $H_{end}$ [m]", min_value=0.0, value=float(pump_preset["Hend_m"]), step=1.0)
    eta_max = st.slider("Eficiencia máxima de referencia $\\eta_{max}$", min_value=0.30, max_value=0.95, value=float(pump_preset["eta_max"]), step=0.01)

    st.divider()
    st.header("Configuración de bombas")
    arrangement = st.selectbox("Arreglo", ["1 bomba", "Serie", "Paralelo"])
    pump_count = 1
    if arrangement in {"Serie", "Paralelo"}:
        pump_count = st.number_input("Número de bombas", min_value=2, max_value=4, value=2, step=1)
    speed_ratio = st.slider("Relación de velocidad $N_2/N_1$", min_value=0.60, max_value=1.25, value=1.00, step=0.01)

    st.divider()
    st.caption(
        "La curva de bomba se construye con tres puntos de referencia y se usa con fines pedagógicos. "
        "Para ingeniería real debe reemplazarse por la curva oficial del fabricante."
    )


# ---------------------------------------------------------------------
# Solve
# ---------------------------------------------------------------------
try:
    curve = fit_pump_curve(H0, Qbep, Hbep, Qend, Hend, eta_max)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

op = find_operating_point(
    curve=curve,
    rho=rho,
    mu=mu,
    L_m=L_m,
    D_mm=D_mm,
    epsilon_mm=epsilon_mm,
    K_total=K_total,
    z1_m=z1,
    z2_m=z2,
    p1_kPa_g=p1,
    p2_kPa_g=p2,
    speed_ratio=speed_ratio,
    arrangement=arrangement,
    pump_count=pump_count,
)

q_limit = curve.Qend_m3s * speed_ratio * 1.55
if arrangement == "Paralelo":
    q_limit *= pump_count

q_curve, h_pump_curve, h_sys_curve, eta_curve = sample_curves(
    curve,
    rho,
    mu,
    L_m,
    D_mm,
    epsilon_mm,
    K_total,
    z1,
    z2,
    p1,
    p2,
    speed_ratio,
    arrangement,
    pump_count,
    q_limit,
)

st.markdown(
    f"""
<div class="gg-case">
  <div style="font-size:.78rem;font-weight:800;color:#f28e1c;letter-spacing:.08em">CASO DE APLICACIÓN</div>
  <h3 style="margin:.35rem 0 .25rem 0">{preset_name}</h3>
  <div style="color:#737986">{preset['description']}</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="gg-note">
<b>Qué conviene observar:</b> {preset['focus']}
</div>
""",
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "📘 Cómo usar",
    "🧩 Sistema",
    "⚙️ Curva de bomba",
    "🎯 Punto de operación",
    "🔍 Sensibilidad",
    "🔄 Afinidad y arreglos",
    "💧 Succión y NPSH",
    "🏭 Aplicaciones de ingeniería",
])

# ---------------------------------------------------------------------
# Cómo usar
# ---------------------------------------------------------------------
with tabs[0]:
    c1, c2 = st.columns([1.05, .95], gap="large")

    with c1:
        st.subheader("Qué problema resuelve este módulo")
        st.write(
            "Una bomba centrífuga no impone por sí sola un caudal fijo. "
            "El caudal real aparece donde la energía que la bomba puede entregar coincide con la energía que el sistema exige."
        )

        st.markdown("#### Ruta de cálculo")
        route = [
            ("1. Definir el proceso", "Se fijan origen y destino mediante cotas y presiones. Eso determina la parte estática del problema."),
            ("2. Definir la instalación", "Longitud, diámetro, rugosidad y accesorios permiten calcular las pérdidas con el mismo enfoque de Reynolds y Darcy–Weisbach usado en el módulo anterior."),
            ("3. Construir la curva del sistema", "Para cada caudal se calcula la altura estática más la pérdida hidráulica. Así se obtiene una relación entre caudal y altura requerida."),
            ("4. Definir la curva de la bomba", "Se representa la capacidad de la bomba como una relación entre caudal y altura. La curva de referencia se ajusta a partir de tres puntos."),
            ("5. Encontrar la intersección", "El punto donde ambas curvas se cruzan es el punto de operación hidráulico del conjunto."),
            ("6. Evaluar eficiencia y potencia", "Con el caudal y la altura de operación se estima potencia hidráulica y potencia de eje."),
            ("7. Revisar velocidad, arreglos y succión", "Las leyes de afinidad, bombas en serie/paralelo y NPSH permiten estudiar cómo cambia la operación y si la succión es razonable."),
        ]
        for title, body in route:
            st.markdown(f"<div class='gg-step'><b>{title}</b><br>{body}</div>", unsafe_allow_html=True)

    with c2:
        latex_card(
            "Altura del sistema",
            r"H_{sys}(Q)=H_{est}+h_L(Q)",
            "Suma la exigencia estática del proceso y las pérdidas dependientes del caudal."
        )
        latex_card(
            "Parte estática",
            r"H_{est}=(z_2-z_1)+\frac{p_2-p_1}{\rho g}",
            "Incluye diferencia de elevación y diferencia de presión entre origen y destino."
        )
        latex_card(
            "Punto de operación",
            r"H_p(Q)=H_{sys}(Q)",
            "La intersección entre curva de bomba y curva del sistema fija el caudal real."
        )
        latex_card(
            "Potencia hidráulica",
            r"P_h=\rho gQH",
            "Potencia efectivamente transferida al fluido."
        )
        latex_card(
            "Potencia de eje",
            r"P_{eje}=\frac{P_h}{\eta}",
            "Potencia mecánica que debe llegar al eje de la bomba para la eficiencia considerada."
        )

        st.info(
            "La conexión con los módulos anteriores es directa: Bernoulli entrega el balance de energía y Reynolds/Darcy entrega la pérdida hidráulica. "
            "Aquí ambas piezas se unen con la curva de una máquina.",
            icon="🔗"
        )

# ---------------------------------------------------------------------
# Sistema
# ---------------------------------------------------------------------
with tabs[1]:
    st.subheader("Sistema hidráulico completo")
    st.write(
        "El esquema muestra origen, bomba y destino. Las cotas se miden desde un mismo datum y las presiones corresponden a las condiciones de borde del sistema."
    )

    st.plotly_chart(
        make_system_schematic(
            z1, z2, p1, p2, L_m, D_mm,
            sum(row["count"] for row in accessory_rows),
        ),
        width="stretch",
        config={"displaylogo": False},
    )

    H_geom = z2 - z1
    H_press = ((p2 - p1) * 1000.0) / (rho * 9.80665)
    H_static = static_head(rho, z1, z2, p1, p2)

    st.markdown("#### Parte estática del sistema")
    a1, a2, a3 = st.columns(3)
    a1.metric("Diferencia de cota", f"{H_geom:.3f} m")
    a2.metric("Altura equivalente de presión", f"{H_press:.3f} m")
    a3.metric("Altura estática total", f"{H_static:.3f} m")

    st.latex(
        r"H_{est}="
        r"(z_2-z_1)+"
        r"\frac{p_2-p_1}{\rho g}"
    )

    if op.found:
        _, _, hf_op, hm_op = system_head(
            op.Q_m3s, rho, mu, L_m, D_mm, epsilon_mm, K_total,
            z1, z2, p1, p2
        )
        st.markdown("#### De qué está compuesta la altura requerida en el punto de operación")
        st.plotly_chart(
            make_head_components_figure(H_geom, H_press, hf_op, hm_op),
            width="stretch",
            config={"displaylogo": False},
        )

        st.latex(
            rf"H_{{sys}}={H_geom:.3f}+{H_press:.3f}+{hf_op:.3f}+{hm_op:.3f}"
        )
        st.latex(rf"H_{{sys}}={op.system_head_m:.3f}\,\mathrm{{m}}")

# ---------------------------------------------------------------------
# Pump curve
# ---------------------------------------------------------------------
with tabs[2]:
    st.subheader("Cómo se representa la curva de la bomba")

    st.write(
        "Una bomba centrífuga entrega mucha altura cuando el caudal es bajo y, en general, la altura disponible disminuye al aumentar el caudal. "
        "La curva real debe provenir del fabricante; aquí usamos una curva pedagógica ajustada a tres puntos."
    )

    st.markdown("#### Puntos de referencia")
    p1c, p2c, p3c = st.columns(3)
    with p1c:
        st.latex(rf"Q=0")
        st.latex(rf"H={H0:.2f}\,\mathrm{{m}}")
        st.caption("Altura a caudal cero o shutoff de referencia.")
    with p2c:
        st.latex(rf"Q_{{BEP}}={Qbep:.2f}\,\mathrm{{L/s}}")
        st.latex(rf"H_{{BEP}}={Hbep:.2f}\,\mathrm{{m}}")
        st.caption("Punto de mejor eficiencia usado como referencia.")
    with p3c:
        st.latex(rf"Q_{{end}}={Qend:.2f}\,\mathrm{{L/s}}")
        st.latex(rf"H_{{end}}={Hend:.2f}\,\mathrm{{m}}")
        st.caption("Punto final de referencia de la curva.")

    a, b, c = curve.coeffs
    st.markdown("#### Ajuste matemático utilizado")
    st.latex(r"H_p(Q)=aQ^2+bQ+c")
    st.latex(rf"a={a:.4g},\qquad b={b:.4g},\qquad c={c:.4g}")
    st.caption("En esta expresión interna, el caudal está expresado en m³/s.")

    st.markdown("#### Eficiencia de referencia")
    st.write(
        "La eficiencia se representa mediante una curva suave centrada en el punto BEP. "
        "Su objetivo es mostrar cómo la potencia de eje cambia al alejarse del punto de mayor eficiencia."
    )
    st.latex(r"\eta=\frac{P_h}{P_{eje}}")

    st.plotly_chart(
        make_efficiency_figure(q_curve, eta_curve, op),
        width="stretch",
        config={"displaylogo": False},
    )

# ---------------------------------------------------------------------
# Operating point
# ---------------------------------------------------------------------
with tabs[3]:
    st.subheader("Punto de operación · bomba + sistema")

    st.write(
        "La curva del sistema aumenta con el caudal porque las pérdidas crecen. "
        "La curva de la bomba tiende a disminuir con el caudal. La intersección define la condición de funcionamiento."
    )

    st.plotly_chart(
        make_operating_curve_figure(
            q_curve, h_pump_curve, h_sys_curve, op,
            curve, speed_ratio, arrangement, pump_count
        ),
        width="stretch",
        config={"displaylogo": False},
    )

    if not op.found:
        st.error(op.message)
    else:
        o1, o2, o3, o4 = st.columns(4)
        o1.metric("Caudal de operación", f"{op.Q_m3s*1000:.3f} L/s")
        o2.metric("Altura de operación", f"{op.H_m:.3f} m")
        o3.metric("Eficiencia de referencia", f"{op.eta*100:.1f} %")
        o4.metric("Q por bomba", f"{op.pump_each_flow_m3s*1000:.3f} L/s")

        p1m, p2m, p3m = st.columns(3)
        p1m.metric("Potencia hidráulica", f"{op.hydraulic_power_kW:.3f} kW")
        p2m.metric("Potencia total de eje", f"{op.shaft_power_kW:.3f} kW")
        p3m.metric("Q/Q_BEP por bomba", f"{op.bep_ratio:.3f}")

        st.markdown("#### Cómo interpretar la ubicación respecto del BEP")
        st.latex(r"\frac{Q_{op}}{Q_{BEP}}")
        if op.bep_ratio < 0.9:
            st.write(
                "El caudal por bomba está a la izquierda del BEP de referencia. "
                "Eso indica operación a menor caudal que el punto de mejor eficiencia usado en la curva."
            )
        elif op.bep_ratio > 1.1:
            st.write(
                "El caudal por bomba está a la derecha del BEP de referencia. "
                "Eso indica operación a mayor caudal que el punto de mejor eficiencia usado en la curva."
            )
        else:
            st.write(
                "El caudal por bomba está próximo al BEP de referencia. "
                "La cercanía exacta admisible debe verificarse con la curva y documentación del fabricante."
            )

        st.markdown("#### Qué cambia el punto de operación")
        st.markdown(
            """
- aumentar la altura estática desplaza la curva del sistema hacia arriba;
- reducir el diámetro aumenta las pérdidas y desplaza la operación hacia menor caudal;
- cerrar una válvula aumenta la resistencia del sistema;
- aumentar velocidad de giro desplaza la curva de bomba;
- bombas en serie aumentan principalmente la altura disponible;
- bombas en paralelo aumentan principalmente la capacidad de caudal del conjunto.
"""
        )

# ---------------------------------------------------------------------
# Sensitivity
# ---------------------------------------------------------------------
with tabs[4]:
    st.subheader("Sensibilidad del punto de operación")

    st.write(
        "Una de las formas más útiles de estudiar un sistema es preguntar qué ocurre si cambia la instalación. "
        "Aquí puedes modificar diámetro, resistencia localizada y altura estática sin alterar la curva de la bomba."
    )

    s1, s2, s3 = st.columns(3)
    with s1:
        d_factor = st.slider(
            "Factor de diámetro alternativo",
            min_value=0.70, max_value=1.30,
            value=1.00, step=0.01,
            key="pump_sens_D"
        )
    with s2:
        extra_K = st.slider(
            "Resistencia adicional $\\Delta K$",
            min_value=0.0, max_value=20.0,
            value=0.0, step=0.5,
            key="pump_sens_K"
        )
    with s3:
        extra_static = st.slider(
            "Cambio adicional de cota $\\Delta z$ [m]",
            min_value=-10.0, max_value=20.0,
            value=0.0, step=0.5,
            key="pump_sens_z"
        )

    D_alt = D_mm * d_factor
    K_alt = K_total + extra_K
    z2_alt = z2 + extra_static

    op_alt = find_operating_point(
        curve=curve,
        rho=rho,
        mu=mu,
        L_m=L_m,
        D_mm=D_alt,
        epsilon_mm=epsilon_mm,
        K_total=K_alt,
        z1_m=z1,
        z2_m=z2_alt,
        p1_kPa_g=p1,
        p2_kPa_g=p2,
        speed_ratio=speed_ratio,
        arrangement=arrangement,
        pump_count=pump_count,
    )

    q_alt, h_pump_alt, h_sys_alt, _ = sample_curves(
        curve,
        rho,
        mu,
        L_m,
        D_alt,
        epsilon_mm,
        K_alt,
        z1,
        z2_alt,
        p1,
        p2,
        speed_ratio,
        arrangement,
        pump_count,
        q_limit,
    )

    st.plotly_chart(
        make_sensitivity_figure(
            q_curve,
            h_pump_curve,
            h_sys_curve,
            h_sys_alt,
            op,
            op_alt,
            "Sistema alternativo",
        ),
        width="stretch",
        config={"displaylogo": False},
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Configuración actual")
        st.latex(rf"D={D_mm:.1f}\,\mathrm{{mm}}")
        st.latex(rf"\sum K={K_total:.3f}")
        st.latex(rf"z_2-z_1={z2-z1:.3f}\,\mathrm{{m}}")
        if op.found:
            st.latex(rf"Q_{{op}}={op.Q_m3s*1000:.3f}\,\mathrm{{L/s}}")
            st.latex(rf"H_{{op}}={op.H_m:.3f}\,\mathrm{{m}}")

    with c2:
        st.markdown("#### Configuración alternativa")
        st.latex(rf"D_{{alt}}={D_alt:.1f}\,\mathrm{{mm}}")
        st.latex(rf"\sum K_{{alt}}={K_alt:.3f}")
        st.latex(rf"(z_2-z_1)_{{alt}}={z2_alt-z1:.3f}\,\mathrm{{m}}")
        if op_alt.found:
            st.latex(rf"Q_{{op,alt}}={op_alt.Q_m3s*1000:.3f}\,\mathrm{{L/s}}")
            st.latex(rf"H_{{op,alt}}={op_alt.H_m:.3f}\,\mathrm{{m}}")
        else:
            st.write("No se encontró un punto de operación dentro del rango explorado.")

    st.markdown("#### Cómo interpretar los cambios")
    st.markdown(
        """
- reducir el diámetro aumenta la velocidad y normalmente eleva de forma importante las pérdidas;
- agregar resistencia localizada desplaza la curva del sistema hacia arriba;
- aumentar la diferencia de cota desplaza prácticamente toda la curva del sistema hacia arriba;
- si la curva del sistema sube y la bomba no cambia, el punto de operación tiende a desplazarse hacia menor caudal.
"""
    )

# ---------------------------------------------------------------------
# Affinity and arrangements
# ---------------------------------------------------------------------
with tabs[5]:
    st.subheader("Leyes de afinidad y configuración de bombas")

    st.markdown("### Cambio de velocidad")
    st.latex(r"\frac{Q_2}{Q_1}=\frac{N_2}{N_1}")
    st.latex(r"\frac{H_2}{H_1}=\left(\frac{N_2}{N_1}\right)^2")
    st.latex(r"\frac{P_2}{P_1}=\left(\frac{N_2}{N_1}\right)^3")

    if op.found:
        Q2_ref, H2_ref, P2_ref = affinity_scaled_values(
            op.pump_each_flow_m3s,
            op.H_m / pump_count if arrangement == "Serie" else op.H_m,
            op.shaft_power_kW / pump_count,
            speed_ratio,
        )
        st.caption(
            "Las leyes de afinidad son relaciones de semejanza. En equipos reales deben verificarse límites de velocidad, eficiencia, cavitación y rango permitido por el fabricante."
        )

    st.plotly_chart(
        make_affinity_figure(curve, [0.80, 1.00, 1.20], curve.Qend_m3s*1.5),
        width="stretch",
        config={"displaylogo": False},
    )

    a1, a2 = st.columns(2, gap="large")
    with a1:
        st.markdown("### Bombas idénticas en serie")
        st.latex(r"H_{serie}(Q)=n\,H_p(Q)")
        st.write(
            "El mismo caudal atraviesa cada bomba y las alturas se suman. "
            "Es útil cuando el sistema requiere más altura que la disponible con una sola bomba."
        )
    with a2:
        st.markdown("### Bombas idénticas en paralelo")
        st.latex(r"H_{paralelo}(Q)=H_p\left(\frac{Q}{n}\right)")
        st.write(
            "El caudal total se reparte entre las bombas y todas trabajan aproximadamente a la misma altura. "
            "Se utiliza cuando se necesita aumentar capacidad de caudal o flexibilidad operacional."
        )

# ---------------------------------------------------------------------
# NPSH
# ---------------------------------------------------------------------
with tabs[6]:
    st.subheader("Succión, presión absoluta y NPSH")

    st.write(
        "La bomba puede tener suficiente altura para mover el sistema y aun así presentar problemas en succión. "
        "Por eso la selección no termina en el punto de operación."
    )

    st.markdown("#### Datos de succión")
    n1, n2 = st.columns(2)
    with n1:
        p_surface_abs = st.number_input(
            "Presión absoluta sobre la superficie de succión $p_s$ [kPa abs]",
            min_value=1.0,
            value=101.3,
            step=1.0,
        )
        pv_abs = st.number_input(
            "Presión de vapor $p_v$ [kPa abs]",
            min_value=0.0,
            value=float(pv_default),
            step=0.1,
        )
    with n2:
        z_suction = st.number_input(
            "Diferencia de cota superficie–bomba $z_s-z_p$ [m]",
            value=2.0,
            step=0.25,
            help="Positiva cuando la superficie del líquido está por encima del centro de la bomba."
        )
        hL_suction = st.number_input(
            "Pérdidas en succión $h_{L,s}$ [m]",
            min_value=0.0,
            value=1.0,
            step=0.1,
        )

    npsha = npsh_available(rho, p_surface_abs, pv_abs, z_suction, hL_suction)
    npshr = st.number_input(
        "NPSH requerido del fabricante $NPSH_r$ [m]",
        min_value=0.0,
        value=3.0,
        step=0.1,
    )
    margin = npsha - npshr

    st.plotly_chart(
        make_npsh_schematic(z_suction, p_surface_abs, pv_abs, hL_suction),
        width="stretch",
        config={"displaylogo": False},
    )

    st.latex(
        r"NPSH_a="
        r"\frac{p_s}{\rho g}"
        r"+(z_s-z_p)"
        r"-h_{L,s}"
        r"-\frac{p_v}{\rho g}"
    )

    n1m, n2m, n3m = st.columns(3)
    n1m.metric("NPSH disponible", f"{npsha:.3f} m")
    n2m.metric("NPSH requerido", f"{npshr:.3f} m")
    n3m.metric("Margen simple", f"{margin:.3f} m")

    st.markdown("#### Cómo interpretar este cálculo")
    st.write(
        "El NPSH disponible depende de la presión absoluta en succión, la posición de la bomba, las pérdidas de la línea de succión y la presión de vapor del fluido. "
        "El NPSH requerido debe venir de la documentación del fabricante para la bomba y el punto de operación considerados."
    )

    if margin < 0:
        st.error(
            "Con los valores ingresados, el NPSH disponible es menor que el requerido. "
            "Esta condición debe revisarse antes de considerar válida la selección."
        )
    else:
        st.info(
            "El NPSH disponible supera al requerido ingresado. El margen aceptable debe definirse con los criterios del fabricante y del proyecto.",
            icon="ℹ️"
        )

# ---------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------
with tabs[7]:
    st.subheader("Uso del módulo como herramienta de ingeniería")

    a1, a2 = st.columns(2, gap="large")
    with a1:
        st.markdown("### Diseño y evaluación de instalaciones")
        st.markdown(
            """
- transferencia entre estanques;
- recirculación de agua industrial;
- circuitos de refrigeración;
- lubricación y servicios auxiliares de maquinaria;
- alimentación de intercambiadores;
- skids de proceso;
- líneas hacia recipientes presurizados;
- evaluación preliminar de cambios de diámetro o válvulas.
"""
        )

        st.markdown("### Preguntas que permite responder")
        st.markdown(
            """
- ¿Qué caudal entregará realmente esta bomba en mi sistema?
- ¿Qué parte de la altura corresponde a cota, presión o pérdidas?
- ¿Qué ocurre si reduzco el diámetro?
- ¿Qué pasa si aumento la velocidad de la bomba?
- ¿Necesito más altura o más capacidad de caudal?
- ¿Qué cambia al instalar bombas en serie o en paralelo?
- ¿Cuánta potencia mecánica exige la condición de operación?
- ¿La condición de succión merece revisión por NPSH?
"""
        )

    with a2:
        st.markdown("### Qué debe verificarse fuera de esta herramienta")
        st.markdown(
            """
- curva oficial de bomba del fabricante;
- curva real de eficiencia;
- diámetro y velocidad nominal del impulsor;
- potencia y servicio del motor;
- condiciones mínimas y máximas de operación;
- límites de temperatura y material;
- NPSH requerido oficial;
- cavitación, vibración y ruido;
- control mediante válvulas o variador de frecuencia;
- transitorios, golpe de ariete y arranques;
- requisitos normativos del proyecto.
"""
        )

        st.markdown("### Conexión con MechLab")
        st.write(
            "Este módulo cierra una cadena completa de razonamiento: "
            "Continuidad y Bernoulli entregan el balance ideal; Reynolds y Darcy explican las pérdidas reales; "
            "Bombas y Curvas de Sistema determinan cómo una máquina interactúa con esa instalación."
        )

    st.markdown(
        """
<div class="gg-warning">
<b>Criterio de uso:</b> esta herramienta es adecuada para aprendizaje, comparación de escenarios y preanálisis. 
Una selección real debe cerrarse con curvas certificadas del fabricante y las condiciones específicas del proyecto.
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()
st.caption("GG DIMEC · MechLab · Mecánica de Fluidos y Máquinas Hidráulicas.")
