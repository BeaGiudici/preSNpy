from numpy import ndarray, array
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

def _in_grid_units(ax, x, y):
	'''
		Check for conformability in units
		As for now, it does not do anything, but it's gonna be useful once I
		fully implement the units come dio comanda
	'''
	return x, y

class PhysArray(ndarray):
	def __new__ (self, data, unit=None, grid=None, name=None, symbol=None):
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
		setattr(obj, 'unit', unit)
		setattr(obj, 'grid', grid)
		setattr(obj, 'name', name)
		if symbol == None:
			setattr(obj, 'symbol', name)
		else:
			setattr(obj, 'symbol', symbol)

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
			x, y = _in_grid_units(ax, self.grid.getAxis(axis), self)
			line, = ax.plot(x.copy(), y.copy(), *args, **kwargs)
			ax.set_xlabel('%s [%s]' % (axis, x.unit))
			ax.set_ylabel('%s [%s]' % (y.symbol, y.unit))
			if matplotlib.is_interactive() and draw:
				ax.get_figure().canvas.draw()
			return line
		else:
			raise Exception('Data must be 1-dimensional')
