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


def generate_synthetic(rpm: float, fs: float, duration: float, a1: float, a2: float, a3: float, a4: float=0.0,
                       noise_rms: float=0.0, hf_hz: float=0.0, hf_amp: float=0.0, seed: int=26):
    if fs <= 0 or duration <= 0:
        raise ValueError('fs y duración deben ser positivos.')
    n = max(32, int(round(fs * duration)))
    t = np.arange(n) / fs
    fr = max(rpm, 0.0) / 60.0
    s = np.zeros_like(t)
    for order, amp, phase in [(1,a1,0.0),(2,a2,0.43),(3,a3,0.91),(4,a4,1.31)]:
        if fr > 0 and amp != 0:
            s += amp * np.sin(2*np.pi*(order*fr)*t + phase)
    if hf_hz > 0 and hf_amp != 0:
        s += hf_amp * np.sin(2*np.pi*hf_hz*t + 0.27)
    if noise_rms > 0:
        rng = np.random.default_rng(seed)
        s += rng.normal(0.0, noise_rms, size=n)
    return t, s


def generate_runup(rpm_start: float, rpm_end: float, fs: float, duration: float,
                   a1: float=1.0, a2: float=0.25, a3: float=0.10,
                   resonance_rpm: float=1800.0, zeta_demo: float=0.12,
                   resonance_gain: float=1.0, noise_rms: float=0.02, seed: int=26):
    if fs <= 0 or duration <= 0:
        raise ValueError('fs y duración deben ser positivos.')
    n = max(256, int(round(fs*duration)))
    t = np.arange(n)/fs
    rpm = np.linspace(max(0.0,rpm_start), max(0.0,rpm_end), n)
    fr = rpm/60.0
    theta = 2*np.pi*np.cumsum(fr)/fs
    rpm_ref = max(resonance_rpm, 1e-9)
    r = rpm/rpm_ref
    den = np.sqrt(np.maximum((1-r*r)**2 + (2*zeta_demo*r)**2, 1e-12))
    H = 1/den
    H = 1 + resonance_gain * H / max(np.nanmax(H), 1e-12)
    s = (a1*H)*np.sin(theta) + a2*np.sin(2*theta+0.38) + a3*np.sin(3*theta+0.86)
    if noise_rms > 0:
        rng = np.random.default_rng(seed)
        s += rng.normal(0.0, noise_rms, size=n)
    return t, s, rpm, theta


def window_values(name: str, n: int):
    if name == 'Hann': return np.hanning(n)
    if name == 'Hamming': return np.hamming(n)
    return np.ones(n)


def spectrum(t, signal, window='Hann'):
    t = np.asarray(t, dtype=float); x = np.asarray(signal, dtype=float)
    if len(t) != len(x) or len(x) < 8:
        raise ValueError('La señal requiere al menos 8 muestras válidas.')
    dt = np.median(np.diff(t))
    if not np.isfinite(dt) or dt <= 0:
        raise ValueError('El vector de tiempo debe ser estrictamente creciente.')
    fs = 1/dt
    x = x - np.mean(x)
    w = window_values(window, len(x))
    X = np.fft.rfft(x*w)
    f = np.fft.rfftfreq(len(x), dt)
    scale = 2.0/max(np.sum(w),1e-12)
    amp = np.abs(X)*scale
    if len(amp): amp[0] *= .5
    if len(x)%2 == 0 and len(amp)>1: amp[-1] *= .5
    return f, amp, fs


