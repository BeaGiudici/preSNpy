from numpy import ndarray
from ..geometry.grid import Grid, GridList

class PhysArray(ndarray):
	def __new__ (self, data, unit=None):
		obj = ndarray.__new__(self, data.shape, dtype=data.dtype, buffer=data)
		self.unit = unit
		self.grid = None

		self._make_grid(obj)
		return obj
	
	def _make_grid(self):
		from numpy import arange

		grid = self.grid
		self.grid = GridList()

		if not grid:
			# Generate grid
			for (i,l) in enumerate(self.shape):
				self.grid.append(Grid('xyz'[i], arange(l)))