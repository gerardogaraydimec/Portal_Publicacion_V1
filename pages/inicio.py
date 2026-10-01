from __future__ import annotations

import base64
import mimetypes
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets' / 'landing_gg'


def data_uri(name: str) -> str:
    path = ASSETS / name
    if not path.exists():
        return ''
    mime = mimetypes.guess_type(path.name)[0] or 'image/png'
    encoded = base64.b64encode(path.read_bytes()).decode('ascii')
    return f'data:{mime};base64,{encoded}'


portrait = data_uri('portrait_main.jpg')
logo = data_uri('logo_original.png')
field_a = data_uri('gerardo_industria.jpg')
field_b = data_uri('gerardo_terreno.jpg')
brand_banner = data_uri('brand_banner.jpg')
icons = {
    'instagram': data_uri('contact_instagram.png'),
    'linkedin': data_uri('contact_linkedin.png'),
    'mail': data_uri('contact_mail.png'),
    'phone': data_uri('contact_phone.png'),
    'web': data_uri('contact_web.png'),
}

# Enlaces oficiales / públicos utilizados por el landing.
LINK_WEB = 'https://gerardogaraydimec.com/'
LINK_LINKEDIN = 'https://cl.linkedin.com/in/gerardo-garay-pereira'
LINK_INSTAGRAM = 'https://www.instagram.com/gerardogaray.dimec/'
LINK_MAIL = 'mailto:gerardogaray.dimec@gmail.com'
LINK_PHONE = 'https://wa.me/56957288516'

