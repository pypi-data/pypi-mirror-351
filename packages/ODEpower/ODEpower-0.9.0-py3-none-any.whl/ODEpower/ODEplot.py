#try:
    #from phd.prettyPlot import plot
#except:
    # Not fully supported flag for choice required
    #import matplotlib.pyplot as plt
    #plot = plt.figure
from tool.prettyPlot import plot
import numpy as np
import matplotlib.cm as cm
import matplotlib.patches as patches
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
import control as ct
import sympy as sp
import re

class ODEplot:
    def plot_eig(self, damping=[], max=200, param_list=[], n_max=np.inf):
        """
        Plot the eigenvalues of the system.

        Args:
        - damping (list): List of damping ratios to plot.
        - max (int): Maximum number of eigenvalues to plot.
        - eigs (bool): Flag indicating whether to use precomputed eigenvalues.
        - n_max (int): Maximum number of eigenvalues to display annotations for.

        Returns:
        None
        """
        D, P = self.get_eig(getPF=False)

        f = plot()
        f.format()

        color = 'r'

        im = f.ax[0].scatter(np.real(D), np.imag(D), marker='o', color=color, s=50)

        print(f'{D.real.max():.2E} <-- Max real value')
        
        for _i, _d in enumerate(D):
            if _d.real > 0:
                print(f'Eigenvalue {_i + 1} is {_d}.')


        x = np.arange(max, .5, 1)
        for y in damping:
            f.ax[0].plot(x, x / y, 'b--', label=f'{y * 100}%')
            f.ax[0].plot(x, -x / y, 'b--')

        f.xlabel('Real Axis')
        f.ylabel('Imaginary Axis')
        f.format()

        return f

    def plot_pf(self, lims=[0, 1], order=True, method='sum', reduce={}, order_x=[], order_y=[], fs=9, w_scale=1, h_scale=1.5):
        """
        Plot Participation Factors (PFs) of the system.

        Args:
        - lims (list): Lower and upper limits for color normalization.
        - method (str): Method for calculating PFs ('sum' or 'max').
        - reduce (bool): Flag to reduce PFs by combining similar states.
        - PFs (array): Array of PFs if provided externally.
        - fs (int): Font size for plot labels.

        Returns:
        None
        """
        stateVariables = [str(k) for k in self.x]
        D, PF = self.get_eig()
        if order:
            fd = np.real(D) / (2 * np.pi)
            fo = np.imag(D) / (2 * np.pi)

            # Identify oscillating and non-oscillating modes
            oscillating_mask = np.abs(fo) > 0
            non_oscillating_mask = ~oscillating_mask

            # Reorder indices
            oscillating_indices = np.where(oscillating_mask)[0]
            non_oscillating_indices = np.where(non_oscillating_mask)[0]
            sorted_non_oscillating = non_oscillating_indices[np.argsort(fd[non_oscillating_indices])]
            sorted_non_oscillating = non_oscillating_indices[np.argsort(np.abs(fd[non_oscillating_indices]))]
            sorted_oscillating = oscillating_indices[np.argsort(np.abs(fo[oscillating_indices]))]


            mode_order = np.concatenate([sorted_oscillating, sorted_non_oscillating])

            # Reorder PF
            PF[:] = PF[:, mode_order]
            print(mode_order)
            D[:] = D[mode_order]
            self.eig_info = {'fd':fd[mode_order],'fo':fo[mode_order]}


        if len(reduce) > 0:
            #red_states = np.unique([re.sub(r"[n,d]\d", "", str(s)) for s in self.x_str])
            remove_states = [value for _, values in reduce.items() for value in values]
            red_states = [str(s) for s in self.x if s not in remove_states] + list(reduce.keys())
            old_states = np.array(str(self.x))
            mapping = {value: key for key, values in reduce.items() for value in values}

            for i in range(len(old_states)):
                if old_states[i] in mapping.keys():
                    old_states[i] = mapping[old_states[i]]

            red_PF = np.zeros((len(red_states), len(self.x)))
            for i, red_state in enumerate(red_states):
                ind = (old_states == red_state)
                red_PF[i, :] = PF[ind, :].sum(axis=0)
            PF = red_PF
            stateVariables = np.array(red_states)

        if len(order_y) > 0:
            if len(order_y) != len(set(order_y)):
                raise ValueError('Duplicates in order_y!')
            indexes = np.unique(order_y, return_index=True)[1]
            order_y = [order_y[index] for index in sorted(indexes)]
            if not len(order_y) == PF.shape[0]:
                raise ValueError('Length of order_y vector is wrong')
            PF = PF[order_y,:]
            self._test = stateVariables.copy()
            stateVariables = np.array(stateVariables)[order_y]

        if len(order_x) > 0:
            if len(order_x) != len(set(order_x)):
                raise ValueError('Duplicates in order_x!')
            if not len(order_x) == PF.shape[1]:
                raise ValueError('Length of order_x vector is wrong')
            PF = PF[:,order_x]

        if method == 'sum':
            PF = PF / PF.sum(axis=0)
        elif method == 'max':
            PF = PF / PF.max(axis=0)

        f = plot(w_scale=w_scale, h_scale=h_scale)            

        cmap = cm.gray_r
        norm = Normalize(vmin=lims[0], vmax=lims[1])
        nrows, ncols = PF.shape
