from __future__ import annotations

from pathlib import Path
import streamlit as st

_ROOT = Path(__file__).resolve().parents[3]
_ASSET_DIR = _ROOT / "assets" / "hydraulics_applied" / "machine_renders"

_PREMIUM = {
    ("Camión minero", "Levante de tolva"): (
        "mining_truck_hydraulic.png",
        "Camión minero · arquitectura del sistema de levante",
        "La imagen muestra la relación espacial entre tolva, cilindros de levante, chasis y unidad hidráulica. "
        "Las líneas coloreadas son una referencia de ubicación/ruteo; el estado hidráulico exacto debe leerse en el plano funcional superior.",
    ),
    ("Cargador frontal", "Levante de brazos LS"): (
        "wheel_loader_hydraulic.png",
        "Cargador frontal · arquitectura de implementos hidráulicos",
        "La imagen permite reconocer brazos, balde, cilindros y unidad hidráulica. Para cada estado Raise/Hold/Float/Lower, "
        "la ruta activa y las presiones esperadas se leen en el plano funcional superior.",
    ),
    ("Cargador frontal", "Inclinación de balde"): (
        "wheel_loader_hydraulic.png",
        "Cargador frontal · mecanismo de balde y cilindro de tilt",
        "Use esta vista para ubicar físicamente balde, brazos, cilindro de tilt y unidad hidráulica. El cambio Rollback/Hold/Dump "
        "se interpreta con el plano funcional y, si se desea, con el 3D interactivo del estado.",
    ),
}


def premium_available(machine: str, subsystem: str) -> bool:
    entry = _PREMIUM.get((machine, subsystem))
    return bool(entry and (_ASSET_DIR / entry[0]).exists())


def render_machine_premium(machine: str, subsystem: str, state: str) -> None:
    entry = _PREMIUM.get((machine, subsystem))
    if not entry:
        st.info("No hay una vista visual de alta fidelidad definida para este subsistema.")
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
            <div style="color:#b7bbc3;font-size:.82rem;margin-top:.15rem;">Estado seleccionado en MechLab: <b style="color:#f28e1c;">{state}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.image(str(path), use_container_width=True)
    st.markdown(
        f"""
        <div style="margin-top:-.4rem;border:1px solid #e0d9cf;border-top:0;border-radius:0 0 14px 14px;padding:.8rem 1rem;background:#fffaf4;line-height:1.48;">
            <b>Cómo usar esta vista:</b> {note}<br>
            <span style="color:#6f7379;font-size:.86rem;">Representación didáctica de alta fidelidad; no corresponde a un modelo OEM específico.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
