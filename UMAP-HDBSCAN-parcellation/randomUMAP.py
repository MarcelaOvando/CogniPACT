#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  2 12:03:48 2025

@author: marcelaovandotellez
"""

import os
from pathlib import Path
import glob
import argparse

import joblib
from tqdm import tqdm
import numpy as np
import pandas as pd
import nibabel as nib
import umap.umap_ as umap
import matplotlib.pyplot as plt


def create_umap_input(input_path_list, data_mask):
    umap_input_list = []
    for file in tqdm(input_path_list):
        fmri_nii = nib.load(file)
        data_fmri = fmri_nii.get_fdata()
        
        masked_fmri_data = data_fmri[np.where(data_mask)]
        np.random.shuffle(masked_fmri_data)
        transposed_masked_fmri_data = masked_fmri_data.T
        
        umap_input_list.append(transposed_masked_fmri_data)
        
    umap_input_matrix = np.column_stack(umap_input_list)
    return umap_input_matrix


def train_umap(input_matrix, **umap_param):
    umap_model = umap.UMAP(**umap_param)
    umap_model.fit(input_matrix)
    return umap_model


def plot_umap(x_axis, y_axis, save_path=None):
    plt.scatter(x_axis, y_axis, s=0.01, cmap="plasma", alpha=0.5)
    plt.title("UMAP")
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()


def run():
    print('Finished')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UMAP and clustering pipeline')
    
    parser.add_argument('input_folder', nargs='?', type=str,
                        default='/data/extra/movando/umap/asso-asso/DATA1-compu/volumes_ttest_results/',
                        help='Input folder containing fMRI volumes')
    
    parser.add_argument('mask_path', nargs='?', type=str,
                        default='/data/extra/movando/umap/cerebellum_excluded_mni_mask.nii.gz',
                        help='Path to mask file')
    
    parser.add_argument('random_state', nargs='?', type=int, default=1, help='Random seed')
    
    parser.add_argument('output_folder', nargs='?', type=str,
                        default='/data/extra/movando/umap/test_random/',
                        help='Output folder')
    
    parser.add_argument('trained_umap', nargs='?', type=str,
                        default='/data/extra/movando/umap/test_random/group1_trained_umap.sav',
                        help='Path to pre-trained UMAP model')
    
    args = parser.parse_args()
    
    print(f'Parameters:\n{args}')
    
    mask_nii = nib.load(args.mask_path)
    data_mask = mask_nii.get_fdata()
    
    files = sorted(glob.glob(os.path.join(args.input_folder, 'output*')))
    
    if args.trained_umap is None or not Path(args.trained_umap).exists():
        umap_input_matrix = create_umap_input(files, data_mask)
        print(f"UMAP input matrix shape: {umap_input_matrix.shape}")
        
        trained_umap = train_umap(umap_input_matrix, random_state=args.random_state)
        joblib.dump(trained_umap, Path(args.output_folder).joinpath('trained_umap1.sav'))
    else:
        print('Using the provided trained UMAP model')
        trained_umap = joblib.load(args.trained_umap)
        
        # You may want to still create the input matrix if you want to transform it
        umap_input_matrix = create_umap_input(files, data_mask)
    
    X_embedded = trained_umap.fit_transform(umap_input_matrix)
    print(f"Embedded shape: {X_embedded.shape}")
    
    x_axes, y_axes = X_embedded[:, 0], X_embedded[:, 1]
    combined_array = np.column_stack((x_axes, y_axes))
    
    np.savetxt(os.path.join(args.output_folder, 'umap_all_combined_loopFinal_noCerebellum1.csv'), combined_array, delimiter=',')
    
    plot_umap(x_axes, y_axes, save_path=os.path.join(args.output_folder, 'umap_plot_1.png'))
    
    run()
