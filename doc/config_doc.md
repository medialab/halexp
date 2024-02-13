```yaml
app:
show: number of responses to show [int]
  retrieve:
    top_k: number of entities to retrieve from search before ranking and filtering [int]
    score_threshold: minimum score threshold to retrieve an entity [float]
    min_year: minimum year to include an entity in response [int]
    rank_metric: metric used to rank entities in response, must be one of mean, median or log-mean [string]
corpus:
  max_length: [int]
  use_keys:
    abstract: whether to include or not the abstract of a HAL document in the text to be embedded [bool]
    title: whether to include or not the title of a HAL document in the text to be embedded [bool]
    subtitle: whether to include or not the subtitle of a HAL document in the text to be embedded [bool]
    keywords: whether to include or not the keywords of a HAL document in the text to be embedded [bool]
  dump_file: path to HAL dump in json format [str] 
  baseUrl: HAL api url [str]
  portail: must be one of ‘sciencespo’ or ‘index’ [str]
  query: must be one of ‘*:*’ or ‘labStructId_i:394361’ [str]
  pagination_count: pagination number for HAL api request [int]
  fields: fields of HAL api request [list of str]
index:
  hnswlib_space: name of the indexing space, must be one of "l2", "ip", or "cosine" [str]
  ef_construction: parameter that controls speed/accuracy trade-off during the index construction [int]
  M: parameter that defines the maximum number of outgoing connections in the hnsw graph [int]
  num_threads: number of threads to use in add_items and knn_query [int]
  sentence_transformer_model: model to embed entities [str]
  sentence_transformer_model_dim: number of dimension of [int]
  batch_size: batch size for embedding entities [int]
  index_path: path where to store in or load from the index [str]
```

## NOTES
1. The parameters under retrieve are the default parameters for the app, they can be changed at each query.
2. The parameters max_length and use_keys under corpus are used one time at the creation of the index; they will determine the principal characteristic of the entities embedding space and cannot be changed afterwards.
3. All other parameters cannot be changed after the creation of the index.




