from __future__ import annotations
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from modules.ui_brand import render_app_header
from modules.resmat_sections import section_data, profile_params_from_sidebar, visual_section_payload
from modules.torsion_engine import solve_torsion
from modules.torsion_visual3d import render_torsion_3d

st.set_page_config(layout='wide')
st.markdown('''
<style>
.block-container{max-width:1480px;padding-top:1.2rem!important}
.gg-note{border:1px solid #e9e2d7;border-left:4px solid #f28e1c;border-radius:12px;padding:.85rem 1rem;background:#fffaf3}
.gg-card{border:1px solid #e7dfd2;border-radius:14px;background:#fffdf9;padding:1rem 1rem .85rem 1rem; height:100%}
.gg-mini{font-size:.92rem;color:#555}
</style>
''', unsafe_allow_html=True)
render_app_header(
    title='Torsión · Ejes y Perfiles',
    subtitle='Torque · constante torsional · esfuerzo cortante · ángulo de giro · rigidez torsional · alcance y límites del modelo.',
    section='RESISTENCIA Y ESTRUCTURAS',
    logo_width=188,
)

with st.sidebar:
    st.header('Carga y material')
    T = float(st.number_input('Torque T [kN·m]', value=2.0, step=0.25, help='Positivo según la convención de la flecha del modelo 3D.'))
    L = float(st.number_input('Longitud L [m]', min_value=0.05, value=2.0, step=0.1))
    st.divider()
    mat = st.selectbox('Material', ['Acero', 'Aluminio', 'Personalizado'])
    if mat == 'Acero':
        G = 79.3
        st.caption('G = 79.3 GPa')
    elif mat == 'Aluminio':
        G = 26.0
        st.caption('G = 26.0 GPa')
    else:
        G = float(st.number_input('Módulo de corte G [GPa]', min_value=0.001, value=79.3))
    st.divider()
    st.subheader('Sección')
    stype = st.selectbox('Geometría', ['Circular maciza', 'Tubular circular', 'Rectangular', 'Perfil I / H', 'Canal C', 'Propiedades ingresadas'])
    sp = profile_params_from_sidebar(st, stype, 'tor_')

sec = section_data(stype, sp)
res = solve_torsion(T, L, G, stype, sp, sec)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric('Jt', f'{res.jt_mm4:.3e} mm⁴')
m2.metric('Giro total φ', f'{res.twist_deg:.3f}°')
m3.metric('Tasa de giro dφ/dx', f'{np.degrees(res.theta_rate_rad_per_m):.3f} °/m')
m4.metric('Rigidez torsional GJ/L', f'{res.stiffness_knm_per_rad:.2f} kN·m/rad')
m5.metric('τ máx', '—' if res.tau_max_mpa is None else f'{res.tau_max_mpa:.2f} MPa')

st.markdown(
    r'''
<div class="gg-note"><b>Ruta física del problema:</b> 
<span style="white-space:nowrap">Torque <b>T</b></span> 
→ 
<span style="white-space:nowrap">esfuerzo interno torsor <b>T(x)</b></span> 
→ 
<span style="white-space:nowrap">giro por unidad de longitud <b>dφ/dx=T/(GJ_t)</b></span> 
→ 
<span style="white-space:nowrap">deformación cortante <b>γ</b></span> 
→ 
<span style="white-space:nowrap">esfuerzo cortante <b>τ</b></span>.</div>
''', unsafe_allow_html=True
)

tabs = st.tabs(['📘 Concepto', '🌀 Torsión 3D', '📊 Respuesta y diagramas', '📐 Sección y propiedades', '⚖️ Comparador', '∑ Ecuaciones', '🧠 Interpretación'])

with tabs[0]:
    st.subheader('Qué representa la torsión')
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="gg-card"><b>Acción mecánica</b><br><div class="gg-mini">Un par torsor intenta rotar una sección respecto de la siguiente. El sólido desarrolla esfuerzos cortantes internos para equilibrar ese torque.</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="gg-card"><b>Respuesta geométrica</b><br><div class="gg-mini">La barra gira a lo largo de su eje. El parámetro global es el ángulo de giro φ y el parámetro local es la tasa de giro dφ/dx.</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="gg-card"><b>Papel de G y Jt</b><br><div class="gg-mini">A mayor módulo de corte G o mayor constante torsional Jt, menor giro. Jt no es lo mismo que Iz o Iy: una sección muy buena a flexión puede ser muy débil a torsión.</div></div>', unsafe_allow_html=True)

    st.markdown('### Lectura según la geometría')
    if res.exact_circular:
        st.success('En secciones circulares la teoría de Saint-Venant entrega una relación directa y exacta: τ crece linealmente con el radio y alcanza su máximo en la superficie exterior.', icon='⭕')
    elif stype == 'Rectangular':
        st.info('En una sección rectangular la distribución de τ no es radial. El módulo usa Jt aproximado para calcular el giro y presenta la torsión de forma global, sin fingir una ley radial que no corresponde.', icon='▭')
    elif stype in ('Perfil I / H', 'Canal C'):
        st.warning('En perfiles abiertos la torsión de Saint-Venant suele ser pequeña frente al alabeo. Este módulo muestra la respuesta torsional global y remarca que el alabeo restringido no está siendo resuelto.', icon='🌀')
    else:
        st.info('Con propiedades equivalentes puedes estudiar el giro global usando Jt, aunque no se pueda reconstruir con fidelidad una distribución espacial de tensiones.', icon='ℹ️')

with tabs[1]:
    st.subheader('Modelo 3D del eje en torsión')
    c1, c2 = st.columns([1, 2])
    with c1:
        amp = st.slider('Amplificación visual del giro', 1.0, 40.0, 10.0, 1.0)
        show_original = st.toggle('Mostrar geometría inicial de referencia', value=True)
        show_generators = st.toggle('Mostrar generatrices', value=True)
        show_slices = st.toggle('Mostrar secciones intermedias', value=True)
        phi_display = max(-2.8, min(2.8, res.twist_rad * amp))
        st.markdown('<div class="gg-card">La forma deformada está <b>amplificada solo para visualización</b>. Los valores físicos que reporta el módulo siguen siendo los calculados con φ real, G y Jt.</div>', unsafe_allow_html=True)
    with c2:
        render_torsion_3d({
            'phi_display': phi_display,
            'phi_real': res.twist_rad,
            'twist_deg': res.twist_deg,
            'type': stype,
            'section': visual_section_payload(stype, sp),
            'show_original': show_original,
            'show_generators': show_generators,
            'show_slices': show_slices,
            'torque_sign': 1 if T >= 0 else -1,
            'tau_exact': res.exact_circular,
        }, height=690)
    st.caption(f'φ real = {res.twist_deg:.4f}° · amplificación mostrada = {amp:.0f}×.')

with tabs[2]:
    st.subheader('Cómo responde a lo largo del eje')
    c1, c2 = st.columns(2)
    x = np.linspace(0.0, L, 160)
    torq = np.full_like(x, T)
    phi_x_deg = np.degrees(res.twist_rad * x / max(L, 1e-12))

    figT = go.Figure()
    figT.add_trace(go.Scatter(x=x, y=torq, fill='tozeroy', line=dict(color='#4b4c50', width=3), name='T(x)'))
    figT.update_layout(height=320, margin=dict(l=20, r=20, t=15, b=20), xaxis_title='x [m]', yaxis_title='Torque interno [kN·m]', showlegend=False)
    c1.plotly_chart(figT, use_container_width=True)

    figP = go.Figure()
    figP.add_trace(go.Scatter(x=x, y=phi_x_deg, line=dict(color='#c8752d', width=3), name='φ(x)'))
    figP.update_layout(height=320, margin=dict(l=20, r=20, t=15, b=20), xaxis_title='x [m]', yaxis_title='Giro acumulado [°]', showlegend=False)
    c2.plotly_chart(figP, use_container_width=True)

    c3, c4 = st.columns(2)
    if res.exact_circular and res.r_outer_mm:
        if stype == 'Circular maciza':
            r_in, r_out = 0.0, sp['d_mm'] / 2.0
        else:
            r_out = sp['do_mm'] / 2.0
            r_in = r_out - sp['t_mm']
        rr = np.linspace(r_in, r_out, 120)
        tau = abs(T * 1e6 * rr / res.jt_mm4)
        gamma = rr / 1000.0 * res.theta_rate_rad_per_m

        figTau = go.Figure()
        figTau.add_trace(go.Scatter(x=rr, y=tau, line=dict(color='#f28e1c', width=3)))
        figTau.update_layout(height=320, margin=dict(l=20, r=20, t=15, b=20), xaxis_title='r [mm]', yaxis_title='τ(r) [MPa]')
        c3.plotly_chart(figTau, use_container_width=True)

        figGam = go.Figure()
        figGam.add_trace(go.Scatter(x=rr, y=1e3 * gamma, line=dict(color='#4b4c50', width=3)))
        figGam.update_layout(height=320, margin=dict(l=20, r=20, t=15, b=20), xaxis_title='r [mm]', yaxis_title='γ(r) [mrad]')
        c4.plotly_chart(figGam, use_container_width=True)
    else:
        c3.info('Para esta geometría no se muestra τ(r) porque la distribución no es radial. Sí se presenta el giro global, la constante torsional Jt y la interpretación del alcance del modelo.', icon='ℹ️')
        c4.markdown('<div class="gg-card"><b>Lectura útil</b><br><div class="gg-mini">El diagrama T(x) permite identificar dónde existe torsión interna, mientras que φ(x) muestra cómo se acumula el giro. En materiales lineales y T constante, φ(x) crece linealmente a lo largo del eje.</div></div>', unsafe_allow_html=True)

