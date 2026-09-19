from __future__ import annotations
import numpy as np
import plotly.graph_objects as go

ORANGE="#f28e1c"; DARK="#262730"; GREEN="#2c944d"; RED="#c44a3d"
BLUE="#2f6ec8"; PURPLE="#8a56cc"; GRAY="#7b8090"


EA=np.array([1.0,-1.0,0.0])/np.sqrt(2.0)
EB=np.array([1.0,1.0,-2.0])/np.sqrt(6.0)
EH=np.array([1.0,1.0,1.0])/np.sqrt(3.0)


def von_mises_cylinder_figure(
    sigma1: float, sigma2: float, sigma3: float, Sy: float,
    shifted_principal: tuple[float,float,float] | None = None
):
    p=np.array([sigma1,sigma2,sigma3],dtype=float)
    ph=np.mean(p)*np.ones(3)
    R=np.sqrt(2.0/3.0)*Sy

    h0=float(p@EH)
    hmax=max(2.2*Sy,abs(h0)+1.4*Sy)
    if shifted_principal is not None:
        ps=np.array(shifted_principal,dtype=float)
        hmax=max(hmax,abs(float(ps@EH))+1.2*Sy)

    theta=np.linspace(0,2*np.pi,64)
    h=np.linspace(-hmax,hmax,42)
    TH,H=np.meshgrid(theta,h)
    X=np.zeros_like(TH); Y=np.zeros_like(TH); Z=np.zeros_like(TH)
    for i in range(H.shape[0]):
        for j in range(H.shape[1]):
            q=H[i,j]*EH + R*(np.cos(TH[i,j])*EA + np.sin(TH[i,j])*EB)
            X[i,j],Y[i,j],Z[i,j]=q

    fig=go.Figure()
    fig.add_trace(go.Surface(
        x=X,y=Y,z=Z,opacity=0.18,showscale=False,hoverinfo="skip",
        colorscale=[[0,"#f28e1c"],[1,"#f28e1c"]],name="Von Mises"
    ))
    axis=np.linspace(-hmax,hmax,120)
    axis_pts=np.outer(axis,EH)
    fig.add_trace(go.Scatter3d(
        x=axis_pts[:,0],y=axis_pts[:,1],z=axis_pts[:,2],
        mode="lines",line=dict(color=GRAY,width=5,dash="dash"),
        name="Eje hidrostático"
    ))
    fig.add_trace(go.Scatter3d(
        x=[0,ph[0]],y=[0,ph[1]],z=[0,ph[2]],
        mode="lines+markers",line=dict(color=BLUE,width=6),
        marker=dict(size=4,color=BLUE),name="Componente hidrostática"
    ))
    fig.add_trace(go.Scatter3d(
        x=[ph[0],p[0]],y=[ph[1],p[1]],z=[ph[2],p[2]],
        mode="lines+markers",line=dict(color=PURPLE,width=7),
        marker=dict(size=4,color=PURPLE),name="Componente desviadora"
    ))
    fig.add_trace(go.Scatter3d(
        x=[p[0]],y=[p[1]],z=[p[2]],mode="markers+text",
        text=["Estado actual"],textposition="top center",
        marker=dict(size=7,color=RED if np.linalg.norm(p-ph)>R else GREEN,
                    line=dict(color="white",width=1.5)),
        name="Estado de trabajo"
    ))

    if shifted_principal is not None:
        ps=np.array(shifted_principal,dtype=float)
        fig.add_trace(go.Scatter3d(
            x=[p[0],ps[0]],y=[p[1],ps[1]],z=[p[2],ps[2]],
            mode="lines+markers+text",
            text=["","Desplazado hidrostáticamente"],textposition="top center",
            line=dict(color=ORANGE,width=5,dash="dot"),
            marker=dict(size=6,color=ORANGE),
            name="Cambio hidrostático"
        ))

    fig.update_layout(
        height=650,margin=dict(l=0,r=0,t=45,b=0),
        title="Espacio principal · cilindro de fluencia de Von Mises",
        scene=dict(
            xaxis_title="σ1",yaxis_title="σ2",zaxis_title="σ3",
            aspectmode="cube",
            bgcolor="white",
            camera=dict(eye=dict(x=1.55,y=1.55,z=1.25))
        ),
        legend=dict(orientation="h",yanchor="bottom",y=1.02,x=0.0),
        paper_bgcolor="white"
    )
    return fig


def pi_plane_figure(sigma1: float, sigma2: float, sigma3: float, Sy: float):
    p=np.array([sigma1,sigma2,sigma3],dtype=float)
    s=p-np.mean(p)
    x=float(s@EA); y=float(s@EB)
    R=np.sqrt(2.0/3.0)*Sy

    th=np.linspace(0,2*np.pi,361)
    fig=go.Figure()
    fig.add_trace(go.Scatter(
        x=R*np.cos(th),y=R*np.sin(th),mode="lines",
        line=dict(color=ORANGE,width=3),name="Von Mises"
    ))

    # Tresca vertices: permutations of (2,-1,-1)*Sy/3 and their three cyclic directions
    principal_vertices=np.array([
        [ 2,-1,-1],
        [ 1, 1,-2],
        [-1, 2,-1],
        [-2, 1, 1],
        [-1,-1, 2],
        [ 1,-2, 1],
        [ 2,-1,-1],
    ],dtype=float)*(Sy/3.0)
    vx=principal_vertices@EA
    vy=principal_vertices@EB
    fig.add_trace(go.Scatter(
        x=vx,y=vy,mode="lines",
        line=dict(color=PURPLE,width=2.4,dash="dash"),
        name="Tresca"
    ))

    fig.add_trace(go.Scatter(
        x=[0,x],y=[0,y],mode="lines",
        line=dict(color=GRAY,width=1.5,dash="dot"),
        name="Parte desviadora"
    ))
    inside=(x*x+y*y)<=R*R
    fig.add_trace(go.Scatter(
        x=[x],y=[y],mode="markers+text",
        text=["Estado actual"],textposition="top center",
        marker=dict(size=15,color=GREEN if inside else RED,
                    line=dict(color="white",width=2)),
        name="Punto de operación"
    ))
    lim=max(1.25*R,1.2*abs(x),1.2*abs(y),1.0)
    fig.add_hline(y=0,line=dict(color="#d7dbe2",width=1))
    fig.add_vline(x=0,line=dict(color="#d7dbe2",width=1))
    fig.update_xaxes(range=[-lim,lim],title="Coordenada desviadora a")
    fig.update_yaxes(range=[-lim,lim],title="Coordenada desviadora b",
                     scaleanchor="x",scaleratio=1)
    fig.update_layout(
        height=520,margin=dict(l=18,r=18,t=45,b=18),
        title="Plano π · corte perpendicular al eje hidrostático",
        paper_bgcolor="white",plot_bgcolor="white",
        legend=dict(orientation="h",yanchor="bottom",y=1.02,x=0.01)
    )
    return fig
