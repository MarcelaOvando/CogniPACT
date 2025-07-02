#Don't forget to pip install umap-learn
#Don't forget to pip install niilearn

#libraries we will be working with
import os
import sys
#import nibabel as nib
import pandas as pd
from pandas import DataFrame
import numpy as np
#import umap
import umap.umap_ as umap
import matplotlib.pyplot as plt
import pickle
#from mpl_toolkits.mplot3d import Axes3D
#define variables
#output = sys.argv[1]

#space = sys.argv[2]

#Load data

mycsvfile = "Parcelled_wm/AssoComm.csv"
data_csv = pd.read_csv(mycsvfile, header=None, sep=";")
datamatrix = np.matrix(data_csv)
datamatrix.shape
#Combine the data
#X = datamatrix
X = np.array(datamatrix)
#Umap that stuff
fit = umap.UMAP(n_components=3, random_state=1)
X_embedded = fit.fit_transform(X)
X_embedded.shape

#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#ax.scatter(X_embedded[:,0], X_embedded[:,1], X_embedded[:,2], s=100)
#plt.title(title, fontsize=18)

#show me your embedding
#plt.scatter(x_axes, y_axes, c = 'black')
#plt.show()

#save the coordinate for each point.
np.savetxt("00_2017_coordinates_wm_MOTparcels.csv", X_embedded)

#M's method. Can play on the run, but not reload in a second round
#save the space
#joblib.dump(fit, space)

space = '00_2017_wm_3D_MOTparcels.sav'
#joblib.dump(fit, space)
pickle.dump(fit,open(space,'wb'))
#reopen the space
#works only on the run for me
#loaded_reducer = joblib.load(space)

#reopen the space later on..
#loaded_reducer = joblib.load('00_space_SET1.sav')

#import data like X
#embedding = loaded_reducer.fit_transform(scaled_penguin_data)

###################################################################################



#mycsvfile = "LeftRight_2017_parcelled.csv"
#data_csv = pd.read_csv(mycsvfile, header=None, sep=";")
#df = pd.DataFrame (data_csv)
#df1 = df.sample(frac=1).reset_index(drop=True)
#df1.T
#df2 = df1.sample(frac=1).reset_index(drop=True)
