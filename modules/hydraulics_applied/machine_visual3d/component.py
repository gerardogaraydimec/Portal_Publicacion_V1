from __future__ import annotations

from itertools import count

import math
from typing import Iterable

import numpy as np
import plotly.graph_objects as go

_PLOTLY_SEQ = count(1)
import streamlit as st

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


def _rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"rgb({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)})"


def _cuboid(fig: go.Figure, center, size, color, name="", opacity=1.0, showlegend=False):
    cx, cy, cz = center
    lx, ly, lz = size
    x = [cx-lx/2,cx+lx/2,cx+lx/2,cx-lx/2,cx-lx/2,cx+lx/2,cx+lx/2,cx-lx/2]
    y = [cy-ly/2,cy-ly/2,cy+ly/2,cy+ly/2,cy-ly/2,cy-ly/2,cy+ly/2,cy+ly/2]
    z = [cz-lz/2,cz-lz/2,cz-lz/2,cz-lz/2,cz+lz/2,cz+lz/2,cz+lz/2,cz+lz/2]
    i = [0,0,0,1,1,2,4,4,5,3,2,6]
    j = [1,2,4,2,5,3,5,6,6,7,3,7]
    k = [2,4,1,5,2,7,6,5,1,4,7,6]
    fig.add_trace(go.Mesh3d(x=x,y=y,z=z,i=i,j=j,k=k,color=color,opacity=opacity,
                            name=name,showlegend=showlegend,hovertemplate=(name+"<extra></extra>") if name else None,
                            flatshading=True))


def _rotate_z(points: Iterable[tuple[float,float,float]], angle: float, origin=(0.0,0.0,0.0)):
    ox, oy, oz = origin
    c, s = math.cos(angle), math.sin(angle)
    out=[]
    for x,y,z in points:
        dx,dy=x-ox,y-oy
        out.append((ox+c*dx-s*dy, oy+s*dx+c*dy, z))
    return out


def _cuboid_rot_z(fig, center, size, angle, color, name="", opacity=1.0, origin=None):
    cx,cy,cz=center; lx,ly,lz=size
    pts=[
        (cx-lx/2,cy-ly/2,cz-lz/2),(cx+lx/2,cy-ly/2,cz-lz/2),(cx+lx/2,cy+ly/2,cz-lz/2),(cx-lx/2,cy+ly/2,cz-lz/2),
        (cx-lx/2,cy-ly/2,cz+lz/2),(cx+lx/2,cy-ly/2,cz+lz/2),(cx+lx/2,cy+ly/2,cz+lz/2),(cx-lx/2,cy+ly/2,cz+lz/2),
    ]
    pts=_rotate_z(pts,angle,origin or (cx,cy,cz)); x=[p[0] for p in pts];y=[p[1] for p in pts];z=[p[2] for p in pts]
    i=[0,0,0,1,1,2,4,4,5,3,2,6];j=[1,2,4,2,5,3,5,6,6,7,3,7];k=[2,4,1,5,2,7,6,5,1,4,7,6]
    fig.add_trace(go.Mesh3d(x=x,y=y,z=z,i=i,j=j,k=k,color=color,opacity=opacity,name=name,showlegend=False,flatshading=True,
                            hovertemplate=(name+"<extra></extra>") if name else None))



def _cuboid_rot_y(fig, center, size, angle, color, name="", origin=None, opacity=1.0):
    cx,cy,cz=center; lx,ly,lz=size
    ox,oy,oz=origin or center
    pts=[
        (cx-lx/2,cy-ly/2,cz-lz/2),(cx+lx/2,cy-ly/2,cz-lz/2),(cx+lx/2,cy+ly/2,cz-lz/2),(cx-lx/2,cy+ly/2,cz-lz/2),
        (cx-lx/2,cy-ly/2,cz+lz/2),(cx+lx/2,cy-ly/2,cz+lz/2),(cx+lx/2,cy+ly/2,cz+lz/2),(cx-lx/2,cy+ly/2,cz+lz/2),
    ]
    c,s=math.cos(angle),math.sin(angle); out=[]
    for x,y,z in pts:
        dx=x-ox;dz=z-oz
        out.append((ox+c*dx+s*dz,y,oz-s*dx+c*dz))
    x=[p[0] for p in out];y=[p[1] for p in out];z=[p[2] for p in out]
    i=[0,0,0,1,1,2,4,4,5,3,2,6];j=[1,2,4,2,5,3,5,6,6,7,3,7];k=[2,4,1,5,2,7,6,5,1,4,7,6]
    fig.add_trace(go.Mesh3d(x=x,y=y,z=z,i=i,j=j,k=k,color=color,opacity=opacity,name=name,showlegend=False,flatshading=True,hovertemplate=(name+"<extra></extra>") if name else None))

