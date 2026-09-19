
from __future__ import annotations

from pathlib import Path
import base64
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

ORANGE = "#ff6900"
BLACK = "#0b0b0b"
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
        padding-bottom: 2.4rem;
    }}
    .stApp {{ background:#fff; color:{BLACK}; }}
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
        grid-template-columns: 1.1fr .9fr;
        min-height:585px;
        background:
            radial-gradient(circle at 22% 18%, rgba(255,105,0,.19), transparent 29%),
            linear-gradient(135deg,#040404 0%,#101010 60%,#1a1a1a 100%);
        border-radius:22px;
        overflow:hidden;
        box-shadow:0 16px 44px rgba(0,0,0,.14);
    }}
    .hero:after {{
        content:"";
        position:absolute;
        right:-110px;
        top:-120px;
        width:350px;height:350px;
        border-radius:50%;
        border:1px solid rgba(255,105,0,.28);
        box-shadow:0 0 0 46px rgba(255,105,0,.04), 0 0 0 92px rgba(255,105,0,.024);
        pointer-events:none;
    }}
    .hero-copy {{
        padding:62px 56px 56px 58px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        z-index:2;
    }}
    .brand-row {{
        display:flex;
        align-items:center;
        gap:14px;
        margin-bottom:22px;
    }}
    .brand-row img {{
        width:88px;
        height:auto;
        border-radius:10px;
        background:#fffaf5;
    }}
    .brand-title {{
        color:#fff;
        font-weight:800;
        letter-spacing:.04em;
        font-size:1.03rem;
    }}
    .brand-sub {{
        color:#afb3ba;
        font-size:.82rem;
        margin-top:2px;
    }}
    .eyebrow {{
        color:{ORANGE};
        font-weight:800;
        letter-spacing:.08em;
        text-transform:uppercase;
        font-size:.84rem;
        margin-bottom:10px;
    }}
    .hero h1 {{
        color:#fff;
        font-size:clamp(2.65rem,4.8vw,4.9rem);
        line-height:.98;
        margin:0 0 20px 0;
        letter-spacing:-.035em;
    }}
    .hero h1 span {{ color:{ORANGE}; }}
    .hero p {{
        color:#d7d9dd;
        font-size:1.06rem;
        line-height:1.58;
        max-width:760px;
        margin:0 0 14px 0;
    }}
    .hero-vision {{
        border-left:4px solid {ORANGE};
        padding-left:16px;
        color:#fff !important;
        font-weight:600;
        max-width:720px;
    }}
    .cta-row {{
        display:flex;
        gap:12px;
        flex-wrap:wrap;
        margin-top:20px;
    }}
    .cta {{
        display:inline-block;
        padding:13px 19px;
        border-radius:11px;
        text-decoration:none !important;
        font-weight:800;
        font-size:.95rem;
        transition:.16s ease;
    }}
    .cta.primary {{ background:{ORANGE}; color:#fff !important; }}
    .cta.secondary {{
        border:1px solid rgba(255,255,255,.34);
        color:#fff !important;
        background:rgba(255,255,255,.04);
    }}
    .cta:hover {{ transform:translateY(-1px); }}
    .hero-tags {{
        display:flex;
        gap:10px;
        flex-wrap:wrap;
        margin-top:22px;
    }}
    .hero-tags span {{
        color:#fff;
        background:#1a1a1a;
        border:1px solid #343434;
        border-radius:999px;
        padding:8px 12px;
        font-size:.85rem;
        font-weight:700;
    }}
    .hero-photo {{
        min-height:585px;
        position:relative;
        background:
            linear-gradient(90deg,rgba(11,11,11,.44),rgba(11,11,11,.06)),
            url("{hero_img}") center 30%/cover no-repeat;
    }}
    .hero-badge {{
        position:absolute;
        right:24px;
        bottom:26px;
        left:24px;
        background:rgba(10,10,10,.82);
        border:1px solid rgba(255,255,255,.14);
        border-left:4px solid {ORANGE};
        border-radius:14px;
        color:#fff;
        padding:16px 18px;
        line-height:1.42;
        font-size:.93rem;
        backdrop-filter:blur(8px);
    }}

    .section {{
        padding:60px 8px 10px 8px;
    }}
    .section.dark {{
        margin-top:48px;
        background:{BLACK};
        color:#fff;
        border-radius:22px;
        padding:0;
        overflow:hidden;
    }}
    .kicker {{
        color:{ORANGE};
        font-weight:800;
        letter-spacing:.07em;
        text-transform:uppercase;
        font-size:.82rem;
        margin-bottom:8px;
    }}
    .section h2 {{
        font-size:clamp(2rem,3.4vw,3.18rem);
        line-height:1.05;
        margin:0 0 14px 0;
        letter-spacing:-.025em;
    }}
    .section-intro {{
        max-width:920px;
        color:{MUTED};
        font-size:1.02rem;
        line-height:1.63;
        margin-bottom:28px;
    }}

    .icon-strip {{
        display:grid;
        grid-template-columns:repeat(4,1fr);
        gap:14px;
        margin-top:-34px;
        position:relative;
        z-index:5;
        padding:0 14px;
    }}
    .icon-card {{
        background:#fff;
        border:1px solid #e7e7e7;
        border-radius:18px;
        padding:20px 18px;
        box-shadow:0 12px 28px rgba(0,0,0,.06);
        display:flex;
        gap:14px;
        align-items:flex-start;
    }}
    .icon-bubble {{
        width:46px;height:46px;border-radius:12px;
        background:#111; color:{ORANGE};
        display:flex; align-items:center; justify-content:center;
        font-size:1.25rem; font-weight:900; flex:0 0 auto;
    }}
    .icon-card h3 {{ margin:0 0 4px 0; font-size:1.02rem; }}
    .icon-card p {{ margin:0; color:{MUTED}; font-size:.89rem; line-height:1.48; }}

    .quick-grid {{
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:16px;
    }}
    .quick-card {{
        background:#fff;
        border:1px solid #e5e5e5;
        border-radius:18px;
        box-shadow:0 8px 26px rgba(0,0,0,.05);
        padding:22px;
    }}
    .quick-card .qicon {{
        width:54px;height:54px;border-radius:14px;
        background:#111; color:{ORANGE};
        display:flex;align-items:center;justify-content:center;
        font-size:1.35rem; font-weight:900;
        margin-bottom:16px;
    }}
    .quick-card h3 {{ margin:0 0 8px 0; font-size:1.15rem; }}
    .quick-card ul {{
        margin:0; padding-left:18px; color:{MUTED};
        font-size:.91rem; line-height:1.54;
    }}
    .quick-card a {{
        display:inline-block;
        margin-top:14px;
        font-weight:800;
        color:{BLACK} !important;
        text-decoration:none !important;
    }}
    .quick-card a:hover {{ color:{ORANGE} !important; }}

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
        min-height:265px;
        display:flex;
        flex-direction:column;
    }}
    .tool-icon {{
        width:50px;height:50px;border-radius:13px;
        display:flex;align-items:center;justify-content:center;
        background:#111;color:{ORANGE};
        font-weight:900;font-size:1.25rem;margin-bottom:16px;
    }}
    .tool-card h3 {{ margin:0 0 8px 0; font-size:1.18rem; }}
    .tool-card p {{
        color:{MUTED}; line-height:1.55; font-size:.91rem;
        flex:1; margin-bottom:14px;
    }}
    .tool-tags {{
        display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px;
    }}
    .tool-tags span {{
        background:#f7f7f7;
        border-radius:999px;
        padding:6px 9px;
        font-size:.77rem;
        font-weight:700;
        color:#4c4f54;
    }}
    .tool-links a {{
        display:block; color:{BLACK} !important;
        font-weight:800; text-decoration:none !important;
        margin-top:8px; font-size:.9rem;
    }}
    .tool-links a:hover {{ color:{ORANGE} !important; }}

    .steps {{
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:16px;
    }}
    .step {{
        border:1px solid #e7e7e7;
        background:#fff;
        border-radius:18px;
        padding:24px 22px;
        box-shadow:0 8px 24px rgba(0,0,0,.045);
    }}
    .step .num {{
        width:42px;height:42px;border-radius:11px;
        background:#111;color:{ORANGE};
        display:flex;align-items:center;justify-content:center;
        font-weight:900;font-size:1rem;margin-bottom:14px;
    }}
    .step h3 {{ margin:0 0 8px 0; font-size:1.1rem; }}
    .step p {{ margin:0; color:{MUTED}; line-height:1.55; font-size:.91rem; }}

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
        font-size:1.01rem;
        line-height:1.65;
        margin:0 0 14px 0;
    }}
    .vision-quote {{
        color:#fff !important;
        border-left:4px solid {ORANGE};
        padding-left:17px;
        font-weight:700;
        margin-top:8px !important;
    }}
    .vision-tags {{
        display:flex; gap:10px; flex-wrap:wrap; margin-top:18px;
    }}
    .vision-tags span {{
        border:1px solid #333;
        background:#181818;
        color:#fff;
        padding:9px 12px;
        border-radius:999px;
        font-size:.85rem;
        font-weight:700;
    }}

    .about {{
        display:grid;
        grid-template-columns:.82fr 1.18fr;
        gap:28px;
        align-items:stretch;
    }}
    .about-card {{
        border-radius:20px;
        overflow:hidden;
        min-height:430px;
        background:
            linear-gradient(180deg,rgba(11,11,11,.05),rgba(11,11,11,.74)),
            url("{industry_img}") center 20%/cover no-repeat;
        display:flex;
        align-items:flex-end;
        padding:24px;
        color:#fff;
    }}
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

    .gallery {{
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:16px;
        margin-top:22px;
    }}
    .gcard {{
        border-radius:18px;
        overflow:hidden;
        background:#111;
        position:relative;
        min-height:340px;
        box-shadow:0 9px 28px rgba(0,0,0,.07);
    }}
    .gcard img {{
        width:100%;height:100%;object-fit:cover;display:block;
    }}
    .gcard .overlay {{
        position:absolute;left:0;right:0;bottom:0;
        padding:38px 18px 17px 18px;
        background:linear-gradient(transparent,rgba(0,0,0,.88));
        color:#fff;font-weight:800;font-size:1rem;
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
        gap:10px; margin-top:24px;
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
        padding:20px 4px 4px 4px;
        color:#777;
        font-size:.82rem;
        flex-wrap:wrap;
    }}

    @media(max-width:1100px) {{
        .hero, .vision, .about {{ grid-template-columns:1fr; }}
        .hero-photo {{ min-height:470px; }}
        .icon-strip, .tools-grid {{ grid-template-columns:repeat(2,1fr); }}
        .quick-grid, .steps, .gallery {{ grid-template-columns:1fr 1fr; }}
        .contact-grid {{ grid-template-columns:1fr 1fr; }}
    }}
    @media(max-width:700px) {{
        .hero-copy {{ padding:42px 26px; }}
        .hero-photo {{ min-height:420px; }}
        .icon-strip, .quick-grid, .tools-grid, .steps, .gallery, .contact-grid, .skills {{
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
              <div class="brand-title">GG DIMEC SPA · MECHLAB</div>
              <div class="brand-sub">Ingeniería, aprendizaje y aplicación real</div>
            </div>
          </div>
          <div class="eyebrow">Ingeniería visual aplicada</div>
          <h1>Aprende, analiza y diseña con <span>criterio técnico</span></h1>
          <p>
            MechLab reúne herramientas interactivas para estudiantes, docentes e ingenieros
            que buscan comprender mejor la mecánica, la termodinámica, las vibraciones y el diseño de máquinas.
          </p>
          <p class="hero-vision">
            Aquí no solo calculas. Visualizas, entiendes y conectas teoría con problemas reales
            para formar mejor criterio de ingeniería.
          </p>
          <div class="cta-row">
            <a class="cta primary" href="#herramientas">Explorar herramientas ↓</a>
            <a class="cta secondary" href="https://www.gerardogaraydimec.com/" target="_blank">Visitar mi página web ↗</a>
          </div>
          <div class="hero-tags">
            <span>Docencia</span>
            <span>Industria</span>
            <span>Simulación</span>
            <span>Diseño mecánico</span>
            <span>Aprendizaje continuo</span>
          </div>
        </div>
        <div class="hero-photo">
          <div class="hero-badge">
            <b>Gerardo Garay Pereira</b><br>
            Ingeniero Civil Mecánico · Docente · Fundador de GG DIMEC SPA
          </div>
        </div>
      </section>

      <section class="icon-strip">
        <div class="icon-card">
          <div class="icon-bubble">📘</div>
          <div><h3>Aprendizaje claro</h3><p>Herramientas pensadas para comprender, no solo para obtener un número.</p></div>
        </div>
        <div class="icon-card">
          <div class="icon-bubble">🧠</div>
          <div><h3>Criterio técnico</h3><p>Visualización, ecuaciones y lectura física del resultado para tomar mejores decisiones.</p></div>
        </div>
        <div class="icon-card">
          <div class="icon-bubble">⚙️</div>
          <div><h3>Ingeniería aplicada</h3><p>Una forma de enseñar conectada con la realidad de diseño, análisis y terreno.</p></div>
        </div>
        <div class="icon-card">
          <div class="icon-bubble">🚀</div>
          <div><h3>Desarrollo continuo</h3><p>Un laboratorio digital en crecimiento para fortalecer tu formación profesional.</p></div>
        </div>
      </section>

      <section class="section">
        <div class="kicker">Ruta rápida</div>
        <h2>Encuentra tu punto de entrada</h2>
        <div class="section-intro">
          Para que la experiencia sea más directa, MechLab se organiza también según el tipo de usuario y la necesidad de aprendizaje.
        </div>
        <div class="quick-grid">
          <div class="quick-card">
            <div class="qicon">🎓</div>
            <h3>Si eres estudiante</h3>
            <ul>
              <li>Refuerza fundamentos con apoyo visual.</li>
              <li>Entiende cómo leer ecuaciones y diagramas.</li>
              <li>Explora estados, variables y respuesta física.</li>
            </ul>
            <a href="#herramientas">Ir a herramientas →</a>
          </div>
          <div class="quick-card">
            <div class="qicon">🧑‍🏫</div>
            <h3>Si eres docente</h3>
            <ul>
              <li>Apoya clases con material interactivo.</li>
              <li>Muestra fenómenos de forma más intuitiva.</li>
              <li>Conecta teoría, gráficas y visualización.</li>
            </ul>
            <a href="#herramientas">Ver módulos docentes →</a>
          </div>
          <div class="quick-card">
            <div class="qicon">🏭</div>
            <h3>Si eres ingeniero</h3>
            <ul>
              <li>Usa herramientas para revisar conceptos.</li>
              <li>Comunica mejor análisis y resultados.</li>
              <li>Refuerza criterio técnico aplicado.</li>
            </ul>
            <a href="https://www.gerardogaraydimec.com/" target="_blank">Conocer GG DIMEC →</a>
          </div>
        </div>
      </section>

      <div id="herramientas"></div>
      <section class="section">
        <div class="kicker">Herramientas disponibles</div>
        <h2>Empieza a trabajar con MechLab</h2>
        <div class="section-intro">
          Cada módulo está pensado para modificar datos, visualizar resultados y entender qué significa físicamente lo que estás calculando.
        </div>
        <div class="tools-grid">
          <div class="tool-card">
            <div class="tool-icon">RM</div>
            <h3>Resistencia de Materiales</h3>
            <p>Transformación de esfuerzos, tensiones principales, círculos de Mohr y análisis tensorial del estado resistente.</p>
            <div class="tool-tags"><span>Mohr 2D</span><span>Mohr 3D</span><span>Esfuerzos principales</span></div>
            <div class="tool-links">
              <a href="/mohr-2d">Abrir Círculo de Mohr 2D →</a>
              <a href="/mohr-3d">Abrir Círculo de Mohr 3D →</a>
            </div>
          </div>
          <div class="tool-card">
            <div class="tool-icon">VD</div>
            <h3>Vibraciones y Dinámica</h3>
            <p>Respuesta libre y forzada, frecuencia natural, amortiguamiento, resonancia, fase y transmisibilidad.</p>
            <div class="tool-tags"><span>1 GDL</span><span>Respuesta temporal</span><span>Frecuencia</span></div>
            <div class="tool-links">
              <a href="/vibraciones-1gdl">Vibraciones libres 1-GDL →</a>
              <a href="/vibracion-forzada-1gdl">Vibración forzada 1-GDL →</a>
            </div>
          </div>
          <div class="tool-card">
            <div class="tool-icon">TH</div>
            <h3>Termodinámica</h3>
            <p>Propiedades del agua y vapor, regiones de fase, diagramas y ciclos termodinámicos para aprendizaje y análisis.</p>
            <div class="tool-tags"><span>Agua-vapor</span><span>Ciclos</span><span>Visualización</span></div>
            <div class="tool-links">
              <a href="/agua-vapor">Propiedades del agua y vapor →</a>
              <a href="/ciclos-termodinamicos">Ciclos termodinámicos →</a>
            </div>
          </div>
          <div class="tool-card">
            <div class="tool-icon">EM</div>
            <h3>Elementos de Máquinas</h3>
            <p>Criterios de fluencia y falla, interpretación física, esfuerzos combinados y visualización geométrica del criterio.</p>
            <div class="tool-tags"><span>Von Mises</span><span>Tresca</span><span>Falla</span></div>
            <div class="tool-links">
              <a href="/von-mises">Abrir Von Mises Lab →</a>
            </div>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="kicker">Cómo usar MechLab</div>
        <h2>Una experiencia simple y útil</h2>
        <div class="steps">
          <div class="step"><div class="num">1</div><h3>Selecciona una herramienta</h3><p>Elige el tema que quieras estudiar o aplicar según tu curso, proyecto o necesidad de revisión.</p></div>
          <div class="step"><div class="num">2</div><h3>Modifica variables</h3><p>Ajusta parámetros, observa la respuesta del sistema y revisa cómo cambia el fenómeno en tiempo real.</p></div>
          <div class="step"><div class="num">3</div><h3>Interpreta el resultado</h3><p>No te quedes con el valor final: usa diagramas, explicaciones y ecuaciones para comprender lo que ocurre.</p></div>
        </div>
      </section>

      <section class="section dark">
        <div class="vision">
          <div class="vision-photo"></div>
          <div class="vision-copy">
            <div class="kicker">Mi visión</div>
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
              <span>Industria real</span><span>Docencia</span><span>Simulación</span><span>Diseño mecánico</span><span>Mejora continua</span>
            </div>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="kicker">Sobre mí</div>
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
        <div class="kicker">Ingeniería aplicada</div>
        <h2>De la industria a la enseñanza</h2>
        <div class="section-intro">
          MechLab se alimenta de una forma de trabajar que combina modelamiento, simulación, levantamiento, diseño y capacitación técnica.
          Parte de esa experiencia está reflejada en los proyectos y servicios desarrollados por GG DIMEC.
        </div>
        <div class="gallery">
          <div class="gcard"><img src="{sim_img}" alt="Simulación estructural"><div class="overlay">Simulación estructural y dinámica</div></div>
          <div class="gcard"><img src="{scan_img}" alt="Escaneo 3D"><div class="overlay">Escaneo 3D e ingeniería inversa</div></div>
          <div class="gcard"><img src="{train_img}" alt="Capacitación técnica"><div class="overlay">Capacitación y transferencia de conocimiento</div></div>
        </div>
      </section>

      <section class="contact">
        <div class="kicker">Contacto y comunidad</div>
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
