import os
import time
import hnswlib
from tqdm import tqdm

from sentence_transformers import SentenceTransformer


class Index:
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

    def __init__(
        self, corpus, sentence_transformer_model, hnswlib_space, **kwargs):

        self.model_name = sentence_transformer_model
        self.space = hnswlib_space

        self.halCorpus = corpus
        self.loadModel()
        self.encodeData()
        self.createIndex()

    def loadModel(self):
        """
        """
        self.model = SentenceTransformer(self.model_name)

    def encodeData(self):
        """
        """

        bsize = 500
        tsize = len(self.halCorpus.embeddingData)
        batchl = [
            (i*bsize, (i+1)*bsize) for i in range(int(tsize/bsize+1))]

        print(f"Embedding data...")
        start_time = time.time()
        self.embeddings = []
        for b in tqdm(batchl):
            batch = self.halCorpus.embeddingData[b[0]: b[1]]
            self.embeddings.extend(self.model.encode(batch))

        print("took {:.2f} seconds.".format(time.time()-start_time))
        self.embedding_size = self.embeddings[0].shape[0]

    def createIndex(self):
        """
        Creates a Hierarchical Navigable Small World graphs (HNSW) index
        containing the sentences embeddings.
        The HNSWLIB index uses dot-product as Index and normalize
        # vectors to unit length.

        """
        self.index = hnswlib.Index(space=self.space, dim=self.embedding_size)

        if os.path.exists(self.index_path):
            print("Loading index...")
            self.index.load_index(self.index_path)
        else:
            print("Start creating HNSWLIB index")
            self.index.init_index(
                max_elements=len(self.embeddings), ef_construction=400, M=64)

            # Populate index with embeddings
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
