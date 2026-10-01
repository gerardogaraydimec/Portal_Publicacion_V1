from __future__ import annotations

import math
import plotly.graph_objects as go

ORANGE = "#f28e1c"
BLACK = "#171717"
GRAY = "#6f7680"
LIGHT = "#d9dde2"
PALE = "rgba(242,142,28,.08)"
WHITE = "#ffffff"
RETURN = "#7f8994"


def _base(height=430):
    return dict(
        height=height,
        margin=dict(l=12, r=12, t=22, b=16),
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#252932"),
        hovermode=False,
    )


def _line(fig, x0, y0, x1, y1, color=BLACK, width=2.2, dash=None):
    fig.add_shape(
        type="line", x0=x0, y0=y0, x1=x1, y1=y1,
        line=dict(color=color, width=width, dash=dash),
    )


def _rect(fig, x0, y0, x1, y1, color=BLACK, width=2.0, fill=WHITE):
    fig.add_shape(
        type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
        line=dict(color=color, width=width), fillcolor=fill,
    )


def _circle(fig, x, y, r, color=BLACK, width=2.0, fill=WHITE):
    fig.add_shape(
        type="circle", x0=x-r, y0=y-r, x1=x+r, y1=y+r,
        line=dict(color=color, width=width), fillcolor=fill,
    )


def _label(fig, x, y, text, size=12, color=BLACK, bold=False, align="center"):
    fig.add_annotation(
        x=x, y=y, text=f"<b>{text}</b>" if bold else text,
        showarrow=False, font=dict(size=size, color=color), align=align,
        xref="x", yref="y",
    )


def _arrow(fig, x0, y0, x1, y1, color=BLACK, width=2.0, head=2, size=1.0):
    # ax/ay are explicitly in data coordinates. This avoids distorted arrows when the figure is resized.
    fig.add_annotation(
        x=x1, y=y1, ax=x0, ay=y0,
        xref="x", yref="y", axref="x", ayref="y",
        text="", showarrow=True,
        arrowhead=head, arrowsize=size, arrowwidth=width, arrowcolor=color,
    )


def _triangle(fig, x, y, direction="up", color=BLACK, filled=True, size=.22):
    if direction == "up":
        pts = [(x-size, y-size), (x+size, y-size), (x, y+size)]
    elif direction == "down":
        pts = [(x-size, y+size), (x+size, y+size), (x, y-size)]
    elif direction == "right":
        pts = [(x-size, y-size), (x-size, y+size), (x+size, y)]
    else:
        pts = [(x+size, y-size), (x+size, y+size), (x-size, y)]
    path = "M " + " L ".join(f"{a},{b}" for a, b in pts) + " Z"
    fig.add_shape(
        type="path", path=path,
        line=dict(color=color, width=1.4),
        fillcolor=color if filled else WHITE,
    )


def _spring(fig, x0, y0, x1, y1=None, color=BLACK, width=1.6, turns=5):
    if y1 is None:
        y1 = y0
    # Only horizontal springs are needed in this module.
    if abs(y1-y0) > 1e-9:
        _line(fig, x0, y0, x1, y1, color, width)
        return
    dx = (x1-x0)/(2*turns+2)
    xs = [x0]
    ys = [y0]
    for i in range(1, 2*turns+2):
        xs.append(x0+i*dx)
        ys.append(y0 + (.13 if i % 2 else -.13))
    xs.append(x1); ys.append(y0)
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=width), hoverinfo="skip"))


def _blocked_port(fig, x, y, orientation="vertical", color=BLACK):
    # T-shaped closure marker at the end of an internal port line.
    if orientation == "vertical":
        _line(fig, x-.16, y, x+.16, y, color, 2.1)
    else:
        _line(fig, x, y-.16, x, y+.16, color, 2.1)


def _equal_axes(fig, xrange=(0, 10), yrange=(0, 6)):
    fig.update_xaxes(visible=False, range=list(xrange), constrain="domain")
    fig.update_yaxes(visible=False, range=list(yrange), scaleanchor="x", scaleratio=1)
    return fig


# -----------------------------------------------------------------------------
# Fundamental line language
# -----------------------------------------------------------------------------

