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
	'''
	import warnings

	x_unit = ax.xaxis.get_units()
	y_unit = ax.yaxis.get_units()

	if x.unit != x_unit:
		try:
			x.to(x_unit)
		except:
			raise ValueError(f"Conformability error: x.unit = {x.unit}, expected {x_unit}") from None

	if y.unit != y_unit:
		try:
			y.to(y_unit)
		except Exception:
			raise ValueError(f"Conformability error: y.unit = {y.unit}, expected {y_unit}") from None

	return x, y

class PhysArray:
	def __init__ (self, data, unit=None, grid=None, name=None, symbol=None):
		'''
			Parameters:
			data (ndarray): The data to be stored.
			unit (str): The unit of the data.
			grid (Grid): The grid associated with the data.
		'''

		if unit is not None:
			# Ensure the unit is compatible with astropy.units
			#setattr(obj, 'unit', u.Unit(unit))
			self.unit = u.Unit(unit)
		else:
			#setattr(obj, 'unit', None)
			self.unit = None

		#setattr(obj, 'value', data)
		self.value = np.array(data)
		self.ndim = len(self.value.shape)

		#setattr(obj, 'grid', grid)
		#setattr(obj, 'name', name)
		self.grid = grid
		self.name = name

		if symbol == None:
			#setattr(obj, 'symbol', name)
			self.symbol = name
		else:
			#setattr(obj, 'symbol', symbol)
			self.symbol = symbol
	
	def to(self, unit):
		'''
			Return a new PhysArray with the converted unit
		'''
		if hasattr(self, 'unit'):
			oldunit = self.unit

		if oldunit != unit:
			self.value = (self.value * oldunit).to_value(unit)
			self.unit = unit
			
		return self

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

		draw = kwargs.pop('draw', True)
		axis = kwargs.pop('axis', 'radius')
		xlim = kwargs.pop('xlim', None)
		ylim = kwargs.pop('ylim', None)

		if self.ndim == 1:
			x, y = _in_grid_units(ax, self.grid.getAxis(axis), self)
			line, = ax.plot(x.value, y.value, *args, **kwargs)
			ax.set_xlabel(f'{axis} [{x.unit:latex}]')
			ax.set_ylabel(f'{y.symbol} [{y.unit:latex}]')
			ax.xaxis.set_units(x.unit)
			ax.yaxis.set_units(y.unit)
			ax.set_xlim(xlim)
			ax.set_xlim(ylim)
			if matplotlib.is_interactive() and draw:
				ax.get_figure().canvas.draw()
			return ax, line
		else:
			raise Exception('Data must be 1-dimensional')

	@createAxes
	def plot2D(self, ax, *args, **kwargs):
		'''
			Plot 2D model (not useful for now)
		'''
		pass

	@createAxes
	def plotlogx(self, ax, *args, **kwargs):
		'''
			Plot with log scale only on x axis
		'''
		import matplotlib
		ax, line = self.plot(ax, *args, draw=False, **kwargs)

		ax.set_xscale("log")
		if matplotlib.is_interactive():
			ax.get_figure().canvas.draw()
		return ax, line

	@createAxes
	def plotlogy(self, ax, *args, **kwargs):
		'''
			Plot with log scale only on y axis
		'''
		import matplotlib
		ax, line = self.plot(ax, *args, draw=False, **kwargs)

		ax.set_yscale("log")
		if matplotlib.is_interactive():
			ax.get_figure().canvas.draw()
		return ax, line

	@createAxes
	def plotloglog(self, ax, *args, **kwargs):
		'''
			Plot with log scale on both axis
		'''
		import matplotlib
		ax, line = self.plot(ax, *args, draw=False, **kwargs)

		ax.set_xscale("log")
		ax.set_yscale("log")
		if matplotlib.is_interactive():
			ax.get_figure().canvas.draw()
		return ax, line

	# Redefining operations
	def __str__(self):
		return f'{self.value} [{self.unit}]'
	
	def __repr__(self):
		return f'{self.value} [{self.unit}]'
		
	def __add__(self, other):
		'''
			self + other
		'''

		if isinstance(other, PhysArray):
			try:
				other = other.to(self.unit)
				s = self.value + other.value
				return PhysArray(s, unit=self.unit, grid=self.grid, \
										 		 symbol=self.symbol, name=self.name)
			except:
				print('Illegal sum of non-conformable units')
		else:
			raise ValueError('Sum only possible between PhysArray objects')
		
	def __radd__(self, other):
		'''
			* is commutative (other * self)
		'''
		from numbers import Number

		if not isinstance(other, (np.ndarray, np.number, Number, list)):
			raise Exception('Not Implemented')
		
		return self.__add__(other)
	
	def __iadd__(self, other):
		'''
			self += other
		'''
		if isinstance(other, PhysArray):
			if True:
				other = other.to(self.unit)
				self.value += other.value
				return self
			#except:
		#		print('Illegal sum of non-conformable units')
		else:
			raise ValueError('Sum only possible between PhysArray objects')
	
	def __sub__(self, other):
		'''
			self - other
		'''
		if isinstance(other, PhysArray):
			try:
				other = other.to(self.unit)
				s = self.value - other.value
				return PhysArray(s, unit=self.unit, grid=self.grid, \
										 		 symbol=self.symbol, name=self.name)
			except:
				print('Illegal difference of non-conformable units')
		else:
			raise ValueError('Difference only possible between PhysArray objects')
			
	def __mul__(self, other):
		'''
			self * other
		'''
		from numbers import Number
		from astropy.units import Unit, Quantity

		if not isinstance(other, (np.ndarray, np.number, Number, list, PhysArray)):
			raise Exception('Not Implemented')

		if isinstance(other, Unit):
			return Quantity(self.value, unit=other)
		else:
			if isinstance(other, PhysArray):
				r = self.value * other.value
				res = PhysArray(r, grid=self.grid)
				res.unit = self.unit * other.unit
				res.symbol = r'%s $\cdot$ %s' % (self.symbol, other.symbol)
			elif isinstance(other, np.number) or isinstance(other, Number):
				res = PhysArray(self.value * other, grid=self.grid)
				res.unit = self.unit
				res.symbol = self.symbol
			elif isinstance(other, np.ndarray) or isinstance(other, list):
				if np.array(other).shape == self.value.shape:
					res = PhysArray(self.value * other, grid=self.grid)
					res.unit = self.unit
					res.symbol = self.symbol
				else:
					raise ValueError('Array or list must be the same shape as self')
			
			return res
	
	def __rmul__(self, other):
		'''
			* is commutative (other * self)
		'''
		from numbers import Number

		if not isinstance(other, (np.ndarray, np.number, Number, list, PhysArray)):
			raise Exception('Not Implemented')
		
		return self.__mul__(other)
	
	def __div__(self, other):
		'''
			self / other
			Replaced by __truediv__ in Python 3.x
		'''
		from numbers import Number

		if not isinstance(other, (np.ndarray, np.number, Number, list, PhysArray)):
			raise Exception('Not Implemented')
		
		if isinstance(other, PhysArray):
			r = self.value / other.value
			res = PhysArray(r, grid=self.grid)
			res.unit = self.unit * (other.unit**(-1))
			res.symbol = r'%s / %s' % (self.symbol, other.symbol)
		elif isinstance(other, np.number) or isinstance(other, Number):
			res = PhysArray(self.value / other, grid=self.grid)
			res.unit = self.unit
			res.symbol = self.symbol
		elif isinstance(other, np.ndarray) or isinstance(other, list):
			if np.array(other).shape == self.value.shape:
				res = PhysArray(self.value / other, grid=self.grid)
				res.unit = self.unit
				res.symbol = self.symbol
			else:
				raise ValueError('Array or list must be the same shape as self')
		
		return res
	
	def __rdiv__(self, other):
		'''
			other / self
			Replaced by __rtruediv__ in Python 3.x
		'''
		from numbers import Number

		if not isinstance(other, (np.ndarray, np.number, Number, list, PhysArray)):
			raise Exception('Not Implemented')
		
		if isinstance(other, np.number) or isinstance(other, Number):
			res = PhysArray(other / self.value, grid=self.grid)
			res.unit = (self.unit**(-1))
			res.symbol = '1/%s' % self.symbol
		elif isinstance(other, np.ndarray) or isinstance(other, list):
			if np.array(other).shape == self.value.shape:
				res = PhysArray(other / self.value, grid=self.grid)
				res.unit = (self.unit**(-1))
				res.symbol = '1/%s' % self.symbol
			else:
				raise ValueError('Array or list must be the same shape as self')
			
		return res

	def __truediv__(self, other):
		'''
			self / other
		'''
		from numbers import Number

		if not isinstance(other, (np.ndarray, np.number, Number, list, PhysArray)):
			raise Exception('Not Implemented')
		
		if isinstance(other, PhysArray):
			r = self.value / other.value
			res = PhysArray(r, grid=self.grid)
			res.unit = self.unit * (other.unit**(-1))
			res.symbol = r'%s / %s' % (self.symbol, other.symbol)
		elif isinstance(other, np.number) or isinstance(other, Number):
			res = PhysArray(self.value / other, grid=self.grid)
			res.unit = self.unit
			res.symbol = self.symbol
		elif isinstance(other, np.ndarray) or isinstance(other, list):
			if np.array(other).shape == self.value.shape:
				res = PhysArray(self.value / other, grid=self.grid)
				res.unit = self.unit
				res.symbol = self.symbol
			else:
				raise ValueError('Array or list must be the same shape as self')
		
		return res
	
	def __rtruediv__(self, other):
		'''
			other / self
		'''
		from numbers import Number

		if not isinstance(other, (np.ndarray, np.number, Number, list, PhysArray)):
			raise Exception('Not Implemented')
		
		if isinstance(other, np.number) or isinstance(other, Number):
			res = PhysArray(other / self.value, grid=self.grid)
			res.unit = (self.unit**(-1))
			res.symbol = '1/%s' % self.symbol
		elif isinstance(other, np.ndarray) or isinstance(other, list):
			if np.array(other).shape == self.value.shape:
				res = PhysArray(other / self.value, grid=self.grid)
				res.unit = (self.unit**(-1))
				res.symbol = '1/%s' % self.symbol
			else:
				raise ValueError('Array or list must be the same shape as self')
			
		return res
	
	def __floordiv__(self, other):
		'''
			self // other
		'''
		from numbers import Number

		if not isinstance(other, (np.ndarray, np.number, Number, list, PhysArray)):
			raise Exception('Not Implemented')
		
		if isinstance(other, PhysArray):
			r = self.value // other.value
			res = PhysArray(r, grid=self.grid)
			res.unit = self.unit * (other.unit**(-1))
			res.symbol = r'%s / %s' % (self.symbol, other.symbol)
		elif isinstance(other, np.number) or isinstance(other, Number):
			res = PhysArray(self.value // other, grid=self.grid)
			res.unit = self.unit
			res.symbol = self.symbol
		elif isinstance(other, np.ndarray) or isinstance(other, list):
			if np.array(other).shape == self.value.shape:
				res = PhysArray(self.value // other, grid=self.grid)
				res.unit = self.unit
				res.symbol = self.symbol
			else:
				raise ValueError('Array or list must be the same shape as self')
		
		return res
	
	def __rfloordiv__(self, other):
		'''
			other // self
		'''
		from numbers import Number

		if not isinstance(other, (np.ndarray, np.number, Number, list, PhysArray)):
			raise Exception('Not Implemented')
		
		if isinstance(other, np.number) or isinstance(other, Number):
			res = PhysArray(other // self.value, grid=self.grid)
			res.unit = (self.unit**(-1))
			res.symbol = '1/%s' % self.symbol
		elif isinstance(other, np.ndarray) or isinstance(other, list):
			if np.array(other).shape == self.value.shape:
				res = PhysArray(other // self.value, grid=self.grid)
				res.unit = (self.unit**(-1))
				res.symbol = '1/%s' % self.symbol
			else:
				raise ValueError('Array or list must be the same shape as self')
			
		return res
	
	def __pow__(self, other):
		'''
			self ** other
		'''
		from numbers import Number

		if not isinstance(other, (np.ndarray, np.number, Number, list)):
			raise Exception('Not Implemented')
		
		if np.isscalar(other):
			res = PhysArray(self.value**other, grid=self.grid)
			res.unit = self.unit**other
			res.symbol = f'${self.symbol}^{other}$'

		elif isinstance(other, np.ndarray) or isinstance(other, list):
			if np.array(other).shape == self.value.shape:
				res = PhysArray(self.value**other, grid=self.grid)
				res.unit = self.unit**other
			else:
				raise ValueError('Array or list must be the same shape as self')
			
		return res

	
	def __eq__(x, y):
		# x == y

		false = False #PhysArray(False, unit=u.dimensionless_unscaled)
		if isinstance(y, np.ndarray):
			if x.value.shape == y.shape:
				false = (x.value == y)
				return false
			else:
				raise ValueError('Comparison must be between objects with the same shape, or scalar')
		if np.isscalar(y):
			false = (x.value == y)
			return false
		if isinstance(y, PhysArray):
				if (x.unit != y.unit):
					return false
				else:
					try:
							false = (x.value == y.value)
					except:
							return false

	def __ne__(x, y):
		# x != y
		
		return ~ (x == y)

	def __lt__(x, y):
		# x < y
		
		false = False #PhysArray(False, unit=u.dimensionless_unscaled)
		if isinstance(y, np.ndarray):
			if x.value.shape == y.shape:
				false = (x.value < y)
				return false
			else:
				raise ValueError('Comparison must be between objects with the same shape, or scalar')
		if np.isscalar(y):
			false = (x.value < y)
			return false
		if isinstance(y, PhysArray):
				if (x.unit != y.unit):
					raise ValueError('Confront only conformable quantities!')
				else:
					try:
							false = (x.value < y.value)
					except:
							return false

	def __le__(x, y):
		# x <= y
		
		false = False #PhysArray(False, unit=u.dimensionless_unscaled)
		if isinstance(y, np.ndarray):
			if x.value.shape == y.shape:
				false = (x.value <= y)
				return false
			else:
				raise ValueError('Comparison must be between objects with the same shape, or scalar')
		if np.isscalar(y):
			false = (x.value <= y)
			return false
		if isinstance(y, PhysArray):
				if (x.unit != y.unit):
					raise ValueError('Confront only conformable quantities!')
				else:
					try:
							false = (x.value <= y.value)
					except:
							return false

	def __gt__(x, y):
		# x > y

		false = False #PhysArray(False, unit=u.dimensionless_unscaled)
		if isinstance(y, np.ndarray):
			if x.value.shape == y.shape:
				false = (x.value > y)
				return false
			else:
				raise ValueError('Comparison must be between objects with the same shape, or scalar')
		if np.isscalar(y):
			false = (x.value > y)
			return false
		if isinstance(y, PhysArray):
				if (x.unit != y.unit):
					raise ValueError('Confront only conformable quantities!')
				else:
					try:
							false = (x.value > y.value)
					except:
							return false

	def __ge__(x, y):
		#	x >= y
		
		false = False #PhysArray(False, unit=u.dimensionless_unscaled)
		if isinstance(y, np.ndarray):
			if x.value.shape == y.shape:
				false = (x.value >= y)
				return false
			else:
				raise ValueError('Comparison must be between objects with the same shape, or scalar')
		if np.isscalar(y):
			false = (x.value >= y)
			return false
		if isinstance(y, PhysArray):
				if (x.unit != y.unit):
					raise ValueError('Confront only conformable quantities!')
				else:
					try:
							false = (x.value >= y.value)
					except:
							return false
					
	def __getitem__(self, indices):
		'''
			Allow slicing/indexing, making PhysArray iterable
		'''
		from ..geometry.grid import GridList, Grid

		if self.grid != None:
			newgrid = GridList()
			for g in self.grid:
				newgrid.append(Grid(g.name, g.axis.value[indices], unit=g.unit))
		else:
			newgrid = None
		return PhysArray(self.value[indices], unit=self.unit, grid=newgrid, \
									 name=self.name, symbol=self.symbol)
	
	def __setitem__(self, indices, new_value):
		'''
			Allow setting values
		'''
		self.value[indices] = new_value
	
	# Useful operations
	def sin(self):
		res = PhysArray(np.sin(self.value), unit=u.rad, grid=self.grid, \
									  name='sin(%s)' % self.name)
		return res

	def cos(self):
		res = PhysArray(np.cos(self.value), unit=u.rad, grid=self.grid, \
									  name='cos(%s)' % self.name)
		return res

	def abs(self):
		res = PhysArray(np.abs(self.value), unit=self.unit, grid=self.grid, \
									  name='abs(%s)' % self.name)
		return res

	def sqrt(self):
		res = PhysArray(np.sqrt(self.value), unit=(self.unit)**(0.5), \
									grid=self.grid, name='sqrt(%s)' % self.name)
		return res
	
	def cbrt(self):
		res = PhysArray(np.cbrt(self.value), unit=(self.unit)**(1./3.), \
									grid=self.grid, name='cbrt(%s)' % self.name)
		return res

	def sum(self):
		res = PhysArray(np.sum(self.value), unit=self.unit, \
									grid=None, name='sum(%s)' % self.name)
		return res

	def nansum(self):
		res = PhysArray(np.nansum(self.value), unit=self.unit, \
									grid=None, name='nansum(%s)' % self.name)
		return res

	def cumsum(self):
		res = PhysArray(np.cumsum(self.value), unit=self.unit, \
									grid=None, name='cumsum(%s)' % self.name)
		return res

	def min(self):
		res = PhysArray(np.min(self.value), unit=self.unit, \
									grid=None, name='min(%s)' % self.name)
		return res

	def nanmin(self):
		res = PhysArray(np.nanmin(self.value), unit=self.unit, \
									grid=None, name='nanmin(%s)' % self.name)
		return res

	def argmin(self):
		return np.argmin(self.value)

	def nanargmin(self):
		return np.nanargmin(self.value)

	def max(self):
		res = PhysArray(np.max(self.value), unit=self.unit, \
									grid=None, name='max(%s)' % self.name)
		return res

	def nanmax(self):
		res = PhysArray(np.nanmax(self.value), unit=self.unit, \
									grid=None, name='nanmax(%s)' % self.name)
		return res

	def argmax(self):
		return np.argmax(self.value)

	def nanargmax(self):
		return np.nanargmax(self.value)
	
	def diff(self, axis=0):
		res = np.diff(self.value, axis=axis, prepend=0.0)
		return PhysArray(res, unit=self.unit, grid=self.grid, name=f'd{self.name}')