class Grid:
	def __init__(self, ndim):
		self.dim = ndim
		self.radius = None
		self.mass = None
		self.bar_mass = None
		self.grav_mass = None
		if ndim > 1:
			self.theta = None
			if ndim > 2:
				self.phi = None