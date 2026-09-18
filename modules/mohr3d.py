from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np


COLORS = {
    "circle13": "#1f77b4",
    "circle12": "#2ca02c",
    "circle23": "#d62728",
    "rotation": "#ff7f0e",
    "active_plane": "#8ecae6",
    "active_point": "#f28e1c",
    "traction": "#6f42c1",
    "shear": "#444444",
    "cube": "#8c564b",
    "global": "#9aa0a6",
    "x": "#1f77b4",
    "y": "#2ca02c",
    "z": "#d62728",
}

plt.rcParams.update({"font.family": "serif", "mathtext.fontset": "cm"})


def rotation_matrix_x(angle_rad):
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])


def rotation_matrix_y(angle_rad):
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])


def rotation_matrix_z(angle_rad):
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def rotation_matrix(phi_deg, theta_deg, psi_deg):
    phi, theta, psi = np.radians([phi_deg, theta_deg, psi_deg])
    return rotation_matrix_z(psi) @ rotation_matrix_y(theta) @ rotation_matrix_x(phi)


def normal_desde_angulos(azimut_deg, elevacion_deg):
    azimut, elevacion = np.radians([azimut_deg, elevacion_deg])
    return np.array(
        [
            np.cos(elevacion) * np.cos(azimut),
            np.cos(elevacion) * np.sin(azimut),
            np.sin(elevacion),
        ],
        dtype=float,
    )


def base_plano(normal):
    normal = np.asarray(normal, dtype=float)
    norma = np.linalg.norm(normal)
    normal = normal / (norma if norma else 1.0)

    referencia = (
        np.array([0.0, 0.0, 1.0])
        if abs(normal[2]) < 0.85
        else np.array([0.0, 1.0, 0.0])
    )

    tangente_1 = np.cross(normal, referencia)
    norma_t1 = np.linalg.norm(tangente_1)

    if norma_t1 < 1e-8:
        referencia = np.array([1.0, 0.0, 0.0])
        tangente_1 = np.cross(normal, referencia)
        norma_t1 = np.linalg.norm(tangente_1)

    tangente_1 = tangente_1 / (norma_t1 if norma_t1 else 1.0)
    tangente_2 = np.cross(normal, tangente_1)
    norma_t2 = np.linalg.norm(tangente_2)
    tangente_2 = tangente_2 / (norma_t2 if norma_t2 else 1.0)

    return tangente_1, tangente_2


def direcciones_principales(tensor):
    valores, vectores = np.linalg.eigh(tensor)
    orden = np.argsort(valores)[::-1]
    valores = valores[orden]
    vectores = vectores[:, orden]

    if np.linalg.det(vectores) < 0:
        vectores[:, -1] *= -1

    return valores, vectores


def esfuerzo_en_plano(tensor, normal):
    normal = np.asarray(normal, dtype=float)
    normal /= np.linalg.norm(normal) or 1.0

    traccion = tensor @ normal
    sigma_n = float(normal @ traccion)
    vector_cortante = traccion - sigma_n * normal
    tau_n = float(np.linalg.norm(vector_cortante))

    return {
        "normal": normal,
        "traction": traccion,
        "sigma_n": sigma_n,
        "shear_vec": vector_cortante,
        "tau_n": tau_n,
    }


