from __future__ import annotations

import math
import numpy as np
import plotly.graph_objects as go

from modules.pump_engine import (
    pump_group_head,
    pump_group_efficiency_and_each_flow,
    system_head,
)

ORANGE = "#f28e1c"
BLACK = "#171717"
GRAY = "#747980"
LIGHT = "#e8eaed"


def make_system_schematic(
    z1_m: float,
    z2_m: float,
    p1_kPa_g: float,
    p2_kPa_g: float,
    L_m: float,
    D_mm: float,
    accessory_count: int,
):
    fig = go.Figure()

    zmin = min(z1_m, z2_m, 0.0)
    zmax = max(z1_m, z2_m, 0.0)
    span = max(zmax - zmin, 6.0)
    datum = zmin - 0.25 * span

    x1, xp, x2 = 1.2, 5.0, 8.8
    tank_w = 1.2

    # Datum
    fig.add_shape(type="line", x0=0.1, x1=9.9, y0=datum, y1=datum,
                  line=dict(color=LIGHT, width=2, dash="dot"))
    fig.add_annotation(
        x=0.25, y=datum + 0.08*span,
        text="<b>Datum común · z = 0 de referencia</b>",
        showarrow=False, font=dict(size=11, color=GRAY),
        bgcolor="rgba(255,255,255,.96)"
    )

    # Tanks / boundary points.
    for x, z, p, label in [(x1, z1_m, p1_kPa_g, "Origen"), (x2, z2_m, p2_kPa_g, "Destino")]:
        fig.add_shape(type="rect", x0=x-tank_w/2, x1=x+tank_w/2,
                      y0=z-0.55, y1=z+0.55,
                      line=dict(color=BLACK, width=2.5),
                      fillcolor="rgba(242,142,28,0.07)")
        fig.add_shape(type="line", x0=x-tank_w/2+0.08, x1=x+tank_w/2-0.08,
                      y0=z+0.20, y1=z+0.20,
                      line=dict(color=ORANGE, width=2))
        fig.add_annotation(x=x, y=z+0.86, text=f"<b>{label}</b>",
                           showarrow=False, font=dict(size=12, color=BLACK))
        fig.add_annotation(x=x, y=z-0.82,
                           text=f"p = {p:.1f} kPa(g)",
                           showarrow=False, font=dict(size=11, color=GRAY),
                           bgcolor="rgba(255,255,255,.95)")

    # Pump
    pump_y = 0.5*(z1_m+z2_m)
    fig.add_shape(type="circle", x0=xp-0.42, x1=xp+0.42,
                  y0=pump_y-0.42, y1=pump_y+0.42,
                  line=dict(color=BLACK, width=2.5), fillcolor="white")
    fig.add_annotation(x=xp, y=pump_y, text="<b>P</b>", showarrow=False,
                       font=dict(size=16, color=ORANGE))
    fig.add_annotation(x=xp, y=pump_y+0.75, text="<b>Bomba</b>",
                       showarrow=False, font=dict(size=12, color=BLACK))

    # Piping from origin -> pump -> destination
    fig.add_shape(type="line", x0=x1+tank_w/2, x1=xp-0.42,
                  y0=z1_m, y1=pump_y,
                  line=dict(color=BLACK, width=4))
    fig.add_shape(type="line", x0=xp+0.42, x1=x2-tank_w/2,
                  y0=pump_y, y1=z2_m,
                  line=dict(color=BLACK, width=4))

    # Flow arrows
    fig.add_annotation(x=3.25, y=(z1_m+pump_y)/2 + 0.20,
                       ax=2.35, ay=(z1_m+pump_y)/2 + 0.20,
                       text="", showarrow=True, arrowhead=3,
                       arrowwidth=2.2, arrowcolor=ORANGE)
    fig.add_annotation(x=7.65, y=(z2_m+pump_y)/2 + 0.20,
                       ax=6.75, ay=(z2_m+pump_y)/2 + 0.20,
                       text="", showarrow=True, arrowhead=3,
                       arrowwidth=2.2, arrowcolor=ORANGE)

    # Elevation dimensions from datum.
    for x, z, symbol in [(x1-0.9, z1_m, "z₁"), (x2+0.9, z2_m, "z₂")]:
        fig.add_annotation(
            x=x, y=z, ax=x, ay=datum,
            text=f"{symbol} = {z:.2f} m",
            showarrow=True, arrowhead=2, arrowsize=1,
            arrowwidth=1.4, arrowcolor=GRAY,
            font=dict(size=11, color=GRAY),
            bgcolor="rgba(255,255,255,.96)"
        )

    fig.add_annotation(
        x=5.0, y=datum-0.18*span,
        text=f"L = {L_m:.1f} m · D = {D_mm:.0f} mm · accesorios = {accessory_count}",
        showarrow=False, font=dict(size=12, color=GRAY),
        bgcolor="rgba(255,255,255,.96)"
    )

    pad = max(2.0, 0.35*span)
    fig.update_layout(
        height=540,
        margin=dict(l=35, r=35, t=40, b=65),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(visible=False, range=[0, 10]),
        yaxis=dict(visible=False, range=[datum-pad*0.25, zmax+pad]),
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    fig.add_annotation(
        x=0.5, y=-0.06, xref="paper", yref="paper",
        text=(
            "Las cotas z₁ y z₂ se miden desde el mismo datum. La bomba agrega energía al fluido entre el origen y el destino. "
            "La geometría es esquemática: las longitudes y elevaciones no están dibujadas a la misma escala."
        ),
        showarrow=False, font=dict(size=11, color=GRAY)
    )
    return fig


def sample_curves(
    curve,
    rho,
    mu,
    L_m,
    D_mm,
    epsilon_mm,
    K_total,
    z1_m,
    z2_m,
    p1_kPa_g,
    p2_kPa_g,
    speed_ratio,
    arrangement,
    pump_count,
    q_max_m3s,
    n=260,
):
    q = np.linspace(0.0, q_max_m3s, n)
    h_pump = []
    h_sys = []
    eta = []

    for qi in q:
        h_pump.append(
            pump_group_head(curve, float(qi), speed_ratio, arrangement, pump_count)
        )
        hs, *_ = system_head(
            float(qi), rho, mu, L_m, D_mm, epsilon_mm, K_total,
            z1_m, z2_m, p1_kPa_g, p2_kPa_g
        )
        h_sys.append(hs)
        e, _ = pump_group_efficiency_and_each_flow(
            curve, float(qi), speed_ratio, arrangement, pump_count
        )
        eta.append(e)

    return q, np.array(h_pump), np.array(h_sys), np.array(eta)


def make_operating_curve_figure(
    q_m3s,
    h_pump,
    h_sys,
    op,
    curve,
    speed_ratio,
    arrangement,
    pump_count,
):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=q_m3s*1000, y=h_pump, mode="lines",
        line=dict(color=ORANGE, width=4),
        name="Curva de bomba / conjunto"
    ))
    fig.add_trace(go.Scatter(
        x=q_m3s*1000, y=h_sys, mode="lines",
        line=dict(color=BLACK, width=4),
        name="Curva del sistema"
    ))

    qbep_total = curve.Qbep_m3s * speed_ratio
    if arrangement == "Paralelo":
        qbep_total *= max(1, pump_count)
    fig.add_vline(
        x=qbep_total*1000,
        line=dict(color=GRAY, width=1.5, dash="dot"),
        annotation_text="Referencia BEP",
        annotation_position="top right"
    )

    if op.found:
        fig.add_trace(go.Scatter(
            x=[op.Q_m3s*1000], y=[op.H_m],
            mode="markers+text",
            marker=dict(size=15, color="white", line=dict(color=ORANGE, width=3)),
            text=["Punto de operación"],
            textposition="top center",
            name="Punto de operación",
            hovertemplate=f"Q={op.Q_m3s*1000:.3f} L/s<br>H={op.H_m:.3f} m<extra></extra>"
        ))

    fig.update_layout(
        height=610,
        margin=dict(l=60, r=30, t=45, b=55),
        xaxis_title="Caudal total Q [L/s]",
        yaxis_title="Altura H [m]",
        paper_bgcolor="white", plot_bgcolor="white",
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.16),
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_efficiency_figure(q_m3s, eta, op):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=q_m3s*1000, y=eta*100,
        mode="lines", line=dict(color=BLACK, width=3),
        name="Eficiencia de referencia"
    ))
    if op.found:
        fig.add_trace(go.Scatter(
            x=[op.Q_m3s*1000], y=[op.eta*100],
            mode="markers+text",
            marker=dict(size=13, color=ORANGE, line=dict(color=BLACK, width=1.5)),
            text=["Operación"], textposition="top center",
            showlegend=False
        ))
    fig.update_layout(
        height=410,
        margin=dict(l=55, r=25, t=35, b=50),
        xaxis_title="Caudal total Q [L/s]",
        yaxis_title="Eficiencia η [%]",
        yaxis_range=[0, 100],
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_head_components_figure(static_geom_m, pressure_head_m, hf_m, hm_m):
    names = ["Cota", "Presión", "Tubería recta", "Accesorios"]
    values = [static_geom_m, pressure_head_m, hf_m, hm_m]

    fig = go.Figure(go.Bar(
        x=names, y=values,
        text=[f"{v:.2f} m" for v in values],
        textposition="outside",
        marker=dict(color=[GRAY, BLACK, ORANGE, ORANGE])
    ))
    fig.update_layout(
        height=430,
        margin=dict(l=50, r=25, t=35, b=45),
        yaxis_title="Contribución a la altura [m]",
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_affinity_figure(curve, speed_ratios, q_max_m3s):
    q = np.linspace(0, q_max_m3s, 220)
    fig = go.Figure()
    shades = ["#171717", "#747980", ORANGE, "#9a9a9a"]
    for i, s in enumerate(speed_ratios):
        h = [pump_group_head(curve, float(qi), s, "1 bomba", 1) for qi in q]
        fig.add_trace(go.Scatter(
            x=q*1000, y=h, mode="lines",
            line=dict(width=3 if abs(s-1.0)<1e-9 else 2, color=shades[i % len(shades)]),
            name=f"N₂/N₁ = {s:.2f}"
        ))
    fig.update_layout(
        height=470,
        margin=dict(l=55, r=25, t=35, b=50),
        xaxis_title="Caudal Q [L/s]",
        yaxis_title="Altura H [m]",
        paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.16),
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_npsh_schematic(z_surface_minus_pump_m, p_surface_abs_kPa, pv_abs_kPa, hL_suction_m):
    fig = go.Figure()
    z_surface = z_surface_minus_pump_m
    pump_z = 0.0

    # Reservoir
    fig.add_shape(type="rect", x0=1.0, x1=3.0, y0=z_surface-0.8, y1=z_surface+0.4,
                  line=dict(color=BLACK, width=2.5), fillcolor="rgba(242,142,28,0.08)")
    fig.add_shape(type="line", x0=1.1, x1=2.9, y0=z_surface, y1=z_surface,
                  line=dict(color=ORANGE, width=3))
    fig.add_annotation(x=2.0, y=z_surface+0.75, text="<b>Superficie de succión</b>",
                       showarrow=False, font=dict(size=12, color=BLACK))

    # Pump
    fig.add_shape(type="circle", x0=6.6, x1=7.4, y0=-0.4, y1=0.4,
                  line=dict(color=BLACK, width=2.5), fillcolor="white")
    fig.add_annotation(x=7.0, y=0, text="<b>P</b>", showarrow=False,
                       font=dict(size=15, color=ORANGE))
    fig.add_annotation(x=7.0, y=0.72, text="<b>Centro de bomba</b>",
                       showarrow=False, font=dict(size=12, color=BLACK))

    # Suction line
    fig.add_shape(type="line", x0=3.0, x1=6.6, y0=z_surface, y1=0,
                  line=dict(color=BLACK, width=4))
    fig.add_annotation(x=5.2, y=0.5*z_surface+0.25,
                       ax=4.2, ay=0.5*z_surface+0.25,
                       text="", showarrow=True, arrowhead=3,
                       arrowwidth=2.2, arrowcolor=ORANGE)

    # Elevation dimension
    fig.add_annotation(
        x=3.55, y=z_surface, ax=3.55, ay=0.0,
        text=f"z_s - z_p = {z_surface_minus_pump_m:.2f} m",
        showarrow=True, arrowhead=2, arrowwidth=1.4,
        arrowcolor=GRAY, font=dict(size=11, color=GRAY),
        bgcolor="rgba(255,255,255,.96)"
    )

    fig.add_annotation(x=2.0, y=z_surface-1.12,
                       text=f"p superficie = {p_surface_abs_kPa:.1f} kPa(abs)",
                       showarrow=False, font=dict(size=11, color=GRAY))
    fig.add_annotation(x=5.0, y=-1.05,
                       text=f"hL succión = {hL_suction_m:.2f} m · pᵥ = {pv_abs_kPa:.2f} kPa(abs)",
                       showarrow=False, font=dict(size=11, color=GRAY))

    ymin = min(-1.6, z_surface-1.5)
    ymax = max(2.2, z_surface+1.3)
    fig.update_layout(
        height=430,
        margin=dict(l=35, r=30, t=35, b=35),
        xaxis=dict(visible=False, range=[0.4, 8.0]),
        yaxis=dict(visible=False, range=[ymin, ymax]),
        paper_bgcolor="white", plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_sensitivity_figure(q_m3s, h_pump, h_sys_current, h_sys_alt, op_current, op_alt, alt_label):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=q_m3s*1000, y=h_pump, mode="lines",
        line=dict(color=ORANGE, width=4),
        name="Bomba"
    ))
    fig.add_trace(go.Scatter(
        x=q_m3s*1000, y=h_sys_current, mode="lines",
        line=dict(color=BLACK, width=3),
        name="Sistema actual"
    ))
    fig.add_trace(go.Scatter(
        x=q_m3s*1000, y=h_sys_alt, mode="lines",
        line=dict(color=GRAY, width=3, dash="dash"),
        name=alt_label
    ))

    if op_current.found:
        fig.add_trace(go.Scatter(
            x=[op_current.Q_m3s*1000], y=[op_current.H_m],
            mode="markers", marker=dict(size=13, color=BLACK),
            name="Operación actual"
        ))
    if op_alt.found:
        fig.add_trace(go.Scatter(
            x=[op_alt.Q_m3s*1000], y=[op_alt.H_m],
            mode="markers", marker=dict(size=14, color="white", line=dict(color=ORANGE, width=3)),
            name="Operación alternativa"
        ))

    fig.update_layout(
        height=560,
        margin=dict(l=55, r=25, t=40, b=55),
        xaxis_title="Caudal Q [L/s]",
        yaxis_title="Altura H [m]",
        paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.17),
        hovermode="x unified",
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig
