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
		self.density = self.parent.file['den'][...]
		self.pressure = self.parent.file['pre'][...]
		self.temperature = self.parent.file['tem'][...]
		self.entropy = self.parent.file['sto'][...]
		self.velocity = self.parent.file['vex'][...]
		self.internal_energy = self.parent.file['eint'][...]

	def rhor3(self):
		return self.density * self.parent.grid.radius**3