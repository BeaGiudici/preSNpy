import h5py
import numpy as np
from ..geometry import grid
from ..hydro import hydro
from ..nuclear import nuclear

class Postbounce1D:
	def __init__(self, filename):
		'''
		 Postbounce profile data 1D
		'''
		self.filename = filename
		self.file = h5py.File(filename, 'r')

		# Initialize GRID quantities
		self.grid = grid.Grid(self, 1)
		self.grid.fillGrid()

		# Initialize HYDRO quantities
		self.hydro = hydro.Hydro(self)
		self.hydro.fillHydro()

		# Initialize NUCLEAR quantities
		self.nuclear = nuclear.Nuclear(self)
		self.nuclear.fillNuclear()

		# TO-DO: Initialize SCALAR quantities

	def excludeInterior(self):
		'''
		Exclude the interior of the star, where the enclused mass is less 
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

		\begin{equation}
			\xi_{M} = \left.\frac{M / \Msun}{R(M) / \unit[1000]{km}} 
								\right|_{t_\mathrm{bounce}}
		\end{equation}
		
		Reference: O'Connor & Ott (2011), Eq. (1)
		'''
		idx = np.argmin(np.fabs(self.grid.mass - masslim))
		rlim = self.grid.radius[idx] / (1.e5) # in km
		xi = masslim / (rlim/1000)
		return xi