def recopilar_datos(
    sx,
    sy,
    sz,
    txy,
    tyz,
    tzx,
    phi,
    theta,
    psi,
    alpha_n,
    beta_n,
):
    tensor = np.array(
        [
            [sx, txy, tzx],
            [txy, sy, tyz],
            [tzx, tyz, sz],
        ],
        dtype=float,
    )

    rotacion = rotation_matrix(phi, theta, psi)
    tensor_rotado = rotacion.T @ tensor @ rotacion

    principales, ejes_principales = direcciones_principales(tensor)

    normal_local = normal_desde_angulos(alpha_n, beta_n)
    normal_activa = rotacion @ normal_local

    colores_caras = (COLORS["x"], COLORS["y"], COLORS["z"])

    estados_base = []
    estados_rotados = []

    for idx, (label, color) in enumerate(zip(("x", "y", "z"), colores_caras)):
        estado = esfuerzo_en_plano(tensor, np.eye(3)[:, idx])
        estado.update({"label": label, "color": color})
        estados_base.append(estado)

    for idx, (label, color) in enumerate(zip(("x'", "y'", "z'"), colores_caras)):
        estado = esfuerzo_en_plano(tensor, rotacion[:, idx])
        estado.update({"label": label, "color": color})
        estados_rotados.append(estado)

    estado_activo = esfuerzo_en_plano(tensor, normal_activa)
    estado_activo.update(
        {
            "label": "n*",
            "color": COLORS["active_point"],
            "normal_local": normal_local,
            "alpha_n": alpha_n,
            "beta_n": beta_n,
        }
    )

    media = float(np.trace(tensor) / 3.0)
    desviador = tensor - np.eye(3) * media
    j2 = float(0.5 * np.sum(desviador * desviador))

    von_mises = float(
        np.sqrt(
            0.5 * ((sx - sy) ** 2 + (sy - sz) ** 2 + (sz - sx) ** 2)
            + 3.0 * (txy ** 2 + tyz ** 2 + tzx ** 2)
        )
    )

    circulos = (
        {
            "label": r"$C_{13}$",
            "center": (principales[0] + principales[2]) / 2.0,
            "radius": abs(principales[0] - principales[2]) / 2.0,
            "color": COLORS["circle13"],
        },
        {
            "label": r"$C_{12}$",
            "center": (principales[0] + principales[1]) / 2.0,
            "radius": abs(principales[0] - principales[1]) / 2.0,
            "color": COLORS["circle12"],
        },
        {
            "label": r"$C_{23}$",
            "center": (principales[1] + principales[2]) / 2.0,
            "radius": abs(principales[1] - principales[2]) / 2.0,
            "color": COLORS["circle23"],
        },
    )

    return {
        "tensor": tensor,
        "tensor_rotado": tensor_rotado,
        "rotation": rotacion,
        "principal_stresses": principales,
        "principal_axes": ejes_principales,
        "base_states": estados_base,
        "rotated_states": estados_rotados,
        "active_state": estado_activo,
        "circles": circulos,
        "tau_max": float(abs(principales[0] - principales[2]) / 2.0),
        "von_mises": von_mises,
        "mean_stress": media,
        "j2": j2,
        "phi": float(phi),
        "theta": float(theta),
        "psi": float(psi),
        "alpha_n": float(alpha_n),
        "beta_n": float(beta_n),
    }


def geometria_cubo(base, escala):
    medio = escala / 2.0

    vertices_locales = np.array(
        [
            [-medio, -medio, -medio],
            [medio, -medio, -medio],
            [medio, medio, -medio],
            [-medio, medio, -medio],
            [-medio, -medio, medio],
            [medio, -medio, medio],
            [medio, medio, medio],
            [-medio, medio, medio],
        ]
    )

    vertices = vertices_locales @ base.T

    aristas = (
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    )

    caras_idx = (
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (2, 3, 7, 6),
        (1, 2, 6, 5),
        (0, 3, 7, 4),
    )

    caras = [[vertices[idx] for idx in cara] for cara in caras_idx]
    return vertices, aristas, caras


def configurar_eje_mohr(ax, datos):
    sigma_candidatos = list(datos["principal_stresses"])
    sigma_candidatos.extend(estado["sigma_n"] for estado in datos["base_states"])
    sigma_candidatos.extend(estado["sigma_n"] for estado in datos["rotated_states"])
    sigma_candidatos.append(datos["active_state"]["sigma_n"])

    tau_candidatos = [circulo["radius"] for circulo in datos["circles"]]
    tau_candidatos.extend(estado["tau_n"] for estado in datos["base_states"])
    tau_candidatos.extend(estado["tau_n"] for estado in datos["rotated_states"])
    tau_candidatos.append(datos["active_state"]["tau_n"])

    sigma_min = min(sigma_candidatos)
    sigma_max = max(sigma_candidatos)
    tau_max = max(tau_candidatos + [1.0])

    margen_sigma = max(40.0, 0.12 * (sigma_max - sigma_min + 1.0))
    margen_tau = max(30.0, 0.20 * tau_max)

    ax.clear()
    ax.set_title("Círculos de Mohr para el Tensor 3D", fontsize=16, pad=16)
    ax.axhline(0.0, color="black", lw=1.0)
    ax.axvline(0.0, color="black", lw=1.0)
    ax.grid(True, ls=":", alpha=0.35)

    ax.set_xlabel(r"$\sigma$", fontsize=15, fontweight="bold")
    ax.set_ylabel(r"$\tau$", fontsize=15, fontweight="bold")

    ax.set_xlim(sigma_min - margen_sigma, sigma_max + margen_sigma)
    ax.set_ylim(-(tau_max + margen_tau), tau_max + margen_tau)


