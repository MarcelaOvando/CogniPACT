cd ROIs2mm
for a in *.nii.gz
do echo $a
cd ..
    cd Images
    for b in *.nii.gz
    do echo $b
    cd ..
fslstats Images/${b} -k ROIs2mm/${a} -m>>$a.csv
    cd Images
    done
done
