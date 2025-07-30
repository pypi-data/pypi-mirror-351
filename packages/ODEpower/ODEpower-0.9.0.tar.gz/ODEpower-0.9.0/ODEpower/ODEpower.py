from ODEpower.ODEgraph import *
from ODEpower.ODEtool import *
from ODEpower.ODEsimulation import *
from ODEpower.ODEplot import *
from ODEpower.ODEmatlab import *


class ODEpower(ODEgraph, ODEtool, ODEsimulation, ODEplot):
    """
    Main class for the ODEpower package, providing a unified interface for modeling, simulating, and analyzing ODE-based power system networks.
    Inherits from ODEgraph, ODEtool, ODEsimulation, and ODEplot to combine graph construction, mathematical tools, simulation, and plotting.
    Optionally attaches MATLAB backend functionality if enabled in the configuration.
    """
    def __init__(self, config, *args, **kwargs):
        """
        Initialize the ODEpower system.

        Args:
            config: Configuration object containing simulation and backend options.
            *args, **kwargs: Additional arguments passed to parent classes.
        """
        # Step 1: Store debug flag and configuration for later use
        self.DEBUG = config.DEBUG
        self.LOG = config.LOG
        self.config = config

        # Step 2: Initialize all parent classes (ODEgraph, ODEtool, ODEsimulation, ODEplot)
        super().__init__(*args, **kwargs)

        # Step 3: Attach MATLAB backend if enabled in config
        if config.matlab_enable:
            # Create an ODEmatlab instance and attach to self.mat
            self.mat = ODEmatlab(self)
            # Optionally, assign all ODEmatlab methods to self.mat namespace
            # self._assign_matlab_methods_to_mat()

    def _assign_matlab_methods_to_mat(self):
        """
        Assign all callable public methods from ODEmatlab to the self.mat namespace.
        This allows calling MATLAB backend methods directly from self.mat.
        """
        # Iterate over all attributes in ODEmatlab and bind them to self.mat
        for attr_name in dir(ODEmatlab):
            # Skip private and special methods
            if not attr_name.startswith('_'):
                method = getattr(ODEmatlab, attr_name)
                # Only assign if the attribute is callable (i.e., a method)
                if callable(method):
                    # Bind the method to self.mat
                    setattr(self.mat, attr_name, method.__get__(self, self.__class__))