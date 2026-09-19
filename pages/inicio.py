from __future__ import annotations

from pathlib import Path
import base64
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

VERSION = "PREMIUM LANDING V1.4"


def data_uri(path: Path) -> str:
    mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


hero_img = data_uri(ASSETS / "gerardo_hero.jpg")
field_img = data_uri(ASSETS / "gerardo_terreno.jpg")
industry_img = data_uri(ASSETS / "gerardo_industria.jpg")
logo_img = data_uri(ASSETS / "logo_mechlab_landing.png")
sim_img = data_uri(ASSETS / "brochure_simulacion.jpg")
scan_img = data_uri(ASSETS / "brochure_escaneo.jpg")
training_img = data_uri(ASSETS / "brochure_formacion.jpg")

css = """
<style>
:root{
  --gg-orange:#ff6900;
  --gg-black:#090909;
  --gg-charcoal:#171717;
  --gg-paper:#f7f7f4;
  --gg-muted:#686b70;
  --gg-line:#e6e6e2;
}
.block-container{
  max-width:1500px;
  padding-top:.6rem;
  padding-bottom:2.3rem;
}
.stApp{background:#ffffff;}
html{scroll-behavior:smooth;}
.gg-page{
  width:100%;
  color:var(--gg-charcoal);
  font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
.gg-page *{box-sizing:border-box;}
.gg-page a{text-decoration:none!important;}

.gg-hero{
  min-height:610px;
  display:grid;
  grid-template-columns:1.06fr .94fr;
  border-radius:24px;
  overflow:hidden;
  position:relative;
  background:
    radial-gradient(circle at 16% 16%,rgba(255,105,0,.17),transparent 29%),
    linear-gradient(135deg,#050505,#111 62%,#1b1b1b);
  box-shadow:0 18px 52px rgba(0,0,0,.15);
}
.gg-hero:before{
  content:"";
  position:absolute;
  inset:0;
  background-image:
    linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);
  background-size:34px 34px;
  mask-image:linear-gradient(90deg,#000,transparent 76%);
  pointer-events:none;
}
.gg-hero-copy{
  padding:58px 58px 55px 60px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  position:relative;
  z-index:2;
}
.gg-brand{
  display:flex;
  align-items:center;
  gap:14px;
  margin-bottom:23px;
}
.gg-brand img{
  width:86px;
  height:auto;
  border-radius:11px;
  background:#fffaf5;
}
.gg-brand strong{
  display:block;
  color:#fff;
  letter-spacing:.04em;
  font-size:1.04rem;
}
.gg-brand small{
  display:block;
  color:#aeb1b5;
  margin-top:3px;
  font-size:.81rem;
}
.gg-kicker{
  color:var(--gg-orange);
  font-size:.79rem;
  text-transform:uppercase;
  letter-spacing:.10em;
  font-weight:900;
  margin-bottom:10px;
}
.gg-hero h1{
  color:#fff;
  font-size:clamp(2.8rem,4.8vw,5rem);
  line-height:.98;
  letter-spacing:-.045em;
  margin:0 0 20px;
}
.gg-hero h1 span{color:var(--gg-orange);}
.gg-hero-lead{
  color:#dadada;
  font-size:1.06rem;
  line-height:1.58;
  max-width:760px;
  margin:0 0 14px;
}
.gg-hero-promise{
  color:#fff;
  border-left:4px solid var(--gg-orange);
  padding-left:16px;
  max-width:720px;
  line-height:1.52;
  font-weight:650;
}
.gg-actions{
  display:flex;
  gap:11px;
  flex-wrap:wrap;
  margin-top:22px;
}
.gg-btn{
  display:inline-flex;
  align-items:center;
  gap:8px;
  border-radius:11px;
  padding:13px 18px;
  font-weight:850;
  font-size:.92rem;
  transition:.17s ease;
}
.gg-btn:hover{transform:translateY(-2px);}
.gg-btn-primary{background:var(--gg-orange);color:#fff!important;}
.gg-btn-dark{background:#171717;border:1px solid #373737;color:#fff!important;}
.gg-audience{
  display:flex;
  gap:8px;
  flex-wrap:wrap;
  margin-top:20px;
}
.gg-audience span{
  color:#e8e8e8;
  border:1px solid #343434;
  background:#151515;
  border-radius:999px;
  padding:7px 10px;
  font-size:.77rem;
  font-weight:760;
}
.gg-hero-photo{
  min-height:610px;
  position:relative;
  background:
    linear-gradient(90deg,rgba(8,8,8,.45),rgba(8,8,8,.02)),
    url("__HERO__") center 30%/cover no-repeat;
}
.gg-profile{
  position:absolute;
  left:25px;
  right:25px;
  bottom:25px;
  color:#fff;
  background:rgba(7,7,7,.82);
  border:1px solid rgba(255,255,255,.14);
  border-left:4px solid var(--gg-orange);
  border-radius:14px;
  padding:15px 17px;
  backdrop-filter:blur(8px);
  line-height:1.42;
}
.gg-profile strong{font-size:1rem;}

.gg-value-strip{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:13px;
  position:relative;
  z-index:5;
  margin:-32px 18px 0;
}
.gg-value{
  display:flex;
  gap:13px;
  min-height:118px;
  padding:18px;
  background:#fff;
  border:1px solid var(--gg-line);
  border-radius:17px;
  box-shadow:0 14px 30px rgba(0,0,0,.07);
}
.gg-value-icon{
  min-width:48px;
  height:48px;
  border-radius:13px;
  display:flex;
  align-items:center;
  justify-content:center;
  color:var(--gg-orange);
  background:#111;
  font-size:1.12rem;
  font-weight:950;
}
.gg-value h3{
  margin:1px 0 5px;
  font-size:1rem;
}
.gg-value p{
  margin:0;
  color:var(--gg-muted);
  font-size:.84rem;
  line-height:1.43;
}

.gg-section{padding:62px 8px 10px;}
.gg-section h2{
  margin:0 0 13px;
  font-size:clamp(2rem,3.3vw,3.2rem);
  line-height:1.05;
  letter-spacing:-.03em;
}
.gg-intro{
  max-width:900px;
  color:var(--gg-muted);
  font-size:1rem;
  line-height:1.6;
  margin-bottom:27px;
}

.gg-route-grid{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:15px;
}
.gg-route{
  position:relative;
  overflow:hidden;
  padding:22px;
  border:1px solid var(--gg-line);
  border-radius:18px;
  background:#fff;
  box-shadow:0 9px 25px rgba(0,0,0,.045);
}
.gg-route:after{
  content:"";
  position:absolute;
  width:115px;
  height:115px;
  right:-33px;
  top:-38px;
  border:1px solid rgba(255,105,0,.15);
  border-radius:50%;
}
.gg-route-icon{
  width:52px;
  height:52px;
  display:flex;
  align-items:center;
  justify-content:center;
  border-radius:14px;
  color:var(--gg-orange);
  background:#111;
  font-size:1.2rem;
  font-weight:950;
  margin-bottom:15px;
}
.gg-route h3{margin:0 0 7px;font-size:1.12rem;}
.gg-route p{margin:0;color:var(--gg-muted);font-size:.88rem;line-height:1.5;}
.gg-route a{
  display:inline-block;
  margin-top:13px;
  color:#111!important;
  font-weight:850;
  font-size:.87rem;
}
.gg-route a:hover{color:var(--gg-orange)!important;}

.gg-dashboard{
  display:grid;
  grid-template-columns:1.25fr repeat(4,.75fr);
  gap:10px;
  align-items:center;
  border-radius:20px;
  background:#0b0b0b;
  color:#fff;
  padding:24px;
}
.gg-dashboard h3{margin:0 0 5px;color:#fff;font-size:1.17rem;}
.gg-dashboard p{margin:0;color:#bcbcbc;font-size:.86rem;line-height:1.43;}
.gg-stat{border-left:1px solid #303030;padding-left:15px;}
.gg-stat strong{display:block;color:var(--gg-orange);font-size:1.25rem;}
.gg-stat span{font-size:.77rem;color:#d8d8d8;}

.gg-tools{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:16px;
}
.gg-tool{
  display:flex;
  flex-direction:column;
  min-height:316px;
  padding:22px;
  border:1px solid var(--gg-line);
  border-radius:20px;
  background:#fff;
  box-shadow:0 10px 28px rgba(0,0,0,.05);
  transition:.17s ease;
}
.gg-tool:hover{
  transform:translateY(-3px);
  box-shadow:0 15px 35px rgba(0,0,0,.075);
}
.gg-tool-top{
  display:flex;
  align-items:center;
  justify-content:space-between;
  margin-bottom:16px;
}
.gg-tool-symbol{
  width:56px;
  height:56px;
  border-radius:15px;
  display:flex;
  align-items:center;
  justify-content:center;
  color:var(--gg-orange);
  background:#111;
  font-size:1.18rem;
  font-weight:950;
}
.gg-status{
  padding:6px 9px;
  border-radius:999px;
  background:#f4f4f1;
  color:#555;
  font-size:.71rem;
  font-weight:800;
}
.gg-tool h3{font-size:1.18rem;margin:0 0 7px;}
.gg-tool p{color:var(--gg-muted);font-size:.88rem;line-height:1.5;margin:0 0 13px;}
.gg-tags{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;}
.gg-tags span{
  padding:6px 8px;
  border-radius:999px;
  background:#f5f5f2;
  color:#555;
  font-size:.72rem;
  font-weight:700;
}
.gg-tool-links{margin-top:auto;}
.gg-tool-links a{
  display:block;
  color:#111!important;
  font-size:.87rem;
  font-weight:850;
  margin-top:8px;
}
.gg-tool-links a:hover{color:var(--gg-orange)!important;}

.gg-flow{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:14px;
}
.gg-step{
  padding:22px;
  border:1px solid var(--gg-line);
  border-radius:18px;
  background:linear-gradient(180deg,#fff,#fafaf8);
}
.gg-step-number{
  width:40px;
  height:40px;
  display:flex;
  align-items:center;
  justify-content:center;
  border-radius:10px;
  color:var(--gg-orange);
  background:#111;
  font-weight:950;
  margin-bottom:13px;
}
.gg-step h3{font-size:1.06rem;margin:0 0 7px;}
.gg-step p{color:var(--gg-muted);font-size:.88rem;line-height:1.5;margin:0;}

.gg-vision{
  display:grid;
  grid-template-columns:.84fr 1.16fr;
  overflow:hidden;
  border-radius:22px;
  background:#0b0b0b;
}
.gg-vision-photo{
  min-height:515px;
  background:url("__FIELD__") center center/cover no-repeat;
}
.gg-vision-copy{
  display:flex;
  flex-direction:column;
  justify-content:center;
  padding:52px 54px;
  background:
    radial-gradient(circle at 90% 12%,rgba(255,105,0,.12),transparent 31%),
    #0b0b0b;
}
.gg-vision-copy h2{color:#fff;}
.gg-vision-copy p{color:#d0d0d0;font-size:.98rem;line-height:1.6;margin:0 0 13px;}
.gg-quote{
  color:#fff!important;
  border-left:4px solid var(--gg-orange);
  padding-left:16px;
  font-weight:720;
}
.gg-badges{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px;}
.gg-badges span{
  color:#fff;
  background:#171717;
  border:1px solid #343434;
  border-radius:999px;
  padding:8px 10px;
  font-size:.77rem;
  font-weight:750;
}

.gg-about{
  display:grid;
  grid-template-columns:.82fr 1.18fr;
  gap:25px;
}
.gg-about-photo{
  min-height:430px;
  display:flex;
  align-items:flex-end;
  padding:23px;
  border-radius:20px;
  color:#fff;
  background:
    linear-gradient(180deg,transparent 38%,rgba(0,0,0,.76)),
    url("__INDUSTRY__") center 20%/cover no-repeat;
}
.gg-about-copy{
  padding:32px 34px;
  border:1px solid var(--gg-line);
  border-radius:20px;
  background:#fff;
}
.gg-role{color:var(--gg-orange);font-weight:850;margin-bottom:14px;}
.gg-about-copy p{color:#565b60;line-height:1.58;margin:0 0 12px;}
.gg-skills{
  display:grid;
  grid-template-columns:repeat(2,1fr);
  gap:8px;
  margin-top:16px;
}
.gg-skills span{
  padding:9px 11px;
  border-radius:10px;
  background:#f5f5f2;
  font-size:.82rem;
  font-weight:750;
}

.gg-gallery{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:15px;
}
.gg-gallery-card{
  min-height:335px;
  overflow:hidden;
  position:relative;
  border-radius:18px;
  background:#111;
}
.gg-gallery-card img{width:100%;height:100%;object-fit:cover;display:block;}
.gg-gallery-caption{
  position:absolute;
  left:0;
  right:0;
  bottom:0;
  padding:40px 18px 17px;
  color:#fff;
  font-weight:850;
  background:linear-gradient(transparent,rgba(0,0,0,.9));
}

.gg-contact{
  margin-top:60px;
  padding:40px;
  border-radius:22px;
  color:#fff;
  background:#080808;
}
.gg-contact h2{color:#fff;margin:0 0 8px;}
.gg-contact p{color:#c9c9c9;line-height:1.55;max-width:880px;}
.gg-socials{
  display:grid;
  grid-template-columns:repeat(5,1fr);
  gap:9px;
  margin-top:21px;
}
.gg-socials a{
  min-height:67px;
  padding:13px 12px;
  border:1px solid #303030;
  border-radius:12px;
  color:#fff!important;
  background:#151515;
  font-size:.79rem;
  line-height:1.35;
}
.gg-socials a:hover{border-color:var(--gg-orange);}
.gg-socials b{display:block;color:var(--gg-orange);margin-bottom:4px;}

.gg-footer{
  display:flex;
  justify-content:space-between;
  gap:16px;
  flex-wrap:wrap;
  padding:20px 5px 3px;
  color:#777;
  font-size:.79rem;
}
.gg-version{
  color:var(--gg-orange);
  font-weight:850;
}

@media(max-width:1100px){
  .gg-hero,.gg-vision,.gg-about{grid-template-columns:1fr;}
  .gg-hero-photo{min-height:470px;}
  .gg-value-strip,.gg-tools{grid-template-columns:repeat(2,1fr);}
  .gg-route-grid,.gg-flow,.gg-gallery{grid-template-columns:1fr 1fr;}
  .gg-dashboard{grid-template-columns:1fr 1fr;}
  .gg-socials{grid-template-columns:1fr 1fr;}
}
@media(max-width:700px){
  .gg-hero-copy{padding:40px 24px;}
  .gg-value-strip{margin:14px 0 0;}
  .gg-value-strip,.gg-route-grid,.gg-tools,.gg-flow,.gg-gallery,.gg-dashboard,.gg-socials,.gg-skills{grid-template-columns:1fr;}
  .gg-vision-copy,.gg-about-copy,.gg-contact{padding:28px 22px;}
}
</style>
"""

