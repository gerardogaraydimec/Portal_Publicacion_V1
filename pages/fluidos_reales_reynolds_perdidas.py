from __future__ import annotations

import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from modules.ui_brand import render_app_header
from modules.reynolds_engine import (
    FLUID_PRESETS,
    ROUGHNESS_PRESETS_MM,
    energy_profile,
    moody_curves,
    normalized_velocity_profile,
    solve_reynolds_losses,
)
from modules.reynolds_visual3d import render_reynolds_3d

st.markdown(
    """
<style>
.block-container{max-width:1480px;padding-top:1.25rem!important}
.gg-note{border:1px solid #e9e2d7;border-left:4px solid #f28e1c;border-radius:12px;padding:.85rem 1rem;background:#fffaf3}
.gg-card{border:1px solid #e7dfd2;border-radius:14px;background:#fffdf9;padding:1rem;height:100%}
.gg-mini{font-size:.92rem;color:#555}
</style>
""",
    unsafe_allow_html=True,
)

render_app_header(
    title="Fluidos reales · Reynolds y pérdidas",
    subtitle="Régimen de flujo · rugosidad · factor de fricción · Darcy–Weisbach · pérdidas singulares · HGL/EGL · visualización 3D.",
    section="MECÁNICA DE FLUIDOS",
    logo_width=188,
)

with st.sidebar:
    st.header("Fluido")
    fluid_name = st.selectbox("Fluido", list(FLUID_PRESETS) + ["Personalizado"])
    if fluid_name == "Personalizado":
        rho = float(st.number_input("Densidad ρ [kg/m³]", min_value=0.001, value=998.2, step=10.0))
        mu = float(st.number_input("Viscosidad dinámica μ [Pa·s]", min_value=1e-8, value=1.002e-3, format="%.4e"))
    else:
        rho, mu = FLUID_PRESETS[fluid_name]
        st.caption(f"ρ = {rho:g} kg/m³ · μ = {mu:.4g} Pa·s")

    st.divider()
    st.header("Tubería")
    D_mm = float(st.number_input("Diámetro interior D [mm]", min_value=1.0, value=80.0, step=5.0))
    L_m = float(st.number_input("Longitud L [m]", min_value=0.05, value=20.0, step=1.0))
    rough_name = st.selectbox("Rugosidad", list(ROUGHNESS_PRESETS_MM) + ["Personalizada"])
    if rough_name == "Personalizada":
        eps_mm = float(st.number_input("Rugosidad absoluta ε [mm]", min_value=0.0, value=0.045, step=0.005, format="%.4f"))
    else:
        eps_mm = ROUGHNESS_PRESETS_MM[rough_name]
        st.caption(f"ε = {eps_mm:g} mm")

    st.divider()
    st.header("Condición de flujo")
    flow_mode = st.radio("Definir mediante", ["Caudal Q", "Velocidad media V"], horizontal=True)
    if flow_mode == "Caudal Q":
        Q_ls = float(st.number_input("Caudal Q [L/s]", min_value=0.0, value=8.0, step=0.5))
        velocity_input = None
        q_input = Q_ls / 1000.0
    else:
        velocity_input = float(st.number_input("Velocidad media V [m/s]", min_value=0.0, value=1.6, step=0.1))
        q_input = None

    st.divider()
    st.header("Pérdidas singulares")
    K_total = float(st.number_input("ΣK", min_value=0.0, value=2.0, step=0.25, help="Suma de coeficientes de pérdidas locales."))
    minor_pos = float(st.slider("Ubicación esquemática x/L", 0.05, 0.95, 0.70, 0.05, help="Solo ubica visualmente el salto de pérdida singular; no modifica su magnitud."))

D_m = D_mm / 1000.0
eps_m = eps_mm / 1000.0
res = solve_reynolds_losses(
    rho_kgm3=rho,
    mu_pas=mu,
    diameter_m=D_m,
    length_m=L_m,
    roughness_m=eps_m,
    minor_k=K_total,
    flow_rate_m3s=q_input,
    velocity_ms=velocity_input,
)
Q_m3s = res.velocity_ms * res.area_m2

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Velocidad media", f"{res.velocity_ms:.3f} m/s")
m2.metric("Reynolds", f"{res.reynolds:.3e}")
m3.metric("Régimen", res.regime)
m4.metric("Factor Darcy f", f"{res.friction_factor:.4f}")
m5.metric("Pérdida total hL", f"{res.total_loss_m:.3f} m")
m6.metric("Δp equivalente", f"{res.pressure_drop_pa/1000:.2f} kPa")

