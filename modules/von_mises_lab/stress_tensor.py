from __future__ import annotations
import numpy as np


def stress_tensor(
    sigma_x: float = 0.0,
    sigma_y: float = 0.0,
    sigma_z: float = 0.0,
    tau_xy: float = 0.0,
    tau_yz: float = 0.0,
    tau_zx: float = 0.0,
) -> np.ndarray:
    """Tensor simétrico de Cauchy."""
    return np.array([
        [sigma_x, tau_xy, tau_zx],
        [tau_xy, sigma_y, tau_yz],
        [tau_zx, tau_yz, sigma_z],
    ], dtype=float)


def validate_tensor(tensor: np.ndarray, atol: float = 1e-10) -> np.ndarray:
    a = np.asarray(tensor, dtype=float)
    if a.shape != (3, 3):
        raise ValueError("El tensor de esfuerzos debe ser 3×3.")
    if not np.all(np.isfinite(a)):
        raise ValueError("El tensor contiene valores no finitos.")
    if not np.allclose(a, a.T, atol=atol):
        raise ValueError("El tensor de esfuerzos debe ser simétrico.")
    return a


def principal_stresses(tensor: np.ndarray) -> np.ndarray:
    """Esfuerzos principales ordenados σ1 ≥ σ2 ≥ σ3."""
    vals = np.linalg.eigvalsh(validate_tensor(tensor))
    return np.sort(vals)[::-1]


def mean_stress(tensor: np.ndarray) -> float:
    return float(np.trace(validate_tensor(tensor)) / 3.0)


def hydrostatic_tensor(tensor: np.ndarray) -> np.ndarray:
    return np.eye(3) * mean_stress(tensor)


def deviatoric_tensor(tensor: np.ndarray) -> np.ndarray:
    a = validate_tensor(tensor)
    return a - hydrostatic_tensor(a)


def invariants(tensor: np.ndarray) -> dict[str, float]:
    a = validate_tensor(tensor)
    s = deviatoric_tensor(a)
    return {
        "I1": float(np.trace(a)),
        "J2": float(0.5 * np.sum(s * s)),
        "J3": float(np.linalg.det(s)),
    }


def von_mises_from_principal(sigma1: float, sigma2: float, sigma3: float) -> float:
    return float(np.sqrt(
        0.5 * (
            (sigma1 - sigma2) ** 2
            + (sigma2 - sigma3) ** 2
            + (sigma3 - sigma1) ** 2
        )
    ))


def von_mises_from_tensor(tensor: np.ndarray) -> float:
    J2 = invariants(tensor)["J2"]
    return float(np.sqrt(max(0.0, 3.0 * J2)))


def von_mises_plane_stress(sigma_x: float, sigma_y: float, tau_xy: float) -> float:
    return float(np.sqrt(
        sigma_x**2 - sigma_x*sigma_y + sigma_y**2 + 3.0*tau_xy**2
    ))


def principal_stresses_plane(
    sigma_x: float, sigma_y: float, tau_xy: float
) -> tuple[float, float]:
    avg = 0.5 * (sigma_x + sigma_y)
    radius = np.sqrt(((sigma_x - sigma_y) * 0.5)**2 + tau_xy**2)
    return float(avg + radius), float(avg - radius)


def principal_angle_plane(
    sigma_x: float, sigma_y: float, tau_xy: float
) -> float:
    """Ángulo θp [rad] del sistema principal respecto de x."""
    return float(0.5 * np.arctan2(2.0*tau_xy, sigma_x - sigma_y))


def mohr_circle_2d(sigma_x: float, sigma_y: float, tau_xy: float) -> dict[str, float]:
    center = 0.5 * (sigma_x + sigma_y)
    radius = float(np.sqrt(((sigma_x - sigma_y) * 0.5)**2 + tau_xy**2))
    return {
        "center": float(center),
        "radius": radius,
        "sigma1": float(center + radius),
        "sigma2": float(center - radius),
        "tau_max_in_plane": radius,
        "theta_p_rad": principal_angle_plane(sigma_x, sigma_y, tau_xy),
    }


def tresca_equivalent_from_principal(
    sigma1: float, sigma2: float, sigma3: float
) -> float:
    return float(max(
        abs(sigma1 - sigma2),
        abs(sigma2 - sigma3),
        abs(sigma3 - sigma1),
    ))


def safety_factor(yield_strength: float, equivalent_stress: float) -> float:
    Sy = float(yield_strength)
    seq = float(equivalent_stress)
    if Sy <= 0:
        raise ValueError("El límite de fluencia debe ser mayor que cero.")
    if seq < 0:
        raise ValueError("El esfuerzo equivalente no puede ser negativo.")
    return float("inf") if seq == 0 else Sy / seq


def classify_yield_state(yield_strength: float, equivalent_stress: float, tol=1e-9) -> str:
    Sy = float(yield_strength)
    seq = float(equivalent_stress)
    scale = max(abs(Sy), 1.0)
    if seq < Sy - tol*scale:
        return "Estado seguro en régimen elástico"
    if abs(seq - Sy) <= tol*scale:
        return "Inicio de fluencia"
    return "Superación del límite de fluencia"


def octahedral_shear_from_principal(
    sigma1: float, sigma2: float, sigma3: float
) -> float:
    return float((1.0/3.0) * np.sqrt(
        (sigma1 - sigma2)**2
        + (sigma2 - sigma3)**2
        + (sigma3 - sigma1)**2
    ))


def add_hydrostatic_shift(tensor: np.ndarray, delta_sigma_h: float) -> np.ndarray:
    return validate_tensor(tensor) + np.eye(3) * float(delta_sigma_h)


def pi_plane_coordinates(
    sigma1: float, sigma2: float, sigma3: float
) -> tuple[float, float]:
    """
    Coordenadas ortonormales del vector desviador en el plano π.
    e_a=(1,-1,0)/sqrt(2), e_b=(1,1,-2)/sqrt(6).
    """
    s = np.array([sigma1, sigma2, sigma3], dtype=float)
    s = s - np.mean(s)
    ea = np.array([1.0, -1.0, 0.0]) / np.sqrt(2.0)
    eb = np.array([1.0, 1.0, -2.0]) / np.sqrt(6.0)
    return float(s @ ea), float(s @ eb)


def von_mises_cylinder_radius(yield_strength: float) -> float:
    return float(np.sqrt(2.0/3.0) * yield_strength)
