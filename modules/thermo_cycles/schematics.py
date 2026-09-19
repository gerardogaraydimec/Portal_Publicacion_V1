from __future__ import annotations
import plotly.graph_objects as go
import math

ORANGE="#f28e1c"; DARK="#262730"; BLUE="#2f6ec8"; RED="#c44a3d"; GREEN="#2c944d"; PURPLE="#7c49b6"; GRAY="#7b8090"
FILL_ORANGE="#fff4e6"; FILL_BLUE="#edf4ff"; FILL_GREEN="#eefaf1"; FILL_GRAY="#f8f8fa"; PAPER="#fbfbfc"


def _base(title):
    fig=go.Figure()
    fig.update_xaxes(range=[0,12], visible=False)
    fig.update_yaxes(range=[0,8], visible=False, scaleanchor="x", scaleratio=1)
    fig.update_layout(
        title=dict(text=title,x=0.02,font=dict(size=22,color=DARK)),
        height=650,
        margin=dict(l=8,r=8,t=56,b=22),
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor=PAPER,
    )
    # subtle border card
    fig.add_shape(type="rect",x0=0.1,y0=0.12,x1=11.9,y1=7.88,line=dict(color="#e7e8ee",width=1.2),fillcolor="rgba(255,255,255,0)",layer="below")
    return fig


def _poly(fig, pts, line=DARK, fill="rgba(0,0,0,0)", width=2.2):
    x=[p[0] for p in pts]+[pts[0][0]]
    y=[p[1] for p in pts]+[pts[0][1]]
    fig.add_trace(go.Scatter(x=x,y=y,mode="lines",line=dict(color=line,width=width),fill="toself",fillcolor=fill,hoverinfo="skip"))


def _coil(fig, x0, x1, y, amp=0.15, n=4, color=RED, width=2.0):
    xs=[]; ys=[]
    L=x1-x0
    for i in range(120):
        t=i/119
        xs.append(x0+L*t)
        ys.append(y+amp*math.sin(2*math.pi*n*t))
    fig.add_trace(go.Scatter(x=xs,y=ys,mode="lines",line=dict(color=color,width=width),hoverinfo="skip"))


def _label(fig,x,y,text,size=14,color=DARK,bg="rgba(255,255,255,0.96)",border=False):
    fig.add_annotation(
        x=x,y=y,text=text,showarrow=False,
        font=dict(size=size,color=color),bgcolor=bg,
        bordercolor="#d9dbe3" if border else bg, borderwidth=1 if border else 0,
        borderpad=3
    )


def _state(fig,x,y,n):
    fig.add_annotation(x=x,y=y,text=f"<b>{n}</b>",showarrow=False,font=dict(size=13,color=DARK),bgcolor="white",bordercolor=ORANGE,borderwidth=1.7,borderpad=2)


def _arrow(fig,x0,y0,x1,y1,label="",color=DARK,lab_dx=0,lab_dy=0,size=15,dash=None):
    fig.add_annotation(x=x1,y=y1,ax=x0,ay=y0,xref="x",yref="y",axref="x",ayref="y",showarrow=True,arrowhead=3,arrowsize=1.0,arrowwidth=2.6,arrowcolor=color,text="")
    if dash:
        fig.add_shape(type="line",x0=x0,y0=y0,x1=x1,y1=y1,line=dict(color=color,width=2.2,dash=dash),layer="below")
    if label:
        _label(fig,(x0+x1)/2+lab_dx,(y0+y1)/2+lab_dy,label,size=size,color=color,bg="rgba(255,255,255,0.92)",border=True)


def _pipe(fig, pts, color=DARK, width=2.2):
    x=[p[0] for p in pts]; y=[p[1] for p in pts]
    fig.add_trace(go.Scatter(x=x,y=y,mode="lines",line=dict(color=color,width=width),hoverinfo="skip"))


def _pump(fig,x,y,r=0.55,label="BOMBA"):
    fig.add_shape(type="circle",x0=x-r,y0=y-r,x1=x+r,y1=y+r,line=dict(color=DARK,width=2.4),fillcolor=FILL_BLUE)
    _poly(fig, [(x-r*0.14,y-r*0.40),(x+r*0.42,y),(x-r*0.14,y+r*0.40)], line=BLUE, fill=BLUE, width=1.6)
    _label(fig,x,y-r-0.45,label,size=12,border=True)


def _compressor(fig,x,y,r=0.58,label="COMPRESOR"):
    fig.add_shape(type="circle",x0=x-r,y0=y-r,x1=x+r,y1=y+r,line=dict(color=DARK,width=2.4),fillcolor=FILL_BLUE)
    _poly(fig, [(x-r*0.40,y-r*0.45),(x+r*0.22,y),(x-r*0.40,y+r*0.45)], line=BLUE, fill=BLUE, width=1.5)
    _poly(fig, [(x-r*0.05,y-r*0.30),(x+r*0.36,y),(x-r*0.05,y+r*0.30)], line=BLUE, fill="rgba(47,110,200,0.45)", width=1.2)
    _label(fig,x,y-r-0.48,label,size=12,border=True)


def _turbine(fig,x,y,w=1.55,h=1.20,label="TURBINA"):
    pts=[(x-w/2,y-h/2),(x-w/2+0.40,y+h/2),(x+w/2,y+h*0.30),(x+w/2,y-h*0.30)]
    _poly(fig, pts, line=DARK, fill=FILL_GREEN, width=2.4)
    fig.add_shape(type="line",x0=x-0.30,y0=y-0.32,x1=x+0.35,y1=y+0.33,line=dict(color=GREEN,width=2.2))
    fig.add_shape(type="line",x0=x-0.12,y0=y-0.40,x1=x+0.52,y1=y+0.24,line=dict(color=GREEN,width=1.6))
    _label(fig,x,y-h/2-0.46,label,size=12,border=True)


def _hx(fig,x,y,w=1.7,h=1.15,label="INTERCAMBIADOR",kind="hot"):
    fill=FILL_ORANGE if kind in ("hot","boiler") else FILL_BLUE if kind in ("cold","cond","evap") else FILL_GRAY
    fig.add_shape(type="rect",x0=x-w/2,y0=y-h/2,x1=x+w/2,y1=y+h/2,line=dict(color=DARK,width=2.3),fillcolor=fill)
    c=RED if kind in ("hot","boiler") else BLUE if kind in ("cold","cond","evap") else ORANGE
    _coil(fig, x-w*0.30, x+w*0.30, y, amp=h*0.10, n=3, color=c, width=2.0)
    _label(fig,x,y-h/2-0.45,label,size=12,border=True)


