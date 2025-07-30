# %%
from ODEpower.tool import *
import os
import numpy as np
import sympy as sp
from functools import reduce
from pathlib import Path
import subprocess

# Define custom functions for reading casadi
class sq(sp.Function):
    @classmethod
    def eval(cls, x):
        return x**2

# Define custom functions for reading casadi
class fabs(sp.Function):
    @classmethod
    def eval(cls, x):
        return np.abs(x)

class casadiWrapper:
    def __init__(self,casadi_path : str,DEBUG=False):
        self.casadi = casadiInterface(casadi_path, self.model_path, self.matlab, DEBUG=DEBUG)

class casadiInterface:
    def __init__(self,casadi_path : str, model_path, matlab_eng,DEBUG):
        self.DEBUG= DEBUG
        self.casadi_path = Path(casadi_path)
        self.matlab = matlab_eng
        self.model_path = model_path
        self.add_casadi()

    def eval(self,cmd,out=0):
        if self.DEBUG:
            print(cmd)
        return self.matlab.eval(cmd,nargout=out) 


    def add_casadi(self):
        self.eval(f"addpath('{str(self.casadi_path)}');",0)
        self.eval(f"addpath('{str(self.casadi_path / 'build')}');",0)
        self.eval(f"addpath('{str(self.casadi_path / 'casadi')}');",0)
        self.eval(f"addpath('{str(self.casadi_path / 'include')}');",0)
        self.eval(f"addpath('{str(self.casadi_path / 'model_classes')}');",0)
        self.eval(f"addpath('{str(self.casadi_path / 'utils')}');",0)
        self.eval(f"casadi_path = '{self.casadi_path}';")
        self.run_script = self.casadi_path / 'run.py'
    
    def set_model(self,model_path):
        self.eval(f"addpath('{str(os.path.dirname(model_path))}');",0)
        self.model = os.path.splitext(os.path.basename(model_path))[0] 
        self.eval(f'model_file = "{self.model}";')
        self.eval(f'load_system(model_file);')

    def writeODEs(self, ODEs, x, u, name=None):
        if name == None:
            import names
            self.name = names.get_first_name()

        with open(f'{str(self.model_path / name)}.m','w') as f:
            [f.write(f"inputs.{inpt} = sym('{inpt}','real');\n") for i, inpt in enumerate(u)]
            f.write('\n')
            [f.write(f"states.{state} = sym('{state}','real');\n") for state in x]

            f.write('\n[inputVariables, stateVariables] = eval_input_states(inputs,states);\n\n')

            [f.write(f"pyodes.{x[i]} = {eq};\n") for i, eq in enumerate(ODEs)]
            f.write('\n')

    def set_WS(self,params,clear=True):
            # self.eval(f'mdlWks = get_param("{self.model}","ModelWorkspace");')
            #if clear:
                #self.eval(f'clear(mdlWks);')
            for p,v in params.items():
                #self.eval(f'assignin(mdlWks, "{p}",{v});')
                self.eval(f'{p} = {v};')

    # Compile model
    def compile(self):
        # There is also an old run version where it works as one script
        self.eval(f"casadi_compile")
        file = self.eval(f"ref_model_path;",1)
        result = subprocess.run(
            ["python", self.run_script] + [file],
        )
        self.eval(f"casadi_compile2")




    def read_model(self, subs_params=False):
        self.eval(f"casadi_read")

        # Retrieve system parameters
        self.nx = int(self.eval('nx', 1))
        self.nu = int(self.eval('nu', 1))
        self.ny = int(self.eval('ny', 1))
        self.np = int(self.eval('np', 1))
        self.states = self.eval('states', 1)
        self.states = self.states[:self.nx] 
        self.inputs = self.eval('inputs', 1)
        self.outputs = self.eval('outputs', 1)

        # Remove internal states
        idx_keep = [i for i, o in enumerate(self.outputs) if not o.startswith('x_')]
        self.outputs = [self.outputs[i] for i in idx_keep]
        self.ny = len(idx_keep)

        # Retrieve and process parameters
        self.params = self.eval('params', 1)
        self.P = np.array(self.eval('P', 1))

        # Define symbols
        syms = {}
        sp_syms = {}
        if self.nx == 1:
            self.sp_states = {'x': sp.symbols('x')}
            self.sp_states2 = {sp.symbols('x'): sp.symbols('x')}
        else:
            self.sp_states = {f'x_{i}': sp.symbols(f'x_{i}') for i in range(self.nx)}
            self.sp_states2 = {sp.symbols(f'x_{i}'): sp.symbols(f'x_{i}') for i in range(self.nx)}
        syms.update(self.sp_states)
        sp_syms.update(self.sp_states2)

        if self.nu == 1:
            self.sp_inputs = {'u': sp.symbols('u')}
            self.sp_inputs2 = {'u': sp.symbols('u')}
        else:
            self.sp_inputs = {f'u_{i}': sp.symbols(f'u_{i}') for i in range(self.nu)}
            self.sp_inputs2 = {sp.symbols(f'u_{i}'): sp.symbols(f'u_{i}') for i in range(self.nu)}
        syms.update(self.sp_inputs)
        sp_syms.update(self.sp_inputs2)

        if self.np == 1:
            self.sp_params = {'p': sp.symbols('p')}
            self.sp_params2 = {sp.symbols('p'): self.P.item()}
        else:
            self.sp_params = {f'p_{i}': sp.symbols(f'p_{i}') for i in range(self.np)}
            self.sp_params2 = {sp.symbols(f'p_{i}'): self.P[i].item() for i in range(self.np)}
        syms.update(self.sp_params)
        if subs_params:
            sp_syms.update(self.sp_params2)
        self.syms = syms
        self.sp_syms = sp_syms

        # Parse equations
        self.ode_str = self.eval('eqs', 1)
        if '=' in self.ode_str:
            self.eqs = self.subs_eq(self.ode_str) 
        else:
            self.eqs = self.ode_str[1:-1].split(',')
            self.eqs = [sp.sympify(eq, locals=self.syms) for eq in self.eqs]

        self.y_str = self.eval('y', 1)
        self.idx_keep = idx_keep

        if '=' in self.y_str:
            self.y = self.subs_eq(self.y_str)
        else:
            self.y = self.y_str[1:-1].split(',')
            self.y= [sp.sympify(y, locals=self.syms) for y in self.y]

        self.y = [self.y[i] for i in idx_keep]
    
    # Substitute equations
    def subs_eq(self, eq):
        definitions_part, equations_part = eq.split(', [')
        definitions_list = definitions_part.split(', ')
        equations_list = equations_part.rstrip(']').split(', ')

        symbol_definitions = {}
        symbol_syms = {}  
        syms = self.syms.copy()
        syms.update({'sq': sq, 'fabs': fabs})
        # Process definitions to create sympy symbols and expressions
        for i, definition in enumerate(definitions_list):
            symbol_name, expression = definition.replace('@', 'sym').split('=')
            symbol = sp.symbols(symbol_name)  # Create a sympy symbol
            sympy_expression = sp.sympify(expression, locals=syms)

            # Evaluate the expression to sympy
            subs = {k: symbol_definitions[str(k)] for k in sympy_expression.free_symbols if str(k).startswith('sym')}
            subs.update(self.sp_syms)

            symbol_definitions[symbol_name] = sympy_expression.xreplace(subs).together()
            symbol_syms[symbol_name] = symbol 

        # Substitute symbols in equations
        substituted_equations = []
        for equation in equations_list:
            sympy_equation = sp.sympify(equation.replace('@', 'sym'), locals=symbol_syms)
            subs = {k: symbol_definitions[str(k)] for k in sympy_equation.free_symbols if str(k).startswith('sym')}
            subs.update(self.sp_syms)
            eq = sympy_equation.xreplace(subs).together()
            substituted_equations.append(eq)
        return substituted_equations

    # Substitute parameters
    def subs_params(self):
        subs = list(zip(self.sp_params.values(), self.P.tolist()))
        subs = [(v0, v1[0]) for v0, v1 in subs]

        self.eqs_subs = [x.subs(subs) for x in self.eqs]
        self.y_subs = [x.subs(subs) for x in self.y]
        state_inputs = list(self.sp_states.values()) + list(self.sp_inputs.values())
        self.eqs_np = [sp.lambdify(state_inputs, x, 'numpy') for x in self.eqs_subs]
        self.y_np = [sp.lambdify(state_inputs, x, 'numpy') for x in self.y_subs]

        # Subs inputs only if existing
        if self.nu > 0:
            self.U = self.input_vals[:,0]        
            subs = subs + list(zip(self.sp_inputs.values(), self.U.tolist()))
        self.eqs_subs_op = [x.subs(subs) for x in self.eqs]
        self.y_subs_op = [x.subs(subs) for x in self.y]
        state = list(self.sp_states.values()) 
        self.eqs_np_op = [sp.lambdify(state, x, 'numpy') for x in self.eqs_subs_op]
        self.y_np_op = [sp.lambdify(state, x, 'numpy') for x in self.y_subs_op]