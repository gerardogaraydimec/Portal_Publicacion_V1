from pathlib import Path
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from modules.vibracion_forzada1gdl import calcular_respuesta, curva_magnificacion, puntos_adaptativos, formato

ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / "assets" / "logo_card.png"

ORANGE = "#f28e1c"
DARK = "#262730"
GRID = "rgba(0,0,0,0.08)"

st.markdown("""
<style>
.block-container{padding-top:1.1rem;padding-bottom:1.5rem;max-width:1650px}
h1,h2,h3{margin-bottom:.25rem}
div[data-testid="stMetric"]{background:#fafafa;border:1px solid #eee;border-radius:10px;padding:8px 12px}
.stButton>button{background:#f28e1c;color:white;border:0;font-weight:700}
.small-note{font-size:.86rem;color:#666}
</style>
""", unsafe_allow_html=True)

h1, h2 = st.columns([5.5, 1.15], vertical_alignment="center")
with h1:
    st.title("Vibración forzada armónica · Sistema 1-GDL")
    st.caption("GG DIMEC MechLab · Respuesta de $m\\ddot{x}+c\\dot{x}+kx=F_0\\cos(\\omega t)$ con enfoque pedagógico y de ingeniería.")
with h2:
    if LOGO.exists():
        st.image(str(LOGO), use_container_width=True)

with st.form("vibf_forced_inputs"):
    r1 = st.columns(4)
    m = r1[0].number_input("Masa m [kg]", value=1.0, format="%.8g", key="vibf_m")
    k = r1[1].number_input("Rigidez k [N/m]", value=100.0, format="%.8g", key="vibf_k")
    c = r1[2].number_input("Amortiguamiento c [N·s/m]", value=6.0, format="%.8g", key="vibf_c")
    F0 = r1[3].number_input("Fuerza armónica F₀ [N]", value=50.0, format="%.8g", key="vibf_F0")
    r2 = st.columns(4)
    omega = r2[0].number_input("Frecuencia angular ω [rad/s]", value=8.0, format="%.8g", key="vibf_omega")
    x0 = r2[1].number_input("Desplazamiento inicial x₀ [m]", value=0.1, format="%.8g", key="vibf_x0")
    v0 = r2[2].number_input("Velocidad inicial v₀ [m/s]", value=0.0, format="%.8g", key="vibf_v0")
    tmax = r2[3].number_input("Tiempo de análisis [s]", value=15.0, format="%.8g", key="vibf_tmax")
    apply = st.form_submit_button("Aplicar parámetros", use_container_width=True)

errs = []
if m <= 0: errs.append("m debe ser mayor que 0")
if k <= 0: errs.append("k debe ser mayor que 0")
if c < 0: errs.append("c no puede ser negativo")
if F0 < 0: errs.append("F₀ no puede ser negativo")
if omega < 0: errs.append("ω no puede ser negativa")
if tmax <= 0: errs.append("t max debe ser mayor que 0")
if errs:
    st.error(" · ".join(errs)); st.stop()

wn = np.sqrt(k/m)
n, limitado, n_req = puntos_adaptativos(wn, omega, tmax)
t = np.linspace(0, tmax, n)
res = calcular_respuesta(m,k,c,x0,v0,F0,omega,t)

if limitado:
    st.warning(f"La combinación de frecuencia y tiempo requeriría ~{n_req:,} puntos para alta resolución. La gráfica se limita a {n:,} puntos. Para inspección fina, reduzca el tiempo de análisis.")
if res["exact_undamped_resonance"]:
    st.error("Resonancia exacta sin amortiguamiento (ω = ωₙ y c = 0): la amplitud estacionaria no es finita. Se grafica la solución resonante creciente correcta en el tiempo.")

m1,m2,m3,m4,m5,m6 = st.columns(6)
m1.metric("fₙ", f"{res['fn']:.4g} Hz")
m2.metric("nₙ", f"{res['rpm_n']:.5g} rpm")
m3.metric("ζ", f"{res['zeta']:.4g}")
m4.metric("r = ω/ωₙ", f"{res['r']:.4g}")
m5.metric("X estacionaria", "∞" if not np.isfinite(res['X']) else f"{res['X']:.5g} m")
m6.metric("Fase φ", f"{np.degrees(res['phi']):.3g}°")

st.markdown(f"**Régimen transitorio:** {res['regime']} &nbsp;&nbsp; | &nbsp;&nbsp; **Excitación:** {res['f_exc']:.5g} Hz = {res['rpm_exc']:.6g} rpm")

# Respuesta temporal
fig_t = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.075,
                      subplot_titles=("Desplazamiento x(t)", "Velocidad v(t)", "Aceleración a(t)"))
