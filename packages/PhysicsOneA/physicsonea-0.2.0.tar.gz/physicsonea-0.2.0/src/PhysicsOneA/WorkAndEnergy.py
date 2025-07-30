from PhysicsOneA.dependencies import *
from PhysicsOneA.helpers import *

def work(force, displacement, angle_deg=0):
    """
    Calculates the work done by a constant force over a straight-line displacement.

    Formula:
        W = F * s * cos(theta)

    Parameters:
        force (float or UFloat): Magnitude of the force in newtons.
        displacement (float or UFloat): Distance over which the force acts, in meters.
        angle_deg (float): Angle between force and displacement in degrees. Default is 0° (same direction).

    Returns:
        UFloat: Work done in joules.
    """
    F = format_input(force)
    s = format_input(displacement)
    theta = degree_to_radian(angle_deg)
    return F * s * cos(theta)

def spring_work(k, x1, x2):
    """
    Calculates the work done by a spring force between two displacements.

    Formula:
        W = (1/2) * k * x1² - (1/2) * k * x2²

    Parameters:
        k (float or UFloat): Spring constant in N/m.
        x1 (float or UFloat): Initial stretch or compression from equilibrium (in meters).
        x2 (float or UFloat): Final stretch or compression from equilibrium (in meters).

    Returns:
        UFloat: Work done by the spring in joules.
    """
    k = format_input(k)
    x1 = format_input(x1)
    x2 = format_input(x2)
    return 0.5 * k * (x1**2 - x2**2)

def gravity_work(mass, x1, x2, g=gravity()):
    """
    Calculates work done by gravity as an object moves vertically.

    Formula:
        W = m * g * (x1 - x2)

    Parameters:
        mass (float or UFloat): Mass of the object in kg.
        x1 (float or UFloat): Initial vertical position in meters.
        x2 (float or UFloat): Final vertical position in meters.
        g (float or UFloat): Gravitational acceleration, default is local gravity.

    Returns:
        UFloat: Work done by gravity in joules.
    """
    m = format_input(mass)
    x1 = format_input(x1)
    x2 = format_input(x2)
    g = format_input(g)
    return m * g * (x1 - x2)

def friction_work(mu_k, mass, distance, g=gravity()):
    """
    Calculates the work done by kinetic friction, which is always negative.

    Formula:
        W = -μ * m * g * d

    Parameters:
        mu_k (float): Coefficient of kinetic friction.
        mass (float or UFloat): Mass of the object in kg.
        distance (float or UFloat): Distance moved while friction is applied, in meters.
        g (float or UFloat): Gravitational acceleration, default is local gravity.

    Returns:
        UFloat: Work done by friction in joules (negative).
    """
    mu = format_input(mu_k)
    m = format_input(mass)
    d = format_input(distance)
    g = format_input(g)
    return -mu * m * g * d

def kinetic_energy(mass, velocity):
    """
    Calculates the kinetic energy of an object.

    Formula:
        K = 1/2 * m * v²

    Parameters:
        mass (float or UFloat): Mass in kg.
        velocity (float or UFloat): Speed in m/s.

    Returns:
        UFloat: Kinetic energy in joules.
    """
    m = format_input(mass)
    v = format_input(velocity)
    return 0.5 * m * v**2

def delta_kinetic_energy(mass, v_initial, v_final):
    """
    Calculates the change in kinetic energy from v_initial to v_final.

    Formula:
        ΔK = 1/2 * m * (v_final² - v_initial²)

    Parameters:
        mass (float or UFloat): Mass in kg.
        v_initial (float or UFloat): Initial speed in m/s.
        v_final (float or UFloat): Final speed in m/s.

    Returns:
        UFloat: Change in kinetic energy in joules.
    """
    KE1 = kinetic_energy(mass, v_initial)
    KE2 = kinetic_energy(mass, v_final)
    return KE2 - KE1

def average_power(work, time):
    """
    Calculates average power over a time interval.

    Formula:
        P = W / t

    Parameters:
        work (float or UFloat): Work done in joules.
        time (float or UFloat): Time interval in seconds.

    Returns:
        UFloat: Power in watts (J/s).
    """
    W = format_input(work)
    t = format_input(time)
    return W / t

