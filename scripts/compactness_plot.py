
########################################################################
#
# Compute the comapctness for every postbounce model
#
########################################################################

import os
from preSNpy.model import Postbounce1D
from folders import POSTDIR, PLOTSDIR
import numpy as np
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--dir', default=POSTDIR, type=str, \
                    help='Directory where the files are')
parser.add_argument('-M', '-m', type=float, default=2.5, \
                    help='Parameter for the compactness')
parser.add_argument('--xlim', nargs='+', default=[12,30], \
                    help='Limits for the x-axis')
args = parser.parse_args()
M0 = args.M

plt.style.use('../default_style.mlpstyle')

fig, ax = plt.subplots()
ax.set_xlabel(r'$M_\mathrm{ZAMS}$ [$M_{\odot}$]')
ax.set_ylabel(r'$\xi_{2.5}$')
ax.set_xlim(args.xlim)
ax.set_ylim([1e-3, 0.49])

for file in os.listdir(args.dir):
  if '.py' in file:
    continue
  path = os.path.join(args.dir, file)
  print(path)
  m = Postbounce1D(path)
  xi = m.compactness(masslim=M0)
  Mzams = m.ZAMS_mass()
  plt.plot(Mzams.value, xi.value, ls='', marker='o', color='red')

fig.savefig(os.path.join(PLOTSDIR, 'compactness.pdf'), bbox_inches='tight')