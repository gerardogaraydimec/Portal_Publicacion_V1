from __future__ import annotations
import json
import streamlit.components.v1 as components


def render_forced_vibration_3d(data: dict, height: int = 620):
    d = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    html = f'''
<div id="vf3d" style="height:{height}px;border:1px solid #ded7cc;border-radius:14px;overflow:hidden;background:#202126;position:relative">
  <div style="position:absolute;z-index:5;left:13px;top:11px;background:#fff8edee;padding:8px 11px;border-radius:10px;font:13px system-ui;color:#25262a;line-height:1.35">
    <b id="titlebox">Vibración 1GDL</b><br><span id="vfmsg"></span>
  </div>
  <div id="vfread" style="position:absolute;z-index:5;left:13px;bottom:11px;background:#202126dd;border:1px solid #515258;color:#f5ead7;padding:7px 10px;border-radius:9px;font:12px system-ui"></div>
  <div style="position:absolute;z-index:5;right:11px;top:11px;display:flex;gap:5px;flex-wrap:wrap;max-width:58%">
    <button id="play">Pausa</button><button id="front">Frente</button><button id="iso">Isométrica</button><button id="side">Superior</button><button id="fit">Ajustar</button><button id="reset">Restablecer</button>
  </div>
  <canvas id="vffb" width="1000" height="{height}" style="width:100%;height:100%"></canvas>
</div>
<style>
#vf3d button{{border:1px solid #c8752d;background:#fff8ed;color:#292a2e;border-radius:8px;padding:7px 9px;cursor:pointer}}
#vf3d button:hover{{background:#fff1dd}}
</style>
<script type="module">
const D={d};
const mode=D.mode||'force';
const root=document.getElementById('vf3d'),cv=document.getElementById('vffb'),msg=document.getElementById('vfmsg'),read=document.getElementById('vfread'),titlebox=document.getElementById('titlebox');
let paused=false;
function fallback(){{
  const c=cv.getContext('2d'),W=cv.width,H=cv.height;c.fillStyle='#202126';c.fillRect(0,0,W,H);
  const y=H/2,xm=W*.60,wall=90;c.fillStyle='#c8752d';c.fillRect(wall,y-110,30,220);
  c.strokeStyle='#d9c8ae';c.lineWidth=4;c.beginPath();c.moveTo(wall+30,y-20);for(let i=0;i<13;i++){{const xx=wall+55+i*26,yy=y-20+(i%2?25:-25);c.lineTo(xx,yy)}}c.lineTo(xm-80,y-20);c.stroke();
  c.fillStyle='#e8dfcf';c.fillRect(xm-75,y-65,150,130);
  c.strokeStyle='#f28e1c';c.lineWidth=5;c.beginPath();c.moveTo(xm+85,y-95);c.lineTo(xm+180,y-95);c.stroke();c.beginPath();c.moveTo(xm+185,y-95);c.lineTo(xm+165,y-107);c.lineTo(xm+165,y-83);c.closePath();c.fillStyle='#f28e1c';c.fill();
  c.fillStyle='#f5ead7';c.font='16px system-ui';c.fillText(mode==='base'?'y(t)':'F(t)',xm+105,y-115);
  msg.textContent='Vista de respaldo';
}}
fallback();
try{{
  const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm');
  const {{OrbitControls}}=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm');
  cv.style.display='none';
  titlebox.textContent = mode==='force' ? 'Fuerza armónica 3D' : (mode==='unbalance' ? 'Desbalance rotatorio 3D' : 'Excitación de base 3D');

  const scene=new THREE.Scene();scene.background=new THREE.Color('#202126');
  const camera=new THREE.PerspectiveCamera(34,root.clientWidth/{height},.01,120);
  const renderer=new THREE.WebGLRenderer({{antialias:true}});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.setSize(root.clientWidth,{height});root.appendChild(renderer.domElement);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.zoomToCursor=true;controls.minDistance=2;controls.maxDistance=40;
  scene.add(new THREE.HemisphereLight('#fff8ec','#303136',2.25));const dl=new THREE.DirectionalLight('#fff',2);dl.position.set(5,7,8);scene.add(dl);

  const rootG=new THREE.Group();scene.add(rootG);
  const matBase=new THREE.MeshStandardMaterial({{color:'#c8752d',roughness:.78}}),matMass=new THREE.MeshStandardMaterial({{color:'#e6dccb',roughness:.68}}),matMetal=new THREE.MeshStandardMaterial({{color:'#767980',metalness:.25,roughness:.5}});
  const wall=new THREE.Mesh(new THREE.BoxGeometry(.28,2.8,2.35),matBase);wall.position.set(-3.8,0,0);rootG.add(wall);
  const basePlate=new THREE.Mesh(new THREE.BoxGeometry(2.7,.22,2.0), new THREE.MeshStandardMaterial({{color:'#b48558', roughness:.82}}));basePlate.position.set(-2.55,-1.06,0);rootG.add(basePlate);
  const grid=new THREE.GridHelper(11,11,0x46474c,0x303136);grid.position.set(0,-1.45,0);scene.add(grid);
  const rail=new THREE.Mesh(new THREE.BoxGeometry(7.1,.09,.14),matMetal);rail.position.set(-.12,-.78,0);rootG.add(rail);
  const axisArrow=new THREE.ArrowHelper(new THREE.Vector3(1,0,0),new THREE.Vector3(-.35,-1.13,-.02),1.25,0xc8752d,.20,.11);rootG.add(axisArrow);

  const mass=new THREE.Group();rootG.add(mass);const body=new THREE.Mesh(new THREE.BoxGeometry(1.5,1.5,1.5),matMass);mass.add(body);mass.add(new THREE.LineSegments(new THREE.EdgesGeometry(body.geometry),new THREE.LineBasicMaterial({{color:0xaaa08f}})));
  const eqLine=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(1.4,-1.25,-1.05),new THREE.Vector3(1.4,1.25,-1.05)]),new THREE.LineDashedMaterial({{color:0xb0b2b6,dashSize:.13,gapSize:.09}}));eqLine.computeLineDistances();rootG.add(eqLine);

  function spring(xa,xb,y,z){{const pts=[];const N=180;for(let i=0;i<=N;i++){{const q=i/N,x=xa+(xb-xa)*q;let yy=y,zz=z;if(i>5&&i<N-5){{yy+=.2*Math.sin(24*Math.PI*q);zz+=.2*Math.cos(24*Math.PI*q)}}pts.push(new THREE.Vector3(x,yy,zz))}}return new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({{color:'#d9c8ae'}}))}}
  let sp=null;
  const damper=new THREE.Group();rootG.add(damper);const cyl=new THREE.Mesh(new THREE.CylinderGeometry(.20,.20,1.15,24),matMetal);cyl.rotation.z=Math.PI/2;damper.add(cyl);const rod=new THREE.Mesh(new THREE.CylinderGeometry(.06,.06,2.05,18),new THREE.MeshStandardMaterial({{color:'#d3d4d6',metalness:.55,roughness:.3}}));rod.rotation.z=Math.PI/2;damper.add(rod);

  const applied=new THREE.ArrowHelper(new THREE.Vector3(1,0,0),new THREE.Vector3(),1,0xf28e1c,.23,.13);rootG.add(applied);
  const motion=new THREE.ArrowHelper(new THREE.Vector3(1,0,0),new THREE.Vector3(),1,0xf5ead7,.22,.12);rootG.add(motion);
  const trans=new THREE.ArrowHelper(new THREE.Vector3(1,0,0),new THREE.Vector3(),1,0x9fa1a6,.22,.12);rootG.add(trans);
  const fkA=new THREE.ArrowHelper(new THREE.Vector3(1,0,0),new THREE.Vector3(),1,0xc8752d,.18,.10);rootG.add(fkA);
  const fcA=new THREE.ArrowHelper(new THREE.Vector3(1,0,0),new THREE.Vector3(),1,0x6d7076,.18,.10);rootG.add(fcA);
  const baseArrow=new THREE.ArrowHelper(new THREE.Vector3(1,0,0),new THREE.Vector3(),1,0xe0b46d,.20,.11);rootG.add(baseArrow);

  function label(text,color){{const cn=document.createElement('canvas');cn.width=256;cn.height=64;const cx=cn.getContext('2d');cx.font='600 29px system-ui';cx.textAlign='center';cx.fillStyle=color;cx.fillText(text,128,40);const tex=new THREE.CanvasTexture(cn);const s=new THREE.Sprite(new THREE.SpriteMaterial({{map:tex,transparent:true,depthTest:false}}));s.scale.set(1.3,.32,1);rootG.add(s);return s}}
  const lF=label(mode==='base'?'y(t)':'F(t)','#f28e1c'),lV=label('v(t)','#f5ead7'),lT=label('Fₜ','#b8b9bc'),lK=label('Fₖ','#c8752d'),lC=label('F꜀','#8e9095'),lB=label('base','#e0b46d');

  const rotorG=new THREE.Group(); rootG.add(rotorG); rotorG.visible = mode==='unbalance';
  const disk=new THREE.Mesh(new THREE.CylinderGeometry(.42,.42,.18,36), new THREE.MeshStandardMaterial({{color:'#8d9096', metalness:.35, roughness:.45}})); disk.rotation.z=Math.PI/2; rotorG.add(disk);
  const ecc=new THREE.Mesh(new THREE.SphereGeometry(.09,18,18), new THREE.MeshStandardMaterial({{color:'#f28e1c'}})); rotorG.add(ecc);
  const shaft=new THREE.Mesh(new THREE.CylinderGeometry(.06,.06,.85,18), new THREE.MeshStandardMaterial({{color:'#d0d2d6', metalness:.6, roughness:.3}})); shaft.rotation.z=Math.PI/2; rotorG.add(shaft);
  const ring=new THREE.Line(new THREE.BufferGeometry().setFromPoints(Array.from({{length:65}},(_,i)=>{{const a=i/64*2*Math.PI; return new THREE.Vector3(0,.34*Math.cos(a),.34*Math.sin(a)); }})), new THREE.LineBasicMaterial({{color:'#b5b8bd'}})); rotorG.add(ring);

  const t=D.t||[],x=D.x||[],v=D.v||[],inp=D.input||[],fk=D.fk||[],fc=D.fc||[],ft=D.ft||[],yArr=D.y||[],thetaArr=D.theta||[];const duration=Math.max(D.duration||8,1e-6),speed=D.speed||1,amp=D.visual_amp||1;
  const xmax=Math.max(...x.map(q=>Math.abs(q)),1e-9),ymax=Math.max(...yArr.map(q=>Math.abs(q)),1e-9),vmax=Math.max(...v.map(q=>Math.abs(q)),1e-9),fmax=Math.max(...inp.map(Math.abs),...fk.map(Math.abs),...fc.map(Math.abs),...ft.map(Math.abs),1e-9);
  let tm=0,last=performance.now();
  function sample(arr,tt){{if(!arr.length)return 0;const u=((tt%duration)/duration)*(arr.length-1),i=Math.floor(u),j=Math.min(arr.length-1,i+1),q=u-i;return arr[i]*(1-q)+arr[j]*q}}
  function setArr(a,l,val,norm,posY,visible,anchorX,anchorWall=false){{const s=Math.sign(val)||1;a.setDirection(new THREE.Vector3(s,0,0));const len=.22+1.13*Math.min(1,Math.abs(val)/Math.max(norm,1e-12));a.setLength(len,.22,.12);const ox=anchorWall?-3.58:anchorX;a.position.set(ox,posY,0);l.position.set(ox+s*(len*.58),posY+.24,0);a.visible=visible&&Math.abs(val)>norm*.012;l.visible=a.visible}}
  function update(dt){{
    if(!paused)tm+=dt*speed;
    const xx=sample(x,tm),yy=sample(yArr,tm),vv=sample(v,tm),ff=sample(inp,tm),fkv=sample(fk,tm),fcv=sample(fc,tm),ftv=sample(ft,tm),th=sample(thetaArr,tm);
    const baseShift = mode==='base' ? ((yy/ymax)*0.95*amp) : 0;
    wall.position.x = -3.8 + baseShift; basePlate.position.x = -2.55 + baseShift; rail.position.x = -0.12 + baseShift; 
    const eqx = 1.4 + baseShift; eqLine.position.x = baseShift; mass.position.set(eqx + (xx-xmodeOffset())/xmax*1.22*amp,0,0);
    rotorG.position.set(mass.position.x,.78,0);
    if(mode==='unbalance'){{ ecc.position.set(0,.24*Math.cos(th),.24*Math.sin(th)); }}
    if(sp)rootG.remove(sp);sp=spring(-3.62+baseShift,mass.position.x-.80,.50,0);rootG.add(sp);
    const xb=mass.position.x-.80,xa=-3.62+baseShift,len=Math.max(.55,xb-xa),mid=(xa+xb)/2;damper.position.set(mid,-.52,0);cyl.scale.y=Math.max(.42,Math.min(2.0,len/1.15));rod.scale.y=Math.max(.42,Math.min(2.2,len/2.05));
    setArr(applied,lF,ff,fmax,1.18,mode!=='base'||D.show_base===true,mass.position.x,false);setArr(motion,lV,vv,vmax,.80,D.show_motion!==false,mass.position.x,false);setArr(trans,lT,ftv,fmax,-.95,D.show_transmitted!==false,-3.58+baseShift,true);setArr(fkA,lK,fkv,fmax,.25,D.show_internal===true,mass.position.x,false);setArr(fcA,lC,fcv,fmax,-.25,D.show_internal===true,mass.position.x,false);
    setArr(baseArrow,lB,yy,ymax,1.18,D.show_base===true,-3.58+baseShift,true);
    read.textContent = mode==='base' ? `t = ${{(tm%duration).toFixed(2)}} s · y = ${{(yy*1000).toFixed(2)}} mm · x = ${{(xx*1000).toFixed(2)}} mm · z = ${{((xx-yy)*1000).toFixed(2)}} mm` : `t = ${{(tm%duration).toFixed(2)}} s · input = ${{ff.toFixed(1)}} · x = ${{(xx*1000).toFixed(2)}} mm · v = ${{vv.toFixed(3)}} m/s`;
  }}
  function xmodeOffset(){{ return mode==='base' ? sample(yArr,tm) : 0; }}
  function front(){{camera.position.set(-.1,.1,9.3);controls.target.set(-.2,0,0);controls.update()}}function iso(){{camera.position.set(5,3.7,7.8);controls.target.set(-.2,0,0);controls.update()}}function side(){{camera.position.set(-.2,7.3,.01);controls.target.set(-.2,0,0);controls.update()}}function fit(){{const b=new THREE.Box3().setFromObject(rootG),sz=b.getSize(new THREE.Vector3()),ct=b.getCenter(new THREE.Vector3()),md=Math.max(sz.x,sz.y,sz.z,1),f=camera.fov*Math.PI/180,dist=md/(2*Math.tan(f/2))*1.32,dir=new THREE.Vector3().subVectors(camera.position,controls.target).normalize();controls.target.copy(ct);camera.position.copy(ct.clone().add(dir.multiplyScalar(dist)));controls.update()}}function reset(){{front();fit()}}reset();
  document.getElementById('front').onclick=()=>{{front();fit()}};document.getElementById('iso').onclick=()=>{{iso();fit()}};document.getElementById('side').onclick=()=>{{side();fit()}};document.getElementById('fit').onclick=fit;document.getElementById('reset').onclick=reset;document.getElementById('play').onclick=e=>{{paused=!paused;e.target.textContent=paused?'Reproducir':'Pausa'}};
  msg.textContent = mode==='base' ? `r = ${{Number(D.r).toFixed(3)}} · X/Y = ${{Number(D.H).toFixed(3)}} · desfase = ${{Number(D.phase_deg).toFixed(1)}}°` : `r = ${{Number(D.r).toFixed(3)}} · H = ${{Number(D.H).toFixed(3)}} · desfase = ${{Number(D.phase_deg).toFixed(1)}}°`;
  window.addEventListener('resize',()=>{{camera.aspect=root.clientWidth/{height};camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,{height})}});
  function loop(now){{const dt=Math.min(.05,(now-last)/1000);last=now;update(dt);controls.update();renderer.render(scene,camera);requestAnimationFrame(loop)}}requestAnimationFrame(loop);
}}catch(e){{console.error(e);msg.textContent='Vista de respaldo · Three.js no disponible';}}
</script>
'''
    components.html(html, height=height, scrolling=False)
