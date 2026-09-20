from __future__ import annotations

import math
import streamlit as st

from modules.ui_brand import render_app_header
from modules.fluid_real_data import FLUIDS, ROUGHNESS, FITTINGS, PRESETS
from modules.fluid_real_engine import solve_losses, equivalent_length, G
from modules.fluid_real_plotter import (
    make_pipe_schematic,
    make_moody_chart,
    make_loss_breakdown,
    make_relative_energy_figure,
    expand_accessories,
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
.gg-mini{
  border:1px solid var(--gg-line);
  border-radius:12px;
  padding:.75rem .9rem;
  background:#fff;
  min-height:132px;
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
    title="Flujo Real en Tuberías · Reynolds y Pérdidas",
    subtitle="Viscosidad · régimen de flujo · rugosidad · factor de fricción · Darcy–Weisbach · pérdidas menores.",
    section="MECÁNICA DE FLUIDOS",
    logo_width=188,
)


def latex_card(title: str, formula: str, caption: str):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.latex(formula)
        st.caption(caption)


CASE_GUIDES = {
    "Agua · línea de acero industrial": {
        "focus": "Caso base de piping industrial: diámetro moderado, varios accesorios y efecto combinado de pérdidas distribuidas y localizadas.",
        "what_to_watch": [
            "cómo se reparte la pérdida entre tubería recta y accesorios;",
            "cómo la rugosidad del acero afecta el factor de fricción;",
            "cómo cambia la caída de presión cuando aumenta el caudal.",
        ],
    },
    "Agua · tubería PVC": {
        "focus": "Caso de tubería lisa y relativamente larga, útil para contrastar longitud elevada con rugosidad baja.",
        "what_to_watch": [
            "la contribución dominante de la longitud total;",
            "la diferencia entre rugosidad absoluta pequeña y rugosidad relativa;",
            "la sensibilidad de la pérdida a cambios en diámetro y velocidad.",
        ],
    },
    "Aceite hidráulico · línea de máquina": {
        "focus": "Caso viscoso pensado para mostrar que un fluido más viscoso puede modificar fuertemente Reynolds y el régimen del flujo.",
        "what_to_watch": [
            "el descenso del número de Reynolds por efecto de la viscosidad;",
            "cómo cambia el método de cálculo del factor de fricción si el régimen se aproxima al laminar;",
            "por qué una línea corta puede igualmente presentar pérdidas relevantes si el fluido es viscoso.",
        ],
    },
}


# ---------------------------------------------------------------------
# Sidebar inputs
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("Caso de estudio")
    preset_name = st.selectbox("Configuración", list(PRESETS.keys()))
    preset = PRESETS[preset_name]

    st.divider()
    st.header("Fluido")
    fluid_name = st.selectbox(
        "Fluido",
        list(FLUIDS.keys()),
        index=list(FLUIDS.keys()).index(preset["fluid"]) if preset["fluid"] in FLUIDS else 0,
        key=f"fluid_{preset_name}"
    )
    fluid = FLUIDS[fluid_name]

    if fluid["rho"] is None:
        rho = st.number_input("Densidad ρ [kg/m³]", min_value=1.0, value=1000.0, step=10.0)
        mu = st.number_input("Viscosidad dinámica μ [Pa·s]", min_value=1e-6, value=1.0e-3, format="%.6f")
    else:
        rho = float(fluid["rho"])
        mu = float(fluid["mu"])
        st.latex(rf"\rho={rho:.1f}\,\mathrm{{kg/m^3}}")
        st.latex(rf"\mu={mu:.4g}\,\mathrm{{Pa\cdot s}}")

    st.divider()
    st.header("Tubería")
    L_m = st.number_input("Longitud L [m]", min_value=0.0, value=float(preset["L_m"]), step=1.0, key=f"L_{preset_name}")
    D_mm = st.number_input("Diámetro interior D [mm]", min_value=1.0, value=float(preset["D_mm"]), step=5.0, key=f"D_{preset_name}")
    Q_Ls = st.number_input("Caudal Q [L/s]", min_value=0.0, value=float(preset["Q_Ls"]), step=0.5, key=f"Q_{preset_name}")

    st.divider()
    st.header("Rugosidad")
    rough_name = st.selectbox(
        "Superficie interior",
        list(ROUGHNESS.keys()),
        index=list(ROUGHNESS.keys()).index(preset["roughness"]) if preset["roughness"] in ROUGHNESS else 0,
        key=f"rough_{preset_name}"
    )
    if ROUGHNESS[rough_name] is None:
        epsilon_mm = st.number_input("Rugosidad absoluta ε [mm]", min_value=0.0, value=0.045, step=0.005, format="%.4f")
    else:
        epsilon_mm = float(ROUGHNESS[rough_name])
        st.latex(rf"\varepsilon={epsilon_mm:.4g}\,\mathrm{{mm}}")

    st.divider()
    st.header("Accesorios")
    defaults = list(preset["fittings"].keys())
    selected = st.multiselect(
        "Elementos con pérdida localizada",
        list(FITTINGS.keys()),
        default=defaults,
        key=f"fittings_{preset_name}"
    )

    accessory_rows = []
    for name in selected:
        item = FITTINGS[name]
        default_count = int(preset["fittings"].get(name, 1))
        count = st.number_input(f"Cantidad · {name}", min_value=0, value=default_count, step=1, key=f"n_{preset_name}_{name}")
        if item["K"] is None:
            K = st.number_input(f"K · {name}", min_value=0.0, value=1.0, step=0.1, key=f"K_{preset_name}_{name}")
        else:
            K = float(item["K"])
        accessory_rows.append({
            "name": name,
            "symbol": item["symbol"],
            "count": int(count),
            "K": K,
            "K_total": K * int(count),
            "note": item["note"],
        })

    K_total = sum(r["K_total"] for r in accessory_rows)

    st.divider()
    st.caption(
        "Las rugosidades y K predefinidos son valores pedagógicos de referencia. Para diseño real deben reemplazarse por datos de norma, fabricante o proyecto."
    )


result = solve_losses(
    rho=rho,
    mu=mu,
    L_m=L_m,
    D_mm=D_mm,
    Q_Ls=Q_Ls,
    epsilon_mm=epsilon_mm,
    K_total=K_total,
)

if not result.ok:
    st.error(result.message)
    st.stop()

expanded_accessories = expand_accessories(accessory_rows)
case_guide = CASE_GUIDES.get(preset_name, {"focus": preset["description"], "what_to_watch": []})

st.markdown(
    f"""
<div class="gg-case">
  <div style="font-size:.78rem;font-weight:800;color:#f28e1c;letter-spacing:.08em">CASO DE ESTUDIO</div>
  <h3 style="margin:.35rem 0 .25rem 0">{preset_name}</h3>
  <div style="color:#737986">{preset['description']}</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="gg-note">
<b>Cómo leer este caso:</b> {case_guide['focus']}
</div>
""",
    unsafe_allow_html=True,
)

if case_guide["what_to_watch"]:
    st.markdown("#### Qué conviene mirar en este ejemplo")
    cols = st.columns(len(case_guide["what_to_watch"]))
    for col, text in zip(cols, case_guide["what_to_watch"]):
        with col:
            st.markdown(f"<div class='gg-mini'>{text}</div>", unsafe_allow_html=True)


tabs = st.tabs([
    "📘 Cómo usar",
    "🧩 Sistema",
    "🌊 Reynolds",
    "📉 Fricción · Moody",
    "⚙️ Pérdidas",
    "📈 HGL · EGL",
    "🏭 Diseño y aplicaciones",
    "🔧 Impacto en bombas",
])

# ---------------------------------------------------------------------
# Cómo usar
# ---------------------------------------------------------------------
with tabs[0]:
    c1, c2 = st.columns([1.05, .95], gap="large")

    with c1:
        st.subheader("Qué agrega el flujo real")
        st.write(
            "En el módulo ideal la energía mecánica se conservaba entre dos secciones. "
            "En una tubería real, la viscosidad y las perturbaciones introducidas por accesorios disipan parte de esa energía. "
            "Por eso ahora ya no basta con escribir Bernoulli ideal: debemos incorporar pérdidas distribuidas y pérdidas localizadas."
        )

        st.markdown("#### Ruta de cálculo ampliada")
        route = [
            ("1. Definir los datos de entrada", "Selecciona el fluido, fija ρ y μ, y define longitud L, diámetro interior D, caudal Q y accesorios."),
            ("2. Obtener la geometría básica", "Con D se calcula el área interior A de la tubería. Esa área es la sección real por donde circula el flujo."),
            ("3. Calcular la velocidad media", "A partir de Q y A se calcula V=Q/A. Esta velocidad es la variable que conecta continuidad con energía y pérdidas."),
            ("4. Calcular Reynolds", "Con ρ, μ, V y D se identifica si el comportamiento del flujo está dominado por la viscosidad o por la inercia."),
            ("5. Clasificar el régimen", "Se determina si el flujo es laminar, de transición o turbulento. Esta clasificación define cómo se calcula el factor de fricción."),
            ("6. Incorporar la rugosidad", "Se toma la rugosidad absoluta ε del material y luego se calcula la rugosidad relativa ε/D, porque el efecto de la pared depende del tamaño del diámetro."),
            ("7. Determinar el factor de fricción Darcy", "En laminar se usa 64/Re. En turbulento se utiliza Colebrook–White, y se muestran además Haaland y Swamee–Jain para comparación."),
            ("8. Calcular la pérdida distribuida", "Con Darcy–Weisbach se determina h_f, que representa la pérdida a lo largo del tramo recto."),
            ("9. Calcular pérdidas localizadas", "Cada accesorio aporta una pérdida K·V²/(2g). Se suman todas para obtener h_m."),
            ("10. Obtener la pérdida total", "La pérdida total h_L=h_f+h_m permite estimar la caída de presión Δp y visualizar la caída de HGL y EGL."),
        ]
        for title, body in route:
            st.markdown(f"<div class='gg-step'><b>{title}</b><br>{body}</div>", unsafe_allow_html=True)

    with c2:
        latex_card("Continuidad", r"Q=AV", "Relaciona el caudal con el área disponible y la velocidad media.")
        latex_card("Número de Reynolds", r"Re=\frac{\rho V D}{\mu}=\frac{V D}{\nu}", "Compara los efectos inerciales y viscosos del flujo.")
        latex_card("Darcy–Weisbach", r"h_f=f\frac{L}{D}\frac{V^2}{2g}", "Pérdida distribuida por roce a lo largo de la tubería.")
        latex_card("Pérdidas localizadas", r"h_m=\sum K_i\frac{V^2}{2g}", "Pérdidas debidas a entradas, salidas, válvulas, codos y accesorios.")
        latex_card("Pérdida total", r"h_L=h_f+h_m", "Pérdida total de energía mecánica por unidad de peso del fluido.")

        st.markdown("#### Qué significa una pérdida")
        st.write(
            "Una pérdida de carga no significa que desaparezca masa ni caudal. Significa que parte de la energía mecánica ordenada del flujo "
            "se transforma irreversiblemente en energía interna por acción de la viscosidad y de la turbulencia."
        )

# ---------------------------------------------------------------------
# Sistema
# ---------------------------------------------------------------------
with tabs[1]:
    st.subheader("Sistema de tubería y accesorios")
    st.write(
        "La visual superior es una representación pedagógica del sistema. No pretende ubicar con exactitud espacial cada accesorio, "
        "sino ayudarte a leer el recorrido del flujo y a identificar qué variables intervienen en el cálculo."
    )

    st.markdown(
        """
<div class="gg-warning">
<b>Importante:</b> los accesorios se distribuyen de forma referencial a lo largo del tramo para que la lectura sea más clara. 
En este modelo, la posición exacta de cada accesorio no altera el resultado; lo que sí altera el resultado es su cantidad, su coeficiente $K$ y el estado del flujo.
</div>
""",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.45, .9], gap="large")
    with left:
        st.plotly_chart(
            make_pipe_schematic(result.L_m, result.D_m, result.Q_m3s, accessory_rows),
            width="stretch",
            config={"displaylogo": False},
        )
    with right:
        st.markdown("#### Cómo leer el esquema")
        st.markdown(
            """
- **Sección 1**: plano de entrada del sistema, desde donde se evalúa el estado inicial.
- **Sección 2**: plano de salida del sistema, donde se compara el estado final.
- **D**: diámetro interior útil de la tubería. Está acotado a la izquierda para que no se confunda con la longitud.
- **L**: longitud del tramo recto modelado. Aparece bajo la tubería.
- **Q**: caudal impuesto al sistema. Se muestra sobre la línea de flujo.
- **Números naranjos**: accesorios recorridos por el fluido en el sentido del flujo.
- **Línea punteada naranja**: eje o línea media del flujo, usada solo como guía visual.
"""
        )

        st.markdown("#### Idea física")
        st.write(
            "Piensa el esquema como una tubería vista lateralmente. El fluido entra por la sección 1, recorre el tramo recto, "
            "atraviesa los accesorios indicados y sale por la sección 2."
        )

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Diámetro interior", f"{result.D_m*1000:.1f} mm")
    s2.metric("Longitud", f"{result.L_m:.2f} m")
    s3.metric("Caudal", f"{result.Q_m3s*1000:.3f} L/s")
    s4.metric("Velocidad media", f"{result.V_ms:.3f} m/s")

    st.markdown("#### Secuencia del recorrido")
    if expanded_accessories:
        sequence_table = []
        for item in expanded_accessories:
            sequence_table.append({
                "Orden": item["order"],
                "Elemento": item["name"],
                "Símbolo": item["symbol"],
                "K": f"{item['K']:.3g}",
                "Interpretación": f"Pérdida localizada asociada a {item['name'].lower()}.",
            })
        st.dataframe(sequence_table, width="stretch", hide_index=True)
    else:
        st.info("No se han definido accesorios para este caso.")

    st.markdown("#### Variables geométricas y de flujo")
    g1, g2 = st.columns(2)
    with g1:
        latex_card(
            "Área transversal",
            rf"A=\frac{{\pi D^2}}{{4}}={result.A_m2:.6g}\,\mathrm{{m^2}}",
            "Área interior efectiva de la tubería. Se calcula con el diámetro interior, no con el exterior."
        )
    with g2:
        latex_card(
            "Velocidad media",
            rf"V=\frac{{Q}}{{A}}={result.V_ms:.4f}\,\mathrm{{m/s}}",
            "Velocidad media asociada al caudal y al área interior. Si D disminuye, V aumenta para un mismo caudal."
        )