def line_language_figure():
    fig = go.Figure()
    rows = [
        (5.0, "Línea de presión / trabajo / retorno", None, 2.8),
        (3.95, "Línea de mando o pilotaje", "dash", 2.0),
        (2.90, "Línea de drenaje / fugas", "dashdot", 1.8),
    ]
    for y, label, dash, width in rows:
        _line(fig, .9, y, 4.1, y, BLACK, width, dash)
        _label(fig, 5.55, y, label, 11.3, BLACK, True, "left")

    # Flexible line: curved representation, following the conventional idea in ISO/Festo.
    fig.add_trace(go.Scatter(
        x=[1.0, 1.7, 2.5, 3.3, 4.0],
        y=[1.80, 1.55, 1.55, 1.80, 1.80],
        mode="lines", line=dict(color=BLACK, width=2), hoverinfo="skip",
        line_shape="spline",
    ))
    _circle(fig, 1.0, 1.80, .04, BLACK, 1, BLACK)
    _circle(fig, 4.0, 1.80, .04, BLACK, 1, BLACK)
    _label(fig, 5.55, 1.70, "Línea flexible", 11.3, BLACK, True, "left")

    _label(fig, 8.0, 5.45, "Unión", 11, BLACK, True)
    _line(fig, 7.2, 4.85, 8.8, 4.85, BLACK, 2.1)
    _line(fig, 8.0, 4.15, 8.0, 5.55, BLACK, 2.1)
    _circle(fig, 8.0, 4.85, .055, BLACK, 1.0, BLACK)

    _label(fig, 8.0, 3.55, "Cruce sin conexión", 11, BLACK, True)
    _line(fig, 7.2, 2.95, 8.8, 2.95, BLACK, 2.1)
    _line(fig, 8.0, 2.25, 8.0, 3.65, BLACK, 2.1)
    # small bridge in horizontal line
    fig.add_trace(go.Scatter(
        x=[7.75, 7.88, 8.00, 8.12, 8.25],
        y=[2.95, 3.06, 3.10, 3.06, 2.95],
        mode="lines", line=dict(color=WHITE, width=5.0), hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=[7.75, 7.88, 8.00, 8.12, 8.25],
        y=[2.95, 3.06, 3.10, 3.06, 2.95],
        mode="lines", line=dict(color=BLACK, width=2.0), hoverinfo="skip",
    ))

    fig.update_layout(**_base(410))
    fig.update_xaxes(visible=False, range=[.25, 9.4])
    fig.update_yaxes(visible=False, range=[1.1, 5.8])
    return fig


# -----------------------------------------------------------------------------
# Symbol library
# -----------------------------------------------------------------------------

def _draw_pump_motor(fig, mode="pump", variable=False):
    cx, cy, r = 5.0, 3.05, 1.0
    _circle(fig, cx, cy, r, BLACK, 2.8, WHITE)
    # hydraulic connections top and bottom
    _line(fig, cx, cy+r, cx, cy+r+.65, BLACK, 2.5)
    _line(fig, cx, cy-r-.65, cx, cy-r, BLACK, 2.5)
    # shaft marker, pump on left; motor on right (mirrors the Festo presentation)
    sx = cx-r if mode == "pump" else cx+r
    direction = -1 if mode == "pump" else 1
    _line(fig, sx, cy-.13, sx+direction*.58, cy-.13, BLACK, 1.8)
    _line(fig, sx, cy+.13, sx+direction*.58, cy+.13, BLACK, 1.8)
    # filled hydraulic triangle: outward for pump, inward for motor
    if mode == "pump":
        _triangle(fig, cx, cy+.48, "up", BLACK, True, .25)
    else:
        _triangle(fig, cx, cy+.48, "down", BLACK, True, .25)
    if variable:
        _arrow(fig, cx-.88, cy-.90, cx+.88, cy+.90, BLACK, 1.7, 2, .9)


def _draw_filter(fig):
    # ISO/Festo: diamond with internal broken line perpendicular to main flow.
    path = "M 4.0,3.0 L 5.0,4.0 L 6.0,3.0 L 5.0,2.0 Z"
    fig.add_shape(type="path", path=path, line=dict(color=BLACK, width=2.5), fillcolor=WHITE)
    _line(fig, 2.6, 3.0, 4.0, 3.0, BLACK, 2.5)
    _line(fig, 6.0, 3.0, 7.4, 3.0, BLACK, 2.5)
    _line(fig, 5.0, 2.32, 5.0, 3.68, BLACK, 1.9, "dash")


def _draw_pressure_gauge(fig):
    _circle(fig, 5.0, 3.2, .92, BLACK, 2.5, WHITE)
    _line(fig, 5.0, 2.28, 5.0, 1.25, BLACK, 2.3)
    # pointer with arrowhead, as shown in the Festo/ISO family of symbols
    _arrow(fig, 5.0, 3.2, 4.45, 3.72, BLACK, 1.8, 2, .75)


def _draw_reservoir(fig):
    # Open reservoir: three sides, open at top.
    _line(fig, 3.45, 4.15, 3.45, 1.75, BLACK, 2.7)
    _line(fig, 3.45, 1.75, 6.55, 1.75, BLACK, 2.7)
    _line(fig, 6.55, 1.75, 6.55, 4.15, BLACK, 2.7)


def _draw_cylinder_double(fig):
    _rect(fig, 2.0, 2.05, 7.2, 4.05, BLACK, 2.7, WHITE)
    _line(fig, 4.45, 2.05, 4.45, 4.05, BLACK, 2.7)
    _line(fig, 4.45, 3.05, 8.45, 3.05, BLACK, 2.7)
    _line(fig, 2.9, 2.05, 2.9, 1.20, BLACK, 2.2)
    _line(fig, 6.25, 2.05, 6.25, 1.20, BLACK, 2.2)
    _label(fig, 2.9, .86, "A", 11.5, BLACK, True)
    _label(fig, 6.25, .86, "B", 11.5, BLACK, True)


def _draw_check(fig, piloted=False):
    # Ball against an open triangular seat. The triangle point indicates blocked direction.
    y = 3.0
    _line(fig, 2.6, y, 4.15, y, BLACK, 2.5)
    _circle(fig, 4.45, y, .22, BLACK, 1.8, WHITE)
    _triangle(fig, 5.15, y, "left", BLACK, False, .34)
    _line(fig, 5.49, y, 7.4, y, BLACK, 2.5)
    if piloted:
        _rect(fig, 3.95, 2.35, 5.65, 3.65, BLACK, 1.7, "rgba(0,0,0,0)")
        _line(fig, 4.80, 2.35, 4.80, 1.25, BLACK, 1.8, "dash")
        _label(fig, 5.13, 1.08, "X", 11, BLACK, True)


def _draw_flow_control(fig, bypass=False):
    # Adjustable restrictor/orifice: two opposed curved edges plus diagonal adjustment arrow.
    _line(fig, 2.5, 3.0, 4.05, 3.0, BLACK, 2.4)
    _line(fig, 5.95, 3.0, 7.5, 3.0, BLACK, 2.4)
    fig.add_trace(go.Scatter(x=[4.05, 4.55, 5.0], y=[2.55, 2.80, 3.0], mode="lines", line=dict(color=BLACK, width=1.8), hoverinfo="skip", line_shape="spline"))
    fig.add_trace(go.Scatter(x=[5.0, 5.45, 5.95], y=[3.0, 3.20, 3.45], mode="lines", line=dict(color=BLACK, width=1.8), hoverinfo="skip", line_shape="spline"))
    fig.add_trace(go.Scatter(x=[4.05, 4.55, 5.0], y=[3.45, 3.20, 3.0], mode="lines", line=dict(color=BLACK, width=1.8), hoverinfo="skip", line_shape="spline"))
    fig.add_trace(go.Scatter(x=[5.0, 5.45, 5.95], y=[3.0, 2.80, 2.55], mode="lines", line=dict(color=BLACK, width=1.8), hoverinfo="skip", line_shape="spline"))
    _arrow(fig, 4.05, 1.65, 5.95, 4.35, BLACK, 1.6, 2, .8)
    if bypass:
        _line(fig, 3.0, 4.85, 7.0, 4.85, BLACK, 1.7)
        _circle(fig, 4.35, 4.85, .18, BLACK, 1.4, WHITE)
        _triangle(fig, 5.00, 4.85, "left", BLACK, False, .28)
        _line(fig, 3.0, 3.0, 3.0, 4.85, BLACK, 1.7)
        _line(fig, 7.0, 3.0, 7.0, 4.85, BLACK, 1.7)


def _draw_pressure_valve(fig, reducing=False):
    # Pressure valves shown as squares with flow arrow, spring and pressure sensing.
    x0, x1, y0, y1 = 4.15, 5.85, 2.10, 3.90
    _rect(fig, x0, y0, x1, y1, BLACK, 2.3, WHITE)
    if reducing:
        # normally open regulator: P -> A through the valve; downstream sensing.
        _arrow(fig, 5.0, 2.35, 5.0, 3.62, BLACK, 1.9, 2, .8)
        _line(fig, 5.0, y0-.65, 5.0, y0, BLACK, 2.2)
        _line(fig, 5.0, y1, 5.0, y1+.65, BLACK, 2.2)
        _label(fig, 4.70, y0-.82, "P", 11, BLACK, True)
        _label(fig, 4.70, y1+.82, "A", 11, BLACK, True)
        # drain T at side for 3-way regulator
        _line(fig, x1, 2.55, x1+.70, 2.55, BLACK, 1.9)
        _label(fig, x1+.90, 2.55, "T", 10.5, BLACK, True)
        # downstream sensing line
        _line(fig, 5.0, y1+.35, 3.55, y1+.35, BLACK, 1.5, "dash")
        _line(fig, 3.55, y1+.35, 3.55, 3.00, BLACK, 1.5, "dash")
        _line(fig, 3.55, 3.00, x0, 3.00, BLACK, 1.5, "dash")
    else:
        # relief: normally closed path P -> T opens with upstream pressure.
        _arrow(fig, 5.0, 3.60, 5.0, 2.40, BLACK, 1.9, 2, .8)
        _line(fig, 5.0, y1, 5.0, y1+.65, BLACK, 2.2)
        _line(fig, 5.0, y0-.65, 5.0, y0, BLACK, 2.2)
        _label(fig, 4.70, y1+.82, "P", 11, BLACK, True)
        _label(fig, 4.70, y0-.82, "T", 11, BLACK, True)
        # upstream sensing line
        _line(fig, 5.0, y1+.35, 3.55, y1+.35, BLACK, 1.5, "dash")
        _line(fig, 3.55, y1+.35, 3.55, 3.00, BLACK, 1.5, "dash")
        _line(fig, 3.55, 3.00, x0, 3.00, BLACK, 1.5, "dash")
    # spring and adjustment arrow through spring
    _spring(fig, x1, 3.02, x1+1.25, 3.02, BLACK, 1.5, 4)
    _arrow(fig, x1+.20, 2.30, x1+1.10, 3.75, BLACK, 1.4, 2, .7)


def symbol_figure(symbol_key: str, title: str):
    fig = go.Figure()
    if symbol_key == "main_line":
        _line(fig, 2.2, 3.0, 7.8, 3.0, BLACK, 3.0)
    elif symbol_key == "pilot_line":
        _line(fig, 2.2, 3.0, 7.8, 3.0, BLACK, 2.0, "dash")
    elif symbol_key == "drain_line":
        _line(fig, 2.2, 3.0, 7.8, 3.0, BLACK, 1.8, "dashdot")
    elif symbol_key == "reservoir":
        _draw_reservoir(fig)
    elif symbol_key == "pump_fixed":
        _draw_pump_motor(fig, "pump", False)
    elif symbol_key == "pump_variable":
        _draw_pump_motor(fig, "pump", True)
    elif symbol_key == "motor_fixed":
        _draw_pump_motor(fig, "motor", False)
    elif symbol_key == "filter":
        _draw_filter(fig)
    elif symbol_key == "gauge":
        _draw_pressure_gauge(fig)
    elif symbol_key == "cylinder_double":
        _draw_cylinder_double(fig)
    elif symbol_key == "relief":
        _draw_pressure_valve(fig, False)
    elif symbol_key == "reducing":
        _draw_pressure_valve(fig, True)
    elif symbol_key == "check":
        _draw_check(fig, False)
    elif symbol_key == "pilot_check":
        _draw_check(fig, True)
    elif symbol_key == "flow_control":
        _draw_flow_control(fig, False)
    elif symbol_key == "one_way_flow":
        _draw_flow_control(fig, True)
    else:
        _label(fig, 5.0, 3.0, title, 18, BLACK, True)

    _label(fig, 5.0, 5.45, title, 15, BLACK, True)
    fig.update_layout(**_base(430))
    return _equal_axes(fig, (1.3, 8.7), (.45, 5.8))


# -----------------------------------------------------------------------------
# Directional valves
# -----------------------------------------------------------------------------

def _state_specs(valve_name: str):
    low = valve_name.lower()
    if valve_name.startswith("4/3"):
        center = "closed"
        if "tándem" in low:
            center = "tandem"
        elif "flotante" in low:
            center = "float"
        elif "abierto" in low:
            center = "open"
        return ["pa_bt", center, "pb_at"]
    if valve_name.startswith("4/2"):
        return ["pa_bt", "pb_at"]
    if valve_name.startswith("3/2"):
        return ["at_pblocked", "pa_tblocked"]
    if valve_name.startswith("2/2 NC"):
        return ["blocked_pa", "pa"]
    if valve_name.startswith("2/2 NO"):
        return ["pa", "blocked_pa"]
    return []


def _cell_ports(cx, y0, y1):
    return {
        "A": (cx-.34, y1),
        "B": (cx+.34, y1),
        "P": (cx-.34, y0),
        "T": (cx+.34, y0),
    }


