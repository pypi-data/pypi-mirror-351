import numpy as np
import pandas as pd
import sympy as sp
from tabulate import tabulate
from scipy.signal import StateSpace
import scipy.optimize
from functools import partial
import control as ct
from scipy.linalg import eig
from scipy.signal import ss2tf

class ODEtool:
    """
    Provides mathematical tools for manipulating ODE and DAE systems, including state-space conversion, eigenvalue analysis, and operating point calculation.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the ODEtool object and its parameters.
        """
        super().__init__(*args, **kwargs)
        self.params = dict()
    #Create system of ODEs from DAE-System by eliminating the algebraic variables
    def combine_odes_algebraic(self):
        """
        Eliminate algebraic variables from the DAE system to obtain a pure ODE system.
        Updates self.odes by substituting solutions for algebraic variables (self.z).
        """
        # Step 1: Solve algebraic equations for algebraic variables
        alg_sol = sp.solve(self.algebraic, self.z)
        if (alg_sol == []) and self.LOG:
            print('Unable to solve for algebraic variables!')
        # Step 2: Substitute algebraic solutions into ODEs
        self.odes = self.odes.subs(alg_sol)

    def set_input_values(self, v0, v1=np.array([]), params={}, show=True, dt=1e-15):
        """
        Set the input values for simulation, including step changes and simulation parameters.

        Args:
            v0: Initial input values (array-like).
            v1: Final input values (array-like, optional).
            params: Simulation parameters dictionary.
            show: If True, print the input table.
            dt: Small time increment for step change.
        Raises:
            ValueError: If input lengths do not match.
        """
        # Step 1: Check input lengths
        if len(self.u) != len(v0):
            raise ValueError("The lengths of u, v0, and v1 do not match!")
        if  len(self.u) != len(v1):
            v1 = v0
            noStep = True
        else:
            noStep = False

        # Step 2: Store simulation parameters
        self.params['sim_params'] = params

        # Step 3: Determine simulation time and step
        Tsim = self.params['sim_params']['Tsim']
        if 'Tstep' in self.params['sim_params'].keys():
            Tstep = self.params['sim_params']['Tstep']
        else:
            Tstep = 2 * self.params['sim_params']['Tsim']

        # Step 4: Build the input value array for simulation
        arr = np.array([0, Tstep, Tstep+dt, Tsim])
        for i,_ in enumerate(v0):
            arr = np.vstack([arr,np.array([v0[i],v0[i],v1[i],v1[i]])])
        self.u_val = arr 
        self.v0 = v0
        self.v1 = v1
        self.Tstep = Tstep

        # Step 5: Optionally print the input table
        if show:
            if noStep:
                df = pd.DataFrame({
                    "Param Name": self.u,
                    "v0 Value": v0,
                })
                print(f"\nInputs:")
                print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
            else:
                df = pd.DataFrame({
                    "Param Name": self.u,
                    "v0 Value": v0,
                    "v1 Value": v1
                })
                print(f"\nInputs: Step from v0 to v1 at {Tstep} s")
                print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))

    #TODO put this in print_pretty and removed
    def print_input(self):
        """
        Print a formatted table of the current input values and their names.
        """
        try:
            df = pd.DataFrame({
                "Param Name": self.u_str,
                "Internal Name": self.u,
                "v0 Value": self.u_val[1, :],
                "v1 Value": self.u_val[2, :]
            })
        except Exception:
            df = pd.DataFrame({
                "Param Name": self.u_str,
                "Internal Name": self.u,
            })

        print(f"\nInputs")
        print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))

    
    def get_eig(self, getPF=True, rightV=False):
        """
        Compute the eigenvalues and optionally participation factors of the state-space A matrix.

        Args:
            getPF: If True, compute participation factors.
            rightV: If True, return right eigenvectors as well.
        Returns:
            Eigenvalues, and optionally participation factors and right eigenvectors.
        """
        A = self.ss_sys.A
        w, vl, vr = eig(A, left=True, right=True)

        if getPF:
            PF = np.abs(vl * vr)
        else:
            PF = None
        if rightV:
            return w, vr, PF
        return w, PF

    
    def read_casadi(self):
        """
        Read and extract system variables and equations from a CasADi interface object.
        Raises:
            ValueError: If CasADi object is not initialized correctly.
        """
        try:
            self.y = sp.Matrix(self.casadi.y_subs) #outputs
            self.y_str = self.casadi.outputs #outputs_str
            self.u = sp.Matrix(list(self.casadi.sp_inputs.values()))
            self.u_str = self.casadi.inputs #inputs_str
            self.x = sp.Matrix(list(self.casadi.sp_states.values())) #states
            self.x_str = self.casadi.states #state string
            self.odes = sp.Matrix(self.casadi.eqs_subs) # odes

        except:
            raise ValueError('Casadi not initialized correclty!')

