#%%
from PySpice.Spice.Parser import SpiceParser
import matplotlib.pyplot as plt
from PySpice.Unit import *
import numpy as np
import tempfile

class SpiceSimulator:
    def __init__(self, netlist):
        self.netlist = netlist
        self.circuit = None
        self.simulation_result = None

    def parse_netlist(self):
        # Create a temporary file to hold the netlist
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cir") as temp_file:
            temp_file.write(self.netlist.encode())
            temp_file_path = temp_file.name
        
        # Parse the netlist using SpiceParser
        parser = SpiceParser(temp_file_path)
        self.circuit = parser.build_circuit()

    def define_parameters(self, **kwargs):
        # Set circuit parameters after parsing the netlist
        if not self.circuit:
            raise Exception("No circuit found. Make sure to parse the netlist first.")
        
        for param, value in kwargs.items():
            # Update circuit parameters
            if param in self.circuit.parameters:
                self.circuit.parameters[param] = value
            else:
                raise KeyError(f"Parameter '{param}' not found in the circuit.")

    def simulate_transient(self, step_time, end_time):
        if not self.circuit:
            raise Exception("No circuit found. Make sure to parse the netlist first.")

        # Create simulator instance
        simulator = self.circuit.simulator(temperature=25, nominal_temperature=25)

        # Perform transient analysis
        self.simulation_result = simulator.transient(step_time=step_time, end_time=end_time)

    def plot_result(self, node_name):
        if not self.simulation_result:
            raise Exception("No simulation result found. Make sure to run the simulation first.")

        # Extract the data for the specified node
        try:
            time = self.simulation_result.time
            voltage = self.simulation_result[node_name]
        except KeyError:
            raise Exception(f"Node '{node_name}' not found in the simulation results.")
        
        # Plot the data
        plt.figure(figsize=(10, 6))
        plt.plot(time, voltage, label=f'Voltage at {node_name}')
        plt.xlabel('Time [s]')
        if node_name in self.simulation_result.branches.keys():
            plt.ylabel('Current [A]')
        elif node_name in self.simulation_result.nodes.keys():
            plt.ylabel('Voltage [V]')
        plt.title(f'Transient Analysis of Node {node_name}')
        plt.legend()
        plt.grid()
        plt.show()
    
    def info(self):
        print('Current branches:\n',list(self.simulation_result.branches.keys()))
        print('Voltage nodes:\n',list(self.simulation_result.nodes.keys()))

    def run(self, step_time, end_time, node_name):
        # Execute the full flow: parse, simulate and plot
        self.parse_netlist()
        self.simulate_transient(step_time, end_time)
        self.plot_result(node_name)

if __name__ == '__main__':

    # Usage Example
    netlist = """
    * Test circuit netlist
    V1 n1 0 SINE(0 2 10)
    R1 n1 0 5
    .TRAN 0.1m 1
    .END
    """

    # Create a simulator instance and parse Netlist
    simulator = SpiceSimulator(netlist)
    simulator.parse_netlist()

    # Define parameters 
    simulator.circuit['R1'].resistance = 1

    # Run the transient simulation
    simulator.simulate_transient(step_time=0.1e-3, end_time=1)

    # Plot the voltage or currents
    simulator.info()
    simulator.plot_result(node_name='v1')
