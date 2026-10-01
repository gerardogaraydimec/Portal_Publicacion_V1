from __future__ import annotations
import json
import streamlit.components.v1 as components


def render_torsion_3d(data: dict, height: int = 690):
    d = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    html = f'''
<div id="tor3d" style="height:{height}px;border:1px solid #ded7cc;border-radius:14px;overflow:hidden;background:#202126;position:relative">
  <div style="position:absolute;z-index:4;left:14px;top:12px;background:#fff8edee;padding:8px 11px;border-radius:10px;font:13px system-ui;color:#25262a;line-height:1.35">
    <b>Torsión 3D</b><br><span id="tormsg"></span>
  </div>
  <div style="position:absolute;z-index:4;right:12px;top:12px;display:flex;gap:6px;flex-wrap:wrap;max-width:55%">
    <button id="front">Frente</button><button id="iso">Isométrica</button><button id="end">Sección</button><button id="fit">Ajustar</button><button id="reset">Restablecer</button>
  </div>
  <canvas id="fb" width="1000" height="{height}" style="width:100%;height:100%"></canvas>
</div>
<style>
#tor3d button{{border:1px solid #c8752d;background:#fff8ed;color:#292a2e;border-radius:8px;padding:7px 9px;cursor:pointer}}
#tor3d button:hover{{background:#fff1dd}}
</style>
<script type="module">
const D={d};
const root=document.getElementById('tor3d');
const cv=document.getElementById('fb');
const msg=document.getElementById('tormsg');

function drawFallback(){{
  const c=cv.getContext('2d'); const W=cv.width, H=cv.height;
  c.fillStyle='#202126'; c.fillRect(0,0,W,H);
  c.strokeStyle='#3a3b40'; c.lineWidth=1;
  for(let i=0;i<10;i++){{ c.beginPath(); c.moveTo(60+i*90,H-80); c.lineTo(60+i*90,90); c.stroke(); }}
  for(let j=0;j<6;j++){{ c.beginPath(); c.moveTo(60,100+j*80); c.lineTo(W-60,100+j*80); c.stroke(); }}
  const x0=130,x1=W-180,y=H/2; const n=13; const phi=D.phi_display||0; const h=140,b=80;
  for(let i=0;i<n;i++){{
    const t=i/(n-1), x=x0+(x1-x0)*t, a=phi*t;
    c.save(); c.translate(x,y); c.rotate(-a);
    c.strokeStyle = i===n-1 ? '#f28e1c' : '#d9c8ae'; c.lineWidth = i===n-1 ? 2.5 : 1.4;
    c.strokeRect(-b/2,-h/2,b,h); c.restore();
  }}
  c.strokeStyle='#f28e1c'; c.lineWidth=3;
  c.beginPath(); c.arc(W-110,y,48,-Math.PI*0.2,Math.PI*1.4); c.stroke();
  msg.textContent='Vista de respaldo · elemento torsionado';
}}
drawFallback();

try{{
  const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm');
  const {{OrbitControls}}=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm');
  cv.style.display='none';

  const scene=new THREE.Scene();
  scene.background=new THREE.Color('#202126');
  const camera=new THREE.PerspectiveCamera(34, root.clientWidth/{height}, 0.01, 200);
  const renderer=new THREE.WebGLRenderer({{antialias:true, alpha:false}});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(root.clientWidth, {height});
  root.appendChild(renderer.domElement);

  const controls=new OrbitControls(camera, renderer.domElement);
  controls.enableDamping=true;
  controls.dampingFactor=0.08;
  controls.target.set(3.8,0,0);
  controls.minDistance=1.4;
  controls.maxDistance=60;
  controls.zoomToCursor=true;

  const hemi=new THREE.HemisphereLight('#fff8ec','#303136',2.2); scene.add(hemi);
  const dir=new THREE.DirectionalLight('#ffffff',2.0); dir.position.set(4,6,7); scene.add(dir);
  const dir2=new THREE.DirectionalLight('#d4b38f',1.0); dir2.position.set(-5,2,-6); scene.add(dir2);

  const rootGroup=new THREE.Group(); scene.add(rootGroup);
  const deformed=new THREE.Group(); rootGroup.add(deformed);
  const undeformed=new THREE.Group(); rootGroup.add(undeformed);

  const L=7.6;
  const phi=D.phi_display||0;
  const s=D.section || {{kind:'custom'}};

  let H=1.20, B=0.70, TW=0.14, TF=0.17;
  if(s.kind==='rect'){{ const sc=1.25/Math.max(s.h,s.b); H=s.h*sc; B=s.b*sc; }}
  else if(s.kind==='i_profile' || s.kind==='channel'){{ const sc=1.25/Math.max(s.h,s.b); H=s.h*sc; B=s.b*sc; TW=(s.tw||s.b*.12)*sc; TF=(s.tf||s.h*.12)*sc; }}
  else if(s.kind==='solid_circle'){{ H=B=1.15; }}
  else if(s.kind==='tube'){{ H=B=1.20; }}

  function rotateYZ(y,z,a){{ return [y*Math.cos(a)-z*Math.sin(a), y*Math.sin(a)+z*Math.cos(a)]; }}

  function sectionLoops(){{
    const loops=[];
    if(s.kind==='rect' || s.kind==='custom'){{
      loops.push([[-H/2,-B/2],[H/2,-B/2],[H/2,B/2],[-H/2,B/2]]);
    }} else if(s.kind==='i_profile'){{
      loops.push([
        [-H/2,-B/2],[-H/2,B/2],[-H/2+TF,B/2],[-H/2+TF,TW/2],[H/2-TF,TW/2],[H/2-TF,B/2],[H/2,B/2],[H/2,-B/2],[H/2-TF,-B/2],[H/2-TF,-TW/2],[-H/2+TF,-TW/2],[-H/2+TF,-B/2]
      ]);
    }} else if(s.kind==='channel'){{
      loops.push([
        [-H/2,-B/2],[-H/2,B/2],[-H/2+TF,B/2],[-H/2+TF,-B/2+TW],[H/2-TF,-B/2+TW],[H/2-TF,B/2],[H/2,B/2],[H/2,-B/2]
      ]);
    }} else {{
      const outer=[], inner=[]; const ro=0.58; const ri=(s.kind==='tube'&&s.di&&s.do)? ro*s.di/s.do : 0;
      const N=72;
      for(let j=0;j<N;j++){{
        const q=2*Math.PI*j/N;
        outer.push([ro*Math.sin(q), ro*Math.cos(q)]);
        if(ri>0) inner.push([ri*Math.sin(-q), ri*Math.cos(-q)]);
      }}
      loops.push(outer); if(inner.length) loops.push(inner);
    }}
    return loops;
  }}

  const loops=sectionLoops();

  function addLoop(group, loop, x, a, color, width=1.5){{
    const pts=[];
    for(const p of loop){{ const yz=rotateYZ(p[0],p[1],a); pts.push(new THREE.Vector3(x, yz[0], yz[1])); }}
    pts.push(pts[0].clone());
    group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({{color, transparent:true, opacity:0.95, linewidth:width}})));
  }}

  function addGenerators(group, loop, count, color, dashed=false){{
    const mat = dashed ? new THREE.LineDashedMaterial({{color, dashSize:0.18, gapSize:0.13, transparent:true, opacity:0.55}}) : new THREE.LineBasicMaterial({{color, transparent:true, opacity:0.78}});
    const n=loop.length;
    for(let g=0; g<count; g++){{
      const idx=Math.round(g*n/count)%n;
      const pts=[];
      for(let i=0;i<=70;i++){{
        const t=i/70, x=L*t, a=phi*t;
        const yz=rotateYZ(loop[idx][0], loop[idx][1], a);
        pts.push(new THREE.Vector3(x, yz[0], yz[1]));
      }}
      const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat);
      if(dashed) line.computeLineDistances();
      group.add(line);
    }}
  }}

  function addSkinRibbon(group, loop, color, opacity){{
    const seg=Math.min(loop.length, 40);
    const idx=[];
    for(let k=0;k<seg;k++) idx.push(Math.floor(k*loop.length/seg));
    const slices=36;
    const verts=[]; const indices=[];
    for(let i=0;i<=slices;i++){{
      const t=i/slices, x=L*t, a=phi*t;
      for(const j of idx){{
        const yz=rotateYZ(loop[j][0], loop[j][1], a);
        verts.push(x, yz[0], yz[1]);
      }}
    }}
    const m=idx.length;
    for(let i=0;i<slices;i++){{
      for(let j=0;j<m;j++){{
        const jn=(j+1)%m;
        const a=i*m+j, b=(i+1)*m+j, c=(i+1)*m+jn, d=i*m+jn;
        indices.push(a,b,d, b,c,d);
      }}
    }}
    const geo=new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(verts,3));
    geo.setIndex(indices); geo.computeVertexNormals();
    const mesh=new THREE.Mesh(geo, new THREE.MeshStandardMaterial({{color, transparent:true, opacity, side:THREE.DoubleSide, roughness:0.8, metalness:0.05}}));
    group.add(mesh);
  }}

  if(D.show_original){{
    for(const loop of loops){{ addLoop(undeformed, loop, 0, 0, '#77797f'); addLoop(undeformed, loop, L, 0, '#77797f'); addGenerators(undeformed, loop, Math.min(12, loop.length), '#66686d', true); }}
  }}

  if(D.show_slices){{
    for(let i=0;i<=12;i++){{
      const t=i/12, x=L*t, a=phi*t;
      for(const loop of loops) addLoop(deformed, loop, x, a, i===12 ? '#f28e1c' : '#d9c8ae', i===12 ? 2.2 : 1.2);
    }}
  }} else {{
    for(const loop of loops){{ addLoop(deformed, loop, 0, 0, '#d9c8ae', 1.3); addLoop(deformed, loop, L, phi, '#f28e1c', 2.1); }}
  }}

  if(D.show_generators){{
    let first=true;
    for(const loop of loops){{ addGenerators(deformed, loop, Math.min(14, Math.max(6, Math.floor(loop.length/2))), first ? '#f28e1c' : '#b8aa93'); first=false; }}
  }}

  if(s.kind==='solid_circle' || s.kind==='tube' || s.kind==='rect'){{
    for(const loop of loops) addSkinRibbon(deformed, loop, s.kind==='solid_circle' || s.kind==='tube' ? '#8c8f96' : '#958b7d', 0.18);
  }}

  const axisGeo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0), new THREE.Vector3(L,0,0)]);
  deformed.add(new THREE.Line(axisGeo, new THREE.LineBasicMaterial({{color:'#4b4c50'}})));

  const grid=new THREE.GridHelper(12,12,0x47484d,0x303136); grid.position.set(L/2,-1.5,0); scene.add(grid);

  function makeSupport(x){{
    const g=new THREE.Group();
    const base=new THREE.Mesh(new THREE.BoxGeometry(0.18,0.45,0.45), new THREE.MeshStandardMaterial({{color:'#cbc1b1'}}));
    base.position.x=x; g.add(base);
    const cap=new THREE.Mesh(new THREE.CylinderGeometry(0.16,0.16,0.02,28), new THREE.MeshStandardMaterial({{color:'#f1e4cf'}}));
    cap.rotation.z=Math.PI/2; cap.position.set(x+0.1,0,0); g.add(cap);
    return g;
  }}
  scene.add(makeSupport(0));

  function torqueArrow(sign=1){{
    const g=new THREE.Group();
    const mat=new THREE.MeshStandardMaterial({{color:'#f28e1c'}});
    const tor=new THREE.Mesh(new THREE.TorusGeometry(0.7,0.035,12,72,Math.PI*1.55), mat);
    tor.rotation.y=Math.PI/2; tor.rotation.z=sign>0 ? 0 : Math.PI; tor.position.set(L+0.18,0,0); g.add(tor);
    const head=new THREE.Mesh(new THREE.ConeGeometry(0.10,0.25,24), mat);
    head.position.set(L+0.17, sign>0 ? 0.58 : -0.58, sign>0 ? 0.26 : -0.26); head.rotation.x=sign>0 ? -0.95 : 2.2; g.add(head);
    return g;
  }}
  scene.add(torqueArrow(D.torque_sign||1));

  let currentView='front';
  function setFront(){{ currentView='front'; camera.position.set(L/2,0,9.4); controls.target.set(L/2,0,0); controls.update(); }}
  function setIso(){{ currentView='iso'; camera.position.set(L/2+4.7,3.5,7.6); controls.target.set(L/2,0,0); controls.update(); }}
  function setEnd(){{ currentView='end'; camera.position.set(L+2.6,0,0.01); controls.target.set(L,0,0); controls.update(); }}
  function fitPreserveOrientation(){{
    const box=new THREE.Box3().setFromObject(rootGroup);
    const size=box.getSize(new THREE.Vector3());
    const center=box.getCenter(new THREE.Vector3());
    const maxDim=Math.max(size.x,size.y,size.z,1);
    const fov=camera.fov*Math.PI/180;
    const dist=maxDim/(2*Math.tan(fov/2))*1.35;
    const dir=new THREE.Vector3().subVectors(camera.position, controls.target).normalize();
    controls.target.copy(center);
    camera.position.copy(center.clone().add(dir.multiplyScalar(dist)));
    controls.update();
  }}
  function resetDefault(){{ setFront(); fitPreserveOrientation(); }}
  resetDefault();

  document.getElementById('front').onclick=()=>{{setFront(); fitPreserveOrientation();}};
  document.getElementById('iso').onclick=()=>{{setIso(); fitPreserveOrientation();}};
  document.getElementById('end').onclick=()=>{{setEnd(); fitPreserveOrientation();}};
  document.getElementById('fit').onclick=fitPreserveOrientation;
  document.getElementById('reset').onclick=resetDefault;

  const exact = D.tau_exact ? 'Sección circular · τ y γ exactas' : 'Torsión global · lectura geométrica';
  msg.textContent = exact + ' · φ real = ' + Number(D.twist_deg||0).toFixed(4) + '°';

  window.addEventListener('resize', ()=>{{
    camera.aspect=root.clientWidth/{height};
    camera.updateProjectionMatrix();
    renderer.setSize(root.clientWidth, {height});
  }});

  function animate(){{ controls.update(); renderer.render(scene, camera); requestAnimationFrame(animate); }}
  animate();
}}catch(e){{
  console.error(e); msg.textContent='Vista de respaldo · Three.js no disponible';
}}
</script>
'''
    components.html(html, height=height, scrolling=False)
