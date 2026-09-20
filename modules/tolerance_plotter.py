from __future__ import annotations

import math
import plotly.graph_objects as go

ORANGE = "#f28e1c"
BLACK = "#171717"
GRAY = "#747980"
LIGHT = "#e8eaed"


def make_tolerance_zone_figure(fit):
    hole = fit.hole
    shaft = fit.shaft

    all_y = [hole.lower_um, hole.upper_um, shaft.lower_um, shaft.upper_um, 0.0]
    ymin = min(all_y)
    ymax = max(all_y)
    span = max(ymax - ymin, 10.0)
    pad = 0.28 * span

    fig = go.Figure()

    # Zero line
    fig.add_shape(
        type="line", x0=0.25, x1=2.75, y0=0, y1=0,
        line=dict(color=GRAY, width=2, dash="dash")
    )
    fig.add_annotation(
        x=0.33, y=0,
        text="<b>Línea cero · dimensión nominal</b>",
        showarrow=False, xanchor="left", yshift=14,
        font=dict(size=11, color=GRAY),
        bgcolor="rgba(255,255,255,.95)"
    )

    # Hole zone
    fig.add_shape(
        type="rect", x0=0.55, x1=1.25,
        y0=hole.lower_um, y1=hole.upper_um,
        line=dict(color=ORANGE, width=2.5),
        fillcolor="rgba(242,142,28,0.22)"
    )
    fig.add_annotation(
        x=0.90, y=(hole.lower_um + hole.upper_um)/2,
        text=f"<b>Agujero {hole.symbol}{hole.grade}</b>",
        showarrow=False, font=dict(size=12, color=BLACK)
    )

    # Shaft zone
    fig.add_shape(
        type="rect", x0=1.75, x1=2.45,
        y0=shaft.lower_um, y1=shaft.upper_um,
        line=dict(color=BLACK, width=2.5),
        fillcolor="rgba(23,23,23,0.10)"
    )
    fig.add_annotation(
        x=2.10, y=(shaft.lower_um + shaft.upper_um)/2,
        text=f"<b>Eje {shaft.symbol}{shaft.grade}</b>",
        showarrow=False, font=dict(size=12, color=BLACK)
    )

    # Limit labels outside the zones to avoid overlap.
    fig.add_annotation(
        x=0.47, y=hole.upper_um,
        text=f"ES = {hole.upper_um:.0f} µm",
        showarrow=True, arrowhead=2, ax=-70, ay=0,
        arrowcolor=ORANGE, font=dict(size=11, color=ORANGE),
        bgcolor="rgba(255,255,255,.96)"
    )
    fig.add_annotation(
        x=0.47, y=hole.lower_um,
        text=f"EI = {hole.lower_um:.0f} µm",
        showarrow=True, arrowhead=2, ax=-70, ay=0,
        arrowcolor=ORANGE, font=dict(size=11, color=ORANGE),
        bgcolor="rgba(255,255,255,.96)"
    )
    fig.add_annotation(
        x=2.53, y=shaft.upper_um,
        text=f"es = {shaft.upper_um:.0f} µm",
        showarrow=True, arrowhead=2, ax=70, ay=0,
        arrowcolor=BLACK, font=dict(size=11, color=BLACK),
        bgcolor="rgba(255,255,255,.96)"
    )
    fig.add_annotation(
        x=2.53, y=shaft.lower_um,
        text=f"ei = {shaft.lower_um:.0f} µm",
        showarrow=True, arrowhead=2, ax=70, ay=0,
        arrowcolor=BLACK, font=dict(size=11, color=BLACK),
        bgcolor="rgba(255,255,255,.96)"
    )

    fig.update_layout(
        height=560,
        margin=dict(l=100, r=100, t=35, b=50),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        xaxis=dict(
            visible=False,
            range=[0.0, 3.0],
            fixedrange=True,
        ),
        yaxis=dict(
            title="Desviación respecto del nominal [µm]",
            range=[ymin-pad, ymax+pad],
            zeroline=False,
            gridcolor="#efefef",
        ),
        font=dict(family="Arial, sans-serif", color="#262730"),
    )

    fig.add_annotation(
        x=0.5, y=-0.10, xref="paper", yref="paper",
        text=(
            "La letra posiciona la zona respecto de la línea cero; el grado IT define su ancho. "
            "Mayúsculas para agujero, minúsculas para eje."
        ),
        showarrow=False, font=dict(size=11, color=GRAY)
    )
    return fig


