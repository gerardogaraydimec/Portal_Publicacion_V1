from __future__ import annotations
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
HEADER_LOGO = ROOT / "assets" / "logo_header_unificado.png"

_CSS = """
<style>
:root{
  --gg-orange:#f28e1c;
  --gg-orange-dark:#db7810;
  --gg-text:#262730;
  --gg-muted:#737986;
}
.gg-brand-kicker{
  color:var(--gg-orange-dark);
  font-weight:800;
  letter-spacing:.055em;
  font-size:.82rem;
  text-transform:uppercase;
  margin-bottom:.28rem;
}
.gg-app-title{
  color:var(--gg-text);
  font-weight:800;
  font-size:clamp(2.05rem, 3.0vw, 3.25rem);
  line-height:1.06;
  margin:0 0 .52rem 0;
}
.gg-app-subtitle{
  color:var(--gg-muted);
  font-size:1.02rem;
  line-height:1.45;
  margin:0;
}
.gg-header-rule{
  height:1px;
  background:#eceff2;
  margin:.72rem 0 1.0rem 0;
}
@media (max-width: 760px){
  .gg-app-title{font-size:2.0rem;}
  .gg-app-subtitle{font-size:.94rem;}
  .gg-brand-kicker{font-size:.74rem;}
}
</style>
"""


def render_app_header(
    title: str,
    subtitle: str,
    section: str,
    logo_width: int = 190,
    divider: bool = True,
) -> None:
    """Encabezado corporativo común para todas las herramientas MechLab."""
    st.markdown(_CSS, unsafe_allow_html=True)

    logo_col, text_col = st.columns([0.92, 5.08], vertical_alignment="center")
    with logo_col:
        if HEADER_LOGO.exists():
            # Fixed width avoids the cropping/scaling behavior seen with
            # use_container_width=True in narrow or compact layouts.
            st.image(str(HEADER_LOGO), width=logo_width)

    with text_col:
        st.markdown(
            f'<div class="gg-brand-kicker">GG DIMEC · MECHLAB · {section}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="gg-app-title">{title}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="gg-app-subtitle">{subtitle}</div>',
            unsafe_allow_html=True,
        )

    if divider:
        st.markdown('<div class="gg-header-rule"></div>', unsafe_allow_html=True)
