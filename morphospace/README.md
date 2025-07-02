# Cognitive Morphospace: Analysis and Projection Pipeline

This repository contains the data and scripts for building the white matter cognitive morphospace, projecting new functional data into this space, and interpreting the resulting distances in terms of cognitive functions.

---

## Folder and Scripts 

### 1. `Create_morphospace/`

Includes the scripts, input data, and resulting output files used to generate the cognitive morphospace from term-based brain maps. 

Note that, Nifi files to create the morphospace are available in Neurovault : https://neurovault.org/collections/19566/

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
---

### 2. `Projecting_new_data/`

- `transfomrMOT2.py`  
  **Input:**  
  - UMAP space (`Create_morphospace/00_2017_wm_3D_MOTparcels.sav`)  
  - `myparcellationAssoComm.csv` (3655 timepoints × 76 parcels)  
  **Output:** `00_2017_coordinates_wm_MOTparcels.csv`


- `00_2017_coordinates_wm_MOTparcels3d.csv`  
   File containing cognitive term names (first column) and UMAP coordinates

---

### 3. `Euclidean_to_cognition/`

- `EuclediaMOT.ipynb`  
  **Input:**  
  - `Projecting_new_data/00_2017_coordinates_wm_MOTparcels3d.csv`  
  **Output:** `distances_from_new_maps_to_originalMOT.csv` (3655 timepoints × 506 terms)


- `Indentify_cognition_per_frame.ipynb`

  - **Part I**  
    **Input:** `distances_from_new_maps_to_originalMOT.csv`  
    **Output:** `Eucledia_cognition.csv` – closest term and index for each timepoint

  - **Part II**  
    **Input:**  
      - `Eucledia_cognition.csv`  
      - `00_2017_coordinates_wm_MOTparcels3d.csv`  
    **Output:** `final_output_Eucledian_cognition.csv` – includes closest term name

---

