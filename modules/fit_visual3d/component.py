from __future__ import annotations
import json
import streamlit.components.v1 as components


def _build_html(data: dict, height: int = 620) -> str:
    d = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return f'''
<div id="fit3d" style="height:{height}px;border:1px solid #ded7cc;border-radius:16px;overflow:hidden;background:#202126;position:relative">
  <div style="position:absolute;z-index:5;left:13px;top:11px;background:#fff8edee;color:#25262a;padding:9px 11px;border-radius:10px;font:13px system-ui;line-height:1.35">
    <b>Montaje eje–agujero 3D</b><br><span id="msg"></span>
  </div>
  <div style="position:absolute;z-index:5;right:11px;top:11px;display:flex;gap:5px;flex-wrap:wrap">
    <button id="front">Frente</button><button id="iso">Isométrica</button><button id="section">Sección</button><button id="fit">Ajustar</button><button id="reset">Restablecer</button>
  </div>
  <div id="legend" style="position:absolute;z-index:5;left:13px;bottom:11px;background:#202126e6;border:1px solid #55575e;color:#f5ead7;padding:8px 10px;border-radius:9px;font:12px system-ui;max-width:72%"></div>
  <canvas id="fallback" width="1100" height="{height}" style="width:100%;height:100%"></canvas>
</div>
<style>
#fit3d button{{border:1px solid #c8752d;background:#fff8ed;color:#292a2e;border-radius:8px;padding:7px 9px;cursor:pointer}}
#fit3d button:hover{{background:#fff0dc}}
</style>
<script type="module">
const D={d};
const root=document.getElementById('fit3d'), fb=document.getElementById('fallback'), msg=document.getElementById('msg'), legend=document.getElementById('legend');
function drawFallback(){{
  const c=fb.getContext('2d'),W=fb.width,H=fb.height;c.fillStyle='#202126';c.fillRect(0,0,W,H);
  const cy=H/2; c.fillStyle='#8f949c'; c.fillRect(520,cy-120,280,240); c.fillStyle='#202126'; c.beginPath(); c.arc(520,cy,82,0,Math.PI*2); c.fill();
  const shaftX=150+(D.assembly||0)/100*350; c.fillStyle='#e7ddcc'; c.fillRect(shaftX,cy-55,360,110); c.strokeStyle='#a49b8e';c.strokeRect(shaftX,cy-55,360,110);
  c.fillStyle=D.fit_type==='Juego'?'#5aa0ff':(D.fit_type==='Interferencia'?'#e06161':'#f28e1c'); c.globalAlpha=.35; c.fillRect(500,cy-70,45,140); c.globalAlpha=1;
  c.fillStyle='#f5ead7';c.font='600 18px system-ui';c.fillText(D.designation+' · '+D.fit_type,28,38);
  msg.textContent='Vista de respaldo';
  legend.textContent='Eje claro · alojamiento grafito · zona de ajuste coloreada. La escala radial está exagerada para hacer visibles tolerancias micrométricas.';
}}
drawFallback();
try{{
  const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm');
  const {{OrbitControls}}=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm');
  const scene=new THREE.Scene(); scene.background=new THREE.Color('#202126');
  const camera=new THREE.PerspectiveCamera(33,root.clientWidth/{height},.01,100);
  const renderer=new THREE.WebGLRenderer({{antialias:true}}); renderer.setPixelRatio(Math.min(devicePixelRatio||1,2)); renderer.setSize(root.clientWidth,{height}); root.appendChild(renderer.domElement);
  const controls=new OrbitControls(camera,renderer.domElement); controls.enableDamping=true; controls.dampingFactor=.08; controls.zoomToCursor=true; controls.minDistance=2; controls.maxDistance=35;
  scene.add(new THREE.HemisphereLight('#fff8ec','#303136',2.15)); const dl=new THREE.DirectionalLight('#fff',2); dl.position.set(5,7,8); scene.add(dl);
  const grid=new THREE.GridHelper(12,12,0x47494f,0x303136); grid.position.y=-1.6; scene.add(grid);
  const G=new THREE.Group();scene.add(G);

  const typeColor = D.fit_type==='Juego' ? '#5a9aff' : (D.fit_type==='Interferencia' ? '#e35e5e' : '#f28e1c');
  const matHousing=new THREE.MeshStandardMaterial({{color:'#8f939b',metalness:.25,roughness:.58,transparent:true,opacity:.82,side:THREE.DoubleSide}});
  const matInner=new THREE.MeshStandardMaterial({{color:'#555962',metalness:.15,roughness:.65,side:THREE.DoubleSide}});
  const matShaft=new THREE.MeshStandardMaterial({{color:'#e7ddcc',metalness:.18,roughness:.48}});
  const matZone=new THREE.MeshStandardMaterial({{color:typeColor,transparent:true,opacity:.30,side:THREE.DoubleSide}});

  const sleeveLen=2.8, outerR=1.42, boreR=0.86;
  const shell=new THREE.Mesh(new THREE.CylinderGeometry(outerR,outerR,sleeveLen,64,1,true),matHousing);shell.rotation.z=Math.PI/2;shell.position.x=1.55;G.add(shell);
  const inner=new THREE.Mesh(new THREE.CylinderGeometry(boreR,boreR,sleeveLen+.03,64,1,true),matInner);inner.rotation.z=Math.PI/2;inner.position.x=1.55;G.add(inner);
  const ringMat=new THREE.MeshStandardMaterial({{color:'#a7aab0',metalness:.2,roughness:.55,side:THREE.DoubleSide}});
  for(const x of [1.55-sleeveLen/2,1.55+sleeveLen/2]){{const ring=new THREE.Mesh(new THREE.RingGeometry(boreR,outerR,64),ringMat);ring.rotation.y=Math.PI/2;ring.position.x=x;G.add(ring);}}

  const tolSpan=Math.max(Math.abs(D.hole_ES_um-D.hole_EI_um),Math.abs(D.shaft_es_um-D.shaft_ei_um),1);
  const actualGapUm=(D.actual_hole_mm-D.actual_shaft_mm)*1000;
  const exaggerated = Math.max(-.12, Math.min(.12, actualGapUm / Math.max(tolSpan,1)*.10));
  const shaftR = Math.max(.65, boreR - exaggerated);
  const shaftLen=4.2;
  const shaft=new THREE.Mesh(new THREE.CylinderGeometry(shaftR,shaftR,shaftLen,64),matShaft);shaft.rotation.z=Math.PI/2;G.add(shaft);
  const assembly=Math.max(0,Math.min(100,D.assembly||0))/100;
  shaft.position.x = -2.4 + assembly*3.05;

  const zone=new THREE.Mesh(new THREE.CylinderGeometry(boreR+.035,boreR+.035,.28,64,1,true),matZone);zone.rotation.z=Math.PI/2;zone.position.x=.18;G.add(zone);
  const zring1=new THREE.Mesh(new THREE.RingGeometry(Math.min(boreR,shaftR),Math.max(boreR,shaftR)+.05,64),new THREE.MeshBasicMaterial({{color:typeColor,transparent:true,opacity:.5,side:THREE.DoubleSide}}));zring1.rotation.y=Math.PI/2;zring1.position.x=.03;G.add(zring1);

  function makeLabel(text,color='#fff'){{const cn=document.createElement('canvas');cn.width=300;cn.height=80;const cx=cn.getContext('2d');cx.font='600 34px system-ui';cx.fillStyle=color;cx.textAlign='center';cx.fillText(text,150,50);const tex=new THREE.CanvasTexture(cn);const sp=new THREE.Sprite(new THREE.SpriteMaterial({{map:tex,transparent:true,depthTest:false}}));sp.scale.set(1.55,.42,1);G.add(sp);return sp;}}
  const shaftLbl=makeLabel('Eje','#fff2df');shaftLbl.position.set(shaft.position.x,-1.12,0);
  const holeLbl=makeLabel('Agujero / alojamiento','#d7dbe3');holeLbl.position.set(1.55,1.72,0);
  const zoneLbl=makeLabel(D.fit_type,typeColor);zoneLbl.position.set(.18,1.18,0);

  const arrow=new THREE.ArrowHelper(new THREE.Vector3(1,0,0),new THREE.Vector3(-3.9,1.35,0),1.1,0xf28e1c,.18,.10);G.add(arrow);
  const arrLbl=makeLabel('sentido de montaje','#f28e1c');arrLbl.position.set(-3.3,1.7,0);

  const sectionLine=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(.18,-1.5,-1.8),new THREE.Vector3(.18,1.5,1.8)]),new THREE.LineBasicMaterial({{color:0xf28e1c,transparent:true,opacity:.7}}));G.add(sectionLine);

  legend.innerHTML=`<b>${{D.designation}}</b> · ${{D.fit_type}} · agujero real = ${{D.actual_hole_mm.toFixed(4)}} mm · eje real = ${{D.actual_shaft_mm.toFixed(4)}} mm · diferencia = ${{(D.actual_clearance_mm*1000).toFixed(1)}} µm.<br><span style="opacity:.82">La escala radial del juego/interferencia está exagerada visualmente.</span>`;
  msg.textContent=`Nominal Ø${{D.nominal_mm.toFixed(2)}} mm · montaje ${{Math.round(D.assembly||0)}} %`;

  function front(){{camera.position.set(-.2,.3,10.2);controls.target.set(.15,0,0);controls.update()}}
  function iso(){{camera.position.set(6.4,4.2,7.6);controls.target.set(.15,0,0);controls.update()}}
  function section(){{camera.position.set(8.5,.1,.01);controls.target.set(.18,0,0);controls.update()}}
  function fit(){{const b=new THREE.Box3().setFromObject(G),sz=b.getSize(new THREE.Vector3()),ct=b.getCenter(new THREE.Vector3()),md=Math.max(sz.x,sz.y,sz.z,1),f=camera.fov*Math.PI/180,dist=md/(2*Math.tan(f/2))*1.30,dir=new THREE.Vector3().subVectors(camera.position,controls.target).normalize();controls.target.copy(ct);camera.position.copy(ct.clone().add(dir.multiplyScalar(dist)));controls.update()}}
  function reset(){{front();fit()}} reset();
  document.getElementById('front').onclick=()=>{{front();fit()}};document.getElementById('iso').onclick=()=>{{iso();fit()}};document.getElementById('section').onclick=()=>{{section();fit()}};document.getElementById('fit').onclick=fit;document.getElementById('reset').onclick=reset;
  window.addEventListener('resize',()=>{{camera.aspect=root.clientWidth/{height};camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,{height})}});
  let first=false;function loop(){{shaftLbl.position.x=shaft.position.x;controls.update();renderer.render(scene,camera);if(!first){{first=true;fb.style.display='none'}}requestAnimationFrame(loop)}}loop();
}}catch(e){{console.error(e);msg.textContent='Vista de respaldo · Three.js no disponible';}}
</script>
'''


def render_fit_3d(data: dict, height: int = 620):
    components.html(_build_html(data, height), height=height, scrolling=False)
