from preSNpy.model import *
import pandas as pd
import re
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
			mass /= (1.989e33)
		elif source == 'mesa':
			data = self.__read_mesa_file()
			mass = data['mass'].values[:]
			radius = 10 ** data['logR'].values[:]
		else:
			raise ValueError('Source not recognized')

		self.grid.append(grid.Grid('radius', radius, unit='cm'))
		self.grid.append(grid.Grid('mass', mass, unit='Msun'))
		self.mass = mass
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
		return data

	def __find_kepler_header_lines(self, file_lines):
		'''
  		Find the index of the line where the data starts and the name of teh columns.
    	return: int, number of lines to skip from the beginning of the file.
				list, names of the columns.
     	'''
		def find_header_names(line):
			## Find the column names
			names = re.split(r'\s{2,}', file_lines[line_index-1])
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
