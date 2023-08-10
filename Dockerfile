# syntax=docker/dockerfile:1

# tf.__version__ == '2.8.1'
# tensorboard.__version__ == '2.8.0'
FROM tensorflow/tensorflow:2.8.1 AS base

RUN apt-get update && \
    apt-get install nano -y && \
    apt-get install git -y

RUN python -m pip install --upgrade pip

# download sBert models
RUN python -m pip install sentence-transformers
RUN python -c "from sentence_transformers import SentenceTransformer; sBert = SentenceTransformer('all-mpnet-base-v2')"
RUN python -c "from sentence_transformers import SentenceTransformer; sBert = SentenceTransformer('distiluse-base-multilingual-cased-v1')"

# clone project repo and install dependencies
RUN git clone https://github.com/medialab/halexp.git
WORKDIR /halexp
RUN git pull
RUN pip install -r /halexp/python/requirements.txt

# download HAL dump
RUN ls
COPY get_dump.py get_dump.py
COPY config.yaml config.yaml
RUN python get_dump.py

RUN git pull

WORKDIR /halexp/python/halexp
CMD ["flask", "run", "--host=0.0.0.0", "--debugger"]
