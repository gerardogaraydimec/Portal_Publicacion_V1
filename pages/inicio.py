
from __future__ import annotations

from pathlib import Path
import base64
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

ORANGE = "#ff6900"
BLACK = "#090909"
CHARCOAL = "#171717"
MUTED = "#6a6d72"
LIGHT = "#f6f6f4"


def data_uri(path: Path) -> str:
    mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


hero_img = data_uri(ASSETS / "gerardo_hero.jpg")
field_img = data_uri(ASSETS / "gerardo_terreno.jpg")
industry_img = data_uri(ASSETS / "gerardo_industria.jpg")
logo_img = data_uri(ASSETS / "logo_mechlab_landing.png")
sim_img = data_uri(ASSETS / "brochure_simulacion.jpg")
scan_img = data_uri(ASSETS / "brochure_escaneo.jpg")
train_img = data_uri(ASSETS / "brochure_formacion.jpg")

st.markdown(
    f"""
<style>
.block-container {{
    max-width: 1500px;
    padding-top: .65rem;
    padding-bottom: 2.5rem;
}}
.stApp {{ background:#fff; color:{BLACK}; }}
html {{ scroll-behavior:smooth; }}

:root {{
    --orange:{ORANGE};
    --black:{BLACK};
    --charcoal:{CHARCOAL};
    --muted:{MUTED};
    --light:{LIGHT};
    --border:#e6e6e3;
}}

.landing {{
    width:100%;
    overflow:hidden;
    border-radius:24px;
}}
.landing * {{ box-sizing:border-box; }}

.hero {{
    min-height:620px;
    display:grid;
    grid-template-columns:1.08fr .92fr;
    border-radius:24px;
    overflow:hidden;
    position:relative;
    background:
        linear-gradient(120deg, rgba(255,105,0,.10), transparent 26%),
        linear-gradient(135deg,#050505 0%,#0b0b0b 58%,#181818 100%);
    box-shadow:0 18px 52px rgba(0,0,0,.15);
}}
.hero::before {{
    content:"";
    position:absolute;
    inset:0;
    background-image:
        linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
        linear-gradient(90deg,rgba(255,255,255,.025) 1px, transparent 1px);
    background-size:34px 34px;
    mask-image:linear-gradient(90deg,#000,transparent 75%);
    pointer-events:none;
}}
.hero-copy {{
    padding:58px 58px 58px 60px;
    position:relative;
    z-index:2;
    display:flex;
    flex-direction:column;
    justify-content:center;
}}
.brandbar {{
    display:flex;
    align-items:center;
    gap:14px;
    margin-bottom:22px;
}}
.brandbar img {{
    width:88px;
    height:auto;
    background:#fffaf5;
    border-radius:11px;
}}
.brandname {{
    color:#fff;
    font-weight:900;
    font-size:1.04rem;
    letter-spacing:.04em;
}}
.brandline {{
    color:#aeb1b5;
    font-size:.82rem;
    margin-top:2px;
}}
.eyebrow {{
    color:var(--orange);
    text-transform:uppercase;
    letter-spacing:.10em;
    font-size:.80rem;
    font-weight:900;
    margin-bottom:12px;
}}
.hero h1 {{
    color:#fff;
    font-size:clamp(2.8rem,4.9vw,5.1rem);
    line-height:.97;
    letter-spacing:-.045em;
    margin:0 0 22px 0;
    max-width:900px;
}}
.hero h1 em {{
    color:var(--orange);
    font-style:normal;
}}
.hero-lead {{
    color:#d8d8d8;
    font-size:1.08rem;
    line-height:1.58;
    max-width:760px;
    margin:0 0 14px 0;
}}
.hero-promise {{
    color:#fff;
    border-left:4px solid var(--orange);
    padding-left:16px;
    font-size:1rem;
    line-height:1.52;
    font-weight:650;
    max-width:730px;
    margin-top:2px;
}}
.ctas {{
    display:flex;
    flex-wrap:wrap;
    gap:11px;
    margin-top:23px;
}}
.btn {{
    display:inline-flex;
    align-items:center;
    gap:8px;
    text-decoration:none !important;
    border-radius:11px;
    padding:13px 18px;
    font-weight:850;
    font-size:.93rem;
    transition:.16s ease;
}}
.btn:hover {{ transform:translateY(-1px); }}
.btn.primary {{ color:#fff !important; background:var(--orange); }}
.btn.dark {{
    color:#fff !important;
    border:1px solid #3a3a3a;
    background:#171717;
}}
.signal-row {{
    display:flex;
    gap:9px;
    flex-wrap:wrap;
    margin-top:22px;
}}
.signal {{
    padding:7px 10px;
    border:1px solid #343434;
    border-radius:999px;
    color:#e7e7e7;
    background:#161616;
    font-size:.79rem;
    font-weight:750;
}}
.hero-photo {{
    min-height:620px;
    background:
        linear-gradient(90deg, rgba(8,8,8,.50), rgba(8,8,8,.05) 42%),
        url("{hero_img}") center 30%/cover no-repeat;
    position:relative;
}}
.hero-photo::after {{
    content:"";
    position:absolute;
    inset:0;
    background:linear-gradient(0deg, rgba(0,0,0,.36), transparent 45%);
}}
.profile-badge {{
    position:absolute;
    z-index:3;
    left:25px; right:25px; bottom:25px;
    padding:15px 17px;
    color:#fff;
    border-radius:14px;
    background:rgba(7,7,7,.82);
    border:1px solid rgba(255,255,255,.13);
    border-left:4px solid var(--orange);
    backdrop-filter:blur(9px);
    font-size:.91rem;
    line-height:1.45;
}}
.profile-badge b {{ font-size:1rem; }}

.floatnav {{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:13px;
    margin:-33px 18px 0 18px;
    position:relative;
    z-index:8;
}}
.float-card {{
    background:#fff;
    border:1px solid var(--border);
    border-radius:17px;
    padding:18px;
    box-shadow:0 14px 30px rgba(0,0,0,.075);
    min-height:120px;
    display:flex;
    gap:14px;
    align-items:flex-start;
}}
.float-icon {{
    min-width:47px;
    height:47px;
    border-radius:12px;
    background:#111;
    display:flex;
    align-items:center;
    justify-content:center;
    color:var(--orange);
    font-size:1.25rem;
    font-weight:900;
}}
.float-card h3 {{
    margin:1px 0 5px 0;
    font-size:1rem;
}}
.float-card p {{
    margin:0;
    color:var(--muted);
    font-size:.85rem;
    line-height:1.43;
}}

.section {{
    padding:64px 8px 12px 8px;
}}
.kicker {{
    color:var(--orange);
    text-transform:uppercase;
    letter-spacing:.09em;
    font-weight:900;
    font-size:.79rem;
    margin-bottom:9px;
}}
.section h2 {{
    margin:0 0 14px 0;
    font-size:clamp(2rem,3.4vw,3.25rem);
    letter-spacing:-.03em;
    line-height:1.04;
}}
.lead {{
    color:var(--muted);
    line-height:1.62;
    font-size:1.01rem;
    max-width:900px;
    margin-bottom:27px;
}}

.route-grid {{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:15px;
}}
.route {{
    border:1px solid var(--border);
    border-radius:18px;
    padding:22px;
    background:#fff;
    box-shadow:0 9px 25px rgba(0,0,0,.045);
    position:relative;
    overflow:hidden;
}}
.route::after {{
    content:"";
    position:absolute;
    width:110px;height:110px;
    border:1px solid rgba(255,105,0,.14);
    border-radius:50%;
    right:-30px;top:-35px;
}}
.route-icon {{
    width:52px;height:52px;
    border-radius:14px;
    background:#111;
    color:var(--orange);
    display:flex;align-items:center;justify-content:center;
    font-weight:950;
    font-size:1.18rem;
    margin-bottom:16px;
}}
.route h3 {{ margin:0 0 7px 0; font-size:1.15rem; }}
.route ul {{
    margin:0;
    padding-left:17px;
    color:var(--muted);
    font-size:.89rem;
    line-height:1.52;
}}
.route a {{
    display:inline-block;
    margin-top:14px;
    color:#111 !important;
    text-decoration:none !important;
    font-weight:850;
    font-size:.89rem;
}}
.route a:hover {{ color:var(--orange) !important; }}

.labbar {{
    border-radius:20px;
    padding:25px;
    background:#0c0c0c;
    display:grid;
    grid-template-columns:1.25fr repeat(4,.75fr);
    gap:10px;
    align-items:center;
    color:#fff;
}}
.labbar-main h3 {{ margin:0 0 6px 0;color:#fff;font-size:1.20rem; }}
.labbar-main p {{ margin:0;color:#bcbcbc;font-size:.88rem;line-height:1.45; }}
.labmetric {{
    border-left:1px solid #2e2e2e;
    padding-left:15px;
}}
.labmetric .symbol {{
    color:var(--orange);
    font-size:1.25rem;
    font-weight:950;
}}
.labmetric .txt {{
    color:#d8d8d8;
    font-size:.78rem;
    margin-top:3px;
}}

.tools-grid {{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:16px;
}}
.tool {{
    border:1px solid var(--border);
    border-radius:20px;
    background:#fff;
    min-height:320px;
    padding:22px;
    box-shadow:0 10px 28px rgba(0,0,0,.055);
    display:flex;
    flex-direction:column;
    transition:.16s ease;
}}
.tool:hover {{
    transform:translateY(-3px);
    box-shadow:0 15px 34px rgba(0,0,0,.075);
    border-color:#d7d7d2;
}}
.tool-head {{
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin-bottom:17px;
}}
.tool-symbol {{
    width:56px;height:56px;border-radius:15px;
    display:flex;align-items:center;justify-content:center;
    background:#111;
    color:var(--orange);
    font-size:1.25rem;
    font-weight:950;
}}
.tool-status {{
    color:#4e5358;
    background:#f5f5f2;
    border-radius:999px;
    padding:6px 9px;
    font-size:.72rem;
    font-weight:800;
}}
.tool h3 {{ margin:0 0 8px 0; font-size:1.2rem; }}
.tool p {{
    color:var(--muted);
    font-size:.89rem;
    line-height:1.5;
    margin:0 0 14px 0;
}}
.tags {{
    display:flex;
    flex-wrap:wrap;
    gap:7px;
    margin-bottom:13px;
}}
.tags span {{
    background:#f6f6f3;
    color:#555a60;
    border-radius:999px;
    padding:6px 8px;
    font-size:.73rem;
    font-weight:700;
}}
.tool-links {{ margin-top:auto; }}
.tool-links a {{
    display:block;
    text-decoration:none !important;
    color:#111 !important;
    font-size:.88rem;
    font-weight:850;
    margin-top:8px;
}}
.tool-links a:hover {{ color:var(--orange) !important; }}

.workflow {{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:14px;
}}
.flow {{
    border:1px solid var(--border);
    border-radius:18px;
    padding:22px;
    background:linear-gradient(180deg,#fff,#fafaf8);
}}
.flow-num {{
    width:39px;height:39px;
    border-radius:10px;
    display:flex;align-items:center;justify-content:center;
    color:var(--orange);
    background:#111;
    font-weight:950;
    margin-bottom:14px;
}}
.flow h3 {{ margin:0 0 7px 0; font-size:1.07rem; }}
.flow p {{ margin:0;color:var(--muted);font-size:.88rem;line-height:1.5; }}

.vision {{
    display:grid;
    grid-template-columns:.84fr 1.16fr;
    border-radius:22px;
    overflow:hidden;
    background:#0b0b0b;
}}
.vision-photo {{
    min-height:520px;
    background:url("{field_img}") center center/cover no-repeat;
}}
.vision-copy {{
    padding:52px 54px;
    background:
        radial-gradient(circle at 90% 12%,rgba(255,105,0,.12),transparent 31%),
        #0b0b0b;
    display:flex;
    flex-direction:column;
    justify-content:center;
}}
.vision h2 {{ color:#fff; }}
.vision p {{
    color:#cfcfcf;
    font-size:.98rem;
    line-height:1.61;
    margin:0 0 13px 0;
}}
.quote {{
    color:#fff !important;
    border-left:4px solid var(--orange);
    padding-left:16px;
    font-weight:720;
}}
.badges {{
    display:flex;gap:8px;flex-wrap:wrap;margin-top:15px;
}}
.badges span {{
    border:1px solid #343434;
    background:#171717;
    color:#fff;
    border-radius:999px;
    padding:8px 10px;
    font-size:.78rem;
    font-weight:750;
}}

.about {{
    display:grid;
    grid-template-columns:.82fr 1.18fr;
    gap:25px;
}}
.about-photo {{
    min-height:430px;
    border-radius:20px;
    overflow:hidden;
    padding:23px;
    color:#fff;
    display:flex;
    align-items:flex-end;
    background:
        linear-gradient(180deg,transparent 38%,rgba(0,0,0,.76)),
        url("{industry_img}") center 20%/cover no-repeat;
}}
.about-copy {{
    border:1px solid var(--border);
    border-radius:20px;
    padding:32px 34px;
    background:#fff;
}}
.role {{
    color:var(--orange);
    font-weight:850;
    margin-bottom:15px;
}}
.about-copy p {{ color:#565b60;line-height:1.58;margin:0 0 12px 0; }}
.skills {{
    display:grid;
    grid-template-columns:repeat(2,1fr);
    gap:8px;
    margin-top:17px;
}}
.skills span {{
    background:#f5f5f3;
    border-radius:10px;
    padding:9px 11px;
    font-size:.82rem;
    font-weight:750;
}}

.gallery {{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:15px;
}}
.gcard {{
    min-height:340px;
    border-radius:18px;
    overflow:hidden;
    position:relative;
    background:#111;
}}
.gcard img {{ width:100%;height:100%;object-fit:cover;display:block; }}
.gcap {{
    position:absolute;
    left:0;right:0;bottom:0;
    padding:42px 18px 17px 18px;
    color:#fff;
    font-weight:850;
    background:linear-gradient(transparent,rgba(0,0,0,.9));
}}

.contact {{
    margin-top:60px;
    border-radius:22px;
    background:#080808;
    color:#fff;
    padding:40px;
}}
.contact h2 {{ color:#fff;margin-bottom:8px; }}
.contact p {{ color:#c9c9c9;line-height:1.55;max-width:880px; }}
.socials {{
    display:grid;
    grid-template-columns:repeat(5,1fr);
    gap:9px;
    margin-top:22px;
}}
.socials a {{
    text-decoration:none !important;
    color:#fff !important;
    border:1px solid #303030;
    background:#151515;
    border-radius:12px;
    padding:13px 12px;
    min-height:67px;
    font-size:.80rem;
    line-height:1.35;
}}
.socials a:hover {{ border-color:var(--orange); }}
.socials b {{ color:var(--orange);display:block;margin-bottom:4px; }}

.footer {{
    display:flex;
    justify-content:space-between;
    gap:16px;
    flex-wrap:wrap;
    color:#7a7a7a;
    font-size:.80rem;
    padding:20px 5px 3px 5px;
}}

@media(max-width:1100px) {{
    .hero,.vision,.about {{ grid-template-columns:1fr; }}
    .hero-photo {{ min-height:470px; }}
    .floatnav,.tools-grid {{ grid-template-columns:repeat(2,1fr); }}
    .route-grid,.workflow,.gallery {{ grid-template-columns:1fr 1fr; }}
    .labbar {{ grid-template-columns:1fr 1fr; }}
    .socials {{ grid-template-columns:1fr 1fr; }}
}}
@media(max-width:700px) {{
    .hero-copy {{ padding:40px 24px; }}
    .floatnav,.route-grid,.tools-grid,.workflow,.gallery,.skills,.socials,.labbar {{
        grid-template-columns:1fr;
    }}
    .floatnav {{ margin:14px 0 0 0; }}
    .vision-copy,.about-copy,.contact {{ padding:28px 22px; }}
}}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="landing">

  <section class="hero">
    <div class="hero-copy">
      <div class="brandbar">
        <img src="{logo_img}" alt="GG DIMEC">
        <div>
          <div class="brandname">GG DIMEC SPA · MECHLAB</div>
          <div class="brandline">Tecnología avanzada en soluciones reales · aprendizaje aplicado</div>
        </div>
      </div>

      <div class="eyebrow">Ingeniería visual aplicada</div>
      <h1>Entiende la ingeniería.<br><em>Luego úsala mejor.</em></h1>

      <p class="hero-lead">
        Herramientas interactivas para estudiar, enseñar y revisar conceptos de ingeniería mecánica
        con apoyo visual, ecuaciones y lectura física del resultado.
      </p>

      <div class="hero-promise">
        MechLab conecta fundamentos, visualización y experiencia industrial para ayudarte
        a desarrollar criterio técnico, no solo a obtener respuestas.
      </div>

      <div class="ctas">
        <a class="btn primary" href="#herramientas">Explorar herramientas ↓</a>
        <a class="btn dark" href="https://www.gerardogaraydimec.com/" target="_blank">Conocer GG DIMEC ↗</a>
      </div>

      <div class="signal-row">
        <span class="signal">Estudiantes</span>
        <span class="signal">Docentes</span>
        <span class="signal">Ingenieros</span>
        <span class="signal">Industria</span>
      </div>
    </div>

    <div class="hero-photo">
      <div class="profile-badge">
        <b>Gerardo Garay Pereira</b><br>
        Ingeniero Civil Mecánico · Docente · Fundador de GG DIMEC SPA
      </div>
    </div>
  </section>

  <section class="floatnav">
    <div class="float-card">
      <div class="float-icon">σ</div>
      <div><h3>Visualiza</h3><p>Convierte ecuaciones en estados, geometría y comportamiento observable.</p></div>
    </div>
    <div class="float-card">
      <div class="float-icon">∑</div>
      <div><h3>Analiza</h3><p>Cambia variables y entiende por qué cambia la respuesta del modelo.</p></div>
    </div>
    <div class="float-card">
      <div class="float-icon">⚙</div>
      <div><h3>Aplica</h3><p>Conecta los fundamentos con problemas propios del diseño y la industria.</p></div>
    </div>
    <div class="float-card">
      <div class="float-icon">↗</div>
      <div><h3>Crece</h3><p>Refuerza criterio técnico y construye una forma más sólida de pensar ingeniería.</p></div>
    </div>
  </section>

  <section class="section">
    <div class="kicker">Elige tu ruta</div>
    <h2>MechLab se adapta a cómo quieres aprender</h2>
    <div class="route-grid">
      <div class="route">
        <div class="route-icon">🎓</div>
        <h3>Estoy estudiando</h3>
        <ul>
          <li>Refuerza fundamentos.</li>
          <li>Explora gráficos y ecuaciones.</li>
          <li>Comprueba cómo responden las variables.</li>
        </ul>
        <a href="#herramientas">Ir a herramientas →</a>
      </div>
      <div class="route">
        <div class="route-icon">▣</div>
        <h3>Estoy enseñando</h3>
        <ul>
          <li>Apoya clases con recursos visuales.</li>
          <li>Explica fenómenos de forma interactiva.</li>
          <li>Conecta modelo, ecuación e interpretación.</li>
        </ul>
        <a href="#herramientas">Explorar módulos →</a>
      </div>
      <div class="route">
        <div class="route-icon">🏭</div>
        <h3>Estoy trabajando</h3>
        <ul>
          <li>Revisa conceptos de forma rápida.</li>
          <li>Apoya comunicación técnica.</li>
          <li>Conecta fundamentos con ingeniería aplicada.</li>
        </ul>
        <a href="https://www.gerardogaraydimec.com/" target="_blank">Ver GG DIMEC →</a>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="labbar">
      <div class="labbar-main">
        <h3>MechLab en una mirada</h3>
        <p>Un laboratorio digital para aprender desde distintos enfoques de la ingeniería mecánica.</p>
      </div>
      <div class="labmetric"><div class="symbol">σ</div><div class="txt">Esfuerzos y resistencia</div></div>
      <div class="labmetric"><div class="symbol">ω</div><div class="txt">Vibraciones y dinámica</div></div>
      <div class="labmetric"><div class="symbol">T–s</div><div class="txt">Termodinámica</div></div>
      <div class="labmetric"><div class="symbol">VM</div><div class="txt">Diseño y falla</div></div>
    </div>
  </section>

  <div id="herramientas"></div>
  <section class="section">
    <div class="kicker">Herramientas disponibles</div>
    <h2>Entra directo al fenómeno que quieres estudiar</h2>
    <div class="lead">
      Menos navegación y más trabajo: cada área reúne herramientas enfocadas en visualizar,
      modificar condiciones y comprender la respuesta física.
    </div>

    <div class="tools-grid">
      <div class="tool">
        <div class="tool-head"><div class="tool-symbol">σ</div><div class="tool-status">Resistencia</div></div>
        <h3>Resistencia de Materiales</h3>
        <p>Transformación de esfuerzos, tensiones principales, estados 2D y 3D y lectura del tensor.</p>
        <div class="tags"><span>Mohr 2D</span><span>Mohr 3D</span><span>Principales</span></div>
        <div class="tool-links">
          <a href="/mohr-2d">Círculo de Mohr 2D →</a>
          <a href="/mohr-3d">Círculo de Mohr 3D →</a>
        </div>
      </div>

      <div class="tool">
        <div class="tool-head"><div class="tool-symbol">ω</div><div class="tool-status">Dinámica</div></div>
        <h3>Vibraciones y Dinámica</h3>
        <p>Respuesta libre y forzada, frecuencia natural, amortiguamiento, resonancia y transmisibilidad.</p>
        <div class="tags"><span>1-GDL</span><span>Respuesta</span><span>Frecuencia</span></div>
        <div class="tool-links">
          <a href="/vibraciones-1gdl">Vibraciones libres 1-GDL →</a>
          <a href="/vibracion-forzada-1gdl">Vibración forzada 1-GDL →</a>
        </div>
      </div>

      <div class="tool">
        <div class="tool-head"><div class="tool-symbol">T–s</div><div class="tool-status">Energía</div></div>
        <h3>Termodinámica</h3>
        <p>Estados del agua y vapor, regiones termodinámicas, diagramas y ciclos de potencia o refrigeración.</p>
        <div class="tags"><span>Agua-vapor</span><span>Ciclos</span><span>Diagramas</span></div>
        <div class="tool-links">
          <a href="/agua-vapor">Propiedades del agua y vapor →</a>
          <a href="/ciclos-termodinamicos">Ciclos termodinámicos →</a>
        </div>
      </div>

      <div class="tool">
        <div class="tool-head"><div class="tool-symbol">VM</div><div class="tool-status">Diseño</div></div>
        <h3>Elementos de Máquinas</h3>
        <p>Criterios de fluencia, esfuerzo equivalente, comparación con Tresca y geometría del estado multiaxial.</p>
        <div class="tags"><span>Von Mises</span><span>Tresca</span><span>Falla</span></div>
        <div class="tool-links">
          <a href="/von-mises">Abrir Von Mises Lab →</a>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="kicker">Cómo trabajar</div>
    <h2>Tres pasos. Mucho más criterio.</h2>
    <div class="workflow">
      <div class="flow"><div class="flow-num">1</div><h3>Define el problema</h3><p>Selecciona la herramienta y configura las condiciones que quieres estudiar.</p></div>
      <div class="flow"><div class="flow-num">2</div><h3>Explora la respuesta</h3><p>Mueve variables, compara escenarios y observa gráficos, estados y ecuaciones.</p></div>
      <div class="flow"><div class="flow-num">3</div><h3>Interpreta</h3><p>Usa la lectura física para entender qué significa el resultado y cómo se conecta con ingeniería real.</p></div>
    </div>
  </section>

  <section class="section">
    <div class="vision">
      <div class="vision-photo"></div>
      <div class="vision-copy">
        <div class="kicker">Mi visión</div>
        <h2>Aprender con ingeniería real</h2>
        <p>
          GG DIMEC nació desde la ingeniería aplicada y del trabajo con problemas reales.
          Esa misma lógica quiero llevar al aprendizaje: comprender, modelar, visualizar, cuestionar y mejorar.
        </p>
        <p class="quote">
          Quiero que MechLab ayude a estudiantes e ingenieros a aprender mejor y a desarrollar una forma
          más clara, rigurosa y útil de pensar la ingeniería.
        </p>
        <div class="badges">
          <span>Industria real</span><span>Docencia</span><span>Simulación</span><span>Diseño mecánico</span><span>Aprendizaje continuo</span>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="kicker">Sobre mí</div>
    <div class="about">
      <div class="about-photo">
        <div><b>Ingeniería en terreno</b><br>Experiencia técnica, industria y aprendizaje conectado con la realidad.</div>
      </div>
      <div class="about-copy">
        <h2>Gerardo Garay Pereira</h2>
        <div class="role">Ingeniero Civil Mecánico · Docente · Fundador de GG DIMEC SPA</div>
        <p>
          Trabajo en diseño mecánico, simulación, levantamiento 3D, análisis de equipos y formación técnica.
          Me interesa traducir problemas complejos en soluciones claras y aplicables.
        </p>
        <p>
          MechLab nace como una extensión de esa visión: compartir herramientas que ayuden a estudiar,
          enseñar y seguir creciendo profesionalmente.
        </p>
        <div class="skills">
          <span>Diseño mecánico</span><span>Simulación FEM / CFD</span>
          <span>Escaneo 3D</span><span>Ingeniería inversa</span>
          <span>Docencia</span><span>Capacitación técnica</span>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="kicker">Ingeniería aplicada</div>
    <h2>De la industria a la enseñanza</h2>
    <div class="lead">
      La experiencia de GG DIMEC alimenta MechLab: modelamiento, simulación, digitalización 3D y transferencia de conocimiento.
    </div>
    <div class="gallery">
      <div class="gcard"><img src="{sim_img}" alt="Simulación"><div class="gcap">Simulación estructural y dinámica</div></div>
      <div class="gcard"><img src="{scan_img}" alt="Escaneo 3D"><div class="gcap">Escaneo 3D e ingeniería inversa</div></div>
      <div class="gcard"><img src="{train_img}" alt="Capacitación"><div class="gcap">Capacitación y transferencia de conocimiento</div></div>
    </div>
  </section>

  <section class="contact">
    <div class="kicker">Contacto y comunidad</div>
    <h2>Sigamos construyendo mejor ingeniería</h2>
    <p>
      Si eres estudiante, docente, ingeniero o empresa, puedes seguir mi trabajo,
      revisar GG DIMEC y conversar conmigo sobre aprendizaje, ingeniería y colaboración.
    </p>
    <div class="socials">
      <a href="mailto:gerardogaray.dimec@gmail.com"><b>Correo</b>gerardogaray.dimec@gmail.com</a>
      <a href="tel:+56957288516"><b>Teléfono</b>+56 9 5728 8516</a>
      <a href="https://www.instagram.com/gerardogaray.dimec/" target="_blank"><b>Instagram</b>@gerardogaray.dimec</a>
      <a href="https://www.linkedin.com/in/gerardo-garay-pereira/" target="_blank"><b>LinkedIn</b>Gerardo Garay Pereira</a>
      <a href="https://www.gerardogaraydimec.com/" target="_blank"><b>Web</b>www.gerardogaraydimec.com</a>
    </div>
  </section>

  <div class="footer">
    <span>GG DIMEC SPA · Gerardo Garay Pereira · Chile</span>
    <span>MechLab Premium Landing V1.2</span>
  </div>

</div>
""",
    unsafe_allow_html=True,
)
