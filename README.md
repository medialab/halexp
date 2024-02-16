# medialab's expert search engine

![Image description](image.jpeg)

POC of an expert search engine for medialab researchers based on HAL publications.

Inspired by https://recherche.pantheonsorbonne.fr/structures-recherche/rechercher-expertise

## build docker image:
docker build -t halexp -f Dockerfile .

## run docker image:
docker run -ti --name=halexpinstance halexp

## setup a specific configuration within Docker using environment variables (see available ones in [prepare_config.py](prepare_config.py)):
docker run -ti --name=halexpinstance -e HAL_QUERY="labStructId_i:394361" -e DEFAULT_NB_RESULTS=10 halexp

## or setup a specific configuration within Docker using an env file (to create based on the [config.env.example](example one)):
docker run -ti --name=halexpinstance --env-file ./config.env halexp

