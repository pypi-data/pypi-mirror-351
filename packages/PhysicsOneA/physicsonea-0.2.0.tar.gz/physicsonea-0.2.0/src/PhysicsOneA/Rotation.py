from PhysicsOneA.dependencies import *
from PhysicsOneA.helpers import *

def rotational_kinetic_energy(I, omega):
    """
    Calculates rotational kinetic energy.

    Formula:
        K_rot = 1/2 * I * omega^2

    Parameters:
        I (float or UFloat): Moment of inertia (kg*m^2)
        omega (float or UFloat): Angular velocity in rad/s

    Returns:
        UFloat: Rotational kinetic energy in joules
    """
    I = format_input(I)
    omega = format_input(omega)
    return 0.5 * I * omega**2


def combined_kinetic_energy(I, omega, mass, v_cm):
    """
    Calculates total kinetic energy of a rotating and translating object.

    Formula:
        K = 1/2 * I * omega^2 + 1/2 * M * v_cm^2

    Parameters:
        I (float or UFloat): Moment of inertia (kg*m^2)
        omega (float or UFloat): Angular velocity (rad/s)
        mass (float or UFloat): Mass (kg)
        v_cm (float or UFloat): Velocity of center of mass (m/s)

    Returns:
        UFloat: Total kinetic energy (J)
    """
    K_rot = rotational_kinetic_energy(I, omega)
    m = format_input(mass)
    v = format_input(v_cm)
    K_trans = 0.5 * m * v**2
    return K_rot + K_trans


def parallel_axis(I_cm, mass, distance):
    """
    Applies the parallel axis theorem.

    Formula:
        I = I_cm + M * d^2

    Parameters:
        I_cm (float or UFloat): Moment of inertia through CM (kg*m^2)
        mass (float or UFloat): Mass (kg)
        distance (float or UFloat): Distance from new axis to CM (m)

    Returns:
        UFloat: Adjusted moment of inertia (kg*m^2)
    """
    I_cm = format_input(I_cm)
    m = format_input(mass)
    d = format_input(distance)
    return I_cm + m * d**2


def rotational_energy_conservation(K1_rot, K1_trans, U1, W_other, K2_trans, U2):
    """
    Computes final rotational kinetic energy using energy conservation.

    Formula:
        K1_rot + K1_trans + U1 + W_other = K2_rot + K2_trans + U2

    Parameters:
        K1_rot, K1_trans, U1, W_other, K2_trans, U2: all energy terms (float or UFloat)

    Returns:
        UFloat: K2_rot (final rotational kinetic energy)
    """
    terms = [K1_rot, K1_trans, U1, W_other, K2_trans, U2]
    values = [format_input(x) for x in terms]
    return sum(values[:4]) - sum(values[4:])


# --- Inertia formulas for common shapes ---

def inertia_solid_cylinder(mass, radius):
    """
    Moment of inertia of a solid cylinder about its central axis.
    I = 1/2 * M * R^2
    """
    m = format_input(mass)
    R = format_input(radius)
    return 0.5 * m * R**2


def inertia_hollow_cylinder(mass, R1, R2):
    """
    Moment of inertia of a hollow cylinder.
    I = 1/2 * M * (R1^2 + R2^2)
    """
    m = format_input(mass)
    R1 = format_input(R1)
    R2 = format_input(R2)
    return 0.5 * m * (R1**2 + R2**2)


def inertia_hoop(mass, radius):
    """
    Moment of inertia of a hoop about central axis.
    I = M * R^2
    """
    m = format_input(mass)
    R = format_input(radius)
    return m * R**2


def inertia_sphere(mass, radius):
    """
    Moment of inertia of a solid sphere.
    I = 2/5 * M * R^2
    """
    m = format_input(mass)
    R = format_input(radius)
    return (2/5) * m * R**2


def inertia_spherical_shell(mass, radius):
    """
    Moment of inertia of a thin spherical shell.
    I = 2/3 * M * R^2
    """
    m = format_input(mass)
    R = format_input(radius)
    return (2/3) * m * R**2


def inertia_thin_rod_center(mass, length):
    """
    Moment of inertia of a thin rod through its center.
    I = 1/12 * M * L^2
    """
    m = format_input(mass)
    L = format_input(length)
    return (1/12) * m * L**2


