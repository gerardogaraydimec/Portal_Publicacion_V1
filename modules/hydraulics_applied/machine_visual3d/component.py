from __future__ import annotations

from itertools import count

import math
from typing import Iterable, Sequence

import numpy as np
import plotly.graph_objects as go
import streamlit as st

_PLOTLY_SEQ = count(1)

ORANGE = "#f28e1c"
DARK = "#202126"
DARK2 = "#2b2d33"
YELLOW = "#d79b28"
METAL = "#9097a1"
ROD = "#dfe2e6"
GLASS = "#6f8ca0"
PRESSURE = "#d84030"
RETURN = "#2a63b8"
SUCTION = "#4e9b57"
PILOT = "#d6b72c"
INACTIVE = "#6d727b"
OUTLINE = "#17181c"
LABEL = "#f4eee4"


LIGHTING_DEFAULT = dict(ambient=0.55, diffuse=0.92, specular=0.18, roughness=0.78, fresnel=0.05)
LIGHTING_GLASS = dict(ambient=0.40, diffuse=0.70, specular=0.32, roughness=0.40, fresnel=0.18)
LIGHTPOS = dict(x=80, y=60, z=120)


def _rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"rgb({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)})"


def _edge_trace(fig: go.Figure, pts: Sequence[tuple[float, float, float]], width: int = 5, color: str = OUTLINE):
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    ]
    xs, ys, zs = [], [], []
    for a, b in edges:
        pa, pb = pts[a], pts[b]
        xs.extend([pa[0], pb[0], None])
        ys.extend([pa[1], pb[1], None])
        zs.extend([pa[2], pb[2], None])
    fig.add_trace(
        go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode="lines",
            showlegend=False,
            hoverinfo="skip",
            line=dict(color=color, width=width),
        )
    )


def _cuboid_pts(center, size):
    cx, cy, cz = center
    lx, ly, lz = size
    return [
        (cx - lx / 2, cy - ly / 2, cz - lz / 2),
        (cx + lx / 2, cy - ly / 2, cz - lz / 2),
        (cx + lx / 2, cy + ly / 2, cz - lz / 2),
        (cx - lx / 2, cy + ly / 2, cz - lz / 2),
        (cx - lx / 2, cy - ly / 2, cz + lz / 2),
        (cx + lx / 2, cy - ly / 2, cz + lz / 2),
        (cx + lx / 2, cy + ly / 2, cz + lz / 2),
        (cx - lx / 2, cy + ly / 2, cz + lz / 2),
    ]


def _mesh_from_pts(fig, pts, color, name="", opacity=1.0, showlegend=False, flatshading=True, lighting=None):
    x = [p[0] for p in pts]
    y = [p[1] for p in pts]
    z = [p[2] for p in pts]
    i = [0, 0, 0, 1, 1, 2, 4, 4, 5, 3, 2, 6]
    j = [1, 2, 4, 2, 5, 3, 5, 6, 6, 7, 3, 7]
    k = [2, 4, 1, 5, 2, 7, 6, 5, 1, 4, 7, 6]
    fig.add_trace(
        go.Mesh3d(
            x=x,
            y=y,
            z=z,
            i=i,
            j=j,
            k=k,
            color=color,
            opacity=opacity,
            name=name,
            showlegend=showlegend,
            hovertemplate=(name + "<extra></extra>") if name else None,
            flatshading=flatshading,
            lighting=lighting or LIGHTING_DEFAULT,
            lightposition=LIGHTPOS,
        )
    )
    _edge_trace(fig, pts, width=4)


def _cuboid(fig: go.Figure, center, size, color, name="", opacity=1.0, showlegend=False, lighting=None):
    pts = _cuboid_pts(center, size)
    _mesh_from_pts(fig, pts, color, name=name, opacity=opacity, showlegend=showlegend, lighting=lighting)


def _rotate_z(points: Iterable[tuple[float, float, float]], angle: float, origin=(0.0, 0.0, 0.0)):
    ox, oy, oz = origin
    c, s = math.cos(angle), math.sin(angle)
    out = []
    for x, y, z in points:
        dx, dy = x - ox, y - oy
        out.append((ox + c * dx - s * dy, oy + s * dx + c * dy, z))
    return out


def _rotate_y(points: Iterable[tuple[float, float, float]], angle: float, origin=(0.0, 0.0, 0.0)):
    ox, oy, oz = origin
    c, s = math.cos(angle), math.sin(angle)
    out = []
    for x, y, z in points:
        dx, dz = x - ox, z - oz
        out.append((ox + c * dx + s * dz, y, oz - s * dx + c * dz))
    return out


