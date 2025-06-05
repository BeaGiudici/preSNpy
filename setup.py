from setuptools import setup
from setuptools import find_packages
import os

about = {}
with open("preSNpy/__about__.py") as f:
    exec(f.read(), about)

def find_files(dirname, relpath=None):
    def find_paths(dirname):
        items = []
        for fname in os.listdir(dirname):
            path = os.path.join(dirname, fname)
            if os.path.isdir(path):
                items += find_paths(path)
            elif not path.endswith(".py") and not path.endswith(".pyc"):
                items.append(path)
        return items
    items = find_paths(dirname)
    if relpath is None:
        relpath = dirname
    return [os.path.relpath(path, relpath) for path in items]

setup(
    name = about['__title__'],
    version = about['__version__'],    
    description = about['__description__'],
    long_description = open('README.md').read() + '\n\n' + \
                       open('CONTRIBUTORS.md').read(),
    long_description_content_type = "text/markdown",
    url = about['__url__'],
    download_url = about['__url__'],
    author = about['__author__'],
    author_email = about['__author_email__'],
    license = about['__license__'],
    maintainer = about['__maintainer__'],
    packages = find_packages(),
    scripts = find_files('bin', relpath='./'),
    package_data = {
      'preSNpy.model' : ['preSNpy/model/*.py'],
      'preSNpy.geometry' : ['preSNpy/geometry/*.py'],
      'preSNpy.physics' : ['preSNpy/physics/*.py'],
    },
    install_requires = ['matplotlib',
                      'numpy',                     
                      'scipy',
                      'pandas',  
                      'h5py',
                      'astropy',],
    python_requires = '>=3.6',
    classifiers = [
        'Development Status :: 1 - Planning',
        'Topic :: Scientific/Engineering :: Astrophysics',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
    ],
)
