class Grid:
	def __init__(self, name, axis, unit=None):
		from numpy import array
		from ..physics.physarray import PhysArray

		if unit is not None:
			axis = PhysArray(axis, unit=unit)

		if axis.ndim != 1:
			raise ValueError('Grid must be 1-dimensional')
		
		self.name = name
		self.axis = axis
	'''
	def fillGrid(self):
		self.radius = self.parent.file['xzn'][:]
		self.mass = self.parent.file['mass'][:]
		self.bar_mass = self.parent.file['massb'][:]
		self.grav_mass = self.parent.file['massg'][:]
		if self.dim > 1:
			self.theta = self.parent.file['theta'][:]
			if self.dim > 2:
				self.phi = self.parent.file['phi'][:]	
	'''
	def excludeInterior(self, minlim=0.0):
		'''
			Exclude the interior of the star, where the enclosed mass is less 
			than 1.4 Msun.
		'''
		return self.axis > minlim

class GridList(list):
	def axisNames(self, index):
		return self[index].name
	
	def hasAxis(self, name):
		try:
			for i in range(len(self)):
				if self.axisNames(i) == name:
					return True
		except:
			return False
		
	def getAxis(self, name):
		if isinstance(name, str):
			try:
				for i in range(len(self)):
					if self.axisNames(i) == name:
						return self[i].axis
			except:
				return None
			
		elif isinstance(name, int):
			try:
				return self[name].axis
			except:
				return None