# preSNpy v2.0.0
`Python` package to play with pre-supernova progenitor stars.

**Disclaimer.** This package has been build and mantained by non-experts on stellar astrophysics (a.k.a. supernovists). The main purpose of this package is to give a simple tool to extract useful information about the progenitor stars to people that are not familiar with stellar astrophysics.

## Requirements

This package is built entirely in `Python` and it requires a version of [Python3](https://www.python.org/) to be used in all its power.
Besides, the package is based on the use of different `Python` libraries:
 - [NumPy](https://numpy.org/)
 - [h5Py](https://www.h5py.org/)
 - [matplotlib](https://matplotlib.org/)
 - [scipy](https://scipy.org/)
 - [pandas](https://pandas.pydata.org/)
 - [astropy](https://www.astropy.org/)

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

## Basic usage

This library creates objects containing all the information of the progenitor stars taken from the respective files. In order to start the analysis import the module first.
```
import preSNpy
```
Then, open the file. There are, up to now, two possibilites. If the model is a pre-supernova model, then use the class `PreSN1D`.
This is able to handle models generated with the code KEPLER ([Weaver et al. 1978](https://ui.adsabs.harvard.edu/abs/1978ApJ...225.1021W/abstract)), as well as MESA ([Paxton at al. 2011](https://ui.adsabs.harvard.edu/abs/2011ApJS..192....3P/abstract)). They are imported as follows:
- KEPLER:
```
m_kepler = PreSNpy.model.PreSN1D('path-to-kepler-file', source='kepler')
```
- MESA
```
m_mesa = PreSNpy.model.PreSN1D('path-to-mesa-file', source='mesa')
```

Moreover, another kind of data can be used. They are the postbounce profiles evolved from the pre-supernova link. For them there is another class, called `Postbounce1D`. To get the data simply call
```
m_post = preSNpy.model.Postbounce1D('path-to-postbounce-file')
```

Now, the technicalities. Both classes are children to the parent class `Model` (hence, the name of the module), so they contain the same objets:
 - the mass of the star (`self.starMass`),
 - the radius of the star (`self.starRadius`),
 - the zero-age main-sequence (ZAMS) mass (`self.ZAMS_mass`),
 - the compactness $\xi$ (`self.compactness`),
 - the mass coordinate where the s = 4 k$_B$ (M4, `self.M4`),
 - the volume of the cells (`self.dV`),
 - the normalized integrals of rhor3 in the He and H shells as Giudici at al. 20xx (`self.QHe` and `self.QH` respectively).

### Data
The data are divided in two main classes: 
 - `hydro`: it contains all the hydrodynamic quantities (and magnetic fields information, where present),
 - `nuclear`: it contains all the information about the mass fractions of the elements, as well as the electron fraction Y_e and A_bar.

Their structure is the same, as every quantity is defined as a `PhysArray`, with given name, grid, unit, and possible symbol for plotting.

### Plots
Managing the plots is very simple. Every `PhysArray` has a method called `plot()` that produces the radial profile of the given quantity. For example, for `density`,
```
m = Postbounce1D(filename)
m.hydro.density.plot()
```
will produce the profile of the density as function of radius. The parameter `axis` can be changed to have the chosen quantity as function of enclosed mass. Thus
```
m.hydro.density.plot(axis='mass')
```
will produce the same plot as before, but with the mass on the x-axis instead of the radius. All the usual `matplotlib.pyplot` parameters can be passed to this method.

There are also shortcut methods for the logarithmic scale. The methods `plotlogx()`, `plotlogy()`, and `plotloglog()` will create plot with a log-scale on x, y, or both axes, respectively.

Once the planets are alligned, there will be a `plot2D()` method for 2D stellar models.

## License
This package is distributed under the MIT License, see [`LICENSE`](./LICENSE).
