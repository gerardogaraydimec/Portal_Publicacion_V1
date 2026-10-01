from __future__ import annotations
import json
import streamlit.components.v1 as components

TEMPLATE = r'''
<div id="pump3d" style="height:__HEIGHT__px;border:1px solid #ded7cc;border-radius:14px;overflow:hidden;background:#202126;position:relative">
  <div style="position:absolute;z-index:6;left:13px;top:11px;background:#fff8edee;padding:8px 11px;border-radius:10px;font:13px system-ui;color:#25262a;line-height:1.35">
    <b>Sistema hidráulico 3D</b><br><span id="pmsg"></span>
  </div>
  <div id="pread" style="position:absolute;z-index:6;left:13px;bottom:11px;background:#202126e6;border:1px solid #565860;color:#f5ead7;padding:8px 10px;border-radius:9px;font:12px system-ui;max-width:68%"></div>
  <div style="position:absolute;z-index:6;right:11px;top:11px;display:flex;gap:5px;flex-wrap:wrap;max-width:58%">
    <button id="play">Pausa</button><button id="front">Frente</button><button id="iso">Isométrica</button><button id="top">Superior</button><button id="fit">Ajustar</button><button id="reset">Restablecer</button>
  </div>
  <canvas id="pfb" width="1200" height="__HEIGHT__" style="position:absolute;inset:0;width:100%;height:100%;z-index:1"></canvas>
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
  const c=cv.getContext('2d'),W=cv.width,H=cv.height;
  c.fillStyle='#202126';c.fillRect(0,0,W,H);
  const y=H*.56;
  c.strokeStyle='#8d9097';c.lineWidth=22;c.lineCap='round';
  c.beginPath();c.moveTo(135,y);c.lineTo(330,y);c.lineTo(400,y);c.lineTo(650,y);c.lineTo(740,y);c.lineTo(1015,y-80);c.stroke();
  c.strokeStyle='#4fa3b7';c.lineWidth=11;c.beginPath();c.moveTo(135,y);c.lineTo(330,y);c.lineTo(400,y);c.lineTo(650,y);c.lineTo(740,y);c.lineTo(1015,y-80);c.stroke();
  c.fillStyle='#d8d0c0';c.fillRect(55,y-110,125,110);c.fillRect(990,y-230,150,150);
  c.fillStyle='#4fa3b7';c.globalAlpha=.45;c.fillRect(65,y-65,105,65);c.fillRect(1000,y-155,130,75);c.globalAlpha=1;
  c.fillStyle='#c8752d';c.beginPath();c.arc(365,y,52,0,Math.PI*2);c.fill();
  c.strokeStyle='#f28e1c';c.lineWidth=6;c.beginPath();c.moveTo(690,y-55);c.lineTo(720,y+55);c.moveTo(720,y-55);c.lineTo(690,y+55);c.stroke();
  c.fillStyle='#f5ead7';c.font='600 18px system-ui';
  c.fillText('SUCCIÓN',210,y-35);c.fillText('BOMBA',330,y+88);c.fillText('VÁLVULA',655,y+88);c.fillText('DESCARGA',900,y-120);
  msg.textContent='Vista de respaldo · cargando 3D';
  read.textContent='Qop = '+Number(D.q_lps||0).toFixed(2)+' L/s · Hop = '+Number(D.head_m||0).toFixed(2)+' m';
}
fallback();

try{
  const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm');
  const {OrbitControls}=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm');

  const scene=new THREE.Scene();
  scene.background=new THREE.Color('#202126');
  const camera=new THREE.PerspectiveCamera(35,Math.max(root.clientWidth,1)/__HEIGHT__,.05,120);
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
  renderer.setSize(Math.max(root.clientWidth,1),__HEIGHT__);
  renderer.domElement.style.position='absolute';renderer.domElement.style.inset='0';renderer.domElement.style.zIndex='2';
  root.appendChild(renderer.domElement);

  const controls=new OrbitControls(camera,renderer.domElement);
  controls.enableDamping=true;controls.dampingFactor=.08;controls.zoomToCursor=true;controls.minDistance=5;controls.maxDistance=42;

  scene.add(new THREE.AmbientLight('#ffffff',1.15));
  scene.add(new THREE.HemisphereLight('#fff8ec','#303136',1.7));
  const dl=new THREE.DirectionalLight('#ffffff',2.2);dl.position.set(6,8,9);scene.add(dl);

  const model=new THREE.Group();scene.add(model);
  const labels=new THREE.Group();scene.add(labels);

  const matTank=new THREE.MeshStandardMaterial({color:'#d6cfc2',roughness:.76,transparent:true,opacity:.72,side:THREE.DoubleSide});
  const matPipe=new THREE.MeshStandardMaterial({color:'#8d9097',metalness:.28,roughness:.45});
  const matPump=new THREE.MeshStandardMaterial({color:'#c8752d',roughness:.58});
  const matWater=new THREE.MeshStandardMaterial({color:'#4fa3b7',emissive:'#173f48',transparent:true,opacity:.55,roughness:.18});
  const matValve=new THREE.MeshStandardMaterial({color:'#f28e1c',roughness:.50});

  const floor=new THREE.Mesh(new THREE.BoxGeometry(12.7,.16,4.7),new THREE.MeshStandardMaterial({color:'#2e3036',roughness:.92}));
  floor.position.set(.15,-1.52,0);model.add(floor);
  const grid=new THREE.GridHelper(13,13,0x48494e,0x323338);grid.position.y=-1.40;scene.add(grid);

  function addEdges(mesh,color=0x8e887e){
    const e=new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry),new THREE.LineBasicMaterial({color,transparent:true,opacity:.8}));
    e.position.copy(mesh.position);e.rotation.copy(mesh.rotation);e.scale.copy(mesh.scale);return e;
  }

  function tank(x,h,w,d,level){
    const g=new THREE.Group();
    const shell=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),matTank);shell.position.y=h/2-1.35;g.add(shell);g.add(addEdges(shell));
    const wh=Math.max(.10,h*level);const water=new THREE.Mesh(new THREE.BoxGeometry(w*.90,wh,d*.90),matWater);water.position.y=-1.31+wh/2;g.add(water);
    g.position.x=x;model.add(g);return g;
  }
  tank(-5.0,2.0,1.8,2.0,.68);tank(5.15,3.0,2.0,2.15,.72);

  function pipeBetween(a,b,r=.12){
    const va=new THREE.Vector3(...a),vb=new THREE.Vector3(...b);const dir=new THREE.Vector3().subVectors(vb,va);const len=dir.length();const mid=new THREE.Vector3().addVectors(va,vb).multiplyScalar(.5);
    const mesh=new THREE.Mesh(new THREE.CylinderGeometry(r,r,len,28),matPipe);mesh.position.copy(mid);mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.clone().normalize());model.add(mesh);return mesh;
  }
  const path=[[-4.40,-.58,0],[-3.35,-.58,0],[-2.70,-.10,0],[-1.60,-.10,0],[-.55,-.10,0],[.55,-.10,0],[1.55,-.10,0],[2.70,.35,0],[4.15,.35,0],[4.55,1.10,0],[4.55,1.60,0]];
  for(let i=0;i<path.length-1;i++)pipeBetween(path[i],path[i+1]);

  const pumpG=new THREE.Group();pumpG.position.set(-2.12,-.10,0);model.add(pumpG);
  const casing=new THREE.Mesh(new THREE.CylinderGeometry(.52,.52,.56,40),matPump);casing.rotation.z=Math.PI/2;pumpG.add(casing);
  const rim=new THREE.Mesh(new THREE.TorusGeometry(.39,.055,12,40),new THREE.MeshStandardMaterial({color:'#f0dfc7',metalness:.2,roughness:.4}));rim.rotation.y=Math.PI/2;pumpG.add(rim);
  const hub=new THREE.Mesh(new THREE.CylinderGeometry(.11,.11,.63,24),new THREE.MeshStandardMaterial({color:'#eee4d6',metalness:.35,roughness:.35}));hub.rotation.z=Math.PI/2;pumpG.add(hub);
  const impeller=new THREE.Group();pumpG.add(impeller);
  for(let i=0;i<6;i++){const blade=new THREE.Mesh(new THREE.BoxGeometry(.07,.31,.09),new THREE.MeshStandardMaterial({color:'#fff3df'}));blade.position.y=.22;blade.rotation.x=i*Math.PI/3;impeller.add(blade);}

  const valveG=new THREE.Group();valveG.position.set(1.60,-.10,0);model.add(valveG);
  const valveBody=new THREE.Mesh(new THREE.SphereGeometry(.29,24,18),matValve);valveG.add(valveBody);
  const stem=new THREE.Mesh(new THREE.CylinderGeometry(.045,.045,.60,18),matValve);stem.position.y=.38;valveG.add(stem);
  const handle=new THREE.Mesh(new THREE.BoxGeometry(.68,.075,.10),matValve);handle.position.y=.69;handle.rotation.y=(1-Number(D.valve_opening||1))*Math.PI*.42;valveG.add(handle);

  const curve=new THREE.CatmullRomCurve3(path.map(p=>new THREE.Vector3(...p)));
  const particles=[];const pmat=new THREE.MeshStandardMaterial({color:'#7fd7e8',emissive:'#214b55',roughness:.25});
  for(let i=0;i<32;i++){const s=new THREE.Mesh(new THREE.SphereGeometry(.060,12,10),pmat);model.add(s);particles.push({mesh:s,phase:i/32});}

  function makeLabel(text,color='#f5ead7'){
    const cn=document.createElement('canvas');cn.width=400;cn.height=90;const cx=cn.getContext('2d');cx.font='600 34px system-ui';cx.textAlign='center';cx.fillStyle=color;cx.fillText(text,200,55);const tex=new THREE.CanvasTexture(cn);const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,transparent:true,depthTest:false}));sp.scale.set(1.60,.37,1);labels.add(sp);return sp;
  }
  makeLabel('BOMBA').position.set(-2.12,.86,0);
  makeLabel('VÁLVULA').position.set(1.60,.92,0);
  makeLabel('SUCCIÓN','#b7dce3').position.set(-3.65,.08,0);
  makeLabel('DESCARGA','#b7dce3').position.set(3.25,.92,0);

  let tm=0,last=performance.now();
  const flowSpeed=Math.max(.05,Math.min(1.8,Number(D.velocity_ms||0)*.32));
  const rpmSpeed=Math.max(.2,Math.min(4.5,Number(D.rpm||1800)/900));

  function front(){camera.position.set(.10,.90,15.8);controls.target.set(.10,-.05,0);camera.lookAt(controls.target);controls.update();}
  function iso(){camera.position.set(9.5,5.5,11.0);controls.target.set(.10,-.05,0);camera.lookAt(controls.target);controls.update();}
  function top(){camera.position.set(.10,12.5,.01);controls.target.set(.10,-.05,0);camera.lookAt(controls.target);controls.update();}
  function fit(){
    const b=new THREE.Box3().setFromObject(model);const sz=b.getSize(new THREE.Vector3()),ct=b.getCenter(new THREE.Vector3());
    const md=Math.max(sz.x,sz.y,sz.z,1);const f=camera.fov*Math.PI/180;let dist=md/(2*Math.tan(f/2))*1.22;dist=Math.max(8,Math.min(34,dist));
    const dir=new THREE.Vector3().subVectors(camera.position,controls.target);if(dir.lengthSq()<1e-6)dir.set(0,0,1);dir.normalize();
    controls.target.copy(ct);camera.position.copy(ct.clone().add(dir.multiplyScalar(dist)));camera.lookAt(ct);controls.update();
  }
  function reset(){front();}
  reset();

  function update(dt){
    if(!paused)tm+=dt;
    if(!paused)impeller.rotation.x += dt*rpmSpeed*4.0;
    for(const p of particles){const u=(p.phase+tm*flowSpeed*.10)%1;p.mesh.position.copy(curve.getPointAt(u));}
    read.innerHTML='Q<sub>op</sub> = <b>'+Number(D.q_lps||0).toFixed(2)+' L/s</b> · H<sub>op</sub> = <b>'+Number(D.head_m||0).toFixed(2)+' m</b> · V descarga = <b>'+Number(D.velocity_ms||0).toFixed(2)+' m/s</b> · válvula = <b>'+(100*Number(D.valve_opening||1)).toFixed(0)+'%</b>';
  }

  document.getElementById('front').onclick=front;
  document.getElementById('iso').onclick=iso;
  document.getElementById('top').onclick=top;
  document.getElementById('fit').onclick=fit;
  document.getElementById('reset').onclick=reset;
  document.getElementById('play').onclick=e=>{paused=!paused;e.target.textContent=paused?'Reproducir':'Pausa'};
  msg.textContent=(D.arrangement||'Una bomba')+' · '+Number(D.rpm||0).toFixed(0)+' rpm';

  // First render with a fixed, known-safe camera. Only then hide the 2D fallback.
  controls.update();renderer.render(scene,camera);cv.style.display='none';

  window.addEventListener('resize',()=>{camera.aspect=Math.max(root.clientWidth,1)/__HEIGHT__;camera.updateProjectionMatrix();renderer.setSize(Math.max(root.clientWidth,1),__HEIGHT__)});
  function loop(now){const dt=Math.min(.05,(now-last)/1000);last=now;update(dt);controls.update();renderer.render(scene,camera);requestAnimationFrame(loop)}
  requestAnimationFrame(loop);
}catch(e){
  console.error(e);cv.style.display='block';msg.textContent='Vista 2D de respaldo · visor 3D no disponible';
}
</script>
'''


def render_pump_system_3d(data: dict, height: int = 620):
    html = TEMPLATE.replace('__HEIGHT__', str(int(height))).replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    components.html(html, height=height, scrolling=False)
