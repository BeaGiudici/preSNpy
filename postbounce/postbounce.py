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
		self.grid = grid.Grid(self, 1)
		self.grid.fillGrid()

		# Initialize HYDRO quantities
		self.hydro = hydro.Hydro(self)
		self.hydro.fillHydro()

		# Initialize NUCLEAR quantities
		self.nuclear = nuclear.Nuclear(self)
		self.nuclear.fillNuclear()

		# TO-DO: Initialize SCALAR quantities