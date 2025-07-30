import numpy as np
from ODEpower.tool import *
import matlab.engine
from pathlib import Path
import os


class ODEmatlab:
    """
    Provides MATLAB backend integration for ODEpower, including operating point calculation, simulation, and model management.
    """
    def __init__(self, parent):
        """
        Initialize the ODEmatlab backend.

        Args:
            parent: The ODEpower instance using this backend.
        """
        self.parent = parent  # This is the ODEpower instance

        config = parent.config
        self.LOG = config.LOG

        # Step 1: Connect to MATLAB engine or start a new session
        if isinstance(config.matlab_engine, matlab.engine.matlabengine.MatlabEngine):
            self.matlab = config.matlab_engine
        else:
            try:
                self.matlab = matlab.engine.connect_matlab(matlab.engine.find_matlab()[0])
                if self.LOG:
                    print('Connected to Matlab Session')
            except Exception:
                if self.LOG:
                    print('Unable to connect Matlab')
                self.matlab = matlab.engine.start_matlab('-nosplash -noFigureWindows -r')

        # Step 2: Set model path for MATLAB files
        if config.matlab_model_path == '':
            self.model_path = Path(os.getcwd())
        else:
            self.model_path = Path(config.matlab_model_path)

        # Step 3: Ensure the model path exists
        self.model_path.mkdir(parents=True, exist_ok=True)

        # Step 4: Add necessary paths to MATLAB environment
        script_path = Path(__file__).parent.resolve() / '..' / 'matlab'
        self.eval(f"addpath('{str(script_path)}');", 0)
        self.eval(f"addpath('{str(self.model_path)}');", 0)


    def get_op(self, initialGuess=False):
        """
        Calculate the operating point using MATLAB's vpasolve.

        Args:
            initialGuess: If True, use an initial guess for the solver.
        Raises:
            ValueError: If unable to find the operating point.
        """
        # Step 1: Define all state variables as symbolic in MATLAB
        for x in self.x:
            self.eval(f'{str(x)} = sym("{x}","real");')

        # Step 2: Prepare the ODE and state variable arrays for MATLAB
        mat_ode = ('[' + ','.join(str(ode) for ode in self.odes_) + ']').replace('**','^')
        mat_x = '[' + ','.join(str(x) for x in self.x) + ']'
        self.eval(f'eq_subs = {mat_ode};')
        self.eval(f'stateVariables= {mat_x};')

        # Step 3: Call vpasolve to find the operating point
        if initialGuess:
            self.eval(f'StatesOperationPoint = vpasolve(eq_subs, stateVariables, initialGuess);')
        else:
            self.eval(f'StatesOperationPoint = vpasolve(eq_subs, stateVariables);')
        try:
            # Step 4: Convert the result to a cell array and extract the numeric values
            self.eval(f'StatesOperationPoint = struct2cell(StatesOperationPoint);')
            self.op = np.array(self.eval('double([StatesOperationPoint{:}]);',out=1))[0]
        except:
            # Step 5: If solution fails, set op to zeros and raise an error
            self.op = [0 for _ in range(len(self.x))] 
            raise ValueError('Unable to find OP. Setting to zero')

