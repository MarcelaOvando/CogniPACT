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

