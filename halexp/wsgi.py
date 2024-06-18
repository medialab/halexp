import os
import yaml
import pprint
from collections import Counter

from .index import setIndexPath, Index
from .corpus import Corpus

from flask import Flask, abort, request, jsonify, redirect


config_path = os.environ['APPCONFIG']
with open(config_path, "r") as fh:
    params = yaml.load(fh, Loader=yaml.SafeLoader)

LOGOURL = params['app']['style']['logoUrl']
IMAGEWIDTH = params['app']['style']['imageWidth']

params['index']['index_path'] = setIndexPath(params)
index = Index(**params['index'])
corpus = Corpus(index=index, **params['corpus'])
retrieveKwargs = params['app']['retrieve']

# some stats
authors = set([
    a for doc in corpus.documents for a in doc.authors])
a0 = len(authors)
print(f"Local app: found {a0} different authors.")


def castInt(k):
    # there is probably a better way of doing this
    try:
        return int(k)
    except:
        abort(400)

def castFloat(k):
    # there is probably a better way of doing this
    try:
        return float(k)
    except:
        abort(400)


def getFormHtml(imageUrl, imageWidth):
    t = "Veuillez saisir une phrase "
    t += "(sujet, projet de recherche ou d'article...) "
    t += "dans la langue de votre choix : "
    n = "Nombre de réponses souhaitées : "
    y = "Année de départ : "
    s = "Score minimal (entre 0 et 1) : "
    a = "Métrique d'agrégation : "
    mean_selected = " selected" if params['app']['retrieve']['rank_metric'] == "mean" else ""
    median_selected = " selected" if params['app']['retrieve']['rank_metric'] == "median" else ""
    logmean_selected = " selected" if params['app']['retrieve']['rank_metric'] == "log-mean" else ""
    sigmoidmean_selected = " selected" if params['app']['retrieve']['rank_metric'] == "sigmoid-mean" else ""
    sigmoid_selected = " selected" if params['app']['retrieve']['rank_metric'] == "sigmoid" else ""
    return f'''
          <form method="POST">
              <img src={imageUrl} alt="" style="width:{imageWidth}px;">
              <h2>Experts search engine</h2>
              </br>
              <div><label>{t}<input type="text" name="query" size="70" placeholder="cartographies de l’espace public et ses dynamiques"></label></div>
              </br>
              <div><label>{n}<input type="text" name="hits" value="{params['app']['show']}"></label></div>
              </br>
              <div><label>{y}<input type="int" name="min_year" value="{params['app']['retrieve']['min_year']}"></label></div>
              </br>
              <div><label>{s}<input type="float" name="score_threshold" value="{params['app']['retrieve']['score_threshold']}"></label></div>
              </br>
              <div><label>{a}<select name="rank_metric">
                <option value="mean"{mean_selected}>moyenne</option>
                <option value="median"{median_selected}>médiane</option>
                <option value="log-mean"{logmean_selected}>moyenne logarithmique</option>
                <option value="sigmoid-mean"{sigmoidmean_selected}>moyenne sigmoïde</option>
                <option value="sigmoid"{sigmoid_selected}>sigmoïde</option>
              </select>
              </br>
              <input type="submit" value="RECHERCHER">
          </form>'''

def formatDocsReponseHtml(query, res, nb_show, imageUrl, imageWidth):
    html = f'''
        <img src={imageUrl} alt="" style="width:{imageWidth}px;">
        <h2>Experts search engine</h2>
        </br>
        <h3>Votre requête :</h3>
        <p>{query}</p>
        <h3>Documents trouvés :</h3>
    '''
    for r in res[:nb_show]:
        authors_names = r['doc'].getAuthorsFullNamesStr()
        authors_urls = r['doc'].getAuthors()

        phrases_list = """<ol>"""
        for phrase, score in zip(r['doc_phrases'], r['doc_scores']):
            phrases_list += f"<li>{score:.3f} {' '.join(phrase)}</li>"
        phrases_list += """</ol>"""

        html += f'''
            <p><b>  Document # {r['rank'] + 1}</b><p>
            <p><b>  titre :</b>  {r['doc'].title}<p>
            <p><b>  date publication :</b>  {r['doc'].publication_date}<p>
            <p><b>  link HAL :</b> <a href="{r['doc'].uri}">{r['doc'].uri}</a><p>
            <p><b>  auteur·ice·s :</b>  {authors_names}<p>
            <p><b>  aggregation score :</b>  {r['rank_score']:.3f}<p>
            <p><b>  phrases similaires :</b> <i>{phrases_list}</i><p>
            <br>
        '''
    return html


def getAuthorHalLink(author):

    baseUrl = 'https://sciencespo.hal.science/search/index/q/*'

    if author.authIdHal and not author.authIdHal in ['0', 0]:
        return f'{baseUrl}/authIdHal_i/{author.authIdHal}'

    if author.fullName:
        search_name = "+".join(author.fullName.split(' '))
        return f'{baseUrl}/authFullName_s/{search_name}'

    return None


