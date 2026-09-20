from __future__ import annotations

import streamlit as st

from modules.ui_brand import render_app_header
from modules.gdt_data import (
    CONTROL_FAMILIES,
    DATUM_EXAMPLES,
    INSPECTION_METHODS,
    ENGINEERING_CASES,
)
from modules.gdt_engine import (
    positional_error_2d,
    mmr_bonus,
    runout,
    parse_series,
    dof_after_datums,
)
from modules.gdt_plotter import (
    make_form_zone_figure,
    make_orientation_figure,
    make_position_figure,
    make_datum_321_figure,
    make_runout_figure,
    make_mmr_figure,
)

st.markdown(
    """
<style>
:root{
  --gg-orange:#f28e1c;
  --gg-orange-soft:#fff5ea;
  --gg-black:#111111;
  --gg-muted:#737986;
  --gg-line:#eceff2;
}
.block-container{
  max-width:1540px;
  padding-top:1.20rem !important;
  padding-bottom:2rem;
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
.gg-case{
  border:1px solid var(--gg-line);
  border-left:5px solid var(--gg-orange);
  border-radius:14px;
  padding:1rem 1.1rem;
  background:#fff;
  margin:.20rem 0 .85rem 0;
}
.gg-card{
  border:1px solid var(--gg-line);
  border-radius:14px;
  padding:1rem 1.05rem;
  background:#fff;
  margin:.10rem 0 .75rem 0;
  min-height:100%;
}
.gg-mini{
  border:1px solid var(--gg-line);
  border-radius:12px;
  padding:.85rem .95rem;
  background:#fff;
  min-height:120px;
}
.gg-symbol{
  display:inline-flex;
  min-width:48px;
  height:48px;
  align-items:center;
  justify-content:center;
  border:1px solid var(--gg-line);
  border-radius:10px;
  font-size:1.45rem;
  font-weight:800;
  background:#fff;
}
.gg-fcf{
  display:inline-flex;
  border:2px solid #171717;
  border-radius:2px;
  overflow:hidden;
  margin:.35rem 0;
  flex-wrap:wrap;
}
.gg-fcf > span{
  padding:.45rem .72rem;
  border-right:1px solid #171717;
  font-weight:750;
  background:#fff;
}
.gg-fcf > span:last-child{border-right:none;}
.gg-step{
  border:1px solid var(--gg-line);
  border-radius:12px;
  background:#fff;
  padding:.9rem 1rem;
  margin-bottom:.55rem;
}
.gg-step b{color:#1f2430;}
.gg-badge{
  display:inline-block;
  background:var(--gg-orange-soft);
  color:#b8660f;
  border:1px solid #f6d7b1;
  padding:.20rem .55rem;
  border-radius:999px;
  font-size:.80rem;
  font-weight:700;
  margin-right:.35rem;
}
</style>
""",
    unsafe_allow_html=True,
)

FORM_GUIDE = {
    "Rectitud": {
        "controls": "Controla la desviación de una línea real respecto de una línea ideal. Puede aplicarse sobre una generatriz, un eje derivado o una arista funcional.",
        "zone": "Dos líneas paralelas separadas por la tolerancia, o una zona cilíndrica si se controla un eje.",
        "drawing": "En plano suele ligarse a la línea o eje que interesa. Si la función está en el eje, hay que dejar claro que el control actúa sobre el eje derivado y no solamente sobre una generatriz visible.",
        "inspection": "Reloj comparador, prismas, V-blocks, palpado por CMM o escaneo con extracción de eje/recta asociada.",
        "mistakes": [
            "Confundir rectitud de superficie con rectitud de eje.",
            "Usar rectitud cuando en realidad importa la orientación respecto de otra cara.",
            "No definir longitud funcional de evaluación."
        ],
        "latex": [r"d_i\in[-t/2,\;t/2]", r"\mathcal{L}_{real}\subseteq \mathcal{Z}_{rectitud}"],
    },
    "Planitud": {
        "controls": "Controla cuán plana debe ser una superficie sin referirla a otra superficie. Es muy útil en apoyos, sellado y montaje.",
        "zone": "Dos planos paralelos separados por la tolerancia.",
        "drawing": "Se asigna directamente a la superficie. Conviene usarla cuando la superficie debe apoyarse por sí sola, no cuando la relación angular con otra cara es lo crítico.",
        "inspection": "Mesa de granito y reloj comparador, control preliminar con regla cuando corresponda, CMM o escaneo 3D con evaluación de planitud.",
        "mistakes": [
            "Usar planitud cuando lo que importa es paralelismo con la base.",
            "No considerar que una superficie puede cumplir tamaño y aun así no ser plana.",
            "Pedir planitudes muy finas sin capacidad real de fabricación o inspección."
        ],
        "latex": [r"\mathcal{S}_{real}\subseteq [\Pi_1,\Pi_2]", r"d(\Pi_1,\Pi_2)=t"],
    },
    "Redondez": {
        "controls": "Controla la redondez de cada sección circular independiente del eje global. En documentación internacional también encontrarás el término circularity. Es una tolerancia de forma sección por sección.",
        "zone": "Dos círculos concéntricos separados radialmente por la tolerancia.",
        "drawing": "Se usa en diámetros donde interesa la redondez local. Si también importa la rectitud/eje global, probablemente no basta con redondez sola.",
        "inspection": "Equipo de redondez, medición por secciones con reloj comparador o CMM, o evaluación seccional en metrología 3D.",
        "mistakes": [
            "Creer que redondez controla todo el cilindro completo.",
            "Usarla donde realmente se necesita cilindricidad.",
            "Interpretarla como concentricidad respecto de otro elemento."
        ],
        "latex": [r"R_{ext}-R_{int}=t", r"\mathcal{C}_{real}\subseteq \mathcal{Z}_{circ}"],
    },
    "Cilindricidad": {
        "controls": "Controla la forma integral de una superficie cilíndrica, combinando errores de redondez, rectitud generatriz y variación a lo largo del cilindro.",
        "zone": "Dos cilindros coaxiales separados radialmente por la tolerancia.",
        "drawing": "Es apropiada en asientos de rodamientos, sellos y diámetros que deben comportarse bien a lo largo de toda la longitud funcional.",
        "inspection": "CMM, equipo especializado o escaneo metrológico con evaluación cilíndrica completa; controles parciales con reloj comparador entregan solo una verificación parcial.",
        "mistakes": [
            "Asumir que varias mediciones locales equivalen a una evaluación completa.",
            "Usarla donde bastaría redondez o rectitud por costo.",
            "No distinguir entre control del cilindro y control de su orientación respecto de una base."
        ],
        "latex": [r"R_{ext}-R_{int}=t", r"\mathcal{S}_{cil}\subseteq \mathcal{Z}_{cil}"],
    },
}

