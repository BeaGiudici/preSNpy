from preSNpy.model import *

class PreSN1D:
  def __init__(self, filename):
    self.filename = filename
    self.ndim = 1

    # Set the grid
    radius, mass = np.genfromtxt(filename, skip_header=2, usecols=(1,2), \
                                 unpack=True)

    self.grid = grid.GridList()
    self.grid.append(grid.Grid('radius', radius, unit='cm'))
    self.grid.append(grid.Grid('mass', mass, unit='Msun'))
    self.mass = mass