def inertia_thin_rod_end(mass, length):
    """
    Moment of inertia of a thin rod through one end.
    I = 1/3 * M * L^2
    """
    m = format_input(mass)
    L = format_input(length)
    return (1/3) * m * L**2


def torque(force, radius, angle_deg=90):
    """
    Calculates torque from a force.

    Formula:
        τ = R * F * sin(θ)

    Parameters:
        force (float or UFloat): Force in newtons
        radius (float or UFloat): Lever arm in meters
        angle_deg (float): Angle between R and F in degrees (default is 90°)

    Returns:
        UFloat: Torque in N·m
    """
    F = format_input(force)
    R = format_input(radius)
    theta = degree_to_radian(angle_deg)
    return R * F * sin(theta)


def angular_acceleration(torque, inertia):
    """
    Calculates angular acceleration using Newton's 2nd law for rotation.

    Formula:
        α = τ / I

    Parameters:
        torque (float or UFloat): Torque in N·m
        inertia (float or UFloat): Moment of inertia in kg·m²

    Returns:
        UFloat: Angular acceleration in rad/s²
    """
    tau = format_input(torque)
    I = format_input(inertia)
    return tau / I


def linear_from_angular(R, theta=None, omega=None, alpha=None):
    """
    Converts angular quantities to linear equivalents using:
        x = Rθ, v = Rω, a = Rα

    Parameters:
        R (float or UFloat): Radius in meters
        theta, omega, alpha (optional): Angular quantities

    Returns:
        UFloat: Corresponding linear quantity
    """
    R = format_input(R)
    if theta is not None:
        return R * format_input(theta)
    elif omega is not None:
        return R * format_input(omega)
    elif alpha is not None:
        return R * format_input(alpha)
    else:
        raise ValueError("Provide theta, omega, or alpha.")


def angular_from_linear(R, x=None, v=None, a=None):
    """
    Converts linear quantities to angular equivalents using:
        θ = x/R, ω = v/R, α = a/R

    Parameters:
        R (float or UFloat): Radius in meters
        x, v, a (optional): Linear quantities

    Returns:
        UFloat: Corresponding angular quantity
    """
    R = format_input(R)
    if x is not None:
        return format_input(x) / R
    elif v is not None:
        return format_input(v) / R
    elif a is not None:
        return format_input(a) / R
    else:
        raise ValueError("Provide x, v, or a.")


def angular_velocity_conservation(I1, omega1, I2):
    """
    Applies conservation of angular momentum:
        I₁ω₁ = I₂ω₂ ⇒ ω₂ = I₁ω₁ / I₂

    Parameters:
        I1, I2 (float or UFloat): Moments of inertia
        omega1 (float or UFloat): Initial angular velocity

    Returns:
        UFloat: Final angular velocity (rad/s)
    """
    I1 = format_input(I1)
    omega1 = format_input(omega1)
    I2 = format_input(I2)
    return (I1 * omega1) / I2


def angular_velocity_from_acceleration(alpha, time):
    """
    Calculates angular velocity from angular acceleration over time.

    Formula:
        ω = α * t (assuming ω₀ = 0)

    Parameters:
        alpha (float or UFloat): Angular acceleration (rad/s²)
        time (float or UFloat): Time in seconds

    Returns:
        UFloat: Angular velocity (rad/s)
    """
    a = format_input(alpha)
    t = format_input(time)
    return a * t


def angular_velocity_from_height(mass, height, inertia, g=gravity()):
    """
    Finds angular velocity ω when object falls from height and rotates.
    Uses energy conservation:
        mgh = 1/2 * I * ω² ⇒ ω = sqrt(2mgh / I)

    Parameters:
        mass (float or UFloat): Mass in kg
        height (float or UFloat): Drop height in meters
        inertia (float or UFloat): Moment of inertia
        g (float or UFloat): Gravitational acceleration

    Returns:
        UFloat: Angular velocity in rad/s
    """
    m = format_input(mass)
    h = format_input(height)
    I = format_input(inertia)
    g = format_input(g)
    return sqrt((2 * m * g * h) / I)