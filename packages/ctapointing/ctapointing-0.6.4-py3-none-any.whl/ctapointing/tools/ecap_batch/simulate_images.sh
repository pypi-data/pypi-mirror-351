#!/bin/bash -l

#SBATCH --time=04:00:00            # comments start with # and do not count as interruptions
#SBATCH --nodes=1
#SBATCH --job-name=ctapointing_simulate_images
#SBATCH --export=NONE              # do not export environment from submitting shell
# first non-empty non-comment line ends SBATCH options
unset SLURM_EXPORT_ENV             # enable export of environment from this script to srun

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

# path to ctapointing installation
export CTAPOINTING=/home/vault/caph/mppi31/MSTPointing/ctapointing/
export WORK=/home/saturn/caph/mppi31

# run
srun python ${CTAPOINTING}/ctapointing/tools/simulate_images.py -n 100 -config "ZWO ASI2600-MM-Pro" --image-collection "sim_ZWO-standard" --apply-moonlight --path $WORK/sim_ZWO_standard
