from preSNpy.physics import *

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
				setattr(self, name, PhysArray(x, unit=u.dimensionless_unscaled, \
								grid=self.grid, name=name))
			ye = np.genfromtxt(filename, skip_header=6, max_rows=self.parent.nx, \
												 usecols=(8,), unpack=True)
			setattr(self, 'ye', PhysArray(ye, unit=u.dimensionless_unscaled, \
							grid=self.grid, name='ye'))

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
                unit=u.dimensionless_unscaled, grid=self.grid, name=name))

			setattr(self, 'ye', PhysArray(data['cell y_e'].astype(float).fillna(0.0).values[:],
              unit=u.dimensionless_unscaled, grid=self.grid, name='ye', \
							symbol=r'$Y_\mathrm{e}$'))

			setattr(self, 'abar', PhysArray(data['cell a_bar'].astype(float).fillna(0.0).values[:],
              unit=u.dimensionless_unscaled, grid=self.grid, name='abar', \
							symbol=r'$\bar{A}$'))
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
                unit=u.dimensionless_unscaled, grid=self.grid, name=name))
			setattr(self, 'ye', PhysArray(data['ye'].values[:],
              unit=u.dimensionless_unscaled, grid=self.grid, name='ye', \
							symbol=r'$Y_\mathrm{e}$'))

			setattr(self, 'abar', PhysArray(data['abar'].values[:],
              unit=u.dimensionless_unscaled, grid=self.grid, name='abar', \
							symbol=r'$\bar{A}$'))
			X = self.ye
			
		self.parent.nuc = X.shape[0] + 1

	def shellInterface(self, elm1, elm2):
		'''
    Get the coordinates (both in radius and mass) of the shell interface
		between two layers.
		'''
		exclude = self.grid[1].excludeInterior(minlim=1.4)
		mass = self.grid[1].axis.value[exclude]
		radius = self.grid[0].axis.value[exclude]
		N = len(mass)

		if isinstance(elm1, str):
			element1 = getattr(self, elm1).value[exclude]
		elif isinstance(elm1, list):
			element1 = getattr(self, elm1[0]).value[exclude]
			for el in elm1[1:]:
				element1 += getattr(self, el).value[exclude]
		else:
			raise TypeError('elm1 must be a string or a list of strings')
		
		if isinstance(elm2, str):
			element2 = getattr(self, elm2).value[exclude]
		elif isinstance(elm2, list):
			element2 = getattr(self, elm2[0]).value[exclude]
			for el in elm2[1:]:
				element2 += getattr(self, el).value[exclude]
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
		idx_interface = np.argmin(np.fabs(self.grid[0].axis.value - r_interface))
		
		return r_interface, m_interface, idx_interface
	
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

		#mass = np.sum(X[1:] * np.diff(self.parent.mass.value))
		#mass += X[0] * self.parent.mass.value[0]

		mass = (X * self.parent.mass.diff()).sum()
		#mass.value += X.value[0] * self.parent.mass.value[0]
		
		return mass
	
	def core_mass_He(self):
		'''
			Return the core mass of He
		'''
		
		mass_shell = self.parent.mass.diff()
		core_mass = mass_shell.value[self.h1 <= 0.2].sum()
		return PhysArray(core_mass, unit=self.parent.mass.unit, name='He core mass')
	
	def core_mass_CO(self):
		'''
			Return the core mass of C+O
		'''
		
		mass_shell = self.parent.mass.diff()
		core_mass = mass_shell.value[self.he4 <= 0.2].sum()
		return PhysArray(core_mass, unit=self.parent.mass.unit, name='C+O core mass')