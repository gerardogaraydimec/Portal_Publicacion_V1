from __future__ import annotations
from dataclasses import dataclass
import math
from .resmat_sections import SectionData

K_FACTORS = {
    'Articulada – articulada': 1.0,
    'Empotrada – libre': 2.0,
    'Empotrada – empotrada': 0.5,
    'Empotrada – articulada': 0.699,
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
    pcr_y_kn: float
    pcr_z_kn: float
    sigma_euler_mpa: float
    load_ratio: float
    euler_yield_intersection: float | None
    johnson_transition: float | None
    imin_mm4: float
    rmin_mm: float


def solve_column(P_kn: float, L_m: float, E_gpa: float, section: SectionData, end_condition: str, fy_mpa: float | None = None) -> ColumnResult:
    if min(L_m, E_gpa, section.area_mm2, section.iy_mm4, section.iz_mm4) <= 0:
        raise ValueError('L, E, A e inercias deben ser positivas.')
    if end_condition not in K_FACTORS:
        raise KeyError(end_condition)

    K = K_FACTORS[end_condition]
    Le = K * L_m
    Le_mm = Le * 1000.0
    E_mpa = E_gpa * 1000.0

    ly = Le_mm / section.ry_mm
    lz = Le_mm / section.rz_mm
    pcr_y_n = math.pi**2 * E_mpa * section.iy_mm4 / Le_mm**2
    pcr_z_n = math.pi**2 * E_mpa * section.iz_mm4 / Le_mm**2

    if pcr_y_n <= pcr_z_n:
        lam = ly
        Imin = section.iy_mm4
        rmin = section.ry_mm
        axis = 'y (gobierna Iy)'
        pcr_n = pcr_y_n
    else:
        lam = lz
        Imin = section.iz_mm4
        rmin = section.rz_mm
        axis = 'z (gobierna Iz)'
        pcr_n = pcr_z_n

    pcr_kn = pcr_n / 1000.0
    sigma_e = math.pi**2 * E_mpa / lam**2
    sigma = P_kn * 1000.0 / section.area_mm2
    ratio = P_kn / pcr_kn if pcr_kn > 0 else math.inf

    lam_yield = None
    cc = None
    if fy_mpa and fy_mpa > 0:
        lam_yield = math.pi * math.sqrt(E_mpa / fy_mpa)
        cc = math.sqrt(2.0) * lam_yield

    return ColumnResult(
        K=K,
        effective_length_m=Le,
        sigma_axial_mpa=sigma,
        lambda_y=ly,
        lambda_z=lz,
        lambda_governing=lam,
        governing_axis=axis,
        pcr_kn=pcr_kn,
        pcr_y_kn=pcr_y_n/1000.0,
        pcr_z_kn=pcr_z_n/1000.0,
        sigma_euler_mpa=sigma_e,
        load_ratio=ratio,
        euler_yield_intersection=lam_yield,
        johnson_transition=cc,
        imin_mm4=Imin,
        rmin_mm=rmin,
    )


def johnson_stress_mpa(lam, E_gpa: float, fy_mpa: float):
    E_mpa = E_gpa * 1000.0
    return fy_mpa * (1.0 - fy_mpa * lam**2 / (4.0 * math.pi**2 * E_mpa))
