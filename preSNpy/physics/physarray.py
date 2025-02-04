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

		setattr(obj, 'value', data)

		setattr(obj, 'grid', grid)
		setattr(obj, 'name', name)

		if symbol == None:
			setattr(obj, 'symbol', name)
		else:
			setattr(obj, 'symbol', symbol)

		return obj
	
	def to(self, unit):
		'''
			Return a new PhysArray with the converted unit
		'''
		if hasattr(self, 'unit'):
			oldunit = self.unit

		if oldunit != unit:
			value = (self.value * oldunit).to_value(unit)
			return PhysArray(value, unit=unit, grid=self.grid, symbol=self.symbol, \
											 name=self.name)

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

	# Redefining operations
	def __add__(self, other):
		'''
			self + other
		'''
		if hasattr(other, 'unit'):
			try:
				other = other.to(self.unit)
				s = self.value + other.value
				return PhysArray(s, unit=self.unit, grid=self.grid, \
										 		 symbol=self.symbol, name=self.name)
			except:
				print('Illegal sum of non-conformable units')
		else:
			raise ValueError('Sum only possible between PhysArray objects')
	
	def __sub__(self, other):
		'''
			self - other
		'''
		if hasattr(other, 'unit'):
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

		if not isinstance(other, (np.ndarray, np.number, Number, list)):
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

		if not isinstance(other, (np.ndarray, np.number, Number, list)):
			raise Exception('Not Implemented')
		
		return self.__mul__(other)
	
	def __div__(self, other):
		'''
			self / other
			Replaced by __truediv__ in Python 3.x
		'''
		from numbers import Number

		if not isinstance(other, (np.ndarray, np.number, Number, list)):
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

		if not isinstance(other, (np.ndarray, np.number, Number, list)):
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

		if not isinstance(other, (np.ndarray, np.number, Number, list)):
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

		if not isinstance(other, (np.ndarray, np.number, Number, list)):
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

		if not isinstance(other, (np.ndarray, np.number, Number, list)):
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

		if not isinstance(other, (np.ndarray, np.number, Number, list)):
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
		pass

	def __eq__(x, y):
		'''
			x == y
		'''

		false = PhysArray(False, unit=u.dimensionless_unscaled)
		if isinstance(y, np.ndarray):
			if x.value.shape == y.shape:
				false.value = (x.value == y)
				return false
			else:
				raise ValueError('Comparison must be between objects with the same shape, or scalar')
		if np.isscalar(y):
			false.value = (x.value == y)
			return false
		if isinstance(y, PhysArray):
				if (x.unit != y.unit):
					return false
				else:
					try:
							false.value = (x.value == y.value)
					except:
							return false

	def __ne__(x, y):
		'''
			x != y
		'''
		return ~ (x == y)

	def __lt__(x, y):
		'''
			x < y
		'''
		false = PhysArray(False, unit=u.dimensionless_unscaled)
		if isinstance(y, np.ndarray):
			if x.value.shape == y.shape:
				false.value = (x.value < y)
				return false
			else:
				raise ValueError('Comparison must be between objects with the same shape, or scalar')
		if np.isscalar(y):
			false.value = (x.value < y)
			return false
		if isinstance(y, PhysArray):
				if (x.unit != y.unit):
					raise ValueError('Confront only conformable quantities!')
				else:
					try:
							false.value = (x.value < y.value)
					except:
							return false

	def __le__(x, y):
		'''
			x <= y
		'''
		false = PhysArray(False, unit=u.dimensionless_unscaled)
		if isinstance(y, np.ndarray):
			if x.value.shape == y.shape:
				false.value = (x.value <= y)
				return false
			else:
				raise ValueError('Comparison must be between objects with the same shape, or scalar')
		if np.isscalar(y):
			false.value = (x.value <= y)
			return false
		if isinstance(y, PhysArray):
				if (x.unit != y.unit):
					raise ValueError('Confront only conformable quantities!')
				else:
					try:
							false.value = (x.value <= y.value)
					except:
							return false

	def __gt__(x, y):
		'''
			x > y
		'''
		false = PhysArray(False, unit=u.dimensionless_unscaled)
		if isinstance(y, np.ndarray):
			if x.value.shape == y.shape:
				false.value = (x.value > y)
				return false
			else:
				raise ValueError('Comparison must be between objects with the same shape, or scalar')
		if np.isscalar(y):
			false.value = (x.value > y)
			return false
		if isinstance(y, PhysArray):
				if (x.unit != y.unit):
					raise ValueError('Confront only conformable quantities!')
				else:
					try:
							false.value = (x.value > y.value)
					except:
							return false

	def __ge__(x, y):
		'''
			x >= y
		'''
		false = PhysArray(False, unit=u.dimensionless_unscaled)
		if isinstance(y, np.ndarray):
			if x.value.shape == y.shape:
				false.value = (x.value >= y)
				return false
			else:
				raise ValueError('Comparison must be between objects with the same shape, or scalar')
		if np.isscalar(y):
			false.value = (x.value >= y)
			return false
		if isinstance(y, PhysArray):
				if (x.unit != y.unit):
					raise ValueError('Confront only conformable quantities!')
				else:
					try:
							false.value = (x.value >= y.value)
					except:
							return false
		
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