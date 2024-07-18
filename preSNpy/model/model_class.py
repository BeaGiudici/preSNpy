from preSNpy.model import *

class Model:
	def __init__(self):
		self.filename = None
		self.ndim = None
		self.grid = grid.GridList()
		self.nx = None
		self.nuc = None
		self.mass = None
		self.hydro = hydro.Hydro(self, self.grid)
		self.nuclear = nuclear.Nuclear(self, self.grid)

	def starMass(self):
		'''
			Return the mass of the star.
		'''
		volume = self.dV()
		density = self.hydro.density
		mass = np.sum(density * volume)
		return mass 

	def starRadius(self):
		'''
			Return the radius of the star.
		'''
		return self.grid[0].axis[-1]
	
	def compactness(self, masslim=2.5):
		'''
			Return the compactness of the star.
			The compactness is defined as the ratio between the enclosed mass 
			'masslim' (in unit of Msun) and the radius that encloses that mass 
			(in unit of 1000 km).

			Reference: O'Connor & Ott (2011)
		'''
		idx = np.argmin(np.fabs(self.grid.getAxis('mass') - masslim))
		rlim = self.grid.getAxis('radius')[idx] / (1.e5) # in km
		xi = masslim / (rlim/1000)
		return xi
	
	def M4(self):
		'''
			Return the mass coordinate where the entropy per kb is 4.
		'''
		idx = np.argmin(np.fabs(self.hydro.entropy - 4))
		return self.grid.getAxis('mass')[idx]

	def ZAMS_mass(self):
		'''
			Return the zero-age main sequence mass of the star (in unit of Msun).
		'''
		mass = ''
		for (i,s) in enumerate(self.filename):
			if s.isdigit():
				mass += s
			if not s.isdigit() and \
				(self.filename[i-1].isdigit() and self.filename[i+1].isdigit()):
				mass += '.'
		return float(mass)
	
	def dV(self):
		'''
			Return the volume element dV = 4*pi*r^2*dr
		'''
		volume = 4*np.pi*self.x[1:]**2*np.diff(self.x)
		v0 = 4.0 * np.pi * self.x[0]**3 / 3.0
		return np.append(v0, volume)
	
class Postbounce1D(Model):
	def __init__(self, filename):
		'''
		 Postbounce profile data 1D
		'''
		Model.__init__(self)

		self.filename = filename
		self.ndim = 1

		with open(filename, 'r') as f:
			#Header
			f.readline()

			# Global data
			header_global = f.readline().split()[1:]
			data_global = f.readline().split()
		
		for (i, data) in enumerate(data_global):
			setattr(self, header_global[i].lower(), float(data))

		self.nx = int(self.ndat)
		# Set the grid
		radius, mass = np.genfromtxt(filename, skip_header=6, max_rows=self.nx, \
															 usecols=(1,2), unpack=True)

		self.grid.append(grid.Grid('radius', radius, unit='cm'))
		self.grid.append(grid.Grid('mass', mass, unit='Msun'))
		self.mass = mass

		# Initialize HYDRO quantities
		self.hydro.updateGrid(self.grid)
		self.hydro.fillHydro(self.filename, 'postbounce')

		# Initialize NUCLEAR quantities
		self.nuclear.updateGrid(self.grid)
		self.nuclear.fillNuclear(self.filename, 'postbounce')
	
class PreSN1D(Model):
	def __init__(self, filename):
		'''
		 Pre-supernova profile data 1D
		'''
		Model.__init__(self)

		self.filename = filename
		self.ndim = 1

		radius, mass = np.genfromtxt(filename, skip_header=2, usecols=(1,2), \
															 unpack=True)
		self.grid.append(grid.Grid('radius', radius, unit='cm'))
		self.grid.append(grid.Grid('mass', mass, unit='Msun'))
		self.mass = mass
		self.nx = len(mass)

		# Initialize HYDRO quantities
		self.hydro.updateGrid(self.grid)
		self.hydro.fillHydro(self.filename, 'presn')

		# Initialize NUCLEAR quantities
		self.nuclear.updateGrid(self.grid)
		self.nuclear.fillNuclear(self.filename, 'presn')

if __name__ == '__main__':
	p = Postbounce1D('HS13_1')
	print('Done')