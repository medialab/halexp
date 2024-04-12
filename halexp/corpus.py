import re
import json
from tqdm import tqdm
import numpy as np
import nltk.data

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

    def __init__(
            self,
            index,
            dump_file,
            max_length,
            use_keys,
            min_num_characters,
            **kwargs):
        """
        dump_file[str]: path to the HAL dump in json format.

        max_length [int]: maximum lenght of the serie of phrases of each doc.

        use_keys [dict]: wheter to include or not the title, subtirle,
        author and keywords of HAL document in the text to be embedded.
        """

        self.nlp_loaded = False

        self.index = index

        self.documents = []
        self.nb_documents = 0
        self.halIds = set([])

        self.doc_max_length = max_length
        self.include = use_keys
        self.minNbCharacters = min_num_characters

        self.loadDump(dump_file)
        self.createDocuments()

        self.index.createIndex(self.documents)


    def checkAndReplaceMissingMetadata(
        self,
        key,
        drop=False,
        replace_value=''):

        nb_missing = 0
        nb_dropped = 0
        for n, hd in enumerate(self.halData):
            if not key in hd:
                if drop:
                    self.halData.pop(n)
                    nb_dropped += 1
                else:
                    replace = [replace_value,]
                    hd[key] = replace
                    nb_missing += 1

        if nb_missing > 0:
            mssg = f"Corpus: Found {nb_missing} HAL docs out of "
            mssg += f"{len(self.halData)} "
            mssg += f"({100 * nb_missing / len(self.halData):.2f}%) "
            mssg += f"without `{key}` entry."
            print(mssg)

        if nb_dropped > 0:
            mssg = f"Corpus: Dropped {nb_dropped} HAL docs out of "
            mssg += f"{len(self.halData)} "
            mssg += f"({100 * nb_dropped / len(self.halData):.2f}%) "
            mssg += f"without `{key}` entry."
            print(mssg)

    def loadDump(self, dump_file):

        with open(dump_file) as f:
            self.halData = json.load(f)

        # check if duplicated hal ids
        nb_unique_halId = len(set([hd['halId_s'] for hd in self.halData]))
        if not nb_unique_halId == len(self.halData):
            raise ValueError(
                f"There are documents in dump with repeated 'halId_s' key.")

        print(
            f"Corpus: found {len(self.halData)} unique entries from json dump.")

        self.checkAndReplaceMissingMetadata('keyword_s', '')
        self.checkAndReplaceMissingMetadata('title_s', '')
        self.checkAndReplaceMissingMetadata('subtitle_s', '')
        self.checkAndReplaceMissingMetadata(
            'authIdHasPrimaryStructure_fs', drop=True)

    def loadNlp(self):
        self.sentenes_splitter =  nltk.data.load(
            'tokenizers/punkt/english.pickle')
        self.nlp_loaded = True

    def split(self, text):
        """
        Apply strategy for splitting phrases from a text.
        """
        if not self.nlp_loaded:
            self.loadNlp()

        splitted = self.sentenes_splitter.tokenize(text.strip())

        return splitted

    def parseStructure(self, authFullNameId_fs, authIdHasPrimaryStructure_fs):
        """
        Parse author metadata.

        Each entry in authIdHasPrimaryStructure_fs is a string containing :

        Internal identifier + _FacetSep_ + Full name + _JoinSep_ +
        Identifiant HAL de structure primaire + _FacetSep_ +
        Nom de la structure primaire
        """

        # build author data dict
        authorsData = {
            authFullNameId: {
                'authId_i': -1,
                'authFullName_s': "Not found",
                'authPrimStrucId': [],
                'authPrimStrucName': [],
            }
            for authFullNameId in authFullNameId_fs
        }

        for joint in authIdHasPrimaryStructure_fs:

            # get data
            f1, f2 = joint.split('_JoinSep_')
            internalId, fullName = f1.split('_FacetSep_')
            primaryStrucId, primaryStrucName = f2.split('_FacetSep_')
            _, authId_i = internalId.split('-')

            # reconstruct author id (full name+ hal id)
            authFullNameId = '_FacetSep_'.join([fullName, authId_i])

            # fill author data dict
            authorsData[authFullNameId]['authId_i'] = authId_i
            authorsData[authFullNameId]['authFullName_s'] = fullName
            authorsData[authFullNameId]['authPrimStrucId'].append(
                primaryStrucId)
            authorsData[authFullNameId]['authPrimStrucName'].append(
                primaryStrucName)

        # drop authors without hal id
        authorsData = {
            k: v for k, v in authorsData.items() if not v['authId_i'] == -1}

        return authorsData

    def createDocument(self, hd, phrases):

        phrases_ok = self.getValidLengthPhrases(phrases)
        if len(phrases_ok) == 0:
            jp = ','.join([f" `{p}`" for p in phrases])
            print(f"Removing document with too short phrases:{jp}.")
            return None
        phrases = phrases_ok

        document = Document(phrases, self.doc_max_length)
        document.setMetadata(hd)
        document.setAuthors(self.parseStructure(
            hd["authFullNameId_fs"],
            hd["authIdHasPrimaryStructure_fs"]))
        document.setPublicationDate(hd["publicationDate_s"])
        document.setUri(hd["uri_s"])
        document.setHalId(hd["halId_s"])
        document.setOpenAccess(hd["openAccess_bool"])
        document.setTitle(hd["title_s"][0])
        document.setKeywords(hd["keyword_s"])
        document.setSubtitle(hd["subtitle_s"])

        return document

    def getValidLengthPhrases(self, phrases):
        return [p for p in phrases if len(p) > self.minNbCharacters]

    def hasValidAbstracts(self, hd):
        if "abstract_s" not in hd:
            return False
        else:
            abstract = hd["abstract_s"]
            if abstract in self.invalidAbstracts or len(abstract) == 0:
                return False
        return True


    def addDocument(self, document):
        if document is not None:
            self.documents.append(document)

    def createDocuments(self):
        """
        Create documents from dump data
        """

        for hd in self.halData:

            # create docs from metadata
            if self.include['keywords'] and hd['keyword_s'][0]:
                self.addDocument(
                    self.createDocument(hd, [' '.join(hd['keyword_s'])]))
            if self.include['title'] and hd['title_s']:
                self.addDocument(
                    self.createDocument(hd, hd['title_s']))
            if self.include['subtitle'] and hd['subtitle_s'][0]:
                self.addDocument(
                    self.createDocument(hd, hd['subtitle_s']))
        nb_docs = len(self.documents)
        print(f"Corpus: {nb_docs} documents created from metadata.")

        if self.include['abstract']:
            print("Corpus: splitting sentences from abstracts.")
            for hd in tqdm(self.halData):
                # create docs with phrases
                if self.hasValidAbstracts(hd):
                    sentences = self.split(hd["abstract_s"][0])
                    na = 0
                    nb = 0
                    while na < len(sentences)-1:
                        nb += min(self.doc_max_length, len(sentences)-nb)
                        document = self.createDocument(hd, sentences[na: nb])
                        na = nb
                        self.addDocument(document)
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
        elif rank_metric == 'sigmoid-mean':
            return  1/(1+np.exp(-0.5 * len(scores))) * np.mean(scores)
        elif rank_metric == 'sigmoid':
            return np.mean(1/(1+np.exp(-0.5 * np.array(scores))) * np.array(scores))
        else:
            rms = ['mean', 'median', 'log-mean', 'sigmoid-mean', 'sigmoid']
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
            'nb_hits': len(d['scores']),
            'docs': d['docs']
        } for a, d in authors_agg_scores.items()]

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
            'nb_hits': len(values['scores']),
            'metadata': doc.metadata,
            'doc': doc
            }
                for doc, values in docs_agg_scores.items()]

        return self.sortAndRankResults(docs_agg_scores_r)


    def retrieveAuthors(self, query, top_k, score_threshold, rank_metric, min_year=-1):
        return self.sortFilterAndFormatAuthorsResults(
            self.index.retrieve(query, top_k, score_threshold),
            rank_metric,
            min_year)

    def retrieveDocuments(self, query, top_k, score_threshold, rank_metric, min_year):
        return self.sortFilterAndFormatDocsResults(
            self.index.retrieve(query, top_k, score_threshold),
            rank_metric,
            min_year)
