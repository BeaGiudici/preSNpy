import matplotlib.pyplot as plt
import PromPy.global_vars as gv
from PromPy.utility.getinfo import getModelPlotSettings, getPostbounceFile
from preSNpy.model import Postbounce1D
import os

plt.style.use('../default_style.mlpstyle')

fig = plt.figure(figsize=(20, 8), constrained_layout=True)
gs = fig.add_gridspec(1, 2, width_ratios=[1, 1], wspace=0.01)

ax1 = fig.add_subplot(gs[0])
ax1.set_xlabel('Radius [cm]')
ax1.set_ylabel(r'$\rho$ [g/cm$^3$]')
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_ylim([3e-10,3e13])

ax2 = fig.add_subplot(gs[1])
ax2.set_xlabel('Baryonic Mass [M$_{\odot}$]')
ax2.set_yscale('log')
ax2.set_yticklabels([])
ax2.set_ylim([3e-10,3e13])

for model in gv.MODELS:
  m = Postbounce1D(getPostbounceFile(model))
  ps = getModelPlotSettings(model)

  m.hydro.density.plot1D(ax1, label=ps['label'], color=ps['color'], \
                         linestyle=ps['linestyle'])
  m.hydro.density.plot1D(ax2, axis='mass', label=ps['label'], \
                        color=ps['color'], linestyle=ps['linestyle'])

subax11 = ax1.inset_axes([0.03, 0.07, 0.42, 0.4], xlim=[9e7,5e9], ylim=[4e2, 4e7])
ax1.indicate_inset_zoom(subax11, edgecolor='black', linewidth=2)
subax11.set_xscale('log')
subax11.set_yscale('log')
subax11.yaxis.set_ticks_position('right')
for model in ['HS13_1', 'HS18_2', 'HS19_8', 'HS20_8', 'HS26_2']:
  m = Postbounce1D(getPostbounceFile(model))
  ps = getModelPlotSettings(model)
  m.hydro.density.plot1D(subax11, color=ps['color'], linestyle=ps['linestyle'])

ax2.legend(loc='upper right', fontsize=22)
fig.savefig(os.path.join(gv.PLOTSDIR, 'stellarProgenitors', \
            'densityProfile.pdf'), bbox_inches='tight')