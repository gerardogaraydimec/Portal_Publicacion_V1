from __future__ import annotations
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent
HEADER_LOGO = ROOT / "assets" / "logo_header_unificado.png"

_CSS = """
<style>
.st-key-bv3_brand_scope{
  --gg-orange:#f28e1c;
  --gg-orange-dark:#b85d18;
  --gg-text:#292a2d;
  --gg-muted:#6f685f;
}
.st-key-bv3_brand_scope .gg-brand-kicker{
  color:var(--gg-orange-dark);
  font-weight:800;
  letter-spacing:.055em;
  font-size:.82rem;
  text-transform:uppercase;
  margin-bottom:.28rem;
}
.st-key-bv3_brand_scope .gg-app-title{
  color:var(--gg-text);
  font-weight:800;
  font-size:clamp(1.85rem, 2.5vw, 2.65rem);
  line-height:1.06;
  margin:0 0 .52rem 0;
}
.st-key-bv3_brand_scope .gg-app-subtitle{
  color:var(--gg-muted);
  font-size:1.02rem;
  line-height:1.45;
  margin:0;
}
.st-key-bv3_brand_scope .gg-header-rule{
  height:1px;
  background:#e4dbcf;
  margin:.72rem 0 1.0rem 0;
}
@media (max-width: 760px){
  .st-key-bv3_brand_scope .gg-app-title{font-size:2.0rem;}
  .st-key-bv3_brand_scope .gg-app-subtitle{font-size:.94rem;}
  .st-key-bv3_brand_scope .gg-brand-kicker{font-size:.74rem;}
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