# ---------------------------------------------------------------------
# Reynolds
# ---------------------------------------------------------------------
with tabs[2]:
    st.subheader("Número de Reynolds y régimen de flujo")
    st.write(
        "Reynolds compara la importancia de la inercia del movimiento con los efectos viscosos. No es una velocidad ni una fuerza, "
        "sino un parámetro adimensional que ayuda a clasificar el comportamiento del flujo."
    )

    st.latex(r"Re=\frac{\rho V D}{\mu}")
    st.latex(r"\nu=\frac{\mu}{\rho}")
    st.latex(r"Re=\frac{V D}{\nu}")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Re", f"{result.Re:,.0f}")
    r2.metric("Régimen", result.regime)
    r3.metric("ν", f"{result.nu:.3e} m²/s")
    r4.metric("V", f"{result.V_ms:.3f} m/s")

    st.markdown("#### Cómo interpretar el resultado")
    c1, c2, c3 = st.columns(3)
    with c1:
        latex_card("Laminar", r"Re<2300", "El movimiento se mantiene ordenado y los efectos viscosos tienen fuerte control sobre el flujo.")
    with c2:
        latex_card("Transición", r"2300\le Re<4000", "El comportamiento es inestable; pequeñas perturbaciones pueden cambiar apreciablemente el régimen.")
    with c3:
        latex_card("Turbulento", r"Re\ge 4000", "Las fluctuaciones y la mezcla se intensifican, y la rugosidad de la pared puede tener un papel importante.")

    st.markdown("#### Qué significa cada símbolo")
    st.markdown(
        """
- $\rho$: densidad del fluido.
- $V$: velocidad media del flujo.
- $D$: diámetro interior característico.
- $\mu$: viscosidad dinámica.
- $\nu$: viscosidad cinemática.
"""
    )

    if result.transition_warning:
        st.warning(
            "El caso actual está en la zona de transición. MechLab entrega una estimación pedagógica de $f$ para mantener el balance de pérdidas, pero no debe tratarse como valor de diseño.",
            icon="⚠️"
        )

