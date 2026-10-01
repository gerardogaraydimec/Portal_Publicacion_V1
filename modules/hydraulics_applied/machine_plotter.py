from __future__ import annotations
import plotly.graph_objects as go

BLACK="#202126"; ORANGE="#f28e1c"; BLUE="#3977c3"; YELLOW="#d9b835"; GRAY="#777b84"; WHITE="#ffffff"


def _add_line(fig,x0,y0,x1,y1,color=BLACK,width=3,dash=None):
    fig.add_shape(type="line",x0=x0,y0=y0,x1=x1,y1=y1,line=dict(color=color,width=width,dash=dash))


def _box(fig,x,y,w,h,text,fill="#fff",color=BLACK):
    fig.add_shape(type="rect",x0=x-w/2,x1=x+w/2,y0=y-h/2,y1=y+h/2,line=dict(color=color,width=2),fillcolor=fill)
    fig.add_annotation(x=x,y=y,text=text,showarrow=False,font=dict(size=12,color=color))


def machine_schematic_figure(machine:str, subsystem:str, state:str, paths:dict):
    fig=go.Figure()
    fig.update_layout(height=480,margin=dict(l=12,r=12,t=36,b=12),paper_bgcolor=WHITE,plot_bgcolor=WHITE,showlegend=False,
                      xaxis=dict(range=[0,12],visible=False),yaxis=dict(range=[0,7],visible=False),title=f"{machine} · {subsystem} · {state}")
    # common source
    _box(fig,1.0,1.0,1.2,.7,"Depósito",fill="#f7f7f5")
    fig.add_shape(type="circle",x0=.65,x1=1.35,y0=2.1,y1=2.8,line=dict(color=BLACK,width=2),fillcolor="#fff")
    fig.add_annotation(x=1.0,y=2.45,text="Bomba",showarrow=False,font=dict(size=11))
    _add_line(fig,1.0,1.35,1.0,2.1,BLUE,3)
    _box(fig,3.0,2.45,1.7,1.05,"Control\nprincipal",fill="#fffaf4")
    _add_line(fig,1.35,2.45,2.15,2.45,ORANGE,4)
    _box(fig,3.0,4.9,1.5,.8,"Alivio",fill="#fff")
    _add_line(fig,2.65,2.95,2.65,4.5,ORANGE,3)
    _add_line(fig,3.35,4.5,3.35,1.3,BLUE,3)
    _add_line(fig,3.35,1.3,1.6,1.3,BLUE,3)

    if subsystem in ("Levante de tolva","Levante de brazos"):
        _box(fig,6.0,2.45,1.8,1.1,"Válvula\n4/4",fill="#fff")
        _add_line(fig,3.85,2.45,5.1,2.45,ORANGE,4)
        _box(fig,9.2,4.3,1.2,2.1,"Cilindro\n1",fill="#f8f8f8")
        _box(fig,10.7,4.3,1.2,2.1,"Cilindro\n2",fill="#f8f8f8")
        activeA = state in ("Elevar",)
        activeB = state in ("Bajar",)
        ca = ORANGE if activeA else GRAY; cb = ORANGE if activeB else BLUE
        _add_line(fig,6.9,2.7,8.0,2.7,ca,4); _add_line(fig,8.0,2.7,8.0,4.7,ca,4); _add_line(fig,8.0,4.7,8.6,4.7,ca,4); _add_line(fig,8.0,4.7,10.1,4.7,ca,4)
        _add_line(fig,6.9,2.15,7.6,2.15,cb,4); _add_line(fig,7.6,2.15,7.6,3.9,cb,4); _add_line(fig,7.6,3.9,8.6,3.9,cb,4); _add_line(fig,7.6,3.9,10.1,3.9,cb,4)
        _add_line(fig,5.4,1.95,5.4,1.0,BLUE,3); _add_line(fig,5.4,1.0,1.6,1.0,BLUE,3)
        fig.add_annotation(x=9.6,y=6.0,text="Actuadores del implemento",showarrow=False,font=dict(size=13,color=BLACK))
    elif subsystem in ("Dirección","Dirección articulada"):
        _box(fig,6.0,2.45,1.9,1.1,"Unidad de\ndirección",fill="#fff")
        _add_line(fig,3.85,2.45,5.05,2.45,ORANGE,4)
        _box(fig,6.0,5.15,1.8,.75,"Alivios\ncruzados",fill="#fff")
        _add_line(fig,5.5,3.0,5.5,4.77,YELLOW,2,dash="dash"); _add_line(fig,6.5,3.0,6.5,4.77,YELLOW,2,dash="dash")
        _box(fig,9.0,4.5,1.5,1.5,"Cilindro L",fill="#f8f8f8"); _box(fig,10.8,4.5,1.5,1.5,"Cilindro R",fill="#f8f8f8")
        left = state=="Izquierda"; right=state=="Derecha"
        _add_line(fig,6.95,2.7,8.1,2.7,ORANGE if left else BLUE if right else GRAY,4); _add_line(fig,8.1,2.7,8.1,4.5,ORANGE if left else BLUE if right else GRAY,4); _add_line(fig,8.1,4.5,8.25,4.5,ORANGE if left else BLUE if right else GRAY,4)
        _add_line(fig,6.95,2.15,10.0,2.15,ORANGE if right else BLUE if left else GRAY,4); _add_line(fig,10.0,2.15,10.0,4.5,ORANGE if right else BLUE if left else GRAY,4)
        _add_line(fig,5.05,1.95,5.05,1.0,BLUE,3); _add_line(fig,5.05,1.0,1.6,1.0,BLUE,3)
        _add_line(fig,3.2,3.0,4.4,3.9,YELLOW,2,dash="dash"); fig.add_annotation(x=4.4,y=4.0,text="LS / mando",showarrow=False,font=dict(size=10,color="#9a7d11"))
    elif subsystem=="Inclinación de balde":
        _box(fig,6.0,2.45,1.8,1.1,"Sección\ntilt",fill="#fff")
        _add_line(fig,3.85,2.45,5.1,2.45,ORANGE,4)
        _box(fig,9.7,4.3,1.5,2.0,"Cilindro\ntilt",fill="#f8f8f8")
        a=ORANGE if state=="Recoger" else BLUE if state=="Descargar" else GRAY
        b=ORANGE if state=="Descargar" else BLUE if state=="Recoger" else GRAY
        _add_line(fig,6.9,2.7,8.5,2.7,a,4); _add_line(fig,8.5,2.7,8.5,4.7,a,4); _add_line(fig,8.5,4.7,8.95,4.7,a,4)
        _add_line(fig,6.9,2.15,8.0,2.15,b,4); _add_line(fig,8.0,2.15,8.0,3.9,b,4); _add_line(fig,8.0,3.9,8.95,3.9,b,4)
        _add_line(fig,5.1,1.95,5.1,1.0,BLUE,3); _add_line(fig,5.1,1.0,1.6,1.0,BLUE,3)
    else:
        _box(fig,6.0,2.45,1.8,1.1,"Válvula de\nservicio",fill="#fff")
        _box(fig,9.5,4.2,2.0,1.0,"Freno /\nenfriamiento",fill="#f8f8f8")
        _add_line(fig,3.85,2.45,5.1,2.45,ORANGE,4); _add_line(fig,6.9,2.45,8.5,2.45,ORANGE if state=="Servicio" else GRAY,4); _add_line(fig,8.5,2.45,8.5,4.2,ORANGE if state=="Servicio" else GRAY,4)
        _add_line(fig,8.5,3.7,7.7,3.7,BLUE,3); _add_line(fig,7.7,3.7,7.7,1.0,BLUE,3); _add_line(fig,7.7,1.0,1.6,1.0,BLUE,3)

    fig.add_annotation(x=6,y=.35,text="Rojo/naranja: presión · Azul: retorno · Amarillo discontinuo: mando / load sensing",showarrow=False,font=dict(size=11,color=GRAY))
    return fig
