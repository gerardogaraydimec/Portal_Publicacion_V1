"""A static Streamlit component; no npm, build step, or global app changes."""
from __future__ import annotations
from pathlib import Path
import streamlit.components.v1 as components

_COMPONENT = components.declare_component(
    'mechlab_bernoulli_visual_ggdimec',
    path=str(Path(__file__).resolve().parent / 'frontend'),
)


def render_bernoulli_3d(payload: dict, key: str = 'mechlab_bv3_gg_scene') -> None:
    data = dict(payload)
    data['local_three'] = (Path(__file__).resolve().parent / 'frontend' / 'vendor' / 'three.module.js').is_file()
    _COMPONENT(data=data, key=key, default=None)
