from __future__ import annotations

from pathlib import Path

import numpy as np
import matplotlib

# Backend no interactivo: funciona igual en Windows local y en Streamlit Community Cloud.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Arc, FancyArrowPatch

COLORS = {
    "base": "#1f77b4",
    "principal": "#2ca02c",
    "max_tau": "#d62728",
    "beta": "#ff7f0e",
}

plt.rcParams.update({"font.family": "serif", "mathtext.fontset": "cm"})


def calcular_estado(sx: float, sy: float, txy: float, beta_deg: float) -> dict[str, float]:
    """Calcula la transformación plana de esfuerzos y parámetros del círculo de Mohr.

    Parameters
    ----------
    sx, sy, txy:
        Componentes del estado plano de esfuerzos, en una unidad consistente.
    beta_deg:
        Giro físico del elemento en grados. En el círculo de Mohr se representa como 2*beta.
    """
    beta = np.radians(beta_deg)
    dos_beta_deg = 2.0 * beta_deg
    dos_beta_rad = 2.0 * beta

    prom = (sx + sy) / 2.0
    delta = (sx - sy) / 2.0
    radio = np.hypot(delta, txy)
    theta_p = 0.5 * np.arctan2(2.0 * txy, sx - sy)

    sigma_beta = prom + delta * np.cos(dos_beta_rad) + txy * np.sin(dos_beta_rad)
    sigma_beta_ort = prom - delta * np.cos(dos_beta_rad) - txy * np.sin(dos_beta_rad)
    tau_beta = -delta * np.sin(dos_beta_rad) + txy * np.cos(dos_beta_rad)

    return {
        "sx": float(sx),
        "sy": float(sy),
        "txy": float(txy),
        "beta": float(beta),
        "beta_deg": float(beta_deg),
        "dos_beta": float(dos_beta_deg),
        "prom": float(prom),
        "delta": float(delta),
        "radio": float(radio),
        "s1": float(prom + radio),
        "s2": float(prom - radio),
        "theta_p": float(theta_p),
        "theta_p_deg": float(np.degrees(theta_p)),
        "dos_theta_p": float(np.degrees(2.0 * theta_p)),
        "sigma_beta": float(sigma_beta),
        "sigma_beta_ort": float(sigma_beta_ort),
        "tau_beta": float(tau_beta),
        # Polo, conservando la convención utilizada en el programa original.
        "px": float(sx),
        "py": float(-txy),
    }


def _posicion_desplazada(punto, centro, distancia=120.0):
    direccion = np.array(punto, dtype=float) - np.array(centro, dtype=float)
    norma = np.linalg.norm(direccion) or 1.0
    return np.array(punto, dtype=float) + direccion * distancia / norma


def _dibujar_flechas_normales(ax, centro, tam, angulo, valor, color, etiqueta):
    direccion = np.array([np.cos(angulo), np.sin(angulo)])
    base = tam + 3.0
    largo = 2.0 * tam

    for signo in (1, -1):
        inicio = centro + direccion * base * signo
        fin = centro + direccion * (base + largo) * signo
        if valor < 0:
            inicio, fin = fin, inicio

        ax.add_patch(
            FancyArrowPatch(
                inicio,
                fin,
                arrowstyle="-|>",
                color=color,
                mutation_scale=10,
                lw=1.8,
                zorder=7,
            )
        )
        if signo > 0:
            pos = centro + direccion * (base + largo + 3.5)
            ax.text(
                pos[0],
                pos[1],
                fr"${etiqueta}$",
                color=color,
                fontsize=12,
                weight="bold",
                ha="center",
                va="center",
            )