#        for i in range(nrows):
#            for j in range(ncols):
#                rect = patches.Rectangle((j, i), 1, 1, linewidth=0, edgecolor='none', facecolor=plt.cm.gray_r(PF[i, j]))
#                f.ax[0].add_patch(rect)
        #cax = f.ax[0].imshow(PF, aspect='auto', cmap=cmap, norm=norm)
        cax = f.ax[0].imshow(
            PF,
            aspect='auto',
            cmap=cmap,
            norm=norm,
            origin='lower',
            extent=[0, PF.shape[1], 0,PF.shape[0]]  # [x0, x1, y0, y1]
        )

        cax = f.fig.add_axes([f.ax[0].get_position().x1 + 0.01, f.ax[0].get_position().y0, 0.02, f.ax[0].get_position().height])
        f.fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)

        xmin = f.ax[0].get_xlim()[0]
        ymin = f.ax[0].get_ylim()[0]
        ticks = np.arange(.5, int(PF.shape[1]), 1) + xmin
        imageX = np.arange(0, int(PF.shape[1])) + 1
        imageY = np.arange(0, PF.shape[0]) + ymin + .5
        f.ax[0].set_xticks(ticks)
        f.ax[0].set_xticklabels(labels=imageX)
        f.ax[0].set_yticks(imageY, stateVariables)


        f.xlabel('Modes')
        f.ylabel('States')
        f.ax[0].set_xticks([x + xmin for x in range(int(PF.shape[1]) + 1)], minor=True)
        f.ax[0].set_yticks([x + ymin for x in range(PF.shape[0] + 1)], minor=True)
        f.ax[0].grid(which='minor', color='k', linestyle='-', linewidth=.3)
        f.ax[0].tick_params(axis='x', labelrotation=0)
        f.ax[0].tick_params(which='minor', size=0)
        f.ax[0].xaxis.set_tick_params(labelsize=fs)
        f.ax[0].yaxis.set_tick_params(labelsize=fs)
        cax.yaxis.set_tick_params(labelsize=fs)
        return f

    def plot_states(self, states=[], skip=[], Tstart=None, num_markers=0, f = None):
        """
        Plot the states over time.

        Args:
        - states (list): List of states to plot. If empty, all states will be plotted.
        - skip (list): List of strings specifying which results to skip plotting. ['SS,'ODE',Simulink]

        Returns:
        None
        """
        if len(states) == 0:
            states = self.x
        #else:
            #states = [sp.Symbol(s) for s in states]

        for state in states:
            if state not in states:
                continue
            if f == None:
                f = plot()

            state = str(state)
            # State Space
            if hasattr(self, 'sol_ss') and (self.sol_ss != False) and ('SS' not in skip):
                if not Tstart==None:
                    mask = (self.sol_ss.t > Tstart).squeeze()
                    if num_markers > 0:
                        idx= np.linspace(0, len(self.sol_ss.t[mask]) - 1, num_markers).astype(int)
                        f.scatter(self.sol_ss.t[mask][idx], self.sol_ss.x[state][mask][idx],marker='.')
                    f.plot(self.sol_ss.t[mask], self.sol_ss.x[state][mask], label='SS')
                else:
                    if num_markers > 0:
                        idx= np.linspace(0, len(self.sol_ss.t) - 1, num_markers).astype(int)
                        f.scatter(self.sol_ss.t[idx], self.sol_ss.x[state][idx],marker='.')
                    f.plot(self.sol_ss.t, self.sol_ss.x[state], label='SS')

            # ODE
            if hasattr(self, 'sol_ode') and (self.sol_ode != False) and ('ODE' not in skip):
                if not Tstart==None:
                    mask = (self.sol_ode.t > Tstart).squeeze()
                    if num_markers > 0:
                        idx= np.linspace(0, len(self.sol_ode.t[mask]) - 1, num_markers-1).astype(int)
                        f.scatter(self.sol_ode.t[mask][idx], self.sol_ode.x[state][mask][idx],marker='.')
                    f.plot(self.sol_ode.t[mask], self.sol_ode.x[state][mask], label='ODE',alpha=.9)
                else:
                    if num_markers > 0:
                        idx= np.linspace(0, len(self.sol_ode.t) - 1, num_markers-1).astype(int)
                        f.scatter(self.sol_ode.t[idx], self.sol_ode.x[state][idx])
                    f.plot(self.sol_ode.t, self.sol_ode.x[state], label='ODE',alpha=.9)

            # Simulink
            if hasattr(self, 'sol_simulink') and (self.sol_simulink != False) and ('Simulink' not in skip):
                if state in self.sol_simulink.x.keys():
                    if not Tstart==None:
                        mask = (self.sol_simulink.t[state] > Tstart).squeeze()
                        if num_markers > 0:
                            idx= np.linspace(0, len(self.sol_simulink.t[state][mask]) - 1, num_markers+1).astype(int)
                            f.scatter(self.sol_simulink.t[state][mask][idx], self.sol_simulink.x[state][mask][idx],marker='.')
                        f.plot(self.sol_simulink.t[state][mask], self.sol_simulink.x[state][mask], label='Simulink')
                    else:
                        if num_markers > 0:
                            idx= np.linspace(0, len(self.sol_simulink.t) - 1, num_markers+1).astype(int)
                            f.scatter(self.sol_simulink.t[state][idx], self.sol_simulink.x[state][idx],marker='.')
                        f.plot(self.sol_simulink.t[state], self.sol_simulink.x[state], label='Simulink',alpha=.8)
            f.xlabel('Time [s]')
            f.title(f'State - {state}')
            f.legend(default=True)
            f.format()
        return f
    
    def plot_inputs(self,inputs=[]):
        if len(inputs) == 0:
            inputs = self.u
        for i, input in enumerate(inputs):
            if input not in self.u:
                continue
            f = plot()
            input = str(input)
            f.plot(self.u_val[0], self.u_val[i+1])
            f.xlabel('Time [s]')
            f.title(f'Input - {input}')
            f.format()

    def plot_tf(self, Zs=None, names:list=None, x_range=[1e-3,1e5],x_points=1e3,f=None):
        def get_adaptive_freqs(Z, base_range, total_points=1000, extra_density_around_poles=True):
            poles = []
            poles.extend(Z.poles())

            # Convert to Hz (real or imaginary part, depending on what dominates)
            freqs = []
            for p in poles:
                w = np.abs(p)
                if w > 0:
                    freqs.append(w / (2*np.pi))  # rad/s → Hz

            # Base logspace
            base = np.logspace(np.log10(base_range[0]), np.log10(base_range[1]), int(0.6 * total_points))

            if extra_density_around_poles and freqs:
                for fp in freqs:
                    local = np.logspace(np.log10(max(base_range[0], fp/10)), np.log10(min(base_range[1], fp*10)), int(0.1 * total_points))
                    base = np.concatenate([base, local])

            return np.unique(np.sort(base))
        if Zs==None:
            Zs = [self.tf]

        if not isinstance(Zs,list):
            Zs = [Zs]

        #freq = np.logspace(np.log10(x_range[0]), np.log10(x_range[1]), num=int(x_points))  # Frequencies in Hz
        #omega = 2 * np.pi * freq # Convert to rad / s

        # Create custom plot using plot class
        if f==None:
            f = plot(subplots=[2,1])

        for i, Z in enumerate(Zs):
            freq = get_adaptive_freqs(Z, x_range, x_points)
            omega = 2 * np.pi * freq # Convert to rad / s
            mag, pha, _ = ct.frequency_response(Z, omega, Hz=True)

            pha= np.rad2deg(pha)     # Convert phase from radians to degrees
            pha= np.mod(pha + 180, 360) - 180    # Ensure phase is within [-360, 360] degrees


            # Plot magnitude and phase
            if not names==None:
                f.ax[0].plot(freq, mag, label=f'{names[i]}')
                f.ax[1].plot(freq, pha, label=f'{names[i]}')
            else:
                f.ax[0].plot(freq, mag)
                f.ax[1].plot(freq, pha)

        # Set labels
        #f.ylabel(r'|Za| \unit{\Omega} ', pos=0)
        f.ylabel(r'$|Z|$ in $\Omega$', pos=0)
        f.ylabel(r'$\phi$ in $^\circ$', pos=1)
        f.xlabel(r'$f$ in $\mathrm{Hz}$', pos=1)
        f.format(xlog=True)  # Apply logarithmic scale

        return f

 
    def plot_PFs(self, lims=[0, 1], method='sum', fs=6,f=None,reduce={}, order_x=[], order_y=[]):
        """
        Plot Participation Factors (PFs) of the system.

        Args:
        - lims (list): Lower and upper limits for color normalization.
        - method (str): Method for calculating PFs ('sum' or 'max').
        - reduce (bool): Flag to reduce PFs by combining similar states.
        - PFs (array): Array of PFs if provided externally.
        - fs (int): Font size for plot labels.

        Returns:
        None
        """
        stateVariables = [k for k in self.x]
        N = self.PFs.shape[0]
        PF = self.PFs.copy()

        #fd0 = np.array([np.real(val) / (2*np.pi) for val in self.eigs[0,:]]) 
        #fd1 = np.array([np.real(val) / (2*np.pi) for val in self.eigs[-1,:]]) 

        #f0 = np.array([np.imag(val) / (2*np.pi) for val in self.eigs[0,:]]) 
        #f1 = np.array([np.imag(val) / (2*np.pi) for val in self.eigs[-1,:]]) 
        #mode_order = np.argsort(-1 * fd0)
        #print('Mode\t fd0\t fd1\t f0\t f1')
        #[print(f'{i+1}\t fd0:{_f:.2f}\t fd1:{fd1[mode_order][i]:.2f}\t f0:{f0[mode_order][i]:.2f}\t f1:{f1[mode_order][i]:.2f}') for i,_f in enumerate(fd0[mode_order])]

        from collections import defaultdict

        # Dictionary to store modes with low damping per sample
        low_damping_modes_dict = defaultdict(list)
        eig = self.eigs.copy()

        for k in range(self.eigs.shape[0]):
            fd = np.real(self.eigs[k, :]) / (2 * np.pi)
            fo = np.imag(self.eigs[k, :]) / (2 * np.pi)

            # Identify oscillating and non-oscillating modes
            oscillating_mask = np.abs(fo) > 0
            non_oscillating_mask = ~oscillating_mask

            # Reorder indices
            oscillating_indices = np.where(oscillating_mask)[0]
            non_oscillating_indices = np.where(non_oscillating_mask)[0]
            sorted_non_oscillating = non_oscillating_indices[np.argsort(fd[non_oscillating_indices])]
            sorted_non_oscillating = non_oscillating_indices[np.argsort(np.abs(fd[non_oscillating_indices]))]
            sorted_oscillating = oscillating_indices[np.argsort(np.abs(fo[oscillating_indices]))]


            mode_order = np.concatenate([sorted_oscillating, sorted_non_oscillating])

            # Reorder PF
            PF[k] = PF[k, :, mode_order]
            eig[k,:] = eig[k, mode_order]

            # Compute damping ratios
            eigvals = self.eigs[k, :]
            zeta = np.abs(np.real(eigvals) / np.abs(eigvals))

            # Find modes with damping < 5%
            low_damping = np.where(zeta < 0.05)[0]

            # Save (global mode numbers or with respect to current k?)
            low_damping_modes_dict[k].extend(int(mode) for mode in low_damping)

        # Print grouped by sample
        print("Modes with damping < 5%:")
        for k, modes in low_damping_modes_dict.items():
            print(f"Mode: {k}, {modes}")

        fd0 = np.array([np.real(val) / (2*np.pi) for val in eig[0,:]]) 
        fd1 = np.array([np.real(val) / (2*np.pi) for val in eig[-1,:]]) 

        f0 = np.array([np.imag(val) / (2*np.pi) for val in eig[0,:]]) 
        f1 = np.array([np.imag(val) / (2*np.pi) for val in eig[-1,:]]) 

        print('Mode\t fd0\t fd1\t f0\t f1')
        [print(f'{i+1}\t fd0:{_f:.2f}\t fd1:{fd1[i]:.2f}\t f0:{f0[i]:.2f}\t f1:{f1[i]:.2f}') for i,_f in enumerate(fd0)]
            
