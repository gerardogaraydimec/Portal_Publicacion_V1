from __future__ import annotations
import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from modules.ui_brand import render_app_header
from modules.vibration_2dof_engine import solve_modal,harmonic_response,frequency_response,forced_time_response,tmd_reference,sdof_primary_frf
from modules.vibration_2dof_visual3d import render_vibration_2dof_3d

st.markdown('''<style>.block-container{max-width:1480px;padding-top:1rem!important}.gg-note{border:1px solid #e9e2d7;border-left:4px solid #f28e1c;border-radius:12px;padding:.72rem .9rem;background:#fffaf3}.gg-card{border:1px solid #e7dfd2;border-radius:13px;background:#fffdf9;padding:.78rem .88rem;height:100%}.gg-mini{font-size:.88rem;color:#555;line-height:1.38}</style>''',unsafe_allow_html=True)
render_app_header(title='Vibraciones · 2GDL y Absorbedor Dinámico',subtitle='Modos normales · respuesta armónica · antirresonancia · TMD · visualización 3D.',section='MÁQUINAS Y COMPONENTES',logo_width=188)

with st.sidebar:
    st.header('Sistema 2GDL')
    m1=float(st.number_input('Masa primaria m₁ [kg]',min_value=.001,value=100.0,step=5.0))
    k1=float(st.number_input('Rigidez a base k₁ [N/m]',min_value=.001,value=40000.0,step=1000.0))
    c1=float(st.number_input('Amortiguamiento c₁ [N·s/m]',min_value=0.0,value=500.0,step=50.0))
    st.divider(); st.subheader('Segundo grado de libertad / TMD')
    m2=float(st.number_input('Masa m₂ [kg]',min_value=.001,value=10.0,step=1.0))
    k2=float(st.number_input('Rigidez acoplada k₂ [N/m]',min_value=.001,value=3305.8,step=100.0))
    c2=float(st.number_input('Amortiguamiento c₂ [N·s/m]',min_value=0.0,value=73.4,step=10.0))
    st.divider(); st.subheader('Excitación')
    F0=float(st.number_input('Fuerza sobre m₁ F₀ [N]',min_value=0.0,value=1000.0,step=100.0))
    modal0=solve_modal(m1,m2,k1,k2,c1,c2)
    fexc=float(st.number_input('Frecuencia f [Hz]',min_value=0.0,value=float(round(modal0.primary_fn,3)),step=.05,format='%.3f'))

modal=solve_modal(m1,m2,k1,k2,c1,c2); h=harmonic_response(modal,fexc,F0); finite_h=bool(np.all(np.isfinite(h.X))); fgrid,X1g,X2g=frequency_response(modal,F0=max(F0,1.0))

m1c,m2c,m3c,m4c,m5c,m6c=st.columns(6)
m1c.metric('f₁',f'{modal.fn[0]:.3f} Hz');m2c.metric('f₂',f'{modal.fn[1]:.3f} Hz');m3c.metric('f abs.',f'{modal.absorber_fn:.3f} Hz');m4c.metric('X₁','∞' if not finite_h else f'{1000*h.amp[0]:.2f} mm');m5c.metric('X₂','∞' if not finite_h else f'{1000*h.amp[1]:.2f} mm');m6c.metric('μ=m₂/m₁',f'{modal.mass_ratio:.3f}')
if not finite_h:
    st.error('La frecuencia seleccionada coincide con una singularidad del modelo ideal sin amortiguamiento suficiente. Cambia f o agrega amortiguamiento para obtener una respuesta estacionaria finita.',icon='⚠️')
st.markdown('<div class="gg-note"><b>Ruta física:</b> matrices M y K → frecuencias naturales y modos → excitación armónica → dos resonancias + zona de antirresonancia → diseño de absorbedor/TMD.</div>',unsafe_allow_html=True)

tabs=st.tabs(['📊 Vista compacta','🧩 Sistema 3D','🎼 Modos normales','🎯 Antirresonancia y TMD','⚖️ Comparador','📘 Teoría y ecuaciones','🧠 Interpretación'])