def _dibujar_flechas_cortantes(ax, centro, tam, rotacion, puntos, valor, color, etiqueta, origin):
    sentido = 1 if valor >= 0 else -1
    gap = 1.0
    lados = [
        (np.array([-tam - gap, tam]), np.array([-tam - gap, -tam])),
        (np.array([tam + gap, -tam]), np.array([tam + gap, tam])),
        (np.array([tam, tam + gap]), np.array([-tam, tam + gap])),
        (np.array([-tam, -tam - gap]), np.array([tam, -tam - gap])),
    ]

    for inicio_local, fin_local in lados:
        if sentido < 0:
            inicio_local, fin_local = fin_local, inicio_local
        inicio = inicio_local @ rotacion.T + centro
        fin = fin_local @ rotacion.T + centro
        ax.add_patch(
            FancyArrowPatch(
                inicio,
                fin,
                arrowstyle="->",
                color=color,
                mutation_scale=10,
                lw=1.5,
                zorder=6,
            )
        )

    esquina = puntos[:4][np.argmax(np.sum((puntos[:4] - origin) ** 2, axis=1))]
    direccion = esquina - centro
    direccion = direccion / (np.linalg.norm(direccion) or 1.0)
    pos = esquina + direccion * 3.0
    ax.text(
        pos[0],
        pos[1],
        fr"${etiqueta}$",
        color=color,
        fontsize=10,
        weight="bold",
        ha="left" if direccion[0] >= 0 else "right",
        va="bottom" if direccion[1] >= 0 else "top",
    )


def _dibujar_estado(ax, origin, theta, sigma_a, sigma_b, tau, distancia, color, etiquetas, etiqueta_tau=None):
    tam = 4.5
    centro = origin + distancia * np.array([np.cos(theta), np.sin(theta)])
    rotacion = np.array(
        [[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]]
    )
    puntos = (
        np.array([[-tam, -tam], [tam, -tam], [tam, tam], [-tam, tam], [-tam, -tam]])
        @ rotacion.T
        + centro
    )

    if distancia:
        ax.plot(
            [origin[0], centro[0]],
            [origin[1], centro[1]],
            color="gray",
            ls="--",
            alpha=0.2,
            lw=1.0,
        )

    ax.plot(puntos[:, 0], puntos[:, 1], color=color, lw=2.5, zorder=5)

    if etiqueta_tau and abs(tau) > 0.01:
        _dibujar_flechas_cortantes(
            ax, centro, tam, rotacion, puntos, tau, color, etiqueta_tau, origin
        )

    for angulo, valor, etiqueta in zip(
        (theta, theta + np.pi / 2.0),
        (sigma_a, sigma_b),
        etiquetas,
    ):
        _dibujar_flechas_normales(ax, centro, tam, angulo, valor, color, etiqueta)


def _dibujar_angulo(ax, origin, theta, radio, color, etiqueta):
    if abs(theta) < 1e-3:
        return

    theta_deg = np.degrees(theta)
    theta1, theta2 = (0.0, theta_deg) if theta_deg >= 0 else (theta_deg, 0.0)
    ax.add_patch(
        Arc(
            origin,
            2.0 * radio,
            2.0 * radio,
            angle=0,
            theta1=theta1,
            theta2=theta2,
            color=color,
            lw=1.6,
            alpha=0.95,
        )
    )

    angulo = np.radians(theta_deg / 2.0)
    pos = origin + (radio + 2.4) * np.array([np.cos(angulo), np.sin(angulo)])
    ax.text(
        pos[0],
        pos[1],
        fr"${etiqueta}$",
        color=color,
        fontsize=10,
        weight="bold",
        ha="left" if np.cos(angulo) >= 0 else "right",
        va="bottom" if np.sin(angulo) >= 0 else "top",
    )


