from __future__ import annotations

import plotly.graph_objects as go

ORANGE = "#f28e1c"
BLACK = "#151515"
GRAY = "#747980"
LIGHT = "#f5f5f2"


def _rect(fig, x0, y0, x1, y1, fill=BLACK, line=BLACK, width=1.5):
    fig.add_shape(
        type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
        line=dict(color=line, width=width),
        fillcolor=fill,
    )


def _dimension_vertical(fig, x, y0, y1, label, text_x=None):
    fig.add_shape(type="line", x0=x, x1=x, y0=y0, y1=y1,
                  line=dict(color=GRAY, width=1.4))
    cap = max(abs(y1-y0)*0.035, 2.5)
    fig.add_shape(type="line", x0=x-cap, x1=x+cap, y0=y0, y1=y0,
                  line=dict(color=GRAY, width=1.4))
    fig.add_shape(type="line", x0=x-cap, x1=x+cap, y0=y1, y1=y1,
                  line=dict(color=GRAY, width=1.4))
    fig.add_annotation(
        x=x if text_x is None else text_x,
        y=(y0+y1)/2,
        text=label,
        textangle=-90,
        showarrow=False,
        font=dict(size=13, color=GRAY),
        bgcolor="rgba(255,255,255,.92)",
        borderpad=2,
    )


def _dimension_horizontal(fig, x0, x1, y, label, text_y=None):
    fig.add_shape(type="line", x0=x0, x1=x1, y0=y, y1=y,
                  line=dict(color=GRAY, width=1.4))
    cap = max(abs(x1-x0)*0.035, 2.5)
    fig.add_shape(type="line", x0=x0, x1=x0, y0=y-cap, y1=y+cap,
                  line=dict(color=GRAY, width=1.4))
    fig.add_shape(type="line", x0=x1, x1=x1, y0=y-cap, y1=y+cap,
                  line=dict(color=GRAY, width=1.4))
    fig.add_annotation(
        x=(x0+x1)/2,
        y=y if text_y is None else text_y,
        text=label,
        showarrow=False,
        font=dict(size=13, color=GRAY),
        bgcolor="rgba(255,255,255,.92)",
        borderpad=2,
    )


def _axis(fig, x0, x1, y0, y1, label, lx, ly):
    fig.add_shape(
        type="line", x0=x0, x1=x1, y0=y0, y1=y1,
        line=dict(color=ORANGE, width=2, dash="dash")
    )
    fig.add_annotation(
        x=lx, y=ly, text=f"<b>{label}</b>",
        showarrow=False,
        font=dict(size=13, color=ORANGE),
        bgcolor="rgba(255,255,255,.92)",
        borderpad=2,
    )


def _leader(fig, x, y, ax, ay, label):
    fig.add_annotation(
        x=x, y=y, ax=ax, ay=ay,
        text=label, showarrow=True,
        arrowhead=2, arrowsize=1, arrowwidth=1.4,
        arrowcolor=GRAY,
        font=dict(size=12, color=GRAY),
        bgcolor="rgba(255,255,255,.94)",
        borderpad=2,
    )


def _channel_centroid_x(p: dict) -> float:
    b = float(p["b_mm"])
    h = float(p["h_mm"])
    tw = float(p["tw_mm"])
    tf = float(p["tf_mm"])
    aw = tw*h
    af = max(b-tw, 0)*tf
    A = aw + 2*af
    return (aw*(tw/2) + 2*af*(tw + (b-tw)/2)) / A if A > 0 else b/2


