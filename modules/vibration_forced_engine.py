from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class ForcedModeResult:
    mode: str
    m: float
    k: float
    c: float
    wn: float
    fn: float
    ccrit: float
    zeta: float
    w: float
    f_exc: float
    r: float
    input_amp: float
    input_unit: str
    input_label: str
    amplitude_m: float
    response_ratio: float
    phase_rad: float
    phase_deg: float
    transmissibility: float
    transmitted_force_amp_n: float
    velocity_amp: float
    acceleration_amp: float
    singular: bool
    static_reference_m: float | None
    force_amp_n: float | None
    base_amp_m: float | None
    relative_amp_m: float | None
    relative_ratio: float | None
    unbalance_mass: float | None
    eccentricity_m: float | None
    force_balance_kind: str
    note: str


def _system_props(m: float, k: float, c: float):
    if m <= 0 or k <= 0:
        raise ValueError('m y k deben ser mayores que cero.')
    if c < 0:
        raise ValueError('c debe ser no negativo.')
    wn = math.sqrt(k / m)
    fn = wn / (2 * math.pi)
    ccrit = 2 * math.sqrt(k * m)
    zeta = c / ccrit if ccrit > 0 else 0.0
    return wn, fn, ccrit, zeta


def _force_ratios(zeta: float, r: float):
    den2 = (1 - r * r) ** 2 + (2 * zeta * r) ** 2
    singular = den2 < 1e-14
    if singular:
        H = math.inf
        phase = math.pi / 2
        TR = math.inf
    else:
        den = math.sqrt(den2)
        H = 1 / den
        phase = math.atan2(2 * zeta * r, 1 - r * r)
        if phase < 0:
            phase += math.pi
        TR = math.sqrt(1 + (2 * zeta * r) ** 2) / den
    return H, phase, TR, singular


def solve_harmonic_force(m: float, k: float, c: float, F0: float, f_exc: float) -> ForcedModeResult:
    if F0 < 0 or f_exc < 0:
        raise ValueError('F0 y f deben ser no negativos.')
    wn, fn, ccrit, zeta = _system_props(m, k, c)
    w = 2 * math.pi * f_exc
    r = w / wn if wn > 0 else 0.0
    H, phase, TR, singular = _force_ratios(zeta, r)
    xst = F0 / k
    X = math.inf if singular else xst * H
    Ft = math.inf if singular else F0 * TR
    note = 'Excitación armónica clásica: la fuerza aplicada es externa y no depende de la frecuencia salvo por su fase temporal.'
    return ForcedModeResult(
        mode='force', m=m, k=k, c=c, wn=wn, fn=fn, ccrit=ccrit, zeta=zeta, w=w, f_exc=f_exc, r=r,
        input_amp=F0, input_unit='N', input_label='F₀', amplitude_m=X, response_ratio=H, phase_rad=phase,
        phase_deg=math.degrees(phase), transmissibility=TR, transmitted_force_amp_n=Ft,
        velocity_amp=(math.inf if singular else w * X), acceleration_amp=(math.inf if singular else w * w * X),
        singular=singular, static_reference_m=xst, force_amp_n=F0, base_amp_m=None, relative_amp_m=None,
        relative_ratio=None, unbalance_mass=None, eccentricity_m=None, force_balance_kind='external_force', note=note,
    )


