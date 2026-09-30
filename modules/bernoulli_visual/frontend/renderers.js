import {BRAND,rgb,colorNumber} from './palette.js?v=gg31';
/* Original MechLab rendering code. Three.js is optional; the native WebGL
   renderer keeps the 3D lesson usable offline and when a CDN is blocked. */
const PI=Math.PI;
export const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
const sub=(a,b)=>a.map((v,i)=>v-b[i]);
const dot=(a,b)=>a.reduce((v,x,i)=>v+x*b[i],0);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const norm=a=>{const l=Math.hypot(...a)||1;return a.map(x=>x/l);};
export function cameraEye(c){return [c.dist*Math.sin(c.yaw)*Math.cos(c.pitch),c.dist*Math.sin(c.pitch),c.dist*Math.cos(c.yaw)*Math.cos(c.pitch)];}
function perspective(aspect){const f=1/Math.tan(20*PI/180),near=.1,far=100;return new Float32Array([f/aspect,0,0,0,0,f,0,0,0,0,(far+near)/(near-far),-1,0,0,2*far*near/(near-far),0]);}
function lookAt(eye){const z=norm(eye),x=norm(cross([0,1,0],z)),y=cross(z,x);return new Float32Array([x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-dot(x,eye),-dot(y,eye),-dot(z,eye),1]);}
function multiply(a,b){const o=new Float32Array(16);for(let j=0;j<4;j++)for(let i=0;i<4;i++)for(let k=0;k<4;k++)o[j*4+i]+=a[k*4+i]*b[j*4+k];return o;}
export function matrix(c,w,h){return multiply(perspective(w/h),lookAt(cameraEye(c)));}
export function project(pos,c,w,h){const m=matrix(c,w,h);const p=[...pos,1],r=[0,0,0,0];for(let i=0;i<4;i++)for(let j=0;j<4;j++)r[i]+=m[j*4+i]*p[j];return [(r[0]/r[3]*.5+.5)*w,(-r[1]/r[3]*.5+.5)*h,r[3]>0];}
export function geometryData(data){
  const n=data.s.length,maxD=Math.max(...data.diameter_m),midZ=(Math.max(...data.z_m)+Math.min(...data.z_m))/2;
  const zscale=2.8/Math.max(data.length_m,Math.max(...data.z_m)-Math.min(...data.z_m),1);
  const centers=data.s.map((s,i)=>[(s-.5)*10.4,(data.z_m[i]-midZ)*zscale,0]);
  const normals=centers.map((p,i)=>{const t=sub(centers[Math.min(i+1,n-1)],centers[Math.max(0,i-1)]);return norm([-t[1],t[0],0]);});
  const radii=data.diameter_m.map(d=>.69*d/maxD);
  return {centers,normals,radii,n};
}
export function pointAt(g,i,angle,r=1){const c=g.centers[i],v=g.normals[i],rr=g.radii[i]*r;return [c[0]+rr*Math.cos(angle)*v[0],c[1]+rr*Math.cos(angle)*v[1],rr*Math.sin(angle)];}
export function ring(g,i,r=1.04,segments=64){return Array.from({length:segments+1},(_,j)=>pointAt(g,i,2*PI*j/segments,r));}
function sceneMesh(g,cut){
  const positions=[],normals=[],indices=[],m=40,start=cut?PI*.78:0,end=cut?PI*2.22:2*PI;
  for(let i=0;i<g.n;i++)for(let j=0;j<=m;j++){
    const a=start+(end-start)*j/m,p=pointAt(g,i,a);positions.push(...p);
    normals.push(g.normals[i][0]*Math.cos(a),g.normals[i][1]*Math.cos(a),Math.sin(a));
    if(i<g.n-1&&j<m){const k=i*(m+1)+j;indices.push(k,k+m+1,k+1,k+1,k+m+1,k+m+2);}
  }
  return {positions,normals,indices};
}
function staticLines(g,data){
  const lines=[],colors=[];
  const add=(a,b,col)=>{lines.push(...a,...b);colors.push(...col,...col);};
  const rr=(i,r,col)=>{const p=ring(g,i,r);for(let k=0;k<p.length-1;k++)add(p[k],p[k+1],col);};
  for(let x=-8;x<=8;x++)add([x,-2.4,-5],[x,-2.4,5],rgb(BRAND.grid));
  for(let z=-5;z<=5;z++)add([-8,-2.4,z],[8,-2.4,z],rgb(BRAND.grid));
  for(const frac of [0,.2,.35,.5,.65,.8,1])rr(Math.round(frac*(g.n-1)),1,rgb(BRAND.tubeRing));
  for(const angle of [0,PI,PI*1.5])for(let i=0;i<g.n-1;i++)add(pointAt(g,i,angle),pointAt(g,i+1,angle),rgb(BRAND.tubeLine));
  for(const i of [0,g.n-1]){rr(i,1.06,rgb(BRAND.flange));rr(i,1.16,rgb(BRAND.flangeOuter));}
  rr(data.station1_index,1.09,rgb(BRAND.station1));rr(data.station2_index,1.09,rgb(BRAND.station2));
  return {positions:lines,colors};
}
function newCanvas(host){const c=document.createElement('canvas');host.append(c);return c;}
const VERT=`attribute vec3 aPosition;attribute vec3 aNormal;attribute vec3 aColor;uniform mat4 uMVP;uniform float uPointSize;uniform float uLit;varying vec3 vColor;void main(){gl_Position=uMVP*vec4(aPosition,1.0);gl_PointSize=uPointSize*9.0/max(2.0,gl_Position.w);float light=mix(1.0,.46+.54*abs(dot(normalize(aNormal+vec3(.00001)),normalize(vec3(-.3,.8,.7)))),uLit);vColor=aColor*light;}`;
const FRAG=`precision mediump float;varying vec3 vColor;uniform float uAlpha;uniform float uPoints;void main(){float alpha=uAlpha;if(uPoints>.5){float r=length(gl_PointCoord-vec2(.5));if(r>.5)discard;alpha*=smoothstep(.5,.2,r);}gl_FragColor=vec4(vColor,alpha);}`;
export class NativeRenderer{
  constructor(host){
    this.host=host;this.canvas=newCanvas(host);this.gl=this.canvas.getContext('webgl',{alpha:true,antialias:true,preserveDrawingBuffer:true});
    if(!this.gl){this.canvas.remove();throw Error('WebGL unavailable');}
    const gl=this.gl,shader=(type,src)=>{const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;};
    this.program=gl.createProgram();const vs=shader(gl.VERTEX_SHADER,VERT),fs=shader(gl.FRAGMENT_SHADER,FRAG);gl.attachShader(this.program,vs);gl.attachShader(this.program,fs);gl.linkProgram(this.program);gl.deleteShader(vs);gl.deleteShader(fs);
    if(!gl.getProgramParameter(this.program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(this.program));
    this.attrs={};this.uniforms={};for(const n of ['aPosition','aNormal','aColor'])this.attrs[n]=gl.getAttribLocation(this.program,n);for(const n of ['uMVP','uPointSize','uLit','uAlpha','uPoints'])this.uniforms[n]=gl.getUniformLocation(this.program,n);
    this.buffers={};for(const n of ['mesh','norm','meshcol','line','linecol','points','pointcol','zero','probe','probecol'])this.buffers[n]=gl.createBuffer();
    gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.enable(gl.DEPTH_TEST);this.label='3D \u00b7 modo compatible';
  }
  setData(data,cut){this.data=data;this.g=geometryData(data);const g=this.g,m=sceneMesh(g,cut),lines=staticLines(g,data);this.mesh=m.indices.flatMap(i=>m.positions.slice(i*3,i*3+3));this.norm=m.indices.flatMap(i=>m.normals.slice(i*3,i*3+3));this.meshcol=Array.from({length:this.mesh.length/3},()=>rgb(BRAND.tube)).flat();this.lines=lines;this.upload('mesh',this.mesh);this.upload('norm',this.norm);this.upload('meshcol',this.meshcol);this.upload('line',lines.positions);this.upload('linecol',lines.colors);this.upload('zero',new Float32Array(Math.max(this.mesh.length,lines.positions.length,6000)));}
  upload(name,a,dynamic=false){const gl=this.gl;gl.bindBuffer(gl.ARRAY_BUFFER,this.buffers[name]);gl.bufferData(gl.ARRAY_BUFFER,a instanceof Float32Array?a:new Float32Array(a),dynamic?gl.DYNAMIC_DRAW:gl.STATIC_DRAW);}
  attr(name,buffer){const gl=this.gl;gl.bindBuffer(gl.ARRAY_BUFFER,this.buffers[buffer]);gl.vertexAttribPointer(this.attrs[name],3,gl.FLOAT,false,0,0);gl.enableVertexAttribArray(this.attrs[name]);}
  resize(w,h){const ratio=Math.min(devicePixelRatio||1,2);this.w=w;this.h=h;this.ratio=ratio;this.canvas.width=Math.round(w*ratio);this.canvas.height=Math.round(h*ratio);this.gl.viewport(0,0,this.canvas.width,this.canvas.height);}
  draw(p,c,camera,probe){const gl=this.gl;if(!this.g||!this.w)return;gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.useProgram(this.program);gl.uniformMatrix4fv(this.uniforms.uMVP,false,matrix(camera,this.w,this.h));gl.uniform1f(this.uniforms.uPoints,0);gl.uniform1f(this.uniforms.uPointSize,7*this.ratio);gl.uniform1f(this.uniforms.uLit,0);gl.uniform1f(this.uniforms.uAlpha,.7);
    this.attr('aPosition','line');this.attr('aNormal','zero');this.attr('aColor','linecol');gl.drawArrays(gl.LINES,0,this.lines.positions.length/3);
    this.upload('points',p,true);this.upload('pointcol',c,true);this.attr('aPosition','points');this.attr('aNormal','zero');this.attr('aColor','pointcol');gl.uniform1f(this.uniforms.uPoints,1);gl.uniform1f(this.uniforms.uAlpha,1);gl.drawArrays(gl.POINTS,0,p.length/3);
    gl.uniform1f(this.uniforms.uPoints,0);gl.uniform1f(this.uniforms.uLit,1);gl.uniform1f(this.uniforms.uAlpha,.22);gl.depthMask(false);this.attr('aPosition','mesh');this.attr('aNormal','norm');this.attr('aColor','meshcol');gl.drawArrays(gl.TRIANGLES,0,this.mesh.length/3);gl.depthMask(true);
    const rp=ring(this.g,probe,1.16);this.upload('probe',rp.flat(),true);this.upload('probecol',Array.from({length:rp.length},()=>rgb(BRAND.probe)).flat(),true);this.attr('aPosition','probe');this.attr('aNormal','zero');this.attr('aColor','probecol');gl.uniform1f(this.uniforms.uLit,0);gl.uniform1f(this.uniforms.uAlpha,.8);gl.drawArrays(gl.LINE_STRIP,0,rp.length);
  }
  dispose(){const gl=this.gl;for(const b of Object.values(this.buffers))gl.deleteBuffer(b);gl.deleteProgram(this.program);this.canvas.remove();const ext=gl.getExtension('WEBGL_lose_context');if(ext)ext.loseContext();}
}
export class ThreeRenderer{
  constructor(host,T){
    this.T=T;this.host=host;this.canvas=newCanvas(host);try{this.renderer=new T.WebGLRenderer({canvas:this.canvas,alpha:true,antialias:true,preserveDrawingBuffer:true});}catch(e){this.canvas.remove();throw e;}
    this.renderer.setClearColor(0,0);this.renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));this.scene=new T.Scene();this.camera=new T.PerspectiveCamera(40,1,.1,100);
    this.scene.add(new T.HemisphereLight(colorNumber(BRAND.hemisphereSky),colorNumber(BRAND.hemisphereGround),2));const l=new T.DirectionalLight(colorNumber(BRAND.light),2);l.position.set(-4,7,8);this.scene.add(l);this.group=new T.Group();this.scene.add(this.group);this.label='3D \u00b7 Three.js';
  }
  clear(){for(const child of [...this.group.children]){this.group.remove(child);child.geometry?.dispose();if(Array.isArray(child.material))child.material.forEach(m=>m.dispose());else child.material?.dispose();}}
  setData(data,cut){
    this.clear();this.data=data;this.g=geometryData(data);const T=this.T,g=this.g,m=sceneMesh(g,cut),ln=staticLines(g,data);
    const meshGeo=new T.BufferGeometry();meshGeo.setAttribute('position',new T.Float32BufferAttribute(m.positions,3));meshGeo.setAttribute('normal',new T.Float32BufferAttribute(m.normals,3));meshGeo.setIndex(m.indices);
    this.group.add(new T.Mesh(meshGeo,new T.MeshPhongMaterial({color:colorNumber(BRAND.tube),shininess:80,transparent:true,opacity:.23,side:T.DoubleSide,depthWrite:false})));
    const lineGeo=new T.BufferGeometry();lineGeo.setAttribute('position',new T.Float32BufferAttribute(ln.positions,3));lineGeo.setAttribute('color',new T.Float32BufferAttribute(ln.colors,3));this.group.add(new T.LineSegments(lineGeo,new T.LineBasicMaterial({vertexColors:true,transparent:true,opacity:.9})));
    const pg=new T.BufferGeometry();pg.setAttribute('position',new T.Float32BufferAttribute(new Float32Array(1080),3));pg.setAttribute('color',new T.Float32BufferAttribute(new Float32Array(1080),3));
    const canvas=document.createElement('canvas');canvas.width=32;canvas.height=32;const ctx=canvas.getContext('2d');const grad=ctx.createRadialGradient(16,16,0,16,16,16);grad.addColorStop(0,'rgba(255,255,255,1)');grad.addColorStop(.45,'rgba(255,255,255,1)');grad.addColorStop(1,'rgba(255,255,255,0)');ctx.fillStyle=grad;ctx.fillRect(0,0,32,32);this.pointTexture?.dispose();this.pointTexture=new T.CanvasTexture(canvas);
    this.points=new T.Points(pg,new T.PointsMaterial({size:.13,vertexColors:true,map:this.pointTexture,transparent:true,depthWrite:false,opacity:1}));this.group.add(this.points);
    this.probeLine=new T.Line(new T.BufferGeometry().setFromPoints(ring(g,data.station2_index,1.16).map(v=>new T.Vector3(...v))),new T.LineBasicMaterial({color:colorNumber(BRAND.probe),transparent:true,opacity:.9}));this.group.add(this.probeLine);this.lastProbe=-1;
  }
  resize(w,h){this.w=w;this.h=h;this.renderer.setSize(w,h,false);this.camera.aspect=w/h;this.camera.updateProjectionMatrix();}
  draw(p,c,camera,probe){if(!this.g)return;const T=this.T;this.camera.position.set(...cameraEye(camera));this.camera.lookAt(0,0,0);this.points.geometry.attributes.position.array.set(p);this.points.geometry.attributes.position.needsUpdate=true;this.points.geometry.attributes.color.array.set(c);this.points.geometry.attributes.color.needsUpdate=true;
    if(probe!==this.lastProbe){this.probeLine.geometry.dispose();this.probeLine.geometry=new T.BufferGeometry().setFromPoints(ring(this.g,probe,1.16).map(v=>new T.Vector3(...v)));this.lastProbe=probe;}
    this.renderer.render(this.scene,this.camera);
  }
  dispose(){this.clear();this.pointTexture?.dispose();this.renderer.dispose();this.canvas.remove();}
}
export class CanvasRenderer{
  constructor(host){this.host=host;this.canvas=newCanvas(host);this.ctx=this.canvas.getContext('2d');this.label='3D \u00b7 modo sin GPU';}
  setData(data,cut){
    this.data=data;this.g=geometryData(data);const g=this.g,start=cut?PI*.78:0,end=cut?PI*2.22:2*PI;
    this.faces=[];const steps=24,rings=36;
    for(let j=0;j<steps;j++)for(let k=0;k<rings;k++){
      const i=Math.round((g.n-1)*k/rings),ii=Math.round((g.n-1)*(k+1)/rings),a=start+(end-start)*j/steps,b=start+(end-start)*(j+1)/steps;
      this.faces.push({points:[pointAt(g,i,a),pointAt(g,ii,a),pointAt(g,ii,b),pointAt(g,i,b)],shade:.5+.5*Math.abs(Math.cos((a+b)/2))});
    }
    this.lines=staticLines(g,data);
  }
  resize(w,h){this.w=w;this.h=h;const ratio=Math.min(devicePixelRatio||1,2);this.canvas.width=w*ratio;this.canvas.height=h*ratio;this.ctx.setTransform(ratio,0,0,ratio,0,0);}
  draw(p,c,camera,probe){
    if(!this.g)return;const ctx=this.ctx,g=this.g,mat=matrix(camera,this.w,this.h);
    const proj=v=>{const x=mat[0]*v[0]+mat[4]*v[1]+mat[8]*v[2]+mat[12],y=mat[1]*v[0]+mat[5]*v[1]+mat[9]*v[2]+mat[13],w=mat[3]*v[0]+mat[7]*v[1]+mat[11]*v[2]+mat[15];return [(x/w*.5+.5)*this.w,(-y/w*.5+.5)*this.h,w];};
    ctx.clearRect(0,0,this.w,this.h);
    const faces=this.faces.map(f=>{const pts=f.points.map(proj);return {pts,depth:pts.reduce((s,a)=>s+a[2],0)/4,shade:f.shade};}).sort((a,b)=>b.depth-a.depth);
    for(const f of faces){ctx.beginPath();f.pts.forEach((v,i)=>i?ctx.lineTo(v[0],v[1]):ctx.moveTo(v[0],v[1]));ctx.closePath();ctx.fillStyle=`rgba(${Math.round(138+f.shade*34)},${Math.round(119+f.shade*31)},${Math.round(98+f.shade*28)},.16)`;ctx.fill();}
    const pos=this.lines.positions,col=this.lines.colors;const groups=new Map();
    for(let i=0;i<pos.length;i+=6){const color=`rgba(${Math.round(col[i]*255)},${Math.round(col[i+1]*255)},${Math.round(col[i+2]*255)},.72)`;if(!groups.has(color))groups.set(color,[]);groups.get(color).push([proj(pos.slice(i,i+3)),proj(pos.slice(i+3,i+6))]);}
    for(const [color,lines] of groups){ctx.beginPath();for(const [a,b] of lines){ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);}ctx.strokeStyle=color;ctx.lineWidth=1;ctx.stroke();}
    const pts=[];for(let i=0;i<p.length;i+=3)pts.push({v:proj([p[i],p[i+1],p[i+2]]),col:`rgb(${Math.round(c[i]*255)},${Math.round(c[i+1]*255)},${Math.round(c[i+2]*255)})`});pts.sort((a,b)=>b.v[2]-a.v[2]);
    for(const {v,col} of pts){if(v[2]<=0)continue;const r=clamp(26/v[2],1.3,3.8);ctx.beginPath();ctx.arc(v[0],v[1],r,0,2*PI);ctx.fillStyle=col;ctx.fill();}
    const rp=ring(g,probe,1.16).map(proj);ctx.beginPath();rp.forEach((v,i)=>i?ctx.lineTo(v[0],v[1]):ctx.moveTo(v[0],v[1]));ctx.strokeStyle=BRAND.probe+'c9';ctx.lineWidth=1.5;ctx.stroke();
  }
  dispose(){this.canvas.remove();}
}