css = (
    css.replace("__HERO__", hero_img)
       .replace("__FIELD__", field_img)
       .replace("__INDUSTRY__", industry_img)
)
st.html(css)

hero_html = f"""
<div class="gg-page">
<section class="gg-hero">
  <div class="gg-hero-copy">
    <div class="gg-brand">
      <img src="{logo_img}" alt="GG DIMEC">
      <div>
        <strong>GG DIMEC SPA · MECHLAB</strong>
        <small>Tecnología avanzada en soluciones reales · aprendizaje aplicado</small>
      </div>
    </div>
    <div class="gg-kicker">Ingeniería visual aplicada</div>
    <h1>Entiende la ingeniería.<br><span>Luego úsala mejor.</span></h1>
    <p class="gg-hero-lead">
      Herramientas interactivas para estudiar, enseñar y revisar conceptos de ingeniería mecánica
      con apoyo visual, ecuaciones y lectura física del resultado.
    </p>
    <div class="gg-hero-promise">
      MechLab conecta fundamentos, visualización y experiencia industrial para ayudarte a desarrollar
      criterio técnico, no solo a obtener respuestas.
    </div>
    <div class="gg-actions">
      <a class="gg-btn gg-btn-primary" href="#herramientas">Explorar herramientas ↓</a>
      <a class="gg-btn gg-btn-dark" href="https://www.gerardogaraydimec.com/" target="_blank">Conocer GG DIMEC ↗</a>
    </div>
    <div class="gg-audience">
      <span>Estudiantes</span><span>Docentes</span><span>Ingenieros</span><span>Industria</span>
    </div>
  </div>
  <div class="gg-hero-photo">
    <div class="gg-profile">
      <strong>Gerardo Garay Pereira</strong><br>
      Ingeniero Civil Mecánico · Docente · Fundador de GG DIMEC SPA
    </div>
  </div>
</section>

<section class="gg-value-strip">
  <div class="gg-value"><div class="gg-value-icon">σ</div><div><h3>Visualiza</h3><p>Convierte ecuaciones en estados, geometría y comportamiento observable.</p></div></div>
  <div class="gg-value"><div class="gg-value-icon">∑</div><div><h3>Analiza</h3><p>Cambia variables y entiende por qué cambia la respuesta del modelo.</p></div></div>
  <div class="gg-value"><div class="gg-value-icon">⚙</div><div><h3>Aplica</h3><p>Conecta fundamentos con problemas propios del diseño y la industria.</p></div></div>
  <div class="gg-value"><div class="gg-value-icon">↗</div><div><h3>Crece</h3><p>Refuerza criterio técnico y construye una forma más sólida de pensar ingeniería.</p></div></div>
</section>
"""
st.html(hero_html)

