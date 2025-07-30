#!/bin/bash -l
#
# allocate 1 node (4 Cores) with 32 MB RAM for 6 hours
#PBS -l nodes=1:ppn=4:any32g,walltime=06:00:00
#
# job name 
#PBS -N simulate_images_all
#
# first non-empty non-comment line ends PBS options

# conda
__conda_setup="$('/home/vault/caph/mppi31/anaconda2/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/vault/caph/mppi31/anaconda2/etc/profile.d/conda.sh" ]; then
        . "/home/vault/caph/mppi31/anaconda2/etc/profile.d/conda.sh"
    else
        export PATH="/home/vault/caph/mppi31/anaconda2/bin:$PATH"
    fi
fi
unset __conda_setup

conda activate ctapointing-dev

# jobs always start in $HOME - 
# change to work directory
cd  ${PBS_O_WORKDIR}
export OMP_NUM_THREADS=4

# path to ctapointing installation
export CTAPOINTING=${VAULTHOME}/MSTPointing/ctapointing/

# run 
python ${CTAPOINTING}/ctapointing/tools/solve_images.py -n 1000 --spot-collection test_MAGIC-Campaign_ApogeeAspen8050-standard_thresh_0.2_MSTmask --image-collection MAGIC-Campaign
