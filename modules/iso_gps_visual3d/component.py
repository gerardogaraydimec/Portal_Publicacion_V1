from __future__ import annotations
import json
import streamlit.components.v1 as components


def render_iso_gps_3d(data: dict, height: int = 620):
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = f'''
<div id="isoGps3d" style="height:{height}px;border:1px solid #dfd8cc;border-radius:16px;overflow:hidden;background:#1f2128;position:relative">
  <div style="position:absolute;left:14px;top:12px;z-index:6;background:#fff8edee;color:#23252b;padding:10px 12px;border-radius:10px;font:13px system-ui;line-height:1.35">
    <b id="title">ISO GPS 3D</b><br><span id="status">Inicializando…</span>
  </div>
  <div style="position:absolute;right:12px;top:12px;z-index:6;display:flex;gap:6px;flex-wrap:wrap">
    <button id="front">Frente</button><button id="iso">Isométrica</button><button id="top">Superior</button><button id="fit">Ajustar</button>
  </div>
  <div id="legend" style="position:absolute;left:14px;bottom:12px;z-index:6;background:#1f2128dd;border:1px solid #535761;color:#f4ecdf;padding:9px 11px;border-radius:10px;font:12px system-ui;max-width:68%"></div>
  <canvas id="fallback" width="1200" height="{height}" style="width:100%;height:100%"></canvas>
</div>
<style>
#isoGps3d button{{border:1px solid #c8752d;background:#fff8ed;color:#2d2f34;border-radius:8px;padding:7px 9px;cursor:pointer}}
#isoGps3d button:hover{{background:#fff0da}}
</style>
<script type="module">
const D = {payload};
const root = document.getElementById('isoGps3d');
const fb = document.getElementById('fallback');
const statusEl = document.getElementById('status');
const legend = document.getElementById('legend');
function drawFallback() {{
  const c = fb.getContext('2d'), W = fb.width, H = fb.height;
  c.clearRect(0,0,W,H); c.fillStyle='#1f2128'; c.fillRect(0,0,W,H);
  c.fillStyle='#2d2f36'; c.fillRect(70,H-125,W-140,48);
  c.fillStyle='#e7ddcc'; c.fillRect(220,150,460,230);
  c.strokeStyle='#b7ab98'; c.lineWidth=2; c.strokeRect(220,150,460,230);
  c.fillStyle='rgba(90,154,255,0.18)'; c.fillRect(220,340,460,40);
  c.strokeStyle='#5a9aff'; c.lineWidth=3; c.beginPath(); c.moveTo(220,340); c.lineTo(680,340); c.stroke();
  c.fillStyle='#f28e1c'; c.fillRect(210,150,15,230); c.fillStyle='#f4ecdf'; c.font='600 28px system-ui'; c.fillText('B', 182,270);
  c.fillStyle='#49b37b'; c.fillRect(220,145,460,12); c.fillStyle='#f4ecdf'; c.fillText('C', 440,120);
  c.fillStyle='#e8e0d0'; c.beginPath(); c.arc(470,265,48,0,Math.PI*2); c.fill(); c.strokeStyle='#948a79'; c.stroke();
  c.strokeStyle='rgba(255,165,0,0.8)'; c.lineWidth=3;
  if (D.kind==='Posición' || D.kind==='Perpendicularidad') {{
    c.beginPath(); c.arc(470,265,58,0,Math.PI*2); c.stroke();
    c.beginPath(); c.moveTo(470+D.actual_dx*35,185); c.lineTo(470+D.actual_dx*35,345); c.stroke();
  }} else if (D.kind==='Planitud' || D.kind==='Paralelismo') {{
    c.beginPath(); c.moveTo(250,175); c.lineTo(650,175); c.stroke(); c.beginPath(); c.moveTo(250,175+Math.min(40,D.deviation_mm*120)); c.lineTo(650,175+Math.min(40,D.deviation_mm*120)); c.stroke();
  }} else {{
    c.beginPath(); c.arc(470,265,58,0,Math.PI*2); c.stroke(); c.beginPath(); c.arc(470,265,58-Math.min(20,D.deviation_mm*60),0,Math.PI*2); c.stroke();
  }}
  statusEl.textContent = 'Vista de respaldo · ' + D.kind;
  legend.innerHTML = 'Datums: <b>A</b> base, <b>B</b> cara lateral, <b>C</b> cara posterior. El color naranjo muestra la zona de tolerancia o el eje/superficie real.';
}}
drawFallback();
try {{
  const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm');
  const {{OrbitControls}} = await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm');

  const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:false}});
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  renderer.setSize(root.clientWidth, {height});
  renderer.domElement.style.width = '100%'; renderer.domElement.style.height='100%';
  root.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#1f2128');
  const camera = new THREE.PerspectiveCamera(32, root.clientWidth/{height}, 0.01, 100);
  const controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping=true; controls.dampingFactor=.08; controls.minDistance=2; controls.maxDistance=20;

  scene.add(new THREE.HemisphereLight('#fff6ea','#2d3037',2.1));
  const dl = new THREE.DirectionalLight('#ffffff',1.8); dl.position.set(5,6,8); scene.add(dl);
  const grid = new THREE.GridHelper(10,10,0x45474f,0x33353b); grid.position.y=-1.45; scene.add(grid);

  const matBlock = new THREE.MeshStandardMaterial({{color:'#e7ddcc', roughness:.72}});
  const matHole = new THREE.MeshStandardMaterial({{color:'#b9b2a6', roughness:.42, metalness:.15}});
  const matZone = new THREE.MeshStandardMaterial({{color:'#f28e1c', transparent:true, opacity:.28}});
  const lineOrange = new THREE.LineBasicMaterial({{color:0xf28e1c}});

  function makeTextSprite(text, fg='#f5ead7', bg='transparent') {{
    const cn = document.createElement('canvas'); cn.width=256; cn.height=96; const cx = cn.getContext('2d');
    if(bg!=='transparent'){{cx.fillStyle=bg; cx.fillRect(0,0,cn.width,cn.height);}}
    cx.font='700 40px system-ui'; cx.fillStyle=fg; cx.textAlign='center'; cx.fillText(text, cn.width/2, 58);
    const tex = new THREE.CanvasTexture(cn); const sp = new THREE.Sprite(new THREE.SpriteMaterial({{map:tex, transparent:true, depthTest:false}})); sp.scale.set(0.85,0.32,1); return sp;
  }}

  const g = new THREE.Group(); scene.add(g);
  const block = new THREE.Mesh(new THREE.BoxGeometry(4.6, 2.0, 3.0), matBlock); block.position.set(0,0,0); g.add(block);
  const edges = new THREE.LineSegments(new THREE.EdgesGeometry(block.geometry), new THREE.LineBasicMaterial({{color:0x9f978b}})); block.add(edges);

  const holeR = Math.max(0.18, (D.hole_d_mm||18)/50);
  const holeGeo = new THREE.CylinderGeometry(holeR,holeR,2.1,40,1,true);
  const hole = new THREE.Mesh(holeGeo, matHole); hole.rotation.x = Math.PI/2; hole.position.set(0.55,0,0); g.add(hole);

  // datums
  const planeA = new THREE.Mesh(new THREE.PlaneGeometry(4.7,3.1), new THREE.MeshBasicMaterial({{color:'#5a9aff', transparent:true, opacity:.18, side:THREE.DoubleSide}})); planeA.rotation.x=-Math.PI/2; planeA.position.set(0,-1.01,0); g.add(planeA);
  const planeB = new THREE.Mesh(new THREE.PlaneGeometry(2.05,3.1), new THREE.MeshBasicMaterial({{color:'#f28e1c', transparent:true, opacity:.15, side:THREE.DoubleSide}})); planeB.rotation.y=Math.PI/2; planeB.position.set(-2.31,0,0); g.add(planeB);
  const planeC = new THREE.Mesh(new THREE.PlaneGeometry(4.7,2.05), new THREE.MeshBasicMaterial({{color:'#49b37b', transparent:true, opacity:.15, side:THREE.DoubleSide}})); planeC.position.set(0,0,-1.51); g.add(planeC);
  const la = makeTextSprite('A','#d8ebff'); la.position.set(0,-1.3,1.7); g.add(la);
  const lb = makeTextSprite('B','#ffe7d2'); lb.position.set(-2.55,.8,0); g.add(lb);
  const lc = makeTextSprite('C','#d8ffe8'); lc.position.set(0,1.25,-1.72); g.add(lc);

  const centerX = D.basic_x || 0.55, centerZ = D.basic_y || 0.0;
  let zoneMesh = null, actualMesh = null, actualLine = null;
  function addAxisLine(x,z,color=0xff4d4d,y0=-1.0,y1=1.0) {{
    const pts = [new THREE.Vector3(x,y0,z), new THREE.Vector3(x,y1,z)];
    const ln = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({{color}}));
    g.add(ln); return ln;
  }}

  if (D.kind==='Posición' || D.kind==='Perpendicularidad') {{
    zoneMesh = new THREE.Mesh(new THREE.CylinderGeometry(D.tol_mm/20, D.tol_mm/20, 2.2, 48,1,true), matZone);
    zoneMesh.rotation.x = Math.PI/2; zoneMesh.position.set(centerX,0,centerZ); g.add(zoneMesh);
    actualLine = addAxisLine(centerX + (D.actual_dx||0), centerZ + (D.actual_dy||0), 0xff5d5d);
    if (D.kind==='Perpendicularidad') actualLine.rotation.z = (D.angular_deg||0)*Math.PI/180;
  }} else if (D.kind==='Planitud' || D.kind==='Paralelismo') {{
    const sep = Math.max(0.02, D.tol_mm/8);
    const p1 = new THREE.Mesh(new THREE.PlaneGeometry(3.9,2.25), new THREE.MeshBasicMaterial({{color:'#f28e1c', transparent:true, opacity:.22, side:THREE.DoubleSide}}));
    p1.position.set(0,1.02,0); g.add(p1); const p2 = p1.clone(); p2.position.y = 1.02-sep; g.add(p2); zoneMesh = new THREE.Group(); zoneMesh.add(p1); zoneMesh.add(p2);
    const surf = new THREE.Mesh(new THREE.PlaneGeometry(3.8,2.1,18,12), new THREE.MeshStandardMaterial({{color:'#d7c7b0', side:THREE.DoubleSide, wireframe:false}}));
    surf.rotation.x = -Math.PI/2; surf.position.set(0, 1.01-(D.deviation_mm/10), 0);
    if (surf.geometry.attributes.position) {{
      const pos = surf.geometry.attributes.position;
      for(let i=0;i<pos.count;i++){{
        const x=pos.getX(i), y=pos.getY(i);
        const wav = (D.kind==='Planitud'? 1:0.3) * (D.deviation_mm/8) * Math.sin(x*1.8) * Math.cos(y*1.4);
        pos.setZ(i, wav);
      }}
      pos.needsUpdate = true; surf.geometry.computeVertexNormals();
    }}
    actualMesh = surf; g.add(surf);
  }} else if (D.kind==='Circularidad') {{
    const tor = new THREE.Mesh(new THREE.TorusGeometry(holeR, Math.max(0.02,D.tol_mm/20), 24, 80), matZone); tor.rotation.y=Math.PI/2; tor.position.set(centerX,0,centerZ); zoneMesh=tor; g.add(tor);
    const pts=[]; for(let i=0;i<=160;i++){{const t=i/160*Math.PI*2; const r=holeR + 0.03*Math.sin(3*t) + (D.deviation_mm/28); pts.push(new THREE.Vector3(centerX, Math.cos(t)*r, Math.sin(t)*r)); }}
    actualLine = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), lineOrange); actualLine.rotation.y=Math.PI/2; g.add(actualLine);
  }} else if (D.kind==='Cilindricidad') {{
    zoneMesh = new THREE.Mesh(new THREE.CylinderGeometry(holeR + D.tol_mm/40, holeR + D.tol_mm/40, 2.1, 48,1,true), matZone); zoneMesh.rotation.x=Math.PI/2; zoneMesh.position.set(centerX,0,centerZ); g.add(zoneMesh);
    actualMesh = new THREE.Mesh(new THREE.CylinderGeometry(holeR + D.deviation_mm/35, holeR + D.deviation_mm/25, 2.05, 36, 10, true), new THREE.MeshStandardMaterial({{color:'#d4c2a5', transparent:true, opacity:.75, wireframe:true}})); actualMesh.rotation.x=Math.PI/2; actualMesh.position.set(centerX,0,centerZ); g.add(actualMesh);
  }}

  const datumText = (D.kind==='Planitud' || D.kind==='Circularidad' || D.kind==='Cilindricidad') ? 'Sin datums' : 'Datums A, B y C / o A según la tolerancia';
  legend.innerHTML = `Pieza base con datums <b>A</b>, <b>B</b>, <b>C</b>. Zona naranjo = <b>zona de tolerancia</b>. Elemento rojo/naranjo = <b>elemento real</b>. ${{D.pass_ok ? 'Resultado: CUMPLE' : 'Resultado: NO CUMPLE'}}`;

  function front() {{ camera.position.set(0.4,0.8,10); controls.target.set(0,0,0); controls.update(); }}
  function iso() {{ camera.position.set(6.2,4.2,7.6); controls.target.set(0,0,0); controls.update(); }}
  function top() {{ camera.position.set(0.2,9.0,0.01); controls.target.set(0,0,0); controls.update(); }}
  function fit() {{ const b = new THREE.Box3().setFromObject(g), sz=b.getSize(new THREE.Vector3()), ct=b.getCenter(new THREE.Vector3()), md=Math.max(sz.x,sz.y,sz.z,1), f=camera.fov*Math.PI/180, dist=md/(2*Math.tan(f/2))*1.35, dir=new THREE.Vector3().subVectors(camera.position, controls.target).normalize(); controls.target.copy(ct); camera.position.copy(ct.clone().add(dir.multiplyScalar(dist))); controls.update(); }}
  document.getElementById('front').onclick=()=>{{front(); fit();}}; document.getElementById('iso').onclick=()=>{{iso(); fit();}}; document.getElementById('top').onclick=()=>{{top(); fit();}}; document.getElementById('fit').onclick=fit;
  iso(); fit();
  statusEl.textContent = `${{D.kind}} · Tolerancia = ${{D.tol_mm.toFixed(3)}} mm · Desviación = ${{D.deviation_mm.toFixed(3)}} mm`;

  let firstFrame=false;
  function animate() {{ controls.update(); renderer.render(scene,camera); if(!firstFrame){{firstFrame=true; fb.style.display='none';}} requestAnimationFrame(animate); }}
  animate();
  window.addEventListener('resize', ()=>{{ camera.aspect = root.clientWidth/{height}; camera.updateProjectionMatrix(); renderer.setSize(root.clientWidth,{height}); }});
}} catch(e) {{
  console.error(e);
  statusEl.textContent = 'Vista de respaldo · Three.js no disponible';
}}
</script>
'''
    components.html(html, height=height, scrolling=False)