st.markdown(
    """
<div class="gg-note"><b>Ruta física:</b> propiedades del fluido + velocidad + diámetro → <b>Re</b> → régimen de flujo → <b>f</b> y rugosidad relativa → pérdidas distribuidas y singulares → caída de energía y presión.</div>
""",
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "📘 Concepto",
    "🌊 Flujo 3D",
    "📊 Reynolds y fricción",
    "📉 Pérdidas · HGL/EGL",
    "⚖️ Comparador",
    "∑ Ecuaciones",
    "🧠 Interpretación",
])

with tabs[0]:
    st.subheader("Qué cambia cuando el fluido es real")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="gg-card"><b>Reynolds</b><br><div class="gg-mini">Compara efectos inerciales y viscosos. Ayuda a reconocer si el flujo interno tiende a ser ordenado, transicional o turbulento.</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="gg-card"><b>Fricción</b><br><div class="gg-mini">La viscosidad y la interacción con la pared disipan energía. En turbulencia, la rugosidad relativa ε/D también adquiere importancia.</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="gg-card"><b>Pérdidas</b><br><div class="gg-mini">Darcy–Weisbach representa la pérdida distribuida; accesorios, cambios geométricos y válvulas se modelan mediante coeficientes K.</div></div>', unsafe_allow_html=True)

    st.markdown("### Régimen actual")
    if res.regime_key == "laminar":
        st.success("El caso está en régimen laminar: predominan los efectos viscosos y, para flujo completamente desarrollado, el perfil de velocidad es parabólico.", icon="🟢")
    elif res.regime_key == "transition":
        st.warning("El caso cae en la zona de transición. Los límites 2300–4000 son referencias clásicas; el comportamiento real puede cambiar con perturbaciones, entrada, vibraciones y rugosidad.", icon="🟠")
    else:
        st.info("El caso está en régimen turbulento: aparecen fluctuaciones, mezcla radial intensa y una distribución de velocidad más plana en el núcleo.", icon="🔵")

with tabs[1]:
    st.subheader("Flujo 3D dentro de la tubería")
    c1, c2 = st.columns([1, 2.2])
    with c1:
        probe = float(st.slider("Posición de observación x/L", 0.0, 1.0, 0.50, 0.05))
        show_energy = st.toggle("Mostrar HGL/EGL en el modelo", value=True)
        st.markdown(
            '<div class="gg-card"><b>Cómo leer la animación</b><br><div class="gg-mini">Las partículas representan trazadores. En laminar se desplazan de forma ordenada; en transición aparecen perturbaciones moderadas; en turbulento se intensifican las fluctuaciones. No es CFD: es una representación didáctica ligada al Reynolds calculado.</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        render_reynolds_3d(
            {
                "regime": res.regime,
                "regime_key": res.regime_key,
                "reynolds": res.reynolds,
                "friction_factor": res.friction_factor,
                "velocity_ms": res.velocity_ms,
                "velocity_head": res.velocity_head_m,
                "major_loss": res.major_loss_m,
                "minor_loss": res.minor_loss_m,
                "loss_total": res.total_loss_m,
                "minor_k": K_total,
                "minor_location_ratio": minor_pos,
                "probe_ratio": probe,
                "show_energy": show_energy,
            },
            height=690,
            key="reynolds_main_3d",
        )
    st.caption("La amplitud de las fluctuaciones de partículas es gráfica. El cálculo de Re, f y pérdidas es independiente de esa animación.")

with tabs[2]:
    st.subheader("Reynolds, perfil de velocidad y factor de fricción")
    c1, c2 = st.columns(2)
    rr, uu, profile_note = normalized_velocity_profile(res.reynolds, res.regime_key)
    figp = go.Figure()
    figp.add_trace(go.Scatter(x=uu, y=rr, line=dict(width=3), name="u/U"))
    figp.update_layout(height=390, margin=dict(l=20, r=20, t=15, b=20), xaxis_title="u / Vmedia", yaxis_title="r / R", showlegend=False)
    c1.plotly_chart(figp, use_container_width=True)
    c1.caption(profile_note)

    curves = moody_curves()
    figm = go.Figure()
    for relr, (rex, ff) in curves.items():
        label = "liso" if relr == 0 else f"ε/D={relr:g}"
        figm.add_trace(go.Scatter(x=rex, y=ff, mode="lines", line=dict(width=1.5), name=label))
    figm.add_trace(go.Scatter(x=[max(res.reynolds, 500)], y=[res.friction_factor], mode="markers", marker=dict(size=11), name="Caso actual"))
    figm.update_xaxes(type="log", title="Re")
    figm.update_yaxes(type="log", title="Factor Darcy f")
    figm.update_layout(height=390, margin=dict(l=20, r=20, t=15, b=20), legend=dict(orientation="h", y=-0.2))
    c2.plotly_chart(figm, use_container_width=True)
    c2.caption(res.friction_method)

    a, b, c, d = st.columns(4)
    a.metric("ε/D", f"{res.relative_roughness:.3e}")
    b.metric("τ pared", f"{res.wall_shear_pa:.2f} Pa")
    c.metric("V²/2g", f"{res.velocity_head_m:.4f} m")
    d.metric("Q", f"{Q_m3s*1000:.3f} L/s")

