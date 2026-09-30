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
      <label>Color de la viga
        <select id="gg-color-mode">
          <option value="moment">Momento M(x)</option>
          <option value="neutral">Material neutro</option>
        </select>
      </label>
      <label>Lectura del corte 3D
        <select id="gg-stress-mode">
          <option value="both">σx + τxy</option>
          <option value="sigma">Tensión normal σx</option>
          <option value="tau">Tensión de corte τxy</option>
          <option value="neutral">Sección neutra</option>
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
      <div class="gg-view-controls" aria-label="Vistas del modelo 3D">
        <span>Vista</span>
        <button id="gg-front" class="gg-view-btn is-active" type="button">Frente</button>
        <button id="gg-iso" class="gg-view-btn" type="button">Isométrica</button>
        <button id="gg-section-view" class="gg-view-btn" type="button">Sección</button>
        <button id="gg-fit" class="gg-view-btn" type="button">Ajustar</button>
      </div>
      <button id="gg-reset" type="button">Restablecer</button>
    </div>
  </div>

  <div class="gg-grid">
    <section class="gg-scene-card">
      <div id="gg-status" class="gg-status">Cargando visor 3D…</div>
      <div class="gg-help">Izq.: girar · rueda: zoom · der.: desplazar</div>
      <div id="gg-three"></div>
      <canvas id="gg-fallback" aria-label="Vista esquemática de viga deformada"></canvas>
      <div class="gg-legend">
        <span><i class="sw neg"></i>M negativo</span>
        <span><i class="sw zero"></i>M≈0</span>
        <span><i class="sw pos"></i>M positivo</span>
        <span class="gg-legend-sep"></span>
        <span id="gg-cut-legend"><i class="sw cut"></i>Corte: σx por color + τxy por flechas</span>
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
        <div id="gg-stress-readout" class="gg-mini gg-stress-readout"></div>
      </div>

      <div class="gg-card gg-note"><b>Lectura física</b><br><span>La línea punteada es el eje sin deformar. En el corte, el color muestra σx cuando corresponde; las flechas muestran τxy y su sentido. La línea clara identifica el eje neutro.</span></div>
    </aside>
  </div>
</div>

