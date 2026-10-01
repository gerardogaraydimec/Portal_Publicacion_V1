from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title='MechLab · GG DIMEC',
    page_icon='⚙️',
    layout='wide',
)

ROOT = Path(__file__).resolve().parents[1]

# -----------------------------------------------------------------------------
# Imágenes: reutiliza fotos que ya existan en el proyecto.
# No obliga a cambiar nombres ni a volver a copiar imágenes.
# -----------------------------------------------------------------------------
IMAGE_HINTS = (
    'terreno', 'campo', 'planta', 'faena', 'gerardo', 'garay', 'perfil',
    'retrato', 'foto', 'docencia', 'clase', 'maquina', 'equipo', 'inspeccion',
    'ingenieria', 'ingeniería', 'industrial', 'mina', 'taller', 'laboratorio',
)
EXCLUDE_HINTS = (
    'logo', 'icon', 'favicon', 'preview', 'canvas', 'screenshot', 'captura',
    'bernoulli', 'mohr', 'viga', 'plot', 'chart', 'grafico', 'gráfico', 'qr',
    'watermark', 'diagrama', 'diagram', 'scheme', 'esquema',
)
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.webp'}


def _candidate_dirs() -> list[Path]:
    dirs = [
        ROOT / 'assets', ROOT / 'images', ROOT / 'static',
        ROOT / 'pages' / 'assets', ROOT / 'modules' / 'assets', ROOT,
    ]
    return [d for d in dirs if d.exists()]


def _image_size_score(path: Path) -> tuple[int, float]:
    try:
        from PIL import Image
        with Image.open(path) as im:
            w, h = im.size
        if w < 420 or h < 300:
            return 0, 0.0
        area = w * h
        ratio = w / max(h, 1)
        return area, ratio
    except Exception:
        try:
            return int(path.stat().st_size), 1.0
        except Exception:
            return 0, 0.0


def discover_photos(limit: int = 8) -> list[Path]:
    found: dict[str, Path] = {}
    for base in _candidate_dirs():
        # No recorrer entornos virtuales ni repositorios internos.
        for current, dirnames, filenames in os.walk(base):
            rel_depth = len(Path(current).relative_to(base).parts)
            dirnames[:] = [
                d for d in dirnames
                if d not in {'.venv', 'venv', '.git', '__pycache__', 'node_modules'}
            ]
            if rel_depth > 3:
                dirnames[:] = []
                continue
            for filename in filenames:
                p = Path(current) / filename
                if p.suffix.lower() not in IMAGE_EXTS:
                    continue
                low = p.name.lower()
                if any(x in low for x in EXCLUDE_HINTS):
                    continue
                found[str(p.resolve())] = p

    scored = []
    for p in found.values():
        area, ratio = _image_size_score(p)
        if area <= 0:
            continue
        name = p.name.lower()
        score = 0.0
        if any(x in name for x in IMAGE_HINTS):
            score += 100
        if p.suffix.lower() in {'.jpg', '.jpeg'}:
            score += 14
        if area > 1_000_000:
            score += 18
        elif area > 500_000:
            score += 10
        if 0.55 <= ratio <= 1.45:
            score += 12
        if 0.70 <= ratio <= 1.10:
            score += 8
        # Preferir assets de landing o fotos antes que imágenes genéricas.
        lowpath = str(p).lower()
        if 'landing' in lowpath:
            score += 80
        if 'assets' in lowpath:
            score += 12
        scored.append((score, area, p))

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [x[2] for x in scored[:limit]]


def data_uri(path: Path | None) -> str | None:
    if not path or not path.exists():
        return None
    try:
        mime = mimetypes.guess_type(path.name)[0] or 'image/jpeg'
        b64 = base64.b64encode(path.read_bytes()).decode('ascii')
        return f'data:{mime};base64,{b64}'
    except Exception:
        return None


