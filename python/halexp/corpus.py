import re
import json
from tqdm import tqdm
import numpy as np

from .document import Document
from .utils import split_into_sentences

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

    def __init__(self, dump_file, max_length, use_keys, filters, **kwargs):
        """
        dump_file[str]: path to the HAL dump in json format.

        max_length [int]: maximum lenght of the serie of phrases of each doc.

        use_keys [dict]: wheter to include or not the title, subtirle,
        author and keywords of HAL document in the text to be embedded.
        """

        self.documents = []
        self.filters = []
        self.max_length = -1
        self.nb_documents = 0
        self.halIds = set([])

        self.doc_max_length = max_length
        self.include = use_keys

        self.loadDump(dump_file)
        self.createDocuments()
        self.createDocFilters(filters)

    def createDocFilters(self, filters):
        """
        Each filter returs True if the document must be filtered.
        """
        if 'minYear' in filters:
            fn = lambda doc: doc.publication_year < int(filters['minYear'])
            self.filters.append(fn)


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
            mssg = f"Found {nb_missing} HAL docs out of "
            mssg += f"{len(self.halData)} "
            mssg += f"({100 * nb_missing / len(self.halData):.2f}%) "
            mssg += f"without `{key}` entry."
            print(mssg)

    def loadDump(self, dump_file):

        print(f"Loading HAL json dump... ")

        with open(dump_file) as f:
            self.halData = json.load(f)

        # check if duplicated hal ids
        nb_unique_halId_s = len(set([hd['halId_s'] for hd in self.halData]))
        if not nb_unique_halId_s == len(self.halData):
            raise ValueError(
                f"There are documents in dump with repeated 'halId_s' key.")

        print(f"found {len(self.halData)} unique entries.")

        self.checkAndReplaceMissingMetadata('keyword_s', '')
        self.checkAndReplaceMissingMetadata('title_s', '')
        self.checkAndReplaceMissingMetadata('subtitle_s', '')
        self.checkAndReplaceMissingMetadata(
            'labStructName_s', replace_value='NOT FOUND')
        self.checkAndReplaceMissingMetadata(
            'authIdHal_i', replace_nb_key='authFullName_s')

    def split(self, string):
        """
        Apply strategy for splitting phrases from a string.
        """
        splited = [s for s in string.split('.') if s != '']
        splited = [s[1:] if s.startswith(' ') else s for s in splited]
        splited = [s+'.' if not s.endswith('.') else s for s in splited]
        # from nltk.tokenize import sent_tokenize
        # splited = self.split_into_sentences(string)
        return splited

    def createDocument(self, hd, phrases):
        document = Document(phrases)
        document.setMetadata(hd)
        document.setAuthors(
            hd["authFullName_s"], hd["authIdHal_i"], hd["labStructName_s"])
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
        print(f"{nb_docs} documents created from metadata.")

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
        print(f"{self.nb_documents - nb_docs} documents from valid abstracts.")

    def filter_documents(self, doc):
        return any([f(doc) for f in self.filters])

    def formatResults(self, results):

        filtered_docs = []
        scores = []
        for r in results:
            document = self.documents[r['corpus_id']]
            if self.filter_documents(document):
                continue
            filtered_docs.append(document)
            scores.append(r['score'])

        authors_agg_scores = dict()
        for score, doc in zip(scores, filtered_docs):
            for author in doc.getAuthors():
                if not author in authors_agg_scores:
                    authors_agg_scores[author] = {'scores': [], 'docs': []}
                authors_agg_scores[author]['scores'].append(score)
                authors_agg_scores[author]['docs'].append(doc)

        authors_agg_scores_r = [{
            'author': a,
            'score': np.log(len(d['scores'])) * np.mean(d['scores']),
            'docs_scores': d['scores'],
            'docs_median_score': np.median(d['scores']),
            'docs_mean_score': np.mean(d['scores']),
            'docs_max_score': np.max(d['scores']),
            'docs_min_score': np.min(d['scores']),
            'nb_hits': len(d['scores']),
            'docs': d['docs']}
                for a, d in authors_agg_scores.items()]

        sorted_results = sorted(
            authors_agg_scores_r,
            key=lambda x: x['score'],
            reverse=True)

        for k, sr in enumerate(sorted_results):
            sr.update({'rank': k})

        res = {
            "citation": sorted_results,
            "json": sorted_results
        }

        # res = {
        #     "citation": [],
        #     "json": []

        # }

        # for sr in sorted_results:

        #     score = sr['mean_score']

        #     res["json"].append({
        #         'score': score,
        #         'data': document.metadata
        #     })

        #     res["citation"].append({
        #         'score': score,
        #         "citation": remove_html_tags(
        #             document.metadata['citationFull_s']),
        #         "embedded": document.getPhrasesForEmbedding(),
        #         "hal_id": document.hal_id,
        #     })

        return res