with tabs[0]:
    left,right=st.columns([3.25,1.1],gap='medium')
    with left:
        a,b=st.columns(2)
        frf1=1000*np.abs(X1g); frf2=1000*np.abs(X2g)
        fig=go.Figure();fig.add_trace(go.Scatter(x=fgrid,y=frf1,name='|X₁|',line=dict(color='#c8752d',width=2.4)));fig.add_trace(go.Scatter(x=fgrid,y=frf2,name='|X₂|',line=dict(color='#4b4c50',width=2.0)));fig.add_vline(x=modal.fn[0],line_dash='dash',line_color='#999');fig.add_vline(x=modal.fn[1],line_dash='dash',line_color='#999');fig.add_vline(x=modal.antiresonance_hz,line_dash='dot',line_color='#f28e1c');fig.update_layout(height=280,title='Respuesta en frecuencia',xaxis_title='f [Hz]',yaxis_title='Amplitud [mm]',margin=dict(l=15,r=10,t=35,b=15));a.plotly_chart(fig,use_container_width=True)
        modes=modal.modes
        fm=go.Figure();fm.add_trace(go.Scatter(x=['m₁','m₂'],y=modes[:,0],mode='lines+markers',name='Modo 1'));fm.add_trace(go.Scatter(x=['m₁','m₂'],y=modes[:,1],mode='lines+markers',name='Modo 2'));fm.add_hline(y=0,line_color='#aaa');fm.update_layout(height=280,title='Formas modales normalizadas',yaxis_title='Amplitud relativa',margin=dict(l=15,r=10,t=35,b=15));b.plotly_chart(fm,use_container_width=True)
        c,d=st.columns(2)
        duration=6/max(fexc,modal.fn[0],1e-6);tt=np.linspace(0,duration,800);xt=forced_time_response(h,tt)
        if not finite_h:
            c.warning('La respuesta temporal estacionaria no es finita en esta condición ideal.')
            d.warning('La trayectoria x₁–x₂ no está definida en esta condición ideal.')
        else:
            ft=go.Figure();ft.add_trace(go.Scatter(x=tt,y=1000*xt[:,0],name='x₁(t)',line=dict(color='#c8752d',width=2.2)));            ft.add_trace(go.Scatter(x=tt,y=1000*xt[:,1],name='x₂(t)',line=dict(color='#4b4c50',width=2.0)));ft.update_layout(height=255,title='Respuesta estacionaria',xaxis_title='t [s]',yaxis_title='x [mm]',margin=dict(l=15,r=10,t=35,b=15));c.plotly_chart(ft,use_container_width=True)
            fp=go.Figure();fp.add_trace(go.Scatter(x=1000*xt[:,0],y=1000*xt[:,1],mode='lines',line=dict(color='#f28e1c',width=2.2)));fp.update_layout(height=255,title='Trayectoria x₁–x₂',xaxis_title='x₁ [mm]',yaxis_title='x₂ [mm]',margin=dict(l=15,r=10,t=35,b=15));d.plotly_chart(fp,use_container_width=True)
    with right:
        st.markdown('### Lectura del caso');st.markdown(f'''<div class="gg-card"><div class="gg-mini"><b>Frecuencia primaria sola:</b> {modal.primary_fn:.3f} Hz<br><b>Frecuencia del absorbedor:</b> {modal.absorber_fn:.3f} Hz<br><b>Antirresonancia ideal:</b> {modal.antiresonance_hz:.3f} Hz<br><b>Modo 1:</b> [{modal.modes[0,0]:.2f}, {modal.modes[1,0]:.2f}]<br><b>Modo 2:</b> [{modal.modes[0,1]:.2f}, {modal.modes[1,1]:.2f}]<br><b>Residual armónico:</b> {h.residual:.2e}</div></div>''',unsafe_allow_html=True)
        st.info('En un sistema 2GDL aparecen dos resonancias. Entre ellas puede aparecer una frecuencia donde el movimiento de la masa primaria cae fuertemente: la antirresonancia.',icon='🎯')

with tabs[1]:
    st.subheader('Animación 3D del sistema acoplado')
    l,r=st.columns([1,2.4])
    with l:
        view=st.selectbox('Movimiento a visualizar',['Respuesta forzada','Modo 1','Modo 2'])
        ampv=st.slider('Amplificación visual',.5,3.0,1.0,.1);speed=st.slider('Velocidad',.25,2.0,1.0,.25);show_force=st.toggle('Mostrar fuerza aplicada',True)
    with r:
        if view=='Respuesta forzada':
            if not finite_h:
                st.warning('La condición actual no tiene respuesta estacionaria finita para animar. Selecciona un modo o cambia la frecuencia/amortiguamiento.')
                xx=None
            else:
                tt=np.linspace(0,6/max(fexc,1e-6),600);xx=forced_time_response(h,tt);force=F0*np.cos(2*np.pi*fexc*tt);label=f'Respuesta forzada · f={fexc:.3f} Hz'
        else:
            j=0 if view=='Modo 1' else 1; ff=modal.fn[j]; tt=np.linspace(0,4/max(ff,1e-6),600);q=np.sin(2*np.pi*ff*tt);xx=q[:,None]*modal.modes[:,j][None,:]*.01;force=np.zeros_like(tt);label=f'{view} · f={ff:.3f} Hz'
        if xx is not None:
            render_vibration_2dof_3d({'t':tt.tolist(),'x1':xx[:,0].tolist(),'x2':xx[:,1].tolist(),'force':force.tolist(),'duration':float(tt[-1]),'visual_amp':ampv,'speed':speed,'show_force':show_force,'label':label},height=610)