st.markdown('''
<style>
:root{
  --gg-orange:#ff6900;
  --gg-orange2:#f28e1c;
  --gg-black:#070708;
  --gg-graphite:#121316;
  --gg-panel:#1b1d21;
  --gg-white:#ffffff;
  --gg-ivory:#f8f2eb;
  --gg-muted:#b6b2ac;
  --gg-line:#303238;
}
.block-container{
  max-width:1560px;
  padding-top:.45rem!important;
  padding-bottom:0!important;
}
[data-testid="stAppViewContainer"]{background:#f3f0ec;}

/* ---------------- HERO ---------------- */
.gg-hero{
  position:relative;
  overflow:hidden;
  min-height:650px;
  border-radius:0 0 28px 28px;
  background:
    linear-gradient(90deg,rgba(255,105,0,.09) 1px,transparent 1px),
    linear-gradient(rgba(255,105,0,.05) 1px,transparent 1px),
    radial-gradient(circle at 18% 28%,rgba(255,105,0,.16),transparent 28%),
    linear-gradient(128deg,#050506 0%,#0d0e10 58%,#17191d 100%);
  background-size:42px 42px,42px 42px,auto,auto;
  border:1px solid #22252a;
  box-shadow:0 24px 60px rgba(0,0,0,.26);
  margin-bottom:1.25rem;
}
.gg-hero:before{
  content:"";position:absolute;left:-80px;top:78px;width:330px;height:4px;background:var(--gg-orange);transform:rotate(-22deg);opacity:.92;
}
.gg-hero:after{
  content:"";position:absolute;right:-110px;bottom:68px;width:420px;height:4px;background:var(--gg-orange);transform:rotate(-22deg);opacity:.65;
}
.gg-hero-grid{display:grid;grid-template-columns:1.08fr .92fr;min-height:650px;position:relative;z-index:1;}
.gg-hero-copy{padding:3.8rem 3.3rem 2.7rem 3.8rem;display:flex;flex-direction:column;justify-content:center;}
.gg-logo-small{width:210px;max-width:50%;margin-bottom:1.0rem;filter:drop-shadow(0 5px 12px rgba(255,105,0,.12));}
.gg-overline{color:var(--gg-orange);font-size:.78rem;letter-spacing:.20em;text-transform:uppercase;font-weight:900;margin-bottom:.85rem;}
.gg-title{font-size:5.15rem;line-height:.87;letter-spacing:-.065em;font-weight:950;color:white;margin:0;}
.gg-title .accent{color:var(--gg-orange);}
.gg-tagline{font-size:1.48rem;line-height:1.28;color:#f6eee4;font-weight:760;margin:1.15rem 0 .75rem;max-width:760px;}
.gg-intro{font-size:1.02rem;line-height:1.58;color:#c9c4bc;max-width:780px;margin-bottom:1.25rem;}
.gg-badges{display:flex;flex-wrap:wrap;gap:.45rem;margin:.15rem 0 1.2rem;}
.gg-badge{font-size:.75rem;color:#e7dfd4;border:1px solid #44474f;background:#17191d;border-radius:999px;padding:.36rem .66rem;}
.gg-badge b{color:#ff9d55;}
.gg-actions{display:flex;flex-wrap:wrap;gap:.62rem;margin-top:.35rem;}
.gg-btn{display:inline-flex;align-items:center;gap:.4rem;text-decoration:none!important;border-radius:10px;padding:.74rem 1rem;font-size:.83rem;font-weight:820;letter-spacing:.01em;transition:.16s ease;}
.gg-btn-primary{background:var(--gg-orange);color:white!important;border:1px solid var(--gg-orange);}
.gg-btn-primary:hover{background:#ff7d29;transform:translateY(-1px);}
.gg-btn-dark{background:#17191e;color:#f8f1e8!important;border:1px solid #44474f;}
.gg-btn-dark:hover{border-color:#7c4c29;transform:translateY(-1px);}
.gg-hero-photo{position:relative;min-height:650px;overflow:hidden;background:#181a1e;}
.gg-hero-photo img{width:100%;height:100%;min-height:650px;object-fit:cover;object-position:center 32%;display:block;filter:saturate(.96) contrast(1.02);}
.gg-hero-photo:before{content:"";position:absolute;z-index:2;inset:0;background:linear-gradient(90deg,#0b0c0e 0%,rgba(11,12,14,.55) 9%,transparent 32%),linear-gradient(0deg,rgba(6,6,7,.72) 0%,transparent 28%);}
.gg-photo-tag{position:absolute;z-index:3;right:1.1rem;bottom:1.1rem;background:rgba(8,8,9,.88);border:1px solid #41444b;border-left:4px solid var(--gg-orange);border-radius:10px;padding:.75rem .9rem;color:#e7dfd4;font-size:.75rem;line-height:1.4;backdrop-filter:blur(8px);}
.gg-photo-tag strong{color:white;font-size:.85rem;}

/* ---------------- SOCIAL STRIP ---------------- */
.gg-social-strip{display:flex;align-items:center;justify-content:space-between;gap:1rem;background:#0d0e10;border:1px solid #27292f;border-radius:18px;padding:.85rem 1rem;margin:1rem 0 1.35rem;color:white;}
.gg-social-label{font-size:.82rem;line-height:1.35;color:#c8c2ba;}
.gg-social-label b{color:white;display:block;font-size:.95rem;}
.gg-socials{display:flex;gap:.55rem;flex-wrap:wrap;justify-content:flex-end;}
.gg-social{display:flex;align-items:center;justify-content:center;width:42px;height:42px;border-radius:10px;background:#191b20;border:1px solid #35383f;transition:.15s ease;}
.gg-social:hover{transform:translateY(-2px);border-color:#8a5027;background:#202228;}
.gg-social img{width:24px;height:24px;object-fit:contain;}

/* ---------------- SECTIONS ---------------- */
.gg-section{margin:1.7rem 0;}
.gg-section-head{display:flex;justify-content:space-between;align-items:flex-end;gap:1.3rem;margin-bottom:.9rem;}
.gg-kicker{font-size:.72rem;letter-spacing:.17em;text-transform:uppercase;font-weight:900;color:#bd5f20;margin-bottom:.22rem;}
.gg-section-title{font-size:2.35rem;line-height:1.02;letter-spacing:-.045em;font-weight:940;color:#111215;margin:0;}
.gg-section-copy{max-width:700px;color:#68645e;font-size:.93rem;line-height:1.55;}

/* ---------------- BRAND BANNER ---------------- */
.gg-brand-banner{position:relative;border-radius:22px;overflow:hidden;background:#050505;border:1px solid #212328;box-shadow:0 14px 38px rgba(0,0,0,.16);margin:1.45rem 0;}
.gg-brand-banner img{display:block;width:100%;height:auto;max-height:515px;object-fit:cover;object-position:center;}

/* ---------------- FIELD CARDS ---------------- */
.gg-field-grid{display:grid;grid-template-columns:1fr 1fr;gap:.85rem;}
.gg-field-card{position:relative;height:460px;border-radius:20px;overflow:hidden;background:#16181c;border:1px solid #d6cec3;box-shadow:0 10px 28px rgba(0,0,0,.10);}
.gg-field-card img{width:100%;height:100%;object-fit:cover;display:block;}
.gg-field-card:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,transparent 35%,rgba(0,0,0,.87) 100%);}
.gg-field-cap{position:absolute;z-index:2;left:1.25rem;right:1.25rem;bottom:1.2rem;color:white;}
.gg-field-cap .mini{color:#ff9b52;font-size:.70rem;letter-spacing:.13em;text-transform:uppercase;font-weight:900;}
.gg-field-cap b{display:block;font-size:1.35rem;line-height:1.12;margin:.25rem 0;}
.gg-field-cap span{font-size:.83rem;line-height:1.45;color:#d8d1c8;display:block;max-width:580px;}

/* ---------------- IDENTITY / METHOD ---------------- */
.gg-identity{display:grid;grid-template-columns:.9fr 1.1fr;border-radius:22px;overflow:hidden;background:#0d0e10;border:1px solid #27292e;margin:1.5rem 0;}
.gg-identity-left{padding:2rem 2.1rem;color:white;background:radial-gradient(circle at 12% 20%,rgba(255,105,0,.16),transparent 31%),#0d0e10;}
.gg-identity-left h3{font-size:2rem;line-height:1.05;margin:.35rem 0 .8rem;color:white;}
.gg-identity-left p{color:#c7c1b9;font-size:.91rem;line-height:1.6;}
.gg-identity-left .quote{border-left:4px solid var(--gg-orange);padding-left:.9rem;margin-top:1rem;color:#eee6dd;font-weight:650;line-height:1.52;}
.gg-process{padding:1.6rem;display:grid;grid-template-columns:1fr 1fr;gap:.65rem;background:#17191d;}
.gg-process-card{background:#202228;border:1px solid #32353c;border-radius:14px;padding:.9rem;min-height:118px;}
.gg-process-n{color:var(--gg-orange);font-size:.67rem;letter-spacing:.13em;font-weight:900;}
.gg-process-card b{display:block;color:white;font-size:.93rem;margin:.24rem 0;}
.gg-process-card span{display:block;color:#aaa69f;font-size:.76rem;line-height:1.42;}

/* ---------------- LABS ---------------- */
.gg-labs{background:#0b0c0e;border-radius:24px;padding:1.8rem;border:1px solid #24272d;box-shadow:0 18px 45px rgba(0,0,0,.14);}
.gg-labs-head{display:flex;justify-content:space-between;gap:1rem;align-items:flex-end;margin-bottom:1rem;}
.gg-labs h2{color:white;font-size:2.35rem;letter-spacing:-.045em;margin:0;line-height:1.02;}
.gg-labs .lead{color:#b9b4ad;font-size:.9rem;line-height:1.48;max-width:720px;}
.gg-lab-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:.72rem;}
.gg-lab-card{position:relative;background:#17191d;border:1px solid #30333a;border-radius:16px;padding:1rem 1.05rem;min-height:220px;transition:.16s ease;overflow:hidden;}
.gg-lab-card:before{content:"";position:absolute;width:68px;height:4px;background:var(--gg-orange);right:-8px;top:15px;transform:rotate(-16deg);opacity:.8;}
.gg-lab-card:hover{transform:translateY(-2px);border-color:#7d4a24;background:#1c1e23;}
.gg-lab-icon{font-size:1.55rem;margin-bottom:.42rem;}
.gg-lab-name{color:white;font-size:1.03rem;font-weight:880;margin-bottom:.22rem;}
.gg-lab-desc{color:#9d9993;font-size:.76rem;line-height:1.42;margin-bottom:.52rem;}
.gg-mod{color:#ddd7cf;font-size:.75rem;line-height:1.36;padding:.08rem 0;}
.gg-mod:before{content:"›";color:var(--gg-orange);font-weight:900;margin-right:.35rem;}

/* ---------------- CAPABILITIES ---------------- */
.gg-cap-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.68rem;}
.gg-cap{background:white;border:1px solid #dcd4ca;border-radius:14px;padding:1rem;min-height:128px;box-shadow:0 4px 14px rgba(0,0,0,.045);}
.gg-cap .num{color:var(--gg-orange);font-size:.68rem;font-weight:900;letter-spacing:.14em;}
.gg-cap b{display:block;color:#18191c;font-size:.91rem;line-height:1.24;margin:.22rem 0 .3rem;}
.gg-cap span{color:#6b6761;font-size:.76rem;line-height:1.4;display:block;}

/* ---------------- CONTACT ---------------- */
.gg-contact{display:grid;grid-template-columns:1fr .9fr;border-radius:24px;overflow:hidden;background:#060607;color:white;margin:1.75rem 0 0;border:1px solid #25272c;}
.gg-contact-main{padding:2rem 2.2rem;}
.gg-contact-main .k{color:var(--gg-orange);font-size:.72rem;letter-spacing:.16em;font-weight:900;text-transform:uppercase;}
.gg-contact-main h2{font-size:2.35rem;line-height:1.04;margin:.35rem 0 .75rem;color:white;letter-spacing:-.04em;}
.gg-contact-main p{color:#bdb8b1;line-height:1.58;font-size:.9rem;max-width:680px;}
.gg-contact-links{display:grid;grid-template-columns:1fr 1fr;gap:.62rem;margin-top:1.1rem;}
.gg-contact-link{display:flex;gap:.65rem;align-items:center;text-decoration:none!important;background:#17191d;border:1px solid #31343b;border-radius:12px;padding:.72rem .8rem;color:white!important;transition:.15s ease;}
.gg-contact-link:hover{transform:translateY(-1px);border-color:#7c4c28;}
.gg-contact-link img{width:26px;height:26px;object-fit:contain;}
.gg-contact-link .small{display:block;color:#9d9992;font-size:.68rem;line-height:1.2;}
.gg-contact-link b{font-size:.78rem;display:block;color:#f0e8df;line-height:1.2;}
.gg-contact-side{background:linear-gradient(145deg,#ff6900 0%,#d95100 100%);padding:2rem;display:flex;flex-direction:column;justify-content:center;}
.gg-contact-side .big{font-size:1.8rem;line-height:1.08;font-weight:940;color:white;}
.gg-contact-side p{font-size:.86rem;line-height:1.5;color:#fff0e6;margin:.7rem 0 1rem;}
.gg-contact-side a{display:inline-block;text-decoration:none!important;color:#171717!important;background:white;border-radius:10px;padding:.7rem .9rem;font-size:.78rem;font-weight:900;align-self:flex-start;}
.gg-footer{background:#060607;color:#8f8b86;text-align:center;padding:1rem;border-top:1px solid #202228;font-size:.72rem;letter-spacing:.03em;}
.gg-footer b{color:#d9d2c9;}

@media(max-width:1080px){
  .gg-hero-grid{grid-template-columns:1fr}.gg-hero-copy{padding:2.8rem 2.2rem 2rem}.gg-hero-photo{min-height:520px}.gg-hero-photo img{min-height:520px}.gg-title{font-size:4.2rem}
  .gg-lab-grid{grid-template-columns:1fr 1fr}.gg-cap-grid{grid-template-columns:1fr 1fr}.gg-identity,.gg-contact{grid-template-columns:1fr}
}
@media(max-width:760px){
  .gg-title{font-size:3.45rem}.gg-tagline{font-size:1.2rem}.gg-hero-copy{padding:2rem 1.3rem}.gg-section-head,.gg-labs-head{display:block}.gg-section-copy,.gg-labs .lead{margin-top:.45rem}
  .gg-social-strip{display:block}.gg-socials{justify-content:flex-start;margin-top:.65rem}
  .gg-field-grid,.gg-lab-grid,.gg-cap-grid,.gg-process,.gg-contact-links{grid-template-columns:1fr}.gg-field-card{height:390px}
}
</style>
''', unsafe_allow_html=True)