def instantaneous_power(force, velocity, angle_deg=0):
    """
    Calculates instantaneous power delivered by a force.

    Formula:
        P = F * v * cos(theta)

    Parameters:
        force (float or UFloat): Magnitude of the force in newtons.
        velocity (float or UFloat): Speed in m/s.
        angle_deg (float): Angle between force and velocity in degrees.

    Returns:
        UFloat: Power in watts.
    """
    F = format_input(force)
    v = format_input(velocity)
    theta = degree_to_radian(angle_deg)
    return F * v * cos(theta)


class EnergySystem:
    """
    Represents a physical object with mass, velocity, and position, allowing
    calculations of kinetic energy, potential energy, total mechanical energy,
    and work done by external forces.

    This is useful for simulations or keeping state of an object over time.
    """

    def __init__(self, mass, velocity=0, position=0, g=gravity()):
        """
        Initializes the EnergySystem object.

        Parameters:
            mass (float or UFloat): Mass of the object in kilograms.
            velocity (float or UFloat): Current velocity in m/s. Default is 0.
            position (float or UFloat): Vertical position in meters. Default is 0.
            g (float or UFloat): Gravitational acceleration. Default is local gravity.
        """
        self.m = format_input(mass)
        self.v = format_input(velocity)
        self.x = format_input(position)
        self.g = format_input(g)

    @property
    def mass(self):
        """Mass of the object in kg (UFloat)."""
        return self._m

    @property
    def velocity(self):
        """Current velocity in m/s (UFloat)."""
        return self._v

    @property
    def position(self):
        """Current vertical position in m (UFloat)."""
        return self._x

    @property
    def gravity(self):
        """Gravitational acceleration (UFloat)."""
        return self._g

    def kinetic_energy(self):
        """
        Returns the current kinetic energy: (1/2) * m * v²

        Returns:
            UFloat: Kinetic energy in joules.
        """
        return 0.5 * self.m * self.v**2

    def potential_energy(self, reference_height=0):
        """
        Returns the gravitational potential energy relative to a reference height.

        Parameters:
            reference_height (float or UFloat): The zero-point for potential energy.

        Returns:
            UFloat: Potential energy in joules.
        """
        h = self.x - format_input(reference_height)
        return self.m * self.g * h

    def total_mechanical_energy(self, reference_height=0):
        """
        Returns the total mechanical energy (kinetic + potential).

        Parameters:
            reference_height (float or UFloat): Zero point for potential energy.

        Returns:
            UFloat: Total energy in joules.
        """
        return self.kinetic_energy() + self.potential_energy(reference_height)

    def apply_force(self, force, displacement, angle_deg=0):
        """
        Calculates the work done by an external force on the system.

        Parameters:
            force (float or UFloat): Force applied in newtons.
            displacement (float or UFloat): Displacement in meters.
            angle_deg (float): Angle between force and displacement (in degrees).

        Returns:
            UFloat: Work done in joules.
        """
        F = format_input(force)
        d = format_input(displacement)
        theta = degree_to_radian(angle_deg)
        return F * d * cos(theta)

    def update_state(self, velocity=None, position=None):
        """
        Updates the internal velocity and/or position of the system.

        Parameters:
            velocity (float or UFloat, optional): New velocity in m/s.
            position (float or UFloat, optional): New position in meters.
        """
        if velocity is not None:
            self.v = format_input(velocity)
        if position is not None:
            self.x = format_input(position)

    def __str__(self):
        return (
            "--- Energy System ---\n"
            f"Mass: {self.m:.3f} kg\n"
            f"Velocity: {self.v:.3f} m/s\n"
            f"Position: {self.x:.3f} m\n"
            f"Kinetic Energy: {self.kinetic_energy():.3f} J\n"
            f"Potential Energy: {self.potential_energy():.3f} J\n"
            f"Total Energy: {self.total_mechanical_energy():.3f} J"
        )
