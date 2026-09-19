
from __future__ import annotations

from pathlib import Path
import base64
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

ORANGE = "#ff6900"
BLACK = "#0b0b0b"
CHARCOAL = "#171717"
SOFT = "#f6f6f6"
MUTED = "#6f7379"


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
train_img = data_uri(ASSETS / "brochure_formacion.jpg")

st.markdown(
    f"""
    <style>
    .block-container {{
        max-width: 1480px;
        padding-top: .8rem;
        padding-bottom: 2.5rem;
    }}
    .stApp {{ background:#ffffff; color:{BLACK}; }}
    h1,h2,h3,h4 {{ color:{BLACK}; }}

    .landing-shell {{
        width:100%;
        overflow:hidden;
        border-radius:22px;
        background:#fff;
    }}

    .hero {{
        position:relative;
        display:grid;
        grid-template-columns: 1.12fr .88fr;
        min-height:560px;
        background:
            radial-gradient(circle at 22% 18%, rgba(255,105,0,.20), transparent 28%),
            linear-gradient(135deg,#050505 0%,#101010 58%,#1b1b1b 100%);
        border-radius:22px;
        overflow:hidden;
        box-shadow:0 18px 50px rgba(0,0,0,.14);
    }}
    .hero:after {{
        content:"";
        position:absolute;
        right:-130px;
        top:-150px;
        width:390px;
        height:390px;
        border:1px solid rgba(255,105,0,.28);
        border-radius:50%;
        box-shadow:0 0 0 48px rgba(255,105,0,.04), 0 0 0 96px rgba(255,105,0,.025);
        pointer-events:none;
    }}
    .hero-copy {{
        padding:64px 56px 58px 58px;
        z-index:2;
        display:flex;
        flex-direction:column;
        justify-content:center;
    }}
    .brand-row {{
        display:flex;
        align-items:center;
        gap:14px;
        margin-bottom:26px;
    }}
    .brand-row img {{
        width:86px;
        height:auto;
        border-radius:10px;
        background:#fffaf5;
    }}
    .brand-row .brandtext {{
        color:#fff;
        font-weight:800;
        letter-spacing:.04em;
        font-size:1.05rem;
    }}
    .brand-row .brandsub {{
        color:#aeb2b8;
        font-size:.82rem;
        margin-top:2px;
    }}
    .eyebrow {{
        display:inline-block;
        color:{ORANGE};
        font-weight:800;
        letter-spacing:.08em;
        text-transform:uppercase;
        font-size:.84rem;
        margin-bottom:10px;
    }}
    .hero h1 {{
        color:#fff;
        font-size:clamp(2.6rem,4.6vw,4.8rem);
        line-height:.98;
        margin:0 0 22px 0;
        letter-spacing:-.035em;
    }}
    .hero h1 span {{ color:{ORANGE}; }}
    .hero p {{
        color:#d7d9dc;
        font-size:1.10rem;
        line-height:1.60;
        max-width:760px;
        margin:0 0 18px 0;
    }}
    .hero-vision {{
        border-left:4px solid {ORANGE};
        padding-left:17px;
        color:#fff !important;
        font-weight:600;
        margin-top:4px !important;
        max-width:720px;
    }}
    .cta-row {{
        display:flex;
        gap:12px;
        flex-wrap:wrap;
        margin-top:22px;
    }}
    .cta {{
        display:inline-block;
        padding:13px 19px;
        border-radius:11px;
        text-decoration:none !important;
        font-weight:800;
        font-size:.96rem;
        transition:.18s ease;
    }}
    .cta.primary {{ background:{ORANGE}; color:#fff !important; }}
    .cta.secondary {{
        border:1px solid rgba(255,255,255,.34);
        color:#fff !important;
        background:rgba(255,255,255,.04);
    }}
    .cta:hover {{ transform:translateY(-1px); filter:brightness(1.04); }}
    .audience {{
        display:flex;
        gap:10px;
        flex-wrap:wrap;
        margin-top:26px;
    }}
    .pill {{
        color:#fff;
        background:#1d1d1d;
        border:1px solid #323232;
        border-radius:999px;
        padding:8px 12px;
        font-size:.86rem;
        font-weight:700;
    }}

    .hero-photo {{
        min-height:560px;
        position:relative;
        background:
            linear-gradient(90deg,rgba(11,11,11,.45),rgba(11,11,11,.02)),
            url("{hero_img}") center 34%/cover no-repeat;
    }}
    .hero-photo .badge {{
        position:absolute;
        right:26px;
        bottom:28px;
        left:26px;
        background:rgba(10,10,10,.80);
        backdrop-filter:blur(8px);
        border:1px solid rgba(255,255,255,.14);
        border-left:4px solid {ORANGE};
        border-radius:14px;
        color:#fff;
        padding:16px 18px;
        font-size:.94rem;
        line-height:1.45;
    }}

    .section {{
        padding:68px 8px 12px 8px;
    }}
    .section.dark {{
        margin-top:54px;
        background:{BLACK};
        color:#fff;
        border-radius:22px;
        padding:0;
        overflow:hidden;
    }}
    .section-kicker {{
        color:{ORANGE};
        font-weight:800;
        letter-spacing:.07em;
        text-transform:uppercase;
        font-size:.82rem;
        margin-bottom:8px;
    }}
    .section h2 {{
        font-size:clamp(2rem,3.4vw,3.25rem);
        line-height:1.05;
        margin:0 0 15px 0;
        letter-spacing:-.025em;
    }}
    .section-intro {{
        max-width:900px;
        color:{MUTED};
        font-size:1.04rem;
        line-height:1.65;
        margin-bottom:30px;
    }}

    .benefits {{
        display:grid;
        grid-template-columns:repeat(4,1fr);
        gap:14px;
    }}
    .benefit {{
        border:1px solid #e7e7e7;
        background:#fff;
        border-radius:16px;
        padding:21px 20px;
        box-shadow:0 8px 24px rgba(0,0,0,.045);
    }}
    .benefit .num {{
        color:{ORANGE};
        font-weight:900;
        font-size:1.05rem;
        margin-bottom:10px;
    }}
    .benefit h3 {{
        margin:0 0 8px 0;
        font-size:1.08rem;
    }}
    .benefit p {{
        color:{MUTED};
        font-size:.92rem;
        line-height:1.55;
        margin:0;
    }}

    .tools-grid {{
        display:grid;
        grid-template-columns:repeat(4,1fr);
        gap:16px;
        margin-top:18px;
    }}
    .tool-card {{
        border-radius:18px;
        border:1px solid #e3e3e3;
        background:#fff;
        padding:22px;
        box-shadow:0 9px 28px rgba(0,0,0,.05);
        min-height:245px;
        display:flex;
        flex-direction:column;
    }}
    .tool-icon {{
        width:48px;height:48px;
        border-radius:12px;
        display:flex;align-items:center;justify-content:center;
        background:{BLACK};
        color:{ORANGE};
        font-weight:900;
        font-size:1.22rem;
        margin-bottom:17px;
    }}
    .tool-card h3 {{ margin:0 0 9px 0; font-size:1.22rem; }}
    .tool-card p {{
        color:{MUTED};
        line-height:1.55;
        font-size:.92rem;
        flex:1;
        margin-bottom:16px;
    }}
    .tool-links a {{
        display:block;
        color:{BLACK} !important;
        font-weight:800;
        text-decoration:none !important;
        margin-top:8px;
        font-size:.91rem;
    }}
    .tool-links a:hover {{ color:{ORANGE} !important; }}

    .vision {{
        display:grid;
        grid-template-columns:.84fr 1.16fr;
        min-height:520px;
    }}
    .vision-photo {{
        background:url("{field_img}") center center/cover no-repeat;
        min-height:520px;
    }}
    .vision-copy {{
        padding:56px 58px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        background:
            radial-gradient(circle at 88% 18%, rgba(255,105,0,.13), transparent 30%),
            #0c0c0c;
    }}
    .vision-copy h2 {{ color:#fff; }}
    .vision-copy p {{
        color:#d0d0d0;
        font-size:1.02rem;
        line-height:1.66;
        margin:0 0 15px 0;
    }}
    .vision-quote {{
        color:#fff !important;
        border-left:4px solid {ORANGE};
        padding-left:17px;
        font-weight:700;
        margin-top:8px !important;
    }}
    .vision-tags {{
        display:flex;gap:10px;flex-wrap:wrap;margin-top:18px;
    }}
    .vision-tags span {{
        border:1px solid #333;
        background:#181818;
        color:#fff;
        padding:9px 12px;
        border-radius:999px;
        font-size:.86rem;
        font-weight:700;
    }}

    .about {{
        display:grid;
        grid-template-columns:.82fr 1.18fr;
        gap:28px;
        align-items:stretch;
    }}
    .about-card {{
        background:#111;
        border-radius:20px;
        overflow:hidden;
        min-height:430px;
        background:
            linear-gradient(180deg,rgba(11,11,11,.05),rgba(11,11,11,.72)),
            url("{industry_img}") center 20%/cover no-repeat;
        display:flex;
        align-items:flex-end;
        padding:24px;
        color:#fff;
    }}
    .about-card strong {{ font-size:1.18rem; }}
    .about-copy {{
        border:1px solid #e6e6e6;
        border-radius:20px;
        padding:34px 36px;
        background:#fff;
    }}
    .about-copy h2 {{ margin-bottom:8px; }}
    .about-copy .role {{
        color:{ORANGE};
        font-weight:800;
        margin-bottom:17px;
    }}
    .about-copy p {{
        color:#555b62;
        line-height:1.62;
        margin-bottom:14px;
    }}
    .skills {{
        display:grid;
        grid-template-columns:repeat(2,1fr);
        gap:9px;
        margin-top:18px;
    }}
    .skills span {{
        background:#f6f6f6;
        border-radius:10px;
        padding:10px 12px;
        font-size:.88rem;
        font-weight:700;
    }}

    .industry-gallery {{
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:16px;
        margin-top:22px;
    }}
    .industry-card {{
        border-radius:18px;
        overflow:hidden;
        background:#111;
        position:relative;
        min-height:340px;
        box-shadow:0 9px 28px rgba(0,0,0,.07);
    }}
    .industry-card img {{
        width:100%;height:100%;object-fit:cover;display:block;
    }}
    .industry-card .overlay {{
        position:absolute;left:0;right:0;bottom:0;
        padding:38px 18px 17px 18px;
        background:linear-gradient(transparent,rgba(0,0,0,.88));
        color:#fff;
        font-weight:800;
        font-size:1rem;
    }}

    .contact {{
        background:{BLACK};
        border-radius:22px;
        margin-top:64px;
        padding:42px 42px 30px 42px;
        color:#fff;
    }}
    .contact h2 {{ color:#fff; margin-bottom:9px; }}
    .contact p {{ color:#c9c9c9; line-height:1.6; max-width:900px; }}
    .contact-grid {{
        display:grid;
        grid-template-columns:repeat(5,1fr);
        gap:10px;
        margin-top:24px;
    }}
    .contact-grid a {{
        text-decoration:none !important;
        color:#fff !important;
        background:#171717;
        border:1px solid #303030;
        border-radius:13px;
        padding:14px 13px;
        font-size:.84rem;
        line-height:1.35;
        min-height:70px;
    }}
    .contact-grid a:hover {{ border-color:{ORANGE}; }}
    .contact-grid b {{ color:{ORANGE}; display:block; margin-bottom:4px; }}

    .footer {{
        display:flex;
        justify-content:space-between;
        gap:20px;
        align-items:center;
        padding:22px 4px 4px 4px;
        color:#777;
        font-size:.82rem;
        flex-wrap:wrap;
    }}

    @media(max-width:1000px) {{
        .hero {{ grid-template-columns:1fr; }}
        .hero-photo {{ min-height:470px; }}
        .benefits,.tools-grid {{ grid-template-columns:repeat(2,1fr); }}
        .vision,.about {{ grid-template-columns:1fr; }}
        .vision-photo {{ min-height:440px; }}
        .industry-gallery {{ grid-template-columns:1fr 1fr; }}
        .contact-grid {{ grid-template-columns:1fr 1fr; }}
    }}
    @media(max-width:650px) {{
        .hero-copy {{ padding:42px 26px; }}
        .hero-photo {{ min-height:420px; }}
        .benefits,.tools-grid,.industry-gallery,.contact-grid,.skills {{
            grid-template-columns:1fr;
        }}
        .vision-copy,.about-copy,.contact {{ padding:32px 24px; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="landing-shell">
      <section class="hero">
        <div class="hero-copy">
          <div class="brand-row">
            <img src="{logo_img}" alt="GG DIMEC">
            <div>
              <div class="brandtext">GG DIMEC SPA · MECHLAB</div>
              <div class="brandsub">Ingeniería, aprendizaje y aplicación real</div>
            </div>
          </div>
          <div class="eyebrow">Ingeniería visual aplicada</div>
          <h1>Aprende, analiza y diseña con <span>criterio técnico</span></h1>
          <p>
            MechLab es un espacio de herramientas interactivas para estudiantes, docentes e ingenieros
            que quieren comprender mejor la mecánica, la termodinámica, las vibraciones y el diseño de máquinas.
          </p>
          <p class="hero-vision">
            Quiero acompañarte a aprender mejor, visualizar lo que estás estudiando y desarrollar una forma
            de pensar la ingeniería más clara, rigurosa y conectada con problemas reales.
          </p>
          <div class="cta-row">
            <a class="cta primary" href="#herramientas">Explorar herramientas ↓</a>
            <a class="cta secondary" href="https://www.gerardogaraydimec.com/" target="_blank">Visitar mi página web ↗</a>
          </div>
          <div class="audience">
            <span class="pill">Para estudiantes</span>
            <span class="pill">Para docentes</span>
            <span class="pill">Para ingenieros</span>
          </div>
        </div>
        <div class="hero-photo">
          <div class="badge">
            <b>Gerardo Garay Pereira</b><br>
            Ingeniero Civil Mecánico · Docente · Fundador de GG DIMEC SPA
          </div>
        </div>
      </section>

      <section class="section">
        <div class="section-kicker">¿Para qué sirve MechLab?</div>
        <h2>Una herramienta para entender mejor la ingeniería</h2>
        <div class="section-intro">
          No busca reemplazar los fundamentos. Busca ayudarte a verlos, explorarlos y conectarlos:
          ecuaciones, estados, geometría, respuesta de sistemas y criterios de diseño, reunidos en herramientas
          que puedas utilizar para estudiar, enseñar o profundizar un análisis.
        </div>
        <div class="benefits">
          <div class="benefit"><div class="num">01</div><h3>Visualizar conceptos</h3><p>Representaciones interactivas para entender variables, estados y fenómenos complejos.</p></div>
          <div class="benefit"><div class="num">02</div><h3>Aprender con criterio</h3><p>Ecuaciones, explicaciones y análisis para avanzar más allá de una respuesta numérica.</p></div>
          <div class="benefit"><div class="num">03</div><h3>Practicar análisis</h3><p>Modifica condiciones, compara resultados y estudia cómo responde el modelo.</p></div>
          <div class="benefit"><div class="num">04</div><h3>Conectar teoría y realidad</h3><p>Una mirada construida desde la docencia, el diseño mecánico y la experiencia industrial.</p></div>
        </div>
      </section>

      <div id="herramientas"></div>
      <section class="section">
        <div class="section-kicker">Herramientas disponibles</div>
        <h2>Empieza a trabajar con MechLab</h2>
        <div class="section-intro">
          Cada módulo está pensado para que puedas modificar datos, visualizar resultados y entender qué significa físicamente lo que estás calculando.
        </div>
        <div class="tools-grid">
          <div class="tool-card">
            <div class="tool-icon">RM</div>
            <h3>Resistencia de Materiales</h3>
            <p>Transformación de esfuerzos, estados principales, visualización 2D y 3D y análisis tensorial.</p>
            <div class="tool-links">
              <a href="/mohr-2d">Abrir Círculo de Mohr 2D →</a>
              <a href="/mohr-3d">Abrir Círculo de Mohr 3D →</a>
            </div>
          </div>
          <div class="tool-card">
            <div class="tool-icon">VD</div>
            <h3>Vibraciones y Dinámica</h3>
            <p>Respuesta libre y forzada, frecuencia natural, amortiguamiento, resonancia, fase y transmisibilidad.</p>
            <div class="tool-links">
              <a href="/vibraciones-1gdl">Vibraciones libres 1-GDL →</a>
              <a href="/vibracion-forzada-1gdl">Vibración forzada 1-GDL →</a>
            </div>
          </div>
          <div class="tool-card">
            <div class="tool-icon">TH</div>
            <h3>Termodinámica</h3>
            <p>Propiedades del agua y vapor, regiones de fase, diagramas y análisis de ciclos termodinámicos.</p>
            <div class="tool-links">
              <a href="/agua-vapor">Propiedades del agua y vapor →</a>
              <a href="/ciclos-termodinamicos">Ciclos termodinámicos →</a>
            </div>
          </div>
          <div class="tool-card">
            <div class="tool-icon">EM</div>
            <h3>Elementos de Máquinas</h3>
            <p>Criterios de fluencia y falla, interpretación física, estados multiaxiales y visualización geométrica.</p>
            <div class="tool-links">
              <a href="/von-mises">Abrir Von Mises Lab →</a>
            </div>
          </div>
        </div>
      </section>

      <section class="section dark">
        <div class="vision">
          <div class="vision-photo"></div>
          <div class="vision-copy">
            <div class="section-kicker">Mi visión</div>
            <h2>Aprender con ingeniería real</h2>
            <p>
              GG DIMEC nació desde la ingeniería aplicada y el trabajo con problemas reales.
              Esa misma lógica quiero llevar al aprendizaje: comprender, modelar, visualizar, cuestionar y mejorar.
            </p>
            <p>
              MechLab busca acercar herramientas de análisis a estudiantes y profesionales para que puedan
              reforzar fundamentos, experimentar con variables y desarrollar mejor criterio técnico.
            </p>
            <p class="vision-quote">
              La ingeniería más avanzada tiene sentido cuando ayuda a las personas a resolver mejor los problemas que enfrentan.
            </p>
            <div class="vision-tags">
              <span>Industria real</span><span>Docencia</span><span>Simulación</span><span>Diseño mecánico</span><span>Aprendizaje continuo</span>
            </div>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="section-kicker">Sobre mí</div>
        <div class="about">
          <div class="about-card">
            <div><strong>Ingeniería en terreno</strong><br>Experiencia técnica, industria y aprendizaje conectado con la realidad.</div>
          </div>
          <div class="about-copy">
            <h2>Gerardo Garay Pereira</h2>
            <div class="role">Ingeniero Civil Mecánico · Docente · Fundador de GG DIMEC SPA</div>
            <p>
              Mi trabajo une ingeniería mecánica, análisis, diseño, simulación, levantamiento 3D y formación técnica.
              Me interesa resolver problemas complejos con soluciones claras, confiables y aplicables.
            </p>
            <p>
              A través de MechLab quiero compartir herramientas que sirvan para estudiar, enseñar y seguir creciendo profesionalmente,
              acercando la experiencia de la industria al aprendizaje de ingeniería.
            </p>
            <div class="skills">
              <span>Diseño mecánico</span>
              <span>Simulación FEM / CFD</span>
              <span>Escaneo 3D e ingeniería inversa</span>
              <span>Docencia y capacitación</span>
              <span>Análisis de equipos</span>
              <span>Desarrollo de herramientas técnicas</span>
            </div>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="section-kicker">Ingeniería aplicada</div>
        <h2>De la industria a la enseñanza</h2>
        <div class="section-intro">
          MechLab se alimenta de una forma de trabajar que combina modelamiento, simulación, levantamiento, diseño y capacitación técnica.
          Parte de esa experiencia está reflejada en los proyectos y servicios desarrollados por GG DIMEC.
        </div>
        <div class="industry-gallery">
          <div class="industry-card"><img src="{sim_img}" alt="Simulación estructural"><div class="overlay">Simulación estructural y dinámica</div></div>
          <div class="industry-card"><img src="{scan_img}" alt="Escaneo 3D"><div class="overlay">Escaneo 3D e ingeniería inversa</div></div>
          <div class="industry-card"><img src="{train_img}" alt="Capacitación técnica"><div class="overlay">Capacitación y transferencia de conocimiento</div></div>
        </div>
      </section>

      <section class="contact">
        <div class="section-kicker">Contacto y comunidad</div>
        <h2>Conversemos, aprendamos y construyamos mejor ingeniería</h2>
        <p>
          Si eres estudiante, docente, ingeniero o una empresa interesada en estas herramientas, sígueme en redes,
          revisa el contenido de GG DIMEC y conversemos. La idea es seguir construyendo recursos que ayuden a aprender y trabajar mejor.
        </p>
        <div class="contact-grid">
          <a href="mailto:gerardogaray.dimec@gmail.com"><b>Correo</b>gerardogaray.dimec@gmail.com</a>
          <a href="tel:+56957288516"><b>Teléfono</b>+56 9 5728 8516</a>
          <a href="https://www.instagram.com/gerardogaray.dimec/" target="_blank"><b>Instagram</b>@gerardogaray.dimec</a>
          <a href="https://www.linkedin.com/in/gerardo-garay-pereira/" target="_blank"><b>LinkedIn</b>Gerardo Garay Pereira</a>
          <a href="https://www.gerardogaraydimec.com/" target="_blank"><b>Página web</b>www.gerardogaraydimec.com</a>
        </div>
      </section>

      <div class="footer">
        <span>GG DIMEC SPA · Gerardo Garay Pereira · Chile</span>
        <span>MechLab · Conocimiento · Ingeniería · Personas · Futuro</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
