import os
import yaml
import json
import requests
from argparse import ArgumentParser

ap = ArgumentParser()
ap.add_argument('--host', type=str, default="127.0.0.1")
ap.add_argument('--port', type=str, default="80")
args = ap.parse_args()
HOST = args.host
PORT = args.port

HITS = 3
QUERY="Moralisme%20progressiste%20et%20pratiques%20punitives%20dans%20la%20lutte%20contre%20les%20violences%20sexistes"
URL = f"http://{HOST}:{PORT}/query?query={QUERY}&hits={HITS}"

# sending get request and saving the response as response object
print(f"Quering: {URL}\n")
res = requests.get(url=URL)

# extracting data in json format
data = res.json()
print(data)

