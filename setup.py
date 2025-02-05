from setuptools import setup
from setuptools import find_packages

setup(
    name = 'preSNpy',
    version = '2.0',    
    description = 'A library to analyze pre-supernova models.',
    url = 'https://github.com/BeaGiudici/preSNpy',
    download_url = f'https://github.com/BeaGiudici/preSNpy',
    author = 'Beatrice Giudici',
    author_email = 'bea.giudici96@gmail.com',
    license = 'MIT LICENSE',
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
                      'h5py',],
    python_requires = '>=3.6',
    classifiers = [
        'Development Status :: 1 - Planning',
        'Topic :: Scientific/Engineering :: Astrophysics',
        'License :: OSI Approved :: GNU GENERAL PUBLIC LICENSE',  
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',        
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.12',
    ],
)
