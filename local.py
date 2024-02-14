import os
import json
import yaml
import pprint
from collections import Counter
from argparse import ArgumentParser

from halexp import Index, Corpus
from halexp.index import setIndexPath

ap = ArgumentParser()
ap.add_argument('--config', type=str)
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

labsIds = [a.authLabIdHal for a in authors]
li0 = len(set(labsIds))
print(f"Local app: found {a0} different authors from {li0} labs.")
pprint.pprint(dict(Counter(labsIds).most_common(12)))

labs = [a.authSciencesPoSignature.split('/')[-1]
    for a in authors if a.authSciencesPoSignature]
a1 = len(labs)
l0 = len(set(labs))
print(f"Local app: found {a1} different authors from {l0} Sciences Po labs:")
pprint.pprint(dict(Counter(labs)))

# 1. Jean-Philippe Cointet
query = "cartographies de l’espace public et ses dynamiques"
# 2. Dominique Cardon
# query = "l'espace public numérique et les agencements algorithmiques"
# 3. Emma Bonutti D’Agostini
# query = "circulation du discours et de l'idéologie de l'extrême droite dans les sphères journalistiques"
# query = 'Social media polarisation'
# query = "Moralisme progressiste et pratiques punitives dans la lutte contre les violences sexistes"

print(f"\n\n\n\n\nLocal app: query = `{query}`")
res = corpus.retrieveDocuments(query=query, **retrieveKwargs)
for r in res[:params['app']['show']]:
    print("--------------------")
    print(f"doc: {r['doc']}")
    print(f"rank_score: {r['rank_score']:.3f}")
    print(f"doc_median_score: {r['doc_median_score']:.3f}")
    print(f"doc_mean_score: {r['doc_mean_score']:.3f}")
    print(f"doc_max_score: {r['doc_max_score']:.3f}")
    print(f"doc_min_score: {r['doc_min_score']:.3f}")
    print(f"nb_hits: {r['nb_hits']}")
    print(f"rank: {r['rank']}")


print(f"\n\n\n\n\nLocal app: query = `{query}`")
res = corpus.retrieveAuthors(query=query, **retrieveKwargs)
for r in res[:params['app']['show']]:
    print("--------------------")
    print(f"author: {r['author']}")
    print(f"signature: {r['author'].authSciencesPoSignature}")
    print(f"rank: {r['rank']}")
    print(f"rank_score: {r['rank_score']:.3f}")
    print(f"docs_median_score: {r['docs_median_score']:.3f}")
    print(f"docs_mean_score: {r['docs_mean_score']:.3f}")
    print(f"docs_max_score: {r['docs_max_score']:.3f}")
    print(f"docs_min_score: {r['docs_min_score']:.3f}")
    print(f"nb_hits: {r['nb_hits']}")
    for n, (score, doc) in enumerate(zip(r['docs_scores'], r['docs'])):
        print(f"{n}. {score:.2f} {doc.getPhrasesForEmbedding()}")


