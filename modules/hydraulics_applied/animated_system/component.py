from __future__ import annotations
import json
import streamlit.components.v1 as components


def render_animated_hydraulic_system(data: dict, height: int = 690):
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = r'''
<div id="hydv2" class="hyd-root">
  <div class="hyd-head">
    <div><b id="hyd-title">Hidráulica aplicada</b><div id="hyd-sub" class="muted"></div></div>
    <div class="legend"><span><i class="p"></i> Presión</span><span><i class="r"></i> Retorno</span><span><i class="s"></i> Succión</span><span><i class="c"></i> Mando / LS</span></div>
  </div>
  <div class="hyd-stage">
    <svg id="scene" viewBox="0 0 1200 650" preserveAspectRatio="xMidYMid meet"></svg>
  </div>
  <div class="hyd-bottom"><div id="hyd-motion"></div><div id="hyd-note"></div></div>
</div>
<style>
.hyd-root{height:__HEIGHT__px;border-radius:16px;border:1px solid #d8d9dc;background:#d8d8d6;color:#202126;overflow:hidden;font-family:system-ui,-apple-system,Segoe UI,sans-serif;box-shadow:0 8px 22px #00000014}
.hyd-head{height:70px;background:#f1f1ef;border-bottom:1px solid #bfc1c4;display:flex;align-items:center;justify-content:space-between;padding:0 18px;gap:18px}
#hyd-title{font-size:17px}.muted{color:#60646b;font-size:12px;margin-top:3px}.legend{display:flex;gap:12px;flex-wrap:wrap;font-size:12px}.legend span{display:flex;align-items:center;gap:5px}.legend i{display:inline-block;width:17px;height:5px;border-radius:5px}.legend .p{background:#d84030}.legend .r{background:#2a63b8}.legend .s{background:#4e9b57}.legend .c{background:#d6b72c}
.hyd-stage{height:550px;background:#d3d3d1}.hyd-stage svg{width:100%;height:100%;display:block}
.hyd-bottom{height:70px;background:#f1f1ef;border-top:1px solid #bfc1c4;display:flex;justify-content:space-between;gap:22px;align-items:center;padding:0 18px;font-size:13px}.hyd-bottom #hyd-motion{font-weight:700}.hyd-bottom #hyd-note{max-width:58%;color:#60646b;text-align:right;font-size:12px}
.flow{fill:none;stroke-linecap:round;stroke-linejoin:round}.active{stroke-dasharray:11 8;animation:dash 1s linear infinite}.inactive{opacity:.27}.node-label{font-size:13px;fill:#26282d;font-weight:650}.tiny{font-size:10px;fill:#4f545b}.mode-label{font-size:24px;font-weight:750;fill:#292b30}.value-label{font-size:18px;font-weight:650;fill:#3e4248}.component{fill:#f6f6f4;stroke:#5c6169;stroke-width:1.6}.active-component{fill:#fff6e8;stroke:#f28e1c;stroke-width:3}.machine{fill:#d79b28;stroke:#6e511a;stroke-width:2}.machine-dark{fill:#22252a;stroke:#111318;stroke-width:2}.metal{fill:#eceff1;stroke:#60646b;stroke-width:1.6}.cyl-body{fill:#d2d6da;stroke:#555b62;stroke-width:1.4}.cyl-fluid-p{fill:#d84030;opacity:.95}.cyl-fluid-r{fill:#2a63b8;opacity:.95}.cyl-fluid-y{fill:#e1c22b;opacity:.95}.callout{fill:#f7f7f4;stroke:#878b91;stroke-width:1}.callout-title{font-size:12px;font-weight:750;fill:#24272c}.callout-txt{font-size:10px;fill:#4a4f56}.controlbar{fill:#396fc0;stroke:#234b85;stroke-width:1}.pill{fill:#f1f1ef;stroke:#6a7079;stroke-width:1}.highlight{filter:drop-shadow(0 0 6px #f28e1c80)}
@keyframes dash{to{stroke-dashoffset:-38}}
</style>
<script>
const D=__DATA__;
const SVG=document.getElementById('scene'), NS='http://www.w3.org/2000/svg';
const COLORS={pressure:'#d84030',return:'#2a63b8',pilot:'#d6b72c',suction:'#4e9b57',drain:'#e58b32',inactive:'#777d86'};
const activeSets={pressure:new Set(D.pressure||[]),return:new Set(D.return||[]),pilot:new Set(D.pilot||[]),suction:new Set(D.suction||[]),drain:new Set(D.drain||[])};
const activeComp=new Set(D.active_components||[]);
document.getElementById('hyd-title').textContent=D.machine+' · '+D.subsystem;
document.getElementById('hyd-sub').textContent='Estado: '+D.state+' · vista funcional animada';
document.getElementById('hyd-motion').textContent=D.motion||'';
document.getElementById('hyd-note').textContent=(D.notes&&D.notes.length)?D.notes[0]:'Modelo didáctico original: interpreta función y recorridos; para servicio se debe contrastar con documentación del fabricante.';
function el(tag,attrs={},parent=SVG){const n=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));parent.appendChild(n);return n}
function txt(x,y,s,cls='node-label',parent=SVG,anchor='middle'){const t=el('text',{x,y,class:cls,'text-anchor':anchor},parent);t.textContent=s;return t}
function rect(x,y,w,h,cls='component',rx=6,parent=SVG){return el('rect',{x,y,width:w,height:h,rx,class:cls},parent)}
function circle(x,y,r,cls='component',parent=SVG){return el('circle',{cx:x,cy:y,r,class:cls},parent)}
function path(id,d,role='inactive',width=5,parent=SVG){let active=false;if(activeSets[role])active=activeSets[role].has(id);const p=el('path',{d,stroke:COLORS[role]||COLORS.inactive,'stroke-width':width,class:'flow '+(active?'active':'inactive'),'data-id':id},parent);return p}
function component(x,y,w,h,label,key,sub=''){const g=el('g');rect(x,y,w,h,activeComp.has(key)?'active-component':'component',7,g);txt(x+w/2,y+h/2-2,label,'node-label',g);if(sub)txt(x+w/2,y+h/2+14,sub,'tiny',g);return g}
function arrow(x1,y1,x2,y2,color='#4d5259',w=2){el('line',{x1,y1,x2,y2,stroke:color,'stroke-width':w,'marker-end':'url(#arrow)'})}
const defs=el('defs');const marker=el('marker',{id:'arrow',viewBox:'0 0 10 10',refX:8,refY:5,markerWidth:6,markerHeight:6,orient:'auto-start-reverse'},defs);el('path',{d:'M0 0 L10 5 L0 10 z',fill:'#4d5259'},marker);

function machineTruck(){
 const g=el('g',{transform:'translate(50 42)'});
 rect(0,55,270,66,'machine',4,g);rect(6,8,78,58,'machine',3,g);rect(14,18,54,30,'machine-dark',2,g);
 for(const wx of [55,175,232]){circle(wx,132,36,'machine-dark',g);circle(wx,132,16,'machine',g)}
 const bed=el('g',{id:'truck-bed',transform:'translate(118 44) rotate('+(D.subsystem==='Levante de tolva'?(8+Math.max(0,D.machine_value||0)*43):8)+' 20 80)'},g);
 el('path',{d:'M0 15 L165 0 L205 50 L18 72 Z',class:'machine'},bed);rect(8,54,184,9,'machine',2,bed);
 const ang=D.subsystem==='Levante de tolva'?Math.round(15+Math.max(0,D.machine_value||0)*40):15;txt(144,194,'Dump angle: '+ang+'°','value-label',g);
 txt(144,218,D.state,'mode-label',g);
 // hoist cylinder
 el('line',{x1:137,y1:111,x2:188,y2:55,stroke:'#8f949b','stroke-width':9,'stroke-linecap':'round'},g);el('line',{x1:137,y1:111,x2:176,y2:67,stroke:'#eceff1','stroke-width':4,'stroke-linecap':'round'},g);
 return g;
}
function machineLoader(){
 const g=el('g',{transform:'translate(35 45)'});
 rect(12,73,168,55,'machine',4,g);rect(50,18,74,62,'machine',3,g);rect(62,28,49,34,'machine-dark',2,g);rect(176,78,105,48,'machine',4,g);
 for(const wx of [58,228]){circle(wx,142,36,'machine-dark',g);circle(wx,142,15,'machine',g)}
 const lift=(D.subsystem==='Levante de brazos'?(D.machine_value||0):0);const tilt=(D.subsystem==='Inclinación de balde'?(D.machine_value||0):0);
 const armY=80-lift*35;el('line',{x1:235,y1:79,x2:340,y2:armY,stroke:'#d79b28','stroke-width':18,'stroke-linecap':'round'},g);el('line',{x1:235,y1:97,x2:345,y2:armY+22,stroke:'#d79b28','stroke-width':12,'stroke-linecap':'round'},g);
 const bx=337,by=armY-3;el('path',{d:`M${bx} ${by} L${bx+72} ${by-5-tilt*18} L${bx+92} ${by+55-tilt*10} L${bx+20} ${by+45} Z`,class:'machine'},g);
 el('line',{x1:210,y1:112,x2:294,y2:armY+15,stroke:'#eceff1','stroke-width':7,'stroke-linecap':'round'},g);el('line',{x1:210,y1:112,x2:278,y2:armY+22,stroke:'#7a8087','stroke-width':12,'stroke-linecap':'round'},g);
 txt(210,198,D.state,'mode-label',g);return g;
}
function machineStationary(){
 const g=el('g',{transform:'translate(38 48)'});rect(0,96,104,90,'machine-dark',4,g);txt(52,191,'DEPÓSITO','tiny',g);circle(148,129,31,'component',g);txt(148,134,'BOMBA','tiny',g);rect(190,106,76,46,'component',5,g);txt(228,126,'VÁLVULA','tiny',g);
 const v=D.machine_value||0;rect(296,94,132,68,'cyl-body',8,g);rect(312,106,52,44,'cyl-fluid-p',4,g);el('line',{x1:361,y1:128,x2:445+v*35,y2:128,stroke:'#e9ecef','stroke-width':14,'stroke-linecap':'round'},g);el('line',{x1:361,y1:128,x2:445+v*35,y2:128,stroke:'#656b72','stroke-width':2},g);txt(360,187,D.subsystem,'value-label',g);txt(360,214,D.state,'mode-label',g);return g;
}
function cylinderCutaway(x,y,kind='hoist'){
 const g=el('g',{transform:`translate(${x} ${y})`});rect(0,0,90,240,'cyl-body',9,g);const val=D.machine_value||0;
 let split=120-val*55;split=Math.max(45,Math.min(195,split));rect(8,8,74,split-8,activeSets.pressure.size?'cyl-fluid-p':'cyl-fluid-y',5,g);rect(8,split,74,232-split,activeSets.return.size?'cyl-fluid-r':'cyl-fluid-y',5,g);rect(5,split-5,80,10,'metal',2,g);el('line',{x1:45,y1:split,x2:45,y2:280,stroke:'#eceff1','stroke-width':15},g);el('line',{x1:45,y1:split,x2:45,y2:280,stroke:'#596069','stroke-width':2},g);txt(45,302,kind==='hoist'?'Actuador':'Cilindro','tiny',g);return g;
}
function baseCircuit(){
 // generic stationary power path
 component(80,390,95,65,'Depósito','Depósito','TANK');component(210,390,90,65,'Bomba','Bomba','PUMP');component(340,390,95,65,'Alivio','Alivio','RELIEF');component(485,380,135,85,'Direccional','Direccional 4/3','P T A B');component(685,365,150,115,'Actuador','Cilindro','A / B');component(900,390,95,65,'Filtro','Filtro de retorno','RETURN');
 path('tank-pump','M175 423 L210 423','suction');path('pump-relief','M300 410 L340 410','pressure');path('relief-valve','M435 410 L485 410','pressure');path('valve-A','M620 398 L685 398','pressure');path('A-cylinder','M685 398 L715 398','pressure');path('cylinder-B','M715 447 L620 447','return');path('B-valve','M620 447 L620 447','return');path('valve-filter','M485 447 L460 500 L900 500 L900 455','return');path('filter-tank','M900 423 L995 423 L995 520 L128 520 L128 455','return');path('valve-B','M620 447 L685 447','pressure');path('B-cylinder','M685 447 L715 447','pressure');path('cylinder-A','M715 398 L620 398','return');path('A-valve','M620 398 L620 398','return');
}
function truckHoistCircuit(){
 component(65,390,90,62,'Bomba','Bomba de implementos','P');component(205,380,120,82,'Hoist valve','Válvula de levante','RAISE / HOLD / FLOAT / LOWER');component(380,375,110,92,'Load check','Load check','');component(535,375,130,92,'Overcenter','Control overcenter/descenso','');component(735,350,135,140,'Hoist cylinders','Cilindros de levante','HEAD / ROD');component(930,390,92,62,'Tanque','Retorno','T');
 path('pump-hoist','M155 410 L205 410','pressure');path('hoist-loadcheck','M325 395 L380 395','pressure');path('loadcheck-head','M490 395 L535 395','pressure');path('hoist-overcenter','M325 395 L535 395','pressure');path('overcenter-head','M665 395 L735 395','pressure');path('head-hoistcyl','M735 395 L755 395','pressure');path('hoist-rod','M325 438 L735 438','pressure');path('rod-hoistcyl','M735 438 L755 438','pressure');path('hoistcyl-rod','M755 438 L665 438','return');path('rod-hoist','M665 438 L325 438','return');path('hoistcyl-head','M755 395 L665 395','return');path('head-overcenter','M665 395 L535 395','return');path('overcenter-hoist','M535 438 L325 438','return');path('hoist-tank','M325 455 L325 505 L930 505 L930 452','return');path('head-hoist','M755 395 L325 395','return');path('pilot-hoist','M265 380 L265 340 L380 340','pilot',3);path('pilot-overcenter','M265 380 L265 330 L600 330 L600 375','pilot',3);path('pilot-float','M265 380 L265 330 L735 330','pilot',3);path('pilot-lower','M265 380 L265 335 L535 335','pilot',3);
}
function steeringCircuit(){
 component(70,405,105,65,'Bomba / prioridad','Bomba/prioridad','P');component(245,385,125,92,'HMU','HMU','L / R / LS');component(430,375,120,110,'Cross-over','Cross-over relief','L ↔ R');component(650,348,125,145,'Cilindro L','Cilindro L','');component(810,348,125,145,'Cilindro R','Cilindro R','');component(1000,405,90,65,'Tanque','Retorno','T');
 path('pump-priority','M175 425 L245 425','pressure');path('priority-hmu','M175 425 L245 425','pressure');path('hmu-L','M370 402 L650 402','pressure');path('L-steercyl','M650 402 L670 402','pressure');path('hmu-R','M370 445 L810 445','pressure');path('R-steercyl','M810 445 L830 445','pressure');path('steercyl-R','M830 445 L370 445','return');path('R-hmu','M370 445 L330 445','return');path('steercyl-L','M670 402 L370 402','return');path('L-hmu','M370 402 L330 402','return');path('hmu-tank','M305 477 L305 520 L1000 520 L1000 470','return');path('hmu-LS','M305 385 L305 330 L150 330','pilot',3);path('LS-priority','M150 330 L120 405','pilot',3);
 path('pump-steer','M175 425 L245 425','pressure');path('steer-L','M370 402 L650 402','pressure');path('L-artcyl','M650 402 L670 402','pressure');path('steer-R','M370 445 L810 445','pressure');path('R-artcyl','M810 445 L830 445','pressure');path('artcyl-R','M830 445 L370 445','return');path('R-steer','M370 445 L330 445','return');path('artcyl-L','M670 402 L370 402','return');path('L-steer','M370 402 L330 402','return');path('steer-tank','M305 477 L305 520 L1000 520 L1000 470','return');path('steer-LS','M305 385 L305 330 L150 330','pilot',3);
}
function loaderImplCircuit(kind='lift'){
 component(70,405,95,65,'Bomba','Bomba','P');component(225,385,125,90,'Banco','Banco implementos','P T A B');component(405,380,110,100,'Load check','Load check','');component(625,355,140,145,kind==='lift'?'Lift cylinders':'Tilt cylinder',kind==='lift'?'Cilindros de levante':'Cilindro tilt','');component(910,405,90,65,'Tanque','Retorno','T');
 const pre=kind==='lift'?'impl':'tilt';path('pump-'+pre,'M165 425 L225 425','pressure');if(kind==='lift'){path('impl-loadcheck','M350 405 L405 405','pressure');path('loadcheck-liftA','M515 405 L625 405','pressure');path('liftA-cyl','M625 405 L650 405','pressure');path('impl-liftB','M350 450 L625 450','pressure');path('liftB-cyl','M625 450 L650 450','pressure');path('liftB-impl','M650 450 L350 450','return');path('liftA-impl','M650 405 L350 405','return');path('impl-tank','M285 475 L285 520 L910 520 L910 470','return');path('pilot-lift','M285 385 L285 335 L405 335','pilot',3);path('pilot-lower','M285 385 L285 335 L525 335','pilot',3);path('pilot-float','M285 385 L285 335 L650 335','pilot',3)}else{path('tilt-A','M350 405 L625 405','pressure');path('A-tiltcyl','M625 405 L650 405','pressure');path('tilt-B','M350 450 L625 450','pressure');path('B-tiltcyl','M625 450 L650 450','pressure');path('tiltcyl-B','M650 450 L350 450','return');path('B-tilt','M350 450 L300 450','return');path('tiltcyl-A','M650 405 L350 405','return');path('A-tilt','M350 405 L300 405','return');path('tilt-tank','M285 475 L285 520 L910 520 L910 470','return');path('pilot-rollback','M285 385 L285 335 L525 335','pilot',3);path('pilot-dump','M285 385 L285 335 L650 335','pilot',3)}
}
function brakeCircuit(){component(80,405,95,65,'Bomba','Bomba','P');component(235,372,120,100,'Acumuladores','Acumuladores','ENERGÍA');component(410,380,125,90,'Brake valve','Válvula de freno','');component(620,350,135,145,'Frenos','Frenos / cooler','');component(835,390,100,75,'Filtro','Filtro','');component(990,405,90,65,'Tanque','Retorno','T');path('pump-accum','M175 425 L235 425','pressure');path('accum-brakevalve','M355 405 L410 405','pressure');path('brakevalve-brakes','M535 405 L620 405','pressure');path('brakes-tank','M620 455 L990 455','return');path('pump-cooler','M175 425 L410 425 L410 455 L620 455','pressure');path('cooler-brakes','M620 455 L650 455','pressure');path('brakes-filter','M755 455 L835 425','return');path('filter-tank','M935 425 L990 425','return')}

// background panels similar to a technical animation workspace
rect(20,20,470,260,'callout',10);rect(510,20,670,260,'callout',10);txt(38,42,'MÁQUINA / MOVIMIENTO','callout-title',SVG,'start');txt(528,42,'ACTUADOR / ESTADO HIDRÁULICO','callout-title',SVG,'start');
if(D.machine==='Camión minero'){machineTruck();cylinderCutaway(800,30,'hoist')} else if(D.machine==='Cargador frontal'){machineLoader();cylinderCutaway(825,30,'implemento')} else {machineStationary();cylinderCutaway(835,30,'cilindro')}
rect(20,300,1160,270,'callout',10);txt(38,324,'PLANO FUNCIONAL · recorridos activos animados','callout-title',SVG,'start');
if(D.machine==='Sistema estacionario')baseCircuit();
else if(D.machine==='Camión minero'&&D.subsystem==='Levante de tolva')truckHoistCircuit();
else if((D.machine==='Camión minero'&&D.subsystem==='Dirección')||(D.machine==='Cargador frontal'&&D.subsystem==='Dirección articulada'))steeringCircuit();
else if(D.machine==='Camión minero'&&D.subsystem==='Freno / enfriamiento')brakeCircuit();
else if(D.machine==='Cargador frontal'&&D.subsystem==='Levante de brazos')loaderImplCircuit('lift');
else if(D.machine==='Cargador frontal'&&D.subsystem==='Inclinación de balde')loaderImplCircuit('tilt');

// bottom pseudo-control bar in the spirit of the reference video, without copying it.
rect(325,585,550,44,'controlbar',10);txt(354,612,'CONTROLES','tiny',SVG,'start');const states=D.states||[];states.slice(0,5).forEach((s,i)=>{const x=445+i*82;rect(x,596,68,21,s===D.state?'active-component':'pill',10);txt(x+34,610,s,'tiny')});
</script>
'''
    html = html.replace('__DATA__', payload).replace('__HEIGHT__', str(int(height)))
    components.html(html, height=height, scrolling=False)
