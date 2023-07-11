# medialab's expert search engine


POC of an expert search engine for medialab researchers based on HAL publications.

Inspired by https://recherche.pantheonsorbonne.fr/structures-recherche/rechercher-expertise

## build docker image
docker build -t halexp  -f Dockerfile . 

## run docker image
docker run -ti  --name=halexpinstance halexp
