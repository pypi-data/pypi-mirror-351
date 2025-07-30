from PhysicsOneA.dependencies import *

class CollisionAnalyzer:
    """
    Analyzer for different types of collisions based on momentum and energy conservation.
    
    Supports elastic, inelastic, and completely inelastic collisions in 1D.
    """
    
    def __init__(self):
        self.tolerance = 1e-6
    
    def momentum(self, mass: Union[float, UFloat], velocity: Union[float, UFloat]) -> Union[float, UFloat]:
        """
        Calculate momentum: p = mv
        
        Args:
            mass: Mass of object
            velocity: Velocity of object
            
        Returns:
            Momentum
        """
        return mass * velocity
    
    def kinetic_energy(self, mass: Union[float, UFloat], velocity: Union[float, UFloat]) -> Union[float, UFloat]:
        """
        Calculate kinetic energy: K = (1/2)mv²
        
        Args:
            mass: Mass of object
            velocity: Velocity of object
            
        Returns:
            Kinetic energy
        """
        return 0.5 * mass * velocity**2
    
    def impulse_momentum_theorem(self, 
                                initial_momentum: Union[float, UFloat],
                                final_momentum: Union[float, UFloat]) -> Union[float, UFloat]:
        """
        Calculate impulse using momentum change: J = Δp = p_final - p_initial
        
        Args:
            initial_momentum: Initial momentum
            final_momentum: Final momentum
            
        Returns:
            Impulse
        """
        return final_momentum - initial_momentum
    
    def elastic_collision_1d(self, 
                           m1: Union[float, UFloat], v1i: Union[float, UFloat],
                           m2: Union[float, UFloat], v2i: Union[float, UFloat]) -> Tuple[Union[float, UFloat], Union[float, UFloat]]:
        """
        Solve 1D elastic collision using conservation of momentum and energy.
        
        Conservation equations:
        (1) m1*v1i + m2*v2i = m1*v1f + m2*v2f  (momentum)
        (2) (1/2)*m1*v1i² + (1/2)*m2*v2i² = (1/2)*m1*v1f² + (1/2)*m2*v2f²  (energy)
        
        Args:
            m1, v1i: Mass and initial velocity of object 1
            m2, v2i: Mass and initial velocity of object 2
            
        Returns:
            Tuple of final velocities (v1f, v2f)
        """
        # Derived formulas for elastic collision
        total_mass = m1 + m2
        
        v1f = ((m1 - m2) * v1i + 2 * m2 * v2i) / total_mass
        v2f = ((m2 - m1) * v2i + 2 * m1 * v1i) / total_mass
        
        return v1f, v2f
    
    def inelastic_collision_1d(self,
                              m1: Union[float, UFloat], v1i: Union[float, UFloat],
                              m2: Union[float, UFloat], v2i: Union[float, UFloat],
                              coefficient_of_restitution: Union[float, UFloat] = 0.5) -> Tuple[Union[float, UFloat], Union[float, UFloat]]:
        """
        Solve 1D inelastic collision using conservation of momentum and coefficient of restitution.
        
        Conservation of momentum: m1*v1i + m2*v2i = m1*v1f + m2*v2f
        Coefficient of restitution: e = -(v1f - v2f)/(v1i - v2i)
        
        Args:
            m1, v1i: Mass and initial velocity of object 1
            m2, v2i: Mass and initial velocity of object 2
            coefficient_of_restitution: e (0 < e < 1 for inelastic, 0 for completely inelastic)
            
        Returns:
            Tuple of final velocities (v1f, v2f)
        """
        # From conservation of momentum and coefficient of restitution
        relative_velocity_initial = v1i - v2i
        relative_velocity_final = -coefficient_of_restitution * relative_velocity_initial
        
        # Solve system of equations
        total_mass = m1 + m2
        momentum_initial = m1 * v1i + m2 * v2i
        
        v1f = (momentum_initial + m2 * relative_velocity_final) / total_mass
        v2f = (momentum_initial - m1 * relative_velocity_final) / total_mass
        
        return v1f, v2f
    
    def completely_inelastic_collision_1d(self,
                                        m1: Union[float, UFloat], v1i: Union[float, UFloat],
                                        m2: Union[float, UFloat], v2i: Union[float, UFloat]) -> Union[float, UFloat]:
        """
        Solve 1D completely inelastic collision where objects stick together.
        
        Conservation of momentum: m1*v1i + m2*v2i = (m1 + m2)*vf
        
        Args:
            m1, v1i: Mass and initial velocity of object 1
            m2, v2i: Mass and initial velocity of object 2
            
        Returns:
            Final velocity of combined system
        """
        momentum_initial = m1 * v1i + m2 * v2i
        total_mass = m1 + m2
        
        return momentum_initial / total_mass
    
    def analyze_collision_type(self,
                             m1: Union[float, UFloat], v1i: Union[float, UFloat], v1f: Union[float, UFloat],
                             m2: Union[float, UFloat], v2i: Union[float, UFloat], v2f: Union[float, UFloat]) -> str:
        """
        Determine the type of collision based on energy conservation.
        
        Args:
            m1, v1i, v1f: Mass, initial and final velocity of object 1
            m2, v2i, v2f: Mass, initial and final velocity of object 2
            
        Returns:
            String describing collision type
        """
        # Calculate initial and final kinetic energies
        ke_initial = self.kinetic_energy(m1, v1i) + self.kinetic_energy(m2, v2i)
        ke_final = self.kinetic_energy(m1, v1f) + self.kinetic_energy(m2, v2f)
        
        # Check momentum conservation
        p_initial = self.momentum(m1, v1i) + self.momentum(m2, v2i)
        p_final = self.momentum(m1, v1f) + self.momentum(m2, v2f)
        
        momentum_conserved = isclose(nominal_value(p_initial), nominal_value(p_final), rel_tol=self.tolerance)
        energy_conserved = isclose(nominal_value(ke_initial), nominal_value(ke_final), rel_tol=self.tolerance)
        
        if not momentum_conserved:
            return "Invalid collision - momentum not conserved"
        
        if energy_conserved:
            return "Elastic collision"
        elif nominal_value(ke_final) < nominal_value(ke_initial):
            if isclose(nominal_value(v1f), nominal_value(v2f), rel_tol=self.tolerance):
                return "Completely inelastic collision"
            else:
                return "Inelastic collision"
        else:
            return "Invalid collision - energy increased"
    
    def plot_collision_analysis(self,
                              m1: Union[float, UFloat], v1i: Union[float, UFloat], v1f: Union[float, UFloat],
                              m2: Union[float, UFloat], v2i: Union[float, UFloat], v2f: Union[float, UFloat],
                              title: str = "Collision Analysis") -> None:
        """
        Create visualization of collision before and after.
        
        Args:
            m1, v1i, v1f: Mass, initial and final velocity of object 1
            m2, v2i, v2f: Mass, initial and final velocity of object 2
            title: Plot title
        """
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
        
        # Extract nominal values for plotting
        def get_nominal(val):
            return nominal_value(val) if isinstance(val, UFloat) else val
        
        m1_nom, v1i_nom, v1f_nom = get_nominal(m1), get_nominal(v1i), get_nominal(v1f)
        m2_nom, v2i_nom, v2f_nom = get_nominal(m2), get_nominal(v2i), get_nominal(v2f)
        
        # Velocity comparison
        objects = ['Object 1', 'Object 2']
        initial_velocities = [v1i_nom, v2i_nom]
        final_velocities = [v1f_nom, v2f_nom]
        
        x = np.arange(len(objects))
        width = 0.35
        
        ax1.bar(x - width/2, initial_velocities, width, label='Initial', alpha=0.7)
        ax1.bar(x + width/2, final_velocities, width, label='Final', alpha=0.7)
        ax1.set_ylabel('Velocity (m/s)')
        ax1.set_title('Velocities Before and After Collision')
        ax1.set_xticks(x)
        ax1.set_xticklabels(objects)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Momentum comparison
        p1i, p1f = m1_nom * v1i_nom, m1_nom * v1f_nom
        p2i, p2f = m2_nom * v2i_nom, m2_nom * v2f_nom
        
        initial_momenta = [p1i, p2i]
        final_momenta = [p1f, p2f]
        
        ax2.bar(x - width/2, initial_momenta, width, label='Initial', alpha=0.7)
        ax2.bar(x + width/2, final_momenta, width, label='Final', alpha=0.7)
        ax2.set_ylabel('Momentum (kg⋅m/s)')
        ax2.set_title('Momentum Before and After Collision')
        ax2.set_xticks(x)
        ax2.set_xticklabels(objects)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Energy comparison
        ke1i, ke1f = 0.5 * m1_nom * v1i_nom**2, 0.5 * m1_nom * v1f_nom**2
        ke2i, ke2f = 0.5 * m2_nom * v2i_nom**2, 0.5 * m2_nom * v2f_nom**2
        
        initial_energies = [ke1i, ke2i]
        final_energies = [ke1f, ke2f]
        
        ax3.bar(x - width/2, initial_energies, width, label='Initial', alpha=0.7)
        ax3.bar(x + width/2, final_energies, width, label='Final', alpha=0.7)
        ax3.set_ylabel('Kinetic Energy (J)')
        ax3.set_title('Kinetic Energy Before and After Collision')
        ax3.set_xticks(x)
        ax3.set_xticklabels(objects)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.suptitle(title, y=1.02)
        plt.show()