# ---------------------------------------------------------------------
# Fricción & Moody
# ---------------------------------------------------------------------
with tabs[3]:
    st.subheader("Factor de fricción de Darcy")

    st.write(
        "El factor de fricción $f$ resume, dentro de Darcy–Weisbach, cómo el régimen y la condición de la pared afectan la disipación. "
        "Su valor no se inventa: depende del régimen del flujo y de la rugosidad relativa."
    )

    c1, c2 = st.columns([.92, 1.08], gap="large")
    with c1:
        st.markdown("#### Rugosidad relativa")
        st.latex(r"\frac{\varepsilon}{D}")
        st.latex(rf"\frac{{\varepsilon}}{{D}}={result.rel_roughness:.4g}")
        st.caption("La rugosidad absoluta $\varepsilon$ por sí sola no basta; su efecto debe compararse con el diámetro interior.")

        st.markdown("#### Método activo")
        st.write(f"**{result.f_method}**")
        if result.f is not None:
            st.latex(rf"f={result.f:.6f}")

        if result.regime == "Laminar":
            st.latex(r"f=\frac{64}{Re}")
            st.write("En régimen laminar, el factor de fricción no depende de la rugosidad en esta formulación idealizada.")
        else:
            st.latex(
                r"\frac{1}{\sqrt f}="
                r"-2\log_{10}\left("
                r"\frac{\varepsilon/D}{3.7}"
                r"+\frac{2.51}{Re\sqrt f}"
                r"\right)"
            )
            st.write(
                "Colebrook–White es una ecuación implícita en $f$, de modo que la aplicación la resuelve iterativamente. "
                "Eso permite representar correctamente el caso turbulento sin depender solo de aproximaciones rápidas."
            )

        if result.f_haaland is not None:
            st.markdown("#### Aproximaciones explícitas de apoyo")
            st.latex(
                r"\frac{1}{\sqrt f}="
                r"-1.8\log_{10}\left["
                r"\left(\frac{\varepsilon/D}{3.7}\right)^{1.11}"
                r"+\frac{6.9}{Re}"
                r"\right]"
            )
            st.latex(rf"f_{{Haaland}}={result.f_haaland:.6f}")
            st.latex(
                r"f_{SJ}=\frac{0.25}{"
                r"\left[\log_{10}\left("
                r"\frac{\varepsilon/D}{3.7}+\frac{5.74}{Re^{0.9}}"
                r"\right)\right]^2}"
            )
            st.latex(rf"f_{{SJ}}={result.f_swamee_jain:.6f}")
            st.caption("Estas expresiones sirven para comparación o estimación rápida; el valor activo mostrado por la aplicación proviene del método indicado arriba.")

    with c2:
        st.markdown("#### Diagrama tipo Moody")
        st.plotly_chart(
            make_moody_chart(result.Re, result.f, result.rel_roughness),
            width="stretch",
            config={"displaylogo": False},
        )
        st.markdown(
            """
**Cómo leer el gráfico:**
- el eje horizontal muestra Reynolds en escala logarítmica;
- el eje vertical muestra el factor de fricción Darcy;
- la banda sombreada indica la zona de transición;
- el punto naranjo marca el estado actual del problema.
"""
        )

