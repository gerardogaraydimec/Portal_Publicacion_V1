from __future__ import annotations

import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ORANGE = "#f28e1c"
BLACK = "#171717"
GRAY = "#747980"
BLUE = "#2f6f9f"
LIGHT = "#eceff2"
G = 9.80665


def _linspace(a: float, b: float, n: int) -> list[float]:
    if n <= 1:
        return [a]
    step = (b-a)/(n-1)
    return [a + i*step for i in range(n)]


def _smooth_fraction(s: float) -> float:
    return 3*s*s - 2*s*s*s


def _diameter_at(x: float, x_end: float, D1: float, D2: float) -> float:
    s = 0.0 if x_end == 0 else x/x_end
    q = _smooth_fraction(s)
    return D1 + (D2-D1)*q


def _centerline_at(x: float, x_end: float, z1: float, z2: float) -> float:
    s = 0.0 if x_end == 0 else x/x_end
    return z1 + (z2-z1)*s


def make_system_figure(result, geometry: str):
    x = _linspace(0.0, 10.0, 180)
    z = [_centerline_at(xi, 10.0, result.z1_m, result.z2_m) for xi in x]
    D = [_diameter_at(xi, 10.0, result.D1_m, result.D2_m) for xi in x]

    z_span = max(abs(result.z2_m-result.z1_m), 1.0)
    max_D = max(result.D1_m, result.D2_m)
    visual_scale = max(0.32*z_span/max(max_D, 1e-6), 3.0)
    half = [0.5*di*visual_scale for di in D]
    upper = [zi+hi for zi, hi in zip(z, half)]
    lower = [zi-hi for zi, hi in zip(z, half)]

    x1, x2 = 1.0, 9.0
    z1c = _centerline_at(x1, 10.0, result.z1_m, result.z2_m)
    z2c = _centerline_at(x2, 10.0, result.z1_m, result.z2_m)
    h1 = 0.5*_diameter_at(x1, 10.0, result.D1_m, result.D2_m)*visual_scale
    h2 = 0.5*_diameter_at(x2, 10.0, result.D1_m, result.D2_m)*visual_scale

    ymin = min(min(lower), result.z1_m, result.z2_m)
    ymax = max(max(upper), result.z1_m, result.z2_m)
    datum = ymin - max(0.9, 0.25*(ymax-ymin+1))
    pad = max(1.2, 0.18*(ymax-ymin+1))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=upper, mode="lines", line=dict(color=BLACK, width=3), hoverinfo="skip", name="pared superior"))
    fig.add_trace(go.Scatter(x=x, y=lower, mode="lines", line=dict(color=BLACK, width=3), fill="tonexty", fillcolor="rgba(242,142,28,0.12)", hoverinfo="skip", name="tubería"))
    fig.add_trace(go.Scatter(x=x, y=z, mode="lines", line=dict(color=ORANGE, width=2, dash="dash"), hoverinfo="skip", name="eje"))

    fig.add_shape(type="line", x0=-0.1, x1=10.2, y0=datum, y1=datum, line=dict(color=LIGHT, width=2, dash="dot"))
    fig.add_annotation(x=0.15, y=datum+0.12, text="<b>Datum de referencia z = 0</b>", showarrow=False, font=dict(color=GRAY, size=11), bgcolor="rgba(255,255,255,0.9)")

    zm = _centerline_at(5.0, 10.0, result.z1_m, result.z2_m)
    fig.add_annotation(x=6.25, y=zm, ax=4.2, ay=zm, text="<b>Q</b>", showarrow=True, arrowhead=3, arrowsize=1.2, arrowwidth=2.4, arrowcolor=ORANGE, font=dict(color=ORANGE, size=13))

    for xs, zs, hs, sec in [(x1, z1c, h1, "Sección 1"), (x2, z2c, h2, "Sección 2")]:
        fig.add_shape(type="line", x0=xs, x1=xs, y0=zs-1.05*hs, y1=zs+1.05*hs, line=dict(color=BLUE, width=4))
        fig.add_annotation(x=xs, y=zs+1.45*hs, text=f"<b>{sec}</b>", showarrow=False, font=dict(color=BLUE, size=12), bgcolor="rgba(255,255,255,0.95)")

    fig.add_annotation(x=x1-0.45, y=z1c+h1, ax=x1-0.45, ay=z1c-h1, text=f"D₁ = {result.D1_m*1000:.0f} mm", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.7, arrowcolor=BLACK, font=dict(color=BLACK, size=11), textangle=-90, bgcolor="rgba(255,255,255,0.95)")
    fig.add_annotation(x=x2+0.45, y=z2c+h2, ax=x2+0.45, ay=z2c-h2, text=f"D₂ = {result.D2_m*1000:.0f} mm", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.7, arrowcolor=BLACK, font=dict(color=BLACK, size=11), textangle=90, bgcolor="rgba(255,255,255,0.95)")

    fig.add_annotation(x=x1+0.38, y=z1c, ax=x1+0.38, ay=datum, text=f"z₁ = {result.z1_m:.2f} m", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor=GRAY, font=dict(color=GRAY, size=11), bgcolor="rgba(255,255,255,0.95)")
    fig.add_annotation(x=x2-0.38, y=z2c, ax=x2-0.38, ay=datum, text=f"z₂ = {result.z2_m:.2f} m", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor=GRAY, font=dict(color=GRAY, size=11), bgcolor="rgba(255,255,255,0.95)")

    fig.update_layout(
        height=500,
        margin=dict(l=40, r=40, t=30, b=65),
        paper_bgcolor="white", plot_bgcolor="white", showlegend=False,
        xaxis=dict(visible=False, range=[-0.2, 10.2]),
        yaxis=dict(title="Cota relativa [m]", range=[datum-0.35, ymax+pad], zeroline=False, gridcolor="#f2f2f2"),
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    fig.add_annotation(x=0.5, y=-0.15, xref="paper", yref="paper", text="Las cotas z₁ y z₂ se miden desde un mismo datum de referencia. El diámetro está exagerado gráficamente para facilitar la lectura.", showarrow=False, font=dict(size=11, color=GRAY))
    return fig


def make_energy_figure(result):
    x = _linspace(0.0, 10.0, 180)
    D = [_diameter_at(xi, 10.0, result.D1_m, result.D2_m) for xi in x]
    z = [_centerline_at(xi, 10.0, result.z1_m, result.z2_m) for xi in x]
    A = [math.pi*di**2/4 for di in D]
    V = [result.Q_m3s/ai for ai in A]
    vh = [vi**2/(2*G) for vi in V]
    EGL = [result.EGL1_m for _ in x]
    HGL = [egl-vhi for egl, vhi in zip(EGL, vh)]
    pressure_head = [hgl-zi for hgl, zi in zip(HGL, z)]

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.10, row_heights=[0.66, 0.34], subplot_titles=("Línea de energía y línea piezométrica", "Componentes a lo largo del sistema"))
    fig.add_trace(go.Scatter(x=x, y=EGL, mode="lines", line=dict(color=ORANGE, width=3), name="EGL · línea de energía"), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=HGL, mode="lines", line=dict(color=BLACK, width=3), name="HGL · línea piezométrica"), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=z, mode="lines", line=dict(color=GRAY, width=2, dash="dot"), name="z · eje de tubería"), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=pressure_head, mode="lines", line=dict(color=BLACK, width=2), name="p/(ρg)"), row=2, col=1)
    fig.add_trace(go.Scatter(x=x, y=vh, mode="lines", line=dict(color=ORANGE, width=2), name="V²/(2g)"), row=2, col=1)
    fig.update_yaxes(title_text="Altura de energía [m]", row=1, col=1, gridcolor="#f1f1f1")
    fig.update_yaxes(title_text="Altura [m]", row=2, col=1, gridcolor="#f1f1f1")
    fig.update_xaxes(title_text="Posición relativa", row=2, col=1)
    fig.update_layout(height=720, margin=dict(l=55, r=30, t=75, b=45), paper_bgcolor="white", plot_bgcolor="white", hovermode="x unified", legend=dict(orientation="h", y=-0.12), font=dict(family="Arial, sans-serif", color="#262730"))
    return fig


def make_head_bars(result):
    labels = ["Sección 1", "Sección 2"]
    pressure = [result.pressure_head_1_m, result.pressure_head_2_m]
    velocity = [result.velocity_head_1_m, result.velocity_head_2_m]
    elevation = [result.z1_m, result.z2_m]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="z", x=labels, y=elevation, marker_color="#a7a7a7"))
    fig.add_trace(go.Bar(name="p/(ρg)", x=labels, y=pressure, marker_color=BLACK))
    fig.add_trace(go.Bar(name="V²/(2g)", x=labels, y=velocity, marker_color=ORANGE))
    fig.update_layout(barmode="relative", height=430, margin=dict(l=45, r=25, t=35, b=35), yaxis_title="Altura de energía [m]", paper_bgcolor="white", plot_bgcolor="white", legend=dict(orientation="h", y=-0.15), font=dict(family="Arial, sans-serif", color="#262730"))
    return fig
