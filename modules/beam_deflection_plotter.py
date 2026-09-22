from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ORANGE = "#f28e1c"
BLACK = "#171717"
GRAY = "#737986"
LIGHT = "#eceff2"


def make_deflection_figure(result, x_probe: float | None = None):
    x = result.x_m
    theta_mrad = result.slope_rad * 1e3
    v_mm = result.deflection_m * 1e3

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.10,
        subplot_titles=("Rotación / pendiente", "Deflexión"),
    )

    fig.add_trace(
        go.Scatter(
            x=x,
            y=theta_mrad,
            mode="lines",
            line=dict(color=BLACK, width=2.6),
            name="θ(x)",
            hovertemplate="x=%{x:.3f} m<br>θ=%{y:.4f} mrad<extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=x,
            y=v_mm,
            mode="lines",
            line=dict(color=ORANGE, width=3.0),
            fill="tozeroy",
            fillcolor="rgba(242,142,28,.08)",
            name="v(x)",
            hovertemplate="x=%{x:.3f} m<br>v=%{y:.4f} mm<extra></extra>",
        ),
        row=2,
        col=1,
    )

    fig.add_hline(y=0, line=dict(color="#a6abb2", width=1), row=1, col=1)
    fig.add_hline(y=0, line=dict(color="#a6abb2", width=1), row=2, col=1)

    if x_probe is not None:
        fig.add_vline(x=x_probe, line=dict(color=ORANGE, dash="dash", width=1.6), row=1, col=1)
        fig.add_vline(x=x_probe, line=dict(color=ORANGE, dash="dash", width=1.6), row=2, col=1)

    fig.update_yaxes(title_text="θ [mrad]", gridcolor=LIGHT, row=1, col=1)
    fig.update_yaxes(title_text="v [mm]", gridcolor=LIGHT, row=2, col=1)
    fig.update_xaxes(title_text="x [m]", gridcolor=LIGHT, row=2, col=1)
    fig.update_xaxes(gridcolor=LIGHT, row=1, col=1)

    fig.update_layout(
        height=600,
        margin=dict(l=40, r=25, t=60, b=45),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_section_figure(section_type: str, params: dict):
    fig = go.Figure()

    if section_type == "Rectangular":
        b = float(params["b_mm"])
        h = float(params["h_mm"])
        scale = max(b, h)
        bx = 3.2 * b / scale
        hy = 3.2 * h / scale
        fig.add_shape(
            type="rect",
            x0=-bx/2,
            x1=bx/2,
            y0=-hy/2,
            y1=hy/2,
            line=dict(color=BLACK, width=2.5),
            fillcolor="rgba(242,142,28,.06)",
        )
        fig.add_annotation(x=0, y=hy/2+0.45, text=f"b = {b:g} mm", showarrow=False, font=dict(size=12, color=GRAY))
        fig.add_annotation(x=bx/2+0.55, y=0, text=f"h = {h:g} mm", showarrow=False, font=dict(size=12, color=GRAY), textangle=90)

    elif section_type == "Circular maciza":
        d = float(params["d_mm"])
        fig.add_shape(type="circle", x0=-1.7, x1=1.7, y0=-1.7, y1=1.7,
                      line=dict(color=BLACK, width=2.5), fillcolor="rgba(242,142,28,.06)")
        fig.add_shape(type="line", x0=-1.7, x1=1.7, y0=0, y1=0, line=dict(color=ORANGE, width=1.8))
        fig.add_annotation(x=0, y=0.28, text=f"d = {d:g} mm", showarrow=False, font=dict(size=12, color=GRAY))

    elif section_type == "Tubular circular":
        do = float(params["do_mm"])
        t = float(params["t_mm"])
        di = do - 2*t
        ratio = max(0.05, di / do)
        fig.add_shape(type="circle", x0=-1.8, x1=1.8, y0=-1.8, y1=1.8,
                      line=dict(color=BLACK, width=2.5), fillcolor="rgba(242,142,28,.06)")
        r = 1.8 * ratio
        fig.add_shape(type="circle", x0=-r, x1=r, y0=-r, y1=r,
                      line=dict(color=BLACK, width=1.8), fillcolor="white")
        fig.add_annotation(x=0, y=2.2, text=f"Dₒ = {do:g} mm · t = {t:g} mm", showarrow=False, font=dict(size=12, color=GRAY))

    else:
        fig.add_shape(type="rect", x0=-1.7, x1=1.7, y0=-1.2, y1=1.2,
                      line=dict(color=BLACK, width=2, dash="dash"), fillcolor="white")
        fig.add_annotation(x=0, y=0, text="A, I ingresados<br>por el usuario", showarrow=False,
                           font=dict(size=15, color=GRAY), align="center")

    fig.add_shape(type="line", x0=-2.2, x1=2.2, y0=0, y1=0, line=dict(color=ORANGE, width=1.4, dash="dash"))
    fig.add_annotation(x=-2.05, y=0.25, text="eje neutro", showarrow=False, font=dict(size=10.5, color=ORANGE))

    fig.update_layout(
        height=390,
        margin=dict(l=20, r=20, t=25, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
    )
    fig.update_xaxes(visible=False, range=[-3, 3], scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False, range=[-2.7, 2.7])
    return fig
