import numpy as np


def _fmt_complex(z: complex) -> str:
    z = complex(z)
    if abs(z.imag) < 1e-10:
        return f"{z.real:.6g}"
    return f"{z.real:.6g}{z.imag:+.6g}j"


def calcular_respuesta(m, k, c, x0, v0, F0, omega, t):
    """Respuesta de m*x'' + c*x' + k*x = F0*cos(omega*t)."""
    m = float(m); k = float(k); c = float(c)
    x0 = float(x0); v0 = float(v0); F0 = float(F0); omega = float(omega)
    t = np.asarray(t, dtype=float)

    if m <= 0:
        raise ValueError("La masa m debe ser mayor que cero.")
    if k <= 0:
        raise ValueError("La rigidez k debe ser mayor que cero.")
    if c < 0:
        raise ValueError("El amortiguamiento c no puede ser negativo.")
    if F0 < 0:
        raise ValueError("La amplitud F0 no puede ser negativa.")
    if omega < 0:
        raise ValueError("La frecuencia angular ω no puede ser negativa.")

    wn = np.sqrt(k / m)
    fn = wn / (2 * np.pi)
    rpm_n = 60 * fn
    ccr = 2 * np.sqrt(k * m)
    zeta = c / ccr
    r = omega / wn if wn > 0 else np.nan
    f_exc = omega / (2 * np.pi)
    rpm_exc = 60 * f_exc
    delta_st = F0 / k

    den_sq = (k - m * omega**2) ** 2 + (c * omega) ** 2
    exact_undamped_resonance = (c == 0.0) and np.isclose(omega, wn, rtol=1e-10, atol=1e-12) and F0 > 0

    if exact_undamped_resonance:
        X = np.inf
        phi = np.pi / 2
        M = np.inf
        xp = (F0 / (2 * m * wn)) * t * np.sin(wn * t)
        vp = (F0 / (2 * m * wn)) * (np.sin(wn * t) + wn * t * np.cos(wn * t))
        ap = (F0 / (2 * m)) * (2 * np.cos(wn * t) - wn * t * np.sin(wn * t))
        y0, vh0 = x0, v0
    else:
        den = np.sqrt(den_sq)
        X = F0 / den if den > 0 else 0.0
        phi = np.arctan2(c * omega, k - m * omega**2) if F0 > 0 else 0.0
        M = (X / delta_st) if delta_st > 0 else 0.0
        xp = X * np.cos(omega * t - phi)
        vp = -X * omega * np.sin(omega * t - phi)
        ap = -X * omega**2 * np.cos(omega * t - phi)
        xp0 = X * np.cos(phi)
        vp0 = X * omega * np.sin(phi)
        y0, vh0 = x0 - xp0, v0 - vp0

    tol = 1e-8
    if zeta < 1 - tol:
        wd = wn * np.sqrt(max(0.0, 1 - zeta**2))
        A = y0
        B = (vh0 + zeta * wn * A) / wd
        e = np.exp(-zeta * wn * t)
        cos = np.cos(wd * t); sin = np.sin(wd * t)
        yh = e * (A * cos + B * sin)
        vh = e * ((-zeta * wn * A + B * wd) * cos + (-zeta * wn * B - A * wd) * sin)
        ah = -(c / m) * vh - (k / m) * yh
        s1 = complex(-zeta * wn, wd)
        s2 = complex(-zeta * wn, -wd)
        C1 = complex(A / 2, -B / 2)
        C2 = complex(A / 2, B / 2)
        regime = "NO AMORTIGUADO" if c == 0 else "SUBAMORTIGUADO"
        wd_out = wd
    elif zeta > 1 + tol:
        root = np.sqrt(zeta**2 - 1)
        s1 = -wn * (zeta - root)
        s2 = -wn * (zeta + root)
        C1 = (vh0 - s2 * y0) / (s1 - s2)
        C2 = y0 - C1
        e1 = np.exp(s1 * t); e2 = np.exp(s2 * t)
        yh = C1 * e1 + C2 * e2
        vh = C1 * s1 * e1 + C2 * s2 * e2
        ah = C1 * s1**2 * e1 + C2 * s2**2 * e2
        regime = "SOBREAMORTIGUADO"
        wd_out = 0.0
    else:
        s1 = s2 = -wn
        A = y0
        B = vh0 + wn * A
        e = np.exp(-wn * t)
        yh = (A + B * t) * e
        vh = (B - wn * (A + B * t)) * e
        ah = -(c / m) * vh - (k / m) * yh
        C1, C2 = A, B
        regime = "AMORTIGUACIÓN CRÍTICA"
        wd_out = 0.0

    x = yh + xp
    v = vh + vp
    a = ah + ap

    Ec = 0.5 * m * v**2
    Ep = 0.5 * k * x**2
    Em = Ec + Ep
    force = F0 * np.cos(omega * t)

    if np.isfinite(X):
        Fk_amp = k * X
        Fc_amp = c * omega * X
        Fi_amp = m * omega**2 * X
        Ft_amp = np.sqrt(Fk_amp**2 + Fc_amp**2)
        TR = Ft_amp / F0 if F0 > 0 else 0.0
    else:
        Fk_amp = Fc_amp = Fi_amp = Ft_amp = TR = np.inf

    return {
        "t": t, "x": x, "v": v, "a": a, "xp": xp, "force": force,
        "Ec": Ec, "Ep": Ep, "Em": Em,
        "wn": wn, "fn": fn, "rpm_n": rpm_n, "ccr": ccr, "zeta": zeta,
        "wd": wd_out, "r": r, "f_exc": f_exc, "rpm_exc": rpm_exc,
        "X": X, "phi": phi, "M": M, "delta_st": delta_st,
        "s1": s1, "s2": s2, "C1": C1, "C2": C2, "regime": regime,
        "Fk_amp": Fk_amp, "Fc_amp": Fc_amp, "Fi_amp": Fi_amp,
        "Ft_amp": Ft_amp, "TR": TR,
        "exact_undamped_resonance": exact_undamped_resonance,
    }


def curva_magnificacion(zeta, r_max=4.0, n=1600):
    r = np.linspace(0, r_max, n)
    den = np.sqrt((1 - r**2)**2 + (2 * zeta * r)**2)
    with np.errstate(divide="ignore", invalid="ignore"):
        M = 1 / den
    M[~np.isfinite(M)] = np.nan
    return r, M


def puntos_adaptativos(wn, omega, tmax, objetivo_por_ciclo=60, minimo=1600, maximo=30000):
    w_ref = max(float(wn), float(omega), 1e-9)
    ciclos = tmax * w_ref / (2 * np.pi)
    n_req = int(np.ceil(ciclos * objetivo_por_ciclo)) + 1
    n = min(max(minimo, n_req), maximo)
    limitado = n_req > maximo
    return n, limitado, n_req


def formato(z):
    return _fmt_complex(z)