fig_t.add_trace(go.Scatter(x=t,y=res['x'],name="x(t)",line=dict(color="#1E88E5")),1,1)
fig_t.add_trace(go.Scatter(x=t,y=res['v'],name="v(t)",line=dict(color="#E53935")),2,1)
fig_t.add_trace(go.Scatter(x=t,y=res['a'],name="a(t)",line=dict(color="#43A047")),3,1)
fig_t.update_xaxes(title_text="t [s]", row=3,col=1, gridcolor=GRID)
fig_t.update_yaxes(title_text="x [m]", row=1,col=1, gridcolor=GRID)
fig_t.update_yaxes(title_text="v [m/s]", row=2,col=1, gridcolor=GRID)
fig_t.update_yaxes(title_text="a [m/s²]", row=3,col=1, gridcolor=GRID)
fig_t.update_layout(height=620, margin=dict(l=20,r=10,t=45,b=30), showlegend=False, hovermode="x unified")

fig_phase = go.Figure()
fig_phase.add_trace(go.Scatter(x=res['x'],y=res['v'],mode="lines",line=dict(color="#7D3C98",width=2.5),name="Trayectoria"))
fig_phase.update_layout(title="Plano de fase",height=620,xaxis_title="x [m]",yaxis_title="v [m/s]",margin=dict(l=20,r=10,t=45,b=30),showlegend=False)
fig_phase.update_xaxes(gridcolor=GRID); fig_phase.update_yaxes(gridcolor=GRID)

c1,c2 = st.columns([1.08,.92],gap="small")
with c1: st.plotly_chart(fig_t,use_container_width=True,config={"scrollZoom":True,"displaylogo":False})
with c2: st.plotly_chart(fig_phase,use_container_width=True,config={"scrollZoom":True,"displaylogo":False})

# Respuesta frecuencia + particular/fuerza
r_curve, M_curve = curva_magnificacion(res['zeta'])
fig_mag = go.Figure()
fig_mag.add_trace(go.Scatter(x=r_curve,y=M_curve,name="M(r)",line=dict(color="#777")))
if np.isfinite(res['M']):
    fig_mag.add_trace(go.Scatter(x=[res['r']],y=[res['M']],mode="markers",marker=dict(size=11,color="red"),name="Punto de operación"))
fig_mag.update_layout(title="Factor de magnificación",height=390,xaxis_title="r = ω/ωₙ",yaxis_title="M = X/(F₀/k)",margin=dict(l=20,r=10,t=45,b=35))
fig_mag.update_xaxes(range=[0,4],gridcolor=GRID); fig_mag.update_yaxes(gridcolor=GRID)

fig_pf = go.Figure()
fig_pf.add_trace(go.Scatter(x=t,y=res['x'],name="x(t)",line=dict(color="#8E44AD")))
if k>0:
    fig_pf.add_trace(go.Scatter(x=t,y=(F0/k)*np.cos(omega*t),name="F(t)/k",line=dict(color=ORANGE,dash="dash")))
fig_pf.update_layout(title="Respuesta vs desplazamiento estático equivalente F(t)/k",height=390,xaxis_title="t [s]",yaxis_title="Desplazamiento [m]",margin=dict(l=20,r=10,t=45,b=35),hovermode="x unified")
fig_pf.update_xaxes(gridcolor=GRID); fig_pf.update_yaxes(gridcolor=GRID)

c3,c4=st.columns(2,gap="small")
with c3: st.plotly_chart(fig_mag,use_container_width=True,config={"displaylogo":False})
with c4: st.plotly_chart(fig_pf,use_container_width=True,config={"displaylogo":False})

# Fasor interactive
st.subheader("Diagrama fasorial y fuerzas")
phase_deg = st.slider("Ángulo de visualización del fasor [°]", 0, 360, 0, 1, key="vibf_phase_deg")
th=np.deg2rad(phase_deg)
if np.isfinite(res['X']):
    X=res['X']; ph=res['phi']
    # complex vector representation: F0 reference on +x; KX in phase with x, CωX +90°, inertia +180°.
    ang_x = th-ph
    vecs = {
        "F₀": (F0*np.cos(th), F0*np.sin(th), ORANGE),
        "kX": (k*X*np.cos(ang_x), k*X*np.sin(ang_x), "#2E86C1"),
        "cωX": (c*omega*X*np.cos(ang_x+np.pi/2), c*omega*X*np.sin(ang_x+np.pi/2), "#CB4335"),
        "mω²X": (m*omega**2*X*np.cos(ang_x+np.pi), m*omega**2*X*np.sin(ang_x+np.pi), "#1D8348"),
    }
    fig_vec=go.Figure()
    for name,(vx,vy,col) in vecs.items():
        fig_vec.add_annotation(x=vx,y=vy,ax=0,ay=0,xref="x",yref="y",axref="x",ayref="y",showarrow=True,arrowhead=3,arrowwidth=2,arrowcolor=col,text=name,font=dict(color=col,size=14))
        fig_vec.add_trace(go.Scatter(x=[0,vx],y=[0,vy],mode="lines",line=dict(color=col,width=1),showlegend=False,hoverinfo="skip"))
    vmax=max([abs(a) for v in vecs.values() for a in v[:2]]+[1])*1.25
    fig_vec.update_layout(height=430,title="Fasores de fuerza (referencia rotatoria)",xaxis=dict(title="Fₓ [N]",range=[-vmax,vmax],scaleanchor="y",scaleratio=1,gridcolor=GRID),yaxis=dict(title="Fᵧ [N]",range=[-vmax,vmax],gridcolor=GRID),margin=dict(l=20,r=10,t=45,b=35))
