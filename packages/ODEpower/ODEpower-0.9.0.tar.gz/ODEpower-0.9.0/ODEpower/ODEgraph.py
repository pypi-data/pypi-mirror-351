#%%
from components.connection import AlgebraicEquation
from components.components_electric import *
from tabulate import tabulate
import pandas as pd

import sympy as sp
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class ODEgraph:
    """
    Class for constructing and managing the network graph of the power system.
    Handles nodes (components), edges (connections), and equation aggregation.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the ODEgraph object.
        Creates an empty undirected graph and sets up the equation generator.
        """
        super().__init__(*args, **kwargs)
        self.graph = nx.Graph()  # Undirected graph to represent the grid
        self.equation_generator = AlgebraicEquation(self.graph)
        self.sim_params = {}
    
    def graph_reset(self):
        """
        Reset the graph and equation generator to an empty state.
        """
        self.graph = nx.Graph()  # Undirected graph to represent the grid
        self.equation_generator = AlgebraicEquation(self.graph)
        self.sim_params = {}

    def add_node(self, component):
        """
        Add a node (electrical component) to the graph.

        Args:
            component: The component object to add (must have .id and .get()).
        Raises:
            ValueError: If the node already exists.
        """
        if component.id in self.graph:
            raise ValueError(f"Node {component.id} already exists.")
        # Add the component with its properties
        for node_id, properties in component.get().items():
            self.graph.add_node(node_id, **properties)

    def get_node(self, node_id):
        """
        Get the state, input, and parameters for a node.

        Args:
            node_id: The node identifier.
        Returns:
            Tuple of (x, u, params) for the node.
        """
        return self.graph.nodes[node_id]['x'], self.graph.nodes[node_id]['u'], self.graph.nodes[node_id]['params']
    
    def add_edge(self, node1, node2):
        """
        Add an edge (connection) between two nodes and generate algebraic equations for the connection.

        Args:
            node1: First node identifier.
            node2: Second node identifier.
        """
        node1_data = self.graph.nodes[node1]
        node2_data = self.graph.nodes[node2]
        equations = self.equation_generator.generate_equations(node1_data, node2_data)
        self.equations = equations
        # Ensure consistent ordering for undirected edges
        if node1 > node2:
            self.graph.add_edge(node2, node1, algebraic=equations)
        elif node2 > node1:
            self.graph.add_edge(node1, node2, algebraic=equations)


    def set_input(self, input_names: list = None):
        """
        Set the input variables for the system.

        Args:
            input_names: List of input variable names (as strings).
        Raises:
            ValueError: If an input is not found in the existing input list.
        """
        # Step 1: Aggregate all node and edge equations to update self.u, self.x, etc.
        self.aggregate()

        # Step 2: Convert input names to sympy symbols
        input_syms = [sp.symbols(_u) for _u in input_names]

        # Step 3: Store the old input list for reference
        u_old = self.u.copy()

        # Step 4: Build the new input list, ensuring all requested inputs exist
        self.u = [_u if _u in u_old else None for _u in input_syms]

        # Step 5: Raise an error if any requested input is not found
        if None in self.u:
            raise ValueError(f'The input {input_syms[self.u.index(None)]} is not an input!')

        # Step 6: Identify algebraic variables (those not in the new input list)
        self.z = sp.Matrix([_u for _u in u_old if not (_u in self.u)])

        # Step 7: Eliminate algebraic variables from the ODE system
        self.combine_odes_algebraic()


    def set_output(self, output_eqs):
        """
        Set the output equations and their names.

        Args:
            output_eqs: Dictionary of {equation names : output equations}.
        """
        self.y = sp.Matrix(list(output_eqs.values()))
        self.y_str = list(output_eqs.keys())


    def aggregate(self):
        """
        Aggregate all ODEs, states, inputs, and parameters from nodes and edges in the graph.
        This method combines the equations and variables for the entire system.
        """
        def safe_join(matrix):
            if matrix is None or matrix == sp.Matrix([]):
                return sp.Matrix.zeros(0, 1)
            elif isinstance(matrix, sp.Matrix):
                return matrix
            elif hasattr(matrix, '_asdict'):  # likely a namedtuple
                return sp.Matrix(list(matrix._asdict().values()))
            else:
                raise TypeError(f"Unsupported type in safe_join: {type(matrix)}")

        # Initialize empty containers
        self.odes, self.x, self.u, self.params = sp.Matrix(), sp.Matrix(), sp.Matrix(), dict()
        # Aggregate node equations and variables
        for node_id, data in self.graph.nodes(data=True):
            self.odes = self.odes.col_join(safe_join(data.get('odes', None)))
            self.x = self.x.col_join(safe_join(data.get('x', None)))
            self.u = self.u.col_join(safe_join(data.get('u', None)))
            self.params.update(data.get('params', {}))

        # Aggregate edge algebraic equations
        self.algebraic = sp.Matrix()
        for id1, id2, data in self.graph.edges(data=True):
            self.algebraic = self.algebraic.col_join(data.get('algebraic', sp.Matrix()))

    def add_control(self, controller):
        """
        Add a controller to the system and update the graph and equations accordingly.

        Args:
            controller: Controller object with .generate_equation() and .get().
        """
        # Generate controller equations
        controller.generate_equation()

        # Remove the controller's output from the input list
        idx = self.u.index(controller.u_out)
        self.u.pop(idx)

        # Mark the controlled node
        for node_id, data in self.graph.nodes(data=True):
            if controller.u_out in data['u']:
                self.graph.nodes[node_id]['control'] = controller.id
                break
        # Add controller node(s) and update system equations
        for node_id, properties in controller.get().items():
            self.graph.add_node(node_id, **properties)
            self.odes = self.odes.col_join(properties.get('odes', sp.Matrix()))
            self.x = self.x.col_join(properties.get('x', sp.Matrix()))
            self.u.extend(properties.get('u', []))
            self.params.update(properties.get('params', {}))
            self.odes = self.odes.subs(properties['law'])

            
    def plot(self):
        """
        Plot the electrical grid using networkx and matplotlib.
        Shows node names and algebraic equations on edges.
        """
        pos = nx.spring_layout(self.graph)  # Use spring layout for positioning nodes

        # Prepare labels with both number and name
        labels = {
            node: f"{node}\n({data.get('name', '')})"
            for node, data in self.graph.nodes(data=True)
        }

        plt.figure(figsize=(20, 5))
        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            labels=labels,  # Use combined labels
            node_size=2000,
            node_color="lightblue",
            font_size=10,  # Font size for the node number
            font_weight="bold",
        )

        # Annotate the edges with equations
        edge_labels = {}
        for u, v, data in self.graph.edges(data=True):
            equations = data['algebraic']
            edge_labels[(u, v)] = "\n".join(str(eq) for eq in equations)

        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=8)

        plt.title("Electrical Grid")
        plt.show()

    def print_edge(self, ids=None, key='algebraic'):
        """
        Print the algebraic equations for each connection in the grid.

        Args:
            ids: Optional tuple of node ids to print a specific edge.
            key: The key for the edge data (default: 'algebraic').
        """
        if ids is None:
            for u, v, data in self.graph.edges(data=True):
                print(f"Connection between Node {u} and Node {v}\n{self.graph.nodes[u]['name']} - {self.graph.nodes[v]['name']}:")
                for eq in data[key]:
                    print(f"  {eq}")
        else:
            print(f"Connection between Node {ids[0]} and Node {ids[1]}\n{self.graph.nodes[ids[0]]['name']} - {self.graph.nodes[ids[1]]['name']}:")
            for eq in self.graph.edges[ids][key]:
                print(f"  {eq}")

    def add_kcl(self, node_id):
        """
        Add Kirchhoff's Current Law (KCL) equation for a node if multiple sources are connected.

        Args:
            node_id: The node identifier.
        Raises:
            Exception: If unable to formulate the KCL for the node.
        """
        sources = [] 
        # find if multiple nodes connect to the target node
        i_in = self.graph.nodes(data=True)[node_id]['u'][0]
        for id1, id2, data in self.graph.edges(data=True):
            if id1 == node_id:
                if i_in in data['algebraic'][0].free_symbols:
                    sources.append(id2)
                else:
                    print(data['algebraic'])
            elif id2 == node_id:
                if i_in in data['algebraic'][0].free_symbols:
                    sources.append(id1)
                else:
                    print(data['algebraic'])

        if len(sources) > 1:
            kcl = 0  
            # Modify source nodes
            success = 0
            for idx in sources:
                s_data =  self.graph.nodes(data=True)[idx]
                if idx > node_id:
                    e_data =  self.graph.edges[(node_id,idx)]
                else:
                    e_data =  self.graph.edges[(idx,node_id)]
                print(f'Removing equation from node {idx}')
                print(e_data['algebraic'][0])
                e_data['algebraic'].row_del(0)

                for u in s_data['u']:
                    if str(u).startswith('i_out_'):
                        kcl += u
                        success = 1
                        break
                if success == 0:
                    raise Exception(f'Issues with node {idx}. Cannot formulate the current law for connection to node {node_id}.')

            # Add target node
            data = self.graph.nodes(data=True)[node_id]
            success = 0
            for u in data['u']:
                if str(u).startswith('i_in_'):
                    kcl -= u
                    success = 1
                    break
            if success == 0:
                    raise Exception(f'Issues with node {node_id}. Cannot formulate the current law for connection to node {node_id}.')

            # insert kcl in row 0
            kcl = sp.Matrix([kcl])
            if idx > node_id:
                self.graph.edges[(node_id,idx)]['algebraic'] = self.graph.edges[(node_id,idx)]['algebraic'].row_insert(0,kcl)
                print('Adding to edge', (node_id,idx))
            else:
                self.graph.edges[(idx,node_id)]['algebraic'] = self.graph.edges[(idx,node_id)]['algebraic'].row_insert(0,kcl)
                print('Adding to edge', (idx,node_id))

    def print_pretty(self, key, id=None):
        """
        Print the equations or variables for each connection or node in the grid as a formatted table.

        Args:
            key: One of 'u', 'x', 'odes', 'algebraic', 'eig', 'op'.
            id: Optional node id to restrict output.
        Raises:
            ValueError: If key is not recognized.
        """
        # Validate the key argument
        if key not in ['u', 'x', 'odes', 'algebraic', 'eig', 'op']:
            raise ValueError("Key must be either 'u', 'x', 'odes', 'algebraic', 'eig', 'op'.")

        data_list = []  # Will hold the rows for the table

        # Handle input and state variables
        if key in ['u', 'x']:
            title = 'Inputs' if key == 'u' else 'States'
            if id is None:
                # Loop over all nodes and collect their variables
                for u, data in self.graph.nodes(data=True):
                    node_name = self.graph.nodes[u]['name']
                    for i, eq in enumerate(data[key]):
                        # Only include variables that are in the system's input or state list
                        if not ((eq in self.u) or (eq in self.x)):
                            continue
                        data_list.append({
                            "Node": u,
                            "Node Name": node_name,
                            "Reference": eq,
                        })
            else:
                # Only show variables for the specified node
                node_name = self.graph.nodes[id]['name']
                for i, eq in enumerate(self.graph.nodes[id][key]):
                    if not ((eq in self.u) or (eq in self.x)):
                        continue
                    data_list.append({
                        "Node": id,
                        "Node Name": node_name,
                        "Reference": eq
                    })

        # Handle ODE equations
        if key in ['odes']:
            title = 'ODE Equations'
            if id is None:
                # Collect ODEs for all nodes
                for u, data in self.graph.nodes(data=True):
                    node_name = self.graph.nodes[u]['name']
                    for i, eq in enumerate(data[key]):
                        data_list.append({
                            "Node": u,
                            "Node Name": node_name,
                            "Equation": eq,
                        })
            else:
                # Only show ODEs for the specified node
                node_name = self.graph.nodes[id]['name']
                for i, eq in enumerate(self.graph.nodes[id][key]):
                    data_list.append({
                        "Node": id,
                        "Node Name": node_name,
                        "Equation": eq
                    })

        # Handle algebraic equations (edge equations)
        if key in ['algebraic']:
            title = 'Algebraic Equations'
            if id is None:
                # Collect algebraic equations for all edges
                for u, v, data in self.graph.edges(data=True):
                    node_name = self.graph.nodes[u]['name']
                    for i, eq in enumerate(data[key]):
                        data_list.append({
                            "Node 1": self.graph.nodes[u]['name'],
                            "Node 2": self.graph.nodes[v]['name'],
                            "Equation": eq,
                        })
            else:
                # Only show algebraic equations for the specified node
                node_name = self.graph.nodes[id]['name']
                for i, eq in enumerate(self.graph.nodes[id][key]):
                    data_list.append({
                        "Node 1": self.graph.nodes[u]['name'],
                        "Node 2": self.graph.nodes[v]['name'],
                        "Equation": eq
                    })

        # Handle eigenvalue summary
        if key in ['eig']:
            title = 'Eigenvalues'
            # Compute eigenvalues and derived quantities
            D, _ = self.get_eig()
            f0 = np.array([abs(np.imag(val)) / (2*np.pi) for val in D]) # Natural frequencies
            damp = np.array([(-(np.real(val) / np.abs(val)) * 100)  for val in D]) # Damping in %
            omega_c = np.array([abs(val) / (2*np.pi) for val in D]) # Corner freq
            data_list = {
                'Eigenvalue Re.': D.real,
                'Eigenvalue Im.': D.imag,
                'Natural Freq. [kHz]': f0/1e3,
                'Damping in %': damp,
                'Corner Freq. [kHz]': omega_c/1e3,
            }

        # Handle operating point summary
        if key in ['op']:
            title = 'Operating Point'
            data_list = {
                'State': self.x,
                'Value': self.op,
            }

        # Sort by self.u ordering if applicable (for input variables)
        if key == 'u':
            u_order = {ref: i for i, ref in enumerate(self.u)}
            data_list.sort(key=lambda d: u_order.get(d["Reference"], float("inf")))

        # Create a pandas DataFrame for pretty printing
        df = pd.DataFrame(data_list)

        # Print the table if there is data, otherwise print a message
        if not df.empty:
            # Pretty print using tabulate
            print(f"\n{title}")
            print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
        else:
            print("No data to display.")