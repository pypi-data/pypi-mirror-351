
#%%
import sympy as sp

class AlgebraicEquation:
    """
    Class for generating algebraic connection equations between different power system components.
    Each method defines the algebraic constraints for a specific pair of connected components.
    The equations are now written using named attributes (e.g., x.v_Cin) for clarity and maintainability.
    """
    def __init__(self, graph):
        """
        Initialize the AlgebraicEquation class.
        Args:
            graph: The networkx graph containing component nodes and their attributes.
        """
        self.graph = graph
        self.component_equations = {
            ('piLine', 'loadVarRL'): self.eq_piLine_loadVarRL, # Not testes
            ('piLine', 'loadVarR'): self.eq_piLine_loadVarR, # Not testes
            #('dabFHA', 'piLine'): self.eq_dabFHA_piLine, # Not testes
            ('dabGAM', 'piLine'): self.eq_dabGAM_piLine,
            #('boost', 'piLine'): self.eq_boost_piLine,
            #('buck', 'piLine'): self.eq_buck_piLine,
            #('buck', 'loadVarRL'): self.eq_buck_loadRL,
            #('buck', 'loadRL'): self.eq_buck_loadRL,
            ('dabGAM', 'loadVarR'): self.eq_dabGAM_loadVarR,
            ('piLine', 'dabGAM'): self.eq_piLine_dabGAM,
            #('piLine', 'boost'): self.eq_piLine_boost,
            ('piLine', 'piLine'): self.eq_piLine_piLine,
            ('VsourceR', 'piLine'): self.eq_VsourceR_piLine,
            ('VsourceR', 'dabGAM'): self.eq_VsourceR_dabGAM,
            #('VsourceR', 'boost'): self.eq_VsourceR_boost,
            ('dabGAM', 'loadVarRL'): self.eq_dabGAM_loadVarRL,
            ('dabGAM', 'loadRL'): self.eq_dabGAM_loadRL,
        }

    def get_info(self, node1, node2):
        """
        Retrieve state and input namedtuples for two nodes.
        Args:
            node1: Node key for the first component.
            node2: Node key for the second component.
        Returns:
            Tuple of (x1, u1, x2, u2) namedtuples.
        """
        return self.graph.nodes[node1]['x'], self.graph.nodes[node1]['u'], self.graph.nodes[node2]['x'], self.graph.nodes[node2]['u']

    def generate_equations(self, node1, node2):
        """
        Generate algebraic equations for the connection between two components.
        Args:
            node1: Node attribute dict for the first component (must include 'name' and 'id').
            node2: Node attribute dict for the second component (must include 'name' and 'id').
        Returns:
            sympy.Matrix: Algebraic constraint equations for the connection.
        """
        try:
            return self.component_equations.get((node1['name'], node2['name']))(node1['id'], node2['id'])
        except Exception as e:
            raise ValueError(f"Equation generation not defined for {node1['name']} and {node2['name']}: {e}")

    # --- Connection Equations ---

    def eq_piLine_loadVarRL(self, node1, node2):
        """
        Connect piLine (node1) to loadVarRL (node2).
        Enforces current continuity and voltage at the output node.
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        Cline_r = self.graph.nodes[node1]['params'][f'R_c_{node1}']
        return sp.Matrix([
            u_1.i_out - x_2.i_L,  # Output current of piLine = inductor current of loadVarRL
            x_1.v_Cout + (x_1.i_L - u_1.i_out) * Cline_r - u_2.v_in,  # Output voltage continuity
        ])

    def eq_dabGAM_loadVarRL(self, node1, node2):
        """
        Connect dabGAM (node1) to loadVarRL (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        return sp.Matrix([
            u_1.i_out - x_2.i_L,
            x_1.v_Cout - u_2.v_in,
        ])

    def eq_dabGAM_loadRL(self, node1, node2):
        """
        Connect dabGAM (node1) to loadRL (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        return sp.Matrix([
            u_1.i_out - x_2.i_L,
            x_1.v_Cout - u_2.v_in,
        ])

    def eq_piLine_loadVarR(self, node1, node2):
        """
        Connect piLine (node1) to loadVarR (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        Cline_r = self.graph.nodes[node1]['params'][f'R_c_{node1}']
        return sp.Matrix([
            x_1.v_Cout + (x_1.i_L - u_1.i_out) * Cline_r - u_1.i_out * u_2.R,
        ])

    def eq_VsourceR_piLine(self, node1, node2):
        """
        Connect VsourceR (node1) to piLine (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        R = self.graph.nodes[node1]['params'][f'R_{node1}']
        Cline_r = self.graph.nodes[node2]['params'][f'R_c_{node2}']
        return sp.Matrix([
            -u_1.v_in + R * u_2.i_in + x_2.v_Cin + (u_2.i_in - x_2.i_L) * Cline_r
        ])

    def eq_dabGAM_piLine(self, node1, node2):
        """
        Connect dabGAM (node1) to piLine (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        Cline_r = self.graph.nodes[node2]['params'][f'R_c_{node2}']
        return sp.Matrix([
            u_1.i_out - u_2.i_in,
            x_1.v_Cout - x_2.v_Cin - (u_2.i_in - x_2.i_L) * Cline_r,
        ])

    def eq_boost_piLine(self, node1, node2):
        """
        Connect boost (node1) to piLine (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        Cline_r = self.graph.nodes[node2]['params'][f'R_c_{node2}']
        return sp.Matrix([
            u_1.i_out - u_2.i_in,
            x_1.v_Cout - x_2.v_Cin - (u_2.i_in - x_2.i_L) * Cline_r,
        ])

    def eq_dabFHA_piLine(self, node1, node2):
        """
        Connect dabFHA (node1) to piLine (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        Cline_r = self.graph.nodes[node2]['params'][f'R_c_{node2}']
        return sp.Matrix([
            u_1.i_out - u_2.i_in,
            x_1.v_Cout - x_2.v_Cin - (u_2.i_in - x_2.i_L) * Cline_r,
        ])

    def eq_piLine_dabGAM(self, node1, node2):
        """
        Connect piLine (node1) to dabGAM (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        Cline_r = self.graph.nodes[node1]['params'][f'R_c_{node1}']
        return sp.Matrix([
            u_1.i_out - u_2.i_in,
            x_2.v_Cin - x_1.v_Cout - (-u_1.i_out + x_1.i_L) * Cline_r,
        ])

    def eq_piLine_boost(self, node1, node2):
        """
        Connect piLine (node1) to boost (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        Cline_r = self.graph.nodes[node1]['params'][f'R_c_{node1}']
        return sp.Matrix([
            u_1.i_out - u_2.i_in,
            x_2.v_Cin - x_1.v_Cout - (-u_1.i_out + x_1.i_L) * Cline_r,
        ])

    def eq_VsourceR_dabGAM(self, node1, node2):
        """
        Connect VsourceR (node1) to dabGAM (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        R = self.graph.nodes[node1]['params'][f'R_{node1}']
        return sp.Matrix([
            x_2.v_Cin + u_2.i_in * R - u_1.v_in,
        ])

    def eq_VsourceR_boost(self, node1, node2):
        """
        Connect VsourceR (node1) to boost (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        R = self.graph.nodes[node1]['params'][f'R_{node1}']
        return sp.Matrix([
            x_2.v_Cin + u_2.i_in * R - u_1.v_in,
        ])

    def eq_dabGAM_loadVarR(self, node1, node2):
        """
        Connect dabGAM (node1) to loadVarR (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        return sp.Matrix([
            u_1.i_out - x_1.i_tI / u_2.R
        ])

    def eq_buck_piLine(self, node1, node2):
        """
        Connect buck (node1) to piLine (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        R_c1 = self.graph.nodes[node2]['params'][f'R_c_{node2}']
        R_c2 = self.graph.nodes[node1]['params'][f'R_c_{node1}']
        return sp.Matrix([
            u_1.i_out - u_2.i_in,
            (x_1.v_Cout + ((x_1.i_L - u_1.i_out) * (1-u_1.d) + (-u_1.i_out) * u_1.d) * R_c2) - x_2.v_Cin - (u_2.i_in - x_2.i_L) * R_c1,
        ])

    def eq_boost_loadRL(self, node1, node2):
        """
        Connect boost (node1) to loadRL (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        R_c1 = self.graph.nodes[node1]['params'][f'R_c_{node1}']
        # Not implemented: requires model-specific details
        return sp.Matrix([])

    def eq_buck_loadRL(self, node1, node2):
        """
        Connect buck (node1) to loadRL (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        R_c1 = self.graph.nodes[node1]['params'][f'R_c_{node1}']
        return sp.Matrix([
            u_1.i_out - x_2.i_L,
            (x_1.v_Cout + (x_1.i_L - u_1.i_out) * R_c1) - u_2.v_in,
        ])

    def eq_piLine_loadRL(self, node1, node2):
        """
        Connect piLine (node1) to loadRL (node2).
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        R_c1 = self.graph.nodes[node1]['params'][f'R_c_{node1}']
        return sp.Matrix([
            u_1.i_out - x_2.i_L,
            x_1.v_Cout + (x_1.i_L - u_1.i_out) * R_c1 - u_2.v_in,
        ])

    def eq_piLine_piLine(self, node1, node2):
        """
        Connect piLine (node1) to piLine (node2).
        Node 2 is the reference line. KCL must be row 0.
        """
        x_1, u_1, x_2, u_2 = self.get_info(node1, node2)
        R_c1 = self.graph.nodes[node1]['params'][f'R_c_{node1}']
        R_c2 = self.graph.nodes[node2]['params'][f'R_c_{node2}']
        return sp.Matrix([
            u_1.i_out - u_2.i_in,
            x_1.v_Cout + (x_1.i_L - u_1.i_out) * R_c1 - (x_2.v_Cin + (u_2.i_in - x_2.i_L) * R_c2)
        ])

