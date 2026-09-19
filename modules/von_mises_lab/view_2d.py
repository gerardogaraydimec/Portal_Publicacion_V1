from __future__ import annotations
import numpy as np
import plotly.graph_objects as go

ORANGE="#f28e1c"; DARK="#262730"; GREEN="#2c944d"; RED="#c44a3d"
BLUE="#2f6ec8"; PURPLE="#8a56cc"; GRAY="#7b8090"


def stress_element_2d_figure(sigma_x: float, sigma_y: float, tau_xy: float):
    fig=go.Figure()
    fig.update_xaxes(range=[-2.7,2.7],visible=False)
    fig.update_yaxes(range=[-2.7,2.7],visible=False,scaleanchor="x",scaleratio=1)
    fig.update_layout(height=420,margin=dict(l=8,r=8,t=42,b=8),
                      title="Plano xy · estado de esfuerzos conocido",
                      showlegend=False,paper_bgcolor="white",plot_bgcolor="white")

    fig.add_shape(type="rect",x0=-1,y0=-1,x1=1,y1=1,
                  line=dict(color=DARK,width=2.4),fillcolor="#f8f9fb")

    sx_color=RED if sigma_x>=0 else BLUE
    sy_color=RED if sigma_y>=0 else BLUE
    t_color=PURPLE

    # normals x
    if sigma_x>=0:
        fig.add_annotation(x=2.0,y=0.35,ax=1.0,ay=0.35,showarrow=True,arrowhead=3,arrowwidth=3,arrowcolor=sx_color,text="")
        fig.add_annotation(x=-2.0,y=-0.35,ax=-1.0,ay=-0.35,showarrow=True,arrowhead=3,arrowwidth=3,arrowcolor=sx_color,text="")
    else:
        fig.add_annotation(x=1.0,y=0.35,ax=2.0,ay=0.35,showarrow=True,arrowhead=3,arrowwidth=3,arrowcolor=sx_color,text="")
        fig.add_annotation(x=-1.0,y=-0.35,ax=-2.0,ay=-0.35,showarrow=True,arrowhead=3,arrowwidth=3,arrowcolor=sx_color,text="")

    # normals y
    if sigma_y>=0:
        fig.add_annotation(x=0.35,y=2.0,ax=0.35,ay=1.0,showarrow=True,arrowhead=3,arrowwidth=3,arrowcolor=sy_color,text="")
        fig.add_annotation(x=-0.35,y=-2.0,ax=-0.35,ay=-1.0,showarrow=True,arrowhead=3,arrowwidth=3,arrowcolor=sy_color,text="")
    else:
        fig.add_annotation(x=0.35,y=1.0,ax=0.35,ay=2.0,showarrow=True,arrowhead=3,arrowwidth=3,arrowcolor=sy_color,text="")
        fig.add_annotation(x=-0.35,y=-1.0,ax=-0.35,ay=-2.0,showarrow=True,arrowhead=3,arrowwidth=3,arrowcolor=sy_color,text="")

    # shears
    sign=1 if tau_xy>=0 else -1
    fig.add_annotation(x=0.68*sign,y=1.0,ax=-0.68*sign,ay=1.0,showarrow=True,arrowhead=3,arrowwidth=3,arrowcolor=t_color,text="")
    fig.add_annotation(x=-0.68*sign,y=-1.0,ax=0.68*sign,ay=-1.0,showarrow=True,arrowhead=3,arrowwidth=3,arrowcolor=t_color,text="")
    fig.add_annotation(x=1.0,y=-0.68*sign,ax=1.0,ay=0.68*sign,showarrow=True,arrowhead=3,arrowwidth=3,arrowcolor=t_color,text="")
    fig.add_annotation(x=-1.0,y=0.68*sign,ax=-1.0,ay=-0.68*sign,showarrow=True,arrowhead=3,arrowwidth=3,arrowcolor=t_color,text="")

    fig.add_annotation(x=0,y=2.35,text=f"σ<sub>y</sub> = {sigma_y:.4g}",showarrow=False,font=dict(size=13,color=sy_color))
    fig.add_annotation(x=2.28,y=0,text=f"σ<sub>x</sub> = {sigma_x:.4g}",showarrow=False,textangle=90,font=dict(size=13,color=sx_color))
    fig.add_annotation(x=0,y=-2.35,text=f"τ<sub>xy</sub> = {tau_xy:.4g}",showarrow=False,font=dict(size=13,color=t_color))
    return fig


