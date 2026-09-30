from __future__ import annotations

import streamlit as st

from modules.ui_brand import render_app_header
from modules.fluid_cases import CASES, UNKNOWN_OPTIONS
from modules.fluid_engine import solve_ideal_bernoulli, mass_flow_rate, pump_power
from modules.fluid_plotter import make_system_figure, make_energy_figure, make_head_bars


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
div[data-testid="stImage"],div[data-testid="stImage"] img{overflow:visible!important;}
div[data-testid="stImage"] img{object-fit:contain!important;}
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
  padding:.9rem 1rem;
  line-height:1.55;
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
    title="Flujo Interno · Continuidad y Bernoulli",
    subtitle="Caudal · velocidad · presión · altura · conservación de masa · conservación de energía.",
    section="MECÁNICA DE FLUIDOS",
    logo_width=188,
)

FLUIDS = {
    "Agua · referencia 20 °C": 998.2,
    "Agua de mar · referencia": 1025.0,
    "Aceite hidráulico · referencia": 870.0,
    "Personalizada": None,
}


def latex_card(title: str, formula: str, caption: str):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.latex(formula)
        st.caption(caption)


with st.sidebar:
    st.header("Caso de estudio")
    case_name = st.selectbox("Configuración", list(CASES.keys()))
    case = CASES[case_name]

    st.divider()
    st.header("Fluido")
    fluid_name = st.selectbox("Fluido", list(FLUIDS.keys()))
    if FLUIDS[fluid_name] is None:
        rho = st.number_input(
            "Densidad ρ [kg/m³]",
            min_value=1.0, value=1000.0, step=10.0,
            key=f"rho_{case_name}"
        )
    else:
        rho = FLUIDS[fluid_name]
        st.latex(rf"\rho={rho:.1f}\,\mathrm{{kg/m^3}}")

    st.divider()
    st.header("Incógnita")
    unknown = st.selectbox(
        "Resolver",
        UNKNOWN_OPTIONS,
        index=UNKNOWN_OPTIONS.index(case["unknown"]),
        key=f"unknown_{case_name}",
        help="La aplicación usa continuidad y Bernoulli ideal entre las secciones 1 y 2."
    )

    st.divider()
    st.header("Geometría")
    D1 = st.number_input("Diámetro D₁ [mm]", min_value=1.0, value=float(case["D1_mm"]), step=5.0, key=f"D1_{case_name}")
    D2 = st.number_input("Diámetro D₂ [mm]", min_value=1.0, value=float(case["D2_mm"]), step=5.0, key=f"D2_{case_name}")
    z1 = st.number_input("Cota z₁ [m]", value=float(case["z1_m"]), step=0.5, key=f"z1_{case_name}")
    z2 = st.number_input("Cota z₂ [m]", value=float(case["z2_m"]), step=0.5, key=f"z2_{case_name}")

    st.divider()
    st.header("Condiciones")
    p1 = st.number_input("Presión manométrica p₁ [kPa]", value=float(case["p1_kPa"]), step=10.0, disabled=(unknown == "p₁"), key=f"p1_{case_name}_{unknown}")
    p2 = st.number_input("Presión manométrica p₂ [kPa]", value=float(case["p2_kPa"]), step=10.0, disabled=(unknown == "p₂"), key=f"p2_{case_name}_{unknown}")
    Q = st.number_input("Caudal Q [L/s]", min_value=0.0, value=float(case["Q_Ls"]), step=1.0, disabled=(unknown == "Q"), key=f"Q_{case_name}_{unknown}")

    st.divider()
    st.caption("Presiones expresadas como manométricas. El modelo es ideal: líquido incompresible, régimen permanente y sin pérdidas entre 1 y 2.")


result = solve_ideal_bernoulli(
    rho=rho,
    D1_mm=D1,
    D2_mm=D2,
    z1_m=z1,
    z2_m=z2,
    p1_kPa=p1,
    p2_kPa=p2,
    Q_Ls=Q,
    unknown=unknown,
)

