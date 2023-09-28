#bin/bash

# get HAL dump
python get_dump.py --config=config.yaml
# run server
flask run --host=0.0.0.0 --port=80 --debugger
