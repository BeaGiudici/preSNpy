from numpy import ndarray, array
from astropy.units import Unit
from ..geometry.grid import Grid, GridList

def createAxes(func):
	from functools import wraps

	@wraps(func)
	def plotWithAx(self, *args, **kwargs):
		import matplotlib.pyplot as plt
		#plt.style.use('default_style.mlpstyle')
		from matplotlib.axes import Axes
		plt.ion()
		if len(args) > 0 and isinstance(args[0], Axes):
			ax = args[0]
			args = args[1:]
		else:
			ax = plt.gca()
		return func(self, ax, *args, **kwargs)
	return plotWithAx

class PhysArray(ndarray):
	def __new__ (self, data, unit=None, grid=None):
		'''
			Parameters:
			data (ndarray): The data to be stored.
			unit (str): The unit of the data.
			grid (Grid): The grid associated with the data.
		'''
		if isinstance(data, ndarray):
			obj = data.view(PhysArray)
		else:
			if isinstance(data, list):
				data = array(data)
			obj = ndarray.__new__(self, data.shape, dtype=data.dtype, buffer=data)
		# Set additional attributes
		if unit is not None:
				obj.unit = Unit(unit)  # Ensure the unit is compatible with astropy.units
		else:
				obj.unit = None
		setattr(obj, 'grid', grid)

		return obj

	@createAxes
	def plot(self, ax, *args, **kwargs):
		'''
			Plot 1D data.

			Parameters:
			ax (matplotlib.axes.Axes object): The axes to plot on.
			*args, **kwargs: Arguments and keyword arguments passed to the 
												plot function.
		'''
		import matplotlib

		boundaries = kwargs.pop('boundaries', None)
		draw = kwargs.pop('draw', True)
		axis = kwargs.pop('axis', 'radius')

		if self.ndim == 1:
			x = self.grid.getAxis(axis)
			y = self
			ax.plot(x, y, *args, **kwargs)
			if matplotlib.is_interactive() and draw:
				ax.get_figure().canvas.draw()
			return ax
		else:
			raise Exception('Data must be 1-dimensional')
