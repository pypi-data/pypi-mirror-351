from scipy.constants import c, e, m_e, epsilon_0, pi, hbar
from numpy import sqrt

def nc(lambda0 : float) -> float:
    omega0 = 2*pi*c/lambda0
    return epsilon_0 * m_e * omega0**2 / e**2

def Pc(ne : float, nc : float) -> float:
    return 17 * (nc/ne) * 1e9 # W

def matched_n0(lambda0 : float, a0 : float, w0 : float) -> float:
    nc_ = nc(lambda0)
    return 1/pi**2 * a0 * lambda0**2 / w0**2 * nc_

def chi(Ex=0, Ey=0, Ez=0, Bx=0, By=0, Bz=0, ux=0, uy=0, uz=0):
    factor = e*hbar / (m_e**2 * c**3)
    
    gamma = sqrt(ux**2 + uy**2 + uz**2 + 1)

    chi = factor * sqrt(
        (gamma*Ex + (uy*Bz - uz*By)*c)**2 +
        (gamma*Ey + (uz*Bx - ux*Bz)*c)**2 +
        (gamma*Ez + (ux*By - uy*Bx)*c)**2 -
        (ux*Ex + uy*Ey + uz*Ez)**2
    )
    return chi