<style>
#gg-beam3d{--cu:#c8752d;--or:#f28e1c;--ink:#202126;--mut:#6d7078;--iv:#fbf7f0;--line:#ded7cc;--soft:#f2eadf;font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;color:var(--ink)}
#gg-beam3d *{box-sizing:border-box}.gg-toolbar{display:flex;justify-content:space-between;gap:18px;align-items:flex-end;margin-bottom:12px}.gg-kicker{font-size:11px;letter-spacing:.16em;font-weight:800;color:var(--cu)}.gg-title{font-size:24px;font-weight:850;line-height:1.1}.gg-sub{font-size:13px;color:var(--mut);max-width:800px;margin-top:5px}.gg-controls{display:flex;gap:8px;align-items:end;flex-wrap:wrap}.gg-controls label{font-size:11px;color:var(--mut);font-weight:700}.gg-controls select,.gg-controls button{display:block;margin-top:4px;border:1px solid var(--line);background:#fff;border-radius:9px;padding:8px 10px;font-size:12px;color:var(--ink)}.gg-controls>button{background:var(--ink);color:#fff;border-color:var(--ink);cursor:pointer}.gg-view-controls{display:flex;align-items:end;gap:5px;flex-wrap:wrap}.gg-view-controls>span{width:100%;font-size:11px;color:var(--mut);font-weight:700}.gg-view-controls .gg-view-btn{margin-top:0;padding:8px 10px;background:#fff;color:var(--ink);cursor:pointer}.gg-view-controls .gg-view-btn.is-active{background:var(--cu);border-color:var(--cu);color:#fff}.gg-grid{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(280px,.72fr);gap:12px}.gg-scene-card,.gg-card{border:1px solid var(--line);border-radius:16px;background:var(--iv);overflow:hidden}.gg-scene-card{position:relative;min-height:520px;background:linear-gradient(180deg,#2c2d31 0%,#202126 72%)}#gg-three{height:475px;width:100%}#gg-fallback{display:none;width:100%;height:475px}.gg-status{position:absolute;z-index:4;top:12px;left:12px;background:rgba(251,247,240,.94);border:1px solid rgba(222,215,204,.8);border-radius:999px;padding:6px 10px;font-size:11px;color:var(--ink)}.gg-help{position:absolute;z-index:4;right:12px;top:12px;background:rgba(32,33,38,.82);border:1px solid rgba(251,247,240,.18);border-radius:999px;padding:6px 10px;font-size:10px;color:#ded7cc;pointer-events:none}.gg-legend{min-height:44px;background:#202126;color:#c8c9cc;display:flex;align-items:center;gap:14px;padding:8px 15px;font-size:11px;flex-wrap:wrap}.gg-legend span{display:flex;align-items:center;gap:6px}.gg-legend-sep{width:1px;height:20px;background:#55565c;display:inline-block}.sw{width:20px;height:5px;border-radius:999px;display:inline-block}.sw.neg{background:#4a4b51}.sw.zero{background:#d8c8b2}.sw.pos{background:#f28e1c}.sw.cut{background:linear-gradient(90deg,#34353a 0%,#e9dece 50%,#f28e1c 100%);width:28px;height:7px}.gg-stress-readout{padding-top:9px;border-top:1px solid #e8e0d6;margin-top:10px}.gg-side{display:flex;flex-direction:column;gap:12px}.gg-card{padding:14px}.gg-card-title{font-size:11px;text-transform:uppercase;letter-spacing:.12em;font-weight:850;color:var(--cu);margin-bottom:8px}.gg-big{font-size:31px;font-weight:850;line-height:1}.gg-pairs{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:11px}.gg-pairs>div{background:#fff;border:1px solid var(--line);border-radius:10px;padding:9px}.gg-pairs span,.gg-model-row span{display:block;font-size:10px;color:var(--mut);margin-bottom:3px}.gg-pairs b{font-size:13px}.gg-model-row{padding:7px 0;border-bottom:1px solid #e8e0d6}.gg-model-row:last-of-type{border-bottom:0}.gg-model-row b{font-size:12px;font-weight:750}.gg-mini{font-size:10px;color:var(--mut);margin-top:8px;line-height:1.35}.gg-note{font-size:11px;line-height:1.45;background:#f4eadc}.gg-note b{color:var(--cu)}#gg-stress{width:100%;height:205px;display:block}
@media(max-width:950px){.gg-grid{grid-template-columns:1fr}.gg-toolbar{align-items:flex-start;flex-direction:column}.gg-side{display:grid;grid-template-columns:1fr 1fr}.gg-side .gg-note{grid-column:1/-1}}
@media(max-width:620px){#gg-three,#gg-fallback{height:385px}.gg-title{font-size:20px}.gg-side{display:grid;grid-template-columns:1fr}.gg-controls{width:100%}.gg-help{display:none}.gg-view-controls{width:100%}.gg-view-controls .gg-view-btn{flex:1 1 auto}}
</style>

<script type="module">
const DATA=__DATA__;
const root=document.getElementById('gg-beam3d');
const status=root.querySelector('#gg-status');
const threeHost=root.querySelector('#gg-three');
const fallback=root.querySelector('#gg-fallback');
const stressCanvas=root.querySelector('#gg-stress');
const colorMode=root.querySelector('#gg-color-mode');
const stressMode=root.querySelector('#gg-stress-mode');
const ampSelect=root.querySelector('#gg-amp');
const cutLegend=root.querySelector('#gg-cut-legend');
const stressReadout=root.querySelector('#gg-stress-readout');

root.querySelector('#gg-x').textContent=DATA.x_probe.toFixed(3);
root.querySelector('#gg-v').textContent=DATA.probe.V.toFixed(3)+' kN';
root.querySelector('#gg-m').textContent=DATA.probe.M.toFixed(3)+' kN·m';
root.querySelector('#gg-smax').textContent=DATA.stress.sigma_max.toFixed(2)+' MPa';
root.querySelector('#gg-tmax').textContent=DATA.stress.tau_max==null?'—':DATA.stress.tau_max.toFixed(2)+' MPa';
if(!DATA.stress.shear_available){
  const tauOpt=stressMode.querySelector('option[value="tau"]');if(tauOpt)tauOpt.disabled=true;
}
function updateStressUI(){
  const mode=stressMode.value;
  if(mode==='sigma'){cutLegend.innerHTML='<i class="sw cut" style="background:linear-gradient(90deg,#34353a 0%,#eadfce 50%,#f28e1c 100%)"></i>Corte: σx · grafito=compresión · marfil≈0 · naranja=tracción';}
  else if(mode==='tau'){cutLegend.innerHTML='<i class="sw cut" style="background:linear-gradient(90deg,#eadfce 0%,#c8752d 100%)"></i>Corte: |τxy| por intensidad · flechas indican el sentido';}
  else if(mode==='neutral'){cutLegend.innerHTML='<i class="sw cut" style="background:#f28e1c"></i>Corte geométrico · sin mapa de tensiones';}
  else{cutLegend.innerHTML='<i class="sw cut" style="background:linear-gradient(90deg,#34353a 0%,#eadfce 50%,#f28e1c 100%)"></i>Corte: σx por color + τxy por flechas';}
  const top=DATA.stress.sigma_top,bot=DATA.stress.sigma_bottom;
  const topTxt=(top>=0?'tracción ':'compresión ')+Math.abs(top).toFixed(2)+' MPa';
  const botTxt=(bot>=0?'tracción ':'compresión ')+Math.abs(bot).toFixed(2)+' MPa';
  let txt=`Fibra superior: <b>${topTxt}</b> · fibra inferior: <b>${botTxt}</b>.`;
  if(DATA.stress.shear_available && DATA.stress.tau_max!=null) txt+=` |τ|max=${DATA.stress.tau_max.toFixed(2)} MPa cerca de y=${(DATA.stress.tau_max_y_mm??0).toFixed(1)} mm.`;
  else txt+=' La geometría disponible no permite evaluar τ=VQ/(It).';
  stressReadout.innerHTML=txt;
}
updateStressUI();

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

let scene,camera,renderer,controls,THREE,OrbitControls,beamGroup,modelGroup;
let currentView='front';
function momentColor(v,mmax){if(colorMode.value==='neutral')return new THREE.Color('#d8c8b2');const r=mmax?Math.max(-1,Math.min(1,v/mmax)):0;if(r>=0)return new THREE.Color().lerpColors(new THREE.Color('#d8c8b2'),new THREE.Color('#f28e1c'),r);return new THREE.Color().lerpColors(new THREE.Color('#d8c8b2'),new THREE.Color('#38393e'),-r)}
function clamp01(v){return Math.max(0,Math.min(1,v))}
function stressAt(arr,yMm){return interp(DATA.stress.y_mm,arr,yMm)}
function sigmaColor(v){
  const max=Math.max(DATA.stress.sigma_max||0,1e-12),r=clamp01(Math.abs(v)/max);
  const zero=new THREE.Color('#eadfce');
  return v>=0?new THREE.Color().lerpColors(zero,new THREE.Color('#f28e1c'),r):new THREE.Color().lerpColors(zero,new THREE.Color('#34353a'),r);
}
function tauColor(v){
  const max=Math.max(DATA.stress.tau_max||0,1e-12),r=clamp01(Math.abs(v)/max);
  return new THREE.Color().lerpColors(new THREE.Color('#eadfce'),new THREE.Color('#c8752d'),r);
}
function sectionYToMm(yLocal,sd){
  const half=Math.max(sd.h/2,1e-12);return (yLocal/half)*(DATA.stress.c_mm||1);
}
function materialSpans(sd,yLocal){
  if(sd.kind==='rect'||sd.kind==='custom') return [[-sd.b/2,sd.b/2]];
  if(sd.kind==='i_profile'){
    const flange=Math.abs(yLocal)>=sd.h/2-sd.tf;
    return flange?[[-sd.b/2,sd.b/2]]:[[-sd.tw/2,sd.tw/2]];
  }
  if(sd.kind==='channel'){
    const flange=Math.abs(yLocal)>=sd.h/2-sd.tf;
    return flange?[[-sd.b/2,sd.b/2]]:[[-sd.b/2,-sd.b/2+sd.tw]];
  }
  if(sd.kind==='solid_circle'){
    const r=sd.d/2,w=Math.sqrt(Math.max(r*r-yLocal*yLocal,0));return w>1e-9?[[-w,w]]:[];
  }
  const ro=sd.do/2,ri=sd.di/2,wo=Math.sqrt(Math.max(ro*ro-yLocal*yLocal,0));
  if(wo<=1e-9)return [];
  if(Math.abs(yLocal)>=ri||ri<=1e-9)return [[-wo,wo]];
  const wi=Math.sqrt(Math.max(ri*ri-yLocal*yLocal,0));return [[-wo,-wi],[wi,wo]].filter(a=>a[1]-a[0]>1e-9);
}
function addStressBands(group,sd,th,mode){
  if(mode==='neutral')return;
  const n=30,half=sd.h/2,dy=sd.h/n;
  for(let i=0;i<n;i++){
    const yc=-half+(i+.5)*dy,ymm=sectionYToMm(yc,sd),sig=stressAt(DATA.stress.sigma_mpa,ymm),tau=DATA.stress.shear_available?stressAt(DATA.stress.tau_mpa,ymm):0;
    const col=mode==='tau'?tauColor(tau):sigmaColor(sig);
    const mat=new THREE.MeshBasicMaterial({color:col,side:THREE.DoubleSide,transparent:true,opacity:.97});
    for(const sp of materialSpans(sd,yc)){
      const zw=sp[1]-sp[0],zc=(sp[0]+sp[1])/2;if(zw<=1e-9)continue;
      const band=new THREE.Mesh(new THREE.BoxGeometry(th*1.55,dy*1.04,zw),mat);band.position.set(th*.34,yc,zc);group.add(band);
    }
  }
}
function addNeutralAxis(group,sd,th){
  const zspan=(sd.kind==='rect'||sd.kind==='custom'||sd.kind==='i_profile'||sd.kind==='channel')?sd.b:(sd.kind==='solid_circle'?sd.d:sd.do);
  const g=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(th*.95,0,-zspan*.58),new THREE.Vector3(th*.95,0,zspan*.58)]);
  const line=new THREE.Line(g,new THREE.LineBasicMaterial({color:'#fff7e9'}));group.add(line);
}
function representativeZ(sd,yLocal){
  const spans=materialSpans(sd,yLocal);if(!spans.length)return null;
  let best=spans[0];for(const sp of spans)if(sp[1]-sp[0]>best[1]-best[0])best=sp;
  return (best[0]+best[1])/2;
}
function addShearArrows(group,sd,th){
  if(!DATA.stress.shear_available||!DATA.stress.tau_max||DATA.stress.tau_max<1e-10)return;
  const levels=[-.78,-.52,-.26,0,.26,.52,.78],maxLen=sd.h*.24,minLen=sd.h*.055;
  for(const yn of levels){
    const yl=yn*sd.h/2,ymm=sectionYToMm(yl,sd),tau=stressAt(DATA.stress.tau_mpa,ymm);if(Math.abs(tau)<1e-10)continue;
    const z=representativeZ(sd,yl);if(z==null)continue;
    const ratio=clamp01(Math.abs(tau)/(DATA.stress.tau_max||1)),len=minLen+(maxLen-minLen)*ratio,sgn=tau>=0?1:-1;
    const dir=new THREE.Vector3(0,sgn,0),origin=new THREE.Vector3(th*2.05,yl-sgn*len*.5,z);
    const arrow=new THREE.ArrowHelper(dir,origin,len,0xf28e1c,Math.min(len*.30,sd.h*.075),Math.min(len*.16,sd.h*.04));group.add(arrow);
  }
}