#            fd0 = np.array([np.real(val) / (2*np.pi) for val in self.eigs[0,:]]) 
#            fd1 = np.array([np.real(val) / (2*np.pi) for val in self.eigs[-1,:]]) 
#
#            f0 = np.array([np.imag(val) / (2*np.pi) for val in self.eigs[0,:]]) 
#            f1 = np.array([np.imag(val) / (2*np.pi) for val in self.eigs[-1,:]]) 
#            mode_order = np.argsort(-1 * fd0)
#
#            PF = PF[k, :, mode_order]

        PF = self.reshape_array(PF)

        if len(reduce) > 0:
            #red_states = np.unique([re.sub(r"[n,d]\d", "", str(s)) for s in self.x_str])
            remove_states = [value for _, values in reduce.items() for value in values]
            red_states = [str(s) for s in self.x if s not in remove_states] + list(reduce.keys())
            old_states = np.array(str(self.x))
            mapping = {value: key for key, values in reduce.items() for value in values}

            for i in range(len(old_states)):
                if old_states[i] in mapping.keys():
                    old_states[i] = mapping[old_states[i]]

            red_PF = np.zeros((len(red_states), PF.shape[1]))
            for i, red_state in enumerate(red_states):
                ind = (old_states == red_state)
                red_PF[i, :] = PF[ind, :].sum(axis=0)
            PF = red_PF
            stateVariables = np.array(red_states)

        if len(order_y) > 0:
            if len(order_y) != len(set(order_y)):
                raise ValueError('Duplicates in order_y!')
            indexes = np.unique(order_y, return_index=True)[1]
            order_y = [order_y[index] for index in sorted(indexes)]
            if not len(order_y) == PF.shape[0]:
                raise ValueError('Length of order_y vector is wrong')
            PF = PF[order_y,:]
            self._test = stateVariables.copy()
            stateVariables = np.array(stateVariables)[order_y]

        if len(order_x) > 0:
            if len(order_x) != len(set(order_x)):
                raise ValueError('Duplicates in order_x!')
            if not len(order_x) == PF.shape[1]:
                raise ValueError('Length of order_x vector is wrong')
            PF = PF[:,order_x]

        if method == 'sum':
            PF = PF / PF.sum(axis=0, keepdims=True)
        elif method == 'max':
            PF = PF / PF.max(axis=0, keepdims=True)
        elif method == 'notnorm':
            pass


        if f == None:
            f = plot()

        cmap = cm.gray_r
        norm = Normalize(vmin=lims[0], vmax=lims[1])
        print(PF.shape)
        nrows, ncols = PF.shape