#    def get_tf(self,u_str,y_str):
#        if u_str in self.u_str:
#            i_u = self.u_str.index(u_str)
#            inverse = False
#        else:
#            i_y = self.y_str.index(u_str)
#            inverse = True
#
#        if not inverse:
#            i_y = self.y_str.index(y_str)
#        else:
#            i_u = self.u_str.index(y_str)
#
#        A = self.ss_sys.A
#        B = np.expand_dims(self.ss_sys.B[:,i_u],1)
#        C = np.expand_dims(self.ss_sys.C[i_y,:],0)
#        D = self.ss_sys.D[i_y,i_u]
#        num, den = ss2tf(A, B, C, D) 
#
#        if not inverse:
#            #self.tf = ct.ss2tf(A,B,C,D)
#            self.tf = ct.TransferFunction(np.squeeze(num), den)
#        else:
#            self.tf = 1 / ct.TransferFunction(np.squeeze(num), den)
#            self.tf = 1 / ct.ss2tf(A,B,C,D)

    # Create state-space representation
    def get_ss(self, info=True):
        """
        Compute the state-space representation (A, B, C, D matrices) from symbolic ODEs.
        Substitutes operating point and input values for numerical evaluation.

        Args:
            info: If True, print warnings if output is not set.
        """
        # Calculate Jacobians to form A and B matrices
        A_matrix = self.odes.jacobian(self.x)
        B_matrix = self.odes.jacobian(self.u)

        # Form C and D matrices similarly
        if len(self.y) > 0:
            C_matrix = self.y.jacobian(self.x)
            D_matrix = self.y.jacobian(self.u)
        else:
            if info:
                print('Output (y) not set. Setting to zero.')
            C_matrix = sp.Matrix(np.zeros_like(A_matrix))
            D_matrix = sp.Matrix(np.zeros_like(B_matrix))

        # Substitute operating points and any known inputs 
        op = self.op.tolist()
        subs = list(zip(self.x, op))

        u_val = self.u_val[1:,0]  
        subs = subs + list(zip(self.u, u_val))

        self.A_od = A_matrix.subs(subs)
        A_op = A_matrix.subs(subs).evalf()
        self.A_op = A_op
        B_op = B_matrix.subs(subs).evalf()
        C_op = C_matrix.subs(subs).evalf()
        D_op = D_matrix.subs(subs).evalf()

        # Convert SymPy matrices to NumPy arrays for numerical computations
        self.A = np.array(A_op).astype(np.float64)
        self.B = np.array(B_op).astype(np.float64)
        self.C = np.array(C_op).astype(np.float64)
        self.D = np.array(D_op).astype(np.float64)
        
        # Define the state-space system
        self.ss_sys = StateSpace(self.A, self.B, self.C, self.D)
    