photos = discover_photos()
hero_photo = photos[0] if photos else None
field_photos = photos[1:4] if len(photos) > 1 else []
hero_uri = data_uri(hero_photo)

# -----------------------------------------------------------------------------
# Sistema visual restaurado: negro / grafito + cobre / naranja GG DIMEC.
# -----------------------------------------------------------------------------
st.markdown(r'''
<style>
:root{
  --gg-black:#0d0e10;
  --gg-black2:#15171b;
  --gg-panel:#1d1f24;
  --gg-panel2:#24272d;
  --gg-orange:#f28e1c;
  --gg-copper:#c8752d;
  --gg-ivory:#fbf7f0;
  --gg-white:#ffffff;
  --gg-muted:#b8b4ad;
  --gg-line:#35383f;
}
.block-container{
  max-width:1540px;
  padding-top:.55rem!important;
  padding-bottom:0!important;
}
[data-testid="stAppViewContainer"]{background:#f6f4f1;}

/* HERO */
.gg-hero{
  position:relative;
  min-height:520px;
  border-radius:26px;
  overflow:hidden;
  background:
    radial-gradient(circle at 18% 8%,rgba(242,142,28,.20),transparent 28%),
    linear-gradient(125deg,#090a0c 0%,#131519 58%,#202228 100%);
  box-shadow:0 18px 46px rgba(0,0,0,.22);
  margin:.25rem 0 1.15rem 0;
  border:1px solid #292c31;
}
.gg-hero-inner{display:grid;grid-template-columns:1.1fr .9fr;min-height:520px;}
.gg-hero-copy{padding:4.3rem 3.6rem 3.3rem 3.8rem;display:flex;flex-direction:column;justify-content:center;z-index:2}
.gg-eyebrow{color:var(--gg-orange);font-size:.82rem;letter-spacing:.20em;font-weight:800;text-transform:uppercase;margin-bottom:1rem}
.gg-title{font-size:4.45rem;line-height:.91;font-weight:900;letter-spacing:-.055em;color:white;margin:0 0 1rem 0}
.gg-title span{color:var(--gg-orange)}
.gg-subtitle{font-size:1.22rem;line-height:1.55;color:#e8e2d9;max-width:720px;margin-bottom:1.5rem}
.gg-pills{display:flex;gap:.55rem;flex-wrap:wrap;margin-top:.25rem}
.gg-pill{border:1px solid #494c54;color:#ddd8d0;border-radius:999px;padding:.38rem .72rem;font-size:.78rem;background:rgba(255,255,255,.035)}
.gg-pill strong{color:#ffad45}
.gg-hero-media{position:relative;min-height:520px;background:linear-gradient(145deg,#1a1c20,#0f1012);overflow:hidden}
.gg-hero-media img{width:100%;height:100%;min-height:520px;object-fit:cover;object-position:center 35%;display:block;filter:saturate(.92) contrast(1.03)}
.gg-hero-media:after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,#101216 0%,rgba(16,18,22,.46) 14%,transparent 45%)}
.gg-photo-placeholder{height:100%;min-height:520px;display:flex;align-items:center;justify-content:center;color:#7b7f87;font-size:.95rem;padding:2rem;text-align:center;background:radial-gradient(circle at 60% 40%,#30343b,#15171b 65%)}
.gg-photo-tag{position:absolute;right:1.2rem;bottom:1.2rem;z-index:3;background:rgba(13,14,16,.88);border:1px solid #44474e;border-radius:12px;padding:.65rem .85rem;color:#e7e0d7;font-size:.76rem;line-height:1.35}
.gg-photo-tag b{color:#ffad45}

/* STORY STRIP */
.gg-darkstrip{background:var(--gg-black);border-radius:22px;padding:1.6rem 1.7rem;margin:1rem 0;color:white;border:1px solid #26282e}
.gg-darkstrip-grid{display:grid;grid-template-columns:1.25fr repeat(3,.75fr);gap:1rem;align-items:stretch}
.gg-dark-lead{padding:.7rem .85rem}
.gg-kicker{color:var(--gg-orange);font-size:.76rem;letter-spacing:.14em;font-weight:800;text-transform:uppercase}
.gg-dark-title{font-size:1.55rem;font-weight:850;line-height:1.12;margin:.4rem 0 .55rem}
.gg-dark-copy{color:#c9c4bc;line-height:1.48;font-size:.91rem}
.gg-value{background:#1a1c20;border:1px solid #30333a;border-radius:14px;padding:1rem}
.gg-value-n{font-size:1.45rem;font-weight:900;color:#ffad45}
.gg-value-t{font-size:.82rem;color:#d4cec5;line-height:1.35;margin-top:.25rem}

/* PHOTOS / TERRAIN */
.gg-section{margin:1.55rem 0}
.gg-section-head{display:flex;justify-content:space-between;align-items:flex-end;gap:1rem;margin-bottom:.8rem}
.gg-section-kicker{font-size:.73rem;color:#ad6428;letter-spacing:.16em;font-weight:900;text-transform:uppercase}
.gg-section-title{font-size:2rem;font-weight:900;letter-spacing:-.035em;color:#17181b;line-height:1.05}
.gg-section-copy{font-size:.91rem;line-height:1.45;color:#66625c;max-width:620px}
.gg-gallery{display:grid;grid-template-columns:1.3fr .85fr .85fr;gap:.8rem}
.gg-photo-card{position:relative;height:315px;border-radius:18px;overflow:hidden;background:#22252a;border:1px solid #ded7cd;box-shadow:0 8px 25px rgba(0,0,0,.10)}
.gg-photo-card img{width:100%;height:100%;object-fit:cover;display:block;filter:saturate(.9) contrast(1.02)}
.gg-photo-card:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,transparent 42%,rgba(0,0,0,.82) 100%)}
.gg-photo-card .cap{position:absolute;z-index:2;bottom:1rem;left:1rem;right:1rem;color:white}
.gg-photo-card .cap b{font-size:1.04rem;display:block;margin-bottom:.15rem}
.gg-photo-card .cap span{font-size:.78rem;color:#ddd5ca;line-height:1.35}
.gg-photo-empty{display:flex;align-items:center;justify-content:center;height:100%;color:#96999f;font-size:.78rem;padding:1rem;text-align:center;background:linear-gradient(145deg,#26292f,#17191d)}

/* AREAS */
.gg-area-wrap{background:#111316;border-radius:24px;padding:1.7rem;margin-top:1rem;border:1px solid #272a30}
.gg-area-title{color:white;font-size:2rem;font-weight:900;letter-spacing:-.035em;margin-bottom:.2rem}
.gg-area-intro{color:#bcb7af;font-size:.91rem;margin-bottom:1.1rem;max-width:900px}
.gg-area-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem}
.gg-area{background:#1a1c20;border:1px solid #30333a;border-radius:16px;padding:1rem 1.05rem;min-height:214px;transition:.18s ease}
.gg-area:hover{transform:translateY(-2px);border-color:#704a2a;background:#1d1f23}
.gg-area-icon{font-size:1.5rem;margin-bottom:.45rem}
.gg-area-name{font-size:1.05rem;color:white;font-weight:850;margin-bottom:.22rem}
.gg-area-desc{font-size:.78rem;color:#aaa69f;line-height:1.4;margin-bottom:.55rem}
.gg-module{font-size:.77rem;color:#ddd7ce;padding:.13rem 0;line-height:1.35}
.gg-module:before{content:"•";color:var(--gg-orange);margin-right:.38rem}
.gg-chip{display:inline-block;color:#ffb15a;background:#342519;border:1px solid #68441f;border-radius:999px;padding:.08rem .42rem;font-size:.62rem;margin-left:.3rem}

/* PHILOSOPHY */
.gg-flow{display:grid;grid-template-columns:repeat(5,1fr);gap:.65rem;margin-top:.85rem}
.gg-step{background:#fff;border-radius:14px;border:1px solid #ded7cd;padding:.9rem .85rem;min-height:122px;box-shadow:0 4px 14px rgba(0,0,0,.045)}
.gg-step-n{color:var(--gg-orange);font-size:.72rem;font-weight:900;letter-spacing:.11em}
.gg-step-b{font-weight:850;color:#1e2024;margin:.25rem 0;font-size:.96rem}
.gg-step-s{font-size:.76rem;line-height:1.4;color:#6b6862}

/* MACHINE FIRST */
.gg-machine{display:grid;grid-template-columns:.9fr 1.1fr;background:#ece7df;border:1px solid #d9d1c6;border-radius:22px;overflow:hidden;margin:1.5rem 0}
.gg-machine-dark{background:#181a1e;color:white;padding:2rem}
.gg-machine-dark h3{font-size:1.75rem;line-height:1.08;margin:.3rem 0 .7rem;color:white}
.gg-machine-dark p{color:#c5c0b8;font-size:.9rem;line-height:1.55}
.gg-machine-list{padding:1.65rem 1.8rem;display:grid;grid-template-columns:1fr 1fr;gap:.55rem}
.gg-machine-item{background:white;border:1px solid #dcd4c9;border-radius:12px;padding:.8rem;font-size:.8rem;color:#4d4a45;line-height:1.4}
.gg-machine-item b{display:block;color:#1f2023;font-size:.88rem;margin-bottom:.15rem}

.gg-footer{background:#0d0e10;color:#bcb6ad;border-radius:20px 20px 0 0;padding:1.35rem 1.5rem;margin-top:1.6rem;font-size:.78rem;line-height:1.45}
.gg-footer strong{color:#ffad45}

@media(max-width:1050px){
  .gg-hero-inner{grid-template-columns:1fr}.gg-hero-copy{padding:3rem 2.2rem}.gg-title{font-size:3.6rem}.gg-hero-media{min-height:400px}.gg-hero-media img{min-height:400px}
  .gg-darkstrip-grid{grid-template-columns:1fr 1fr}.gg-gallery{grid-template-columns:1fr 1fr}.gg-photo-card:first-child{grid-column:1/-1}.gg-area-grid{grid-template-columns:1fr 1fr}.gg-flow{grid-template-columns:1fr 1fr}.gg-flow .gg-step:last-child{grid-column:1/-1}.gg-machine{grid-template-columns:1fr}
}
@media(max-width:720px){
  .gg-title{font-size:3rem}.gg-hero-copy{padding:2.3rem 1.45rem}.gg-darkstrip-grid,.gg-gallery,.gg-area-grid,.gg-flow,.gg-machine-list{grid-template-columns:1fr}.gg-photo-card:first-child{grid-column:auto}.gg-section-head{display:block}.gg-section-copy{margin-top:.45rem}
}
</style>
''', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Hero
# -----------------------------------------------------------------------------
if hero_uri:
    hero_media = f'<img src="{hero_uri}" alt="GG DIMEC · MechLab">'
else:
    hero_media = '<div class="gg-photo-placeholder">La portada buscará automáticamente tus fotografías existentes en <b>assets/</b>, <b>images/</b> o <b>static/</b>.</div>'

st.markdown(f'''
<div class="gg-hero">
  <div class="gg-hero-inner">
    <div class="gg-hero-copy">
      <div class="gg-eyebrow">GG DIMEC · Ingeniería Mecánica Aplicada</div>
      <div class="gg-title">MECH<span>LAB</span></div>
      <div class="gg-subtitle"><b>Máquinas primero.</b> Un laboratorio digital para ver el fenómeno, construir el modelo, calcular y desarrollar criterio de ingeniería.</div>
      <div class="gg-pills">
        <div class="gg-pill"><strong>3D</strong> cuando ayuda a comprender</div>
        <div class="gg-pill"><strong>A/B</strong> para comparar diseños</div>
        <div class="gg-pill"><strong>Terreno</strong> conectado con teoría</div>
        <div class="gg-pill"><strong>Máquinas</strong> como hilo conductor</div>
      </div>
    </div>
    <div class="gg-hero-media">
      {hero_media}
      <div class="gg-photo-tag"><b>MECHLAB</b><br>Del fenómeno físico a la decisión de ingeniería.</div>
    </div>
  </div>
</div>
''', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Statement oscuro: devuelve presencia de marca.
# -----------------------------------------------------------------------------
st.markdown('''
<div class="gg-darkstrip">
  <div class="gg-darkstrip-grid">
    <div class="gg-dark-lead">
      <div class="gg-kicker">Una plataforma que creció desde la práctica</div>
      <div class="gg-dark-title">No es una colección de calculadoras.</div>
      <div class="gg-dark-copy">MechLab conecta máquinas, modelos físicos, ecuaciones, animación 3D y comparación para que el estudiante comprenda <b>qué está ocurriendo</b> antes de quedarse solamente con el resultado numérico.</div>
    </div>
    <div class="gg-value"><div class="gg-value-n">01</div><div class="gg-value-t"><b>Fenómeno</b><br>Primero reconocer qué hace realmente la máquina o el sistema.</div></div>
    <div class="gg-value"><div class="gg-value-n">02</div><div class="gg-value-t"><b>Modelo</b><br>Después simplificar, idealizar y definir variables con sentido físico.</div></div>
    <div class="gg-value"><div class="gg-value-n">03</div><div class="gg-value-t"><b>Criterio</b><br>El cálculo termina en interpretación, comparación y decisión.</div></div>
  </div>
</div>
''', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Fotos reales / terreno.
# -----------------------------------------------------------------------------
st.markdown('''
<div class="gg-section">
  <div class="gg-section-head">
    <div><div class="gg-section-kicker">Ingeniería real</div><div class="gg-section-title">Del terreno al modelo.</div></div>
    <div class="gg-section-copy">La plataforma nace de observar equipos, enseñar mecánica y traducir fenómenos reales a modelos que puedan explorarse. Por eso la portada vuelve a mostrar personas, máquinas y contexto.</div>
  </div>
</div>
''', unsafe_allow_html=True)

caps = [
    ('Terreno y máquinas', 'Observar antes de modelar: geometría, operación, cargas y comportamiento real.'),
    ('Docencia y explicación', 'Convertir una ecuación en una representación que permita entender el fenómeno.'),
    ('Desarrollo y simulación', 'Unir cálculo, programación, visualización 3D y criterio de ingeniería.'),
]
photo_cards = []
for i in range(3):
    p = field_photos[i] if i < len(field_photos) else None
    uri = data_uri(p)
    title, desc = caps[i]
    if uri:
        media = f'<img src="{uri}" alt="{title}">'
    else:
        media = '<div class="gg-photo-empty">Esta tarjeta reutilizará automáticamente una foto real disponible en tus carpetas de imágenes.</div>'
    photo_cards.append(f'<div class="gg-photo-card">{media}<div class="cap"><b>{title}</b><span>{desc}</span></div></div>')

st.markdown('<div class="gg-gallery">' + ''.join(photo_cards) + '</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Áreas: contenido actual, estética potente restaurada.
# -----------------------------------------------------------------------------
st.markdown('''
<div class="gg-area-wrap">
  <div class="gg-area-title">El laboratorio que ya construimos</div>
  <div class="gg-area-intro">MechLab hoy cubre varias áreas de ingeniería mecánica, pero todas mantienen la misma lógica visual y conceptual. El menú superior sigue siendo la navegación principal; esta portada explica el mapa completo.</div>
  <div class="gg-area-grid">
    <div class="gg-area">
      <div class="gg-area-icon">🏗️</div><div class="gg-area-name">Resistencia y Estructuras</div>
      <div class="gg-area-desc">De cargas y tensiones a deformación, estabilidad y comportamiento de secciones.</div>
      <div class="gg-module">Vigas · V, M, tensiones y deflexión <span class="gg-chip">3D</span></div>
      <div class="gg-module">Columnas · compresión y pandeo <span class="gg-chip">3D</span></div>
      <div class="gg-module">Torsión · giro y comparación <span class="gg-chip">3D</span></div>
      <div class="gg-module">Mohr 2D/3D · Von Mises · perfiles</div>
    </div>
    <div class="gg-area">
      <div class="gg-area-icon">🌀</div><div class="gg-area-name">Dinámica y Vibraciones</div>
      <div class="gg-area-desc">De la vibración libre al comportamiento de máquinas rotatorias y diagnóstico.</div>
      <div class="gg-module">1GDL libre · plano de fase y energía <span class="gg-chip">3D</span></div>
      <div class="gg-module">Forzada · resonancia, desbalance y base <span class="gg-chip">3D</span></div>
      <div class="gg-module">2GDL · modos, TMD y antirresonancia <span class="gg-chip">3D</span></div>
      <div class="gg-module">FFT · órdenes · waterfall · sensores <span class="gg-chip">3D</span></div>
    </div>
    <div class="gg-area">
      <div class="gg-area-icon">🌊</div><div class="gg-area-name">Fluidos y Energía</div>
      <div class="gg-area-desc">Energía del flujo, pérdidas y operación de sistemas hidráulicos.</div>
      <div class="gg-module">Continuidad y Bernoulli <span class="gg-chip">3D</span></div>
      <div class="gg-module">Reynolds y pérdidas <span class="gg-chip">3D</span></div>
      <div class="gg-module">Bombas y curva del sistema <span class="gg-chip">3D</span></div>
      <div class="gg-module">Propiedades y ciclos termodinámicos</div>
    </div>
    <div class="gg-area">
      <div class="gg-area-icon">📏</div><div class="gg-area-name">Metrología y Calidad</div>
      <div class="gg-area-desc">Especificar, medir, interpretar y decidir sobre geometría real.</div>
      <div class="gg-module">ISO GPS · datums y zonas <span class="gg-chip">3D</span></div>
      <div class="gg-module">Ajustes ISO · juego, transición e interferencia <span class="gg-chip">3D</span></div>
      <div class="gg-module">Medición e incertidumbre</div>
    </div>
    <div class="gg-area">
      <div class="gg-area-icon">⚙️</div><div class="gg-area-name">Máquinas y Componentes</div>
      <div class="gg-area-desc">La máquina no es el último capítulo: es el punto de partida y el lugar donde convergen los modelos.</div>
      <div class="gg-module">Ejes, rotores, soportes y bombas</div>
      <div class="gg-module">Comparación de diseños y sensibilidad</div>
      <div class="gg-module">Lectura de componentes y sistemas reales</div>
    </div>
    <div class="gg-area">
      <div class="gg-area-icon">🧭</div><div class="gg-area-name">Una forma común de aprender</div>
      <div class="gg-area-desc">La interfaz cambia según el fenómeno; la lógica de aprendizaje se mantiene.</div>
      <div class="gg-module">Configurar → observar → calcular</div>
      <div class="gg-module">Comparar → interpretar</div>
      <div class="gg-module">3D como apoyo, no como decoración</div>
    </div>
  </div>
</div>
''', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Flujo de trabajo transversal.
# -----------------------------------------------------------------------------
st.markdown('''
<div class="gg-section">
  <div class="gg-section-head">
    <div><div class="gg-section-kicker">Método MechLab</div><div class="gg-section-title">Una misma lógica en todo el portal.</div></div>
    <div class="gg-section-copy">Puedes entrar por vigas, vibraciones, bombas o tolerancias. La pregunta siempre es la misma: ¿qué está pasando físicamente y cómo puedo demostrarlo?</div>
  </div>
  <div class="gg-flow">
    <div class="gg-step"><div class="gg-step-n">01</div><div class="gg-step-b">Fenómeno</div><div class="gg-step-s">Identifica la máquina, componente o situación física que quieres comprender.</div></div>
    <div class="gg-step"><div class="gg-step-n">02</div><div class="gg-step-b">Modelo</div><div class="gg-step-s">Define idealizaciones, variables, condiciones de borde y alcance.</div></div>
    <div class="gg-step"><div class="gg-step-n">03</div><div class="gg-step-b">Cálculo</div><div class="gg-step-s">Relaciona ecuaciones, diagramas y magnitudes con el comportamiento físico.</div></div>
    <div class="gg-step"><div class="gg-step-n">04</div><div class="gg-step-b">Visualización</div><div class="gg-step-s">Usa 3D, animaciones y comparadores para ver lo que las ecuaciones representan.</div></div>
    <div class="gg-step"><div class="gg-step-n">05</div><div class="gg-step-b">Interpretación</div><div class="gg-step-s">Explica qué cambia, por qué cambia y qué significa para el sistema.</div></div>
  </div>
</div>
''', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Máquina como enfoque central.
# -----------------------------------------------------------------------------
st.markdown('''
<div class="gg-machine">
  <div class="gg-machine-dark">
    <div class="gg-kicker">Máquinas primero</div>
    <h3>La teoría se reconoce mejor cuando tiene un lugar donde vivir.</h3>
    <p>Una viga puede ser un soporte. Una vibración puede venir de un rotor. Una pérdida hidráulica cambia el punto de operación de una bomba. Una tolerancia define si dos componentes realmente pueden montarse. MechLab busca que esas conexiones estén visibles.</p>
  </div>
  <div class="gg-machine-list">
    <div class="gg-machine-item"><b>Ver</b>Reconocer el fenómeno en una geometría o sistema comprensible.</div>
    <div class="gg-machine-item"><b>Relacionar</b>Conectar el fenómeno con variables, ecuaciones y supuestos.</div>
    <div class="gg-machine-item"><b>Explorar</b>Cambiar parámetros y observar sensibilidad sin perder la física.</div>
    <div class="gg-machine-item"><b>Decidir</b>Terminar con una lectura de ingeniería, no solo con un número.</div>
  </div>
</div>
''', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Rutas y alcance sin cargar visualmente la portada.
# -----------------------------------------------------------------------------
with st.expander('📚 Rutas sugeridas para recorrer MechLab', expanded=False):
    a, b, c = st.columns(3)
    with a:
        st.markdown('''**Resistencia y máquinas**
- Tensiones y Mohr
- Vigas
- Columnas
- Torsión
- Von Mises
- Perfiles y geometría''')
    with b:
        st.markdown('''**Dinámica de máquinas**
- Vibración libre
- Vibración forzada
- Desbalance / base
- 2GDL y TMD
- FFT / órdenes / diagnóstico''')
    with c:
        st.markdown('''**Fluidos y sistemas**
- Continuidad y Bernoulli
- Reynolds y pérdidas
- Bombas y punto de operación
- Energía y termodinámica''')

with st.expander('🧪 Cómo interpretar los modelos 3D', expanded=False):
    st.markdown('''
Los modelos 3D de MechLab tienen una función **didáctica y física**. En varios laboratorios se amplifican desplazamientos, giros, deformaciones o movimientos para que el fenómeno pueda verse. Esa amplificación visual **no modifica los valores calculados**. Cuando una representación requiere una simplificación —por ejemplo partículas de flujo, modos críticos o una geometría esquemática— debe leerse junto con el modelo y sus supuestos.
''')

st.markdown('''
<div class="gg-footer">
  <strong>GG DIMEC · MECHLAB</strong><br>
  Ingeniería mecánica para comprender máquinas, modelar fenómenos y desarrollar criterio. Navega por las áreas desde el menú superior.
</div>
''', unsafe_allow_html=True)
