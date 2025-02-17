from preSNpy.units import *

# Define a new unit
bethe = u.def_unit('bethe', 1e51 * u.erg, 'Bethe')
k_B = u.def_unit('k_B', 1.38064852e-16 * u.erg / u.K, 'Boltzmann constant', \
                 {'latex':r'k_\mathrm{B}'})