def formatAuthorsReponseHtml(query, res, nb_show, imageUrl, imageWidth):
    html = f'''
        <img src={imageUrl} alt="" style="width:{imageWidth}px;">
        <h2>Experts search engine</h2>
        </br>
        <h3>Votre requête :</h3>
        <p>{query}</p>
        <h3>Auteur·ice·s trouvé·es :</h3>
    '''
    for r in res[:nb_show]:
        author = r['author']

        signature = author.authSciencesPoSignature
        if not signature:
            signature = [""]

        phrases_list = """<ol>"""
        for n, (score, doc) in enumerate(zip(r['docs_scores'], r['docs'])):
                phrases_list += f'<li>{score:.3f} {" ".join(doc.phrases)} <a href="{doc.uri}">doc</a></li>'
        phrases_list += """</ol>"""

        authorLink = getAuthorHalLink(r['author'])
        if authorLink:
            authorNom = f"<a href='{authorLink}'>{r['author'].fullName}</a>"
        else:
            authorNom = r['author'].fullName

        html += f'''
            <p><b>  auteur·ice # {r['rank'] + 1}</b><p>
            <p><b>  nom : </b>{authorNom}<p>
            <p><b>  id HAL :</b>  {r['author'].authIdHal}<p>
            <p><b>  laboratoires :</b>  {' AND '.join(r['author'].authLabs)}<p>
            <p><b>  signature : <a href="{signature[0]}">{signature[0]}</a></b><p>
            <p><b>  aggregation score :</b>  {r['rank_score']:.3f}<p>
            <p><b>  phrases similaires :</b> <i>{phrases_list}</i><p>
            <br>
        '''

    return html



app = Flask(__name__)

@app.route('/')
def landing():
    return redirect("authors/form")


@app.route('/docs/query')
def queryDocs():
    query = request.args.get('query')
    if query is None:
        return {'error': 'Missing `query` argument in query string'}
    nb_show = request.args.get('hits')
    if nb_show is None:
        nb_show = params['app']['show']
    nb_show = castInt(nb_show)
    score_threshold = request.args.get('score_threshold')
    if score_threshold is None:
        score_threshold = params['app']['retrieve']['score_threshold']
    min_year = request.args.get('min_year')
    if min_year is None:
        min_year = params['app']['retrieve']['min_year']
    rank_metric = request.args.get('rank_metric')
    if rank_metric is None:
        rank_metric = params['app']['retrieve']['rank_metric']

    res = corpus.retrieveDocuments(
        query=query,
        top_k=castInt(params['app']['retrieve']['top_k']),
        score_threshold=castFloat(score_threshold),
        min_year=castInt(min_year),
        rank_metric=rank_metric
        )

    reponses = res[:nb_show]
    for r in reponses:
        del r['doc']

    return jsonify(reponses=reponses)

@app.route('/docs/form', methods=['GET', 'POST'])
def formDocs():
    """
    Allows both GET and POST requests.
    Displays the form if GET and process incoming data if POST.
    """

    if request.method == 'POST':
        query = request.form.get('query')
        nb_show = request.form.get('hits')
        if nb_show is None:
            nb_show = params['app']['show']
        score_threshold = request.form.get('score_threshold')
        min_year = request.form.get('min_year')
        rank_metric = request.form.get('rank_metric')
        res = corpus.retrieveDocuments(
            query=query,
            top_k=castInt(params['app']['retrieve']['top_k']),
            score_threshold=castFloat(score_threshold),
            min_year=castInt(min_year),
            rank_metric=rank_metric
            )
        return formatDocsReponseHtml(query, res, castInt(nb_show), LOGOURL, IMAGEWIDTH)

    return getFormHtml(LOGOURL, IMAGEWIDTH)


@app.route('/authors/query')
def queryAuthors():
    query = request.args.get('query')
    if query is None:
        return {'error': 'Missing `query` argument in query string'}
    nb_show = request.args.get('hits')
    if nb_show is None:
        nb_show = params['app']['show']
    nb_show = castInt(nb_show)
    score_threshold = request.args.get('score_threshold')
    if score_threshold is None:
        score_threshold = params['app']['retrieve']['score_threshold']
    min_year = request.args.get('min_year')
    if min_year is None:
        min_year = params['app']['retrieve']['min_year']
    rank_metric = request.args.get('rank_metric')
    if rank_metric is None:
        rank_metric = params['app']['retrieve']['rank_metric']

    res = corpus.retrieveAuthors(
        query=query,
        top_k=castInt(params['app']['retrieve']['top_k']),
        score_threshold=castFloat(score_threshold),
        min_year=castInt(min_year),
        rank_metric=rank_metric
        )

    res = res[:nb_show]

    reponses = []
    for r in res:
        tmp = {
            'position': r['rank'] + 1,
            'author_name': r['author'].fullName,
            'author_id-hal': r['author'].authIdHal,
            'author_labs_id': r['author'].authLabs,
            'aggregation score': r['rank_score'],
            'author_signature': r['author'].authSciencesPoSignature,
        }
        tmp['results_phrases'] = [f'{score:.3f} {" ".join(doc.phrases)}'
            for score, doc in zip(r['docs_scores'], r['docs'])]

        tmp['results_metadata'] = [doc.metadata for doc in r['docs']]

        reponses.append(tmp)

    return jsonify(reponses=reponses)


@app.route('/authors/form', methods=['GET', 'POST'])
def formAuthors():
    """
    Allows both GET and POST requests.
    Displays the form if GET and process incoming data if POST.
    """

    if request.method == 'POST':
        query = request.form.get('query')
        nb_show = request.form.get('hits')
        if nb_show is None:
            nb_show = params['app']['show']
        score_threshold = request.form.get('score_threshold')
        min_year = request.form.get('min_year')
        rank_metric = request.form.get('rank_metric')

        res = corpus.retrieveAuthors(
            query=query,
            top_k=castInt(params['app']['retrieve']['top_k']),
            score_threshold=castFloat(score_threshold),
            min_year=castInt(min_year),
            rank_metric=rank_metric
            )
        return formatAuthorsReponseHtml(query, res, castInt(nb_show), LOGOURL, IMAGEWIDTH)

    return getFormHtml(LOGOURL, IMAGEWIDTH)