# Example usage and demonstrations
if __name__ == "__main__":
    analyzer = CollisionAnalyzer()
    
    # Example 1: Elastic collision
    print("=== Elastic Collision Example ===")
    m1, v1i = 2.0, 5.0  # 2 kg moving at 5 m/s
    m2, v2i = 1.0, -3.0  # 1 kg moving at -3 m/s
    
    v1f, v2f = analyzer.elastic_collision_1d(m1, v1i, m2, v2i)
    print(f"Initial: m1={m1} kg, v1i={v1i} m/s, m2={m2} kg, v2i={v2i} m/s")
    print(f"Final: v1f={v1f:.3f} m/s, v2f={v2f:.3f} m/s")
    
    collision_type = analyzer.analyze_collision_type(m1, v1i, v1f, m2, v2i, v2f)
    print(f"Collision type: {collision_type}")
    
    # Example 2: Completely inelastic collision
    print("\n=== Completely Inelastic Collision Example ===")
    vf = analyzer.completely_inelastic_collision_1d(m1, v1i, m2, v2i)
    print(f"Final velocity of combined system: {vf:.3f} m/s")
    
    # Example 3: With uncertainties
    print("\n=== Collision with Uncertainties ===")
    m1_u = ufloat(2.0, 0.1)  # 2.0 ± 0.1 kg
    v1i_u = ufloat(5.0, 0.2)  # 5.0 ± 0.2 m/s
    m2_u = ufloat(1.0, 0.05)  # 1.0 ± 0.05 kg
    v2i_u = ufloat(-3.0, 0.1)  # -3.0 ± 0.1 m/s
    
    v1f_u, v2f_u = analyzer.elastic_collision_1d(m1_u, v1i_u, m2_u, v2i_u)
    print(f"Final velocities with uncertainties:")
    print(f"v1f = {v1f_u}")