with tabs[2]:
    st.subheader('Modos normales')
    c1,c2=st.columns(2)
    for j,col in [(0,c1),(1,c2)]:
        with col:
            st.markdown(f'### Modo {j+1} · {modal.fn[j]:.3f} Hz')
            st.write(f'Amplitud relativa: m₁ = {modal.modes[0,j]:.3f}, m₂ = {modal.modes[1,j]:.3f}')
            if modal.modes[0,j]*modal.modes[1,j] > 0: st.success('Las masas se mueven en fase.')
            else: st.warning('Las masas se mueven en oposición de fase.')
    st.latex(r'\det(\mathbf K-\omega^2\mathbf M)=0')
    st.latex(r'(\mathbf K-\omega_i^2\mathbf M)\boldsymbol\phi_i=0')

with tabs[3]:
    st.subheader('Antirresonancia y absorbedor dinámico')
    mu=st.slider('Relación de masa sugerida μ=m₂/m₁',0.02,0.30,0.10,0.01)
    ref=tmd_reference(m1,k1,mu)
    q1,q2,q3,q4=st.columns(4);q1.metric('m₂ sugerida',f"{ref['m2']:.2f} kg");q2.metric('k₂ sugerida',f"{ref['k2']:.0f} N/m");q3.metric('c₂ sugerido',f"{ref['c2']:.1f} N·s/m");q4.metric('ζ₂ ref.',f"{ref['zeta2']:.3f}")
    st.caption('Referencia didáctica tipo Den Hartog para una estructura primaria idealmente poco amortiguada; no es una especificación normativa.')
    modal_ref=solve_modal(m1,ref['m2'],k1,ref['k2'],c1,ref['c2']);fR,X1R,_=frequency_response(modal_ref,F0=max(F0,1.0));Xsd=sdof_primary_frf(m1,k1,c1,max(F0,1.0),fR)
    fg=go.Figure();fg.add_trace(go.Scatter(x=fR,y=1000*np.abs(Xsd),name='Sin TMD',line=dict(color='#4b4c50',width=2.2)));fg.add_trace(go.Scatter(x=fR,y=1000*np.abs(X1R),name='Con TMD ref.',line=dict(color='#c8752d',width=2.5)));fg.add_vline(x=modal_ref.antiresonance_hz,line_dash='dot',line_color='#f28e1c');fg.update_layout(height=380,xaxis_title='f [Hz]',yaxis_title='|X₁| [mm]',title='Efecto del absorbedor sobre la masa primaria');st.plotly_chart(fg,use_container_width=True)

with tabs[4]:
    st.subheader('Comparador A/B')
    st.caption('Compara el sistema actual A con un segundo sistema B manteniendo la misma fuerza de excitación.')
    b1,b2,b3=st.columns(3);m2b=float(b1.number_input('m₂ B [kg]',min_value=.001,value=float(m2),step=1.0));k2b=float(b2.number_input('k₂ B [N/m]',min_value=.001,value=float(k2),step=100.0));c2b=float(b3.number_input('c₂ B [N·s/m]',min_value=0.0,value=float(c2),step=10.0))
    mb=solve_modal(m1,m2b,k1,k2b,c1,c2b);fb,X1b,X2b=frequency_response(mb,F0=max(F0,1.0));figb=go.Figure();figb.add_trace(go.Scatter(x=fgrid,y=1000*np.abs(X1g),name='A · masa primaria',line=dict(color='#c8752d',width=2.5)));figb.add_trace(go.Scatter(x=fb,y=1000*np.abs(X1b),name='B · masa primaria',line=dict(color='#4b4c50',width=2.2)));figb.update_layout(height=380,xaxis_title='f [Hz]',yaxis_title='|X₁| [mm]');st.plotly_chart(figb,use_container_width=True)

with tabs[5]:
    st.latex(r'\mathbf M\ddot{\mathbf x}+\mathbf C\dot{\mathbf x}+\mathbf K\mathbf x=\mathbf F(t)')
    st.latex(r'\mathbf M=\begin{bmatrix}m_1&0\\0&m_2\end{bmatrix},\quad \mathbf K=\begin{bmatrix}k_1+k_2&-k_2\\-k_2&k_2\end{bmatrix}')
    st.latex(r'\mathbf X(\omega)=\left(\mathbf K-\omega^2\mathbf M+i\omega\mathbf C\right)^{-1}\mathbf F_0')
    st.latex(r'\omega_{ar}\approx\sqrt{k_2/m_2}\quad\text{(absorbedor ideal, excitación sobre }m_1\text{)}')
with tabs[6]:
    st.write('El 2GDL permite pasar de “una frecuencia natural” a una visión modal: cada modo tiene una frecuencia y una forma propia. El absorbedor dinámico aprovecha esa interacción para crear una zona de baja respuesta en la masa primaria.')
    st.warning('La antirresonancia ideal y las fórmulas de ajuste son modelos lineales. En una máquina real deben revisarse no linealidades, amortiguamiento, rigidez de soportes, desalineaciones y múltiples grados de libertad.')
