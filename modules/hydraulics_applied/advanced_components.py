from __future__ import annotations

import json
import streamlit.components.v1 as components


ADVANCED_COMPONENTS = {
    "relief": {
        "name": "Válvula de alivio",
        "family": "Control de presión",
        "ports": "P → T",
        "principle": "Limita la presión máxima del circuito desviando caudal hacia tanque cuando la presión alcanza el ajuste.",
        "measure": "Mida P antes de la válvula y T/contrapresión en retorno. Compare presión real de apertura con el ajuste esperado.",
        "failure": "Ajuste bajo o fuga interna: no se desarrolla fuerza. Ajuste alto o válvula trabada: riesgo de sobrepresión.",
        "states": ["Debajo del ajuste", "Alivio activo"],
    },
    "reducing": {
        "name": "Válvula reductora de presión",
        "family": "Control de presión",
        "ports": "P → A · control desde A · Y drenaje",
        "principle": "Mantiene una presión menor en una rama. La presión aguas abajo actúa sobre el elemento regulador y estrangula el paso cuando alcanza el ajuste.",
        "measure": "Compare P de entrada con A de salida y revise Y/drenaje. La variable regulada es la presión de salida.",
        "failure": "Si queda abierta, la rama puede recibir presión excesiva. Si queda demasiado cerrada, la función pierde fuerza o velocidad.",
        "states": ["Rama bajo ajuste", "Regulando"],
    },
    "sequence": {
        "name": "Válvula de secuencia",
        "family": "Control de presión",
        "ports": "P → A · pilotaje por presión",
        "principle": "Habilita una segunda función cuando la presión de la primera alcanza el valor de secuencia.",
        "measure": "Mida presión antes y después de la válvula. Compruebe que la segunda función comienza solo al alcanzar el ajuste.",
        "failure": "Ajuste bajo: la segunda función entra demasiado pronto. Ajuste alto o bloqueo: la segunda función no se inicia.",
        "states": ["Antes de secuencia", "Secuencia abierta"],
    },
    "pilot_check": {
        "name": "Check pilotado",
        "family": "Retención / bloqueo",
        "ports": "A ↔ B · X pilotaje",
        "principle": "Permite flujo libre en un sentido y bloquea el retorno hasta que una presión de pilotaje abre el asiento.",
        "measure": "Compare presión en la cámara bloqueada con X. Verifique si existe pilotaje suficiente para liberar la carga.",
        "failure": "Sin pilotaje: el actuador queda bloqueado. Fuga en el asiento: deriva o pérdida de posición.",
        "states": ["Carga bloqueada", "Pilotado abierto"],
    },
    "counterbalance": {
        "name": "Contrabalance / control de carga",
        "family": "Control de carga",
        "ports": "Carga → retorno · X pilotaje · check de bypass",
        "principle": "Mantiene una carga motriz y dosifica su descarga para evitar caída libre o movimiento descontrolado.",
        "measure": "Mida presión de carga, presión de pilotaje X y contrapresión aguas abajo durante descenso controlado.",
        "failure": "Ajuste alto: movimiento lento/caliente. Ajuste bajo o fuga: deriva, descenso inestable o riesgo de runaway.",
        "states": ["Sostener", "Elevar", "Bajar controlado"],
    },
    "oneway_flow": {
        "name": "Control de caudal unidireccional",
        "family": "Control de caudal",
        "ports": "A ↔ B · orificio ajustable + check",
        "principle": "Dosifica el caudal en un sentido y permite retorno libre por el check en el sentido contrario.",
        "measure": "Mida caudal y caída de presión a través del orificio. Relacione Q con velocidad del actuador.",
        "failure": "Restricción excesiva: movimiento lento y calentamiento. Check bloqueado: retorno también queda estrangulado.",
        "states": ["Sentido dosificado", "Bypass libre"],
    },
    "comp_flow": {
        "name": "Control de caudal compensado",
        "family": "Control de caudal",
        "ports": "P → A · compensador mantiene Δp",
        "principle": "Mantiene aproximadamente constante la caída de presión en el orificio para estabilizar el caudal frente a variaciones de carga.",
        "measure": "Mida presión antes y después del orificio y el caudal. Compruebe que Δp de control se mantiene mientras cambia la carga.",
        "failure": "Compensador trabado o contaminado: la velocidad cambia con la carga y aumenta la pérdida de energía.",
        "states": ["Carga baja", "Carga alta compensada"],
    },
    "load_sensing": {
        "name": "Compensación Load Sensing (LS)",
        "family": "Bomba / control de demanda",
        "ports": "P · LS/X · T/control",
        "principle": "La presión de carga se realimenta al control de una bomba variable. El control ajusta desplazamiento para mantener un margen de presión sobre la carga.",
        "measure": "Mida P de bomba y LS en el mismo estado. Compare P−LS con el margen esperado y observe respuesta al variar la carga.",
        "failure": "LS bloqueada/fugada: standby incorrecto, respuesta lenta, exceso de presión o pérdida de velocidad bajo carga.",
        "states": ["Standby", "Demanda", "Carga aumenta"],
    },
}


