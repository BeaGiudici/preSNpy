from preSNpy.model import *
import pandas as pd
pd.set_option("future.no_silent_downcasting", True)
import re
from astropy.constants import M_sun, R_sun


class Model:
	def __init__(self):
		self.filename = None
		self.ndim = None
		self.grid = grid.GridList()
		self.nx = None
		self.nuc = None
		self.x = None
		self.mass = None
		self.hydro = hydro.Hydro(self, self.grid)
		self.nuclear = nuclear.Nuclear(self, self.grid)

	def starMass(self):
		'''
			Return the mass of the star.
		'''
		#volume = self.dV()
		#density = self.hydro.density
		#mass = np.sum(density * volume)
		#return mass 
		return self.mass[-1]

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
		from ..physics.physarray import PhysArray
		m0 = PhysArray(masslim, unit=self.mass.unit, grid=self.grid)
		#idx = np.argmin(np.abs(self.mass - m0))
		idx = (self.mass - m0).abs().argmin()
		rlim = self.x[idx] / (1.e5) # in km
		xi = masslim / (rlim/1000)
		return xi
	
	def M4(self):
		'''
			Return the mass coordinate where the entropy per kb is 4.
		'''
		from ..physics.physarray import PhysArray
		sto4 = PhysArray(4.0, unit=self.hydro.entropy.unit, grid=self.grid)
		idx = (self.hydro.entropy - sto4).abs().argmin()
		return self.grid.getAxis('mass')[idx]

	def ZAMS_mass(self):
		'''
			Return the zero-age main sequence mass of the star (in unit of Msun).
		'''
		from ..physics.physarray import PhysArray
		mass = ''
		for (i,s) in enumerate(self.filename):
			if s.isdigit():
				mass += s
			if not s.isdigit() and \
				(self.filename[i-1].isdigit() and self.filename[i+1].isdigit()):
				mass += '.'
		return PhysArray(float(mass), unit=u.Msun, name='ZAMS mass', \
									 symbol=r'$M_\mathrm{ZAMS}$')
	
	def dV(self):
		'''
			Return the volume element dV = 4*pi*r^2*dr
		'''
		volume = 4 * np.pi * (self.x**2) * self.x.diff()
		volume.grid = self.grid
		volume.name = 'Volume'
		volume.symbol = 'dV'
		#v0 = 4.0 * np.pi * self.x[0]**3 / 3.0
		return volume #np.append(v0, volume)
	
	def QHe(self):
		'''
			Compute the normalized integral of rhor3 on the He composition 
			shell as defined in Giudici et al. 20xx.
		'''

		rCOHe, mCOHe, idxCOHe = self.nuclear.shellInterface(['c12', 'o16'], 'he4')
		rHeH, mHeH, idxHeH = self.nuclear.shellInterface('he4', 'h1')
		rhor3 = self.hydro.rhor3().value
		r = self.x.value
		
		curve_integral = np.trapz(rhor3[idxCOHe:idxHeH+1], \
													 r[idxCOHe:idxHeH+1])
		rectangle = (rHeH - rCOHe) * rhor3[idxCOHe]
		QHe = curve_integral / rectangle
		QHe.name = 'QHe'
		QHe.symbol = r'$\mathcal{Q}_\mathrm{He}$'
		return QHe
	
	def QH(self, **kwargs):
		'''
			Compute the normalized integral of rhor3 on the H composition 
			shell as defined in Giudici et al. 20xx.
		'''
		from ..physics.physarray import PhysArray
		rHeH, mHeH, idxHeH = self.nuclear.shellInterface('he4', 'h1')
		rmax = kwargs.pop('rmax', 2.0 * rHeH)
		if not isinstance(rmax, PhysArray):
			if isinstance(rmax, float):
				rmax = PhysArray(rmax, unit=rHeH.unit, grid=rHeH.grid)
			elif isinstance(rmax, int):
				rmax = PhysArray(float(rmax), unit=rHeH.unit, grid=rHeH.grid)
			else:
				raise ValueError('What kind of radius are you passing? >.>\n' \
				'The only acceptable ones are PhysArray, float, or int')
		#idx_max = np.argmin(np.fabs(self.grid[0].axis - rmax))
		idx_max = (self.x - rmax).abs().argmin()
		rhor3 = self.hydro.rhor3().value
		r= self.x.value

		curve_integral = np.trapz(rhor3[idxHeH:idx_max], \
													 r[idxHeH:idx_max])
		rectangle = (rmax - rHeH) * rhor3[idx_max]

		QH = curve_integral / rectangle
		QH.name = 'QH'
		QH.symbol = r'$\mathcal{Q}_\mathrm{H}$'
		return QH
	
