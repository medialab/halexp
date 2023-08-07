"""
https://www.digitalocean.com/community/tutorials/processing-incoming-request-data-in-flask
"""

from flask import Flask, abort, request, jsonify
from .retriever import Retriever
import json

# create the Flask app
app = Flask(__name__)

retriever = Retriever(
    data_path='/home/jimena/work/dev/halexp/hal-productions.json',
)


def formatHtml(query, res):
    html = f"<h3>Votre requête :</h3>"
    html += f"<p>{query}</p>"
    html += "\n<h3>Resultats obtenus :</h3>"
    for r in res:
        score = f"{r['score']:.3f}"
        citation = str(r['citation'])
        p = score+'   '+citation
        html += f"\n<p>{p}<p>"
    return html

def castInt(k):
    # there is probably a better way of doing this
    try:
        return int(k)
    except:
        abort(400)


@app.route('/query')
def query():
    """
    ip:port/query?query=Moralisme%20progressiste%20et%20pratiques%20punitives%20dans%20la%20lutte%20contre%20les%20violences%20sexistes&hits=3
    """

    query = request.args.get('query')
    nb_hits = request.args.get('hits')
    if query is None:
        return {'error': 'Missing `query` argument in query string'}
    if nb_hits is None:
        return {'error': 'Missing `hits` argument in query string'}

    nb_hits = castInt(nb_hits)

    print(f"The query is: {query}")
    res = retriever.retrieve(query=query, top_k=nb_hits)
    res = res['json']
    print(f"The responses are:\n{res}")

    return jsonify(reponses=res)



# allow both GET and POST requests
@app.route('/form', methods=['GET', 'POST'])
def form():
    """
    ip:port/form
    """
    if request.method == 'POST':
        query = request.form.get('query')
        nb_hits = request.form.get('hits')
        nb_hits = castInt(nb_hits)
        print(query)
        res = retriever.retrieve(query=query, top_k=nb_hits)
        return formatHtml(query, res['citation'])

    t = "Veuillez saisir une phrase "
    t += "(sujet, projet de recherche ou d'article...) "
    t += "dans la langue de votre choix : "
    n = "Nombre de réponses souhaitées : "
    html = f'''
          <form method="POST">
              <div><label>{t}<input type="text" name="query"></label></div>
              <div><label>{n}<input type="text" name="hits"></label></div>
              </br>
              <input type="submit" value="RECHERCHER">
          </form>'''

    return html