#        for i in range(nrows):
#            for j in range(ncols):
#                rect = patches.Rectangle((j, i), 1, 1, linewidth=0, edgecolor='none', facecolor=plt.cm.gray_r(PF[i, j]))
#                f.ax[0].add_patch(rect)
        #cax = f.ax[0].imshow(PF, aspect='auto', cmap=cmap, norm=norm)
        cax = f.ax[0].imshow(
            PF,
            aspect='auto',
            cmap=cmap,
            norm=norm,
            origin='lower',
            extent=[0, PF.shape[1], 0,PF.shape[0]]  # [x0, x1, y0, y1]
        )
        cax = f.fig.add_axes([f.ax[0].get_position().x1 + 0.01, f.ax[0].get_position().y0, 0.02, f.ax[0].get_position().height])
        f.fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)

        xmin = f.ax[0].get_xlim()[0]
        ymin = f.ax[0].get_ylim()[0]
        ticks = np.arange(N / 2, int(PF.shape[1]), N) + xmin
        imageX = np.arange(0, int(PF.shape[1] / N)) + 1
        imageY = np.arange(0, PF.shape[0])         + ymin + .5
        f.ax[0].set_xticks(ticks)
        f.ax[0].set_xticklabels(labels=imageX)
        f.ax[0].set_yticks(imageY, stateVariables)

        f.xlabel('Modes')
        f.ylabel('States')
        f.ax[0].set_xticks([N * x + xmin for x in range(int(PF.shape[1] / N) + 1)], minor=True)
        f.ax[0].set_yticks([x + ymin for x in range(PF.shape[0] + 1)], minor=True)
        f.ax[0].grid(which='minor', color='k', linestyle='-', linewidth=.3)
        f.ax[0].tick_params(axis='x', labelrotation=0)
        f.ax[0].tick_params(which='minor', size=0)
        f.ax[0].xaxis.set_tick_params(labelsize=fs)
        f.ax[0].yaxis.set_tick_params(labelsize=fs)
        cax.yaxis.set_tick_params(labelsize=fs)
        return f
        
    def plot_eigs(self, damping=[], max=200, n_max=np.inf,f=None):
        """
        Plot the eigenvalues of the system.

        Args:
        - damping (list): List of damping ratios to plot.
        - max (int): Maximum number of eigenvalues to plot.
        - eigs (bool): Flag indicating whether to use precomputed eigenvalues.
        - n_max (int): Maximum number of eigenvalues to display annotations for.

        Returns:
        None
        """
        param_list = self.parametric_val 

        DN = self.eigs
        N = self.eigs.shape[0]

        if f == None:
            f = plot()
        f.format()


        cmap = plt.get_cmap('viridis')
        norm = Normalize(vmin=param_list.min(), vmax=param_list.max())
        scalar_map = cm.ScalarMappable(norm=norm, cmap=cmap)

        for n in range(N):
            D = DN[n]
            p = param_list[n]
            color = scalar_map.to_rgba(p)

            im = f.ax[0].scatter(np.real(D), np.imag(D), marker='o', color=color, s=50)
            if n == 0:
                for i, txt in enumerate(range(len(D))):
                    if i > n_max:
                        continue
                    plt.annotate(txt + 1, (np.real(D[i]), np.imag(D[i])),
                                    xytext=(3, 3.5), textcoords='offset points')

            print(f'P={param_list[n]} --> {D.real.max():.2E} <-- Max real value')
            
            for _i, _d in enumerate(D):
                if _d.real > 0:
                    print(f'Eigenvalue {_i + 1} is {_d}.')

        cax = f.fig.add_axes([f.ax[0].get_position().x1 + 0.01, f.ax[0].get_position().y0, 0.02, f.ax[0].get_position().height])
        f.fig.colorbar(im, cax=cax, norm=norm)
        cax.set_yticklabels([f'{x:.0f}' for x in np.linspace(param_list.min(), param_list.max(), 6)])

        x = np.arange(max, .5, 1)
        for y in damping:
            f.ax[0].plot(x, x / y, 'b--', label=f'{y * 100}%')
            f.ax[0].plot(x, -x / y, 'b--')

        f.xlabel('Real Axis')
        f.ylabel('Imaginary Axis')
        f.format()
        return f

    ################################################################
    #Function to avoid eigenvalue crossing when performing parameter variation

    def match_eigenvalues(D_ref, D_new):
        matched_indices = []
        available_indices = np.arange(len(D_new))
        
        for d_ref in D_ref:
            # Find the index of the closest eigenvalue in D_new to d_ref
            distances = np.abs(D_new[available_indices] - d_ref)
            closest_index = available_indices[np.argmin(distances)]
            matched_indices.append(closest_index)
            # Remove the matched index from the list of available indices
            available_indices = np.delete(available_indices, np.argmin(distances))
        
        return matched_indices

    def reshape_array(self, arr):
        """
        Reshape a 3D array into a 2D array.

        Args:
        - arr (array): 3D array to be reshaped.

        Returns:
        - reshaped_list (array): 2D array after reshaping.

        # Transpose to shape (n_states, n_modes, n_params)
        arr_transposed = np.transpose(arr, (1, 2, 0))
        # Reshape to (n_states, n_modes * n_params)
        return arr_transposed.reshape(arr.shape[1], arr.shape[2] * arr.shape[0])
        """
        num_blocks, rows_per_block, elements_per_row = arr.shape
        reshaped_list = []
        for row_idx in range(rows_per_block):
            row_elements = []
            for element_idx in range(elements_per_row):
                for block_idx in range(num_blocks):
                    row_elements.append(arr[block_idx, row_idx, element_idx])
            reshaped_list.append(row_elements)
        return np.array(reshaped_list)