class Postbounce1D(Model):
	def __init__(self, filename):
		'''
		 Postbounce profile data 1D
		'''
		super().__init__()

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

		self.grid.append(grid.Grid('radius', radius, unit=u.cm))
		self.grid.append(grid.Grid('mass', mass, unit=u.Msun))
		self.x = self.grid.getAxis('radius')
		self.mass = self.grid.getAxis('mass')

		# Initialize HYDRO quantities
		self.hydro.updateGrid(self.grid)
		self.hydro.fillHydro(self.filename, 'postbounce')

		# Initialize NUCLEAR quantities
		self.nuclear.updateGrid(self.grid)
		self.nuclear.fillNuclear(self.filename, 'postbounce')
	
class PreSN1D(Model):
	def __init__(self, filename, source='kepler'):
		'''
		 Pre-supernova profile data 1D
		'''
		super().__init__()

		self.filename = filename
		self.ndim = 1
		self.source = source

		if source == 'kepler':
			data = self.__read_kepler_file()
			mass = data['cell outer total mass'].astype(float).fillna(0.0).values[:]
			radius = data['cell outer radius'].astype(float).fillna(0.0).values[:]
			mass /= M_sun.to(u.g).value
		elif source == 'mesa':
			data = self.__read_mesa_file()
			mass = data['mass'].values[:]
			radius = (10 ** data['logR'].values[:]) * R_sun.to(u.cm).value
		else:
			raise ValueError('Source not recognized')

		self.grid.append(grid.Grid('radius', radius, unit=u.cm))
		self.grid.append(grid.Grid('mass', mass, unit=u.Msun))
		self.x = self.grid.getAxis('radius')
		self.mass = self.grid.getAxis('mass')
		self.nx = len(mass)

		# Initialize HYDRO quantities
		self.hydro.updateGrid(self.grid)
		self.hydro.fillHydro(data, source)

		# Initialize NUCLEAR quantities
		self.nuclear.updateGrid(self.grid)
		self.nuclear.fillNuclear(data, source)

	def __read_kepler_file(self):
		with open(self.filename, 'r') as f:
			lines = f.readlines()
			# Find the line where the data starts
			line_index, column_names = self.__find_kepler_header_lines(lines)
			# Find the line where the data ends
			footer_index = self.__find_footer(lines)
			# Read the data
			data = pd.read_csv(self.filename, skiprows=line_index, delimiter='\s+', \
							   skipfooter=footer_index, names=column_names)
			data = data.replace('---', 0.0)
			data = data.replace('-', 0.0)
		return data

	def __find_kepler_header_lines(self, file_lines):
		'''
  		Find the index of the line where the data starts and the name of 
			the columns.
    	file_lines: int, number of lines to skip from the beginning of the 
							file.
			return: list, names of the columns.
     	'''
		def find_header_names(line):
			## Find the column names
			names = re.split(r'\s{2,}', line)
			names = [n.replace('#', '').strip().casefold() for n in names]
			names = list(filter(None, names))
			return names

		for lindex in range(1,len(file_lines)):
			try:
				float(file_lines[lindex].split()[1])
				line_index = lindex
				break
			except:
				pass
		
		for lindex in reversed(range(0,line_index)):
			column_names = find_header_names(file_lines[lindex])
			if 'cell outer total mass' in column_names:
				break

		return line_index, column_names

	def __read_mesa_file(self):
		with open(self.filename, 'r') as f:
			lines = f.readlines()
			line_index = self.__find_MESA_header_lines(lines)
			footer_index = self.__find_footer(lines)
		data = pd.read_csv(self.filename, skiprows=line_index, delimiter='\s+',
						   skipfooter=footer_index, header=0)
		data = data.iloc[::-1].reset_index(drop=True)
		return data
	
	def __find_MESA_header_lines(self, file_lines):
		for lindex in range(1,len(file_lines)):
			if 'logT' in file_lines[lindex]:
				line_index = lindex
				break
		return line_index

	def __find_footer(self, file_lines):
		'''
        Find the index of the line where the data ends.
        return: int, number on lines to skip from the end of the file.
        '''
		findex = 0
		lines = list(reversed(file_lines))
		for lindex in range(len(lines)):
			try:
				float(lines[lindex].split()[0].replace(':',''))
				findex = lindex
				break
			except:
				continue
		return findex


if __name__ == '__main__':
	p = Postbounce1D('HS13_1')
	print('Done')