def _cylinder(fig: go.Figure, p0, p1, radius, color, name="", opacity=1.0, n=20, showlegend=False):
    p0=np.asarray(p0,float); p1=np.asarray(p1,float); axis=p1-p0; L=np.linalg.norm(axis)
    if L < 1e-9: return
    w=axis/L
    a=np.array([1.,0.,0.]) if abs(w[0])<.9 else np.array([0.,1.,0.])
    u=np.cross(w,a);u=u/np.linalg.norm(u);v=np.cross(w,u)
    th=np.linspace(0,2*np.pi,n)
    ring0=np.array([p0+radius*(math.cos(t)*u+math.sin(t)*v) for t in th])
    ring1=np.array([p1+radius*(math.cos(t)*u+math.sin(t)*v) for t in th])
    x=np.r_[ring0[:,0],ring1[:,0]];y=np.r_[ring0[:,1],ring1[:,1]];z=np.r_[ring0[:,2],ring1[:,2]]
    ii=[];jj=[];kk=[]
    m=len(th)
    for q in range(m-1):
        ii += [q,q]; jj += [q+1,m+q+1]; kk += [m+q,m+q]
    fig.add_trace(go.Mesh3d(x=x,y=y,z=z,i=ii,j=jj,k=kk,color=color,opacity=opacity,name=name,showlegend=showlegend,
                            flatshading=True,hovertemplate=(name+"<extra></extra>") if name else None))


def _wheel(fig, x, y, z, r=.62, width=.42, steer=0.0, name="Rueda"):
    # eje principal en Y; en dirección se rota el eje en planta
    axis=np.array([math.sin(steer), math.cos(steer), 0.0])
    p0=np.array([x,y,z])-axis*width/2
    p1=np.array([x,y,z])+axis*width/2
    _cylinder(fig,p0,p1,r,DARK,name,1.0,n=24)
    _cylinder(fig,p0-axis*.015,p1+axis*.015,r*.42,METAL,"Maza",1.0,n=20)


def _line(fig, pts, color, name, width=6, dash=None, showlegend=False):
    x=[p[0] for p in pts];y=[p[1] for p in pts];z=[p[2] for p in pts]
    fig.add_trace(go.Scatter3d(x=x,y=y,z=z,mode="lines",name=name,showlegend=showlegend,
                               line=dict(color=color,width=width,dash=dash or "solid"),hovertemplate=name+"<extra></extra>"))


def _label(fig, x,y,z,text,color="#f4eee4",size=11):
    fig.add_trace(go.Scatter3d(x=[x],y=[y],z=[z],mode="text",text=[text],showlegend=False,
                               textfont=dict(color=color,size=size),hoverinfo="skip"))


