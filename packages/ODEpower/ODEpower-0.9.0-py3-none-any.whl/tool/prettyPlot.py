# Created by Robert Annuth
# robert.annuth@tuhh.de

import matplotlib as mpl
import os


pgf = os.getenv('pgf')
if os.getenv('paper'):
    pgf = True
if pgf:
    from matplotlib.backends.backend_pgf import FigureCanvasPgf
    mpl.backend_bases.register_backend('pgf', FigureCanvasPgf)
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import AutoMinorLocator
from math import sqrt

bbox = (0.5, 1)
default_width = 6.3 # width in inches
default_ratio = (sqrt(5.0) - 1.0) / 4.0 

CB91_Blue = '#2CBDFE'
CB91_Green = '#47DBCD'
CB91_Pink = '#F3A0F2'
CB91_Purple = '#9D2EC5'
CB91_Violet = '#661D98'
CB91_Amber = '#F5B14C'
color_list = [CB91_Blue, CB91_Pink, CB91_Green, CB91_Amber,
              CB91_Purple, CB91_Violet]
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=color_list)
plt.rcParams['legend.loc'] = 'upper center'
plt.rcParams['legend.fancybox'] = True
plt.rcParams['figure.dpi'] = 300

#plt.rcParams['mathtext.default'] =  'regular' 

# Set global font properties
#plt.rcParams['font.family'] = 'Arial'
#plt.rcParams['font.family'] = 'Times New Roman'
#plt.rcParams['font.weight'] = 'normal'  # You can adjust this as needed
plt.rcParams.update({'font.size': 10})


##### cmap
#A list of hex colours running between blue and purple
CB91_Grad_BP = ['#2cbdfe', '#2fb9fc', '#33b4fa', '#36b0f8',
                '#3aacf6', '#3da8f4', '#41a3f2', '#449ff0',
                '#489bee', '#4b97ec', '#4f92ea', '#528ee8',
                '#568ae6', '#5986e4', '#5c81e2', '#607de0',
                '#6379de', '#6775dc', '#6a70da', '#6e6cd8',
                '#7168d7', '#7564d5', '#785fd3', '#7c5bd1',
                '#7f57cf', '#8353cd', '#864ecb', '#894ac9',
                '#8d46c7', '#9042c5', '#943dc3', '#9739c1',
                '#9b35bf', '#9e31bd', '#a22cbb', '#a528b9',
                '#a924b7', '#ac20b5', '#b01bb3', '#b317b1']
if pgf:
    # conda install -c conda-forge mscorefonts
    # rm ~/.cache/matplotlib -rf

    plt.rcParams.update({
        #"pgf.texsystem": "lualatex",
        #"pgf.texsystem": "xelatex",
        "pgf.texsystem": "pdflatex",
        "font.family": "serif",
        "pgf.rcfonts": False,  # Do not use rc parameters for font setup
        #"font.sans-serif": "Arial",
        "text.usetex": True, # use inline math for ticks
        #"font.sans-serif": ["Comic Sans MS"],
        #"font.cursive": [ "Comic Neue", "Comic Sans MS"],
        "figure.figsize": [default_width, default_width * default_ratio],
        "pgf.preamble": "\n".join([
            #r'\usepackage[LGRgreek]{mathastext}'
            #r'\usepackage{SI}'
            # package and macros definitions are also possible, e.g.:
            # has to be pdflatex and xelatex compatible
        ]),
    })


class plot:
    def __init__(self, subplots=[], sharex=False, default=False, h_scale=-1, w_scale=-1,*args,**kwargs):
        self.sharex = sharex
        if not default:
            if w_scale == -1:
                if os.getenv('p2c'):
                    w_scale = .5
                else:
                    w_scale = 1

            if h_scale == -1:
                if os.getenv('p2c'):
                    h_scale = 2
                else:
                    h_scale = 1.2

            self.fig = plt.figure(figsize=(8.3*w_scale, 11.7/h_scale))
            if sharex:
                if subplots==[2,1]:
                    self.ax = np.array([
                        self.fig.add_axes([0.2, 0.49, 0.6, 0.2], xticklabels=[]),
                        self.fig.add_axes([0.2, 0.28, 0.6, 0.2]),
                    ])

                elif subplots==[3,1]:
                    self.ax= np.array([
                        self.fig.add_axes([0.2, 0.7, 0.6, 0.2], xticklabels=[]),
                        self.fig.add_axes([0.2, 0.49, 0.6, 0.2], xticklabels=[]),
                        self.fig.add_axes([0.2, 0.28, 0.6, 0.2]),
                    ])

                else:
                    self.ax= np.array([
                        self.fig.add_axes([0.2, 0.7, 0.6, 0.2],*args,**kwargs)
                    ])
            else:
                if subplots==[2,1]:
                    self.ax= np.array([
                        self.fig.add_axes([0.2, 0.49, 0.6, 0.2], xticklabels=[]),
                        self.fig.add_axes([0.2, 0.28, 0.6, 0.2]),
                    ])

                elif subplots==[3,1]:
                    self.ax= np.array([
                        self.fig.add_axes([0.2, 0.7, 0.6, 0.2], xticklabels=[]),
                        self.fig.add_axes([0.2, 0.49, 0.6, 0.2], xticklabels=[]),
                        self.fig.add_axes([0.2, 0.28, 0.6, 0.2]),
                    ])

                else:
                    self.ax= np.array([
                        self.fig.add_axes([0.2, 0.28, 0.6, 0.2],*args,**kwargs),
                    ])
        else:
            self.fig, self.ax = plt.subplots(*subplots,*args,**kwargs)
            try:
                if len(self.ax) > 1:
                    pass
            except:
                self.ax = np.array([self.ax])

         
    def get(self):
        return self.fig, self.ax
    
    def plot(self,x, y, pos=0, *args,**kwargs):
        self.ax[pos].plot(x,y,*args,**kwargs)

    def scatter(self,x, y, pos=0, *args,**kwargs):
        self.ax[pos].scatter(x,y,*args,**kwargs)

    def xlabel(self,label,pos=0):
        self.ax[pos].set_xlabel(label)

    def ylabel(self,label,pos=0):
        self.ax[pos].set_ylabel(label)
    
    def title(self,title,pos=0):
        self.ax[pos].set_title(title)

    def format(self,xlog=False,ylog=False):
        for i, axis in enumerate(self.ax):
            # X-Axis
            if i == len(self.ax)-1:
                if xlog:
                    axis.set_xscale('log')
                    locmin = mpl.ticker.LogLocator(base=10.0,subs=(0.2,0.4,0.6,0.8),numticks=12)
                    axis.xaxis.set_minor_locator(locmin)
                    axis.xaxis.set_minor_formatter(mpl.ticker.NullFormatter())
                    #axis.xaxis.set_minor_locator(mpl.ticker.LogLocator(base=10.0, subs=np.arange(1.0, 10.0) * 0.1, numticks=10))

                else:
                    axis.xaxis.set_minor_locator(AutoMinorLocator())
                    axis.tick_params(which='minor', length=2)
            else:
                if xlog:
                    axis.set_xscale('log')
                    locmin = mpl.ticker.LogLocator(base=10.0,subs=(0.2,0.4,0.6,0.8),numticks=12)
                    axis.xaxis.set_minor_locator(locmin)
                    axis.xaxis.set_minor_formatter(mpl.ticker.NullFormatter())

                    axis.xaxis.set_ticklabels([])
                    axis.xaxis.set_tick_params(which='minor',bottom=False)
                    axis.xaxis.set_tick_params(which='major',bottom=False)
                else:
                    axis.xaxis.set_ticklabels([])
                    axis.xaxis.set_tick_params(which='minor',bottom=False)
                    axis.xaxis.set_tick_params(which='major',bottom=False)


            # Y-Axis
            if ylog:
                axis.set_yscale('log')
                locmin = mpl.ticker.LogLocator(base=10,subs=(0.2,0.4,0.6,0.8),numticks=12)
                axis.yaxis.set_minor_locator(locmin)
                axis.yaxis.set_minor_formatter(mpl.ticker.NullFormatter())
                
            else:
                axis.yaxis.set_minor_locator(AutoMinorLocator())
                axis.tick_params(which='minor', length=2)

            axis.grid(ls='dashed')
            axis.set_axisbelow(True)


    def set(self,pos=-1,*args,**kwargs):
        if pos == -1:
            for axis in self.ax:
                axis.set(*args,**kwargs)
        else:
            self.ax[pos].set(*args,**kwargs) 

    def legend(self,default=False,ncol=None,pos=0,*args,**kwargs):
        if default:
            l = self.ax[pos].legend(loc='best',*args,**kwargs)
        else:
            l = self.ax[pos].legend(loc='lower center', bbox_to_anchor=(0.5, 1), ncol=3,*args,**kwargs)
        return l
            
    def save(self,filename, bbox_inches='tight',ftypes=['.pgf'], *args, **kwargs):
        for ftype in ftypes:
            fname = filename + ftype 
            self.fig.savefig(fname, bbox_inches=bbox_inches, *args, **kwargs)

        if os.getenv('cp_tmp'):
            fname = filename +'.svg' 
            import shutil
            from pathlib import Path
            p = Path('/mnt/cao2851/tmp/')

            # Construct the full path to the destination file
            destination = os.path.join(p, os.path.basename(fname))
            try:
                # Copy the file
                shutil.copy(fname, destination)
            except IOError as e:
                print(f"Unable to copy file. {e}")
        
        