st.markdown(
    f"""
<div class="gg-case">
  <div style="font-size:.78rem;font-weight:800;color:#f28e1c;letter-spacing:.08em">CASO DE ESTUDIO</div>
  <h3 style="margin:.35rem 0 .25rem 0">{case_name}</h3>
  <div style="color:#737986">{case['description']}</div>
</div>
""",
    unsafe_allow_html=True,
)

if not result.ok:
    st.error(result.message)
    st.stop()

Q_Ls_result = result.Q_m3s * 1000.0
p1_kPa_result = result.p1_Pa / 1000.0
p2_kPa_result = result.p2_Pa / 1000.0
mdot = mass_flow_rate(rho, result.Q_m3s)

tabs = st.tabs([
    "📘 Cómo usar",
    "🧩 Sistema",
    "∑ Continuidad",
    "⚡ Bernoulli",
    "📈 HGL · EGL",
    "🏭 Aplicaciones",
    "⚙️ Puente a bombas",
])

with tabs[0]:
    c1, c2 = st.columns([1.05, .95], gap="large")

    with c1:
        st.subheader("Qué problema estamos resolviendo")
        st.write(
            "El módulo estudia un flujo interno entre dos secciones. "
            "Primero conserva masa y después analiza cómo se reparte la energía mecánica del fluido "
            "entre presión, velocidad y altura."
        )

        st.markdown("#### Ruta de lectura")
        st.markdown(
            """
1. Define las secciones 1 y 2 mediante sus diámetros y cotas.
2. Fija el fluido y selecciona la incógnita: p₁, p₂ o Q.
3. Usa continuidad para relacionar área, velocidad y caudal.
4. Usa Bernoulli ideal para conectar presión, velocidad y altura.
5. Revisa HGL y EGL para entender visualmente el balance energético.
6. Interpreta el resultado: ¿sube la velocidad?, ¿cae la presión?, ¿cuánto influye el cambio de cota?
"""
        )

        st.markdown("#### Condiciones de trabajo del modelo")
        st.write(
            "El análisis se hace con un líquido de densidad constante, flujo permanente, perfil unidimensional promedio, "
            "factor cinético α = 1, sin pérdidas por fricción, sin pérdidas menores y sin máquinas entre las secciones del cálculo principal."
        )
        st.write(
            "Eso significa que este módulo no busca todavía describir la instalación real completa, sino ordenar el razonamiento físico: "
            "primero continuidad y después energía."
        )

    with c2:
        st.subheader("Tres ideas clave antes de calcular")
        latex_card(
            "Caudal volumétrico",
            r"Q=A\,V",
            "Relaciona cuánto volumen atraviesa una sección por unidad de tiempo con el área y la velocidad media."
        )
        latex_card(
            "Flujo másico",
            r"\dot m=\rho Q=\rho A V",
            "Representa la masa que atraviesa la sección por unidad de tiempo."
        )
        latex_card(
            "Energía mecánica por unidad de peso",
            r"H=z+\frac{p}{\rho g}+\frac{V^2}{2g}",
            "Cada término se expresa como una altura [m] y permite comparar presión, velocidad y posición."
        )
        st.markdown(
            '<div class="gg-note"><b>Clave pedagógica:</b> en esta app, la <b>cota z</b> siempre se mide desde un mismo datum de referencia. '
            'No importa si ese datum es el piso, el eje de una bomba o un nivel arbitrario; lo importante es que <b>z₁ y z₂ se midan desde la misma base</b>.</div>',
            unsafe_allow_html=True,
        )

