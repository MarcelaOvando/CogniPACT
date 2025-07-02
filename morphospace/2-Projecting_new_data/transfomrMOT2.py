import pickle
import numpy as np
import pandas as pd

# Reopen the space
loaded_reducer = pickle.load(open('00_2017_wm_3D_MOTparcels.sav', 'rb'))

# Read the CSV of the new maps parcellation matrix
mycsvfile = "myparcellationAssoComm.csv"
data_csv = pd.read_csv(mycsvfile, header=None, sep=';')

# Convert to ndarray and transpose
df = np.array(data_csv).T
print(f"Shape of df after transpose: {df.shape}")

# Coordinates output file
output = "coordinates_newMOT.csv"

# Projection of each new map in the BCS
dist = np.zeros((len(data_csv), 3))  # Ensure the shape is (n_samples, 3)

for col in range(df.shape[1]):
    # Transform each column of df (which is a 1D array) into the model's space
    d = loaded_reducer.transform(df[:, col].reshape(1, -1))  # Reshape to (1, n_features)
    dist[col] = d.flatten()  # Flatten to match the target shape (3,) for each sample

# Save the result
np.savetxt(output, dist, delimiter=',')