def _cuboid_rot_z(fig, center, size, angle, color, name="", opacity=1.0, origin=None, lighting=None):
    pts = _cuboid_pts(center, size)
    pts = _rotate_z(pts, angle, origin or center)
    _mesh_from_pts(fig, pts, color, name=name, opacity=opacity, lighting=lighting)


def _cuboid_rot_y(fig, center, size, angle, color, name="", origin=None, opacity=1.0, lighting=None):
    pts = _cuboid_pts(center, size)
    pts = _rotate_y(pts, angle, origin or center)
    _mesh_from_pts(fig, pts, color, name=name, opacity=opacity, lighting=lighting)


def _beam_y(fig, center, length, width, height, angle, color, name="", origin=None):
    _cuboid_rot_y(fig, center, (length, width, height), angle, color, name=name, origin=origin)


def _line(fig, pts, color, name, width=6, dash=None, showlegend=False):
    x = [p[0] for p in pts]
    y = [p[1] for p in pts]
    z = [p[2] for p in pts]
    fig.add_trace(
        go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="lines",
            name=name,
            showlegend=showlegend,
            line=dict(color=color, width=width, dash=dash or "solid"),
            hovertemplate=name + "<extra></extra>",
        )
    )


def _polyline_tube(fig, pts, radius, color, name="", showlegend=False, opacity=1.0):
    for a, b in zip(pts[:-1], pts[1:]):
        _cylinder(fig, a, b, radius, color, name=name, opacity=opacity, showlegend=showlegend)
        showlegend = False


def _label(fig, x, y, z, text, color=LABEL, size=11):
    fig.add_trace(
        go.Scatter3d(
            x=[x],
            y=[y],
            z=[z],
            mode="text",
            text=[text],
            showlegend=False,
            textfont=dict(color=color, size=size),
            hoverinfo="skip",
        )
    )


