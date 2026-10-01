from __future__ import annotations
import json
import streamlit.components.v1 as components

TEMPLATE = r'''
<div id="pump3d" style="height:__HEIGHT__px;border:1px solid #ded7cc;border-radius:14px;overflow:hidden;background:#202126;position:relative">
  <div style="position:absolute;z-index:5;left:13px;top:11px;background:#fff8edee;padding:8px 11px;border-radius:10px;font:13px system-ui;color:#25262a;line-height:1.35">
    <b>Sistema hidráulico 3D</b><br><span id="pmsg"></span>
  </div>
  <div id="pread" style="position:absolute;z-index:5;left:13px;bottom:11px;background:#202126e6;border:1px solid #565860;color:#f5ead7;padding:8px 10px;border-radius:9px;font:12px system-ui;max-width:62%"></div>
  <div style="position:absolute;z-index:5;right:11px;top:11px;display:flex;gap:5px;flex-wrap:wrap;max-width:58%">
    <button id="play">Pausa</button><button id="front">Frente</button><button id="iso">Isométrica</button><button id="top">Superior</button><button id="fit">Ajustar</button><button id="reset">Restablecer</button>
  </div>
  <canvas id="pfb" width="1000" height="__HEIGHT__" style="width:100%;height:100%"></canvas>
</div>
<style>
#pump3d button{border:1px solid #c8752d;background:#fff8ed;color:#292a2e;border-radius:8px;padding:7px 9px;cursor:pointer}
#pump3d button:hover{background:#fff1dd}
</style>
<script type="module">
const D=__DATA__;
const root=document.getElementById('pump3d'),cv=document.getElementById('pfb'),msg=document.getElementById('pmsg'),read=document.getElementById('pread');
let paused=false;
function fallback(){
  const c=cv.getContext('2d'),W=cv.width,H=cv.height;c.fillStyle='#202126';c.fillRect(0,0,W,H);
  const y=H*.56;c.strokeStyle='#4fa3b7';c.lineWidth=16;c.beginPath();c.moveTo(110,y);c.lineTo(330,y);c.lineTo(360,y);c.lineTo(550,y);c.lineTo(600,y);c.lineTo(820,y);c.stroke();
  c.fillStyle='#d8d0c0';c.fillRect(55,y-95,110,95);c.fillRect(790,y-150,135,150);
  c.fillStyle='#c8752d';c.beginPath();c.arc(360,y,45,0,Math.PI*2);c.fill();
  c.strokeStyle='#f28e1c';c.lineWidth=5;c.beginPath();c.moveTo(590,y-45);c.lineTo(610,y+45);c.moveTo(610,y-45);c.lineTo(590,y+45);c.stroke();
  c.fillStyle='#f5ead7';c.font='15px system-ui';c.fillText('Depósito succión',50,y+35);c.fillText('Bomba',335,y+70);c.fillText('Válvula',565,y+70);c.fillText('Depósito descarga',780,y+35);
  msg.textContent='Vista de respaldo · sistema hidráulico';
  read.textContent='Qop = '+Number(D.q_lps||0).toFixed(2)+' L/s · Hop = '+Number(D.head_m||0).toFixed(2)+' m';
}
fallback();
try{
  const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm');
  const {OrbitControls}=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm');
  cv.style.display='none';
  const scene=new THREE.Scene();scene.background=new THREE.Color('#202126');
  const camera=new THREE.PerspectiveCamera(34,root.clientWidth/__HEIGHT__,.01,180);
  const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.setSize(root.clientWidth,__HEIGHT__);root.appendChild(renderer.domElement);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.zoomToCursor=true;controls.minDistance=4;controls.maxDistance=45;
  scene.add(new THREE.HemisphereLight('#fff8ec','#303136',2.2));const dl=new THREE.DirectionalLight('#fff',2);dl.position.set(5,8,7);scene.add(dl);
  const G=new THREE.Group();scene.add(G);
  const matTank=new THREE.MeshStandardMaterial({color:'#d6cfc2',roughness:.75,transparent:true,opacity:.82});
  const matPipe=new THREE.MeshStandardMaterial({color:'#8d9097',metalness:.25,roughness:.48});
  const matPump=new THREE.MeshStandardMaterial({color:'#c8752d',roughness:.65});
  const matWater=new THREE.MeshStandardMaterial({color:'#4fa3b7',transparent:true,opacity:.38,roughness:.25});
  const matValve=new THREE.MeshStandardMaterial({color:'#f28e1c',roughness:.55});
  const floor=new THREE.Mesh(new THREE.BoxGeometry(12,.16,5),new THREE.MeshStandardMaterial({color:'#2e3036',roughness:.9}));floor.position.set(.2,-1.5,0);G.add(floor);
  const grid=new THREE.GridHelper(13,13,0x48494e,0x323338);grid.position.y=-1.40;scene.add(grid);

  function tank(x,z,h,w,d,level){
    const g=new THREE.Group();
    const box=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),matTank);box.position.y=h/2-1.35;g.add(box);
    const waterH=Math.max(.08,h*level);const water=new THREE.Mesh(new THREE.BoxGeometry(w*.91,waterH,d*.91),matWater);water.position.y=-1.30+waterH/2;g.add(water);g.position.set(x,0,z);G.add(g);return g;
  }
  const t1=tank(-5.0,0,2.0,1.8,2.0,.68);const t2=tank(5.2,0,3.0,2.0,2.15,.72);

  function pipeBetween(a,b,r=.105){
    const va=new THREE.Vector3(...a),vb=new THREE.Vector3(...b),dir=new THREE.Vector3().subVectors(vb,va),len=dir.length(),mid=new THREE.Vector3().addVectors(va,vb).multiplyScalar(.5);
    const mesh=new THREE.Mesh(new THREE.CylinderGeometry(r,r,len,24),matPipe);mesh.position.copy(mid);mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.clone().normalize());G.add(mesh);return mesh;
  }
  const path=[[-4.45,-.65,0],[-3.4,-.65,0],[-2.65,-.15,0],[-1.65,-.15,0],[-.65,-.15,0],[.4,-.15,0],[1.5,-.15,0],[2.7,.35,0],[4.25,.35,0],[4.55,1.15,0],[4.55,1.65,0]];
  for(let i=0;i<path.length-1;i++)pipeBetween(path[i],path[i+1]);

  const pumpG=new THREE.Group();G.add(pumpG);pumpG.position.set(-2.15,-.15,0);
  const casing=new THREE.Mesh(new THREE.CylinderGeometry(.48,.48,.50,36),matPump);casing.rotation.z=Math.PI/2;pumpG.add(casing);
  const hub=new THREE.Mesh(new THREE.CylinderGeometry(.12,.12,.58,24),new THREE.MeshStandardMaterial({color:'#e3d9c9',metalness:.3,roughness:.4}));hub.rotation.z=Math.PI/2;pumpG.add(hub);
  const impeller=new THREE.Group();pumpG.add(impeller);for(let i=0;i<6;i++){const blade=new THREE.Mesh(new THREE.BoxGeometry(.08,.32,.08),new THREE.MeshStandardMaterial({color:'#f4eadb'}));blade.position.y=.21;blade.rotation.x=i*Math.PI/3;impeller.add(blade);}

  const valveG=new THREE.Group();G.add(valveG);valveG.position.set(1.65,-.15,0);
  const valveBody=new THREE.Mesh(new THREE.SphereGeometry(.27,22,16),matValve);valveG.add(valveBody);
  const stem=new THREE.Mesh(new THREE.CylinderGeometry(.04,.04,.55,16),matValve);stem.position.y=.35;valveG.add(stem);
  const handle=new THREE.Mesh(new THREE.BoxGeometry(.62,.07,.08),matValve);handle.position.y=.63;valveG.add(handle);handle.rotation.y=(1-Number(D.valve_opening||1))*Math.PI*.42;

  // Static-head reference line between reservoir free surfaces.
  const zline=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-5,1.0,-1.25),new THREE.Vector3(5.2,1.0+Math.max(-.8,Math.min(1.8,Number(D.static_head_m||0)*.08)),-1.25)]),new THREE.LineDashedMaterial({color:0xf28e1c,dashSize:.16,gapSize:.10}));zline.computeLineDistances();G.add(zline);

  // Flow particles along the hydraulic path.
  const curve=new THREE.CatmullRomCurve3(path.map(p=>new THREE.Vector3(...p)));
  const particles=[];const pmat=new THREE.MeshStandardMaterial({color:'#77d1e1',emissive:'#224a53',roughness:.3});
  for(let i=0;i<28;i++){const s=new THREE.Mesh(new THREE.SphereGeometry(.055,12,10),pmat);G.add(s);particles.push({mesh:s,phase:i/28});}

  function makeLabel(text,color='#f5ead7'){
    const cn=document.createElement('canvas');cn.width=360;cn.height=80;const cx=cn.getContext('2d');cx.font='600 31px system-ui';cx.textAlign='center';cx.fillStyle=color;cx.fillText(text,180,48);const tex=new THREE.CanvasTexture(cn);const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,transparent:true,depthTest:false}));sp.scale.set(1.55,.36,1);G.add(sp);return sp;
  }
  const lp=makeLabel('BOMBA','#f5ead7');lp.position.set(-2.15,.80,0);const lv=makeLabel('VÁLVULA','#f5ead7');lv.position.set(1.65,.86,0);
  const ls=makeLabel('SUCCIÓN','#b7dce3');ls.position.set(-3.7,.10,0);const ld=makeLabel('DESCARGA','#b7dce3');ld.position.set(3.3,.88,0);

  let tm=0,last=performance.now();
  const flowSpeed=Math.max(.05,Math.min(1.8,Number(D.velocity_ms||0)*.32));
  const rpmSpeed=Math.max(.2,Math.min(4.5,Number(D.rpm||1800)/900));
  function update(dt){
    if(!paused)tm+=dt;
    impeller.rotation.x += paused?0:dt*rpmSpeed*4.0;
    for(const p of particles){const u=(p.phase+tm*flowSpeed*.10)%1;p.mesh.position.copy(curve.getPointAt(u));}
    read.innerHTML=`Q<sub>op</sub> = <b>${Number(D.q_lps||0).toFixed(2)} L/s</b> · H<sub>op</sub> = <b>${Number(D.head_m||0).toFixed(2)} m</b> · V descarga = <b>${Number(D.velocity_ms||0).toFixed(2)} m/s</b> · apertura válvula = <b>${(100*Number(D.valve_opening||1)).toFixed(0)}%</b>`;
  }
  function front(){camera.position.set(.2,.6,13.5);controls.target.set(.1,-.1,0);controls.update()}
  function iso(){camera.position.set(9,5.6,10.5);controls.target.set(.1,-.1,0);controls.update()}
  function top(){camera.position.set(.1,11,.01);controls.target.set(.1,-.1,0);controls.update()}
  function fit(){const b=new THREE.Box3().setFromObject(G),sz=b.getSize(new THREE.Vector3()),ct=b.getCenter(new THREE.Vector3()),md=Math.max(sz.x,sz.y,sz.z,1),f=camera.fov*Math.PI/180,dist=md/(2*Math.tan(f/2))*1.28,dir=new THREE.Vector3().subVectors(camera.position,controls.target).normalize();controls.target.copy(ct);camera.position.copy(ct.clone().add(dir.multiplyScalar(dist)));controls.update()}
  function reset(){front();fit()} reset();
  document.getElementById('front').onclick=()=>{front();fit()};document.getElementById('iso').onclick=()=>{iso();fit()};document.getElementById('top').onclick=()=>{top();fit()};document.getElementById('fit').onclick=fit;document.getElementById('reset').onclick=reset;document.getElementById('play').onclick=e=>{paused=!paused;e.target.textContent=paused?'Reproducir':'Pausa'};
  msg.textContent=(D.arrangement||'Una bomba')+' · '+Number(D.rpm||0).toFixed(0)+' rpm';
  window.addEventListener('resize',()=>{camera.aspect=root.clientWidth/__HEIGHT__;camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,__HEIGHT__)});
  function loop(now){const dt=Math.min(.05,(now-last)/1000);last=now;update(dt);controls.update();renderer.render(scene,camera);requestAnimationFrame(loop)}requestAnimationFrame(loop);
}catch(e){console.error(e);msg.textContent='Vista de respaldo · Three.js no disponible';}
</script>
'''


def render_pump_system_3d(data: dict, height: int = 620):
    html = TEMPLATE.replace('__HEIGHT__', str(int(height))).replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    components.html(html, height=height, scrolling=False)
