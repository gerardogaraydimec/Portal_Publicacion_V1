from __future__ import annotations

import math
import statistics
import plotly.graph_objects as go

ORANGE = "#f28e1c"
BLACK = "#171717"
GRAY = "#747980"
LIGHT = "#e8eaed"


def make_measurement_chain_figure():
    fig = go.Figure()

    boxes = [
        (0.6, "Pieza\nMensurando"),
        (2.4, "Método\n+ operador"),
        (4.2, "Instrumento"),
        (6.0, "Calibración\n+ ambiente"),
        (7.8, "Correcciones"),
        (9.4, "Resultado\n± U"),
    ]

    for x, label in boxes:
        fig.add_shape(
            type="rect",
            x0=x-0.65, x1=x+0.65,
            y0=-0.45, y1=0.45,
            line=dict(color=BLACK, width=2),
            fillcolor="rgba(242,142,28,0.08)" if x in [0.6, 9.4] else "white"
        )
        fig.add_annotation(
            x=x, y=0,
            text="<b>" + label.replace("\n", "<br>") + "</b>",
            showarrow=False,
            font=dict(size=12, color=BLACK)
        )

    for a, b in zip(boxes[:-1], boxes[1:]):
        fig.add_annotation(
            x=b[0]-0.75, y=0,
            ax=a[0]+0.75, ay=0,
            text="",
            showarrow=True,
            arrowhead=3,
            arrowwidth=2,
            arrowcolor=ORANGE
        )

    fig.update_layout(
        height=320,
        margin=dict(l=25, r=25, t=25, b=35),
        xaxis=dict(visible=False, range=[-0.2, 10.2]),
        yaxis=dict(visible=False, range=[-1.0, 1.0]),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    fig.add_annotation(
        x=0.5, y=-0.10, xref="paper", yref="paper",
        text="El resultado no proviene solo del instrumento: depende del mensurando, método, ambiente, calibración, correcciones y modelo de incertidumbre.",
        showarrow=False,
        font=dict(size=11, color=GRAY)
    )
    return fig


def make_repeatability_figure(readings_mm, mean_mm):
    x = list(range(1, len(readings_mm)+1))
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x,
        y=readings_mm,
        mode="markers+lines",
        marker=dict(size=10, color=ORANGE, line=dict(color=BLACK, width=1)),
        line=dict(color=LIGHT, width=2),
        name="Lecturas"
    ))
    fig.add_hline(
        y=mean_mm,
        line=dict(color=BLACK, width=2, dash="dash"),
        annotation_text=f"Promedio = {mean_mm:.3f} mm",
        annotation_position="top right"
    )

    fig.update_layout(
        height=430,
        margin=dict(l=55, r=35, t=35, b=50),
        xaxis_title="Número de lectura",
        yaxis_title="Indicación [mm]",
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_uncertainty_budget_figure(items):
    labels = [i.name for i in items]
    values = [i.contribution_um for i in items]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker=dict(color=[ORANGE if i == max(values) and i > 0 else BLACK for i in values]),
        text=[f"{v:.0f} µm" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        height=470,
        margin=dict(l=55, r=25, t=35, b=120),
        xaxis_tickangle=-28,
        yaxis_title="Contribución estándar [µm]",
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_conformity_figure(lsl_mm, usl_mm, measured_mm, U_um, acc_lsl_mm=None, acc_usl_mm=None):
    tolerance = usl_mm-lsl_mm
    pad = max(0.30*tolerance, U_um/1000.0*2.5, 0.001)

    fig = go.Figure()

    xmin = lsl_mm-pad
    xmax = usl_mm+pad

    # Outside zones
    fig.add_shape(
        type="rect",
        x0=xmin, x1=lsl_mm,
        y0=0.22, y1=0.78,
        line=dict(color="rgba(0,0,0,0)", width=0),
        fillcolor="rgba(214, 69, 65, 0.08)"
    )
    fig.add_shape(
        type="rect",
        x0=usl_mm, x1=xmax,
        y0=0.22, y1=0.78,
        line=dict(color="rgba(0,0,0,0)", width=0),
        fillcolor="rgba(214, 69, 65, 0.08)"
    )

    # Specification zone
    fig.add_shape(
        type="rect",
        x0=lsl_mm, x1=usl_mm,
        y0=0.25, y1=0.75,
        line=dict(color=ORANGE, width=2),
        fillcolor="rgba(242,142,28,0.13)"
    )

    # Acceptance zone (guard band if applicable)
    if acc_lsl_mm is not None and acc_usl_mm is not None and acc_lsl_mm <= acc_usl_mm:
        fig.add_shape(
            type="rect",
            x0=acc_lsl_mm, x1=acc_usl_mm,
            y0=0.34, y1=0.66,
            line=dict(color=BLACK, width=1.5),
            fillcolor="rgba(33, 150, 83, 0.12)"
        )
        if (acc_lsl_mm > lsl_mm) or (acc_usl_mm < usl_mm):
            fig.add_annotation(
                x=(acc_lsl_mm+acc_usl_mm)/2, y=0.68,
                text="Zona de aceptación",
                showarrow=False, font=dict(size=10, color=BLACK)
            )

    U_mm = U_um/1000.0
    low = measured_mm-U_mm
    high = measured_mm+U_mm

    fig.add_shape(
        type="line",
        x0=low, x1=high,
        y0=0.5, y1=0.5,
        line=dict(color=BLACK, width=6)
    )
    for x in [low, high]:
        fig.add_shape(
            type="line",
            x0=x, x1=x,
            y0=0.41, y1=0.59,
            line=dict(color=BLACK, width=2)
        )

    fig.add_trace(go.Scatter(
        x=[measured_mm], y=[0.5],
        mode="markers",
        marker=dict(size=16, color=ORANGE, line=dict(color=BLACK, width=2)),
        name="Resultado"
    ))

    fig.add_annotation(
        x=lsl_mm, y=0.82,
        text=f"LSL<br>{lsl_mm:.3f} mm",
        showarrow=False, xanchor="left",
        font=dict(size=10, color=GRAY)
    )
    fig.add_annotation(
        x=usl_mm, y=0.82,
        text=f"USL<br>{usl_mm:.3f} mm",
        showarrow=False, xanchor="right",
        font=dict(size=10, color=GRAY)
    )
    fig.add_annotation(
        x=(lsl_mm+usl_mm)/2, y=0.86,
        text="Zona de especificación",
        showarrow=False, font=dict(size=11, color=ORANGE)
    )
    fig.add_annotation(
        x=measured_mm, y=0.16,
        text=f"<b>{measured_mm:.3f} mm ± {U_um:.0f} µm</b>",
        showarrow=False,
        font=dict(size=12, color=BLACK)
    )

    fig.update_layout(
        height=360,
        margin=dict(l=55, r=55, t=40, b=55),
        xaxis=dict(
            title="Dimensión [mm]",
            range=[xmin, xmax],
            gridcolor="#efefef",
        ),
        yaxis=dict(visible=False, range=[0, 1]),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig

def make_temperature_correction_figure(indicated_mm, corrected_mm, reference_C, temp_C):
    delta_um = (corrected_mm-indicated_mm)*1000.0

    fig = go.Figure(go.Bar(
        x=["Indicación", f"Corregido a {reference_C:.0f} °C"],
        y=[indicated_mm, corrected_mm],
        marker=dict(color=[BLACK, ORANGE]),
        text=[f"{indicated_mm:.3f} mm", f"{corrected_mm:.3f} mm"],
        textposition="outside",
    ))

    ymin = min(indicated_mm, corrected_mm)
    ymax = max(indicated_mm, corrected_mm)
    span = max(ymax-ymin, 0.001)

    fig.update_layout(
        height=380,
        margin=dict(l=60, r=25, t=40, b=45),
        yaxis_title="Dimensión [mm]",
        yaxis=dict(range=[ymin-2*span, ymax+3*span], gridcolor="#efefef"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    fig.add_annotation(
        x=0.5, y=0.04, xref="paper", yref="paper",
        text=f"Corrección térmica estimada: {delta_um:+.0f} µm · Temperatura medida: {temp_C:.1f} °C",
        showarrow=False,
        font=dict(size=11, color=GRAY)
    )
    return fig


def make_instrument_suitability_figure(tolerance_um, U_um, resolution_um, target_ratio):
    max_U = tolerance_um/target_ratio if target_ratio > 0 else tolerance_um

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=["Tolerancia", "U expandida", "Resolución"],
        x=[tolerance_um, U_um, resolution_um],
        orientation="h",
        marker=dict(color=[BLACK, ORANGE, GRAY]),
        text=[f"{tolerance_um:.0f} µm", f"{U_um:.0f} µm", f"{resolution_um:.0f} µm"],
        textposition="outside",
    ))
    fig.add_vline(
        x=max_U,
        line=dict(color=ORANGE, width=2, dash="dash"),
        annotation_text=f"U objetivo ≤ {max_U:.0f} µm",
        annotation_position="top right",
    )
    fig.update_layout(
        height=350,
        margin=dict(l=90, r=40, t=45, b=40),
        xaxis_title="Magnitud [µm]",
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_shaft_measurement_schematic():
    fig = go.Figure()

    # Shaft
    fig.add_shape(
        type="rect", x0=3.0, x1=7.0, y0=3.9, y1=6.1,
        line=dict(color=BLACK, width=3),
        fillcolor="rgba(242,142,28,0.08)"
    )
    fig.add_shape(
        type="line", x0=3.0, x1=7.0, y0=5.0, y1=5.0,
        line=dict(color=ORANGE, width=1.8, dash="dash")
    )

    # Micrometer anvils
    fig.add_shape(type="rect", x0=2.2, x1=2.9, y0=4.1, y1=5.9,
                  line=dict(color=BLACK, width=2), fillcolor="white")
    fig.add_shape(type="rect", x0=7.1, x1=7.8, y0=4.1, y1=5.9,
                  line=dict(color=BLACK, width=2), fillcolor="white")

    # Contact arrows and dimension
    fig.add_annotation(
        x=3.0, y=3.45, ax=2.2, ay=3.45,
        text="", showarrow=True, arrowhead=2,
        arrowwidth=1.8, arrowcolor=GRAY
    )
    fig.add_annotation(
        x=7.0, y=3.45, ax=7.8, ay=3.45,
        text="", showarrow=True, arrowhead=2,
        arrowwidth=1.8, arrowcolor=GRAY
    )
    fig.add_annotation(
        x=5.0, y=3.1,
        text="$D$",
        showarrow=False,
        font=dict(size=15, color=BLACK)
    )

    # Measurement axis
    fig.add_shape(
        type="line", x0=2.45, x1=7.55, y0=5.0, y1=5.0,
        line=dict(color=GRAY, width=2)
    )
    fig.add_annotation(
        x=5.0, y=6.75,
        text="<b>Eje de medición</b>",
        showarrow=False,
        font=dict(size=12, color=GRAY)
    )

    fig.add_annotation(
        x=5.0, y=1.35,
        text=(
            "<b>Lectura correcta:</b> contactos opuestos, eje de medición normal a la superficie "
            "y alineado con el diámetro que se quiere verificar."
        ),
        showarrow=False,
        font=dict(size=11, color=GRAY),
        bgcolor="rgba(255,255,255,.96)"
    )

    fig.update_layout(
        height=360,
        margin=dict(l=25, r=25, t=20, b=25),
        xaxis=dict(visible=False, range=[1.3, 8.7]),
        yaxis=dict(visible=False, range=[0.8, 7.3]),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_hole_measurement_schematic():
    fig = go.Figure()

    # Bore / housing
    fig.add_shape(
        type="circle", x0=3.2, x1=6.8, y0=3.0, y1=6.6,
        line=dict(color=BLACK, width=3),
        fillcolor="rgba(242,142,28,0.05)"
    )
    fig.add_shape(
        type="circle", x0=4.0, x1=6.0, y0=3.8, y1=5.8,
        line=dict(color=BLACK, width=2),
        fillcolor="white"
    )

    # Bore gauge contacts
    fig.add_shape(type="line", x0=4.0, x1=6.0, y0=4.8, y1=4.8,
                  line=dict(color=ORANGE, width=3))
    fig.add_shape(type="circle", x0=3.88, x1=4.12, y0=4.68, y1=4.92,
                  line=dict(color=BLACK, width=1.5), fillcolor=ORANGE)
    fig.add_shape(type="circle", x0=5.88, x1=6.12, y0=4.68, y1=4.92,
                  line=dict(color=BLACK, width=1.5), fillcolor=ORANGE)

    # Gauge stem
    fig.add_shape(type="line", x0=5.0, x1=5.0, y0=4.8, y1=7.2,
                  line=dict(color=BLACK, width=3))
    fig.add_annotation(
        x=5.0, y=7.55,
        text="<b>Alesómetro / comparador</b>",
        showarrow=False,
        font=dict(size=12, color=BLACK)
    )

    fig.add_annotation(
        x=5.0, y=3.15,
        text="$D$",
        showarrow=False,
        font=dict(size=15, color=BLACK)
    )
    fig.add_annotation(
        x=8.2, y=4.85,
        text=(
            "<b>Buscar el diámetro efectivo:</b><br>"
            "bascular el instrumento y localizar<br>"
            "el punto de inversión / mínimo indicado."
        ),
        showarrow=False,
        align="left",
        font=dict(size=11, color=GRAY),
        bgcolor="rgba(255,255,255,.96)"
    )

    fig.update_layout(
        height=390,
        margin=dict(l=25, r=25, t=20, b=25),
        xaxis=dict(visible=False, range=[2.0, 10.3]),
        yaxis=dict(visible=False, range=[2.2, 8.0]),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_temperature_model_schematic():
    fig = go.Figure()

    boxes = [
        (1.2, "$L_T$", "Dimensión indicada\na temperatura $T$"),
        (4.0, "$C_T$", "Corrección térmica"),
        (6.8, "$L_{20}$", "Resultado referido\na $20\\,^{\\circ}\\mathrm{C}$"),
    ]

    for x, symbol, subtitle in boxes:
        fig.add_shape(
            type="rect",
            x0=x-0.85, x1=x+0.85,
            y0=3.8, y1=5.6,
            line=dict(color=BLACK, width=2),
            fillcolor="rgba(242,142,28,0.08)" if x != 4.0 else "white"
        )
        fig.add_annotation(
            x=x, y=4.95,
            text=symbol,
            showarrow=False,
            font=dict(size=16, color=ORANGE if x != 4.0 else BLACK)
        )
        fig.add_annotation(
            x=x, y=4.3,
            text=subtitle.replace("\n", "<br>"),
            showarrow=False,
            font=dict(size=10, color=GRAY)
        )

    fig.add_annotation(
        x=3.0, y=4.7, ax=2.15, ay=4.7,
        text="", showarrow=True, arrowhead=3,
        arrowwidth=2, arrowcolor=ORANGE
    )
    fig.add_annotation(
        x=5.85, y=4.7, ax=4.85, ay=4.7,
        text="", showarrow=True, arrowhead=3,
        arrowwidth=2, arrowcolor=ORANGE
    )

    fig.add_annotation(
        x=4.0, y=2.5,
        text="$L_{20}=\\dfrac{L_T}{1+\\alpha(T-20\\,^{\\circ}\\mathrm{C})}$",
        showarrow=False,
        font=dict(size=15, color=BLACK)
    )

    fig.update_layout(
        height=330,
        margin=dict(l=25, r=25, t=20, b=25),
        xaxis=dict(visible=False, range=[0.0, 8.0]),
        yaxis=dict(visible=False, range=[1.8, 6.2]),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_cosine_error_schematic(angle_deg: float):
    theta = math.radians(angle_deg)
    x0, y0 = 1.5, 2.0
    L = 5.2
    x1 = x0 + L
    y1 = y0
    xm = x0 + L*math.cos(theta)
    ym = y0 + L*math.sin(theta)

    fig = go.Figure()

    # True axis
    fig.add_shape(
        type="line", x0=x0, x1=x1, y0=y0, y1=y1,
        line=dict(color=BLACK, width=3)
    )
    # Misaligned measurement axis
    fig.add_shape(
        type="line", x0=x0, x1=xm, y0=y0, y1=ym,
        line=dict(color=ORANGE, width=3)
    )

    fig.add_annotation(
        x=(x0+x1)/2, y=y0-0.45,
        text="$L$",
        showarrow=False,
        font=dict(size=15, color=BLACK)
    )
    fig.add_annotation(
        x=(x0+xm)/2, y=(y0+ym)/2+0.45,
        text="$L_m=L\\cos\\theta$",
        showarrow=False,
        font=dict(size=14, color=ORANGE)
    )
    fig.add_annotation(
        x=x0+0.9, y=y0+0.30,
        text=f"$\\theta={angle_deg:.2f}^\\circ$",
        showarrow=False,
        font=dict(size=13, color=GRAY)
    )
    fig.add_annotation(
        x=4.2, y=4.1,
        text="<b>Error de coseno</b><br>aparece cuando el eje de medición<br>no coincide con la magnitud buscada.",
        showarrow=False,
        align="center",
        font=dict(size=11, color=GRAY),
        bgcolor="rgba(255,255,255,.96)",
    )

    fig.update_layout(
        height=330,
        margin=dict(l=25, r=25, t=20, b=25),
        xaxis=dict(visible=False, range=[0.8, 7.5]),
        yaxis=dict(visible=False, range=[1.0, 4.6]),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_abbe_error_schematic(offset_mm: float, angle_deg: float):
    fig = go.Figure()

    # Reference / measurement axes
    fig.add_shape(
        type="line", x0=1.2, x1=7.4, y0=2.0, y1=2.0,
        line=dict(color=BLACK, width=3)
    )
    fig.add_shape(
        type="line", x0=1.2, x1=7.4, y0=4.3, y1=4.3,
        line=dict(color=ORANGE, width=3)
    )
    fig.add_shape(
        type="line", x0=2.0, x1=2.0, y0=2.0, y1=4.3,
        line=dict(color=GRAY, width=2, dash="dash")
    )
    fig.add_annotation(
        x=2.15, y=3.15,
        text=f"$h={offset_mm:.1f}\\,\\mathrm{{mm}}$",
        showarrow=False,
        xanchor="left",
        font=dict(size=13, color=GRAY)
    )

    # Angular error indicator
    fig.add_shape(
        type="line", x0=5.8, x1=7.2, y0=2.0, y1=2.0+1.4*math.tan(math.radians(angle_deg)),
        line=dict(color=ORANGE, width=2)
    )
    fig.add_annotation(
        x=6.25, y=2.45,
        text=f"$\\theta={angle_deg:.2f}^\\circ$",
        showarrow=False,
        font=dict(size=13, color=GRAY)
    )
    fig.add_annotation(
        x=4.3, y=5.15,
        text="<b>Error de Abbe</b><br>una separación entre la línea de medida y la línea de referencia<br>convierte pequeños errores angulares en errores lineales.",
        showarrow=False,
        align="center",
        font=dict(size=11, color=GRAY),
        bgcolor="rgba(255,255,255,.96)",
    )

    fig.update_layout(
        height=350,
        margin=dict(l=25, r=25, t=20, b=25),
        xaxis=dict(visible=False, range=[0.7, 7.8]),
        yaxis=dict(visible=False, range=[1.0, 5.6]),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig
