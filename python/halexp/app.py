import os
import json
import yaml

from .index import Index
from .corpus import Corpus

from flask import Flask, abort, request, jsonify, redirect


config_path = os.environ['APPCONFIG']
with open(config_path, "r") as fh:
    params = yaml.load(fh, Loader=yaml.SafeLoader)

LOGOURL = params['app']['style']['logoUrl']
IMAGEWIDTH = params['app']['style']['imageWidth']


app = Flask(__name__)
print(params['corpus'])
halCorpus = Corpus(**params['corpus'])
index = Index(corpus=halCorpus, **params['index'])


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
    return f'''
          <form method="POST">
              <img src={imageUrl} alt="" style="width:{imageWidth}px;">
              <h2>Experts search engine</h2>
              </br>
              <div><label>{t}<input type="text" name="query"></label></div>
              </br>
              <div><label>{n}<input type="text" name="hits"></label></div>
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
    return redirect("form")

@app.route('/query')
def query():
    """
    """
    query = request.args.get('query')
    if query is None:
        return {'error': 'Missing `query` argument in query string'}
    nb_hits = request.args.get('hits')
    if nb_hits is None:
        return {'error': 'Missing `hits` argument in query string'}

    res = index.retrieve(query=query, top_k=castInt(nb_hits))

    return jsonify(reponses=res['json'])

@app.route('/form', methods=['GET', 'POST'])
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
        res = index.retrieve(query=query, top_k=castInt(nb_hits))
        return formatReponseHtml(query, res['citation'], LOGOURL, IMAGEWIDTH)

    return getFormHtml(LOGOURL, IMAGEWIDTH)

