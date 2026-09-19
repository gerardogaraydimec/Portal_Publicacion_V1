from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .beam_cases import CASES
from .beam_engine import sample_segments, point_state, discontinuities, domain_end

ORANGE = "#f28e1c"
BLACK = "#151515"
MUTED = "#737986"
GRID = "#eceff2"


def _support_fixed(fig, x, side="left", row=1):
    fig.add_shape(
        type="line", x0=x, x1=x, y0=-0.62, y1=0.62,
        line=dict(color=BLACK, width=5), row=row, col=1
    )
    sign = -1 if side == "left" else 1
    for y in np.linspace(-0.56, 0.56, 8):
        fig.add_shape(
            type="line",
            x0=x + sign * 0.12, x1=x,
            y0=y - 0.12, y1=y,
            line=dict(color=MUTED, width=1),
            row=row, col=1,
        )


def _support_pin(fig, x, row=1):
    dx = 0.18
    fig.add_trace(go.Scatter(
        x=[x-dx, x, x+dx, x-dx],
        y=[-0.42, 0.0, -0.42, -0.42],
        mode="lines",
        fill="toself",
        fillcolor="rgba(242,142,28,.12)",
        line=dict(color=BLACK, width=2),
        hoverinfo="skip",
        showlegend=False,
    ), row=row, col=1)
    fig.add_shape(
        type="line",
        x0=x-dx*1.25, x1=x+dx*1.25,
        y0=-0.46, y1=-0.46,
        line=dict(color=BLACK, width=2),
        row=row, col=1,
    )


def _support_roller(fig, x, row=1):
    _support_pin(fig, x, row=row)
    fig.add_trace(go.Scatter(
        x=[x-0.08, x+0.08],
        y=[-0.56, -0.56],
        mode="markers",
        marker=dict(size=7, color="white", line=dict(color=BLACK, width=1.5)),
        hoverinfo="skip",
        showlegend=False,
    ), row=row, col=1)
    fig.add_shape(
        type="line",
        x0=x-0.25, x1=x+0.25,
        y0=-0.66, y1=-0.66,
        line=dict(color=BLACK, width=2),
        row=row, col=1,
    )


def _down_arrow(fig, x, label, y0=1.42, y1=0.12, row=1):
    axis_suffix = "" if row == 1 else str(row)
    fig.add_annotation(
        x=x, y=y1, ax=x, ay=y0,
        xref=f"x{axis_suffix}",
        yref=f"y{axis_suffix}",
        axref=f"x{axis_suffix}",
        ayref=f"y{axis_suffix}",
        text=label,
        showarrow=True,
        arrowhead=3,
        arrowsize=1.15,
        arrowwidth=2.2,
        arrowcolor=BLACK,
        font=dict(size=13, color=BLACK),
        bgcolor="rgba(255,255,255,.88)",
        borderpad=2,
    )


def _udl(fig, x0, x1, label="w", row=1):
    xs = np.linspace(x0 + 0.07*(x1-x0), x1 - 0.07*(x1-x0), 10)
    fig.add_shape(
        type="line",
        x0=x0, x1=x1, y0=1.33, y1=1.33,
        line=dict(color=BLACK, width=2),
        row=row, col=1,
    )
    for x in xs:
        _down_arrow(fig, float(x), "", y0=1.33, y1=0.12, row=row)
    fig.add_annotation(
        x=(x0+x1)/2, y=1.60,
        text=label,
        showarrow=False,
        font=dict(size=13, color=BLACK),
        row=row, col=1,
    )


def _moment_label(fig, x, label, row=1):
    fig.add_annotation(
        x=x, y=0.78,
        text=f"↺ {label}",
        showarrow=False,
        font=dict(size=18, color=BLACK),
        bgcolor="rgba(255,255,255,.84)",
        borderpad=2,
        row=row, col=1,
    )


def _point_label(fig, x, label, y=-0.92, row=1):
    fig.add_annotation(
        x=x, y=y,
        text=label,
        showarrow=False,
        font=dict(size=11, color=MUTED),
        row=row, col=1,
    )


