from __future__ import annotations
import json
import streamlit.components.v1 as components


def render_vibration_3d(data: dict, height: int = 690):
    d=json.dumps(data,ensure_ascii=False,separators=(',',':'))
    html=f'''
<div id="vib3d" style="height:{height}px;border:1px solid #ded7cc;border-radius:14px;overflow:hidden;background:#202126;position:relative">
  <div style="position:absolute;z-index:5;left:14px;top:12px;background:#fff8edee;padding:8px 11px;border-radius:10px;font:13px system-ui;color:#25262a;line-height:1.35;max-width:44%">
    <b>Vibración libre 1GDL</b><br><span id="vibmsg"></span>
  </div>
  <div style="position:absolute;z-index:5;right:12px;top:12px;display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end;max-width:52%">
    <button id="play">Pausa</button><button id="front">Frente</button><button id="iso">Isométrica</button><button id="side">Lateral</button><button id="fit">Ajustar</button><button id="reset">Restablecer</button>
  </div>
  <div style="position:absolute;z-index:5;left:14px;bottom:12px;background:#202126dd;color:#eee;border:1px solid #4b4c50;border-radius:10px;padding:7px 10px;font:12px system-ui">
    <span id="readout">x = 0 mm</span>
  </div>
  <canvas id="fb" width="1000" height="{height}" style="width:100%;height:100%"></canvas>
</div>
<style>
#vib3d button{{border:1px solid #c8752d;background:#fff8ed;color:#292a2e;border-radius:8px;padding:7px 9px;cursor:pointer}}
#vib3d button:hover{{background:#fff1dd}}
</style>
<script type="module">
const D={d};
const root=document.getElementById('vib3d'), cv=document.getElementById('fb'), msg=document.getElementById('vibmsg'), readout=document.getElementById('readout');
let paused=false;
function fallback(){{
  const c=cv.getContext('2d'),W=cv.width,H=cv.height;c.fillStyle='#202126';c.fillRect(0,0,W,H);
  c.fillStyle='#c8752d';c.fillRect(100,H/2-100,30,200);
  const x=520,y=H/2;
  c.strokeStyle='#d7cab5';c.lineWidth=4;c.beginPath();c.moveTo(130,y);for(let i=0;i<14;i++){{const xx=130+i*24,yy=y+(i%2?34:-34);c.lineTo(xx,yy)}}c.lineTo(x-80,y);c.stroke();
  c.fillStyle='#e8dfcf';c.fillRect(x-80,y-70,160,140);
  c.strokeStyle='#f28e1c';c.lineWidth=3;c.beginPath();c.moveTo(x,y-70);c.lineTo(x,y-150);c.stroke();
  msg.textContent='Vista de respaldo · masa–resorte–amortiguador';
}}
fallback();
try{{
  const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm');
  const {{OrbitControls}}=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm');
  cv.style.display='none';
  const scene=new THREE.Scene();scene.background=new THREE.Color('#202126');
  const camera=new THREE.PerspectiveCamera(35,root.clientWidth/{height},0.01,120);
  const renderer=new THREE.WebGLRenderer({{antialias:true}});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.setSize(root.clientWidth,{height});root.appendChild(renderer.domElement);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.zoomToCursor=true;controls.minDistance=2;controls.maxDistance=40;
  scene.add(new THREE.HemisphereLight('#fff8ec','#303136',2.2));const dl=new THREE.DirectionalLight('#ffffff',2);dl.position.set(5,7,8);scene.add(dl);

  const rootG=new THREE.Group();scene.add(rootG);
  const matBase=new THREE.MeshStandardMaterial({{color:'#c8752d',roughness:.75}}),matMass=new THREE.MeshStandardMaterial({{color:'#e6dccb',roughness:.7}}),matMetal=new THREE.MeshStandardMaterial({{color:'#767980',metalness:.25,roughness:.5}}),matOrange=new THREE.MeshStandardMaterial({{color:'#f28e1c'}});
  const wall=new THREE.Mesh(new THREE.BoxGeometry(.28,3.0,2.5),matBase);wall.position.set(-3.8,0,0);rootG.add(wall);
  const floor=new THREE.GridHelper(12,12,0x47484d,0x303136);floor.position.set(0,-1.6,0);scene.add(floor);
  const rail=new THREE.Mesh(new THREE.BoxGeometry(7.0,.10,.16),matMetal);rail.position.set(-.2,-.8,0);rootG.add(rail);
  const mass=new THREE.Group();rootG.add(mass);const massBody=new THREE.Mesh(new THREE.BoxGeometry(1.55,1.55,1.55),matMass);mass.add(massBody);
  const eqLine=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(1.4,-1.4,-1.4),new THREE.Vector3(1.4,1.4,-1.4)]),new THREE.LineDashedMaterial({{color:0x9a9ca1,dashSize:.15,gapSize:.1}}));eqLine.computeLineDistances();rootG.add(eqLine);
  const eqLabel=new THREE.Mesh(new THREE.SphereGeometry(.055,12,12),matOrange);eqLabel.position.set(1.4,-1.38,-1.4);rootG.add(eqLabel);

  function makeSpring(xa,xb,y,z){{
    const pts=[];const turns=13,N=180;const lead=.22;
    for(let i=0;i<=N;i++){{const t=i/N,x=xa+(xb-xa)*t;let yy=y,zz=z;if(i>5&&i<N-5){{yy+=lead*Math.sin(turns*Math.PI*2*t);zz+=lead*Math.cos(turns*Math.PI*2*t)}}pts.push(new THREE.Vector3(x,yy,zz))}}
    return new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({{color:'#d9c8ae'}}));
  }}
  let spring=null;
  const damper=new THREE.Group();rootG.add(damper);
  const cyl=new THREE.Mesh(new THREE.CylinderGeometry(.22,.22,1.2,24),matMetal);cyl.rotation.z=Math.PI/2;damper.add(cyl);
  const rod=new THREE.Mesh(new THREE.CylinderGeometry(.07,.07,2.2,18),new THREE.MeshStandardMaterial({{color:'#d3d4d6',metalness:.55,roughness:.3}}));rod.rotation.z=Math.PI/2;damper.add(rod);

  function arrow(color){{const g=new THREE.Group();const m=new THREE.MeshStandardMaterial({{color}});const shaft=new THREE.Mesh(new THREE.CylinderGeometry(.035,.035,.7,12),m);shaft.rotation.z=Math.PI/2;shaft.position.x=.35;g.add(shaft);const head=new THREE.Mesh(new THREE.ConeGeometry(.10,.24,18),m);head.rotation.z=-Math.PI/2;head.position.x=.82;g.add(head);return g}}
  const fk=arrow('#f28e1c');const fc=arrow('#9fa1a6');rootG.add(fk);rootG.add(fc);fk.position.y=.65;fc.position.y=-.65;

  const tArr=D.t||[],xArr=D.x||[],vArr=D.v||[];const xmax=Math.max(...xArr.map(v=>Math.abs(v)),1e-9);const amp=(D.visual_amp||1);let time=0,last=performance.now();const duration=Math.max(D.duration||10,1e-6);const speed=D.speed||1;
  function sample(arr,t){{if(!arr.length)return 0;const u=((t%duration)/duration)*(arr.length-1),i=Math.floor(u),j=Math.min(arr.length-1,i+1),a=u-i;return arr[i]*(1-a)+arr[j]*a}}
  function updateModel(dt){{if(!paused)time+=dt*speed;const x=sample(xArr,time),v=sample(vArr,time);const disp=(x/xmax)*1.25*amp;mass.position.set(1.4+disp,0,0);
    if(spring)rootG.remove(spring);spring=makeSpring(-3.62,mass.position.x-.83,.55,0);rootG.add(spring);
    damper.position.set((-3.62+mass.position.x-.83)/2,-.55,0);const len=Math.max(.5,mass.position.x-.83+3.62);cyl.scale.y=Math.min(1.6,len/1.2);rod.scale.y=Math.min(2.0,len/2.2);
    const fkVal=-D.k*x,fcVal=-D.c*v;const fscale=Math.max(Math.abs(fkVal),Math.abs(fcVal),1e-9);for(const [g,val] of [[fk,fkVal],[fc,fcVal]]){{g.position.x=mass.position.x;g.scale.x=Math.max(.25,Math.min(1.5,Math.abs(val)/fscale*1.25));g.rotation.y=val>=0?0:Math.PI;}}
    readout.textContent=`t = ${{(time%duration).toFixed(2)}} s · x = ${{(x*1000).toFixed(2)}} mm · v = ${{v.toFixed(3)}} m/s`;
  }}
  function setFront(){{camera.position.set(0,0,10);controls.target.set(0,0,0);controls.update()}}
  function setIso(){{camera.position.set(5,4,8);controls.target.set(0,0,0);controls.update()}}
  function setSide(){{camera.position.set(0,7,0.01);controls.target.set(0,0,0);controls.update()}}
  function fit(){{const b=new THREE.Box3().setFromObject(rootG),s=b.getSize(new THREE.Vector3()),c=b.getCenter(new THREE.Vector3()),md=Math.max(s.x,s.y,s.z,1),f=camera.fov*Math.PI/180,dist=md/(2*Math.tan(f/2))*1.4,dir=new THREE.Vector3().subVectors(camera.position,controls.target).normalize();controls.target.copy(c);camera.position.copy(c.clone().add(dir.multiplyScalar(dist)));controls.update()}}
  function reset(){{setFront();fit()}}reset();
  document.getElementById('front').onclick=()=>{{setFront();fit()}};document.getElementById('iso').onclick=()=>{{setIso();fit()}};document.getElementById('side').onclick=()=>{{setSide();fit()}};document.getElementById('fit').onclick=fit;document.getElementById('reset').onclick=reset;document.getElementById('play').onclick=(e)=>{{paused=!paused;e.target.textContent=paused?'Reproducir':'Pausa'}};
  msg.textContent=`${{D.regime}} · ζ = ${{Number(D.zeta).toFixed(3)}} · fₙ = ${{Number(D.fn).toFixed(3)}} Hz`;
  function resize(){{camera.aspect=root.clientWidth/{height};camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,{height})}}window.addEventListener('resize',resize);
  function loop(now){{const dt=Math.min(.05,(now-last)/1000);last=now;updateModel(dt);controls.update();renderer.render(scene,camera);requestAnimationFrame(loop)}}requestAnimationFrame(loop);
}}catch(e){{console.error(e);msg.textContent='Vista de respaldo · Three.js no disponible'}}
</script>'''
    components.html(html,height=height,scrolling=False)