routes_html = """
<section class="gg-section gg-page">
  <div class="gg-kicker">Elige tu ruta</div>
  <h2>MechLab se adapta a cómo quieres aprender</h2>
  <div class="gg-route-grid">
    <div class="gg-route">
      <div class="gg-route-icon">🎓</div>
      <h3>Estoy estudiando</h3>
      <p>Refuerza fundamentos, explora gráficos y comprende cómo responden las variables.</p>
      <a href="#herramientas">Ir a herramientas →</a>
    </div>
    <div class="gg-route">
      <div class="gg-route-icon">▣</div>
      <h3>Estoy enseñando</h3>
      <p>Apoya clases con recursos visuales que conectan modelo, ecuación e interpretación.</p>
      <a href="#herramientas">Explorar módulos →</a>
    </div>
    <div class="gg-route">
      <div class="gg-route-icon">🏭</div>
      <h3>Estoy trabajando</h3>
      <p>Revisa conceptos y conecta fundamentos con ingeniería aplicada y comunicación técnica.</p>
      <a href="https://www.gerardogaraydimec.com/" target="_blank">Ver GG DIMEC →</a>
    </div>
  </div>
</section>
"""
st.html(routes_html)

dashboard_html = """
<section class="gg-section gg-page">
  <div class="gg-dashboard">
    <div>
      <h3>MechLab en una mirada</h3>
      <p>Un laboratorio digital para aprender ingeniería mecánica desde distintos enfoques.</p>
    </div>
    <div class="gg-stat"><strong>σ</strong><span>Resistencia y esfuerzos</span></div>
    <div class="gg-stat"><strong>ω</strong><span>Vibraciones y dinámica</span></div>
    <div class="gg-stat"><strong>T–s</strong><span>Termodinámica</span></div>
    <div class="gg-stat"><strong>VM</strong><span>Diseño y falla</span></div>
  </div>
</section>
"""
st.html(dashboard_html)