def _combustor(fig,x,y,w=1.6,h=1.2,label="CÁMARA DE\nCOMBUSTIÓN"):
    fig.add_shape(type="rect",x0=x-w/2,y0=y-h/2,x1=x+w/2,y1=y+h/2,line=dict(color=DARK,width=2.3),fillcolor=FILL_ORANGE)
    flame=[(x-0.14,y-0.10),(x+0.03,y+0.34),(x+0.16,y+0.04),(x+0.28,y+0.36),(x+0.10,y+0.08),(x-0.05,y+0.26)]
    _poly(fig, flame, line=RED, fill="rgba(196,74,61,0.35)", width=1.5)
    _label(fig,x,y-h/2-0.50,label,size=11,border=True)


def _open_heater(fig,x,y,w=1.8,h=1.2,label="CALENTADOR\nABIERTO"):
    fig.add_shape(type="rect",x0=x-w/2,y0=y-h/2,x1=x+w/2,y1=y+h/2,line=dict(color=DARK,width=2.3),fillcolor="#f7f7fb")
    fig.add_shape(type="line",x0=x-w/2+0.18,y0=y+h*0.08,x1=x+w/2-0.18,y1=y+h*0.08,line=dict(color="#9aa3b2",width=1.5,dash="dot"))
    fig.add_shape(type="circle",x0=x-0.18,y0=y+0.18,x1=x+0.18,y1=y+0.54,line=dict(color=BLUE,width=1.4),fillcolor="rgba(47,110,200,0.18)")
    fig.add_shape(type="line",x0=x,y0=y-0.34,x1=x,y1=y+0.10,line=dict(color=BLUE,width=1.6))
    _label(fig,x,y-h/2-0.46,label,size=11,border=True)

def _closed_heater(fig,x,y,w=1.9,h=1.05,label="CALENTADOR\nCERRADO"):
    fig.add_shape(type="rect",x0=x-w/2,y0=y-h/2,x1=x+w/2,y1=y+h/2,line=dict(color=DARK,width=2.3),fillcolor=FILL_GRAY)
    fig.add_shape(type="line",x0=x-w*0.30,y0=y+h*0.16,x1=x+w*0.30,y1=y+h*0.16,line=dict(color=ORANGE,width=1.6))
    fig.add_shape(type="line",x0=x-w*0.30,y0=y-h*0.16,x1=x+w*0.30,y1=y-h*0.16,line=dict(color=BLUE,width=1.6))
    fig.add_shape(type="line",x0=x-w*0.18,y0=y-h*0.28,x1=x-w*0.18,y1=y+h*0.28,line=dict(color="#a9afb9",width=1.2,dash="dot"))
    fig.add_shape(type="line",x0=x+w*0.18,y0=y-h*0.28,x1=x+w*0.18,y1=y+h*0.28,line=dict(color="#a9afb9",width=1.2,dash="dot"))
    _label(fig,x,y-h/2-0.46,label,size=11,border=True)

def _deaerator(fig,x,y,w=1.9,h=1.18,label="DEAERADOR"):
    fig.add_shape(type="rect",x0=x-w/2,y0=y-h/2,x1=x+w/2,y1=y+h/2,line=dict(color=DARK,width=2.3),fillcolor="#f8f4eb")
    fig.add_shape(type="line",x0=x-w*0.34,y0=y+h*0.10,x1=x+w*0.34,y1=y+h*0.10,line=dict(color=ORANGE,width=1.5))
    fig.add_shape(type="circle",x0=x-0.18,y0=y-0.18,x1=x+0.18,y1=y+0.18,line=dict(color=ORANGE,width=1.2),fillcolor="rgba(242,142,28,0.18)")
    _label(fig,x,y-h/2-0.46,label,size=11,border=True)

def _stack(fig,x,y,w=1.05,h=1.55,label="HRSG"):
    fig.add_shape(type="rect",x0=x-w/2,y0=y-h/2,x1=x+w/2,y1=y+h/2,line=dict(color=DARK,width=2.3),fillcolor=FILL_ORANGE)
    _coil(fig, x-w*0.24, x+w*0.24, y+0.1, amp=0.10, n=3, color=RED, width=1.9)
    fig.add_shape(type="line",x0=x-w*0.28,y0=y-0.28,x1=x+w*0.28,y1=y-0.28,line=dict(color=BLUE,width=1.5))
    _label(fig,x,y-h/2-0.44,label,size=11,border=True)

def _note(fig,x,y,text,color=GRAY,size=12):
    _label(fig,x,y,text,size=size,color=color,bg="rgba(255,255,255,0)")

def _valve(fig,x,y,w=1.0,h=0.9,label="VÁLVULA"):
    _poly(fig, [(x-w/2,y),(x-0.05,y+h/2),(x-0.05,y-h/2)], line=DARK, fill=FILL_GRAY, width=2.0)
    _poly(fig, [(x+w/2,y),(x+0.05,y+h/2),(x+0.05,y-h/2)], line=DARK, fill=FILL_GRAY, width=2.0)
    _label(fig,x,y-h/2-0.40,label,size=11,border=True)


def _throttle_valve(fig,x,y,label="VÁLVULA DE\nEXPANSIÓN"):
    _valve(fig,x,y,1.0,0.9,label)


def _drum(fig,x,y,w=1.2,h=1.6,label="CÁMARA\nFLASH"):
    fig.add_shape(type="rect",x0=x-w/2,y0=y-h/2,x1=x+w/2,y1=y+h/2,line=dict(color=DARK,width=2.1),fillcolor=FILL_BLUE)
    fig.add_shape(type="line",x0=x-w/2,y0=y+h*0.18,x1=x+w/2,y1=y+h*0.18,line=dict(color=BLUE,width=1.6,dash="dot"))
    _label(fig,x,y-h/2-0.42,label,size=11,border=True)


