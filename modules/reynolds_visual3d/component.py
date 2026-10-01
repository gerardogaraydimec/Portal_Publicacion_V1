from __future__ import annotations

import json
import streamlit.components.v1 as components


def render_reynolds_3d(data: dict, height: int = 690, key: str | None = None) -> None:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    uid = (key or "reynolds3d").replace("-", "_").replace(" ", "_")
    template = r'''
<div id="__UID___root" style="height:__HEIGHT__px;border:1px solid #ded7cc;border-radius:14px;overflow:hidden;background:#202126;position:relative">
  <div style="position:absolute;z-index:5;left:14px;top:12px;background:#fff8edee;padding:9px 12px;border-radius:10px;font:13px system-ui;color:#25262a;line-height:1.35;max-width:48%">
    <b>Flujo interno 3D</b><br><span id="__UID___msg"></span>
  </div>
  <div style="position:absolute;z-index:5;right:12px;top:12px;display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end;max-width:48%">
    <button id="__UID___front">Frente</button><button id="__UID___iso">Isométrica</button><button id="__UID___section">Sección</button><button id="__UID___fit">Ajustar</button><button id="__UID___reset">Restablecer</button>
  </div>
  <div style="position:absolute;z-index:5;left:14px;bottom:12px;background:#202126dd;border:1px solid #55565b;color:#f7f1e7;padding:8px 10px;border-radius:9px;font:12px system-ui;line-height:1.4">
    <span style="color:#f28e1c">●</span> partículas · <span style="color:#f1d8b4">━</span> EGL · <span style="color:#d7d8da">━</span> HGL
  </div>
  <canvas id="__UID___fallback" width="1000" height="__HEIGHT__" style="width:100%;height:100%"></canvas>
</div>
<style>
#__UID___root button{border:1px solid #c8752d;background:#fff8ed;color:#292a2e;border-radius:8px;padding:7px 9px;cursor:pointer}
#__UID___root button:hover{background:#fff1dd}
</style>
<script type="module">
const D=__DATA__;
const root=document.getElementById('__UID___root');
const cv=document.getElementById('__UID___fallback');
const msg=document.getElementById('__UID___msg');
const H=__HEIGHT__;

function fallback(){
  const c=cv.getContext('2d'),W=cv.width,h=cv.height;
  c.fillStyle='#202126';c.fillRect(0,0,W,h);
  const x0=95,x1=W-95,y=h*.55,R=86;
  c.strokeStyle='#8d8f95';c.lineWidth=3;c.strokeRect(x0,y-R,x1-x0,2*R);
  const regime=D.regime_key||'laminar';
  for(let j=0;j<36;j++){
    const yy=y-R*.85+(j%12)*(1.7*R/11); const phase=(j*71)%100/100;
    c.strokeStyle=j%5===0?'#f28e1c':'#c8752d';c.lineWidth=1.5;
    c.beginPath();
    for(let k=0;k<90;k++){
      const t=k/89,x=x0+(x1-x0)*t;
      let off=0;if(regime==='transition')off=5*Math.sin(t*9+j);if(regime==='turbulent')off=11*Math.sin(t*15+j*.7)+5*Math.sin(t*31+j);
      const yp=yy+off;if(k===0)c.moveTo(x,yp);else c.lineTo(x,yp);
    }c.stroke();
  }
  c.strokeStyle='#f1d8b4';c.lineWidth=3;c.beginPath();c.moveTo(x0,y-R-75);c.lineTo(x1,y-R-75-(D.loss_total||0)*12);c.stroke();
  msg.textContent=(D.regime||'')+' · Re = '+Number(D.reynolds||0).toExponential(2)+' · vista de respaldo';
}
fallback();

try{
  const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm');
  const {OrbitControls}=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm');
  cv.style.display='none';
  const scene=new THREE.Scene();scene.background=new THREE.Color('#202126');
  const camera=new THREE.PerspectiveCamera(35,root.clientWidth/H,.01,200);
  const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.setSize(root.clientWidth,H);root.appendChild(renderer.domElement);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.zoomToCursor=true;controls.minDistance=2;controls.maxDistance=60;
  scene.add(new THREE.HemisphereLight('#fff8ec','#303136',2.0));const dl=new THREE.DirectionalLight('#ffffff',1.8);dl.position.set(4,7,8);scene.add(dl);

  const group=new THREE.Group();scene.add(group);
  const L=8.2,R=.72;
  const minorX=L*Math.max(0,Math.min(1,Number(D.minor_location_ratio||.7)));
  const probeX=L*Math.max(0,Math.min(1,Number(D.probe_ratio||.5)));

  const pipeMat=new THREE.MeshStandardMaterial({color:'#767980',transparent:true,opacity:.18,side:THREE.DoubleSide,roughness:.65,metalness:.05,depthWrite:false});
  const pipe=new THREE.Mesh(new THREE.CylinderGeometry(R,R,L,64,1,true),pipeMat);pipe.rotation.z=Math.PI/2;pipe.position.x=L/2;group.add(pipe);
  const edgeMat=new THREE.LineBasicMaterial({color:'#b9babd',transparent:true,opacity:.55});
  for(const x of [0,L]){const pts=[];for(let i=0;i<=72;i++){const a=2*Math.PI*i/72;pts.push(new THREE.Vector3(x,R*Math.sin(a),R*Math.cos(a)));}group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),edgeMat));}

  const axis=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0),new THREE.Vector3(L,0,0)]),new THREE.LineBasicMaterial({color:'#4e5055'}));group.add(axis);

  // Minor-loss element is schematic: its position is selected in the Streamlit page.
  if(Number(D.minor_k||0)>0){
    const ringMat=new THREE.MeshStandardMaterial({color:'#c8752d',transparent:true,opacity:.72});
    const r1=new THREE.Mesh(new THREE.TorusGeometry(R*.9,.045,12,48),ringMat);r1.rotation.y=Math.PI/2;r1.position.x=minorX-.08;group.add(r1);
    const r2=r1.clone();r2.position.x=minorX+.08;group.add(r2);
  }

  // Probe section.
  const disc=new THREE.Mesh(new THREE.CircleGeometry(R*.985,64),new THREE.MeshBasicMaterial({color:'#f28e1c',transparent:true,opacity:.07,side:THREE.DoubleSide}));disc.rotation.y=Math.PI/2;disc.position.x=probeX;group.add(disc);
  const probePts=[];for(let i=0;i<=72;i++){const a=2*Math.PI*i/72;probePts.push(new THREE.Vector3(probeX,R*Math.sin(a),R*Math.cos(a)));}
  group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(probePts),new THREE.LineBasicMaterial({color:'#f28e1c'})));

  // Velocity profile arrows at the probe plane.
  const regime=D.regime_key||'laminar';
  const arrowMat=new THREE.LineBasicMaterial({color:'#f28e1c',transparent:true,opacity:.9});
  for(let j=-5;j<=5;j++){
    const rr=Math.abs(j/5);let uf=1;
    if(regime==='laminar')uf=Math.max(0,2*(1-rr*rr));
    else if(regime==='turbulent')uf=1.22*Math.pow(Math.max(1-rr,0),1/7);
    else{const lam=Math.max(0,2*(1-rr*rr));const turb=1.22*Math.pow(Math.max(1-rr,0),1/7);uf=.45*lam+.55*turb;}
    const y=j*R*.16;const len=.2+.55*uf;
    group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(probeX,y,0),new THREE.Vector3(probeX+len,y,0)]),arrowMat));
  }

  // Deterministic particle field.
  function rnd(i){const x=Math.sin(i*12.9898+78.233)*43758.5453;return x-Math.floor(x);}
  const particleCount=regime==='laminar'?85:(regime==='transition'?110:145);
  const geom=new THREE.SphereGeometry(.025,7,7);const pmat=new THREE.MeshStandardMaterial({color:'#f28e1c',emissive:'#5d2e0a',emissiveIntensity:.25});
  const particles=[];
  for(let i=0;i<particleCount;i++){
    const rad=R*.82*Math.sqrt(rnd(i+1));const ang=2*Math.PI*rnd(i+31);const y=rad*Math.sin(ang),z=rad*Math.cos(ang);
    let sf=1;
    if(regime==='laminar')sf=.2+1.8*(1-(rad/(R*.85))**2);
    else if(regime==='transition')sf=.7+.55*rnd(i+81);
    else sf=.65+.85*rnd(i+81);
    const m=new THREE.Mesh(geom,pmat);group.add(m);
    particles.push({m,phase:rnd(i+110)*L,y,z,sf,a:rnd(i+180)*Math.PI*2,b:rnd(i+210)*Math.PI*2});
  }

  // Relative EGL / HGL. Vertical exaggeration is graphical.
  const loss=Math.max(Number(D.loss_total||0),1e-9);const vh=Math.max(Number(D.velocity_head||0),0);const scale=1.45/Math.max(loss+vh,.25);
  function energyY(x,isHGL){const distributed=Number(D.major_loss||0)*(x/L);const step=x>=minorX?Number(D.minor_loss||0):0;const e=-(distributed+step)-(isHGL?vh:0);return 1.25+e*scale;}
  function addEnergy(isHGL,color){const pts=[];const N=100;for(let i=0;i<=N;i++){const x=L*i/N;pts.push(new THREE.Vector3(x,energyY(x,isHGL),-1.0));}group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({color,linewidth:2})));}
  if(D.show_energy!==false){addEnergy(false,'#f1d8b4');addEnergy(true,'#d7d8da');}

  const grid=new THREE.GridHelper(11,11,0x494a4f,0x333438);grid.position.set(L/2,-1.35,0);scene.add(grid);

  let speedBase=.42+Math.min(1.6,Math.max(.15,Number(D.velocity_ms||0)/2.5));
  const clock=new THREE.Clock();
  function moveParticles(){const t=clock.getElapsedTime();for(const p of particles){let x=(p.phase+t*speedBase*p.sf)%L;let y=p.y,z=p.z;if(regime==='transition'){const a=.045*Math.sin(x*2.2+p.a+t*1.1);y+=a;z+=.035*Math.sin(x*2.7+p.b+t*.9);}else if(regime==='turbulent'){const a=.10*Math.sin(x*3.7+p.a+t*2.1)+.04*Math.sin(x*8+p.b-t*1.3);const b=.09*Math.cos(x*4.2+p.b-t*1.8)+.035*Math.sin(x*9+p.a+t*1.1);y+=a;z+=b;const rr=Math.hypot(y,z);if(rr>R*.86){const k=R*.86/rr;y*=k;z*=k;}}p.m.position.set(x,y,z);}}

  function setFront(){camera.position.set(L/2,.15,8.8);controls.target.set(L/2,0,0);controls.update();}
  function setIso(){camera.position.set(L/2+4.4,3.7,7.6);controls.target.set(L/2,0,0);controls.update();}
  function setSection(){camera.position.set(probeX+3.2,0,.01);controls.target.set(probeX,0,0);controls.update();}
  function fit(){const box=new THREE.Box3().setFromObject(group);const size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());const maxDim=Math.max(size.x,size.y,size.z,1);const fov=camera.fov*Math.PI/180;const dist=maxDim/(2*Math.tan(fov/2))*1.25;const dir=new THREE.Vector3().subVectors(camera.position,controls.target).normalize();controls.target.copy(center);camera.position.copy(center.clone().add(dir.multiplyScalar(dist)));controls.update();}
  function reset(){setFront();fit();}
  reset();
  document.getElementById('__UID___front').onclick=()=>{setFront();fit();};
  document.getElementById('__UID___iso').onclick=()=>{setIso();fit();};
  document.getElementById('__UID___section').onclick=()=>{setSection();};
  document.getElementById('__UID___fit').onclick=fit;
  document.getElementById('__UID___reset').onclick=reset;

  msg.textContent=(D.regime||'')+' · Re = '+Number(D.reynolds||0).toExponential(2)+' · f = '+Number(D.friction_factor||0).toFixed(4);
  window.addEventListener('resize',()=>{camera.aspect=root.clientWidth/H;camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,H);});
  function animate(){moveParticles();controls.update();renderer.render(scene,camera);requestAnimationFrame(animate);}animate();
}catch(e){console.error(e);msg.textContent=(D.regime||'')+' · vista de respaldo · Three.js no disponible';}
</script>
'''
    html = template.replace("__UID__", uid).replace("__HEIGHT__", str(int(height))).replace("__DATA__", payload)
    components.html(html, height=height, scrolling=False)