# ---------------- HERO ----------------
hero_logo = f'<img class="gg-logo-small" src="{logo}" alt="Gerardo Garay Diseño Industrial Mecánico">' if logo else ''
hero_photo = f'<img src="{portrait}" alt="Gerardo Garay · Ingeniería Mecánica">' if portrait else ''

st.markdown(f'''
<div class="gg-hero">
  <div class="gg-hero-grid">
    <div class="gg-hero-copy">
      {hero_logo}
      <div class="gg-overline">Ingeniería mecánica · industria · docencia</div>
      <div class="gg-title">MECH<span class="accent">LAB</span></div>
      <div class="gg-tagline">Máquinas primero. Ingeniería que se ve, se modela y se entiende.</div>
      <div class="gg-intro">Un laboratorio digital construido desde experiencia real en terreno, diseño mecánico, simulación computacional y enseñanza. El objetivo no es entregar solo un número: es desarrollar criterio para comprender cómo se comporta una máquina.</div>
      <div class="gg-badges">
        <div class="gg-badge"><b>Director Técnico</b></div>
        <div class="gg-badge"><b>Docente USM</b></div>
        <div class="gg-badge"><b>FEM / CFD / DEM</b></div>
        <div class="gg-badge"><b>3D + ingeniería aplicada</b></div>
      </div>
      <div class="gg-actions">
        <a class="gg-btn gg-btn-primary" href="#laboratorios">Explorar MechLab</a>
        <a class="gg-btn gg-btn-dark" href="{LINK_WEB}" target="_blank">Sitio GG DIMEC ↗</a>
        <a class="gg-btn gg-btn-dark" href="{LINK_LINKEDIN}" target="_blank">LinkedIn ↗</a>
      </div>
    </div>
    <div class="gg-hero-photo">
      {hero_photo}
      <div class="gg-photo-tag"><strong>GERARDO GARAY</strong><br>Diseño Industrial Mecánico<br><span style="color:#ff8a39">MechLab · Ingeniería para comprender máquinas</span></div>
    </div>
  </div>
</div>
''', unsafe_allow_html=True)

