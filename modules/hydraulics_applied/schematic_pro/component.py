from __future__ import annotations

import json
import streamlit.components.v1 as components


def render_hydraulic_schematic(data: dict, height: int = 650):
    payload=json.dumps(data,ensure_ascii=False,separators=(",",":"))
    html=r'''
<div class="hydv4">
  <div class="topbar">
    <div><b id="title"></b><span id="subtitle"></span></div>
    <div class="legend"><span><i class="p"></i>P / trabajo</span><span><i class="t"></i>T / retorno</span><span><i class="s"></i>succión</span><span><i class="ls"></i>pilotaje / LS</span><span><i class="d"></i>drenaje</span></div>
  </div>
  <div class="stage"><svg id="svg" viewBox="0 0 1280 515" preserveAspectRatio="xMidYMid meet"></svg></div>
  <div class="footer"><div><b>MOVIMIENTO ESPERADO</b><span id="motion"></span></div><div><b>LECTURAS ESPERADAS</b><span id="readings"></span></div></div>
</div>
<style>
html,body{margin:0;background:transparent;font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#202126}.hydv4{height:__HEIGHT__px;border:1px solid #d9dcdf;border-radius:16px;background:#fff;overflow:hidden;box-shadow:0 7px 20px #0000000d}.topbar{height:66px;box-sizing:border-box;padding:9px 16px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #e3e4e7;background:#fff;gap:14px}.topbar b{display:block;font-size:15px}.topbar span#subtitle{display:block;color:#697079;font-size:11px;margin-top:3px}.legend{display:flex;gap:9px;flex-wrap:wrap;font-size:10.5px;color:#555b63;justify-content:flex-end}.legend span{display:flex;align-items:center;gap:4px}.legend i{display:inline-block;width:18px;height:4px;border-radius:99px}.legend .p{background:#d84030}.legend .t{background:#2a63b8}.legend .s{background:#4e9b57}.legend .ls{background:#d6b72c}.legend .d{background:#e58b32}.stage{height:515px;background:linear-gradient(#fcfcfb,#f8f7f4)}.stage svg{width:100%;height:100%;display:block}.footer{height:68px;display:grid;grid-template-columns:1fr 1fr;background:#e1e3e6;gap:1px;border-top:1px solid #e1e3e6}.footer>div{background:#fff;padding:9px 14px;font-size:11.5px;line-height:1.35}.footer b{display:block;font-size:10px;letter-spacing:.055em;margin-bottom:3px}.footer span{color:#59606a}
.base{fill:none;stroke:#b4b9c0;stroke-width:1.65;stroke-linecap:round;stroke-linejoin:round}.flow{fill:none;stroke-width:4.2;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:13 9;animation:dash .82s linear infinite}.pressure{stroke:#d84030}.return{stroke:#2a63b8}.suction{stroke:#4e9b57}.pilot{stroke:#d6b72c;stroke-width:2.7;stroke-dasharray:8 7}.drain{stroke:#e58b32;stroke-width:3;stroke-dasharray:4 7}.sym{fill:#fff;stroke:#25282d;stroke-width:2.6}.symActive{stroke:#f28e1c;stroke-width:4}.thin{fill:none;stroke:#25282d;stroke-width:2}.tagBox{fill:#202126}.tagTxt{fill:#fff;font-size:10px;font-weight:800}.name{font-size:10.5px;fill:#40454d;font-weight:680}.port{font-size:10px;fill:#202126;font-weight:850}.lane{font-size:9px;fill:#9a9fa7;font-weight:650;letter-spacing:.08em}.tp{fill:#fff;stroke:#f28e1c;stroke-width:2}.tpTxt{font-size:9px;fill:#a65b10;font-weight:850}.note{fill:#fffaf3;stroke:#ead5ba;stroke-width:1}.noteTitle{fill:#c97317;font-size:9px;font-weight:850;letter-spacing:.08em}.noteBody{fill:#5d626a;font-size:9px}.ghost{opacity:.30}.groupBox{fill:#fbfbfa;stroke:#cfd4da;stroke-width:1.25;stroke-dasharray:6 5}.groupTitle{font-size:9px;fill:#727981;font-weight:850;letter-spacing:.09em}.routeLabel{font-size:9px;fill:#5d646d;font-weight:760}@keyframes dash{to{stroke-dashoffset:-44}}
</style>
<script>
const D=__DATA__,S=document.getElementById('svg'),NS='http://www.w3.org/2000/svg';
document.getElementById('title').textContent=D.machine+' · '+D.subsystem;
document.getElementById('subtitle').textContent='Estado: '+D.state+' · esquema funcional didáctico · NO OEM';
document.getElementById('motion').textContent=D.motion||'';
document.getElementById('readings').textContent=Object.entries(D.readings||{}).map(([k,v])=>k+': '+v).join(' · ')||'—';
const active={pressure:new Set(D.pressure||[]),return:new Set(D.return||[]),pilot:new Set(D.pilot||[]),suction:new Set(D.suction||[]),drain:new Set(D.drain||[])};
const comps=new Set(D.active_components||[]),mode=D.study_mode||'Guiado';
function el(tag,a={},p=S){const n=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(a))n.setAttribute(k,v);p.appendChild(n);return n}
function line(x1,y1,x2,y2,cl='base',p=S){return el('line',{x1,y1,x2,y2,class:cl},p)}
function rect(x,y,w,h,cl='sym',rx=0,p=S){return el('rect',{x,y,width:w,height:h,rx,class:cl},p)}
function circle(x,y,r,cl='sym',p=S){return el('circle',{cx:x,cy:y,r,class:cl},p)}
function path(d,cl='base',p=S){return el('path',{d,class:cl},p)}
function txt(x,y,t,cl='name',anc='middle',p=S){const n=el('text',{x,y,class:cl,'text-anchor':anc},p);n.textContent=t;return n}
function poly(points,cl='sym',p=S){return el('polygon',{points,class:cl},p)}
function gcomp(key){return el('g',{class:comps.has(key)?'active':''})}
function activeClass(role,id){return active[role]&&active[role].has(id)?'flow '+role:null}
function wire(id,role,pts){let d='M'+pts[0][0]+' '+pts[0][1];for(let i=1;i<pts.length;i++)d+=' L'+pts[i][0]+' '+pts[i][1];path(d,'base');const c=activeClass(role,id);if(c)path(d,c)}
function spring(x,y,h=48,p=S){let q=[];for(let i=0;i<8;i++)q.push((x+(i%2?7:-7))+','+(y+i*h/7));el('polyline',{points:q.join(' '),class:'thin'},p)}
function tag(x,y,code,name){rect(x,y,30,18,'tagBox',4);txt(x+15,y+12,code,'tagTxt');if(mode!=='Técnico')txt(x+38,y+12,name,'name','start')}
function tp(x,y,name){circle(x,y,11,'tp');txt(x,y+3.5,name,'tpTxt')}
function port(x,y,name){txt(x,y,name,'port')}
function lane(y,name){txt(18,y,name,'lane','start');line(82,y,125,y,'base ghost')}
function tank(x,y,code='T1'){const g=gcomp('Depósito');line(x,y,x,y+62,'thin',g);line(x+88,y,x+88,y+62,'thin',g);line(x,y+62,x+88,y+62,'thin',g);tag(x,y+78,code,'Depósito');return g}
function pump(x,y,key='Bomba',variable=false,code='P1'){const g=gcomp(key);circle(x,y,31,comps.has(key)?'sym symActive':'sym',g);poly(`${x-10},${y-12} ${x+16},${y} ${x-10},${y+12}`,'sym',g);if(variable)line(x-38,y+38,x+38,y-38,'thin',g);tag(x-15,y+49,code,variable?'Bomba variable':'Bomba');return g}
function relief(x,y,key='Alivio',code='V0'){const g=gcomp(key);rect(x-24,y-32,48,64,comps.has(key)?'sym symActive':'sym',3,g);line(x,y+22,x,y-15,'thin',g);poly(`${x-6},${y-5} ${x+6},${y-5} ${x},${y-17}`,'sym',g);spring(x+35,y-26,52,g);tag(x-15,y+44,code,key);return g}
function check(x,y,key='Load check',code='V2'){const g=gcomp(key);poly(`${x-22},${y-17} ${x+8},${y} ${x-22},${y+17}`,'sym',g);circle(x+20,y,8,'sym',g);tag(x-15,y+28,code,key);return g}
function pressureValve(x,y,key='Control de descenso',code='V3'){const g=gcomp(key);rect(x-32,y-34,64,68,comps.has(key)?'sym symActive':'sym',3,g);line(x,y+22,x,y-18,'thin',g);poly(`${x-6},${y-7} ${x+6},${y-7} ${x},${y-19}`,'sym',g);spring(x+43,y-28,56,g);tag(x-15,y+45,code,key);return g}
function shuttle(x,y,key='Shuttle LS',code='V4'){const g=gcomp(key);rect(x-38,y-22,76,44,'sym',3,g);circle(x,y,7,'sym',g);line(x-38,y-12,x-7,y,'thin',g);line(x-38,y+12,x-7,y,'thin',g);line(x+7,y,x+38,y,'thin',g);tag(x-15,y+31,code,key);return g}
function comp(x,y,key='Compensador',code='V1'){const g=gcomp(key);rect(x-28,y-27,56,54,'sym',3,g);line(x-16,y+15,x+16,y-15,'thin',g);line(x-16,y-15,x+16,y+15,'thin',g);tag(x-15,y+37,code,key);return g}
function hmu(x,y,code='U1'){circle(x,y,34,'sym');txt(x,y+4,'HMU','port');tag(x-15,y+45,code,'Unidad medición/dirección')}
function priority(x,y,code='V1'){rect(x-34,y-27,68,54,'sym',3);txt(x,y+4,'PRIO','port');tag(x-15,y+37,code,'Prioridad')}
function accum(x,y,code){rect(x-22,y-43,44,86,'sym',20);line(x-22,y,x+22,y,'thin');txt(x,y-14,'G','port');tag(x-15,y+54,code,'Acumulador')}
function brake(x,y){rect(x-38,y-27,76,54,'sym',3);line(x-24,y+16,x+24,y-16,'thin');tag(x-15,y+37,'V2','Válvula freno')}
function dcv43(x,y,key='Direccional 4/3',center='closed',code='V1'){const g=gcomp(key),w=54,h=62;for(let i=0;i<3;i++)rect(x+i*w,y,w,h,comps.has(key)?'sym symActive':'sym',0,g);line(x+13,y+h-10,x+41,y+10,'thin',g);line(x+13,y+10,x+41,y+h-10,'thin',g);const cx=x+w;if(center==='float'){line(cx+14,y+12,cx+14,y+33,'thin',g);line(cx+40,y+12,cx+40,y+33,'thin',g);line(cx+14,y+33,cx+40,y+33,'thin',g);line(cx+27,y+33,cx+27,y+h-9,'thin',g)}else if(center==='tandem'){line(cx+14,y+h-13,cx+40,y+h-13,'thin',g);line(cx+14,y+12,cx+14,y+27,'thin',g);line(cx+40,y+12,cx+40,y+27,'thin',g)}else{for(const [xx,yy] of [[cx+14,y+15],[cx+40,y+15],[cx+14,y+h-15],[cx+40,y+h-15]])line(xx-6,yy,xx+6,yy,'thin',g)}line(x+2*w+13,y+10,x+2*w+41,y+h-10,'thin',g);line(x+2*w+13,y+h-10,x+2*w+41,y+10,'thin',g);const mid=x+1.5*w;port(mid-18,y-9,'A');port(mid+18,y-9,'B');port(mid-18,y+h+15,'P');port(mid+18,y+h+15,'T');tag(mid-15,y+h+23,code,key);return g}
function cyl(x,y,key='Cilindro',code='A1',tel=false){const g=gcomp(key);if(tel){rect(x,y,125,56,'sym',4,g);rect(x+40,y+8,115,40,'sym',4,g);line(x+155,y+28,x+205,y+28,'thin',g);port(x-10,y+17,'A');port(x-10,y+47,'B')}else{rect(x,y,155,58,'sym',4,g);line(x+56,y,x+56,y+58,'thin',g);line(x+56,y+29,x+200,y+29,'thin',g);port(x+20,y-8,'A');port(x+124,y+74,'B')}tag(x+58,y+69,code,key);return g}
function cylV(x,y,key='Cilindro vertical',code='A1'){rect(x,y,62,150,'sym',4);line(x,y+77,x+62,y+77,'thin');line(x+31,y+77,x+31,y-52,'thin');port(x-12,y+118,'A');port(x+74,y+42,'B');tag(x+15,y+162,code,key)}
function note(x,y,w,title,body){rect(x,y,w,50,'note',8);txt(x+12,y+16,title,'noteTitle','start');txt(x+12,y+35,body,'noteBody','start')}
function groupBox(x,y,w,h,title){rect(x,y,w,h,'groupBox',10);txt(x+12,y+17,title,'groupTitle','start')}
function routeLabel(x,y,label){txt(x,y,label,'routeLabel','start')}
function headerLanes(){lane(108,'SEÑAL / LS');lane(205,'TRABAJO A');lane(292,'TRABAJO B');lane(405,'PRESIÓN P');lane(470,'RETORNO T')}

function stationary(){headerLanes();tank(42,393);pump(184,405,'Bomba fija',false);relief(290,438,'Alivio');dcv43(430,260,'Direccional 4/3','closed');cyl(900,175,'Cilindro doble efecto');
 wire('tank-pump','suction',[[130,438],[153,438],[153,405]]);wire('pump-p','pressure',[[215,405],[403,405],[403,353]]);wire('p-valve','pressure',[[403,353],[484,353]]);wire('valve-a','pressure',[[466,260],[466,205],[920,205]]);wire('a-cyl','pressure',[[920,205],[920,175]]);wire('cyl-b','return',[[1024,233],[1024,292],[520,292]]);wire('b-valve','return',[[520,292],[520,260]]);wire('valve-t','return',[[520,322],[520,470],[130,470],[130,455]]);wire('t-filter','return',[[520,470],[130,470]]);wire('filter-tank','return',[[130,470],[130,455]]);wire('p-relief','pressure',[[290,405],[290,406]]);wire('relief-t','return',[[290,470],[130,470]]);tp(360,405,'P');tp(735,205,'A');tp(735,292,'B');note(40,30,330,'LECTURA','P abajo; A/B arriba; T retorna por la franja inferior.');note(390,30,350,'REGLA','Primero centro de la 4/3; luego posición accionada.');note(780,30,420,'MEDICIÓN','Compare P, A, B y T antes de culpar a un componente.')}
function counterbal(){headerLanes();tank(42,393);pump(184,405,'Bomba');relief(290,438,'Alivio');dcv43(430,260,'Direccional','closed');pressureValve(760,205,'Contrabalance','V2');cylV(1040,175,'Cilindro vertical');
 wire('tank-pump','suction',[[130,438],[153,438],[153,405]]);wire('pump-p','pressure',[[215,405],[484,405],[484,353]]);wire('p-valve','pressure',[[484,353],[484,322]]);wire('valve-a','pressure',[[466,260],[466,205],[728,205]]);wire('a-cb-check','pressure',[[728,205],[760,205]]);wire('cb-cyl','pressure',[[792,205],[1030,205],[1030,293]]);wire('cyl-b','return',[[1114,217],[1114,292],[520,292],[520,260]]);wire('b-valve','return',[[1114,292],[520,292]]);wire('valve-t','return',[[520,322],[520,470],[130,470]]);wire('t-tank','return',[[130,470],[130,455]]);wire('b-pilot','pilot',[[640,292],[640,108],[760,108],[760,171]]);wire('pilot-cb','pilot',[[760,108],[760,171]]);wire('load-cb','pressure',[[1030,293],[792,205]]);tp(680,205,'A');tp(680,292,'B');tp(760,108,'X');note(40,30,330,'CARGA MOTRIZ','El control de carga gobierna la salida del lado cargado.');note(390,30,350,'DESCENSO','El pilotaje X abre de forma controlada el contrabalance.');note(780,30,420,'SEGURIDAD','Sostener mecánicamente la carga antes de intervenir.')}
function regen(){headerLanes();tank(42,393);pump(184,405,'Bomba');relief(290,438,'Alivio');dcv43(430,260,'Direccional','closed');check(700,205,'Check regeneración','V2');cyl(930,175,'Cilindro','A1');
 wire('tank-pump','suction',[[130,438],[153,438],[153,405]]);wire('pump-p','pressure',[[215,405],[484,405],[484,353]]);wire('p-valve','pressure',[[484,353],[484,322]]);wire('valve-a','pressure',[[466,260],[466,205],[678,205]]);wire('a-cyl','pressure',[[722,205],[950,205],[950,175]]);wire('cyl-b-regen','pressure',[[1054,233],[1054,292],[820,292],[820,205],[722,205]]);wire('regen-a','pressure',[[678,205],[466,205]]);wire('cyl-b','return',[[1054,233],[1054,292],[520,292]]);wire('b-valve','return',[[520,292],[520,260]]);wire('valve-t','return',[[520,322],[520,470],[130,470]]);wire('t-tank','return',[[130,470],[130,455]]);wire('valve-b','pressure',[[520,260],[520,292],[1054,292]]);wire('b-cyl','pressure',[[1054,292],[1054,233]]);wire('cyl-a','return',[[950,175],[950,205],[466,205]]);wire('a-valve','return',[[950,205],[466,205]]);tp(365,405,'P');tp(610,205,'A');tp(610,292,'B');note(40,30,330,'AVANCE RÁPIDO','El caudal del lado vástago se suma al caudal de bomba.');note(390,30,350,'FUERZA','A y B presurizados reducen la fuerza neta disponible.');note(780,30,420,'TRANSICIÓN','Al aumentar la carga se abandona regeneración para recuperar fuerza.')}
function sequenceC(){headerLanes();tank(42,393);pump(184,405,'Bomba');relief(290,438,'Alivio');dcv43(410,260,'Direccional','closed');cyl(740,175,'Cilindro A','A1');pressureValve(830,292,'Válvula de secuencia','V2');cyl(1020,175,'Cilindro B','A2');
 wire('tank-pump','suction',[[130,438],[153,438],[153,405]]);wire('pump-p','pressure',[[215,405],[464,405],[464,353]]);wire('p-valve','pressure',[[464,353],[464,322]]);wire('valve-a','pressure',[[446,260],[446,205],[760,205]]);wire('a-cyla','pressure',[[760,205],[760,175]]);wire('a-seq','pressure',[[680,205],[680,292],[798,292]]);wire('seq-cylb','pressure',[[862,292],[960,292],[960,205],[1040,205]]);wire('cyla-ret','return',[[864,233],[864,470],[500,470]]);wire('cylb-ret','return',[[1144,233],[1144,470],[500,470]]);wire('ret-valve','return',[[500,470],[500,322]]);wire('valve-t','return',[[500,470],[130,470]]);wire('t-tank','return',[[130,470],[130,455]]);wire('valve-ret','pressure',[[500,292],[960,292]]);wire('ret-cyls','pressure',[[960,292],[960,205]]);wire('cyls-a','return',[[760,205],[760,470]]);tp(720,292,'M1');tp(900,292,'M2');note(40,30,330,'SECUENCIA','A primero; cuando sube presión abre V2 y habilita B.');note(390,30,350,'NO ES TEMPORIZADOR','La condición es de presión, no de tiempo.');note(780,30,420,'RETORNO','La reversa necesita una ruta libre/check adecuada.')}
function loaderLift(){
 headerLanes();
 tank(42,393);pump(184,405,'Bomba LS',true);comp(300,405,'Compensador','V1');
 groupBox(400,145,510,230,'BANCO DE IMPLEMENTOS LS');
 dcv43(438,252,'Banco implementos','float','V2');check(690,195,'Load check','V3');shuttle(785,108,'Shuttle LS','V4');cyl(1000,165,'Cilindros lift','A1');
 wire('tank-pump','suction',[[130,438],[153,438],[153,405]]);
 wire('pump-p','pressure',[[215,405],[272,405]]);
 wire('p-comp','pressure',[[328,405],[492,405],[492,345]]);
 wire('comp-spool','pressure',[[492,345],[492,314]]);
 wire('spool-check','pressure',[[474,252],[474,195],[664,195]]);
 wire('check-a','pressure',[[716,195],[1020,195]]);
 wire('a-cyl','pressure',[[1020,195],[1020,165]]);
 wire('spool-b','pressure',[[528,252],[528,305],[1120,305]]);
 wire('b-cyl','pressure',[[1120,305],[1120,223]]);
 wire('cyl-b','return',[[1120,223],[1120,305],[528,305]]);
 wire('b-spool','return',[[528,305],[528,252]]);
 wire('cyl-a','return',[[1020,165],[1020,195],[474,195]]);
 wire('a-spool','return',[[474,195],[474,252]]);
 wire('a-spool-t','return',[[474,252],[474,470]]);
 wire('b-spool-t','return',[[528,252],[528,470]]);
 wire('spool-t','return',[[528,314],[528,470],[130,470]]);
 wire('t-tank','return',[[130,470],[130,455]]);
 wire('a-shuttle','pilot',[[860,195],[860,132],[823,132]]);
 wire('b-shuttle','pilot',[[900,305],[900,132],[823,132]]);
 wire('shuttle-ls','pilot',[[747,108],[300,108]]);
 wire('ls-pump','pilot',[[300,108],[184,108],[184,374]]);
 wire('ls-vent','pilot',[[785,130],[785,148],[528,148],[528,252]]);
 wire('pump-standby','pressure',[[215,405],[272,405]]);
 wire('load-check','pressure',[[716,195],[1020,195]]);
 tp(370,405,'P');tp(610,195,'A');tp(610,305,'B');tp(530,108,'LS');
 routeLabel(925,188,'A → cámara de levante');routeLabel(925,298,'B → cámara opuesta');
 note(40,30,330,'LOAD SENSING','LS informa presión de carga; no transporta potencia.');
 note(390,30,350,'MARGEN','La bomba busca P ≈ LS + Δp de control.');
 note(780,30,420,'LECTURA','Siga P → A/B → LS. No mezcle señal con potencia.');
}
function loaderTilt(){headerLanes();tank(42,393);pump(184,405,'Bomba',true);dcv43(430,260,'Banco implementos','closed','V1');check(690,205,'Load check','V2');cyl(990,175,'Cilindro tilt','A1');
 wire('tank-pump','suction',[[130,438],[153,438],[153,405]]);wire('pump-p','pressure',[[215,405],[484,405],[484,353]]);wire('p-spool','pressure',[[484,353],[484,322]]);wire('spool-a','pressure',[[466,260],[466,205],[664,205]]);wire('a-cyl','pressure',[[716,205],[1010,205],[1010,175]]);wire('cyl-b','return',[[1114,233],[1114,292],[520,292],[520,260]]);wire('b-spool','return',[[1114,292],[520,292]]);wire('spool-b','pressure',[[520,260],[520,292],[1114,292]]);wire('b-cyl','pressure',[[1114,292],[1114,233]]);wire('cyl-a','return',[[1010,175],[1010,205],[466,205]]);wire('a-spool','return',[[1010,205],[466,205]]);wire('spool-t','return',[[520,322],[520,470],[130,470]]);wire('t-tank','return',[[130,470],[130,455]]);wire('work-ls','pilot',[[800,205],[800,108],[184,108]]);wire('ls-pump','pilot',[[184,108],[184,374]]);wire('load-check','pressure',[[716,205],[1010,205]]);tp(350,405,'P');tp(610,205,'A');tp(610,292,'B');note(40,30,330,'TILT','Lea el cilindro junto con el linkage del balde.');note(390,30,350,'HOLD','La deriva exige aislar cilindro, check y spool antes de concluir.');note(780,30,420,'TERRENO','A/B pueden conservar presión con el mando en neutro.')}
function truckHoist(){
 headerLanes();
 tank(42,393);pump(184,405,'Bomba',true);relief(305,438,'Control/compensador','V0');
 groupBox(400,145,515,240,'MÓDULO DE LEVANTE / CONTROL DE CARGA');
 dcv43(435,252,'Hoist valve','float','V1');check(690,195,'Load check','V2');pressureValve(790,300,'Control de descenso','V3');cyl(1000,165,'Cilindros','A1',true);
 wire('tank-pump','suction',[[130,438],[153,438],[153,405]]);
 wire('pump-p','pressure',[[215,405],[489,405],[489,345]]);
 wire('p-hoist','pressure',[[489,345],[489,314]]);
 wire('hoist-check','pressure',[[471,252],[471,195],[664,195]]);
 wire('check-head','pressure',[[716,195],[1020,195]]);
 wire('head-cyl','pressure',[[1020,195],[1020,165]]);
 wire('hoist-rod','pressure',[[525,252],[525,320],[1160,320]]);
 wire('rod-cyl','pressure',[[1160,320],[1160,213]]);
 wire('cyl-rod','return',[[1160,213],[1160,320],[525,320]]);
 wire('rod-hoist','return',[[525,320],[525,252]]);
 wire('cyl-head','return',[[1020,165],[1020,195],[900,195],[900,300],[824,300]]);
 wire('head-control','return',[[824,300],[756,300],[756,350],[471,350],[471,252]]);
 wire('control-t','return',[[790,334],[790,470],[525,470]]);
 wire('hoist-t','return',[[525,314],[525,470],[130,470]]);
 wire('t-tank','return',[[130,470],[130,455]]);
 wire('head-hoist-t','return',[[1020,195],[950,195],[950,455],[525,455],[525,314]]);
 wire('rod-hoist-t','return',[[1160,320],[1125,320],[1125,470],[525,470]]);
 wire('work-ls','pilot',[[850,195],[850,108],[305,108]]);
 wire('ls-pump','pilot',[[305,108],[184,108],[184,374]]);
 wire('rod-pilot','pilot',[[880,320],[880,365],[790,365],[790,334]]);
 wire('pilot-control','pilot',[[790,365],[790,334]]);
 wire('float-pilot','pilot',[[489,252],[489,108]]);
 wire('load-check','pressure',[[716,195],[1020,195]]);
 wire('ls-standby','pilot',[[489,108],[305,108]]);
 tp(375,405,'P');tp(740,195,'HEAD');tp(725,320,'ROD');tp(440,108,'LS');
 routeLabel(925,188,'HEAD / carga');routeLabel(925,313,'ROD / mando');
 note(40,30,330,'FUNCIONAL / NO OEM','Fuente → mando → retención → carga → actuador.');
 note(390,30,350,'RAISE','P → HEAD; ROD → T. El check permite entrada libre.');
 note(780,30,420,'LOWER','P → ROD; HEAD sale dosificado por control de carga.');
}
function steering(){headerLanes();tank(42,393);pump(184,405,'Bomba',true);priority(315,405,'V1');hmu(500,250,'U1');pressureValve(700,250,'Alivios cruzados','V2');cyl(940,175,'Cilindro L','A1');cyl(940,310,'Cilindro R','A2');
 wire('tank-pump','suction',[[130,438],[153,438],[153,405]]);wire('pump-priority','pressure',[[215,405],[281,405]]);wire('priority-hmu','pressure',[[349,405],[500,405],[500,284]]);wire('hmu-l','pressure',[[500,216],[500,205],[960,205]]);wire('l-cyl','pressure',[[960,205],[960,175]]);wire('hmu-r','pressure',[[534,250],[560,250],[560,340],[960,340]]);wire('r-cyl','pressure',[[960,340],[960,310]]);wire('cyl-r-hmu','return',[[1064,368],[1064,470],[466,470],[466,250]]);wire('cyl-l-hmu','return',[[1064,233],[1064,292],[466,292],[466,250]]);wire('hmu-t','return',[[466,250],[466,470],[130,470]]);wire('t-tank','return',[[130,470],[130,455]]);wire('hmu-ls','pilot',[[500,250],[500,108],[315,108]]);wire('ls-priority','pilot',[[315,108],[315,378]]);wire('ls-standby','pilot',[[500,108],[315,108]]);tp(410,405,'P');tp(410,108,'LS');tp(800,205,'L');tp(800,340,'R');note(40,30,330,'PRIORIDAD','La dirección mantiene disponibilidad de caudal.');note(390,30,350,'HMU','Dosifica y dirige el caudal de dirección.');note(780,30,420,'LS','La señal comunica carga al control; no es línea principal.')}
function brakeCircuit(){headerLanes();tank(42,393);pump(184,405,'Bomba');pressureValve(330,405,'Válvula de carga','V1');accum(520,205,'ACC1');accum(600,205,'ACC2');brake(760,292);circle(1020,245,34,'sym');circle(1020,350,34,'sym');tag(1005,392,'B1','Frenos');
 wire('tank-pump','suction',[[130,438],[153,438],[153,405]]);wire('pump-charge','pressure',[[215,405],[298,405]]);wire('charge-accum','pressure',[[362,405],[520,405],[520,248]]);wire('charge-t','return',[[330,439],[330,470],[130,470]]);wire('t-tank','return',[[130,470],[130,455]]);wire('accum-hold','pressure',[[542,205],[650,205]]);wire('accum-brake','pressure',[[650,205],[650,292],[722,292]]);wire('brake-wheel','pressure',[[798,292],[920,292],[920,245],[986,245],[920,292],[920,350],[986,350]]);wire('brake-t','return',[[760,319],[760,470],[130,470]]);tp(445,405,'P1');tp(650,205,'Pacc');tp(870,292,'Pbr');note(40,30,330,'ACUMULADOR','Es fuente de energía aun con el motor detenido.');note(390,30,350,'CARGA','Verifique cut-in / cut-out del circuito real.');note(780,30,420,'SEGURIDAD','Descargar según procedimiento antes de abrir conexiones.')}

switch(D.circuit){case 'stationary_basic':stationary();break;case 'counterbalance':counterbal();break;case 'regenerative':regen();break;case 'sequence':sequenceC();break;case 'loader_lift_ls':loaderLift();break;case 'loader_tilt':loaderTilt();break;case 'truck_hoist':truckHoist();break;case 'steering':steering();break;case 'brake_accum':brakeCircuit();break;default:stationary();}
</script>
'''
    html=html.replace('__DATA__',payload).replace('__HEIGHT__',str(int(height)))
    components.html(html,height=height,scrolling=False)