with tabs[3]:
    st.subheader('Propiedades geométricas y torsionales')
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Área A', f'{sec.area_mm2:.0f} mm²')
    c2.metric('Iz', f'{sec.iz_mm4:.3e} mm⁴')
    c3.metric('Iy', f'{sec.iy_mm4:.3e} mm⁴')
    c4.metric('Jt', f'{sec.jt_mm4:.3e} mm⁴' if sec.jt_mm4 else '—')

    if sec.note:
        st.markdown(f'<div class="gg-note"><b>Nota sobre la sección:</b> {sec.note}</div>', unsafe_allow_html=True)

    if stype in ('Perfil I / H', 'Canal C'):
        st.warning('En perfiles abiertos, Jt suele ser mucho menor que Iz. Esta es una de las razones por las que una pieza puede ser rígida a flexión y, al mismo tiempo, muy flexible a torsión.', icon='📌')

with tabs[4]:
    st.subheader('Comparador torsional de dos secciones')
    st.write('Mantén **el mismo torque, longitud y material** y cambia solamente la geometría. Así puedes observar directamente qué hace la sección sobre la rigidez torsional, el giro y, cuando corresponde, el esfuerzo cortante.')

    types_cmp = ['Circular maciza', 'Tubular circular', 'Rectangular', 'Perfil I / H', 'Canal C', 'Propiedades ingresadas']
    ca, cb = st.columns(2)
    with ca:
        st.markdown('### Sección A')
        stype_a = st.selectbox('Geometría A', types_cmp, index=0, key='tor_cmp_type_a')
        sp_a = profile_params_from_sidebar(st, stype_a, 'tor_cmp_a_')
    with cb:
        st.markdown('### Sección B')
        stype_b = st.selectbox('Geometría B', types_cmp, index=3, key='tor_cmp_type_b')
        sp_b = profile_params_from_sidebar(st, stype_b, 'tor_cmp_b_')

    sec_a = section_data(stype_a, sp_a)
    sec_b = section_data(stype_b, sp_b)
    res_a = solve_torsion(T, L, G, stype_a, sp_a, sec_a)
    res_b = solve_torsion(T, L, G, stype_b, sp_b, sec_b)

    eta_a = res_a.jt_mm4 / (sec_a.area_mm2 ** 2)
    eta_b = res_b.jt_mm4 / (sec_b.area_mm2 ** 2)
    ratio_j = res_b.jt_mm4 / res_a.jt_mm4 if res_a.jt_mm4 else float('nan')
    ratio_k = res_b.stiffness_knm_per_rad / res_a.stiffness_knm_per_rad if res_a.stiffness_knm_per_rad else float('nan')
    if abs(res_a.twist_deg) > 1e-15:
        ratio_phi = abs(res_b.twist_deg / res_a.twist_deg)
    else:
        ratio_phi = None

    st.markdown('#### Resultado comparativo')
    r1, r2, r3, r4 = st.columns(4)
    r1.metric('Jt B / Jt A', f'{ratio_j:.3f}')
    r2.metric('(GJ/L) B / A', f'{ratio_k:.3f}')
    r3.metric('|φB| / |φA|', '—' if ratio_phi is None else f'{ratio_phi:.3f}')
    r4.metric('Área B / Área A', f'{sec_b.area_mm2/sec_a.area_mm2:.3f}')

    aa, bb = st.columns(2)
    with aa:
        st.markdown(f'<div class="gg-card"><b>Sección A · {stype_a}</b><br><div class="gg-mini">A = <b>{sec_a.area_mm2:.0f} mm²</b><br>Jt = <b>{res_a.jt_mm4:.3e} mm⁴</b><br>φ = <b>{res_a.twist_deg:.4f}°</b><br>GJ/L = <b>{res_a.stiffness_knm_per_rad:.2f} kN·m/rad</b><br>η<sub>J</sub>=Jt/A² = <b>{eta_a:.5f}</b><br>τmáx = <b>{"—" if res_a.tau_max_mpa is None else f"{res_a.tau_max_mpa:.2f} MPa"}</b></div></div>', unsafe_allow_html=True)
    with bb:
        st.markdown(f'<div class="gg-card"><b>Sección B · {stype_b}</b><br><div class="gg-mini">A = <b>{sec_b.area_mm2:.0f} mm²</b><br>Jt = <b>{res_b.jt_mm4:.3e} mm⁴</b><br>φ = <b>{res_b.twist_deg:.4f}°</b><br>GJ/L = <b>{res_b.stiffness_knm_per_rad:.2f} kN·m/rad</b><br>η<sub>J</sub>=Jt/A² = <b>{eta_b:.5f}</b><br>τmáx = <b>{"—" if res_b.tau_max_mpa is None else f"{res_b.tau_max_mpa:.2f} MPa"}</b></div></div>', unsafe_allow_html=True)

    st.caption('ηJ = Jt/A² es un índice geométrico adimensional para comparar eficiencia torsional por cantidad de área. No es un criterio normativo de diseño.')

    st.markdown('#### Comparación 3D bajo las mismas condiciones')
    cmp_amp = st.slider('Amplificación visual compartida', 1.0, 40.0, 10.0, 1.0, key='tor_cmp_amp')
    va, vb = st.columns(2)
    with va:
        st.markdown(f'**A · {stype_a}**')
        render_torsion_3d({
            'phi_display': max(-2.8, min(2.8, res_a.twist_rad * cmp_amp)),
            'phi_real': res_a.twist_rad,
            'twist_deg': res_a.twist_deg,
            'type': stype_a,
            'section': visual_section_payload(stype_a, sp_a),
            'show_original': True,
            'show_generators': True,
            'show_slices': True,
            'torque_sign': 1 if T >= 0 else -1,
            'tau_exact': res_a.exact_circular,
        }, height=520)
    with vb:
        st.markdown(f'**B · {stype_b}**')
        render_torsion_3d({
            'phi_display': max(-2.8, min(2.8, res_b.twist_rad * cmp_amp)),
            'phi_real': res_b.twist_rad,
            'twist_deg': res_b.twist_deg,
            'type': stype_b,
            'section': visual_section_payload(stype_b, sp_b),
            'show_original': True,
            'show_generators': True,
            'show_slices': True,
            'torque_sign': 1 if T >= 0 else -1,
            'tau_exact': res_b.exact_circular,
        }, height=520)
    st.caption('Ambos visores usan la misma amplificación angular. Cada sección se autoescala transversalmente para poder leerse; el tamaño aparente del perfil en el visor no debe usarse para comparar área.')

    st.markdown('#### Curvas de giro acumulado')
    xcmp = np.linspace(0.0, L, 160)
    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Scatter(x=xcmp, y=np.degrees(res_a.twist_rad*xcmp/max(L,1e-12)), line=dict(color='#c8752d', width=3), name=f'A · {stype_a}'))
    fig_cmp.add_trace(go.Scatter(x=xcmp, y=np.degrees(res_b.twist_rad*xcmp/max(L,1e-12)), line=dict(color='#4b4c50', width=3, dash='dash'), name=f'B · {stype_b}'))
    fig_cmp.update_layout(height=360, margin=dict(l=20,r=20,t=15,b=20), xaxis_title='x [m]', yaxis_title='Giro acumulado φ(x) [°]', legend=dict(orientation='h', y=1.1))
    st.plotly_chart(fig_cmp, use_container_width=True)

    st.markdown('#### Qué debes mirar')
    q1, q2, q3 = st.columns(3)
    with q1:
        st.markdown('<div class="gg-card"><b>1 · Jt</b><br><div class="gg-mini">Con el mismo material y longitud, una sección con mayor Jt presenta mayor rigidez torsional.</div></div>', unsafe_allow_html=True)
    with q2:
        st.markdown('<div class="gg-card"><b>2 · Giro</b><br><div class="gg-mini">Para el mismo T, G y L, el giro es inversamente proporcional a Jt. Aumentar Jt reduce φ.</div></div>', unsafe_allow_html=True)
    with q3:
        st.markdown('<div class="gg-card"><b>3 · Eficiencia geométrica</b><br><div class="gg-mini">Jt/A² ayuda a comparar cuánto rendimiento torsional entrega la forma por cantidad de sección, sin confundirlo con una verificación resistente.</div></div>', unsafe_allow_html=True)

    if stype_a in ('Perfil I / H','Canal C') or stype_b in ('Perfil I / H','Canal C'):
        st.warning('Los perfiles abiertos se comparan aquí mediante la torsión de Saint-Venant y Jt de pared delgada. El alabeo restringido puede cambiar significativamente la respuesta real y no está incluido en esta comparación.', icon='🧭')
    if res_a.exact_circular != res_b.exact_circular:
        st.info('Solo se muestra τmáx cuando la sección es circular, porque allí τ=Tr/J es válida. La ausencia de τmáx en la otra sección no significa que no existan esfuerzos cortantes; significa que no se está usando una ley radial incorrecta.', icon='ℹ️')