def convert_motion_signal(t, signal, source_kind: str, target_kind: str, integration_cutoff_hz: float=1.0):
    """Convert displacement/velocity/acceleration through frequency-domain differentiation/integration.
    Source/target kinds: 'disp_um', 'vel_mms', 'acc_ms2', 'dimensionless'.
    """
    x = np.asarray(signal, dtype=float)
    if source_kind == target_kind or source_kind == 'dimensionless' or target_kind == 'dimensionless':
        return x.copy()
    tt = np.asarray(t, dtype=float)
    dt = np.median(np.diff(tt))
    if dt <= 0 or len(x) < 8:
        return x.copy()
    # source -> SI base
    if source_kind == 'disp_um': si = x*1e-6; power = 0
    elif source_kind == 'vel_mms': si = x*1e-3; power = 1
    elif source_kind == 'acc_ms2': si = x; power = 2
    else: return x.copy()
    target_power = {'disp_um':0,'vel_mms':1,'acc_ms2':2}[target_kind]
    X = np.fft.rfft(si - np.mean(si))
    f = np.fft.rfftfreq(len(si), dt)
    jw = 1j*2*np.pi*f
    delta = target_power - power
    Y = X.astype(complex)
    if delta > 0:
        Y = Y * (jw**delta)
    elif delta < 0:
        mask = f >= max(float(integration_cutoff_hz), 1e-9)
        out = np.zeros_like(Y)
        out[mask] = Y[mask] / (jw[mask]**(-delta))
        Y = out
    y_si = np.fft.irfft(Y, n=len(si))
    if target_kind == 'disp_um': return y_si*1e6
    if target_kind == 'vel_mms': return y_si*1e3
    return y_si


def top_peaks(f, amp, n=8, min_hz=0.01, max_hz=None):
    f=np.asarray(f); amp=np.asarray(amp)
    if len(f)<3: return []
    if max_hz is None: max_hz=float(np.nanmax(f))
    candidates=[]
    for i in range(1,len(amp)-1):
        if min_hz <= f[i] <= max_hz and amp[i] >= amp[i-1] and amp[i] > amp[i+1]:
            candidates.append((float(amp[i]),float(f[i])))
    candidates.sort(reverse=True)
    return [(hz,a) for a,hz in candidates[:n]]


def metrics(t, signal, rpm: float|None=None, window='Hann'):
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


def spectrogram_segments(t, signal, window='Hann', segment_seconds=0.5, overlap=0.5):
    t=np.asarray(t,float); x=np.asarray(signal,float)
    dt=np.median(np.diff(t)); fs=1/dt
    nseg=max(64,int(round(segment_seconds*fs)))
    nseg=min(nseg,len(x))
    step=max(1,int(round(nseg*(1-overlap))))
    rows=[]; centers=[]; freq=None
    for start in range(0,max(1,len(x)-nseg+1),step):
        end=start+nseg
        if end>len(x): break
        tt=t[start:end]; xx=x[start:end]
        ff,aa,_=spectrum(tt,xx,window)
        freq=ff; rows.append(aa); centers.append(float(np.mean(tt)))
    if not rows:
        ff,aa,_=spectrum(t,x,window); return ff,np.array([aa]),np.array([float(np.mean(t))])
    return freq,np.asarray(rows),np.asarray(centers)


def order_track_runup(t, signal, rpm_t, theta, orders=(1,2,3), segment_seconds=0.4, overlap=0.5):
    t=np.asarray(t,float); x=np.asarray(signal,float); rpm_t=np.asarray(rpm_t,float); theta=np.asarray(theta,float)
    dt=np.median(np.diff(t)); fs=1/dt
    nseg=max(64,int(round(segment_seconds*fs))); nseg=min(nseg,len(x)); step=max(1,int(round(nseg*(1-overlap))))
    rows=[]
    win=np.hanning(nseg)
    norm=max(np.sum(win),1e-12)
    for start in range(0,max(1,len(x)-nseg+1),step):
        end=start+nseg
        if end>len(x): break
        xs=x[start:end]-np.mean(x[start:end]); th=theta[start:end]; ww=win
        rec={'rpm':float(np.mean(rpm_t[start:end])),'time':float(np.mean(t[start:end]))}
        for order in orders:
            c=(2.0/norm)*np.sum(xs*ww*np.exp(-1j*order*th))
            rec[f'amp_{order}x']=float(abs(c)); rec[f'phase_{order}x']=float(np.degrees(np.angle(c)))
        rows.append(rec)
    return rows
