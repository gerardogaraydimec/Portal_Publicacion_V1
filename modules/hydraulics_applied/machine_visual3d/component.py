from __future__ import annotations
import json
import streamlit.components.v1 as components


def render_machine_hydraulics_3d(data: dict, height: int = 620):
    d = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = f'''
<div id="hyd3d" style="height:{height}px;border:1px solid #ded7cc;border-radius:14px;overflow:hidden;background:#202126;position:relative">
  <div style="position:absolute;z-index:5;left:13px;top:11px;background:#fff8edee;padding:8px 11px;border-radius:10px;font:13px system-ui;color:#25262a;line-height:1.35">
    <b id="titlebox">Hidráulica aplicada 3D</b><br><span id="msg"></span>
  </div>
  <div style="position:absolute;z-index:5;right:11px;top:11px;display:flex;gap:5px;flex-wrap:wrap;max-width:62%">
    <button id="play">Pausa</button><button id="front">Frente</button><button id="iso">Isométrica</button><button id="top">Superior</button><button id="fit">Ajustar</button><button id="reset">Restablecer</button>
  </div>
  <div id="legend" style="position:absolute;z-index:5;left:13px;bottom:11px;background:#202126dd;border:1px solid #515258;color:#f5ead7;padding:8px 10px;border-radius:9px;font:12px system-ui;max-width:72%"></div>
  <canvas id="fallback" width="1100" height="{height}" style="width:100%;height:100%"></canvas>
</div>
<style>
#hyd3d button{{border:1px solid #c8752d;background:#fff8ed;color:#292a2e;border-radius:8px;padding:7px 9px;cursor:pointer}}
#hyd3d button:hover{{background:#fff1dd}}
</style>
<script type="module">
const D={d};
const root=document.getElementById('hyd3d'),cv=document.getElementById('fallback'),msg=document.getElementById('msg'),legend=document.getElementById('legend');
let paused=false;
function fallback(){{
  const c=cv.getContext('2d'),W=cv.width,H=cv.height;c.fillStyle='#202126';c.fillRect(0,0,W,H);
  c.fillStyle='#f28e1c';c.font='700 28px system-ui';c.fillText(D.machine,55,85);c.fillStyle='#f5ead7';c.font='20px system-ui';c.fillText(D.subsystem+' · '+D.state,55,120);
  if(D.machine==='Camión minero'){{
    c.fillStyle='#d89b23';c.fillRect(210,290,430,110);c.fillStyle='#d89b23';c.beginPath();c.moveTo(320,280);c.lineTo(610,200);c.lineTo(650,300);c.lineTo(340,315);c.closePath();c.fill();
    c.fillStyle='#111';for(const x of [280,550]){{c.beginPath();c.arc(x,420,65,0,Math.PI*2);c.fill();c.fillStyle='#b27b18';c.beginPath();c.arc(x,420,32,0,Math.PI*2);c.fill();c.fillStyle='#111';}}
    c.strokeStyle='#f28e1c';c.lineWidth=12;c.beginPath();c.moveTo(420,335);c.lineTo(505,230);c.stroke();
  }}else{{
    c.fillStyle='#d89b23';c.fillRect(260,310,310,100);c.fillRect(540,250,150,70);c.strokeStyle='#d89b23';c.lineWidth=25;c.beginPath();c.moveTo(550,300);c.lineTo(735,195);c.stroke();c.fillStyle='#d89b23';c.fillRect(700,170,120,70);c.fillStyle='#111';for(const x of [320,560]){{c.beginPath();c.arc(x,430,62,0,Math.PI*2);c.fill();}}
  }}
  c.fillStyle='#f5ead7';c.font='16px system-ui';c.fillText('Vista de respaldo',55,H-55);
}}
fallback();
try{{
  const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm');
  const {{OrbitControls}}=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm');
  const scene=new THREE.Scene();scene.background=new THREE.Color('#202126');
  const camera=new THREE.PerspectiveCamera(34,root.clientWidth/{height},.01,120);
  const renderer=new THREE.WebGLRenderer({{antialias:true}});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.setSize(root.clientWidth,{height});root.appendChild(renderer.domElement);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.zoomToCursor=true;controls.minDistance=3;controls.maxDistance=45;
  scene.add(new THREE.HemisphereLight('#fff8ec','#303136',2.2));const dl=new THREE.DirectionalLight('#fff',2);dl.position.set(7,9,8);scene.add(dl);
  const grid=new THREE.GridHelper(18,18,0x4b4c50,0x303136);grid.position.y=-1.55;scene.add(grid);
  const G=new THREE.Group();scene.add(G);
  const matYellow=new THREE.MeshStandardMaterial({{color:'#d39a24',roughness:.65}}),matDark=new THREE.MeshStandardMaterial({{color:'#292b31',roughness:.75}}),matMetal=new THREE.MeshStandardMaterial({{color:'#969aa2',metalness:.35,roughness:.45}}),matOrange=new THREE.MeshStandardMaterial({{color:'#f28e1c',roughness:.45}}),matBlue=new THREE.MeshStandardMaterial({{color:'#3977c3',roughness:.45}}),matPilot=new THREE.MeshStandardMaterial({{color:'#d9b835',roughness:.45}});
  function box(w,h,d,mat,x,y,z){{const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);m.position.set(x,y,z);G.add(m);return m;}}
  function wheel(x,z,r=.78){{const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,.48,36),matDark);m.rotation.z=Math.PI/2;m.position.set(x,-.82,z);G.add(m);const hub=new THREE.Mesh(new THREE.CylinderGeometry(r*.42,r*.42,.52,28),matYellow);hub.rotation.z=Math.PI/2;hub.position.copy(m.position);G.add(hub);return m;}}
  function cyl(x,y,z,len=.9,rotZ=0){{const g=new THREE.Group();const body=new THREE.Mesh(new THREE.CylinderGeometry(.12,.12,len,20),matMetal);body.rotation.z=Math.PI/2;g.add(body);const rod=new THREE.Mesh(new THREE.CylinderGeometry(.055,.055,len*.72,16),new THREE.MeshStandardMaterial({{color:'#d6d8dd',metalness:.55,roughness:.25}}));rod.rotation.z=Math.PI/2;rod.position.x=len*.6;g.add(rod);g.position.set(x,y,z);g.rotation.z=rotZ;G.add(g);return g;}}
  function tube(points,mat,r=.035){{const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)));const geo=new THREE.TubeGeometry(curve,40,r,8,false);const m=new THREE.Mesh(geo,mat);G.add(m);return m;}}
  let moving=[];
  if(D.machine==='Camión minero'){{
    box(5.2,.75,2.35,matYellow,0,-.45,0); box(1.25,1.15,2.2,matYellow,-1.8,.52,0); wheel(-1.8,1.05);wheel(-1.8,-1.05);wheel(1.55,1.05);wheel(1.55,-1.05);
    const bed=new THREE.Group();const bedBase=new THREE.Mesh(new THREE.BoxGeometry(4.1,.22,2.25),matYellow);bedBase.position.x=.3;bed.add(bedBase);const side=new THREE.Mesh(new THREE.BoxGeometry(3.7,.85,.10),matYellow);side.position.set(.45,.45,1.12);bed.add(side);const side2=side.clone();side2.position.z=-1.12;bed.add(side2);bed.position.set(.55,.55,0);G.add(bed);moving.push({{type:'bed',obj:bed}});
    const hoist1=cyl(.15,.0,.58,1.0,.65),hoist2=cyl(.15,.0,-.58,1.0,.65);moving.push({{type:'hoist',obj:hoist1}},{{type:'hoist',obj:hoist2}});
    tube([[-1.7,.15,.75],[-.9,.1,.75],[-.2,.15,.72],[.35,.1,.65]],matOrange,.045);tube([[.35,.0,-.65],[-.2,-.05,-.72],[-.9,-.1,-.75],[-1.7,-.1,-.75]],matBlue,.045);
    if(D.subsystem==='Dirección'){{const s1=cyl(-2.0,-.15,.65,.72,0),s2=cyl(-2.0,-.15,-.65,.72,0);moving.push({{type:'steer',obj:s1,sign:1}},{{type:'steer',obj:s2,sign:-1}});}}
  }} else {{
    const rear=new THREE.Group();const front=new THREE.Group();G.add(rear);G.add(front);rear.add(new THREE.Mesh(new THREE.BoxGeometry(2.8,.75,2.25),matYellow));rear.position.set(-1.4,-.4,0);front.add(new THREE.Mesh(new THREE.BoxGeometry(2.5,.72,2.15),matYellow));front.position.set(1.35,-.42,0);
    wheel(-2.0,1.02);wheel(-2.0,-1.02);wheel(1.75,1.0);wheel(1.75,-1.0);box(1.1,1.2,2.0,matYellow,-1.35,.52,0);
    const arms=new THREE.Group();const a1=new THREE.Mesh(new THREE.BoxGeometry(3.3,.18,.18),matYellow);a1.position.set(1.0,.75,.82);a1.rotation.z=.35;arms.add(a1);const a2=a1.clone();a2.position.z=-.82;arms.add(a2);const bucket=new THREE.Mesh(new THREE.BoxGeometry(1.45,.65,2.2),matYellow);bucket.position.set(2.8,1.35,0);bucket.rotation.z=-.25;arms.add(bucket);arms.position.set(.45,0,0);G.add(arms);moving.push({{type:'arms',obj:arms}});
    const lift1=cyl(.25,.1,.7,1.0,.38),lift2=cyl(.25,.1,-.7,1.0,.38);moving.push({{type:'lift',obj:lift1}},{{type:'lift',obj:lift2}});const tilt=cyl(1.0,.78,0,.78,.18);moving.push({{type:'tilt',obj:tilt}});
    tube([[-1.4,.2,.72],[-.7,.1,.72],[.0,.12,.7],[.65,.2,.7]],matOrange,.045);tube([[.65,.0,-.7],[0,-.05,-.7],[-.7,-.1,-.72],[-1.4,-.1,-.72]],matBlue,.045);
    moving.push({{type:'front',obj:front}});moving.push({{type:'rear',obj:rear}});
  }}
  function label(text,x,y,z,color='#f5ead7'){{const cn=document.createElement('canvas');cn.width=360;cn.height=80;const cx=cn.getContext('2d');cx.font='600 30px system-ui';cx.textAlign='center';cx.fillStyle=color;cx.fillText(text,180,48);const tex=new THREE.CanvasTexture(cn);const sp=new THREE.Sprite(new THREE.SpriteMaterial({{map:tex,transparent:true,depthTest:false}}));sp.scale.set(1.65,.37,1);sp.position.set(x,y,z);G.add(sp);return sp}}
  label(D.subsystem,0,2.45,0,'#f5ead7');
  const amp=D.visual_amp||1;let tm=0,last=performance.now();
  function stateFactor(){{if(D.state==='Elevar'||D.state==='Recoger'||D.state==='Izquierda'||D.state==='Servicio')return 1;if(D.state==='Bajar'||D.state==='Descargar'||D.state==='Derecha')return -1;return 0}}
  function update(dt){{if(!paused)tm+=dt*(D.speed||1);const wave=Math.sin(tm*1.8);const sf=stateFactor();const q=sf===0?0:sf*(.55+.45*wave)*amp;
    for(const it of moving){{if(it.type==='bed'){{it.obj.rotation.z=D.subsystem==='Levante de tolva'?Math.max(0,q)*.62:0;it.obj.position.y=.55+Math.max(0,q)*.3;}}
      else if(it.type==='hoist'){{it.obj.scale.x=1+Math.max(0,q)*.55;it.obj.rotation.z=.65+Math.max(0,q)*.18;}}
      else if(it.type==='steer'){{it.obj.position.x=-2.0+(it.sign||1)*q*.12;}}
      else if(it.type==='arms'){{if(D.subsystem==='Levante de brazos')it.obj.rotation.z=Math.max(-.15,q*.42);else if(D.subsystem==='Inclinación de balde')it.obj.rotation.z=q*.10;}}
      else if(it.type==='lift'){{if(D.subsystem==='Levante de brazos')it.obj.scale.x=1+q*.25;}}
      else if(it.type==='tilt'){{if(D.subsystem==='Inclinación de balde')it.obj.scale.x=1+q*.22;}}
      else if(it.type==='front'&&D.subsystem==='Dirección articulada'){{it.obj.rotation.y=q*.20;}}
      else if(it.type==='rear'&&D.subsystem==='Dirección articulada'){{it.obj.rotation.y=-q*.08;}}
    }}
    legend.innerHTML=`<b>${{D.machine}}</b> · ${{D.subsystem}} · ${{D.state}}<br><span style="color:#f28e1c">Presión</span> · <span style="color:#6fa5e5">Retorno</span> · <span style="color:#d9b835">Mando/LS</span> · ${{D.motion}}`;
  }}
  function front(){{camera.position.set(0,2.0,11);controls.target.set(0,.1,0);controls.update()}}function iso(){{camera.position.set(7,4.5,8.5);controls.target.set(0,.1,0);controls.update()}}function top(){{camera.position.set(0,10,.01);controls.target.set(0,0,0);controls.update()}}function fit(){{const b=new THREE.Box3().setFromObject(G),sz=b.getSize(new THREE.Vector3()),ct=b.getCenter(new THREE.Vector3()),md=Math.max(sz.x,sz.y,sz.z,1),f=camera.fov*Math.PI/180,dist=md/(2*Math.tan(f/2))*1.35,dir=new THREE.Vector3().subVectors(camera.position,controls.target).normalize();controls.target.copy(ct);camera.position.copy(ct.clone().add(dir.multiplyScalar(dist)));controls.update()}}function reset(){{iso();fit()}}reset();
  document.getElementById('front').onclick=()=>{{front();fit()}};document.getElementById('iso').onclick=()=>{{iso();fit()}};document.getElementById('top').onclick=()=>{{top();fit()}};document.getElementById('fit').onclick=fit;document.getElementById('reset').onclick=reset;document.getElementById('play').onclick=e=>{{paused=!paused;e.target.textContent=paused?'Reproducir':'Pausa'}};
  msg.textContent=D.machine+' · '+D.subsystem+' · '+D.state;
  window.addEventListener('resize',()=>{{camera.aspect=root.clientWidth/{height};camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,{height})}});
  let first=false;function loop(now){{const dt=Math.min(.05,(now-last)/1000);last=now;update(dt);controls.update();renderer.render(scene,camera);if(!first){{first=true;cv.style.display='none'}}requestAnimationFrame(loop)}}requestAnimationFrame(loop);
}}catch(e){{console.error(e);msg.textContent='Vista de respaldo · Three.js no disponible';}}
</script>
'''
    components.html(html, height=height, scrolling=False)
