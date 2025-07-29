from typing import Tuple
from numpy import sqrt, arctan, sin, cos, exp
from scipy.constants import mu_0, c, e, m_e, pi


def a0_from_E0(E0: float, lambda0: float = 0.8e-6) -> float:
    omega0 = 2*pi*c/lambda0
    return E0 * e / m_e / c / omega0


def E0_from_a0(a0: float, lambda0: float = 0.8e-6) -> float:
    omega0 = 2*pi*c/lambda0
    return a0 * m_e * c * omega0 / e


def I_from_E0(E0: float) -> float:
    return 0.5 * E0**2 / mu_0 / c


def E0_from_I(I: float) -> float:
    return sqrt(I*mu_0*c*2)


def I_from_a0(a0: float, lambda0: float = 0.8e-6) -> float:
    E0 = E0_from_a0(a0, lambda0)
    return I_from_E0(E0)


def a0_from_I(I: float, lambda0: float = 0.8e-6) -> float:
    E0 = E0_from_I(I)
    return a0_from_E0(E0, lambda0)


def power(a0: float, w0: float, lambda0: float = 0.8e-6) -> float:
    I = I_from_a0(a0, lambda0)
    return 0.5 * pi * w0**2 * I


def E0_from_power(power: float, w0: float, lambda0: float = 0.8e-6) -> float:
    I = 2*power / (pi*w0**2)
    return E0_from_I(I)


def a0_from_power(power: float, w0: float, lambda0: float = 0.8e-6) -> float:
    E0 = E0_from_power(power, w0, lambda0)
    return a0_from_E0(E0, lambda0)


def w0_from_power(power: float, a0: float, lambda0: float = 0.8e-6) -> float:
    I = I_from_a0(a0, lambda0)
    return sqrt(power/I/(0.5*pi))


def GaussianSpaceProfile(
    amp: float, w0: float, ctau: float, x0: Tuple[float, float, float],
    xf: float = None, lambda0: float = 0.8e-6, cep: float = 0.0
):
    k0 = 2*pi/lambda0
    zR = pi*w0**2/lambda0

    if xf is None:
        xf = x0[0]

    def profile2d(x, y):
        x -= xf
        y -= x0[1]

        r2 = y**2
        wz = w0 * sqrt(1 + (x/zR)**2)
        Rz = x * (1 + (zR/x)**2)
        gouy = arctan(x/zR)

        phi = k0 * (x + xf - x0[0]) + k0*r2/2/Rz - gouy
        return amp * cos(phi+cep) * w0/wz * exp(-r2/wz**2) * exp(-phi**2/(k0*ctau)**2)

    def profile3d(x, y, z):
        x -= xf
        y -= x0[1]
        z -= x0[2]

        r2 = y**2 + z**2
        wz = w0 * sqrt(1 + (x/zR)**2)
        Rz = x * (1 + (zR/x)**2)
        gouy = arctan(x/zR)

        phi = k0 * (x + xf - x0[0]) + k0*r2/2/Rz - gouy
        return amp * cos(phi+cep) * w0/wz * exp(-r2/wz**2) * exp(-phi**2/(k0*ctau)**2)

    if len(x0) == 2:
        return profile2d
    if len(x0) == 3:
        return profile3d