def schematic(kind,title="Esquema del ciclo", context=None):
    fig=_base(title)

    if kind=="heat_engine":
        fig.add_shape(type="rect",x0=4.25,y0=2.45,x1=7.15,y1=5.55,line=dict(color=DARK,width=2.4),fillcolor=FILL_ORANGE)
        _label(fig,5.7,4.02,"MÁQUINA TÉRMICA",size=18,bg="rgba(255,255,255,0.0)")
        _arrow(fig,5.7,7.0,5.7,5.6,"Q̇<sub>in</sub>",RED,lab_dx=.82,lab_dy=.05)
        _arrow(fig,5.7,2.45,5.7,0.95,"Q̇<sub>out</sub>",BLUE,lab_dx=.90)
        _arrow(fig,9.5,4.0,7.15,4.0,"Ẇ<sub>neto,out</sub>",GREEN,lab_dy=.30)
        _label(fig,5.05,7.35,"T<sub>H</sub>",size=16)
        _label(fig,5.05,0.55,"T<sub>L</sub>",size=16)

    elif kind=="reciprocating":
        fig.add_shape(type="rect",x0=3.8,y0=2.7,x1=7.1,y1=5.1,line=dict(color=DARK,width=2.3),fillcolor=FILL_ORANGE)
        fig.add_shape(type="rect",x0=6.25,y0=2.95,x1=6.95,y1=4.85,line=dict(color=DARK,width=2.0),fillcolor="#ffffff")
        fig.add_shape(type="line",x0=6.95,y0=3.9,x1=8.15,y1=3.9,line=dict(color=DARK,width=2.2))
        fig.add_shape(type="line",x0=8.15,y0=3.9,x1=9.0,y1=4.4,line=dict(color=DARK,width=2.2))
        fig.add_shape(type="line",x0=8.15,y0=3.9,x1=9.0,y1=3.4,line=dict(color=DARK,width=2.2))
        _label(fig,5.0,4.25,"PISTÓN - CILINDRO",size=16,bg="rgba(255,255,255,0.0)")
        _label(fig,8.95,3.88,"W<sub>neto,out</sub>",size=14,color=GREEN)
        _arrow(fig,4.65,6.55,4.65,5.10,"Q<sub>in</sub>",RED,lab_dx=.62)
        _arrow(fig,4.65,2.70,4.65,1.10,"Q<sub>out</sub>",BLUE,lab_dx=.72)
        for n,(x,y) in [(1,(4.25,3.0)),(2,(4.25,4.8)),(3,(6.70,4.8)),(4,(6.70,3.0))]: _state(fig,x,y,n)

    elif kind=="brayton":
        _compressor(fig,2.0,4.0,label="COMPRESOR")
        _combustor(fig,5.0,4.0,label="COMBUSTOR")
        _turbine(fig,8.1,4.0,label="TURBINA")
        _hx(fig,10.7,4.0,1.6,1.1,label="ENFRIADOR",kind="cold")
        _arrow(fig,2.65,4.0,4.2,4.0)
        _arrow(fig,5.8,4.0,7.2,4.0)
        _arrow(fig,8.95,4.0,9.9,4.0)
        _arrow(fig,11.45,4.0,11.8,4.0)
        for n,(x,y) in [(1,(11.52,4.40)),(2,(3.38,4.40)),(3,(6.45,4.40)),(4,(9.35,4.40))]: _state(fig,x,y,n)
        _arrow(fig,5.0,6.6,5.0,4.62,"Q̇<sub>in</sub>",RED,lab_dx=.62)
        _arrow(fig,10.7,3.45,10.7,1.50,"Q̇<sub>out</sub>",BLUE,lab_dx=.82)
        _arrow(fig,1.25,1.45,1.25,3.30,"Ẇ<sub>c,in</sub>",PURPLE,lab_dx=.82)
        _arrow(fig,8.1,3.35,8.1,1.45,"Ẇ<sub>t,out</sub>",GREEN,lab_dx=.90)

    elif kind=="brayton_regen":
        _compressor(fig,1.4,4.0,label="COMP.")
        _hx(fig,3.6,5.45,1.8,1.0,label="REGENERADOR",kind="neutral")
        _combustor(fig,6.0,4.0,label="COMBUSTOR")
        _turbine(fig,8.8,4.0,label="TURBINA")
        _hx(fig,10.9,4.0,1.5,1.0,label="ENFR.",kind="cold")
        _pipe(fig,[(1.95,4.0),(3.15,4.0),(3.15,5.15),(4.5,5.15),(4.5,4.0),(5.15,4.0)])
        _arrow(fig,5.15,4.0,5.25,4.0)
        _arrow(fig,6.8,4.0,7.85,4.0)
        _arrow(fig,9.6,4.0,10.15,4.0)
        _arrow(fig,11.65,4.0,11.85,4.0)
        _pipe(fig,[(10.15,3.55),(10.15,2.45),(4.05,2.45),(4.05,4.95)])
        _arrow(fig,4.05,4.95,4.05,4.55,"Q̇<sub>reg</sub>",ORANGE,lab_dx=.85,lab_dy=.1,size=13)
        _arrow(fig,6.0,6.5,6.0,4.62,"Q̇<sub>in</sub>",RED,lab_dx=.6)
        _arrow(fig,10.9,3.45,10.9,1.55,"Q̇<sub>out</sub>",BLUE,lab_dx=.78)
        _arrow(fig,.75,1.45,.75,3.25,"Ẇ<sub>c,in</sub>",PURPLE,lab_dx=.78)
        _arrow(fig,8.8,3.35,8.8,1.45,"Ẇ<sub>t,out</sub>",GREEN,lab_dx=.84)

    elif kind=="brayton_advanced":
        _compressor(fig,1.2,4.0,label="COMP. 1")
        _hx(fig,3.15,4.0,1.5,1.0,label="INTERENFR.",kind="cold")
        _compressor(fig,5.1,4.0,label="COMP. 2")
        _hx(fig,7.1,5.45,1.8,1.0,label="REGEN.",kind="neutral")
        _combustor(fig,9.2,4.0,label="COMB.")
        _turbine(fig,10.9,4.0,w=1.35,label="TURB.")
        _pipe(fig,[(1.8,4.0),(2.4,4.0)]); _arrow(fig,2.4,4.0,2.45,4.0)
        _arrow(fig,3.9,4.0,4.45,4.0); _arrow(fig,5.75,4.0,6.2,4.0)
        _pipe(fig,[(6.2,4.0),(6.2,5.15),(8.05,5.15),(8.05,4.0),(8.4,4.0)]); _arrow(fig,8.4,4.0,8.45,4.0)
        _arrow(fig,9.95,4.0,10.15,4.0); _arrow(fig,11.55,4.0,11.85,4.0)
        _pipe(fig,[(11.35,3.55),(11.35,2.3),(7.55,2.3),(7.55,4.95)])
        _arrow(fig,7.55,4.95,7.55,4.55,"Q̇<sub>reg</sub>",ORANGE,lab_dx=.83,size=13)
        _arrow(fig,9.2,6.4,9.2,4.62,"Q̇<sub>in</sub>",RED,lab_dx=.62)
        _arrow(fig,1.2,1.5,1.2,3.3,"Ẇ<sub>c1</sub>",PURPLE,lab_dx=.65,size=13)
        _arrow(fig,5.1,1.5,5.1,3.3,"Ẇ<sub>c2</sub>",PURPLE,lab_dx=.65,size=13)
        _arrow(fig,10.9,3.35,10.9,1.45,"Ẇ<sub>t,out</sub>",GREEN,lab_dx=.83)

    elif kind=="rankine":
        _pump(fig,1.8,2.0,label="BOMBA")
        _hx(fig,4.5,4.9,1.9,1.2,label="CALDERA",kind="boiler")
        _turbine(fig,8.0,5.0,w=1.6,h=1.2,label="TURBINA")
        _hx(fig,9.4,1.9,1.8,1.1,label="CONDENSADOR",kind="cond")
        _pipe(fig,[(2.35,2.0),(2.9,2.0),(2.9,4.25),(3.55,4.25)])
        _arrow(fig,3.55,4.25,3.7,4.25)
        _pipe(fig,[(5.45,4.9),(6.2,4.9)]); _arrow(fig,6.2,4.9,7.1,4.9)
        _pipe(fig,[(8.9,4.65),(9.4,4.65),(9.4,2.45)]); _arrow(fig,9.4,2.45,9.4,2.35)
        _pipe(fig,[(8.5,1.9),(2.25,1.9)]); _arrow(fig,2.25,1.9,2.25,1.95)
        for n,(x,y) in [(1,(2.55,2.35)),(2,(3.28,4.62)),(3,(6.45,5.25)),(4,(9.78,3.45))]: _state(fig,x,y,n)
        _arrow(fig,4.5,7.1,4.5,5.52,"Q̇<sub>in</sub>",RED,lab_dx=.65)
        _arrow(fig,8.0,4.35,8.0,2.8,"Ẇ<sub>t,out</sub>",GREEN,lab_dx=.87)
        _arrow(fig,1.8,0.75,1.8,1.45,"Ẇ<sub>p,in</sub>",PURPLE,lab_dx=.82)
        _arrow(fig,10.15,1.9,10.15,0.65,"Q̇<sub>out</sub>",BLUE,lab_dx=.86)

    elif kind=="rankine_reheat":
        _pump(fig,1.3,1.95,label="BOMBA")
        _hx(fig,3.7,4.85,1.7,1.1,label="CALDERA",kind="boiler")
        _turbine(fig,6.3,5.0,w=1.35,h=1.05,label="TURB. HP")
        _hx(fig,8.0,4.85,1.6,1.0,label="RECALENT.",kind="boiler")
        _turbine(fig,10.3,5.0,w=1.35,h=1.05,label="TURB. LP")
        _hx(fig,10.2,1.95,1.7,1.05,label="CONDENSADOR",kind="cond")
        _pipe(fig,[(1.85,1.95),(2.45,1.95),(2.45,4.2),(2.85,4.2)]); _arrow(fig,2.85,4.2,2.95,4.2)
        _arrow(fig,4.55,4.85,5.45,4.85)
        _arrow(fig,7.0,4.85,7.15,4.85)
        _arrow(fig,8.8,4.85,9.45,4.85)
        _pipe(fig,[(11.0,4.75),(10.2,4.75),(10.2,2.45)]); _arrow(fig,10.2,2.45,10.2,2.35)
        _pipe(fig,[(9.35,1.95),(1.75,1.95)]); _arrow(fig,1.75,1.95,1.78,1.95)
        for n,(x,y) in [(1,(2.25,2.32)),(2,(3.08,4.55)),(3,(5.1,5.22)),(4,(7.48,5.22)),(5,(9.15,5.22)),(6,(10.62,3.2))]: _state(fig,x,y,n)
        _arrow(fig,3.7,6.95,3.7,5.38,"Q̇<sub>in</sub>",RED,lab_dx=.65)
        _arrow(fig,8.0,6.95,8.0,5.36,"Q̇<sub>RH</sub>",RED,lab_dx=.68)
        _arrow(fig,6.3,4.35,6.3,2.90,"Ẇ<sub>t,HP</sub>",GREEN,lab_dx=.92,size=13)
        _arrow(fig,10.3,4.35,10.3,2.90,"Ẇ<sub>t,LP</sub>",GREEN,lab_dx=.92,size=13)
        _arrow(fig,1.3,0.75,1.3,1.45,"Ẇ<sub>p,in</sub>",PURPLE,lab_dx=.82)
        _arrow(fig,10.95,1.95,10.95,0.72,"Q̇<sub>out</sub>",BLUE,lab_dx=.86)

    elif kind=="rankine_closed":
        _pump(fig,1.20,1.60,label="BOMBA")
        _closed_heater(fig,3.45,3.95,2.15,1.00,label="CALENTADOR\nCERRADO")
        _hx(fig,6.2,5.20,1.95,1.15,label="CALDERA",kind="boiler")
        _turbine(fig,9.10,5.20,w=1.55,h=1.16,label="TURBINA")
        _hx(fig,10.65,1.70,1.85,1.0,label="CONDENSADOR",kind="cond")
        _valve(fig,4.05,2.35,label="VÁLVULA\nDRENAJE")

        _pipe(fig,[(1.75,1.60),(2.15,1.60),(2.15,3.95),(2.38,3.95)]); _arrow(fig,2.38,3.95,2.45,3.95)
        _pipe(fig,[(4.52,3.95),(5.10,3.95),(5.10,4.88)]); _arrow(fig,5.10,4.88,5.10,4.95)
        _arrow(fig,7.18,5.20,8.25,5.20)
        _pipe(fig,[(9.82,4.92),(10.65,4.92),(10.65,2.20)]); _arrow(fig,10.65,2.20,10.65,2.12)
        _pipe(fig,[(8.82,4.62),(7.40,4.62),(7.40,3.95),(4.55,3.95)]); _arrow(fig,4.55,3.95,4.48,3.95,"y·ṁ",PURPLE,lab_dx=.42,lab_dy=.22,size=12)
        _pipe(fig,[(3.95,3.45),(3.95,2.72)]); _arrow(fig,3.95,2.72,3.95,2.64,"drenaje",GRAY,lab_dx=.45,size=10)
        _pipe(fig,[(4.05,1.90),(4.05,1.60),(1.65,1.60)]); _arrow(fig,1.65,1.60,1.70,1.60)
        _pipe(fig,[(9.90,1.70),(4.58,1.70),(4.58,1.95)]); _arrow(fig,4.58,1.95,4.58,1.88)

        _arrow(fig,6.20,7.00,6.20,5.82,"Q̇<sub>in</sub>",RED,lab_dx=.60)
        _arrow(fig,9.10,4.45,9.10,3.15,"Ẇ<sub>t,out</sub>",GREEN,lab_dx=.84)
        _arrow(fig,1.20,0.62,1.20,1.12,"Ẇ<sub>p,in</sub>",PURPLE,lab_dx=.72,size=11)
        _arrow(fig,11.15,1.70,11.15,0.68,"Q̇<sub>out</sub>",BLUE,lab_dx=.78)
        _note(fig,6.0,0.34,"Precalentamiento indirecto: las corrientes no se mezclan y el drenaje descarga por válvula",size=11)

    elif kind=="rankine_multi":
        n = 3
        if isinstance(context, dict):
            n = int(context.get("n_extract", 3) or 3)
        n = max(2, min(4, n))

        heater_x = [2.3, 4.1, 5.9, 7.7][:n]
        pump_x = [1.3, 3.1, 4.9, 6.7][:n]
        top_branch_y = [4.95, 4.62, 4.28, 3.95][:n]
        closed_count = max(0, n-1)

        for i, px in enumerate(pump_x):
            _pump(fig, px, 1.55, r=0.40, label=f"BOMBA {i+1}")
        for i, hx in enumerate(heater_x):
            if i < closed_count:
                _closed_heater(fig, hx, 3.55, 1.65, 0.90, label=f"CALENTADOR\nCERRADO {i+1}")
            else:
                _deaerator(fig, hx, 3.55, 1.75, 0.96, label="DEAERADOR")

        _hx(fig, 9.15, 5.55, 1.95, 1.15, label="CALDERA", kind="boiler")
        _turbine(fig, 11.0, 5.50, w=1.35, h=1.08, label="TURBINA")
        _hx(fig, 10.95, 1.55, 1.55, 0.92, label="COND.", kind="cond")

        # línea principal de agua condensada
        _pipe(fig,[(10.18,1.55),(1.72,1.55)]); _arrow(fig,1.72,1.55,1.76,1.55)

        # escalera principal entre bombas y calentadores
        _pipe(fig,[(1.72,1.55),(1.95,1.55),(1.95,3.05)]); _arrow(fig,1.95,3.05,1.95,3.12)
        for i, hx in enumerate(heater_x):
            xin = hx - 0.82
            xout = hx + 0.82
            if i == 0:
                _pipe(fig,[(1.95,3.12),(1.95,3.55),(xin,3.55)]); _arrow(fig,xin,3.55,xin+0.05,3.55)
            else:
                px = pump_x[i]
                _pipe(fig,[(px,1.95),(px,3.55),(xin,3.55)]); _arrow(fig,xin,3.55,xin+0.05,3.55)
            if i < len(pump_x)-1:
                nx = pump_x[i+1]
                _pipe(fig,[(xout,3.55),(nx,3.55),(nx,1.95)]); _arrow(fig,nx,1.95,nx,1.90)

        # del último calentador a caldera
        last_p = pump_x[-1]
        _pipe(fig,[(last_p+0.40,1.55),(last_p+0.40,4.95),(8.15,4.95)]); _arrow(fig,8.15,4.95,8.28,4.95)
        _arrow(fig,10.12,5.55,10.28,5.55)

        # retorno al condensador
        _pipe(fig,[(11.68,5.18),(11.68,1.98)]); _arrow(fig,11.68,1.98,11.68,1.92)

        # líneas de extracción desde turbina a cada calentador
        for i, hx in enumerate(heater_x):
            xb = 10.58 - 0.10*i
            yb = top_branch_y[i]
            _pipe(fig,[(xb,5.02),(xb,yb),(hx+0.18,yb),(hx+0.18,4.02)])
            _arrow(fig,hx+0.18,4.02,hx+0.18,3.98,f"y_{i+1}·ṁ",PURPLE,lab_dx=.35,lab_dy=.18,size=11)

        # drenajes en calentadores cerrados
        for i in range(closed_count):
            hx = heater_x[i]
            drop_to = 1.98 if i == 0 else 3.55
            if i == 0:
                _pipe(fig,[(hx,3.10),(hx,2.15),(1.95,2.15)])
                _arrow(fig,1.95,2.15,1.88,2.15,"drenaje",GRAY,lab_dx=.05,lab_dy=.24,size=10)
            else:
                prev_hx = heater_x[i-1]
                _pipe(fig,[(hx,3.10),(hx,2.60),(prev_hx+0.55,2.60),(prev_hx+0.55,3.10)])
                _arrow(fig,prev_hx+0.55,3.10,prev_hx+0.55,3.16,"cascada",GRAY,lab_dx=.34,lab_dy=.12,size=10)

        _arrow(fig,9.15,7.05,9.15,6.12,"Q̇<sub>in</sub>",RED,lab_dx=.58)
        _arrow(fig,11.0,4.78,11.0,3.45,"Ẇ<sub>t,out</sub>",GREEN,lab_dx=.82,size=12)
        for i, px in enumerate(pump_x):
            _arrow(fig,px,0.62,px,1.13,f"Ẇ<sub>p{i+1}</sub>",PURPLE,lab_dx=.52,size=10)
        _arrow(fig,11.58,1.55,11.58,0.68,"Q̇<sub>out</sub>",BLUE,lab_dx=.70,size=11)
        _note(fig,6.1,0.34,f"Esquema original GG DIMEC · regenerativo escalonado con {n} extracciones",size=11)

    elif kind=="rankine_regen":
        _pump(fig,1.35,1.75,label="BOMBA 1")
        _open_heater(fig,3.25,3.85,1.8,1.15,label="CALENTADOR\nABIERTO")
        _pump(fig,5.2,1.75,label="BOMBA 2")
        _hx(fig,7.35,5.10,1.95,1.15,label="CALDERA",kind="boiler")
        _turbine(fig,10.05,5.10,w=1.55,h=1.18,label="TURBINA")
        _hx(fig,10.65,1.75,1.75,1.0,label="CONDENSADOR",kind="cond")

        _pipe(fig,[(1.90,1.75),(2.25,1.75),(2.25,3.28)]); _arrow(fig,2.25,3.28,2.25,3.35)
        _pipe(fig,[(4.15,3.85),(5.2,3.85),(5.2,2.35)]); _arrow(fig,5.2,2.35,5.2,2.28)
        _pipe(fig,[(5.75,1.75),(5.75,4.85),(6.35,4.85)]); _arrow(fig,6.35,4.85,6.48,4.85)
        _arrow(fig,8.33,5.10,9.10,5.10)
        _pipe(fig,[(10.92,4.88),(10.65,4.88),(10.65,2.28)]); _arrow(fig,10.65,2.28,10.65,2.20)
        _pipe(fig,[(9.88,4.45),(8.55,4.45),(8.55,3.85),(4.15,3.85)]); _arrow(fig,4.15,3.85,4.08,3.85,"y·ṁ",PURPLE,lab_dx=.42,lab_dy=.22,size=12)
        _pipe(fig,[(9.85,1.75),(1.82,1.75)]); _arrow(fig,1.82,1.75,1.86,1.75)

        _arrow(fig,7.35,6.95,7.35,5.68,"Q̇<sub>in</sub>",RED,lab_dx=.60)
        _arrow(fig,10.05,4.35,10.05,3.05,"Ẇ<sub>t,out</sub>",GREEN,lab_dx=.84)
        _arrow(fig,1.35,0.70,1.35,1.28,"Ẇ<sub>p1</sub>",PURPLE,lab_dx=.62,size=12)
        _arrow(fig,5.2,0.70,5.2,1.28,"Ẇ<sub>p2</sub>",PURPLE,lab_dx=.62,size=12)
        _arrow(fig,11.22,1.75,11.22,0.72,"Q̇<sub>out</sub>",BLUE,lab_dx=.78)
        _note(fig,6.2,0.34,"Extracción parcial desde la turbina para mezclar y precalentar el agua de alimentación",size=11)

    elif kind=="cogeneration":
        _hx(fig,2.3,4.4,1.8,1.1,label="CALDERA",kind="boiler")
        _turbine(fig,5.3,4.4,label="TURBINA")
        _hx(fig,8.6,5.45,2.2,1.0,label="PROCESO TÉRMICO",kind="hot")
        _hx(fig,8.6,2.15,1.7,1.0,label="CONDENSADOR",kind="cond")
        _arrow(fig,3.2,4.4,4.45,4.4)
        _pipe(fig,[(6.15,4.25),(7.3,4.25),(7.3,5.45)]); _arrow(fig,7.3,5.45,7.55,5.45,"y·ṁ",PURPLE,lab_dy=.25,size=13)
        _pipe(fig,[(6.15,4.25),(7.3,4.25),(7.3,2.15)]); _arrow(fig,7.3,2.15,7.55,2.15,"(1−y)·ṁ",GRAY,lab_dy=-.28,size=13)
        _arrow(fig,2.3,6.3,2.3,5.0,"Q̇<sub>in</sub>",RED,lab_dx=.64)
        _arrow(fig,5.3,3.75,5.3,2.35,"Ẇ<sub>out</sub>",GREEN,lab_dx=.78)
        _arrow(fig,8.6,6.95,8.6,5.95,"Q̇<sub>útil</sub>",RED,lab_dx=.70)
        _arrow(fig,9.2,2.15,9.2,0.88,"Q̇<sub>out</sub>",BLUE,lab_dx=.75)

    elif kind=="combined":
        # Tren Brayton superior
        _compressor(fig,1.55,5.55,label="COMP.")
        _combustor(fig,3.75,5.55,label="COMBUSTOR")
        _turbine(fig,6.15,5.55,w=1.42,h=1.08,label="TURBINA GT")
        _stack(fig,8.65,5.55,1.20,1.55,label="HRSG")
        _arrow(fig,2.12,5.55,2.95,5.55)
        _arrow(fig,4.55,5.55,5.30,5.55)
        _arrow(fig,6.95,5.55,8.00,5.55,"Gases de escape",GRAY,lab_dy=.28,size=12)
        _arrow(fig,3.75,7.0,3.75,6.15,"Q̇<sub>in</sub>",RED,lab_dx=.58)
        _arrow(fig,1.55,4.72,1.55,3.70,"Ẇ<sub>c</sub>",PURPLE,lab_dx=.46,size=11)
        _arrow(fig,6.15,4.72,6.15,3.70,"Ẇ<sub>GT</sub>",GREEN,lab_dx=.48,size=11)

        # Tren Rankine inferior
        _pump(fig,8.55,1.85,label="BOMBA")
        _turbine(fig,10.85,2.95,w=1.35,h=1.02,label="TURBINA ST")
        _hx(fig,6.15,1.85,1.85,1.0,label="CONDENSADOR",kind="cond")
        _pipe(fig,[(6.90,1.85),(8.02,1.85)]); _arrow(fig,8.02,1.85,8.08,1.85)
        _pipe(fig,[(9.12,1.85),(9.12,4.82),(8.08,4.82)]); _arrow(fig,8.08,4.82,8.25,4.82,"Vapor desde HRSG",BLUE,lab_dy=.28,size=12)
        _arrow(fig,9.32,2.95,10.02,2.95)
        _pipe(fig,[(11.60,2.75),(11.90,2.75),(11.90,1.85),(7.05,1.85)]); _arrow(fig,7.05,1.85,6.98,1.85)
        _arrow(fig,10.85,2.20,10.85,1.15,"Ẇ<sub>ST</sub>",GREEN,lab_dx=.48,size=11)
        _arrow(fig,6.15,1.85,6.15,0.68,"Q̇<sub>out</sub>",BLUE,lab_dx=.72,size=11)
        _arrow(fig,8.65,4.72,8.65,3.52,"Q̇<sub>HRSG→vapor</sub>",ORANGE,lab_dx=.86,size=11)
        _note(fig,6.1,0.32,"Ciclo combinado: recuperación del calor de escape de la turbina a gas para alimentar el Rankine",size=11)

    elif kind=="binary":
        fig.add_shape(type="rect",x0=0.95,y0=4.45,x1=4.35,y1=6.65,line=dict(color=DARK,width=2.2),fillcolor="#fff7ee")
        _label(fig,2.65,6.12,"CICLO PRIMARIO",size=15,bg="rgba(255,255,255,0.0)")
        _compressor(fig,1.60,5.10,label="BOMBA/COMP.")
        _hx(fig,3.45,5.10,1.55,0.95,label="GENERADOR",kind="boiler")
        _arrow(fig,2.18,5.10,2.65,5.10)
        _arrow(fig,4.22,5.10,4.95,4.30,"Q̇_{12}",RED,lab_dy=.20,size=12)

        fig.add_shape(type="rect",x0=7.65,y0=1.20,x1=11.20,y1=3.95,line=dict(color=DARK,width=2.2),fillcolor="#eef5ff")
        _label(fig,9.43,3.50,"CICLO SECUNDARIO",size=15,bg="rgba(255,255,255,0.0)")
        _pump(fig,8.20,1.95,label="BOMBA")
        _hx(fig,9.55,2.95,1.55,0.95,label="EVAP./CALDERA",kind="boiler")
        _turbine(fig,10.85,2.95,w=1.10,h=0.90,label="TURB.")
        _pipe(fig,[(8.78,1.95),(8.78,2.95),(8.78,2.95)]); _arrow(fig,8.78,2.95,8.82,2.95)
        _arrow(fig,10.33,2.95,10.38,2.95)
        _pipe(fig,[(11.42,2.75),(11.42,1.95),(8.75,1.95)]); _arrow(fig,8.75,1.95,8.70,1.95)
        _arrow(fig,10.85,2.25,10.85,1.18,"Ẇ<sub>sec</sub>",GREEN,lab_dx=.50,size=11)

        _hx(fig,6.05,4.00,2.10,1.08,label="INTERCAMBIADOR INTERMEDIO",kind="neutral")
        _arrow(fig,4.95,4.30,5.00,4.24)
        _arrow(fig,7.10,3.72,7.70,2.98,"Q̇_{12}",BLUE,lab_dy=-.18,size=12)
        _note(fig,6.05,0.34,"Esquema original GG DIMEC: dos lazos acoplados térmicamente sin mezclar sus fluidos",size=11)

    elif kind=="refrigerator":
        fig.add_shape(type="rect",x0=4.15,y0=2.3,x1=7.25,y1=5.55,line=dict(color=DARK,width=2.4),fillcolor=FILL_BLUE)
        _label(fig,5.7,4.0,"REFRIGERADOR",size=18,bg="rgba(255,255,255,.0)")
        _arrow(fig,5.7,0.95,5.7,2.3,"Q̇<sub>L</sub>",BLUE,lab_dx=.72)
        _arrow(fig,5.7,5.55,5.7,7.0,"Q̇<sub>H</sub>",RED,lab_dx=.72)
        _arrow(fig,9.5,4.0,7.25,4.0,"Ẇ<sub>in</sub>",PURPLE,lab_dy=.28)
        _label(fig,5.05,0.55,"T<sub>L</sub>",size=16)
        _label(fig,5.05,7.35,"T<sub>H</sub>",size=16)

    elif kind=="heat_pump":
        fig.add_shape(type="rect",x0=4.15,y0=2.3,x1=7.25,y1=5.55,line=dict(color=DARK,width=2.4),fillcolor=FILL_BLUE)
        _label(fig,5.7,4.0,"BOMBA DE CALOR",size=18,bg="rgba(255,255,255,.0)")
        _arrow(fig,5.7,0.95,5.7,2.3,"Q̇<sub>L</sub>",BLUE,lab_dx=.72)
        _arrow(fig,5.7,5.55,5.7,7.0,"Q̇<sub>H</sub>",RED,lab_dx=.72)
        _arrow(fig,9.5,4.0,7.25,4.0,"Ẇ<sub>in</sub>",PURPLE,lab_dy=.28)
        _label(fig,5.05,0.55,"T<sub>fría</sub>",size=15)
        _label(fig,4.85,7.35,"T<sub>caliente</sub>",size=15)

    elif kind=="vcr":
        _compressor(fig,2.1,4.8,label="COMPRESOR")
        _hx(fig,5.1,4.8,1.8,1.05,label="CONDENSADOR",kind="cond")
        _throttle_valve(fig,8.0,4.8,label="VÁLVULA DE\nEXPANSIÓN")
        _hx(fig,10.2,2.1,1.8,1.05,label="EVAPORADOR",kind="evap")
        _pipe(fig,[(2.68,4.8),(4.2,4.8)]); _arrow(fig,4.2,4.8,4.25,4.8)
        _arrow(fig,6.0,4.8,7.05,4.8)
        _pipe(fig,[(8.95,4.8),(10.2,4.8),(10.2,2.65)]); _arrow(fig,10.2,2.65,10.2,2.55)
        _pipe(fig,[(9.3,2.1),(2.1,2.1),(2.1,4.15)]); _arrow(fig,2.1,4.15,2.1,4.22)
        for n,(x,y) in [(1,(1.62,3.1)),(2,(3.35,5.15)),(3,(6.55,5.15)),(4,(9.3,4.2))]: _state(fig,x,y,n)
        _arrow(fig,5.1,5.35,5.1,6.8,"Q̇<sub>H</sub>",RED,lab_dx=.62)
        _arrow(fig,10.75,0.85,10.75,1.55,"Q̇<sub>L</sub>",BLUE,lab_dx=.72)
        _arrow(fig,2.1,6.75,2.1,5.45,"Ẇ<sub>c,in</sub>",PURPLE,lab_dx=.83)

    elif kind=="cascade":
        _hx(fig,2.0,2.0,2.3,1.0,label="ETAPA BAJA\nEVAPORADOR",kind="evap")
        _compressor(fig,2.0,5.0,label="COMP. BAJA")
        _hx(fig,5.2,5.0,2.3,1.0,label="INTERCAMBIADOR\nCASCADA",kind="neutral")
        _compressor(fig,8.4,5.0,label="COMP. ALTA")
        _hx(fig,10.4,5.0,1.6,1.0,label="COND.",kind="cond")
        _pipe(fig,[(2.0,2.5),(2.0,4.35)]); _arrow(fig,2.0,4.35,2.0,4.42)
        _arrow(fig,2.58,5.0,4.0,5.0)
        _arrow(fig,6.35,5.0,7.45,5.0)
        _arrow(fig,8.98,5.0,9.55,5.0)
        _arrow(fig,10.4,4.45,10.4,3.2,"Q̇<sub>H</sub>",RED,lab_dx=.70)
        _arrow(fig,1.2,0.7,1.2,1.45,"Q̇<sub>L</sub>",BLUE,lab_dx=.70)
        _label(fig,5.2,6.4,"Transferencia de calor entre etapas",size=13,color=GRAY)

    elif kind=="multistage_ref":
        _compressor(fig,1.6,4.8,label="COMP. 1")
        _drum(fig,4.3,4.7,label="CÁMARA\nFLASH")
        _compressor(fig,7.0,4.8,label="COMP. 2")
        _hx(fig,9.8,4.8,1.7,1.0,label="CONDENSADOR",kind="cond")
        _hx(fig,5.4,1.9,2.0,1.0,label="EVAPORADOR",kind="evap")
        _arrow(fig,2.2,4.8,3.25,4.8,"ṁ<sub>1</sub>",lab_dy=.25,size=13)
        _arrow(fig,4.95,4.8,6.0,4.8,"ṁ<sub>2</sub>",lab_dy=.25,size=13)
        _arrow(fig,7.6,4.8,8.85,4.8)
        _pipe(fig,[(4.3,4.0),(4.3,2.4),(4.4,2.4)]); _arrow(fig,4.4,2.4,4.45,2.4)
        _arrow(fig,6.35,1.2,6.35,1.55,"Q̇<sub>L</sub>",BLUE,lab_dx=.70)
        _arrow(fig,9.8,4.25,9.8,3.0,"Q̇<sub>H</sub>",RED,lab_dx=.70)

    elif kind=="multipurpose_ref":
        _compressor(fig,1.8,4.4,label="COMPRESOR")
        _hx(fig,4.5,4.4,1.7,1.0,label="CONDENSADOR",kind="cond")
        _hx(fig,8.8,5.8,2.0,0.95,label="EVAPORADOR 1",kind="evap")
        _hx(fig,8.8,4.1,2.0,0.95,label="EVAPORADOR 2",kind="evap")
        _hx(fig,8.8,2.4,2.0,0.95,label="EVAPORADOR 3",kind="evap")
        _arrow(fig,2.38,4.4,3.55,4.4)
        _pipe(fig,[(5.35,4.4),(7.1,4.4),(7.1,5.8)]); _arrow(fig,7.1,5.8,7.65,5.8,"ṁ<sub>1</sub>",lab_dy=.25,size=13)
        _pipe(fig,[(5.35,4.4),(7.1,4.4),(7.1,4.1)]); _arrow(fig,7.1,4.1,7.65,4.1,"ṁ<sub>2</sub>",lab_dy=.25,size=13)
        _pipe(fig,[(5.35,4.4),(7.1,4.4),(7.1,2.4)]); _arrow(fig,7.1,2.4,7.65,2.4,"ṁ<sub>3</sub>",lab_dy=.25,size=13)
        _arrow(fig,9.75,6.7,9.75,6.3,"Q̇<sub>L1</sub>",BLUE,lab_dx=.66,size=13)
        _arrow(fig,9.75,1.45,9.75,1.85,"Q̇<sub>L3</sub>",BLUE,lab_dx=.66,size=13)

    elif kind=="liquefaction":
        _compressor(fig,1.7,4.2,label="COMPRESOR")
        _hx(fig,4.8,4.2,2.0,1.0,label="HX REGENERATIVO",kind="neutral")
        _throttle_valve(fig,7.7,4.2,label="VÁLVULA JT")
        _drum(fig,10.2,4.2,w=1.2,h=1.5,label="SEPARADOR")
        _arrow(fig,2.3,4.2,3.7,4.2)
        _arrow(fig,5.8,4.2,6.75,4.2,"h<sub>3</sub>",lab_dy=.25,size=13)
        _arrow(fig,8.65,4.2,9.3,4.2,"h<sub>4</sub>=h<sub>3</sub>",lab_dy=.25,size=13)
        _arrow(fig,10.2,3.45,10.2,2.0,"ṁ<sub>L</sub>",BLUE,lab_dx=.56,size=13)
        _pipe(fig,[(10.8,4.2),(11.5,4.2),(11.5,6.0),(3.8,6.0),(3.8,4.65)])
        _arrow(fig,3.8,4.65,3.8,4.55,"Retorno gas frío",GRAY,lab_dx=.82,size=12)

    elif kind=="gas_refrigeration":
        _compressor(fig,1.7,4.1,label="COMPRESOR")
        _hx(fig,4.4,4.1,1.7,1.0,label="ENFRIADOR",kind="cold")
        _turbine(fig,7.1,4.1,w=1.45,h=1.1,label="TURBINA")
        _hx(fig,10.0,2.2,1.8,1.0,label="HX FRÍO",kind="evap")
        _arrow(fig,2.3,4.1,3.5,4.1)
        _arrow(fig,5.25,4.1,6.15,4.1)
        _pipe(fig,[(7.95,3.9),(10.0,3.9),(10.0,2.75)]); _arrow(fig,10.0,2.75,10.0,2.65)
        _pipe(fig,[(9.1,2.2),(1.7,2.2),(1.7,3.45)]); _arrow(fig,1.7,3.45,1.7,3.55)
        _arrow(fig,4.4,4.65,4.4,6.0,"Q̇<sub>H</sub>",RED,lab_dx=.60)
        _arrow(fig,10.75,0.95,10.75,1.65,"Q̇<sub>L</sub>",BLUE,lab_dx=.66)
        _arrow(fig,1.7,6.0,1.7,4.75,"Ẇ<sub>c</sub>",PURPLE,lab_dx=.55)
        _arrow(fig,7.1,3.45,7.1,2.05,"Ẇ<sub>t</sub>",GREEN,lab_dx=.55)

    elif kind=="absorption":
        _hx(fig,1.4,5.5,1.8,1.0,label="GENERADOR",kind="boiler")
        _hx(fig,4.2,5.5,1.8,1.0,label="CONDENSADOR",kind="cond")
        _throttle_valve(fig,6.8,5.5,label="VÁLVULA")
        _hx(fig,9.7,5.5,1.6,1.0,label="EVAPORADOR",kind="evap")
        _hx(fig,8.0,1.9,2.0,1.0,label="ABSORBEDOR",kind="cold")
        _pump(fig,4.0,1.95,label="BOMBA")
        _arrow(fig,2.3,5.5,3.3,5.5)
        _arrow(fig,5.1,5.5,5.95,5.5)
        _arrow(fig,7.65,5.5,8.85,5.5)
        _pipe(fig,[(10.5,5.0),(10.5,1.9),(9.05,1.9)]); _arrow(fig,9.05,1.9,9.0,1.9)
        _pipe(fig,[(7.0,1.9),(4.55,1.95)]); _arrow(fig,4.55,1.95,4.6,1.95)
        _pipe(fig,[(4.55,1.95),(1.4,1.95),(1.4,4.95)]); _arrow(fig,1.4,4.95,1.4,5.0)
        _arrow(fig,1.4,7.0,1.4,6.05,"Q̇<sub>G</sub>",RED,lab_dx=.60)
        _arrow(fig,9.7,4.95,9.7,3.65,"Q̇<sub>L</sub>",BLUE,lab_dx=.62)
        _arrow(fig,8.0,1.35,8.0,0.50,"Q̇<sub>A</sub>",RED,lab_dx=.60)
        _arrow(fig,4.0,0.75,4.0,1.35,"Ẇ<sub>p</sub>",PURPLE,lab_dx=.55)

    elif kind=="turbojet":
        _hx(fig,1.2,4.0,1.2,1.0,label="DIFUSOR",kind="neutral")
        _compressor(fig,3.3,4.0,label="COMPRESOR")
        _combustor(fig,6.0,4.0,label="COMBUSTOR")
        _turbine(fig,8.6,4.0,w=1.4,h=1.08,label="TURBINA")
        _hx(fig,10.8,4.0,1.25,1.0,label="TOBERA",kind="neutral")
        _arrow(fig,1.8,4.0,2.4,4.0)
        _arrow(fig,3.9,4.0,5.0,4.0)
        _arrow(fig,6.8,4.0,7.75,4.0)
        _arrow(fig,9.35,4.0,10.15,4.0)
        _arrow(fig,6.0,6.5,6.0,4.62,"Q̇<sub>in</sub>",RED,lab_dx=.60)
        _arrow(fig,8.6,3.35,8.6,1.75,"Ẇ<sub>t</sub>",GREEN,lab_dx=.55)
        _arrow(fig,3.3,1.65,3.3,3.35,"Ẇ<sub>c</sub>",PURPLE,lab_dx=.55)
        _arrow(fig,11.35,4.0,11.85,4.0,"Empuje F",GREEN,lab_dy=.26,size=14)

    else:
        fig.add_shape(type="rect",x0=4.0,y0=2.8,x1=8.0,y1=5.2,line=dict(color=DARK,width=2.2),fillcolor=FILL_ORANGE)
        _label(fig,6.0,4.0,"ESQUEMA DEL CICLO",size=18,bg="rgba(255,255,255,0)")

    return fig
