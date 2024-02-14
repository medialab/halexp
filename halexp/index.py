import os
import time
import hnswlib
from tqdm import tqdm

from sentence_transformers import SentenceTransformer


def setIndexPath(params):
    indexPath = f"{params['corpus']['portail']}_"
    indexPath += f"{params['corpus']['query']}_"
    indexPath += f"max_length_{params['corpus']['max_length']}"
    if params['corpus']['use_keys']['title']:
        indexPath += f"_title"
    if params['corpus']['use_keys']['abstract']:
        indexPath += f"_abstract"
    if params['corpus']['use_keys']['subtitle']:
        indexPath += f"_subtitle"
    if params['corpus']['use_keys']['keywords']:
        indexPath += f"_keywords"
    indexPath = os.path.join('index', indexPath.replace('*:*', 'xxx')+'.index')
    return indexPath


class Index:
    """
    This class index the phrases of a corpus documents using a sentence bert
    model and Hierarchical Navigable Small World graphs (HNSW).
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
        batch_size,
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

        self.length = -1
        self.space = hnswlib_space
        self.num_threads = num_threads
        self.path = index_path
        self.indexKwargs = {'M': M, 'ef_construction': ef_construction}

        self.batch_size = batch_size

        self.loadModel()

    def __str__(self):
        _str = f"HNSW index: embedding_size {self.embedding_size}"
        _str += f" | length {self.length}"
        return _str

    def loadModel(self):
        self.model = SentenceTransformer(self.model_name)

    def embedData(self, documents):
        bsize = self.batch_size
        tsize = len(documents)
        batchl = [
            (i*bsize, (i+1)*bsize) for i in range(int(tsize/bsize+1))]

        print(f"Index: embedding data for {len(documents)} documents...")
        start_time = time.time()
        self.embeddings = []
        for b in tqdm(batchl):
            batchDocs = documents[b[0]: b[1]]
            batch = [d.getPhrasesForEmbedding() for d in batchDocs]
            self.embeddings.extend(self.model.encode(batch))

        print("Index: took {:.2f} seconds.".format(time.time()-start_time))

    def createIndex(self, documents):
        """
        Creates a Hierarchical Navigable Small World graphs (HNSW) index
        containing the sentences embeddings.
        The HNSWLIB index uses dot-product as Index and normalize
        # vectors to unit length.
        """
        self.length = len(documents)

        # Declare index
        self.index = hnswlib.Index(
            space=self.space,
            dim=self.embedding_size)

        # load index and check its coherence
        if os.path.exists(self.path):
            self.index.load_index(self.path, max_elements=self.length)
            print(f"Index: index loaded from {self.path}.\n{self}")
            a1 = self.embedding_size == self.index.dim
            a2 = self.space == self.index.space
            if not a1 and a2:
                raise ValueError(f"Index loaded not coherent with parameters.")
            self.index.set_num_threads(self.num_threads)
        # init index and populate it with embeddings
        else:
            self.embedData(documents)
            self.index.init_index(max_elements=self.length, **self.indexKwargs)
            self.index.set_num_threads(self.num_threads)
            print("Index: populating HNSWLIB index...")
            self.index.add_items(
                data=self.embeddings, ids=list(range(self.length)))
            self.index.save_index(self.path)
            print(f"Index: HNSW index saved to {self.path}\n{self}")


    def parseAndFilterResults(self, corpus_ids, distances, score_threshold):
        """
        Transform distances in scores, sort scores and filter query results.
        """
        parsed_results = [
            {'corpus_id': id, 'score': 1-distance}
                for id, distance in zip(corpus_ids[0], distances[0])
                    if 1-distance >= score_threshold
        ]

        return parsed_results


    def retrieve(self, query, top_k, score_threshold):

        # top_k = top_k if top_k > 0 else min(self.length, 10000)

        query_embedding = self.model.encode(query)

        # Use hnswlib knn_query method to get the closest embeddings
        start_time = time.time()

        corpus_ids, distances = self.index.knn_query(
            query_embedding, k=top_k)
        parsed_res = self.parseAndFilterResults(
            corpus_ids, distances, score_threshold)
        t = time.time() - start_time

        print(f"Index: retrieved {len(parsed_res)} results after {t:.5f} s.")

        return parsed_res