# ---------------- SOCIAL STRIP ----------------
social_data = [
    ('web', LINK_WEB, 'Sitio web'),
    ('linkedin', LINK_LINKEDIN, 'LinkedIn'),
    ('instagram', LINK_INSTAGRAM, 'Instagram'),
    ('mail', LINK_MAIL, 'Correo'),
    ('phone', LINK_PHONE, 'WhatsApp'),
]
social_html = ''.join(
    f'<a class="gg-social" href="{url}" target="_blank" title="{label}"><img src="{icons[key]}" alt="{label}"></a>'
    for key, url, label in social_data if icons.get(key)
)
st.markdown(f'''
<div class="gg-social-strip">
  <div class="gg-social-label"><b>Conectado con mi trabajo real.</b> Proyectos, terreno, docencia y desarrollo técnico.</div>
  <div class="gg-socials">{social_html}</div>
</div>
''', unsafe_allow_html=True)

# ---------------- BRAND BANNER ----------------
if brand_banner:
    st.markdown(f'<div class="gg-brand-banner"><img src="{brand_banner}" alt="Tecnología avanzada en soluciones reales"></div>', unsafe_allow_html=True)

# ---------------- WHY / METHOD ----------------
st.markdown('''
<div class="gg-identity">
  <div class="gg-identity-left">
    <div class="gg-kicker" style="color:#ff7b22">DE LA INDUSTRIA AL APRENDIZAJE</div>
    <h3>MechLab nace de resolver problemas reales.</h3>
    <p>Mi trabajo se mueve entre terreno, modelamiento, simulación, diseño y formación técnica. MechLab toma esa misma secuencia y la transforma en un espacio donde el estudiante puede explorar el fenómeno antes de quedarse solamente con la ecuación.</p>
    <div class="quote">Tecnología avanzada para problemas reales; modelos claros para decisiones de ingeniería.</div>
  </div>
  <div class="gg-process">
    <div class="gg-process-card"><div class="gg-process-n">01 · OBSERVAR</div><b>Máquina y fenómeno</b><span>Partir por lo que realmente ocurre: geometría, fuerzas, movimiento, flujo, contacto, medición.</span></div>
    <div class="gg-process-card"><div class="gg-process-n">02 · MODELAR</div><b>Idealización con sentido físico</b><span>Definir variables, hipótesis, restricciones y el nivel de complejidad que el problema necesita.</span></div>
    <div class="gg-process-card"><div class="gg-process-n">03 · CALCULAR</div><b>Ecuaciones + simulación</b><span>Usar el cálculo como una herramienta para comprender y comparar, no como un fin aislado.</span></div>
    <div class="gg-process-card"><div class="gg-process-n">04 · INTERPRETAR</div><b>Criterio de ingeniería</b><span>Conectar resultados, visualización 3D y decisión técnica con el comportamiento de la máquina.</span></div>
  </div>
</div>
''', unsafe_allow_html=True)

