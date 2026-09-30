from __future__ import annotations

import json
import streamlit.components.v1 as components


def render_beam_3d(payload: dict, height: int = 760) -> None:
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    html = r'''
<div id="gg-beam3d" class="gg-root">
  <div class="gg-toolbar">
    <div>
      <div class="gg-kicker">MECHLAB · VISUALIZACIÓN MECÁNICA</div>
      <div class="gg-title">Viga deformada y sección de análisis</div>
      <div class="gg-sub">El modelo 3D respeta apoyos, posición de cargas y signo de la deformada. La deformación y la sección pueden amplificarse solo para hacerlas visibles.</div>
    </div>
    <div class="gg-controls">
      <label>Color
        <select id="gg-color-mode">
          <option value="moment">Momento M(x)</option>
          <option value="neutral">Material neutro</option>
        </select>
      </label>
      <label>Amplificación de v(x)
        <select id="gg-amp">
          <option value="auto">Automática</option>
          <option value="1">1×</option>
          <option value="10">10×</option>
          <option value="50">50×</option>
          <option value="100">100×</option>
          <option value="500">500×</option>
        </select>
      </label>
      <button id="gg-reset" type="button">Restablecer vista</button>
    </div>
  </div>

  <div class="gg-grid">
    <section class="gg-scene-card">
      <div id="gg-status" class="gg-status">Cargando visor 3D…</div>
      <div id="gg-three"></div>
      <canvas id="gg-fallback" aria-label="Vista esquemática de viga deformada"></canvas>
      <div class="gg-legend">
        <span><i class="sw neg"></i>M negativo</span>
        <span><i class="sw zero"></i>M≈0</span>
        <span><i class="sw pos"></i>M positivo</span>
        <span><i class="sw cut"></i>sección x</span>
      </div>
    </section>

    <aside class="gg-side">
      <div class="gg-card gg-probe">
        <div class="gg-card-title">Sección seleccionada</div>
        <div class="gg-big"><span id="gg-x"></span> m</div>
        <div class="gg-pairs">
          <div><span>V(x)</span><b id="gg-v"></b></div>
          <div><span>M(x)</span><b id="gg-m"></b></div>
        </div>
      </div>

      <div class="gg-card">
        <div class="gg-card-title">Modelo representado</div>
        <div class="gg-model-row"><span>Apoyos</span><b id="gg-supports"></b></div>
        <div class="gg-model-row"><span>Carga</span><b id="gg-loads"></b></div>
        <div class="gg-model-row"><span>Sección</span><b id="gg-section"></b></div>
        <div id="gg-scale-note" class="gg-mini"></div>
      </div>

      <div class="gg-card">
        <div class="gg-card-title">Tensiones en el corte</div>
        <canvas id="gg-stress" aria-label="Distribución de esfuerzo normal y cortante"></canvas>
        <div class="gg-pairs">
          <div><span>|σ|max</span><b id="gg-smax"></b></div>
          <div><span>|τ|max</span><b id="gg-tmax"></b></div>
        </div>
      </div>

      <div class="gg-card gg-note"><b>Lectura física</b><br><span>La línea punteada es el eje sin deformar. La carga termina sobre la viga, la sección cobre sigue la tangente local de la deformada y el corte conecta M→σ y V→τ.</span></div>
    </aside>
  </div>
</div>

<style>
#gg-beam3d{--cu:#c8752d;--or:#f28e1c;--ink:#202126;--mut:#6d7078;--iv:#fbf7f0;--line:#ded7cc;--soft:#f2eadf;font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;color:var(--ink)}
#gg-beam3d *{box-sizing:border-box}.gg-toolbar{display:flex;justify-content:space-between;gap:18px;align-items:flex-end;margin-bottom:12px}.gg-kicker{font-size:11px;letter-spacing:.16em;font-weight:800;color:var(--cu)}.gg-title{font-size:24px;font-weight:850;line-height:1.1}.gg-sub{font-size:13px;color:var(--mut);max-width:800px;margin-top:5px}.gg-controls{display:flex;gap:8px;align-items:end;flex-wrap:wrap}.gg-controls label{font-size:11px;color:var(--mut);font-weight:700}.gg-controls select,.gg-controls button{display:block;margin-top:4px;border:1px solid var(--line);background:#fff;border-radius:9px;padding:8px 10px;font-size:12px;color:var(--ink)}.gg-controls button{background:var(--ink);color:#fff;border-color:var(--ink);cursor:pointer}.gg-grid{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(280px,.72fr);gap:12px}.gg-scene-card,.gg-card{border:1px solid var(--line);border-radius:16px;background:var(--iv);overflow:hidden}.gg-scene-card{position:relative;min-height:520px;background:linear-gradient(180deg,#2c2d31 0%,#202126 72%)}#gg-three{height:475px;width:100%}#gg-fallback{display:none;width:100%;height:475px}.gg-status{position:absolute;z-index:4;top:12px;left:12px;background:rgba(251,247,240,.94);border:1px solid rgba(222,215,204,.8);border-radius:999px;padding:6px 10px;font-size:11px;color:var(--ink)}.gg-legend{height:44px;background:#202126;color:#c8c9cc;display:flex;align-items:center;gap:18px;padding:0 15px;font-size:11px;flex-wrap:wrap}.gg-legend span{display:flex;align-items:center;gap:6px}.sw{width:20px;height:5px;border-radius:999px;display:inline-block}.sw.neg{background:#4a4b51}.sw.zero{background:#d8c8b2}.sw.pos{background:#f28e1c}.sw.cut{background:#f28e1c;width:3px;height:18px}.gg-side{display:flex;flex-direction:column;gap:12px}.gg-card{padding:14px}.gg-card-title{font-size:11px;text-transform:uppercase;letter-spacing:.12em;font-weight:850;color:var(--cu);margin-bottom:8px}.gg-big{font-size:31px;font-weight:850;line-height:1}.gg-pairs{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:11px}.gg-pairs>div{background:#fff;border:1px solid var(--line);border-radius:10px;padding:9px}.gg-pairs span,.gg-model-row span{display:block;font-size:10px;color:var(--mut);margin-bottom:3px}.gg-pairs b{font-size:13px}.gg-model-row{padding:7px 0;border-bottom:1px solid #e8e0d6}.gg-model-row:last-of-type{border-bottom:0}.gg-model-row b{font-size:12px;font-weight:750}.gg-mini{font-size:10px;color:var(--mut);margin-top:8px;line-height:1.35}.gg-note{font-size:11px;line-height:1.45;background:#f4eadc}.gg-note b{color:var(--cu)}#gg-stress{width:100%;height:205px;display:block}
@media(max-width:950px){.gg-grid{grid-template-columns:1fr}.gg-toolbar{align-items:flex-start;flex-direction:column}.gg-side{display:grid;grid-template-columns:1fr 1fr}.gg-side .gg-note{grid-column:1/-1}}
@media(max-width:620px){#gg-three,#gg-fallback{height:385px}.gg-title{font-size:20px}.gg-side{display:grid;grid-template-columns:1fr}.gg-controls{width:100%}}
</style>

<script type="module">
const DATA=__DATA__;
const root=document.getElementById('gg-beam3d');
const status=root.querySelector('#gg-status');
const threeHost=root.querySelector('#gg-three');
const fallback=root.querySelector('#gg-fallback');
const stressCanvas=root.querySelector('#gg-stress');
const colorMode=root.querySelector('#gg-color-mode');
const ampSelect=root.querySelector('#gg-amp');

root.querySelector('#gg-x').textContent=DATA.x_probe.toFixed(3);
root.querySelector('#gg-v').textContent=DATA.probe.V.toFixed(3)+' kN';
root.querySelector('#gg-m').textContent=DATA.probe.M.toFixed(3)+' kN·m';
root.querySelector('#gg-smax').textContent=DATA.stress.sigma_max.toFixed(2)+' MPa';
root.querySelector('#gg-tmax').textContent=DATA.stress.tau_max==null?'—':DATA.stress.tau_max.toFixed(2)+' MPa';

function supportText(){
  const names={fixed:'empotramiento',pin:'pasador',roller:'rodillo'};
  return DATA.supports.map(s=>`${s.label}: ${names[s.kind]||s.kind}`).join(' · ');
}
function loadText(){
  return DATA.loads.map(ld=>{
    if(ld.kind==='point') return `${ld.label}=${ld.value.toFixed(2)} kN en x=${ld.x.toFixed(2)} m`;
    if(ld.kind==='udl') return `${ld.label}=${ld.value.toFixed(2)} kN/m entre ${ld.x0.toFixed(2)}–${ld.x1.toFixed(2)} m`;
    return `${ld.label}=${ld.value.toFixed(2)} kN·m en x=${ld.x.toFixed(2)} m`;
  }).join(' · ') || 'sin carga representable';
}
function sectionText(){
  const s=DATA.section;
  if(s.kind==='rect') return `${s.label} · ${s.b_mm.toFixed(0)}×${s.h_mm.toFixed(0)} mm`;
  if(s.kind==='solid_circle') return `${s.label} · Ø${s.d_mm.toFixed(0)} mm`;
  if(s.kind==='tube') return `${s.label} · Ø${s.do_mm.toFixed(0)} mm · t=${s.t_mm.toFixed(1)} mm`;
  return s.label;
}
root.querySelector('#gg-supports').textContent=supportText();
root.querySelector('#gg-loads').textContent=loadText();
root.querySelector('#gg-section').textContent=sectionText();
if(DATA.section.geometry_known && DATA.section.visual_scale>1.05){
  root.querySelector('#gg-scale-note').textContent=`La sección se muestra ${DATA.section.visual_scale.toFixed(1)}× mayor solo para legibilidad 3D; su proporción b/h o D/t se conserva.`;
}else if(!DATA.section.geometry_known){
  root.querySelector('#gg-scale-note').textContent='A e I no definen una forma única: el sólido se muestra como prisma genérico y no debe interpretarse como la sección real.';
}

function stressPlot(){
  const c=stressCanvas,dpr=Math.max(1,Math.min(2,devicePixelRatio||1));
  const w=c.clientWidth||280,h=205;c.width=w*dpr;c.height=h*dpr;const g=c.getContext('2d');g.scale(dpr,dpr);g.clearRect(0,0,w,h);
  g.fillStyle='#fbf7f0';g.fillRect(0,0,w,h);g.strokeStyle='#ded7cc';g.strokeRect(.5,.5,w-1,h-1);
  const pad={l:34,r:12,t:20,b:22},iw=w-pad.l-pad.r,ih=h-pad.t-pad.b;
  const y=DATA.stress.y_mm,s=DATA.stress.sigma_mpa,t=DATA.stress.tau_mpa;
  const ymax=Math.max(...y.map(Math.abs),1),xmax=Math.max(...s.map(Math.abs),...t.map(Math.abs),1);
  const X=v=>pad.l+(v+xmax)/(2*xmax)*iw,Y=v=>pad.t+(ymax-v)/(2*ymax)*ih;
  g.strokeStyle='#aaa59d';g.lineWidth=1;g.beginPath();g.moveTo(X(0),pad.t);g.lineTo(X(0),pad.t+ih);g.moveTo(pad.l,Y(0));g.lineTo(pad.l+iw,Y(0));g.stroke();
  function line(arr,col,dash=[]){g.strokeStyle=col;g.lineWidth=2;g.setLineDash(dash);g.beginPath();arr.forEach((v,i)=>{const a=X(v),b=Y(y[i]);i?g.lineTo(a,b):g.moveTo(a,b)});g.stroke();g.setLineDash([])}
  line(s,'#c8752d');line(t,'#202126',[5,4]);
  g.font='11px system-ui';g.fillStyle='#6d7078';g.fillText('σx',pad.l+3,14);g.fillText('τxy',pad.l+35,14);g.fillStyle='#c8752d';g.fillRect(pad.l-10,7,8,3);g.fillStyle='#202126';g.fillRect(pad.l+24,7,8,3);
}
stressPlot();

function ampValue(){return ampSelect.value==='auto'?DATA.auto_amplification:Number(ampSelect.value)}
function interp(arrX,arrY,x){
  if(x<=arrX[0])return arrY[0]; if(x>=arrX[arrX.length-1])return arrY[arrY.length-1];
  let lo=0;while(lo<arrX.length-2&&arrX[lo+1]<x)lo++;
  const t=(x-arrX[lo])/(arrX[lo+1]-arrX[lo]);return arrY[lo]*(1-t)+arrY[lo+1]*t;
}
function defY(x,amp){return interp(DATA.x,DATA.deflection,x)*amp}
function tangentAt(x,amp){
  const eps=Math.max(DATA.length*0.003,1e-6),x0=Math.max(DATA.x[0],x-eps),x1=Math.min(DATA.x[DATA.x.length-1],x+eps);
  const dy=defY(x1,amp)-defY(x0,amp),dx=Math.max(x1-x0,1e-9);return {x:1,y:dy/dx};
}

function drawFallback(){
  threeHost.style.display='none';fallback.style.display='block';status.textContent='Vista 2D de respaldo';
  const dpr=Math.max(1,Math.min(2,devicePixelRatio||1)),w=fallback.clientWidth||700,h=fallback.clientHeight||475;fallback.width=w*dpr;fallback.height=h*dpr;const g=fallback.getContext('2d');g.scale(dpr,dpr);g.clearRect(0,0,w,h);g.fillStyle='#202126';g.fillRect(0,0,w,h);
  const pad=55,iw=w-2*pad,mid=h*.52,L=Math.max(DATA.length,1e-9),def=DATA.deflection,amp=ampValue();const maxd=Math.max(...def.map(Math.abs),1e-9);const sy=Math.min(h*.25/(maxd*amp),1);const X=x=>pad+x/L*iw,Y=v=>mid-v*amp*sy;
  g.strokeStyle='#7a7b80';g.lineWidth=2;g.setLineDash([5,6]);g.beginPath();DATA.x.forEach((x,i)=>i?g.lineTo(X(x),mid):g.moveTo(X(x),mid));g.stroke();g.setLineDash([]);
  const mmax=Math.max(...DATA.moment.map(Math.abs),1e-9);for(let i=0;i<DATA.x.length-1;i++){const mn=(DATA.moment[i]+DATA.moment[i+1])/(2*mmax);g.strokeStyle=colorMode.value==='neutral'?'#e8d9c3':(mn>=0?`rgb(${Math.round(216+37*Math.min(mn,1))},${Math.round(200-58*Math.min(mn,1))},${Math.round(178-150*Math.min(mn,1))})`:'#55565c');g.lineWidth=8;g.beginPath();g.moveTo(X(DATA.x[i]),Y(def[i]));g.lineTo(X(DATA.x[i+1]),Y(def[i+1]));g.stroke()}
  const xp=X(DATA.x_probe);g.strokeStyle='#f28e1c';g.lineWidth=3;g.beginPath();g.moveTo(xp,mid-h*.18);g.lineTo(xp,mid+h*.18);g.stroke();
  g.fillStyle='#fbf7f0';g.font='12px system-ui';g.fillText('línea punteada: eje sin deformar',pad,24);g.fillStyle='#f28e1c';g.fillText('x = '+DATA.x_probe.toFixed(3)+' m',Math.min(xp+7,w-105),mid-h*.18+12);
}

let scene,camera,renderer,controls,THREE,OrbitControls,beamGroup;
function momentColor(v,mmax){if(colorMode.value==='neutral')return new THREE.Color('#d8c8b2');const r=mmax?Math.max(-1,Math.min(1,v/mmax)):0;if(r>=0)return new THREE.Color().lerpColors(new THREE.Color('#d8c8b2'),new THREE.Color('#f28e1c'),r);return new THREE.Color().lerpColors(new THREE.Color('#d8c8b2'),new THREE.Color('#38393e'),-r)}

function dims(){
  const s=DATA.section,vs=s.visual_scale||1;
  if(s.kind==='rect') return {kind:'rect',h:s.h_m*vs,b:s.b_m*vs};
  if(s.kind==='solid_circle') return {kind:'solid_circle',d:s.d_m*vs,h:s.d_m*vs,b:s.d_m*vs};
  if(s.kind==='tube') return {kind:'tube',do:s.do_m*vs,di:s.di_m*vs,h:s.do_m*vs,b:s.do_m*vs};
  const q=DATA.length*.045;return {kind:'custom',h:q,b:q};
}
function orientX(obj,dir){obj.quaternion.setFromUnitVectors(new THREE.Vector3(1,0,0),dir.clone().normalize())}
function orientY(obj,dir){obj.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.clone().normalize())}

function beamSegment(a,b,color,sd){
  const mid=a.clone().add(b).multiplyScalar(.5),dir=b.clone().sub(a),len=dir.length();
  const mat=new THREE.MeshStandardMaterial({color,metalness:.05,roughness:.62});
  let mesh;
  if(sd.kind==='rect'||sd.kind==='custom'){
    mesh=new THREE.Mesh(new THREE.BoxGeometry(len,sd.h,sd.b),mat);orientX(mesh,dir);
  }else if(sd.kind==='solid_circle'){
    mesh=new THREE.Mesh(new THREE.CylinderGeometry(sd.d/2,sd.d/2,len,24,1,false),mat);orientY(mesh,dir);
  }else{
    const grp=new THREE.Group();
    const outer=new THREE.Mesh(new THREE.CylinderGeometry(sd.do/2,sd.do/2,len,28,1,true),mat);orientY(outer,dir);grp.add(outer);
    if(sd.di>0){const imat=new THREE.MeshStandardMaterial({color:'#17181b',side:THREE.BackSide,roughness:.9});const inner=new THREE.Mesh(new THREE.CylinderGeometry(sd.di/2,sd.di/2,len*1.002,28,1,true),imat);orientY(inner,dir);grp.add(inner)}
    mesh=grp;
  }
  mesh.position.copy(mid);return mesh;
}

function addFixedSupport(x,isRight,sd){
  const t=Math.max(DATA.length*.018,sd.h*.25),hh=Math.max(sd.h*3.6,DATA.length*.11),bb=Math.max(sd.b*3.2,DATA.length*.13);
  const m=new THREE.Mesh(new THREE.BoxGeometry(t,hh,bb),new THREE.MeshStandardMaterial({color:'#c8752d',roughness:.75}));
  m.position.set(x+(isRight?t/2:-t/2),0,0);scene.add(m);
}
function addSimpleSupport(x,kind,sd){
  const h=Math.max(sd.h*2.4,DATA.length*.065),w=Math.max(sd.b*2.8,DATA.length*.07),beamBottom=-sd.h/2;
  const shape=new THREE.Shape();shape.moveTo(-w/2,-h);shape.lineTo(w/2,-h);shape.lineTo(0,0);shape.closePath();
  const geom=new THREE.ExtrudeGeometry(shape,{depth:Math.max(sd.b*1.3,w*.42),bevelEnabled:false});geom.translate(0,0,-Math.max(sd.b*1.3,w*.42)/2);
  const tri=new THREE.Mesh(geom,new THREE.MeshStandardMaterial({color:'#c8752d',roughness:.8}));tri.position.set(x,beamBottom,0);scene.add(tri);
  if(kind==='roller'){
    const rz=-Math.max(sd.b*1.3,w*.42)*.32;for(const dz of [rz,-rz]){const r=new THREE.Mesh(new THREE.CylinderGeometry(w*.10,w*.10,Math.max(sd.b*.7,w*.22),18),new THREE.MeshStandardMaterial({color:'#e7d6bd',roughness:.65}));r.rotation.x=Math.PI/2;r.position.set(x,beamBottom-h-w*.11,dz);scene.add(r)}
  }
}
function addPointArrow(x,value,amp,sd){
  const y=defY(x,amp),down=value>=0,beamTop=y+(down?sd.h/2:-sd.h/2),gap=Math.max(DATA.length*.025,sd.h*.55),len=Math.max(DATA.length*.115,sd.h*2.5);
  const origin=new THREE.Vector3(x,beamTop+(down?len+gap:-(len+gap)),0),dir=new THREE.Vector3(0,down?-1:1,0);
  const arrow=new THREE.ArrowHelper(dir,origin,len+gap,0xf28e1c,Math.min(len*.28,DATA.length*.035),Math.min(len*.14,DATA.length*.018));scene.add(arrow);
}
function addUDL(ld,amp,sd){
  const n=9,tops=[];for(let i=0;i<n;i++){const x=ld.x0+(ld.x1-ld.x0)*i/(n-1),y=defY(x,amp),down=ld.value>=0,beamTop=y+(down?sd.h/2:-sd.h/2),gap=Math.max(DATA.length*.02,sd.h*.5),len=Math.max(DATA.length*.09,sd.h*2.2);const oy=beamTop+(down?len+gap:-(len+gap));tops.push(new THREE.Vector3(x,oy,0));const arrow=new THREE.ArrowHelper(new THREE.Vector3(0,down?-1:1,0),new THREE.Vector3(x,oy,0),len+gap,0xf28e1c,Math.min(len*.27,DATA.length*.03),Math.min(len*.13,DATA.length*.016));scene.add(arrow)}
  const rail=new THREE.Line(new THREE.BufferGeometry().setFromPoints(tops),new THREE.LineBasicMaterial({color:'#f28e1c'}));scene.add(rail);
}
function addMoment(ld,amp,sd){
  const x=ld.x,y=defY(x,amp),r=Math.max(DATA.length*.055,sd.h*1.6),tube=Math.max(DATA.length*.004,sd.h*.09),positive=ld.value>=0;
  const arc=new THREE.Mesh(new THREE.TorusGeometry(r,tube,10,46,Math.PI*1.55),new THREE.MeshStandardMaterial({color:'#f28e1c'}));arc.position.set(x,y,0);arc.rotation.z=positive?Math.PI*.18:Math.PI*1.36;scene.add(arc);
  const a=positive?Math.PI*1.73:Math.PI*.18;const p=new THREE.Vector3(x+r*Math.cos(a),y+r*Math.sin(a),0);const tangent=new THREE.Vector3(-Math.sin(a),Math.cos(a),0).multiplyScalar(positive?1:-1).normalize();const cone=new THREE.Mesh(new THREE.ConeGeometry(tube*2.4,tube*5.5,12),new THREE.MeshStandardMaterial({color:'#f28e1c'}));orientY(cone,tangent);cone.position.copy(p);scene.add(cone);
}

function addCut(x,amp,sd){
  const y=defY(x,amp),tan=tangentAt(x,amp),dir=new THREE.Vector3(1,tan.y,0).normalize(),q=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(1,0,0),dir),th=Math.max(DATA.length*.005,sd.h*.08),mat=new THREE.MeshStandardMaterial({color:'#f28e1c',transparent:true,opacity:.58,side:THREE.DoubleSide,roughness:.55});
  let cut;
  if(sd.kind==='rect'||sd.kind==='custom') cut=new THREE.Mesh(new THREE.BoxGeometry(th,sd.h*1.12,sd.b*1.12),mat);
  else if(sd.kind==='solid_circle'){cut=new THREE.Mesh(new THREE.CylinderGeometry(sd.d*.56,sd.d*.56,th,32,1,false),mat);orientY(cut,new THREE.Vector3(1,0,0))}
  else{const grp=new THREE.Group();const outer=new THREE.Mesh(new THREE.CylinderGeometry(sd.do*.56,sd.do*.56,th,32,1,true),mat);orientY(outer,new THREE.Vector3(1,0,0));grp.add(outer);if(sd.di>0){const inner=new THREE.Mesh(new THREE.CylinderGeometry(sd.di*.48,sd.di*.48,th*1.02,32,1,true),new THREE.MeshStandardMaterial({color:'#202126',side:THREE.BackSide}));orientY(inner,new THREE.Vector3(1,0,0));grp.add(inner)}cut=grp}
  cut.quaternion.premultiply(q);cut.position.set(x,y,0);scene.add(cut);
  // short normal marker instead of a giant plane
  const normal=new THREE.ArrowHelper(dir,new THREE.Vector3(x,y,0),Math.max(DATA.length*.075,sd.h*2.0),0xf28e1c,DATA.length*.018,DATA.length*.009);scene.add(normal);
}

function buildScene(){
  while(scene.children.length)scene.remove(scene.children[0]);
  scene.background=new THREE.Color('#202126');scene.add(new THREE.HemisphereLight('#fff7e9','#313238',2.15));const dl=new THREE.DirectionalLight('#ffffff',2.25);dl.position.set(DATA.length*.25,DATA.length*.55,DATA.length*.65);scene.add(dl);
  const L=Math.max(DATA.length,1e-9),amp=ampValue(),sd=dims(),mmax=Math.max(...DATA.moment.map(Math.abs),1e-9);
  const baseMat=new THREE.LineDashedMaterial({color:'#7b7c82',dashSize:L*.025,gapSize:L*.018});const baseGeo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0),new THREE.Vector3(L,0,0)]);const baseLine=new THREE.Line(baseGeo,baseMat);baseLine.computeLineDistances();scene.add(baseLine);
  const grid=new THREE.GridHelper(L*1.28,12,0x494a4f,0x34353a);grid.position.set(L*.5,-Math.max(L*.16,sd.h*3.2),0);scene.add(grid);
  beamGroup=new THREE.Group();scene.add(beamGroup);
  for(let i=0;i<DATA.x.length-1;i++){
    const a=new THREE.Vector3(DATA.x[i],DATA.deflection[i]*amp,0),b=new THREE.Vector3(DATA.x[i+1],DATA.deflection[i+1]*amp,0),col=momentColor((DATA.moment[i]+DATA.moment[i+1])/2,mmax);beamGroup.add(beamSegment(a,b,col,sd));
  }
  DATA.supports.forEach((s,i)=>{if(s.kind==='fixed')addFixedSupport(s.x,s.x>DATA.length/2,sd);else addSimpleSupport(s.x,s.kind,sd)});
  DATA.loads.forEach(ld=>{if(ld.kind==='point')addPointArrow(ld.x,ld.value,amp,sd);else if(ld.kind==='udl')addUDL(ld,amp,sd);else addMoment(ld,amp,sd)});
  addCut(DATA.x_probe,amp,sd);
}
function resetCamera(){const L=Math.max(DATA.length,1e-9);camera.position.set(L*.58,L*.36,L*.72);controls.target.set(L*.50,-L*.02,0);controls.update()}
async function start3D(){
  try{
    THREE=await import('https://cdn.jsdelivr.net/npm/three@0.180.0/+esm');
    ({OrbitControls}=await import('https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/OrbitControls.js/+esm'));
    scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(39,1,.001,10000);renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.outputColorSpace=THREE.SRGBColorSpace;threeHost.appendChild(renderer.domElement);controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.minDistance=DATA.length*.23;controls.maxDistance=DATA.length*3;buildScene();resetCamera();status.textContent='3D interactivo · arrastra para girar';
    function resize(){const w=threeHost.clientWidth,h=threeHost.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()}resize();new ResizeObserver(resize).observe(threeHost);
    function loop(){controls.update();renderer.render(scene,camera);requestAnimationFrame(loop)}loop();
    colorMode.addEventListener('change',buildScene);ampSelect.addEventListener('change',buildScene);root.querySelector('#gg-reset').addEventListener('click',resetCamera);
  }catch(e){console.warn(e);drawFallback();colorMode.addEventListener('change',drawFallback);ampSelect.addEventListener('change',drawFallback);root.querySelector('#gg-reset').addEventListener('click',drawFallback)}
}
start3D();
</script>
'''.replace('__DATA__', data)
    components.html(html, height=height, scrolling=False)
