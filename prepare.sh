#bin/bash

# read Environment variables to edit config
python prepare_config.py

# get HAL dump
python get_dump.py --config=config.yaml

export APPCONFIG=$(pwd)/config.yaml

# prepare models & index from dump
mkdir -p index
python load_models.py --config=config.yaml

exec "$@"
