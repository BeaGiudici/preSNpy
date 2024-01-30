import h5py
import numpy as np
from ..geometry import grid
from ..physics import hydro
from ..physics import nuclear

class Postbounce1D:
	def __init__(self, filename):
		'''
		 Postbounce profile data 1D
		'''
		self.filename = filename
		self.file = h5py.File(filename, 'r')
		self.ndim = 1

		self.grid = grid.GridList()
		self.grid.append(grid.Grid('radius', self.file['xzn'][:], unit='cm'))
		self.grid.append(grid.Grid('mass', self.file['massb'][:], unit='Msun'))


		# Initialize SCALAR quantities
		self.nx = self.file['nx'][()]
		self.nuc_ad = self.file['nnuc_ad'][()]
		self.pmass = self.file['pmass'][()]
		self.pmbar = self.file['pmbar'][()]
		self.pmgrv = self.file['pmgrv'][()]

		# Initialize GRID quantities
		#self.grid = grid.Grid(self, 1)
		#self.grid.fillGrid()

		# Initialize HYDRO quantities
		self.hydro = hydro.Hydro(self)
		self.hydro.fillHydro(self.grid)

		# Initialize NUCLEAR quantities
		self.nuclear = nuclear.Nuclear(self)
		self.nuclear.fillNuclear()


	def excludeInterior(self):
		'''
			Exclude the interior of the star, where the enclosed mass is less 
			than 1.4 Msun.
		'''
		return self.grid.mass > 1.4
	
	def starMass(self):
		'''
			Return the mass of the star.
		'''
		return self.grid.mass[-1]

	def starRadius(self):
		'''
			Return the radius of the star.
		'''
		return self.grid.radius[-1]
	
	def compactness(self, masslim=2.5):
		'''
			Return the compactness of the star.
			The compactness is defined as the ratio between the enclosed mass 
			'masslim' (in unit of Msun) and the radius that encloses that mass 
			(in unit of 1000 km).

			Reference: O'Connor & Ott (2011)
		'''
		idx = np.argmin(np.fabs(self.grid.mass - masslim))
		rlim = self.grid.radius[idx] / (1.e5) # in km
		xi = masslim / (rlim/1000)
		return xi
	
	def plot1D(self):
		pass