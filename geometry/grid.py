class Grid:
	def __init__(self, parent, ndim):
		self.parent = parent
		self.dim = ndim
		self.radius = None
		self.mass = None
		self.bar_mass = None
		self.grav_mass = None
		if ndim > 1:
			self.theta = None
			if ndim > 2:
				self.phi = None

	def fillGrid(self):
		self.radius = self.parent.file['xzn'][:]
		self.mass = self.parent.file['mass'][:]
		self.bar_mass = self.parent.file['massb'][:]
		self.grav_mass = self.parent.file['massg'][:]
		if self.dim > 1:
			self.theta = self.parent.file['theta'][:]
			if self.dim > 2:
				self.phi = self.parent.file['phi'][:]