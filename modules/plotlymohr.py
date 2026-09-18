from __future__ import annotations

import numpy as np
import plotly.graph_objects as go


COLORS = {
    "circle13": "#1f77b4",
    "circle12": "#2ca02c",
    "circle23": "#d62728",
    "active": "#f28e1c",
    "x": "#1f77b4",
    "y": "#2ca02c",
    "z": "#d62728",
    "principal": "#f28e1c",
    "axis": "#222222",
    "brand": "#f28e1c",
}


def _circle_points(center, radius, n=520):
    theta = np.linspace(0.0, 2.0 * np.pi, n)
    return center + radius * np.cos(theta), radius * np.sin(theta)


def _circle_fill_trace(center, radius, fillcolor, linecolor="rgba(0,0,0,0)",
                       linewidth=0.0, showlegend=False, name=None):
    x, y = _circle_points(center, radius)
    return go.Scatter(
        x=x,
        y=y,
        mode="lines",
        fill="toself",
        fillcolor=fillcolor,
        line=dict(color=linecolor, width=linewidth),
        showlegend=showlegend,
        name=name,
        hoverinfo="skip",
    )


def crear_figura_mohr_interactiva(datos):
    """Círculos de Mohr 3D interactivos con dominio físico correcto.

    El dominio admisible se representa como:
        interior de C13 - interior de C12 - interior de C23

    Los dos círculos interiores se rellenan de blanco para mostrar
    explícitamente las zonas excluidas.
    """
    fig = go.Figure()

    c13, c12, c23 = datos["circles"]

    # Dominio exterior: interior de C13.
    fig.add_trace(
        _circle_fill_trace(
            c13["center"],
            c13["radius"],
            "rgba(31,119,180,0.10)",
        )
    )

    # Zonas excluidas: interior de C12 y C23.
    # Se dibujan sobre el sombreado exterior.
    fig.add_trace(
        _circle_fill_trace(
            c12["center"],
            c12["radius"],
            "rgba(255,255,255,1.0)",
        )
    )
    fig.add_trace(
        _circle_fill_trace(
            c23["center"],
            c23["radius"],
            "rgba(255,255,255,1.0)",
        )
    )

    # Contornos de los tres círculos.
    for circle, key, label in zip(
        datos["circles"],
        ("circle13", "circle12", "circle23"),
        ("C₁₃", "C₁₂", "C₂₃"),
    ):
        x, y = _circle_points(circle["center"], circle["radius"])
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                line=dict(color=COLORS[key], width=2.6),
                name=label,
                hovertemplate=f"{label}<extra></extra>",
            )
        )

    # Tensiones principales.
    for idx, sigma in enumerate(datos["principal_stresses"], start=1):
        fig.add_trace(
            go.Scatter(
                x=[sigma],
                y=[0.0],
                mode="markers+text",
                marker=dict(size=8, color=COLORS["principal"]),
                text=[f"σ{idx}"],
                textposition="top center",
                textfont=dict(size=11, color=COLORS["principal"]),
                showlegend=False,
                hovertemplate=f"σ{idx} = %{{x:.2f}}<extra></extra>",
            )
        )

    # Estados globales.
    for state in datos["base_states"]:
        fig.add_trace(
            go.Scatter(
                x=[state["sigma_n"], state["sigma_n"]],
                y=[state["tau_n"], -state["tau_n"]],
                mode="markers",
                marker=dict(
                    size=[8, 6],
                    symbol="circle-open",
                    color=state["color"],
                    line=dict(width=1.7, color=state["color"]),
                    opacity=[1.0, 0.35],
                ),
                showlegend=False,
                hovertemplate=(
                    f"Plano {state['label']}<br>"
                    "σₙ = %{x:.2f}<br>"
                    "τₙ = %{y:.2f}<extra></extra>"
                ),
            )
        )

    # Estados girados.
    for state in datos["rotated_states"]:
        fig.add_trace(
            go.Scatter(
                x=[state["sigma_n"], state["sigma_n"]],
                y=[state["tau_n"], -state["tau_n"]],
                mode="markers",
                marker=dict(
                    size=[8, 6],
                    symbol="square",
                    color=state["color"],
                    opacity=[1.0, 0.30],
                ),
                showlegend=False,
                hovertemplate=(
                    f"Plano {state['label']}<br>"
                    "σₙ = %{x:.2f}<br>"
                    "τₙ = %{y:.2f}<extra></extra>"
                ),
            )
        )

    # Plano activo.
    active = datos["active_state"]
    fig.add_trace(
        go.Scatter(
            x=[active["sigma_n"]],
            y=[active["tau_n"]],
            mode="markers+text",
            marker=dict(
                size=14,
                symbol="star",
                color=COLORS["active"],
                line=dict(width=1.0, color="#333333"),
            ),
            text=["n*"],
            textposition="top right",
            textfont=dict(size=12, color=COLORS["active"]),
            name="Plano activo n*",
            hovertemplate=(
                "Plano activo n*<br>"
                "σₙ = %{x:.2f}<br>"
                "τₙ = %{y:.2f}<extra></extra>"
            ),
        )
    )

    fig.add_shape(
        type="line",
        x0=active["sigma_n"],
        x1=active["sigma_n"],
        y0=-active["tau_n"],
        y1=active["tau_n"],
        line=dict(color=COLORS["active"], width=1.2, dash="dash"),
        opacity=0.45,
    )

    sigma3 = float(datos["principal_stresses"][2])
    sigma1 = float(datos["principal_stresses"][0])
    tau_max = max(float(datos["tau_max"]), 1.0)

    # Escalado automático: preserva geometría 1:1 y utiliza mejor el alto.
    # La vista se centra en C13 y se adapta al rango real del tensor.
    center_x = 0.5 * (sigma1 + sigma3)
    radius = max(float(c13["radius"]), 1.0)

    # Margen pequeño y proporcional.
    y_half = max(radius * 1.16, 25.0)

    # Relación objetivo aproximada del área gráfica web. Si el tensor crece,
    # los límites se recalculan sin deformar los círculos.
    target_plot_aspect = 1.78
    x_half = max(radius * 1.16, y_half * target_plot_aspect)

    x_range = [center_x - x_half, center_x + x_half]
    y_range = [-y_half, y_half]

    fig.update_layout(
        height=500,
        margin=dict(l=20, r=10, t=42, b=32),
        title=dict(
            text="Círculos de Mohr para el Tensor 3D",
            x=0.5,
            xanchor="center",
            y=0.965,
            yanchor="top",
            font=dict(size=17),
        ),
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=0.985,
            yanchor="top",
            font=dict(size=9),
            bgcolor="rgba(255,255,255,0.0)",
            borderwidth=0,
            itemwidth=42,
        ),
        xaxis=dict(
            title="σ",
            range=x_range,
            domain=[0.00, 1.00],
            showgrid=True,
            gridcolor="rgba(160,160,160,0.24)",
            zeroline=True,
            zerolinecolor="#222222",
            zerolinewidth=1.2,
            fixedrange=False,
        ),
        yaxis=dict(
            title="τ",
            range=y_range,
            domain=[0.00, 0.95],
            showgrid=True,
            gridcolor="rgba(160,160,160,0.24)",
            zeroline=True,
            zerolinecolor="#222222",
            zerolinewidth=1.2,
            scaleanchor="x",
            scaleratio=1,
            fixedrange=False,
        ),
        dragmode="pan",
        hovermode="closest",
        paper_bgcolor="white",
        plot_bgcolor="white",
        uirevision="mohr2d-view-v08",
    )

    # Etiquetas de círculos.
    for circle, label, color in zip(
        datos["circles"],
        ("C₁₃", "C₁₂", "C₂₃"),
        (COLORS["circle13"], COLORS["circle12"], COLORS["circle23"]),
    ):
        fig.add_annotation(
            x=circle["center"],
            y=circle["radius"],
            text=label,
            showarrow=False,
            yshift=9,
            font=dict(color=color, size=12),
        )

    # Ayuda integrada a la derecha, sin ocupar una fila completa.
    fig.add_annotation(
        x=1.0,
        y=0.945,
        xref="paper",
        yref="paper",
        text="Zoom: rueda · Pan: arrastrar · Reset: doble clic",
        showarrow=False,
        xanchor="right",
        yanchor="middle",
        font=dict(size=8.5, color="#6b6b6b"),
        bgcolor="rgba(255,255,255,0.75)",
        borderpad=2,
    )

    return fig