ORIENTATION_GUIDE = {
    "Paralelismo": {
        "controls": "Mantiene una línea, eje o superficie paralela a un referencia funcional. Sirve cuando importa la orientación relativa entre elementos.",
        "drawing": "El marco de tolerancia debe apuntar a la superficie o elemento y declarar claramente la referencia especificada. Es una tolerancia relacional.",
        "inspection": "Mesa de granito + reloj comparador, CMM o verificación con útil de montaje según la pieza.",
        "mistakes": [
            "Usar paralelismo cuando en realidad importa planitud.",
            "No definir una referencia especificada coherente con la función.",
            "Pensar que tamaño correcto garantiza paralelismo."
        ],
        "latex": [r"\mathcal{G}_{real}\subseteq\mathcal{Z}_{\parallel A}"],
    },
    "Perpendicularidad": {
        "controls": "Garantiza que una línea, eje o superficie se mantenga a 90° respecto de la referencia. Muy usada en hombros, caras de apoyo y perforaciones.",
        "drawing": "Se especifica respecto de una referencia que represente la referencia funcional del montaje o del apoyo real.",
        "inspection": "Escuadra + reloj comparador en controles preliminares, útil dedicado o CMM para liberación formal.",
        "mistakes": [
            "Confundir perpendicularidad con posición.",
            "Seleccionar como referencia una cara que no representa la función del montaje.",
            "No definir si el control actúa sobre superficie o eje."
        ],
        "latex": [r"\mathcal{G}_{real}\subseteq\mathcal{Z}_{\perp A}"],
    },
}

POSITION_NOTES = [
    "La posición no controla solo ‘centros dentro de una cota aparente’: protege ensamblaje, paso de pernos, coincidencia de ejes y repetibilidad de montaje.",
    "La zona de posición suele expresarse como un cilindro de diámetro t alrededor de la posición teórica exacta.",
    "La lectura metrológica requiere decidir cómo se establece el sistema A-B-C y cómo se extrae el centro o eje real.",
]

RUNOUT_NOTES = [
    "Oscilación circular: lectura de una sección durante una vuelta.",
    "Oscilación total: lectura de toda la superficie barrida durante rotación y desplazamiento axial.",
    "Si la referencia de rotación está mal definida, el resultado de oscilación pierde sentido funcional.",
]

MMR_NOTES = [
    "La requisito de máximo material protege el peor caso de ensamblaje.",
    "Si el tamaño real se aleja del máximo material, aparece tolerancia geométrica adicional o bonus.",
    "La condición virtual sirve para pensar funcionalmente el límite del elemento en acoplamiento.",
]

def render_fcf(cells: list[str]):
    html = '<div class="gg-fcf">' + ''.join(f'<span>{c}</span>' for c in cells) + '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_step(number: str, title: str, text: str):
    st.markdown(
        f'<div class="gg-step"><b>{number}. {title}</b><br>{text}</div>',
        unsafe_allow_html=True,
    )


render_app_header(
    title="Tolerancias Geométricas · ISO GPS / GD&T",
    subtitle="Forma · orientación · posición · referencias · oscilación · MMR/LMR · teoría aplicada, plano e inspección.",
    section="METROLOGÍA Y FABRICACIÓN",
    logo_width=188,
)

