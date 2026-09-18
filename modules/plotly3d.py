from __future__ import annotations

import numpy as np
import plotly.graph_objects as go


COLORS = {
    "circle13": "#1f77b4",
    "circle12": "#2ca02c",
    "circle23": "#d62728",
    "active_plane": "#8ecae6",
    "active_point": "#f28e1c",
    "traction": "#6f42c1",
    "shear": "#444444",
    "normal": "#f28e1c",
    "cube": "#8c564b",
    "global": "#9aa0a6",
    "x": "#1f77b4",
    "y": "#2ca02c",
    "z": "#d62728",
}


def _cube_geometry(base, scale=1.8):
    half = scale / 2.0
    local = np.array(
        [
            [-half, -half, -half],
            [ half, -half, -half],
            [ half,  half, -half],
            [-half,  half, -half],
            [-half, -half,  half],
            [ half, -half,  half],
            [ half,  half,  half],
            [-half,  half,  half],
        ],
        dtype=float,
    )
    vertices = local @ np.asarray(base, dtype=float).T
    edges = (
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    )
    return vertices, edges


def _plane_basis(normal):
    n = np.asarray(normal, dtype=float)
    n /= np.linalg.norm(n) or 1.0
    ref = np.array([0.0, 0.0, 1.0]) if abs(n[2]) < 0.85 else np.array([0.0, 1.0, 0.0])
    t1 = np.cross(n, ref)
    norm_t1 = np.linalg.norm(t1)
    if norm_t1 < 1e-8:
        ref = np.array([1.0, 0.0, 0.0])
        t1 = np.cross(n, ref)
        norm_t1 = np.linalg.norm(t1)
    t1 /= norm_t1 or 1.0
    t2 = np.cross(n, t1)
    t2 /= np.linalg.norm(t2) or 1.0
    return t1, t2


def _add_segment(fig, start, end, color, width=4, name=None, dash="solid",
                 showlegend=False, hover=None):
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    fig.add_trace(
        go.Scatter3d(
            x=[start[0], end[0]],
            y=[start[1], end[1]],
            z=[start[2], end[2]],
            mode="lines",
            line=dict(color=color, width=width, dash=dash),
            name=name,
            showlegend=showlegend,
            hovertemplate=hover or "<extra></extra>",
        )
    )


def _add_axis(fig, vector, label, color, scale=1.45, width=6, showlegend=False):
    v = np.asarray(vector, dtype=float)
    end = v * scale
    _add_segment(
        fig,
        [0, 0, 0],
        end,
        color,
        width=width,
        name=label,
        showlegend=showlegend,
    )
    fig.add_trace(
        go.Scatter3d(
            x=[end[0] * 1.08],
            y=[end[1] * 1.08],
            z=[end[2] * 1.08],
            mode="text",
            text=[label],
            textfont=dict(color=color, size=12),
            hoverinfo="skip",
            showlegend=False,
        )
    )


def _add_arrow(fig, start, vector, color, name, scale=1.0, width=5,
               showlegend=False):
    """Vector con línea + cono corto para indicar sentido."""
    start = np.asarray(start, dtype=float)
    vector = np.asarray(vector, dtype=float) * scale
    end = start + vector

    _add_segment(
        fig,
        start,
        end,
        color,
        width=width,
        name=name,
        showlegend=showlegend,
        hover=f"{name}<extra></extra>",
    )

    mag = np.linalg.norm(vector)
    if mag > 1e-10:
        direction = vector / mag
        cone_len = min(0.22, max(0.10, mag * 0.25))
        cone_start = end - direction * cone_len
        fig.add_trace(
            go.Cone(
                x=[cone_start[0]],
                y=[cone_start[1]],
                z=[cone_start[2]],
                u=[direction[0]],
                v=[direction[1]],
                w=[direction[2]],
                sizemode="absolute",
                sizeref=cone_len,
                anchor="tail",
                colorscale=[[0, color], [1, color]],
                showscale=False,
                hoverinfo="skip",
                showlegend=False,
            )
        )