with tabs[5]:
    st.subheader('Ecuaciones organizadas por nivel')
    st.markdown('**Equilibrio interno**')
    st.latex(r'T(x)=\text{cte}\quad\text{(si no hay torques distribuidos ni cambios de carga a lo largo del eje)}')
    st.markdown('**Compatibilidad / deformación**')
    st.latex(r'\frac{d\phi}{dx}=\frac{T(x)}{GJ_t}')
    st.latex(r'\phi=\int_0^L \frac{T(x)}{GJ_t}\,dx')
    st.markdown('**Rigidez torsional global**')
    st.latex(r'k_t=\frac{GJ_t}{L}')
    st.markdown('**Secciones circulares (Saint-Venant exacto)**')
    st.latex(r'J_{\text{circ}}=\frac{\pi d^4}{32},\qquad J_{\text{tubo}}=\frac{\pi(D_o^4-D_i^4)}{32}')
    st.latex(r'\tau(r)=\frac{Tr}{J},\qquad \gamma(r)=r\,\frac{d\phi}{dx},\qquad \tau=G\gamma')
    st.markdown('**Rectángulos y perfiles abiertos**')
    st.latex(r'\phi\approx\frac{TL}{GJ_t}\quad\text{con}\quad J_t\ \text{de Saint-Venant}')
    st.write('La forma de τ en estas geometrías no es radial. Para perfiles abiertos, el módulo no incluye alabeo restringido ni bimomento.')

