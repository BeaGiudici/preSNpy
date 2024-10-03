########################################################################
#
# This script reads the output of the 1D stellar evolution code KEPLER
# The original routine is not mine
# 
########################################################################
import argparse
import os
import numpy as np
import h5py
import preSNpy.global_vars as gv

parser = argparse.ArgumentParser()
parser.add_argument("--filename", required=True, \
          help="Name of the file")
parser.add_argument("--model", required=True, \
          help="Name of the model")
parser.add_argument("--progenitor", required=True, \
                    help="Progenitor type (rsg/bsg/wolf)")
parser.add_argument('--state', required=True, \
                    help='State of the model (presn/postbounce)')

args = parser.parse_args()
progenitor = args.progenitor
filename = args.filename
state = args.state
model = args.model
model_upper = model.upper()

species=(['n1'],['p1','H1'],['he4','He4'],['c12','C12'],['o16','O16'],\
         ['ne20','Ne20'],['mg24','Mg24'],['si28','Si28'],['s32','S32'],\
         ['ar36','Ar36'],['ca40','Ca40'],['ti44','Ti44'],['cr48','Cr48'],\
         ['fe52','Fe52'],['ni56','Ni56'],['x56','X'])

if state == 'postbounce':

  if progenitor == 'rsg':
    file = open(os.path.join(gv.POSTDIR, filename), 'r')

    # Header
    file.readline()

    # Global data
    header_global = file.readline().split()[1:]
    data_global = file.readline().split()

    file.readline()
    file.readline()

    header_data = file.readline().split()[1:]
    data = np.asfarray(file.readline().split(), float)

    dummy = file.readline().split()

    while dummy[0] != '#':
      data = np.vstack((data, np.asfarray(dummy, float)))
      dummy = file.readline().split()

    if len(data) != int(data_global[0]):
      raise ValueError('Number of data points does not match the global data.\n \
                      Data length: %d\nGlobal data: %d' % (len(data), \
                        int(data_global[0])))
    
    dummy=file.readline().split()
    dummy=file.readline().split()
    dummy=file.readline().split()
    dummy=file.readline().split()

    composition=file.readline().split()[2:]

    xnuc=np.asfarray(file.readline().split()[1:],float)

    dummy=file.readline().split()
    while(int(dummy[0])<=len(data)):     
      xnuc=np.vstack((xnuc,np.asfarray(dummy[1:],float)))
      if(int(dummy[0])==len(data)):
        break
      else:
        dummy=file.readline().split()

    nspecies=len(composition)+1 #including Ye as last entry
    ye=data[:,8]
    xnuc=np.swapaxes(np.asarray(np.insert(xnuc,xnuc.shape[1],values=ye,axis=1)),\
                    0,1)
    
    xzn=data[:,1]
    massb=data[:,2]
    massg=data[:,3]
    mass=data[:,4]
    vel=data[:,5]
    den=data[:,6]
    tem=data[:,7]*11604525006.17 #from MeV to K
    sto=data[:,9]
    pre=data[:,10]
    eint=data[:,11]

    nx=len(data)

    # Create .h5 file
    hf = h5py.File(gv.SNMODEL_DIR + model_upper, 'w')

    for i in range(len(header_global)):
        print(header_global[i])
        hf.create_dataset(header_global[i], data=float(data_global[i]))

    '''
    hf.create_dataset('nx', data=nx)
    hf.create_dataset('nnuc_ad', data=nspecies)
    hf.create_dataset('xzn', data=xzn)
    hf.create_dataset('vex', data=vel)
    hf.create_dataset('den', data=den)
    hf.create_dataset('tem', data=tem)
    hf.create_dataset('sto', data=sto)
    hf.create_dataset('pre', data=pre)
    hf.create_dataset('eint', data=eint)
    hf.create_dataset('xnu', data=xnuc)
    hf.create_dataset('mass', data=mass)
    hf.create_dataset('massg', data=massg)
    hf.create_dataset('massb', data=massb)
    '''
    g = hf.create_group('global')
    gr = hf.create_group('grid')
    n = hf.create_group('nuclear')
    h = hf.create_group('hydro')

    g.create_dataset('mass', data=mass)
    gr.create_dataset('massg', data=massg)
    gr.create_dataset('massb', data=massb)
    g.create_dataset('nx', data=nx)
    g.create_dataset('nnuc_ad', data=nspecies)
    gr.create_dataset('xzn', data=xzn)
    h.create_dataset('vex', data=vel)
    #h.create_dataset('vomega', data=vomega)
    h.create_dataset('den', data=den)
    h.create_dataset('tem', data=tem)
    h.create_dataset('sto', data=sto)
    h.create_dataset('pre', data=pre)
    h.create_dataset('eint', data=eint)
    n.create_dataset('xnu', data=xnuc)
    #n.create_dataset('Abar', data=Abar)
    gr.create_dataset('mass', data=mass)
    hf.close()

elif state == 'presn':

  if progenitor == 'rsg':
    species = ['n', 'h1', 'he3', 'he4', 'c12', 'n14', 'o16', 'ne20', 'mg24', \
              'si28', 's32', 'ar36', 'ca40', 'ti44', 'cr48', 'fe52', 'ge54', \
              'ni56', 'fe56', 'x56']
    
    data = np.genfromtxt(os.path.join(gv.PRESN_DIR, filename), skip_header=2, \
                         unpack=True)
    
    nx = data.shape[1]

    # Arrays
    mass = data[1]
    xzn = data[2]
    vel = data[3]
    den = data[4]
    tem = data[5]
    pre = data[6]
    eint = data[7]
    sto = data[8]
    vomega = data[9]
    Abar = data[10]
    xnu = data[14:]
    ye = data[11]

    # Create .h5 file
    hf = h5py.File(gv.SNMODELS_DIR + model_upper, 'w')

    g = hf.create_group('global')
    gr = hf.create_group('grid')
    n = hf.create_group('nuclear')
    h = hf.create_group('hydro')

    for (i,s) in enumerate(species):
      n.create_dataset(s, data=xnu[i])
    n.create_dataset('ye', data=ye)

    g.create_dataset('nx', data=nx)
    g.create_dataset('nnuc_ad', data=xnu.shape[0])
    gr.create_dataset('xzn', data=xzn)
    h.create_dataset('vex', data=vel)
    h.create_dataset('vomega', data=vomega)
    h.create_dataset('den', data=den)
    h.create_dataset('tem', data=tem)
    h.create_dataset('sto', data=sto)
    h.create_dataset('pre', data=pre)
    h.create_dataset('eint', data=eint)
    n.create_dataset('Abar', data=Abar)
    gr.create_dataset('mass', data=mass)
    hf.close()