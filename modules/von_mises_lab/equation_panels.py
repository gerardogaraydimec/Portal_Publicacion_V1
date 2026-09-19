from __future__ import annotations
import streamlit as st


def equations_1d():
    st.markdown("### Formulación 1D")
    st.latex(r"\sigma_x=\frac{F}{A}")
    st.latex(r"""\boldsymbol{\sigma}=
    \begin{bmatrix}
    \sigma_x&0&0\\
    0&0&0\\
    0&0&0
    \end{bmatrix}""")
    st.latex(r"\sigma_{VM}=|\sigma_x|")
    st.latex(r"n=\frac{S_y}{\sigma_{VM}}")
    st.latex(r"\sigma_{VM}<S_y\Rightarrow\text{régimen elástico}")
    st.latex(r"\sigma_{VM}=S_y\Rightarrow\text{inicio de fluencia}")


def equations_2d():
    st.markdown("### Transformación del estado plano")
    st.latex(r"\sigma_{avg}=\frac{\sigma_x+\sigma_y}{2}")
    st.latex(r"R=\sqrt{\left(\frac{\sigma_x-\sigma_y}{2}\right)^2+\tau_{xy}^2}")
    st.latex(r"\sigma_1=\sigma_{avg}+R")
    st.latex(r"\sigma_2=\sigma_{avg}-R")
    st.latex(r"\theta_p=\frac{1}{2}\tan^{-1}\!\left(\frac{2\tau_{xy}}{\sigma_x-\sigma_y}\right)")
    st.markdown("### Criterio de Von Mises en esfuerzo plano")
    st.latex(r"\sigma_{VM}=\sqrt{\sigma_x^2-\sigma_x\sigma_y+\sigma_y^2+3\tau_{xy}^2}")
    st.latex(r"\sigma_{VM}=\sqrt{\sigma_1^2-\sigma_1\sigma_2+\sigma_2^2}")
    st.latex(r"\sigma_1^2-\sigma_1\sigma_2+\sigma_2^2=S_y^2")
    st.latex(r"n_{VM}=\frac{S_y}{\sigma_{VM}}")


def equations_3d():
    st.markdown("### Descomposición hidrostática y desviadora")
    st.latex(r"\sigma_m=\frac{\sigma_1+\sigma_2+\sigma_3}{3}")
    st.latex(r"\boldsymbol{\sigma}=\sigma_m\mathbf{I}+\mathbf{s}")
    st.latex(r"\mathbf{s}=\boldsymbol{\sigma}-\sigma_m\mathbf{I}")
    st.latex(r"J_2=\frac{1}{2}\mathbf{s}:\mathbf{s}")
    st.markdown("### Von Mises tridimensional")
    st.latex(r"\sigma_{VM}=\sqrt{3J_2}")
    st.latex(
        r"\sigma_{VM}=\sqrt{\frac{(\sigma_1-\sigma_2)^2+"
        r"(\sigma_2-\sigma_3)^2+(\sigma_3-\sigma_1)^2}{2}}"
    )
    st.latex(
        r"\sigma_{VM}=\sqrt{\frac{(\sigma_x-\sigma_y)^2+(\sigma_y-\sigma_z)^2+"
        r"(\sigma_z-\sigma_x)^2+6(\tau_{xy}^2+\tau_{yz}^2+\tau_{zx}^2)}{2}}"
    )
