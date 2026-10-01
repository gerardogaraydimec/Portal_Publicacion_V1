from __future__ import annotations

import json
import streamlit.components.v1 as components


def render_machine_hydraulics_3d(data: dict, height: int = 640):
    payload=json.dumps(data,ensure_ascii=False,separators=(",",":"))
    html=r'''
<div id="hyd3d" class="root">
  <canvas id="fallback" width="1200" height="__HEIGHT__"></canvas>
  <div class="badge"><b id="title">Modelo físico 3D</b><span id="status"></span></div>
  <div class="tools"><button id="play">Pausa</button><button id="front">Frente</button><button id="iso">Isométrica</button><button id="side">Lateral</button><button id="top">Superior</button><button id="fit">Ajustar</button></div>
  <div class="legend" id="legend"></div>
</div>
<style>
html,body{margin:0;background:transparent;font-family:system-ui,-apple-system,Segoe UI,sans-serif}.root{height:__HEIGHT__px;position:relative;overflow:hidden;border-radius:16px;border:1px solid #32343a;background:#202126}.root canvas{position:absolute;inset:0;width:100%;height:100%}.badge{position:absolute;z-index:6;left:13px;top:12px;background:#fff8edee;border:1px solid #d8c3a7;padding:8px 11px;border-radius:10px;color:#202126;font-size:12px;line-height:1.35}.badge b{display:block;font-size:13px}.badge span{color:#5d6066}.tools{position:absolute;z-index:6;right:11px;top:11px;display:flex;gap:5px;flex-wrap:wrap;max-width:72%;justify-content:flex-end}.tools button{border:1px solid #c8752d;background:#fff8ed;color:#292a2e;border-radius:8px;padding:7px 9px;cursor:pointer;font-size:12px}.tools button:hover{background:#fff0dc}.legend{position:absolute;z-index:6;left:13px;bottom:11px;max-width:82%;background:#17181bdc;border:1px solid #55575e;color:#f5ead7;padding:8px 10px;border-radius:9px;font-size:12px;line-height:1.45}
</style>
<script type="module">
const D=__DATA__,root=document.getElementById('hyd3d'),cv=document.getElementById('fallback'),ctx=cv.getContext('2d'),status=document.getElementById('status'),legend=document.getElementById('legend');let paused=false;
function fallback(){const W=cv.width,H=cv.height;ctx.fillStyle='#202126';ctx.fillRect(0,0,W,H);ctx.fillStyle='#f28e1c';ctx.font='700 30px system-ui';ctx.fillText(D.machine,50,85);ctx.fillStyle='#f5ead7';ctx.font='20px system-ui';ctx.fillText(D.subsystem+' · '+D.state,50,120);ctx.strokeStyle='#f28e1c';ctx.lineWidth=6;ctx.strokeRect(120,200,W-240,H-330);ctx.fillStyle='#a6abb4';ctx.font='18px system-ui';ctx.fillText('Vista de respaldo: el navegador no cargó WebGL/Three.js.',150,H-75)}fallback();
try{
 const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm');
 const {OrbitControls}=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm');
 const scene=new THREE.Scene();scene.background=new THREE.Color('#202126');scene.fog=new THREE.Fog('#202126',18,45);
 const camera=new THREE.PerspectiveCamera(33,root.clientWidth/__HEIGHT__,.02,120);camera.position.set(0,2.5,14);
 const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.setSize(root.clientWidth,__HEIGHT__);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;root.appendChild(renderer.domElement);
 const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.07;controls.zoomToCursor=true;controls.minDistance=4.2;controls.maxDistance=36;controls.screenSpacePanning=true;controls.target.set(0,.1,0);
 scene.add(new THREE.HemisphereLight('#fff8ec','#292a31',2.2));const key=new THREE.DirectionalLight('#ffffff',3.0);key.position.set(7,10,9);key.castShadow=true;key.shadow.mapSize.set(2048,2048);scene.add(key);const fill=new THREE.DirectionalLight('#f5b36b',1.0);fill.position.set(-8,4,5);scene.add(fill);
 const ground=new THREE.Mesh(new THREE.PlaneGeometry(32,22),new THREE.MeshStandardMaterial({color:'#27292e',roughness:.95,metalness:.03}));ground.rotation.x=-Math.PI/2;ground.position.y=-1.55;ground.receiveShadow=true;scene.add(ground);const grid=new THREE.GridHelper(22,22,0x4a4d54,0x34363c);grid.position.y=-1.545;scene.add(grid);
 const G=new THREE.Group();scene.add(G);const moving=[];const flows=[];const particles=[];
 const M={yellow:new THREE.MeshStandardMaterial({color:'#d79b28',roughness:.55,metalness:.16}),dark:new THREE.MeshStandardMaterial({color:'#25272c',roughness:.7}),metal:new THREE.MeshStandardMaterial({color:'#7e848d',roughness:.36,metalness:.62}),rod:new THREE.MeshStandardMaterial({color:'#d7d9dd',roughness:.18,metalness:.9}),glass:new THREE.MeshStandardMaterial({color:'#6d8594',roughness:.18,metalness:.25,transparent:true,opacity:.78}),orange:new THREE.MeshStandardMaterial({color:'#f28e1c',roughness:.42,metalness:.15}),red:new THREE.MeshStandardMaterial({color:'#d84030',roughness:.45}),blue:new THREE.MeshStandardMaterial({color:'#2a63b8',roughness:.45}),green:new THREE.MeshStandardMaterial({color:'#4e9b57',roughness:.45}),pilot:new THREE.MeshStandardMaterial({color:'#d6b72c',roughness:.45}),gray:new THREE.MeshStandardMaterial({color:'#5e636b',roughness:.6})};
 const roleMat={pressure:M.red,return:M.blue,suction:M.green,pilot:M.pilot,drain:M.orange};
 function shadow(o){o.traverse?.(c=>{if(c.isMesh){c.castShadow=true;c.receiveShadow=true}});return o}
 function box(w,h,d,mat,x,y,z,parent=G){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);m.position.set(x,y,z);parent.add(m);shadow(m);return m}
 function cylMesh(x,y,z,len=.9,rz=0,parent=G,rad=.13){const g=new THREE.Group();const b=new THREE.Mesh(new THREE.CylinderGeometry(rad,rad,len,28),M.metal);b.rotation.z=Math.PI/2;g.add(b);const r=new THREE.Mesh(new THREE.CylinderGeometry(rad*.42,rad*.42,len*.92,22),M.rod);r.rotation.z=Math.PI/2;r.position.x=len*.70;g.add(r);g.position.set(x,y,z);g.rotation.z=rz;parent.add(g);shadow(g);return g}
 function wheel(x,z,r=.72,parent=G){const t=new THREE.Mesh(new THREE.CylinderGeometry(r,r,.48,40),M.dark);t.rotation.z=Math.PI/2;t.position.set(x,-.83,z);parent.add(t);const h=new THREE.Mesh(new THREE.CylinderGeometry(r*.42,r*.42,.52,30),M.yellow);h.rotation.z=Math.PI/2;h.position.copy(t.position);parent.add(h);shadow(t);shadow(h);return t}
 function pipe(points,role='pressure',active=true,r=.034,parent=G){const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)));const mat=active?(roleMat[role]||M.gray):M.gray;const mesh=new THREE.Mesh(new THREE.TubeGeometry(curve,60,r,10,false),mat);mesh.material.transparent=!active;mesh.material.opacity=active?1:.42;parent.add(mesh);shadow(mesh);if(active){flows.push({curve,role});for(let j=0;j<2;j++){const p=new THREE.Mesh(new THREE.SphereGeometry(r*1.9,14,10),roleMat[role]);parent.add(p);particles.push({mesh:p,curve,phase:j/2,role})}}return mesh}
 function label(text,x,y,z,color='#f5ead7',scale=1){if(D.study_mode==='Técnico')return null;const cn=document.createElement('canvas');cn.width=620;cn.height=96;const c=cn.getContext('2d');c.font='600 30px system-ui';c.textAlign='center';c.fillStyle=color;c.fillText(text,310,56);const tex=new THREE.CanvasTexture(cn);const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,transparent:true,depthTest:false}));sp.scale.set(2.45*scale,.38*scale,1);sp.position.set(x,y,z);G.add(sp);return sp}
 function active(key){return (D.active_components||[]).includes(key)}
 function matFor(key,normal=M.metal){return active(key)?M.orange:normal}
 function tank3d(x,y,z,parent=G){const g=new THREE.Group();box(1.35,.95,1.35,M.dark,0,0,0,g);box(.9,.05,.12,M.glass,.23,.03,.69,g);const cap=new THREE.Mesh(new THREE.CylinderGeometry(.15,.15,.18,24),M.metal);cap.position.set(-.25,.58,0);g.add(cap);g.position.set(x,y,z);parent.add(g);shadow(g);return g}
 function motor3d(x,y,z,parent=G){const g=new THREE.Group();const m=new THREE.Mesh(new THREE.CylinderGeometry(.42,.42,1.05,32),M.dark);m.rotation.z=Math.PI/2;g.add(m);for(let i=-3;i<=3;i++){const f=new THREE.Mesh(new THREE.TorusGeometry(.43,.02,8,30),M.metal);f.rotation.y=Math.PI/2;f.position.x=i*.11;g.add(f)}g.position.set(x,y,z);parent.add(g);shadow(g);return g}
 function pump3d(x,y,z,keyName='Bomba',parent=G){const g=new THREE.Group();const b=new THREE.Mesh(new THREE.CylinderGeometry(.31,.31,.55,28),matFor(keyName,M.metal));b.rotation.z=Math.PI/2;g.add(b);const shaft=new THREE.Mesh(new THREE.CylinderGeometry(.09,.09,.45,18),M.rod);shaft.rotation.z=Math.PI/2;shaft.position.x=-.42;g.add(shaft);g.position.set(x,y,z);parent.add(g);shadow(g);return g}
 function manifold(x,y,z,keyName='Banco implementos',parent=G){const g=new THREE.Group();box(.9,.48,1.12,matFor(keyName,M.dark),0,0,0,g);for(let i=-2;i<=2;i++){const p=new THREE.Mesh(new THREE.CylinderGeometry(.065,.065,.14,16),M.metal);p.position.set(i*.16,.31,.35);g.add(p)}g.position.set(x,y,z);parent.add(g);shadow(g);return g}
 function accumulator3d(x,y,z,parent=G){const g=new THREE.Group();const body=new THREE.Mesh(new THREE.CapsuleGeometry(.19,.55,8,16),matFor('Acumuladores',M.dark));body.rotation.z=Math.PI/2;g.add(body);g.position.set(x,y,z);parent.add(g);shadow(g);return g}
 // --- models ---
 if(D.machine==='Camión minero'){
   box(6.0,.42,2.4,M.yellow,0,-.45,0);box(1.0,.62,2.1,M.yellow,-2.55,.0,0);box(1.45,1.35,2.02,M.dark,-1.85,.58,0);box(1.12,.65,1.82,M.glass,-1.87,.78,0);box(.62,.85,2.08,M.yellow,-1.12,.22,0);
   for(const [x,z,r] of [[-2.05,1.08,.73],[-2.05,-1.08,.73],[1.02,1.08,.80],[1.02,-1.08,.80],[2.20,1.08,.80],[2.20,-1.08,.80]])wheel(x,z,r);
   const bed=new THREE.Group();const floor=box(4.45,.18,2.35,M.yellow,-1.6,.0,0,bed);box(3.95,1.0,.10,M.yellow,-1.45,.5,1.13,bed);box(3.95,1.0,.10,M.yellow,-1.45,.5,-1.13,bed);box(.16,1.35,2.35,M.yellow,.55,.55,0,bed);bed.position.set(2.0,.73,0);G.add(bed);shadow(bed);moving.push({type:'bed',obj:bed});
   const h1=cylMesh(.1,.08,.62,1.45,.65),h2=cylMesh(.1,.08,-.62,1.45,.65);moving.push({type:'hoist',obj:h1},{type:'hoist',obj:h2});
   pump3d(-.7,-.02,.0,'Bomba');manifold(.0,.18,0,D.subsystem==='Levante de tolva'?'Hoist valve':'HMU');
   if(D.subsystem==='Levante de tolva'){
     const press=(D.pressure||[]).length>0,ret=(D.return||[]).length>0,pil=(D.pilot||[]).length>0;
     pipe([[-.7,.05,.80],[-.25,.12,.80],[.25,.18,.72],[.65,.25,.62]],'pressure',press,.045);pipe([[.65,.10,-.62],[.25,.0,-.72],[-.25,-.05,-.80],[-.7,-.02,-.80]],'return',ret,.045);pipe([[-.35,.36,0],[.05,.48,0],[.4,.45,0]],'pilot',pil,.026);label('Cilindros de levante',.75,1.75,0);label('Bomba + hoist valve',-.45,1.18,0,'#d8c44a',.88);
   }else if(D.subsystem==='Dirección hidrostática'){
     const s1=cylMesh(-2.1,-.10,.72,.88,0),s2=cylMesh(-2.1,-.10,-.72,.88,0);moving.push({type:'steer',obj:s1,sign:1},{type:'steer',obj:s2,sign:-1});pipe([[-.4,.12,.6],[-1.05,.12,.72],[-1.65,.0,.72]],'pressure',(D.pressure||[]).length>0,.04);pipe([[-1.65,-.06,-.72],[-1.05,-.10,-.72],[-.4,-.02,-.6]],'return',(D.return||[]).length>0,.04);pipe([[-.3,.32,0],[-.75,.45,0],[-1.2,.42,0]],'pilot',(D.pilot||[]).length>0,.025);label('HMU / prioridad / LS',-.7,1.55,0,'#d8c44a',.9);
   }else{
     for(const x of [-.6,.1,.8])accumulator3d(x,.4,1.2);for(const x of [-2.05,1.02,2.2]){const disc=new THREE.Mesh(new THREE.TorusGeometry(.36,.06,12,32),matFor('Frenos',M.metal));disc.rotation.y=Math.PI/2;disc.position.set(x,-.82,1.34);G.add(disc)}pipe([[-.7,.05,.5],[-.2,.18,.75],[.35,.38,1.05]],'pressure',(D.pressure||[]).length>0,.04);label('Acumuladores de freno',.15,1.65,1.05,'#f5ead7',.9);
   }
 } else if(D.machine==='Cargador frontal'){
   const rear=new THREE.Group(),front=new THREE.Group();G.add(rear);G.add(front);box(2.8,.62,2.25,M.yellow,-.6,-.35,0,rear);box(1.25,1.42,1.92,M.dark,-1.05,.60,0,rear);box(.93,.72,1.70,M.glass,-1.03,.82,0,rear);box(1.35,.75,2.08,M.yellow,.72,.0,0,rear);box(2.35,.58,2.12,M.yellow,1.2,-.38,0,front);rear.position.x=-.75;front.position.x=.75;moving.push({type:'rear',obj:rear},{type:'front',obj:front});wheel(-2.0,1.05,.74);wheel(-2.0,-1.05,.74);wheel(1.95,1.02,.78);wheel(1.95,-1.02,.78);box(.25,.78,.72,M.dark,.0,-.12,0);pump3d(-.25,.05,.0,'Bomba LS');manifold(.55,.30,0,'Banco implementos');
   const arms=new THREE.Group();G.add(arms);for(const z of [.82,-.82]){const a=box(3.35,.20,.17,M.yellow,1.5,.72,z,arms);a.rotation.z=.31}const bucket=new THREE.Group();arms.add(bucket);const b=box(1.3,.55,2.15,M.yellow,3.15,1.48,0,bucket);b.rotation.z=-.28;box(.17,.78,2.15,M.yellow,3.62,1.34,0,bucket);moving.push({type:'arms',obj:arms},{type:'bucket',obj:bucket});const l1=cylMesh(.3,.08,.72,1.25,.42),l2=cylMesh(.3,.08,-.72,1.25,.42),tilt=cylMesh(1.25,.82,0,.92,.12);moving.push({type:'lift',obj:l1},{type:'lift',obj:l2},{type:'tilt',obj:tilt});
   pipe([[-.25,.10,.72],[.15,.18,.72],[.75,.26,.72],[1.25,.38,.72]],'pressure',(D.pressure||[]).length>0,.045);pipe([[1.25,.12,-.72],[.75,.02,-.72],[.15,-.08,-.72],[-.25,-.05,-.72]],'return',(D.return||[]).length>0,.045);pipe([[.55,.55,0],[.1,.65,0],[-.35,.6,0]],'pilot',(D.pilot||[]).length>0,.025);
   label('Banco de implementos',.55,1.55,0,'#d8c44a',.88);if(D.subsystem==='Levante de brazos LS')label('Cilindros lift',1.15,1.95,0);if(D.subsystem==='Inclinación de balde')label('Cilindro tilt',1.8,2.05,0);
 } else {
   // unidad hidráulica fija y banco de ensayo / prensa
   tank3d(-2.7,-.55,0);motor3d(-1.35,-.15,0);pump3d(-.45,-.15,0,'Bomba');manifold(.65,.15,0,'Direccional');
   const frame=new THREE.Group();G.add(frame);box(.28,3.0,.35,M.dark,2.25,.15,.8,frame);box(.28,3.0,.35,M.dark,2.25,.15,-.8,frame);box(2.1,.25,1.9,M.dark,2.25,1.58,0,frame);box(2.1,.25,1.9,M.dark,2.25,-1.18,0,frame);const c1=cylMesh(2.25,.3,0,1.35,-Math.PI/2);moving.push({type:'statCyl',obj:c1});
   if(D.subsystem==='Secuencia de dos cilindros'){const c2=cylMesh(3.75,.3,0,1.1,-Math.PI/2);moving.push({type:'statCyl2',obj:c2});label('Cilindro B',3.75,1.85,0)}
   pipe([[-2.65,-.15,.65],[-1.9,-.10,.62],[-.5,-.05,.58],[.65,.12,.52],[1.6,.28,.45]],'pressure',(D.pressure||[]).length>0,.042);pipe([[1.6,.12,-.45],[.65,-.05,-.52],[-.5,-.12,-.58],[-1.7,-.25,-.62],[-2.65,-.28,-.65]],'return',(D.return||[]).length>0,.042);label('Unidad hidráulica',-.9,1.15,0,'#d8c44a',.9);label(D.subsystem,2.25,2.05,0);
 }
 // camera + animation
 function bounds(){return new THREE.Box3().setFromObject(G)}
 function fit(direction){const b=bounds(),sz=b.getSize(new THREE.Vector3()),ct=b.getCenter(new THREE.Vector3()),md=Math.max(sz.x,sz.y,sz.z,1),f=camera.fov*Math.PI/180,dist=Math.min(28,Math.max(7.2,md/(2*Math.tan(f/2))*1.42)),dir=direction||new THREE.Vector3().subVectors(camera.position,controls.target).normalize();controls.target.copy(ct);camera.position.copy(ct.clone().add(dir.normalize().multiplyScalar(dist)));controls.update()}
 const dirs={front:new THREE.Vector3(0,.12,1),iso:new THREE.Vector3(.75,.48,1),side:new THREE.Vector3(1,.12,.02),top:new THREE.Vector3(.01,1,.01)};fit(dirs.front);
 document.getElementById('front').onclick=()=>fit(dirs.front);document.getElementById('iso').onclick=()=>fit(dirs.iso);document.getElementById('side').onclick=()=>fit(dirs.side);document.getElementById('top').onclick=()=>fit(dirs.top);document.getElementById('fit').onclick=()=>fit();document.getElementById('play').onclick=e=>{paused=!paused;e.target.textContent=paused?'Reproducir':'Pausa'};
 status.textContent=D.machine+' · '+D.subsystem+' · '+D.state;legend.innerHTML='<b>'+D.motion+'</b><br><span style="color:#e85b4b">● presión</span> &nbsp; <span style="color:#72a4e5">● retorno</span> &nbsp; <span style="color:#66b66e">● succión</span> &nbsp; <span style="color:#d9c34c">● LS/pilotaje</span> · partículas = sentido de flujo';
 let t=0,last=performance.now();function update(dt){if(!paused)t+=dt*(D.speed||1);const amp=D.visual_amp||1;const mv=(D.machine_value||0);const osc=.82+.18*Math.sin(t*1.5);const q=mv*amp*osc;
   for(const it of moving){if(it.type==='bed'&&D.subsystem==='Levante de tolva'){const k=Math.max(0,q);it.obj.rotation.z=k*.68}else if(it.type==='hoist'&&D.subsystem==='Levante de tolva'){it.obj.scale.x=1+Math.max(0,q)*.55;it.obj.rotation.z=.65+Math.max(0,q)*.16}else if(it.type==='steer'&&D.subsystem==='Dirección hidrostática'){it.obj.position.x=-2.1+(it.sign||1)*q*.16}else if(it.type==='arms'&&D.subsystem==='Levante de brazos LS'){it.obj.rotation.z=Math.max(-.08,q*.36)}else if(it.type==='bucket'&&D.subsystem==='Inclinación de balde'){it.obj.rotation.z=-q*.42}else if(it.type==='lift'&&D.subsystem==='Levante de brazos LS'){it.obj.scale.x=1+q*.28}else if(it.type==='tilt'&&D.subsystem==='Inclinación de balde'){it.obj.scale.x=1+q*.32}else if(it.type==='front'&&D.subsystem==='Dirección articulada'){it.obj.rotation.y=q*.22}else if(it.type==='rear'&&D.subsystem==='Dirección articulada'){it.obj.rotation.y=-q*.11}else if(it.type==='statCyl'){it.obj.scale.x=1+Math.max(-.35,q*.28)}else if(it.type==='statCyl2'){it.obj.scale.x=1+Math.max(-.25,q*.18)}}
   for(const p of particles){const u=(t*.28+p.phase)%1;p.mesh.position.copy(p.curve.getPointAt(u))}
 }
 window.addEventListener('resize',()=>{camera.aspect=root.clientWidth/__HEIGHT__;camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,__HEIGHT__)});let first=false;function loop(now){const dt=Math.min(.05,(now-last)/1000);last=now;update(dt);controls.update();renderer.render(scene,camera);if(!first){first=true;cv.style.display='none'}requestAnimationFrame(loop)}requestAnimationFrame(loop);
}catch(e){console.error(e);status.textContent='Vista de respaldo · Three.js/WebGL no disponible';}
</script>
'''
    html=html.replace('__DATA__',payload).replace('__HEIGHT__',str(int(height)))
    components.html(html,height=height,scrolling=False)
