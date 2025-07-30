
"""
components_control.py
---------------------
This module defines symbolic control system components for ODE-based power system modeling.
Each control component class generates its own symbolic ODEs and algebraic laws for use in system simulation.
The structure is compatible with the Component base class from components_electric.
"""

from abc import ABC, abstractmethod
from components.components_electric import Component
from scipy.signal import TransferFunction, tf2ss
import control as ct
import sympy as sp
from sympy.abc import s
import numpy as np
from sympy.physics.control.lti import TransferFunction

class CtrlComponent(Component):
    """
    Abstract base class for control components.
    Inherits from Component and adds input/output port naming for control law connections.
    Automatically generates equations on initialization.
    """
    def __init__(self, component_id, u_in=None, u_out=None, properties=None, forceSymbol=False):
        self.id = component_id
        self.properties = properties
        self.u_in = u_in
        self.u_out = u_out
        self.forceSymbol = forceSymbol
        # Automatically generate the equations upon initialization
        self.equations = self.generate_equation()

###############################################################
### PI Control
###############################################################
class PI(CtrlComponent):
    """
    Proportional-Integral (PI) controller.
    State: xI (integrator state)
    Input: ref (reference)
    Algebraic law: output = Kp*(ref-u_in) + Ki*xI
    ODE: dxI/dt = ref - u_in
    """
    def generate_equation(self):
        if self.u_in is None:
            raise ValueError('No reference id for control set')
        u_in, u_out = self.u_in, self.u_out
        id = self.id
        p = self.properties
        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(id, ['Kp', 'Ki'])
        params = {k + '_' + str(id): v for k, v in p.items()}
        # State: xI, Input: ref
        x, u = self.set_vars_tuple(id, ['xI'], ['ref'])
        # Algebraic law for controller output
        law = {u_out: (p['Kp'] * (u.ref - u_in) + p['Ki'] * x.xI)}
        # ODE for integrator state
        odes = sp.Matrix([
            u.ref - u_in
        ])
        return {id: {'name': 'PI', 'odes': odes, 'x': x, 'u': u, 'params': params, 'id': id, 'type': 'ctrl', 'law': law}}

###############################################################
### Delay PI Control
###############################################################
class delayPI(CtrlComponent):
    """
    PI controller with input delay.
    States: Td (delay state), xI (integrator state)
    Input: ref (reference)
    Algebraic law: output = Kp*(ref - Td) + Ki*xI
    ODEs: dTd/dt = (-Td + u_in)/Td, dxI/dt = ref - Td
    """
    def generate_equation(self):
        if (self.u_in is None) or (self.u_out is None):
            raise ValueError('No reference id for control set')
        u_in, u_out = self.u_in, self.u_out
        id = self.id
        p = self.properties
        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(id, ['Kp', 'Ki', 'Td'])
        params = {k + '_' + str(id): v for k, v in p.items()}
        # States: Td, xI; Input: ref
        x, u = self.set_vars_tuple(id, ['Td', 'xI'], ['ref'])
        # Algebraic law for controller output
        law = {u_out: (p['Kp'] * (u.ref - x.Td) + p['Ki'] * x.xI)}
        # ODEs for delay and integrator
        odes = sp.Matrix([
            (-x.Td + u_in) / p['Td'],
            u.ref - x.Td,
        ])
        return {id: {'name': 'PI', 'odes': odes, 'x': x, 'u': u, 'params': params, 'id': id, 'type': 'ctrl', 'law': law}}

###############################################################
### LowPass PI
###############################################################
class LpPI(CtrlComponent):
    """
    Low-pass filtered PI controller.
    States: T_lp1, T_lp2, xI
    Input: ref
    Algebraic law: output = Kp*(ref - tfy) + xI
    ODEs: tfode (from transfer function), dxI/dt = Ki*(ref - tfy)
    """
    def generate_equation(self):
        if (self.u_in is None) or (self.u_out is None):
            raise ValueError('No reference id for control set')
        u_in, u_out = self.u_in, self.u_out
        id = self.id
        p = self.properties
        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(id, ['Kp', 'Ki', 'Fb', 'Td'])
        params = {k + '_' + str(id): v for k, v in p.items()}
        # States: T_lp1, T_lp2, xI; Input: ref
        x, u = self.set_vars_tuple(id, ['T_lp1', 'T_lp2', 'xI'], ['ref'])
        # Define transfer function for low-pass filter
        tf1 = TransferFunction(1, 1 + p['Td'] * s, s)
        tf = (tf1 * TransferFunction(p['Fb'] * 2 * sp.pi, s + p['Fb'] * 2 * sp.pi, s)).doit()
        tfode, tfy = tf2ode(tf, x[:-1], u_in)
        # Algebraic law for controller output
        law = {u_out: (p['Kp'] * (u[0] - tfy) + x[2])}
        # ODEs for filter and integrator
        odes = sp.Matrix([
            tfode,
            p['Ki'] * (u[0] - tfy),
        ])
        return {id: {'name': 'LpPI', 'odes': odes, 'x': x, 'u': u, 'x_str': None, 'u_str': None, 'params': params, 'id': id, 'type': 'ctrl', 'law': law}}