# ---------------- FIELD PHOTOS ----------------
st.markdown('''
<div class="gg-section">
  <div class="gg-section-head">
    <div><div class="gg-kicker">Ingeniería real</div><div class="gg-section-title">Del terreno al modelo.</div></div>
    <div class="gg-section-copy">MechLab no está separado de la industria. La plataforma busca acercar a estudiantes y profesionales a la forma en que una necesidad real se transforma en levantamiento, modelo, cálculo, simulación y decisión.</div>
  </div>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div class="gg-field-grid">
  <div class="gg-field-card">
    <img src="{field_a}" alt="Ingeniería en planta industrial">
    <div class="gg-field-cap"><div class="mini">TERRENO · PLANTA · EQUIPOS</div><b>Observar antes de modelar.</b><span>La ingeniería aplicada comienza entendiendo cómo funciona el equipo, cómo se interviene y cuáles son sus restricciones reales.</span></div>
  </div>
  <div class="gg-field-card">
    <img src="{field_b}" alt="Ingeniería mecánica en terreno">
    <div class="gg-field-cap"><div class="mini">LEVANTAMIENTO · OPERACIÓN · CONTEXTO</div><b>La máquina siempre tiene una historia.</b><span>Geometría, operación, mantenimiento, montaje y seguridad son parte del problema; MechLab busca que esa mirada también llegue al aprendizaje.</span></div>
  </div>
</div>
''', unsafe_allow_html=True)

