import os
import yaml
import json
import requests
from argparse import ArgumentParser

ap = ArgumentParser()
ap.add_argument('--config', type=str)
args = ap.parse_args()
config = args.config

with open(config, "r") as fh:
    params = yaml.load(fh, Loader=yaml.SafeLoader)

params = params['corpus']

dump_file = os.path.abspath(params['dump_file'])

BASE_URL = params['baseUrl']
PAGINATION_COUNT = params['pagination_count']
QUERY = params['query']
FL_PARAM = '&fl='+','.join(params['fields'])
PORTAIL = params['portail']

base_url = f"{BASE_URL}/search/{PORTAIL}/?q={QUERY}"
base_url += f"&wt=json&fl={FL_PARAM}"
base_url += f"&rows={PAGINATION_COUNT}&sort=docid+asc"

print("Downloading HAL dump...")

cursorMark = "*"
prevCursorMark = ""

docs = []
while cursorMark != prevCursorMark:

    url = base_url+f"&cursorMark={cursorMark}"
    print(url)
    prevCursorMark = cursorMark
    x = requests.get(url)
    if x.ok:
        res = json.loads(x.text)
    else:
        raise ValueError(f"Failed query: {x}")
    if 'error' in res:
        raise ValueError(res['error'])
    docs.extend(res['response']['docs'])
    cursorMark = res['nextCursorMark']

with open(dump_file, 'w') as fp:
    json.dump(docs, fp)
print(f"got {len(docs)} entries, saved at {dump_file}.")