with tabs[1]:
    st.subheader("Geometría, secciones y referencia de alturas")
    st.write(
        "Las líneas azules representan los cortes de Sección 1 y Sección 2, que son los planos donde se aplican continuidad y Bernoulli. "
        "La línea punteada clara bajo el sistema es el datum de referencia desde el cual se miden las cotas."
    )

    st.plotly_chart(make_system_figure(result, case["geometry"]), width="stretch", config={"displaylogo": False})

    s1, s2 = st.columns(2, gap="large")
    with s1:
        st.markdown("#### Sección 1")
        latex_card("Área", rf"A_1=\frac{{\pi D_1^2}}{{4}}={result.A1_m2:.6f}\,\mathrm{{m^2}}", "Área transversal asociada al diámetro D₁.")
        latex_card("Velocidad media", rf"V_1=\frac{{Q}}{{A_1}}={result.V1_ms:.3f}\,\mathrm{{m/s}}", "Velocidad media del modelo unidimensional en la sección 1.")
        st.latex(rf"p_1={p1_kPa_result:.2f}\,\mathrm{{kPa}}")
        st.latex(rf"z_1={result.z1_m:.2f}\,\mathrm{{m}}")

    with s2:
        st.markdown("#### Sección 2")
        latex_card("Área", rf"A_2=\frac{{\pi D_2^2}}{{4}}={result.A2_m2:.6f}\,\mathrm{{m^2}}", "Área transversal asociada al diámetro D₂.")
        latex_card("Velocidad media", rf"V_2=\frac{{Q}}{{A_2}}={result.V2_ms:.3f}\,\mathrm{{m/s}}", "Velocidad media del modelo unidimensional en la sección 2.")
        st.latex(rf"p_2={p2_kPa_result:.2f}\,\mathrm{{kPa}}")
        st.latex(rf"z_2={result.z2_m:.2f}\,\mathrm{{m}}")

    st.markdown("#### Cómo leer las cotas")
    st.markdown(
        """
- La cota no se mide desde el borde de la tubería ni desde la superficie del fluido.
- En este módulo, la cota z se asocia al eje de la tubería en cada sección.
- Lo importante no es el valor absoluto del datum, sino la diferencia de cotas entre secciones.
- Si cambias el datum pero lo haces de forma consistente para ambas secciones, la física no cambia.
"""
    )

    st.markdown("#### Resultado global")
    r1, r2, r3 = st.columns(3)
    r1.metric("Caudal volumétrico", f"{Q_Ls_result:.3f} L/s")
    r2.metric("Flujo másico", f"{mdot:.3f} kg/s")
    r3.metric("Relación V₂/V₁", f"{result.V2_ms/result.V1_ms:.3f}")

with tabs[2]:
    st.subheader("Conservación de masa")
    st.write(
        "La ecuación de continuidad expresa que, en régimen permanente, la masa que entra al volumen de control debe ser igual a la masa que sale."
    )
    st.latex(r"\dot m_{in}=\dot m_{out}")
    st.write("Para una entrada y una salida:")
    st.latex(r"\rho_1 A_1 V_1=\rho_2 A_2 V_2")
    st.write("Si el líquido se modela como incompresible:")
    st.latex(r"\rho_1=\rho_2=\rho")
    st.write("entonces la continuidad queda:")
    st.latex(r"A_1V_1=A_2V_2=Q")

    m1, m2 = st.columns(2, gap="large")
    with m1:
        st.markdown("#### Método de cálculo")
        st.markdown(
            """
1. Se calcula el área en cada sección a partir del diámetro.
2. Si el caudal es conocido, se obtiene cada velocidad mediante V = Q/A.
3. Si la incógnita es Q, continuidad se combina con Bernoulli para resolverlo.
"""
        )
        latex_card("Área 1", rf"A_1={result.A1_m2:.6f}\,\mathrm{{m^2}}", f"Corresponde al diámetro D₁ = {D1:.1f} mm.")
        latex_card("Velocidad 1", rf"V_1={result.V1_ms:.3f}\,\mathrm{{m/s}}", "Resultado de dividir el caudal por A₁.")
    with m2:
        st.markdown("#### Interpretación física")
        latex_card("Área 2", rf"A_2={result.A2_m2:.6f}\,\mathrm{{m^2}}", f"Corresponde al diámetro D₂ = {D2:.1f} mm.")
        latex_card("Velocidad 2", rf"V_2={result.V2_ms:.3f}\,\mathrm{{m/s}}", "Resultado de dividir el mismo caudal por A₂.")

    area_ratio = result.A1_m2 / result.A2_m2
    velocity_ratio = result.V2_ms / result.V1_ms

    st.markdown("#### Relaciones que ayudan a leer el caso")
    st.latex(rf"\frac{{A_1}}{{A_2}}={area_ratio:.3f}")
    st.latex(rf"\frac{{V_2}}{{V_1}}={velocity_ratio:.3f}")

    if result.A2_m2 < result.A1_m2:
        st.success("La sección 2 tiene menor área. Como el caudal debe conservarse, V₂ aumenta.")
    elif result.A2_m2 > result.A1_m2:
        st.success("La sección 2 tiene mayor área. Para mantener el mismo caudal, V₂ disminuye.")
    else:
        st.success("Las áreas son iguales; en el modelo incompresible, V₁ = V₂.")