with tabs[6]:
    st.subheader('Interpretación de los resultados')
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="gg-card"><b>Resultado principal</b><br><div class="gg-mini">Con T = {T:.3f} kN·m, L = {L:.3f} m y G = {G:.3f} GPa, la sección seleccionada produce un giro total de <b>{res.twist_deg:.4f}°</b>. La rigidez torsional equivalente del elemento es <b>{res.stiffness_knm_per_rad:.2f} kN·m/rad</b>.</div></div>', unsafe_allow_html=True)
        if res.exact_circular and res.gamma_max is not None:
            st.markdown(f'<div class="gg-card"><b>Deformación y esfuerzo máximos</b><br><div class="gg-mini">En esta sección circular, la deformación cortante máxima es γ<sub>máx</sub> = <b>{1e3*res.gamma_max:.3f} mrad</b> y el esfuerzo cortante máximo es τ<sub>máx</sub> = <b>{res.tau_max_mpa:.2f} MPa</b>, ambos en la superficie exterior.</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="gg-card"><b>Lectura para sección no circular</b><br><div class="gg-mini">El dato clave aquí es la combinación entre giro total φ, rigidez torsional GJ/L y la nota de validez del modelo. <b>No conviene interpretar τ como si siguiera una ley radial</b>.</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="gg-card"><b>Alcance del modelo</b><br><div class="gg-mini">{res.tau_mode}</div></div>', unsafe_allow_html=True)
        if abs(res.twist_deg) > 5:
            st.warning('El giro calculado es grande. Conviene revisar si la hipótesis de pequeñas deformaciones sigue siendo apropiada para la interpretación del caso.', icon='⚠️')
        else:
            st.success('El giro calculado permanece moderado dentro de este modelo elástico lineal. El módulo es útil para comprender tendencias y comparar geometrías.', icon='✅')
        if stype in ('Perfil I / H', 'Canal C'):
            st.warning('Si quieres estudiar con más fidelidad perfiles abiertos en torsión, el siguiente nivel teórico debe incorporar alabeo y torsión no uniforme.', icon='🧭')
