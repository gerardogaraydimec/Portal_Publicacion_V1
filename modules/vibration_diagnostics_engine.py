from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

@dataclass(frozen=True)
class SignalMetrics:
    rms: float
    peak: float
    p2p: float
    crest: float
    mean: float
    dominant_hz: float
    dominant_order: float | None


def generate_synthetic(rpm: float, fs: float, duration: float, a1: float, a2: float, a3: float, a4: float=0.0, noise_rms: float=0.0, hf_hz: float=0.0, hf_amp: float=0.0, seed: int=26):
    if fs<=0 or duration<=0: raise ValueError('fs y duración deben ser positivos.')
    n=max(32,int(round(fs*duration)))
    t=np.arange(n)/fs
    fr=max(rpm,0.0)/60.0
    s=np.zeros_like(t)
    for order,amp,phase in [(1,a1,0.0),(2,a2,0.43),(3,a3,0.91),(4,a4,1.31)]:
        if fr>0 and amp!=0: s += amp*np.sin(2*np.pi*(order*fr)*t+phase)
    if hf_hz>0 and hf_amp!=0: s += hf_amp*np.sin(2*np.pi*hf_hz*t+0.27)
    if noise_rms>0:
        rng=np.random.default_rng(seed); s += rng.normal(0.0,noise_rms,size=n)
    return t,s


def window_values(name: str,n: int):
    if name=='Hann': return np.hanning(n)
    if name=='Hamming': return np.hamming(n)
    return np.ones(n)


def spectrum(t,signal,window='Hann'):
    t=np.asarray(t,dtype=float); x=np.asarray(signal,dtype=float)
    if len(t)!=len(x) or len(x)<8: raise ValueError('La señal requiere al menos 8 muestras válidas.')
    dt=np.median(np.diff(t))
    if not np.isfinite(dt) or dt<=0: raise ValueError('El vector de tiempo debe ser estrictamente creciente.')
    fs=1/dt
    x=x-np.mean(x)
    w=window_values(window,len(x))
    X=np.fft.rfft(x*w)
    f=np.fft.rfftfreq(len(x),dt)
    scale=2.0/max(np.sum(w),1e-12)
    amp=np.abs(X)*scale
    if len(amp): amp[0]*=.5
    if len(x)%2==0 and len(amp)>1: amp[-1]*=.5
    return f,amp,fs


def top_peaks(f,amp,n=8,min_hz=0.01):
    f=np.asarray(f); amp=np.asarray(amp)
    if len(f)<3: return []
    candidates=[]
    for i in range(1,len(amp)-1):
        if f[i]>=min_hz and amp[i]>=amp[i-1] and amp[i]>amp[i+1]:
            candidates.append((float(amp[i]),float(f[i])))
    candidates.sort(reverse=True)
    return [(hz,a) for a,hz in candidates[:n]]


def metrics(t,signal,rpm: float|None=None,window='Hann'):
    x=np.asarray(signal,dtype=float)
    mean=float(np.mean(x)); xc=x-mean
    rms=float(np.sqrt(np.mean(xc*xc))); peak=float(np.max(np.abs(xc))); p2p=float(np.ptp(xc)); crest=(peak/rms if rms>1e-15 else 0.0)
    f,a,_=spectrum(t,x,window)
    idx=1+int(np.argmax(a[1:])) if len(a)>1 else 0
    dom=float(f[idx]) if len(f) else 0.0
    order=(dom/(rpm/60.0) if rpm and rpm>0 else None)
    return SignalMetrics(rms,peak,p2p,crest,mean,dom,order)


def analytic_envelope(signal):
    x=np.asarray(signal,dtype=float)
    n=len(x); X=np.fft.fft(x)
    h=np.zeros(n)
    if n%2==0:
        h[0]=h[n//2]=1; h[1:n//2]=2
    else:
        h[0]=1; h[1:(n+1)//2]=2
    z=np.fft.ifft(X*h)
    return np.abs(z)
