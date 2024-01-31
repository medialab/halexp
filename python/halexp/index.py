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
    embedding_size = 512
    model_name = 'distiluse-base-multilingual-cased-v1'

    space = 'cosine'
    index = None

    def __init__(
        self,
        corpus,
        index_path,
        hnswlib_space,
        ef_construction,
        M,
        min_threshold_score,
        sentence_transformer_model,
        sentence_transformer_model_dim,
        **kwargs):

        """
        ef_construction - controls index search speed/build speed tradeoff
        higher ef leads to better accuracy, but slower search

        M - is tightly connected with internal dimensionality of the data.
        Strongly affects memory consumption (~M)
        Higher M leads to higher accuracy/run_time at fixed ef/efConstruction
        """

        self.model_name = sentence_transformer_model
        self.embedding_size = sentence_transformer_model_dim
        self.space = hnswlib_space
        self.index_path = f"./index/{index_path}_hnswlib.index"
        self.min_threshold_score = float(min_threshold_score)

        self.loadModel()

        self.halCorpus = corpus
        self.courpus_length = self.halCorpus.nb_documents
        self.createIndex()

    def loadModel(self):
        """
        """
        self.model = SentenceTransformer(self.model_name)

    def encodeData(self):
        """
        """

        bsize = 500
        tsize = self.courpus_length
        batchl = [
            (i*bsize, (i+1)*bsize) for i in range(int(tsize/bsize+1))]

        print(f"Embedding data...")
        start_time = time.time()
        self.embeddings = []
        for b in tqdm(batchl):
            batchDocs = self.halCorpus.documents[b[0]: b[1]]
            batch = [d.getPhrasesForEmbedding() for d in batchDocs]
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

        if not os.path.exists(self.index_path):
            self.encodeData()

        # Declare index
        self.index = hnswlib.Index(
            space=self.space,
            dim=self.embedding_size)

        if os.path.exists(self.index_path):
            self.index.load_index(
                self.index_path,
                max_elements=len(self.embeddings))
            print(f"HNSWLIB index loaded from {self.index_path}...")
            print(self.index)
        else:
            self.index.init_index(
                max_elements=len(self.embeddings),
                ef_construction=400,
                M=64)
            self.index.set_num_threads(1)
            print("Populating HNSWLIB index...")
            # Populate index with embeddings
            self.index.add_items(
                data=self.embeddings,
                ids=list(range(len(self.embeddings))))

            self.index.save_index(self.index_path)
            print(f"HNSWLIB index saved to {self.index_path}")


    def rank(self, query):

        query_embedding = self.model.encode(query)

        start_time = time.time()

        # Use hnswlib knn_query method to get the closest embeddings
        corpus_ids, distances = self.index.knn_query(
            query_embedding, k=self.courpus_length)

        # Parse and sort results
        parsed_results = [
            {'corpus_id': id, 'score': 1-score}
            for id, score in zip(corpus_ids[0], distances[0])
            if 1-score >= self.min_threshold_score]
        sorted_results = sorted(
            parsed_results,
            key=lambda x: x['score'],
            reverse=True)

        end_time = time.time()

        print(f"Input question:\n{query}")
        print(f"Index ranked (after {end_time-start_time:.3f} seconds).")

        return self.halCorpus.parseAndFormatResults(sorted_results)


    def retrieve(self, query, top_k):

        query_embedding = self.model.encode(query)

        start_time = time.time()

        # Use hnswlib knn_query method to get the closest embeddings
        corpus_ids, distances = self.index.knn_query(query_embedding, k=top_k)

        # Parse and sort results
        parsed_results = [
            {'corpus_id': id, 'score': 1-score}
            for id, score in zip(corpus_ids[0], distances[0])
            if 1-score >= self.min_threshold_score]
        sorted_results = sorted(
            parsed_results,
            key=lambda x: x['score'],
            reverse=True)

        end_time = time.time()

        print(f"Input question:\n{query}")
        print(f"Results (after {end_time-start_time:.3f} seconds).")

        results = sorted_results[:top_k]

        return self.halCorpus.parseAndFormatResults(results)
