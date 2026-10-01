from __future__ import annotations

import html
import streamlit.components.v1 as components

from modules.hydraulics_applied.symbol_catalog_v3 import SYMBOLS

INK = "#202126"
ORANGE = "#f28e1c"
MUTED = "#777b82"
BG = "#fbfaf7"


def _svg_wrap(body: str, width: int = 640, height: int = 250) -> str:
    return f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" aria-label="símbolo hidráulico">
    <defs>
      <marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{INK}"/></marker>
      <marker id="arrO" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{ORANGE}"/></marker>
    </defs>{body}</svg>'''


def _line(x1,y1,x2,y2, dash="", w=3, color=INK, extra=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"{d} {extra}/>'


def _circle(cx,cy,r, fill="white", stroke=INK, w=3):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>'


def _rect(x,y,w,h, fill="white", stroke=INK, sw=3, rx=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def _txt(x,y,s,size=18,weight=600, anchor="middle", color=INK):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="system-ui,Segoe UI,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{html.escape(str(s))}</text>'


def _triangle(cx, cy, direction="out", size=24, fill=INK):
    if direction == "out":
        pts=f"{cx-size},{cy-size*0.75} {cx+size},{cy} {cx-size},{cy+size*0.75}"
    elif direction == "in":
        pts=f"{cx+size},{cy-size*0.75} {cx-size},{cy} {cx+size},{cy+size*0.75}"
    elif direction == "up":
        pts=f"{cx-size*0.75},{cy+size} {cx},{cy-size} {cx+size*0.75},{cy+size}"
    else:
        pts=f"{cx-size*0.75},{cy-size} {cx},{cy+size} {cx+size*0.75},{cy-size}"
    return f'<polygon points="{pts}" fill="{fill}"/>'


def _tank(x=245,y=80,w=150,h=100,closed=False):
    top = _line(x,y,x+w,y) if closed else ""
    return top + _line(x,y,x,y+h) + _line(x+w,y,x+w,y+h) + _line(x,y+h,x+w,y+h)


def _pump(cx=320,cy=125,variable=False,reversible=False,motor=False):
    body=_circle(cx,cy,58)
    if reversible:
        body += _triangle(cx-12,cy,"in" if motor else "out",17)
        body += _triangle(cx+12,cy,"out" if motor else "in",17)
    else:
        body += _triangle(cx,cy,"in" if motor else "out",22)
    if variable:
        body += _line(cx-64,cy+64,cx+64,cy-64,w=3,extra='marker-end="url(#arr)"')
    body += _line(cx,cy-58,cx,cy-95) + _line(cx,cy+58,cx,cy+95)
    return body


def _cylinder(double=True,double_rod=False,cushion=False,telescope=False,single=False):
    if telescope:
        return (_rect(170,78,180,94)+_rect(230,92,185,66)+_rect(285,104,175,42)+_line(460,125,520,125,w=8)+
                _line(170,125,130,125)+_txt(320,215,"etapas",14,500,color=MUTED))
    s=_rect(165,82,280,88)
    s+=_line(300,82,300,170)
    s+=_line(300,126,510,126,w=10)
    if double_rod:
        s+=_line(300,126,100,126,w=10)
    if double:
        s+=_line(215,170,215,205)+_line(390,170,390,205)
        s+=_txt(215,228,"A",16,700)+_txt(390,228,"B",16,700)
    else:
        s+=_line(215,170,215,205)+_txt(215,228,"A",16,700)
    if cushion:
        s+=_line(182,95,205,118,w=2)+_line(182,157,205,134,w=2)+_line(421,95,398,118,w=2)+_line(421,157,398,134,w=2)
    if single:
        # spring return cue
        pts=[];x=330;y=95
        for i in range(8):
            pts.append(f"{x+i*13},{y+(15 if i%2 else 0)}")
        s+=f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="2"/>'
    return s


def _dcv(kind="43_closed"):
    # Main envelopes: 3 squares or 2 squares. P/T bottom, A/B top.
    if kind.startswith("22"):
        x0,y0,w,h=225,80,95,95
        s=_rect(x0,y0,w,h)+_rect(x0+w,y0,w,h)
        # rest left blocked, active right connected vertical
        s+=_line(x0+25,y0+30,x0+70,y0+30)+_line(x0+25,y0+65,x0+70,y0+65)
        s+=_line(x0+w+47,y0+8,x0+w+47,y0+87,extra='marker-end="url(#arr)"')
        s+=_line(x0+47,y0+h,x0+47,y0+h+36)+_line(x0+w+47,y0+h,x0+w+47,y0+h+36)
        return s
    if kind.startswith("32"):
        x0,y0,w,h=190,80,110,95
        s=_rect(x0,y0,w,h)+_rect(x0+w,y0,w,h)
        # left: P blocked, A->T; right: P->A, T blocked
        s+=_line(x0+55,y0+5,x0+55,y0+32)+_line(x0+30,y0+62,x0+80,y0+62,extra='marker-end="url(#arr)"')
        s+=_line(x0+w+55,y0+88,x0+w+55,y0+18,extra='marker-end="url(#arr)"')
        s+=_txt(245,65,"A",16,700)+_txt(220,212,"P",16,700)+_txt(270,212,"T",16,700)
        return s
    positions = 2 if kind=="42" else 3
    w=110;h=95;x0=155 if positions==3 else 210;y0=72
    s="".join(_rect(x0+i*w,y0,w,h) for i in range(positions))
    def conn(x, mode):
        nonlocal s
        if mode=="cross":
            s+=_line(x+25,y0+78,x+85,y0+17,extra='marker-end="url(#arr)"')
            s+=_line(x+25,y0+17,x+85,y0+78,extra='marker-end="url(#arr)"')
        elif mode=="straight":
            s+=_line(x+30,y0+78,x+30,y0+17,extra='marker-end="url(#arr)"')
            s+=_line(x+80,y0+17,x+80,y0+78,extra='marker-end="url(#arr)"')
        elif mode=="closed":
            for xx,yy in [(x+30,y0+20),(x+80,y0+20),(x+30,y0+75),(x+80,y0+75)]:
                s+=_line(xx-12,yy,xx+12,yy)
        elif mode=="open":
            s+=_line(x+20,y0+50,x+90,y0+50)
            s+=_line(x+30,y0+20,x+30,y0+50)+_line(x+80,y0+20,x+80,y0+50)+_line(x+30,y0+50,x+30,y0+80)+_line(x+80,y0+50,x+80,y0+80)
        elif mode=="tandem":
            s+=_line(x+30,y0+78,x+80,y0+78,extra='marker-end="url(#arr)"')
            s+=_line(x+30,y0+18,x+30,y0+38)+_line(x+80,y0+18,x+80,y0+38)
        elif mode=="float":
            s+=_line(x+30,y0+18,x+30,y0+52)+_line(x+80,y0+18,x+80,y0+52)+_line(x+30,y0+52,x+80,y0+52)+_line(x+55,y0+52,x+55,y0+78,extra='marker-end="url(#arr)"')
    if positions==2:
        conn(x0,"straight");conn(x0+w,"cross")
    else:
        conn(x0,"straight")
        center = {"43_closed":"closed","43_open":"open","43_tandem":"tandem","43_float":"float","prop":"closed"}.get(kind,"closed")
        conn(x0+w,center);conn(x0+2*w,"cross")
    # ports
    cx=x0+(positions*w)/2
    s+=_line(cx-36,y0-35,cx-36,y0)+_line(cx+36,y0-35,cx+36,y0)
    s+=_line(cx-36,y0+h,cx-36,y0+h+35)+_line(cx+36,y0+h,cx+36,y0+h+35)
    s+=_txt(cx-36,y0-45,"A",16,700)+_txt(cx+36,y0-45,"B",16,700)+_txt(cx-36,y0+h+58,"P",16,700)+_txt(cx+36,y0+h+58,"T",16,700)
    if kind=="prop":
        s+=_line(x0-36,y0+20,x0-4,y0+20,w=2)+_line(x0-36,y0+76,x0-4,y0+76,w=2)
        s+=_rect(x0-70,y0+15,30,66,fill="#fff7ed",stroke=ORANGE,sw=2)
        s+=_txt(x0-55,y0+55,"∝",22,800,color=ORANGE)
    return s


def _pressure_valve(kind):
    # functional ISO-like envelopes
    x,y,w,h=260,66,120,115
    s=_rect(x,y,w,h)
    if kind=="relief":
        s+=_line(x+60,y+h,x+60,y+22,extra='marker-end="url(#arr)"')
        s+=_line(x-45,y+h-18,x,y+h-18)+_line(x+w,y+22,x+w+45,y+22)
        s+=_txt(x-55,y+h-11,"P",16,700)+_txt(x+w+55,y+28,"T",16,700)
    elif kind=="reducing":
        s+=_line(x+60,y+10,x+60,y+h-10,extra='marker-end="url(#arr)"')
        s+=_line(x-45,y+58,x,y+58)+_line(x+w,y+58,x+w+45,y+58)
        s+=_line(x+w+12,y+58,x+w+12,y+h+45,dash="7 6",w=2)
        s+=_txt(x-55,y+65,"P",16,700)+_txt(x+w+55,y+65,"A",16,700)+_txt(x+w+12,y+h+63,"Y",14,700)
    elif kind=="sequence":
        s+=_line(x+60,y+h,x+60,y+18,extra='marker-end="url(#arr)"')
        s+=_line(x-45,y+h-18,x,y+h-18)+_line(x+w,y+22,x+w+45,y+22)
        s+=_line(x-22,y+h-18,x-22,y+15,dash="7 6",w=2)+_line(x-22,y+15,x+20,y+15,dash="7 6",w=2)
        s+=_txt(x-55,y+h-11,"P",16,700)+_txt(x+w+55,y+28,"A",16,700)+_txt(x-22,y+5,"X",14,700)
    elif kind=="unloading":
        s+=_line(x+60,y+h,x+60,y+18,extra='marker-end="url(#arr)"')
        s+=_line(x-45,y+h-18,x,y+h-18)+_line(x+w,y+22,x+w+45,y+22)
        s+=_line(x+90,y+22,x+90,y-35,dash="7 6",w=2)
        s+=_txt(x+90,y-45,"X",14,700)+_txt(x-55,y+h-11,"P",16,700)+_txt(x+w+55,y+28,"T",16,700)
    # spring and adjust arrow
    pts=[]
    for i in range(8):pts.append(f"{x+w+8+i*10},{y+h-20+(10 if i%2 else 0)}")
    s+=f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="2"/>'
    s+=_line(x+w+45,y+h+30,x+w+105,y+h-30,w=2,extra='marker-end="url(#arr)"')
    return s


def _check(pilot=False):
    s=_line(145,125,250,125)+_line(390,125,495,125)
    s+=f'<polygon points="250,98 250,152 320,125" fill="white" stroke="{INK}" stroke-width="3"/>'
    s+=_circle(342,125,18)
    if pilot:
        s=_rect(220,70,180,110)+s
        s+=_line(310,180,310,222,dash="7 6",w=2)+_triangle(310,202,"up",10)
        s+=_txt(310,240,"X",16,700)
    return s


def _counterbalance():
    # pressure valve + bypass check + pilot
    s=_rect(215,58,210,135)
    s+=_line(150,145,215,145)+_line(425,85,500,85)
    s+=_line(320,145,320,82,extra='marker-end="url(#arr)"')
    # bypass check at top
    s+=f'<polygon points="260,78 285,65 285,91" fill="white" stroke="{INK}" stroke-width="2"/>' + _circle(300,78,8,w=2)
    s+=_line(245,78,260,78,w=2)+_line(308,78,385,78,w=2)
    # spring/adjust
    pts=[]
    for i in range(7):pts.append(f"{355+i*9},{145+(8 if i%2 else 0)}")
    s+=f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="2"/>'
    s+=_line(370,188,420,138,w=2,extra='marker-end="url(#arr)"')
    s+=_line(500,145,500,220,dash="7 6",w=2)+_line(500,220,340,220,dash="7 6",w=2)+_line(340,220,340,193,dash="7 6",w=2)
    s+=_txt(135,152,"A",16,700)+_txt(517,92,"B",16,700)+_txt(518,225,"X",14,700)
    return s


def _flow(kind):
    s=_line(130,125,510,125)
    # restriction at center
    s+=f'<path d="M290 98 Q320 125 290 152 M350 98 Q320 125 350 152" fill="none" stroke="{INK}" stroke-width="3"/>'
    if kind in ("flow_adjust","flow_oneway","flow_comp"):
        s+=_line(275,165,365,75,w=2,extra='marker-end="url(#arr)"')
    if kind=="flow_oneway":
        s+=_line(210,80,430,80,w=2)
        s+=f'<polygon points="295,60 295,100 330,80" fill="white" stroke="{INK}" stroke-width="2"/>' + _circle(342,80,10,w=2)
    if kind=="flow_comp":
        s+=_rect(250,55,140,140,fill="none",stroke=MUTED,sw=1)
        s+=_line(370,105,370,145,extra='marker-end="url(#arr)"')
    return s


def _accessory(kind):
    if kind=="filter":
        return _line(120,125,250,125)+f'<polygon points="250,65 370,125 250,185 130,125" fill="white" stroke="{INK}" stroke-width="3" transform="translate(60,0)"/>'+_line(310,85,310,165,w=2)+_line(370,125,520,125)
    if kind=="cooler":
        return _line(120,125,240,125)+f'<polygon points="240,75 360,125 240,175 120,125" fill="white" stroke="{INK}" stroke-width="3" transform="translate(70,0)"/>'+_line(285,100,335,150,w=2)+_line(335,100,285,150,w=2)+_line(360,125,520,125)
    if kind=="accumulator_gas":
        s=_rect(275,55,90,140,fill="white",stroke=INK,sw=3,rx=42)+_line(275,125,365,125,w=3)+_line(320,195,320,225)
        s+=_txt(320,103,"GAS",13,700)+_txt(320,155,"ACEITE",12,700)
        return s
    if kind=="gauge":
        return _line(320,185,320,220)+_circle(320,125,60)+_line(320,125,355,88,w=4)+_txt(320,55,"p",18,700)
    if kind=="pressure_switch":
        return _line(250,125,300,125)+_circle(330,125,30)+_line(360,125,430,125)+_line(330,95,330,70,dash="6 5",w=2)+_line(330,70,390,70,w=2)+_circle(400,70,5,fill=INK,w=1)+_line(410,55,445,75,w=2)
    if kind=="flow_meter":
        return _line(120,125,250,125)+_circle(320,125,60)+_line(320,125,355,95,w=4)+_line(390,125,520,125)+_txt(320,55,"Q",18,700)
    if kind=="temperature":
        return _circle(320,125,60)+_line(320,95,320,150,w=4)+_circle(320,158,12,fill=INK,w=2)+_txt(320,55,"T",18,700)
    return ""


def _actuation(kind):
    if kind=="spring":
        pts=[]
        for i in range(12):pts.append(f"{150+i*28},{125+(28 if i%2 else -28)}")
        return f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="3"/>'
    if kind=="manual":
        return _line(245,150,245,95,w=4)+_line(245,95,390,55,w=6)+_circle(400,52,12,fill="white")
    if kind=="solenoid":
        return _rect(245,80,150,95)+_line(260,165,380,90,w=3)+_txt(320,215,"bobina",15,600,color=MUTED)
    if kind=="hyd_pilot":
        return _line(200,125,270,125,dash="8 6",w=2)+_triangle(305,125,"out",22)+_line(330,125,430,125,dash="8 6",w=2)+_txt(320,185,"señal hidráulica",15,600,color=MUTED)
    if kind=="detent":
        return _line(170,125,280,125,w=4)+f'<path d="M280 95 L310 125 L340 95 L370 125 L400 95" fill="none" stroke="{INK}" stroke-width="3"/>'
    return ""


def symbol_svg(key: str) -> str:
    if key in ("main_line","pilot_line","drain_line","flex_line","junction","crossing","fixed_orifice","test_point","quick_disconnect"):
        if key=="main_line": body=_line(105,125,535,125,w=4)+_txt(320,205,"línea continua",15,500,color=MUTED)
        elif key=="pilot_line": body=_line(105,125,535,125,dash="18 12",w=3)+_txt(320,205,"pilotaje / control",15,500,color=MUTED)
        elif key=="drain_line": body=_line(105,125,535,125,dash="5 8",w=3)+_txt(320,205,"drenaje / fuga",15,500,color=MUTED)
        elif key=="flex_line": body=f'<path d="M130 125 C210 55 430 195 510 125" fill="none" stroke="{INK}" stroke-width="4"/>'+_circle(130,125,8,fill=INK,w=1)+_circle(510,125,8,fill=INK,w=1)
        elif key=="junction": body=_line(150,125,490,125)+_line(320,45,320,205)+_circle(320,125,8,fill=INK,w=1)
        elif key=="crossing": body=_line(150,125,490,125)+f'<path d="M320 45 L320 95 Q320 112 336 112 Q352 112 352 125 Q352 138 336 138 Q320 138 320 155 L320 205" fill="none" stroke="{INK}" stroke-width="3"/>'
        elif key=="fixed_orifice": body=_flow("fixed")
        elif key=="test_point": body=_line(130,125,505,125)+_line(320,125,320,65)+_line(307,65,333,65)+_txt(320,45,"M",15,700)
        else: body=_line(110,125,230,125)+f'<polygon points="230,95 280,125 230,155" fill="white" stroke="{INK}" stroke-width="3"/>'+f'<polygon points="410,95 360,125 410,155" fill="white" stroke="{INK}" stroke-width="3"/>'+_circle(292,125,12)+_circle(348,125,12)+_line(410,125,530,125)
        return _svg_wrap(body)
    if key.startswith("reservoir") or key in ("tank_above","tank_below"):
        body=_tank(closed=(key=="reservoir_pressurized"))
        if key=="tank_above": body+=_line(320,30,320,80)+_line(270,125,370,125,w=2,color=MUTED)
        elif key=="tank_below": body+=_line(320,30,320,150)+_line(270,125,370,125,w=2,color=MUTED)
        else: body+=_line(320,35,320,80)
        return _svg_wrap(body)
    if key in ("pump_fixed","pump_variable","pump_reversible","motor_fixed","motor_reversible"):
        body=_pump(variable=key=="pump_variable",reversible=key in ("pump_reversible","motor_reversible"),motor=key.startswith("motor"))
        return _svg_wrap(body)
    if key.startswith("cyl_"):
        body=_cylinder(double=key!="cyl_single",double_rod=key=="cyl_double_rod",cushion=key=="cyl_cushion",telescope=key=="cyl_telescopic",single=key=="cyl_single")
        return _svg_wrap(body)
    if key.startswith("dcv_"):
        kind={"dcv_22_nc":"22","dcv_32_nc":"32","dcv_42":"42","dcv_43_closed":"43_closed","dcv_43_open":"43_open","dcv_43_tandem":"43_tandem","dcv_43_float":"43_float","dcv_prop":"prop"}[key]
        return _svg_wrap(_dcv(kind))
    if key in ("relief","reducing","sequence","unloading"):
        return _svg_wrap(_pressure_valve(key))
    if key=="counterbalance": return _svg_wrap(_counterbalance())
    if key in ("check","pilot_check"):
        return _svg_wrap(_check(pilot=key=="pilot_check"))
    if key in ("flow_adjust","flow_oneway","flow_comp"):
        return _svg_wrap(_flow(key))
    if key=="shuttle":
        b=_rect(220,70,200,110)+_line(130,95,220,95)+_line(130,155,220,155)+_line(420,125,510,125)+_circle(305,125,14)+_line(220,95,291,125)+_line(220,155,291,125)+_line(319,125,420,125)
        return _svg_wrap(b)
    if key in ("filter","cooler","accumulator_gas","gauge","pressure_switch","flow_meter","temperature"):
        return _svg_wrap(_accessory(key))
    if key in ("spring","manual","solenoid","hyd_pilot","detent"):
        return _svg_wrap(_actuation(key))
    if key in ("pump_pressure_comp","pump_ls"):
        b=_pump(variable=True)
        b+=_rect(405,62,105,72,fill="#fff7ed",stroke=ORANGE,sw=2,rx=4)+_txt(457,91,"CTRL",13,800,color=ORANGE)
        b+=_line(405,125,365,125,dash="7 6",w=2)
        if key=="pump_ls": b+=_line(457,62,457,35,dash="7 6",w=2)+_txt(457,25,"LS",13,800,color=ORANGE)
        else: b+=_txt(457,118,"P comp",11,700,color=ORANGE)
        return _svg_wrap(b)
    if key=="rotary_actuator":
        b=_circle(320,125,58)+_line(285,170,355,170,w=4)+f'<path d="M270 125 A50 50 0 0 1 370 125" fill="none" stroke="{INK}" stroke-width="3" marker-end="url(#arr)"/>'+_txt(320,215,"giro limitado",14,500,color=MUTED)
        return _svg_wrap(b)
    if key=="cyl_telescopic_double":
        b=_cylinder(telescope=True)+_line(170,155,125,155)+_txt(110,160,"B",15,700)
        return _svg_wrap(b)
    if key=="relief_pilot":
        b=_pressure_valve("relief")+_line(320,66,320,35,dash="7 6",w=2)+_txt(320,24,"X",13,700)
        return _svg_wrap(b)
    if key=="brake_valve":
        return _svg_wrap(_counterbalance()+_txt(320,35,"OVER-CENTER / BRAKE",13,800,color=ORANGE))
    if key=="flow_divider":
        b=_line(120,125,250,125)+_rect(250,70,140,110)+_line(320,125,320,86,extra='marker-end="url(#arr)"')+_line(320,125,285,165,extra='marker-end="url(#arr)"')+_line(320,125,355,165,extra='marker-end="url(#arr)"')+_line(285,180,285,215)+_line(355,180,355,215)+_txt(285,235,"A",14,700)+_txt(355,235,"B",14,700)
        return _svg_wrap(b)
    if key=="priority_valve":
        b=_rect(225,65,190,120)+_line(150,125,225,125)+_line(415,95,490,95)+_line(415,155,490,155)+_txt(510,100,"CF",14,700)+_txt(510,160,"EF",14,700)+_line(255,155,385,95,extra='marker-end="url(#arr)"')+_line(320,65,320,35,dash="7 6",w=2)+_txt(320,25,"LS",13,700)
        return _svg_wrap(b)
    if key=="logic_cartridge":
        b=_rect(235,55,170,140)+f'<polygon points="270,155 320,105 370,155" fill="white" stroke="{INK}" stroke-width="3"/>'+_line(320,105,320,70)+_line(170,155,270,155)+_line(370,155,470,155)+_line(320,55,320,30,dash="7 6",w=2)+_txt(320,20,"X",13,700)
        return _svg_wrap(b)
    if key=="diff_gauge":
        b=_circle(320,115,58)+_line(320,115,355,82,w=4)+_line(280,173,280,220)+_line(360,173,360,220)+_txt(280,238,"P1",13,700)+_txt(360,238,"P2",13,700)+_txt(320,48,"Δp",18,800)
        return _svg_wrap(b)
    if key=="pressure_transducer":
        b=_circle(300,125,52)+_line(300,177,300,220)+_line(352,125,430,125)+_txt(455,130,"4–20 mA",13,700)+_txt(300,132,"p",20,800)
        return _svg_wrap(b)
    if key=="level_gauge":
        b=_tank(240,70,160,120,closed=False)+_rect(420,82,24,95,fill="white",stroke=INK,sw=2,rx=8)+_line(424,135,440,135,w=5,color=ORANGE)+_txt(432,205,"nivel",13,600,color=MUTED)
        return _svg_wrap(b)
    if key=="tachometer":
        b=_circle(320,125,60)+_line(320,125,355,92,w=4)+_txt(320,55,"n",18,800)+_txt(320,210,"rpm",14,600,color=MUTED)
        return _svg_wrap(b)
    if key=="pressure_compensator":
        b=_rect(245,70,150,110)+_line(270,155,370,95,extra='marker-end="url(#arr)"')+_line(320,70,320,35,dash="7 6",w=2)+_txt(320,24,"LS",13,700)+_txt(320,215,"mantiene Δp",14,600,color=MUTED)
        return _svg_wrap(b)
    return _svg_wrap(_txt(320,125,"Símbolo no disponible",20,700))


def render_symbol(key: str, height: int = 345):
    meta = SYMBOLS[key]
    svg = symbol_svg(key)
    body=f'''
