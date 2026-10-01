from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class ForcedVibrationResult:
    m: float
    k: float
    c: float
    F0: float
    f_exc: float
    wn: float
    fn: float
    ccrit: float
    zeta: float
    w: float
    r: float
    static_deflection_m: float
    magnification: float
    phase_rad: float
    phase_deg: float
    amplitude_m: float
    transmissibility: float
    transmitted_force_amp_n: float
    resonant_ratio: float | None
    resonant_frequency_hz: float | None
    peak_magnification: float | None
    singular: bool


def solve_forced_vibration(m: float, k: float, c: float, F0: float, f_exc: float) -> ForcedVibrationResult:
    if m <= 0 or k <= 0:
        raise ValueError('m y k deben ser mayores que cero.')
    if c < 0 or F0 < 0 or f_exc < 0:
        raise ValueError('c, F0 y f deben ser no negativos.')

    wn = math.sqrt(k / m)
    fn = wn / (2 * math.pi)
    ccrit = 2 * math.sqrt(k * m)
    zeta = c / ccrit
    w = 2 * math.pi * f_exc
    r = w / wn
    xst = F0 / k

    den2 = (1 - r * r) ** 2 + (2 * zeta * r) ** 2
    singular = den2 < 1e-14
    if singular:
        H = math.inf
        X = math.inf
        phase = math.pi / 2
        TR = math.inf
        Ft = math.inf
    else:
        den = math.sqrt(den2)
        H = 1 / den
        phase = math.atan2(2 * zeta * r, 1 - r * r)
        if phase < 0:
            phase += math.pi
        X = xst * H
        TR = math.sqrt(1 + (2 * zeta * r) ** 2) / den
        Ft = F0 * TR

    if zeta < 1 / math.sqrt(2):
        rr = math.sqrt(max(0.0, 1 - 2 * zeta * zeta))
        fr = rr * fn
        if zeta == 0:
            hp = math.inf
        else:
            hp = 1 / (2 * zeta * math.sqrt(max(1e-15, 1 - zeta * zeta)))
    else:
        rr = fr = hp = None

    return ForcedVibrationResult(
        m=m, k=k, c=c, F0=F0, f_exc=f_exc,
        wn=wn, fn=fn, ccrit=ccrit, zeta=zeta, w=w, r=r,
        static_deflection_m=xst, magnification=H,
        phase_rad=phase, phase_deg=math.degrees(phase), amplitude_m=X,
        transmissibility=TR, transmitted_force_amp_n=Ft,
        resonant_ratio=rr, resonant_frequency_hz=fr, peak_magnification=hp,
        singular=singular,
    )


def steady_response(res: ForcedVibrationResult, t: np.ndarray):
    t = np.asarray(t, dtype=float)
    F = res.F0 * np.sin(res.w * t)
    if res.singular or not math.isfinite(res.amplitude_m):
        nan = np.full_like(t, np.nan, dtype=float)
        return F, nan, nan, nan, nan, nan, nan
    q = res.w * t - res.phase_rad
    x = res.amplitude_m * np.sin(q)
    v = res.w * res.amplitude_m * np.cos(q)
    a = -(res.w ** 2) * res.amplitude_m * np.sin(q)
    fk = -res.k * x
    fc = -res.c * v
    ftrans = res.k * x + res.c * v
    return F, x, v, a, fk, fc, ftrans


def frequency_response(zeta: float, rmax: float = 3.0, n: int = 700):
    r = np.linspace(0.0, rmax, n)
    den2 = (1-r*r)**2 + (2*zeta*r)**2
    den = np.sqrt(np.maximum(den2, 1e-14))
    H = 1/den
    phase = np.degrees(np.arctan2(2*zeta*r, 1-r*r))
    phase = np.where(phase < 0, phase + 180.0, phase)
    TR = np.sqrt(1 + (2*zeta*r)**2) / den
    return r, H, phase, TR


def force_balance_residual(F, a, fk, fc, m: float):
    F=np.asarray(F); a=np.asarray(a); fk=np.asarray(fk); fc=np.asarray(fc)
    return F + fk + fc - m*a
