#bin/bash

# read Environment variables to edit config
python prepare_config.py || (echo "ERROR while preparing configuration file" && exit)

# get HAL dump
python get_dump.py --config=config.yaml || (echo "ERROR while downloading HAL data" && exit)

export APPCONFIG=$(pwd)/config.yaml

# prepare models & index from dump
mkdir -p index
python create_index.py --config=config.yaml || (echo "ERROR while building index" && exit)

exec "$@"