def _dibujar_circulo_mohr(ax, d):
    centro = (d["prom"], 0.0)

    circulo = plt.Circle(
        centro,
        d["radio"],
        color=COLORS["base"],
        fill=False,
        lw=1.8,
        alpha=0.75,
    )
    ax.add_patch(circulo)
    ax.axhline(0, color="black", lw=1)
    ax.axvline(0, color="black", lw=1)
    ax.grid(True, ls=":", alpha=0.3)

    ax.plot(
        [d["sx"], d["sy"]],
        [d["txy"], -d["txy"]],
        "o--",
        color=COLORS["base"],
        markersize=6,
        lw=1.2,
    )
    ax.plot(
        [d["prom"], d["prom"]],
        [-d["radio"], d["radio"]],
        color=COLORS["max_tau"],
        ls="-.",
        lw=1,
        alpha=0.4,
    )

    etiquetas = [
        ((d["sx"], d["txy"]), r"$X(\sigma_x, \tau_{xy})$", COLORS["base"]),
        ((d["sy"], -d["txy"]), r"$Y(\sigma_y, \tau_{yx})$", COLORS["base"]),
        (
            (d["sigma_beta"], d["tau_beta"]),
            r"$(\sigma_\beta, \tau_\beta)$",
            COLORS["beta"],
        ),
    ]

    # Evita desplazamientos excesivos cuando el radio es muy pequeño.
    distancia_etiqueta = max(20.0, min(120.0, d["radio"] * 0.20 + 20.0))
    for punto, etiqueta, color in etiquetas:
        pos = _posicion_desplazada(punto, centro, distancia=distancia_etiqueta)
        ax.text(
            *pos,
            etiqueta,
            color=color,
            fontsize=10,
            weight="bold",
            ha="center",
            va="center",
        )

    offset = max(15.0, d["radio"] * 0.08)
    ax.text(
        d["prom"],
        -offset,
        r"$\sigma_{prom}$",
        color=COLORS["max_tau"],
        fontsize=11,
        ha="center",
        va="top",
    )
    ax.text(
        d["prom"],
        d["radio"] + offset,
        r"$\tau_{max}$",
        color=COLORS["max_tau"],
        fontsize=11,
        ha="center",
        va="bottom",
    )

    # Polo: se conserva la convención del código original.
    ax.plot(d["px"], d["py"], "ko", markersize=6, zorder=10)
    ax.text(
        d["px"] + offset,
        d["py"] + offset,
        r"$\mathbf{P(Polo)}$",
        fontsize=10,
        color="black",
        weight="bold",
    )
    ax.plot(
        [d["px"], d["sx"]],
        [d["py"], d["txy"]],
        color="black",
        ls=":",
        lw=1,
        alpha=0.6,
    )
    ax.plot(
        [d["px"], d["sy"]],
        [d["py"], -d["txy"]],
        color="black",
        ls=":",
        lw=1,
        alpha=0.6,
    )

    ax.text(d["s1"] + offset, offset * 0.3, r"$\sigma_1$", color=COLORS["principal"], fontsize=12, weight="bold")
    ax.text(d["s2"] - 3.5 * offset, offset * 0.3, r"$\sigma_2$", color=COLORS["principal"], fontsize=12, weight="bold")

    ax.plot(
        [d["prom"], d["sigma_beta"]],
        [0, d["tau_beta"]],
        color=COLORS["beta"],
        lw=1.5,
    )
    ax.plot(
        d["sigma_beta"],
        d["tau_beta"],
        "o",
        color=COLORS["beta"],
        markersize=7,
        zorder=10,
    )

    # Arcos angulares del círculo, conservando la lógica del programa original.
    ang_x = np.degrees(np.arctan2(d["txy"], d["delta"]))
    if d["dos_theta_p"] >= 0:
        theta1_p, theta2_p = ang_x - d["dos_theta_p"], ang_x
    else:
        theta1_p, theta2_p = ang_x, ang_x - d["dos_theta_p"]

    arc_base = max(d["radio"], 1.0)
    ax.add_patch(
        Arc(
            centro,
            arc_base * 0.4,
            arc_base * 0.4,
            theta1=theta1_p,
            theta2=theta2_p,
            color=COLORS["principal"],
            lw=2,
        )
    )
    ax.add_patch(
        Arc(
            centro,
            arc_base * 0.6,
            arc_base * 0.6,
            theta1=ang_x - d["dos_beta"],
            theta2=ang_x,
            color=COLORS["beta"],
            lw=2,
        )
    )

    for angulo, escala, etiqueta, color in [
        (
            np.radians((theta1_p + theta2_p) / 2.0),
            0.25,
            r"$2\theta_p$",
            COLORS["principal"],
        ),
        (
            np.radians(ang_x - d["dos_beta"] / 2.0),
            0.45,
            r"$2\beta$",
            COLORS["beta"],
        ),
    ]:
        ax.text(
            d["prom"] + arc_base * escala * np.cos(angulo),
            arc_base * escala * np.sin(angulo),
            etiqueta,
            color=color,
            fontsize=10,
            fontweight="bold",
            ha="center",
        )

    margen = max(50.0, d["radio"] * 0.35)
    ax.set_xlim(d["prom"] - d["radio"] - margen, d["prom"] + d["radio"] + margen)
    ax.set_ylim(-d["radio"] - margen, d["radio"] + margen)
    ax.set_aspect("equal")
    ax.set_xlabel(r"Esfuerzo normal, $\sigma$")
    ax.set_ylabel(r"Esfuerzo cortante, $\tau$")
    ax.set_title("Círculo de Mohr", fontsize=15, pad=14)