function addModel(obj){modelGroup.add(obj);return obj}
function setActiveView(name){
  currentView=name;
  for(const [id,key] of [['#gg-front','front'],['#gg-iso','iso'],['#gg-section-view','section']]){
    const el=root.querySelector(id);if(el)el.classList.toggle('is-active',key===name);
  }
}

function dims(){
  const s=DATA.section,vs=s.visual_scale||1;
  if(s.kind==='rect') return {kind:'rect',h:s.h_m*vs,b:s.b_m*vs};
  if(s.kind==='solid_circle') return {kind:'solid_circle',d:s.d_m*vs,h:s.d_m*vs,b:s.d_m*vs};
  if(s.kind==='tube') return {kind:'tube',do:s.do_m*vs,di:s.di_m*vs,h:s.do_m*vs,b:s.do_m*vs};
  if(s.kind==='i_profile'||s.kind==='channel') return {kind:s.kind,h:s.h_m*vs,b:s.bf_m*vs,tw:s.tw_m*vs,tf:s.tf_m*vs};
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
  }else if(sd.kind==='i_profile'||sd.kind==='channel'){
    const grp=new THREE.Group(),hw=Math.max(sd.h-2*sd.tf,1e-9);
    const web=new THREE.Mesh(new THREE.BoxGeometry(len,hw,sd.tw),mat);
    web.position.z=sd.kind==='channel'?(-sd.b/2+sd.tw/2):0;grp.add(web);
    for(const yy of [sd.h/2-sd.tf/2,-sd.h/2+sd.tf/2]){const fl=new THREE.Mesh(new THREE.BoxGeometry(len,sd.tf,sd.b),mat);fl.position.y=yy;grp.add(fl)}
    orientX(grp,dir);mesh=grp;
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
  m.position.set(x+(isRight?t/2:-t/2),0,0);addModel(m);
}
function addSimpleSupport(x,kind,sd){
  const h=Math.max(sd.h*2.4,DATA.length*.065),w=Math.max(sd.b*2.8,DATA.length*.07),beamBottom=-sd.h/2;
  const shape=new THREE.Shape();shape.moveTo(-w/2,-h);shape.lineTo(w/2,-h);shape.lineTo(0,0);shape.closePath();
  const geom=new THREE.ExtrudeGeometry(shape,{depth:Math.max(sd.b*1.3,w*.42),bevelEnabled:false});geom.translate(0,0,-Math.max(sd.b*1.3,w*.42)/2);
  const tri=new THREE.Mesh(geom,new THREE.MeshStandardMaterial({color:'#c8752d',roughness:.8}));tri.position.set(x,beamBottom,0);addModel(tri);
  if(kind==='roller'){
    const rz=-Math.max(sd.b*1.3,w*.42)*.32;for(const dz of [rz,-rz]){const r=new THREE.Mesh(new THREE.CylinderGeometry(w*.10,w*.10,Math.max(sd.b*.7,w*.22),18),new THREE.MeshStandardMaterial({color:'#e7d6bd',roughness:.65}));r.rotation.x=Math.PI/2;r.position.set(x,beamBottom-h-w*.11,dz);addModel(r)}
  }
}
function addPointArrow(x,value,amp,sd){
  const y=defY(x,amp),down=value>=0,beamTop=y+(down?sd.h/2:-sd.h/2),gap=Math.max(DATA.length*.025,sd.h*.55),len=Math.max(DATA.length*.115,sd.h*2.5);
  const origin=new THREE.Vector3(x,beamTop+(down?len+gap:-(len+gap)),0),dir=new THREE.Vector3(0,down?-1:1,0);
  const arrow=new THREE.ArrowHelper(dir,origin,len+gap,0xf28e1c,Math.min(len*.28,DATA.length*.035),Math.min(len*.14,DATA.length*.018));addModel(arrow);
}
function addUDL(ld,amp,sd){
  const n=9,tops=[];for(let i=0;i<n;i++){const x=ld.x0+(ld.x1-ld.x0)*i/(n-1),y=defY(x,amp),down=ld.value>=0,beamTop=y+(down?sd.h/2:-sd.h/2),gap=Math.max(DATA.length*.02,sd.h*.5),len=Math.max(DATA.length*.09,sd.h*2.2);const oy=beamTop+(down?len+gap:-(len+gap));tops.push(new THREE.Vector3(x,oy,0));const arrow=new THREE.ArrowHelper(new THREE.Vector3(0,down?-1:1,0),new THREE.Vector3(x,oy,0),len+gap,0xf28e1c,Math.min(len*.27,DATA.length*.03),Math.min(len*.13,DATA.length*.016));addModel(arrow)}
  const rail=new THREE.Line(new THREE.BufferGeometry().setFromPoints(tops),new THREE.LineBasicMaterial({color:'#f28e1c'}));addModel(rail);
}
function addMoment(ld,amp,sd){
  const x=ld.x,y=defY(x,amp),r=Math.max(DATA.length*.055,sd.h*1.6),tube=Math.max(DATA.length*.004,sd.h*.09),positive=ld.value>=0;
  const arc=new THREE.Mesh(new THREE.TorusGeometry(r,tube,10,46,Math.PI*1.55),new THREE.MeshStandardMaterial({color:'#f28e1c'}));arc.position.set(x,y,0);arc.rotation.z=positive?Math.PI*.18:Math.PI*1.36;addModel(arc);
  const a=positive?Math.PI*1.73:Math.PI*.18;const p=new THREE.Vector3(x+r*Math.cos(a),y+r*Math.sin(a),0);const tangent=new THREE.Vector3(-Math.sin(a),Math.cos(a),0).multiplyScalar(positive?1:-1).normalize();const cone=new THREE.Mesh(new THREE.ConeGeometry(tube*2.4,tube*5.5,12),new THREE.MeshStandardMaterial({color:'#f28e1c'}));orientY(cone,tangent);cone.position.copy(p);addModel(cone);
}

