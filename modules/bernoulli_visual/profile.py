"""Quasi-one-dimensional sampling for the educational 3D view.

The original V2 solver remains unchanged. The intermediate geometry is an
explicit visualization assumption, not a measured pipe and not a CFD result.
All values sent to the frontend are calculated in Python in SI units.
"""
from __future__ import annotations

import math
from dataclasses import asdict
from typing import Any

import numpy as np

from .fluid_engine import G, FluidResult, solve_ideal_bernoulli


def solve_checked(**kwargs: Any) -> FluidResult:
    """Reject nonfinite inputs before invoking the original, unchanged solver."""
    for name in ('rho', 'D1_mm', 'D2_mm', 'z1_m', 'z2_m',
                 'p1_kPa', 'p2_kPa', 'Q_Ls'):
        if name not in kwargs or not math.isfinite(float(kwargs[name])):
            raise ValueError(f'El dato {name} debe ser un n\u00famero finito.')
    return solve_ideal_bernoulli(**kwargs)


def _smooth(values: np.ndarray, a: float, b: float) -> np.ndarray:
    t = np.clip((values - a) / (b - a), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def sample_profile(result: FluidResult, rho: float, geometry: str,
                   length_m: float = 6.0, samples: int = 321) -> dict[str, Any]:
    """Return smooth geometry and ideal-flow samples.

    length_m is the horizontal length used only for tracer travel time.
    Stations are 0.1/0.9, except Venturi, where station 2 is the throat at 0.5.
    The Venturi extension after station 2 recovers D1 while keeping z2.
    It is a labeled illustrative extension, not a third measured state.
    """
    if not result.ok:
        raise ValueError(result.message)
    if not math.isfinite(rho) or rho <= 0:
        raise ValueError('La densidad debe ser positiva y finita.')
    if not math.isfinite(length_m) or length_m <= 0:
        raise ValueError('La longitud debe ser positiva y finita.')
    if samples < 41 or samples > 2001:
        raise ValueError('Se requieren entre 41 y 2001 muestras.')
    for name, value in asdict(result).items():
        if isinstance(value, (int, float)) and not math.isfinite(value):
            raise ValueError(f'El resultado {name} no es finito.')

    venturi = geometry == 'venturi'
    s1, s2 = 0.1, 0.5 if venturi else 0.9
    s = np.unique(np.r_[np.linspace(0.0, 1.0, samples), s1, s2])
    if venturi:
        blend = _smooth(s, 0.20, 0.43) - _smooth(s, 0.57, 0.84)
        z = result.z1_m + (result.z2_m-result.z1_m)*_smooth(s, 0.18, 0.43)
    else:
        blend = _smooth(s, 0.20, 0.80)
        z = result.z1_m + (result.z2_m-result.z1_m)*blend
    diameter = result.D1_m + (result.D2_m-result.D1_m)*blend
    area = np.pi*diameter**2/4.0
    velocity = float(result.Q_m3s)/area
    kinetic = velocity**2/(2*G)
    total = np.full_like(s, float(result.EGL1_m))
    pressure_head = total-z-kinetic
    pressure = rho*G*pressure_head
    x = length_m*s
    ds = np.hypot(np.diff(x), np.diff(z))
    # Uniform tracer density in residence time yields equal flux and avoids
    # the misleading pile-up of particles in the throat.
    if float(result.Q_m3s) > 0.0:
        dt = ds*0.5*(1.0/velocity[:-1]+1.0/velocity[1:])
        travel = np.r_[0.0, np.cumsum(dt)]
    else:
        travel = np.zeros_like(s)
    arrays = {
        's': s, 'x_m': x, 'z_m': z, 'diameter_m': diameter, 'area_m2': area,
        'velocity_ms': velocity, 'pressure_Pa': pressure,
        'pressure_head_m': pressure_head, 'velocity_head_m': kinetic,
        'hgl_m': total-kinetic, 'egl_m': total, 'travel_s': travel,
    }
    if any(not np.all(np.isfinite(v)) for v in arrays.values()):
        raise ValueError('Estos datos exceden el rango num\u00e9rico del modelo.')
    payload: dict[str, Any] = {name: values.tolist() for name, values in arrays.items()}
    payload.update({
        'schema': 1, 'geometry': geometry, 'rho': rho, 'g': G,
        'length_m': length_m, 'Q_m3s': float(result.Q_m3s),
        'station1_index': int(np.argmin(abs(s-s1))),
        'station2_index': int(np.argmin(abs(s-s2))),
        'station2_name': 'Garganta 2' if venturi else 'Secci\u00f3n 2',
        'duration_s': float(travel[-1]),
        'case_name': '',
        'visual_assumption': (
            'Geometr\u00eda esquem\u00e1tica; di\u00e1metros ampliados. '
            'Flujo ideal 1D, no CFD. '
            + ('La secci\u00f3n 2 es la garganta; el difusor posterior es ilustrativo. '
               if venturi else '')
            + 'La longitud indicada solo define el tiempo de los trazadores.'
        ),
    })
    return payload


def station_row(payload: dict[str, Any], index: int) -> dict[str, float]:
    return {k: float(payload[k][index]) for k in (
        's', 'x_m', 'z_m', 'diameter_m', 'area_m2', 'velocity_ms',
        'pressure_Pa', 'pressure_head_m', 'velocity_head_m', 'hgl_m', 'egl_m')}


def profile_csv(payload: dict[str, Any]) -> str:
    import csv
    import io
    keys = ['s', 'x_m', 'z_m', 'diameter_m', 'area_m2', 'velocity_ms',
            'pressure_Pa', 'pressure_head_m', 'velocity_head_m', 'hgl_m', 'egl_m']
    stream = io.StringIO(newline='')
    writer = csv.writer(stream)
    writer.writerow(keys)
    writer.writerows(zip(*(payload[k] for k in keys)))
    return stream.getvalue()