def component_rows():
    return [(k, v["name"]) for k, v in ADVANCED_COMPONENTS.items()]


def component_state_names(key: str):
    return list(ADVANCED_COMPONENTS[key]["states"])


def render_advanced_component(key: str, state: str, height: int = 520):
    meta = ADVANCED_COMPONENTS[key]
    payload = json.dumps({"key": key, "state": state, "meta": meta}, ensure_ascii=False, separators=(",", ":"))
    html = r'''
<div class="advhyd">
  <div class="bar">
    <div><b id="name"></b><span id="family"></span></div>
    <div class="state"><small>ESTADO</small><b id="state"></b></div>
  </div>
  <div class="canvas"><svg id="s" viewBox="0 0 1120 390" preserveAspectRatio="xMidYMid meet"></svg></div>
  <div class="foot"><div><b>PRINCIPIO</b><span id="principle"></span></div><div><b>QUÉ MEDIR</b><span id="measure"></span></div></div>
</div>
<style>
html,body{margin:0;background:transparent;font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#202126}.advhyd{height:__HEIGHT__px;border:1px solid #d9dcdf;border-radius:15px;background:#fff;overflow:hidden}.bar{height:62px;box-sizing:border-box;padding:9px 14px;border-bottom:1px solid #e4e5e7;display:flex;justify-content:space-between;align-items:center;gap:16px}.bar b{display:block;font-size:15px}.bar span{display:block;font-size:11px;color:#6e747d;margin-top:2px}.state{border:1px solid #f0c992;background:#fff9f1;border-radius:10px;padding:6px 11px;min-width:145px;text-align:right}.state small{display:block;font-size:8px;color:#b36a17;letter-spacing:.1em;font-weight:800}.state b{font-size:12px}.canvas{height:365px;background:linear-gradient(#fcfcfb,#f7f6f2)}.canvas svg{width:100%;height:100%;display:block}.foot{height:88px;display:grid;grid-template-columns:1fr 1fr;border-top:1px solid #e0e2e5;background:#e0e2e5;gap:1px}.foot>div{background:#fff;padding:9px 13px;font-size:11px;line-height:1.35}.foot b{display:block;font-size:9px;letter-spacing:.07em;margin-bottom:3px}.foot span{color:#59606a}
.base{fill:none;stroke:#b8bdc4;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}.flowTrack{fill:none;stroke-width:3.1;stroke-linecap:round;stroke-linejoin:round;opacity:.28}.flow{fill:none;stroke-width:3.4;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:10 8;animation:dash .85s linear infinite}.pressure{stroke:#d84030}.return{stroke:#2a63b8}.pilot{stroke:#d6b72c}.suction{stroke:#4e9b57}.drain{stroke:#e58b32}.sym{fill:#fff;stroke:#22262b;stroke-width:2.5}.thin{fill:none;stroke:#22262b;stroke-width:2.2}.label{font-size:11px;font-weight:700;fill:#30343a}.muted{font-size:9px;fill:#757b84}.port{font-size:10px;font-weight:850;fill:#202126}.tp{fill:#fff;stroke:#f28e1c;stroke-width:2}.tpT{font-size:9px;font-weight:850;fill:#a85d11}.call{fill:#fffaf3;stroke:#ead5ba;stroke-width:1}.callT{font-size:9px;font-weight:850;fill:#bf6f17}.callB{font-size:9px;fill:#5f656d}.hot{stroke:#f28e1c;stroke-width:3.8}.dashed{stroke-dasharray:7 6}@keyframes dash{to{stroke-dashoffset:-36}}@media(prefers-reduced-motion:reduce){.flow{animation:none}}
</style>
<script>
const D=__DATA__,S=document.getElementById('s'),NS='http://www.w3.org/2000/svg';
document.getElementById('name').textContent=D.meta.name;document.getElementById('family').textContent=D.meta.family+' · '+D.meta.ports;document.getElementById('state').textContent=D.state;document.getElementById('principle').textContent=D.meta.principle;document.getElementById('measure').textContent=D.meta.measure;
function el(t,a={},p=S){const n=document.createElementNS(NS,t);Object.entries(a).forEach(([k,v])=>n.setAttribute(k,v));p.appendChild(n);return n}function line(x1,y1,x2,y2,c='base',p=S){return el('line',{x1,y1,x2,y2,class:c},p)}function rect(x,y,w,h,c='sym',rx=0,p=S){return el('rect',{x,y,width:w,height:h,rx,class:c},p)}function circle(x,y,r,c='sym',p=S){return el('circle',{cx:x,cy:y,r,class:c},p)}function text(x,y,t,c='label',a='middle',p=S){const n=el('text',{x,y,class:c,'text-anchor':a},p);n.textContent=t;return n}function poly(q,c='sym',p=S){return el('polygon',{points:q,class:c},p)}function path(d,c='base',p=S){return el('path',{d,class:c},p)}
function wire(pts,role='pressure',active=true){let d='M'+pts[0][0]+' '+pts[0][1];for(let i=1;i<pts.length;i++)d+=' L'+pts[i][0]+' '+pts[i][1];path(d,'base');if(active){path(d,'flowTrack '+role);path(d,'flow '+role)}}function tp(x,y,n){circle(x,y,10,'tp');text(x,y+3,n,'tpT')}function spring(x,y,h=50){let q=[];for(let i=0;i<8;i++)q.push((x+(i%2?7:-7))+','+(y+i*h/7));el('polyline',{points:q.join(' '),class:'thin'})}function note(x,y,w,ttl,body){rect(x,y,w,47,'call',8);text(x+10,y+15,ttl,'callT','start');text(x+10,y+33,body,'callB','start')}
function tank(){line(45,260,45,330,'thin');line(45,330,135,330,'thin');line(135,330,135,260,'thin');text(90,350,'TANQUE','muted')}function pump(){circle(220,285,30,'sym');poly('210,273 240,285 210,297','sym');text(220,335,'BOMBA','muted')}
function actuator(){rect(900,140,155,58,'sym',4);line(955,140,955,198,'thin');line(955,169,1095,169,'thin');text(978,220,'ACTUADOR','muted')}
function relief(){rect(470,210,70,72,'sym',4);line(505,267,505,226,'thin');poly('499,239 511,239 505,226','sym');spring(555,215);text(505,300,'ALIVIO','muted');text(451,264,'P','port');text(553,227,'T','port')}
function reducing(){rect(465,205,84,78,'sym',4);line(507,217,507,271,'thin');poly('501,258 513,258 507,271','sym');spring(565,215);line(549,243,585,243,'thin dashed');line(585,243,585,315,'thin dashed');text(507,302,'REDUCTORA','muted');text(449,249,'P','port');text(565,249,'A','port');text(585,330,'Y','port')}
function sequenceV(){rect(465,205,84,78,'sym',4);line(507,268,507,218,'thin');poly('501,231 513,231 507,218','sym');spring(565,215);line(465,265,438,265,'thin dashed');line(438,265,438,188,'thin dashed');text(507,302,'SECUENCIA','muted');text(449,271,'P','port');text(565,224,'A','port');text(438,178,'X','port')}
function checkPilot(){rect(450,190,115,88,'sym',4);poly('470,225 505,245 470,265','sym');circle(523,245,8,'sym');line(507,278,507,325,'thin dashed');text(507,339,'X','port');text(507,298,'CHECK PILOTADO','muted')}
function counterbalance(){rect(450,185,125,105,'sym',4);line(506,270,506,220,'thin');poly('500,233 512,233 506,220','sym');poly('466,200 487,210 466,220','sym');circle(498,210,6,'sym');spring(589,200);line(535,290,535,330,'thin dashed');text(535,344,'X','port');text(512,308,'CONTRABALANCE','muted')}
function oneWayFlow(){rect(445,190,130,95,'sym',4);path('M480 215 Q510 238 480 261 M540 215 Q510 238 540 261','thin');line(478,275,544,205,'thin');poly('468,202 486,212 468,222','sym');circle(497,212,6,'sym');text(510,305,'CAUDAL + CHECK','muted')}
function compFlow(){rect(440,185,145,105,'sym',4);path('M472 213 Q500 237 472 261 M528 213 Q500 237 528 261','thin');rect(540,205,30,55,'sym',2);line(555,205,555,175,'thin dashed');text(555,165,'Δp','port');text(510,310,'CAUDAL COMPENSADO','muted')}
function ls(){circle(410,250,31,'sym');poly('400,238 430,250 400,262','sym');line(365,295,455,205,'thin');rect(500,205,90,78,'sym',4);text(545,250,'LS CTRL','port');line(545,205,545,165,'thin dashed');text(545,154,'LS / X','port');text(470,312,'BOMBA VARIABLE + CONTROL LS','muted')}
function common(){tank();pump();wire([[135,305],[190,305],[190,285]],'suction',true);wire([[250,285],[380,285]],'pressure',true);tp(330,285,'P1');actuator();wire([[660,169],[900,169]],'pressure',false);wire([[1055,198],[1055,320],[135,320]],'return',false);tp(820,169,'A1')}
function drawRelief(){tank();pump();wire([[135,305],[190,305],[190,285]],'suction',true);wire([[250,285],[470,285],[470,260]],'pressure',true);relief();const on=D.state==='Alivio activo';wire([[540,228],[650,228],[650,320],[135,320]],'return',on);wire([[470,285],[900,285],[900,169]],'pressure',!on);actuator();tp(360,285,'P');note(70,45,300,'LECTURA',on?'P alcanzó ajuste: caudal desvía a T.':'P bajo ajuste: alivio permanece cerrado.');note(410,45,300,'MEDIR','Compare P real con ajuste y contrapresión T.');}
function drawReducing(){tank();pump();wire([[135,305],[190,305],[190,285]],'suction',true);wire([[250,285],[465,285],[465,244]],'pressure',true);reducing();wire([[549,244],[900,244],[900,169]],'pressure',true);actuator();const reg=D.state==='Regulando';wire([[585,315],[585,330],[135,330]],'drain',reg);tp(365,285,'P');tp(720,244,'A');note(70,45,300,'VARIABLE REGULADA','La presión de salida A gobierna el cierre.');note(410,45,300,'ESTADO',reg?'La válvula estrangula para sostener A.':'La conexión está mayormente abierta.');}
function drawSequence(){tank();pump();wire([[135,305],[190,305],[190,285]],'suction',true);wire([[250,285],[465,285],[465,262]],'pressure',true);sequenceV();const on=D.state==='Secuencia abierta';wire([[549,222],[900,222],[900,169]],'pressure',on);actuator();wire([[438,188],[438,150],[330,150]],'pilot',true);tp(365,285,'P1');tp(720,222,'P2');note(70,45,300,'SECUENCIA',on?'La presión alcanzó el ajuste: segunda función habilitada.':'La segunda función permanece bloqueada.');note(410,45,300,'REGLA','Es una condición de presión, no un temporizador.');}
function drawPilotCheck(){tank();pump();wire([[135,305],[190,305],[190,285]],'suction',true);wire([[250,285],[450,285],[450,245]],'pressure',true);checkPilot();const on=D.state==='Pilotado abierto';wire([[565,245],[900,245],[900,169]],'pressure',on);wire([[507,325],[507,345],[735,345],[735,245]],'pilot',on);actuator();tp(365,285,'P');tp(735,345,'X');note(70,45,300,'BLOQUEO',on?'X libera el asiento y permite retorno.':'Sin X la carga queda hidráulicamente bloqueada.');note(410,45,300,'DIAGNÓSTICO','Si no libera, compruebe X antes de culpar al cilindro.');}
function drawCounterbalance(){tank();pump();wire([[135,305],[190,305],[190,285]],'suction',true);wire([[250,285],[450,285],[450,245]],'pressure',true);counterbalance();const lower=D.state==='Bajar controlado',raise=D.state==='Elevar';wire([[575,220],[900,220],[900,169]],raise?'pressure':'return',raise||lower);wire([[535,330],[535,350],[760,350],[760,220]],'pilot',lower);actuator();tp(365,285,'P');tp(760,350,'X');note(70,45,300,'CARGA MOTRIZ',D.state==='Sostener'?'La salida queda bloqueada y la carga se sostiene.':(raise?'El check permite entrada libre en elevación.':'X abre de forma controlada el camino de descarga.'));note(410,45,300,'SEGURIDAD','Nunca confíe solo en la válvula para intervenir bajo carga.');}
function drawOneWayFlow(){tank();pump();wire([[135,305],[190,305],[190,285]],'suction',true);wire([[250,285],[445,285],[445,240]],'pressure',true);oneWayFlow();const bypass=D.state==='Bypass libre';wire([[575,240],[900,240],[900,169]],bypass?'return':'pressure',true);actuator();tp(365,285,'P');tp(720,240,'A');note(70,45,300,'VELOCIDAD',bypass?'El check evita la restricción en retorno.':'El orificio dosifica Q y por tanto velocidad.');note(410,45,300,'MEDIR','Compruebe Q y Δp en el elemento de caudal.');}
function drawCompFlow(){tank();pump();wire([[135,305],[190,305],[190,285]],'suction',true);wire([[250,285],[440,285],[440,240]],'pressure',true);compFlow();wire([[585,240],[900,240],[900,169]],'pressure',true);actuator();tp(365,285,'P1');tp(720,240,'P2');wire([[555,175],[555,145],[700,145]],'pilot',true);note(70,45,300,'COMPENSACIÓN',D.state==='Carga alta compensada'?'El compensador reajusta para preservar Δp y Q.':'El compensador mantiene el margen con carga baja.');note(410,45,300,'MEDIR','P1, P2 y Q deben leerse juntos.');}
function drawLS(){tank();wire([[135,305],[380,305],[380,250]],'suction',true);ls();const standby=D.state==='Standby';wire([[441,250],[500,250]],'pressure',true);wire([[590,250],[900,250],[900,169]],'pressure',!standby);wire([[760,169],[760,145],[545,145],[545,165]],'pilot',!standby);actuator();tp(680,250,'P');tp(650,145,'LS');note(70,45,300,'RELACIÓN',standby?'LS descargada: bomba mantiene presión de standby.':'La bomba busca P ≈ LS + margen de control.');note(410,45,300,'NO CONFUNDIR','LS es señal de carga; no es la línea principal de potencia.');}
switch(D.key){case'relief':drawRelief();break;case'reducing':drawReducing();break;case'sequence':drawSequence();break;case'pilot_check':drawPilotCheck();break;case'counterbalance':drawCounterbalance();break;case'oneway_flow':drawOneWayFlow();break;case'comp_flow':drawCompFlow();break;case'load_sensing':drawLS();break;}
</script>
'''
    html = html.replace("__DATA__", payload).replace("__HEIGHT__", str(int(height)))
    components.html(html, height=height, scrolling=False)
