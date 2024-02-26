import re
import json
from tqdm import tqdm
import numpy as np

from .document import Document

def remove_html_tags(text):
    """Remove html tags from a string"""
    text = re.sub('<a .*?</a>', '', text)
    text = re.sub('<i .*?</i>', '', text)
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


class Corpus:
    """
    A Corpus is a collection of documents.
    """

    invalidAbstracts = [
        "",
        "absent",
        "This item has no abstract",
        "Cette communication n'a pas de résumé",
        "Cette étude n'a pas de résumé",
        "Introduit l'ouvrage",
        "no abstract"
        "...",
        "Résumé à venir",
        "à venir",
        "Non disponible",
        "Not available",
        "Prochainement",
        "Non renseigné",
        "Ce chapitre n'a pas de résumé",
        "This communication has no abstract",
        "Cette publication n'a pas de résumé",
        "Interview",
        "Table ronde",
        "indisponible",
        "non disponible",
        "Résumé",
        "Abstract",
        "Préface",
        "Pas de résumé",
        "Edition de poche augmentée d'un chapitre introductif",
        "This publication has no abstract",
        "Compte rendu de lecture",
        "Éditorial d'inauguration de la revue",
        "Esta publicación no tiene resumen",
        "Les résumés des articles de ce dossier sont disponibles en ligne sur le site de la revue",
        "Commentaire d’arrêt"
    ]

    def __init__(self, index, dump_file, max_length, use_keys, **kwargs):
        """
        dump_file[str]: path to the HAL dump in json format.

        max_length [int]: maximum lenght of the serie of phrases of each doc.

        use_keys [dict]: wheter to include or not the title, subtirle,
        author and keywords of HAL document in the text to be embedded.
        """

        self.index = index

        self.documents = []
        self.nb_documents = 0
        self.halIds = set([])

        self.doc_max_length = max_length
        self.include = use_keys

        self.loadDump(dump_file)
        self.createDocuments()
        self.index.createIndex(self.documents)


    def checkAndReplaceMissingMetadata(
        self,
        key,
        replace_value='',
        replace_nb_key=None):

        nb_missing = 0
        for hd in self.halData:
            if not key in hd:
                replace = [replace_value,]
                if replace_nb_key:
                    replace = replace * len(hd[replace_nb_key])
                hd[key] = replace
                nb_missing += 1

        if nb_missing > 0:
            mssg = f"Corpus: Found {nb_missing} HAL docs out of "
            mssg += f"{len(self.halData)} "
            mssg += f"({100 * nb_missing / len(self.halData):.2f}%) "
            mssg += f"without `{key}` entry."
            print(mssg)

    def loadDump(self, dump_file):

        with open(dump_file) as f:
            self.halData = json.load(f)

        # check if duplicated hal ids
        nb_unique_halId_s = len(set([hd['halId_s'] for hd in self.halData]))
        if not nb_unique_halId_s == len(self.halData):
            raise ValueError(
                f"There are documents in dump with repeated 'halId_s' key.")

        print(
            f"Corpus: found {len(self.halData)} unique entries from json dump.")

        self.checkAndReplaceMissingMetadata('keyword_s', '')
        self.checkAndReplaceMissingMetadata('title_s', '')
        self.checkAndReplaceMissingMetadata('subtitle_s', '')
        self.checkAndReplaceMissingMetadata(
            'labStructName_s', replace_value='LAB NOT FOUND')
        self.checkAndReplaceMissingMetadata(
            'labStructId_i', replace_value='LAB ID NOT FOUND')
        self.checkAndReplaceMissingMetadata(
            'authIdHal_i', replace_nb_key='authFullName_s')

    def split(self, string):
        """
        Apply strategy for splitting phrases from a string.
        """
        splited = [s for s in string.split('.') if s != '']
        splited = [s[1:] if s.startswith(' ') else s for s in splited]
        splited = [s+'.' if not s.endswith('.') else s for s in splited]
        return splited

    def createDocument(self, hd, phrases):
        document = Document(phrases, self.doc_max_length)
        document.setMetadata(hd)
        document.setAuthors(
            hd["authFullName_s"],
            hd["authIdHal_i"],
            hd["labStructName_s"],
            hd["labStructId_i"])
        document.setPublicationDate(hd["publicationDate_s"])
        document.setUri(hd["uri_s"])
        document.setHalId(hd["halId_s"])
        document.setOpenAccess(hd["openAccess_bool"])
        document.setTitle(hd["title_s"][0])
        document.setKeywords(hd["keyword_s"])
        document.setSubtitle(hd["subtitle_s"])

        return document

    def hasValidAbstracts(self, hd):
        if "abstract_s" not in hd:
            return False
        else:
            abstract = hd["abstract_s"]
            if abstract in self.invalidAbstracts or len(abstract) == 0:
                return False
        return True

    def createDocuments(self):
        """
        Create documents from dump data
        """
        for hd in self.halData:
            # create docs from metadata
            if self.include['keywords'] and hd['keyword_s'][0]:
                self.documents.append(
                    self.createDocument(hd, [' '.join(hd['keyword_s'])]))
            if self.include['title'] and hd['title_s']:
                self.documents.append(
                    self.createDocument(hd, hd['title_s']))
            if self.include['subtitle'] and hd['subtitle_s'][0]:
                self.documents.append(
                    self.createDocument(hd, hd['subtitle_s']))
        nb_docs = len(self.documents)
        print(f"Corpus: {nb_docs} documents created from metadata.")

        if self.include['abstract']:
            for hd in self.halData:
                # create docs with phrases
                if self.hasValidAbstracts(hd):
                    sentences = self.split(hd["abstract_s"][0])
                    n = 0
                    while n < len(sentences)-1:
                        r = min(self.doc_max_length, len(sentences)-n)
                        phrases = [sentences[j] for j in range(r)]
                        n += r
                        # create doc with phrases
                        document = self.createDocument(hd, phrases)
                        self.documents.append(document)
        self.nb_documents = len(self.documents)
        print(
            f"Corpus: {self.nb_documents - nb_docs} docs from valid abstracts.")


    def filter_documents(self, results, filters):
        filter_docs = []
        scores = []

        l0 = len(results)
        for r in results:
            document = self.documents[r['corpus_id']]
            if any([f(document) for f in filters]):
                continue
            filter_docs.append(document)
            scores.append(r['score'])
        print(
            f"Corpus: filtered {l0 - len(filter_docs)} out of {l0}.")

        return scores, filter_docs

    def sortAndRankResults(self, agg_scores_dics):

        sorted_results = sorted(
            agg_scores_dics,
            key=lambda x: x['rank_score'],
            reverse=True)

        for k, sr in enumerate(sorted_results):
            sr.update({'rank': k})

        return sorted_results


    def rankScores(self, scores, rank_metric):
        if rank_metric == 'median':
            return np.median(scores)
        elif rank_metric == 'mean':
            return np.mean(scores)
        elif rank_metric == 'log-mean':
            return np.log(1+len(scores)) * np.mean(scores)
        else:
            rms = ['mean', 'median', 'log-mean']
            raise ValueError(
                f"Invalid rank metric `{rank_metric}`, must be one of {rms}")


    def sortFilterAndFormatAuthorsResults(self, results, rank_metric, min_year=-1):

        filters = []
        if min_year > 0:
            filters = [lambda doc: doc.publication_year < int(min_year)]

        scores, filter_docs = self.filter_documents(results, filters)

        authors_agg_scores = dict()
        for score, doc in zip(scores, filter_docs):
            for author in doc.getAuthors():
                if not author in authors_agg_scores:
                    authors_agg_scores[author] = {'scores': [], 'docs': []}
                authors_agg_scores[author]['scores'].append(score)
                authors_agg_scores[author]['docs'].append(doc)

        print(f"Corpus: found {len(authors_agg_scores)} different authors.")

        authors_agg_scores_r = [{
            'author': a,
            'rank_score': self.rankScores(d['scores'], rank_metric),
            'docs_scores': d['scores'],
            'docs_median_score': np.median(d['scores']),
            'docs_mean_score': np.mean(d['scores']),
            'docs_max_score': np.max(d['scores']),
            'docs_min_score': np.min(d['scores']),
            'nb_hits': len(d['scores']),
            'docs': d['docs']}
                for a, d in authors_agg_scores.items()]

        return self.sortAndRankResults(authors_agg_scores_r)


    def sortFilterAndFormatDocsResults(self, results, rank_metric, min_year=-1):

        filters = []
        if min_year > 0:
            filters = [lambda doc: doc.publication_year < int(min_year)]

        scores, filter_docs = self.filter_documents(results, filters)

        docs_agg_scores = dict()
        for score, doc in zip(scores, filter_docs):
            if not doc in docs_agg_scores:
                docs_agg_scores[doc] = {'scores': [], 'phrases': []}
            docs_agg_scores[doc]['scores'].append(score)
            docs_agg_scores[doc]['phrases'].append(doc.phrases)

        print(f"Corpus: Found {len(docs_agg_scores)} different documents.")

        docs_agg_scores_r = [{
            'rank_score': self.rankScores(values['scores'], rank_metric),
            'doc_scores': values['scores'],
            'doc_phrases': values['phrases'],
            'doc_median_score': np.median(values['scores']),
            'doc_mean_score': np.mean(values['scores']),
            'doc_max_score': np.max(values['scores']),
            'doc_min_score': np.min(values['scores']),
            'nb_hits': len(values['scores']),
            'doc': doc}
                for doc, values in docs_agg_scores.items()]

        return self.sortAndRankResults(docs_agg_scores_r)


    def retrieveAuthors(self, query, top_k, score_threshold, rank_metric, min_year=-1):
        return self.sortFilterAndFormatAuthorsResults(
            self.index.retrieve(query, top_k, score_threshold), rank_metric, min_year)

    def retrieveDocuments(self, query, top_k, score_threshold, rank_metric, min_year):
        return self.sortFilterAndFormatDocsResults(
            self.index.retrieve(query, top_k, score_threshold), rank_metric, min_year)

