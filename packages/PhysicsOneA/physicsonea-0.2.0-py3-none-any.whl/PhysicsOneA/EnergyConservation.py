from PhysicsOneA.dependencies import *
from PhysicsOneA.helpers import *

def total_mechanical_energy(mass, velocity=0, height=0, spring_k=0, spring_x=0, g=gravity()):
    """
    Calculates total mechanical energy: E = KE + PE_gravitational + PE_spring

    Parameters:
        mass (float or UFloat): Mass in kg
        velocity (float or UFloat): Speed in m/s
        height (float or UFloat): Height in meters
        spring_k (float or UFloat): Spring constant (N/m)
        spring_x (float or UFloat): Compression/stretch of spring (m)
        g (float or UFloat): Gravitational acceleration (default is local gravity)

    Returns:
        UFloat: Total mechanical energy in joules
    """
    m = format_input(mass)
    v = format_input(velocity)
    h = format_input(height)
    k = format_input(spring_k)
    x = format_input(spring_x)
    g = format_input(g)

    KE = 0.5 * m * v**2
    PE_grav = m * g * h
    PE_spring = 0.5 * k * x**2

    return KE + PE_grav + PE_spring


def energy_conservation(E_initial, W_other=0):
    """
    Applies energy conservation with external work:
        E_final = E_initial + W_other

    Parameters:
        E_initial (float or UFloat): Initial total mechanical energy (J)
        W_other (float or UFloat): Work done by non-conservative forces (J)

    Returns:
        UFloat: Final mechanical energy in joules
    """
    E1 = format_input(E_initial)
    W = format_input(W_other)
    return E1 + W


def spring_compression_from_fall(mass, height, spring_k, g=gravity()):
    """
    Calculates spring compression after falling from height onto spring.

    Parameters:
        mass (float or UFloat): Mass in kg
        height (float or UFloat): Drop height in meters
        spring_k (float or UFloat): Spring constant in N/m
        g (float or UFloat): Gravitational acceleration

    Returns:
        UFloat: Maximum compression distance d (m)
    """
    m = format_input(mass)
    h = format_input(height)
    k = format_input(spring_k)
    g = format_input(g)

    return sqrt((2 * m * g * h) / k)


def speed_from_height_drop(height_start, height_end, g=gravity()):
    """
    Calculates speed from falling a vertical height.

    Parameters:
        height_start (float or UFloat): Initial height in meters
        height_end (float or UFloat): Final height in meters
        g (float or UFloat): Gravitational acceleration

    Returns:
        UFloat: Speed at bottom in m/s
    """
    h1 = format_input(height_start)
    h2 = format_input(height_end)
    g = format_input(g)

    return sqrt(2 * g * (h1 - h2))


def spring_potential_energy(k, x):
    """
    Calculates potential energy stored in a spring.

    Parameters:
        k (float or UFloat): Spring constant (N/m)
        x (float or UFloat): Compression/stretch from equilibrium (m)

    Returns:
        UFloat: Spring potential energy in joules
    """
    k = format_input(k)
    x = format_input(x)
    return 0.5 * k * x**2


def gravitational_potential_energy(mass, height, g=gravity()):
    """
    Calculates gravitational potential energy.

    Parameters:
        mass (float or UFloat): Mass in kg
        height (float or UFloat): Height above reference in meters
        g (float or UFloat): Gravitational acceleration

    Returns:
        UFloat: Gravitational potential energy in joules
    """
    m = format_input(mass)
    h = format_input(height)
    g = format_input(g)
    return m * g * h


def kinetic_energy(mass, velocity):
    """
    Calculates kinetic energy of an object.

    Parameters:
        mass (float or UFloat): Mass in kg
        velocity (float or UFloat): Speed in m/s

    Returns:
        UFloat: Kinetic energy in joules
    """
    m = format_input(mass)
    v = format_input(velocity)
    return 0.5 * m * v**2


def delta_mechanical_energy(E_initial, E_final):
    """
    Computes change in mechanical energy.

    Parameters:
        E_initial (float or UFloat): Initial total energy
        E_final (float or UFloat): Final total energy

    Returns:
        UFloat: ΔE = E_final - E_initial
    """
    Ei = format_input(E_initial)
    Ef = format_input(E_final)
    return Ef - Ei

def energy_conserved(E1, E2, tol=1e-3):
    """
    Checks if energy is conserved within a tolerance.

    Parameters:
        E1 (float or UFloat): Initial energy
        E2 (float or UFloat): Final energy
        tol (float): Allowed relative difference

    Returns:
        bool: True if conserved, else False
    """
    E1 = format_input(E1)
    E2 = format_input(E2)
    return abs(E2 - E1) / abs(E1) < tol
