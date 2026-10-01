from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

G = 9.80665

try:
    from .reynolds_engine import friction_factor as _portal_friction_factor
except Exception:
    _portal_friction_factor = None


@dataclass(frozen=True)
class FluidData:
    name: str
    rho: float
    mu: float
    vapor_pressure_pa: float


@dataclass(frozen=True)
class PumpCurve:
    h0_ref_m: float
    q_ref_m3s: float
    h_ref_m: float
    n_ref_rpm: float
    n_rpm: float
    arrangement: str
    count: int
    efficiency: float


@dataclass(frozen=True)
class SystemData:
    static_head_m: float
    ls_m: float
    ds_m: float
    ld_m: float
    dd_m: float
    roughness_m: float
    k_suction: float
    k_discharge_other: float
    valve_opening: float
    valve_k_full: float
    suction_surface_minus_pump_m: float
    suction_pressure_pa: float


@dataclass(frozen=True)
class HydraulicState:
    q_m3s: float
    vs_ms: float
    vd_ms: float
    re_s: float
    re_d: float
    f_s: float
    f_d: float
    suction_loss_m: float
    discharge_major_loss_m: float
    discharge_minor_loss_m: float
    valve_loss_m: float
    total_loss_m: float
    system_head_m: float
    valve_k: float


@dataclass(frozen=True)
class OperatingPoint:
    exists: bool
    q_m3s: float | None
    pump_head_m: float | None
    state: HydraulicState | None
    hydraulic_power_w: float | None
    shaft_power_w: float | None
    npsha_m: float | None
    message: str


FLUID_PRESETS = {
    'Agua · 20 °C': FluidData('Agua · 20 °C', 998.2, 1.002e-3, 2.34e3),
    'Agua · 60 °C': FluidData('Agua · 60 °C', 983.2, 4.66e-4, 19.95e3),
}


def _friction_factor(re: float, rel_roughness: float) -> float:
    if re <= 0:
        return 0.0
    if _portal_friction_factor is not None:
        return float(_portal_friction_factor(re, rel_roughness)[0])
    if re < 2300:
        return 64.0 / re
    # Haaland fallback, Darcy factor.
    x = -1.8 * math.log10((max(rel_roughness, 0.0) / 3.7) ** 1.11 + 6.9 / re)
    return 1.0 / max(x * x, 1e-12)


def valve_k(opening: float, k_full: float) -> float:
    """Didactic valve model. opening is 0..1. Not a manufacturer characteristic."""
    a = max(0.05, min(1.0, float(opening)))
    return max(float(k_full), 0.0) / (a * a)


def _pump_a(curve: PumpCurve) -> float:
    if curve.q_ref_m3s <= 0:
        raise ValueError('Q de referencia debe ser mayor que cero.')
    if curve.h0_ref_m <= curve.h_ref_m:
        raise ValueError('La altura a caudal cero H₀ debe ser mayor que H en el punto de referencia.')
    return (curve.h0_ref_m - curve.h_ref_m) / curve.q_ref_m3s**2


def pump_head_single(q_m3s: float | np.ndarray, curve: PumpCurve) -> float | np.ndarray:
    a = _pump_a(curve)
    s = curve.n_rpm / curve.n_ref_rpm
    q = np.asarray(q_m3s, dtype=float)
    h = s * s * curve.h0_ref_m - a * q * q
    h = np.maximum(h, 0.0)
    return float(h) if h.ndim == 0 else h


def pump_head(q_total_m3s: float | np.ndarray, curve: PumpCurve) -> float | np.ndarray:
    q = np.asarray(q_total_m3s, dtype=float)
    n = max(1, int(curve.count))
    if curve.arrangement == 'Serie':
        h = n * np.asarray(pump_head_single(q, curve), dtype=float)
    elif curve.arrangement == 'Paralelo':
        h = np.asarray(pump_head_single(q / n, curve), dtype=float)
    else:
        h = np.asarray(pump_head_single(q, curve), dtype=float)
    return float(h) if h.ndim == 0 else h


def pump_zero_head_flow(curve: PumpCurve) -> float:
    a = _pump_a(curve)
    s = curve.n_rpm / curve.n_ref_rpm
    q_single = math.sqrt(max(s*s*curve.h0_ref_m/a, 0.0))
    if curve.arrangement == 'Paralelo':
        return q_single * max(1, int(curve.count))
    return q_single


