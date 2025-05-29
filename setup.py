from setuptools import setup
from setuptools import find_packages

about = {}
with open("preSNpy/__about__.py") as f:
    exec(f.read(), about)

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