#        This could be used to determine OP by EMT
#        if simulink:
#            if not self.eval(f'isvarname("mdl")',out=1):
#                raise ValueError('Simulink model not set!')
#            
#            self.eval(f'Tstep = {simulink_T + 1};')
#            self.mat_set_model_input(self.v0,self.v1,show=False)
#
#            self.eval(f'configSet = getActiveConfigSet(mdl);')
#            self.eval(f"set_param(configSet,'StopTime','{simulink_T}');")
#            self.eval(f"set_param('{self.model}/Solver Configuration','DoFixedCost','On')") #Change
#            self.eval(f"set_param(configSet,LoadInitialState='off');")
#            self.eval(f"res = sim(mdl);")
#            self.eval(f"xInitial = res.xFinal;")
#            self.eval(f"set_param(configSet,LoadInitialState='on');")
#            self.eval(f"set_param(configSet,InitialState='xInitial');")
#            self.eval(f"set_param(configSet,'StopTime','Tsim');")
#            self.eval(f"set_param('{self.model}/Solver Configuration','DoFixedCost','Off')") #Change



    #TODO make consistent
    def set_input_values(self):
        """
        Placeholder for setting input values in MATLAB backend (not implemented).
        """
        pass
    def set_input(self, simulink_params={}):
        """
        Set the input values for Simulink simulation in MATLAB workspace.

        Args:
            simulink_params: Dictionary of Simulink-specific parameters.
        """
        #self.set_model_input(v0,v1,show=show)

        #Tsim = self.params['sim_params']['Tsim']
        #t = self.u_val[0,:]

        #self.matlab.workspace['t'] = matlab.double(t.tolist())
        #self.eval(f'u_vals = ')
        self.matlab.workspace['u_val'] = matlab.double(self.parent.u_val)

        #% Calculate the difference to OP input
        self.matlab.workspace['inputArr'] = matlab.double([self.parent.v0.tolist(),self.parent.v1.tolist()])

        self.parent.params['simulink_params'] = simulink_params

        #self.eval(f'u_ss = zeros(length(t),{len(self.v0)});')
        #self.eval(f'u_ss(t < Tstep,:) = repmat(inputArr(1,:)-inputArr(1,:),sum(t < Tstep),1);')
        #self.eval(f'u_ss(t >= Tstep,:) = repmat(inputArr(2,:)-inputArr(1,:),sum(t >= Tstep),1);')

        #self.eval(f'u_simulink = zeros(length(t),{len(self.v0)});')
        #self.eval(f'u_simulink(t < Tstep,:) = repmat(inputArr(1,:), sum(t < Tstep),1);')
        #self.eval(f'u_simulink(t >= Tstep,:) = repmat(inputArr(2,:), sum(t >= Tstep),1);')

    def set_model(self, model, simulink_rename=True):
        """
        Set the Simulink model for simulation and assign parameters in the MATLAB workspace.

        Args:
            model: Name of the Simulink model.
            simulink_rename: If True, update block parameters.
        """
        self.model = model
        self.matlab.workspace['model_name'] = model
        self.eval(f'load_system(model_name);')

        self.eval('ds = Simulink.SimulationData.Dataset;')
        self.eval('ds{1} = struct;')

        self.eval(f'mdlWks = get_param("{self.model}","ModelWorkspace");')
        self.eval(f'clear(mdlWks);')

        for p,v in self.parent.params['sim_params'].items():
            self.eval(f'assignin(mdlWks, "{p}",{v});')

        for p,v in self.parent.params['simulink_params'].items():
            self.eval(f'assignin(mdlWks, "{p}",{v});')

        for _, data in self.parent.graph.nodes(data=True):
            for p,v in data['params'].items():
                self.eval(f'assignin(mdlWks, "{p}",{v});')   

        if simulink_rename:
            self.eval('update_block_parameters(model_name)')

    # TODO write to tmp file and delete
    def py_writeODE(self, name=None):
        """
        Write the ODE system to a MATLAB .m file for use in MATLAB/Simulink.

        Args:
            name: Optional base name for the file.
        """
        if name == None:
            pass
            #import names
            #self.name = names.get_first_name()
        else:
            self.name = name + '_py'
        with open(f'{str(self.model_path/ self.name)}.m','w') as f:
            f.write('\nclear pyodes inputVariables stateVariables inputs states outputVariables stateDerivatives fields;')
            f.write(r'\nclear -regexp ^u\d+_\d+$;')
            f.write(r'\nclear -regexp ^x\d+_\d+$;\n\n')
            [f.write(f"inputs.{inpt} = sym('{inpt}','real');\n") for i, inpt in enumerate(self.u)]
            f.write('\n')
            [f.write(f"states.{state} = sym('{state}','real');\n") for state in self.x]

            f.write('\n[inputVariables, stateVariables] = eval_input_states(inputs,states);\n\n')

            [f.write(f"pyodes.{self.x[i]} = {str(eq).replace('**','^')};\n") for i, eq in enumerate(self.odes)]
            f.write('\n')


    #make dottict acailable in self?
    def sim_ode(self, setOp=False, save=True):
        """
        Simulate the ODE system in MATLAB and store the results in the parent object.

        Args:
            setOp: If True, use the operating point as the initial state.
            save: If True, store the simulation results in the parent.
        """
        if not setOp:
            self.eval('y0_ODE = zeros(length(fields),1);')
        else:
            #self.eval('y0_ODE = double([StatesOperationPoint{:}]);')
            op_str = '[' + ','.join(map(str, self.op.tolist())) + ']'
            self.eval(f'y0_ODE = {op_str};')
        self.eval(f'tspan = [0,Tsim];')
        self.eval('ode_simODE')
        if save:
            x_ODE = np.array(self.eval('Y_nl;',1))
            x_ODE = {str(self.x_str[i]) : x_ODE[:,i] for i in range(len(self.x))}
            t_ODE = np.array(self.eval('t_nl;',1))
            self.sol_ode = dotdict({'t':t_ODE, 'x':x_ODE})
        else:
            return np.array(self.eval('Y_nl(end,:);',1))

    def sim_simulink(self, setOp=False, dataset='out.yout{1}'):
        """
        Simulate the system using Simulink in MATLAB and store the results in the parent object.

        Args:
            setOp: If True, use the operating point as the initial state.
            dataset: Name of the Simulink output dataset.
        """
        #TODO move this into a prepare sim function
        # Check if model is loaded
        self.eval(f'configSet = getActiveConfigSet(model_name);')
        self.eval(f"set_param(configSet,'StopTime','Tsim');")
        #if setOp: 
            #self.eval(f"set_param(configSet,LoadInitialState='on');")
        self.eval(f"set_param('{self.model}/Solver Configuration','DoFixedCost','Off')") # Ensure Fixed Cost is Off

        for i, k in enumerate(self.parent.u):
            self.eval(f'series = timeseries(u_val({i+2},:),u_val(1,:));')
            self.eval(f"ds{{1}}.('{str(k)}') = series;")

        self.eval(f'mdlWks = get_param("{self.model}","ModelWorkspace");')
        self.eval(f'clear(mdlWks);')
        for p,v in self.parent.params['sim_params'].items():
            self.eval(f'assignin(mdlWks, "{p}",{v});')
        for p,v in self.parent.params['simulink_params'].items():
            self.eval(f'assignin(mdlWks, "{p}",{v});')
        for _, data in self.parent.graph.nodes(data=True):
            for p,v in data['params'].items():
                self.eval(f'assignin(mdlWks, "{p}",{v});')

        self.eval(f'out = sim("{self.model}");')

        s = self.eval(f'fieldnames({dataset}.Values)', 1)[0]
        # Simulink
        x_m = {}
        t_m = {}
        for s in self.eval(f'fieldnames({dataset}.Values)', 1):
            val = np.array(self.eval(f'{dataset}.Values.{s}.Data;', 1))
            x_m.update({s:val})
            val = np.array(self.eval(f'{dataset}.Values.{s}.Time;', 1))
            t_m.update({s:val})
        self.parent.sol_simulink = dotdict({'t':t_m, 'x':x_m})

    def sim_ss(self):
        """
        Simulate the state-space system in MATLAB and store the results in the parent object.
        """
        self.eval('ode_simSS')
        x_SS = np.array(self.eval('Y_lin;', 1))
        x_SS = {str(self.x_str[i]): x_SS[:, i] for i in range(len(self.x))}
        t_SS = np.array(self.eval('t_lin;', 1))
        self.sol_ss = dotdict({'t': t_SS, 'x': x_SS})
    
    def eval(self, cmd, out=0):
        """
        Evaluate a MATLAB command in the MATLAB engine.

        Args:
            cmd: Command string to execute.
            out: Number of output arguments to return.
        Returns:
            Result of the MATLAB command.
        """
        if self.parent.DEBUG:
            print(cmd)
        return self.matlab.eval(cmd, nargout=out)
"""



"""