<div class="card">
  <div class="head"><div><div class="family">{html.escape(meta['family'])}</div><h2>{html.escape(meta['name'])}</h2></div><div class="level">{html.escape(meta['level'])}</div></div>
  <div class="drawing">{svg}</div>
  <div class="port"><b>Puertos / conexión:</b> {html.escape(meta['ports'])}</div>
</div>
<style>
html,body{{margin:0;background:transparent;font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:{INK}}}
.card{{height:{height-4}px;background:{BG};border:1px solid #ded9d0;border-radius:15px;overflow:hidden;box-sizing:border-box}}
.head{{height:74px;padding:12px 16px 6px;display:flex;justify-content:space-between;align-items:flex-start;background:#fff;border-bottom:1px solid #e7e1d8;box-sizing:border-box}}
h2{{font-size:19px;margin:3px 0 0}}.family{{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#777}}.level{{font-size:11px;border:1px solid #f3c895;background:#fff4e7;color:#9b5612;border-radius:999px;padding:4px 8px}}
.drawing{{height:{height-145}px;display:flex;align-items:center;justify-content:center;padding:0 12px;box-sizing:border-box}}.drawing svg{{width:100%;height:100%}}.port{{height:66px;border-top:1px solid #e7e1d8;background:#fff;padding:12px 16px;font-size:13px;box-sizing:border-box}}
</style>'''
    components.html(body,height=height,scrolling=False)



def _h_spring(x1: int, y: int, direction: int = 1, length: int = 64) -> str:
    pts=[]
    steps=8
    for i in range(steps+1):
        xx=x1 + direction*(i*length/steps)
        yy=y + (10 if i%2 else -10)
        pts.append(f"{xx:.1f},{yy:.1f}")
    return f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="2.5"/>'


def _actuator_side(x: float, y: float, side: str, kind: str) -> str:
    left = side == 'left'
    d = -1 if left else 1
    out=''
    lower=kind.lower()
    if 'resorte' in lower or 'centrado' in lower:
        sx=x + d*8
        out += _h_spring(sx, y, d, 56)
    if 'solenoide' in lower:
        bx=x + d*86 - (28 if left else 0)
        out += _rect(bx, y-25, 28, 50, fill='white', stroke=INK, sw=2)
        if left: out += _line(bx+4,y+20,bx+24,y-20,w=2)
        else: out += _line(bx+4,y-20,bx+24,y+20,w=2)
    if 'pilotaje' in lower or 'pilotado' in lower:
        cx=x + d*93
        pts=(f"{cx+18},{y-18} {cx+18},{y+18} {cx-12},{y}" if left else f"{cx-18},{y-18} {cx-18},{y+18} {cx+12},{y}")
        out += f'<polygon points="{pts}" fill="white" stroke="{INK}" stroke-width="2.2"/>'
        out += _line(cx+d*20,y,cx+d*58,y,dash='7 6',w=2)
    if 'manual' in lower or 'palanca' in lower:
        px=x + d*72
        out += _line(x+d*6,y,px,y,w=2.5)
        out += _line(px,y,px+d*34,y-46,w=4)
        out += _circle(px+d*38,y-50,7,fill='white',stroke=INK,w=2)
    if 'detent' in lower:
        px=x+d*72
        out += _line(x+d*5,y,px,y,w=2.5)
        if left:
            path_d=f'M{px} {y-22} L{px-14} {y} L{px} {y+22} L{px-14} {y+44}'
        else:
            path_d=f'M{px} {y-22} L{px+14} {y} L{px} {y+22} L{px+14} {y+44}'
        out += f'<path d="{path_d}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
    return out


def _builder_valve_svg(ways: int, positions: int, center: str, actuation: str) -> str:
    W,H=120,112
    total=W*positions
    x0=(760-total)/2
    y0=72
    body=''
    if positions==3:
        rest_idx=1
    elif 'detent' in actuation.lower() or 'doble solenoide' in actuation.lower():
        rest_idx=None
    else:
        rest_idx=1
    for i in range(positions):
        fill='#fff7ed' if i==rest_idx else 'white'
        body += _rect(x0+i*W,y0,W,H,fill=fill,stroke=INK,sw=3)

    def arr(x1,y1,x2,y2):
        return _line(x1,y1,x2,y2,w=3,extra='marker-end="url(#arr)"')
    def cap(x,y):
        return _line(x-11,y,x+11,y,w=3)

    def fourway_cell(x,mode):
        if mode=='pa_bt':
            return arr(x+34,y0+H-14,x+34,y0+16)+arr(x+86,y0+16,x+86,y0+H-14)
        if mode=='pb_at':
            return arr(x+34,y0+H-14,x+86,y0+16)+arr(x+34,y0+16,x+86,y0+H-14)
        if mode=='closed':
            return cap(x+34,y0+24)+cap(x+86,y0+24)+cap(x+34,y0+H-24)+cap(x+86,y0+H-24)
        if mode=='open':
            out=_line(x+34,y0+24,x+34,y0+56,w=3)+_line(x+86,y0+24,x+86,y0+56,w=3)+_line(x+34,y0+56,x+86,y0+56,w=3)+_line(x+34,y0+56,x+34,y0+H-24,w=3)+_line(x+86,y0+56,x+86,y0+H-24,w=3)
            return out+_circle(x+60,y0+56,4,fill=INK,stroke=INK,w=1)
        if mode=='tandem':
            return arr(x+34,y0+H-18,x+86,y0+H-18)+cap(x+34,y0+25)+cap(x+86,y0+25)
        jx=x+86; jy=y0+64
        return (_line(x+34,y0+22,x+34,jy,w=3)+_line(x+86,y0+22,x+86,jy,w=3)+
                _line(x+34,jy,jx,jy,w=3)+arr(jx,jy,jx,y0+H-14)+cap(x+34,y0+H-23))

    def threeway_cell(x,mode):
        if mode=='closed_rest':
            return _line(x+60,y0+22,x+60,y0+56,w=3)+arr(x+60,y0+56,x+92,y0+H-18)+cap(x+30,y0+H-24)
        return arr(x+30,y0+H-18,x+60,y0+18)+cap(x+92,y0+H-24)

    def twoway_cell(x,open_state=False):
        return arr(x+60,y0+H-18,x+60,y0+18) if open_state else cap(x+60,y0+24)+cap(x+60,y0+H-24)

    if ways==4:
        if positions==3:
            body+=fourway_cell(x0,'pa_bt')
            mode={'Cerrado':'closed','Abierto':'open','Tándem':'tandem','Flotante':'float'}.get(center,'closed')
            body+=fourway_cell(x0+W,mode)
            body+=fourway_cell(x0+2*W,'pb_at')
            px=x0+W
        else:
            body+=fourway_cell(x0,'pa_bt')+fourway_cell(x0+W,'pb_at')
            px=x0+W
        body+=_line(px+34,y0-36,px+34,y0)+_line(px+86,y0-36,px+86,y0)
        body+=_line(px+34,y0+H,px+34,y0+H+36)+_line(px+86,y0+H,px+86,y0+H+36)
        body+=_txt(px+34,y0-46,'A',18,800)+_txt(px+86,y0-46,'B',18,800)+_txt(px+34,y0+H+58,'P',18,800)+_txt(px+86,y0+H+58,'T',18,800)
    elif ways==3:
        body+=threeway_cell(x0,'active')+threeway_cell(x0+W,'closed_rest')
        px=x0+W
        body+=_line(px+60,y0-36,px+60,y0)+_line(px+30,y0+H,px+30,y0+H+36)+_line(px+92,y0+H,px+92,y0+H+36)
        body+=_txt(px+60,y0-46,'A',18,800)+_txt(px+30,y0+H+58,'P',18,800)+_txt(px+92,y0+H+58,'T',18,800)
    else:
        body+=twoway_cell(x0,True)+twoway_cell(x0+W,False)
        px=x0+W
        body+=_line(px+60,y0-36,px+60,y0)+_line(px+60,y0+H,px+60,y0+H+36)
        body+=_txt(px+60,y0-46,'2',18,800)+_txt(px+60,y0+H+58,'1',18,800)

    left_x=x0; right_x=x0+total; cy=y0+H/2; lower=actuation.lower()
    if positions==3:
        if 'doble solenoide' in lower:
            body += _actuator_side(left_x,cy,'left','solenoide')+_actuator_side(right_x,cy,'right','solenoide')
            body += _actuator_side(left_x,cy,'left','resorte')+_actuator_side(right_x,cy,'right','resorte')
        elif 'doble pilotaje' in lower:
            body += _actuator_side(left_x,cy,'left','pilotaje')+_actuator_side(right_x,cy,'right','pilotaje')
            body += _actuator_side(left_x,cy,'left','resorte')+_actuator_side(right_x,cy,'right','resorte')
        elif 'solenoide pilotado' in lower:
            body += _actuator_side(left_x,cy,'left','solenoide pilotaje')+_actuator_side(right_x,cy,'right','solenoide pilotaje')
            body += _actuator_side(left_x,cy,'left','resorte')+_actuator_side(right_x,cy,'right','resorte')
        else:
            body += _actuator_side(left_x,cy,'left','manual')
            body += _actuator_side(left_x,cy,'left','resorte')+_actuator_side(right_x,cy,'right','resorte')
    else:
        if 'doble solenoide' in lower and 'detent' in lower:
            body += _actuator_side(left_x,cy,'left','solenoide detent')+_actuator_side(right_x,cy,'right','solenoide detent')
        elif 'solenoide' in lower:
            body += _actuator_side(left_x,cy,'left','solenoide')+_actuator_side(right_x,cy,'right','resorte')
        elif 'pilotaje' in lower:
            body += _actuator_side(left_x,cy,'left','pilotaje')+_actuator_side(right_x,cy,'right','resorte')
        else:
            body += _actuator_side(left_x,cy,'left','manual')+_actuator_side(right_x,cy,'right','resorte')

    if rest_idx is not None:
        rx=x0+rest_idx*W+W/2
        body += _txt(rx,y0-66,'REPOSO',12,800,color=ORANGE)+_line(rx,y0-60,rx,y0-52,w=2,color=ORANGE)
    else:
        body += _txt(380,y0-66,'SIN REPOSO FIJO · DETENT',12,800,color=ORANGE)
    return _svg_wrap(body,width=760,height=300)

def render_valve_builder(ways: int, positions: int, center: str, actuation: str, height: int = 430):
    svg=_builder_valve_svg(ways,positions,center,actuation)
    if ways==4 and positions==3:
        rest={
            'Cerrado':'P, T, A y B bloqueados.',
            'Abierto':'P, T, A y B quedan intercomunicados en la posición central.',
            'Tándem':'P comunica con T; A y B permanecen bloqueados.',
            'Flotante':'A y B comunican con T; P permanece bloqueado.',
        }.get(center,'Centro no definido.')
    elif ways==4:
        rest='En una válvula 4/2 con retorno por resorte, la casilla junto al resorte representa el reposo.'
    elif ways==3:
        rest='En esta 3/2 didáctica, el reposo junto al resorte deja P bloqueado y A comunicado con T.'
    else:
        rest='En esta 2/2 didáctica, el reposo junto al resorte deja el paso 1–2 cerrado.'
    if positions==3:
        ref='La casilla central es la posición de referencia cuando existe centrado por resortes.'
    elif 'detent' in actuation.lower():
        ref='Con detent no se asume una posición de reposo automática: la válvula permanece en la última posición seleccionada.'
    else:
        ref='La casilla junto al resorte es el reposo; la casilla junto al accionamiento representa la posición accionada.'
    html_body=f'''\
<div class="wrap">
 <div class="left">
   <div class="caption"><b>Cómo leer el dibujo</b><span>1) identifique reposo · 2) lea puertos externos · 3) siga conexiones dentro de una sola casilla · 4) recién prediga el actuador.</span></div>
   {svg}
 </div>
 <div class="right">
  <div class="tag">CONSTRUCTOR</div>
  <h3>{ways}/{positions} · {html.escape(center if positions==3 else 'sin centro')}</h3>
  <p><b>Vías / puertos:</b> {ways}. <b>Posiciones:</b> {positions}.</p>
  <p><b>Referencia:</b> {html.escape(ref)}</p>
  <p><b>Condición de reposo:</b> {html.escape(rest)}</p>
  <p><b>Accionamiento representado:</b> {html.escape(actuation)}.</p>
  <div class="mini"><b>Convención del constructor</b><br>Las flechas muestran el camino del caudal en cada casilla. Las líneas cortas transversales representan puertos bloqueados. Los accionamientos se dibujan fuera del sobre de la válvula.</div>
 </div>
</div>
<style>
html,body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:{INK};background:transparent}}.wrap{{height:{height-4}px;border:1px solid #ded9d0;border-radius:15px;background:#fbfaf7;display:grid;grid-template-columns:1.42fr .58fr;overflow:hidden}}.left{{position:relative;display:flex;align-items:flex-end;padding:44px 8px 8px;background:white}}.left svg{{width:100%;height:100%}}.caption{{position:absolute;left:18px;top:12px;right:18px;display:flex;gap:10px;align-items:baseline;font-size:11px;color:#666}}.caption b{{color:{INK};font-size:12px}}.right{{padding:22px 20px;border-left:1px solid #e5e0d8;background:#faf7f1}}.tag{{font-size:11px;letter-spacing:.12em;color:{ORANGE};font-weight:800}}h3{{margin:6px 0 12px;font-size:24px}}p{{font-size:13px;line-height:1.48;margin:8px 0}}.mini{{margin-top:14px;padding:10px 11px;background:#fff;border:1px solid #e3ddd4;border-left:4px solid {ORANGE};border-radius:9px;font-size:11.5px;line-height:1.45}}
</style>'''
    components.html(html_body,height=height,scrolling=False)