def _draw_cell(fig, cx, y0, y1, spec, active=False):
    w = 1.46
    _rect(fig, cx-w/2, y0, cx+w/2, y1, ORANGE if active else BLACK, 2.5 if active else 1.8, PALE if active else WHITE)
    p = _cell_ports(cx, y0+.15, y1-.15)
    flow_color = ORANGE if active else BLACK
    if spec == "pa_bt":
        # straight vertical paths, as in the standard examples
        _arrow(fig, p["P"][0], p["P"][1], p["A"][0], p["A"][1], flow_color, 1.9, 2, .7)
        _arrow(fig, p["B"][0], p["B"][1], p["T"][0], p["T"][1], flow_color, 1.9, 2, .7)
    elif spec == "pb_at":
        # crossed position: straight diagonal paths are conventional and avoid artificial dog-leg geometry
        _arrow(fig, p["P"][0], p["P"][1], p["B"][0], p["B"][1], flow_color, 1.9, 2, .7)
        _arrow(fig, p["A"][0], p["A"][1], p["T"][0], p["T"][1], flow_color, 1.9, 2, .7)
    elif spec == "closed":
        for x, y in p.values():
            _blocked_port(fig, x, y, "vertical", BLACK)
    elif spec == "tandem":
        # P connected to T along bottom; A and B blocked.
        y = y0+.42
        _line(fig, p["P"][0], p["P"][1], p["P"][0], y, flow_color, 1.8)
        _arrow(fig, p["P"][0], y, p["T"][0], y, flow_color, 1.8, 2, .7)
        _line(fig, p["T"][0], y, p["T"][0], p["T"][1], flow_color, 1.8)
        _blocked_port(fig, p["A"][0], p["A"][1], "vertical")
        _blocked_port(fig, p["B"][0], p["B"][1], "vertical")
    elif spec == "float":
        # A and B connected to T; P blocked.
        ym = (y0+y1)/2
        _line(fig, p["A"][0], p["A"][1], p["A"][0], ym, flow_color, 1.8)
        _line(fig, p["B"][0], p["B"][1], p["B"][0], ym, flow_color, 1.8)
        _line(fig, p["A"][0], ym, p["T"][0], ym, flow_color, 1.8)
        _line(fig, p["B"][0], ym, p["T"][0], ym, flow_color, 1.8)
        _arrow(fig, p["T"][0], ym, p["T"][0], p["T"][1], flow_color, 1.8, 2, .7)
        _blocked_port(fig, p["P"][0], p["P"][1], "vertical")
    elif spec == "open":
        ym = (y0+y1)/2
        _circle(fig, cx, ym, .045, flow_color, 1, flow_color)
        for name, (x, y) in p.items():
            _line(fig, x, y, x, ym, flow_color, 1.7)
            _line(fig, x, ym, cx, ym, flow_color, 1.7)
    elif spec == "at_pblocked":
        _arrow(fig, p["A"][0], p["A"][1], p["T"][0], p["T"][1], flow_color, 1.8, 2, .7)
        _blocked_port(fig, p["P"][0], p["P"][1], "vertical")
    elif spec == "pa_tblocked":
        _arrow(fig, p["P"][0], p["P"][1], p["A"][0], p["A"][1], flow_color, 1.8, 2, .7)
        _blocked_port(fig, p["T"][0], p["T"][1], "vertical")
    elif spec == "blocked_pa":
        _blocked_port(fig, cx, y0+.15, "vertical")
        _blocked_port(fig, cx, y1-.15, "vertical")
    elif spec == "pa":
        _arrow(fig, cx, y0+.15, cx, y1-.15, flow_color, 1.8, 2, .7)


def _draw_solenoid(fig, edge, mid, side="left"):
    w, h = .55, .72
    if side == "left":
        _rect(fig, edge-w, mid-h/2, edge, mid+h/2, BLACK, 1.7, WHITE)
        _line(fig, edge-w+.08, mid-h/2+.08, edge-.08, mid+h/2-.08, BLACK, 1.4)
    else:
        _rect(fig, edge, mid-h/2, edge+w, mid+h/2, BLACK, 1.7, WHITE)
        _line(fig, edge+.08, mid-h/2+.08, edge+w-.08, mid+h/2-.08, BLACK, 1.4)


def _draw_lever(fig, edge, mid, side="left"):
    # Lever with pivot/end circle, attached by a short stem.
    if side == "left":
        _line(fig, edge-.22, mid, edge, mid, BLACK, 1.8)
        _line(fig, edge-.22, mid, edge-.72, mid+.72, BLACK, 1.8)
        _circle(fig, edge-.78, mid+.82, .075, BLACK, 1.2, WHITE)
    else:
        _line(fig, edge, mid, edge+.22, mid, BLACK, 1.8)
        _line(fig, edge+.22, mid, edge+.72, mid+.72, BLACK, 1.8)
        _circle(fig, edge+.78, mid+.82, .075, BLACK, 1.2, WHITE)


