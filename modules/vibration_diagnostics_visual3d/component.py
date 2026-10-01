from __future__ import annotations
import json
import streamlit.components.v1 as components


def render_diagnostics_3d(data: dict, height: int = 560):
    d = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = f'''
<div id="vd3d" style="height:{height}px;border:1px solid #ded7cc;border-radius:14px;overflow:hidden;background:#202126;position:relative">
  <div style="position:absolute;z-index:6;left:13px;top:11px;background:#fff8edee;padding:8px 11px;border-radius:10px;font:13px system-ui;color:#25262a;line-height:1.35">
    <b>Punto de medición</b><br><span id="msg">Vista de respaldo</span>
  </div>
  <div id="read" style="position:absolute;z-index:6;left:13px;bottom:11px;background:#202126e6;border:1px solid #555;color:#f5ead7;padding:7px 10px;border-radius:9px;font:12px system-ui"></div>
  <div style="position:absolute;z-index:6;right:11px;top:11px;display:flex;gap:5px;flex-wrap:wrap">
    <button id="play">Pausa</button><button id="front">Frente</button><button id="iso">Isométrica</button><button id="top">Superior</button><button id="fit">Ajustar</button>
  </div>
  <canvas id="fb" width="1000" height="{height}" style="width:100%;height:100%"></canvas>
</div>
<style>
#vd3d button{{border:1px solid #c8752d;background:#fff8ed;color:#292a2e;border-radius:8px;padding:7px 9px;cursor:pointer}}
#vd3d button:hover{{background:#fff1dd}}
</style>
<script>
(function(){{
  const D={d};
  const cv=document.getElementById('fb'), msg=document.getElementById('msg'), read=document.getElementById('read');
  const c=cv.getContext('2d'), W=cv.width, H=cv.height;
  c.fillStyle='#202126'; c.fillRect(0,0,W,H);
  c.fillStyle='#2f3137'; c.fillRect(120,H-105,W-240,55);
  c.fillStyle='#b48558'; c.fillRect(220,H-155,560,50);
  c.fillStyle='#8d9096'; c.fillRect(300,185,310,170);
  c.fillStyle='#d4d5d8'; c.fillRect(610,245,160,28);
  c.fillStyle='#62656c'; c.fillRect(265,225,42,92); c.fillRect(760,225,42,92);
  const pos={{'Motor DE':[600,175],'Motor NDE':[315,175],'Soporte DE':[780,205],'Soporte NDE':[285,205],'Base':[500,H-175]}};
  const p=pos[D.position]||pos['Motor DE'];
  c.fillStyle='#f28e1c'; c.fillRect(p[0]-13,p[1]-13,26,26);
  c.strokeStyle='#f5ead7'; c.fillStyle='#f5ead7'; c.lineWidth=5;
  let dx=0,dy=0; if(D.orientation==='Vertical')dy=-75; else if(D.orientation==='Axial')dx=85; else dy=0,dx=75;
  c.beginPath();c.moveTo(p[0],p[1]);c.lineTo(p[0]+dx,p[1]+dy);c.stroke();
  const ex=p[0]+dx,ey=p[1]+dy; const ang=Math.atan2(dy,dx);
  c.beginPath();c.moveTo(ex,ey);c.lineTo(ex-18*Math.cos(ang-.5),ey-18*Math.sin(ang-.5));c.lineTo(ex-18*Math.cos(ang+.5),ey-18*Math.sin(ang+.5));c.closePath();c.fill();
  msg.textContent=`Sensor ${{D.position}} · ${{D.orientation}} · vista de respaldo`;
  read.textContent='Si WebGL/Three.js no está disponible, esta vista mantiene visible la ubicación y dirección del sensor.';
}})();
</script>
<script type="module">
const D={d};
const root=document.getElementById('vd3d'), cv=document.getElementById('fb'), msg=document.getElementById('msg'), read=document.getElementById('read');
let paused=false;
try {{
  const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm');
  const {{OrbitControls}}=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm');

  const scene=new THREE.Scene(); scene.background=new THREE.Color('#202126');
  const camera=new THREE.PerspectiveCamera(34,root.clientWidth/{height},.01,100);
  const renderer=new THREE.WebGLRenderer({{antialias:true}});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2)); renderer.setSize(root.clientWidth,{height});
  root.appendChild(renderer.domElement);
  cv.style.display='none';

  const controls=new OrbitControls(camera,renderer.domElement); controls.enableDamping=true; controls.dampingFactor=.08; controls.zoomToCursor=true; controls.minDistance=2; controls.maxDistance=30;
  scene.add(new THREE.HemisphereLight('#fff8ec','#303136',2.3));
  const dl=new THREE.DirectionalLight('#ffffff',2.0); dl.position.set(5,7,8); scene.add(dl);
  const dl2=new THREE.DirectionalLight('#c7a77f',.8); dl2.position.set(-5,2,-4); scene.add(dl2);

  const machine=new THREE.Group(); scene.add(machine);
  const baseMat=new THREE.MeshStandardMaterial({{color:'#b48558',roughness:.80}});
  const motorMat=new THREE.MeshStandardMaterial({{color:'#8d9096',metalness:.25,roughness:.48}});
  const darkMat=new THREE.MeshStandardMaterial({{color:'#62656c',metalness:.18,roughness:.62}});
  const shaftMat=new THREE.MeshStandardMaterial({{color:'#d4d5d8',metalness:.58,roughness:.28}});
  const copperMat=new THREE.MeshStandardMaterial({{color:'#c8752d',roughness:.72}});

  const base=new THREE.Mesh(new THREE.BoxGeometry(6.3,.34,2.9),baseMat); base.position.y=-1.03; machine.add(base);
  const skid1=new THREE.Mesh(new THREE.BoxGeometry(6.8,.14,.30),darkMat); skid1.position.set(0,-1.28,.95); machine.add(skid1);
  const skid2=skid1.clone(); skid2.position.z=-.95; machine.add(skid2);

  const motorBody=new THREE.Mesh(new THREE.CylinderGeometry(.92,.92,2.35,48),motorMat); motorBody.rotation.z=Math.PI/2; motorBody.position.x=-.45; machine.add(motorBody);
  const motorCap1=new THREE.Mesh(new THREE.CylinderGeometry(.98,.98,.12,48),darkMat); motorCap1.rotation.z=Math.PI/2; motorCap1.position.x=-1.65; machine.add(motorCap1);
  const motorCap2=motorCap1.clone(); motorCap2.position.x=.75; machine.add(motorCap2);

  const shaft=new THREE.Mesh(new THREE.CylinderGeometry(.16,.16,4.65,28),shaftMat); shaft.rotation.z=Math.PI/2; shaft.position.x=1.05; machine.add(shaft);
  const coupling=new THREE.Mesh(new THREE.CylinderGeometry(.36,.36,.42,32),copperMat); coupling.rotation.z=Math.PI/2; coupling.position.x=.98; machine.add(coupling);

  const bearingMat=darkMat;
  const b1=new THREE.Mesh(new THREE.BoxGeometry(.52,1.20,1.22),bearingMat); b1.position.x=1.82; machine.add(b1);
  const b2=b1.clone(); b2.position.x=3.05; machine.add(b2);
  const pedestal1=new THREE.Mesh(new THREE.BoxGeometry(.92,.42,1.65),baseMat); pedestal1.position.set(1.82,-.70,0); machine.add(pedestal1);
  const pedestal2=pedestal1.clone(); pedestal2.position.x=3.05; machine.add(pedestal2);

  const fan=new THREE.Mesh(new THREE.CylinderGeometry(.70,.70,.28,36),motorMat); fan.rotation.z=Math.PI/2; fan.position.x=3.55; machine.add(fan);
  const hub=new THREE.Mesh(new THREE.CylinderGeometry(.22,.22,.42,24),copperMat); hub.rotation.z=Math.PI/2; hub.position.x=3.55; machine.add(hub);

  const sensor=new THREE.Mesh(
    new THREE.BoxGeometry(.34,.34,.34),
    new THREE.MeshStandardMaterial({{color:'#f28e1c',roughness:.65}})
  );
  const sensorPositions={{
    'Motor DE':new THREE.Vector3(.72,1.02,0),
    'Motor NDE':new THREE.Vector3(-1.55,1.02,0),
    'Soporte DE':new THREE.Vector3(3.05,.72,.68),
    'Soporte NDE':new THREE.Vector3(1.82,.72,.68),
    'Base':new THREE.Vector3(0,-.76,1.22)
  }};
  const spos=(sensorPositions[D.position]||sensorPositions['Motor DE']).clone(); sensor.position.copy(spos); machine.add(sensor);

  const axes={{Horizontal:new THREE.Vector3(0,0,1),Vertical:new THREE.Vector3(0,1,0),Axial:new THREE.Vector3(1,0,0)}};
  const dir=(axes[D.orientation]||axes.Horizontal).clone().normalize();
  const arrow=new THREE.ArrowHelper(dir,spos.clone(),1.15,0xf5ead7,.22,.12); machine.add(arrow);

  function makeLabel(text,color='#f5ead7'){{
    const cn=document.createElement('canvas'); cn.width=320; cn.height=80; const cx=cn.getContext('2d');
    cx.font='600 34px system-ui'; cx.textAlign='center'; cx.fillStyle=color; cx.fillText(text,160,50);
    const tex=new THREE.CanvasTexture(cn); const sp=new THREE.Sprite(new THREE.SpriteMaterial({{map:tex,transparent:true,depthTest:false}})); sp.scale.set(1.25,.32,1); return sp;
  }}
  const sensorLbl=makeLabel(`${{D.position}} · ${{D.orientation}}`,'#f28e1c'); sensorLbl.position.copy(spos.clone().add(new THREE.Vector3(0,.45,0))); machine.add(sensorLbl);

  const grid=new THREE.GridHelper(11,11,0x46474c,0x303136); grid.position.y=-1.33; scene.add(grid);
  const sig=D.signal||[], dur=Math.max(D.duration||3,1e-6), amp=D.visual_amp||1;
  const smax=Math.max(...sig.map(v=>Math.abs(v)),1e-9); let tm=0,last=performance.now();
  function sample(a,tt){{if(!a.length)return 0;const u=((tt%dur)/dur)*(a.length-1),i=Math.floor(u),j=Math.min(a.length-1,i+1),q=u-i;return a[i]*(1-q)+a[j]*q;}}
  function update(dt){{
    if(!paused) tm+=dt;
    const raw=sample(sig,tm); const q=(raw/smax)*.14*amp;
    machine.position.copy(dir.clone().multiplyScalar(q));
    read.textContent=`${{D.position}} · ${{D.orientation}} · señal = ${{raw.toFixed(3)}}`;
  }}

  function front(){{camera.position.set(.8,.4,9.4);controls.target.set(.7,-.05,0);controls.update();}}
  function iso(){{camera.position.set(6.5,4.0,7.8);controls.target.set(.7,-.05,0);controls.update();}}
  function top(){{camera.position.set(.7,8.4,.01);controls.target.set(.7,-.05,0);controls.update();}}
  function fit(){{const b=new THREE.Box3().setFromObject(machine),sz=b.getSize(new THREE.Vector3()),ct=b.getCenter(new THREE.Vector3()),md=Math.max(sz.x,sz.y,sz.z,1),f=camera.fov*Math.PI/180,dist=md/(2*Math.tan(f/2))*1.28,di=new THREE.Vector3().subVectors(camera.position,controls.target).normalize();controls.target.copy(ct);camera.position.copy(ct.clone().add(di.multiplyScalar(dist)));controls.update();}}
  front(); fit();
  document.getElementById('front').onclick=()=>{{front();fit();}};
  document.getElementById('iso').onclick=()=>{{iso();fit();}};
  document.getElementById('top').onclick=()=>{{top();fit();}};
  document.getElementById('fit').onclick=fit;
  document.getElementById('play').onclick=e=>{{paused=!paused;e.target.textContent=paused?'Reproducir':'Pausa';}};
  msg.textContent=`Sensor ${{D.position}} · ${{D.orientation}}`;
  window.addEventListener('resize',()=>{{camera.aspect=root.clientWidth/{height};camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,{height});}});
  function loop(now){{const dt=Math.min(.05,(now-last)/1000);last=now;update(dt);controls.update();renderer.render(scene,camera);requestAnimationFrame(loop);}}
  requestAnimationFrame(loop);
}} catch(e) {{
  console.error(e);
  msg.textContent=`Sensor ${{D.position}} · ${{D.orientation}} · vista de respaldo`;
}}
</script>
'''
    components.html(html, height=height, scrolling=False)
