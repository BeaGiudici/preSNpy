########################################################################
#
# Open different files, including a non-existent one.
#
# Created: Beatrice Giudici
#
########################################################################
from preSNpy.model import Postbounce1D, PreSN1D
import pytest

def test_open_postbounce():
  Postbounce1D('models/postbounce')

def test_open_kepler():
  PreSN1D('models/kepler1', source='kepler')
  PreSN1D('models/kepler2', source='kepler')

def test_open_mesa():
  PreSN1D('models/mesa', source='mesa')

def test_fail_open():
  with pytest.raises(FileNotFoundError):
    Postbounce1D('boh')
  with pytest.raises(FileNotFoundError):
    PreSN1D('mah', source='kepler')
  with pytest.raises(FileNotFoundError):
    PreSN1D('eh', source='mesa')

if __name__ == '__main__':
  # Open postbounce file
  test_open_postbounce()
  # Open KEPLER files
  test_open_kepler()
  # Open MESA file
  #test_open_mesa()
  # Try to open non-existent files
  test_fail_open()