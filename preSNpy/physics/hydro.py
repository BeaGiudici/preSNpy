from .physarray import PhysArray
import numpy as np

class Hydro:
	def __init__(self, parent, grid):
		self.parent = parent
		self.grid = grid

	def updateGrid(self, grid):
		self.grid = grid
		
	def fillHydro(self, filename, type):
		if type == 'postbounce':
			data = np.genfromtxt(filename, skip_header=6, max_rows=self.parent.nx, \
														usecols=(5,6,7,9,10,11), unpack=True)
			
			setattr(self, 'density', PhysArray(data[1], unit='g/cm^3', \
														grid=self.grid, name='density', symbol=r'$\rho$'))
			setattr(self, 'pressure', PhysArray(data[4], unit='erg/cm^3', \
															name='pressure', grid=self.grid, symbol=r'$p$'))
			setattr(self, 'temperature', PhysArray(data[2]*11604525006.17, unit='K',\
														grid=self.grid, symbol=r'$T$', name='temperature'))
			setattr(self, 'entropy', PhysArray(data[3], unit='k_B', grid=self.grid, \
																			symbol=r'$S$', name='entropy'))
			setattr(self, 'velocity', PhysArray(data[0], unit='cm/s', \
						name='radial velocity', grid=self.grid, symbol=r'$v_\mathrm{x}$'))
			setattr(self, 'energy', PhysArray(data[5], unit='erg/g', grid=self.grid, \
																		 symbol=r'$e$', name='energy'))
		
		elif type == 'kepler':
			data = filename
			setattr(self, 'density', PhysArray(data['cell density'].astype(float).fillna(0.0).values[:],
                                      unit='g/cm^3', grid=self.grid, \
																			name='density', symbol=r'$\rho$'))
			setattr(self, 'pressure', PhysArray(data['cell pressure'].astype(float).fillna(0.0).values[:],
                                       unit='erg/cm^3', grid=self.grid, \
																				name='pressure', symbol=r'$p$'))
			setattr(self, 'temperature', PhysArray(data['cell temperature'].astype(float).fillna(0.0).values[:],
                                          unit='K', grid=self.grid, \
																						name='temeprature', symbol=r'$T$'))
			setattr(self, 'entropy', PhysArray(data['cell specific entropy'].astype(float).fillna(0.0).values[:],
                                      unit='k_B', grid=self.grid, \
																			name='entropy', symbol=r'$S$'))
			setattr(self, 'velocity', PhysArray(data['cell outer velocity'].astype(float).fillna(0.0).values[:],
                                       unit='cm/s', grid=self.grid, \
																			name='radial velocity', symbol=r'$v_\mathrm{x}$'))
			if 'cell specific energy' in data.keys():
				setattr(self, 'energy', PhysArray(data['cell specific energy'].astype(float).fillna(0.0).values[:],
                                     unit='erg/g', grid=self.grid, \
																		name='specific energy', symbol=r'$e$'))
			elif 'cell spec. int. energy' in data.keys():
				setattr(self, 'energy', PhysArray(data['cell spec. int. energy'].astype(float).fillna(0.0).values[:],
																		 unit='erg/g', grid=self.grid, \
																		name='specific internal energy', symbol=r'$e_\mathrm{int}$'))
			setattr(self, 'omega', PhysArray(data['cell angular velocity'].astype(float).fillna(0.0).values[:],
                                    unit='rad/s', grid=self.grid, \
																		name='angular velocity', symbol=r'$\Omega'))
			if 'b_r' in data.keys():
				setattr(self, 'B_r', PhysArray(data['b_r'].astype(float).fillna(0.0).values[:],
                                   unit='G', grid=self.grid, \
																	 name='poloidal magnetic field', symbol=r'$B_\mathrm{r}$'))
				setattr(self, 'B_phi', PhysArray(data['b_phi'].astype(float).fillna(0.0).values[:],
                                   unit='G', grid=self.grid, \
																	name='toroidal magnetic field', symbol=r'$B_{\phi}$'))

		elif type == 'mesa':
			data = filename
			setattr(self, 'density', PhysArray(10 ** data['logRho'].values[:],
                                      unit='g/cm^3', grid=self.grid, \
																				name='density', symbol=r'$\rho$'))
			setattr(self, 'pressure', PhysArray(10 ** data['logP'].values[:],
                                       unit='erg/cm^3', grid=self.grid, \
																				name='pressure', symbol=r'$p$'))
			setattr(self, 'temperature', PhysArray(10 ** data['logT'].astype(float).fillna(0.0).values[:],
                                          unit='K', grid=self.grid, \
																						name='temperature', symbol=r'$T$'))
			setattr(self, 'entropy', PhysArray(data['entropy'].values[:],
                                      unit='k_B', grid=self.grid, \
																				name='entropy', symbol=r'$S$'))
			setattr(self, 'velocity', PhysArray(data['velocity'].values[:],
                                       unit='cm/s', grid=self.grid, \
																				name='radial velocity', symbol=r'$v_\mathrm{x}$'))
			if 'energy' in data.keys():
				setattr(self, 'energy', PhysArray(data['energy'].values[:],
                                     unit='erg/g', grid=self.grid, \
																			name='energy', symbol=r'$e$'))
			setattr(self, 'omega', PhysArray(data['omega'].values[:],
                                    unit='rad/s', grid=self.grid, \
																			name='engular velocity', symbol=r'$\Omega$'))
			if 'dynamo_log_B_r' in data.keys():
				setattr(self, 'B_r', PhysArray(10 ** data['dynamo_log_B_r'].astype(float).fillna(-99).values[:],
                                   unit='G', grid=self.grid, \
																		name='poloidal magnetic field', symbol=r'$B_\mathrm{r}$'))
				setattr(self, 'B_phi', PhysArray(10 ** data['dynamo_log_B_phi'].astype(float).fillna(-99).values[:],
                                   unit='G', grid=self.grid, \
																		name='toroidal magentic field', symbol=r'$B_{\phi}$'))


	def rhor3(self):
		return PhysArray(self.density * (self.density.grid[0].axis**3), unit='g', \
											grid=self.grid, name='rescaled density', symbol=r'$\rho \cdot r^3$')