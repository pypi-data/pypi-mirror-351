import numpy as np
from ODEpower.tool import *
import matplotlib.pyplot as plt
import scipy.integrate as spi
from scipy.signal import lsim
from scipy.interpolate import interp1d
from scipy.optimize import linear_sum_assignment
from scipy.interpolate import interp1d
import numpy as np
import sympy as sp


class ODEsimulation:
    """
    Provides simulation routines for ODE and state-space models, including numerical integration and parameter sweeps.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the ODEsimulation object.
        """
        # Step 1: Call parent initializers
        super().__init__(*args, **kwargs)
        # Step 2: Default integration method can be set via config

#    #Definition of ODEs to solve with solve_ivp
#    def odefunc(self, t, y):
#        """
#        Defines the ODE system for use with scipy's solve_ivp.
#        Interpolates the input at time t and evaluates the ODEs.
#
#        Args:
#            t: Current time.
#            y: Current state vector.
#        Returns:
#            List of derivatives at time t.
#        """
#        # Step 1: Interpolate the input value at time t
#        if (self.u_val.shape[0] > 1):
#            idx = (np.abs(self.u_val[0, :] - t)).argmin()
#            u = self.u_val[1:, idx]
#        # Step 2: Evaluate the ODEs with the current state and input
#        return [f(*y, *u) for f in self.odes_np]


#    # Simulate ODE system
#    def sim_ode(self, setOp=False, Tsim=-1, save_y=True, rtol=1e-6, atol=1e-8, max_step=1e-5):
#        """
#        Simulate the ODE system using scipy's solve_ivp.
#
#        Args:
#            setOp: If True, use the operating point as the initial state.
#            Tsim: Simulation end time (if -1, use from params).
#            save_y: If True, compute and store outputs.
#            rtol: Relative tolerance for the solver.
#            atol: Absolute tolerance for the solver.
#            max_step: Maximum integration step size.
#        """
#        # Step 1: Determine simulation time span
#        if Tsim == -1:
#            t_span = [0, self.params['sim_params']['Tsim']]
#        else:
#            t_span = [0, Tsim]
#
#        # Step 2: Set initial state (operating point or zeros)
#        if setOp:
#            y0 = self.op
#        else:
#            y0 = [0 for _ in self.x]
#
#        # Step 3: Run the ODE solver
#        sol = spi.solve_ivp(
#            fun=lambda t, y: self.odefunc(t, y),
#            t_span=t_span,
#            y0=y0,
#            method=self.config.pySolver,
#            rtol=rtol,
#            atol=atol,
#            max_step=max_step)
#
#        # Step 4: Store state trajectories in a dictionary
#        #x_ODE = {str(self.x[i]): sol.y.T[:, i] for i in range(len(self.x))}
#        x_ODE = {str(self.x[i]): sol.y[i, :] for i in range(len(self.x))}
#        self.sol_ode = dotdict({'t': sol.t, 'x': x_ODE})
#
#        # Step 5: Optionally compute and store outputs
#        ny = len(self.y)
#        if save_y and (ny > 0):
#            nu = len(self.u)
#            self.sol_ode.y = np.zeros((ny, len(self.sol_ode.t)))
#
#            if nu > 0:
#                # Interpolate input values for each time step
#                u_interp = interp1d(self.u_val[0, :], self.u_val[1:, :], axis=1, kind='linear', fill_value="extrapolate")
#                u_interp_values = u_interp(self.sol_ode.t)  # Shape: (nu, len(self.sol_ode.t))
#                self.sol_ode.y[:, :] = np.array([eq(*sol.y[:, :], *u_interp_values) for eq in self.y_np])
#            else:
#                self.sol_ode.y[:, :] = np.array([eq(*sol.y[:, :]) for eq in self.y_np])

    # Simulate state-space system
    def sim_ss(self, Tsim=-1, dt=1e-6):
        """
        Simulate the state-space system using scipy's lsim.

        Args:
            Tsim: Simulation end time (if -1, use from params).
            dt: Time step for simulation.
        Raises:
            ValueError: If the operating point is not available.
        """
        # Check if op is available
        if not hasattr(self, 'op'):
            raise ValueError('Calculate OP first.')

        # Extract time vector and data
        t = self.u_val[0]
        values = self.u_val[1:]

        if Tsim == -1:
            Tsim = self.params['sim_params']['Tsim']

        # Generate new time vector
        new_time = np.arange(t[0], min(Tsim, t[-1]) + dt, dt)

        # Interpolate each data row
        interpolated_values = []
        for row in values:
            interpolator = interp1d(t, row, kind='linear', fill_value="extrapolate")
            interpolated_values.append(interpolator(new_time))

        # Combine new time vector with interpolated data
        input = np.vstack([new_time, interpolated_values])

        # Reshape input values for lsim
        u_ss = input[1:] - np.tile(input[1:, 0].reshape(input[1:, 0].shape[0], 1), (1, len(input[0])))

        x0 = [0 for _ in self.op]
        t_out, y_out, x_out = lsim(self.ss_sys, U=u_ss.T, T=new_time, X0=x0)
        x_out = x_out + np.tile(self.op, (len(new_time), 1))
        x_ODE = {str(self.x[i]): x_out[:, i] for i in range(len(self.x))}

        if len(self.y) > 0:
            y_op = np.array([eq(*self.op, *self.u_val[1:, 0]) for eq in self.y_np]).flatten()
            y_out = (y_out + np.tile(y_op, (len(new_time), 1))).T
        else:
            y_out = None

        self.sol_ss = dotdict({'t': t_out, 'y': y_out, 'x': x_ODE})

    def sim_ode(self, setOp=False, Tsim=-1, save_y=True, rtol=1e-6, atol=1e-8, max_step=1e-3):
        """
        Simulate the ODE system using scipy's solve_ivp with performance optimizations.

        This version uses:
            - Precomputed input interpolation (no per-step argmin)
            - Vectorized lambdified functions for ODEs and outputs
            - Efficient handling of state and output arrays

        Args:
            setOp: If True, use the operating point as the initial state. Otherwise, start from zero.
            Tsim: Simulation end time. If -1, use the value from simulation parameters.
            save_y: If True, compute and store output trajectories.
            rtol: Relative tolerance for the ODE solver.
            atol: Absolute tolerance for the ODE solver.
            max_step: Maximum time step allowed by the solver.

        Populates:
            self.sol_ode: A dotdict with keys:
                - 't': time vector (1D numpy array)
                - 'x': state trajectories (dict of variable name → time series)
                - 'y': output trajectories (2D numpy array), if save_y is True
        """
        # Step 1: Determine simulation time span
        t_span = [0, self.params['sim_params']['Tsim']] if Tsim == -1 else [0, Tsim]

        # Step 2: Set initial state
        y0 = self.op if setOp else np.zeros(len(self.x))

        # Step 3: Setup input interpolation only once
        if self.u_val.shape[0] > 1:
            u_interp = interp1d(self.u_val[0, :], self.u_val[1:, :], axis=1, kind='linear', fill_value="extrapolate")
        else:
            u_interp = lambda t: []

        # self.Tstep is the switching time
        def u_func(t):
            return self.v0 if t < self.Tstep else self.v1

        # Step 4: Vectorized ODE function
        def odefunc(t, y):
            #u = u_interp(t) if callable(u_interp) else []
            u = u_func(t)
            return self.odes_np(*y, *u)

        # Step 5: Solve the ODE
        sol = spi.solve_ivp(
            fun=odefunc,
            t_span=t_span,
            y0=y0,
            method=self.config.pySolver,
            rtol=rtol,
            atol=atol,
            max_step=max_step,
            dense_output=False
        )

        # Step 6: Store state trajectories
        x_ODE = {str(self.x[i]): sol.y[i, :] for i in range(len(self.x))}
        self.sol_ode = dotdict({'t': sol.t, 'x': x_ODE})

        # Step 7: Compute and store outputs efficiently
        #TODO ensure consistency in case self.y equation is 0
        if save_y and len(self.y) > 0:
    
            T = len(sol.t)
            self.sol_ode.y = np.zeros((len(self.y), T))