tools_html = """
<div id="herramientas"></div>
<section class="gg-section gg-page">
  <div class="gg-kicker">Herramientas disponibles</div>
  <h2>Entra directo al fenómeno que quieres estudiar</h2>
  <div class="gg-intro">
    Menos navegación y más trabajo: cada área reúne herramientas enfocadas en visualizar,
    modificar condiciones y comprender la respuesta física.
  </div>
  <div class="gg-tools">
    <div class="gg-tool">
      <div class="gg-tool-top"><div class="gg-tool-symbol">σ</div><span class="gg-status">Resistencia</span></div>
      <h3>Resistencia de Materiales</h3>
      <p>Transformación de esfuerzos, tensiones principales y lectura del estado resistente.</p>
      <div class="gg-tags"><span>Mohr 2D</span><span>Mohr 3D</span><span>Principales</span></div>
      <div class="gg-tool-links">
        <a href="/mohr-2d">Círculo de Mohr 2D →</a>
        <a href="/mohr-3d">Círculo de Mohr 3D →</a>
      </div>
    </div>
    <div class="gg-tool">
      <div class="gg-tool-top"><div class="gg-tool-symbol">ω</div><span class="gg-status">Dinámica</span></div>
      <h3>Vibraciones y Dinámica</h3>
      <p>Respuesta libre y forzada, frecuencia natural, amortiguamiento y resonancia.</p>
      <div class="gg-tags"><span>1-GDL</span><span>Respuesta</span><span>Frecuencia</span></div>
      <div class="gg-tool-links">
        <a href="/vibraciones-1gdl">Vibraciones libres 1-GDL →</a>
        <a href="/vibracion-forzada-1gdl">Vibración forzada 1-GDL →</a>
      </div>
    </div>
    <div class="gg-tool">
      <div class="gg-tool-top"><div class="gg-tool-symbol">T–s</div><span class="gg-status">Energía</span></div>
      <h3>Termodinámica</h3>
      <p>Estados del agua y vapor, regiones termodinámicas, diagramas y ciclos.</p>
      <div class="gg-tags"><span>Agua-vapor</span><span>Ciclos</span><span>Diagramas</span></div>
      <div class="gg-tool-links">
        <a href="/agua-vapor">Propiedades del agua y vapor →</a>
        <a href="/ciclos-termodinamicos">Ciclos termodinámicos →</a>
      </div>
    </div>
    <div class="gg-tool">
      <div class="gg-tool-top"><div class="gg-tool-symbol">VM</div><span class="gg-status">Diseño</span></div>
      <h3>Elementos de Máquinas</h3>
      <p>Criterios de fluencia, esfuerzo equivalente y estados multiaxiales.</p>
      <div class="gg-tags"><span>Von Mises</span><span>Tresca</span><span>Falla</span></div>
      <div class="gg-tool-links"><a href="/von-mises">Abrir Von Mises Lab →</a></div>
    </div>
  </div>
</section>
"""
st.html(tools_html)

