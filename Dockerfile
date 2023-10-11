# Inspired from https://github.com/KEINOS/Dockerfile_of_SQLite3
# -----------------------------------------------------------------------------
#  Stage 0: build sqlite binary
# -----------------------------------------------------------------------------
FROM ubuntu:22.04 AS sqlite

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# install sqlite
COPY test_sqlite3.sh test_sqlite3.sh

RUN apt-get update && \
    apt-get install build-essential -y && \
    apt-get install wget -y
RUN wget https://www.sqlite.org/2023/sqlite-autoconf-3410100.tar.gz
RUN tar -xvf sqlite-autoconf-3410100.tar.gz
RUN ./sqlite-autoconf-3410100/configure && \
    make && \
    make install
RUN sqlite3 --version && \
    ./test_sqlite3.sh


# -----------------------------------------------------------------------------
#  Stage 1: install pyenv
# -----------------------------------------------------------------------------
FROM ubuntu:22.04 AS pyenv

ENV DEBIAN_FRONTEND=noninteractive

# install pyenv with pyenv-installer
COPY pyenv_dependencies.txt pyenv_dependencies.txt

ENV PYENV_GIT_TAG=v2.3.14

RUN apt-get update && \
    apt-get install -y $(cat pyenv_dependencies.txt) && \
    apt-get install curl -y
RUN curl https://pyenv.run | bash
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

RUN pyenv install 3.10 && \
    pyenv global 3.10

RUN pip install --no-cache-dir torch==2.0.1+cpu -f https://download.pytorch.org/whl/torch_stable.html && \
    pip install --no-cache-dir flask && \
    pip install --no-cache-dir hnswlib==0.7.0 && \
    pip install --no-cache-dir nltk && \
    pip install --no-cache-dir requests && \
    pip install --no-cache-dir scikit-learn && \
    pip install --no-cache-dir scipy && \
    pip install --no-cache-dir sentencepiece && \
    pip install --no-cache-dir torchvision && \
    pip install --no-cache-dir 'transformers[torch-cpu]' && \
    pip install --no-cache-dir --no-dependencies sentence-transformers && \
    pip cache purge

# # -----------------------------------------------------------------------------
# #  Stage 2: user setup
# # -----------------------------------------------------------------------------
FROM ubuntu:22.04

COPY --from=sqlite /usr/local/bin/sqlite3 /usr/local/bin/sqlite3
COPY --from=sqlite /usr/local/lib/libsqlite3.so.0 /usr/local/lib/libsqlite3.so.0
COPY test_sqlite3.sh test_sqlite3.sh
RUN sqlite3 --version && \
    ./test_sqlite3.sh

COPY --from=pyenv /root/.pyenv /root/.pyenv
ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
ENV PYTHONIOENCODING utf-8

RUN apt-get update && \
    apt-get install -y git && \
    apt-get install -y nano

# clone project repo
RUN git clone https://github.com/medialab/halexp.git
WORKDIR /halexp

ENV APPCONFIG=/halexp/config.yaml
ENV FLASK_APP=/halexp/python/halexp/app.py

# to remove when being able to push to github without triggering a build
COPY config.yaml config.yaml
COPY get_dump.py get_dump.py
COPY start.sh start.sh
COPY python/halexp/index.py python/halexp/index.py
CMD ["bash", "start.sh"]