def hydraulic_state(q_m3s: float, fluid: FluidData, sys: SystemData) -> HydraulicState:
    q = max(float(q_m3s), 0.0)
    if min(sys.ls_m, sys.ld_m, sys.ds_m, sys.dd_m) <= 0:
        raise ValueError('Longitudes y diámetros deben ser mayores que cero.')
    As = math.pi * sys.ds_m**2 / 4.0
    Ad = math.pi * sys.dd_m**2 / 4.0
    vs = q / As
    vd = q / Ad
    re_s = fluid.rho * vs * sys.ds_m / fluid.mu if q > 0 else 0.0
    re_d = fluid.rho * vd * sys.dd_m / fluid.mu if q > 0 else 0.0
    fs = _friction_factor(re_s, sys.roughness_m / sys.ds_m) if q > 0 else 0.0
    fd = _friction_factor(re_d, sys.roughness_m / sys.dd_m) if q > 0 else 0.0
    vhs = vs**2 / (2*G)
    vhd = vd**2 / (2*G)
    kv = valve_k(sys.valve_opening, sys.valve_k_full)
    hs = (fs * sys.ls_m / sys.ds_m + sys.k_suction) * vhs
    hd_major = fd * sys.ld_m / sys.dd_m * vhd
    hd_other = sys.k_discharge_other * vhd
    hv = kv * vhd
    total = hs + hd_major + hd_other + hv
    return HydraulicState(
        q_m3s=q, vs_ms=vs, vd_ms=vd, re_s=re_s, re_d=re_d, f_s=fs, f_d=fd,
        suction_loss_m=hs, discharge_major_loss_m=hd_major,
        discharge_minor_loss_m=hd_other, valve_loss_m=hv,
        total_loss_m=total, system_head_m=sys.static_head_m + total, valve_k=kv,
    )


def system_head(q_m3s: float | np.ndarray, fluid: FluidData, sys: SystemData):
    qarr = np.asarray(q_m3s, dtype=float)
    if qarr.ndim == 0:
        return hydraulic_state(float(qarr), fluid, sys).system_head_m
    return np.array([hydraulic_state(float(q), fluid, sys).system_head_m for q in qarr])


def find_operating_point(curve: PumpCurve, fluid: FluidData, sys: SystemData) -> OperatingPoint:
    if curve.n_ref_rpm <= 0 or curve.n_rpm <= 0:
        raise ValueError('Las rpm deben ser mayores que cero.')
    if not (0 < curve.efficiency <= 1):
        raise ValueError('La eficiencia debe estar entre 0 y 1.')
    qz = max(pump_zero_head_flow(curve), curve.q_ref_m3s, 1e-6)
    qmax = qz * 1.7
    def diff(q: float) -> float:
        return float(pump_head(q, curve)) - hydraulic_state(q, fluid, sys).system_head_m
    d0 = diff(0.0)
    if d0 < 0:
        return OperatingPoint(False, None, None, None, None, None, None,
            'La bomba no alcanza la altura estática del sistema a caudal cero.')
    qs = np.linspace(0.0, qmax, 900)
    ds = np.array([diff(float(q)) for q in qs])
    idx = np.where(np.signbit(ds[:-1]) != np.signbit(ds[1:]))[0]
    if len(idx) == 0:
        j = int(np.nanargmin(np.abs(ds)))
        if abs(ds[j]) < 1e-4:
            root = float(qs[j])
        else:
            return OperatingPoint(False, None, None, None, None, None, None,
                'No se encontró una intersección física dentro del rango de la curva de bomba.')
    else:
        lo, hi = float(qs[idx[0]]), float(qs[idx[0] + 1])
        flo = diff(lo)
        for _ in range(70):
            mid = 0.5*(lo+hi)
            fm = diff(mid)
            if abs(fm) < 1e-10:
                lo = hi = mid
                break
            if flo * fm <= 0:
                hi = mid
            else:
                lo, flo = mid, fm
        root = 0.5*(lo+hi)
    st = hydraulic_state(root, fluid, sys)
    hp = float(pump_head(root, curve))
    ph = fluid.rho * G * root * hp
    ps = ph / curve.efficiency
    npsha = (sys.suction_pressure_pa - fluid.vapor_pressure_pa)/(fluid.rho*G) + sys.suction_surface_minus_pump_m - st.suction_loss_m
    return OperatingPoint(True, root, hp, st, ph, ps, npsha, 'Punto de operación encontrado.')