def solve_rotating_unbalance(m: float, k: float, c: float, me: float, e_m: float, rpm: float) -> ForcedModeResult:
    if me < 0 or e_m < 0 or rpm < 0:
        raise ValueError('me, e y rpm deben ser no negativos.')
    wn, fn, ccrit, zeta = _system_props(m, k, c)
    f_exc = rpm / 60.0
    w = 2 * math.pi * f_exc
    r = w / wn if wn > 0 else 0.0
    H, phase, TR, singular = _force_ratios(zeta, r)
    F0 = me * e_m * w * w
    xref = (me / m) * e_m * r * r if m > 0 else 0.0
    X = math.inf if singular else xref * H
    Ft = math.inf if singular else F0 * TR
    note = 'Desbalance rotatorio: la excitación armónica proviene de una masa excéntrica. Su amplitud crece con ω², por lo que aumentar rpm incrementa simultáneamente la razón de frecuencia y la fuerza excitadora.'
    return ForcedModeResult(
        mode='unbalance', m=m, k=k, c=c, wn=wn, fn=fn, ccrit=ccrit, zeta=zeta, w=w, f_exc=f_exc, r=r,
        input_amp=me * e_m * 1e3, input_unit='kg·mm', input_label='mₑe', amplitude_m=X, response_ratio=(math.inf if singular or e_m == 0 else X / e_m), phase_rad=phase,
        phase_deg=math.degrees(phase), transmissibility=TR, transmitted_force_amp_n=Ft,
        velocity_amp=(math.inf if singular else w * X), acceleration_amp=(math.inf if singular else w * w * X),
        singular=singular, static_reference_m=(F0 / k if k > 0 else None), force_amp_n=F0, base_amp_m=None, relative_amp_m=None,
        relative_ratio=None, unbalance_mass=me, eccentricity_m=e_m, force_balance_kind='external_force', note=note,
    )


def solve_base_excitation(m: float, k: float, c: float, Y_m: float, f_exc: float) -> ForcedModeResult:
    if Y_m < 0 or f_exc < 0:
        raise ValueError('Y y f deben ser no negativos.')
    wn, fn, ccrit, zeta = _system_props(m, k, c)
    w = 2 * math.pi * f_exc
    r = w / wn if wn > 0 else 0.0
    den2 = (1 - r * r) ** 2 + (2 * zeta * r) ** 2
    singular = den2 < 1e-14
    if singular:
        Td = math.inf
        Zr = math.inf
        phase_x = math.pi / 2
        phase_z = math.pi / 2
        Ft = math.inf
    else:
        den = math.sqrt(den2)
        Td = math.sqrt(1 + (2 * zeta * r) ** 2) / den  # |X/Y|
        Zr = (r * r) / den  # |Z/Y|, Z = X - Y
        # phase lag of x relative to y, with x = X sin(wt - phase_x)
        phase_x = math.atan2(2 * zeta * r, 1.0) - math.atan2(2 * zeta * r, 1 - r * r)
        if phase_x < 0:
            phase_x += math.pi
        phase_z = math.atan2(2 * zeta * r, 1 - r * r)
        if phase_z < 0:
            phase_z += math.pi
        Ft = k * Y_m * Zr * math.sqrt(1 + (2 * zeta * r) ** 2)
    X = math.inf if singular else Y_m * Td
    Z = math.inf if singular else Y_m * Zr
    note = 'Excitación de base: el soporte se mueve con y(t). La variable clave para el aislador es el movimiento relativo z=x−y y la fuerza transmitida a la base.'
    return ForcedModeResult(
        mode='base', m=m, k=k, c=c, wn=wn, fn=fn, ccrit=ccrit, zeta=zeta, w=w, f_exc=f_exc, r=r,
        input_amp=Y_m * 1000, input_unit='mm', input_label='Y', amplitude_m=X, response_ratio=Td, phase_rad=phase_x,
        phase_deg=math.degrees(phase_x), transmissibility=Td, transmitted_force_amp_n=Ft,
        velocity_amp=(math.inf if singular else w * X), acceleration_amp=(math.inf if singular else w * w * X),
        singular=singular, static_reference_m=Y_m, force_amp_n=None, base_amp_m=Y_m, relative_amp_m=Z,
        relative_ratio=Zr, unbalance_mass=None, eccentricity_m=None, force_balance_kind='base_excitation', note=note,
    )


def solve_vibration(mode: str, **kwargs) -> ForcedModeResult:
    if mode == 'force':
        return solve_harmonic_force(kwargs['m'], kwargs['k'], kwargs['c'], kwargs['F0'], kwargs['f_exc'])
    if mode == 'unbalance':
        return solve_rotating_unbalance(kwargs['m'], kwargs['k'], kwargs['c'], kwargs['me'], kwargs['e_m'], kwargs['rpm'])
    if mode == 'base':
        return solve_base_excitation(kwargs['m'], kwargs['k'], kwargs['c'], kwargs['Y_m'], kwargs['f_exc'])
    raise ValueError('Modo no reconocido.')


