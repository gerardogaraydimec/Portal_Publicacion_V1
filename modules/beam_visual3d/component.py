from __future__ import annotations

import json
import streamlit.components.v1 as components


def render_beam_3d(payload: dict, height: int = 720) -> None:
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    html = r'''
<div id="gg-beam3d" class="gg-root">
  <div class="gg-toolbar">
    <div>
      <div class="gg-kicker">MECHLAB · VISUALIZACIÓN MECÁNICA</div>
      <div class="gg-title">Viga deformada y sección de análisis</div>
      <div class="gg-sub">La deformada se amplifica solo para visualizarla. Los valores numéricos conservan su magnitud física.</div>
    </div>
    <div class="gg-controls">
      <label>Color
        <select id="gg-color-mode"><option value="moment">Momento M(x)</option><option value="neutral">Material</option></select>
      </label>
      <label>Amplificación
        <select id="gg-amp"><option value="auto">Automática</option><option value="1">1×</option><option value="10">10×</option><option value="50">50×</option><option value="100">100×</option><option value="500">500×</option></select>
      </label>
      <button id="gg-reset" type="button">Restablecer vista</button>
    </div>
  </div>

  <div class="gg-grid">
    <section class="gg-scene-card">
      <div id="gg-status" class="gg-status">Cargando visor 3D…</div>
      <div id="gg-three"></div>
      <canvas id="gg-fallback" aria-label="Vista esquemática de viga deformada"></canvas>
      <div class="gg-legend"><span><i class="sw neg"></i>M negativo</span><span><i class="sw zero"></i>M≈0</span><span><i class="sw pos"></i>M positivo</span><span><i class="sw cut"></i>corte x</span></div>
    </section>

    <aside class="gg-side">
      <div class="gg-card gg-probe">
        <div class="gg-card-title">Sección seleccionada</div>
        <div class="gg-big"><span id="gg-x"></span> m</div>
        <div class="gg-pairs"><div><span>V(x)</span><b id="gg-v"></b></div><div><span>M(x)</span><b id="gg-m"></b></div></div>
      </div>
      <div class="gg-card">
        <div class="gg-card-title">Tensiones en el corte</div>
        <canvas id="gg-stress" aria-label="Distribución de esfuerzo normal y cortante"></canvas>
        <div class="gg-pairs"><div><span>|σ|max</span><b id="gg-smax"></b></div><div><span>|τ|max</span><b id="gg-tmax"></b></div></div>
      </div>
      <div class="gg-card gg-note"><b>Lectura física</b><br><span>El plano cobre sigue la misma posición x del módulo. El color de la viga representa M(x); la sección lateral conecta M→σ y V→τ.</span></div>
    </aside>
  </div>
</div>
<style>
#gg-beam3d{--cu:#c8752d;--or:#f28e1c;--ink:#202126;--mut:#6d7078;--iv:#fbf7f0;--line:#ded7cc;--soft:#f2eadf;font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;color:var(--ink)}
#gg-beam3d *{box-sizing:border-box}.gg-toolbar{display:flex;justify-content:space-between;gap:18px;align-items:flex-end;margin-bottom:12px}.gg-kicker{font-size:11px;letter-spacing:.16em;font-weight:800;color:var(--cu)}.gg-title{font-size:24px;font-weight:850;line-height:1.1}.gg-sub{font-size:13px;color:var(--mut);max-width:760px;margin-top:5px}.gg-controls{display:flex;gap:8px;align-items:end;flex-wrap:wrap}.gg-controls label{font-size:11px;color:var(--mut);font-weight:700}.gg-controls select,.gg-controls button{display:block;margin-top:4px;border:1px solid var(--line);background:#fff;border-radius:9px;padding:8px 10px;font-size:12px;color:var(--ink)}.gg-controls button{background:var(--ink);color:#fff;border-color:var(--ink);cursor:pointer}.gg-grid{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(260px,.7fr);gap:12px}.gg-scene-card,.gg-card{border:1px solid var(--line);border-radius:16px;background:var(--iv);overflow:hidden}.gg-scene-card{position:relative;min-height:520px;background:linear-gradient(180deg,#2c2d31 0%,#202126 72%)}#gg-three{height:475px;width:100%}#gg-fallback{display:none;width:100%;height:475px}.gg-status{position:absolute;z-index:4;top:12px;left:12px;background:rgba(251,247,240,.92);border:1px solid rgba(222,215,204,.8);border-radius:999px;padding:6px 10px;font-size:11px;color:var(--ink)}.gg-legend{height:44px;background:var(--iv);display:flex;gap:15px;align-items:center;padding:0 14px;flex-wrap:wrap;font-size:11px;color:var(--mut)}.gg-legend span{display:flex;align-items:center;gap:5px}.sw{width:15px;height:5px;border-radius:3px;display:inline-block}.sw.neg{background:#3b3c42}.sw.zero{background:#d6c5ad}.sw.pos{background:var(--or)}.sw.cut{background:var(--cu);height:14px;width:3px}.gg-side{display:flex;flex-direction:column;gap:12px}.gg-card{padding:14px;background:#fff}.gg-card-title{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--mut);font-weight:800}.gg-big{font-size:27px;font-weight:850;margin:8px 0 10px;color:var(--cu)}.gg-pairs{display:grid;grid-template-columns:1fr 1fr;gap:8px}.gg-pairs div{background:var(--iv);border:1px solid var(--line);border-radius:10px;padding:8px}.gg-pairs span{display:block;font-size:10px;color:var(--mut)}.gg-pairs b{display:block;font-size:14px;margin-top:2px}.gg-note{font-size:12px;line-height:1.45;background:var(--soft)}#gg-stress{width:100%;height:250px;margin:8px 0 4px}
@media(max-width:760px){.gg-toolbar{align-items:flex-start;flex-direction:column}.gg-grid{grid-template-columns:1fr}.gg-scene-card{min-height:430px}#gg-three,#gg-fallback{height:385px}.gg-title{font-size:20px}.gg-side{display:grid;grid-template-columns:1fr}.gg-controls{width:100%}}
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

function stressPlot(){
  const c=stressCanvas, dpr=Math.max(1,Math.min(2,devicePixelRatio||1));
  const w=c.clientWidth||280,h=250;c.width=w*dpr;c.height=h*dpr;const g=c.getContext('2d');g.scale(dpr,dpr);g.clearRect(0,0,w,h);
  g.fillStyle='#fbf7f0';g.fillRect(0,0,w,h);g.strokeStyle='#ded7cc';g.strokeRect(.5,.5,w-1,h-1);
  const pad={l:34,r:12,t:20,b:24}, iw=w-pad.l-pad.r, ih=h-pad.t-pad.b;
  const y=DATA.stress.y_mm,s=DATA.stress.sigma_mpa,t=DATA.stress.tau_mpa;
  const ymax=Math.max(...y.map(Math.abs),1), xmax=Math.max(...s.map(Math.abs),...t.map(Math.abs),1);
  const X=v=>pad.l+(v+xmax)/(2*xmax)*iw, Y=v=>pad.t+(ymax-v)/(2*ymax)*ih;
  g.strokeStyle='#aaa59d';g.lineWidth=1;g.beginPath();g.moveTo(X(0),pad.t);g.lineTo(X(0),pad.t+ih);g.moveTo(pad.l,Y(0));g.lineTo(pad.l+iw,Y(0));g.stroke();
  function line(arr,col,dash=[]){g.strokeStyle=col;g.lineWidth=2;g.setLineDash(dash);g.beginPath();arr.forEach((v,i)=>{const a=X(v),b=Y(y[i]);i?g.lineTo(a,b):g.moveTo(a,b)});g.stroke();g.setLineDash([])}
  line(s,'#c8752d');line(t,'#202126',[5,4]);
  g.font='11px system-ui';g.fillStyle='#6d7078';g.fillText('σx',pad.l+3,14);g.fillText('τxy',pad.l+34,14);g.fillStyle='#c8752d';g.fillRect(pad.l-10,7,8,3);g.fillStyle='#202126';g.fillRect(pad.l+23,7,8,3);
}
stressPlot();

function drawFallback(){
  threeHost.style.display='none';fallback.style.display='block';status.textContent='Vista 2D de respaldo';
  const dpr=Math.max(1,Math.min(2,devicePixelRatio||1)),w=fallback.clientWidth||700,h=fallback.clientHeight||475;fallback.width=w*dpr;fallback.height=h*dpr;const g=fallback.getContext('2d');g.scale(dpr,dpr);g.clearRect(0,0,w,h);g.fillStyle='#202126';g.fillRect(0,0,w,h);
  const pad=55,iw=w-2*pad,mid=h*.48,L=Math.max(DATA.length,1e-9),def=DATA.deflection,amp=ampSelect.value==='auto'?DATA.auto_amplification:Number(ampSelect.value);const maxd=Math.max(...def.map(Math.abs),1e-9);const sy=Math.min(h*.27/(maxd*amp),1);const X=x=>pad+x/L*iw,Y=v=>mid+v*amp*sy;
  g.strokeStyle='#8a8b90';g.lineWidth=2;g.setLineDash([5,6]);g.beginPath();DATA.x.forEach((x,i)=>i?g.lineTo(X(x),mid):g.moveTo(X(x),mid));g.stroke();g.setLineDash([]);
  const mmax=Math.max(...DATA.moment.map(Math.abs),1e-9);for(let i=0;i<DATA.x.length-1;i++){const mn=(DATA.moment[i]+DATA.moment[i+1])/(2*mmax);g.strokeStyle=colorMode.value==='neutral'?'#e8d9c3':(mn>=0?`rgb(${Math.round(214+41*Math.min(mn,1))},${Math.round(184-42*Math.min(mn,1))},${Math.round(145-117*Math.min(mn,1))})`:'#55565c');g.lineWidth=8;g.beginPath();g.moveTo(X(DATA.x[i]),Y(def[i]));g.lineTo(X(DATA.x[i+1]),Y(def[i+1]));g.stroke()}
  const xp=X(DATA.x_probe);g.strokeStyle='#f28e1c';g.lineWidth=3;g.beginPath();g.moveTo(xp,mid-h*.22);g.lineTo(xp,mid+h*.22);g.stroke();
  g.fillStyle='#fbf7f0';g.font='12px system-ui';g.fillText('deformada amplificada',pad,24);g.fillStyle='#f28e1c';g.fillText('x = '+DATA.x_probe.toFixed(3)+' m',Math.min(xp+7,w-105),mid-h*.22+12);
}

let scene,camera,renderer,controls,THREE,OrbitControls,beamGroup;
function momentColor(v,mmax){if(colorMode.value==='neutral')return new THREE.Color('#d8c8b2');const r=mmax?Math.max(-1,Math.min(1,v/mmax)):0;if(r>=0){return new THREE.Color().lerpColors(new THREE.Color('#d8c8b2'),new THREE.Color('#f28e1c'),r)}return new THREE.Color().lerpColors(new THREE.Color('#d8c8b2'),new THREE.Color('#38393e'),-r)}
function addArrow(x,y,z,scale=1){const grp=new THREE.Group();const mat=new THREE.MeshStandardMaterial({color:'#f28e1c'});const shaft=new THREE.Mesh(new THREE.CylinderGeometry(.018,.018,.22,12),mat);shaft.position.y=.11;const head=new THREE.Mesh(new THREE.ConeGeometry(.055,.13,14),mat);head.position.y=-.065;head.rotation.z=Math.PI;grp.add(shaft,head);grp.position.set(x,y,z);grp.scale.setScalar(scale);scene.add(grp)}
function yAt(x,amp){const xs=DATA.x,ys=DATA.deflection;if(x<=xs[0])return ys[0]*amp;if(x>=xs[xs.length-1])return ys[ys.length-1]*amp;let lo=0;while(lo<xs.length-2&&xs[lo+1]<x)lo++;const t=(x-xs[lo])/(xs[lo+1]-xs[lo]);return (ys[lo]*(1-t)+ys[lo+1]*t)*amp}
function buildScene(){
  while(scene.children.length)scene.remove(scene.children[0]);
  scene.background=new THREE.Color('#202126');scene.add(new THREE.HemisphereLight('#fff7e9','#323237',2.2));const dl=new THREE.DirectionalLight('#ffffff',2.4);dl.position.set(2,4,4);scene.add(dl);
  const L=Math.max(DATA.length,1e-9), amp=ampSelect.value==='auto'?DATA.auto_amplification:Number(ampSelect.value), beamH=L*.035,beamB=L*.055,mmax=Math.max(...DATA.moment.map(Math.abs),1e-9);
  const baseMat=new THREE.LineDashedMaterial({color:'#77787d',dashSize:L*.025,gapSize:L*.018});const baseGeo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0),new THREE.Vector3(L,0,0)]);const baseLine=new THREE.Line(baseGeo,baseMat);baseLine.computeLineDistances();scene.add(baseLine);
  beamGroup=new THREE.Group();scene.add(beamGroup);
  for(let i=0;i<DATA.x.length-1;i++){const x0=DATA.x[i],x1=DATA.x[i+1],y0=DATA.deflection[i]*amp,y1=DATA.deflection[i+1]*amp;const a=new THREE.Vector3(x0,-y0,0),b=new THREE.Vector3(x1,-y1,0),mid=a.clone().add(b).multiplyScalar(.5),dir=b.clone().sub(a),len=dir.length();const geom=new THREE.BoxGeometry(len,beamH,beamB);const mat=new THREE.MeshStandardMaterial({color:momentColor((DATA.moment[i]+DATA.moment[i+1])/2,mmax),metalness:.08,roughness:.62});const mesh=new THREE.Mesh(geom,mat);mesh.position.copy(mid);mesh.quaternion.setFromUnitVectors(new THREE.Vector3(1,0,0),dir.clone().normalize());beamGroup.add(mesh)}
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(L*1.35,L*.55),new THREE.MeshStandardMaterial({color:'#292a2e',roughness:1}));floor.rotation.x=-Math.PI/2;floor.position.set(L*.5,-L*.18,0);scene.add(floor);
  DATA.supports.forEach(s=>{const yy=-yAt(s.x,amp)-beamH*.5;if(s.kind==='fixed'){const m=new THREE.Mesh(new THREE.BoxGeometry(L*.025,L*.22,L*.16),new THREE.MeshStandardMaterial({color:'#c8752d'}));m.position.set(s.x-L*.012,yy,0);scene.add(m)}else{const cone=new THREE.Mesh(new THREE.ConeGeometry(L*.065,L*.12,4),new THREE.MeshStandardMaterial({color:'#c8752d'}));cone.rotation.y=Math.PI/4;cone.position.set(s.x,yy-L*.07,0);scene.add(cone);if(s.kind==='roller'){for(const dz of [-L*.035,L*.035]){const r=new THREE.Mesh(new THREE.CylinderGeometry(L*.014,L*.014,L*.07,14),new THREE.MeshStandardMaterial({color:'#e7d6bd'}));r.rotation.x=Math.PI/2;r.position.set(s.x,yy-L*.145,dz);scene.add(r)}}}});
  DATA.loads.forEach(ld=>{if(ld.kind==='point'){addArrow(ld.x,-yAt(ld.x,amp)+L*.16,0,Math.max(.7,Math.min(1.25,ld.value/20||1)))}else if(ld.kind==='udl'){for(let i=0;i<9;i++){const x=ld.x0+(ld.x1-ld.x0)*i/8;addArrow(x,-yAt(x,amp)+L*.15,0,.62)}}else if(ld.kind==='moment'){const tor=new THREE.Mesh(new THREE.TorusGeometry(L*.07,L*.008,8,40,Math.PI*1.6),new THREE.MeshStandardMaterial({color:'#f28e1c'}));tor.position.set(ld.x,-yAt(ld.x,amp)+L*.08,0);tor.rotation.y=Math.PI/2;scene.add(tor)}});
  const xp=DATA.x_probe,yp=-yAt(xp,amp);const cut=new THREE.Mesh(new THREE.PlaneGeometry(L*.18,L*.18),new THREE.MeshBasicMaterial({color:'#f28e1c',transparent:true,opacity:.30,side:THREE.DoubleSide}));cut.rotation.y=Math.PI/2;cut.position.set(xp,yp,0);scene.add(cut);const edge=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.PlaneGeometry(L*.18,L*.18)),new THREE.LineBasicMaterial({color:'#f28e1c'}));edge.rotation.y=Math.PI/2;edge.position.copy(cut.position);scene.add(edge);
}
function resetCamera(){const L=Math.max(DATA.length,1e-9);camera.position.set(L*.62,L*.48,L*.78);controls.target.set(L*.48,0,0);controls.update()}
async function start3D(){
  try{
    THREE=await import('https://cdn.jsdelivr.net/npm/three@0.180.0/+esm');
    ({OrbitControls}=await import('https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/OrbitControls.js/+esm'));
    scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(38,1,.001,10000);renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.outputColorSpace=THREE.SRGBColorSpace;threeHost.appendChild(renderer.domElement);controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.minDistance=DATA.length*.25;controls.maxDistance=DATA.length*3;buildScene();resetCamera();status.textContent='3D interactivo · arrastra para girar';
    function resize(){const w=threeHost.clientWidth,h=threeHost.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()}resize();new ResizeObserver(resize).observe(threeHost);
    let raf;function loop(){controls.update();renderer.render(scene,camera);raf=requestAnimationFrame(loop)}loop();
    colorMode.addEventListener('change',buildScene);ampSelect.addEventListener('change',buildScene);root.querySelector('#gg-reset').addEventListener('click',resetCamera);
  }catch(e){console.warn(e);drawFallback();colorMode.addEventListener('change',drawFallback);ampSelect.addEventListener('change',drawFallback);root.querySelector('#gg-reset').addEventListener('click',drawFallback)}
}
start3D();
</script>
'''.replace('__DATA__', data)
    components.html(html, height=height, scrolling=False)
