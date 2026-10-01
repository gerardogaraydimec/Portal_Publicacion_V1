from __future__ import annotations
import json
import streamlit.components.v1 as components


def render_vibration_2dof_3d(data: dict, height: int = 640):
    d = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = f'''
<div id="v2d" style="height:{height}px;border:1px solid #ded7cc;border-radius:14px;overflow:hidden;background:#202126;position:relative">
  <div style="position:absolute;z-index:5;left:13px;top:11px;background:#fff8edee;padding:8px 11px;border-radius:10px;font:13px system-ui;color:#25262a;line-height:1.35">
    <b id="title">2GDL · resortes y amortiguadores</b><br><span id="msg"></span>
  </div>
  <div id="legend" style="position:absolute;z-index:5;left:13px;bottom:11px;background:#202126e6;border:1px solid #565860;color:#f5ead7;padding:8px 10px;border-radius:9px;font:12px system-ui;max-width:56%"></div>
  <div style="position:absolute;z-index:5;right:11px;top:11px;display:flex;gap:5px;flex-wrap:wrap">
    <button id="play">Pausa</button><button id="front">Frente</button><button id="iso">Isométrica</button><button id="top">Superior</button><button id="fit">Ajustar</button><button id="reset">Restablecer</button>
  </div>
  <canvas id="fb" width="1000" height="{height}" style="width:100%;height:100%"></canvas>
</div>
<style>
#v2d button{{border:1px solid #c8752d;background:#fff8ed;color:#292a2e;border-radius:8px;padding:7px 9px;cursor:pointer}}
#v2d button:hover{{background:#fff1dd}}
</style>
<script type="module">
const D = {d};
const root=document.getElementById('v2d'), cv=document.getElementById('fb'), msg=document.getElementById('msg'), legend=document.getElementById('legend');
let paused=false;
function fallback(){{
  const c=cv.getContext('2d'),W=cv.width,H=cv.height;
  c.fillStyle='#202126'; c.fillRect(0,0,W,H);
  c.fillStyle='#c8752d'; c.fillRect(70,H/2-120,28,240);
  c.fillStyle='#8a8d94'; c.fillRect(98,H/2-5,180,10); c.fillRect(440,H/2-5,160,10);
  c.strokeStyle='#d9c8ae'; c.lineWidth=4;
  c.beginPath(); c.moveTo(98,H/2-48); for(let i=0;i<12;i++){{c.lineTo(118+i*16,H/2-48+(i%2?18:-18));}} c.lineTo(278,H/2-48); c.stroke();
  c.beginPath(); c.moveTo(278,H/2-48); c.lineTo(440,H/2-48); for(let i=0;i<10;i++){{c.lineTo(456+i*16,H/2-48+(i%2?18:-18));}} c.lineTo(600,H/2-48); c.stroke();
  c.strokeStyle='#8f939b'; c.lineWidth=5; c.beginPath(); c.moveTo(98,H/2+42); c.lineTo(238,H/2+42); c.stroke(); c.strokeRect(238,H/2+23,42,38); c.beginPath(); c.moveTo(280,H/2+42); c.lineTo(440,H/2+42); c.stroke(); c.strokeRect(440,H/2+23,42,38); c.beginPath(); c.moveTo(482,H/2+42); c.lineTo(600,H/2+42); c.stroke();
  c.fillStyle='#e8dfcf'; c.fillRect(278,H/2-85,160,120); c.fillRect(600,H/2-70,130,100);
  c.fillStyle='#f5ead7'; c.font='15px system-ui';
  c.fillText('k₁',185,H/2-72); c.fillText('c₁',185,H/2+85); c.fillText('k₂',518,H/2-72); c.fillText('c₂',518,H/2+85); c.fillText('m₁',346,H/2+60); c.fillText('m₂',650,H/2+60);
  c.strokeStyle='#f28e1c'; c.lineWidth=6; c.beginPath(); c.moveTo(350,H/2-115); c.lineTo(430,H/2-115); c.stroke();
  c.beginPath(); c.moveTo(438,H/2-115); c.lineTo(418,H/2-127); c.lineTo(418,H/2-103); c.closePath(); c.fillStyle='#f28e1c'; c.fill();
  msg.textContent='Vista de respaldo';
  legend.textContent='Arriba: resortes k₁ y k₂. Abajo: amortiguadores c₁ y c₂. La fuerza F(t) actúa sobre m₁.';
}}
fallback();
try {{
  const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm');
  const {{OrbitControls}} = await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm');
  cv.style.display='none';

  const scene = new THREE.Scene(); scene.background = new THREE.Color('#202126');
  const camera = new THREE.PerspectiveCamera(32, root.clientWidth/{height}, 0.01, 120);
  const renderer = new THREE.WebGLRenderer({{antialias:true}}); renderer.setPixelRatio(Math.min(devicePixelRatio||1,2)); renderer.setSize(root.clientWidth,{height}); root.appendChild(renderer.domElement);
  const controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping=true; controls.dampingFactor=.08; controls.zoomToCursor=true; controls.minDistance=3; controls.maxDistance=30;

  scene.add(new THREE.HemisphereLight('#fff8ec','#303136',2.25));
  const dl = new THREE.DirectionalLight('#ffffff', 2.0); dl.position.set(6,7,8); scene.add(dl);
  const grid = new THREE.GridHelper(12,12,0x48494e,0x323338); grid.position.set(0,-1.55,0); scene.add(grid);

  const G = new THREE.Group(); scene.add(G);
  const matCopper = new THREE.MeshStandardMaterial({{color:'#c8752d', roughness:.78}});
  const matMass = new THREE.MeshStandardMaterial({{color:'#e7ddcc', roughness:.62}});
  const matMetal = new THREE.MeshStandardMaterial({{color:'#8a8d94', metalness:.35, roughness:.45}});
  const matRod = new THREE.MeshStandardMaterial({{color:'#d6d7da', metalness:.55, roughness:.28}});

  const wall = new THREE.Mesh(new THREE.BoxGeometry(.30,2.95,2.35), matCopper); wall.position.set(-4.15,0,0); G.add(wall);
  const floor = new THREE.Mesh(new THREE.BoxGeometry(8.6,.18,2.5), new THREE.MeshStandardMaterial({{color:'#2d2f36', roughness:.92}})); floor.position.set(.2,-1.47,0); G.add(floor);
  const rail = new THREE.Mesh(new THREE.BoxGeometry(7.7,.08,.12), matMetal); rail.position.set(.15,-.88,0); G.add(rail);
  const plusX = new THREE.ArrowHelper(new THREE.Vector3(1,0,0), new THREE.Vector3(-.65,-1.18,-.05), 1.0, 0xc8752d, .16, .09); G.add(plusX);

  function createMass(w,h,d,labelText) {{
    const g = new THREE.Group();
    const body = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), matMass); g.add(body);
    g.add(new THREE.LineSegments(new THREE.EdgesGeometry(body.geometry), new THREE.LineBasicMaterial({{color:0x9f978b}})));
    const slide = new THREE.Mesh(new THREE.BoxGeometry(w*.74,.07,d*.82), matMetal); slide.position.y = -h/2-.11; g.add(slide);
    const lbl = makeLabel(labelText, '#ffffff', '#202126'); lbl.position.set(0, h/2+.28, 0); g.add(lbl);
    G.add(g); return g;
  }}

  function makeLabel(text, fg, bg='transparent') {{
    const cn = document.createElement('canvas'); cn.width=320; cn.height=96; const cx = cn.getContext('2d');
    if(bg!=='transparent'){{ cx.fillStyle=bg; cx.fillRect(0,0,cn.width,cn.height); }}
    cx.font='600 42px system-ui'; cx.fillStyle=fg; cx.textAlign='center'; cx.fillText(text, cn.width/2, 58);
    const tex = new THREE.CanvasTexture(cn); const sp = new THREE.Sprite(new THREE.SpriteMaterial({{map:tex,transparent:true,depthTest:false}})); sp.scale.set(1.25,.38,1); return sp;
  }}

  function createSpring(color='#d9c8ae') {{
    const line = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({{color}})); G.add(line); return line;
  }}
  function updateSpring(line, xa, xb, y, z) {{
    const pts=[]; const N=180; const dx=xb-xa;
    for(let i=0;i<=N;i++){{
      const q=i/N; const x=xa+dx*q; let yy=y, zz=z;
      if(i>5 && i<N-5){{ yy += .18*Math.sin(22*Math.PI*q); zz += .05*Math.cos(22*Math.PI*q); }}
      pts.push(new THREE.Vector3(x,yy,zz));
    }}
    line.geometry.dispose(); line.geometry = new THREE.BufferGeometry().setFromPoints(pts);
  }}

  function createDamper() {{
    const g = new THREE.Group();
    const leftRod = new THREE.Mesh(new THREE.CylinderGeometry(.03,.03,.55,14), matRod); leftRod.rotation.z=Math.PI/2; leftRod.position.x=-.42; g.add(leftRod);
    const box = new THREE.Mesh(new THREE.BoxGeometry(.28,.18,.18), matMetal); g.add(box);
    const piston = new THREE.Mesh(new THREE.CylinderGeometry(.05,.05,.50,18), matRod); piston.rotation.z=Math.PI/2; piston.position.x=.18; g.add(piston);
    const rightRod = new THREE.Mesh(new THREE.CylinderGeometry(.03,.03,.55,14), matRod); rightRod.rotation.z=Math.PI/2; rightRod.position.x=.62; g.add(rightRod);
    G.add(g); return g;
  }}
  function updateDamper(g, xa, xb, y, z) {{
    const len = Math.max(.70, xb-xa);
    g.position.set((xa+xb)/2, y, z);
    const leftRod = g.children[0], box = g.children[1], piston = g.children[2], rightRod = g.children[3];
    const lc = Math.max(.15, len*0.28), rc = Math.max(.18, len*0.36), pc = Math.max(.10, len*0.18);
    leftRod.scale.y = lc/.55; leftRod.position.x = -len/2 + lc/2;
    box.position.x = -len*0.08; box.scale.x = Math.max(.75, len*0.16/.28);
    piston.scale.y = pc/.50; piston.position.x = box.position.x + box.scale.x*.14 + pc/2;
    rightRod.scale.y = rc/.55; rightRod.position.x = len/2 - rc/2;
  }}

  const M1 = createMass(1.45,1.28,1.12,'m₁');
  const M2 = createMass(1.18,1.05,1.00,'m₂');
  const spring1 = createSpring(); const spring2 = createSpring();
  const damper1 = createDamper(); const damper2 = createDamper();
  const k1Lbl = makeLabel('k₁', '#f5ead7'); const c1Lbl = makeLabel('c₁', '#c8ccd3'); const k2Lbl = makeLabel('k₂', '#f5ead7'); const c2Lbl = makeLabel('c₂', '#c8ccd3');
  k1Lbl.scale.set(.9,.28,1); c1Lbl.scale.set(.9,.28,1); k2Lbl.scale.set(.9,.28,1); c2Lbl.scale.set(.9,.28,1);
  G.add(k1Lbl); G.add(c1Lbl); G.add(k2Lbl); G.add(c2Lbl);

  const forceArrow = new THREE.ArrowHelper(new THREE.Vector3(1,0,0), new THREE.Vector3(), 1, 0xf28e1c, .22, .12); G.add(forceArrow);
  const x1Arrow = new THREE.ArrowHelper(new THREE.Vector3(1,0,0), new THREE.Vector3(), 1, 0xf5ead7, .18, .10); G.add(x1Arrow);
  const x2Arrow = new THREE.ArrowHelper(new THREE.Vector3(1,0,0), new THREE.Vector3(), 1, 0xb6bcc5, .18, .10); G.add(x2Arrow);
  const fxLbl = makeLabel('F(t)', '#f28e1c'); fxLbl.scale.set(1.0,.30,1); G.add(fxLbl);
  const x1Lbl = makeLabel('x₁', '#f5ead7'); x1Lbl.scale.set(.75,.24,1); G.add(x1Lbl);
  const x2Lbl = makeLabel('x₂', '#b6bcc5'); x2Lbl.scale.set(.75,.24,1); G.add(x2Lbl);

  const eq1 = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-.25,-1.18,-1.0), new THREE.Vector3(-.25,1.1,-1.0)]), new THREE.LineDashedMaterial({{color:0x8f939b,dashSize:.12,gapSize:.08}})); eq1.computeLineDistances(); G.add(eq1);
  const eq2 = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(2.85,-1.18,-1.0), new THREE.Vector3(2.85,1.1,-1.0)]), new THREE.LineDashedMaterial({{color:0x8f939b,dashSize:.12,gapSize:.08}})); eq2.computeLineDistances(); G.add(eq2);

  const t = D.t || [], x1 = D.x1 || [], x2 = D.x2 || [], ff = D.force || [];
  const dur = Math.max(D.duration || 6, 1e-6), speed = D.speed || 1, amp = D.visual_amp || 1;
  const xmax = Math.max(...x1.map(v=>Math.abs(v)), ...x2.map(v=>Math.abs(v)), 1e-9);
  const fmax = Math.max(...ff.map(v=>Math.abs(v)), 1e-9);
  let tm=0, last=performance.now();
  function sample(arr, tt) {{ if(!arr.length) return 0; const u=((tt%dur)/dur)*(arr.length-1); const i=Math.floor(u), j=Math.min(arr.length-1,i+1), q=u-i; return arr[i]*(1-q)+arr[j]*q; }}
  function setArrow(ar, lbl, val, norm, px, py, pz) {{
    const s = Math.sign(val)||1; const len = .18 + 1.00*Math.min(1, Math.abs(val)/Math.max(norm,1e-12));
    ar.position.set(px,py,pz); ar.setDirection(new THREE.Vector3(s,0,0)); ar.setLength(len,.18,.10);
    ar.visible = Math.abs(val) > norm*0.015; lbl.visible = ar.visible; lbl.position.set(px + s*(len*.55), py+.22, pz);
  }}
  function update(dt) {{
    if(!paused) tm += dt*speed;
    const a = sample(x1,tm), b = sample(x2,tm), fv = sample(ff,tm);
    const px1 = -.25 + (a/xmax)*1.10*amp;
    const px2 =  2.85 + (b/xmax)*1.10*amp;
    M1.position.set(px1,0,0); M2.position.set(px2,0,0);
    updateSpring(spring1, -3.98, px1-.78, .52, 0);
    updateDamper(damper1, -3.98, px1-.78, -.25, 0);
    updateSpring(spring2, px1+.78, px2-.64, .52, 0);
    updateDamper(damper2, px1+.78, px2-.64, -.25, 0);
    k1Lbl.position.set((-3.98 + px1-.78)/2, .92, .16); c1Lbl.position.set((-3.98 + px1-.78)/2, -.64, .16);
    k2Lbl.position.set((px1+.78 + px2-.64)/2, .92, .16); c2Lbl.position.set((px1+.78 + px2-.64)/2, -.64, .16);
    forceArrow.visible = D.show_force !== false; fxLbl.visible = D.show_force !== false;
    if(D.show_force !== false) setArrow(forceArrow, fxLbl, fv, fmax, px1, 1.02, 0);
    setArrow(x1Arrow, x1Lbl, a, xmax, px1, -.98, .18);
    setArrow(x2Arrow, x2Lbl, b, xmax, px2, -.98, -.18);
    legend.innerHTML = `Arriba: <b>resortes</b> k₁ y k₂ · Abajo: <b>amortiguadores</b> c₁ y c₂ · Líneas punteadas: posición de equilibrio.<br>t = ${(tm%dur).toFixed(2)} s · x₁ = ${(a*1000).toFixed(2)} mm · x₂ = ${(b*1000).toFixed(2)} mm`;
  }}

  function front() {{ camera.position.set(-.2,.05,10.2); controls.target.set(.6,-.05,0); controls.update(); }}
  function iso() {{ camera.position.set(5.8,3.9,8.0); controls.target.set(.6,-.05,0); controls.update(); }}
  function top() {{ camera.position.set(.6,8.2,.01); controls.target.set(.6,-.05,0); controls.update(); }}
  function fit() {{ const b = new THREE.Box3().setFromObject(G), sz=b.getSize(new THREE.Vector3()), ct=b.getCenter(new THREE.Vector3()), md=Math.max(sz.x,sz.y,sz.z,1), f=camera.fov*Math.PI/180, dist=md/(2*Math.tan(f/2))*1.25, dir=new THREE.Vector3().subVectors(camera.position,controls.target).normalize(); controls.target.copy(ct); camera.position.copy(ct.clone().add(dir.multiplyScalar(dist))); controls.update(); }}
  function reset() {{ front(); fit(); }}
  reset();
  document.getElementById('front').onclick=()=>{{front(); fit();}};
  document.getElementById('iso').onclick=()=>{{iso(); fit();}};
  document.getElementById('top').onclick=()=>{{top(); fit();}};
  document.getElementById('fit').onclick=fit;
  document.getElementById('reset').onclick=reset;
  document.getElementById('play').onclick=(e)=>{{ paused=!paused; e.target.textContent=paused?'Reproducir':'Pausa'; }};
  msg.textContent = D.label || 'Sistema 2GDL';

  window.addEventListener('resize', ()=>{{ camera.aspect=root.clientWidth/{height}; camera.updateProjectionMatrix(); renderer.setSize(root.clientWidth,{height}); }});
  function loop(now) {{ const dt=Math.min(.05,(now-last)/1000); last=now; update(dt); controls.update(); renderer.render(scene,camera); requestAnimationFrame(loop); }}
  requestAnimationFrame(loop);
}} catch(e) {{
  console.error(e); msg.textContent='Vista de respaldo · Three.js no disponible';
}}
</script>
'''
    components.html(html, height=height, scrolling=False)
