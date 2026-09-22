from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots

ORANGE = "#f28e1c"
BLACK = "#171717"
GRID = "#eceff2"
GRAY = "#737986"


def make_stress_distribution_figure(result):
    fig = make_subplots(
        rows=1,
        cols=2,
        shared_yaxes=True,
        horizontal_spacing=0.12,
        subplot_titles=("Esfuerzo normal por flexión", "Esfuerzo cortante"),
    )

    fig.add_trace(
        go.Scatter(
            x=result.sigma_mpa,
            y=result.y_mm,
            mode="lines",
            line=dict(color=BLACK, width=3),
            fill="tozerox",
            fillcolor="rgba(23,23,23,.06)",
            hovertemplate="σx=%{x:.4f} MPa<br>y=%{y:.2f} mm<extra></extra>",
            name="σx(y)",
        ),
        row=1,
        col=1,
    )

    if result.shear_available and result.tau_mpa is not None:
        fig.add_trace(
            go.Scatter(
                x=result.tau_mpa,
                y=result.y_mm,
                mode="lines",
                line=dict(color=ORANGE, width=3),
                fill="tozerox",
                fillcolor="rgba(242,142,28,.09)",
                hovertemplate="τxy=%{x:.4f} MPa<br>y=%{y:.2f} mm<extra></extra>",
                name="τxy(y)",
            ),
            row=1,
            col=2,
        )
    else:
        fig.add_annotation(
            x=0.5,
            y=0.5,
            xref="x2 domain",
            yref="y2 domain",
            text="Se requiere geometría<br>para obtener Q(y) y t(y)",
            showarrow=False,
            font=dict(color=GRAY, size=14),
        )

    fig.add_vline(x=0, line=dict(color="#9aa0a6", width=1), row=1, col=1)
    fig.add_vline(x=0, line=dict(color="#9aa0a6", width=1), row=1, col=2)
    fig.add_hline(y=0, line=dict(color=ORANGE, width=1.3, dash="dash"), row=1, col=1)
    fig.add_hline(y=0, line=dict(color=ORANGE, width=1.3, dash="dash"), row=1, col=2)

    fig.update_xaxes(title_text="σx [MPa]", gridcolor=GRID, row=1, col=1)
    fig.update_xaxes(title_text="τxy [MPa]", gridcolor=GRID, row=1, col=2)
    fig.update_yaxes(title_text="y [mm]", gridcolor=GRID, row=1, col=1)
    fig.update_yaxes(gridcolor=GRID, row=1, col=2)

    fig.update_layout(
        height=520,
        margin=dict(l=55, r=25, t=65, b=45),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig
