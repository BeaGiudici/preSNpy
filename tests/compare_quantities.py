########################################################################
#
# Compute and cross-check quantities between models.
#
# Created: Beatrice Giudici
#
########################################################################

from preSNpy.model import Postbounce1D, PreSN1D
from preSNpy.physics import PhysArray
from astropy import units as u

def relative_difference(q1, q2, tol=1.e-03):
  '''
  Find the relative distance between two quantities
  '''
  import numpy as np
  if hasattr(q1, 'value'):
    q1 = q1.value
  if hasattr(q2, 'value'):
    q2 = q2.value
  ratio = np.min([q1, q2]) / np.max([q1, q2])
  s = 1.0 - ratio
  #print(s)
  return s < tol

ref = {
  'starMass' : 5.03,
  'He mass' : 0.459,
  'QHe' : 1.117,
}


# Load the models
pk1 = PreSN1D('tests/models/kepler1')
pk2 = PreSN1D('tests/models/kepler2')
post = Postbounce1D('tests/models/postbounce')

# SINGLE CHECK: Total mass
for model in [pk1, pk2, post]:
  print('Checking %s' % model.filename)
  cont_mass = (model.dV() * model.hydro.density).to('g')
  starMass = model.starMass().to('g')
  print('\tSINGLE CHECK: total mass')
  assert relative_difference(cont_mass.value[-1], starMass)
  print('\tSINGLE CHECK: star mass')
  assert relative_difference(model.starMass(), ref['starMass'])
  print('\tSINGLE CHECK: He mass')
  assert relative_difference(model.nuclear.element_mass('he4'), ref['He mass'])
  print('\tSINGLE CHECK: QHe')
  assert relative_difference(model.QHe(), ref['QHe'])

# CROSS-CHECKING: The models are initialised so that they should give 
# the same results (up to conversion numerical errors).

# Star mass
print('CROSS-CHECK: star mass')
assert relative_difference(pk1.starMass(), pk2.starMass())
assert relative_difference(post.starMass(), pk2.starMass())
assert relative_difference(pk1.starMass(), post.starMass())

# He-core mass
print('CROSS-CHECK: He mass')
assert relative_difference(pk1.nuclear.element_mass('he4'), \
                           pk2.nuclear.element_mass('he4'))
assert relative_difference(pk1.nuclear.element_mass('he4'), \
                           post.nuclear.element_mass('he4'))
assert relative_difference(post.nuclear.element_mass('he4'), \
                           pk2.nuclear.element_mass('he4'))

# QHe
print('CROSS-CHECK: QHe')
assert relative_difference(pk1.QHe(), pk2.QHe())
assert relative_difference(pk1.QHe(), post.QHe())
assert relative_difference(post.QHe(), pk2.QHe())