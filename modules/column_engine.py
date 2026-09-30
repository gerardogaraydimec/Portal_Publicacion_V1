from __future__ import annotations
from dataclasses import dataclass
import math
from .resmat_sections import SectionData

K_FACTORS={
    'Articulada – articulada':1.0,
    'Empotrada – libre':2.0,
    'Empotrada – empotrada':0.5,
    'Empotrada – articulada':0.699,
}

@dataclass(frozen=True)
class ColumnResult:
    K: float
    effective_length_m: float
    sigma_axial_mpa: float
    lambda_y: float
    lambda_z: float
    lambda_governing: float
    governing_axis: str
    pcr_kn: float
    sigma_euler_mpa: float
    load_ratio: float
    euler_yield_limit: float | None


def solve_column(P_kn:float,L_m:float,E_gpa:float,section:SectionData,end_condition:str,fy_mpa:float|None=None)->ColumnResult:
    if min(L_m,E_gpa,section.area_mm2,section.iy_mm4,section.iz_mm4)<=0: raise ValueError('L, E, A e inercias deben ser positivas.')
    K=K_FACTORS[end_condition]; Le=K*L_m
    # dimensionless slenderness, L in mm
    ly=Le*1000/section.ry_mm; lz=Le*1000/section.rz_mm
    if ly>=lz: lam=ly; Imin=section.iy_mm4; axis='y (eje débil)'
    else: lam=lz; Imin=section.iz_mm4; axis='z'
    E_mpa=E_gpa*1000
    pcr_n=math.pi**2*E_mpa*Imin/(Le*1000)**2
    pcr_kn=pcr_n/1000
    sigma_e=math.pi**2*E_mpa/lam**2
    sigma=P_kn*1000/section.area_mm2
    ratio=P_kn/pcr_kn if pcr_kn>0 else math.inf
    lim=None if not fy_mpa or fy_mpa<=0 else math.pi*math.sqrt(2*E_mpa/fy_mpa)
    return ColumnResult(K,Le,sigma,ly,lz,lam,axis,pcr_kn,sigma_e,ratio,lim)