function addCut(x,amp,sd){
  const y=defY(x,amp),tan=tangentAt(x,amp),dir=new THREE.Vector3(1,tan.y,0).normalize(),q=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(1,0,0),dir),th=Math.max(DATA.length*.005,sd.h*.08);
  const group=new THREE.Group();
  const shellMat=new THREE.MeshStandardMaterial({color:'#f28e1c',transparent:true,opacity:.16,side:THREE.DoubleSide,roughness:.55,depthWrite:false});
  let shell;
  if(sd.kind==='rect'||sd.kind==='custom') shell=new THREE.Mesh(new THREE.BoxGeometry(th,sd.h*1.12,sd.b*1.12),shellMat);
  else if(sd.kind==='i_profile'||sd.kind==='channel'){
    const grp=new THREE.Group(),hw=Math.max(sd.h-2*sd.tf,1e-9);
    const web=new THREE.Mesh(new THREE.BoxGeometry(th,hw*1.03,sd.tw*1.08),shellMat);web.position.z=sd.kind==='channel'?(-sd.b/2+sd.tw/2):0;grp.add(web);
    for(const yy of [sd.h/2-sd.tf/2,-sd.h/2+sd.tf/2]){const fl=new THREE.Mesh(new THREE.BoxGeometry(th,sd.tf*1.06,sd.b*1.04),shellMat);fl.position.y=yy;grp.add(fl)}
    shell=grp;
  } else if(sd.kind==='solid_circle'){
    shell=new THREE.Mesh(new THREE.CylinderGeometry(sd.d*.56,sd.d*.56,th,40,1,false),shellMat);orientY(shell,new THREE.Vector3(1,0,0));
  }else{
    const grp=new THREE.Group();
    const outer=new THREE.Mesh(new THREE.CylinderGeometry(sd.do*.56,sd.do*.56,th,40,1,true),shellMat);orientY(outer,new THREE.Vector3(1,0,0));grp.add(outer);
    if(sd.di>0){const inner=new THREE.Mesh(new THREE.CylinderGeometry(sd.di*.48,sd.di*.48,th*1.02,40,1,true),new THREE.MeshStandardMaterial({color:'#202126',side:THREE.BackSide,transparent:true,opacity:.55}));orientY(inner,new THREE.Vector3(1,0,0));grp.add(inner)}
    shell=grp;
  }
  group.add(shell);
  const mode=stressMode.value;
  addStressBands(group,sd,th,mode);
  addNeutralAxis(group,sd,th);
  if(mode==='tau'||mode==='both') addShearArrows(group,sd,th);
  group.quaternion.copy(q);group.position.set(x,y,0);addModel(group);
  const normal=new THREE.ArrowHelper(dir,new THREE.Vector3(x,y,0),Math.max(DATA.length*.075,sd.h*2.0),0xf28e1c,DATA.length*.018,DATA.length*.009);addModel(normal);
}

