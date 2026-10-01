from __future__ import annotations
import json
import streamlit.components.v1 as components


def render_vibration_3d(data: dict, height: int = 625):
    d=json.dumps(data,ensure_ascii=False,separators=(',',':'))
    html=f'''
<div id="vib3d" style="height:{height}px;border:1px solid #ded7cc;border-radius:14px;overflow:hidden;background:#202126;position:relative">
  <div style="position:absolute;z-index:5;left:14px;top:12px;background:#fff8edee;padding:8px 11px;border-radius:10px;font:13px system-ui;color:#25262a;line-height:1.35;max-width:42%">
    <b>Vibración libre 1GDL</b><br><span id="vibmsg"></span>
  </div>
  <div style="position:absolute;z-index:5;right:12px;top:12px;display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end;max-width:55%">
    <button id="play">Pausa</button><button id="front">Frente</button><button id="iso">Isométrica</button><button id="side">Lateral</button><button id="fit">Ajustar</button><button id="reset">Restablecer</button>
  </div>
  <div style="position:absolute;z-index:5;left:14px;bottom:12px;background:#202126e8;color:#eee;border:1px solid #4b4c50;border-radius:10px;padding:7px 10px;font:12px system-ui;line-height:1.45">
    <span id="readout">x = 0 mm</span>
  </div>
  <div style="position:absolute;z-index:5;right:14px;bottom:12px;background:#fff8edeb;color:#25262a;border-radius:10px;padding:7px 10px;font:12px system-ui;line-height:1.5">
    <span style="color:#f5ead7">━━</span> movimiento v(t)&nbsp;&nbsp; <span style="color:#f28e1c">━━</span> Fₖ = −kx&nbsp;&nbsp; <span style="color:#9fa1a6">━━</span> F꜀ = −cẋ
  </div>
  <canvas id="fb" width="1000" height="{height}" style="width:100%;height:100%"></canvas>
</div>
<style>
#vib3d button{{border:1px solid #c8752d;background:#fff8ed;color:#292a2e;border-radius:8px;padding:7px 9px;cursor:pointer}}
#vib3d button:hover{{background:#fff1dd}}
</style>
<script type="module">
const D={d};
const root=document.getElementById('vib3d'),cv=document.getElementById('fb'),msg=document.getElementById('vibmsg'),readout=document.getElementById('readout');
let paused=false;
function fallback(){{
  const c=cv.getContext('2d'),W=cv.width,H=cv.height;c.fillStyle='#202126';c.fillRect(0,0,W,H);
  const y=H/2,xm=W*.60,wall=95;
  c.fillStyle='#c8752d';c.fillRect(wall,y-115,30,230);
  c.strokeStyle='#d9c8ae';c.lineWidth=4;c.beginPath();c.moveTo(wall+30,y-25);for(let i=0;i<13;i++){{const xx=wall+55+i*27,yy=y-25+(i%2?28:-28);c.lineTo(xx,yy)}}c.lineTo(xm-80,y-25);c.stroke();
  c.fillStyle='#e8dfcf';c.fillRect(xm-80,y-70,160,140);
  c.strokeStyle='#f5ead7';c.lineWidth=4;c.beginPath();c.moveTo(xm,y-100);c.lineTo(xm+105,y-100);c.stroke();c.fillStyle='#f5ead7';c.beginPath();c.moveTo(xm+118,y-100);c.lineTo(xm+98,y-110);c.lineTo(xm+98,y-90);c.fill();
  c.fillStyle='#f5ead7';c.font='16px system-ui';c.fillText('v(t)',xm+42,y-116);
  msg.textContent='Vista de respaldo · movimiento + fuerzas';
}}
fallback();
try{{
  const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm');
  const {{OrbitControls}}=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm');
  cv.style.display='none';
  const scene=new THREE.Scene();scene.background=new THREE.Color('#202126');
  const camera=new THREE.PerspectiveCamera(34,root.clientWidth/{height},.01,120);
  const renderer=new THREE.WebGLRenderer({{antialias:true}});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.setSize(root.clientWidth,{height});root.appendChild(renderer.domElement);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.zoomToCursor=true;controls.minDistance=2;controls.maxDistance=40;
  scene.add(new THREE.HemisphereLight('#fff8ec','#303136',2.25));const dl=new THREE.DirectionalLight('#ffffff',2);dl.position.set(5,7,8);scene.add(dl);

  const rootG=new THREE.Group();scene.add(rootG);
  const matBase=new THREE.MeshStandardMaterial({{color:'#c8752d',roughness:.78}}),matMass=new THREE.MeshStandardMaterial({{color:'#e6dccb',roughness:.68}}),matMetal=new THREE.MeshStandardMaterial({{color:'#767980',metalness:.25,roughness:.5}}),matOrange=new THREE.MeshStandardMaterial({{color:'#f28e1c'}});
  const wall=new THREE.Mesh(new THREE.BoxGeometry(.28,2.8,2.35),matBase);wall.position.set(-3.8,0,0);rootG.add(wall);
  const grid=new THREE.GridHelper(11,11,0x46474c,0x303136);grid.position.set(0,-1.45,0);scene.add(grid);
  const rail=new THREE.Mesh(new THREE.BoxGeometry(7.1,.09,.14),matMetal);rail.position.set(-.12,-.78,0);rootG.add(rail);

  // Sentido positivo fijo del grado de libertad.
  const axisArrow=new THREE.ArrowHelper(new THREE.Vector3(1,0,0),new THREE.Vector3(-.35,-1.13,-.02),1.25,0xc8752d,.20,.11);rootG.add(axisArrow);

  const mass=new THREE.Group();rootG.add(mass);
  const massBody=new THREE.Mesh(new THREE.BoxGeometry(1.5,1.5,1.5),matMass);mass.add(massBody);
  const massEdge=new THREE.LineSegments(new THREE.EdgesGeometry(massBody.geometry),new THREE.LineBasicMaterial({{color:0xaaa08f}}));mass.add(massEdge);

  const eqMat=new THREE.LineDashedMaterial({{color:0xb0b2b6,dashSize:.13,gapSize:.09,transparent:true,opacity:.9}});
  const eqLine=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(1.4,-1.25,-1.05),new THREE.Vector3(1.4,1.25,-1.05)]),eqMat);eqLine.computeLineDistances();rootG.add(eqLine);

  function makeSpring(xa,xb,y,z){{
    const pts=[];const turns=12,N=180,rad=.20;
    for(let i=0;i<=N;i++){{const q=i/N,x=xa+(xb-xa)*q;let yy=y,zz=z;if(i>5&&i<N-5){{yy+=rad*Math.sin(turns*2*Math.PI*q);zz+=rad*Math.cos(turns*2*Math.PI*q)}}pts.push(new THREE.Vector3(x,yy,zz))}}
    return new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({{color:'#d9c8ae'}}));
  }}
  let spring=null;

  const damper=new THREE.Group();rootG.add(damper);
  const cyl=new THREE.Mesh(new THREE.CylinderGeometry(.20,.20,1.15,24),matMetal);cyl.rotation.z=Math.PI/2;damper.add(cyl);
  const rod=new THREE.Mesh(new THREE.CylinderGeometry(.06,.06,2.05,18),new THREE.MeshStandardMaterial({{color:'#d3d4d6',metalness:.55,roughness:.3}}));rod.rotation.z=Math.PI/2;damper.add(rod);

  // Flechas físicas: movimiento, resorte y amortiguador.
  const origin=new THREE.Vector3();
  const motionArrow=new THREE.ArrowHelper(new THREE.Vector3(1,0,0),origin,1.0,0xf5ead7,.22,.12);rootG.add(motionArrow);
  const fkArrow=new THREE.ArrowHelper(new THREE.Vector3(1,0,0),origin,1.0,0xf28e1c,.22,.12);rootG.add(fkArrow);
  const fcArrow=new THREE.ArrowHelper(new THREE.Vector3(1,0,0),origin,1.0,0x9fa1a6,.22,.12);rootG.add(fcArrow);

  function makeLabel(text,color){{
    const cn=document.createElement('canvas');cn.width=256;cn.height=64;const ctx=cn.getContext('2d');ctx.clearRect(0,0,256,64);ctx.font='600 30px system-ui';ctx.textAlign='center';ctx.fillStyle=color;ctx.fillText(text,128,40);const tex=new THREE.CanvasTexture(cn);tex.needsUpdate=true;const sp=new THREE.Sprite(new THREE.SpriteMaterial({{map:tex,transparent:true,depthTest:false}}));sp.scale.set(1.25,.31,1);return sp;
  }}
  const lblV=makeLabel('v(t)','#f5ead7'),lblFk=makeLabel('Fₖ','#f28e1c'),lblFc=makeLabel('F꜀','#b8b9bc');rootG.add(lblV);rootG.add(lblFk);rootG.add(lblFc);

  // Línea de desplazamiento x(t) desde equilibrio a la posición actual.
  const dimMat=new THREE.LineDashedMaterial({{color:0xc8752d,dashSize:.10,gapSize:.07,transparent:true,opacity:.95}});
  const dimGeo=new THREE.BufferGeometry();const dimLine=new THREE.Line(dimGeo,dimMat);rootG.add(dimLine);
  const dimA=new THREE.Mesh(new THREE.SphereGeometry(.035,10,10),matOrange);const dimB=new THREE.Mesh(new THREE.SphereGeometry(.035,10,10),matOrange);rootG.add(dimA);rootG.add(dimB);

  const tArr=D.t||[],xArr=D.x||[],vArr=D.v||[],aArr=D.a||[];
  const xmax=Math.max(...xArr.map(q=>Math.abs(q)),1e-9),vmax=Math.max(...vArr.map(q=>Math.abs(q)),1e-9);
  const fkAll=xArr.map(q=>-D.k*q),fcAll=vArr.map(q=>-D.c*q);const fmax=Math.max(...fkAll.map(Math.abs),...fcAll.map(Math.abs),1e-9);
  const amp=D.visual_amp||1;let time=0,last=performance.now();const duration=Math.max(D.duration||10,1e-6),speed=D.speed||1;
  function sample(arr,tt){{if(!arr.length)return 0;const u=((tt%duration)/duration)*(arr.length-1),i=Math.floor(u),j=Math.min(arr.length-1,i+1),f=u-i;return arr[i]*(1-f)+arr[j]*f}}
  function setArrow(arrow,label,val,norm,y,colorVisible=true){{
    const s=Math.sign(val)||1;arrow.setDirection(new THREE.Vector3(s,0,0));const len=.25+1.15*Math.min(1,Math.abs(val)/Math.max(norm,1e-12));arrow.setLength(len,.22,.12);arrow.position.set(mass.position.x,y,0);label.position.set(mass.position.x+s*(len*.55),y+.25,0);arrow.visible=colorVisible && Math.abs(val)>Math.max(norm*0.015,1e-10);label.visible=arrow.visible;
  }}
  function updateModel(dt){{
    if(!paused)time+=dt*speed;
    const xx=sample(xArr,time),vv=sample(vArr,time),aa=sample(aArr,time);const disp=(xx/xmax)*1.25*amp;
    mass.position.set(1.4+disp,0,0);
    if(spring)rootG.remove(spring);spring=makeSpring(-3.62,mass.position.x-.80,.50,0);rootG.add(spring);
    const xb=mass.position.x-.80,xa=-3.62,len=Math.max(.55,xb-xa),mid=(xa+xb)/2;damper.position.set(mid,-.52,0);cyl.scale.y=Math.max(.42,Math.min(2.0,len/1.15));rod.scale.y=Math.max(.42,Math.min(2.2,len/2.05));
    const fk=-D.k*xx,fc=-D.c*vv;
    setArrow(motionArrow,lblV,vv,vmax,1.18,D.show_motion!==false);
    setArrow(fkArrow,lblFk,fk,fmax,.52,D.show_forces!==false);
    setArrow(fcArrow,lblFc,fc,fmax,-.52,D.show_forces!==false);
    if(D.show_dimension!==false){{const y=-1.08;dimGeo.setFromPoints([new THREE.Vector3(1.4,y,.02),new THREE.Vector3(mass.position.x,y,.02)]);dimLine.computeLineDistances();dimA.position.set(1.4,y,.02);dimB.position.set(mass.position.x,y,.02);dimLine.visible=dimA.visible=dimB.visible=true}}else{{dimLine.visible=dimA.visible=dimB.visible=false}}
    readout.textContent=`t = ${{(time%duration).toFixed(2)}} s · x = ${{(xx*1000).toFixed(2)}} mm · v = ${{vv.toFixed(3)}} m/s · a = ${{aa.toFixed(3)}} m/s²`;
  }}

  function setFront(){{camera.position.set(-.1,.1,9.3);controls.target.set(-.2,0,0);controls.update()}}
  function setIso(){{camera.position.set(5,3.7,7.8);controls.target.set(-.2,0,0);controls.update()}}
  function setSide(){{camera.position.set(-.2,7.3,.01);controls.target.set(-.2,0,0);controls.update()}}
  function fit(){{const b=new THREE.Box3().setFromObject(rootG),sz=b.getSize(new THREE.Vector3()),ct=b.getCenter(new THREE.Vector3()),md=Math.max(sz.x,sz.y,sz.z,1),f=camera.fov*Math.PI/180,dist=md/(2*Math.tan(f/2))*1.32,dir=new THREE.Vector3().subVectors(camera.position,controls.target).normalize();controls.target.copy(ct);camera.position.copy(ct.clone().add(dir.multiplyScalar(dist)));controls.update()}}
  function reset(){{setFront();fit()}}reset();
  document.getElementById('front').onclick=()=>{{setFront();fit()}};document.getElementById('iso').onclick=()=>{{setIso();fit()}};document.getElementById('side').onclick=()=>{{setSide();fit()}};document.getElementById('fit').onclick=fit;document.getElementById('reset').onclick=reset;document.getElementById('play').onclick=(e)=>{{paused=!paused;e.target.textContent=paused?'Reproducir':'Pausa'}};
  msg.textContent=`${{D.regime}} · ζ = ${{Number(D.zeta).toFixed(3)}} · fₙ = ${{Number(D.fn).toFixed(3)}} Hz · +x hacia la derecha`;
  window.addEventListener('resize',()=>{{camera.aspect=root.clientWidth/{height};camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,{height})}});
  function loop(now){{const dt=Math.min(.05,(now-last)/1000);last=now;updateModel(dt);controls.update();renderer.render(scene,camera);requestAnimationFrame(loop)}}requestAnimationFrame(loop);
}}catch(e){{console.error(e);msg.textContent='Vista de respaldo · Three.js no disponible'}}
</script>'''
    components.html(html,height=height,scrolling=False)