with tabs[3]:
    st.subheader("Conservación de energía mecánica")
    st.write(
        "Bernoulli muestra cómo la energía mecánica por unidad de peso se redistribuye entre presión, velocidad y posición. "
        "En esta versión trabajamos con el caso ideal entre dos secciones."
    )
    st.latex(r"\frac{p_1}{\rho g}+\frac{V_1^2}{2g}+z_1=\frac{p_2}{\rho g}+\frac{V_2^2}{2g}+z_2")

    st.markdown("### ¿Qué significa cada término?")
    e1, e2, e3 = st.columns(3)
    with e1:
        latex_card("Altura de presión", r"\frac{p}{\rho g}", "Presión expresada como una altura equivalente de columna del mismo fluido.")
    with e2:
        latex_card("Altura de velocidad", r"\frac{V^2}{2g}", "Contribución cinética asociada a la velocidad media.")
    with e3:
        latex_card("Altura geométrica", r"z", "Contribución potencial gravitatoria medida desde el datum escogido.")

    st.markdown("### Método de trabajo")
    st.markdown(
        """
1. Se define el estado de la sección 1 y de la sección 2.
2. Se calculan las velocidades con continuidad.
3. Se escriben los tres aportes de energía en cada lado de la ecuación.
4. Se despeja la incógnita: p₁, p₂ o Q.
5. Se interpreta el resultado físicamente.
"""
    )

    st.markdown("### Balance numérico")
    b1, b2 = st.columns(2, gap="large")
    with b1:
        st.markdown("#### Sección 1")
        st.latex(rf"\frac{{p_1}}{{\rho g}}={result.pressure_head_1_m:.3f}\,\mathrm{{m}}")
        st.latex(rf"\frac{{V_1^2}}{{2g}}={result.velocity_head_1_m:.3f}\,\mathrm{{m}}")
        st.latex(rf"z_1={result.z1_m:.3f}\,\mathrm{{m}}")
        st.latex(rf"H_1={result.EGL1_m:.3f}\,\mathrm{{m}}")
    with b2:
        st.markdown("#### Sección 2")
        st.latex(rf"\frac{{p_2}}{{\rho g}}={result.pressure_head_2_m:.3f}\,\mathrm{{m}}")
        st.latex(rf"\frac{{V_2^2}}{{2g}}={result.velocity_head_2_m:.3f}\,\mathrm{{m}}")
        st.latex(rf"z_2={result.z2_m:.3f}\,\mathrm{{m}}")
        st.latex(rf"H_2={result.EGL2_m:.3f}\,\mathrm{{m}}")

    st.latex(rf"H_1-H_2={result.EGL1_m-result.EGL2_m:.3e}\,\mathrm{{m}}")

    st.markdown("#### Cómo interpretar el signo de cada cambio")
    st.markdown(
        """
- Si la velocidad aumenta, la altura de velocidad crece.
- Si la tubería asciende, la altura geométrica aumenta.
- Si no entra energía externa y no hay pérdidas, ese aumento debe compensarse con una disminución en otro término, normalmente la altura de presión.
"""
    )

    st.markdown("#### Interpretación del caso")
    st.write(case["insight"])

    if p1_kPa_result < 0 or p2_kPa_result < 0:
        st.warning(
            "Aparece presión manométrica negativa. Eso no implica por sí solo cavitación: para evaluarla se necesita presión absoluta, presión de vapor y análisis del sistema completo.",
            icon="⚠️"
        )

