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
		
	def fillHydro(self):
		self.density = PhysArray(self.parent.file['den'][...], unit='g/cm^3')
		self.pressure = PhysArray(self.parent.file['pre'][...], unit='erg/cm^3')
		self.temperature = PhysArray(self.parent.file['tem'][...], unit='K')
		self.entropy = PhysArray(self.parent.file['sto'][...], unit='k_B')
		self.velocity = PhysArray(self.parent.file['vex'][...], unit='cm/s')
		self.internal_energy = PhysArray(self.parent.file['eint'][...], unit=\
																	 'erg/g')

	def rhor3(self):
		return self.density * self.parent.grid.radius**3