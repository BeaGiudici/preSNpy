########################################################################
#
# This script reads the output of the 1D stellar evolution code KEPLER
# The original routine is not mine
# 
########################################################################
import sys
import numpy as np
import h5py
import preSNpy.global_vars as gv

if len(sys.argv) != 3:
  raise ValueError('Usage: python read_model.py <progenitor> <model>')
progenitor = sys.argv[1]
model = sys.argv[2]

species=(['n1'],['p1','H1'],['he4','He4'],['c12','C12'],['o16','O16'],\
         ['ne20','Ne20'],['mg24','Mg24'],['si28','Si28'],['s32','S32'],\
         ['ar36','Ar36'],['ca40','Ca40'],['ti44','Ti44'],['cr48','Cr48'],\
         ['fe52','Fe52'],['ni56','Ni56'],['x56','X'])

if progenitor == 'rsg':
  model_upper = model.upper()
  model_upper.replace('.', '_')
  model += '_postbounce'
  file = open(gv.POSTDIR + model)

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
  hf.close()