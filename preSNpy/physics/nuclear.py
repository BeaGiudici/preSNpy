import numpy as np
from .physarray import PhysArray

class Nuclear:
	def __init__(self, parent, grid):
		self.parent = parent
		self.grid = grid

	def updateGrid(self, grid):
		self.grid = grid
	
	def fillNuclear(self, filename, type):
		if type == 'postbounce':
			X = np.genfromtxt(filename, skip_header=12+self.parent.nx, \
										 unpack=True)[1:]
			header = np.genfromtxt(filename, skip_header=11+self.parent.nx, \
													skip_footer=self.parent.nx, unpack=True, \
													comments='/', dtype='str')[2:]

			for (i,x) in enumerate(X):
				name = header[i][2:].lower()
				if name == 'p':
					name = 'h1'
				setattr(self, name, PhysArray(x, unit='1', grid=self.grid, name=name))
			ye = np.genfromtxt(filename, skip_header=6, max_rows=self.parent.nx, \
											usecols=(8,), unpack=True)
			setattr(self, 'ye', PhysArray(ye, unit='1', grid=self.grid, name='ye'))

		elif type == 'kepler':
			data = filename
			header = list(data.keys())
			if 'neutrons' in header:
				neutron_index = header.index('neutrons')
			elif 'nt1':
				neutron_index = header.index('nt1')
			for key in header[neutron_index:]:
				
				if key in ['neutrons', 'nt1']:
					name = 'n'
				elif key == "'Fe'":
					name = 'x56'
				else:
					name = key
				setattr(self, name, PhysArray(data[key].astype(float).fillna(0.0).values[:],
                                  unit='1', grid=self.grid, name=name))

			setattr(self, 'ye', PhysArray(data['cell y_e'].astype(float).fillna(0.0).values[:],
                                 unit='1', grid=self.grid, name='ye', symbol=r'$Y_\mathrm{e}$'))

			setattr(self, 'abar', PhysArray(data['cell a_bar'].astype(float).fillna(0.0).values[:],
                                   unit='1', grid=self.grid, name='abar', symbol=r'$\bar{A}$'))
			X = self.ye
		elif type == 'mesa':
			data = filename
			header = list(data.keys())
			neutron_index = header.index('neut')
			ni56_index = header.index('ni56')
			for key in header[neutron_index:ni56_index + 1]:
				if key == 'neut':
					name = 'n'
				elif key == "'Fe'":
					name = 'x56'
				else:
					name = key
				setattr(self, name, PhysArray(data[key].values[:],
                                  unit='1', grid=self.grid, name=name))
			setattr(self, 'ye', PhysArray(data['ye'].values[:],
                                 unit='1', grid=self.grid, name='ye', symbol=r'$Y_\mathrm{e}$'))

			setattr(self, 'abar', PhysArray(data['abar'].values[:],
                                   unit='1', grid=self.grid, name='abar', symbol=r'$\bar{A}$'))
			X = self.ye
			
		self.parent.nuc = X.shape[0] + 1

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

		rCOHe, mCOHe, idxCOHe = self.shellInterface(['c12', 'o16'], 'he4')
		rHeH, mHeH, idxHeH = self.shellInterface('he4', 'h1')
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

		rHeH, mHeH, idxHeH = self.shellInterface('he4', 'h1')
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

		mass = np.sum(X[1:] * np.diff(self.parent.mass))
		mass += X[0] * self.parent.mass[0]
		return mass
	
	def core_mass_He(self):
		'''
			Return the core mass of He
		'''
		
		mass_shell = np.insert(np.diff(self.parent.mass),0,self.parent.mass[0])
		core_mass = np.sum(mass_shell[self.h1 <= 0.2])
		return core_mass
	
	def core_mass_CO(self):
		'''
			Return the core mass of C+O
		'''
		
		mass_shell = np.insert(np.diff(self.parent.mass),0,self.parent.mass[0])
		core_mass = np.sum(mass_shell[self.he4 <= 0.2])
		return core_mass