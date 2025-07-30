#%%
from abc import ABC, abstractmethod
import sympy as sp
from collections import namedtuple


class Component(ABC):
    def __init__(self, component_id, properties=None,forceSymbol=False):
        self.id = component_id
        self.properties = properties
        self.forceSymbol = forceSymbol

        # Automatically generate the equations upon initialization
        self.equations = self.generate_equation()  # Generate equations on creation

    @abstractmethod
    def generate_equation(self, *args, **kwargs):
        """Generate the actual equations in the required format."""
        raise NotImplementedError("Subclasses should implement this method.")

    def get(self):
        return self.equations
    
    def set_default_params(self,id,p):
        return {x : sp.Symbol(f'{x}_{id}') for x in p}

    def set_vars(self,id,x_str,u_str):
        x = sp.Matrix(sp.symbols(['x'+str(id)+'_'+str(x) for x in range(len(x_str))]))
        x_str = [_x+'_'+str(id) for _x in x_str]

        # Input Symbols definition
        u = sp.Matrix(sp.symbols(['u'+str(id)+'_'+str(x) for x in range(len(u_str))]))
        u_str = [_x+'_'+str(id) for _x in u_str]
        return [x,x_str,u,u_str]

    def set_vars_tuple(self, id, x_str, u_str):
        # Define namedtuples
        nt_x = namedtuple('states', x_str)
        nt_u = namedtuple('inputs', u_str)

        # Create symbolic variables
        x_syms = sp.symbols([f'{name}_{id}' for name in x_str])
        u_syms = sp.symbols([f'{name}_{id}' for name in u_str])

        # Wrap in namedtuples
        x = nt_x(*x_syms)
        u = nt_u(*u_syms)

        return [x, u]

###############################################################
### piline
###############################################################
class piLine(Component):
    def generate_equation(self):
        """
        Generate the ODEs for a piLine component.

        States (x):
            v_Cin  : Voltage at input-side capacitor
            i_L    : Inductor current
            v_Cout : Voltage at output-side capacitor
        Inputs (u):
            i_in   : Input current
            i_out  : Output current

        Returns:
            dict: Contains symbolic ODEs, state/input namedtuples, and variable names for documentation.
        """
        id = self.id
        p = self.properties

        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(id, ['C', 'R_c', 'R', 'L', 'Len'])
        params = {k + '_' + str(id): v for k, v in p.items()}

        x, u = self.set_vars_tuple(id,
            ['v_Cin', 'i_L', 'v_Cout'],  # States
            ['i_in', 'i_out']            # Inputs
        )

        # ODE Equations using named attributes
        odes = sp.Matrix([
            (-x.i_L + u.i_in) / (p['C'] * p['Len'] / 2),
            (x.v_Cin + (u.i_in - x.i_L) * p['R_c'] - x.i_L * p['R'] * p['Len'] - x.v_Cout - (x.i_L - u.i_out) * p['R_c']) / (p['L'] * p['Len']),
            (x.i_L - u.i_out) / (p['C'] * p['Len'] / 2),
        ])

        return {id: {'name': 'piLine', 'odes': odes, 'x': x, 'u': u, 'params': params, 'id': id, 'type': 'electric', 'control': False}}

###############################################################
### piline + Rload
###############################################################
class piLineRload(Component):
    def generate_equation(self):
        """
        Generate the ODEs for a piLineRload component (piLine with resistive load).

        States (x):
            v_Cin  : Voltage at input-side capacitor
            i_L    : Inductor current
            v_Cout : Voltage at output-side capacitor
        Inputs (u):
            i_in   : Input current
        Outputs:
            i_load : Algebraic load current (computed internally)

        Returns:
            dict: Contains symbolic ODEs, state/input namedtuples, and variable names for documentation.
        """
        id = self.id
        p = self.properties
        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(id, ['C', 'R_c', 'R', 'L', 'Len'])
        params = {k + '_' + str(id): v for k, v in p.items()}

        x, u = self.set_vars_tuple(id,
            ['v_Cin', 'i_L', 'v_Cout'],  # States
            ['i_in']                     # Inputs
        )

        # Algebraic equation for load current
        i_load = (x.v_Cout + x.i_L * p['R_c']) / (p['R_c'] + p['R'])

        # ODE Equations using named attributes
        odes = sp.Matrix([
            (-x.i_L + u.i_in) / (p['C'] * p['Len'] / 2),
            (x.v_Cin + (u.i_in - x.i_L) * p['R_c'] - x.i_L * p['R'] * p['Len'] - x.v_Cout - (x.i_L - i_load) * p['R_c']) / (p['L'] * p['Len']),
            (x.i_L - i_load) / (p['C'] * p['Len'] / 2),
        ])
        
        return {id: {'name': 'piLineRload', 'odes': odes, 'x': x, 'u': u, 'params': params, 'id': id, 'type': 'electric', 'control': False}}
