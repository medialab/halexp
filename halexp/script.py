import re
import os
import json
import time
import hnswlib
from sentence_transformers import SentenceTransformer, util


# https://github.com/nmslib/hnswlib/
# https://www.sbert.net/examples/applications/retrieve_rerank/README.html
# https://www.sbert.net/examples/applications/semantic-search/README.html

# (0) load and parse medialab's / HAL data

print(f"Loading and parsing medialab HAL json dump...")

with open('hal-productions.json') as f:
    halData = json.load(f)

halData_l = len(halData)
print(f"Found {halData_l} entries in Medialab HAL json dump.")

corpus = []
for hd in halData:
    try:
        corpus.append([
            hd["hal"]['meta']["citationFull_s"],
            hd["hal"]['meta']["abstract_s"]]
        )
    except Exception as e:
        pass
print(f"Found {len(corpus)} entries with `abstract_s` and `citationFull_s`.")


def remove_html_tags(text):
    """Remove html tags from a string"""
    text = re.sub('<a .*?</a>', '', text)
    text = re.sub('<i .*?</i>', '', text)
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

citations = [doc[0] for doc in corpus]
citations = [remove_html_tags(c) for c in citations]
abstracts = [doc[1][0] for doc in corpus]

# (1) Load sBert model
model = SentenceTransformer('distiluse-base-multilingual-cased-v1')

# Encode all abstracts
embeddings = model.encode(abstracts)

# (2) Most similar abstracts

# Compute cosine similarity between all pairs
cos_sim = util.cos_sim(embeddings, embeddings)

# Add all pairs to a list with their cosine similarity score
all_sentence_combinations = []
for i in range(len(cos_sim)-1):
    for j in range(i+1, len(cos_sim)):
        all_sentence_combinations.append([cos_sim[i][j], i, j])

# Sort list by the highest cosine similarity score
all_sentence_combinations = sorted(
    all_sentence_combinations, key=lambda x: x[0], reverse=True)

print("Top-5 most similar pairs:\n")
for score, i, j in all_sentence_combinations[0:5]:
    print(
        f"A: {citations[i]}\nB: {citations[j]}\n{cos_sim[i][j]:.4f}\n\n")

# (3) Create index

embedding_size = embeddings[0].shape[0]
top_k_hits = 3

# Defining our hnswlib index
index_path = "./hnswlib.index"
# We use Inner Product (dot-product) as Index.
# We will normalize our vectors to unit length.
index = hnswlib.Index(space='cosine', dim=embedding_size)

if os.path.exists(index_path):
    print("Loading index...")
    index.load_index(index_path)
else:
    # Create the HNSWLIB index
    print("Start creating HNSWLIB index")
    index.init_index(max_elements=len(embeddings), ef_construction=400, M=64)

    # Then we train the index to find a suitable clustering
    index.add_items(embeddings, list(range(len(embeddings))))

    print("Saving index to:", index_path)
    index.save_index(index_path)

# (4) some examples of information retrieval


inp_questions = [
    "enjeux environnementaux",
    "inégalités de genre et les violences sexuelles",
    "évaluations des politiques publiques",
    "partis de droite radicale",
    "l’Église orthodoxe en Russie"
]

print('---------------------------------------------------')
for inp_question in inp_questions:

    question_embedding = model.encode(inp_question)

    start_time = time.time()
    question_embedding = model.encode(inp_question)

    # We use hnswlib knn_query method to find the top_k_hits
    corpus_ids, distances = index.knn_query(question_embedding, k=top_k_hits)

    # We extract corpus ids and scores for the first query
    hits = [{'corpus_id': id, 'score': 1-score} for id, score in zip(corpus_ids[0], distances[0])]
    hits = sorted(hits, key=lambda x: x['score'], reverse=True)
    end_time = time.time()

    print("Input question:", inp_question)
    print("Results (after {:.3f} seconds):".format(end_time-start_time))
    for hit in hits[0:top_k_hits]:
        print("\t{:.3f}\t{}".format(hit['score'], citations[hit['corpus_id']]))
    print('---------------------------------------------------')


# (5) Information retrieval
while True:
    inp_question = input("Please enter a question: ")

    start_time = time.time()
    question_embedding = model.encode(inp_question)

    #We use hnswlib knn_query method to find the top_k_hits
    corpus_ids, distances = index.knn_query(question_embedding, k=top_k_hits)

    # We extract corpus ids and scores for the first query
    hits = [{'corpus_id': id, 'score': 1-score} for id, score in zip(corpus_ids[0], distances[0])]
    hits = sorted(hits, key=lambda x: x['score'], reverse=True)
    end_time = time.time()

    print("Input question:", inp_question)
    print("Results (after {:.3f} seconds):".format(end_time-start_time))
    for hit in hits[0:top_k_hits]:
        print("\t{:.3f}\t{}".format(hit['score'], citations[hit['corpus_id']]))

    # Approximate Nearest Neighbor (ANN) is not exact, it might miss entries with high cosine similarity
    # Here, we compute the recall of ANN compared to the exact results
    correct_hits = util.semantic_search(question_embedding, embeddings, top_k=top_k_hits)[0]
    correct_hits_ids = set([hit['corpus_id'] for hit in correct_hits])

    ann_corpus_ids = set([hit['corpus_id'] for hit in hits])
    if len(ann_corpus_ids) != len(correct_hits_ids):
        print("Approximate Nearest Neighbor returned a different number of results than expected")

    recall = len(ann_corpus_ids.intersection(correct_hits_ids)) / len(correct_hits_ids)
    print("\nApproximate Nearest Neighbor Recall@{}: {:.2f}".format(top_k_hits, recall * 100))

    if recall < 1:
        print("Missing results:")
        for hit in correct_hits[0:top_k_hits]:
            if hit['corpus_id'] not in ann_corpus_ids:
                print("\t{:.3f}\t{}".format(hit['score'], citations[hit['corpus_id']]))
    print("\n\n========\n")


# (5) tensorboard viz
# TO DO