# ---------------------------------------------------------------------
# Losses
# ---------------------------------------------------------------------
with tabs[4]:
    st.subheader("Pérdidas distribuidas y localizadas")

    st.markdown("### 1. Pérdida distribuida en la tubería")
    st.latex(r"h_f=f\frac{L}{D}\frac{V^2}{2g}")
    st.latex(rf"h_f={result.hf_major_m:.4f}\,\mathrm{{m}}")
    st.write(
        "Esta pérdida representa el roce continuo a lo largo del tramo recto. "
        "Aumenta con la longitud, con el factor de fricción y con la altura de velocidad."
    )

    st.markdown("### 2. Pérdidas localizadas")
    st.latex(r"h_m=\sum K_i\frac{V^2}{2g}")
    st.latex(rf"\sum K_i={result.K_total:.4f}")
    st.latex(rf"h_m={result.hm_minor_m:.4f}\,\mathrm{{m}}")
    st.write(
        "Cada accesorio produce perturbaciones y separación del flujo, lo que se traduce en una pérdida adicional concentrada en su zona de influencia."
    )

    if accessory_rows:
        table_rows = []
        for row in accessory_rows:
            Leq = equivalent_length(row["K_total"], result.D_m, result.f)
            table_rows.append({
                "Elemento": row["name"],
                "Cantidad": row["count"],
                "K unitario": f"{row['K']:.3g}",
                "ΣK": f"{row['K_total']:.3g}",
                "Leq [m]": "—" if Leq is None else f"{Leq:.2f}",
                "Interpretación": row["note"],
            })
        st.dataframe(table_rows, width="stretch", hide_index=True)

        st.write("La longitud equivalente se muestra como una forma alternativa de entender cuánto “pesa” hidráulicamente un accesorio dentro del sistema:")
        st.latex(r"L_{eq}=\frac{K D}{f}")

    st.markdown("### 3. Pérdida total")
    st.latex(r"h_L=h_f+h_m")
    st.latex(rf"h_L={result.hL_total_m:.4f}\,\mathrm{{m}}")
    st.latex(r"\Delta p=\rho g h_L")
    st.latex(rf"\Delta p={result.dp_total_Pa/1000:.3f}\,\mathrm{{kPa}}")

    m1, m2, m3 = st.columns(3)
    m1.metric("Pérdida distribuida", f"{result.hf_major_m:.3f} m")
    m2.metric("Pérdidas localizadas", f"{result.hm_minor_m:.3f} m")
    m3.metric("Pérdida total", f"{result.hL_total_m:.3f} m")

    st.plotly_chart(
        make_loss_breakdown(result.hf_major_m, accessory_rows, result.velocity_head_m),
        width="stretch",
        config={"displaylogo": False},
    )
    st.caption("La barra negra corresponde a la tubería recta y las barras naranjas muestran la contribución de cada familia de accesorios.")