###############################################################
### loadVarRL
###############################################################
class loadVarRL(Component):
    def generate_equation(self):
        """
        Generate the ODEs for a loadVarRL component (variable resistor-inductor load).

        States (x):
            i_L    : Inductor current
        Inputs (u):
            v_in   : Input voltage
            R      : Load resistance (variable)

        Returns:
            dict: Contains symbolic ODEs, state/input namedtuples, and variable names for documentation.
        """
        id = self.id
        p = self.properties

        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(id, ['L'])
        params = {k + '_' + str(id): v for k, v in p.items()}

        x, u = self.set_vars_tuple(id,
            ['i_L'],           # States
            ['v_in', 'R']      # Inputs
        )

        # ODE Equations using named attributes
        odes = sp.Matrix([
            (u.v_in - u.R * x.i_L) / p['L']
        ])
        return {id: {'name': 'loadVarRL', 'odes': odes, 'x': x, 'u': u, 'params': params, 'id': id, 'type': 'electric', 'control': False}}

###############################################################
### loadRL
###############################################################
class loadRL(Component):
    def generate_equation(self):
        """
        Generate the ODEs for a loadRL component (fixed resistor-inductor load).

        States (x):
            i_L    : Inductor current
        Inputs (u):
            v_in   : Input voltage

        Returns:
            dict: Contains symbolic ODEs, state/input namedtuples, and variable names for documentation.
        """
        id = self.id
        p = self.properties

        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(id, ['L', 'R'])
        params = {k + '_' + str(id): v for k, v in p.items()}

        x, u = self.set_vars_tuple(id,
            ['i_L'],      # States
            ['v_in']      # Inputs
        )

        # ODE Equations using named attributes
        odes = sp.Matrix([
            (u.v_in - p['R'] * x.i_L) / p['L']
        ])
        return {id: {'name': 'loadRL', 'odes': odes, 'x': x, 'u': u, 'params': params, 'id': id, 'type': 'electric', 'control': False}}


###############################################################
### DAB FHA 
###############################################################
class dabFHA(Component):
    def generate_equation(self):
        """
        Generate the ODEs for a DAB FHA (Dual Active Bridge, Fundamental Harmonic Approximation) converter.

        States (x):
            v_Cout : Output capacitor voltage
            i_tR   : Transformer current (real part)
            i_tI   : Transformer current (imaginary part)
        Inputs (u):
            v_in   : Input voltage
            i_out  : Output current
            d      : Phase shift (degrees)

        Returns:
            dict: Contains symbolic ODEs, state/input namedtuples, and variable names for documentation.
        """
        id = self.id
        p = self.properties

        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(id, ['fs', 'Cout', 'Lt', 'N'])
        params = {k + '_' + str(id): v for k, v in p.items()}

        x, u = self.set_vars_tuple(id,
            ['v_Cout', 'i_tR', 'i_tI'],
            ['v_in', 'i_out', 'd']
        )

        ws = 2 * sp.pi * p['fs']
        u2 = u.d * sp.pi / 180

        odes = sp.Matrix([
            - x.i_tR * 2 / (sp.pi * p['Cout']) * sp.sin(u2)
            - x.i_tI * 2 / (sp.pi * p['Cout']) * sp.cos(u2)
            - u.i_out / p['Cout'],

            x.v_Cout * 4 / (sp.pi * p['Lt']) * sp.sin(u2)
            + x.i_tI * ws,

            x.v_Cout * 4 / (sp.pi * p['Lt']) * sp.cos(u2)
            - x.i_tR * ws
            - (4 * p['N']) / (sp.pi * p['Lt']) * u.v_in
        ])
        return {id: {'name': 'dabFHA', 'odes': odes, 'x': x, 'u': u, 'params': params, 'id': id, 'type': 'electric', 'control': False}}