flow_html = """
<section class="gg-section gg-page">
  <div class="gg-kicker">Cómo trabajar</div>
  <h2>Tres pasos. Mucho más criterio.</h2>
  <div class="gg-flow">
    <div class="gg-step"><div class="gg-step-number">1</div><h3>Define el problema</h3><p>Selecciona la herramienta y configura las condiciones que quieres estudiar.</p></div>
    <div class="gg-step"><div class="gg-step-number">2</div><h3>Explora la respuesta</h3><p>Mueve variables, compara escenarios y observa gráficos, estados y ecuaciones.</p></div>
    <div class="gg-step"><div class="gg-step-number">3</div><h3>Interpreta</h3><p>Entiende qué significa el resultado y cómo se conecta con ingeniería real.</p></div>
  </div>
</section>
"""
st.html(flow_html)

vision_html = """
<section class="gg-section gg-page">
  <div class="gg-vision">
    <div class="gg-vision-photo"></div>
    <div class="gg-vision-copy">
      <div class="gg-kicker">Mi visión</div>
      <h2>Aprender con ingeniería real</h2>
      <p>
        GG DIMEC nació desde la ingeniería aplicada y el trabajo con problemas reales.
        Esa misma lógica quiero llevar al aprendizaje: comprender, modelar, visualizar, cuestionar y mejorar.
      </p>
      <p class="gg-quote">
        Quiero que MechLab ayude a estudiantes e ingenieros a aprender mejor y a desarrollar una forma
        más clara, rigurosa y útil de pensar la ingeniería.
      </p>
      <div class="gg-badges">
        <span>Industria real</span><span>Docencia</span><span>Simulación</span><span>Diseño mecánico</span><span>Aprendizaje continuo</span>
      </div>
    </div>
  </div>
</section>
"""
st.html(vision_html)