def _draw_hydraulic_pilot(fig, edge, mid, side="left"):
    if side == "left":
        _triangle(fig, edge-.27, mid, "right", BLACK, False, .23)
        _line(fig, edge-.85, mid, edge-.50, mid, BLACK, 1.5, "dash")
    else:
        _triangle(fig, edge+.27, mid, "left", BLACK, False, .23)
        _line(fig, edge+.50, mid, edge+.85, mid, BLACK, 1.5, "dash")


def directional_valve_figure(valve_name: str, position: str, actuation: str="Solenoide + retorno por resorte"):
    specs = _state_specs(valve_name)
    n = len(specs)
    labels = ["Izquierda", "Centro", "Derecha"] if n == 3 else ["Izquierda", "Derecha"]
    centers = [3.55, 5.00, 6.45] if n == 3 else [4.28, 5.72]
    y0, y1 = 2.10, 4.30
    active_idx = labels.index(position if position in labels else labels[0])
    fig = go.Figure()

    for i, (cx, spec) in enumerate(zip(centers, specs)):
        _draw_cell(fig, cx, y0, y1, spec, i == active_idx)
        _label(fig, cx, 4.70, labels[i], 9.8, ORANGE if i == active_idx else GRAY, i == active_idx)

    # External ports are shown at the rest/central position for 4/3, consistent with circuit convention.
    ref = centers[1] if n == 3 else centers[0]
    if valve_name.startswith("4/"):
        ports = [(ref-.34, y1, "A", .50), (ref+.34, y1, "B", .50), (ref-.34, y0, "P", -.50), (ref+.34, y0, "T", -.50)]
    elif valve_name.startswith("3/2"):
        ports = [(ref, y1, "A", .50), (ref-.34, y0, "P", -.50), (ref+.34, y0, "T", -.50)]
    else:
        ports = [(ref, y1, "A", .50), (ref, y0, "P", -.50)]
    for x, y, p, dy in ports:
        _line(fig, x, y, x, y+dy, BLACK, 2.0)
        _label(fig, x, y+dy+(.16 if dy > 0 else -.16), p, 10.7, BLACK, True)

    left_edge = min(centers)-.73
    right_edge = max(centers)+.73
    mid = (y0+y1)/2
    if actuation.startswith("Solenoide"):
        if n == 3:
            # Centering springs adjacent to body + solenoids outside.
            _spring(fig, left_edge-.62, mid, left_edge, mid, BLACK, 1.4, 3)
            _spring(fig, right_edge, mid, right_edge+.62, mid, BLACK, 1.4, 3)
            _draw_solenoid(fig, left_edge-.62, mid, "left")
            _draw_solenoid(fig, right_edge+.62, mid, "right")
        else:
            _draw_solenoid(fig, left_edge, mid, "left")
            _spring(fig, right_edge, mid, right_edge+.85, mid, BLACK, 1.4, 4)
    elif actuation.startswith("Palanca"):
        _draw_lever(fig, left_edge, mid, "left")
        _spring(fig, right_edge, mid, right_edge+.85, mid, BLACK, 1.4, 4)
    else:
        if n == 3:
            _draw_hydraulic_pilot(fig, left_edge, mid, "left")
            _draw_hydraulic_pilot(fig, right_edge, mid, "right")
            _spring(fig, left_edge-.55, mid-.55, left_edge, mid-.55, BLACK, 1.2, 3)
            _spring(fig, right_edge, mid-.55, right_edge+.55, mid-.55, BLACK, 1.2, 3)
        else:
            _draw_hydraulic_pilot(fig, left_edge, mid, "left")
            _spring(fig, right_edge, mid, right_edge+.85, mid, BLACK, 1.4, 4)

    _label(fig, 5.0, 5.60, valve_name, 15, BLACK, True)
    fig.update_layout(**_base(455))
    fig.update_xaxes(visible=False, range=[1.0, 9.0])
    fig.update_yaxes(visible=False, range=[.70, 5.90])
    return fig


# -----------------------------------------------------------------------------
# Complete teaching circuit with real 4/3 symbol changing by center and state
# -----------------------------------------------------------------------------

def _draw_circuit_pump(fig, cx, cy, r=.34):
    _circle(fig, cx, cy, r, BLACK, 2.0, WHITE)
    _triangle(fig, cx+.11, cy, "right", BLACK, True, .12)


def _draw_circuit_reservoir(fig, x, y, w=1.1, h=.65):
    _line(fig, x, y+h, x, y, BLACK, 2.0)
    _line(fig, x, y, x+w, y, BLACK, 2.0)
    _line(fig, x+w, y, x+w, y+h, BLACK, 2.0)