function buildScene(){
  while(scene.children.length)scene.remove(scene.children[0]);
  scene.background=new THREE.Color('#202126');scene.add(new THREE.HemisphereLight('#fff7e9','#313238',2.15));const dl=new THREE.DirectionalLight('#ffffff',2.25);dl.position.set(DATA.length*.25,DATA.length*.55,DATA.length*.65);scene.add(dl);
  const L=Math.max(DATA.length,1e-9),amp=ampValue(),sd=dims(),mmax=Math.max(...DATA.moment.map(Math.abs),1e-9);
  modelGroup=new THREE.Group();scene.add(modelGroup);
  const baseMat=new THREE.LineDashedMaterial({color:'#7b7c82',dashSize:L*.025,gapSize:L*.018});const baseGeo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0),new THREE.Vector3(L,0,0)]);const baseLine=new THREE.Line(baseGeo,baseMat);baseLine.computeLineDistances();addModel(baseLine);
  const grid=new THREE.GridHelper(L*1.28,12,0x494a4f,0x34353a);grid.position.set(L*.5,-Math.max(L*.16,sd.h*3.2),0);scene.add(grid);
  beamGroup=new THREE.Group();modelGroup.add(beamGroup);
  for(let i=0;i<DATA.x.length-1;i++){
    const a=new THREE.Vector3(DATA.x[i],DATA.deflection[i]*amp,0),b=new THREE.Vector3(DATA.x[i+1],DATA.deflection[i+1]*amp,0),col=momentColor((DATA.moment[i]+DATA.moment[i+1])/2,mmax);beamGroup.add(beamSegment(a,b,col,sd));
  }
  DATA.supports.forEach((s,i)=>{if(s.kind==='fixed')addFixedSupport(s.x,s.x>DATA.length/2,sd);else addSimpleSupport(s.x,s.kind,sd)});
  DATA.loads.forEach(ld=>{if(ld.kind==='point')addPointArrow(ld.x,ld.value,amp,sd);else if(ld.kind==='udl')addUDL(ld,amp,sd);else addMoment(ld,amp,sd)});
  addCut(DATA.x_probe,amp,sd);
}