def momentum(mass, velocity):
    """Calculate momentum: p = mv"""
    return mass * velocity

def elastic_collision_1d(m1, v1i, m2, v2i):
    """Solve 1D elastic collision"""
    analyzer = CollisionAnalyzer()
    return analyzer.elastic_collision_1d(m1, v1i, m2, v2i)

def inelastic_collision_1d(m1, v1i, m2, v2i, coefficient_of_restitution=0.5):
    """Solve 1D inelastic collision"""
    analyzer = CollisionAnalyzer()
    return analyzer.inelastic_collision_1d(m1, v1i, m2, v2i, coefficient_of_restitution)

def completely_inelastic_collision_1d(m1, v1i, m2, v2i):
    """Solve 1D completely inelastic collision"""
    analyzer = CollisionAnalyzer()
    return analyzer.completely_inelastic_collision_1d(m1, v1i, m2, v2i)

def analyze_collision_type(m1, v1i, v1f, m2, v2i, v2f):
    """Determine collision type"""
    analyzer = CollisionAnalyzer()
    return analyzer.analyze_collision_type(m1, v1i, v1f, m2, v2i, v2f)

def impulse_momentum_theorem(initial_momentum, final_momentum):
    """Calculate impulse from momentum change"""
    return final_momentum - initial_momentum

def plot_collision_analysis(m1, v1i, v1f, m2, v2i, v2f, title="Collision Analysis"):
    """Plot collision analysis"""
    analyzer = CollisionAnalyzer()
    return analyzer.plot_collision_analysis(m1, v1i, v1f, m2, v2i, v2f, title)

def coefficient_of_restitution(v1i, v2i, v1f, v2f):
    """Calculate coefficient of restitution"""
    relative_velocity_initial = v1i - v2i
    relative_velocity_final = v1f - v2f
    
    if abs(relative_velocity_initial) < 1e-10:
        return 0.0
    
    return -relative_velocity_final / relative_velocity_initial
