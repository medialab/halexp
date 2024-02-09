import os
import json
import yaml
import pprint
from collections import Counter

from .index import Index
from .corpus import Corpus

from flask import Flask, abort, request, jsonify, redirect


config_path = os.environ['APPCONFIG']
with open(config_path, "r") as fh:
    params = yaml.load(fh, Loader=yaml.SafeLoader)

LOGOURL = params['app']['style']['logoUrl']
IMAGEWIDTH = params['app']['style']['imageWidth']

app = Flask(__name__)


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

def castInt(k):
    # there is probably a better way of doing this
    try:
        return int(k)
    except:
        abort(400)


def getFormHtml(imageUrl, imageWidth):
    t = "Veuillez saisir une phrase "
    t += "(sujet, projet de recherche ou d'article...) "
    t += "dans la langue de votre choix : "
    n = "Nombre de réponses souhaitées : "
    y = "Année minimale : "
    s = "Score minimale : "
    return f'''
          <form method="POST">
              <img src={imageUrl} alt="" style="width:{imageWidth}px;">
              <h2>Experts search engine</h2>
              </br>
              <div><label>{t}<input type="text" name="query"></label></div>
              </br>
              <div><label>{n}<input type="text" name="hits" value="5"></label></div>
              </br>
              <div><label>{y}<input type="text" name="min_year" value="2000"></label></div>
              </br>
              <div><label>{s}<input type="text" name="score_threshold" value="0.3"></label></div>
              </br>
              <input type="submit" value="RECHERCHER">
          </form>'''

def formatReponseHtml(query, res, imageUrl, imageWidth):
    html = f'''
        <img src={imageUrl} alt="" style="width:{imageWidth}px;">
        <h2>Experts search engine</h2>
        </br>
        <h3>Votre requête :</h3>
        <p>{query}</p>
        <h3>Resultats obtenus :</h3>
    '''
    for r in res:
        score = f"{r['score']:.3f}"
        citation = str(r['citation'])
        p = score+'   '+citation
        html += f'''
            <p>{p}<p>
        '''
    return html


@app.route('/')
def landing():
    return redirect("docs/form")

@app.route('/docs/query')
def query():
    """
    """
    query = request.args.get('query')
    if query is None:
        return {'error': 'Missing `query` argument in query string'}
    nb_hits = request.args.get('hits')
    if nb_hits is None:
        nb_hits = params['app']['default_nb_hits']

    res = index.retrieve(query=query, top_k=castInt(nb_hits))

    return jsonify(reponses=res['json'])

@app.route('/docs/form', methods=['GET', 'POST'])
def form():
    """
    Allows both GET and POST requests.
    Displays the form if GET and process incoming data if POST.
    """

    # from logzero import logger
    # https://logzero.readthedocs.io/en/latest/
    # logger.info("/")

    if request.method == 'POST':
        query = request.form.get('query')
        nb_hits = request.form.get('hits')
        score_threshold = request.form.get('score_threshold')
        min_year = request.form.get('min_year')
        if nb_hits is None:
            nb_hits = params['app']['default_nb_hits']
        res = corpus.retrieveDocuments(
            query=query,
            top_k=castInt(nb_hits),
            score_threshold=score_threshold,
            min_year=min_year,
            )
        return formatReponseHtml(query, res['citation'], LOGOURL, IMAGEWIDTH)

    return getFormHtml(LOGOURL, IMAGEWIDTH)

