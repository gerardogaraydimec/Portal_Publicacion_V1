from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

@dataclass(frozen=True)
class VibrationResult:
    m: float
    k: float
    c: float
    x0: float
    v0: float
    wn: float
    fn: float
    period: float
    ccrit: float
    zeta: float
    wd: float | None
    fd: float | None
    regime: str
    log_decrement: float | None
    tau_decay: float | None


def solve_free_vibration(m: float, k: float, c: float, x0: float, v0: float) -> VibrationResult:
    if m <= 0 or k <= 0:
        raise ValueError('m y k deben ser mayores que cero.')
    if c < 0:
        raise ValueError('c no puede ser negativo.')
    wn = math.sqrt(k/m)
    fn = wn/(2*math.pi)
    period = 1/fn
    ccrit = 2*math.sqrt(k*m)
    zeta = c/ccrit
    tol = 1e-7
    if zeta < 1-tol:
        regime = 'Subamortiguado' if zeta > tol else 'No amortiguado'
        wd = wn*math.sqrt(max(0.0, 1-zeta*zeta))
        fd = wd/(2*math.pi)
        logdec = None if zeta <= tol else 2*math.pi*zeta/math.sqrt(1-zeta*zeta)
        tau = None if zeta <= tol else 1/(zeta*wn)
    elif abs(zeta-1) <= tol:
        regime = 'Críticamente amortiguado'
        wd = None; fd = None; logdec = None; tau = 1/wn
    else:
        regime = 'Sobreamortiguado'
        wd = None; fd = None; logdec = None
        rslow = -wn*(zeta-math.sqrt(zeta*zeta-1))
        tau = None if abs(rslow) < 1e-12 else -1/rslow
    return VibrationResult(m,k,c,x0,v0,wn,fn,period,ccrit,zeta,wd,fd,regime,logdec,tau)


def free_response(res: VibrationResult, t: np.ndarray):
    m,k,c,x0,v0 = res.m,res.k,res.c,res.x0,res.v0
    wn,z = res.wn,res.zeta
    t=np.asarray(t,dtype=float)
    tol=1e-7
    if z < 1-tol:
        wd=wn*math.sqrt(max(0.0,1-z*z))
        A=x0
        B=(v0+z*wn*x0)/wd if wd>0 else 0.0
        e=np.exp(-z*wn*t)
        co=np.cos(wd*t); si=np.sin(wd*t)
        x=e*(A*co+B*si)
        v=e*((-z*wn)*(A*co+B*si)+(-A*wd*si+B*wd*co))
    elif abs(z-1)<=tol:
        A=x0
        B=v0+wn*x0
        e=np.exp(-wn*t)
        x=(A+B*t)*e
        v=(B-wn*(A+B*t))*e
    else:
        s=math.sqrt(z*z-1)
        r1=-wn*(z-s); r2=-wn*(z+s)
        den=r1-r2
        C1=(v0-r2*x0)/den
        C2=x0-C1
        x=C1*np.exp(r1*t)+C2*np.exp(r2*t)
        v=C1*r1*np.exp(r1*t)+C2*r2*np.exp(r2*t)
    a=-(c/m)*v-(k/m)*x
    return x,v,a


def energies(res: VibrationResult, x: np.ndarray, v: np.ndarray):
    Ek=0.5*res.m*np.asarray(v)**2
    Ep=0.5*res.k*np.asarray(x)**2
    Et=Ek+Ep
    return Ek,Ep,Et
