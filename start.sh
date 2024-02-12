#bin/bash

# read Environment variables to edit config
python prepare_config.py

# get HAL dump
python get_dump.py --config=config.yaml

# run server
export APPCONFIG=$(pwd)/config.yaml
export FLASK_APP=$(pwd)/halexp/app.py
flask run --host=0.0.0.0 --port=80 --debugger
#gunicorn --bind 0.0.0.0:5000 halexp.app:app