#            if len(self.u) > 0:
#                u_vals = u_interp(sol.t)  # shape (nu, T)
#                args = np.vstack((sol.y, u_vals))  # shape (nx + nu, T)
#            else:
#                args = sol.y  # shape (nx, T)

            u_vals = np.where(sol.t < self.Tstep, self.v0[:, np.newaxis], self.v1[:, np.newaxis])  # shape (nu, T)
            args = np.vstack((sol.y, u_vals))  # shape (nx + nu, T)
            y_vals = self.y_np(*args)
            self.sol_ode.y = {str(name): y_vals[i]           # 1-D array length T
                                for i, name in enumerate(self.y_str)}


    # Compute eigenvalues and pfs for given parameters
    def parametric_ode(self, param, vals, initGuess=False):
        """
        Perform a parameter sweep, simulating the system for each value and storing eigenvalues and participation factors.

        Args:
            param: The parameter to vary (symbol).
            vals: List of values to sweep.
            initGuess: If True, use initial guess for operating point.
        """
        self.PFs = np.zeros((len(vals), len(self.x), len(self.x)))
        self.eigs = np.zeros((len(vals), len(self.x)), dtype=np.complex128)
        _odes = self.odes
        _y = self.y
        _u = self.u_val
        _u_sp = sp.Matrix(self.u_val)
        self.parametric_val = vals
        self.parametric_name = str(param)

        for i, val in enumerate(vals):
            print(i, val)
            self.odes = _odes.subs({param: val})
            self.y = _y.subs({param: val})
            self.u_val = np.array(_u_sp.subs({param: val}), dtype=np.float64)
            self.odes_lamdify()
            self.get_op(matlab=True, initialGuess=initGuess)
            self.create_ss(info=False)

            D, V, PF = self.get_eig(rightV=True)

            self.eigs[i, :] = D
            self.PFs[i, :, :] = PF

        self.odes = _odes
        self.y = _y
        self.u_val = _u