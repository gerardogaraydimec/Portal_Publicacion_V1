from __future__ import annotations
from dataclasses import dataclass
import math
from .resmat_sections import SectionData

@dataclass(frozen=True)
class TorsionResult:
    jt_mm4: float
    twist_rad: float
    twist_deg: float
    tau_max_mpa: float | None
    tau_mode: str
    stiffness_knm_per_rad: float
    theta_rate_rad_per_m: float
    gamma_max: float | None
    r_outer_mm: float | None
    exact_circular: bool


def solve_torsion(T_knm: float, L_m: float, G_gpa: float, section_type: str, p: dict, section: SectionData) -> TorsionResult:
    if section.jt_mm4 is None or section.jt_mm4 <= 0:
        raise ValueError('La sección requiere una constante torsional Jt positiva.')

    T_nmm = T_knm * 1e6
    L_mm = L_m * 1000
    G_mpa = G_gpa * 1000
    J = section.jt_mm4

    phi = T_nmm * L_mm / (G_mpa * J)
    theta_rate = phi / max(L_m, 1e-12)

    tau = None
    gamma_max = None
    r_outer = None
    exact_circular = False
    mode = 'No se muestra una distribución puntual simple para esta geometría.'

    if section_type == 'Circular maciza':
        r_outer = float(p['d_mm']) / 2.0
        tau = abs(T_nmm * r_outer / J)
        gamma_max = abs((r_outer / 1000.0) * theta_rate)
        exact_circular = True
        mode = 'Sección circular maciza: distribución exacta de Saint-Venant. τ(r)=T·r/J y γ(r)=r·dφ/dx.'
    elif section_type == 'Tubular circular':
        r_outer = float(p['do_mm']) / 2.0
        tau = abs(T_nmm * r_outer / J)
        gamma_max = abs((r_outer / 1000.0) * theta_rate)
        exact_circular = True
        mode = 'Tubo circular: distribución exacta de Saint-Venant. τ(r)=T·r/J y γ(r)=r·dφ/dx.'
    elif section_type == 'Rectangular':
        mode = 'Rectángulo macizo: el giro usa Jt aproximado de Saint-Venant. La distribución de τ no es radial y el alabeo queda libre.'
    elif section_type in ('Perfil I / H', 'Canal C'):
        mode = 'Perfil abierto: Jt usa aproximación de pared delgada abierta. Esta vista muestra el giro torsional global, pero no calcula alabeo restringido ni tensiones normales asociadas al alabeo.'
    elif section_type == 'Propiedades ingresadas':
        mode = 'Con propiedades equivalentes ingresadas se calcula el giro con Jt, pero no se infiere una distribución detallada de τ sin geometría real.'

    k = G_mpa * J / L_mm / 1e6  # kN·m/rad
    return TorsionResult(
        jt_mm4=J,
        twist_rad=phi,
        twist_deg=math.degrees(phi),
        tau_max_mpa=tau,
        tau_mode=mode,
        stiffness_knm_per_rad=k,
        theta_rate_rad_per_m=theta_rate,
        gamma_max=gamma_max,
        r_outer_mm=r_outer,
        exact_circular=exact_circular,
    )
