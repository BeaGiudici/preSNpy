from preSNpy.physics import *
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

class PhysArray(np.ndarray):
	def __new__ (self, data, unit=None, grid=None, name=None, symbol=None):
		'''
			Parameters:
			data (ndarray): The data to be stored.
			unit (str): The unit of the data.
			grid (Grid): The grid associated with the data.
		'''
		if isinstance(data, np.ndarray):
			obj = data.view(PhysArray)
		else:
			if isinstance(data, list):
				data = np.array(data)
			obj = np.ndarray.__new__(self, data.shape, dtype=data.dtype, buffer=data)

		if unit is not None:
			# Ensure the unit is compatible with astropy.units
			setattr(obj, 'unit', u.Unit(unit))
		else:
			setattr(obj, 'unit', None)

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
			ax.set_xlabel(r'%s [$\mathrm{%s}$]' % (axis, x.unit))
			ax.set_ylabel(r'%s [$\mathrm{%s}$]' % (y.symbol, y.unit))
			if matplotlib.is_interactive() and draw:
				ax.get_figure().canvas.draw()
			return line
		else:
			raise Exception('Data must be 1-dimensional')

	def plot2D(self, ax, *args, **kwargs):
		'''
			Plot 2D model (not useful for now)
		'''
		pass

	def plotlogx(self, ax, *args, **kwargs):
		'''
			Plot with log scale only on x axis
		'''
		import matplotlib
		line, = self.plot(ax, *args, draw=False, **kwargs)

		ax.set_xscale("log")
		if matplotlib.is_interactive():
			ax.get_figure().canvas.draw()
		return line,

	def plotlogy(self, ax, *args, **kwargs):
		'''
			Plot with log scale only on y axis
		'''
		import matplotlib
		line, = self.plot(ax, *args, draw=False, **kwargs)

		ax.set_yscale("log")
		if matplotlib.is_interactive():
			ax.get_figure().canvas.draw()
		return line,

	def plotloglog(self, ax, *args, **kwargs):
		'''
			Plot with log scale on both axis
		'''
		import matplotlib
		line, = self.plot(ax, *args, draw=False, **kwargs)

		ax.set_xscale("log")
		ax.set_yscale("log")
		if matplotlib.is_interactive():
			ax.get_figure().canvas.draw()
		return line,