# ---------------- LABS ----------------
st.markdown('''
<div id="laboratorios" class="gg-section">
  <div class="gg-labs">
    <div class="gg-labs-head">
      <div><div class="gg-kicker" style="color:#ff7b22">MECHLAB</div><h2>Un mapa de ingeniería mecánica que ya creció.</h2></div>
      <div class="lead">Las herramientas se organizan por fenómenos y máquinas. El 3D se usa cuando realmente mejora la comprensión; los gráficos y ecuaciones permanecen sincronizados con la interpretación.</div>
    </div>
    <div class="gg-lab-grid">
      <div class="gg-lab-card"><div class="gg-lab-icon">🏗️</div><div class="gg-lab-name">Resistencia y Estructuras</div><div class="gg-lab-desc">De cargas y tensiones a deformación, estabilidad y comportamiento resistente.</div><div class="gg-mod">Vigas · V, M, tensiones y deflexión</div><div class="gg-mod">Columnas · pandeo y comparación</div><div class="gg-mod">Torsión 3D</div><div class="gg-mod">Mohr 2D / 3D · Von Mises</div><div class="gg-mod">Perfiles estructurales</div></div>
      <div class="gg-lab-card"><div class="gg-lab-icon">🌀</div><div class="gg-lab-name">Dinámica y Vibraciones</div><div class="gg-lab-desc">Del movimiento libre a resonancia, TMD y diagnóstico vibracional.</div><div class="gg-mod">1GDL libre y forzada</div><div class="gg-mod">Desbalance y excitación de base</div><div class="gg-mod">2GDL · modos · antirresonancia</div><div class="gg-mod">TMD / absorbedor dinámico</div><div class="gg-mod">FFT · órdenes · waterfall</div></div>
      <div class="gg-lab-card"><div class="gg-lab-icon">🌊</div><div class="gg-lab-name">Fluidos y Energía</div><div class="gg-lab-desc">Flujo, pérdidas, bombas y lectura energética de sistemas.</div><div class="gg-mod">Continuidad y Bernoulli 3D</div><div class="gg-mod">Reynolds y pérdidas</div><div class="gg-mod">Bombas y curva del sistema 3D</div><div class="gg-mod">HGL / EGL · operación</div><div class="gg-mod">Termodinámica y ciclos</div></div>
      <div class="gg-lab-card"><div class="gg-lab-icon">📏</div><div class="gg-lab-name">Metrología y Calidad</div><div class="gg-lab-desc">Dimensión, geometría, tolerancia y decisión de conformidad.</div><div class="gg-mod">ISO GPS 3D</div><div class="gg-mod">Ajustes y tolerancias ISO 3D</div><div class="gg-mod">Medición e incertidumbre</div><div class="gg-mod">Datums y zonas de tolerancia</div></div>
      <div class="gg-lab-card"><div class="gg-lab-icon">⚙️</div><div class="gg-lab-name">Máquinas y Componentes</div><div class="gg-lab-desc">El lugar donde convergen resistencia, dinámica, fluidos y manufactura.</div><div class="gg-mod">Componentes y comportamiento mecánico</div><div class="gg-mod">Bombas y sistemas</div><div class="gg-mod">Vibraciones de máquinas</div><div class="gg-mod">Diseño y comparación</div></div>
      <div class="gg-lab-card"><div class="gg-lab-icon">🧠</div><div class="gg-lab-name">Método MechLab</div><div class="gg-lab-desc">La herramienta no reemplaza el razonamiento: lo hace visible y explorable.</div><div class="gg-mod">Fenómeno → modelo</div><div class="gg-mod">Cálculo → visualización</div><div class="gg-mod">Comparador A/B</div><div class="gg-mod">Interpretación → decisión</div></div>
    </div>
  </div>
</div>
''', unsafe_allow_html=True)

