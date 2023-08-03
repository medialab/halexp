import re
import os
import json
import time
import hnswlib
from sentence_transformers import SentenceTransformer


def remove_html_tags(text):
    """Remove html tags from a string"""
    text = re.sub('<a .*?</a>', '', text)
    text = re.sub('<i .*?</i>', '', text)
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


class Retriever:
    """
    Class for retreiving ...
    """

    corpus = []
    citations = []
    abstracts = []

    embeddings = []
    embedding_size = -1

    index_path = "./hnswlib.index"
    space = 'cosine'
    index = None
    top_k_hits = -1

    def __init__(self, data_path='hal-productions.json', rebuild=False):

        self.data_path = data_path
        self.parseData()
        self.loadSbertModel()
        self.encodeData()
        self.createIndex()

    def parseData(self):
        """
        """

        print(f"Loading and parsing medialab HAL json dump...")

        with open(self.data_path) as f:
            halData = json.load(f)

        print(f"Found {len(halData)} entries in Medialab HAL json dump.")

        for hd in halData:
            try:
                self.corpus.append([
                    hd["hal"]['meta']["citationFull_s"],
                    hd["hal"]['meta']["abstract_s"]]
                )
            except Exception as e:
                pass
        lc = len(self.corpus)
        print(f"Found {lc} entries with `abstract_s` and `citationFull_s`.")

        self.citations = [doc[0] for doc in self.corpus]
        self.citations = [remove_html_tags(c) for c in self.citations]
        self.abstracts = [doc[1][0] for doc in self.corpus]

    def loadSbertModel(self):
        """
        """
        self.model = SentenceTransformer('distiluse-base-multilingual-cased-v1')

    def encodeData(self):
        """
        """
        self.embeddings = self.model.encode(abstracts)
        self.embedding_size = embeddings[0].shape[0]

    def createIndex(self):
        """
        """

        # Defining our hnswlib index

        # We use Inner Product (dot-product) as Index.
        # We will normalize our vectors to unit length.
        self.index = hnswlib.Index(space=self.space, dim=self.embedding_size)

        if os.path.exists(self.index_path):
            print("Loading index...")
            self.index.load_index(self.index_path)
        else:
            # Create the HNSWLIB index
            print("Start creating HNSWLIB index")
            self.index.init_index(
                max_elements=len(self.embeddings), ef_construction=400, M=64)

            # Then we train the index to find a suitable clustering
            self.index.add_items(
                self.embeddings, list(range(len(self.embeddings))))

            print(f"Saving index to {self.index_path}")
            self.index.save_index(self.index_path)



    def retrieve(self, inp_question):

        question_embedding = self.model.encode(inp_question)

        start_time = time.time()

        # We use hnswlib knn_query method to find the top_k_hits
        corpus_ids, distances = self.index.knn_query(
            question_embedding, k=top_k_hits)

        # We extract corpus ids and scores for the first query
        hits = [
            {'corpus_id': id, 'score': 1-score}
            for id, score in zip(corpus_ids[0], distances[0])]
        hits = sorted(hits, key=lambda x: x['score'], reverse=True)
        end_time = time.time()

        print("Input question:", inp_question)
        print("Results (after {:.3f} seconds):".format(end_time-start_time))

        for hit in hits[0:top_k_hits]:
            print(f"\t{hit['score']:.3f}\t{citations[hit['corpus_id']]}")

        return {
            n: {
                'score': hits[n]['score'],
                'text': citations[hits[n]['corpus_id']]
            }
            for n in range(top_k_hits)
        }