with tabs[4]:
    st.subheader("Línea piezométrica y línea de energía")
    c1, c2 = st.columns([1.1, .9], gap="large")
    with c1:
        st.latex(r"HGL=z+\frac{p}{\rho g}")
        st.write(
            "La línea piezométrica (HGL) suma altura geométrica y altura de presión. "
            "Indica la altura que alcanzaría el fluido en un piezómetro conectado idealmente a la tubería."
        )
    with c2:
        st.latex(r"EGL=z+\frac{p}{\rho g}+\frac{V^2}{2g}")
        st.write(
            "La línea de energía (EGL) agrega la altura de velocidad. En el modelo ideal sin pérdidas, "
            "la energía total permanece constante entre las dos secciones."
        )

    st.latex(r"EGL-HGL=\frac{V^2}{2g}")
    st.plotly_chart(make_energy_figure(result), width="stretch", config={"displaylogo": False})
    st.markdown("#### Cómo se reparte la energía en cada sección")
    st.plotly_chart(make_head_bars(result), width="stretch", config={"displaylogo": False})
    st.info(
        "La HGL ayuda a visualizar presión + cota; la EGL agrega velocidad. Esa lectura será clave cuando analices pérdidas reales o máquinas hidráulicas.",
        icon="💡"
    )

with tabs[5]:
    st.subheader("Aplicaciones de Continuidad y Bernoulli")
    st.write("Estas relaciones aparecen constantemente en tuberías, boquillas, medición de caudal, sistemas de bombeo y equipos de proceso.")

    a1, a2 = st.columns(2, gap="large")
    with a1:
        st.markdown("### Reducciones y boquillas")
        st.latex(r"A_1V_1=A_2V_2")
        st.write("Reducir el área aumenta la velocidad. En una boquilla ideal, una parte importante de la altura de presión puede transformarse en altura de velocidad.")

        st.markdown("### Venturi")
        st.write("Una diferencia de presión entre una sección amplia y una garganta permite inferir el caudal.")
        st.latex(r"Q=A_2\sqrt{\frac{2\left[\frac{p_1-p_2}{\rho g}+z_1-z_2\right]}{\frac{1}{A_2^2}-\frac{1}{A_1^2}}}")
        st.caption("La expresión mostrada corresponde al modelo ideal implementado. Un medidor real requiere coeficiente de descarga y consideración de pérdidas.")

        st.markdown("### Descarga de un depósito")
        st.write("Si la superficie libre es muy grande, su velocidad puede aproximarse a cero. Si superficie y descarga están a presión atmosférica, Bernoulli conduce a Torricelli:")
        st.latex(r"V=\sqrt{2g\Delta z}")
        st.latex(r"Q=A\,\sqrt{2g\Delta z}")

    with a2:
        st.markdown("### Cambios de elevación")
        st.write("Cuando el diámetro no cambia, la velocidad permanece aproximadamente constante y Bernoulli permite ver con claridad el intercambio entre presión y cota.")
        st.latex(r"\frac{p_1-p_2}{\rho g}=z_2-z_1\qquad\text{si }V_1=V_2")

        st.markdown("### Sistemas de máquinas")
        st.write("Una bomba agrega energía al fluido. La presión, el caudal y la altura de operación dependen de la interacción entre la máquina y la instalación.")

        st.markdown("### Instrumentación")
        st.write("La lectura de presión antes y después de restricciones, válvulas o equipos permite interpretar qué parte de la energía se conserva, se transforma o se disipa.")

        st.markdown("### Diseño mecánico e industrial")
        st.write("En piping, skids, sistemas de refrigeración, lubricación, hidráulica industrial y servicios de planta, estas ecuaciones son el punto de partida para definir diámetros, velocidades y requerimientos de energía.")