# ---------------- CAPABILITIES ----------------
st.markdown('''
<div class="gg-section">
  <div class="gg-section-head">
    <div><div class="gg-kicker">La experiencia que sostiene MechLab</div><div class="gg-section-title">Ingeniería aplicada, no solo teoría.</div></div>
    <div class="gg-section-copy">La plataforma se alimenta de las mismas áreas que desarrollo profesionalmente: diseño, levantamiento, simulación, automatización y capacitación técnica.</div>
  </div>
  <div class="gg-cap-grid">
    <div class="gg-cap"><div class="num">01</div><b>Diseño de Soluciones Industriales</b><span>Transformar una necesidad operacional en una solución mecánica desarrollable y fabricable.</span></div>
    <div class="gg-cap"><div class="num">02</div><b>Asistencia en terreno</b><span>Levantamiento, inspección, contexto operacional y conexión con talleres y fabricación.</span></div>
    <div class="gg-cap"><div class="num">03</div><b>Simulación estructural y dinámica</b><span>Comprender cargas, respuesta, deformación y comportamiento de equipos y componentes.</span></div>
    <div class="gg-cap"><div class="num">04</div><b>Escaneo 3D e ingeniería inversa</b><span>Capturar geometría real y convertirla en información útil para diseño, inspección y desarrollo.</span></div>
    <div class="gg-cap"><div class="num">05</div><b>Simulación de falla</b><span>Investigar cómo condiciones operacionales pueden modificar la respuesta de equipos industriales.</span></div>
    <div class="gg-cap"><div class="num">06</div><b>Automatización CAD</b><span>Parametrización, generación sistemática de geometría y soporte a procesos de diseño y fabricación.</span></div>
    <div class="gg-cap"><div class="num">07</div><b>Capacitación técnica</b><span>Conectar fundamentos mecánicos con herramientas actuales y situaciones de aplicación real.</span></div>
    <div class="gg-cap"><div class="num">08</div><b>FEM · CFD · DEM</b><span>Simulación computacional avanzada para sólidos, fluidos y manejo de materiales.</span></div>
  </div>
</div>
''', unsafe_allow_html=True)

