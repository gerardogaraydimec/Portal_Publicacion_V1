from __future__ import annotations
import json
import streamlit.components.v1 as components

def render_diagnostics_3d(data:dict,height:int=560):
    d=json.dumps(data,ensure_ascii=False,separators=(',',':'))
    html=f'''
<div id="vd3d" style="height:{height}px;border:1px solid #ded7cc;border-radius:14px;overflow:hidden;background:#202126;position:relative">
  <div style="position:absolute;z-index:4;left:13px;top:11px;background:#fff8edee;padding:8px 11px;border-radius:10px;font:13px system-ui;color:#25262a"><b>Punto de medición</b><br><span id="msg"></span></div>
  <div id="read" style="position:absolute;z-index:4;left:13px;bottom:11px;background:#202126e6;border:1px solid #555;color:#f5ead7;padding:7px 10px;border-radius:9px;font:12px system-ui"></div>
  <div style="position:absolute;z-index:4;right:11px;top:11px;display:flex;gap:5px"><button id="play">Pausa</button><button id="front">Frente</button><button id="iso">Isométrica</button><button id="fit">Ajustar</button></div>
  <canvas id="fb" width="1000" height="{height}" style="width:100%;height:100%"></canvas>
</div>
<style>#vd3d button{{border:1px solid #c8752d;background:#fff8ed;color:#292a2e;border-radius:8px;padding:7px 9px;cursor:pointer}}</style>
<script type="module">
const D={d},root=document.getElementById('vd3d'),cv=document.getElementById('fb'),msg=document.getElementById('msg'),read=document.getElementById('read');let paused=false;
function fallback(){{const c=cv.getContext('2d');c.fillStyle='#202126';c.fillRect(0,0,cv.width,cv.height);c.fillStyle='#e7ddcc';c.fillRect(300,170,360,210);c.fillStyle='#f28e1c';c.fillRect(560,145,35,35);msg.textContent='Vista de respaldo';}}
fallback();
try{{
 const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm'); const {{OrbitControls}}=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm'); cv.style.display='none';
 const scene=new THREE.Scene();scene.background=new THREE.Color('#202126'); const camera=new THREE.PerspectiveCamera(34,root.clientWidth/{height},.01,80); const renderer=new THREE.WebGLRenderer({{antialias:true}});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.setSize(root.clientWidth,{height});root.appendChild(renderer.domElement); const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.zoomToCursor=true;
 scene.add(new THREE.HemisphereLight('#fff8ec','#303136',2.3));const dl=new THREE.DirectionalLight('#fff',2);dl.position.set(5,7,8);scene.add(dl); const G=new THREE.Group();scene.add(G);
 const base=new THREE.Mesh(new THREE.BoxGeometry(5.8,.30,2.7),new THREE.MeshStandardMaterial({{color:'#b48558',roughness:.8}}));base.position.y=-1.0;G.add(base);
 const motor=new THREE.Mesh(new THREE.CylinderGeometry(1.0,1.0,2.6,40),new THREE.MeshStandardMaterial({{color:'#8d9096',metalness:.25,roughness:.5}}));motor.rotation.z=Math.PI/2;G.add(motor);
 const shaft=new THREE.Mesh(new THREE.CylinderGeometry(.18,.18,3.9,24),new THREE.MeshStandardMaterial({{color:'#d4d5d8',metalness:.55,roughness:.3}}));shaft.rotation.z=Math.PI/2;G.add(shaft);
 const bearingMat=new THREE.MeshStandardMaterial({{color:'#62656c',metalness:.18,roughness:.62}}); const b1=new THREE.Mesh(new THREE.BoxGeometry(.48,1.15,1.18),bearingMat);b1.position.x=-1.55;G.add(b1); const b2=b1.clone();b2.position.x=1.55;G.add(b2);
 const sensor=new THREE.Mesh(new THREE.BoxGeometry(.34,.34,.34),new THREE.MeshStandardMaterial({{color:'#f28e1c'}}); const sensorPositions={{'Motor DE':new THREE.Vector3(1.05,1.03,0),'Motor NDE':new THREE.Vector3(-1.05,1.03,0),'Soporte DE':new THREE.Vector3(1.55,.72,.64),'Soporte NDE':new THREE.Vector3(-1.55,.72,.64),'Base':new THREE.Vector3(0,-.72,1.12)}}; const spos=sensorPositions[D.position]||sensorPositions['Motor DE'];sensor.position.copy(spos);G.add(sensor);
 const axes={{Horizontal:new THREE.Vector3(0,0,1),Vertical:new THREE.Vector3(0,1,0),Axial:new THREE.Vector3(1,0,0)}};const dir=axes[D.orientation]||axes.Horizontal;const arrow=new THREE.ArrowHelper(dir,spos.clone(),1.2,0xf5ead7,.22,.12);G.add(arrow);
 const grid=new THREE.GridHelper(10,10,0x46474c,0x303136);grid.position.y=-1.15;scene.add(grid); const sig=D.signal||[],dur=Math.max(D.duration||3,1e-6),amp=D.visual_amp||1;const smax=Math.max(...sig.map(Math.abs),1e-9);let tm=0,last=performance.now();function sample(a,tt){{if(!a.length)return 0;const u=((tt%dur)/dur)*(a.length-1),i=Math.floor(u),j=Math.min(a.length-1,i+1),q=u-i;return a[i]*(1-q)+a[j]*q}}function update(dt){{if(!paused)tm+=dt;const raw=sample(sig,tm),q=raw/smax*.12*amp;G.position.copy(dir.clone().multiplyScalar(q));read.textContent=`${{D.position}} · ${{D.orientation}} · señal = ${{raw.toFixed(3)}}`;}}
 function front(){{camera.position.set(0,.3,8.5);controls.target.set(0,0,0);controls.update()}}function iso(){{camera.position.set(5,3.5,7.2);controls.target.set(0,0,0);controls.update()}}function fit(){{const b=new THREE.Box3().setFromObject(G),sz=b.getSize(new THREE.Vector3()),ct=b.getCenter(new THREE.Vector3()),md=Math.max(sz.x,sz.y,sz.z,1),f=camera.fov*Math.PI/180,dist=md/(2*Math.tan(f/2))*1.3,di=new THREE.Vector3().subVectors(camera.position,controls.target).normalize();controls.target.copy(ct);camera.position.copy(ct.clone().add(di.multiplyScalar(dist)));controls.update()}}front();fit();document.getElementById('front').onclick=()=>{{front();fit()}};document.getElementById('iso').onclick=()=>{{iso();fit()}};document.getElementById('fit').onclick=fit;document.getElementById('play').onclick=e=>{{paused=!paused;e.target.textContent=paused?'Reproducir':'Pausa'}};msg.textContent=`Sensor ${{D.position}} · ${{D.orientation}}`;function loop(now){{const dt=Math.min(.05,(now-last)/1000);last=now;update(dt);controls.update();renderer.render(scene,camera);requestAnimationFrame(loop)}}requestAnimationFrame(loop);
}}catch(e){{console.error(e);msg.textContent='Vista de respaldo · Three.js no disponible';}}
</script>'''
    components.html(html,height=height,scrolling=False)
