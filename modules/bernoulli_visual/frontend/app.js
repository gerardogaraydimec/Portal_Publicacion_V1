import {NativeRenderer,ThreeRenderer,CanvasRenderer,geometryData,pointAt,project,clamp} from './renderers.js?v=gg31';
import {BRAND,rgb,gradient} from './palette.js?v=gg31';
const $=id=>document.getElementById(id),host=$('canvas-host'),wrap=$('scene-wrap');
const fmt=(v,n=2)=>(Math.abs(Number(v))<.5*Math.pow(10,-n)?0:Number(v)).toLocaleString('es-CL',{minimumFractionDigits:n,maximumFractionDigits:n});
const N=360,positions=new Float32Array(N*3),colors=new Float32Array(N*3);
let seed=619;const rand=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};
const tracers=Array.from({length:N},()=>({phase:rand(),radius:Math.sqrt(rand())*.86,angle:rand()*Math.PI*2}));
let data=null,geom=null,renderer=null,width=1,height=1,elapsed=0,last=performance.now(),visible=true;
let colorMode='velocity',cut=true,playing=!matchMedia('(prefers-reduced-motion: reduce)').matches,playback=1,probe=0;
const camera={yaw:.38,pitch:.22,dist:13};let threePromise=null,threeModule=null;
const isStreamlit=window.parent!==window;
const send=(type,args={})=>{if(isStreamlit)window.parent.postMessage({isStreamlitMessage:true,type,...args},'*');};
function heightToParent(){send('streamlit:setFrameHeight',{height:Math.ceil($('lab').getBoundingClientRect().height)+3});}
function resize(){const oldFit=clamp(17/(width/height),10.5,22);const r=wrap.getBoundingClientRect();width=Math.max(1,r.width);height=Math.max(1,r.height);const newFit=clamp(17/(width/height),10.5,22);if(renderer)camera.dist=clamp(camera.dist*newFit/oldFit,7,35);renderer?.resize(width,height);heightToParent();}
function resetCamera(){camera.yaw=.38;camera.pitch=.22;camera.dist=clamp(17/(width/height),10.5,22);$('view').textContent='Vista lateral';}
function buildRenderer(T=null){
  let next;
  if(T){try{next=new ThreeRenderer(host,T);}catch(e){console.info('Three.js no disponible en este dispositivo.',String(e));return;}}
  else{try{next=new NativeRenderer(host);}catch(e){next=new CanvasRenderer(host);}}
  if(data)next.setData(data,cut);next.resize(width,height);renderer?.dispose();renderer=next;$('renderer-label').textContent=renderer.label;
  if(renderer instanceof CanvasRenderer){$('scene-note').hidden=false;$('scene-note').textContent='Vista 3D liviana: este dispositivo no habilit\u00f3 WebGL.';$('view').disabled=false;}
  else{$('scene-note').hidden=true;$('view').disabled=false;}
}
async function loadThree(){
  if(threePromise)return threePromise;
  threePromise=(async()=>{
    const urls=[];
    if(data?.local_three)urls.push('./vendor/three.module.js');
    if(!window.BERNOULLI_DISABLE_CDN){urls.push('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js','https://unpkg.com/three@0.160.0/build/three.module.js');}
    for(const url of urls){try{const mod=await Promise.race([import(url),new Promise((_,reject)=>setTimeout(()=>reject(Error('Tiempo de espera')),7000))]);if(mod.WebGLRenderer){threeModule=mod;buildRenderer(mod);return;}}catch(e){console.info('Se conserva el visor compatible.',url);}}
  })();
  return threePromise;
}
function heat(t,mode){t=clamp(t,0,1);const stops=BRAND[mode].map(rgb);const u=t*2,i=Math.min(1,Math.floor(u)),f=u-i;return stops[i].map((a,j)=>a+(stops[i+1][j]-a)*f);}
function limits(){const v=colorMode==='velocity'?data.velocity_ms:data.pressure_Pa.map(p=>p/1000);return [Math.min(...v),Math.max(...v)];}
function updateLegend(){if(!data)return;const [a,b]=limits();$('legend-title').textContent=colorMode==='velocity'?'VELOCIDAD MEDIA [m/s]':'PRESI\u00d3N MANOM\u00c9TRICA [kPa]';$('legend-min').textContent=fmt(a);$('legend-max').textContent=fmt(b);$('legend-gradient').style.background=gradient(colorMode);for(const id of ['velocity','pressure']){$(id).classList.toggle('active',id===colorMode);$(id).setAttribute('aria-pressed',String(id===colorMode));}}
function updateProbe(){
  if(!data)return;probe=clamp(Math.round(probe),0,data.s.length-1);$('probe').value=probe;$('probe-pos').textContent=fmt(data.s[probe]*100,0)+' %';
  const one=probe===data.station1_index,two=probe===data.station2_index;
  $('probe-title').textContent=one?'Secci\u00f3n 1':two?data.station2_name:'Corte de inspecci\u00f3n';
  $('station1').classList.toggle('active',one);$('station2').classList.toggle('active',two);
  $('diameter').textContent=fmt(data.diameter_m[probe]*1000,1);$('speed').textContent=fmt(data.velocity_ms[probe],2);$('pressure-value').textContent=fmt(data.pressure_Pa[probe]/1000,2);$('elevation').textContent=fmt(data.z_m[probe],2);
  if(!data.Q_m3s)$('probe-tip').textContent='Q = 0: los trazadores est\u00e1n detenidos. El balance se reduce a presi\u00f3n y cota.';
  else if(data.geometry==='venturi')$('probe-tip').textContent='2 es la garganta. El difusor ilustrativo recupera presi\u00f3n sin p\u00e9rdidas.';
  else $('probe-tip').textContent='Inspecciona el \u00e1rea, la velocidad y la presi\u00f3n sin cambiar el caudal calculado.';
}
function updateEnergy(){
  const ids=[data.station1_index,data.station2_index],keys=['pressure_head_m','velocity_head_m','z_m'];
  const vals=ids.flatMap(i=>keys.map(k=>data[k][i]));let lo=Math.min(0,...vals),hi=Math.max(0,...vals);if(hi-lo<1e-12)hi=lo+1;const zero=100*(0-lo)/(hi-lo);
  const labels=['p / (\u03c1g)','V\u00b2 / (2g)','z'],col=BRAND.energy;
  $('energy-grid').innerHTML=ids.map((i,j)=>`<div class="energy-card"><div class="heading"><strong>${j===0?'Secci\u00f3n 1':data.station2_name}</strong><span>H = ${fmt(data.egl_m[i],3)} m</span></div>${keys.map((k,t)=>{const v=data[k][i],pos=100*(v-lo)/(hi-lo),left=Math.min(pos,zero),wid=Math.abs(pos-zero);return `<div class="energy-row"><span style="color:${BRAND.energyText[t]}">${labels[t]}</span><div class="energy-track"><i class="zero" style="left:${zero}%"></i><i class="bar" data-energy="${t}" style="background-color:${col[t]};left:${left}%;width:${wid}%"></i></div><span class="val">${fmt(v,3)}</span></div>`;}).join('')}</div>`).join('');
  $('balance').textContent='H\u2081 = H\u2082';
}
function updatePlay(){const allowed=data?.Q_m3s>0&&data?.animation_allowed!==false;$('play').disabled=!allowed;$('play').textContent=!allowed?'Sin animaci\u00f3n':playing?'Pausar':'Reproducir';$('play').setAttribute('aria-label',playing?'Pausar animaci\u00f3n':'Reproducir animaci\u00f3n');}
function applyData(payload){
  if(!payload||payload.schema!==1||!Array.isArray(payload.s))return;
  const initial=!data;data=payload;geom=geometryData(data);elapsed=0;probe=data.station2_index;
  $('case-title').textContent=data.case_name||'Continuidad y Bernoulli';$('flow').textContent=fmt(data.Q_m3s*1000,2)+' L/s';$('station2').textContent=data.station2_name;$('label2').title=data.station2_name;
  $('probe').max=data.s.length-1;$('assumptions').textContent=data.visual_assumption;$('time-note').textContent=data.duration_s>0?'Tr\u00e1nsito ilustrativo: '+fmt(data.duration_s,2)+' s':'Fluido en reposo';
  resize();if(initial)resetCamera();if(!renderer)buildRenderer();else renderer.setData(data,cut);
  updateProbe();updateLegend();updateEnergy();updatePlay();heightToParent();loadThree();
}
function sampleIndex(t){let lo=0,hi=data.travel_s.length-1;while(hi-lo>1){const m=(lo+hi)>>1;if(data.travel_s[m]<=t)lo=m;else hi=m;}const d=data.travel_s[hi]-data.travel_s[lo];return [lo,hi,d>0?(t-data.travel_s[lo])/d:0];}
function updateParticles(){if(!data)return;const [low,high]=limits();const dur=data.duration_s;
  for(let n=0;n<N;n++){const tr=tracers[n];let i,j,f;if(dur>0){const t=((tr.phase*dur+elapsed)%dur+dur)%dur;[i,j,f]=sampleIndex(t);}else{i=Math.min(data.s.length-2,Math.floor(tr.phase*(data.s.length-1)));j=i+1;f=0;}
    const a=pointAt(geom,i,tr.angle,tr.radius),b=pointAt(geom,j,tr.angle,tr.radius);for(let k=0;k<3;k++)positions[n*3+k]=a[k]+(b[k]-a[k])*f;
    const arr=colorMode==='velocity'?data.velocity_ms:data.pressure_Pa;let val=arr[i]+(arr[j]-arr[i])*f;if(colorMode==='pressure')val/=1000;const rgb=heat(high>low?(val-low)/(high-low):.5,colorMode);colors.set(rgb,n*3);
  }
}
function updateLabels(){if(!geom||!renderer)return;for(const [id,i] of [['label1',data.station1_index],['label2',data.station2_index]]){const c=geom.centers[i],v=geom.normals[i],rr=geom.radii[i]+.52,p=[c[0]+v[0]*rr,c[1]+v[1]*rr,0];const r=project(p,camera,width,height);$(id).style.left=r[0]+'px';$(id).style.top=r[1]+'px';$(id).hidden=!r[2];}}
function animate(now){const dt=Math.min((now-last)/1000,.05);last=now;if(data&&renderer&&visible&&!document.hidden){if(playing&&data.Q_m3s>0&&data.animation_allowed!==false)elapsed+=dt*playback;updateParticles();renderer.draw(positions,colors,camera,probe);updateLabels();}requestAnimationFrame(animate);}
$('velocity').onclick=()=>{colorMode='velocity';updateLegend();};$('pressure').onclick=()=>{colorMode='pressure';updateLegend();};$('play').onclick=()=>{playing=!playing;updatePlay();};$('cut').onclick=()=>{cut=!cut;$('cut').classList.toggle('active',cut);$('cut').setAttribute('aria-pressed',String(cut));$('cut').textContent=cut?'Corte abierto':'Tubo completo';if(data)renderer?.setData(data,cut);};
$('view').onclick=()=>{if(camera.pitch===.02&&camera.yaw===0){resetCamera();}else{camera.yaw=0;camera.pitch=.02;camera.dist=clamp(17/(width/height),10.5,22);$('view').textContent='Vista isom\u00e9trica';}};$('reset').onclick=resetCamera;
for(const id of ['station1','label1'])$(id).onclick=()=>{if(data){probe=data.station1_index;updateProbe();}};for(const id of ['station2','label2'])$(id).onclick=()=>{if(data){probe=data.station2_index;updateProbe();}};
$('probe').oninput=e=>{probe=Number(e.target.value);updateProbe();};$('playback').oninput=e=>{playback=Number(e.target.value);$('playback-value').textContent=fmt(playback,1)+'\u00d7';};
let drag=null;host.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY];host.setPointerCapture(e.pointerId);});host.addEventListener('pointermove',e=>{if(!drag)return;camera.yaw-=(e.clientX-drag[0])*.006;camera.pitch=clamp(camera.pitch+(e.clientY-drag[1])*.004,-.7,.9);drag=[e.clientX,e.clientY];});for(const evt of ['pointerup','pointercancel'])host.addEventListener(evt,()=>drag=null);host.addEventListener('wheel',e=>{e.preventDefault();camera.dist=clamp(camera.dist*(1+Math.sign(e.deltaY)*.075),7,35);},{passive:false});
new ResizeObserver(resize).observe(wrap);new ResizeObserver(heightToParent).observe($('lab'));new IntersectionObserver(entries=>visible=entries[0].isIntersecting).observe($('lab'));
window.addEventListener('message',event=>{if(event.source===window.parent&&event.data?.type==='streamlit:render')applyData(event.data.args?.data);});
window.__BERNOULLI_TEST__={get state(){return {ready:!!data,mode:renderer?.label,color:colorMode,playing,probe,elapsed,point:Array.from(positions.slice(0,3)),pressure: data?.pressure_Pa[probe],velocity:data?.velocity_ms[probe]};},applyData};
send('streamlit:componentReady',{apiVersion:1});heightToParent();if(window.BERNOULLI_DEMO)applyData(window.BERNOULLI_DEMO);requestAnimationFrame(animate);
