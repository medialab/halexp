import os
import yaml
import json
import requests

config = os.path.abspath("config.yaml")
with open(config, "r") as fh:
    params = yaml.load(fh, Loader=yaml.SafeLoader)

params = params['corpus']

dump_path = os.path.abspath(params['dump_path'])

BASE_URL = params['baseUrl']
labStructId_i = params['labStructId_i']
collId_i = params['collId_i']
PAGINATION_COUNT = params['pagination_count']

query = f"labStructId_i:{labStructId_i}+OR+collId_i:{collId_i}"
FL_PARAM = '&fl='+','.join(params['fields'])
url = f"{BASE_URL}/search/index/?q={query}&wt=json&fl={FL_PARAM}"
url += f"&rows={PAGINATION_COUNT}&cursorMark=&sort=docid+asc"

print(f"Query: {url}\n")

print("Downloading HAL dump...")
x = requests.get(url)

if x.ok:
    docs = json.loads(x.text)['response']['docs']
    with open(dump_path, 'w') as fp:
        json.dump(docs, fp)
    print(f"got {len(docs)} entries, saved at {dump_path}.")
else:
    print(x)