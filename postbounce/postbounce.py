import h5py
from ..geometry import grid
from ..hydro import hydro
from ..nuclear import nuclear

class Postbounce1D:
	def __init__(self, filename):
		'''
		 Postbounce profile data 1D
		'''
		self.filename = filename
		self.file = h5py.File(filename, 'r')

		# Initialize GRID quantities
		self.grid = grid.Grid(1)
		self.grid.radius = self.file['xzn'][:]
		self.grid.mass = self.file['mass'][:]
		self.grid.bar_mass = self.file['massb'][:]
		self.grid.grav_mass = self.file['massg'][:]

		# Initialize HYDRO quantities
		self.hydro = hydro.Hydro()
		self.hydro.density = self.file['den'][:]
		self.hydro.pressure = self.file['pre'][:]
		self.hydro.temperature = self.file['tem'][:]
		self.hydro.entropy = self.file['sto'][:]
		self.hydro.velocity = self.file['vex'][:]
		self.hydro.internal_energy = self.file['eint'][:]

		# Initialize NUCLEAR quantities
		self.nuclear = nuclear.Nuclear()
		self.nuclear.n1 = self.file['xnu'][0][:]
		self.nuclear.H1 = self.file['xnu'][1][:]
		self.nuclear.He4 = self.file['xnu'][2][:]
		self.nuclear.C12 = self.file['xnu'][3][:]
		self.nuclear.O16 = self.file['xnu'][4][:]
		self.nuclear.Ne20 = self.file['xnu'][5][:]
		self.nuclear.Mg24 = self.file['xnu'][6][:]
		self.nuclear.Si28 = self.file['xnu'][7][:]
		self.nuclear.S32 = self.file['xnu'][8][:]
		self.nuclear.Ar36 = self.file['xnu'][9][:]
		self.nuclear.Ca40 = self.file['xnu'][10][:]
		self.nuclear.Ti44 = self.file['xnu'][11][:]
		self.nuclear.Cr48 = self.file['xnu'][12][:]
		self.nuclear.Fe52 = self.file['xnu'][13][:]
		self.nuclear.Ni56 = self.file['xnu'][14][:]
		self.nuclear.X56 = self.file['xnu'][15][:]
		self.nuclear.Ye = self.file['xnu'][16][:]

		# TO-DO: Initialize SCALAR quantities