def steady_response(res: ForcedModeResult, t: np.ndarray):
    t = np.asarray(t, dtype=float)
    y = np.zeros_like(t)
    yd = np.zeros_like(t)
    ydd = np.zeros_like(t)
    fin = np.zeros_like(t)
    rotor_theta = res.w * t
    if res.singular or not math.isfinite(res.amplitude_m):
        nan = np.full_like(t, np.nan, dtype=float)
        return dict(input=nan, x=nan, v=nan, a=nan, y=nan, yd=nan, ydd=nan, z=nan, zd=nan, zdd=nan, fk=nan, fc=nan, ft=nan, rotor_theta=rotor_theta)

    if res.mode == 'force':
        fin = res.force_amp_n * np.sin(res.w * t)
        q = res.w * t - res.phase_rad
        x = res.amplitude_m * np.sin(q)
        v = res.w * res.amplitude_m * np.cos(q)
        a = -(res.w ** 2) * res.amplitude_m * np.sin(q)
        z, zd, zdd = x.copy(), v.copy(), a.copy()
    elif res.mode == 'unbalance':
        fin = res.force_amp_n * np.sin(res.w * t)
        q = res.w * t - res.phase_rad
        x = res.amplitude_m * np.sin(q)
        v = res.w * res.amplitude_m * np.cos(q)
        a = -(res.w ** 2) * res.amplitude_m * np.sin(q)
        z, zd, zdd = x.copy(), v.copy(), a.copy()
    elif res.mode == 'base':
        Y = res.base_amp_m
        y = Y * np.sin(res.w * t)
        yd = res.w * Y * np.cos(res.w * t)
        ydd = -(res.w ** 2) * Y * np.sin(res.w * t)
        z = res.relative_amp_m * np.sin(res.w * t - math.atan2(2 * res.zeta * res.r, 1 - res.r * res.r))
        zd = res.w * res.relative_amp_m * np.cos(res.w * t - math.atan2(2 * res.zeta * res.r, 1 - res.r * res.r))
        zdd = -(res.w ** 2) * res.relative_amp_m * np.sin(res.w * t - math.atan2(2 * res.zeta * res.r, 1 - res.r * res.r))
        x = y + z
        v = yd + zd
        a = ydd + zdd
        fin = y
    else:
        raise ValueError('Modo no reconocido.')

    fk = -res.k * z
    fc = -res.c * zd
    ft = res.k * z + res.c * zd
    return dict(input=fin, x=x, v=v, a=a, y=y, yd=yd, ydd=ydd, z=z, zd=zd, zdd=zdd, fk=fk, fc=fc, ft=ft, rotor_theta=rotor_theta)


def frequency_response(mode: str, zeta: float, rmax: float = 3.0, n: int = 700):
    r = np.linspace(0.0, rmax, n)
    den2 = (1 - r * r) ** 2 + (2 * zeta * r) ** 2
    den = np.sqrt(np.maximum(den2, 1e-14))
    if mode in ('force', 'unbalance'):
        H = 1 / den
        phase = np.degrees(np.arctan2(2 * zeta * r, 1 - r * r))
        phase = np.where(phase < 0, phase + 180.0, phase)
        T = np.sqrt(1 + (2 * zeta * r) ** 2) / den
        extra = None
    elif mode == 'base':
        H = np.sqrt(1 + (2 * zeta * r) ** 2) / den   # X/Y
        phase = np.degrees(np.arctan2(2 * zeta * r, 1.0) - np.arctan2(2 * zeta * r, 1 - r * r))
        phase = np.where(phase < 0, phase + 180.0, phase)
        T = H
        extra = (r * r) / den  # Z/Y
    else:
        raise ValueError('Modo no reconocido.')
    return r, H, phase, T, extra


def force_balance_residual(res: ForcedModeResult, resp: dict):
    x = np.asarray(resp['x'])
    a = np.asarray(resp['a'])
    fk = np.asarray(resp['fk'])
    fc = np.asarray(resp['fc'])
    if res.mode in ('force', 'unbalance'):
        F = np.asarray(resp['input'])
        return F + fk + fc - res.m * a
    else:
        ydd = np.asarray(resp['ydd'])
        return -(res.m * ydd) + fk + fc - res.m * np.asarray(resp['zdd'])