def curve_data(curve: PumpCurve, fluid: FluidData, sys: SystemData, n: int = 260):
    qmax = max(pump_zero_head_flow(curve)*1.20, curve.q_ref_m3s*1.4, 1e-5)
    q = np.linspace(0, qmax, n)
    hp = np.asarray(pump_head(q, curve), dtype=float)
    hs = system_head(q, fluid, sys)
    return q, hp, hs


def energy_profile(op: OperatingPoint, curve: PumpCurve, sys: SystemData, points: int = 180):
    if not op.exists or op.state is None:
        return np.array([]), np.array([]), np.array([]), np.array([])
    st = op.state
    hp = float(op.pump_head_m)
    vh_s = st.vs_ms**2/(2*G)
    vh_d = st.vd_ms**2/(2*G)
    x = np.linspace(0, 1, points)
    egl = np.zeros_like(x)
    hgl = np.zeros_like(x)
    for i,xx in enumerate(x):
        if xx <= .25:
            # suction reservoir + suction line loss
            frac = xx/.25
            egl[i] = -st.suction_loss_m*frac
            hgl[i] = egl[i] if xx < .04 else egl[i]-vh_s
        elif xx <= .33:
            # pump jump
            frac = (xx-.25)/.08
            egl[i] = -st.suction_loss_m + hp*frac
            hgl[i] = egl[i]-vh_d
        elif xx <= .90:
            frac=(xx-.33)/.57
            dloss = st.discharge_major_loss_m*frac + st.discharge_minor_loss_m*frac
            # Place valve at 72% of route as a loss step.
            valve = st.valve_loss_m if xx >= .72 else 0.0
            egl[i] = -st.suction_loss_m + hp - dloss - valve
            hgl[i] = egl[i]-vh_d
        else:
            frac=(xx-.90)/.10
            start = -st.suction_loss_m + hp - st.discharge_major_loss_m - st.discharge_minor_loss_m - st.valve_loss_m
            egl[i] = start*(1-frac) + sys.static_head_m*frac
            hgl[i] = egl[i]
    return x, egl, hgl, np.full_like(x, sys.static_head_m)


def affinity_summary(curve: PumpCurve) -> dict[str, float]:
    s = curve.n_rpm / curve.n_ref_rpm
    return {'speed_ratio': s, 'q_ratio': s, 'head_ratio': s*s, 'power_ratio': s**3}


def sensitivity(curve: PumpCurve, fluid: FluidData, sys: SystemData, parameter: str, values: np.ndarray):
    qop=[]; hop=[]; power=[]
    for val in values:
        if parameter == 'rpm':
            c = PumpCurve(curve.h0_ref_m,curve.q_ref_m3s,curve.h_ref_m,curve.n_ref_rpm,float(val),curve.arrangement,curve.count,curve.efficiency)
            s = sys
        elif parameter == 'diameter':
            c=curve
            s=SystemData(sys.static_head_m,sys.ls_m,sys.ds_m,sys.ld_m,float(val),sys.roughness_m,sys.k_suction,sys.k_discharge_other,sys.valve_opening,sys.valve_k_full,sys.suction_surface_minus_pump_m,sys.suction_pressure_pa)
        elif parameter == 'valve':
            c=curve
            s=SystemData(sys.static_head_m,sys.ls_m,sys.ds_m,sys.ld_m,sys.dd_m,sys.roughness_m,sys.k_suction,sys.k_discharge_other,float(val),sys.valve_k_full,sys.suction_surface_minus_pump_m,sys.suction_pressure_pa)
        else:
            raise ValueError(parameter)
        op=find_operating_point(c,fluid,s)
        qop.append(np.nan if not op.exists else op.q_m3s)
        hop.append(np.nan if not op.exists else op.pump_head_m)
        power.append(np.nan if not op.exists else op.shaft_power_w)
    return np.array(qop),np.array(hop),np.array(power)
