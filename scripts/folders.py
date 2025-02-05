########################################################################
#
# Floders needed for the scripts. The user has to change them depending 
# on the necessities.
#
########################################################################

import os

global POSTDIR
POSTDIR = os.path.join(os.path.expanduser('~'), 'PhD/postbounce_profies/')
PRESN_DIR = os.path.join(os.path.expanduser('~'), 'PhD/progenitor_models/')

global SNMODDEL_DIR
global PLOTSDIR
if os.uname()[1] == 'dorothy':
  SNMODELS_DIR = os.path.join(os.path.expanduser('~'), '1Dsnmodels/')
  PLOTSDIR = os.path.join(os.path.expanduser('~'), 'PhD', 'plots', 'stellarProgenitors')
elif os.uname()[1] == 'superviz':
  SNMODELS_DIR = os.path.join(os.path.expanduser('~'), '1Dsnmodels')
  PLOTSDIR = os.path.join(os.path.expanduser('~'), 'plots', 'stellarProgenitors')