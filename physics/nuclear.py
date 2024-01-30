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
	
	def fillNuclear(self):
		self.n1 = PhysArray(self.parent.file['xnu'][0][...], unit='1')
		self.H1 = PhysArray(self.parent.file['xnu'][1][...], unit='1')
		self.He4 = PhysArray(self.parent.file['xnu'][2][...], unit='1')
		self.C12 = PhysArray(self.parent.file['xnu'][3][...], unit='1')
		self.O16 = PhysArray(self.parent.file['xnu'][4][...], unit='1')
		self.Ne20 = PhysArray(self.parent.file['xnu'][5][...], unit='1')
		self.Mg24 = PhysArray(self.parent.file['xnu'][6][...], unit='1')
		self.Si28 = PhysArray(self.parent.file['xnu'][7][...], unit='1')
		self.S32 = PhysArray(self.parent.file['xnu'][8][...], unit='1')
		self.Ar36 = PhysArray(self.parent.file['xnu'][9][...], unit='1')
		self.Ca40 = PhysArray(self.parent.file['xnu'][10][...], unit='1')
		self.Ti44 = PhysArray(self.parent.file['xnu'][11][...], unit='1')
		self.Cr48 = PhysArray(self.parent.file['xnu'][12][...], unit='1')
		self.Fe52 = PhysArray(self.parent.file['xnu'][13][...], unit='1')
		self.Ni56 = PhysArray(self.parent.file['xnu'][14][...], unit='1')
		self.X56 = PhysArray(self.parent.file['xnu'][15][...], unit='1')
		self.Ye = PhysArray(self.parent.file['xnu'][16][...], unit='1')

	def shellInterface(self, elm1, elm2):
		'''
    Get the coordinates (both in radius and mass) of the shell interface
		between two layers.
		'''
		exclude = self.parent.excludeInterior()
		mass = self.parent.grid.bar_mass[exclude]
		radius = self.parent.grid.radius[exclude]
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
		for j in range(N):
			shell1[j] = element1[j] > element2[j]
			shell2[j] = element2[j] > element1[j]

		# Max values in the respective cells
		max1 = np.max(element1[shell1])
		max2 = np.max(element2[shell2])

		# Find where element2 is larger than half its max value
		idx2 = element2 > (max2 / 2.)

		# Find where the element is larger than half its max value INSIDE THE 
  	# RESPECTIVE CELL
		idx_in_shell_2 = np.empty(len(idx2), dtype=bool)

		for j in range(len(idx_in_shell_2)):
			# element2 is inside the cell AND is larger than max/2
			idx_in_shell_2[j] = shell2[j] and idx2[j]

		# mass coordinate of the interface
		m_interface = np.nanmin(mass[idx_in_shell_2])
		# radius coordinate of the interface 
		r_interface = np.nanmin(radius[idx_in_shell_2])
		# index of the interface
		idx_interface = np.argwhere(idx_in_shell_2)[0][0] 
		
		return r_interface, m_interface, idx_interface