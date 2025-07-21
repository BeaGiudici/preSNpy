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
  Postbounce1D('tests/models/postbounce')

def test_open_kepler():
  PreSN1D('tests/models/kepler1', source='kepler')
  PreSN1D('tests/models/kepler2', source='kepler')

#def test_open_mesa():
#  PreSN1D('models/mesa', source='mesa')

def test_fail_open():
  with pytest.raises(FileNotFoundError):
    Postbounce1D('boh')
  with pytest.raises(FileNotFoundError):
    PreSN1D('mah', source='kepler')
  with pytest.raises(FileNotFoundError):
    PreSN1D('eh', source='mesa')