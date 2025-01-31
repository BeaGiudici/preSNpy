from preSNpy.model import Postbounce1D
import matplotlib.pyplot as plt
import os
import numpy as np
from preSNpy.global_vars import PLOTSDIR, POSTDIR

plt.style.use('../default_style.mlpstyle')

fig, ax = plt.subplots(1, 2, figsize=[20,10], constrained_layout=True)

# Plot settings
ax[0].set_xlim(2e9,5e11)
ax[1].set_xlim(4e9,7e11)
ax[0].set_xscale('log')
ax[1].set_xscale('log')
ax[0].set_ylim(1.5e30, 1.5e32)
ax[0].set_yscale('log')
ax[1].set_ylim(8e29, 9e32)
ax[1].set_yscale('log')
ax[1].yaxis.set_ticks_position('right')
ax[1].yaxis.set_label_position('right')

models = {
    'model1' : {
        'im' : 0,
        'name' : 'SW13.1',
        'filename' : 'hs13.1_postbounce'
    },
    'model2' : {
        'im' : 1,
        'name' : 'SW26.2',
        'filename' : 'hs26.2_postbounce'
    },
}

files = [os.path.join(POSTDIR, 'hs13.1_postbounce')]

for model in models.keys():
    m = Postbounce1D(os.path.join(POSTDIR, model.filename))
    rhor3 = m.hydro.rhor3()

    rCOHe, mCOHe, idxCOHe = m.nuclear.shellInterface(['c12','o16'], 'he4')
    rHeH = m.nuclear.shellInterface('he4', 'h1')[0]
    idx2HeH = np.argmin(np.fabs(m.radius - 2.0*rHeH))

    # Plot rho r^3
    rhor3.plot(ax[model.im], ls='-', color='black', zorder=2)

    # Single figure
    fig_s, ax_s = plt.subplots()
    rhor3.plot(ax_s, ls='-', color='black', zorder=2)
    ax_s.set_yscale('log')
    ax_s.set_xscale('log')
    ax_s.set_xlim(ax[model.im].get_xlim())
    ax_s.set_ylim(ax[model.im].get_ylim())
    ax_s.set_ylabel(r'$\rho r^3$ [g]')
    ax_s.set_xlabel('Radius [cm]')

    # Plots shaded areas
    ax[model.im].set_xlabel('Radius [cm]')
    ax[model.im].set_ylabel(r'$\rho r^3$ [g]')
    ax_s.axvline(rCOHe, ls='-.', color='red', zorder=3)
    ax_s.axvline(rHeH, ls='--', color='red', zorder=3)
    ax_s.text(0.82, 0.92, model.name, fontweight='bold', color='black', \
                transform=ax_s.transAxes, zorder=4)
    ax_s.set_xlabel('Radius [cm]')
    ax_s.set_ylabel(r'$\rho r^3$ [g]')
    
    xfill = np.linspace(rCOHe, rHeH, 10)
    ax[model.im].fill_between(xfill, rhor3[idxCOHe], color='blue', alpha=0.5, zorder=1)
    ax_s.fill_between(xfill, rhor3[idxCOHe], color='blue', alpha=0.5, zorder=1)
    ax_s.axvline(rCOHe, ls='-.', color='red', zorder=3)
    ax_s.axvline(rHeH, ls='--', color='red', zorder=3)
    fig_s.savefig(os.path.join(PLOTSDIR, model, 'rhor3_shadeCOHe.pdf'), bbox_inches='tight')
    xfill = np.linspace(rHeH, 2.0*rHeH, 10)
    ax[model.im].fill_between(xfill, rhor3[idx2HeH], color='cyan', alpha=0.5, zorder=1)
    ax_s.fill_between(xfill, rhor3[idx2HeH], color='cyan', alpha=0.5, zorder=1)
    fig_s.savefig(os.path.join(PLOTSDIR, model, 'rhor3_shadeBoth.pdf'), bbox_inches='tight')

    ax[model.im].axvline(rCOHe, ls='-.', color='red', zorder=3)
    ax[model.im].axvline(rHeH, ls='--', color='red', zorder=3)
    ax[model.im].text(0.72, 0.92, model.name, fontweight='bold', color='black', \
                transform=ax[model.im].transAxes, zorder=4)
    

plt.subplots_adjust(wspace=0.01, hspace=0.01)
fig.savefig(os.path.join(PLOTSDIR, 'rhor3_shaded.pdf'), bbox_inches='tight')