def make_section_figure(p: dict):
    shape = p["shape"]
    fig = go.Figure()
    caption = ""

    if shape in {"I", "H", "IPN"}:
        h = float(p["h_mm"]); b = float(p["b_mm"])
        tw = float(p["tw_mm"]); tf = float(p["tf_mm"])
        _rect(fig, -b/2, h/2-tf, b/2, h/2)
        _rect(fig, -tw/2, -h/2+tf, tw/2, h/2-tf)
        _rect(fig, -b/2, -h/2, b/2, -h/2+tf)

        _axis(fig, -0.62*b, 0.62*b, 0, 0, "x–x", 0.56*b, 0.06*h)
        _axis(fig, 0, 0, -0.62*h, 0.62*h, "y–y", 0.08*b, 0.56*h)
        fig.add_annotation(x=0, y=0, text="<b>G</b>", showarrow=False,
                           font=dict(size=11, color="white"),
                           bgcolor=ORANGE, borderpad=4)

        dim_x = -0.78*b
        dim_y = -0.72*h
        _dimension_vertical(fig, dim_x, -h/2, h/2, f"h = {h:g} mm")
        _dimension_horizontal(fig, -b/2, b/2, dim_y, f"b = {b:g} mm")

        _leader(fig, tw/2, 0.17*h, 0.42*b, 0.22*h, f"tᵥ = {tw:g} mm")
        _leader(fig, 0.18*b, h/2-tf/2, 0.48*b, 0.38*h, f"t_f = {tf:g} mm")

        if p.get("r_mm"):
            _leader(fig, tw/2, h/2-tf, 0.46*b, 0.17*h, f"r = {p['r_mm']:g} mm")

        caption = (
            "El eje x–x corresponde normalmente al eje de mayor rigidez a flexión. "
            "El eje y–y es el eje débil. G identifica el centroide."
        )
        if shape == "IPN":
            caption += " El IPN real posee inclinación interior de alas; el dibujo es pedagógico."

        limx = max(b*1.10, h*0.58)
        limy = h*0.82
        fig.update_xaxes(range=[-limx, limx])
        fig.update_yaxes(range=[-limy, limy])

    elif shape == "C":
        h = float(p["h_mm"]); b = float(p["b_mm"])
        tw = float(p["tw_mm"]); tf = float(p["tf_mm"])
        _rect(fig, 0, -h/2, tw, h/2)
        _rect(fig, tw, h/2-tf, b, h/2)
        _rect(fig, tw, -h/2, b, -h/2+tf)

        xg = _channel_centroid_x(p)
        _axis(fig, -0.12*b, 1.10*b, 0, 0, "x–x", 1.02*b, 0.06*h)
        _axis(fig, xg, xg, -0.62*h, 0.62*h, "y–y", xg+0.09*b, 0.56*h)
        fig.add_annotation(x=xg, y=0, text="<b>G</b>", showarrow=False,
                           font=dict(size=10, color="white"),
                           bgcolor=ORANGE, borderpad=4)

        _dimension_vertical(fig, -0.30*b, -h/2, h/2, f"h = {h:g} mm")
        _dimension_horizontal(fig, 0, b, -0.72*h, f"b = {b:g} mm")
        _leader(fig, tw/2, 0.18*h, 0.40*b, 0.22*h, f"tᵥ = {tw:g} mm")
        _leader(fig, 0.54*b, h/2-tf/2, 0.82*b, 0.36*h, f"t_f = {tf:g} mm")
        if p.get("r_mm"):
            _leader(fig, tw, h/2-tf, 0.76*b, 0.12*h, f"r = {p['r_mm']:g} mm")

        caption = (
            "En una sección U el centroide no está sobre la mitad del ancho. "
            "El eje x–x es horizontal y pasa por G; el eje y–y también pasa por G. "
            "El esquema no representa con detalle la inclinación/radios reales del UPN."
        )
        fig.update_xaxes(range=[-0.48*b, 1.35*b])
        fig.update_yaxes(range=[-0.82*h, 0.82*h])

    elif shape == "BOX":
        h = float(p["h_mm"]); b = float(p["b_mm"]); t = float(p["t_mm"])
        _rect(fig, -b/2, -h/2, b/2, h/2)
        ib = max(b-2*t, 0); ih = max(h-2*t, 0)
        _rect(fig, -ib/2, -ih/2, ib/2, ih/2, fill="white", line="white", width=1)

        _axis(fig, -0.62*b, 0.62*b, 0, 0, "x–x", 0.56*b, 0.06*h)
        _axis(fig, 0, 0, -0.62*h, 0.62*h, "y–y", 0.08*b, 0.56*h)
        fig.add_annotation(x=0, y=0, text="<b>G</b>", showarrow=False,
                           font=dict(size=11, color=ORANGE))

        _dimension_vertical(fig, -0.78*b, -h/2, h/2, f"h = {h:g} mm")
        _dimension_horizontal(fig, -b/2, b/2, -0.72*h, f"b = {b:g} mm")
        _leader(fig, b/2-t/2, 0.18*h, 0.72*b, 0.20*h, f"t = {t:g} mm")

        caption = (
            "Para SHS/RHS los ejes centroidales pasan por el centro geométrico. "
            "La orientación del RHS importa: el eje asociado a la mayor dimensión suele entregar mayor I."
        )
        lim = max(h, b)*0.84
        fig.update_xaxes(range=[-lim, lim])
        fig.update_yaxes(range=[-lim, lim])

    elif shape == "CIRCLE":
        Do = float(p["Do_mm"]); Di = float(p["Di_mm"]); t = float(p["t_mm"])
        R = Do/2; r = Di/2
        fig.add_shape(type="circle", x0=-R, y0=-R, x1=R, y1=R,
                      line=dict(color=BLACK, width=2), fillcolor=BLACK)
        fig.add_shape(type="circle", x0=-r, y0=-r, x1=r, y1=r,
                      line=dict(color="white", width=1), fillcolor="white")
        _axis(fig, -0.62*Do, 0.62*Do, 0, 0, "x–x", 0.56*Do, 0.06*Do)
        _axis(fig, 0, 0, -0.62*Do, 0.62*Do, "y–y", 0.08*Do, 0.56*Do)
        fig.add_annotation(x=0, y=0, text="<b>G</b>", showarrow=False,
                           font=dict(size=11, color=ORANGE))
        _dimension_horizontal(fig, -R, R, -0.72*Do, f"Dₒ = {Do:g} mm")
        _leader(fig, 0.78*R, 0, 1.32*R, 0.18*Do, f"t = {t:g} mm")
        _leader(fig, r, 0, 1.28*R, -0.18*Do, f"Dᵢ = {Di:g} mm")

        caption = (
            "La sección circular tiene la misma geometría respecto de cualquier eje centroidal del plano: "
            "Iₓ = Iᵧ y Sₓ = Sᵧ."
        )
        lim = Do*0.84
        fig.update_xaxes(range=[-lim, lim])
        fig.update_yaxes(range=[-lim, lim])

    else:
        caption = "Esquema no disponible para esta sección."

    fig.update_xaxes(visible=False, scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False)
    fig.update_layout(
        height=560,
        margin=dict(l=25, r=25, t=30, b=70),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial, sans-serif", color="#262730"),
    )
    fig.add_annotation(
        x=0.5, y=-0.055, xref="paper", yref="paper",
        text=caption, showarrow=False,
        font=dict(size=11, color=GRAY),
        align="center",
    )
    return fig