###############################################################
### Vsource with R
###############################################################
class VsourceR(Component):
    def generate_equation(self):
        """
        Generate the ODEs for a voltage source with series resistance.

        States (x):
            (none)
        Inputs (u):
            v_in   : Source voltage

        Returns:
            dict: Contains symbolic ODEs, state/input namedtuples, and variable names for documentation.
        """
        id = self.id
        p = self.properties

        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(id, ['R'])
        params = {k + '_' + str(id): v for k, v in p.items()}

        x, u = self.set_vars_tuple(id,
            [],
            ['v_in']
        )

        odes = sp.Matrix([])
        return {id: {'name': 'VsourceR', 'odes': odes, 'x': x, 'u': u, 'params': params, 'id': id, 'type': 'electric', 'control': False}}

###############################################################
### load var Resistor
###############################################################
class loadVarR(Component):
    def generate_equation(self):
        """
        Generate the ODEs for a variable resistor load.

        States (x):
            (none)
        Inputs (u):
            R      : Load resistance (variable)

        Returns:
            dict: Contains symbolic ODEs, state/input namedtuples, and variable names for documentation.
        """
        id = self.id
        p = self.properties

        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(id, [])
        params = {k + '_' + str(id): v for k, v in p.items()}

        x, u = self.set_vars_tuple(id,
            [],
            ['R']
        )

        odes = sp.Matrix([])
        return {id: {'name': 'loadVarR', 'odes': odes, 'x': x, 'u': u, 'params': params, 'id': id, 'type': 'electric', 'control': False}}



###############################################################
### Boost
###############################################################

class boost(Component):
    def generate_equation(self):
        """
        Generate the ODEs for a boost converter.

        States (x):
            v_Cin  : Input capacitor voltage
            v_Cout : Output capacitor voltage
            i_L    : Inductor current
        Inputs (u):
            i_in   : Input current
            i_out  : Output current
            d      : Duty cycle (switch control)

        Returns:
            dict: Contains symbolic ODEs, state/input namedtuples, and variable names for documentation.
        """
        id = self.id
        p = self.properties

        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(id, ['Cin', 'Cout', 'L', 'rD', 'rDS', 'rL', 'vD', 'rD'])
        params = {k + '_' + str(id): v for k, v in p.items()}

        x, u = self.set_vars_tuple(id,
            ['v_Cin', 'v_Cout', 'i_L'],
            ['i_in', 'i_out', 'd']
        )

        d_ = 1 - u.d
        d = u.d
        #########
        # ALTERNATIVE ODE FORMS (for reference/debugging):

        # --- Reduced ODE using i_out (no parasitic resistances)
        # odes = sp.Matrix([
        #     (u.i_in - x.i_L) / p['Cin'],
        #     (1 - u.d) * x.i_L / p['Cout'] - u.i_out / p['Cout'],
        #     -p['vD'] * (1 - u.d) / p['L'] + u.i_in / p['L'] - (1 - u.d) * x.v_Cin / p['L']
        # ])

        # --- Alternative with direct Rload modeling instead of i_out
        # R = sp.symbols('R')
        # odes = sp.Matrix([
        #     (u.i_in - x.i_L) / p['Cin'],
        #     (1 - u.d) * x.i_L / p['Cout'] - x.v_Cout / (R * p['Cout']),
        #     -p['vD'] * (1 - u.d) / p['L'] + u.i_in / p['L'] - (1 - u.d) * x.v_Cin / p['L']
        # ])
        odes = sp.Matrix([
            (u.i_in - x.i_L) / p['Cin'],
            (d_ * x.i_L - u.i_out) / p['Cout'],
            (
                d * (x.v_Cin - x.i_L * (p['rL'] + p['rDS'])) +
                d_ * (x.v_Cin - x.v_Cout - x.i_L * (p['rL'] + p['rD']) - p['vD'])
            ) / p['L']
        ])
        return {id: {'name': 'boost', 'odes': odes, 'x': x, 'u': u, 'params': params, 'id': id, 'type': 'electric', 'control': False}}


###############################################################
### Buck
###############################################################

