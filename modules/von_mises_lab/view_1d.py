from __future__ import annotations
import numpy as np
import plotly.graph_objects as go

ORANGE="#f28e1c"; DARK="#262730"; GREEN="#2c944d"; RED="#c44a3d"
BLUE="#2f6ec8"; PURPLE="#8a56cc"; GRAY="#7b8090"


def axial_bar_figure(sigma_x: float, Sy: float, force: float | None = None, area: float | None = None):
    """Esquema original GG DIMEC: barra axial + plano normal de corte."""
    fig=go.Figure()
    fig.update_xaxes(range=[-5.0,5.0],visible=False)
    fig.update_yaxes(range=[-3.0,3.0],visible=False,scaleanchor="x",scaleratio=1)
    fig.update_layout(
        height=420, margin=dict(l=8,r=8,t=42,b=8),
        title="Modelo físico unidimensional", showlegend=False,
        paper_bgcolor="white", plot_bgcolor="white"
    )

    # bar and grips
    fig.add_shape(type="rect",x0=-2.4,y0=-0.55,x1=2.4,y1=0.55,
                  line=dict(color=DARK,width=2.3),fillcolor="#f6f7f9")
    fig.add_shape(type="rect",x0=-3.0,y0=-0.90,x1=-2.4,y1=0.90,
                  line=dict(color=DARK,width=2.0),fillcolor="#e9ebef")
    fig.add_shape(type="rect",x0=2.4,y0=-0.90,x1=3.0,y1=0.90,
                  line=dict(color=DARK,width=2.0),fillcolor="#e9ebef")

    # section plane x = 0
    fig.add_shape(type="line",x0=0,y0=-0.82,x1=0,y1=0.82,
                  line=dict(color=ORANGE,width=3,dash="dash"))
    fig.add_annotation(x=0,y=1.18,text="Plano normal al eje x",showarrow=False,
                       font=dict(size=13,color=ORANGE),bgcolor="white")

    state_color = RED if abs(sigma_x) >= Sy else GREEN
    if sigma_x >= 0:
        fig.add_annotation(x=-4.25,y=0,ax=-3.0,ay=0,showarrow=True,
                           arrowhead=3,arrowwidth=3,arrowcolor=state_color,text="")
        fig.add_annotation(x=4.25,y=0,ax=3.0,ay=0,showarrow=True,
                           arrowhead=3,arrowwidth=3,arrowcolor=state_color,text="")
        load="TRACCIÓN"
    else:
        fig.add_annotation(x=-3.0,y=0,ax=-4.25,ay=0,showarrow=True,
                           arrowhead=3,arrowwidth=3,arrowcolor=state_color,text="")
        fig.add_annotation(x=3.0,y=0,ax=4.25,ay=0,showarrow=True,
                           arrowhead=3,arrowwidth=3,arrowcolor=state_color,text="")
        load="COMPRESIÓN"

    fig.add_annotation(x=0,y=-1.22,text=f"<b>{load}</b>",showarrow=False,
                       font=dict(size=14,color=state_color))
    fig.add_annotation(x=0,y=-1.68,text=f"σ<sub>x</sub> = {sigma_x:.5g}",
                       showarrow=False,font=dict(size=14,color=state_color))
    if force is not None and area is not None:
        fig.add_annotation(x=0,y=-2.12,text=f"σ<sub>x</sub> = F/A = {force:.5g}/{area:.5g}",
                           showarrow=False,font=dict(size=12,color=DARK))
    return fig


def uniaxial_flow_figure(sigma_x: float, Sy: float):
    """Secuencia visual: carga → esfuerzo → Von Mises → comparación."""
    vm=abs(sigma_x)
    n=np.inf if vm==0 else Sy/vm
    color=GREEN if vm < Sy else ORANGE if np.isclose(vm,Sy) else RED
    fig=go.Figure()
    fig.update_xaxes(range=[0,10],visible=False)
    fig.update_yaxes(range=[0,4],visible=False)
    fig.update_layout(height=310,margin=dict(l=5,r=5,t=38,b=5),
                      title="Ruta de análisis 1D",showlegend=False,
                      paper_bgcolor="white",plot_bgcolor="white")

    boxes=[
        (0.5,1.25,2.2,2.6,"1 · CARGA\\naxial"),
        (3.0,1.25,4.7,2.6,"2 · ESFUERZO\\nσx"),
        (5.5,1.25,7.2,2.6,"3 · VON MISES\\nσVM = |σx|"),
        (8.0,1.25,9.5,2.6,"4 · DISEÑO\\ncomparar con Sy"),
    ]
    for x0,y0,x1,y1,txt in boxes:
        fig.add_shape(type="rect",x0=x0,y0=y0,x1=x1,y1=y1,
                      line=dict(color=DARK,width=2),
                      fillcolor="#fff8ef" if "VON" in txt else "#f8f9fb")
        fig.add_annotation(x=(x0+x1)/2,y=(y0+y1)/2,text=txt.replace("\n","<br>"),
                           showarrow=False,font=dict(size=13,color=DARK))
    for x0,x1 in [(2.2,3.0),(4.7,5.5),(7.2,8.0)]:
        fig.add_annotation(x=x1,y=1.925,ax=x0,ay=1.925,showarrow=True,
                           arrowhead=3,arrowwidth=2.2,arrowcolor=GRAY,text="")
    fig.add_annotation(x=8.75,y=0.60,
                       text=f"n = {'∞' if np.isinf(n) else f'{n:.4g}'}",
                       showarrow=False,font=dict(size=15,color=color),
                       bgcolor="white",bordercolor=color,borderwidth=1)
    return fig


def yield_axis_figure(sigma_x: float, Sy: float):
    span=max(1.35*Sy,1.15*abs(sigma_x),1.0)
    fig=go.Figure()
    fig.add_shape(type="rect",x0=-Sy,x1=Sy,y0=-0.28,y1=0.28,
                  line=dict(color=GREEN,width=1.8),
                  fillcolor="rgba(44,148,77,0.13)")
    fig.add_vline(x=-Sy,line=dict(color=ORANGE,width=2))
    fig.add_vline(x=Sy,line=dict(color=ORANGE,width=2))
    fig.add_trace(go.Scatter(
        x=[sigma_x],y=[0],mode="markers+text",
        marker=dict(size=18,color=RED if abs(sigma_x)>Sy else BLUE,
                    line=dict(color="white",width=2)),
        text=["Estado de trabajo"],textposition="top center",
        hovertemplate="σx = %{x:.5g}<extra></extra>"
    ))
    fig.add_annotation(x=-Sy,y=-0.46,text="−S<sub>y</sub>",showarrow=False,
                       font=dict(color=ORANGE,size=14))
    fig.add_annotation(x=Sy,y=-0.46,text="+S<sub>y</sub>",showarrow=False,
                       font=dict(color=ORANGE,size=14))
    fig.update_xaxes(range=[-span,span],title="Esfuerzo normal σx")
    fig.update_yaxes(range=[-0.7,0.7],visible=False)
    fig.update_layout(height=300,margin=dict(l=20,r=20,t=35,b=45),
                      title="Dominio elástico unidimensional",showlegend=False,
                      paper_bgcolor="white",plot_bgcolor="white")
    return fig