def crear_figura_3d_interactiva(datos):
    """Construye el estado de esfuerzos 3D interactivo con Plotly.

    El usuario puede orbitar, hacer zoom y desplazar la cámara con el mouse.
    `uirevision` mantiene la perspectiva elegida al modificar los sliders.
    """
    fig = go.Figure()

    # Cubo original
    vertices, edges = _cube_geometry(np.eye(3), 1.8)
    first = True
    for i, j in edges:
        _add_segment(
            fig,
            vertices[i],
            vertices[j],
            COLORS["global"],
            width=3,
            name="Original",
            showlegend=first,
        )
        first = False

    # Cubo rotado
    vertices_r, edges_r = _cube_geometry(datos["rotation"], 1.8)
    first = True
    for i, j in edges_r:
        _add_segment(
            fig,
            vertices_r[i],
            vertices_r[j],
            COLORS["cube"],
            width=6,
            name="Rotado",
            showlegend=first,
        )
        first = False

    # Ejes globales suaves
    for idx, label in enumerate(("x", "y", "z")):
        _add_axis(
            fig,
            np.eye(3)[:, idx],
            label,
            COLORS["global"],
            scale=1.16,
            width=3,
        )

    # Ejes rotados
    for idx, (label, color) in enumerate(
        zip(("x′", "y′", "z′"), (COLORS["x"], COLORS["y"], COLORS["z"]))
    ):
        _add_axis(
            fig,
            datos["rotation"][:, idx],
            label,
            color,
            scale=1.42,
            width=7,
        )

    # Direcciones principales
    for idx, (vec, color) in enumerate(
        zip(
            datos["principal_axes"].T,
            (COLORS["circle13"], COLORS["circle12"], COLORS["circle23"]),
        ),
        start=1,
    ):
        vec = np.asarray(vec, dtype=float)
        _add_segment(
            fig,
            -vec * 1.48,
            vec * 1.48,
            color,
            width=3,
            dash="dash",
        )
        p = vec * 1.62
        fig.add_trace(
            go.Scatter3d(
                x=[p[0]], y=[p[1]], z=[p[2]],
                mode="text",
                text=[f"σ{idx}"],
                textfont=dict(color=color, size=11),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # Plano activo
    activo = datos["active_state"]
    n = np.asarray(activo["normal"], dtype=float)
    t1, t2 = _plane_basis(n)
    half = 0.70
    plane = np.array(
        [
            (-t1 - t2) * half,
            ( t1 - t2) * half,
            ( t1 + t2) * half,
            (-t1 + t2) * half,
        ]
    )

    fig.add_trace(
        go.Mesh3d(
            x=plane[:, 0],
            y=plane[:, 1],
            z=plane[:, 2],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            color=COLORS["active_plane"],
            opacity=0.24,
            name="Plano n*",
            showlegend=True,
            hovertemplate="Plano activo n*<extra></extra>",
        )
    )
    closed = np.vstack([plane, plane[0]])
    fig.add_trace(
        go.Scatter3d(
            x=closed[:, 0],
            y=closed[:, 1],
            z=closed[:, 2],
            mode="lines",
            line=dict(color=COLORS["active_point"], width=5),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # Normal del plano
    _add_arrow(
        fig,
        [0, 0, 0],
        n * 1.10,
        COLORS["active_point"],
        "Normal n*",
        width=5,
        showlegend=False,
    )

    # Tracciones del plano activo
    reference = max(float(np.max(np.abs(datos["principal_stresses"]))), 1.0)
    factor = 0.88 / reference

    normal_vec = activo["sigma_n"] * n * factor
    shear_vec = activo["shear_vec"] * factor
    total_vec = activo["traction"] * factor

    _add_arrow(
        fig,
        [0, 0, 0],
        normal_vec,
        COLORS["normal"],
        "Normal",
        width=6,
        showlegend=True,
    )
    _add_arrow(
        fig,
        normal_vec,
        shear_vec,
        COLORS["shear"],
        "Cortante",
        width=6,
        showlegend=True,
    )
    _add_arrow(
        fig,
        [0, 0, 0],
        total_vec,
        COLORS["traction"],
        "Tracción",
        width=5,
        showlegend=True,
    )

    # Algunos vectores de tracción de las caras rotadas, más discretos
    factor_faces = 0.60 / reference
    for estado in datos["rotated_states"]:
        center = estado["normal"] * 0.95
        vec = estado["traction"] * factor_faces
        _add_segment(
            fig,
            center,
            center + vec,
            estado["color"],
            width=3,
        )

    fig.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=42, b=0),
        title=dict(
            text="Giro del Estado de Esfuerzos",
            x=0.5,
            y=0.965,
            xanchor="center",
            yanchor="top",
            font=dict(size=16),
        ),
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=0.985,
            yanchor="top",
            font=dict(size=8.2),
            bgcolor="rgba(255,255,255,0.0)",
            borderwidth=0,
            itemsizing="constant",
            entrywidth=54,
            entrywidthmode="pixels",
        ),
        scene=dict(
            domain=dict(x=[0.00, 1.00], y=[0.00, 0.95]),
            xaxis=dict(
                title="X",
                range=[-1.65, 1.65],
                showbackground=True,
                backgroundcolor="rgba(245,245,245,0.45)",
                gridcolor="rgba(160,160,160,0.45)",
                zeroline=False,
            ),
            yaxis=dict(
                title="Y",
                range=[-1.65, 1.65],
                showbackground=True,
                backgroundcolor="rgba(245,245,245,0.45)",
                gridcolor="rgba(160,160,160,0.45)",
                zeroline=False,
            ),
            zaxis=dict(
                title="Z",
                range=[-1.65, 1.65],
                showbackground=True,
                backgroundcolor="rgba(245,245,245,0.45)",
                gridcolor="rgba(160,160,160,0.45)",
                zeroline=False,
            ),
            aspectmode="cube",
            dragmode="orbit",
            camera=dict(
                eye=dict(x=0.98, y=-1.05, z=0.78),
                up=dict(x=0, y=0, z=1),
            ),
            uirevision="mohr3d-camera-v08",
        ),
        annotations=[
            dict(
                x=1.0,
                y=0.945,
                xref="paper",
                yref="paper",
                text="Girar: arrastrar · Zoom: rueda · Reset: doble clic",
                showarrow=False,
                xanchor="right",
                yanchor="middle",
                font=dict(size=8.5, color="#6b6b6b"),
                bgcolor="rgba(255,255,255,0.75)",
                borderpad=2,
            )
        ],
        paper_bgcolor="white",
        plot_bgcolor="white",
        uirevision="mohr3d-camera-v08",
    )

    return fig
