"""
https://www.digitalocean.com/community/tutorials/processing-incoming-request-data-in-flask
"""

import os
import json
import yaml

from .index import Index
from .corpus import Corpus

from flask import Flask, abort, request, jsonify, redirect


config = os.path.abspath("../../config.yaml")
with open(config, "r") as fh:
    params = yaml.load(fh, Loader=yaml.SafeLoader)

app = Flask(__name__)
halCorpus = Corpus(**params['corpus'])
index = Index(corpus=halCorpus, **params['index'])


def castInt(k):
    # there is probably a better way of doing this
    try:
        return int(k)
    except:
        abort(400)

def formatReponseHtml(query, res):
    html = f'''
        <img src={params['logoUrl']} alt="" style="width:450px;">
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

def getFormHtml():
    t = "Veuillez saisir une phrase "
    t += "(sujet, projet de recherche ou d'article...) "
    t += "dans la langue de votre choix : "
    n = "Nombre de réponses souhaitées : "
    return f'''
          <form method="POST">
              <img src={params['logoUrl']} alt="" style="width:450px;">
              <h2>Experts search engine</h2>
              </br>
              <div><label>{t}<input type="text" name="query"></label></div>
              </br>
              <div><label>{n}<input type="text" name="hits"></label></div>
              </br>
              <input type="submit" value="RECHERCHER">
          </form>'''

@app.route('/')
def landing():
    return redirect("form")


@app.route('/query')
def query():
    """
    ip:port/query?query=Moralisme%20progressiste%20et%20pratiques%20punitives%20dans%20la%20lutte%20contre%20les%20violences%20sexistes&hits=3
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
    ip:port/form
    Allows both GET and POST requests.
    Displays the form if GET and process incoming data if POST.
    """
    if request.method == 'POST':
        query = request.form.get('query')
        nb_hits = request.form.get('hits')
        res = index.retrieve(query=query, top_k=castInt(nb_hits))
        return formatReponseHtml(query, res['citation'])

    return getFormHtml()

