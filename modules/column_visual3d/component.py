from __future__ import annotations
import json
import streamlit.components.v1 as components


def render_column_3d(data: dict, height: int = 680):
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    html = f'''
<div id="col3d" style="height:{height}px;border:1px solid #ded7cc;border-radius:14px;overflow:hidden;background:#202126;position:relative">
  <div style="position:absolute;z-index:4;left:14px;top:12px;background:#fff8edee;padding:8px 11px;border-radius:10px;font:13px system-ui;color:#25262a;line-height:1.35;max-width:48%">
    <b>Columna 3D</b><br><span id="colmsg"></span>
  </div>
  <div style="position:absolute;z-index:4;right:12px;top:12px;display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end;max-width:52%">
    <button id="front">Frente</button><button id="iso">Isométrica</button><button id="section">Sección</button><button id="fit">Ajustar</button><button id="reset">Restablecer</button>
  </div>
  <div style="position:absolute;z-index:4;left:14px;bottom:12px;background:#24252ad9;color:#f7ead8;padding:7px 10px;border-radius:9px;font:12px system-ui;line-height:1.4">
    <span style="color:#f28e1c">●</span> modo crítico amplificado &nbsp; <span style="color:#8f9298">┄</span> eje recto de referencia
  </div>
  <canvas id="fallback" width="1000" height="{height}" style="width:100%;height:100%"></canvas>
</div>
<style>
#col3d button{{border:1px solid #c8752d;background:#fff8ed;color:#292a2e;border-radius:8px;padding:7px 9px;cursor:pointer}}
#col3d button:hover{{background:#fff1dd}}
</style>
<script type="module">
const D={payload};
const root=document.getElementById('col3d'), cv=document.getElementById('fallback'), msg=document.getElementById('colmsg');

function rawMode(t){{
  const e=D.end||'Articulada – articulada';
  if(e==='Articulada – articulada') return Math.sin(Math.PI*t);
  if(e==='Empotrada – libre') return 1-Math.cos(Math.PI*t/2);
  if(e==='Empotrada – empotrada') return (1-Math.cos(2*Math.PI*t))/2;
  const q=4.493409458; return Math.sin(q*t)-q*Math.cos(q*t)-q*t+q;
}}
function mode(t){{
  if(!D.show_buckling) return 0;
  let mx=0; for(let i=0;i<=200;i++) mx=Math.max(mx,Math.abs(rawMode(i/200)));
  return mx>0 ? rawMode(t)/mx : 0;
}}
function slope(t){{ const h=0.0008; return (mode(Math.min(1,t+h))-mode(Math.max(0,t-h)))/(2*h); }}

function fallback(){{
  const c=cv.getContext('2d'),W=cv.width,H=cv.height; c.fillStyle='#202126';c.fillRect(0,0,W,H);
  const x=W*.50,y0=H*.82,y1=H*.17,amp=95*(D.visual_amp||1);
  c.strokeStyle='#8f9298';c.setLineDash([8,8]);c.lineWidth=2;c.beginPath();c.moveTo(x,y0);c.lineTo(x,y1);c.stroke();c.setLineDash([]);
  c.strokeStyle='#f28e1c';c.lineWidth=12;c.beginPath();
  for(let i=0;i<=140;i++){{const t=i/140,xx=x+amp*mode(t),yy=y0+(y1-y0)*t;i?c.lineTo(xx,yy):c.moveTo(xx,yy)}}c.stroke();
  c.fillStyle='#f28e1c'; c.font='14px system-ui'; c.fillText('P',x-5,y1-55);
  c.beginPath();c.moveTo(x,y1-45);c.lineTo(x,y1-5);c.strokeStyle='#f28e1c';c.lineWidth=3;c.stroke();
  msg.textContent='Vista de respaldo · modo crítico amplificado';
}}
fallback();

try{{
  const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm');
  const {{OrbitControls}}=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm');
  cv.style.display='none';
  const scene=new THREE.Scene();scene.background=new THREE.Color('#202126');
  const camera=new THREE.PerspectiveCamera(34,root.clientWidth/{height},.01,200);
  const renderer=new THREE.WebGLRenderer({{antialias:true}});renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.setSize(root.clientWidth,{height});root.appendChild(renderer.domElement);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.zoomToCursor=true;controls.minDistance=1.4;controls.maxDistance=70;
  scene.add(new THREE.HemisphereLight('#fff8ec','#303136',2.25)); const dl=new THREE.DirectionalLight('#fff',2);dl.position.set(6,8,7);scene.add(dl);const dl2=new THREE.DirectionalLight('#d7bb98',1);dl2.position.set(-5,4,-6);scene.add(dl2);

  const rootGroup=new THREE.Group(); scene.add(rootGroup);
  const L=6.6, visualAmp=0.85*(D.visual_amp||1), s=D.section||{{kind:'custom'}};
  const buckleDepth=(D.buckling_axis||'y').startsWith('y');

  let H=.68,B=.44,TW=.09,TF=.11;
  if(s.kind==='rect'){{const sc=.72/Math.max(s.h,s.b);H=s.h*sc;B=s.b*sc;}}
  else if(s.kind==='i_profile'||s.kind==='channel'){{const sc=.72/Math.max(s.h,s.b);H=s.h*sc;B=s.b*sc;TW=(s.tw||s.b*.12)*sc;TF=(s.tf||s.h*.12)*sc;}}
  else if(s.kind==='solid_circle'||s.kind==='tube'){{H=B=.66;}}

  function sectionLoop(){{
    if(s.kind==='rect'||s.kind==='custom') return [[-B/2,-H/2],[B/2,-H/2],[B/2,H/2],[-B/2,H/2]];
    if(s.kind==='i_profile') return [[-B/2,-H/2],[B/2,-H/2],[B/2,-H/2+TF],[TW/2,-H/2+TF],[TW/2,H/2-TF],[B/2,H/2-TF],[B/2,H/2],[-B/2,H/2],[-B/2,H/2-TF],[-TW/2,H/2-TF],[-TW/2,-H/2+TF],[-B/2,-H/2+TF]];
    if(s.kind==='channel') return [[-B/2,-H/2],[B/2,-H/2],[B/2,-H/2+TF],[-B/2+TW,-H/2+TF],[-B/2+TW,H/2-TF],[B/2,H/2-TF],[B/2,H/2],[-B/2,H/2]];
    const out=[];const ro=.34;for(let j=0;j<64;j++){{const q=2*Math.PI*j/64;out.push([ro*Math.cos(q),ro*Math.sin(q)])}}return out;
  }}
  const outer=sectionLoop();
  const inner=[]; if(s.kind==='tube'&&s.di&&s.do){{const ri=.34*s.di/s.do;for(let j=0;j<64;j++){{const q=-2*Math.PI*j/64;inner.push([ri*Math.cos(q),ri*Math.sin(q)])}}}}
  const loops=[outer]; if(inner.length)loops.push(inner);

  function centerAt(t){{const m=visualAmp*mode(t);return buckleDepth?new THREE.Vector3(0,L*t,m):new THREE.Vector3(m,L*t,0)}}
  function framePoint(t,p){{
    const c=centerAt(t); const ang=Math.atan((visualAmp/L)*slope(t));
    let x=p[0], z=p[1];
    if(buckleDepth){{ // deflection in z, rotation about x
      const yy=-z*Math.sin(ang), zz=z*Math.cos(ang); return new THREE.Vector3(c.x+x,c.y+yy,c.z+zz);
    }} else {{ // deflection in x, rotation about z
      const xx=x*Math.cos(ang), yy=x*Math.sin(ang); return new THREE.Vector3(c.x+xx,c.y-yy,c.z+z);
    }}
  }}

  function addSkin(loop,color,opacity){{
    const slices=54, n=loop.length, verts=[], inds=[];
    for(let i=0;i<=slices;i++){{const t=i/slices;for(const p of loop){{const q=framePoint(t,p);verts.push(q.x,q.y,q.z)}}}}
    for(let i=0;i<slices;i++)for(let j=0;j<n;j++){{const jn=(j+1)%n,a=i*n+j,b=(i+1)*n+j,c=(i+1)*n+jn,d=i*n+jn;inds.push(a,b,d,b,c,d)}}
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));g.setIndex(inds);g.computeVertexNormals();
    rootGroup.add(new THREE.Mesh(g,new THREE.MeshStandardMaterial({{color,transparent:true,opacity,side:THREE.DoubleSide,roughness:.78,metalness:.04}})));
  }}
  for(const lp of loops)addSkin(lp,'#8d8f95',.34);

  function addLoop(t,color,w=1){{const pts=outer.map(p=>framePoint(t,p));pts.push(pts[0].clone());rootGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({{color,linewidth:w}})));}}
  for(let i=0;i<=13;i++)addLoop(i/13,i===13?'#f28e1c':'#d9c8ae',i===13?2:1);

  // Generatrices de la sección real
  const gens=Math.min(14,outer.length);for(let g=0;g<gens;g++){{const idx=Math.floor(g*outer.length/gens),pts=[];for(let i=0;i<=80;i++)pts.push(framePoint(i/80,outer[idx]));rootGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({{color:g===0?'#f28e1c':'#9e9589',transparent:true,opacity:g===0?.95:.55}})))}}

  // Eje recto de referencia
  if(D.show_original!==false){{const ax=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0),new THREE.Vector3(0,L,0)]),new THREE.LineDashedMaterial({{color:'#8f9298',dashSize:.16,gapSize:.11}}));ax.computeLineDistances();scene.add(ax)}}

  function fixedPlate(y){{const m=new THREE.Mesh(new THREE.BoxGeometry(1.5,.13,1.25),new THREE.MeshStandardMaterial({{color:'#c8752d',roughness:.75}}));m.position.set(0,y,0);scene.add(m)}}
  function pinMark(y,flip=false){{const cone=new THREE.Mesh(new THREE.ConeGeometry(.42,.48,4),new THREE.MeshStandardMaterial({{color:'#c8752d',roughness:.75}}));cone.position.set(0,y,0);if(flip)cone.rotation.z=Math.PI;scene.add(cone);const base=new THREE.Mesh(new THREE.BoxGeometry(1.0,.08,.9),new THREE.MeshStandardMaterial({{color:'#8d8f95'}}));base.position.set(0,y+(flip?.25:-.25),0);scene.add(base)}}
  const e=D.end||'';
  if(e.startsWith('Empotrada')) fixedPlate(-.12); else pinMark(-.26,false);
  if(e==='Empotrada – libre'){{ /* extremo libre */ }}
  else if(e.endsWith('empotrada')) fixedPlate(L+.12);
  else pinMark(L+.26,true);

  // Carga axial
  for(let k=-1;k<=1;k++){{const origin=new THREE.Vector3(k*.28,L+.9,0);scene.add(new THREE.ArrowHelper(new THREE.Vector3(0,-1,0),origin,.72,0xf28e1c,.16,.09))}}

  // Indicador de eje de pandeo
  const guideMat=new THREE.LineBasicMaterial({{color:'#f2c58d',transparent:true,opacity:.8}});
  const m=.5; const cMid=centerAt(m); let gp;
  if(buckleDepth) gp=[new THREE.Vector3(cMid.x,cMid.y,cMid.z-.9),new THREE.Vector3(cMid.x,cMid.y,cMid.z+.9)]; else gp=[new THREE.Vector3(cMid.x-.9,cMid.y,cMid.z),new THREE.Vector3(cMid.x+.9,cMid.y,cMid.z)];
  scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(gp),guideMat));

  const grid=new THREE.GridHelper(6,12,0x4a4b50,0x34353a);scene.add(grid);

  function setFront(){{camera.position.set(7.8,L*.52,0.01);controls.target.set(0,L*.5,0);controls.update()}}
  function setIso(){{camera.position.set(7.5,L*.68,7.5);controls.target.set(0,L*.48,0);controls.update()}}
  function setSection(){{const c=centerAt(.5);camera.position.set(c.x,c.y,c.z+5.2);controls.target.copy(c);controls.update()}}
  function fit(){{const box=new THREE.Box3().setFromObject(rootGroup);const size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3()),maxDim=Math.max(size.x,size.y,size.z,1);const fov=camera.fov*Math.PI/180;const dist=maxDim/(2*Math.tan(fov/2))*1.35;const dir=new THREE.Vector3().subVectors(camera.position,controls.target).normalize();controls.target.copy(center);camera.position.copy(center.clone().add(dir.multiplyScalar(dist)));controls.update()}}
  function reset(){{setFront();fit()}}
  reset();
  document.getElementById('front').onclick=()=>{{setFront();fit()}};document.getElementById('iso').onclick=()=>{{setIso();fit()}};document.getElementById('section').onclick=()=>{{setSection();fit()}};document.getElementById('fit').onclick=fit;document.getElementById('reset').onclick=reset;

  msg.textContent='Modo crítico ideal · '+(D.axis_label||'eje gobernante')+' · P/Pcr='+(Number(D.load_ratio||0).toFixed(3));
  window.addEventListener('resize',()=>{{camera.aspect=root.clientWidth/{height};camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,{height})}});
  function animate(){{controls.update();renderer.render(scene,camera);requestAnimationFrame(animate)}}animate();
}}catch(e){{console.error(e);msg.textContent='Vista de respaldo · Three.js no disponible';}}
</script>
'''
    components.html(html, height=height, scrolling=False)
