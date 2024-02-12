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

COPY pyenv_dependencies.txt pyenv_dependencies.txt
RUN apt-get update && \
    apt-get install -y $(cat pyenv_dependencies.txt) && \
    apt-get install curl -y

ENV PYENV_GIT_TAG=v2.3.14
RUN curl https://pyenv.run | bash
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
RUN pyenv install 3.10 && \
    pyenv global 3.10

RUN pip install --cache-dir=/tmp/pipcache --upgrade setuptools pip && \
    pip install --cache-dir=/tmp/pipcache pyyaml==6.0.1 && \
    pip install --cache-dir=/tmp/pipcache requests==2.31.0 && \
    pip install --cache-dir=/tmp/pipcache Flask==2.3.3 && \
    pip install --cache-dir=/tmp/pipcache gunicorn==21.2.0 && \
    pip install --cache-dir=/tmp/pipcache Pillow==10.0.1 && \
    pip install --cache-dir=/tmp/pipcache numpy==1.26.0 && \
    pip install --cache-dir=/tmp/pipcache scipy==1.11.2 && \
    pip install --cache-dir=/tmp/pipcache hnswlib==0.7.0 && \
    pip install --cache-dir=/tmp/pipcache nltk==3.8.1 && \
    pip install --cache-dir=/tmp/pipcache scikit-learn==1.3.1 && \
    pip install --cache-dir=/tmp/pipcache sentencepiece==0.1.99 && \
    pip install --cache-dir=/tmp/pipcache torch==2.0.1+cpu -f https://download.pytorch.org/whl/torch_stable.html && \
    pip install --cache-dir=/tmp/pipcache --no-dependencies torchvision==0.15.2 -f https://download.pytorch.org/whl/torch_stable.html && \
    pip install --cache-dir=/tmp/pipcache 'transformers[torch-cpu]'==4.37.2 && \
    pip install --cache-dir=/tmp/pipcache --no-dependencies sentence-transformers==2.2.2 && \
    pip cache purge && \
    rm -r /tmp/pipcache


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
    apt-get install -y git

WORKDIR /halexp

COPY ./halexp /halexp/halexp
COPY config_default.yaml config_default.yaml
COPY prepare_config.py prepare_config.py
COPY get_dump.py get_dump.py
COPY start.sh start.sh

CMD ["bash", "start.sh"]
