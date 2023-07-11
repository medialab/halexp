# syntax=docker/dockerfile:1

# tf.__version__ == '2.8.1'
# tensorboard.__version__ == '2.8.0'
FROM tensorflow/tensorflow:2.8.1 AS base

RUN apt-get update && \
    apt-get install nano -y && \
    apt-get install git -y

RUN python -m pip install --upgrade pip

# clone project repo and install dependencies
RUN git clone https://github.com/medialab/halexp.git
WORKDIR /halexp
RUN pip install -r requirements.txt

# download sBert models
RUN python -c "from sentence_transformers import SentenceTransformer; sBert = SentenceTransformer('all-mpnet-base-v2')"
RUN python -c "from sentence_transformers import SentenceTransformer; sBert = SentenceTransformer('distiluse-base-multilingual-cased-v1')"

COPY hal-productions.json hal-productions.json