def _hydraulic_lines(fig, machine: str, subsystem: str, state: str):
    """Rutas físicas simplificadas. No representan routing OEM; muestran asociación espacial."""
    if machine=="Cargador frontal":
        base=[(-1.1,-.55,.55),(-.15,-.55,.55),(.55,-.55,.72)]
        _line(fig,base,SUCTION,"Succión",5,showlegend=True)
        if subsystem=="Levante de brazos LS":
            if state=="Raise":
                _line(fig,[(.55,-.48,.72),(1.25,-.70,.92),(2.05,-.72,1.18)],PRESSURE,"Presión",7,showlegend=True)
                _line(fig,[(2.05,.72,1.18),(1.25,.70,.72),(.55,.50,.62)],RETURN,"Retorno",6,showlegend=True)
            elif state=="Lower":
                _line(fig,[(.55,.48,.72),(1.25,.70,.82),(2.05,.72,1.18)],PRESSURE,"Presión",7,showlegend=True)
                _line(fig,[(2.05,-.72,1.18),(1.25,-.70,.74),(.55,-.50,.62)],RETURN,"Retorno",6,showlegend=True)
            elif state=="Float":
                _line(fig,[(2.05,-.72,1.18),(1.25,-.70,.74),(.55,-.5,.62),(.0,-.5,.4)],RETURN,"A/B a tanque",6,showlegend=True)
                _line(fig,[(2.05,.72,1.18),(1.25,.70,.74),(.55,.5,.62),(.0,.5,.4)],RETURN,"A/B a tanque",6)
            _line(fig,[(1.5,.0,1.05),(.9,.0,1.55),(.0,.0,1.55),(-.8,.0,1.2)],PILOT,"LS",4,dash="dash",showlegend=True)
        elif subsystem=="Inclinación de balde":
            col=PRESSURE if state!="Hold" else INACTIVE
            _line(fig,[(.55,-.2,.72),(1.8,-.15,1.35),(2.9,-.1,1.55)],col,"Línea tilt",6,showlegend=True)
            _line(fig,[(2.9,.1,1.55),(1.8,.15,1.2),(.55,.2,.62)],RETURN,"Retorno",5,showlegend=True)
        else:
            _line(fig,[(-.1,-.5,.7),(-.7,-.75,.55),(-1.55,-.8,.45)],PRESSURE,"Dirección",6,showlegend=True)
            _line(fig,[(-1.55,.8,.45),(-.7,.75,.45),(-.1,.5,.6)],RETURN,"Retorno",5,showlegend=True)
            _line(fig,[(-.4,0,.95),(-1.1,0,1.2)],PILOT,"LS",4,dash="dash",showlegend=True)
    elif machine=="Camión minero":
        _line(fig,[(-1.1,-.6,.52),(-.3,-.6,.55),(.4,-.6,.7)],SUCTION,"Succión",5,showlegend=True)
        if subsystem=="Levante de tolva":
            col=PRESSURE if state in ("Raise","Lower") else INACTIVE
            _line(fig,[(.4,-.65,.7),(1.4,-.75,.9),(2.2,-.78,1.2)],col,"Trabajo A",7,showlegend=True)
            _line(fig,[(2.2,.78,1.2),(1.4,.75,.75),(.4,.65,.62)],RETURN if state!="Hold" else INACTIVE,"Trabajo B",6,showlegend=True)
            _line(fig,[(1.3,0,1.0),(.7,0,1.5),(-.2,0,1.55),(-1.0,0,1.2)],PILOT,"Pilotaje / LS",4,dash="dash",showlegend=True)
        elif subsystem=="Dirección hidrostática":
            _line(fig,[(-.5,-.3,.65),(-1.3,-.6,.52),(-2.2,-.7,.42)],PRESSURE,"L/R",6,showlegend=True)
            _line(fig,[(-2.2,.7,.42),(-1.3,.6,.48),(-.5,.3,.58)],RETURN,"Retorno",5,showlegend=True)
            _line(fig,[(-.5,0,.9),(-1.35,0,1.2)],PILOT,"LS",4,dash="dash",showlegend=True)
        else:
            _line(fig,[(.2,-.55,.75),(.9,-.65,.95),(1.65,-.75,.55)],PRESSURE,"Circuito de freno",6,showlegend=True)
    else:
        _line(fig,[(-2.5,-.45,.2),(-1.7,-.45,.3),(-.7,-.45,.45),(.2,-.45,.65)],SUCTION,"Succión",5,showlegend=True)
        _line(fig,[(.2,-.45,.65),(1.2,-.45,.75),(2.1,-.45,1.0)],PRESSURE,"Presión",7,showlegend=True)
        _line(fig,[(2.1,.45,1.0),(1.2,.45,.55),(.2,.45,.45),(-2.5,.45,.2)],RETURN,"Retorno",6,showlegend=True)


