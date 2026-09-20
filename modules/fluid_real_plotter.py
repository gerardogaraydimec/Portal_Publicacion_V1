from __future__ import annotations

import math
import numpy as np
import plotly.graph_objects as go

ORANGE = "#f28e1c"
BLACK = "#171717"
DARK_GRAY = "#52565d"
GRAY = "#7b7f86"
LIGHT = "#e8eaed"


def expand_accessories(accessories: list[dict], x0: float = 2.0, x1: float = 8.5):
    expanded = []
    order = 1
    for item in accessories:
        for n in range(int(item["count"])):
            expanded.append({
                "order": order,
                "name": item["name"],
                "symbol": item.get("symbol", "K"),
                "K": float(item["K"]),
                "index": n + 1,
            })
            order += 1
    if not expanded:
        return []
    xs = np.linspace(x0, x1, len(expanded))
    for x, item in zip(xs, expanded):
        item["x"] = float(x)
    return expanded


def make_pipe_schematic(L_m: float, D_m: float, Q_m3s: float, accessories: list[dict]):
    fig = go.Figure()

    y_top, y_bottom = 0.52, -0.52
    x_start, x_end = 1.0, 9.0

    # Pipe body.
    fig.add_shape(
        type="rect", x0=x_start, x1=x_end, y0=y_bottom, y1=y_top,
        line=dict(color=BLACK, width=3),
        fillcolor="rgba(242,142,28,0.08)"
    )

    # Centerline.
    fig.add_shape(
        type="line", x0=x_start, x1=x_end, y0=0, y1=0,
        line=dict(color=ORANGE, width=2, dash="dash")
    )

    # Section cuts.
    for x, label in [(x_start, "Sección 1"), (x_end, "Sección 2")]:
        fig.add_shape(type="line", x0=x, x1=x, y0=-0.63, y1=0.63,
                      line=dict(color=DARK_GRAY, width=4))
        fig.add_annotation(
            x=x, y=0.86, text=f"<b>{label}</b>", showarrow=False,
            font=dict(size=12, color=DARK_GRAY),
            bgcolor="rgba(255,255,255,0.96)", bordercolor=LIGHT, borderwidth=1
        )

    # Diameter dimension to the left.
    dim_x = 0.56
    fig.add_shape(type="line", x0=dim_x, x1=dim_x, y0=y_bottom, y1=y_top,
                  line=dict(color=GRAY, width=1.5))
    fig.add_shape(type="line", x0=dim_x-0.08, x1=dim_x+0.08, y0=y_bottom, y1=y_bottom,
                  line=dict(color=GRAY, width=1.5))
    fig.add_shape(type="line", x0=dim_x-0.08, x1=dim_x+0.08, y0=y_top, y1=y_top,
                  line=dict(color=GRAY, width=1.5))
    fig.add_annotation(
        x=0.28, y=0, text=f"D = {D_m*1000:.0f} mm", textangle=-90, showarrow=False,
        font=dict(size=12, color=GRAY), bgcolor="rgba(255,255,255,0.96)"
    )

    # Length dimension below.
    dim_y = -1.08
    fig.add_shape(type="line", x0=x_start, x1=x_end, y0=dim_y, y1=dim_y,
                  line=dict(color=GRAY, width=1.5))
    for x in (x_start, x_end):
        fig.add_shape(type="line", x0=x, x1=x, y0=dim_y-0.08, y1=dim_y+0.08,
                      line=dict(color=GRAY, width=1.5))
    fig.add_annotation(
        x=5.0, y=dim_y-0.17, text=f"L = {L_m:.2f} m", showarrow=False,
        font=dict(size=12, color=GRAY), bgcolor="rgba(255,255,255,0.96)"
    )

    # Flow arrow above.
    fig.add_annotation(
        x=6.1, y=1.22, ax=3.9, ay=1.22,
        text=f"<b>Q = {Q_m3s*1000:.2f} L/s</b>",
        showarrow=True, arrowhead=3, arrowsize=1.2,
        arrowwidth=2.2, arrowcolor=ORANGE,
        font=dict(size=12, color=ORANGE)
    )

    # Accessory markers as numbered nodes only.
    expanded = expand_accessories(accessories)
    for i, item in enumerate(expanded):
        x = item["x"]
        marker_y = 0.0
        label_y = 1.45 if i % 2 == 0 else -1.45
        stub_y = 0.30 if label_y > 0 else -0.30

        fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=stub_y,
                      line=dict(color=GRAY, width=1.1, dash="dot"))
        fig.add_trace(go.Scatter(
            x=[x], y=[marker_y], mode="markers+text",
            marker=dict(size=16, color=ORANGE, line=dict(color=BLACK, width=1.4)),
            text=[str(item["order"])], textfont=dict(color="white", size=10),
            textposition="middle center",
            hovertemplate=(
                f"<b>{item['order']}</b> · {item['name']}"
                f"<br>{item['symbol']}"
                f"<br>K={item['K']:.3g}<extra></extra>"
            ),
            showlegend=False,
        ))
        fig.add_annotation(
            x=x, y=stub_y, ax=x, ay=label_y,
            text=f"<b>{item['order']}</b>",
            showarrow=True, arrowhead=0, arrowsize=1,
            arrowwidth=1.1, arrowcolor=GRAY,
            font=dict(size=11, color=DARK_GRAY),
            bgcolor="rgba(255,255,255,0.98)",
            bordercolor=LIGHT, borderwidth=1, borderpad=4,
        )

    # Visual direction of flow.
    for arrow_x in [2.3, 4.5, 6.7]:
        fig.add_annotation(
            x=arrow_x + 0.55, y=0.16, ax=arrow_x, ay=0.16,
            text="", showarrow=True, arrowhead=2,
            arrowwidth=1.5, arrowcolor=ORANGE
        )

    fig.update_layout(
        height=540,
        margin=dict(l=35, r=25, t=35, b=35),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(visible=False, range=[0.0, 10.0]),
        yaxis=dict(visible=False, range=[-2.0, 2.0]),
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    fig.add_annotation(
        x=0.5, y=-0.03, xref="paper", yref="paper",
        text=(
            "Lectura del esquema: la posición de los accesorios es referencial y solo sirve para seguir el recorrido. "
            "Lo que afecta el cálculo es la cantidad de elementos, su K y las condiciones del flujo."
        ),
        showarrow=False, font=dict(size=11, color=GRAY)
    )
    return fig


def _colebrook_curve(Re_values: np.ndarray, rel_roughness: float):
    f = np.full_like(Re_values, 0.03, dtype=float)
    for _ in range(35):
        rhs = -2.0 * np.log10(rel_roughness / 3.7 + 2.51 / (Re_values * np.sqrt(f)))
        f = 1.0 / rhs**2
    return f


def make_moody_chart(Re_point: float, f_point: float | None, rel_roughness_point: float):
    fig = go.Figure()

    Re_lam = np.logspace(math.log10(500), math.log10(2300), 90)
    fig.add_trace(go.Scatter(
        x=Re_lam, y=64.0/Re_lam,
        mode="lines", name="Laminar · 64/Re",
        line=dict(color=BLACK, width=3)
    ))

    Re_turb = np.logspace(math.log10(4000), 8, 150)
    rr_values = [0.0, 1e-5, 5e-5, 1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2]
    gray_scale = ["#a8a8a8", "#999999", "#8a8a8a", "#7b7b7b", "#6c6c6c",
                  "#5d5d5d", "#4e4e4e", "#3f3f3f", "#303030"]

    for rr, color in zip(rr_values, gray_scale):
        f = _colebrook_curve(Re_turb, rr)
        label = "Lisa" if rr == 0 else f"ε/D = {rr:g}"
        fig.add_trace(go.Scatter(
            x=Re_turb, y=f, mode="lines", name=label,
            line=dict(color=color, width=1.5)
        ))

    fig.add_vrect(x0=2300, x1=4000, fillcolor="rgba(242,142,28,0.08)",
                  line_width=0, annotation_text="Transición",
                  annotation_position="top left")

    if f_point is not None and Re_point > 0:
        fig.add_trace(go.Scatter(
            x=[Re_point], y=[f_point],
            mode="markers+text",
            marker=dict(size=14, color=ORANGE, line=dict(color=BLACK, width=1.5)),
            text=["Caso actual"], textposition="top center",
            name="Caso actual",
            hovertemplate=f"Re={Re_point:.4g}<br>f={f_point:.5f}<br>ε/D={rel_roughness_point:.3g}<extra></extra>"
        ))

    fig.update_xaxes(type="log", title="Número de Reynolds · Re", gridcolor="#eeeeee")
    fig.update_yaxes(type="log", title="Factor de fricción Darcy · f",
                     range=[math.log10(0.008), math.log10(0.12)], gridcolor="#eeeeee")
    fig.update_layout(
        height=650,
        margin=dict(l=60, r=30, t=50, b=50),
        paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="v", x=1.01, y=1.0),
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_loss_breakdown(hf: float, accessory_rows: list[dict], velocity_head: float):
    names = ["Tubería recta"]
    values = [hf]

    for row in accessory_rows:
        loss = row["K_total"] * velocity_head
        if loss > 0:
            names.append(row["name"])
            values.append(loss)

    fig = go.Figure(go.Bar(
        x=names, y=values,
        text=[f"{v:.3f} m" for v in values],
        textposition="outside",
        marker=dict(color=[BLACK] + [ORANGE] * (len(values)-1))
    ))
    fig.update_layout(
        height=470,
        margin=dict(l=45, r=25, t=35, b=110),
        yaxis_title="Pérdida de carga [m]",
        xaxis_tickangle=-30,
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig


def make_relative_energy_figure(L_m: float, velocity_head: float, hf_major: float, accessory_rows: list[dict]):
    x = np.linspace(0.0, L_m, 300) if L_m > 0 else np.array([0.0, 1.0])
    major_cumulative = hf_major * (x / max(L_m, 1e-12))

    expanded = []
    for row in accessory_rows:
        for _ in range(int(row["count"])):
            expanded.append({"K": row["K"], "name": row["name"]})
    positions = np.linspace(0.15*L_m, 0.85*L_m, len(expanded)) if expanded and L_m > 0 else []

    minor_cumulative = np.zeros_like(x)
    for pos, item in zip(positions, expanded):
        minor_cumulative += np.where(x >= pos, item["K"] * velocity_head, 0.0)

    total_loss = major_cumulative + minor_cumulative
    HGL = -total_loss
    EGL = velocity_head - total_loss

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=EGL, mode="lines", line=dict(color=ORANGE, width=3), name="EGL relativa"))
    fig.add_trace(go.Scatter(x=x, y=HGL, mode="lines", line=dict(color=BLACK, width=3), name="HGL relativa"))
    fig.add_trace(go.Scatter(x=x, y=np.zeros_like(x), mode="lines", line=dict(color=GRAY, width=1.5, dash="dot"), name="Referencia HGL entrada"))

    for pos in positions:
        fig.add_vline(x=pos, line_width=1, line_dash="dot", line_color=GRAY)

    fig.update_layout(
        height=520,
        margin=dict(l=55, r=25, t=45, b=50),
        xaxis_title="Longitud de tubería [m]",
        yaxis_title="Altura relativa [m]",
        paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.18),
        hovermode="x unified",
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    return fig