about_html = """
<section class="gg-section gg-page">
  <div class="gg-kicker">Sobre mí</div>
  <div class="gg-about">
    <div class="gg-about-photo">
      <div><b>Ingeniería en terreno</b><br>Experiencia técnica, industria y aprendizaje conectado con la realidad.</div>
    </div>
    <div class="gg-about-copy">
      <h2>Gerardo Garay Pereira</h2>
      <div class="gg-role">Ingeniero Civil Mecánico · Docente · Fundador de GG DIMEC SPA</div>
      <p>
        Trabajo en diseño mecánico, simulación, levantamiento 3D, análisis de equipos y formación técnica.
        Me interesa traducir problemas complejos en soluciones claras y aplicables.
      </p>
      <p>
        MechLab nace como una extensión de esa visión: compartir herramientas que ayuden a estudiar,
        enseñar y seguir creciendo profesionalmente.
      </p>
      <div class="gg-skills">
        <span>Diseño mecánico</span><span>Simulación FEM / CFD</span>
        <span>Escaneo 3D</span><span>Ingeniería inversa</span>
        <span>Docencia</span><span>Capacitación técnica</span>
      </div>
    </div>
  </div>
</section>
"""
st.html(about_html)

gallery_html = f"""
<section class="gg-section gg-page">
  <div class="gg-kicker">Ingeniería aplicada</div>
  <h2>De la industria a la enseñanza</h2>
  <div class="gg-intro">
    La experiencia de GG DIMEC alimenta MechLab: modelamiento, simulación,
    digitalización 3D y transferencia de conocimiento.
  </div>
  <div class="gg-gallery">
    <div class="gg-gallery-card"><img src="{sim_img}" alt="Simulación"><div class="gg-gallery-caption">Simulación estructural y dinámica</div></div>
    <div class="gg-gallery-card"><img src="{scan_img}" alt="Escaneo 3D"><div class="gg-gallery-caption">Escaneo 3D e ingeniería inversa</div></div>
    <div class="gg-gallery-card"><img src="{training_img}" alt="Capacitación"><div class="gg-gallery-caption">Capacitación y transferencia de conocimiento</div></div>
  </div>
</section>
"""
st.html(gallery_html)