def _truck(fig, data):
    state=data.get("state",""); subsystem=data.get("subsystem",""); amp=float(data.get("visual_amp",1.0))
    _cuboid(fig,(0,0,0),(6.6,2.5,.45),YELLOW,"Chasis")
    _cuboid(fig,(-2.35,0,.85),(1.5,2.15,1.65),DARK2,"Cabina")
    _cuboid(fig,(-2.45,0,1.15),(1.1,1.75,.62),GLASS,"Parabrisas",.72)
    steer=0.0
    if subsystem=="Dirección hidrostática": steer={"Izquierda":-.28,"Derecha":.28}.get(state,0.0)*amp
    for x in [-2.1,.95,2.15]:
        for y in [-1.24,1.24]: _wheel(fig,x,y,-.45,.75 if x<0 else .82,.42,steer if x<0 else 0.0)
    # Tolva como cuerpo realista simplificado; pivote en sector posterior
    angle={"Raise":.58,"Hold":.45,"Float":.18,"Lower":.10}.get(state,.10) if subsystem=="Levante de tolva" else .10
    angle*=min(1.35,amp)
    pivot=(2.55,0,.35)
    cx=1.15; cz=.95
    # cuerpo con piso y laterales rotados en plano XZ usando cubo rotado alrededor eje Y -> helper manual
    def cuboid_rot_y(center,size,a,color,name):
        cx,cy,cz=center; lx,ly,lz=size
        pts=[]
        for sx in (-1,1):
            for sy in (-1,1):
                for sz in (-1,1): pts.append([cx+sx*lx/2,cy+sy*ly/2,cz+sz*lz/2])
        # rotate around pivot y-axis
        c,s=math.cos(a),math.sin(a); out=[]
        for x,y,z in pts:
            dx=x-pivot[0];dz=z-pivot[2]
            out.append((pivot[0]+c*dx+s*dz,y,pivot[2]-s*dx+c*dz))
        # index order from loops not standard, define convex hull-ish mesh faces by scipy unavailable; use plotly mesh alphahull=0
        fig.add_trace(go.Mesh3d(x=[p[0] for p in out],y=[p[1] for p in out],z=[p[2] for p in out],color=color,opacity=1,
                                alphahull=0,name=name,showlegend=False,flatshading=True,hovertemplate=name+"<extra></extra>"))
    cuboid_rot_y((1.15,0,.95),(4.2,2.35,.28),angle,YELLOW,"Piso tolva")
    cuboid_rot_y((1.05,-1.1,1.48),(4.15,.12,1.2),angle,YELLOW,"Lateral tolva")
    cuboid_rot_y((1.05,1.1,1.48),(4.15,.12,1.2),angle,YELLOW,"Lateral tolva")
    cuboid_rot_y((-.85,0,1.5),(.18,2.3,1.3),angle,YELLOW,"Frente tolva")
    if subsystem=="Levante de tolva":
        _cylinder(fig,(-.2,-.72,.25),(1.35,-.72,1.1+angle),.12,METAL,"Cilindro levante")
        _cylinder(fig,(-.2,.72,.25),(1.35,.72,1.1+angle),.12,METAL,"Cilindro levante")
        _cylinder(fig,(1.0,-.72,.93),(1.55,-.72,1.25+angle),.055,ROD,"Vástago")
        _cylinder(fig,(1.0,.72,.93),(1.55,.72,1.25+angle),.055,ROD,"Vástago")
        _label(fig,1.5,0,2.65,"TOLVA / CARGA")
    elif subsystem=="Freno con acumuladores":
        for x in (-.2,.45,1.1): _cylinder(fig,(x,-.85,.7),(x+.5,-.85,.7),.15,DARK2,"Acumulador")
        _label(fig,.6,-.9,1.15,"ACUMULADORES")
    else:
        _label(fig,-1.2,0,2.15,"DIRECCIÓN HIDROSTÁTICA")


