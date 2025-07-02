#!/bin/bash

#SBATCH --mem=64G
#SBATCH --time=6-00:00:00
#SBATCH --chdir=.
#SBATCH --job-name=AllFlirt



# Base paths
base_dir="/scratch/movando/NBS"
ref_img="/scratch/movando/movie/all_preprocessed/MNI152_T1_2mm_brain.nii.gz"
motion_params_dir="/scratch/movando/NBS/motion_params"
output_base="/scratch/movando/NBS/preprocessed_output"

# Loop over subjects
for subj in sub{1..8}; do
    subj_dir="${base_dir}/${subj}"

    # Loop over sessions
    for sess_num in {1..30}; do
        session_name=$(printf "session%02d" $sess_num)
        session_dir="${subj_dir}/${session_name}"

        if [ ! -d "$session_dir" ]; then
            echo "Skipping missing $session_dir"
            continue
        fi

        echo "Processing $session_dir"
        out_subj_dir="${output_base}/preprocessing_${subj}"
        out_sess_dir="${out_subj_dir}/${session_name}"
        mkdir -p "$out_sess_dir"

        # Process all time series in the session
        for nii_file in "${session_dir}"/timeseries_session${sess_num}_run*.nii.gz; do
            [ -e "$nii_file" ] || continue

            file_base=$(basename "${nii_file%.nii.gz}")
            run_dir="${out_sess_dir}/${file_base}"
            mkdir -p "$run_dir"

            # Extract run number from filename (e.g., run01, run02...)
            run_num=$(echo "$nii_file" | grep -oP 'run\K[0-9]{2}')
            motion_file="${motion_params_dir}/${subj}/motion_session$(printf "%02d" $sess_num)_run${run_num}.tsv"

            echo "High-pass filtering for $file_base (sigma=38 for 100s cutoff, TR=1.333s)"
            fslmaths "$nii_file" -bptf 38 -1 "$run_dir/${file_base}_filtered.nii.gz"

            echo "Checking volumes before and after filtering:"
            n_before=$(fslnvols "$nii_file")
            n_after=$(fslnvols "$run_dir/${file_base}_filtered.nii.gz")
            echo "    Volumes before: $n_before | after filtering: $n_after"

            if [ -f "$motion_file" ]; then
                echo "🧹 Running Nuisance Regression (motion parameters) and demean"
                fsl_glm -i "$run_dir/${file_base}_filtered.nii.gz" \
                        -d "$motion_file" \
                        --out_res="$run_dir/${file_base}_nuisance_regressed.nii.gz" \
                        --demean
            else
                echo "Missing motion file: $motion_file. Skipping nuisance regression."
                cp "$run_dir/${file_base}_filtered.nii.gz" "$run_dir/${file_base}_nuisance_regressed.nii.gz"
            fi

            echo "Resampling to 2mm using FLIRT"
            flirt -in "$run_dir/${file_base}_nuisance_regressed.nii.gz" \
                  -ref "$ref_img" \
                  -applyisoxfm 2.0 \
                  -nosearch \
                  -out "${run_dir}/${file_base}_2mm.nii.gz"
        done
    done
done