with tabs[6]:
    st.subheader("Del Bernoulli ideal a una máquina hidráulica")
    st.write(
        "Cuando una bomba aparece en el sistema, Bernoulli deja de ser solo un balance entre presión, velocidad y cota: "
        "se transforma en una herramienta para pensar cuánta energía necesita el fluido para cumplir una tarea real."
    )
    st.latex(r"\frac{p_1}{\rho g}+\alpha_1\frac{V_1^2}{2g}+z_1+h_p-h_t-h_L=\frac{p_2}{\rho g}+\alpha_2\frac{V_2^2}{2g}+z_2")

    c1, c2, c3 = st.columns(3)
    with c1:
        latex_card("Altura agregada por bomba", r"h_p", "Energía mecánica por unidad de peso que la bomba entrega al fluido.")
    with c2:
        latex_card("Altura extraída por turbina", r"h_t", "Energía por unidad de peso retirada del fluido por una máquina motriz.")
    with c3:
        latex_card("Pérdidas", r"h_L", "Energía mecánica disipada por fricción, accesorios, válvulas y otros elementos reales.")

    st.markdown("### Qué debes pensar cuando analices una bomba")
    st.markdown(
        """
1. Qué caudal necesitas mover (Q).
2. Qué cambio de cota debe vencer el sistema (z₂ - z₁).
3. Qué presiones necesitas mantener en succión y descarga.
4. Qué velocidades aparecen según los diámetros elegidos.
5. Cuánta energía se pierde por fricción y accesorios.
6. Qué energía adicional debe entregar la bomba para cerrar el balance.
"""
    )

    st.markdown("### Vista numérica simplificada")
    q_for_pump = result.Q_m3s
    pc1, pc2 = st.columns(2)
    with pc1:
        hp = st.slider("Altura agregada por la bomba hₚ [m]", min_value=0.0, max_value=100.0, value=25.0, step=1.0)
    with pc2:
        eta = st.slider("Eficiencia de bomba η", min_value=0.20, max_value=1.00, value=0.75, step=0.01)

    Ph, Pshaft = pump_power(rho, q_for_pump, hp, eta)
    st.latex(r"P_h=\rho gQh_p")
    st.latex(r"P_{eje}=\frac{P_h}{\eta}")

    p1c, p2c, p3c = st.columns(3)
    p1c.metric("Caudal usado", f"{q_for_pump*1000:.2f} L/s")
    p2c.metric("Potencia hidráulica", f"{Ph:.2f} kW")
    p3c.metric("Potencia de eje idealizada", f"{Pshaft:.2f} kW")

    st.markdown("### Lectura de diseño")
    st.markdown(
        """
- Si el sistema exige más altura estática o más pérdidas, la bomba debe agregar más energía.
- Si aumentas demasiado la velocidad al reducir diámetros, la penalización energética futura crece.
- Pensar bien las presiones y las cotas desde ahora facilita después la selección de bomba, potencia y eficiencia.
"""
    )

    st.info(
        "La idea central no es pensar la bomba como un equipo que da presión, sino como una máquina que entrega energía al fluido dentro de un sistema completo.",
        icon="⚙️"
    )

st.divider()
st.caption("GG DIMEC · MechLab · Herramienta pedagógica de Mecánica de Fluidos.")