def _draw_supports(fig, case_id, L, total):
    family = CASES[case_id]["family"]

    if family.startswith("Voladizo"):
        _support_fixed(fig, 0, side="left")
        _point_label(fig, 0, "A")

    elif family == "Simplemente apoyada":
        _support_pin(fig, 0)
        if case_id == "simple_overhang_load":
            _support_roller(fig, L)
            _point_label(fig, 0, "A")
            _point_label(fig, L, "B")
            _point_label(fig, total, "C")
        else:
            _support_roller(fig, L)
            _point_label(fig, 0, "A")
            _point_label(fig, L, "B")

    elif family == "Empotrada + apoyo simple":
        _support_fixed(fig, 0, side="left")
        _support_roller(fig, L)
        _point_label(fig, 0, "A")
        _point_label(fig, L, "B")

    elif family == "Empotrada–empotrada":
        _support_fixed(fig, 0, side="left")
        _support_fixed(fig, L, side="right")
        _point_label(fig, 0, "A")
        _point_label(fig, L, "B")


def _draw_loads(fig, case_id, p):
    L = float(p["L"])
    total = domain_end(case_id, p)
    case = CASES[case_id]
    load_type = case["load_type"]

    if load_type == "point_end":
        _down_arrow(fig, total, f"F = {p['F']:.3g} kN")

    elif load_type == "point_center":
        _down_arrow(fig, L/2, f"F = {p['F']:.3g} kN")
        _point_label(fig, L/2, "Carga en L/2", y=-1.12)

    elif load_type == "point":
        xpos = float(p["a"])
        _down_arrow(fig, xpos, f"F = {p['F']:.3g} kN")
        _point_label(fig, xpos, f"a = {xpos:.3g} m", y=-1.12)

    elif load_type == "udl":
        _udl(fig, 0, L, f"w = {p['w']:.3g} kN/m")

    elif load_type == "moment_end":
        _moment_label(fig, total*0.92, f"M₀ = {p['M0']:.3g} kN·m")

    elif load_type == "moment":
        xpos = float(p["a"])
        _moment_label(fig, xpos, f"M₀ = {p['M0']:.3g} kN·m")
        _point_label(fig, xpos, f"a = {xpos:.3g} m", y=-1.12)

    elif load_type == "twin_points":
        a = float(p["a"])
        _down_arrow(fig, a, f"F = {p['F']:.3g}")
        _down_arrow(fig, L-a, f"F = {p['F']:.3g}")
        _point_label(fig, a, f"a = {a:.3g} m", y=-1.12)
        _point_label(fig, L-a, f"L−a", y=-1.12)

    elif load_type == "overhang_point":
        a = float(p["a"])
        _down_arrow(fig, total, f"F = {p['F']:.3g} kN")
        _point_label(fig, L + a/2, f"a = {a:.3g} m", y=-1.12)

    # span annotation
    if case_id == "simple_overhang_load":
        fig.add_annotation(
            x=L/2, y=-1.34, text=f"L = {L:.3g} m entre apoyos",
            showarrow=False, font=dict(size=11, color=MUTED), row=1, col=1
        )
    else:
        fig.add_annotation(
            x=L/2, y=-1.34, text=f"L = {L:.3g} m",
            showarrow=False, font=dict(size=11, color=MUTED), row=1, col=1
        )


