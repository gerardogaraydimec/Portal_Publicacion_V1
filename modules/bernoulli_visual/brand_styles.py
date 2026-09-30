"""GG DIMEC styles scoped to this module; no global portal theme is replaced."""
import streamlit as st

CSS = """
/* Styles apply only while the Bernoulli containers are present. */
.st-key-bv3_brand_scope, .st-key-bv3_sidebar_scope {
 --gg-orange:#f28e1c; --gg-orange-dark:#b85d18; --gg-text:#292a2d;
 --gg-black:#292a2d; --gg-muted:#6f685f; --gg-line:#e4dbcf;
 --primary-color:#b85d18; --text-color:#292a2d;
 color:#292a2d; font-family:'Segoe UI',Arial,sans-serif;
}
.st-key-bv3_brand_scope .gg-case {
 border:1px solid var(--gg-line); border-left:5px solid var(--gg-orange);
 border-radius:14px; padding:1rem 1.1rem; background:#fbf7f0; margin:.25rem 0 .85rem;
}
.st-key-bv3_brand_scope .gg-case h3 { color:#292a2d; }
.st-key-bv3_brand_scope .gg-note {
 border:1px solid #e4dbcf; background:#fbf7f0; border-radius:12px;
 padding:.9rem 1rem; line-height:1.55; color:#62594e;
}
.st-key-bv3_brand_scope [data-testid="stMetric"] {
 border:1px solid #e4dbcf; border-top:3px solid #f28e1c; border-radius:12px;
 padding:.7rem .9rem; background:#fffdfa;
}
.st-key-bv3_brand_scope [data-testid="stMetricValue"] { color:#292a2d; }
.st-key-bv3_brand_scope [data-testid="stMetricLabel"] { color:#6f685f; }
.st-key-bv3_brand_scope [data-baseweb="tab-list"] { gap:6px; border-bottom:1px solid #e4dbcf; }
.st-key-bv3_brand_scope button[role="tab"] { color:#62594e; padding:.6rem .9rem; border-radius:8px 8px 0 0; }
.st-key-bv3_brand_scope button[role="tab"][aria-selected="true"] { color:#994a12!important; background:#f8e8d5; }
.st-key-bv3_brand_scope [data-baseweb="tab-highlight"] { background-color:#f28e1c!important; }
:is(.st-key-bv3_brand_scope,.st-key-bv3_sidebar_scope) :is([data-testid="stButton"],[data-testid="stDownloadButton"]) button {
 border:1px solid #cba880; border-radius:8px; background:#fbf0e2; color:#894311;
}
:is(.st-key-bv3_brand_scope,.st-key-bv3_sidebar_scope) :is([data-testid="stButton"],[data-testid="stDownloadButton"]) button:hover {
 border-color:#b85d18; background:#f4dfc5; color:#71360d;
}
:is(.st-key-bv3_brand_scope,.st-key-bv3_sidebar_scope) button:focus-visible {
 outline:2px solid #b85d18; outline-offset:2px;
}
:is(.st-key-bv3_brand_scope,.st-key-bv3_sidebar_scope) [data-testid="stExpander"] details {
 border-color:#e4dbcf; border-radius:10px;
}
:is(.st-key-bv3_brand_scope,.st-key-bv3_sidebar_scope) [data-testid="stExpander"] summary { color:#51483e; }
section[data-testid="stSidebar"]:has(.st-key-bv3_sidebar_scope) { background:#fbf7f0; }
.st-key-bv3_sidebar_scope :is(h1,h2,h3) { color:#292a2d; }
.st-key-bv3_sidebar_scope h2 { font-size:1.15rem; }
.st-key-bv3_sidebar_scope :is([data-testid="stNumberInputContainer"],[data-baseweb="select"]>div) {
 background:#fffdfa; border-color:#d8cdbf; color:#292a2d;
}
.st-key-bv3_sidebar_scope input { color:#292a2d; caret-color:#b85d18; }
.st-key-bv3_sidebar_scope input:disabled { color:#8a8175; }
.st-key-bv3_sidebar_scope hr { border-color:#e4dbcf; }
.st-key-bv3_sidebar_scope [data-testid="stCaptionContainer"] { color:#6f685f; }
"""


def apply_brand_styles() -> None:
    st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)
