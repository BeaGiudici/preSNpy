# preSNpy v1.0
`Python` package to play with pre-supernova progenitor stars.

**Disclaimer.** This package has been build and mantained by a non-expert on stellar astrophysics. The main purpose of this package is to give a simple tool to extract useful information about the progenitor stars to people that are not familiar with stellar astrophysics.

## Requirements

This package is built entirely in `Python` and it requires a version of [Python3](https://www.python.org/) to be used in all its power.
Besides, the package is based on the use of different `Python` libraries:
 - [NumPy](https://numpy.org/)
 - [h5Py](https://www.h5py.org/)
 - [matplotlib](https://matplotlib.org/)
 - [scipy](https://scipy.org/)

## Installation
`preSNpy` can be installed through `pip`. What follows is an easy step-by-step guide to the installation.

1. Clone the repository, either with SSH
   ```
   git clone git@github.com:BeaGiudici/preSNpy.git
   ```
   or the URL
   ```
   git clone https://github.com/BeaGiudici/preSNpy.git
   ```
3. Go to the package folder and run `pip`
   ```
   cd preSNpy
   pip install .
   ```
4. Have fun!

If the repository is modified, make sure to remember to upgrade the installation with
   ```
   pip install . --upgrade
   ```
To remove the installation use
   ```
   pip uninstall presnpy
   ```

## Environment creation

In case you use [Anaconda](https://docs.anaconda.com/), the environment file `presnpy.yml` is also provided to create an environment with all the requirements.

To create an environment from `presnpy.yml` run the command
```
conda env create -f presnpy.yml
```
then activate the environment with
```
conda activate presnpy
```