# ---------------------------------------------------------------------
# HGL / EGL
# ---------------------------------------------------------------------
with tabs[5]:
    st.subheader("Cómo cae la energía en una tubería real")

    st.write(
        "Con diámetro constante, la distancia entre EGL y HGL permanece igual a la altura de velocidad. "
        "Lo que cambia es que ambas líneas descienden a medida que el sistema pierde energía."
    )

    st.latex(r"EGL-HGL=\frac{V^2}{2g}")
    st.latex(rf"\frac{{V^2}}{{2g}}={result.velocity_head_m:.4f}\,\mathrm{{m}}")

    st.plotly_chart(
        make_relative_energy_figure(result.L_m, result.velocity_head_m, result.hf_major_m, accessory_rows),
        width="stretch",
        config={"displaylogo": False},
    )

    st.markdown("#### Cómo leer el gráfico")
    st.markdown(
        """
- la pendiente continua representa la pérdida distribuida a lo largo de la tubería;
- los pequeños saltos verticales representan pérdidas localizadas en accesorios;
- la separación entre EGL y HGL es la altura de velocidad $V^2/(2g)$;
- la cota absoluta no es lo importante aquí: lo importante es la **caída de energía** entre entrada y salida.
"""
    )

# ---------------------------------------------------------------------
# Design applications
# ---------------------------------------------------------------------
with tabs[6]:
    st.subheader("Diseño mecánico e industrial")

    d1, d2 = st.columns(2, gap="large")
    with d1:
        st.markdown("### Qué mirar al elegir un diámetro")
        st.write(
            "El diámetro modifica simultáneamente el área, la velocidad, Reynolds, la rugosidad relativa y la pérdida de carga. "
            "Por eso no se debe seleccionar solo por espacio disponible o por costumbre."
        )
        st.latex(r"V=\frac{4Q}{\pi D^2}")
        st.write(
            "Si se reduce $D$, la velocidad sube rápidamente. Como muchas pérdidas contienen el término $V^2/(2g)$, "
            "una reducción aparentemente pequeña de diámetro puede aumentar de forma importante la potencia requerida para bombear."
        )

        st.markdown("### Qué mirar en una línea de máquina")
        st.markdown(
            """
- velocidad del fluido;
- régimen de flujo;
- longitud total del recorrido;
- material y condición superficial interna;
- cantidad de codos, válvulas y derivaciones;
- temperatura y viscosidad del fluido;
- caída de presión admisible;
- exigencia energética del sistema.
"""
        )

    with d2:
        st.markdown("### Dónde se aplica")
        st.markdown(
            """
- circuitos de refrigeración;
- lubricación de maquinaria;
- líneas hidráulicas;
- piping de proceso;
- skids industriales;
- servicios de agua;
- sistemas de impulsión y recirculación;
- alimentación de intercambiadores y equipos.
"""
        )

        st.markdown("### Cómo usar esto en ingeniería")
        st.write(
            "Este modelo sirve para comparar alternativas de diámetro, reconocer si un sistema está penalizado por demasiados accesorios, "
            "estimar el orden de magnitud de la caída de presión y preparar el paso hacia selección de bombas o análisis de curva de sistema."
        )

    st.info(
        "Una buena selección hidráulica busca equilibrio entre diámetro, velocidad, pérdida de carga, fabricación, costo, espacio y requerimiento energético.",
        icon="🧭"
    )