class buck(Component):
    def generate_equation(self):
        """
        Generate the ODEs for a buck converter.

        States (x):
            v_Cout : Output capacitor voltage
            i_L    : Inductor current
        Inputs (u):
            v_in   : Input voltage
            i_out  : Output current
            d      : Duty cycle (switch control)

        Returns:
            dict: Contains symbolic ODEs, state/input namedtuples, and variable names for documentation.
        """
        id = self.id
        p = self.properties

        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(id, ['Cout', 'L', 'R_c', 'R_d', 'R_ds', 'R_l', 'V_d'])
        params = {k + '_' + str(id): v for k, v in p.items()}

        x, u = self.set_vars_tuple(id,
            ['v_Cout', 'i_L'],
            ['v_in', 'i_out', 'd']
        )

        d = u.d

        odes = sp.Matrix([
            (x.i_L - u.i_out) / p['Cout'],
            (u.v_in * d - x.v_Cout) / p['L']
        ])

        #########
        # ALTERNATIVE: Full model with parasitic resistances (from Suntio 2018, pg 133)
        # odes = sp.Matrix([
        #     # Output capacitor dynamics (with resistive drop across R_c)
        #     x.i_L / p['Cout'] - u.i_out / p['Cout'],
        #     
        #     # Inductor dynamics with ON and OFF stage contributions
        #     d * ((u.v_in - (p['R_l'] + p['R_ds'] + p['R_c']) * x.i_L - x.v_Cout + p['R_c'] * u.i_out) / p['L']) -
        #     d_ * (((p['R_l'] + p['R_d'] + p['R_c']) * x.i_L + x.v_Cout - p['R_c'] * u.i_out + p['V_d']) / p['L'])
        # ])
        return {id: {'name': 'buck', 'odes': odes, 'x': x, 'u': u, 'params': params, 'id': id, 'type': 'electric', 'control': False}}

class dabGAM(Component):
    def generate_equation(self):
        """
        Generate the ODEs for a DAB GAM (Dual Active Bridge, Generalized Averaged Model) converter.

        States (x):
            i_t{k}R : Harmonic k transformer current (real part), for k=1..order
            i_t{k}I : Harmonic k transformer current (imag part), for k=1..order
            v_Cin   : Input capacitor voltage
            v_Cout  : Output capacitor voltage
        Inputs (u):
            i_in    : Input current
            i_out   : Output current
            d       : Phase shift (degrees)

        Returns:
            dict: Contains symbolic ODEs, state/input namedtuples, and variable names for documentation.
        """
        id = self.id
        p = self.properties
        order = p.get('order', 1)  # M (number of harmonics)

        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(
                id,
                ['fs', 'Cin', 'Cout', 'Lt', 'Rt', 'N']
            )
        params = {k + '_' + str(id): v for k, v in p.items()}

        # Extract parameters
        fs, N, Lt, Rt, Cin, Cout = p['fs'], p['N'], p['Lt'], p['Rt'], p['Cin'], p['Cout']
        ws = 2 * sp.pi * fs  # Angular frequency

        # Define state variable names dynamically based on harmonic order
        state_names = []
        for k in range(1, order + 1):
            if not (k & 1):
                continue
            state_names.append(f'i_t{k}R')
            state_names.append(f'i_t{k}I')
        state_names.extend(['v_Cin', 'v_Cout'])

        # Use named tuples for states and inputs
        x, u = self.set_vars_tuple(id, state_names, ['i_in', 'i_out', 'd'])

        # Correction factor for output capacitor (if present)
        if p.get('correction', 1):
            correction = 1
        else:
            correction = (((sp.pi) * (sp.pi) * u.d) * (1 - (u.d / sp.pi))) / (8 * sp.sin(u.d))

        u2 = u.d * sp.pi / 180  # Phase shift in radians

        # ODE for input capacitor voltage (Cin)
        sum_cin = u.i_in / Cin
        sum_cout = -u.i_out / (Cout * correction)

        for k in range(1, order + 1):
            if not (k & 1):
                continue
            iR = getattr(x, f'i_t{k}R')
            iI = getattr(x, f'i_t{k}I')
            sum_cin += (0 / (sp.pi * Cin * k)) * iR + (2 / (sp.pi * Cin * k)) * iI
            sum_cout += N * (
                (-2 / (sp.pi * Cout * k)) * iR * sp.sin(k * u2) +
                (-2 / (sp.pi * Cout * k)) * iI * sp.cos(k * u2)
            )

        # Harmonic inductor dynamics (real/imag parts)
        odes = []
        for k in range(1, order + 1):
            if not (k & 1):
                continue
            iR = getattr(x, f'i_t{k}R')
            iI = getattr(x, f'i_t{k}I')

            expr_iR = (
                x.v_Cout * 4 * N * sp.sin(k * u2) / (k * sp.pi)
                - Rt * iR
            ) / Lt + k * ws * iI

            expr_iI = (
                x.v_Cout * 4 * N * sp.cos(k * u2) / (k * sp.pi)
                - 4 * x.v_Cin / (k * sp.pi)
                - Rt * iI
            ) / Lt - k * ws * iR

            odes.append(expr_iR)
            odes.append(expr_iI)

        # Append capacitor voltage dynamics
        odes.append(sum_cin)
        odes.append(sum_cout)

        return {
            id: {'name': 'dabGAM',
                'odes': sp.Matrix(odes),
                'x': x,
                'u': u,
                'params': params,
                'id': id,
                'type': 'electric',
                'control': False
            }
        }