st.markdown(
    """
<div class="gg-note">
<b>Enfoque de esta versión:</b> no solo mostrar la herramienta, sino explicar <b>qué controla cada tolerancia</b>,
<b>qué zona geométrica representa</b>, <b>cómo se coloca en plano</b>, <b>cómo se inspecciona</b> y <b>qué errores de interpretación son comunes</b>.
</div>

<div class="gg-note">
<b>Terminología usada:</b> se prioriza el lenguaje técnico empleado en Chile y en la NCh2203: <b>marco de tolerancia</b>, <b>referencia especificada</b>, <b>redondez</b>, <b>oscilación circular</b> y <b>oscilación total</b>. Para algunos conceptos, como <b>planitud</b>, se mantiene además la denominación más habitual en software y práctica industrial. Entre paréntesis se conservan términos internacionales como <b>run-out</b> cuando ayudan a relacionar documentación de fabricante.
</div>
""",
    unsafe_allow_html=True,
)


tabs = st.tabs([
    "📘 Cómo usar",
    "🧩 Marco de tolerancia",
    "◻️ Forma",
    "📐 Orientación",
    "⌖ Posición",
    "🅰️ Referencias A-B-C",
    "↗️ Oscilación",
    "Ⓜ️ MMR / LMR",
    "🔬 Inspección e ingeniería",
])