function modelBounds(){
  const box=new THREE.Box3().setFromObject(modelGroup);
  if(box.isEmpty()) box.set(new THREE.Vector3(0,-DATA.length*.1,-DATA.length*.05),new THREE.Vector3(DATA.length,DATA.length*.1,DATA.length*.05));
  return box;
}
function fitView(name='front'){
  if(!camera||!controls||!modelGroup)return;
  const box=modelBounds(),center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3());
  const sphere=box.getBoundingSphere(new THREE.Sphere()),fov=THREE.MathUtils.degToRad(camera.fov),aspect=Math.max(camera.aspect||1,0.2);
  let dir;
  if(name==='section'){
    const xp=DATA.x_probe,amp=ampValue(),tan=tangentAt(xp,amp);dir=new THREE.Vector3(tan.x,tan.y,0).normalize();
    center.set(xp,defY(xp,amp),0);
  }else if(name==='iso') dir=new THREE.Vector3(.72,.48,1).normalize();
  else if(name==='free') dir=camera.position.clone().sub(center).normalize();
  else dir=new THREE.Vector3(0,0,1);
  let distance;
  if(name==='front'){
    const dv=(size.y*.5)/Math.tan(fov*.5),dh=(size.x*.5)/(Math.tan(fov*.5)*aspect);
    distance=Math.max(dv,dh,size.z*2.5,DATA.length*.35)*1.18;
  }else if(name==='section'){
    const sd=dims(),sectionSpan=Math.max(sd.h*2.35,sd.b*2.35,DATA.length*.075);
    distance=Math.max(sectionSpan/Math.tan(fov*.5),DATA.length*.12)*1.18;
  }else{
    distance=Math.max(sphere.radius/Math.sin(fov*.5),DATA.length*.45)*1.18;
  }
  camera.up.set(0,1,0);camera.position.copy(center).add(dir.multiplyScalar(distance));
  camera.near=Math.max(distance/1500,0.001);camera.far=Math.max(distance*30,DATA.length*20);camera.updateProjectionMatrix();
  controls.target.copy(center);controls.minDistance=Math.max(distance*.18,DATA.length*.08);controls.maxDistance=Math.max(distance*5,DATA.length*3);controls.update();
  setActiveView(name==='section'?'section':name==='iso'?'iso':name==='free'?'free':'front');
}
function fitCurrent(){fitView(currentView||'front')}
function resetCamera(){fitView('front')}
async function start3D(){
  try{
    THREE=await import('https://cdn.jsdelivr.net/npm/three@0.180.0/+esm');
    ({OrbitControls}=await import('https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/OrbitControls.js/+esm'));
    scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(36,1,.001,10000);renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.outputColorSpace=THREE.SRGBColorSpace;threeHost.appendChild(renderer.domElement);controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.enablePan=true;controls.screenSpacePanning=true;controls.zoomToCursor=true;controls.addEventListener('start',()=>{currentView='free';setActiveView('free')});buildScene();
    function resize(){const w=threeHost.clientWidth,h=threeHost.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()}resize();fitView('front');let resizeTimer=null;new ResizeObserver(()=>{resize();clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(currentView==='front')fitView('front')},80)}).observe(threeHost);
    status.textContent='Vista frontal · lista para explorar';
    function loop(){controls.update();renderer.render(scene,camera);requestAnimationFrame(loop)}loop();
    colorMode.addEventListener('change',()=>{buildScene();fitCurrent()});
    ampSelect.addEventListener('change',()=>{buildScene();fitCurrent()});
    stressMode.addEventListener('change',()=>{updateStressUI();buildScene();if(currentView==='section')fitView('section');else fitCurrent()});
    root.querySelector('#gg-front').addEventListener('click',()=>fitView('front'));root.querySelector('#gg-iso').addEventListener('click',()=>fitView('iso'));root.querySelector('#gg-section-view').addEventListener('click',()=>fitView('section'));root.querySelector('#gg-fit').addEventListener('click',fitCurrent);root.querySelector('#gg-reset').addEventListener('click',resetCamera);
  }catch(e){console.warn(e);drawFallback();colorMode.addEventListener('change',drawFallback);ampSelect.addEventListener('change',drawFallback);stressMode.addEventListener('change',()=>{updateStressUI();drawFallback()});for(const id of ['#gg-front','#gg-iso','#gg-section-view','#gg-fit','#gg-reset'])root.querySelector(id).addEventListener('click',drawFallback)}
}
start3D();
</script>
'''.replace('__DATA__', data)
    components.html(html, height=max(height, 810), scrolling=False)
