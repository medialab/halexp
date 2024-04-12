import os
import json
import yaml
import pprint
from collections import Counter
from argparse import ArgumentParser
from flask import jsonify

from halexp import Index, Corpus
from halexp.index import setIndexPath

ap = ArgumentParser()
ap.add_argument('--config', required=True, type=str)
args = ap.parse_args()
config = args.config

with open(config, "r") as fh:
    params = yaml.load(fh, Loader=yaml.SafeLoader)

params['index']['index_path'] = setIndexPath(params)
index = Index(**params['index'])
corpus = Corpus(index=index, **params['corpus'])
retrieveKwargs = params['app']['retrieve']

# some stats
authors = set([
    a for doc in corpus.documents for a in doc.authors])
a0 = len(authors)

# labsIds = [a.authLabIdHal for a in authors]
# li0 = len(set(labsIds))
print(f"Local app: found {a0} different authors") #  from {li0} labs.")# 1. Jean-Philippe Cointet
# query = "cartographies de l’espace public et ses dynamiques"
# 2. Dominique Cardon
# query = "l'espace public numérique et les agencements algorithmiques"
# 3. Emma Bonutti D’Agostini
# query = "circulation du discours et de l'idéologie de l'extrême droite dans les sphères journalistiques"
# query = 'Social media polarisation'
query = "Moralisme progressiste et pratiques punitives dans la lutte contre les violences sexistes"

print(f"\n\n\n\n\nLocal app: query = `{query}`")
res = corpus.retrieveAuthors(query=query, **retrieveKwargs)
print(res[:params['app']['show']])





print(f"\n\n\n\n\nLocal app: query = `{query}`")
res = corpus.retrieveDocuments(query=query, **retrieveKwargs)
print(res[:params['app']['show']])