def _dibujar_estados(ax, d):
    origin = np.array([-9.0, 0.0])

    ax.set_title("Transformación de esfuerzos", fontsize=15, pad=14)
    ax.set_xlim(-52, 52)
    ax.set_ylim(-52, 52)
    ax.set_aspect("equal")
    ax.axis("off")

    _dibujar_estado(
        ax,
        origin,
        0.0,
        d["sx"],
        d["sy"],
        d["txy"],
        0.0,
        COLORS["base"],
        (r"\sigma_x", r"\sigma_y"),
        r"\tau_{xy}",
    )
    _dibujar_estado(
        ax,
        origin,
        d["theta_p"],
        d["s1"],
        d["s2"],
        0.0,
        34.0,
        COLORS["principal"],
        (r"\sigma_1", r"\sigma_2"),
    )
    _dibujar_estado(
        ax,
        origin,
        d["theta_p"] - np.pi / 4.0,
        d["prom"],
        d["prom"],
        d["radio"],
        34.0,
        COLORS["max_tau"],
        (r"\sigma_p", r"\sigma_p"),
        r"\tau_{max}",
    )
    _dibujar_estado(
        ax,
        origin,
        d["beta"],
        d["sigma_beta"],
        d["sigma_beta_ort"],
        d["tau_beta"],
        22.0,
        COLORS["beta"],
        (r"\sigma_\beta", r"\sigma_{\beta^\perp}"),
        r"\tau_\beta",
    )

    _dibujar_angulo(ax, origin, d["theta_p"], 7.5, COLORS["principal"], r"\theta_p")
    _dibujar_angulo(
        ax,
        origin,
        d["theta_p"] - np.pi / 4.0,
        11.0,
        COLORS["max_tau"],
        r"\theta_p-45^\circ",
    )
    _dibujar_angulo(ax, origin, d["beta"], 15.0, COLORS["beta"], r"\beta")


def crear_figura(d: dict[str, float], logo_path=None):
    """Construye la figura completa para Streamlit.

    Si se entrega ``logo_path``, incorpora el logo corporativo en la zona
    inferior derecha de la figura, manteniendo la ubicación conceptual del
    programa de escritorio original.
    """
    fig = plt.figure(figsize=(15, 8.2))
    gs = fig.add_gridspec(
        2,
        2,
        height_ratios=[1.0, 0.16],
        width_ratios=[1.0, 1.0],
        hspace=0.10,
        wspace=0.12,
    )

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    _dibujar_circulo_mohr(ax1, d)
    _dibujar_estados(ax2, d)

    # Franja inferior: se reserva para mantener la identidad visual.
    ax_footer = fig.add_subplot(gs[1, 0])
    ax_footer.axis("off")
    ax_footer.text(
        0.0,
        0.50,
        "Herramienta pedagógica · Círculo de Mohr",
        transform=ax_footer.transAxes,
        fontsize=10,
        ha="left",
        va="center",
        alpha=0.75,
    )

    ax_logo = fig.add_subplot(gs[1, 1])
    ax_logo.axis("off")

    if logo_path is not None:
        logo_path = Path(logo_path)
        if logo_path.exists():
            try:
                imagen = plt.imread(logo_path)
                ax_logo.imshow(imagen)
                ax_logo.set_aspect("equal")
            except Exception:
                ax_logo.text(
                    0.98,
                    0.50,
                    "GG DIMEC",
                    transform=ax_logo.transAxes,
                    ha="right",
                    va="center",
                    fontsize=13,
                    fontweight="bold",
                )

    return fig