def make_figure(case_id: str, p: dict, x_probe: float):
    L = float(p["L"])
    total = domain_end(case_id, p)
    segments = sample_segments(case_id, p, n_per_segment=500)
    disc = discontinuities(case_id, p)
    probe = point_state(case_id, p, x_probe)

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.32, 0.30, 0.38],
        vertical_spacing=0.09,
        subplot_titles=(
            "Esquema de carga",
            "Diagrama de fuerza cortante V(x)",
            "Diagrama de momento flector M(x)",
        ),
    )

    fig.add_trace(go.Scatter(
        x=[0, total], y=[0, 0],
        mode="lines",
        line=dict(color=BLACK, width=7),
        hoverinfo="skip",
        showlegend=False,
    ), row=1, col=1)

    _draw_supports(fig, case_id, L, total)
    _draw_loads(fig, case_id, p)

    for s in segments:
        fig.add_trace(go.Scatter(
            x=s["x"], y=s["V"],
            mode="lines",
            line=dict(color=ORANGE, width=3),
            fill="tozeroy",
            fillcolor="rgba(242,142,28,.15)",
            hovertemplate="x=%{x:.3f} m<br>V=%{y:.3f} kN<extra></extra>",
            showlegend=False,
        ), row=2, col=1)

        fig.add_trace(go.Scatter(
            x=s["x"], y=s["M"],
            mode="lines",
            line=dict(color=BLACK, width=3),
            fill="tozeroy",
            fillcolor="rgba(21,21,21,.10)",
            hovertemplate="x=%{x:.3f} m<br>M=%{y:.3f} kN·m<extra></extra>",
            showlegend=False,
        ), row=3, col=1)

    # Jumps in V
    for xj in disc["V"]:
        st = point_state(case_id, p, xj)
        if st["V_left"] is not None and abs(st["V_left"] - st["V_right"]) > 1e-9:
            fig.add_trace(go.Scatter(
                x=[xj, xj], y=[st["V_left"], st["V_right"]],
                mode="lines",
                line=dict(color=ORANGE, width=2, dash="dot"),
                hoverinfo="skip", showlegend=False,
            ), row=2, col=1)

    # Jumps in M
    for xj in disc["M"]:
        st = point_state(case_id, p, xj)
        if st["M_left"] is not None and abs(st["M_left"] - st["M_right"]) > 1e-9:
            fig.add_trace(go.Scatter(
                x=[xj, xj], y=[st["M_left"], st["M_right"]],
                mode="lines",
                line=dict(color=BLACK, width=2, dash="dot"),
                hoverinfo="skip", showlegend=False,
            ), row=3, col=1)

    # Probe line
    for row in (1, 2, 3):
        fig.add_vline(
            x=x_probe,
            line_width=1.7,
            line_dash="dash",
            line_color=ORANGE,
            row=row, col=1,
        )

    v_vals = [probe["V"]]
    if probe["V_left"] is not None and abs(probe["V_left"] - probe["V_right"]) > 1e-8:
        v_vals = [probe["V_left"], probe["V_right"]]

    m_vals = [probe["M"]]
    if probe["M_left"] is not None and abs(probe["M_left"] - probe["M_right"]) > 1e-8:
        m_vals = [probe["M_left"], probe["M_right"]]

    fig.add_trace(go.Scatter(
        x=[x_probe]*len(v_vals), y=v_vals,
        mode="markers",
        marker=dict(size=10, color=ORANGE, line=dict(color="white", width=2)),
        hoverinfo="skip", showlegend=False,
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=[x_probe]*len(m_vals), y=m_vals,
        mode="markers",
        marker=dict(size=10, color=BLACK, line=dict(color="white", width=2)),
        hoverinfo="skip", showlegend=False,
    ), row=3, col=1)

    # More headroom than V0.1: avoids clipping of arrows / labels in upper schematic.
    fig.update_yaxes(
        range=[-1.55, 2.05],
        showgrid=False, zeroline=False, showticklabels=False,
        row=1, col=1,
    )
    fig.update_yaxes(
        title_text="V [kN]",
        zeroline=True, zerolinecolor="#90949b",
        gridcolor=GRID,
        row=2, col=1,
    )
    fig.update_yaxes(
        title_text="M [kN·m]",
        zeroline=True, zerolinecolor="#90949b",
        gridcolor=GRID,
        row=3, col=1,
    )

    xr = [-0.035*total, 1.035*total]
    fig.update_xaxes(range=xr, row=1, col=1)
    fig.update_xaxes(range=xr, row=2, col=1)
    fig.update_xaxes(range=xr, title_text="x [m]", row=3, col=1)

    fig.update_layout(
        height=790,
        margin=dict(l=58, r=28, t=92, b=42),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", color="#262730"),
        hoverlabel=dict(bgcolor="white"),
    )

    for ann in fig.layout.annotations[:3]:
        ann.font = dict(size=14, color="#262730")

    return fig