class plot_projection:
    def __init__(self,projection='3d', w_scale=1, *args, **kwargs):
        self.figure = plt.figure(figsize=(8.3*w_scale, 11.7/1.1),*args,**kwargs)
        self.axis = np.array([
            self.figure.add_axes([0.2, 0.28, 0.6, 0.2], projection=projection),
        ])
         
    def get(self):
        return self.figure, self.axis
    
    def fig(self):
        return self.figure
    
    def ax(self):
        return self.axis
    
    def plot_surface(self, x, y, z, *args,**kwargs):
        self.axis[0].plot_surface(x, y, z,*args,**kwargs)

    def format(self):
        plt.legend(frameon=False)
        for axis in self.axis:
            axis.xaxis.set_minor_locator(AutoMinorLocator())
            axis.yaxis.set_minor_locator(AutoMinorLocator())
            axis.tick_params(which='minor', length=4)
            axis.grid(ls='dashed')
    
    def setup(self,xlabel=[], ylabel=[], figtitle=[], title=''):
        for idx, axis in enumerate(self.axis):
            axis.set(xlabel=xlabel[idx],ylabel=ylabel[idx])
        
        if not title=='': 
            plt.title(title)

    def savefig(filename, *args, **kwargs):
        plt.savefig(filename, *args, **kwargs) #'.pgf' or '.pdf'



#locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
#formatter = mdates.ConciseDateFormatter(locator)
#formatter.formats = ['%y',          # ticks are mostly years
#                        '%b',       # ticks are mostly months
#                        '%d',       # ticks are mostly days
#                        '%H:%M',    # hrs
#                        '%H:%M',    # min
#                        '%S.%f', ]  # secs
#
#formatter.offset_formats = ['',
#                            '%Y',
#                            '%b %Y',
#                            '%d %b %Y',
#                            '%d %b %Y',
#                            '%d %b %Y %H:%M', ]
#ax.xaxis.set_major_locator(locator)
#ax.xaxis.set_major_formatter(formatter)

#num = 15 
#date_format(ax[0])
#tick = [ts.strftime('%b\n%Y') if ts.year != x.index[idx-1].year
#                    else ts.strftime('%d-%H') for idx, ts in enumerate(x.index[::num])]
#
#ax[0].set_xticks(x.index[::num],tick)

def write_eig_table(filepath, eig_info):
    fd = eig_info["fd"]
    fo = eig_info["fo"]
    
    with open(filepath, "w") as f:
        f.write("\\begin{tabular}{ccc}\n")
        f.write("\\toprule\n")
        #f.write("Mode & Damping Frequency in \\unit{Hz} & Natural Frequency in \\unit{Hz} \\\\\n")
        f.write("Mode & \\shortstack{Damping Frequency\\\\ in \\unit{Hz}} & \\shortstack{Natural Frequency\\\\ in \\unit{Hz}} \\\\\n")

        f.write("\\midrule\n")
        for i, (d, o) in enumerate(zip(fd, fo), 1):
            nat_freq = 0 if abs(o) < 1e-12 else f"{abs(o):.4e}"
            f.write(f"{i} & {d:.4e} & {nat_freq} \\\\\n")
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")