def _loader(fig,data):
    state=data.get("state",""); subsystem=data.get("subsystem","");amp=float(data.get("visual_amp",1.0))
    steer={"Izquierda":-.28,"Derecha":.28}.get(state,0.0)*amp if subsystem=="Dirección articulada" else 0.0
    # bastidores: delantero gira respecto del trasero
    _cuboid(fig,(-1.25,0,0),(2.8,2.15,.55),YELLOW,"Bastidor trasero")
    _cuboid(fig,(-1.6,0,.85),(1.25,1.85,1.55),DARK2,"Cabina")
    _cuboid(fig,(-1.65,0,1.12),(.9,1.55,.62),GLASS,"Cabina",.72)
    _cuboid_rot_z(fig,(1.05,0,0),(2.45,2.1,.55),steer,YELLOW,"Bastidor delantero",origin=(0,0,0))
    _cylinder(fig,(-.1,0,-.18),(.25,0,-.18),.17,METAL,"Pivote")
    # ruedas realmente verticales con eje Y
    for y in (-1.13,1.13):
        _wheel(fig,-2.0,y,-.45,.72,.44,0.0)
        wx,wy,wz=_rotate_z([(1.55,y,-.45)],steer,(0,0,0))[0]
        _wheel(fig,wx,wy,wz,.78,.44,steer)
    # brazos y balde en plano XZ
    lift_angle={"Raise":.48,"Hold":.26,"Float":.08,"Lower":-.04}.get(state,.12) if subsystem=="Levante de brazos LS" else .22
    lift_angle*=min(1.3,amp)
    arm_origin=np.array([1.15,0,.35])
    arm_len=3.0
    end=np.array([arm_origin[0]+arm_len*math.cos(lift_angle),0,arm_origin[2]+arm_len*math.sin(lift_angle)])
    for y in (-.78,.78):
        p0=_rotate_z([(arm_origin[0],y,arm_origin[2])],steer,(0,0,0))[0]
        p1=_rotate_z([(end[0],y,end[2])],steer,(0,0,0))[0]
        _cylinder(fig,p0,p1,.10,YELLOW,"Brazo lift")
    bucket_angle={"Rollback":.38,"Hold":.05,"Dump":-.55}.get(state,-.10) if subsystem=="Inclinación de balde" else -.10
    # bucket body near arm end
    bucket_angle*=min(1.25,amp)
    bucket_center=(end[0]+.45,0,end[2])
    bucket_center=_rotate_z([bucket_center],steer,(0,0,0))[0]
    end_rot=_rotate_z([(end[0],0,end[2])],steer,(0,0,0))[0]
    _cuboid_rot_y(fig,bucket_center,(1.05,2.0,.55),bucket_angle,YELLOW,"Balde",origin=end_rot)
    # cutting edge; se desplaza con el ángulo del balde y sigue la articulación
    edge_x=end[0]+.95*math.cos(bucket_angle); edge_z=end[2]-.95*math.sin(bucket_angle)-.18
    e0,e1=_rotate_z([(edge_x,-1.0,edge_z),(edge_x,1.0,edge_z)],steer,(0,0,0))
    _cylinder(fig,e0,e1,.05,METAL,"Filo")
    # lift cylinders
    if subsystem=="Levante de brazos LS":
        for y in (-.62,.62):
            _cylinder(fig,(.1,y,.2),(1.75,y,.55+lift_angle),.12,METAL,"Cilindro lift")
            _cylinder(fig,(1.35,y,.48),(1.95,y,.62+lift_angle),.055,ROD,"Vástago")
        _label(fig,1.3,0,2.2,"LEVANTE LS")
    elif subsystem=="Inclinación de balde":
        _cylinder(fig,(1.2,0,1.05),(end[0]-.15,0,end[2]+.45),.12,METAL,"Cilindro tilt")
        _cylinder(fig,(end[0]-.45,0,end[2]+.35),(end[0]+.05,0,end[2]+.4+bucket_angle*.2),.055,ROD,"Vástago")
        _label(fig,1.8,0,2.2,"TILT / BALDE")
    else:
        _cylinder(fig,(-.2,-.68,.15),(.65,-.72,.15),.10,METAL,"Cilindro dirección")
        _cylinder(fig,(-.2,.68,.15),(.65,.72,.15),.10,METAL,"Cilindro dirección")
        _label(fig,0,0,2.15,"ARTICULACIÓN")
    _cuboid(fig,(-.4,0,.45),(.55,.75,.5),DARK2,"Bomba LS")
    _cuboid(fig,(.35,0,.65),(.7,.85,.55),DARK2,"Banco de válvulas")