#    def odes_lamdify(self):
#        """
#        Convert symbolic ODEs and outputs to numpy-callable functions for simulation.
#        Also substitutes input values for operating point evaluation.
#        """
#        state_inputs = list(sp.Matrix([self.x, sp.Matrix(self.u)]))
#        self.odes_np = [sp.lambdify(state_inputs, x, 'numpy') for x in self.odes]
#        if not hasattr(self,'y'):
#            self.y = []
#        self.y_np = [sp.lambdify(state_inputs, x, 'numpy') for x in self.y]
#
#
#        subs = {k : self.u_val[i+1,0].item() for i, k in enumerate(self.u)}
#        self.odes_ = sp.Matrix([x.subs(subs) for x in self.odes])
#        self.y_ = sp.Matrix([x.subs(subs) for x in self.y])
#
#        self.odes_np_ = [sp.lambdify(self.x, i, 'numpy') for i in self.odes_]
#        self.y_np_ = [sp.lambdify(self.x, i, 'numpy') for i in self.y_]
#
    def odes_lamdify(self):
        """
        Convert symbolic ODEs and outputs to single vectorized numpy-callable functions for simulation.
        Also substitutes input values for operating point evaluation.
        """
        # Create input vector: [x1, x2, ..., u1, u2, ...]
        state_inputs = list(sp.Matrix([self.x, sp.Matrix(self.u)]))

        # Convert full system of ODEs and outputs to vectorized lambdified functions
        self.odes_np = sp.lambdify(state_inputs, sp.Matrix(self.odes), 'numpy')

        if not hasattr(self, 'y'):
            self.y = []

        self.y_np = sp.lambdify(state_inputs, sp.Matrix(self.y), 'numpy')

        # Substitute input values to compute operating point expressions
        subs = {k: self.u_val[i + 1, 0].item() for i, k in enumerate(self.u)}
        self.odes_ = sp.Matrix([x.subs(subs) for x in self.odes])
        self.y_ = sp.Matrix([x.subs(subs) for x in self.y])

        self.odes_np_ = [sp.lambdify(self.x, i, 'numpy') for i in self.odes_]
        self.y_np_ = [sp.lambdify(self.x, i, 'numpy') for i in self.y_]


    def get_op_sim(self, duration=2, criteria=("v_C", "i_L", "xI_")):
        """
        Estimate the operating point by simulating the system for a short duration and using the result as an initial guess.

        Args:
            duration: Simulation time for the initial guess.
            criteria: Tuple of variable name prefixes to exclude from the guess.
        """
        # assuming available odes
        self.eval(f"Tsim_ = Tsim;")
        self.eval(f"Tstep_ = Tstep;")
        self.eval(f"Tsim = {duration};")
        self.eval(f"Tstep = {duration+1};")
        self.sim(ode=True)
        self.eval(f"Tsim = Tsim_;")
        self.eval(f"Tstep = Tstep_;")
        self.eval(f"clear Tsim_ Tstep_")
        self.eval(f"op_ = Y_nl(end,:);")
        nan_list = np.array([n for n, s in enumerate(self.x_str) if not s.startswith(criteria)]) + 1
        # Ensure nan_list is a 1D array
        nan_list = nan_list.flatten()

        # Convert to a MATLAB-compatible string (space-separated numbers in square brackets)
        nan_list_str = " ".join(map(str, nan_list))

        # Execute the MATLAB command
        self.eval(f"op_([{nan_list_str}]) = nan;")

        #self.eval(f"op_({nan_list}) = nan;")
        self.eval(f"initialGuess= [op_*.9; op_*1.1]';")
        self.get_op(matlab=True,initialGuess=True)
    
    # Find operating point
    def get_op(self, x0=None, bounds=None, get_ss=True):
        """
        Find the operating point (steady-state) of the system by solving the ODEs for equilibrium.

        Args:
            x0: Initial guess for the state vector.
            bounds: Bounds for the optimizer.
            get_ss: If True, update the state-space matrices at the operating point.
        """
        def residuals(fkt,x):
            return np.array([f(*x) for f in fkt])

        nx = len(self.x)
        if x0 == None:
            x0 = [0 for _ in range(nx)]

        if bounds == None:
            b_low = [-np.inf for _ in range(nx)]
            b_high = [np.inf for _ in range(nx)]
            bounds = [tuple(b_low), tuple(b_high)]
        

        residuals_fkt = partial(residuals,self.odes_np_)
        res = scipy.optimize.least_squares(residuals_fkt , x0, bounds=bounds)
        self.op = res.x

        # Verify operating point by substituting back into equations
        verified = residuals_fkt(self.op)
        print("Verification of operating point (should be close to 0):\n", verified)
        
        if get_ss:
            self.get_ss()

    def adapt_op(self, other_sys):
        """
        Adapt the operating point and input values from another system instance.

        Args:
            other_sys: Another system object with .x, .op, and .u_val attributes.
        """
        x_list = list(other_sys.x)
        self.op = np.array([other_sys.op[x_list.index(_x)] if _x in x_list else np.nan for _x in self.x])

        # ensure consistent inputs
        self.u_val = other_sys.u_val[0, :]
        for u in self.u:
            if u in other_sys.u:
                self.u_val = np.vstack([self.u_val, other_sys.u_val[other_sys.u.index(u) + 1, :]])
            else:
                print(f'Adding nan row for {u} as input.')
                row = np.empty((other_sys.u_val[0, :].shape))
                row[:] = np.nan
                self.u_val = np.vstack([self.u_val, row])
        

        