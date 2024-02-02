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
        index_path,
        hnswlib_space,
        ef_construction,
        num_threads,
        M,
        top_k,
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
        self.num_threads = num_threads
        self.index_path = index_path
        self.min_threshold_score = float(min_threshold_score)

        self.loadModel()

    def loadModel(self):
        self.model = SentenceTransformer(self.model_name)

    def encodeData(self, documents):
        """
        """

        bsize = 500
        tsize = len(documents)
        batchl = [
            (i*bsize, (i+1)*bsize) for i in range(int(tsize/bsize+1))]

        print(f"Embedding data...")
        start_time = time.time()
        self.embeddings = []
        for b in tqdm(batchl):
            batchDocs = documents[b[0]: b[1]]
            batch = [d.getPhrasesForEmbedding() for d in batchDocs]
            self.embeddings.extend(self.model.encode(batch))

        print("took {:.2f} seconds.".format(time.time()-start_time))
        self.embedding_size = self.embeddings[0].shape[0]
        self.index_length = tsize

    def createIndex(self, documents):
        """
        Creates a Hierarchical Navigable Small World graphs (HNSW) index
        containing the sentences embeddings.
        The HNSWLIB index uses dot-product as Index and normalize
        # vectors to unit length.

        """
        if not os.path.exists(self.index_path):
            self.encodeData(documents)

        # Declare index
        self.index = hnswlib.Index(
            space=self.space,
            dim=self.embedding_size)

        if os.path.exists(self.index_path):
            self.index.load_index(
                self.index_path,
                max_elements=len(self.embeddings))
            print(
                f"Index: index loaded from {self.index_path}: {self.index} th={self.min_threshold_score}")
            self.index_length = len(documents)

        else:
            self.index.init_index(
                max_elements=len(self.embeddings),
                ef_construction=400,
                M=64)
            self.index.set_num_threads(self.num_threads)
            print("Populating HNSWLIB index...")
            # Populate index with embeddings
            self.index.add_items(
                data=self.embeddings,
                ids=list(range(len(self.embeddings))))

            self.index.save_index(self.index_path)
            print(f"HNSWLIB index saved to {self.index_path}")


    def parseAndFilterResults(self, corpus_ids, distances):
        """
        Transform distances in scores, sort scores and filter query results.
        """
        parsed_results = [
            {'corpus_id': id, 'score': 1-distance}
                for id, distance in zip(corpus_ids[0], distances[0])
                    if 1-distance >= self.min_threshold_score
        ]

        return parsed_results


    def retrieve(self, query, top_k):

        top_k = top_k if top_k > 0 else self.index_length

        query_embedding = self.model.encode(query)

        # Use hnswlib knn_query method to get the closest embeddings
        start_time = time.time()
        corpus_ids, distances = self.index.knn_query(
            query_embedding, k=top_k)
        parsed_res = self.parseAndFilterResults(corpus_ids, distances)
        t = time.time() - start_time

        print(f"Index: retrieved {len(parsed_res)} results after {t:.5f} s.")

        return parsed_res