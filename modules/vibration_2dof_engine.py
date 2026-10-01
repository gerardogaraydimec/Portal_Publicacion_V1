from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

@dataclass(frozen=True)
class Modal2DOF:
    M: np.ndarray
    K: np.ndarray
    C: np.ndarray
    wn: np.ndarray
    fn: np.ndarray
    modes: np.ndarray
    mass_ratio: float
    absorber_fn: float
    primary_fn: float
    antiresonance_hz: float

@dataclass(frozen=True)
class Harmonic2DOF:
    f_exc: float
    w: float
    F0: float
    X: np.ndarray
    amp: np.ndarray
    phase_deg: np.ndarray
    residual: float


def matrices(m1: float, m2: float, k1: float, k2: float, c1: float, c2: float):
    vals=(m1,m2,k1,k2)
    if min(vals) <= 0:
        raise ValueError('m1, m2, k1 y k2 deben ser mayores que cero.')
    if min(c1,c2) < 0:
        raise ValueError('c1 y c2 deben ser no negativos.')
    M=np.array([[m1,0.0],[0.0,m2]],dtype=float)
    K=np.array([[k1+k2,-k2],[-k2,k2]],dtype=float)
    C=np.array([[c1+c2,-c2],[-c2,c2]],dtype=float)
    return M,K,C


def solve_modal(m1: float,m2: float,k1: float,k2: float,c1: float=0.0,c2: float=0.0)->Modal2DOF:
    M,K,C=matrices(m1,m2,k1,k2,c1,c2)
    A=np.linalg.solve(M,K)
    eigvals,eigvecs=np.linalg.eig(A)
    idx=np.argsort(np.real(eigvals))
    eigvals=np.real(eigvals[idx]); eigvecs=np.real(eigvecs[:,idx])
    eigvals=np.maximum(eigvals,0.0)
    wn=np.sqrt(eigvals); fn=wn/(2*np.pi)
    modes=eigvecs.copy()
    for j in range(2):
        v=modes[:,j]
        scale=np.max(np.abs(v)) or 1.0
        v=v/scale
        if v[0] < 0: v=-v
        modes[:,j]=v
    mu=m2/m1
    absorber_fn=math.sqrt(k2/m2)/(2*math.pi)
    primary_fn=math.sqrt(k1/m1)/(2*math.pi)
    anti=absorber_fn
    return Modal2DOF(M,K,C,wn,fn,modes,mu,absorber_fn,primary_fn,anti)


def harmonic_response(modal: Modal2DOF, f_exc: float, F0: float, force_on: int=0)->Harmonic2DOF:
    if f_exc < 0 or F0 < 0: raise ValueError('f y F0 deben ser no negativos.')
    w=2*np.pi*f_exc
    Z=modal.K - (w*w)*modal.M + 1j*w*modal.C
    F=np.zeros(2,dtype=complex); F[force_on]=F0
    try:
        X=np.linalg.solve(Z,F)
    except np.linalg.LinAlgError:
        X=np.array([complex(np.inf),complex(np.inf)])
    amp=np.abs(X)
    phase=np.degrees(np.angle(X))
    if np.all(np.isfinite(X)):
        residual=float(np.linalg.norm(Z@X-F))
    else:
        residual=math.inf
    return Harmonic2DOF(f_exc,w,F0,X,amp,phase,residual)


def frequency_response(modal: Modal2DOF, F0: float=1.0, fmax_factor: float=2.2, n: int=1000):
    fmax=max(modal.fn[-1]*fmax_factor,modal.primary_fn*2.5,1e-3)
    f=np.linspace(0.0,fmax,n)
    X1=np.empty(n,dtype=complex); X2=np.empty(n,dtype=complex)
    F=np.array([F0,0.0],dtype=complex)
    for i,ff in enumerate(f):
        w=2*np.pi*ff
        Z=modal.K - w*w*modal.M + 1j*w*modal.C
        try:
            X=np.linalg.solve(Z,F)
        except np.linalg.LinAlgError:
            X=np.array([np.nan+1j*np.nan,np.nan+1j*np.nan])
        X1[i],X2[i]=X
    return f,X1,X2


def free_modal_response(modal: Modal2DOF, x0, v0, t):
    x0=np.asarray(x0,dtype=float); v0=np.asarray(v0,dtype=float); t=np.asarray(t,dtype=float)
    Phi=modal.modes
    # For the undamped modal visualization, solve initial modal amplitudes directly.
    q0=np.linalg.solve(Phi,x0)
    qd0=np.linalg.solve(Phi,v0)
    x=np.zeros((len(t),2))
    for j,w in enumerate(modal.wn):
        if w<=1e-12:
            q=q0[j]+qd0[j]*t
        else:
            q=q0[j]*np.cos(w*t)+(qd0[j]/w)*np.sin(w*t)
        x += q[:,None]*Phi[:,j][None,:]
    return x


def forced_time_response(h: Harmonic2DOF, t):
    t=np.asarray(t,dtype=float)
    if not np.all(np.isfinite(h.X)):
        return np.full((len(t),2),np.nan)
    e=np.exp(1j*h.w*t)
    return np.real(e[:,None]*h.X[None,:])


def tmd_reference(m1: float,k1: float,mu: float):
    if m1<=0 or k1<=0 or mu<=0: raise ValueError('m1, k1 y μ deben ser positivos.')
    m2=mu*m1
    w1=math.sqrt(k1/m1)
    tuning=1/(1+mu)
    w2=tuning*w1
    k2=m2*w2*w2
    zeta2=math.sqrt(3*mu/(8*(1+mu)**3))
    c2=2*zeta2*math.sqrt(k2*m2)
    return dict(m2=m2,k2=k2,c2=c2,tuning=tuning,zeta2=zeta2,fn2=w2/(2*math.pi))


def sdof_primary_frf(m1: float,k1: float,c1: float,F0: float,f):
    f=np.asarray(f,dtype=float); w=2*np.pi*f
    Z=k1-m1*w*w+1j*c1*w
    return F0/Z
