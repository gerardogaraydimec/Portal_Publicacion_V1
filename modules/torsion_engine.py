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


def solve_torsion(T_knm:float,L_m:float,G_gpa:float,section_type:str,p:dict,section:SectionData)->TorsionResult:
    if section.jt_mm4 is None or section.jt_mm4<=0:
        raise ValueError('La sección requiere una constante torsional Jt positiva.')
    T_nmm=T_knm*1e6; L_mm=L_m*1000; G_mpa=G_gpa*1000; J=section.jt_mm4
    phi=T_nmm*L_mm/(G_mpa*J)
    tau=None; mode='No se muestra una distribución puntual simple para esta geometría.'
    if section_type=='Circular maciza':
        r=float(p['d_mm'])/2; tau=abs(T_nmm*r/J); mode='Circular exacta: τ(r)=T·r/J.'
    elif section_type=='Tubular circular':
        r=float(p['do_mm'])/2; tau=abs(T_nmm*r/J); mode='Tubo circular exacto en Saint-Venant: τ(r)=T·r/J.'
    elif section_type=='Rectangular':
        mode='Rectangular: el giro usa Jt aproximado; la tensión no es radial ni lineal como en un eje circular.'
    elif section_type in ('Perfil I / H','Canal C'):
        mode='Perfil abierto: Jt usa aproximación de pared delgada. No se modela alabeo restringido ni tensiones normales de alabeo.'
    k=G_mpa*J/L_mm/1e6 # kN m/rad
    return TorsionResult(J,phi,math.degrees(phi),tau,mode,k)