contact_html = f"""
<section class="gg-contact gg-page">
  <div class="gg-kicker">Contacto y comunidad</div>
  <h2>Sigamos construyendo mejor ingeniería</h2>
  <p>
    Si eres estudiante, docente, ingeniero o empresa, puedes seguir mi trabajo,
    revisar GG DIMEC y conversar conmigo sobre aprendizaje, ingeniería y colaboración.
  </p>
  <div class="gg-socials">
    <a href="mailto:gerardogaray.dimec@gmail.com"><b>Correo</b>gerardogaray.dimec@gmail.com</a>
    <a href="tel:+56957288516"><b>Teléfono</b>+56 9 5728 8516</a>
    <a href="https://www.instagram.com/gerardogaray.dimec/" target="_blank"><b>Instagram</b>@gerardogaray.dimec</a>
    <a href="https://www.linkedin.com/in/gerardo-garay-pereira/" target="_blank"><b>LinkedIn</b>Gerardo Garay Pereira</a>
    <a href="https://www.gerardogaraydimec.com/" target="_blank"><b>Web</b>www.gerardogaraydimec.com</a>
  </div>
</section>
<div class="gg-footer gg-page">
  <span>GG DIMEC SPA · Gerardo Garay Pereira · Chile</span>
  <span class="gg-version">{VERSION}</span>
</div>
"""
st.html(contact_html)