class delayLpPIDroop(CtrlComponent):
    """
    Low-pass filtered PI controller with droop control and input delay.
    States: T_lp1, T_lp2, xI, T_lp3
    Input: ref
    Algebraic law: output = Kp*(u_droop - tfy) + xI
    ODEs: tfode (from transfer function), dxI/dt = Ki*(u_droop - tfy), tfode2 (droop filter)
    """
    def generate_equation(self):
        if (self.u_in is None) or (self.u_out is None):
            raise ValueError('No reference id for control set')
        u_in, u_out = self.u_in, self.u_out
        id = self.id
        p = self.properties
        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(id, ['Kp', 'Ki', 'Fb', 'Fb_d', 'Td', 'K_d', 'P_d'])
        params = {k + '_' + str(id): v for k, v in p.items()}
        # States: T_lp1, T_lp2, xI, T_lp3; Input: ref
        x, u = self.set_vars_tuple(id, ['T_lp1', 'T_lp2', 'xI', 'T_lp3'], ['ref'])
        tf1 = TransferFunction(1, 1 + p['Td'] * s, s)
        tf = (tf1 * TransferFunction(p['Fb'] * 2 * sp.pi, s + p['Fb'] * 2 * sp.pi, s)).doit()
        tf2 = (TransferFunction(p['Fb_d'] * 2 * sp.pi, s + p['Fb_d'] * 2 * sp.pi, s)).doit()
        P = u_in[0] * u_in[1]  # Voltage * Current
        tfode, tfy = tf2ode(tf, x[:2], u_in[0])
        tfode2, tfy2 = tf2ode(tf2, x[-1:], P)
        u_droop = u[0] * (1 - p['K_d'] * tfy2 / p['P_d'])
        # Algebraic law for controller output
        law = {u_out: (p['Kp'] * (u_droop - tfy) + x[2])}
        # ODEs for filter, integrator, and droop
        odes = sp.Matrix([
            tfode,
            p['Ki'] * (u_droop - tfy),
            tfode2
        ])
        return {id: {'name': 'LpPIDroop', 'odes': odes, 'x': x, 'u': u, 'params': params, 'id': id, 'type': 'ctrl', 'law': law}}

###############################################################
### Generic TF
###############################################################

# TODO NOT WORKING YET!!!!
class tf_fkt(CtrlComponent):
    """
    Generic transfer function controller (not fully implemented).
    """
    def generate_equation(self):
        # TODO: Not working yet!
        if (self.u_in is None) or (self.u_out is None):
            raise ValueError('No reference id for control set')
        u_in, u_out = self.u_in, self.u_out
        id = self.id
        p = self.properties
        # Parameter definition
        if self.forceSymbol or p is None:
            p = self.set_default_params(id, ['_tf'])
        params = {k + '_' + str(id): v for k, v in p.items()}
        x, x_str, u, u_str = self.set_vars(id, ['T_lp1', 'T_lp2', 'xI'], ['ref'])
        tf1 = TransferFunction(1, 1 + p['Td'] * s, s)
        tf = (tf1 * TransferFunction(p['Fb'] * 2 * sp.pi, s + p['Fb'] * 2 * sp.pi, s)).doit()
        tfode, tfy = tf2ode(tf, x[:-1], u_in)
        # Algebraic law for controller output
        law = {u_out: (p['Kp'] * (u[0] - tfy) + x[2])}
        # ODEs for filter and integrator
        odes = sp.Matrix([
            tfode,
            p['Ki'] * (u[0] - tfy),
        ])
        return {id: {'name': 'LpPI', 'odes': odes, 'x': x, 'u': u, 'x_str': x_str, 'u_str': u_str, 'params': params, 'id': id, 'type': 'ctrl', 'law': law}}

def symbolic_tf_to_numeric(tf_sympy):
    """
    Convert a sympy TransferFunction to numeric coefficient lists for use with scipy.signal.tf2ss.
    Args:
        tf_sympy: sympy.physics.control.lti.TransferFunction
    Returns:
        (num_coeffs, den_coeffs): Lists of numerator and denominator coefficients.
    """
    num_expr = sp.Poly(tf_sympy.num, s)
    den_expr = sp.Poly(tf_sympy.den, s)
    num_coeffs = [float(c) for c in num_expr.all_coeffs()]
    den_coeffs = [float(c) for c in den_expr.all_coeffs()]
    return num_coeffs, den_coeffs

def tf2ode(tf_sympy, x, u):
    """
    Convert a sympy TransferFunction to state-space ODEs and output equation.
    Args:
        tf_sympy: sympy.physics.control.lti.TransferFunction
        x: state vector (sympy symbols)
        u: input symbol
    Returns:
        dx: ODEs for state vector
        y: output equation
    """
    num, den = symbolic_tf_to_numeric(tf_sympy)
    A, B, C, D = tf2ss(num, den)
    A = sp.Matrix(A)
    B = sp.Matrix(B)
    C = sp.Matrix(C)
    D = sp.Matrix(D)
    x = sp.Matrix(x)
    dx = A * x + B * u
    y = C * x + D * u
    return dx, y[0]