def principal_element_2d_figure(sigma1: float, sigma2: float, theta_deg: float):
    th=np.deg2rad(theta_deg)
    R=np.array([[np.cos(th),-np.sin(th)],[np.sin(th),np.cos(th)]])
    corners=np.array([[-1,-1],[1,-1],[1,1],[-1,1],[-1,-1]],dtype=float)
    rc=corners@R.T

    fig=go.Figure()
    fig.add_trace(go.Scatter(x=rc[:,0],y=rc[:,1],mode="lines",
                             line=dict(color=DARK,width=2.5),
                             fill="toself",fillcolor="#f8f9fb",hoverinfo="skip"))

    e1=np.array([np.cos(th),np.sin(th)])
    e2=np.array([-np.sin(th),np.cos(th)])
    c1=RED if sigma1>=0 else BLUE
    c2=RED if sigma2>=0 else BLUE

    def arr(start,end,color):
        fig.add_annotation(x=end[0],y=end[1],ax=start[0],ay=start[1],
                           xref="x",yref="y",axref="x",ayref="y",
                           showarrow=True,arrowhead=3,arrowwidth=3,arrowcolor=color,text="")

    # arrows on positive and negative principal faces
    arr(1.0*e1,2.0*e1 if sigma1>=0 else 0.35*e1,c1)
    arr(-1.0*e1,-2.0*e1 if sigma1>=0 else -0.35*e1,c1)
    arr(1.0*e2,2.0*e2 if sigma2>=0 else 0.35*e2,c2)
    arr(-1.0*e2,-2.0*e2 if sigma2>=0 else -0.35*e2,c2)

    fig.add_annotation(x=2.15*e1[0],y=2.15*e1[1],text=f"σ₁ = {sigma1:.4g}",
                       showarrow=False,font=dict(size=13,color=c1),bgcolor="white")
    fig.add_annotation(x=2.15*e2[0],y=2.15*e2[1],text=f"σ₂ = {sigma2:.4g}",
                       showarrow=False,font=dict(size=13,color=c2),bgcolor="white")
    fig.add_annotation(x=-2.1,y=2.0,text=f"θp = {theta_deg:.3g}°",showarrow=False,
                       font=dict(size=13,color=ORANGE),bgcolor="white")
    fig.add_annotation(x=0,y=-2.25,text="En los planos principales: τ = 0",
                       showarrow=False,font=dict(size=13,color=GREEN),bgcolor="white")

    fig.update_xaxes(range=[-2.6,2.6],visible=False)
    fig.update_yaxes(range=[-2.6,2.6],visible=False,scaleanchor="x",scaleratio=1)
    fig.update_layout(height=420,margin=dict(l=8,r=8,t=42,b=8),
                      title="Planos principales · estado transformado",
                      showlegend=False,paper_bgcolor="white",plot_bgcolor="white")
    return fig


def mohr_circle_figure(sigma_x: float, sigma_y: float, tau_xy: float,
                       center: float, radius: float, sigma1: float, sigma2: float):
    th=np.linspace(0,2*np.pi,361)
    x=center+radius*np.cos(th); y=radius*np.sin(th)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=x,y=y,mode="lines",name="Círculo de Mohr",
                             line=dict(color=ORANGE,width=3),
                             fill="toself",fillcolor="rgba(242,142,28,0.09)"))
    fig.add_trace(go.Scatter(x=[sigma_x,sigma_y],y=[tau_xy,-tau_xy],
                             mode="markers+text",text=["A","B"],textposition="top center",
                             marker=dict(size=12,color=BLUE),name="Estado xy"))
    fig.add_trace(go.Scatter(x=[sigma1,sigma2],y=[0,0],
                             mode="markers+text",text=["σ1","σ2"],textposition="top center",
                             marker=dict(size=12,color=RED),name="Principales"))
    fig.add_hline(y=0,line=dict(color="#d7dbe2",width=1))
    span=max(abs(sigma1),abs(sigma2),abs(center)+radius,1.0)
    yr=max(radius*1.25,1.0)
    fig.update_xaxes(range=[-1.15*span,1.15*span],title="Esfuerzo normal σ")
    fig.update_yaxes(range=[-yr,yr],title="Esfuerzo cortante τ",scaleanchor="x",scaleratio=1)
    fig.update_layout(height=470,margin=dict(l=18,r=18,t=45,b=18),
                      title="Transformación mediante el círculo de Mohr",
                      paper_bgcolor="white",plot_bgcolor="white",
                      legend=dict(orientation="h",yanchor="bottom",y=1.02,x=0.01))
    return fig


