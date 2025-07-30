#!/bin/bash
set -e
. /opt/conda/etc/profile.d/conda.sh
conda activate base
mamba env create -f /tmp/envs/environment.yml
