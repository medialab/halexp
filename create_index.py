import os
import yaml
from time import time as now

from halexp.index import setIndexPath, Index
from halexp.corpus import Corpus

config_path = os.environ['APPCONFIG']
with open(config_path, "r") as fh:
    params = yaml.load(fh, Loader=yaml.SafeLoader)

params['index']['index_path'] = setIndexPath(params)
print("Preparing Index...")
t0 = now()
index = Index(**params['index'])
t1 = now()
print("Index prepared in %ss." % int(t1 - t0))
print("Indexing corpus...")
corpus = Corpus(index=index, **params['corpus'])
t2 = now()
print("Corpus indexed in %ss." % int(t2 - t1))
print("Index path prebuilt in:", params['index']['index_path'])