def _stationary(fig,data):
    state=data.get("state",""); subsystem=data.get("subsystem","");amp=float(data.get("visual_amp",1.0))
    _cuboid(fig,(-2.6,0,-.35),(1.35,1.5,.95),DARK2,"Depósito")
    _cylinder(fig,(-1.65,0,.0),(-.85,0,.0),.38,DARK2,"Motor eléctrico")
    _cylinder(fig,(-.75,0,.0),(-.25,0,.0),.28,METAL,"Bomba")
    _cuboid(fig,(.55,0,.25),(1.0,.8,.7),DARK2,"Banco hidráulico")
    # frame + cylinder
    _cuboid(fig,(2.65,-.75,.65),(.25,.25,3.2),DARK2,"Bastidor")
    _cuboid(fig,(2.65,.75,.65),(.25,.25,3.2),DARK2,"Bastidor")
    _cuboid(fig,(2.65,0,2.15),(.3,1.7,.25),DARK2,"Travesaño")
    pos={"Avance":.8,"Avance rápido":.85,"Trabajo":.65,"Elevar":.65,"Cilindro A":.55,"Cilindro B":.85,
         "Retroceso":.1,"Retorno":.1,"Bajar controlado":.25}.get(state,.35)
    _cylinder(fig,(2.65,0,1.95),(2.65,0,.55),.18,METAL,"Cilindro")
    _cylinder(fig,(2.65,0,.75),(2.65,0,.15+pos*.75*amp),.075,ROD,"Vástago")
    _label(fig,-1.2,0,1.25,"UNIDAD HIDRÁULICA")
    _label(fig,2.65,0,2.5,subsystem.upper(),size=10)


def render_machine_hydraulics_3d(data: dict, height: int = 640):
    """Visor 3D robusto basado en Plotly.

    No depende de Three.js/CDN externos. Se actualiza con cada rerun de Streamlit,
    por lo que los cambios de estado y amplificación se reflejan de inmediato.
    """
    fig=go.Figure()
    machine=data.get("machine","Sistema estacionario")
    if machine=="Camión minero": _truck(fig,data)
    elif machine=="Cargador frontal": _loader(fig,data)
    else: _stationary(fig,data)
    if data.get("show_paths", True):
        _hydraulic_lines(fig,machine,data.get("subsystem",""),data.get("state",""))

    view=data.get("view","Isométrica")
    cams={
        "Frente":dict(eye=dict(x=0.0,y=2.8,z=.8),up=dict(x=0,y=0,z=1)),
        "Lateral":dict(eye=dict(x=2.8,y=0.0,z=.8),up=dict(x=0,y=0,z=1)),
        "Superior":dict(eye=dict(x=.01,y=.01,z=3.3),up=dict(x=0,y=1,z=0)),
        "Isométrica":dict(eye=dict(x=2.2,y=2.2,z=1.55),up=dict(x=0,y=0,z=1)),
    }
    camera=cams.get(view,cams["Isométrica"])
    title=f"{machine} · {data.get('subsystem','')} · {data.get('state','')}"
    fig.update_layout(
        height=height,
        margin=dict(l=0,r=0,t=44,b=0),
        paper_bgcolor=DARK,
        plot_bgcolor=DARK,
        title=dict(text=title,x=.02,y=.98,font=dict(color="#f5ead7",size=15)),
        legend=dict(orientation="h",x=.02,y=.02,bgcolor="rgba(20,20,22,.72)",font=dict(color="#f5ead7",size=11)),
        scene=dict(
            bgcolor=DARK,
            aspectmode="data",
            camera=camera,
            xaxis=dict(showgrid=True,gridcolor="#34373e",zeroline=False,showbackground=False,color="#888e98",title=""),
            yaxis=dict(showgrid=True,gridcolor="#34373e",zeroline=False,showbackground=False,color="#888e98",title=""),
            zaxis=dict(showgrid=True,gridcolor="#34373e",zeroline=False,showbackground=False,color="#888e98",title=""),
        ),
        annotations=[dict(text="Arrastra para rotar · rueda para zoom · líneas de color = asociación hidráulica espacial",x=.5,y=1.02,xref="paper",yref="paper",showarrow=False,font=dict(color="#aeb3bb",size=10))],
        uirevision=f"hyd3d-{machine}-{data.get('subsystem','')}-{data.get('state','')}-{data.get('visual_amp',1)}-{view}",
    )
    chart_key = data.get("plotly_key")
    if not chart_key:
        # Compatibilidad con una página V3 o V4 incompleta: evita que cuatro
        # visores ocultos compartan la clave fija "hyd3d".
        chart_key = f"hyd3d_auto_{next(_PLOTLY_SEQ)}"
    st.plotly_chart(fig,use_container_width=True,config={"displaylogo":False,"scrollZoom":True},key=chart_key)
