import re
import json


def remove_html_tags(text):
    """Remove html tags from a string"""
    text = re.sub('<a .*?</a>', '', text)
    text = re.sub('<i .*?</i>', '', text)
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


class Corpus:
    """
    The corpus :)
    """

    embeddingData = None
    halData = None
    halDump = None

    def __init__(self, dump_file, **kwargs):

        self.parseDump(dump_file)
        self.extractInputData()

    def parseDump(self, dump_file):
        """
        Parse data :)
        """

        print(f"Loading and parsing HAL json dump ...  ")

        with open(dump_file) as f:
            self.halDump = json.load(f)

        print(f"found {len(self.halDump)} entries.")

    # def extractInputData(self):
    #     """
    #     Create input data for embeddings from dump
    #     """

    #     noAbstractCount = 0
    #     self.embeddingData = [ ]
    #     for hd in self.halDump:
    #         sentence = ""
    #         if "abstract_s" in hd:
    #             sentence += hd["abstract_s"][0]
    #         else:
    #             noAbstractCount += 1
    #             continue
    #         if "title_s" in hd:
    #             sentence += hd["title_s"][0]
    #         if "authFirstName_s" in hd:
    #             sentence += hd["authFirstName_s"][0]
    #         if "authLastName_s" in hd:
    #             sentence += hd["authLastName_s"][0]
    #         self.embeddingData.append(sentence)

    #     n = len(self.embeddingData)
    #     print(f"Found {n} entries with `abstract_s`. Ignored {noAbstractCount}")

    def extractInputData(self):
        """
        Create input data for embeddings from dump
        """

        # first extract all available authors
        authors = set()
        for hd in self.halDump:
            #  ignore entries with no authors names
            try:
                authFirstName_s = hd["authFirstName_s"]
                authLastName_s = hd["authLastName_s"]
                for firstName, lastName in zip(authFirstName_s, authLastName_s):
                    author = "|".join([firstName, lastName])
                    authors.add(author)
            except:
                pass
        authors = list(authors)

        # create list of sentences
        print(f"Found {len(authors)} different authors in dump.")
        self.embeddingData = [''] * len(authors)

        # extract now data to create a concatenated sentence for each author
        ac = 0
        nac = 0
        for doc in self.halDump:

            #  ignore entries with no abstract and title
            try:
                abstract_s = doc["abstract_s"][0]
                ac += 1
            except:
                nac += 1
                continue

            title_s = doc["title_s"][0]
            authFirstName_s = doc["authFirstName_s"]
            authLastName_s = doc["authLastName_s"]

            for firstName, lastName in zip(authFirstName_s, authLastName_s):
                author = "|".join([firstName, lastName])
                idx = authors.index(author)
                self.embeddingData[idx] += title_s
                self.embeddingData[idx] += ' '
                self.embeddingData[idx] += abstract_s

        # remove authos with empty sentences, this happend if the author is only
        # present in documents withput abstract
        idxOk = [i for i, e in enumerate(self.embeddingData) if e != '']
        self.embeddingData = [self.embeddingData[i] for i in idxOk]
        self.halData = [authors[i] for i in idxOk]

        n = len(self.embeddingData)
        print(f"Found {ac} entries with `abstract_s`, ignored {nac}.")
        print(f"Found {n} different authors in documents with abstracts.")

    def parseAndFormatResults(self, results):

        # scores are the distances between query and the results retrieved
        # corpus_ids are the ids of the result retrieved in the index
        corpus_ids = [r['corpus_id'] for r in results]
        scores = [r['score'] for r in results]

        # json contains original hal data of the result retrieved and scores
        # citations contains string to be showed of the result retrieved and scores
        res = {
            "citation": [],
            "json": []

        }

        for i, idx in enumerate(corpus_ids):

            # get original hal data of the result retrieved
            haldata = self.halData[idx]
            sentence = self.embeddingData[idx]
            score = scores[i]

            res["json"].append({
                'score': score,
                'data': haldata
            })

            res["citation"].append({
                'score': score,
                "citation": haldata + ' : ' + sentence
            })

        return res


