"""
https://www.digitalocean.com/community/tutorials/processing-incoming-request-data-in-flask
"""

from flask import Flask, request, jsonify
from .retriever import Retriever

# create the Flask app
app = Flask(__name__)

retriever = Retriever(
    data_path='/home/jimena/work/dev/halexp/hal-productions.json',
    top_k=3
)


def formatHtml(query, authors):
    html = f"<h1>Votre requête :</h1>"
    html += f"<p>{query}</p>"
    html += "\n<h1>Resultats obtenus :</h1>"
    for author in authors:
        html += f"\n<p>{author}<p>"
    return html


@app.route('/query')
def query():
    """
    ip:5000/query?query=Moralisme%20progressiste%20et%20pratiques%20punitives%20dans%20la%20lutte%20contre%20les%20violences%20sexistes
    """
    # if key doesn't exist, returns None
    query = request.args.get('query')
    if query is not None:
        print(query)
        dict_, authors = retriever.retrieve(inp_question=query)
        print(authors)
        return formatHtml(query, authors)
    return "<p>Missing `query` argument in query string.<p>"


# allow both GET and POST requests
@app.route('/form', methods=['GET', 'POST'])
def form():
    """
    ip:5000/form
    """
    if request.method == 'POST':
        query = request.form.get('query')
        print(query)
        dict_, authors = retriever.retrieve(inp_question=query)
        print(authors)
        return formatHtml(query, authors)

    t = "Veuillez saisir une phrase "
    t += "(sujet, projet de recherche ou d'article...) "
    t += "dans la langue de votre choix:"
    html = f'''
          <form method="POST">
              <div><label>{t}<input type="text" name="query"></label></div>
              </br>
              <input type="submit" value="RECHERCHER">
          </form>'''

    return html


# GET requests will be blocked
@app.route('/json', methods=['POST'])
def json():
    """
    python -c 'import requests; print(requests.post(url="http://ip:5000/json", json={"query": "Moralisme progressiste et pratiques punitives dans la lutte contre les violences sexistes"}).text)'

    """
    request_data = request.get_json()

    if request_data:
        if 'query' in request_data:
            query = request_data['query']
            if query:
                print(query)
                dict_, authors = retriever.retrieve(inp_question=query)
                print(dict_)
                return dict_

    return {}


# if __name__ == '__main__':
#     # run app in debug mode on port 5000
#     app.run(debug=True, port=5000)
