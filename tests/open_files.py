########################################################################
#
# Open different files, including a non-existent one.
#
# Created: Beatrice Giudici
#
########################################################################
from preSNpy.model import Postbounce1D, PreSN1D
import pytest

def open_postbounce(filename):
  Postbounce1D(filename)

def open_kepler(filename):
  PreSN1D(filename, source='kepler')

def open_mesa(filename):
  PreSN1D(filename, source='mesa')

def fail_open():
  with pytest.raises(FileNotFoundError):
    Postbounce1D('boh')
  with pytest.raises(FileNotFoundError):
    PreSN1D('mah', source='kepler')
  with pytest.raises(FileNotFoundError):
    PreSN1D('eh', source='mesa')

if __name__ == '__main__':
  # Open postbounce file
  open_postbounce('models/postbounce')
  # Open KEPLER files
  open_kepler('models/kepler1')
  open_kepler('models/kepler2')
  # Open MESA file
  #open_mesa('models/mesa')
  # Try to open non-existent files
  fail_open()