else:
    fig_vec=go.Figure(); fig_vec.add_annotation(text="Fasor estacionario no definido en resonancia exacta sin amortiguamiento",showarrow=False,x=.5,y=.5,xref="paper",yref="paper")
    fig_vec.update_layout(height=430)

f1,f2,f3,f4,f5=st.columns(5)
f1.metric("|kX|", "∞" if not np.isfinite(res['Fk_amp']) else f"{res['Fk_amp']:.5g} N")
f2.metric("|cωX|", "∞" if not np.isfinite(res['Fc_amp']) else f"{res['Fc_amp']:.5g} N")
f3.metric("|mω²X|", "∞" if not np.isfinite(res['Fi_amp']) else f"{res['Fi_amp']:.5g} N")
f4.metric("F transmitida", "∞" if not np.isfinite(res['Ft_amp']) else f"{res['Ft_amp']:.5g} N")
f5.metric("Transmisibilidad", "∞" if not np.isfinite(res['TR']) else f"{res['TR']:.5g}")
st.plotly_chart(fig_vec,use_container_width=True,config={"scrollZoom":True,"displaylogo":False})

with st.expander("Energía, raíces y constantes", expanded=False):
    e1,e2=st.columns([1.2,.8])
    fig_e=go.Figure()
    fig_e.add_trace(go.Scatter(x=t,y=res['Ec'],name="E cinética",line=dict(color="#E74C3C")))
    fig_e.add_trace(go.Scatter(x=t,y=res['Ep'],name="E potencial",line=dict(color="#3498DB")))
    fig_e.add_trace(go.Scatter(x=t,y=res['Em'],name="E mecánica",line=dict(color="#555",width=2)))
    fig_e.update_layout(height=380,title="Energía mecánica instantánea",xaxis_title="t [s]",yaxis_title="E [J]",margin=dict(l=20,r=10,t=45,b=35),hovermode="x unified")
    with e1: st.plotly_chart(fig_e,use_container_width=True,config={"displaylogo":False})
    with e2:
        st.markdown(f"""
**Parámetros dinámicos**  
$\\omega_n$ = {res['wn']:.8g} rad/s  
$c_{{cr}}$ = {res['ccr']:.8g} N·s/m  
$\\zeta$ = {res['zeta']:.8g}  
$r$ = {res['r']:.8g}  
$\\delta_{{st}}=F_0/k$ = {res['delta_st']:.8g} m  

**Raíces / constantes del transitorio**  
$s_1$ = `{formato(res['s1'])}`  
$s_2$ = `{formato(res['s2'])}`  
$C_1$ = `{formato(res['C1'])}`  
$C_2$ = `{formato(res['C2'])}`
""")

with st.expander("Ecuaciones y alcance del modelo", expanded=False):
    st.latex(r"m\ddot{x}+c\dot{x}+kx=F_0\cos(\omega t)")
    st.latex(r"\omega_n=\sqrt{\frac{k}{m}},\qquad \zeta=\frac{c}{2\sqrt{km}},\qquad r=\frac{\omega}{\omega_n}")
    st.latex(r"X=\frac{F_0}{\sqrt{(k-m\omega^2)^2+(c\omega)^2}}"); st.latex(r"\phi=\operatorname{atan2}(c\omega,k-m\omega^2)")
    st.latex(r"M=\frac{X}{F_0/k}=\frac{1}{\sqrt{(1-r^2)^2+(2\zeta r)^2}}")
    st.markdown("El modelo representa un sistema lineal de 1 GDL sometido a una **fuerza armónica externa**. Es apropiado para análisis preliminar de respuesta, resonancia y aislamiento, pero no sustituye un modelo multigrado, no lineal o estructural cuando la máquina lo requiera.")

st.caption("Los campos de entrada no tienen un máximo industrial prefijado. La validez física depende de que el sistema pueda representarse razonablemente como lineal y de 1 GDL.")