def dibujar_mohr(ax, datos):
    configurar_eje_mohr(ax, datos)

    theta = np.linspace(0.0, 2.0 * np.pi, 400)

    circulo_dominio = datos["circles"][0]
    x_dominio = np.linspace(
        circulo_dominio["center"] - circulo_dominio["radius"],
        circulo_dominio["center"] + circulo_dominio["radius"],
        500,
    )
    y_dominio = np.sqrt(
        np.clip(
            circulo_dominio["radius"] ** 2
            - (x_dominio - circulo_dominio["center"]) ** 2,
            0.0,
            None,
        )
    )

    ax.fill_between(
        x_dominio,
        -y_dominio,
        y_dominio,
        facecolor=circulo_dominio["color"],
        edgecolor=circulo_dominio["color"],
        hatch="///",
        alpha=0.10,
        linewidth=0.0,
        zorder=0,
    )

    for circulo_vacio in datos["circles"][1:]:
        x_vacio = np.linspace(
            circulo_vacio["center"] - circulo_vacio["radius"],
            circulo_vacio["center"] + circulo_vacio["radius"],
            400,
        )
        y_vacio = np.sqrt(
            np.clip(
                circulo_vacio["radius"] ** 2
                - (x_vacio - circulo_vacio["center"]) ** 2,
                0.0,
                None,
            )
        )
        ax.fill_between(
            x_vacio,
            -y_vacio,
            y_vacio,
            facecolor="white",
            edgecolor="none",
            alpha=1.0,
            zorder=0.2,
        )

    for circulo in datos["circles"]:
        centro = circulo["center"]
        radio = circulo["radius"]

        x = centro + radio * np.cos(theta)
        y = radio * np.sin(theta)

        ax.plot(x, y, color=circulo["color"], lw=2.3)
        ax.text(
            centro,
            radio + max(10.0, 0.05 * (datos["tau_max"] + 1.0)),
            circulo["label"],
            color=circulo["color"],
            fontsize=11,
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    for idx, sigma_principal in enumerate(datos["principal_stresses"], start=1):
        ax.plot(sigma_principal, 0.0, "o", color=COLORS["rotation"], markersize=6)
        ax.text(
            sigma_principal,
            10.0,
            fr"$\sigma_{idx}$",
            color=COLORS["rotation"],
            fontsize=11,
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    for estado in datos["base_states"]:
        ax.plot(
            estado["sigma_n"],
            estado["tau_n"],
            marker="o",
            markersize=7,
            markerfacecolor="white",
            markeredgecolor=estado["color"],
            markeredgewidth=1.8,
            linestyle="None",
        )
        ax.plot(
            estado["sigma_n"],
            -estado["tau_n"],
            marker="o",
            markersize=5,
            markerfacecolor="white",
            markeredgecolor=estado["color"],
            markeredgewidth=1.1,
            linestyle="None",
            alpha=0.45,
        )

    for estado in datos["rotated_states"]:
        ax.plot(
            estado["sigma_n"],
            estado["tau_n"],
            marker="s",
            markersize=7,
            color=estado["color"],
            linestyle="None",
        )
        ax.plot(
            estado["sigma_n"],
            -estado["tau_n"],
            marker="s",
            markersize=5,
            color=estado["color"],
            linestyle="None",
            alpha=0.35,
        )

    estado_activo = datos["active_state"]
    ax.plot(
        [estado_activo["sigma_n"], estado_activo["sigma_n"]],
        [-estado_activo["tau_n"], estado_activo["tau_n"]],
        color=estado_activo["color"],
        lw=1.0,
        ls="--",
        alpha=0.35,
    )
    ax.plot(
        estado_activo["sigma_n"],
        estado_activo["tau_n"],
        marker="*",
        markersize=15,
        color=estado_activo["color"],
        markeredgecolor="#333333",
        markeredgewidth=0.8,
        linestyle="None",
        zorder=6,
    )
    ax.annotate(
        r"$n^*$",
        xy=(estado_activo["sigma_n"], estado_activo["tau_n"]),
        xytext=(10, 13),
        textcoords="offset points",
        color=estado_activo["color"],
        fontsize=11,
        fontweight="bold",
        ha="left",
        va="bottom",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=0.15),
    )

    handles = [
        Line2D(
            [], [],
            marker="o",
            markersize=7,
            markerfacecolor="white",
            markeredgecolor="#333333",
            markeredgewidth=1.5,
            linestyle="None",
            label="Planos globales x, y, z",
        ),
        Line2D(
            [], [],
            marker="s",
            markersize=7,
            color="#333333",
            linestyle="None",
            label="Planos girados x', y', z'",
        ),
        Line2D(
            [], [],
            marker="*",
            markersize=12,
            markerfacecolor=COLORS["active_point"],
            markeredgecolor="#333333",
            linestyle="None",
            label="Plano activo n*",
        ),
        Patch(
            facecolor=COLORS["circle13"],
            edgecolor=COLORS["circle13"],
            hatch="///",
            alpha=0.10,
            label="Dominio de los posibles\nestados de esfuerzos",
        ),
    ]

    ax.legend(
        handles=handles,
        loc="upper left",
        fontsize=8.5,
        framealpha=0.9,
        borderpad=0.35,
    )


def configurar_eje_3d(ax):
    ax.cla()
    ax.set_title("Giro del Estado de Esfuerzos", fontsize=16, pad=16)
    ax.set_xlabel("X", fontsize=10)
    ax.set_ylabel("Y", fontsize=10)
    ax.set_zlabel("Z", fontsize=10)

    ax.set_xlim(-2.3, 2.3)
    ax.set_ylim(-2.3, 2.3)
    ax.set_zlim(-2.3, 2.3)
    ax.set_box_aspect((1.0, 1.0, 1.0))
    ax.view_init(elev=23, azim=-52)

    ax.xaxis.pane.set_alpha(0.06)
    ax.yaxis.pane.set_alpha(0.06)
    ax.zaxis.pane.set_alpha(0.06)


def dibujar_cubo(ax, base, color, alpha_caras, alpha_aristas, linewidth):
    vertices, aristas, caras = geometria_cubo(base, escala=1.8)

    if alpha_caras > 0.0:
        ax.add_collection3d(
            Poly3DCollection(
                caras,
                facecolors=color,
                edgecolors=color,
                linewidths=0.6,
                alpha=alpha_caras,
            )
        )

    for idx_i, idx_j in aristas:
        puntos = vertices[[idx_i, idx_j]]
        ax.plot(
            puntos[:, 0],
            puntos[:, 1],
            puntos[:, 2],
            color=color,
            lw=linewidth,
            alpha=alpha_aristas,
        )


def dibujar_ejes(ax, base, labels, colors, scale, alpha=1.0):
    for idx, (label, color) in enumerate(zip(labels, colors)):
        vector = base[:, idx] * scale

        ax.quiver(
            0.0, 0.0, 0.0,
            vector[0], vector[1], vector[2],
            color=color,
            linewidth=2.2,
            arrow_length_ratio=0.12,
            alpha=alpha,
        )

        posicion = vector * 1.12
        ax.text(
            posicion[0],
            posicion[1],
            posicion[2],
            label,
            color=color,
            fontsize=11,
            fontweight="bold",
            ha="center",
            va="center",
        )


def dibujar_ejes_principales(ax, datos):
    escala = 1.55

    for idx, (vector, color) in enumerate(
        zip(
            datos["principal_axes"].T,
            (COLORS["circle13"], COLORS["circle12"], COLORS["circle23"]),
        ),
        start=1,
    ):
        extremos = np.vstack((-vector * escala, vector * escala))
        ax.plot(
            extremos[:, 0],
            extremos[:, 1],
            extremos[:, 2],
            color=color,
            ls="--",
            lw=1.3,
            alpha=0.75,
        )

        etiqueta = vector * (escala * 1.08)
        ax.text(
            etiqueta[0],
            etiqueta[1],
            etiqueta[2],
            fr"$\sigma_{idx}$",
            color=color,
            fontsize=10,
            fontweight="bold",
        )


def dibujar_tracciones(ax, datos):
    referencia = max(np.max(np.abs(datos["principal_stresses"])), 1.0)
    factor = 0.8 / referencia

    for estado in datos["rotated_states"]:
        centro = estado["normal"] * 0.95
        vector_normal = estado["sigma_n"] * estado["normal"] * factor
        vector_cortante = estado["shear_vec"] * factor
        vector_total = estado["traction"] * factor

        ax.quiver(
            centro[0], centro[1], centro[2],
            vector_normal[0], vector_normal[1], vector_normal[2],
            color=estado["color"],
            linewidth=2.5,
            arrow_length_ratio=0.15,
        )

        ax.quiver(
            centro[0] + vector_normal[0],
            centro[1] + vector_normal[1],
            centro[2] + vector_normal[2],
            vector_cortante[0],
            vector_cortante[1],
            vector_cortante[2],
            color=COLORS["shear"],
            linewidth=2.0,
            arrow_length_ratio=0.15,
        )

        ax.quiver(
            centro[0], centro[1], centro[2],
            vector_total[0], vector_total[1], vector_total[2],
            color=COLORS["traction"],
            linewidth=1.6,
            arrow_length_ratio=0.12,
            alpha=0.65,
        )

    handles = [
        Line2D([], [], color=COLORS["global"], lw=2.6, label="Cubo original"),
        Line2D([], [], color=COLORS["cube"], lw=2.6, label="Cubo rotado"),
        Line2D([], [], color=COLORS["active_plane"], lw=2.8, label="Plano activo n*"),
        Line2D([], [], color=COLORS["traction"], lw=2.6, label="Tracción total"),
        Line2D([], [], color=COLORS["shear"], lw=2.6, label="Componente cortante"),
    ]

    ax.legend(
        handles=handles,
        loc="upper left",
        bbox_to_anchor=(0.01, 0.98),
        fontsize=8.3,
        framealpha=0.9,
        borderpad=0.35,
        labelspacing=0.35,
        handlelength=2.2,
        handletextpad=0.55,
    )


def dibujar_plano_activo(ax, datos):
    estado = datos["active_state"]
    tangente_1, tangente_2 = base_plano(estado["normal"])

    semilado = 0.72
    vertices = [
        (-tangente_1 - tangente_2) * semilado,
        (tangente_1 - tangente_2) * semilado,
        (tangente_1 + tangente_2) * semilado,
        (-tangente_1 + tangente_2) * semilado,
    ]

    ax.add_collection3d(
        Poly3DCollection(
            [vertices],
            facecolors=COLORS["active_plane"],
            edgecolors=COLORS["active_point"],
            linewidths=1.2,
            alpha=0.18,
        )
    )

    referencia = max(np.max(np.abs(datos["principal_stresses"])), 1.0)
    factor = 0.9 / referencia

    vector_normal = estado["sigma_n"] * estado["normal"] * factor
    vector_cortante = estado["shear_vec"] * factor
    vector_total = estado["traction"] * factor

    ax.quiver(
        0.0, 0.0, 0.0,
        estado["normal"][0] * 1.12,
        estado["normal"][1] * 1.12,
        estado["normal"][2] * 1.12,
        color=COLORS["active_point"],
        linewidth=2.8,
        arrow_length_ratio=0.12,
        alpha=0.95,
    )

    ax.quiver(
        0.0, 0.0, 0.0,
        vector_normal[0], vector_normal[1], vector_normal[2],
        color=COLORS["active_point"],
        linewidth=2.5,
        arrow_length_ratio=0.14,
        alpha=0.95,
    )

    ax.quiver(
        vector_normal[0],
        vector_normal[1],
        vector_normal[2],
        vector_cortante[0],
        vector_cortante[1],
        vector_cortante[2],
        color=COLORS["shear"],
        linewidth=2.2,
        arrow_length_ratio=0.14,
        alpha=0.95,
    )

    ax.quiver(
        0.0, 0.0, 0.0,
        vector_total[0], vector_total[1], vector_total[2],
        color=COLORS["traction"],
        linewidth=2.3,
        arrow_length_ratio=0.13,
        alpha=0.82,
    )

    etiqueta = estado["normal"] * 1.22
    ax.text(
        etiqueta[0],
        etiqueta[1],
        etiqueta[2],
        r"$n^*$",
        color=COLORS["active_point"],
        fontsize=11,
        fontweight="bold",
    )


def dibujar_estado_3d(ax, datos):
    configurar_eje_3d(ax)

    dibujar_cubo(
        ax,
        np.eye(3),
        COLORS["global"],
        alpha_caras=0.00,
        alpha_aristas=0.40,
        linewidth=1.0,
    )
    dibujar_ejes(
        ax,
        np.eye(3),
        ("x", "y", "z"),
        (COLORS["global"],) * 3,
        scale=1.2,
        alpha=0.75,
    )

    dibujar_cubo(
        ax,
        datos["rotation"],
        COLORS["cube"],
        alpha_caras=0.08,
        alpha_aristas=0.95,
        linewidth=2.0,
    )
    dibujar_ejes(
        ax,
        datos["rotation"],
        ("x'", "y'", "z'"),
        (COLORS["x"], COLORS["y"], COLORS["z"]),
        scale=1.45,
    )

    dibujar_ejes_principales(ax, datos)
    dibujar_tracciones(ax, datos)
    dibujar_plano_activo(ax, datos)


def crear_figura(datos, logo_path=None):
    fig = plt.figure(figsize=(16, 8.8))

    gs = fig.add_gridspec(
        2,
        2,
        height_ratios=[1.0, 0.11],
        width_ratios=[1.0, 1.08],
        hspace=0.03,
        wspace=0.14,
    )

    ax_mohr = fig.add_subplot(gs[0, 0])
    ax_3d = fig.add_subplot(gs[0, 1], projection="3d")

    dibujar_mohr(ax_mohr, datos)
    dibujar_estado_3d(ax_3d, datos)

    ax_footer = fig.add_subplot(gs[1, 0])
    ax_footer.axis("off")
    ax_footer.text(
        0.0,
        0.52,
        "Herramienta pedagógica · Círculo de Mohr 3D",
        transform=ax_footer.transAxes,
        fontsize=9.5,
        ha="left",
        va="center",
        alpha=0.72,
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
                pass

    return fig


def crear_figura_mohr_compacta(datos):
    """Figura compacta del Círculo de Mohr con escala geométrica 1:1.

    El eje mantiene la misma escala física para sigma y tau. De este modo los
    círculos siguen siendo círculos aunque cambie mucho el rango de esfuerzos.
    Matplotlib expande automáticamente los límites necesarios para aprovechar
    el rectángulo disponible sin deformar la geometría.
    """
    fig, ax = plt.subplots(figsize=(9.6, 3.85))
    dibujar_mohr(ax, datos)

    # Clave para no deformar el Círculo de Mohr.
    ax.set_aspect("equal", adjustable="datalim", anchor="C")

    ax.set_title("Círculos de Mohr para el Tensor 3D", fontsize=12.8, pad=5)
    ax.tick_params(axis="both", labelsize=8.0)
    ax.xaxis.label.set_size(11.0)
    ax.yaxis.label.set_size(11.0)

    leyenda = ax.get_legend()
    if leyenda is not None:
        for text in leyenda.get_texts():
            text.set_fontsize(6.6)

    fig.subplots_adjust(left=0.075, right=0.995, top=0.89, bottom=0.15)
    return fig


def crear_figura_3d_compacta(datos):
    """Figura 3D compacta con jerarquía visual secundaria respecto de Mohr."""
    # Figura más angosta y relativamente alta: al vivir en una columna menor,
    # queda con altura similar a Mohr sin dominar el ancho de la pantalla.
    fig = plt.figure(figsize=(6.4, 4.2))
    ax = fig.add_subplot(111, projection="3d")
    dibujar_estado_3d(ax, datos)

    ax.set_title("Giro del Estado de Esfuerzos", fontsize=12.4, pad=4)
    ax.tick_params(axis="both", labelsize=6.8)
    ax.xaxis.label.set_size(8.2)
    ax.yaxis.label.set_size(8.2)
    ax.zaxis.label.set_size(8.2)

    leyenda = ax.get_legend()
    if leyenda is not None:
        for text in leyenda.get_texts():
            text.set_fontsize(6.1)

    fig.subplots_adjust(left=0.00, right=0.96, top=0.90, bottom=0.01)
    return fig
