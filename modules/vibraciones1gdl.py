from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Resultado1GDL:
    t: np.ndarray
    x: np.ndarray
    v: np.ndarray
    a: np.ndarray
    wn: float
    ccr: float
    zeta: float
    regime: str
    s1: complex
    s2: complex
    c1: complex
    c2: complex
    wd: float | None


def _roots(m: float, k: float, c: float) -> tuple[complex, complex]:
    disc = complex(c * c - 4.0 * m * k)
    root = np.lib.scimath.sqrt(disc)
    return ((-c + root) / (2.0 * m), (-c - root) / (2.0 * m))


def calcular_respuesta(
    m: float,
    k: float,
    c: float,
    x0: float,
    v0: float,
    tmax: float,
    n: int | None = None,
    tol: float = 1e-6,
) -> Resultado1GDL:
    """Respuesta libre de un sistema lineal masa-resorte-amortiguador de 1 GDL.

    Ecuación: m*x'' + c*x' + k*x = 0.
    Se emplean expresiones cerradas distintas para cada régimen para evitar
    pérdida de precisión numérica cerca de la amortiguación crítica.
    """
    if m <= 0:
        raise ValueError("La masa m debe ser mayor que cero.")
    if k <= 0:
        raise ValueError("La rigidez k debe ser mayor que cero.")
    if c < 0:
        raise ValueError("El amortiguamiento c no puede ser negativo.")
    if tmax <= 0:
        raise ValueError("tmax debe ser mayor que cero.")

    wn = float(np.sqrt(k / m))

    # Muestreo adaptativo para abarcar desde ejercicios académicos hasta
    # sistemas de mayor frecuencia sin fijar un rango artificial de entrada.
    if n is None:
        cycles = max(wn * float(tmax) / (2.0 * np.pi), 0.0)
        n = int(np.clip(np.ceil(cycles * 80.0) + 1, 1400, 20000))
    t = np.linspace(0.0, float(tmax), int(n))
    ccr = float(2.0 * np.sqrt(k * m))
    zeta = float(c / ccr)
    s1, s2 = _roots(m, k, c)

    if np.isclose(c, 0.0, atol=tol):
        regime = "Sistema no amortiguado"
        wd = wn
        A = float(x0)
        B = float(v0 / wn)
        ct = np.cos(wn * t)
        st = np.sin(wn * t)
        x = A * ct + B * st
        v = -A * wn * st + B * wn * ct
        # Coeficientes de la forma exponencial compleja usada en el programa original.
        c1 = complex((v0 - s2 * x0) / (s1 - s2))
        c2 = complex(x0 - c1)

    elif zeta < 1.0 - tol:
        regime = "Subamortiguado"
        wd = float(wn * np.sqrt(1.0 - zeta * zeta))
        A = float(x0)
        B = float((v0 + zeta * wn * x0) / wd)
        decay = np.exp(-zeta * wn * t)
        ct = np.cos(wd * t)
        st = np.sin(wd * t)
        q = A * ct + B * st
        dq = -A * wd * st + B * wd * ct
        x = decay * q
        v = decay * (dq - zeta * wn * q)
        c1 = complex((v0 - s2 * x0) / (s1 - s2))
        c2 = complex(x0 - c1)

    elif zeta > 1.0 + tol:
        regime = "Sobreamortiguado"
        wd = None
        c1 = complex((v0 - s2 * x0) / (s1 - s2))
        c2 = complex(x0 - c1)
        x_complex = c1 * np.exp(s1 * t) + c2 * np.exp(s2 * t)
        v_complex = c1 * s1 * np.exp(s1 * t) + c2 * s2 * np.exp(s2 * t)
        x = np.real_if_close(x_complex).real
        v = np.real_if_close(v_complex).real

    else:
        regime = "Amortiguación crítica"
        wd = None
        # Raíz doble s=-wn. La solución correcta es (C1 + C2*t)e^(-wn*t).
        s1 = s2 = complex(-wn, 0.0)
        c1 = complex(x0, 0.0)
        c2 = complex(v0 + wn * x0, 0.0)
        decay = np.exp(-wn * t)
        x = (x0 + (v0 + wn * x0) * t) * decay
        v = (v0 - wn * (v0 + wn * x0) * t) * decay

    # Ecuación de movimiento: forma más estable para obtener la aceleración.
    a = -(c / m) * v - (k / m) * x

    return Resultado1GDL(
        t=t,
        x=np.asarray(x, dtype=float),
        v=np.asarray(v, dtype=float),
        a=np.asarray(a, dtype=float),
        wn=wn,
        ccr=ccr,
        zeta=zeta,
        regime=regime,
        s1=complex(s1),
        s2=complex(s2),
        c1=complex(c1),
        c2=complex(c2),
        wd=wd,
    )


def fmt_complex(z: complex, dec: int = 3) -> str:
    z = complex(z)
    if abs(z.imag) < 10 ** (-(dec + 1)):
        return f"{z.real:.{dec}f}"
    sign = "+" if z.imag >= 0 else "−"
    return f"{z.real:.{dec}f} {sign} {abs(z.imag):.{dec}f}j"
