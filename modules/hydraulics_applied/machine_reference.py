from __future__ import annotations

from pathlib import Path
import streamlit as st

_ROOT = Path(__file__).resolve().parents[2]
_ASSET_DIR = _ROOT / "assets" / "hydraulics_applied" / "machine_renders"

_REFERENCES = {
    ("Camión minero", "Levante de tolva"): (
        "mining_truck_hydraulic.png",
        "Camión minero · ubicación física del sistema de levante",
        "Use esta vista solo para reconocer tolva, cilindros de levante, chasis y unidad hidráulica. "
        "La trayectoria del aceite, la condición de cada puerto y las lecturas esperadas se determinan en el plano funcional.",
    ),
    ("Cargador frontal", "Levante de brazos LS"): (
        "wheel_loader_hydraulic.png",
        "Cargador frontal · ubicación de implementos hidráulicos",
        "Use esta referencia para ubicar brazos, balde, cilindros y unidad hidráulica. "
        "Los estados Raise/Hold/Float/Lower se interpretan en el esquema hidráulico y en las lecturas asociadas.",
    ),
    ("Cargador frontal", "Inclinación de balde"): (
        "wheel_loader_hydraulic.png",
        "Cargador frontal · balde y cilindro de tilt",
        "Use esta vista para localizar balde, brazos y cilindro de inclinación. "
        "La función Rollback/Hold/Dump se estudia en el plano funcional, no en esta imagen.",
    ),
}


def reference_available(machine: str, subsystem: str) -> bool:
    entry = _REFERENCES.get((machine, subsystem))
    return bool(entry and (_ASSET_DIR / entry[0]).exists())


def render_machine_reference(machine: str, subsystem: str, state: str) -> None:
    entry = _REFERENCES.get((machine, subsystem))
    if not entry:
        st.info("No hay una referencia visual definida para este subsistema.")
        return

    filename, title, note = entry
    path = _ASSET_DIR / filename
    if not path.exists():
        st.warning(f"No se encontró el recurso visual: {path.name}")
        return

    st.markdown(
        f"""
        <div style="background:#202126;border:1px solid #34363c;border-radius:14px 14px 0 0;padding:.72rem 1rem;color:#f7f1e8;">
            <div style="font-weight:800;font-size:1rem;">{title}</div>
            <div style="color:#b7bbc3;font-size:.82rem;margin-top:.15rem;">Estado seleccionado: <b style="color:#f28e1c;">{state}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.image(str(path), use_container_width=True)
    st.markdown(
        f"""
        <div style="margin-top:-.4rem;border:1px solid #e0d9cf;border-top:0;border-radius:0 0 14px 14px;padding:.8rem 1rem;background:#fffaf4;line-height:1.48;">
            <b>Cómo usar esta referencia:</b> {note}<br>
            <span style="color:#6f7379;font-size:.86rem;">Representación didáctica de contexto; no es un plano OEM ni una simulación cinemática.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