def _draw_full_4_3(fig, cx, cy, valve_name, state):
    specs = _state_specs(valve_name)
    centers = [cx-1.0, cx, cx+1.0]
    y0, y1 = cy-.72, cy+.72
    idx = {"Izquierda": 0, "Centro": 1, "Derecha": 2}[state]
    for i, (x, spec) in enumerate(zip(centers, specs)):
        _draw_cell(fig, x, y0, y1, spec, i == idx)
    # ports on center cell
    ports = {
        "A": (cx-.34, y1), "B": (cx+.34, y1),
        "P": (cx-.34, y0), "T": (cx+.34, y0),
    }
    return ports, centers, (y0, y1), idx


def circuit_state_figure(valve_name: str, state: str):
    fig = go.Figure()

    # Fixed geometry coordinates
    tank_x, tank_y = .55, .45
    _draw_circuit_reservoir(fig, tank_x, tank_y, 1.20, .72)
    _label(fig, 1.15, .18, "DEPÓSITO", 9.2, GRAY, True)

    # Pump and suction
    pump_x, pump_y = 2.30, 1.55
    _draw_circuit_pump(fig, pump_x, pump_y, .38)
    _line(fig, 1.15, 1.17, 1.15, pump_y, BLACK, 2.1)
    _line(fig, 1.15, pump_y, pump_x-.38, pump_y, BLACK, 2.1)
    _label(fig, pump_x, .98, "BOMBA", 9.2, GRAY, True)

    # Pressure line to valve
    p_y = pump_y
    _line(fig, pump_x+.38, p_y, 5.12, p_y, ORANGE, 3.0)

    # Pressure gauge tee
    _line(fig, 3.10, p_y, 3.10, 2.22, BLACK, 1.8)
    _circle(fig, 3.10, 2.58, .30, BLACK, 1.6, WHITE)
    _arrow(fig, 3.10, 2.58, 2.93, 2.75, BLACK, 1.2, 2, .6)

    # Relief branch: conventional compact representation
    rel_x = 3.82
    _line(fig, rel_x, p_y, rel_x, 1.05, ORANGE, 2.2)
    _rect(fig, rel_x-.28, .63, rel_x+.28, 1.05, BLACK, 1.5, WHITE)
    _arrow(fig, rel_x, .98, rel_x, .70, BLACK, 1.1, 2, .6)
    _spring(fig, rel_x+.28, .84, rel_x+.80, .84, BLACK, 1.1, 3)
    _line(fig, rel_x, .63, rel_x, tank_y, RETURN, 2.1)
    _line(fig, rel_x, tank_y, tank_x+1.05, tank_y, RETURN, 2.1)
    _label(fig, rel_x+.62, .45, "ALIVIO", 8.5, GRAY)

    # Full 4/3 valve: changes visibly with selected center type
    valve_cx, valve_cy = 5.80, 3.55
    ports, centers, (vy0, vy1), active_idx = _draw_full_4_3(fig, valve_cx, valve_cy, valve_name, state)
    _label(fig, valve_cx, 4.70, "VÁLVULA 4/3", 9.4, GRAY, True)

    # P and T connections to center-box external ports
    _line(fig, 5.12, p_y, ports["P"][0], p_y, ORANGE, 3.0)
    _line(fig, ports["P"][0], p_y, ports["P"][0], ports["P"][1], ORANGE, 3.0)
    _line(fig, ports["T"][0], ports["T"][1], ports["T"][0], .76, RETURN, 2.5)
    _line(fig, ports["T"][0], .76, tank_x+.65, .76, RETURN, 2.5)
    _line(fig, tank_x+.65, .76, tank_x+.65, tank_y, RETURN, 2.5)

    # Cylinder
    cyl_x0, cyl_x1, cyl_y0, cyl_y1 = 7.55, 9.65, 5.25, 6.35
    _rect(fig, cyl_x0, cyl_y0, cyl_x1, cyl_y1, BLACK, 2.2, WHITE)
    piston_x = 8.38
    _line(fig, piston_x, cyl_y0, piston_x, cyl_y1, BLACK, 2.2)
    _line(fig, piston_x, (cyl_y0+cyl_y1)/2, 10.10, (cyl_y0+cyl_y1)/2, BLACK, 2.2)
    a_x, b_x = 7.95, 9.18
    _line(fig, a_x, cyl_y0, a_x, 5.02, BLACK, 2.0)
    _line(fig, b_x, cyl_y0, b_x, 5.02, BLACK, 2.0)
    _label(fig, 8.60, 6.68, "CILINDRO DOBLE EFECTO", 9.4, GRAY, True)

    # Working lines (always fixed geometry)
    _line(fig, ports["A"][0], ports["A"][1], ports["A"][0], 4.90, BLACK, 2.1)
    _line(fig, ports["A"][0], 4.90, a_x, 4.90, BLACK, 2.1)
    _line(fig, a_x, 4.90, a_x, 5.25, BLACK, 2.1)
    _line(fig, ports["B"][0], ports["B"][1], ports["B"][0], 4.62, BLACK, 2.1)
    _line(fig, ports["B"][0], 4.62, b_x, 4.62, BLACK, 2.1)
    _line(fig, b_x, 4.62, b_x, 5.25, BLACK, 2.1)

    # Highlight active outside paths. Full valve symbol itself also highlights the active state.
    if state == "Izquierda":
        _line(fig, ports["A"][0], ports["A"][1], ports["A"][0], 4.90, ORANGE, 3.0)
        _line(fig, ports["A"][0], 4.90, a_x, 4.90, ORANGE, 3.0)
        _line(fig, a_x, 4.90, a_x, 5.25, ORANGE, 3.0)
        _line(fig, b_x, 5.25, b_x, 4.62, RETURN, 2.8)
        _line(fig, b_x, 4.62, ports["B"][0], 4.62, RETURN, 2.8)
        _line(fig, ports["B"][0], 4.62, ports["B"][0], ports["B"][1], RETURN, 2.8)
        _arrow(fig, 8.60, 6.95, 9.55, 6.95, ORANGE, 2.0, 2, .8)
        _label(fig, 9.05, 7.18, "AVANCE", 9.0, ORANGE, True)
    elif state == "Derecha":
        _line(fig, ports["B"][0], ports["B"][1], ports["B"][0], 4.62, ORANGE, 3.0)
        _line(fig, ports["B"][0], 4.62, b_x, 4.62, ORANGE, 3.0)
        _line(fig, b_x, 4.62, b_x, 5.25, ORANGE, 3.0)
        _line(fig, a_x, 5.25, a_x, 4.90, RETURN, 2.8)
        _line(fig, a_x, 4.90, ports["A"][0], 4.90, RETURN, 2.8)
        _line(fig, ports["A"][0], 4.90, ports["A"][0], ports["A"][1], RETURN, 2.8)
        _arrow(fig, 9.55, 6.95, 8.60, 6.95, ORANGE, 2.0, 2, .8)
        _label(fig, 9.05, 7.18, "RETROCESO", 9.0, ORANGE, True)
    else:
        # Center state: show only behavior associated with the chosen center.
        low = valve_name.lower()
        if "tándem" in low:
            _line(fig, ports["P"][0], p_y, ports["P"][0], ports["P"][1], ORANGE, 3.0)
            _line(fig, ports["T"][0], ports["T"][1], ports["T"][0], .76, RETURN, 2.8)
        elif "flotante" in low:
            _line(fig, a_x, 5.25, a_x, 4.90, RETURN, 2.8)
            _line(fig, a_x, 4.90, ports["A"][0], 4.90, RETURN, 2.8)
            _line(fig, b_x, 5.25, b_x, 4.62, RETURN, 2.8)
            _line(fig, b_x, 4.62, ports["B"][0], 4.62, RETURN, 2.8)
        elif "abierto" in low:
            # all ports communicate: show supply and return colors without implying a unique actuator motion
            _line(fig, ports["P"][0], p_y, ports["P"][0], ports["P"][1], ORANGE, 3.0)
            _line(fig, a_x, 5.25, a_x, 4.90, RETURN, 2.6)
            _line(fig, b_x, 5.25, b_x, 4.62, RETURN, 2.6)

    # labels and legend
    _label(fig, 5.35, 7.65, "Circuito hidráulico base", 14, BLACK, True)
    _label(fig, 5.35, 7.35, "El símbolo 4/3 cambia con el centro seleccionado; el estado activo queda resaltado sin mover la geometría del circuito.", 10.0, GRAY)
    _line(fig, 7.20, .45, 7.80, .45, ORANGE, 3.0); _label(fig, 8.18, .45, "alimentación / presión", 9.0, GRAY, False, "left")
    _line(fig, 7.20, .18, 7.80, .18, RETURN, 2.7); _label(fig, 8.18, .18, "retorno", 9.0, GRAY, False, "left")

    fig.update_layout(**_base(610))
    fig.update_xaxes(visible=False, range=[.15, 10.45])
    fig.update_yaxes(visible=False, range=[0, 7.95])
    return fig