def _cylinder(fig: go.Figure, p0, p1, radius, color, name="", opacity=1.0, n=24, showlegend=False):
    p0 = np.asarray(p0, float)
    p1 = np.asarray(p1, float)
    axis = p1 - p0
    L = np.linalg.norm(axis)
    if L < 1e-9:
        return
    w = axis / L
    a = np.array([1.0, 0.0, 0.0]) if abs(w[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(w, a)
    u = u / np.linalg.norm(u)
    v = np.cross(w, u)
    th = np.linspace(0, 2 * np.pi, n)
    ring0 = np.array([p0 + radius * (math.cos(t) * u + math.sin(t) * v) for t in th])
    ring1 = np.array([p1 + radius * (math.cos(t) * u + math.sin(t) * v) for t in th])
    x = np.r_[ring0[:, 0], ring1[:, 0]]
    y = np.r_[ring0[:, 1], ring1[:, 1]]
    z = np.r_[ring0[:, 2], ring1[:, 2]]
    ii, jj, kk = [], [], []
    m = len(th)
    for q in range(m - 1):
        ii += [q, q]
        jj += [q + 1, m + q + 1]
        kk += [m + q, m + q]
    fig.add_trace(
        go.Mesh3d(
            x=x,
            y=y,
            z=z,
            i=ii,
            j=jj,
            k=kk,
            color=color,
            opacity=opacity,
            name=name,
            showlegend=showlegend,
            flatshading=True,
            hovertemplate=(name + "<extra></extra>") if name else None,
            lighting=LIGHTING_DEFAULT,
            lightposition=LIGHTPOS,
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=[p0[0], p1[0]],
            y=[p0[1], p1[1]],
            z=[p0[2], p1[2]],
            mode="lines",
            showlegend=False,
            hoverinfo="skip",
            line=dict(color=OUTLINE, width=3),
        )
    )


def _wheel(fig, x, y, z, r=0.62, width=0.42, steer=0.0, name="Rueda"):
    axis = np.array([math.sin(steer), math.cos(steer), 0.0])
    p0 = np.array([x, y, z]) - axis * width / 2
    p1 = np.array([x, y, z]) + axis * width / 2
    _cylinder(fig, p0, p1, r, DARK, name, 1.0, n=28)
    _cylinder(fig, p0 - axis * 0.015, p1 + axis * 0.015, r * 0.42, METAL, "Maza", 1.0, n=22)


def _ground_shadow(fig, center=(0.0, 0.0), size=(6.0, 3.5), opacity=0.12):
    cx, cy = center
    sx, sy = size
    pts = [
        (cx - sx / 2, cy - sy / 2, -0.72),
        (cx + sx / 2, cy - sy / 2, -0.72),
        (cx + sx / 2, cy + sy / 2, -0.72),
        (cx - sx / 2, cy + sy / 2, -0.72),
    ]
    fig.add_trace(
        go.Mesh3d(
            x=[p[0] for p in pts],
            y=[p[1] for p in pts],
            z=[p[2] for p in pts],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            color="#000000",
            opacity=opacity,
            flatshading=True,
            showlegend=False,
            hoverinfo="skip",
            lighting=dict(ambient=1, diffuse=0, specular=0, roughness=1, fresnel=0),
        )
    )


def _hydraulic_lines(fig, machine: str, subsystem: str, state: str):
    """Rutas físicas simplificadas. No representan routing OEM; muestran asociación espacial."""
    if machine == "Cargador frontal":
        base = [(-1.1, -0.55, 0.55), (-0.15, -0.55, 0.55), (0.55, -0.55, 0.72)]
        _line(fig, base, SUCTION, "Succión", 5, showlegend=True)
        if subsystem == "Levante de brazos LS":
            if state == "Raise":
                _line(fig, [(0.55, -0.48, 0.72), (1.25, -0.70, 0.92), (2.05, -0.72, 1.18)], PRESSURE, "Presión", 7, showlegend=True)
                _line(fig, [(2.05, 0.72, 1.18), (1.25, 0.70, 0.72), (0.55, 0.50, 0.62)], RETURN, "Retorno", 6, showlegend=True)
            elif state == "Lower":
                _line(fig, [(0.55, 0.48, 0.72), (1.25, 0.70, 0.82), (2.05, 0.72, 1.18)], PRESSURE, "Presión", 7, showlegend=True)
                _line(fig, [(2.05, -0.72, 1.18), (1.25, -0.70, 0.74), (0.55, -0.50, 0.62)], RETURN, "Retorno", 6, showlegend=True)
            elif state == "Float":
                _line(fig, [(2.05, -0.72, 1.18), (1.25, -0.70, 0.74), (0.55, -0.5, 0.62), (0.0, -0.5, 0.4)], RETURN, "A/B a tanque", 6, showlegend=True)
                _line(fig, [(2.05, 0.72, 1.18), (1.25, 0.70, 0.74), (0.55, 0.5, 0.62), (0.0, 0.5, 0.4)], RETURN, "A/B a tanque", 6)
            _line(fig, [(1.5, 0.0, 1.05), (0.9, 0.0, 1.55), (0.0, 0.0, 1.55), (-0.8, 0.0, 1.2)], PILOT, "LS", 4, dash="dash", showlegend=True)
        elif subsystem == "Inclinación de balde":
            col = PRESSURE if state != "Hold" else INACTIVE
            _line(fig, [(0.55, -0.2, 0.72), (1.8, -0.15, 1.35), (2.9, -0.1, 1.55)], col, "Línea tilt", 6, showlegend=True)
            _line(fig, [(2.9, 0.1, 1.55), (1.8, 0.15, 1.2), (0.55, 0.2, 0.62)], RETURN, "Retorno", 5, showlegend=True)
        else:
            _line(fig, [(-0.1, -0.5, 0.7), (-0.7, -0.75, 0.55), (-1.55, -0.8, 0.45)], PRESSURE, "Dirección", 6, showlegend=True)
            _line(fig, [(-1.55, 0.8, 0.45), (-0.7, 0.75, 0.45), (-0.1, 0.5, 0.6)], RETURN, "Retorno", 5, showlegend=True)
            _line(fig, [(-0.4, 0, 0.95), (-1.1, 0, 1.2)], PILOT, "LS", 4, dash="dash", showlegend=True)
    elif machine == "Camión minero":
        _line(fig, [(-1.1, -0.6, 0.52), (-0.3, -0.6, 0.55), (0.4, -0.6, 0.7)], SUCTION, "Succión", 5, showlegend=True)
        if subsystem == "Levante de tolva":
            col = PRESSURE if state in ("Raise", "Lower") else INACTIVE
            _line(fig, [(0.4, -0.65, 0.7), (1.4, -0.75, 0.9), (2.2, -0.78, 1.2)], col, "Trabajo A", 7, showlegend=True)
            _line(fig, [(2.2, 0.78, 1.2), (1.4, 0.75, 0.75), (0.4, 0.65, 0.62)], RETURN if state != "Hold" else INACTIVE, "Trabajo B", 6, showlegend=True)
            _line(fig, [(1.3, 0, 1.0), (0.7, 0, 1.5), (-0.2, 0, 1.55), (-1.0, 0, 1.2)], PILOT, "Pilotaje / LS", 4, dash="dash", showlegend=True)
        elif subsystem == "Dirección hidrostática":
            _line(fig, [(-0.5, -0.3, 0.65), (-1.3, -0.6, 0.52), (-2.2, -0.7, 0.42)], PRESSURE, "L/R", 6, showlegend=True)
            _line(fig, [(-2.2, 0.7, 0.42), (-1.3, 0.6, 0.48), (-0.5, 0.3, 0.58)], RETURN, "Retorno", 5, showlegend=True)
            _line(fig, [(-0.5, 0, 0.9), (-1.35, 0, 1.2)], PILOT, "LS", 4, dash="dash", showlegend=True)
        else:
            _line(fig, [(0.2, -0.55, 0.75), (0.9, -0.65, 0.95), (1.65, -0.75, 0.55)], PRESSURE, "Circuito de freno", 6, showlegend=True)
    else:
        _line(fig, [(-2.5, -0.45, 0.2), (-1.7, -0.45, 0.3), (-0.7, -0.45, 0.45), (0.2, -0.45, 0.65)], SUCTION, "Succión", 5, showlegend=True)
        _line(fig, [(0.2, -0.45, 0.65), (1.2, -0.45, 0.75), (2.1, -0.45, 1.0)], PRESSURE, "Presión", 7, showlegend=True)
        _line(fig, [(2.1, 0.45, 1.0), (1.2, 0.45, 0.55), (0.2, 0.45, 0.45), (-2.5, 0.45, 0.2)], RETURN, "Retorno", 6, showlegend=True)


def _truck(fig, data):
    state = data.get("state", "")
    subsystem = data.get("subsystem", "")
    amp = float(data.get("visual_amp", 1.0))

    _ground_shadow(fig, center=(0.2, 0), size=(8.2, 4.5), opacity=0.10)

    # Chasis más claro y proporcional
    _cuboid(fig, (0.10, 0, -0.02), (7.45, 2.65, 0.28), YELLOW, "Chasis")
    _cuboid(fig, (-0.10, 0, 0.18), (4.80, 2.00, 0.18), "#bf8723", "Plataforma")
    _cuboid(fig, (2.85, 0, 0.02), (1.95, 2.20, 0.18), "#bf8723", "Puente trasero")
    _cuboid(fig, (3.35, 0, 0.10), (0.65, 2.55, 0.20), "#b67f1e", "Tope trasero")

    # Cabina más reconocible
    _cuboid(fig, (-2.75, 0, 0.98), (1.45, 1.95, 1.58), DARK2, "Cabina")
    _cuboid(fig, (-1.92, 0, 0.56), (1.35, 1.78, 0.60), "#393c44", "Capó")
    _cuboid(fig, (-2.82, 0, 1.22), (0.90, 1.46, 0.64), GLASS, "Parabrisas", opacity=0.78, lighting=LIGHTING_GLASS)
    _cuboid(fig, (-2.86, -0.74, 1.00), (0.10, 0.42, 0.54), GLASS, "Ventana", opacity=0.72, lighting=LIGHTING_GLASS)
    _cuboid(fig, (-2.86, 0.74, 1.00), (0.10, 0.42, 0.54), GLASS, "Ventana", opacity=0.72, lighting=LIGHTING_GLASS)

    steer = 0.0
    if subsystem == "Dirección hidrostática":
        steer = {"Izquierda": -0.24, "Derecha": 0.24}.get(state, 0.0) * amp

    # 6 ruedas de mejor tamaño
    for x in (-2.15, 0.35, 2.35):
        for y in (-1.24, 1.24):
            _wheel(fig, x, y, -0.50, 0.82 if x > -1.0 else 0.74, 0.42, steer if x < -1.0 else 0.0)

    # Tolva mejor proporcionada
    angle = {"Raise": 0.58, "Hold": 0.34, "Float": 0.16, "Lower": 0.08}.get(state, 0.08) if subsystem == "Levante de tolva" else 0.08
    angle *= min(1.15, amp)
    pivot = (2.08, 0, 0.32)

    # Tolva: piso + laterales + frente, más compacta y cercana al camión real
    _cuboid_rot_y(fig, (0.95, 0, 1.04), (4.10, 2.18, 0.20), angle, YELLOW, "Piso tolva", origin=pivot)
    _cuboid_rot_y(fig, (0.86, -1.03, 1.40), (3.95, 0.14, 0.92), angle, YELLOW, "Lateral tolva", origin=pivot)
    _cuboid_rot_y(fig, (0.86, 1.03, 1.40), (3.95, 0.14, 0.92), angle, YELLOW, "Lateral tolva", origin=pivot)
    _cuboid_rot_y(fig, (-0.84, 0, 1.32), (0.16, 2.12, 0.92), angle, YELLOW, "Frente tolva", origin=pivot)
    _cuboid_rot_y(fig, (2.55, 0, 1.22), (0.62, 2.02, 0.15), angle, "#e0b64d", "Alero trasero", origin=pivot)

    # Cilindros de levante mejor visibles
    if subsystem == "Levante de tolva":
        cyl_top = 0.98 + 0.42 * max(0.0, math.sin(angle))
        rod_top = 1.18 + 0.44 * max(0.0, math.sin(angle))
        _cylinder(fig, (0.08, -0.64, 0.18), (1.30, -0.64, cyl_top), 0.13, METAL, "Cilindro levante")
        _cylinder(fig, (0.08, 0.64, 0.18), (1.30, 0.64, cyl_top), 0.13, METAL, "Cilindro levante")
        _cylinder(fig, (1.02, -0.64, 0.84), (1.70, -0.64, rod_top), 0.055, ROD, "Vástago")
        _cylinder(fig, (1.02, 0.64, 0.84), (1.70, 0.64, rod_top), 0.055, ROD, "Vástago")
        _label(fig, 0.95, 0, 2.66, "TOLVA / CARGA")
        _label(fig, 0.95, 0, 1.82, "CILINDROS DE LEVANTE", size=10)
    elif subsystem == "Freno con acumuladores":
        for x in (-0.10, 0.62, 1.34):
            _cylinder(fig, (x, -0.92, 0.68), (x + 0.50, -0.92, 0.68), 0.15, DARK2, "Acumulador")
        _label(fig, 0.82, -0.92, 1.18, "ACUMULADORES")
    else:
        _label(fig, -1.55, 0, 2.05, "DIRECCIÓN HIDROSTÁTICA")

    _cuboid(fig, (-0.45, 0, 0.53), (0.56, 0.74, 0.54), DARK2, "Unidad hidráulica")
    _cuboid(fig, (0.38, 0, 0.63), (0.88, 0.90, 0.56), "#34373e", "Banco de válvulas")
    _label(fig, -0.02, 0, 1.26, "UNIDAD HIDRÁULICA")


def _loader(fig, data):
    state = data.get("state", "")
    subsystem = data.get("subsystem", "")
    amp = float(data.get("visual_amp", 1.0))
    steer = {"Izquierda": -0.22, "Derecha": 0.22}.get(state, 0.0) * amp if subsystem == "Dirección articulada" else 0.0

    _ground_shadow(fig, center=(0.15, 0), size=(6.8, 4.0), opacity=0.10)

    # Bastidor trasero y cabina, más masivos y legibles
    _cuboid(fig, (-1.38, 0, 0.02), (3.05, 2.18, 0.34), YELLOW, "Bastidor trasero")
    _cuboid(fig, (-1.52, 0, 0.30), (2.22, 1.72, 0.28), "#bf8723", "Motor")
    _cuboid(fig, (-1.92, 0, 1.02), (1.22, 1.58, 1.50), DARK2, "Cabina")
    _cuboid(fig, (-1.98, 0, 1.22), (0.86, 1.30, 0.60), GLASS, "Cabina", opacity=0.78, lighting=LIGHTING_GLASS)
    _cuboid(fig, (-0.68, 0, 0.40), (0.72, 1.24, 0.42), "#b67f1e", "Contrapeso")

    # Bastidor delantero articulado más claro
    _cuboid_rot_z(fig, (0.98, 0, 0.02), (2.72, 2.00, 0.30), steer, YELLOW, "Bastidor delantero", origin=(0, 0, 0))
    _cuboid_rot_z(fig, (1.58, 0, 0.24), (1.48, 1.48, 0.18), steer, "#bf8723", "Soporte delantero", origin=(0, 0, 0))
    _cylinder(fig, (-0.04, 0, -0.14), (0.22, 0, -0.14), 0.16, METAL, "Pivote")

    # Ruedas
    for y in (-1.08, 1.08):
        _wheel(fig, -2.08, y, -0.46, 0.72, 0.44, 0.0)
        wx, wy, wz = _rotate_z([(1.66, y, -0.46)], steer, (0, 0, 0))[0]
        _wheel(fig, wx, wy, wz, 0.80, 0.44, steer)

    # Brazos de levante, más cortos y robustos para evitar aspecto confuso
    lift_angle = {"Raise": 0.48, "Hold": 0.24, "Float": 0.08, "Lower": -0.06}.get(state, 0.20) if subsystem == "Levante de brazos LS" else 0.22
    lift_angle *= min(1.15, amp)
    arm_origin = np.array([0.92, 0, 0.46])
    arm_len = 2.45
    end = np.array([arm_origin[0] + arm_len * math.cos(lift_angle), 0, arm_origin[2] + arm_len * math.sin(lift_angle)])

    for y in (-0.64, 0.64):
        base_side = _rotate_z([(arm_origin[0], y, arm_origin[2])], steer, (0, 0, 0))[0]
        arm_center_local = ((arm_origin[0] + end[0]) / 2, y, (arm_origin[2] + end[2]) / 2)
        arm_center = _rotate_z([arm_center_local], steer, (0, 0, 0))[0]
        _beam_y(fig, arm_center, arm_len, 0.12, 0.16, lift_angle, YELLOW, "Brazo", origin=base_side)

    # Traviesa superior
    p_left = _rotate_z([(end[0] - 0.18, -0.64, end[2] + 0.04)], steer, (0, 0, 0))[0]
    p_right = _rotate_z([(end[0] - 0.18, 0.64, end[2] + 0.04)], steer, (0, 0, 0))[0]
    _cylinder(fig, p_left, p_right, 0.07, YELLOW, "Traviesa")

    # Balde más compacto y reconocible
    bucket_angle = {"Rollback": 0.34, "Hold": 0.02, "Dump": -0.52}.get(state, -0.06) if subsystem == "Inclinación de balde" else -0.04
    bucket_angle *= min(1.20, amp)
    bucket_pivot_local = (end[0] + 0.06, 0, end[2] - 0.02)
    pivot_rot = _rotate_z([bucket_pivot_local], steer, (0, 0, 0))[0]
    bucket_center = _rotate_z([(end[0] + 0.50, 0, end[2] - 0.02)], steer, (0, 0, 0))[0]
    _cuboid_rot_y(fig, bucket_center, (0.96, 1.78, 0.18), bucket_angle, YELLOW, "Piso balde", origin=pivot_rot)
    _cuboid_rot_y(fig, (end[0] + 0.18, -0.86, end[2] + 0.20), (0.62, 0.12, 0.62), bucket_angle, YELLOW, "Lateral balde", origin=bucket_pivot_local)
    _cuboid_rot_y(fig, (end[0] + 0.18, 0.86, end[2] + 0.20), (0.62, 0.12, 0.62), bucket_angle, YELLOW, "Lateral balde", origin=bucket_pivot_local)
    _cuboid_rot_y(fig, (end[0] + 0.82, 0, end[2] + 0.10), (0.18, 1.72, 0.44), bucket_angle, "#e0b64d", "Frente balde", origin=bucket_pivot_local)
    edge_x = end[0] + 0.88 * math.cos(bucket_angle)
    edge_z = end[2] - 0.18 * math.sin(bucket_angle) - 0.14
    e0, e1 = _rotate_z([(edge_x, -0.86, edge_z), (edge_x, 0.86, edge_z)], steer, (0, 0, 0))
    _cylinder(fig, e0, e1, 0.035, METAL, "Filo")

    # Cinemática secundaria sencilla para entender la máquina
    link_a = _rotate_z([(end[0] - 0.34, -0.30, end[2] + 0.06), (end[0] + 0.10, -0.30, end[2] + 0.22)], steer, (0, 0, 0))
    link_b = _rotate_z([(end[0] - 0.34, 0.30, end[2] + 0.06), (end[0] + 0.10, 0.30, end[2] + 0.22)], steer, (0, 0, 0))
    _cylinder(fig, link_a[0], link_a[1], 0.045, METAL, "Biela balde")
    _cylinder(fig, link_b[0], link_b[1], 0.045, METAL, "Biela balde")

    # Cilindros
    if subsystem == "Levante de brazos LS":
        for y in (-0.54, 0.54):
            _cylinder(fig, (0.02, y, 0.22), (1.38, y, 0.58 + 0.18 * math.sin(lift_angle)), 0.12, METAL, "Cilindro lift")
            _cylinder(fig, (1.02, y, 0.48), (1.70, y, 0.68 + 0.26 * math.sin(lift_angle)), 0.055, ROD, "Vástago")
        _label(fig, 1.62, 0, 2.08, "BRAZOS / LEVANTE LS")
    elif subsystem == "Inclinación de balde":
        p0 = _rotate_z([(1.24, 0, 0.98)], steer, (0, 0, 0))[0]
        p1 = _rotate_z([(end[0] - 0.12, 0, end[2] + 0.28)], steer, (0, 0, 0))[0]
        p2 = _rotate_z([(end[0] + 0.08, 0, end[2] + 0.20 + bucket_angle * 0.10)], steer, (0, 0, 0))[0]
        _cylinder(fig, p0, p1, 0.11, METAL, "Cilindro tilt")
        _cylinder(fig, p1, p2, 0.05, ROD, "Vástago")
        _label(fig, 1.88, 0, 2.02, "TILT / BALDE")
    else:
        _cylinder(fig, (-0.18, -0.66, 0.14), (0.64, -0.70, 0.14), 0.10, METAL, "Cilindro dirección")
        _cylinder(fig, (-0.18, 0.66, 0.14), (0.64, 0.70, 0.14), 0.10, METAL, "Cilindro dirección")
        _label(fig, 0.08, 0, 1.92, "ARTICULACIÓN")

    _cuboid(fig, (-0.44, 0, 0.42), (0.54, 0.76, 0.46), DARK2, "Bomba LS")
    _cuboid(fig, (0.34, 0, 0.62), (0.76, 0.88, 0.54), "#34373e", "Banco de válvulas")
    _label(fig, -0.02, 0, 1.22, "UNIDAD HIDRÁULICA")


def _scene_params(machine: str):
    if machine == "Camión minero":
        return dict(
            aspectratio=dict(x=1.85, y=1.05, z=1.00),
            ranges=dict(x=[-4.2, 4.2], y=[-2.2, 2.2], z=[-0.8, 3.6]),
            iso_eye=dict(x=2.25, y=2.10, z=1.55),
            front_eye=dict(x=0.0, y=2.9, z=1.08),
            side_eye=dict(x=3.55, y=0.0, z=1.05),
            top_eye=dict(x=0.01, y=0.01, z=4.1),
        )
    if machine == "Cargador frontal":
        return dict(
            aspectratio=dict(x=1.75, y=1.05, z=0.95),
            ranges=dict(x=[-3.3, 4.8], y=[-2.1, 2.1], z=[-0.8, 2.8]),
            iso_eye=dict(x=2.15, y=2.05, z=1.45),
            front_eye=dict(x=0.0, y=2.8, z=0.98),
            side_eye=dict(x=3.15, y=0.0, z=0.98),
            top_eye=dict(x=0.01, y=0.01, z=3.7),
        )
    return dict(
        aspectratio=dict(x=1.9, y=1.15, z=0.9),
        ranges=dict(x=[-3.4, 3.4], y=[-2.0, 2.0], z=[-0.8, 2.8]),
        iso_eye=dict(x=2.55, y=2.35, z=1.72),
        front_eye=dict(x=0.0, y=2.85, z=0.95),
        side_eye=dict(x=3.25, y=0.0, z=0.95),
        top_eye=dict(x=0.01, y=0.01, z=3.9),
    )

def _stationary(fig, data):
    state = data.get("state", "")
    subsystem = data.get("subsystem", "")
    amp = float(data.get("visual_amp", 1.0))
    _ground_shadow(fig, center=(0.15, 0), size=(6.0, 3.2), opacity=0.10)
    _cuboid(fig, (-2.6, 0, -0.35), (1.35, 1.5, 0.95), DARK2, "Depósito")
    _cylinder(fig, (-1.65, 0, 0.0), (-0.85, 0, 0.0), 0.38, DARK2, "Motor eléctrico")
    _cylinder(fig, (-0.75, 0, 0.0), (-0.25, 0, 0.0), 0.28, METAL, "Bomba")
    _cuboid(fig, (0.55, 0, 0.25), (1.0, 0.8, 0.7), DARK2, "Banco hidráulico")
    _cuboid(fig, (2.65, -0.75, 0.65), (0.25, 0.25, 3.2), DARK2, "Bastidor")
    _cuboid(fig, (2.65, 0.75, 0.65), (0.25, 0.25, 3.2), DARK2, "Bastidor")
    _cuboid(fig, (2.65, 0, 2.15), (0.3, 1.7, 0.25), DARK2, "Travesaño")
    pos = {
        "Avance": 0.8,
        "Avance rápido": 0.85,
        "Trabajo": 0.65,
        "Elevar": 0.65,
        "Cilindro A": 0.55,
        "Cilindro B": 0.85,
        "Retroceso": 0.1,
        "Retorno": 0.1,
        "Bajar controlado": 0.25,
    }.get(state, 0.35)
    _cylinder(fig, (2.65, 0, 1.95), (2.65, 0, 0.55), 0.18, METAL, "Cilindro")
    _cylinder(fig, (2.65, 0, 0.75), (2.65, 0, 0.15 + pos * 0.75 * amp), 0.075, ROD, "Vástago")
    _label(fig, -1.2, 0, 1.25, "UNIDAD HIDRÁULICA")
    _label(fig, 2.65, 0, 2.5, subsystem.upper(), size=10)


def render_machine_hydraulics_3d(data: dict, height: int = 640):
    """Visor 3D robusto basado en Plotly.

    No depende de Three.js/CDN externos. Se actualiza con cada rerun de Streamlit,
    por lo que los cambios de estado y amplificación se reflejan de inmediato.
    """
    fig = go.Figure()
    machine = data.get("machine", "Sistema estacionario")
    if machine == "Camión minero":
        _truck(fig, data)
    elif machine == "Cargador frontal":
        _loader(fig, data)
    else:
        _stationary(fig, data)
    if data.get("show_paths", True):
        _hydraulic_lines(fig, machine, data.get("subsystem", ""), data.get("state", ""))

    view = data.get("view", "Isométrica")
    scn = _scene_params(machine)
    cams = {
        "Frente": dict(eye=scn["front_eye"], up=dict(x=0, y=0, z=1), projection=dict(type="orthographic")),
        "Lateral": dict(eye=scn["side_eye"], up=dict(x=0, y=0, z=1), projection=dict(type="orthographic")),
        "Superior": dict(eye=scn["top_eye"], up=dict(x=0, y=1, z=0), projection=dict(type="orthographic")),
        "Isométrica": dict(eye=scn["iso_eye"], up=dict(x=0, y=0, z=1), projection=dict(type="orthographic")),
    }
    camera = cams.get(view, cams["Isométrica"])
    title = f"{machine} · {data.get('subsystem', '')} · {data.get('state', '')}"
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=44, b=0),
        paper_bgcolor=DARK,
        plot_bgcolor=DARK,
        title=dict(text=title, x=0.02, y=0.98, font=dict(color="#f5ead7", size=15)),
        legend=dict(
            orientation="h",
            x=0.02,
            y=0.02,
            bgcolor="rgba(20,20,22,.78)",
            font=dict(color="#f5ead7", size=11),
        ),
        scene=dict(
            bgcolor=DARK,
            aspectmode="manual",
            aspectratio=scn["aspectratio"],
            camera=camera,
            xaxis=dict(showgrid=True, gridcolor="#2a2d36", zeroline=False, showbackground=False, color="#525861", title="", showticklabels=False, range=scn["ranges"]["x"]),
            yaxis=dict(showgrid=True, gridcolor="#2a2d36", zeroline=False, showbackground=False, color="#525861", title="", showticklabels=False, range=scn["ranges"]["y"]),
            zaxis=dict(showgrid=True, gridcolor="#2a2d36", zeroline=False, showbackground=False, color="#525861", title="", showticklabels=False, range=scn["ranges"]["z"]),
        ),
        annotations=[
            dict(
                text="Arrastra para rotar · rueda para zoom · modelo didáctico simplificado con proporciones más legibles",
                x=0.5,
                y=1.02,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(color="#aeb3bb", size=10),
            )
        ],
        uirevision=f"hyd3d-{machine}-{data.get('subsystem', '')}-{data.get('state', '')}-{data.get('visual_amp', 1)}-{view}",
    )
    chart_key = data.get("plotly_key")
    if not chart_key:
        chart_key = f"hyd3d_auto_{next(_PLOTLY_SEQ)}"
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displaylogo": False, "scrollZoom": True},
        key=chart_key,
    )
