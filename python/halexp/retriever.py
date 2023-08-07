import re
import os
import time
import hnswlib

from .corpus import Corpus

from sentence_transformers import SentenceTransformer


class Retriever:
    """
    Class for retreiving things :)
    """

    halCorpus = None

    embeddings = []
    embedding_size = -1
    model_name = 'distiluse-base-multilingual-cased-v1'

    index_path = "./hnswlib.index"
    space = 'cosine'
    index = None

    def __init__(self, data_path):

        self.halCorpus = Corpus(data_path)
        self.loadModel()
        self.encodeData()
        self.createIndex()

    def loadModel(self):
        """
        """
        print(f"Loading embedding model...")
        self.model = SentenceTransformer(self.model_name)
        print(f"done.")

    def encodeData(self):
        """
        """
        print(f"Embedding data...")
        start_time = time.time()
        self.embeddings = self.model.encode(self.halCorpus.embeddingData)
        print("took {:.2f} seconds.".format(time.time()-start_time))
        self.embedding_size = self.embeddings[0].shape[0]

    def createIndex(self):
        """
        """
        # Defining hnswlib index using dot-product as Index and normalize
        # vectors to unit length.
        self.index = hnswlib.Index(space=self.space, dim=self.embedding_size)

        if os.path.exists(self.index_path):
            print("Loading index...")
            self.index.load_index(self.index_path)
        else:
            # Create the HNSWLIB index
            print("Start creating HNSWLIB index")
            self.index.init_index(
                max_elements=len(self.embeddings), ef_construction=400, M=64)

            # Train the index to find a suitable clustering
            self.index.add_items(
                self.embeddings, list(range(len(self.embeddings))))

            print(f"Saving index to {self.index_path}")
            self.index.save_index(self.index_path)


    def retrieve(self, query, top_k):

        query_embedding = self.model.encode(query)

        start_time = time.time()

        # Use hnswlib knn_query method to get the closest embeddings
        corpus_ids, distances = self.index.knn_query(query_embedding, k=top_k)

        # Parse and sort results
        parsed_results = [
            {'corpus_id': id, 'score': 1-score}
            for id, score in zip(corpus_ids[0], distances[0])]
        sorted_results = sorted(
            parsed_results,
            key=lambda x: x['score'],
            reverse=True)

        end_time = time.time()

        print(f"Input question:\n{query}")
        print(f"Results (after {end_time-start_time:.3f} seconds).")

        results = sorted_results[:top_k]

        return self.halCorpus.parseAndFormatResults(results)
