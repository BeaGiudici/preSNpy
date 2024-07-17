import numpy as np
from .physarray import PhysArray

class Nuclear:
	def __init__(self, parent):
		self.parent = parent
		self.n1 = None
		self.H1 = None
		self.He4 = None
		self.C12 = None
		self.O16 = None
		self.Ne20 = None
		self.Mg24 = None
		self.Si28 = None
		self.S32 = None
		self.Ar36 = None
		self.Ca40 = None
		self.Ti44 = None
		self.Cr48 = None
		self.Fe52 = None
		self.Ni56 = None
		self.X56 = None
		self.Ye = None
		self.grid = None
	
	def fillNuclear(self, grid):
		self.grid = grid
		self.n1 = PhysArray(self.parent.file['xnu'][0][...], unit='1', grid=grid)
		self.H1 = PhysArray(self.parent.file['xnu'][1][...], unit='1', grid=grid)
		self.He4 = PhysArray(self.parent.file['xnu'][2][...], unit='1', grid=grid)
		self.C12 = PhysArray(self.parent.file['xnu'][3][...], unit='1', grid=grid)
		self.O16 = PhysArray(self.parent.file['xnu'][4][...], unit='1', grid=grid)
		self.Ne20 = PhysArray(self.parent.file['xnu'][5][...], unit='1', grid=grid)
		self.Mg24 = PhysArray(self.parent.file['xnu'][6][...], unit='1', grid=grid)
		self.Si28 = PhysArray(self.parent.file['xnu'][7][...], unit='1', grid=grid)
		self.S32 = PhysArray(self.parent.file['xnu'][8][...], unit='1', grid=grid)
		self.Ar36 = PhysArray(self.parent.file['xnu'][9][...], unit='1', grid=grid)
		self.Ca40 = PhysArray(self.parent.file['xnu'][10][...], unit='1', \
												grid=grid)
		self.Ti44 = PhysArray(self.parent.file['xnu'][11][...], unit='1', \
												grid=grid)
		self.Cr48 = PhysArray(self.parent.file['xnu'][12][...], unit='1', \
												grid=grid)
		self.Fe52 = PhysArray(self.parent.file['xnu'][13][...], unit='1', \
												grid=grid)
		self.Ni56 = PhysArray(self.parent.file['xnu'][14][...], unit='1', \
												grid=grid)
		self.X56 = PhysArray(self.parent.file['xnu'][15][...], unit='1', grid=grid)
		self.Ye = PhysArray(self.parent.file['xnu'][16][...], unit='1', grid=grid)

	def shellInterface(self, elm1, elm2):
		'''
    Get the coordinates (both in radius and mass) of the shell interface
		between two layers.
		'''
		exclude = self.grid[1].excludeInterior(minlim=1.4)
		mass = self.grid[1].axis[exclude]
		radius = self.grid[0].axis[exclude]
		N = len(mass)

		if isinstance(elm1, str):
			element1 = getattr(self, elm1)[exclude]
		elif isinstance(elm1, list):
			element1 = getattr(self, elm1[0])[exclude]
			for el in elm1[1:]:
				element1 += getattr(self, el)[exclude]
		else:
			raise TypeError('elm1 must be a string or a list of strings')
		
		if isinstance(elm2, str):
			element2 = getattr(self, elm2)[exclude]
		elif isinstance(elm2, list):
			element2 = getattr(self, elm2[0])[exclude]
			for el in elm2[1:]:
				element2 += getattr(self, el)[exclude]
		else:
			raise TypeError('elm2 must be a string or a list of strings')
		
		shell1 = np.empty(N, dtype=bool)
		shell2 = np.empty(N, dtype=bool)

		# Define shell1 and shell2 looking at the composition
		shell1 = element1 > element2
		shell2 = element2 > element1

		# Max values in the respective cells
		max1 = np.max(element1[shell1])
		max2 = np.max(element2[shell2])

		# Find where element2 is larger than half its max value
		idx2 = element2 > (max2 / 2.)

		# Find where the element is larger than half its max value INSIDE THE 
  	# RESPECTIVE CELL
		idx_in_shell_2 = np.empty(len(idx2), dtype=bool)

		#for j in range(len(idx_in_shell_2)):
			# element2 is inside the cell AND is larger than max/2
		idx_in_shell_2 = shell2 & idx2

		# mass coordinate of the interface
		m_interface = float(np.nanmin(mass[idx_in_shell_2]))
		# radius coordinate of the interface 
		r_interface = float(np.nanmin(radius[idx_in_shell_2]))
		# index of the interface
		idx_interface = np.argmin(np.fabs(self.grid[0].axis - r_interface))
		
		return r_interface, m_interface, idx_interface
	
	def QHe(self):
		'''
			Compute the normalized integral of rhor3 on the He composition 
			shell as defined in Giudici et al. 2024.
		'''
		from scipy.integrate import trapz

		rCOHe, mCOHe, idxCOHe = self.shellInterface(['C12', 'O16'], 'He4')
		rHeH, mHeH, idxHeH = self.shellInterface('He4', 'H1')
		rhor3 = self.parent.hydro.rhor3()
		
		curve_integral = trapz(rhor3[idxCOHe:idxHeH+1], \
													 self.grid[0].axis[idxCOHe:idxHeH+1])
		rectangle = (rHeH - rCOHe) * rhor3[idxCOHe]

		return float(curve_integral / rectangle)
	
	def QH(self, **kwargs):
		'''
			Compute the normalized integral of rhor3 on the H composition 
			shell as defined in Giudici et al. 2024.
		'''
		from scipy.integrate import trapz

		rHeH, mHeH, idxHeH = self.shellInterface('He4', 'H1')
		rmax = kwargs.pop('rmax', 2.0 * rHeH)
		idx_max = np.argmin(np.fabs(self.grid[0].axis - rmax))
		rhor3 = self.parent.hydro.rhor3()

		curve_integral = trapz(rhor3[idxHeH:idx_max], \
													 self.grid[0].axis[idxHeH:idx_max])
		rectangle = (rmax - rHeH) * rhor3[idx_max]

		return float(curve_integral / rectangle)
	
	def element_mass(self, element):
		'''
			Return the mass of a given element.
		'''
		if isinstance(element, str):
			if not hasattr(self, element):
				raise AttributeError(f'{element} not found in nuclear data')
			X = getattr(self, element)
		else:
			raise TypeError('element must be a string or a list of strings')

		volume = self.parent.dV()
		density = self.parent.hydro.density
		mass = np.sum(X[1:] * np.diff(self.grid[1].axis))
		mass += X[0] * self.grid[1].axis[0]
		return mass