def make_fit_interval_figure(fit):
    jmin = fit.clearance_min_um
    jmax = fit.clearance_max_um

    xmin = min(jmin, jmax, 0.0)
    xmax = max(jmin, jmax, 0.0)
    span = max(xmax - xmin, 10.0)
    pad = 0.25 * span

    fig = go.Figure()

    fig.add_shape(
        type="line", x0=0, x1=0, y0=0.18, y1=0.82,
        line=dict(color=GRAY, width=2, dash="dash")
    )
    fig.add_annotation(
        x=0, y=0.92,
        text="<b>0 µm</b><br>línea a línea",
        showarrow=False, font=dict(size=11, color=GRAY)
    )

    # Interval bar
    x0, x1 = sorted([jmin, jmax])
    fig.add_shape(
        type="rect", x0=x0, x1=x1, y0=0.35, y1=0.65,
        line=dict(color=ORANGE, width=2.5),
        fillcolor="rgba(242,142,28,0.25)"
    )

    fig.add_annotation(
        x=jmin, y=0.30,
        text=f"Jmín = {jmin:.0f} µm",
        showarrow=True, arrowhead=2, ax=0, ay=48,
        arrowcolor=BLACK, font=dict(size=11, color=BLACK),
        bgcolor="rgba(255,255,255,.96)"
    )
    fig.add_annotation(
        x=jmax, y=0.70,
        text=f"Jmáx = {jmax:.0f} µm",
        showarrow=True, arrowhead=2, ax=0, ay=-48,
        arrowcolor=ORANGE, font=dict(size=11, color=ORANGE),
        bgcolor="rgba(255,255,255,.96)"
    )

    fig.add_annotation(
        x=(xmin-pad+xmin)/2, y=0.12,
        text="Interferencia",
        showarrow=False, font=dict(size=11, color=GRAY)
    )
    fig.add_annotation(
        x=(xmax+xmax+pad)/2, y=0.12,
        text="Juego",
        showarrow=False, font=dict(size=11, color=GRAY)
    )

    fig.update_layout(
        height=350,
        margin=dict(l=60, r=60, t=35, b=55),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        xaxis=dict(
            title="Juego equivalente J = D_agujero − d_eje [µm]",
            range=[xmin-pad, xmax+pad],
            zeroline=False,
            gridcolor="#efefef",
        ),
        yaxis=dict(visible=False, range=[0, 1]),
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_it_grade_figure(nominal_mm, it_values: dict[int, float], selected_grades: list[int]):
    grades = sorted(it_values.keys())
    vals = [it_values[g] for g in grades]

    colors = [ORANGE if g in selected_grades else BLACK for g in grades]

    fig = go.Figure(go.Bar(
        x=[f"IT{g}" for g in grades],
        y=vals,
        marker=dict(color=colors),
        text=[f"{v:.0f} µm" for v in vals],
        textposition="outside",
    ))
    fig.update_layout(
        height=430,
        margin=dict(l=55, r=25, t=35, b=45),
        yaxis_title="Ancho de tolerancia [µm]",
        xaxis_title=f"Grado IT para D nominal = {nominal_mm:.3f} mm",
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_process_cost_figure():
    x = list(range(5, 17))
    # Pedagogical qualitative index; no claim of monetary cost.
    effort = [100, 90, 78, 68, 58, 49, 41, 34, 28, 23, 19, 16]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=effort,
        mode="lines+markers",
        line=dict(color=ORANGE, width=3),
        marker=dict(size=8, color=BLACK),
        name="Exigencia relativa"
    ))
    fig.update_layout(
        height=390,
        margin=dict(l=55, r=25, t=35, b=45),
        xaxis_title="Grado IT",
        yaxis_title="Exigencia relativa de proceso",
        yaxis=dict(showticklabels=False, gridcolor="#efefef"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_measurement_position_figure(value_mm, min_mm, max_mm, label):
    nominal = 0.5 * (min_mm + max_mm)
    span = max(max_mm - min_mm, 1e-6)
    pad = 0.45 * span

    fig = go.Figure()
    fig.add_shape(
        type="rect",
        x0=min_mm, x1=max_mm, y0=0.35, y1=0.65,
        line=dict(color=ORANGE, width=2),
        fillcolor="rgba(242,142,28,0.20)"
    )
    fig.add_shape(
        type="line",
        x0=value_mm, x1=value_mm, y0=0.22, y1=0.78,
        line=dict(color=BLACK, width=4)
    )
    fig.add_annotation(
        x=value_mm, y=0.86,
        text=f"{label} = {value_mm:.3f} mm",
        showarrow=False, font=dict(size=11, color=BLACK)
    )
    fig.add_annotation(
        x=min_mm, y=0.25,
        text=f"Lím. inf. {min_mm:.3f}",
        showarrow=False, font=dict(size=10, color=GRAY),
        xanchor="left"
    )
    fig.add_annotation(
        x=max_mm, y=0.25,
        text=f"Lím. sup. {max_mm:.3f}",
        showarrow=False, font=dict(size=10, color=GRAY),
        xanchor="right"
    )

    fig.update_layout(
        height=260,
        margin=dict(l=40, r=40, t=25, b=35),
        xaxis=dict(range=[min_mm-pad, max_mm+pad], gridcolor="#efefef"),
        yaxis=dict(visible=False, range=[0, 1]),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_capability_figure(xs, ys, lsl_mm, usl_mm, mean_mm):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode="lines",
        line=dict(color=BLACK, width=3),
        fill="tozeroy",
        fillcolor="rgba(23,23,23,0.07)",
        name="Distribución estimada",
    ))

    fig.add_vline(
        x=lsl_mm,
        line=dict(color=ORANGE, width=2.5, dash="dash"),
        annotation_text="LSL",
        annotation_position="top left",
    )
    fig.add_vline(
        x=usl_mm,
        line=dict(color=ORANGE, width=2.5, dash="dash"),
        annotation_text="USL",
        annotation_position="top right",
    )
    fig.add_vline(
        x=mean_mm,
        line=dict(color=BLACK, width=2),
        annotation_text="Media",
        annotation_position="bottom",
    )

    fig.update_layout(
        height=430,
        margin=dict(l=50, r=30, t=35, b=50),
        xaxis_title="Dimensión medida [mm]",
        yaxis_title="Densidad relativa",
        yaxis=dict(showticklabels=False, gridcolor="#efefef"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_thermal_clearance_figure(clearance_ref_um, clearance_op_um):
    fig = go.Figure(go.Bar(
        x=["Referencia", "Operación"],
        y=[clearance_ref_um, clearance_op_um],
        marker=dict(color=[BLACK, ORANGE]),
        text=[f"{clearance_ref_um:.0f} µm", f"{clearance_op_um:.0f} µm"],
        textposition="outside",
    ))

    fig.add_hline(
        y=0,
        line=dict(color=GRAY, width=2, dash="dash"),
        annotation_text="Línea a línea",
        annotation_position="bottom right",
    )

    ymin = min(clearance_ref_um, clearance_op_um, 0.0)
    ymax = max(clearance_ref_um, clearance_op_um, 0.0)
    span = max(ymax-ymin, 10.0)

    fig.update_layout(
        height=390,
        margin=dict(l=55, r=30, t=35, b=45),
        yaxis_title="Juego (+) / interferencia (−) [µm]",
        yaxis=dict(range=[ymin-0.25*span, ymax+0.30*span], gridcolor="#efefef"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig
