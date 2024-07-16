import os

global POSTDIR
POSTDIR = os.path.join(os.path.expanduser('~'), 'PhD/postbounce_profies/')

global SNMODDEL_DIR
if os.uname()[1] == 'dorothy':
  SNMODELS_DIR = os.path.join(os.path.expanduser('~'), '1Dsnmodels/')
elif os.uname()[1] == 'superviz':
  SNMODELS_DIR = os.path.join(os.path.expanduser('~'), '1Dsnmodels')
