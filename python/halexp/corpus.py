import re
import json
from tqdm import tqdm

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
        dump_file,
        max_length,
        include_title,
        include_author,
        include_keywords,
        include_subtitle,
        filters,
        **kwargs):
        """
        dump_file[str]: path to the HAL dump in json format.

        max_length [int]: maximum lenght of the serie of phrases of each doc.

        include_title [boolean]: wheter to include or not the title of HAL
        document in the text to be embedded.

        include_author [boolean]: wheter to include or not the author
        (first name and last name) of HAL document in the text to be embedded.

        include_keywords [boolean]: wheter to include or not the keywords of
        the HAL document in the text to be embedded.
        """

        self.documents = []
        self.filters = []
        self.max_length = -1
        self.nb_documents = 0
        self.halIds = set([])

        self.doc_max_length = max_length
        self.include_title = include_title
        self.include_author = include_author
        self.include_keywords = include_keywords
        self.include_subtitle = include_subtitle
        self.loadDump(dump_file)
        self.createDocuments()
        self.createDocFilters(filters)

        exit()

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

        self.checkAndReplaceMissingMetadata('keyword_s')
        self.checkAndReplaceMissingMetadata('labStructName_s')
        self.checkAndReplaceMissingMetadata(
            'authIdHal_i', replace_nb_key='authFullName_s')

    def split(self, string):
        "Apply strategy for splitting phrases from a string."
        return string.split('.')

    def createDocument(self, hd):
        document = Document(
            self.doc_max_length,
            self.include_title,
            self.include_author,
            self.include_keywords,
            self.include_subtitle
        )
        document.setMetadata(hd)
        document.setTitle(hd["title_s"][0])
        if not 'labStructName_s' in hd:
            hd["labStructName_s"] = "NOT FOUND"
        document.setAuthors(
            hd["authFullName_s"], hd["authIdHal_i"], hd["labStructName_s"])
        document.setPublicationDate(hd["publicationDate_s"])
        document.setUri(hd["uri_s"])
        document.setHalId(hd["halId_s"])
        document.setOpenAccess(hd["openAccess_bool"])
        document.setKeywords(hd["keyword_s"])
        if 'subtitle_s' in hd:
            document.setSubtitle(hd["subtitle_s"])

        return document

    def sepatedValidAbstracts(self):

        with_valid_abstract = []
        without_valid_abstract = []

        for hd in self.halData:
            if "abstract_s" not in hd:
                without_valid_abstract.append(hd)
            else:
                abstract = hd["abstract_s"]
                if abstract in self.invalidAbstracts or len(abstract) == 0:
                    without_valid_abstract.append(hd)
                else:
                    with_valid_abstract.append(hd)

        la = len(with_valid_abstract)
        lna = len(without_valid_abstract)
        assert  la + lna == len(self.halData)

        print(f"Found {la} entries with valid abstract.")
        print(f"Found {lna} entries without valid abstract.")

        return with_valid_abstract, without_valid_abstract


    def createDocuments(self):
        """
        Create input data for embeddings from dump
        """
        print(f"Extracting data... ")

        with_valid_abstract, without_valid_abstract = \
            self.sepatedValidAbstracts()

        # create docs without phrases and add it to corpus
        for hd in tqdm(without_valid_abstract):
            self.documents.append(self.createDocument(hd))

        # create docs with phrases and add it to corpus
        for hd in tqdm(with_valid_abstract):

            sentences = self.split(hd["abstract_s"][0])
            n = 0
            while n < len(sentences)-1:
                # create doc
                document = self.createDocument(hd)
                # add phrases
                r = min(self.doc_max_length, len(sentences)-n)
                for i in range(r):
                    document.add_phrase(sentences[n])
                    n += 1
                # add doc to corpus
                self.documents.append(document)

        self.nb_documents = len(self.documents)
        print(f"Create {self.nb_documents} documents in Corpus.")


    def filter_documents(self, doc):
        return any([f(doc) for f in self.filters])


    def formatResults(self, results):

        corpus_ids = [r['corpus_id'] for r in results]
        scores = [r['score'] for r in results]

        res = {
            "citation": [],
            "json": []

        }

        for i, idx in enumerate(corpus_ids):

            document = self.documents[idx]
            if self.filter_documents(document):
                continue

            score = scores[i]

            res["json"].append({
                'score': score,
                'data': document.metadata
            })

            res["citation"].append({
                'score': score,
                "citation": remove_html_tags(
                    document.metadata['citationFull_s']),
                "embedded": document.getPhrasesForEmbedding(),
                "hal_id": document.hal_id,
            })

        return res


