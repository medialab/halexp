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

    def __init__(self, dump_path):

        self.parseDump(dump_path)
        self.extractInputData()

    def parseDump(self, data_path):
        """
        Parse data :)
        """

        print(f"Loading and parsing medialab HAL json dump ...")

        with open(data_path) as f:
            self.halData = json.load(f)

        print(f"found {len(self.halData)} entries.")


    def extractInputData(self):
        """
        Create input data for embeddings from dump
        """

        for hd in self.halData:
            try:
                self.embeddingData.append(hd["hal"]['meta']["abstract_s"][0])
            except Exception as e:
                pass

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
                    hd['hal']['meta']['citationFull_s'])
            })

        return res


