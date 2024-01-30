from .physarray import PhysArray

class Hydro:
	def __init__(self, parent):
		self.parent = parent
		self.density = None
		self.pressure = None
		self.temperature = None
		self.entropy = None
		self.velocity = None
		self.internal_energy = None
		self.grid = None
		
	def fillHydro(self, grid):
		self.density = PhysArray(self.parent.file['den'][...], unit='g/cm^3', \
													 grid=grid)
		self.pressure = PhysArray(self.parent.file['pre'][...], unit='erg/cm^3', \
													 grid=grid)
		self.temperature = PhysArray(self.parent.file['tem'][...], unit='K', \
													 grid=grid)
		self.entropy = PhysArray(self.parent.file['sto'][...], unit='k_B', \
													 grid=grid)
		self.velocity = PhysArray(self.parent.file['vex'][...], unit='cm/s', \
													 grid=grid)
		self.internal_energy = PhysArray(self.parent.file['eint'][...], unit=\
																	 'erg/g')

	def rhor3(self):
		return self.density * (self.grid[0].axis**3)