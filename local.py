import os
import json
import yaml
from argparse import ArgumentParser

from halexp import Index, Corpus

ap = ArgumentParser()
ap.add_argument('--config', type=str)
args = ap.parse_args()
config = args.config

with open(config, "r") as fh:
    params = yaml.load(fh, Loader=yaml.SafeLoader)

def setIndexPath(params):
    indexPath = f"{params['corpus']['portail']}_"
    indexPath += f"{params['corpus']['query']}_"
    indexPath += f"max_length_{params['corpus']['max_length']}"
    if params['corpus']['use_keys']['title']:
        indexPath += f"_title"
    if params['corpus']['use_keys']['subtitle']:
        indexPath += f"_subtitle"
    if params['corpus']['use_keys']['keywords']:
        indexPath += f"_keywords"
    indexPath = os.path.join('index', indexPath.replace('*:*', 'xxx')+'.index')
    return indexPath

params['index']['index_path'] = setIndexPath(params)
index = Index(**params['index'])

corpus = Corpus(index=index, **params['corpus'])


# Jean-Philippe Cointet
query = "cartographies de l’espace public et ses dynamiques"
# Dominique Cardon
# query = "l'espace public numérique et les agencements algorithmiques"
# Emma Bonutti D’Agostini
# query = "circulation du discours et de l'idéologie de l'extrême droite dans les sphères journalistiques"

# query = 'Social media polarisation'
# query = "Moralisme progressiste et pratiques punitives dans la lutte contre les violences sexistes"

print(f"Local app: query = `{query}`")

# res = corpus.retrieveAuthors(query=query, top_k=-1)
# print("Local app:")
# for r in res[:params['app']['default_nb_hits']]:
#     print("--------------------")
#     print(f"author: {r['author']}")
#     print(f"rank: {r['rank']}")
#     print(f"rank_score: {r['rank_score']:.3f}")
#     print(f"docs_median_score: {r['docs_median_score']:.3f}")
#     print(f"docs_mean_score: {r['docs_mean_score']:.3f}")
#     print(f"docs_max_score: {r['docs_max_score']:.3f}")
#     print(f"docs_min_score: {r['docs_min_score']:.3f}")
#     print(f"nb_hits: {r['nb_hits']}")
#     for n, (score, doc) in enumerate(zip(r['docs_scores'], r['docs'])):
#         print(f"{n}. {score:.2f} {doc}")

res = corpus.retrievePapers(query=query, top_k=-1)
print("Local app:")
for r in res[:params['app']['default_nb_hits']]:
    print("--------------------")
    print(f"doc: {r['doc']}")
    print(f"rank_score: {r['rank_score']:.3f}")
    print(f"doc_median_score: {r['doc_median_score']:.3f}")
    print(f"doc_mean_score: {r['doc_mean_score']:.3f}")
    print(f"doc_max_score: {r['doc_max_score']:.3f}")
    print(f"doc_min_score: {r['doc_min_score']:.3f}")
    print(f"nb_hits: {r['nb_hits']}")
    print(f"rank: {r['rank']}")

