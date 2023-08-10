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

    embeddingData = []

    def __init__(self, dump_file, **kwargs):

        self.parseDump(dump_file)
        self.extractInputData()

    def parseDump(self, dump_file):
        """
        Parse data :)
        """

        print(f"Loading and parsing medialab HAL json dump ...  ")

        with open(dump_file) as f:
            self.halData = json.load(f)

        print(f"found {len(self.halData)} entries.")


    def extractInputData(self):
        """
        Create input data for embeddings from dump
        """

        for hd in self.halData:
            sentence = ""
            if "abstract_s" in hd:
                sentence += hd["abstract_s"][0]
            else:
                pass
            if "title_s" in hd:
                sentence += hd["title_s"][0]
            if "authFirstName_s" in hd:
                sentence += hd["authFirstName_s"][0]
            if "authLastName_s" in hd:
                sentence += hd["authLastName_s"][0]
            self.embeddingData.append(sentence)
        print(f"Found {len(self.embeddingData)} entries with `abstract_s`.")

    def parseAndFormatResults(self, results):

        corpus_ids = [r['corpus_id'] for r in results]
        scores = [r['score'] for r in results]

        res = {
            "citation": [],
            "json": []

        }

        for i, idx in enumerate(corpus_ids):

            hd = self.halData[idx]
            score = scores[i]

            res["json"].append({
                'score': score,
                'data': hd
            })

            res["citation"].append({
                'score': score,
                "citation": remove_html_tags(
                    hd['citationFull_s'])
            })

        return res