def yield_plane_vm_figure(sigma1: float, sigma2: float, Sy: float,
                          n_vm: float, show_tresca: bool=True):
    lim=max(1.32*Sy,1.18*max(abs(sigma1),abs(sigma2),1.0))
    xs=np.linspace(-lim,lim,260); ys=np.linspace(-lim,lim,260)
    X,Y=np.meshgrid(xs,ys)
    Z=(X**2-X*Y+Y**2)/(Sy**2)

    fig=go.Figure()
    fig.add_trace(go.Contour(
        x=xs,y=ys,z=Z,
        contours=dict(start=0,end=2,size=1,coloring="fill"),
        colorscale=[
            [0.0,"rgba(44,148,77,0.17)"],
            [0.499,"rgba(44,148,77,0.17)"],
            [0.500,"rgba(196,74,61,0.10)"],
            [1.0,"rgba(196,74,61,0.10)"],
        ],
        line=dict(width=0),showscale=False,hoverinfo="skip"
    ))
    fig.add_trace(go.Contour(
        x=xs,y=ys,z=Z,
        contours=dict(start=1,end=1,size=1,coloring="lines"),
        line=dict(color=ORANGE,width=3),showscale=False,
        name="Von Mises",hovertemplate="Frontera Von Mises<extra></extra>"
    ))

    if show_tresca:
        vx=[Sy,Sy,0,-Sy,-Sy,0,Sy]
        vy=[0,Sy,Sy,0,-Sy,-Sy,0]
        fig.add_trace(go.Scatter(x=vx,y=vy,mode="lines",name="Tresca",
                                 line=dict(color=PURPLE,width=2.3,dash="dash")))

    fig.add_trace(go.Scatter(x=[0,sigma1],y=[0,sigma2],mode="lines",
                             line=dict(color=GRAY,width=1.6,dash="dot"),
                             name="Línea de carga"))

    if np.isfinite(n_vm) and n_vm>0:
        xb=n_vm*sigma1; yb=n_vm*sigma2
        fig.add_trace(go.Scatter(x=[xb],y=[yb],mode="markers+text",
                                 text=["Intersección con fluencia"],
                                 textposition="bottom center",
                                 marker=dict(size=11,color=ORANGE,
                                             symbol="diamond",
                                             line=dict(color="white",width=1.5)),
                                 name="Límite proporcional"))
        fig.add_trace(go.Scatter(x=[sigma1,xb],y=[sigma2,yb],mode="lines",
                                 line=dict(color=ORANGE,width=2),
                                 name="Margen hasta fluencia"))

    inside=(sigma1**2-sigma1*sigma2+sigma2**2)<=Sy**2
    fig.add_trace(go.Scatter(x=[sigma1],y=[sigma2],mode="markers+text",
                             text=["Estado de trabajo"],textposition="top center",
                             marker=dict(size=16,color=BLUE if inside else RED,
                                         line=dict(color="white",width=2)),
                             name="Punto de operación"))

    fig.add_hline(y=0,line=dict(color="#d7dbe2",width=1))
    fig.add_vline(x=0,line=dict(color="#d7dbe2",width=1))
    fig.update_xaxes(range=[-lim,lim],title="Esfuerzo principal σ1")
    fig.update_yaxes(range=[-lim,lim],title="Esfuerzo principal σ2",scaleanchor="x",scaleratio=1)
    fig.update_layout(height=540,margin=dict(l=18,r=18,t=45,b=18),
                      title="Plano de fluencia · Von Mises y Tresca",
                      paper_bgcolor="white",plot_bgcolor="white",
                      legend=dict(orientation="h",yanchor="bottom",y=1.02,x=0.01))
    return fig