class dabGAM2(Component):
    def generate_equation(self):
        """
        Generate the ODEs for a DAB GAM (Dual Active Bridge, Generalized Averaged Model) converter.

        States (x):
            i_t{k}R : Harmonic k transformer current (real part), for k=1..order
            i_t{k}I : Harmonic k transformer current (imag part), for k=1..order
            v_Cin   : Input capacitor voltage
            v_Cout  : Output capacitor voltage
        Inputs (u):
            i_in    : Input current
            i_out   : Output current
            d       : Phase shift (degrees)

        Returns:
            dict: Contains symbolic ODEs, state/input namedtuples, and variable names for documentation.
        """
        id = self.id
        p = self.properties
        order = p.get('order', 1)  # M (number of harmonics)

        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(
                id,
                ['fs', 'Cin', 'Cout', 'Lt', 'Rt', 'N', 'RL']
            )
        params = {k + '_' + str(id): v for k, v in p.items()}

        # Extract parameters
        fs, N, Lt, Rt, Cin, Cout, RL = p['fs'], p['N'], p['Lt'], p['Rt'], p['Cin'], p['Cout'], p['RL']
        ws = 2 * sp.pi * fs  # Angular frequency

        # Define state variable names dynamically based on harmonic order
        state_names = []
        for k in range(1, order + 1):
            if not (k & 1):
                continue
            state_names.append(f'i_t{k}R')
            state_names.append(f'i_t{k}I')
        state_names.extend(['v_Cin', 'v_Cout'])

        # Use named tuples for states and inputs
        x, u = self.set_vars_tuple(id, state_names, ['i_in', 'd'])

        # Correction factor for output capacitor (if present)
        if p.get('correction', 1):
            correction = 1
        else:
            correction = (((sp.pi) * (sp.pi) * u.d) * (1 - (u.d / sp.pi))) / (8 * sp.sin(u.d))

        u2 = u.d * sp.pi / 180  # Phase shift in radians

        # ODE for input capacitor voltage (Cin)
        sum_cin = u.i_in / Cin
        sum_cout = -x.v_Cout / ( RL * Cout * correction)

        for k in range(1, order + 1):
            if not (k & 1):
                continue
            iR = getattr(x, f'i_t{k}R')
            iI = getattr(x, f'i_t{k}I')
            sum_cin += (0 / (sp.pi * Cin * k)) * iR + (2 / (sp.pi * Cin * k)) * iI
            sum_cout += N * (
                (-2 / (sp.pi * Cout * k)) * iR * sp.sin(k * u2) +
                (-2 / (sp.pi * Cout * k)) * iI * sp.cos(k * u2)
            )

        # Harmonic inductor dynamics (real/imag parts)
        odes = []
        for k in range(1, order + 1):
            if not (k & 1):
                continue
            iR = getattr(x, f'i_t{k}R')
            iI = getattr(x, f'i_t{k}I')

            expr_iR = (
                x.v_Cout * 4 * N * sp.sin(k * u2) / (k * sp.pi)
                - Rt * iR
            ) / Lt + k * ws * iI

            expr_iI = (
                x.v_Cout * 4 * N * sp.cos(k * u2) / (k * sp.pi)
                - 4 * x.v_Cin / (k * sp.pi)
                - Rt * iI
            ) / Lt - k * ws * iR

            odes.append(expr_iR)
            odes.append(expr_iI)

        # Append capacitor voltage dynamics
        odes.append(sum_cin)
        odes.append(sum_cout)

        return {
            id: {'name': 'dabGAM',
                'odes': sp.Matrix(odes),
                'x': x,
                'u': u,
                'params': params,
                'id': id,
                'type': 'electric',
                'control': False
            }
        }