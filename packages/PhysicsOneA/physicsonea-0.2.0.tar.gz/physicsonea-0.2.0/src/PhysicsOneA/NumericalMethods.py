import numpy as np
import matplotlib.pyplot as plt

class NumericalSolver:
    """
    Fast numerical solver using standard floats instead of uncertainty objects.
    """
    
    def __init__(self, f, y0, t_span, method='rk4', dt=0.01):
        self.f = f
        self.y0 = np.array(y0, dtype=float)
        self.t_start, self.t_end = t_span
        self.dt = dt
        self.method = method
        
        self.t_values = []
        self.y_values = []
        self.solved = False
    
    def solve(self):
        if self.method == 'euler':
            self._euler_method()
        elif self.method == 'euler_cromer':
            self._euler_cromer_method()
        elif self.method == 'rk4':
            self._runge_kutta_4()
        
        self.solved = True
        return self.t_values, self.y_values
    
    def _euler_method(self):
        t = self.t_start
        y = self.y0.copy()
        
        self.t_values = [t]
        self.y_values = [y.copy()]
        
        while t < self.t_end:
            dydt = np.array(self.f(t, y), dtype=float)
            y = y + self.dt * dydt
            t = t + self.dt
            
            self.t_values.append(t)
            self.y_values.append(y.copy())
    
    def _runge_kutta_4(self):
        t = self.t_start
        y = self.y0.copy()
        
        self.t_values = [t]
        self.y_values = [y.copy()]
        
        while t < self.t_end:
            k1 = np.array(self.f(t, y), dtype=float)
            k2 = np.array(self.f(t + self.dt/2, y + self.dt*k1/2), dtype=float)
            k3 = np.array(self.f(t + self.dt/2, y + self.dt*k2/2), dtype=float)
            k4 = np.array(self.f(t + self.dt, y + self.dt*k3), dtype=float)
            
            y = y + (self.dt/6) * (k1 + 2*k2 + 2*k3 + k4)
            t = t + self.dt
            
            self.t_values.append(t)
            self.y_values.append(y.copy())
    
    def _euler_cromer_method(self):
        t = self.t_start
        y = self.y0.copy()
        
        self.t_values = [t]
        self.y_values = [y.copy()]
        
        while t < self.t_end:
            dydt = np.array(self.f(t, y), dtype=float)
            
            if len(y) >= 2:
                y[1] = y[1] + self.dt * dydt[1]
                y[0] = y[0] + self.dt * y[1]
                for i in range(2, len(y)):
                    y[i] = y[i] + self.dt * dydt[i]
            else:
                y = y + self.dt * dydt
            
            t = t + self.dt
            self.t_values.append(t)
            self.y_values.append(y.copy())
    
    def plot_solution(self, component=0, title="Solution"):
        if not self.solved:
            self.solve()
        
        plt.figure(figsize=(8, 6))
        plt.plot(self.t_values, [y[component] for y in self.y_values])
        plt.xlabel('Time (s)')
        plt.ylabel(f'y[{component}]')
        plt.title(title)
        plt.grid(True)
        plt.show()
    
    def plot_phase_space(self, x_component=0, y_component=1, title="Phase Space"):
        if not self.solved:
            self.solve()
        
        if len(self.y_values[0]) < max(x_component, y_component) + 1:
            raise ValueError("Not enough components for phase space plot")
        
        x_vals = [y[x_component] for y in self.y_values]
        y_vals = [y[y_component] for y in self.y_values]
        
        plt.figure(figsize=(8, 6))
        plt.plot(x_vals, y_vals)
        plt.xlabel(f'Component {x_component}')
        plt.ylabel(f'Component {y_component}')
        plt.title(title)
        plt.grid(True)
        plt.show()

def simple_harmonic_oscillator(k, m, x0, v0, t_span=(0, 10), method='euler_cromer', dt=0.01):
    def f(t, y):
        x, v = y[0], y[1]
        return [v, -k * x / m]
    
    solver = NumericalSolver(f, [x0, v0], t_span, method, dt)
    solver.solve()
    return solver

def damped_harmonic_oscillator(k, m, b, x0, v0, t_span=(0, 10), method='euler_cromer', dt=0.01):
    def f(t, y):
        x, v = y[0], y[1]
        return [v, (-k * x - b * v) / m]
    
    solver = NumericalSolver(f, [x0, v0], t_span, method, dt)
    solver.solve()
    return solver

def driven_oscillator(k, m, b, F0, omega, x0, v0, t_span=(0, 20), method='rk4', dt=0.01):
    def f(t, y):
        x, v = y[0], y[1]
        driving_force = F0 * np.cos(omega * t)
        return [v, (-k * x - b * v + driving_force) / m]
    
    solver = NumericalSolver(f, [x0, v0], t_span, method, dt)
    solver.solve()
    return solver

def projectile_with_drag(m, g, b, x0, y0, vx0, vy0, t_span=(0, 10), method='rk4', dt=0.01):
    def f(t, y):
        x, y_pos, vx, vy = y[0], y[1], y[2], y[3]
        
        v_mag = np.sqrt(vx**2 + vy**2)
        
        if v_mag > 1e-10:
            drag_x = -b * vx * v_mag / m
            drag_y = -b * vy * v_mag / m
        else:
            drag_x = drag_y = 0
        
        return [vx, vy, drag_x, -g + drag_y]
    
    solver = NumericalSolver(f, [x0, y0, vx0, vy0], t_span, method, dt)
    solver.solve()
    return solver

def pendulum(L, g, theta0, omega0, t_span=(0, 20), method='euler_cromer', dt=0.01):
    def f(t, y):
        theta, omega = y[0], y[1]
        return [omega, -g * np.sin(theta) / L]
    
    solver = NumericalSolver(f, [theta0, omega0], t_span, method, dt)
    solver.solve()
    return solver

def orbital_motion(mu, r0, v0, t_span=(0, 100), method='rk4', dt=0.1):
    def f(t, y):
        x, y_pos, vx, vy = y[0], y[1], y[2], y[3]
        
        r = np.sqrt(x**2 + y_pos**2)
        r_cubed = r**3
        
        ax = -mu * x / r_cubed
        ay = -mu * y_pos / r_cubed
        
        return [vx, vy, ax, ay]
    
    solver = NumericalSolver(f, [r0[0], r0[1], v0[0], v0[1]], t_span, method, dt)
    solver.solve()
    return solver

def coupled_oscillators(k1, k2, k3, m1, m2, x1_0, x2_0, v1_0, v2_0, t_span=(0, 20), method='rk4', dt=0.01):
    def f(t, y):
        x1, x2, v1, v2 = y[0], y[1], y[2], y[3]
        
        F1 = -k1 * x1 + k2 * (x2 - x1)
        F2 = -k3 * x2 - k2 * (x2 - x1)
        
        return [v1, v2, F1 / m1, F2 / m2]
    
    solver = NumericalSolver(f, [x1_0, x2_0, v1_0, v2_0], t_span, method, dt)
    solver.solve()
    return solver
