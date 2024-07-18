from .physarray import PhysArray
import numpy as np

class Hydro:
	def __init__(self, parent, grid):
		self.parent = parent
		self.grid = grid
		
	def fillHydro(self, filename, type):
		if type == 'postbounce':
			data = np.genfromtxt(filename, skip_header=6, max_rows=self.parent.nx, \
														usecols=(5,6,7,9,10,11), unpack=True)
			
			setattr(self, 'density', PhysArray(data[1], unit='g/cm^3', \
																			grid=self.grid))
			setattr(self, 'pressure', PhysArray(data[4], unit='erg/cm^3', \
																			 grid=self.grid))
			setattr(self, 'temperature', PhysArray(data[2]*11604525006.17, unit='K',\
														grid=self.grid))
			setattr(self, 'entropy', PhysArray(data[3], unit='k_B', grid=self.grid))
			setattr(self, 'velocity', PhysArray(data[0], unit='cm/s', \
																			 grid=self.grid))
			setattr(self, 'energy', PhysArray(data[5], unit='erg/g', grid=self.grid))

	def rhor3(self):
		return self.density * (self.density.grid[0].axis**3)