# ---------------------------------------------------------------------
# Pump impact
# ---------------------------------------------------------------------
with tabs[7]:
    st.subheader("Cómo estas pérdidas afectan una bomba")

    st.write(
        "La bomba debe aportar la energía que el sistema necesita para vencer diferencia de cota, diferencia de presión, cambios de velocidad y pérdidas. "
        "En esta etapa, el punto central es comprender que las pérdidas calculadas aquí pasan a formar parte directa de la altura que la bomba debe entregar."
    )

    st.latex(
        r"h_p="
        r"\left(\frac{p_2-p_1}{\rho g}\right)"
        r"+\left(\frac{V_2^2-V_1^2}{2g}\right)"
        r"+\left(z_2-z_1\right)"
        r"+h_L"
    )

    st.markdown("### Si solo miramos esta tubería de diámetro constante")
    st.write(
        "Si no existieran diferencia de cota ni cambio de velocidad entre extremos, entonces la parte mínima que la bomba debe compensar sería la pérdida total de carga del sistema."
    )
    st.latex(r"h_p\approx h_L")
    st.latex(rf"h_p\approx {result.hL_total_m:.4f}\,\mathrm{{m}}")

    st.markdown("### Potencia asociada a esa pérdida")
    eta = st.slider("Eficiencia de bomba η", min_value=0.20, max_value=1.00, value=0.75, step=0.01, key="eta_pump_loss")
    P_h_kW = rho * G * result.Q_m3s * result.hL_total_m / 1000.0
    P_shaft_kW = P_h_kW / eta if eta > 0 else math.inf

    st.latex(r"P_h=\rho gQh_p")
    st.latex(r"P_{eje}=\frac{P_h}{\eta}")

    p1, p2, p3 = st.columns(3)
    p1.metric("Altura asociada a pérdidas", f"{result.hL_total_m:.3f} m")
    p2.metric("Potencia hidráulica", f"{P_h_kW:.3f} kW")
    p3.metric("Potencia de eje", f"{P_shaft_kW:.3f} kW")

    st.markdown("### Qué debes pensar cuando luego pases a bombas")
    st.markdown(
        """
1. Qué caudal requiere realmente el proceso.
2. Qué altura estática existe entre origen y destino.
3. Qué presiones deben existir en ambos extremos.
4. Cuánto pierde la instalación al caudal de trabajo.
5. Cómo varían esas pérdidas cuando el caudal cambia.
6. Qué potencia y eficiencia serán necesarias para operar en el punto real.
"""
    )

    st.warning(
        "La pérdida calculada aquí es solo una parte de la altura total del sistema. Una selección de bomba real también debe considerar cotas, presiones, curvas de bomba, curva de sistema, eficiencia y condiciones de succión.",
        icon="⚙️"
    )

st.divider()
st.caption("GG DIMEC · MechLab · Herramienta pedagógica de Mecánica de Fluidos.")