# ----------------------------------------------------------------------------------
# TAB 1: Cómo usar
# ----------------------------------------------------------------------------------
with tabs[0]:
    st.subheader("Ruta didáctica · del requisito funcional a la decisión de control")

    c1, c2 = st.columns([1.0, 1.0], gap="large")
    with c1:
        render_step("1", "Parte por la función", "Antes de pensar en un símbolo, pregúntate qué debe ocurrir en la pieza: apoyar, girar, sellar, ensamblar, centrarse o ubicarse respecto de otra.")
        render_step("2", "Separa tamaño y geometría", "Un diámetro puede estar dentro de tolerancia y aun así no funcionar si el elemento no es cilíndrico, no está orientado o quedó mal ubicado.")
        render_step("3", "Identifica el tipo de control", "Si te preocupa la forma de una sola superficie, probablemente estás en forma. Si importa la relación con otra referencia, ya estás en orientación, localización o oscilación.")
        render_step("4", "Piensa en la zona de tolerancia", "Toda tolerancia geométrica define una zona: entre dos líneas, entre dos planos, entre dos cilindros, alrededor de una posición teórica o durante una rotación.")
        render_step("5", "Define referencias funcionales A-B-C", "La referencia especificada (datum) debe representar cómo la pieza se apoya, se monta o se centra en la realidad, no solamente una cara conveniente del dibujo.")
        render_step("6", "Verifica fabricabilidad e inspección", "La tolerancia debe poder fabricarse y medirse con el proceso y el equipo disponibles.")
    with c2:
        st.markdown("### Tres ideas base")
        st.latex(r"\text{Tamaño correcto}\;\not\Rightarrow\;\text{geometría correcta}")
        st.write("Los problemas de montaje y funcionamiento suelen aparecer cuando se confunden tolerancias dimensionales con tolerancias geométricas.")

        st.latex(r"\mathcal{G}_{real}\subseteq\mathcal{Z}_{tol}")
        st.write("Toda interpretación del módulo gira en torno a esta idea: la geometría real debe quedar contenida dentro de una zona geométrica definida por la especificación.")

        st.latex(r"\text{Función} \rightarrow \text{Especificación} \rightarrow \text{Inspección}")
        st.write("La tolerancia bien definida nace de la función, se comunica en el plano y se confirma mediante una estrategia de control coherente.")

        st.markdown("### Selector rápido · ¿qué te preocupa controlar?")
        concern = st.selectbox(
            "Situación principal",
            [
                "La superficie por sí sola debe quedar plana o recta",
                "Dos caras deben quedar orientadas entre sí",
                "Un agujero o eje debe quedar en la ubicación correcta",
                "Una pieza rotacional no debe oscilar al girar",
                "Quiero proteger ensamblaje usando condición de material",
            ],
            key="gdt_concern",
        )
        if concern.startswith("La superficie"):
            st.info("Punto de partida recomendado: **Forma**. Revisa planitud, rectitud, redondez o cilindricidad según la geometría real.")
        elif concern.startswith("Dos caras"):
            st.info("Punto de partida recomendado: **Orientación**. Evalúa paralelismo o perpendicularidad respecto de una referencia especificada funcional.")
        elif concern.startswith("Un agujero"):
            st.info("Punto de partida recomendado: **Posición** + **Referencias A-B-C**. Probablemente necesitarás controlar ubicación respecto de referencias funcionales.")
        elif concern.startswith("Una pieza rotacional"):
            st.info("Punto de partida recomendado: **Oscilación**. Asegúrate primero de cuál es el eje de referencia de rotación.")
        else:
            st.info("Punto de partida recomendado: **MMR / LMR**. Útil cuando tamaño y tolerancia geométrica deben conversar para proteger ensamblaje.")

    st.markdown("### Mapa general de familias")
    for family, rows in CONTROL_FAMILIES.items():
        st.markdown(f"#### {family}")
        cols = st.columns(min(4, len(rows)))
        for col, row in zip(cols, rows):
            with col:
                st.markdown(
                    f"""
<div class="gg-card">
  <div class="gg-symbol">{row['symbol']}</div>
  <h4 style="margin:.6rem 0 .25rem 0">{row['name']}</h4>
  <div style="color:#737986"><b>Zona:</b> {row['zone']}</div>
  <div style="margin-top:.5rem"><b>Uso:</b> {row['use']}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

# ----------------------------------------------------------------------------------
# TAB 2: Marco de tolerancia
# ----------------------------------------------------------------------------------
with tabs[1]:
    st.subheader("Marco de tolerancia · cómo leer e interpretar la indicación geométrica")

    left, right = st.columns([0.95, 1.05], gap="large")
    with left:
        characteristic = st.selectbox(
            "Símbolo geométrico",
            ["Rectitud", "Planitud", "Paralelismo", "Perpendicularidad", "Posición", "Oscilación circular"],
            key="fcf_characteristic",
        )
        tol_value = st.number_input(
            "Valor de tolerancia [mm]",
            min_value=0.001,
            value=0.050,
            step=0.001,
            format="%.3f",
            key="fcf_tol",
        )
        use_diameter = st.checkbox("Zona cilíndrica / diametral", value=characteristic in ["Posición"], key="fcf_diam")
        with_mm = st.checkbox("Con requisito de material (Ⓜ)", value=False, key="fcf_mmr")
        datum_1 = st.selectbox("Referencia primaria A", ["—", "A", "B", "C"], index=1 if characteristic in ["Paralelismo", "Perpendicularidad", "Posición", "Oscilación circular"] else 0, key="fcf_d1")
        datum_2 = st.selectbox("Referencia secundaria B", ["—", "A", "B", "C"], index=2 if characteristic == "Posición" else 0, key="fcf_d2")
        datum_3 = st.selectbox("Referencia terciaria C", ["—", "A", "B", "C"], index=3 if characteristic == "Posición" else 0, key="fcf_d3")

        symbol_map = {
            "Rectitud": "—",
            "Planitud": "▱",
            "Paralelismo": "∥",
            "Perpendicularidad": "⟂",
            "Posición": "⌖",
            "Oscilación circular": "↗",
        }
        tol_label = ("⌀ " if use_diameter else "") + f"{tol_value:.3f}" + (" Ⓜ" if with_mm else "")
        cells = [symbol_map[characteristic], tol_label] + [d for d in [datum_1, datum_2, datum_3] if d != "—"]

        st.markdown("### Vista didáctica")
        render_fcf(cells)
        st.caption("Marco de tolerancia didáctico. La simbología contractual debe seguir la norma y el estilo de tu plano.")

    with right:
        st.markdown("### ¿Qué significa cada casilla?")
        cols = st.columns(4)
        texts = [
            ("1", "Característica", "Indica qué se controla: forma, orientación, posición o oscilación."),
            ("2", "Tolerancia", "Entrega el tamaño de la zona geométrica permitida. Puede ser lineal o diametral."),
            ("3", "Condición de material", "Si aplica, modifica cómo interactúa la tolerancia con el tamaño del elemento."),
            ("4", "Referencias especificadas", "Declaran el sistema de referencia funcional que debe usarse para orientar o localizar la pieza."),
        ]
        for col, (n, h, b) in zip(cols, texts):
            with col:
                st.markdown(f"<div class='gg-mini'><span class='gg-badge'>{n}</span><b>{h}</b><br><div style='margin-top:.45rem'>{b}</div></div>", unsafe_allow_html=True)

        st.markdown("### Reglas prácticas")
        st.markdown(
            """
- Si la tolerancia controla una **forma aislada**, normalmente no necesitas datum.
- Si controla una **relación** entre elementos, normalmente sí necesitas datum.
- El símbolo **⌀** delante del valor indica una **zona cilíndrica**.
- El símbolo de condición de material debe usarse solo cuando tenga sentido funcional y de inspección.
- No mezcles referencias especificadas por costumbre: deben representar la cadena real de apoyo, orientación y localización.
"""
        )

# ----------------------------------------------------------------------------------
# TAB 3: Forma
# ----------------------------------------------------------------------------------
with tabs[2]:
    st.subheader("Tolerancias de forma · entender qué geometría se está limitando")

    control_form = st.selectbox("Control de forma", list(FORM_GUIDE.keys()), key="form_control_v11")
    form_tol = st.number_input("Tolerancia geométrica [mm]", min_value=0.001, value=0.050, step=0.001, format="%.3f", key="form_tol_v11")
    info = FORM_GUIDE[control_form]

    ftabs = st.tabs(["Concepto", "Zona y ecuaciones", "En plano", "Inspección", "Errores frecuentes"])

    with ftabs[0]:
        a, b = st.columns([0.95, 1.05], gap="large")
        with a:
            st.markdown(f"### {control_form}")
            st.write(info["controls"])
            st.markdown(f"**Zona geométrica:** {info['zone']}")
            st.markdown(f"**Aplicación típica:** {FORM_GUIDE[control_form]['inspection']}")
        with b:
            st.plotly_chart(make_form_zone_figure(control_form, form_tol), width="stretch", config={"displaylogo": False}, key=f"plot_form_{control_form}")
    with ftabs[1]:
        st.markdown("### Lectura geométrica")
        st.write(info["zone"])
        for eq in info["latex"]:
            st.latex(eq)
        st.markdown(
            """
<div class="gg-note">
<b>Cómo leer la ecuación aquí:</b> la expresión no pretende reemplazar la definición normativa completa;
se usa para recordar que la geometría real debe quedar contenida dentro de una zona permitida cuyo tamaño está dado por la tolerancia.
</div>
""",
            unsafe_allow_html=True,
        )
    with ftabs[2]:
        st.markdown("### ¿Cómo se especifica en plano?")
        render_fcf([
            {"Rectitud":"—","Planitud":"▱","Redondez":"○","Cilindricidad":"⌭"}[control_form],
            f"{form_tol:.3f}"
        ])
        st.write(info["drawing"])
        st.markdown(
            """
- Si controlas una **superficie**, el líder debe llegar a esa superficie.
- Si controlas un **eje derivado**, el plano debe dejar clara la característica de tamaño desde la cual se deriva ese eje.
- En elementos rotacionales, conviene separar mentalmente: **tamaño**, **forma** y luego **orientación/localización**.
"""
        )
    with ftabs[3]:
        st.markdown("### ¿Cómo se verifica?")
        st.write(info["inspection"])
        st.markdown(
            """
- **Taller / preliminar:** útil para tendencia, detección rápida y ajuste de proceso.
- **Metrología formal:** útil para liberación, trazabilidad o reclamos de calidad.
- **Escaneo 3D / CMM:** requiere definir cómo se extrae el elemento asociado que se va a evaluar.
"""
        )
    with ftabs[4]:
        st.markdown("### Qué suele confundir")
        for item in info["mistakes"]:
            st.markdown(f"- {item}")

# ----------------------------------------------------------------------------------
# TAB 4: Orientación
# ----------------------------------------------------------------------------------
with tabs[3]:
    st.subheader("Orientación · la geometría ya no se interpreta sola, sino respecto de una referencia especificada")

    orientation = st.radio("Control", ["Paralelismo", "Perpendicularidad"], horizontal=True, key="ori_kind_v11")
    ori_tol = st.number_input("Tolerancia de orientación [mm]", min_value=0.001, value=0.050, step=0.001, format="%.3f", key="ori_tol_v11")
    datum_name = st.selectbox("Referencia especificada", ["A", "B", "C"], key="ori_datum_v11")
    oinfo = ORIENTATION_GUIDE[orientation]

    otabs = st.tabs(["Concepto", "Esquema", "En plano", "Inspección", "Errores frecuentes"])
    with otabs[0]:
        st.write(oinfo["controls"])
        for eq in oinfo["latex"]:
            st.latex(eq)
        st.write("La clave es que la zona de tolerancia queda construida a partir de la referencia especificada; por eso orientación no es igual a forma.")
    with otabs[1]:
        st.plotly_chart(make_orientation_figure(orientation, ori_tol), width="stretch", config={"displaylogo": False}, key=f"ori_plot_{orientation}")
        st.markdown(f"**Interpretación:** la zona se orienta respecto de la referencia {datum_name}. Si la superficie o eje real se sale de esa zona, no cumple.")
    with otabs[2]:
        render_fcf(["∥" if orientation == "Paralelismo" else "⟂", f"{ori_tol:.3f}", datum_name])
        st.write(oinfo["drawing"])
        st.markdown("La referencia especificada debe representar la referencia funcional real del montaje o de la operación que la pieza debe cumplir.")
    with otabs[3]:
        st.write(oinfo["inspection"])
        st.markdown(
            """
- Con reloj comparador, lo más crítico es reproducir la referencia funcional.
- En CMM, lo más crítico es la alineación y la estrategia de asociación de elementos.
- En control de proceso, orientación y posición suelen analizarse juntas porque los errores comparten causa de mecanizado o fijación.
"""
        )
    with otabs[4]:
        for item in oinfo["mistakes"]:
            st.markdown(f"- {item}")

# ----------------------------------------------------------------------------------
# TAB 5: Posición
# ----------------------------------------------------------------------------------
with tabs[4]:
    st.subheader("Posición · proteger ensamblaje, paso de pernos, centros y ejes")

    i1, i2, i3 = st.columns(3, gap="medium")
    with i1:
        pos_tol = st.number_input(
            "Tolerancia diametral de posición [mm]",
            min_value=0.001,
            value=0.100,
            step=0.001,
            format="%.3f",
            key="pos_tol_v12",
        )
    with i2:
        dx = st.number_input(
            "Desviación Δx [mm]",
            value=0.020,
            step=0.001,
            format="%.3f",
            key="pos_dx_v12",
        )
    with i3:
        dy = st.number_input(
            "Desviación Δy [mm]",
            value=0.015,
            step=0.001,
            format="%.3f",
            key="pos_dy_v12",
        )

    pos = positional_error_2d(dx, dy, pos_tol)

    left, right = st.columns([0.86, 1.14], gap="large")
    with left:
        st.markdown("### Modelo geométrico simplificado")
        st.latex(r"r=\sqrt{(\Delta x)^2+(\Delta y)^2}")
        st.latex(r"e_p=2r=2\sqrt{(\Delta x)^2+(\Delta y)^2}")
        st.write(
            "El centro real se desplaza una distancia radial $r$ respecto de la posición teórica exacta. "
            "Como la zona de posición es diametral, la desviación equivalente se expresa como $e_p=2r$."
        )

        k1, k2 = st.columns(2)
        k1.metric("Desplazamiento radial r", f"{pos.radial_offset_mm:.3f} mm")
        k2.metric("Desviación diametral eₚ", f"{pos.diametral_position_error_mm:.3f} mm")
        st.metric("Margen respecto de la zona", f"{pos.margin_mm:+.3f} mm")

        if pos.status == "Dentro de zona":
            st.success(pos.status)
        else:
            st.error(pos.status)

    with right:
        st.plotly_chart(
            make_position_figure(dx, dy, pos_tol),
            width="stretch",
            config={"displaylogo": False},
            key="pos_plot_v12",
        )

    st.markdown("### Lectura práctica")
    pcols = st.columns(3)
    for col, note in zip(pcols, POSITION_NOTES):
        with col:
            st.markdown(f"<div class='gg-mini'>{note}</div>", unsafe_allow_html=True)

    ptabs = st.tabs(["Qué significa", "Cómo va en plano", "Qué parámetros influyen", "Cómo controlar"])
    with ptabs[0]:
        st.write(
            "La posición se usa cuando el problema no es solamente el tamaño del agujero o del eje, sino su ubicación funcional. "
            "En un patrón de agujeros, una mala posición puede impedir el montaje aunque todos los diámetros cumplan."
        )
        st.markdown("Una posición bien definida normalmente conversa con:")
        st.markdown(
            "- dimensiones teóricamente exactas;\n"
            "- referencias A-B-C;\n"
            "- forma y orientación del elemento;\n"
            "- requisito de material cuando aplica."
        )
    with ptabs[1]:
        render_fcf(["⌖", f"⌀ {pos_tol:.3f}", "A", "B", "C"])
        st.markdown(
            """
- El símbolo de diámetro indica que la zona de posición es cilíndrica.
- Las referencias A-B-C construyen el sistema que define la posición teórica exacta.
- El agujero o eje también debe tener declarado su tamaño nominal y tolerancia dimensional.
- La tolerancia de posición no reemplaza la tolerancia de tamaño.
"""
        )
    with ptabs[2]:
        st.markdown("### Parámetros relevantes")
        st.markdown(
            """
- **Valor de tolerancia**: define el diámetro de la zona permitida.
- **Sistema de referencias A-B-C**: define cómo se orienta y localiza la pieza para la evaluación.
- **Tipo de elemento**: agujero, eje, ranura o patrón.
- **Requisito de material**: puede entregar tolerancia adicional cuando corresponde.
- **Método de asociación/extracción**: determina cómo se obtiene el centro o eje real a partir de los puntos medidos.
"""
        )
    with ptabs[3]:
        st.markdown(
            """
- En taller pueden utilizarse útiles, plantillas o calibres funcionales cuando la función lo permite.
- En CMM o escáner 3D, el resultado depende de la reconstrucción del sistema de referencias y del cálculo del elemento asociado.
- Para control formal no basta con observar si el centro está corrido: la evaluación debe reproducir la referencia declarada en el plano.
"""
        )

# ----------------------------------------------------------------------------------
# TAB 6: Referencias especificadas
# ----------------------------------------------------------------------------------
with tabs[5]:
    st.subheader("Referencias A-B-C · cómo se establece el sistema de referencia funcional")

    d1, d2 = st.columns([0.85, 1.15], gap="large")
    with d1:
        primary = st.checkbox("Referencia primaria A", value=True, key="datumA_v11")
        secondary = st.checkbox("Referencia secundaria B", value=True, key="datumB_v11")
        tertiary = st.checkbox("Referencia terciaria C", value=True, key="datumC_v11")
        dof = dof_after_datums(primary, secondary, tertiary)
        st.metric("Grados de libertad restringidos", f"{dof['constrained']}/6")
        st.metric("Grados de libertad remanentes", str(dof['free']))
        st.latex(r"3+2+1=6")
        for note in dof["notes"]:
            st.markdown(f"- {note}")
        st.markdown(
            """
<div class="gg-warning">
<b>Advertencia didáctica:</b> el modelo 3-2-1 es un excelente recurso para piezas prismáticas y enseñanza de referencia funcional,
pero una realización de datum formal en GPS puede involucrar simuladores, restricciones y características derivadas.
</div>
""",
            unsafe_allow_html=True,
        )
    with d2:
        st.plotly_chart(make_datum_321_figure(primary, secondary, tertiary), width="stretch", config={"displaylogo": False}, key="datum_plot_v11")

    dtabs = st.tabs(["Qué es una referencia especificada (datum)", "Cómo elegirlo", "Ejemplos", "Errores comunes"])
    with dtabs[0]:
        st.write(
            "La referencia especificada (datum) no es simplemente una superficie dibujada. Es una referencia teóricamente exacta obtenida a partir de una característica de referencia y realizada mediante una regla de apoyo, centrado o simulación funcional."
        )
        st.markdown("En términos simples:")
        st.markdown("- la **característica de referencia** es la superficie o elemento real de la pieza;\n- el **datum** es la referencia geométrica ideal;\n- el **sistema de referencias A-B-C** ordena cómo se orienta y localiza la pieza para evaluar otras tolerancias.")
    with dtabs[1]:
        st.markdown(
            """
- El **primario** debe ser la referencia más estable y funcional.
- El **secundario** debe orientar lo que aún queda libre.
- El **terciario** termina de fijar la localización o la orientación angular.
- Si eliges mal las referencias especificadas, incluso una buena tolerancia geométrica puede dejar de representar la función de la pieza.
"""
        )
    with dtabs[2]:
        st.dataframe(DATUM_EXAMPLES, width="stretch", hide_index=True)
    with dtabs[3]:
        st.markdown(
            """
- Elegir referencias especificadas por comodidad de dibujo y no por función.
- Usar demasiadas referencias especificadas sin una necesidad real.
- No distinguir entre referencia (datum) de diseño y referencia improvisada de inspección.
- Medir una posición respecto de referencias distintas de las especificadas en el plano.
"""
        )

# ----------------------------------------------------------------------------------
# TAB 7: Oscilación
# ----------------------------------------------------------------------------------
with tabs[6]:
    st.subheader("Oscilación circular y total (run-out) · control durante la rotación")

    readings_text = st.text_area("Lecturas del reloj comparador durante una vuelta [mm]", value="0.000; 0.008; 0.014; 0.010; 0.002; -0.004; -0.006; 0.000", key="runout_read_v11")
    run_tol = st.number_input("Tolerancia de oscilación circular [mm]", min_value=0.001, value=0.030, step=0.001, format="%.3f", key="runout_tol_v11")

    try:
        readings = parse_series(readings_text)
        ro = runout(readings, run_tol)
    except Exception as exc:
        st.error(str(exc))
        readings = None
        ro = None

    if ro is not None:
        st.latex(r"\mathrm{TIR}=x_{\max}-x_{\min}")
        st.latex(rf"\mathrm{{TIR}}={ro.tir_mm:.3f}\,\mathrm{{mm}}")
        r1, r2, r3 = st.columns(3)
        r1.metric("Mínimo", f"{ro.min_mm:.3f} mm")
        r2.metric("Máximo", f"{ro.max_mm:.3f} mm")
        r3.metric("Variación total indicada (TIR)", f"{ro.tir_mm:.3f} mm")
        if ro.status == "Cumple":
            st.success(ro.status)
        else:
            st.error(ro.status)
        st.plotly_chart(make_runout_figure(readings, run_tol), width="stretch", config={"displaylogo": False}, key="run_plot_v11")

    rtabs = st.tabs(["Qué mide", "Oscilación circular vs total", "Cómo se pone en plano", "Qué suele fallar"])
    with rtabs[0]:
        for note in RUNOUT_NOTES:
            st.markdown(f"- {note}")
        st.write("La oscilación es especialmente útil cuando el problema real se manifiesta al girar: sellado dinámico, contacto de caras, excentricidad, vibración o variación de apoyo.")
    with rtabs[1]:
        st.markdown("**Oscilación circular**: controla una sección en una posición axial dada durante una revolución.")
        st.markdown("**Oscilación total**: controla la envolvente de toda la superficie durante rotación y barrido a lo largo de la longitud funcional.")
        st.write("En muchos casos de ejes, caras y asientos, el paso de circular a total cambia fuertemente el costo de fabricación y la exigencia de control.")
    with rtabs[2]:
        render_fcf(["↗", f"{run_tol:.3f}", "A"])
        st.write("La referencia A suele ser un eje funcional de rotación. Si el eje de referencia no representa el funcionamiento real, el valor de oscilación puede perder sentido práctico.")
    with rtabs[3]:
        st.markdown(
            """
- Medir oscilación respecto de un eje improvisado y no de la referencia funcional.
- Confundir oscilación con redondez.
- No distinguir entre error de forma y error de referencia.
- Declarar tolerancias de oscilación muy pequeñas sin revisar si el proceso o el método de control pueden sostenerlos.
"""
        )

# ----------------------------------------------------------------------------------
# TAB 8: MMR/LMR
# ----------------------------------------------------------------------------------
with tabs[7]:
    st.subheader("MMR / LMR · cuando el tamaño real modifica la tolerancia geométrica disponible")

    m1, m2 = st.columns([0.95, 1.05], gap="large")
    with m1:
        feature_type = st.radio("Tipo de elemento", ["Agujero / elemento interno", "Eje / elemento externo"], horizontal=True, key="mmr_type_v11")
        if feature_type.startswith("Agujero"):
            default_mms, default_actual = 10.000, 10.040
        else:
            default_mms, default_actual = 10.000, 9.960
        mms = st.number_input("Tamaño en máximo material (MMS) [mm]", value=default_mms, step=0.001, format="%.3f", key="mmr_mms_v11")
        actual = st.number_input("Tamaño real [mm]", value=default_actual, step=0.001, format="%.3f", key="mmr_actual_v11")
        specified = st.number_input("Tolerancia geométrica indicada en MMR [mm]", min_value=0.001, value=0.100, step=0.001, format="%.3f", key="mmr_spec_v11")
        mmr = mmr_bonus(feature_type, mms, actual, specified)

        st.latex(r"t_{disp}=t_{MMR}+t_{bonus}")
        if feature_type.startswith("Agujero"):
            st.latex(r"t_{bonus}=D_{real}-D_{MMS}")
            st.latex(r"VC\approx D_{MMS}-t_{MMR}")
        else:
            st.latex(r"t_{bonus}=D_{MMS}-D_{real}")
            st.latex(r"VC\approx D_{MMS}+t_{MMR}")

        a, b, c = st.columns(3)
        a.metric("Bonus", f"{mmr.bonus_tol_mm:.3f} mm")
        b.metric("Tol. disponible", f"{mmr.available_geom_tol_mm:.3f} mm")
        c.metric("Condición virtual", f"{mmr.virtual_condition_mm:.3f} mm")
        for note in MMR_NOTES:
            st.markdown(f"- {note}")
    with m2:
        st.plotly_chart(make_mmr_figure(mmr.feature_type, mmr.maximum_material_size_mm, mmr.actual_size_mm, mmr.specified_geom_tol_mm, mmr.available_geom_tol_mm), width="stretch", config={"displaylogo": False}, key="mmr_plot_v11")

    mtabs = st.tabs(["Interpretación", "Cómo se pone", "Cuándo usarlo", "Qué no hacer"])
    with mtabs[0]:
        st.write(
            "La lógica del máximo material es funcional: protege el peor caso de ensamble. Si un agujero sale más grande o un eje más pequeño, puede aumentar la tolerancia geométrica disponible sin perder capacidad de montaje."
        )
    with mtabs[1]:
        render_fcf(["⌖", f"⌀ {specified:.3f} Ⓜ", "A", "B", "C"])
        st.write("La indicación debe ser coherente con una característica de tamaño compatible y con una necesidad funcional real. Debe responder a una función de ensamblaje e inspección; no debe agregarse por costumbre.")
    with mtabs[2]:
        st.markdown(
            """
- Patrones de agujeros con requerimiento de ensamblaje.
- Ejes y agujeros cuya función depende de mantener una condición virtual funcional.
- Casos donde se desea combinar intercambiabilidad con libertad manufacturable adicional.
"""
        )
    with mtabs[3]:
        st.markdown(
            """
- Aplicarlo sin comprender la condición virtual.
- Usarlo donde no existe una característica de tamaño compatible.
- Confundir tolerancia adicional (bonus) con permiso general de fabricación.
- Olvidar que la inspección también debe reconocer ese requisito.
"""
        )

# ----------------------------------------------------------------------------------
# TAB 9: Inspección e ingeniería
# ----------------------------------------------------------------------------------
with tabs[8]:
    st.subheader("Inspección e ingeniería · cómo transformar una tolerancia en criterio de control")

    case_name = st.selectbox("Caso industrial", list(ENGINEERING_CASES.keys()), key="eng_case_v11")
    case = ENGINEERING_CASES[case_name]

    st.markdown(
        f"""
<div class="gg-case">
  <div style="font-size:.78rem;font-weight:800;color:#f28e1c;letter-spacing:.08em">CASO INDUSTRIAL</div>
  <h3 style="margin:.35rem 0 .35rem 0">{case_name}</h3>
  <div>{case['description']}</div>
  <div style="margin-top:.55rem"><b>Control principal:</b> {case['primary']}</div>
  <div><b>Referencias especificadas:</b> {case['datums']}</div>
  <div style="margin-top:.55rem;color:#737986">{case['question']}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    etabs = st.tabs(["Métodos", "Ruta de control", "En planos", "Errores típicos de ingeniería"])
    with etabs[0]:
        st.dataframe(INSPECTION_METHODS, width="stretch", hide_index=True)
        st.markdown(
            """
<div class="gg-note">
<b>Idea importante:</b> una CMM o un escáner 3D no convierten automáticamente un mapa de desviaciones en verificación GPS.
Primero debes definir sistema de referencia, elemento asociado, estrategia de captura y regla de evaluación.
</div>
""",
            unsafe_allow_html=True,
        )
    with etabs[1]:
        st.latex(r"\text{Función}\rightarrow\text{símbolo}\rightarrow\text{referencias especificadas}\rightarrow\text{estrategia de medición}\rightarrow\text{evaluación}\rightarrow\text{decisión}")
        st.markdown(
            """
1. Entender para qué trabaja la superficie o el elemento.
2. Elegir la tolerancia geométrica que protege esa función.
3. Definir referencias especificadas funcionales.
4. Especificar una estrategia de control reproducible.
5. Evaluar con criterio consistente.
6. Emitir una decisión que pueda defenderse técnica y documentalmente.
"""
        )
    with etabs[2]:
        st.markdown(
            """
- Si la exigencia es crítica, el plano debería dejar claro **qué se controla**, **contra qué referencia especificada**, **con qué tamaño de zona** y, si aplica, **bajo qué requisito de material**.
- Si la pieza tiene alta criticidad de montaje, conviene complementar el plano con notas de inspección, criterio funcional o referencia a plan de control.
- Para producción repetitiva, vale la pena pensar en útiles funcionales o calibres dedicados cuando la función lo permita.
"""
        )
    with etabs[3]:
        st.markdown(
            """
- Sobretolerar: pedir tolerancias muy cerradas “por si acaso”.
- Subdefinir: dejar una dimensión y asumir que con eso basta.
- Elegir mal el datum: la pieza cumple en informe pero falla en montaje.
- Medir con un método que no reproduce la función.
- No coordinar diseño, fabricación y calidad antes de liberar el plano.
"""
        )

st.divider()
st.caption("GG DIMEC · MechLab · Metrología y Fabricación · Tolerancias geométricas, teoría aplicada, plano e inspección.")
