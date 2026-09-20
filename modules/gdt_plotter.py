from __future__ import annotations

import math
import plotly.graph_objects as go

ORANGE = "#f28e1c"
BLACK = "#171717"
GRAY = "#747980"
LIGHT = "#e8eaed"


def make_form_zone_figure(control: str, tolerance_mm: float):
    fig = go.Figure()
    c = control.lower()

    if "rectitud" in c:
        x = [0, 1, 2, 3, 4, 5, 6]
        y = [0.00, 0.01, -0.005, 0.012, -0.008, 0.004, 0.0]
        half = tolerance_mm/2
        fig.add_shape(type="rect", x0=0, x1=6, y0=-half, y1=half,
                      line=dict(color=ORANGE, width=2),
                      fillcolor="rgba(242,142,28,0.10)")
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers",
                                 line=dict(color=BLACK, width=3),
                                 marker=dict(size=7, color=BLACK)))
        fig.update_xaxes(title="Longitud de evaluación")
        fig.update_yaxes(title="Desviación [mm]")
    elif "planitud" in c:
        fig.add_shape(type="rect", x0=0.7, x1=6.3, y0=2.2, y1=4.8,
                      line=dict(color=ORANGE, width=2),
                      fillcolor="rgba(242,142,28,0.08)")
        pts_x = [1,1.8,2.6,3.4,4.2,5.0,5.8]
        pts_y = [2.7,3.1,3.9,3.4,4.2,3.6,4.0]
        fig.add_trace(go.Scatter(x=pts_x, y=pts_y, mode="lines+markers",
                                 line=dict(color=BLACK, width=2),
                                 marker=dict(size=7, color=BLACK)))
        fig.add_annotation(x=3.5, y=5.25, text="Zona entre dos planos paralelos",
                           showarrow=False, font=dict(size=12, color=ORANGE))
        fig.update_xaxes(visible=False, range=[0,7])
        fig.update_yaxes(visible=False, range=[1.5,5.8])
    elif "redondez" in c or "circularidad" in c:
        theta = [i*2*math.pi/180 for i in range(181)]
        r0 = 2.0
        tol = max(tolerance_mm, 0.01)*7
        outer = [r0+tol/2 for _ in theta]
        inner = [r0-tol/2 for _ in theta]
        actual = [r0 + 0.08*math.sin(3*t) + 0.04*math.sin(7*t) for t in theta]
        fig.add_trace(go.Scatterpolar(theta=[math.degrees(t) for t in theta], r=outer,
                                      mode="lines", line=dict(color=ORANGE, width=2)))
        fig.add_trace(go.Scatterpolar(theta=[math.degrees(t) for t in theta], r=inner,
                                      mode="lines", line=dict(color=ORANGE, width=2)))
        fig.add_trace(go.Scatterpolar(theta=[math.degrees(t) for t in theta], r=actual,
                                      mode="lines", line=dict(color=BLACK, width=3)))
        fig.update_polars(radialaxis=dict(visible=False), angularaxis=dict(visible=False))
    else:  # cilindricidad
        for z in [0.8, 1.8, 2.8, 3.8]:
            fig.add_shape(type="circle", x0=2.0, x1=5.8, y0=z, y1=z+1.2,
                          line=dict(color=ORANGE, width=1.8))
            fig.add_shape(type="circle", x0=2.3, x1=5.5, y0=z+0.12, y1=z+1.08,
                          line=dict(color=BLACK, width=1.5))
        fig.add_annotation(x=3.9, y=5.5, text="Superficie completa contenida entre dos cilindros",
                           showarrow=False, font=dict(size=12, color=GRAY))
        fig.update_xaxes(visible=False, range=[1.3,6.5])
        fig.update_yaxes(visible=False, range=[0.3,6.0])

    fig.update_layout(
        height=430,
        margin=dict(l=55, r=35, t=35, b=45),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_orientation_figure(kind: str, tolerance_mm: float):
    fig = go.Figure()
    kind_l = kind.lower()

    # Datum A
    fig.add_shape(type="rect", x0=0.8, x1=6.6, y0=0.9, y1=1.25,
                  line=dict(color=BLACK, width=2), fillcolor="rgba(23,23,23,0.08)")
    fig.add_annotation(x=1.0, y=0.55, text="<b>Datum A</b>", showarrow=False,
                       font=dict(size=12, color=BLACK))

    if "paralel" in kind_l:
        fig.add_shape(type="rect", x0=1.2, x1=6.2, y0=3.2, y1=4.0,
                      line=dict(color=ORANGE, width=2),
                      fillcolor="rgba(242,142,28,0.10)")
        fig.add_shape(type="line", x0=1.5, x1=5.9, y0=3.48, y1=3.70,
                      line=dict(color=BLACK, width=3))
        fig.add_annotation(x=3.7, y=4.35, text="Zona paralela respecto de A",
                           showarrow=False, font=dict(size=12, color=ORANGE))
    else:
        # Perpendicularity
        fig.add_shape(type="rect", x0=3.2, x1=4.0, y0=1.25, y1=5.8,
                      line=dict(color=ORANGE, width=2),
                      fillcolor="rgba(242,142,28,0.10)")
        fig.add_shape(type="line", x0=3.55, x1=3.82, y0=1.25, y1=5.45,
                      line=dict(color=BLACK, width=3))
        fig.add_annotation(x=4.55, y=4.7, text="Zona a 90° de A",
                           showarrow=False, font=dict(size=12, color=ORANGE))

    fig.update_layout(
        height=420,
        margin=dict(l=30, r=30, t=30, b=30),
        xaxis=dict(visible=False, range=[0.3,7.0]),
        yaxis=dict(visible=False, range=[0.2,6.2]),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_position_figure(dx_mm: float, dy_mm: float, tolerance_diam_mm: float):
    fig = go.Figure()

    radius = tolerance_diam_mm/2
    fig.add_shape(type="circle",
                  x0=-radius, x1=radius, y0=-radius, y1=radius,
                  line=dict(color=ORANGE, width=3),
                  fillcolor="rgba(242,142,28,0.10)")
    fig.add_shape(type="line", x0=-radius*1.35, x1=radius*1.35, y0=0, y1=0,
                  line=dict(color=GRAY, width=1, dash="dash"))
    fig.add_shape(type="line", x0=0, x1=0, y0=-radius*1.35, y1=radius*1.35,
                  line=dict(color=GRAY, width=1, dash="dash"))

    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode="markers",
        marker=dict(size=12, color=BLACK),
        name="Posición teórica"
    ))
    fig.add_trace(go.Scatter(
        x=[dx_mm], y=[dy_mm], mode="markers",
        marker=dict(size=14, color=ORANGE, line=dict(color=BLACK, width=2)),
        name="Centro real"
    ))
    fig.add_shape(type="line", x0=0, x1=dx_mm, y0=0, y1=dy_mm,
                  line=dict(color=BLACK, width=2))

    lim = max(radius*1.5, abs(dx_mm)*1.4, abs(dy_mm)*1.4, 0.05)
    fig.update_layout(
        height=390,
        margin=dict(l=45, r=25, t=25, b=45),
        xaxis=dict(title="Δx [mm]", range=[-lim, lim], zeroline=False, gridcolor="#efefef"),
        yaxis=dict(title="Δy [mm]", range=[-lim, lim], scaleanchor="x", scaleratio=1,
                   zeroline=False, gridcolor="#efefef"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=True,
        legend=dict(orientation="h", y=-0.13, x=0.5, xanchor="center"),
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_datum_321_figure(primary=True, secondary=True, tertiary=True):
    fig = go.Figure()

    # Part
    fig.add_shape(type="rect", x0=2.2, x1=6.5, y0=2.2, y1=5.5,
                  line=dict(color=BLACK, width=3),
                  fillcolor="rgba(242,142,28,0.06)")

    # Primary contacts
    if primary:
        for x in [2.8, 4.35, 5.9]:
            fig.add_trace(go.Scatter(x=[x], y=[2.05], mode="markers",
                                     marker=dict(size=12, color=ORANGE, symbol="triangle-up")))
        fig.add_annotation(x=4.35, y=1.55, text="<b>A · 3 apoyos</b>",
                           showarrow=False, font=dict(size=12, color=ORANGE))

    # Secondary contacts
    if secondary:
        for y in [3.0, 4.5]:
            fig.add_trace(go.Scatter(x=[2.05], y=[y], mode="markers",
                                     marker=dict(size=12, color=BLACK, symbol="triangle-right")))
        fig.add_annotation(x=1.3, y=3.75, text="<b>B · 2 apoyos</b>",
                           showarrow=False, font=dict(size=12, color=BLACK), textangle=-90)

    # Tertiary
    if tertiary:
        fig.add_trace(go.Scatter(x=[6.65], y=[3.7], mode="markers",
                                 marker=dict(size=12, color=GRAY, symbol="triangle-left")))
        fig.add_annotation(x=7.25, y=3.7, text="<b>C · 1 apoyo</b>",
                           showarrow=False, font=dict(size=12, color=GRAY))

    fig.add_annotation(x=4.35, y=5.95,
                       text="Pieza localizada progresivamente por el sistema de referencias A-B-C",
                       showarrow=False, font=dict(size=12, color=GRAY))

    fig.update_layout(
        height=420,
        margin=dict(l=30, r=30, t=30, b=30),
        xaxis=dict(visible=False, range=[0.5,8.0]),
        yaxis=dict(visible=False, range=[1.0,6.4]),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_runout_figure(readings_mm, tolerance_mm):
    angles = [i*360/(len(readings_mm)-1) if len(readings_mm)>1 else 0 for i in range(len(readings_mm))]
    mean = sum(readings_mm)/len(readings_mm)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=angles, y=[(v-mean)*1000 for v in readings_mm],
        mode="lines+markers",
        line=dict(color=BLACK, width=3),
        marker=dict(size=8, color=ORANGE),
    ))
    half = tolerance_mm*1000/2
    fig.add_hrect(y0=-half, y1=half,
                  line_width=0,
                  fillcolor="rgba(242,142,28,0.10)")
    fig.add_hline(y=0, line=dict(color=GRAY, dash="dash"))
    fig.update_layout(
        height=370,
        margin=dict(l=50, r=25, t=25, b=45),
        xaxis_title="Ángulo de rotación [°]",
        yaxis_title="Desviación respecto del promedio [µm]",
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_mmr_figure(feature_type, mms_mm, actual_mm, specified_tol_mm, available_tol_mm):
    labels = ["Tamaño en MMR", "Tamaño real", "Tol. geométrica indicada", "Tol. geométrica disponible"]
    values = [mms_mm, actual_mm, specified_tol_mm, available_tol_mm]
    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker=dict(color=[BLACK, ORANGE, BLACK, ORANGE]),
        text=[f"{v:.3f} mm" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        height=380,
        margin=dict(l=50, r=25, t=25, b=80),
        yaxis_title="Magnitud [mm]",
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig
