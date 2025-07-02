### 1. `Create_morphospace/`

Includes the scripts, input data, and resulting output files used to generate the cognitive morphospace from term-based brain maps. 

Note that the folowwing Nifi files to create the morphospace are available in Neurovault : https://neurovault.org/collections/19566/

- `Images/` – NIfTI files for 506 cognitive terms (from Neurosynth) projected to the white matter
- `ROI2mm/` – Binary parcels for association and commissural parcellations

#### Scripts:
- `0-ExtractROIs.sh`  
  Computes the mean intensity of each term map within each parcel using `fslstats`.

- `1-Combineit.sh`  
  Combines all extracted values into a single CSV (`AssoComm.csv`) with one column per parcel.

- `2-perlit.sh`  
  Cleans the resulting CSV file for use in further steps.


- `3-parcellUMAP_neurosynth_2017_changedDIM.py`  
  **Input:** `AssoComm.csv`  
  **Output:**  
  - `00_2017_coordinates_wm_MOTparcels.csv` (2D UMAP coordinates)  
  - `00_2017_wm_3D_MOTparcels.sav` (saved UMAP space)


- `Plot3D.ipynb`  
  **Input:** `00_2017_coordinates_wm_MOTparcels.csv`  
  **Output:** 3D plot of the morphospace (interactive figure)

