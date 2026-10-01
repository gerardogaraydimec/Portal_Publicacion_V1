from __future__ import annotations
import json
import streamlit.components.v1 as components


def render_machine_hydraulics_3d(data: dict, height: int = 640):
    payload=json.dumps(data,ensure_ascii=False,separators=(",", ":"))
    html=r'''
<div id="m3d" style="height:__HEIGHT__px;border:1px solid #d8d9dc;border-radius:15px;overflow:hidden;background:#202126;position:relative">
 <div style="position:absolute;z-index:5;left:12px;top:10px;background:#fff8edee;color:#25262a;padding:8px 11px;border-radius:9px;font:13px system-ui;line-height:1.35"><b id="m3dTitle">Modelo físico 3D</b><br><span id="m3dStatus"></span></div>
 <div style="position:absolute;z-index:5;right:10px;top:10px;display:flex;gap:5px;flex-wrap:wrap"><button id="pause">Pausa</button><button id="front">Frente</button><button id="iso">Isométrica</button><button id="side">Lateral</button><button id="fit">Ajustar</button></div>
 <div id="m3dLegend" style="position:absolute;z-index:5;left:12px;bottom:10px;background:#202126df;color:#f5ead7;border:1px solid #575a61;padding:8px 10px;border-radius:9px;font:12px system-ui;max-width:66%"></div>
 <canvas id="fallback" width="1100" height="__HEIGHT__" style="width:100%;height:100%"></canvas>
</div>
<style>#m3d button{border:1px solid #c8752d;background:#fff8ed;color:#292a2e;border-radius:8px;padding:7px 9px;cursor:pointer}#m3d button:hover{background:#fff1dd}</style>
<script type="module">
const D=__DATA__,root=document.getElementById('m3d'),cv=document.getElementById('fallback'),status=document.getElementById('m3dStatus'),legend=document.getElementById('m3dLegend');let paused=false;
function fallback(){const c=cv.getContext('2d'),W=cv.width,H=cv.height;c.fillStyle='#202126';c.fillRect(0,0,W,H);c.fillStyle='#d69b27';if(D.machine==='Camión minero'){c.fillRect(220,310,430,95);c.fillRect(220,235,115,80);c.beginPath();c.moveTo(370,300);c.lineTo(650,210);c.lineTo(720,300);c.closePath();c.fill();for(const x of [285,520,625]){c.fillStyle='#111';c.beginPath();c.arc(x,430,55,0,Math.PI*2);c.fill();c.fillStyle='#d69b27';c.beginPath();c.arc(x,430,24,0,Math.PI*2);c.fill()}}else if(D.machine==='Cargador frontal'){c.fillRect(250,320,340,90);c.fillRect(310,245,100,78);c.strokeStyle='#d69b27';c.lineWidth=24;c.beginPath();c.moveTo(555,330);c.lineTo(740,215);c.stroke();c.fillRect(720,190,120,65);for(const x of [310,560]){c.fillStyle='#111';c.beginPath();c.arc(x,440,54,0,Math.PI*2);c.fill()}}else{c.fillStyle='#2f333a';c.fillRect(180,340,150,120);c.fillStyle='#d69b27';c.fillRect(420,330,110,90);c.fillStyle='#d9dce0';c.fillRect(660,300,200,100)}c.fillStyle='#f5ead7';c.font='20px system-ui';c.fillText(D.machine+' · '+D.subsystem,45,82);c.font='16px system-ui';c.fillText('Vista de respaldo',45,H-35)}fallback();
try{
 const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm');const {OrbitControls}=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm');
 const scene=new THREE.Scene();scene.background=new THREE.Color('#202126');const camera=new THREE.PerspectiveCamera(31,root.clientWidth/__HEIGHT__,.01,120);const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.setSize(root.clientWidth,__HEIGHT__);root.appendChild(renderer.domElement);
 const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.zoomToCursor=true;controls.minDistance=3;controls.maxDistance=45;scene.add(new THREE.HemisphereLight('#fff7e8','#2e3036',2.2));const dl=new THREE.DirectionalLight('#fff',2.2);dl.position.set(8,10,9);scene.add(dl);const fill=new THREE.DirectionalLight('#ffedd0',.8);fill.position.set(-6,4,-5);scene.add(fill);const grid=new THREE.GridHelper(20,20,0x4d4f55,0x303238);grid.position.y=-1.62;scene.add(grid);
 const G=new THREE.Group();scene.add(G);const mYellow=new THREE.MeshStandardMaterial({color:'#d49a24',roughness:.64}),mDark=new THREE.MeshStandardMaterial({color:'#22252b',roughness:.78}),mCab=new THREE.MeshStandardMaterial({color:'#2b3036',roughness:.45,metalness:.08}),mGlass=new THREE.MeshStandardMaterial({color:'#263f50',roughness:.18,metalness:.1,transparent:true,opacity:.82}),mMetal=new THREE.MeshStandardMaterial({color:'#a5a9ae',roughness:.38,metalness:.5}),mRod=new THREE.MeshStandardMaterial({color:'#e3e6e9',roughness:.24,metalness:.75}),mPress=new THREE.MeshStandardMaterial({color:'#d84030',roughness:.42}),mReturn=new THREE.MeshStandardMaterial({color:'#2a63b8',roughness:.42}),mPilot=new THREE.MeshStandardMaterial({color:'#d6b72c',roughness:.42}),mGreen=new THREE.MeshStandardMaterial({color:'#4e9b57',roughness:.42}),mOrange=new THREE.MeshStandardMaterial({color:'#f28e1c',roughness:.45});
 const physical=new THREE.Group();G.add(physical),pipes=new THREE.Group();G.add(pipes),labels=new THREE.Group();G.add(labels),moving=[];
 function box(w,h,d,mat,x,y,z,parent=physical){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);m.position.set(x,y,z);parent.add(m);return m}
 function wheel(x,z,r=.7,parent=physical){const tire=new THREE.Mesh(new THREE.CylinderGeometry(r,r,.45,36),mDark);tire.rotation.z=Math.PI/2;tire.position.set(x,-.85,z);parent.add(tire);const hub=new THREE.Mesh(new THREE.CylinderGeometry(r*.43,r*.43,.48,30),mYellow);hub.rotation.z=Math.PI/2;hub.position.copy(tire.position);parent.add(hub)}
 function cyl(x,y,z,len=1,rz=0,parent=physical){const g=new THREE.Group();const body=new THREE.Mesh(new THREE.CylinderGeometry(.13,.13,len,22),mMetal);body.rotation.z=Math.PI/2;body.position.x=0;g.add(body);const rod=new THREE.Mesh(new THREE.CylinderGeometry(.055,.055,len*.85,18),mRod);rod.rotation.z=Math.PI/2;rod.position.x=len*.72;g.add(rod);g.position.set(x,y,z);g.rotation.z=rz;parent.add(g);return g}
 function tube(points,mat,r=.035,parent=pipes){const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)));const mesh=new THREE.Mesh(new THREE.TubeGeometry(curve,48,r,8,false),mat);parent.add(mesh);return mesh}
 function label(text,x,y,z,color='#f5ead7'){const cn=document.createElement('canvas');cn.width=420;cn.height=88;const cx=cn.getContext('2d');cx.font='600 30px system-ui';cx.textAlign='center';cx.fillStyle=color;cx.fillText(text,210,52);const tex=new THREE.CanvasTexture(cn);const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,transparent:true,depthTest:false}));sp.scale.set(1.8,.38,1);sp.position.set(x,y,z);labels.add(sp);return sp}
 function actMat(name,normal=mMetal){return (D.active_components||[]).includes(name)?mOrange:normal}
 if(D.machine==='Camión minero'){
   // chassis, deck, cab, radiator deck
   box(5.7,.45,2.35,mYellow,0,-.45,0);box(1.45,.16,2.45,mDark,-2.0,.0,0);box(1.25,1.28,2.05,mCab,-1.95,.55,0);box(1.0,.62,1.82,mGlass,-1.93,.72,0);box(.75,.48,2.1,mYellow,-2.55,.12,0);box(.55,.8,2.0,mYellow,-1.12,.18,0);
   for(const [x,z,r] of [[-2,1.05,.72],[-2,-1.05,.72],[1.0,1.03,.78],[1.0,-1.03,.78],[2.15,1.03,.78],[2.15,-1.03,.78]])wheel(x,z,r);
   // ladder and handrails
   for(let i=0;i<4;i++)box(.05,.38,.05,mMetal,-2.85,-.08+i*.34,1.13);box(.05,1.2,.05,mMetal,-2.85,.45,1.13);box(.05,1.2,.05,mMetal,-2.48,.45,1.13);
   // dump body group with walls
   const bed=new THREE.Group();physical.add(bed);const floor=box(4.4,.18,2.4,mYellow,.25,0,0,bed);box(4.0,.95,.12,mYellow,.38,.5,1.18,bed);box(4.0,.95,.12,mYellow,.38,.5,-1.18,bed);box(.18,1.25,2.4,mYellow,2.38,.45,0,bed);bed.position.set(.45,.75,0);moving.push({type:'truck-bed',obj:bed});
   const h1=cyl(.0,.05,.66,1.25,.68),h2=cyl(.0,.05,-.66,1.25,.68);moving.push({type:'hoist',obj:h1},{type:'hoist',obj:h2});
   // hydraulic manifolds
   box(.7,.45,1.15,actMat('Válvula de levante',mDark),-.55,-.05,0);box(.42,.38,.75,actMat('Control overcenter/descenso',mDark),.18,.12,0);label(D.subsystem,0,2.65,0);
   // active lines
   tube([[-1.3,.15,.82],[-.8,.1,.82],[-.35,.12,.75],[.2,.15,.68]],mPress,.045);tube([[.2,.04,-.68],[-.35,-.03,-.75],[-.8,-.08,-.82],[-1.3,-.08,-.82]],mReturn,.045);tube([[-.75,.35,0],[-.25,.45,0],[.2,.45,0]],mPilot,.025);
   if(D.subsystem==='Dirección'){const s1=cyl(-2.0,-.05,.73,.75,0),s2=cyl(-2.0,-.05,-.73,.75,0);moving.push({type:'steer',obj:s1,sign:1},{type:'steer',obj:s2,sign:-1});box(.55,.32,.75,actMat('HMU',mDark),-1.55,.15,0);label('Dirección: HMU + LS + alivios cruzados',0,2.2,0,'#d8c44a')}
   if(D.subsystem==='Freno / enfriamiento'){for(const x of [-1.0,0,1.0]){const a=new THREE.Mesh(new THREE.SphereGeometry(.18,20,14),actMat('Acumuladores',mDark));a.position.set(x,.25,1.22);physical.add(a)}label('Acumuladores / freno / enfriamiento',0,2.2,0,'#f5ead7')}
 } else if(D.machine==='Cargador frontal'){
   const rear=new THREE.Group(),front=new THREE.Group();physical.add(rear);physical.add(front);box(2.8,.58,2.2,mYellow,-1.35,-.35,0,rear);box(1.1,1.35,1.9,mCab,-1.55,.58,0,rear);box(.85,.72,1.65,mGlass,-1.55,.75,0,rear);box(1.0,.7,2.0,mYellow,-.25,.15,0,rear);box(2.5,.58,2.1,mYellow,1.45,-.38,0,front);wheel(-2.0,1.03,.72);wheel(-2.0,-1.03,.72);wheel(1.75,1.0,.78);wheel(1.75,-1.0,.78);box(.2,.75,.65,mDark,.1,-.15,0);moving.push({type:'front',obj:front},{type:'rear',obj:rear});
   const arms=new THREE.Group();physical.add(arms);for(const z of [.78,-.78]){const a=box(3.2,.2,.18,mYellow,1.2,.76,z,arms);a.rotation.z=.34}const bucket=new THREE.Group();arms.add(bucket);const b1=box(1.35,.55,2.1,mYellow,2.9,1.5,0,bucket);b1.rotation.z=-.25;box(.18,.8,2.1,mYellow,3.45,1.35,0,bucket);moving.push({type:'arms',obj:arms},{type:'bucket',obj:bucket});const l1=cyl(.1,.15,.68,1.15,.42),l2=cyl(.1,.15,-.68,1.15,.42),tilt=cyl(1.15,.85,0,.82,.16);moving.push({type:'lift',obj:l1},{type:'lift',obj:l2},{type:'tilt',obj:tilt});tube([[-1.0,.15,.72],[-.4,.12,.72],[.15,.18,.7],[.75,.26,.7]],mPress,.045);tube([[.75,.04,-.7],[.15,-.02,-.7],[-.4,-.05,-.72],[-1,-.05,-.72]],mReturn,.045);box(.7,.45,1.1,actMat('Banco de implementos',mDark),-.25,.25,0);label(D.subsystem,.4,2.65,0);label('Bomba → banco → actuador → retorno',.5,2.2,0,'#d8c44a');
 } else {
   // stationary power unit + press/cylinder
   box(2.0,.95,1.75,mDark,-2.2,-.5,0);box(.85,.85,.85,mYellow,-2.2,.25,0);const motor=new THREE.Mesh(new THREE.CylinderGeometry(.38,.38,1.0,28),mDark);motor.rotation.z=Math.PI/2;motor.position.set(-.8,-.1,0);physical.add(motor);const pump=new THREE.Mesh(new THREE.CylinderGeometry(.3,.3,.55,24),actMat('Bomba',mMetal));pump.rotation.z=Math.PI/2;pump.position.set(-.05,-.1,0);physical.add(pump);box(1.1,.6,1.2,actMat('Direccional 4/3',mDark),.85,.15,0);const stc=cyl(2.25,.18,0,1.35,0);moving.push({type:'stationary-cylinder',obj:stc});tube([[-2.15,-.05,.7],[-1.1,-.08,.7],[-.2,-.05,.6],[.55,.1,.5],[1.65,.2,.4]],mPress,.04);tube([[1.65,0,-.4],[.55,-.05,-.5],[-.2,-.1,-.6],[-1.2,-.2,-.7],[-2.15,-.2,-.7]],mReturn,.04);label(D.subsystem,0,2.35,0);label('Unidad hidráulica estacionaria',0,1.95,0,'#d8c44a')
 }
 const amp=D.visual_amp||1;let tm=0,last=performance.now();function pulse(now){return .72+.28*Math.sin(now*1.7)}
 function update(dt){
   if(!paused) tm += dt*(D.speed||1);
   const q=(D.machine_value||0)*pulse(tm)*amp;
   if(D.machine==='Camión minero'){
     for(const it of moving){
       if(it.type==='truck-bed'&&D.subsystem==='Levante de tolva'){
         const k=Math.max(0,q); it.obj.rotation.z=k*.72; it.obj.position.y=.75+k*.32;
       }else if(it.type==='hoist'&&D.subsystem==='Levante de tolva'){
         it.obj.scale.x=1+Math.max(0,q)*.65; it.obj.rotation.z=.68+Math.max(0,q)*.18;
       }else if(it.type==='steer'&&D.subsystem==='Dirección'){
         it.obj.position.x=-2.0+(it.sign||1)*q*.16;
       }
     }
   }else if(D.machine==='Cargador frontal'){
     for(const it of moving){
       if(it.type==='arms'&&D.subsystem==='Levante de brazos') it.obj.rotation.z=Math.max(-.12,q*.38);
       else if(it.type==='bucket'&&D.subsystem==='Inclinación de balde') it.obj.rotation.z=-q*.38;
       else if(it.type==='lift'&&D.subsystem==='Levante de brazos') it.obj.scale.x=1+q*.28;
       else if(it.type==='tilt'&&D.subsystem==='Inclinación de balde') it.obj.scale.x=1+q*.3;
       else if(it.type==='front'&&D.subsystem==='Dirección articulada') it.obj.rotation.y=q*.24;
       else if(it.type==='rear'&&D.subsystem==='Dirección articulada') it.obj.rotation.y=-q*.12;
     }
   }else{
     for(const it of moving){ if(it.type==='stationary-cylinder') it.obj.position.x=2.25+q*.45; }
   }
   legend.innerHTML='<b>'+D.machine+'</b> · '+D.subsystem+' · '+D.state+'<br><span style="color:#e85a49">Presión</span> · <span style="color:#6f9ee0">Retorno</span> · <span style="color:#d8c44a">Mando / LS</span> · '+D.motion;
 }
 function front(){camera.position.set(0,2.1,11);controls.target.set(0,.1,0);controls.update()}function iso(){camera.position.set(7,4.6,8.7);controls.target.set(0,.1,0);controls.update()}function side(){camera.position.set(10,1.8,0.1);controls.target.set(0,.1,0);controls.update()}function fit(){const b=new THREE.Box3().setFromObject(physical),sz=b.getSize(new THREE.Vector3()),ct=b.getCenter(new THREE.Vector3()),md=Math.max(sz.x,sz.y,sz.z,1),f=camera.fov*Math.PI/180,dist=Math.min(24,Math.max(6,md/(2*Math.tan(f/2))*1.22)),dir=new THREE.Vector3().subVectors(camera.position,controls.target).normalize();controls.target.copy(ct);camera.position.copy(ct.clone().add(dir.multiplyScalar(dist)));controls.update()}iso();fit();document.getElementById('front').onclick=()=>{front();fit()};document.getElementById('iso').onclick=()=>{iso();fit()};document.getElementById('side').onclick=()=>{side();fit()};document.getElementById('fit').onclick=fit;document.getElementById('pause').onclick=e=>{paused=!paused;e.target.textContent=paused?'Reproducir':'Pausa'};status.textContent=D.machine+' · '+D.subsystem+' · '+D.state;window.addEventListener('resize',()=>{camera.aspect=root.clientWidth/__HEIGHT__;camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,__HEIGHT__)});let first=false;function loop(now){const dt=Math.min(.05,(now-last)/1000);last=now;update(dt);controls.update();renderer.render(scene,camera);if(!first){first=true;cv.style.display='none'}requestAnimationFrame(loop)}requestAnimationFrame(loop)
}catch(e){console.error(e);status.textContent='Vista de respaldo · Three.js no disponible'}
</script>
'''
    html=html.replace('__DATA__',payload).replace('__HEIGHT__',str(int(height)))
    components.html(html,height=height,scrolling=False)
