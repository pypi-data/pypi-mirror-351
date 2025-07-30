#!/bin/bash

. /opt/conda/etc/profile.d/conda.sh
conda activate $CONDA_ENV
if [ -n "$CI" ]; then
    echo "CI detected, using default /bin/bash"
    exec /bin/bash
fi

echo Command: "$COMMAND"
exec $@