## Experimental
def plot_PFs_im(self, lims=[0, 1], method='sum', reduce=False, fs=6, w_scale=1, h_scale=1.5):
    """
    Plot Participation Factors (PFs) of the system.

    Args:
    - lims (list): Lower and upper limits for color normalization.
    - method (str): Method for calculating PFs ('sum' or 'max').
    - reduce (bool): Flag to reduce PFs by combining similar states.
    - fs (int): Font size for plot labels.

    Returns:
    None
    """
    stateVariables = [k for k in self.x]
    N = self.PFs.shape[0]
    PF = self.reshape_array(self.PFs)

    if reduce:
        red_states = np.unique([re.sub(r"[n,d]\d", "", s) for s in self.x])
        states = np.array([re.sub(r"[n,d]\d", "", s) for s in self.x])
        red_PF = np.zeros((len(red_states), len(states) * N))
        for i, red_state in enumerate(red_states):
            ind = (states == red_state)
            red_PF[i, :] = PF[ind, :].sum(axis=0)
        self.PF = PF
        PF = red_PF
        stateVariables = red_states

    if method == 'sum':
        PF = PF / PF.sum(axis=0)
    elif method == 'max':
        PF = PF / PF.max(axis=0)
    elif method == 'notnorm':
        pass

    # Normalize the data for color mapping
    norm = Normalize(vmin=lims[0], vmax=lims[1])
    cmap = cm.gray_r

    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(w_scale * PF.shape[1], h_scale * PF.shape[0]))

    # Use imshow for faster rendering
    cax = ax.imshow(PF, aspect='auto', cmap=cmap, norm=norm)

    # Add colorbar
    colorbar = fig.colorbar(cax, ax=ax)
    colorbar.ax.tick_params(labelsize=fs)

    # Set ticks and labels
    nrows, ncols = PF.shape
    ticks = np.arange(N / 2, int(PF.shape[1]), N)
    imageX = np.arange(1, int(PF.shape[1] / N) + 1)
    imageY = np.arange(PF.shape[0])

    ax.set_xticks(ticks)
    ax.set_xticklabels(imageX)
    ax.set_yticks(imageY)
    ax.set_yticklabels(stateVariables)

    ax.set_xlabel('Modes', fontsize=fs)
    ax.set_ylabel('States', fontsize=fs)
    ax.tick_params(axis='x', labelsize=fs)
    ax.tick_params(axis='y', labelsize=fs)

    ax.grid(which='minor', color='k', linestyle='-', linewidth=0.3)
    ax.tick_params(which='minor', size=0)
    