with tabs[3]:
    st.subheader("Dónde se pierde la energía")
    x, cumulative, egl, hgl = energy_profile(res, L_m, minor_pos)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=egl, mode="lines", line=dict(width=3), name="EGL"))
    fig.add_trace(go.Scatter(x=x, y=hgl, mode="lines", line=dict(width=3), name="HGL"))
    fig.update_layout(height=410, margin=dict(l=20, r=20, t=15, b=20), xaxis_title="x [m]", yaxis_title="Altura relativa [m]", legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pérdida distribuida hf", f"{res.major_loss_m:.3f} m")
    c2.metric("Pérdida singular hm", f"{res.minor_loss_m:.3f} m")
    c3.metric("Pérdida total hL", f"{res.total_loss_m:.3f} m")
    c4.metric("Potencia hidráulica disipada", f"{res.hydraulic_power_w:.1f} W")
    st.caption("La ubicación de la pérdida singular en el gráfico es esquemática y corresponde al control x/L de la barra lateral. Su magnitud depende de ΣK, no de esa ubicación.")

with tabs[4]:
    st.subheader("Comparar dos tuberías bajo el mismo fluido")
    st.write("El caso A es el definido en la barra lateral. Para B se mantienen ρ y μ y puedes cambiar geometría, caudal, rugosidad y pérdidas singulares.")
    ca, cb = st.columns(2)
    with ca:
        st.markdown("#### Caso A · actual")
        st.write(f"D = **{D_mm:.1f} mm** · L = **{L_m:.1f} m** · Q = **{Q_m3s*1000:.2f} L/s**")
        st.write(f"ε = **{eps_mm:g} mm** · ΣK = **{K_total:g}**")
    with cb:
        st.markdown("#### Caso B")
        D2_mm = float(st.number_input("D B [mm]", min_value=1.0, value=max(1.0, D_mm * 1.25), step=5.0, key="rey_cmp_D"))
        L2_m = float(st.number_input("L B [m]", min_value=0.05, value=L_m, step=1.0, key="rey_cmp_L"))
        Q2_ls = float(st.number_input("Q B [L/s]", min_value=0.0, value=Q_m3s * 1000.0, step=0.5, key="rey_cmp_Q"))
        eps2_mm = float(st.number_input("ε B [mm]", min_value=0.0, value=eps_mm, step=0.005, format="%.4f", key="rey_cmp_eps"))
        K2 = float(st.number_input("ΣK B", min_value=0.0, value=K_total, step=0.25, key="rey_cmp_K"))

    res2 = solve_reynolds_losses(
        rho_kgm3=rho,
        mu_pas=mu,
        diameter_m=D2_mm/1000.0,
        length_m=L2_m,
        roughness_m=eps2_mm/1000.0,
        minor_k=K2,
        flow_rate_m3s=Q2_ls/1000.0,
    )
    rows = [
        ("Velocidad [m/s]", res.velocity_ms, res2.velocity_ms),
        ("Re", res.reynolds, res2.reynolds),
        ("f Darcy", res.friction_factor, res2.friction_factor),
        ("hf [m]", res.major_loss_m, res2.major_loss_m),
        ("hm [m]", res.minor_loss_m, res2.minor_loss_m),
        ("hL [m]", res.total_loss_m, res2.total_loss_m),
        ("Δp [kPa]", res.pressure_drop_pa/1000, res2.pressure_drop_pa/1000),
    ]
    st.dataframe({"Magnitud": [r[0] for r in rows], "Caso A": [r[1] for r in rows], "Caso B": [r[2] for r in rows]}, use_container_width=True, hide_index=True)

    r1, r2, r3, r4 = st.columns(4)
    ratio_loss = math.inf if res.total_loss_m == 0 else res2.total_loss_m / res.total_loss_m
    ratio_vel = math.inf if res.velocity_ms == 0 else res2.velocity_ms / res.velocity_ms
    ratio_re = math.inf if res.reynolds == 0 else res2.reynolds / res.reynolds
    ratio_d = D2_mm / D_mm
    r1.metric("D B / D A", f"{ratio_d:.3f}")
    r2.metric("V B / V A", "—" if not math.isfinite(ratio_vel) else f"{ratio_vel:.3f}")
    r3.metric("Re B / Re A", "—" if not math.isfinite(ratio_re) else f"{ratio_re:.3f}")
    r4.metric("hL B / hL A", "—" if not math.isfinite(ratio_loss) else f"{ratio_loss:.3f}")

    st.markdown("#### Comparación visual 3D")
    va, vb = st.columns(2)
    with va:
        st.caption("Caso A")
        render_reynolds_3d({"regime":res.regime,"regime_key":res.regime_key,"reynolds":res.reynolds,"friction_factor":res.friction_factor,"velocity_ms":res.velocity_ms,"velocity_head":res.velocity_head_m,"major_loss":res.major_loss_m,"minor_loss":res.minor_loss_m,"loss_total":res.total_loss_m,"minor_k":K_total,"minor_location_ratio":minor_pos,"probe_ratio":.5,"show_energy":True}, height=430, key="reynolds_compare_A")
    with vb:
        st.caption("Caso B")
        render_reynolds_3d({"regime":res2.regime,"regime_key":res2.regime_key,"reynolds":res2.reynolds,"friction_factor":res2.friction_factor,"velocity_ms":res2.velocity_ms,"velocity_head":res2.velocity_head_m,"major_loss":res2.major_loss_m,"minor_loss":res2.minor_loss_m,"loss_total":res2.total_loss_m,"minor_k":K2,"minor_location_ratio":minor_pos,"probe_ratio":.5,"show_energy":True}, height=430, key="reynolds_compare_B")

with tabs[5]:
    st.subheader("Ecuaciones, en el orden en que se usan")
    st.markdown("**1 · Cinemática del flujo**")
    st.latex(r"A=\frac{\pi D^2}{4},\qquad V=\frac{Q}{A}")
    st.markdown("**2 · Reynolds**")
    st.latex(r"Re=\frac{\rho V D}{\mu}=\frac{VD}{\nu}")
    st.markdown("**3 · Rugosidad relativa y factor de fricción de Darcy**")
    st.latex(r"\varepsilon_r=\frac{\varepsilon}{D}")
    st.latex(r"f=\frac{64}{Re}\qquad\text{(laminar completamente desarrollado)}")
    st.latex(r"\frac{1}{\sqrt f}=-2\log_{10}\left(\frac{\varepsilon/D}{3.7}+\frac{2.51}{Re\sqrt f}\right)\qquad\text{(Colebrook, turbulento)}")
    st.markdown("**4 · Pérdidas**")
    st.latex(r"h_f=f\frac{L}{D}\frac{V^2}{2g}")
    st.latex(r"h_m=\sum K\,\frac{V^2}{2g}")
    st.latex(r"h_L=h_f+h_m")
    st.markdown("**5 · Caída de presión equivalente en tubería horizontal de diámetro constante**")
    st.latex(r"\Delta p=\rho g h_L")
    st.markdown("**6 · Esfuerzo cortante medio en la pared**")
    st.latex(r"\tau_w=\frac{f}{8}\rho V^2")

with tabs[6]:
    st.subheader("Qué nos está diciendo este caso")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="gg-card"><b>Régimen</b><br><div class="gg-mini">Re = <b>{res.reynolds:.3e}</b>, por lo que el caso se clasifica como <b>{res.regime}</b>. El factor de fricción de Darcy usado es <b>{res.friction_factor:.5f}</b>.</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="gg-card"><b>Disipación</b><br><div class="gg-mini">La pérdida distribuida es <b>{res.major_loss_m:.3f} m</b> y la pérdida singular es <b>{res.minor_loss_m:.3f} m</b>. La pérdida total equivale a <b>{res.pressure_drop_pa/1000:.2f} kPa</b> para este fluido.</div></div>', unsafe_allow_html=True)
    with c2:
        if res.major_loss_m > res.minor_loss_m:
            st.info("En este caso dominan las pérdidas distribuidas. Cambiar L, D, V, f o la rugosidad puede tener un efecto importante.", icon="📏")
        elif res.minor_loss_m > res.major_loss_m:
            st.info("En este caso las pérdidas singulares son comparables o mayores que las distribuidas. Conviene revisar accesorios, válvulas y cambios geométricos.", icon="🔧")
        else:
            st.info("Las pérdidas distribuidas y singulares tienen magnitud similar en este caso.", icon="⚖️")
        if res.regime_key == "transition":
            st.warning("La zona de transición no debe interpretarse como una frontera rígida. La instalación real puede transicionar antes o después según perturbaciones y condiciones de entrada.", icon="⚠️")
        st.markdown('<div class="gg-card"><b>Alcance</b><br><div class="gg-mini">El módulo usa un modelo 1D de flujo interno y una visualización 3D didáctica. No reemplaza CFD ni captura campos locales alrededor de accesorios. La ubicación gráfica de ΣK es esquemática.</div></div>', unsafe_allow_html=True)