# ---------------- CONTACT ----------------
def contact_link(icon_key: str, href: str, small: str, title: str) -> str:
    icon = icons.get(icon_key, '')
    img = f'<img src="{icon}" alt="{title}">' if icon else ''
    return f'<a class="gg-contact-link" href="{href}" target="_blank">{img}<div><span class="small">{small}</span><b>{title}</b></div></a>'

contact_links = ''.join([
    contact_link('web', LINK_WEB, 'Sitio oficial', 'gerardogaraydimec.com'),
    contact_link('linkedin', LINK_LINKEDIN, 'Perfil profesional', 'LinkedIn · Gerardo Garay'),
    contact_link('instagram', LINK_INSTAGRAM, 'Proyectos y contenido', '@gerardogaray.dimec'),
    contact_link('mail', LINK_MAIL, 'Correo', 'gerardogaray.dimec@gmail.com'),
    contact_link('phone', LINK_PHONE, 'WhatsApp / contacto', '+56 9 5728 8516'),
])

st.markdown(f'''
<div class="gg-contact">
  <div class="gg-contact-main">
    <div class="k">CONECTEMOS</div>
    <h2>Ingeniería que se comparte, se enseña y se lleva a terreno.</h2>
    <p>MechLab es una extensión educativa de una forma de trabajar: mirar el problema completo, usar tecnología cuando aporta valor y convertir resultados técnicos en decisiones comprensibles.</p>
    <div class="gg-contact-links">{contact_links}</div>
  </div>
  <div class="gg-contact-side">
    <div class="big">¿Quieres conocer el trabajo detrás de MechLab?</div>
    <p>En el sitio de GG DIMEC puedes revisar proyectos, servicios y desarrollos de ingeniería mecánica industrial.</p>
    <a href="{LINK_WEB}" target="_blank">VISITAR SITIO WEB ↗</a>
  </div>
</div>
<div class="gg-footer"><b>GERARDO GARAY · DISEÑO INDUSTRIAL MECÁNICO</b> · MechLab · Ingeniería Mecánica Aplicada</div>
''', unsafe_allow_html=True)
